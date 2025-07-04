#!/usr/bin/env python3
"""
Intelligence Manager - Orchestrates all data acquisition operations
"""

import os
import sys
import subprocess
import threading
import time
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timezone, timedelta

# Set Eastern timezone globally for the project
try:
    import pytz
    EST = pytz.timezone('US/Eastern')  # Automatically handles EST/EDT
except ImportError:
    # Fallback to manual timezone (currently EDT during summer)
    import time
    # Check if we're in daylight saving time
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    offset_hours = -4 if is_dst else -5  # EDT is UTC-4, EST is UTC-5
    EST = timezone(timedelta(hours=offset_hours))

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages all data acquisition operations with real-time monitoring"""
    
    ACQUISITION_MODES = {
        'test': {
            'script': 'acquire_from_sitemap.py',
            'description': 'Test mode with limited products (default: 10 URLs)',
            'args': []
        },
        'sitemap': {
            'script': 'acquire_from_sitemap.py',
            'description': 'Full sitemap acquisition with recovery',
            'args': []
        },
        'category': {
            'script': 'acquire_from_sitemap.py',
            'description': 'Category-based acquisition with optimized parsing',
            'args': []
        }
    }
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.current_process = None
        self.is_running = False
        self.current_mode = None
        self.current_args = []
        self.start_time = None
        self.stats = {
            'products_processed': 0,
            'success_count': 0,
            'error_count': 0,
            'current_url': '',
            'estimated_total': 0,
            'progress_percent': 0
        }
        
        # Rolling performance tracking for speed calculation
        self.recent_successful_saves = []  # Store last 5 successful save timestamps
        self.max_recent_saves = 5
        
        # Counter tracking for time between page reads
        self.last_page_read_time = None
        self.seconds_since_last_read = 0
        self.counter_start_time = None
        self.recent_counter_values = []  # Store last 5 counter values for average
        self.max_counter_values = 5
        
        self.log_lines = []
        self.max_log_lines = 100
        
        # Pre-warming state
        self.is_prewarmed = False
        self.prewarm_status = {
            'virtual_env': False,
            'relational_db': False,
            'vector_db': False,
            'sitemap_validation': False,
            'crawl4ai_service': False
        }
        self.prewarm_thread = None
        
    def start_prewarm(self):
        """Start pre-warming initialization in background"""
        if self.prewarm_thread and self.prewarm_thread.is_alive():
            return {'success': True, 'message': 'Pre-warming already in progress'}
            
        if self.is_prewarmed:
            return {'success': True, 'message': 'System already pre-warmed'}
            
        logger.info("Starting pre-warming initialization...")
        self.prewarm_thread = threading.Thread(target=self._prewarm_initialization)
        self.prewarm_thread.daemon = True
        self.prewarm_thread.start()
        
        return {'success': True, 'message': 'Pre-warming started'}
    
    def _prewarm_initialization(self):
        """Pre-warm all initialization components"""
        try:
            logger.info("Pre-warming: Checking virtual environment...")
            # Check virtual environment
            venv_python = '/Users/robertsher/Projects/autogen_env/bin/python'
            if os.path.exists(venv_python):
                self.prewarm_status['virtual_env'] = True
                logger.info("Pre-warming: Virtual environment OK")
            
            logger.info("Pre-warming: Testing database connections...")
            # Test both database connections using the same method as system stats
            try:
                from .db_manager import DatabaseManager
                db_manager = DatabaseManager()
                db_connections = db_manager.test_connections()
                
                # Test relational_db (PostgreSQL)
                if db_connections.get('relational_db', {}).get('connected', False):
                    self.prewarm_status['relational_db'] = True
                    logger.info("Pre-warming: relational_db connection OK")
                else:
                    logger.warning(f"Pre-warming: relational_db connection failed")
                
                # Test vector_db (Supabase)
                if db_connections.get('supabase', {}).get('connected', False):
                    self.prewarm_status['vector_db'] = True
                    logger.info("Pre-warming: vector_db connection OK")
                else:
                    logger.warning(f"Pre-warming: vector_db connection failed")
                    
            except Exception as e:
                logger.warning(f"Pre-warming: Database connections test failed: {e}")
            
            logger.info("Pre-warming: Validating sitemap...")
            # Validate sitemap existence
            try:
                sitemap_file = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'tileshop_sitemap.json'
                )
                if os.path.exists(sitemap_file):
                    self.prewarm_status['sitemap_validation'] = True
                    logger.info("Pre-warming: Sitemap validation OK")
            except Exception as e:
                logger.warning(f"Pre-warming: Sitemap validation failed: {e}")
            
            logger.info("Pre-warming: Testing Crawler service...")
            # Test Crawler service
            try:
                import requests
                response = requests.get('http://localhost:11235/health', timeout=5)
                if response.status_code == 200:
                    self.prewarm_status['crawl4ai_service'] = True
                    logger.info("Pre-warming: Crawler service OK")
            except Exception as e:
                logger.warning(f"Pre-warming: Crawler service check failed: {e}")
            
            # Check if all components are ready
            all_ready = all(self.prewarm_status.values())
            self.is_prewarmed = all_ready
            
            if all_ready:
                logger.info("Pre-warming completed successfully - system ready for instant learning")
            else:
                failed_components = [k for k, v in self.prewarm_status.items() if not v]
                logger.warning(f"Pre-warming completed with issues: {failed_components}")
                
        except Exception as e:
            logger.error(f"Pre-warming initialization failed: {e}")
    
    def get_prewarm_status(self) -> Dict[str, Any]:
        """Get current pre-warming status"""
        return {
            'is_prewarmed': self.is_prewarmed,
            'prewarm_status': self.prewarm_status.copy(),
            'prewarm_in_progress': self.prewarm_thread and self.prewarm_thread.is_alive()
        }
        
    def start_acquisition(self, mode: str, limit: Optional[int] = None, fresh: bool = False, batch_size: Optional[int] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Start data acquisition in specified mode"""
        if self.is_running:
            return {
                'success': False,
                'error': 'Data acquisition is already running'
            }
        
        if mode not in self.ACQUISITION_MODES:
            return {
                'success': False,
                'error': f'Unknown acquisition mode: {mode}'
            }
        
        # Build command arguments
        script_path = self.ACQUISITION_MODES[mode]['script']
        args = ['python', script_path]
        
        # Add mode-specific arguments
        if mode == 'test' and limit:
            args.append(str(limit))
        elif mode == 'sitemap':
            if limit:
                args.append(str(limit))
            if fresh:
                args.append('--fresh')
        elif mode == 'category':
            if category:
                args.extend(['--category', category])
            if fresh:
                args.append('--fresh')
        
        # Add batch size parameter if provided
        if batch_size:
            args.extend(['--batch-size', str(batch_size)])
        
        self.current_mode = mode
        self.current_args = args
        self.reset_stats()
        
        try:
            # Start the acquisition process
            self.start_time = datetime.now(EST)
            self.is_running = True
            
            # Run in separate thread to avoid blocking
            thread = threading.Thread(target=self._run_acquisition, args=(args,))
            thread.daemon = True
            thread.start()
            
            return {
                'success': True,
                'message': f'Started {mode} acquisition',
                'mode': mode,
                'args': args
            }
            
        except Exception as e:
            self.is_running = False
            return {
                'success': False,
                'error': f'Failed to start acquisition: {str(e)}'
            }
    
    def _run_acquisition(self, args: list):
        """Run the acquisition subprocess with monitoring"""
        try:
            # Change to project directory
            project_dir = os.path.dirname(os.path.abspath(__file__)).replace('/modules', '')
            
            # Activate virtual environment and run
            venv_python = '/Users/robertsher/Projects/autogen_env/bin/python'  # Sandbox environment
            if os.path.exists(venv_python):
                args[0] = venv_python
            
            # Set up environment for virtual environment
            env = os.environ.copy()
            venv_dir = '/Users/robertsher/Projects/sandbox_env'  # Sandbox directory
            if os.path.exists(venv_dir):
                env['VIRTUAL_ENV'] = venv_dir
                env['PATH'] = f"{venv_dir}/bin:{env.get('PATH', '')}"
            
            self.current_process = subprocess.Popen(
                args,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env
            )
            
            # Monitor output with enhanced progress detection
            for line in iter(self.current_process.stdout.readline, ''):
                if line:
                    line_stripped = line.strip()
                    self._process_log_line(line_stripped)
                    
                    # Debug: Log every line to help diagnose issues
                    logger.debug(f"Acquisition subprocess output: {line_stripped}")
                    
                    # Enhanced progress callback with detailed parsing
                    if self.progress_callback:
                        progress_data = self._parse_progress_line(line_stripped)
                        if progress_data:
                            self.progress_callback('progress_update', progress_data)
                        self.progress_callback('log', {'line': line_stripped})
            
            # Wait for completion
            return_code = self.current_process.wait()
            
            # Update final status
            self.is_running = False
            final_status = 'completed' if return_code == 0 else 'failed'
            
            if self.progress_callback:
                self.progress_callback('completed', {
                    'status': final_status,
                    'return_code': return_code,
                    'stats': self.stats
                })
                
        except Exception as e:
            logger.error(f"Error running acquisition: {e}")
            self.is_running = False
            if self.progress_callback:
                self.progress_callback('error', {'error': str(e)})
    
    def _parse_progress_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse progress information from enhanced crawl output"""
        line_lower = line.lower()
        
        # Parse crawl progress events
        if '📊 crawl_start:' in line:
            return {'type': 'crawl_start', 'stage': 'starting', 'message': line}
        elif '📋 task submitted:' in line:
            # Extract task ID and timing
            if 'task submitted:' in line and '(' in line:
                parts = line.split('task submitted:')[1].strip()
                task_id = parts.split('(')[0].strip()
                timing = parts.split('(')[1].replace(')', '').replace('s', '')
                return {
                    'type': 'crawl_submitted', 
                    'task_id': task_id, 
                    'submit_time': float(timing) if timing.replace('.', '').isdigit() else 0
                }
        elif '🔍 status check #' in line and ':' in line:
            # Extract status and timing info
            try:
                if 'elapsed' in line and 'check' in line:
                    status_part = line.split(':')[1].split('(')[0].strip()
                    elapsed_part = line.split('elapsed')[0].split('(')[-1].replace('s', '')
                    return {
                        'type': 'crawl_status',
                        'status': status_part,
                        'elapsed': float(elapsed_part) if elapsed_part.replace('.', '').isdigit() else 0
                    }
            except (IndexError, ValueError):
                pass
        elif '✅ crawl completed in' in line or '⚡ crawl completed immediately' in line:
            # Log crawl completion but don't use for speed calculation
            try:
                if 'completed in' in line:
                    time_part = line.split('completed in')[1].split('s')[0].strip()
                elif 'completed immediately' in line and '(' in line:
                    time_part = line.split('(')[1].split('s')[0].strip()
                else:
                    time_part = None
                
                if time_part and time_part.replace('.', '').isdigit():
                    crawl_time = float(time_part)
                    return {
                        'type': 'crawl_complete',
                        'total_time': crawl_time
                    }
            except (IndexError, ValueError):
                pass
        elif '⏰ crawl timeout' in line:
            return {'type': 'crawl_timeout', 'message': line}
        elif '✗ crawl failed:' in line:
            error_msg = line.split('crawl failed:')[1].strip() if 'crawl failed:' in line else 'Unknown error'
            return {'type': 'crawl_error', 'error': error_msg}
        
        # Parse general progress patterns
        elif any(pattern in line_lower for pattern in ['processing', 'scraping', 'extracting']):
            if 'processing ' in line_lower and '/' in line:
                try:
                    # Extract current/total pattern like "Processing 5/100"
                    progress_part = line.split('Processing')[1].split(':')[0].strip()
                    if '/' in progress_part:
                        current, total = progress_part.split('/')
                        return {
                            'type': 'processing_progress',
                            'current': int(current),
                            'total': int(total),
                            'percent': (int(current) / int(total)) * 100
                        }
                except (IndexError, ValueError):
                    pass
        
        return None
    
    def _calculate_rolling_speed(self) -> float:
        """Calculate rolling average speed from last 5 successful saves based on timestamp differences"""
        if len(self.recent_successful_saves) < 2:
            return 0.0
        
        # Calculate time differences between consecutive saves
        time_differences = []
        for i in range(1, len(self.recent_successful_saves)):
            time_diff = self.recent_successful_saves[i] - self.recent_successful_saves[i-1]
            time_differences.append(time_diff)
        
        if not time_differences:
            return 0.0
        
        # Calculate average time between saves (in seconds)
        avg_time_between_saves = sum(time_differences) / len(time_differences)
        
        # Convert to pages per minute
        if avg_time_between_saves > 0:
            pages_per_minute = 60.0 / avg_time_between_saves
            return round(pages_per_minute, 1)
        
        return 0.0
    
    def _calculate_average_read_speed(self) -> float:
        """Calculate average read speed from counter values (sum of 5 counters divided by 5)"""
        if len(self.recent_counter_values) == 0:
            return 0.0
        
        # Calculate average of counter values
        avg_counter_seconds = sum(self.recent_counter_values) / len(self.recent_counter_values)
        
        # Convert to pages per minute (60 seconds / avg_seconds_per_page)
        if avg_counter_seconds > 0:
            pages_per_minute = 60.0 / avg_counter_seconds
            return round(pages_per_minute, 1)
        
        return 0.0
    
    def _get_current_counter_value(self) -> int:
        """Get current counter value (seconds since last page read)"""
        if not self.is_running:
            return 0
            
        import time
        current_time = time.time()
        
        # If we have a last page read time, count from there
        if self.last_page_read_time is not None:
            return int(current_time - self.last_page_read_time)
        # If we haven't read any pages yet but are running, count from start
        elif self.start_time is not None:
            return int(current_time - self.start_time.timestamp())
        else:
            return 0
    
    def _process_log_line(self, line: str):
        """Process log line and extract progress information"""
        # Add to log buffer
        self.log_lines.append({
            'timestamp': datetime.now(EST).isoformat(),
            'message': line
        })
        
        # Keep only recent lines
        if len(self.log_lines) > self.max_log_lines:
            self.log_lines = self.log_lines[-self.max_log_lines:]
        
        # Extract progress information
        try:
            line_lower = line.lower()
            
            # Look for URL processing patterns (broader patterns)
            processing_patterns = [
                'processing url:', 'processing product', '🔄 processing url:', 
                'scraping url', 'scraping:', 'fetching:', 'crawling:', 
                'extracting from', 'loading url', 'requesting url'
            ]
            
            if any(pattern in line_lower for pattern in processing_patterns):
                self.stats['products_processed'] += 1
                
                # Try to extract current URL
                if 'https://' in line:
                    url_start = line.find('https://')
                    url_end = line.find(' ', url_start)
                    if url_end == -1:
                        url_end = len(line)
                    self.stats['current_url'] = line[url_start:url_end]
            
            # Look for success patterns (broader patterns)
            success_patterns = [
                '✓ saved product data', 'saved product data for:', 'successfully extracted', 'success', 
                '✅ product scraped', 'completed successfully', 'saved to database',
                'product data saved', 'extraction complete', 'successfully processed',
                'inserted product', 'data extraction complete', 'saved product',
                'product stored', 'database insert', 'successfully saved'
            ]
            
            if any(pattern in line_lower for pattern in success_patterns):
                self.stats['success_count'] += 1
                
                # Track successful save timestamp for speed calculation
                import time
                current_timestamp = time.time()
                self.recent_successful_saves.append(current_timestamp)
                
                # Keep only last 5 successful saves
                if len(self.recent_successful_saves) > self.max_recent_saves:
                    self.recent_successful_saves = self.recent_successful_saves[-self.max_recent_saves:]
                
                # Update counter for time between page reads
                if self.last_page_read_time is not None:
                    counter_value = int(current_timestamp - self.last_page_read_time)
                    # Store this counter value for average calculation
                    self.recent_counter_values.append(counter_value)
                    # Keep only last 5 counter values
                    if len(self.recent_counter_values) > self.max_counter_values:
                        self.recent_counter_values = self.recent_counter_values[-self.max_counter_values:]
                    
                    # Reset counter to 0 for next page
                    self.seconds_since_last_read = 0
                else:
                    # First page read, initialize counter
                    self.counter_start_time = current_timestamp
                    self.seconds_since_last_read = 0
                    
                self.last_page_read_time = current_timestamp
                
                # Extract URL from success messages
                if 'https://' in line:
                    url_start = line.find('https://')
                    url_end = line.find(' ', url_start)
                    if url_end == -1:
                        url_end = len(line)
                    self.stats['current_url'] = line[url_start:url_end]
                
            # Look for error patterns (broader patterns)
            error_patterns = [
                'error', 'failed to', '❌', '⚠️', 'exception', 'timeout',
                'could not', 'unable to', 'failed', 'error:', 'warning:'
            ]
            
            if any(pattern in line_lower for pattern in error_patterns):
                self.stats['error_count'] += 1
                
            # Look for total count patterns (broader patterns)
            total_patterns = [
                'total products to scrape', 'found', 'urls to process:',
                'total urls:', 'processing', 'items to scrape', 'total items:'
            ]
            
            if any(pattern in line_lower for pattern in total_patterns):
                # Try to extract total count
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    # Take the largest number found
                    max_number = max(int(n) for n in numbers)
                    # Only update if it's a reasonable number
                    if max_number > self.stats['estimated_total'] and max_number < 100000:
                        self.stats['estimated_total'] = max_number
            
            # Calculate progress percentage - use success_count for more accurate progress
            if self.stats['estimated_total'] > 0:
                # Use success_count for progress calculation as it's more meaningful
                self.stats['progress_percent'] = min(
                    100,
                    (self.stats['success_count'] / self.stats['estimated_total']) * 100
                )
            elif self.stats['products_processed'] > 0:
                # If no total, show relative progress
                self.stats['progress_percent'] = min(100, self.stats['products_processed'] * 2)
            
        except Exception as e:
            logger.debug(f"Error parsing log line: {e}")
        
        # Emit progress update via callback for real-time UI updates
        if self.progress_callback:
            self.progress_callback('log', {
                'line': line,
                'stats': self.stats.copy()
            })
    
    def stop_acquisition(self) -> Dict[str, Any]:
        """Stop the currently running acquisition process"""
        if not self.is_running or not self.current_process:
            return {
                'success': False,
                'error': 'No acquisition process is currently running'
            }
        
        try:
            self.current_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.current_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.current_process.kill()
                self.current_process.wait()
            
            self.is_running = False
            self.current_process = None
            
            return {
                'success': True,
                'message': 'Acquisition stopped successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to stop acquisition: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current acquisition status and statistics"""
        runtime = None
        if self.start_time:
            runtime = (datetime.now(EST) - self.start_time).total_seconds()
        
        # Check scraper status file to get real-time status
        scraper_is_running = self.is_running
        try:
            with open('/tmp/tileshop_scraper_status.json', 'r') as f:
                scraper_status = json.load(f)
                scraper_file_status = scraper_status.get('status', 'idle')
                
                # If scraper status file indicates processing, update is_running
                if scraper_file_status in ['starting', 'processing']:
                    scraper_is_running = True
                elif scraper_file_status in ['completed', 'idle'] and not self.current_process:
                    scraper_is_running = False
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Fall back to internal is_running state
            pass
        
        # Reprocess logs to ensure accurate statistics
        self._reprocess_logs_for_stats()
        
        # Enhance stats with sitemap data for accurate progress
        enhanced_stats = self._enhance_stats_with_sitemap()
        
        return {
            'is_running': scraper_is_running,
            'mode': self.current_mode,
            'args': self.current_args,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'runtime_seconds': runtime,
            'stats': enhanced_stats,
            'recent_logs': self.log_lines[-10:] if self.log_lines else [],
            'average_read_speed_pages_per_minute': self._calculate_average_read_speed(),
            'counter_seconds_since_last_read': self._get_current_counter_value(),
            'recent_save_count': len(self.recent_successful_saves)
        }
    
    def get_logs(self, lines: int = 50) -> List[Dict[str, str]]:
        """Get recent log lines"""
        return self.log_lines[-lines:] if self.log_lines else []
    
    def _reprocess_logs_for_stats(self):
        """Reprocess all logs to calculate accurate statistics"""
        if not self.log_lines:
            return
            
        # Reset counters but preserve estimated_total
        estimated_total = self.stats.get('estimated_total', 0)
        current_url = self.stats.get('current_url', '')
        
        temp_stats = {
            'products_processed': 0,
            'success_count': 0,
            'error_count': 0,
            'current_url': current_url,
            'estimated_total': estimated_total,
            'progress_percent': 0
        }
        
        # Process all log lines to get accurate counts
        for log_entry in self.log_lines:
            line = log_entry.get('message', '')
            line_lower = line.lower()
            
            # Count processing events (use same patterns as _process_log_line)
            processing_patterns = [
                'processing url:', 'processing product', '🔄 processing url:', 
                'scraping url', 'scraping:', 'fetching:', 'crawling:', 
                'extracting from', 'loading url', 'requesting url'
            ]
            
            if any(pattern in line_lower for pattern in processing_patterns):
                temp_stats['products_processed'] += 1
                
                # Extract current URL
                if 'https://' in line:
                    url_start = line.find('https://')
                    url_end = line.find(' ', url_start)
                    if url_end == -1:
                        url_end = len(line)
                    temp_stats['current_url'] = line[url_start:url_end]
            
            # Count successes (use same patterns as _process_log_line)
            success_patterns = [
                '✓ saved product data', 'saved product data for:', 'successfully extracted', 'success', 
                '✅ product scraped', 'completed successfully', 'saved to database',
                'product data saved', 'extraction complete', 'successfully processed'
            ]
            
            if any(pattern in line_lower for pattern in success_patterns):
                temp_stats['success_count'] += 1
                
                # Extract URL from success messages
                if 'https://' in line:
                    url_start = line.find('https://')
                    url_end = line.find(' ', url_start)
                    if url_end == -1:
                        url_end = len(line)
                    temp_stats['current_url'] = line[url_start:url_end]
            
            # Count errors (use same patterns as _process_log_line)
            error_patterns = [
                'error', 'failed to', '❌', '⚠️', 'exception', 'timeout',
                'could not', 'unable to', 'failed', 'error:', 'warning:'
            ]
            
            if any(pattern in line_lower for pattern in error_patterns):
                temp_stats['error_count'] += 1
            
            # Extract total count (use same patterns as _process_log_line)
            total_patterns = [
                'total products to scrape', 'found', 'urls to process:',
                'total urls:', 'processing', 'items to scrape', 'total items:'
            ]
            
            if any(pattern in line_lower for pattern in total_patterns):
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    max_number = max(int(n) for n in numbers)
                    if max_number > temp_stats['estimated_total'] and max_number < 100000:
                        temp_stats['estimated_total'] = max_number
        
        # Calculate progress percentage
        if temp_stats['estimated_total'] > 0:
            temp_stats['progress_percent'] = min(
                100,
                (temp_stats['success_count'] / temp_stats['estimated_total']) * 100
            )
        
        # Update main stats
        self.stats.update(temp_stats)
    
    def _enhance_stats_with_sitemap(self) -> Dict[str, Any]:
        """Enhance stats with actual sitemap data for accurate progress tracking"""
        enhanced_stats = self.stats.copy()
        
        # Try to read sitemap data for accurate totals
        sitemap_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tileshop_sitemap.json')
        
        try:
            if os.path.exists(sitemap_path):
                with open(sitemap_path, 'r') as f:
                    sitemap_data = json.load(f)
                
                # Get accurate counts from sitemap
                total_urls = sitemap_data.get('total_urls', enhanced_stats['estimated_total'])
                
                # Count completed and pending URLs
                urls = sitemap_data.get('urls', [])
                completed_count = len([url for url in urls if url.get('scrape_status') == 'completed'])
                pending_count = len([url for url in urls if url.get('scrape_status') == 'pending'])
                failed_count = len([url for url in urls if url.get('scrape_status') == 'failed'])
                
                # Update enhanced stats with sitemap data - preserve real-time counts if higher
                enhanced_stats['estimated_total'] = total_urls
                
                # Use the higher of real-time log count vs sitemap count to prevent jumps
                current_success = enhanced_stats.get('success_count', 0)
                current_error = enhanced_stats.get('error_count', 0)
                
                # Only update counts if sitemap shows more progress (prevents backwards jumps)
                if completed_count > current_success:
                    logger.debug(f"Success count updated: {current_success} → {completed_count}")
                    enhanced_stats['success_count'] = completed_count
                if failed_count > current_error:
                    logger.debug(f"Error count updated: {current_error} → {failed_count}")
                    enhanced_stats['error_count'] = failed_count
                    
                enhanced_stats['products_processed'] = enhanced_stats['success_count'] + enhanced_stats['error_count']
                
                # Calculate accurate progress percentage using consistent success count
                if total_urls > 0:
                    enhanced_stats['progress_percent'] = (enhanced_stats['success_count'] / total_urls) * 100
                
                # Try to get current URL from scraper status file first
                try:
                    with open('/tmp/tileshop_scraper_status.json', 'r') as f:
                        scraper_status = json.load(f)
                        if self.is_running and scraper_status.get('current_url'):
                            enhanced_stats['current_url'] = scraper_status['current_url']
                        elif scraper_status.get('status') == 'starting':
                            enhanced_stats['current_url'] = 'Starting scraper...'
                        elif scraper_status.get('status') == 'processing' and scraper_status.get('current_url'):
                            enhanced_stats['current_url'] = scraper_status['current_url']
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    # Fall back to original logic if status file is not available
                    if self.is_running and not enhanced_stats['current_url']:
                        # Find the first pending URL as likely current processing
                        for url_data in urls:
                            if url_data.get('scrape_status') == 'pending':
                                enhanced_stats['current_url'] = url_data.get('url', '')
                                break
                        
                        if not enhanced_stats['current_url']:
                            enhanced_stats['current_url'] = 'Starting scraper...'
                    elif not self.is_running:
                        enhanced_stats['current_url'] = ''
                    
        except Exception as e:
            logger.warning(f"Could not enhance stats with sitemap data: {e}")
            # Fall back to log-based stats
            pass
        
        return enhanced_stats
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'products_processed': 0,
            'success_count': 0,
            'error_count': 0,
            'current_url': '',
            'estimated_total': 0,
            'progress_percent': 0
        }
        self.log_lines = []
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if all required dependencies are running"""
        # This could be enhanced to actually check services
        # For now, return a basic check
        
        dependencies = {
            'postgres': False,
            'crawl4ai-browser': False,
            'python_environment': False
        }
        
        try:
            # Check if virtual environment exists
            venv_python = '/Users/robertsher/Projects/autogen_env/bin/python'  # Sandbox environment
            if os.path.exists(venv_python):
                dependencies['python_environment'] = True
            
            # Check if acquisition scripts exist
            project_dir = os.path.dirname(os.path.abspath(__file__)).replace('/modules', '')
            for mode, config in self.ACQUISITION_MODES.items():
                script_path = os.path.join(project_dir, config['script'])
                if not os.path.exists(script_path):
                    return {
                        'ready': False,
                        'error': f'Missing acquisition script: {config["script"]}',
                        'dependencies': dependencies
                    }
            
            # Basic dependency check (would need Docker manager for full check)
            all_ready = all(dependencies.values())
            
            return {
                'ready': all_ready,
                'dependencies': dependencies,
                'message': 'All dependencies ready' if all_ready else 'Some dependencies missing'
            }
            
        except Exception as e:
            return {
                'ready': False,
                'error': f'Dependency check failed: {str(e)}',
                'dependencies': dependencies
            }
    
    def get_available_modes(self) -> Dict[str, Dict[str, str]]:
        """Get all available acquisition modes"""
        return self.ACQUISITION_MODES.copy()
    
    def learn_single_product(self, url: str, sku: str = 'Unknown') -> Dict[str, Any]:
        """Learn a single product by URL"""
        try:
            logger.info(f"Starting single product learning for SKU {sku}: {url}")
            
            if self.is_running:
                return {
                    'success': False,
                    'error': 'Acquisition system is currently running. Please wait for it to complete or stop it first.'
                }
            
            # Prepare single URL for learning
            self.is_running = True
            self.stats = {
                'total_processed': 0,
                'successful': 0,
                'errors': 0,
                'start_time': datetime.now(EST).isoformat(),
                'current_url': url
            }
            
            # Update status file
            self.update_scraper_status(url, 'processing')
            
            # Use curl-based enhanced extraction (only working method)
            try:
                script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'curl_scraper.py')
                
                # Use subprocess to run curl-based enhanced extraction with specific URL
                self.current_process = subprocess.Popen(
                    [sys.executable, script_path, '--single-url', url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    cwd=os.path.dirname(os.path.dirname(__file__))
                )
                
                # Monitor progress in background thread
                def monitor_learning():
                    try:
                        for line in iter(self.current_process.stdout.readline, ''):
                            if line:
                                line_stripped = line.strip()
                                logger.info(f"Single product learning: {line_stripped}")
                                
                                # Update stats based on output
                                if 'saved product data' in line_stripped.lower():
                                    self.stats['successful'] += 1
                                elif 'error' in line_stripped.lower() or 'failed' in line_stripped.lower():
                                    self.stats['errors'] += 1
                                
                                self.stats['total_processed'] += 1
                        
                        # Wait for completion
                        return_code = self.current_process.wait()
                        self.is_running = False
                        
                        if return_code == 0:
                            self.update_scraper_status(None, 'idle')
                            logger.info(f"Successfully completed learning for SKU {sku}")
                        else:
                            self.update_scraper_status(None, 'error')
                            logger.error(f"Learning failed for SKU {sku} with return code {return_code}")
                            
                    except Exception as e:
                        logger.error(f"Error in single product learning monitor: {e}")
                        self.is_running = False
                        self.update_scraper_status(None, 'error')
                
                # Start monitoring thread
                monitor_thread = threading.Thread(target=monitor_learning, daemon=True)
                monitor_thread.start()
                
                return {
                    'success': True,
                    'message': f'Started learning process for SKU {sku}. This will take 30-60 seconds.',
                    'url': url,
                    'sku': sku,
                    'process_id': self.current_process.pid
                }
                
            except Exception as e:
                self.is_running = False
                self.update_scraper_status(None, 'error')
                return {
                    'success': False,
                    'error': f'Failed to start learning process: {str(e)}'
                }
                
        except Exception as e:
            logger.error(f"Error in learn_single_product: {e}")
            self.is_running = False
            return {
                'success': False,
                'error': f'Single product learning failed: {str(e)}'
            }
    
    def update_scraper_status(self, current_url=None, status='idle'):
        """Update scraper status file for dashboard communication"""
        try:
            status_file = '/tmp/tileshop_scraper_status.json'
            status_data = {
                'current_url': current_url or '',
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
            with open(status_file, 'w') as f:
                json.dump(status_data, f)
        except Exception as e:
            logger.error(f"Failed to update scraper status: {e}")