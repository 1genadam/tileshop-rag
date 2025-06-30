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
from datetime import datetime

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
            
            logger.info("Pre-warming: Testing Crawl4AI service...")
            # Test Crawl4AI service
            try:
                import requests
                response = requests.get('http://localhost:11235/health', timeout=5)
                if response.status_code == 200:
                    self.prewarm_status['crawl4ai_service'] = True
                    logger.info("Pre-warming: Crawl4AI service OK")
            except Exception as e:
                logger.warning(f"Pre-warming: Crawl4AI service check failed: {e}")
            
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
        
    def start_acquisition(self, mode: str, limit: Optional[int] = None, fresh: bool = False) -> Dict[str, Any]:
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
        
        self.current_mode = mode
        self.current_args = args
        self.reset_stats()
        
        try:
            # Start the acquisition process
            self.start_time = datetime.now()
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
            
            # Monitor output
            for line in iter(self.current_process.stdout.readline, ''):
                if line:
                    self._process_log_line(line.strip())
                    if self.progress_callback:
                        self.progress_callback('log', {'line': line.strip()})
            
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
    
    def _process_log_line(self, line: str):
        """Process log line and extract progress information"""
        # Add to log buffer
        self.log_lines.append({
            'timestamp': datetime.now().isoformat(),
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
                '✓ saved product data', 'successfully extracted', 'success', 
                '✅ product scraped', 'completed successfully', 'saved to database',
                'product data saved', 'extraction complete', 'successfully processed'
            ]
            
            if any(pattern in line_lower for pattern in success_patterns):
                self.stats['success_count'] += 1
                
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
            runtime = (datetime.now() - self.start_time).total_seconds()
        
        # Reprocess logs to ensure accurate statistics
        self._reprocess_logs_for_stats()
        
        # Enhance stats with sitemap data for accurate progress
        enhanced_stats = self._enhance_stats_with_sitemap()
        
        return {
            'is_running': self.is_running,
            'mode': self.current_mode,
            'args': self.current_args,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'runtime_seconds': runtime,
            'stats': enhanced_stats,
            'recent_logs': self.log_lines[-10:] if self.log_lines else []
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
                '✓ saved product data', 'successfully extracted', 'success', 
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
                
                # Update enhanced stats with sitemap data
                enhanced_stats['estimated_total'] = total_urls
                enhanced_stats['success_count'] = completed_count
                enhanced_stats['error_count'] = failed_count
                enhanced_stats['products_processed'] = completed_count + failed_count
                
                # Calculate accurate progress percentage
                if total_urls > 0:
                    enhanced_stats['progress_percent'] = (completed_count / total_urls) * 100
                
                # If scraper is running but no current URL from logs, try to get from sitemap
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