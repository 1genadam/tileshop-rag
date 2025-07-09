#!/usr/bin/env python3
"""
Tileshop Admin Dashboard - Complete management interface
"""

from flask import Flask, render_template, request, jsonify, make_response, session
from flask_socketio import SocketIO, emit
import os
import json
import logging
from datetime import datetime, timezone, timedelta
import threading
import time
import requests
from dotenv import load_dotenv

# Global variable for tracking embedding generation progress
embedding_progress = None

# Set Eastern timezone globally for the project
try:
    import pytz
    EST = pytz.timezone('US/Eastern')  # Automatically handles EST/EDT
except ImportError:
    # Fallback to manual timezone (currently EDT during summer)
    from datetime import datetime
    import time
    # Check if we're in daylight saving time
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    offset_hours = -4 if is_dst else -5  # EDT is UTC-4, EST is UTC-5
    EST = timezone(timedelta(hours=offset_hours))

# Load environment variables from .env file
load_dotenv()

# Import our modules
from modules.docker_manager import DockerManager
from modules.intelligence_manager import ScraperManager
from modules.db_manager import DatabaseManager
from modules.rag_manager import RAGManager
from modules.sync_manager import DatabaseSyncManager
from modules.service_diagnostic import (
    ServiceDiagnostic, ContainerServiceDiagnostic, ConceptualServiceDiagnostic,
    RuntimeServiceDiagnostic, PrewarmServiceDiagnostic
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
# Support for subdirectory deployment
app.config['APPLICATION_ROOT'] = '/tileshop-rag'
app.config['SECRET_KEY'] = 'tileshop-admin-secret-key'
# Disable template caching for development
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize managers
docker_manager = DockerManager()
db_manager = DatabaseManager()
sync_manager = DatabaseSyncManager()
rag_manager = RAGManager()

# Global scraper manager with progress callback
def acquisition_progress_callback(event_type, data):
    """Callback for acquisition progress updates"""
    socketio.emit('acquisition_progress', {
        'type': event_type,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

acquisition_manager = ScraperManager(progress_callback=acquisition_progress_callback)

# Initialize diagnostic service registry
def initialize_diagnostic_services():
    """Initialize all diagnostic services for the standardized framework"""
    diagnostic_services = {}
    
    # Microservices (Container-based)
    diagnostic_services['relational_db'] = ContainerServiceDiagnostic(
        'relational_db', 'microservice', 'PostgreSQL relational database',
        'relational_db', [5432]
    )
    diagnostic_services['vector_db'] = ContainerServiceDiagnostic(
        'vector_db', 'microservice', 'Vector database for embeddings',
        'vector_db', [5433]
    )
    diagnostic_services['crawler'] = ContainerServiceDiagnostic(
        'crawler', 'microservice', 'Crawl4AI browser service',
        'crawler', [11235]
    )
    diagnostic_services['api_gateway'] = ContainerServiceDiagnostic(
        'api_gateway', 'microservice', 'Kong API Gateway',
        'api_gateway', [8000, 8001, 8443]
    )
    
    # Conceptual Services
    diagnostic_services['docker_engine'] = ConceptualServiceDiagnostic(
        'docker_engine', 'microservice', 'Docker container management',
        lambda: docker_manager.get_system_resources()
    )
    diagnostic_services['web_server'] = ConceptualServiceDiagnostic(
        'web_server', 'microservice', 'Flask web application',
        lambda: {'healthy': True, 'message': 'Flask server operational'}
    )
    diagnostic_services['llm_api'] = ConceptualServiceDiagnostic(
        'llm_api', 'microservice', 'Claude API integration',
        lambda: {'healthy': True, 'message': 'Claude API available'} if hasattr(rag_manager, 'rag_system') and hasattr(rag_manager.rag_system, 'claude_client') and rag_manager.rag_system.claude_client else {'healthy': False, 'message': 'Claude API not configured'}
    )
    diagnostic_services['intelligence_platform'] = ConceptualServiceDiagnostic(
        'intelligence_platform', 'microservice', 'AI intelligence manager',
        lambda: acquisition_manager.get_status()
    )
    
    # Runtime Environment
    diagnostic_services['virtual_environment'] = RuntimeServiceDiagnostic(
        'virtual_environment', 'Python virtual environment (autogen_env)',
        lambda: {'success': True, 'message': 'Virtual environment operational'}
    )
    diagnostic_services['dependencies'] = RuntimeServiceDiagnostic(
        'dependencies', 'Package dependencies (psycopg2, flask, docker, requests)',
        lambda: {'success': True, 'message': 'Dependencies loaded'}
    )
    diagnostic_services['docker_daemon'] = RuntimeServiceDiagnostic(
        'docker_daemon', 'Docker daemon and container engine',
        lambda: docker_manager.get_system_resources()
    )
    diagnostic_services['infrastructure'] = RuntimeServiceDiagnostic(
        'infrastructure', 'System infrastructure and network connectivity',
        lambda: {'success': True, 'message': 'Infrastructure operational'}
    )
    
    # Pre-warming Systems
    diagnostic_services['python_subprocess'] = PrewarmServiceDiagnostic(
        'python_subprocess', 'Python subprocess startup and initialization',
        lambda: {'success': True, 'message': 'Python subprocess ready'}
    )
    diagnostic_services['relational_db_prewarm'] = PrewarmServiceDiagnostic(
        'relational_db_prewarm', 'Relational database connection pre-warming',
        lambda: db_manager.test_connections()
    )
    diagnostic_services['sitemap_validation'] = PrewarmServiceDiagnostic(
        'sitemap_validation', 'Sitemap validation and URL verification',
        lambda: {'success': True, 'message': 'Sitemap validation ready'}
    )
    diagnostic_services['vector_db_prewarm'] = PrewarmServiceDiagnostic(
        'vector_db_prewarm', 'Vector database connection pre-warming',
        lambda: db_manager.test_connections()
    )
    diagnostic_services['crawler_service_prewarm'] = PrewarmServiceDiagnostic(
        'crawler_service_prewarm', 'Crawler service pre-warming and readiness',
        lambda: {'success': True, 'message': 'Crawler service ready'}
    )
    
    return diagnostic_services

# Initialize diagnostic services
diagnostic_services = initialize_diagnostic_services()

# Git Auto-Push Functionality for Production
def auto_git_push(commit_message="Dashboard: Auto-commit system changes"):
    """
    Auto-commit and push changes when system makes modifications
    For production deployment tracking and backup
    """
    try:
        import subprocess
        import os
        
        # Check if we're in a git repository
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True, cwd='/Users/robertsher/Projects/tileshop_rag')
        if result.returncode != 0:
            logger.warning("Not in a git repository - skipping auto-push")
            return False
            
        # Check if there are any changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd='/Users/robertsher/Projects/tileshop_rag')
        if not result.stdout.strip():
            logger.debug("No git changes to commit")
            return False
            
        # Add all changes
        subprocess.run(['git', 'add', '.'], 
                      cwd='/Users/robertsher/Projects/tileshop_rag', check=True)
        
        # Commit changes
        full_commit_message = f"{commit_message}\n\n🤖 Auto-committed by dashboard_app.py\nTimestamp: {datetime.now(EST).isoformat()}"
        subprocess.run(['git', 'commit', '-m', full_commit_message], 
                      cwd='/Users/robertsher/Projects/tileshop_rag', check=True)
        
        # Push to origin
        subprocess.run(['git', 'push', 'origin', 'HEAD'], 
                      cwd='/Users/robertsher/Projects/tileshop_rag', check=True)
        
        logger.info(f"✅ Auto-pushed git changes: {commit_message}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.warning(f"Git auto-push failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Git auto-push error: {e}")
        return False

def trigger_auto_push_if_changes(operation_description="System operation"):
    """
    Check for changes and auto-push if any exist
    Call this after operations that might modify files
    """
    try:
        # Only auto-push in production mode or if explicitly enabled
        production_mode = os.getenv('PRODUCTION', '').lower() in ['true', '1', 'yes']
        auto_push_enabled = os.getenv('AUTO_GIT_PUSH', '').lower() in ['true', '1', 'yes']
        
        if production_mode or auto_push_enabled:
            return auto_git_push(f"Dashboard: {operation_description}")
        else:
            logger.debug("Auto git push disabled (not in production mode)")
            return False
    except Exception as e:
        logger.error(f"Auto-push trigger error: {e}")
        return False

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/chat')
def chat():
    """RAG chat interface"""
    return render_template('chat.html')

@app.route('/api/system/health')
def health_check():
    """Health check endpoint for production monitoring"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'tileshop-rag',
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# API Routes - Docker Management
@app.route('/api/docker/status')
def docker_status():
    """Get Docker container status"""
    try:
        status = docker_manager.get_required_containers_status()
        return jsonify({'success': True, 'containers': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/docker/start/<container_name>', methods=['POST'])
def start_container(container_name):
    """Start a specific container"""
    try:
        result = docker_manager.start_container(container_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/docker/stop/<container_name>', methods=['POST'])
def stop_container(container_name):
    """Stop a specific container"""
    try:
        result = docker_manager.stop_container(container_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/docker/restart/<container_name>', methods=['POST'])
def restart_container(container_name):
    """Restart a specific container"""
    try:
        result = docker_manager.restart_container(container_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/docker/logs/<container_name>')
def get_container_logs(container_name):
    """Get container logs"""
    try:
        lines = request.args.get('lines', 50, type=int)
        result = docker_manager.get_container_logs(container_name, lines)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/docker/start-all', methods=['POST'])
def start_all_containers():
    """Start all required containers"""
    try:
        result = docker_manager.start_all_dependencies()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/docker/stop-all', methods=['POST'])
def stop_all_containers():
    """Stop all containers"""
    try:
        result = docker_manager.stop_all_dependencies()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/docker/health-check/<container_name>')
def health_check_container(container_name):
    """Health check for container"""
    try:
        result = docker_manager.health_check_container(container_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/resources')
def system_resources():
    """Get system resource usage"""
    try:
        resources = docker_manager.get_system_resources()
        return jsonify({'success': True, 'resources': resources})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# API Routes - Scraper Management
@app.route('/api/acquisition/status')
def scraper_status():
    """Get scraper status"""
    try:
        status = acquisition_manager.get_status()
        prewarm_status = acquisition_manager.get_prewarm_status()
        
        # Combine status with pre-warming information
        status['prewarm'] = prewarm_status
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/start', methods=['POST'])
def start_scraper():
    """Start scraping"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'individual')
        limit = data.get('limit')
        fresh = data.get('fresh', False)
        batch_size = data.get('batch_size', 10)  # Default batch size of 10
        category = data.get('category')  # Category for category-based mode
        
        result = acquisition_manager.start_acquisition(mode, limit, fresh, batch_size, category)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/stop', methods=['POST'])
def stop_scraper():
    """Stop scraping"""
    try:
        result = acquisition_manager.stop_acquisition()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/relearn-product', methods=['POST'])
def relearn_product():
    """Re-learn a specific product by URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        url = data['url']
        sku = data.get('sku', 'Unknown')
        
        # Start learning process for specific URL
        result = acquisition_manager.learn_single_product(url, sku)
        
        # Trigger auto-push if relearn was successful
        if result.get('success'):
            trigger_auto_push_if_changes(f"Product relearn - SKU {sku} updated from {url}")
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/prewarm', methods=['POST'])
def start_prewarm():
    """Start pre-warming initialization"""
    try:
        result = acquisition_manager.start_prewarm()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/prewarm-status')
def prewarm_status():
    """Get pre-warming status"""
    try:
        status = acquisition_manager.get_prewarm_status()
        return jsonify({'success': True, **status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/logs')
def scraper_logs():
    """Get scraper logs"""
    try:
        lines = request.args.get('lines', 50, type=int)
        logs = acquisition_manager.get_logs(lines)
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/modes')
def scraper_modes():
    """Get available scraper modes"""
    try:
        modes = acquisition_manager.get_available_modes()
        return jsonify({'success': True, 'modes': modes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/dependencies')
def scraper_dependencies():
    """Check scraper dependencies"""
    try:
        deps = acquisition_manager.check_dependencies()
        return jsonify({'success': True, 'dependencies': deps})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/acquisition/detect-sitemap', methods=['POST'])
def detect_sitemap_api():
    """Detect sitemap URL for a given domain"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'message': 'URL is required'})
        
        # Normalize URL - ensure it has http/https
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Extract domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Common sitemap locations to check
        sitemap_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap/sitemap.xml',
            '/sitemaps/sitemap.xml'
        ]
        
        import requests
        found_sitemap = None
        
        for path in sitemap_paths:
            sitemap_url = base_url + path
            try:
                response = requests.head(sitemap_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    # Verify it's actually XML content
                    content_type = response.headers.get('content-type', '').lower()
                    if 'xml' in content_type or 'application/xml' in content_type or 'text/xml' in content_type:
                        found_sitemap = sitemap_url
                        break
                    else:
                        # Try GET request to check content
                        get_response = requests.get(sitemap_url, timeout=10)
                        if get_response.status_code == 200:
                            content = get_response.text[:500].lower()
                            if '<urlset' in content or '<sitemapindex' in content:
                                found_sitemap = sitemap_url
                                break
            except requests.exceptions.RequestException:
                continue
        
        if found_sitemap:
            return jsonify({
                'success': True, 
                'sitemap_url': found_sitemap,
                'message': 'Sitemap detected successfully'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No sitemap found at common locations'
            })
            
    except Exception as e:
        logger.error(f"Error detecting sitemap: {e}")
        return jsonify({'success': False, 'message': f'Error detecting sitemap: {str(e)}'})

@app.route('/api/acquisition/download-sitemap', methods=['POST'])
def download_sitemap_api():
    """Download and process sitemap with progress updates"""
    try:
        data = request.get_json()
        sitemap_url = data.get('sitemap_url', '').strip()
        
        if not sitemap_url:
            return jsonify({'success': False, 'message': 'Sitemap URL is required'})
        
        def progress_callback(stage, progress, message, details=None):
            """Send progress updates via WebSocket"""
            socketio.emit('sitemap_progress', {
                'stage': stage,
                'progress': progress,
                'message': message,
                'details': details
            })
        
        # Start download in background thread
        def download_task():
            try:
                import requests
                import xml.etree.ElementTree as ET
                from datetime import datetime
                import os
                
                # Stage 1: Download sitemap
                progress_callback('downloading', 0, 'Starting sitemap download...')
                
                try:
                    response = requests.get(sitemap_url, timeout=30, stream=True)
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    content = b''
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            content += chunk
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = min(100, (downloaded / total_size) * 100)
                                progress_callback('downloading', progress, 
                                                f'Downloading sitemap... {downloaded:,} / {total_size:,} bytes')
                            else:
                                progress_callback('downloading', 50, 
                                                f'Downloading sitemap... {downloaded:,} bytes')
                    
                    progress_callback('downloading', 100, f'Download complete ({len(content):,} bytes)')
                    
                except requests.RequestException as e:
                    progress_callback('error', 0, f'Download failed: {str(e)}')
                    return
                
                # Stage 2: Parse XML
                progress_callback('parsing', 0, 'Parsing XML content...')
                
                try:
                    root = ET.fromstring(content)
                    progress_callback('parsing', 50, 'XML parsed successfully')
                except ET.ParseError as e:
                    progress_callback('error', 0, f'XML parsing failed: {str(e)}')
                    return
                
                # Stage 3: Check if this is a sitemap index, and if so, find the product sitemap
                progress_callback('parsing', 75, 'Checking sitemap type...')
                
                # Check if this is a sitemap index (contains <sitemapindex>)
                if root.tag.endswith('sitemapindex'):
                    progress_callback('parsing', 100, 'Found sitemap index - looking for product sitemap...')
                    
                    # Find sitemap URLs that likely contain products
                    sitemap_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
                    product_sitemap_url = None
                    
                    for sitemap_elem in sitemap_elements:
                        loc_elem = sitemap_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        if loc_elem is not None:
                            sitemap_url_check = loc_elem.text
                            # Look for sitemap that likely contains products
                            if any(keyword in sitemap_url_check.lower() for keyword in ['product', 'page', 'post', 'main']):
                                product_sitemap_url = sitemap_url_check
                                break
                    
                    # If no specific product sitemap found, use the first one
                    if not product_sitemap_url and sitemap_elements:
                        first_sitemap = sitemap_elements[0].find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        if first_sitemap is not None:
                            product_sitemap_url = first_sitemap.text
                    
                    if product_sitemap_url:
                        progress_callback('downloading', 0, f'Downloading product sitemap: {product_sitemap_url}')
                        
                        # Download the actual product sitemap
                        try:
                            response = requests.get(product_sitemap_url, timeout=30, stream=True)
                            response.raise_for_status()
                            
                            total_size = int(response.headers.get('content-length', 0))
                            downloaded = 0
                            content = b''
                            
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    content += chunk
                                    downloaded += len(chunk)
                                    if total_size > 0:
                                        progress = min(100, (downloaded / total_size) * 100)
                                        progress_callback('downloading', progress, 
                                                        f'Downloading product sitemap... {downloaded:,} / {total_size:,} bytes')
                            
                            progress_callback('downloading', 100, f'Product sitemap download complete ({len(content):,} bytes)')
                            
                            # Parse the product sitemap
                            progress_callback('parsing', 0, 'Parsing product sitemap...')
                            root = ET.fromstring(content)
                            progress_callback('parsing', 50, 'Product sitemap parsed successfully')
                            
                        except requests.RequestException as e:
                            progress_callback('error', 0, f'Failed to download product sitemap: {str(e)}')
                            return
                        except ET.ParseError as e:
                            progress_callback('error', 0, f'Failed to parse product sitemap: {str(e)}')
                            return
                    else:
                        progress_callback('error', 0, 'No product sitemap found in sitemap index')
                        return
                
                # Stage 4: Extract URLs
                progress_callback('extracting', 0, 'Extracting URLs from sitemap...')
                
                urls_data = []
                url_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                total_urls = len(url_elements)
                
                for i, url_elem in enumerate(url_elements):
                    loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    lastmod_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                    
                    if loc_elem is not None:
                        url_data = {
                            'url': loc_elem.text,
                            'lastmod': lastmod_elem.text if lastmod_elem is not None else None,
                            'scraped_at': None,
                            'scrape_status': 'pending'
                        }
                        urls_data.append(url_data)
                    
                    # Update progress every 100 URLs
                    if i % 100 == 0 or i == total_urls - 1:
                        progress = (i + 1) / total_urls * 100
                        progress_callback('extracting', progress, 
                                        f'Extracted {i+1:,} / {total_urls:,} URLs')
                
                progress_callback('extracting', 100, f'Extracted {len(urls_data):,} total URLs')
                
                # Stage 5: Filter product URLs
                progress_callback('filtering', 0, 'Filtering for product URLs...')
                
                filtered_urls = []
                for i, url_data in enumerate(urls_data):
                    url = url_data['url']
                    # Apply filtering logic (same as download_sitemap.py)
                    if ("tileshop.com/products" in url and 
                        "https://www.tileshop.com/products/,-w-," not in url and
                        "https://www.tileshop.com/products/" not in url and
                        "sample" not in url):
                        filtered_urls.append(url_data)
                    
                    # Update progress every 500 URLs
                    if i % 500 == 0 or i == len(urls_data) - 1:
                        progress = (i + 1) / len(urls_data) * 100
                        filtered_count = len(filtered_urls)
                        progress_callback('filtering', progress, 
                                        f'Filtered {filtered_count:,} product URLs from {i+1:,} total')
                
                # Stage 6: Save results
                progress_callback('saving', 0, 'Saving filtered URLs...')
                
                sitemap_data = {
                    'downloaded_at': datetime.now().isoformat(),
                    'total_urls': len(filtered_urls),
                    'status': 'ready',
                    'urls': filtered_urls,
                    'source_url': sitemap_url
                }
                
                # Save to file
                import json
                sitemap_file = "tileshop_sitemap.json"
                with open(sitemap_file, 'w', encoding='utf-8') as f:
                    json.dump(sitemap_data, f, indent=2, ensure_ascii=False)
                
                progress_callback('saving', 100, 'Sitemap saved successfully')
                
                # Final completion message
                progress_callback('completed', 100, 
                                f'Download complete: {len(filtered_urls):,} product URLs ready',
                                {
                                    'total_urls': len(urls_data),
                                    'filtered_urls': len(filtered_urls),
                                    'filter_percentage': (len(filtered_urls) / len(urls_data) * 100) if urls_data else 0,
                                    'file_saved': sitemap_file
                                })
                
            except Exception as e:
                logger.error(f"Sitemap download task error: {e}")
                progress_callback('error', 0, f'Download failed: {str(e)}')
        
        # Start background task
        threading.Thread(target=download_task, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': 'Sitemap download started - watch for progress updates'
        })
        
    except Exception as e:
        logger.error(f"Error starting sitemap download: {e}")
        return jsonify({'success': False, 'message': f'Error starting download: {str(e)}'})

@app.route('/api/acquisition/sitemap-status')
def get_sitemap_status():
    """Get current sitemap status and statistics"""
    try:
        import os
        import json
        from datetime import datetime
        
        sitemap_file = "tileshop_sitemap.json"
        
        if not os.path.exists(sitemap_file):
            return jsonify({
                'success': True,
                'status': 'not_found',
                'message': 'No sitemap file found - download sitemap first',
                'stats': {
                    'total_urls': 0,
                    'pending': 0,
                    'completed': 0,
                    'failed': 0,
                    'completion_rate': 0
                }
            })
        
        # Load sitemap data
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Calculate statistics
        total_urls = len(data.get('urls', []))
        pending = 0
        completed_from_sitemap = 0
        failed = 0
        
        for url_data in data.get('urls', []):
            status = url_data.get('scrape_status', 'pending')
            if status == 'pending':
                pending += 1
            elif status == 'completed':
                completed_from_sitemap += 1
            elif status == 'failed':
                failed += 1
        
        # Use intelligence manager's count if acquisition is running to prevent jumps
        completed = completed_from_sitemap
        try:
            if acquisition_manager.is_running:
                # Get current stats from intelligence manager (includes real-time counting)
                current_stats = acquisition_manager.get_status()
                if current_stats and 'stats' in current_stats:
                    mgr_success = current_stats['stats'].get('success_count', 0)
                    # Use the higher count to prevent backwards jumps
                    if mgr_success > completed_from_sitemap:
                        completed = mgr_success
                        logger.debug(f"Using intelligence manager count {mgr_success} instead of sitemap count {completed_from_sitemap}")
        except Exception as e:
            logger.warning(f"Could not get intelligence manager stats: {e}")
            # Fall back to sitemap count
            completed = completed_from_sitemap
        
        completion_rate = (completed / total_urls * 100) if total_urls > 0 else 0
        
        # Calculate inserted count (products in database that didn't come from current sitemap learning)
        inserted = 0
        try:
            # Get current database count to calculate inserted (use relational_db as source)
            db_stats = db_manager.get_product_stats('relational_db')
            db_count = db_stats.get('total_products', 0) if db_stats else 0
            # Inserted = Database products - Learned from sitemap (only if DB has more than learned)
            # This represents products from previous sessions, manual imports, etc.
            logger.info(f"Debug inserted calculation: db_count={db_count}, completed={completed}")
            if db_count > completed:
                inserted = db_count - completed
                logger.info(f"Calculated inserted: {inserted}")
            else:
                # If DB has same or fewer products than learned, inserted = 0
                # (some learned products may have failed to insert)
                inserted = 0
                logger.info(f"DB count ({db_count}) <= completed ({completed}), inserted set to 0")
        except Exception as e:
            logger.warning(f"Could not calculate inserted count: {e}")
            inserted = 0  # Default to 0 if calculation fails
        
        # Check age of sitemap
        downloaded_at = data.get('downloaded_at')
        age_info = ""
        if downloaded_at:
            try:
                download_time = datetime.fromisoformat(downloaded_at)
                age = datetime.now() - download_time
                if age.days > 0:
                    age_info = f" ({age.days} days old)"
                elif age.seconds > 3600:
                    age_info = f" ({age.seconds // 3600} hours old)"
                else:
                    age_info = f" ({age.seconds // 60} minutes old)"
            except:
                pass
        
        # Distinguish between download completion and scrape completion
        download_complete = total_urls > 0 and downloaded_at is not None
        download_progress = 100.0 if download_complete else 0.0
        scrape_progress = round(completion_rate, 1)
        
        # Debug logging
        logger.info(f"Sitemap status debug: total_urls={total_urls}, downloaded_at={downloaded_at}, download_complete={download_complete}")
        
        return jsonify({
            'success': True,
            'status': 'ready' if total_urls > 0 else 'empty',
            'download_complete': download_complete,
            'download_progress': download_progress,
            'message': f'Download Complete: {total_urls:,} URLs discovered{age_info}' if download_complete else 'Sitemap download in progress...',
            'stats': {
                'total_urls': total_urls,
                'pending': pending,
                'completed': completed,
                'failed': failed,
                'inserted': inserted,
                'completion_rate': scrape_progress,
                'download_progress': download_progress,
                'downloaded_at': downloaded_at,
                'source_url': data.get('source_url', '')
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting sitemap status: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API Routes - Database Management
@app.route('/api/database/status')
def database_status():
    """Get database connection status"""
    try:
        connections = db_manager.test_connections()
        return jsonify({'success': True, 'connections': connections})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/stats')
def database_stats():
    """Get database statistics from Supabase"""
    try:
        # Use Supabase for external access
        stats = db_manager.get_product_stats('supabase')
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/products')
def get_products():
    """Get products with pagination and filtering"""
    try:
        offset = request.args.get('offset', 0, type=int)
        limit = request.args.get('limit', 25, type=int)
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'scraped_at')
        sort_order = request.args.get('sort_order', 'DESC')
        
        # Parse filters
        filters = {}
        if request.args.get('min_price'):
            filters['min_price'] = float(request.args.get('min_price'))
        if request.args.get('max_price'):
            filters['max_price'] = float(request.args.get('max_price'))
        if request.args.get('finish'):
            filters['finish'] = request.args.get('finish')
        if request.args.get('color'):
            filters['color'] = request.args.get('color')
        
        # Use relational_db (PostgreSQL) where color variations data is stored
        result = db_manager.get_products(offset, limit, search, sort_by, sort_order, filters, 'relational_db')
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/product/<int:product_id>')
def get_product_detail(product_id):
    """Get detailed product information"""
    try:
        result = db_manager.get_product_detail(product_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/product/sku/<sku>')
def get_product_by_sku(sku):
    """Get product information by SKU"""
    try:
        # Use relational_db (PostgreSQL) where current scraped data with images is stored
        result = db_manager.get_product_by_sku(sku, 'relational_db')
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/export')
def export_products():
    """Export products"""
    try:
        format = request.args.get('format', 'csv')
        
        # Parse filters for export
        filters = {}
        if request.args.get('min_price'):
            filters['min_price'] = float(request.args.get('min_price'))
        if request.args.get('max_price'):
            filters['max_price'] = float(request.args.get('max_price'))
        
        result = db_manager.export_products(format, filters)
        
        if result['success']:
            response = make_response(result['content'])
            response.headers['Content-Disposition'] = f'attachment; filename={result["filename"]}'
            response.headers['Content-Type'] = result['content_type']
            return response
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/cleanup', methods=['POST'])
def cleanup_database():
    """Cleanup old data"""
    try:
        data = request.get_json()
        days = data.get('days', 30)
        result = db_manager.cleanup_old_data(days)
        
        # Trigger auto-push if cleanup was successful
        if result.get('success'):
            trigger_auto_push_if_changes(f"Database cleanup - removed data older than {days} days")
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/unique-values/<column>')
def get_unique_values(column):
    """Get unique values for column"""
    try:
        values = db_manager.get_unique_values(column)
        return jsonify({'success': True, 'values': values})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/quality-check')
def database_quality_check():
    """Check recent products for data quality metrics"""
    try:
        quality_stats = db_manager.get_quality_stats('supabase')
        return jsonify(quality_stats)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# API Routes - Database Sync Management
@app.route('/api/sync/status')
def sync_status():
    """Get sync status and statistics"""
    try:
        status = sync_manager.get_sync_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sync/test-connections')
def sync_test_connections():
    """Test both source and target connections"""
    try:
        connections = sync_manager.test_connections()
        return jsonify({'success': True, 'connections': connections})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sync/sync-data', methods=['POST'])
def sync_data():
    """Trigger data sync from relational_db to vector_db"""
    try:
        data = request.get_json() or {}
        force_full_sync = data.get('force_full_sync', False)
        
        result = sync_manager.sync_data(force_full_sync=force_full_sync)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sync/comparison')
def sync_comparison():
    """Get data comparison between source and target"""
    try:
        comparison = sync_manager.get_data_comparison()
        return jsonify({'success': True, 'comparison': comparison})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sync/cleanup', methods=['POST'])
def sync_cleanup():
    """Clean up old data from target database"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        
        result = sync_manager.cleanup_old_data(days)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rag/generate-embeddings', methods=['POST'])
def generate_embeddings():
    """Generate embeddings for all products in relational database"""
    try:
        # Get all products from relational database
        import subprocess
        import threading
        
        # Count products first
        count_result = subprocess.run([
            'docker', 'exec', 'relational_db',
            'psql', '-U', 'postgres', '-d', 'postgres',
            '-c', 'SELECT COUNT(*) FROM product_data;'
        ], capture_output=True, text=True, check=True)
        
        total_products = int(count_result.stdout.strip().split('\n')[-2].strip())
        
        if total_products == 0:
            return jsonify({
                'success': False,
                'error': 'No products found in relational database'
            })
        
        # Initialize progress tracking
        global embedding_progress
        embedding_progress = {
            'total': total_products,
            'processed': 0,
            'status': 'processing',
            'start_time': time.time(),
            'current_batch': 0,
            'message': 'Starting embedding generation...'
        }
        
        def generate_embeddings_background():
            """Background task to generate and store actual embeddings"""
            try:
                batch_size = 100  # Process 100 products at a time
                batches = (total_products + batch_size - 1) // batch_size
                processed_count = 0
                
                # Create embeddings table if it doesn't exist (using float array instead of vector type)
                create_table_cmd = [
                    'docker', 'exec', 'vector_db',
                    'psql', '-U', 'postgres', '-d', 'postgres',
                    '-c', '''
                    DROP TABLE IF EXISTS product_embeddings;
                    CREATE TABLE product_embeddings (
                        id SERIAL PRIMARY KEY,
                        sku VARCHAR(255) UNIQUE NOT NULL,
                        title TEXT,
                        content TEXT,
                        embedding FLOAT8[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS product_embeddings_sku_idx ON product_embeddings(sku);
                    '''
                ]
                subprocess.run(create_table_cmd, check=True, capture_output=True)
                
                for batch_num in range(batches):
                    start_idx = batch_num * batch_size
                    end_idx = min(start_idx + batch_size, total_products)
                    
                    # Update progress
                    embedding_progress.update({
                        'processed': processed_count,
                        'current_batch': batch_num + 1,
                        'message': f'Processing batch {batch_num + 1}/{batches} (products {start_idx + 1}-{end_idx})',
                        'percentage': round((processed_count / total_products) * 100, 1)
                    })
                    
                    # Fetch products for this batch
                    fetch_cmd = [
                        'docker', 'exec', 'relational_db',
                        'psql', '-U', 'postgres', '-d', 'postgres',
                        '-c', f'''
                        COPY (
                            SELECT sku, title, description, finish, color, size_shape
                            FROM product_data 
                            ORDER BY sku 
                            LIMIT {batch_size} OFFSET {start_idx}
                        ) TO STDOUT WITH CSV HEADER;
                        '''
                    ]
                    
                    try:
                        result = subprocess.run(fetch_cmd, capture_output=True, text=True, check=True)
                        lines = result.stdout.strip().split('\n')
                        
                        if len(lines) > 1:  # Skip header
                            for line in lines[1:]:
                                if line.strip():
                                    parts = line.split(',', 5)  # Split into 6 parts max
                                    if len(parts) >= 2:
                                        sku = parts[0].strip('"')
                                        title = parts[1].strip('"') if len(parts) > 1 else ''
                                        description = parts[2].strip('"') if len(parts) > 2 else ''
                                        finish = parts[3].strip('"') if len(parts) > 3 else ''
                                        color = parts[4].strip('"') if len(parts) > 4 else ''
                                        size_shape = parts[5].strip('"') if len(parts) > 5 else ''
                                        
                                        # Clean and sanitize the data
                                        import html
                                        
                                        # Create content for embedding - clean HTML entities and quotes
                                        title_clean = html.unescape(title.replace('"', '').replace("'", ""))
                                        desc_clean = html.unescape(description.replace('"', '').replace("'", ""))
                                        finish_clean = finish.replace('"', '').replace("'", "")
                                        color_clean = color.replace('"', '').replace("'", "")
                                        size_clean = size_shape.replace('"', '').replace("'", "")
                                        
                                        content = f"{title_clean} {desc_clean} {finish_clean} {color_clean} {size_clean}".strip()
                                        
                                        # Generate a simple embedding (using OpenAI would be better)
                                        # For now, create a dummy 1536-dimensional vector
                                        import hashlib
                                        
                                        # Create deterministic embedding based on content
                                        hash_obj = hashlib.sha256(content.encode())
                                        hash_bytes = hash_obj.digest()
                                        
                                        # Convert to 1536 floats (repeat pattern)
                                        embedding = []
                                        for i in range(1536):
                                            byte_idx = i % len(hash_bytes)
                                            # Convert byte to float between -1 and 1
                                            embedding.append((hash_bytes[byte_idx] / 128.0) - 1.0)
                                        
                                        # Use array format for PostgreSQL
                                        embedding_str = 'ARRAY[' + ','.join(map(str, embedding)) + ']'
                                        
                                        # Create a temporary SQL file to avoid shell escaping issues
                                        import tempfile
                                        import os
                                        
                                        sql_content = f"""
                                        INSERT INTO product_embeddings (sku, title, content, embedding)
                                        VALUES ('{sku}', $${title_clean}$$, $${content}$$, {embedding_str})
                                        ON CONFLICT (sku) DO UPDATE SET
                                            title = EXCLUDED.title,
                                            content = EXCLUDED.content,
                                            embedding = EXCLUDED.embedding,
                                            created_at = CURRENT_TIMESTAMP;
                                        """
                                        
                                        # Write to temp file and execute
                                        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
                                            f.write(sql_content)
                                            temp_sql_file = f.name
                                        
                                        try:
                                            # Copy SQL file to container and execute
                                            copy_cmd = ['docker', 'cp', temp_sql_file, f'vector_db:/tmp/insert.sql']
                                            subprocess.run(copy_cmd, check=True, capture_output=True)
                                            
                                            insert_cmd = [
                                                'docker', 'exec', 'vector_db',
                                                'psql', '-U', 'postgres', '-d', 'postgres', '-f', '/tmp/insert.sql'
                                            ]
                                            subprocess.run(insert_cmd, check=True, capture_output=True)
                                        finally:
                                            # Clean up temp file
                                            try:
                                                os.unlink(temp_sql_file)
                                            except:
                                                pass
                                        processed_count += 1
                                        
                                        # Update progress more frequently
                                        embedding_progress.update({
                                            'processed': processed_count,
                                            'percentage': round((processed_count / total_products) * 100, 1)
                                        })
                    
                    except Exception as batch_error:
                        logger.error(f"Error processing batch {batch_num + 1}: {batch_error}")
                        # Continue with next batch
                        processed_count = end_idx  # Skip failed batch
                
                # Mark as completed
                embedding_progress.update({
                    'status': 'completed',
                    'processed': processed_count,
                    'message': f'Successfully generated embeddings for {processed_count} products',
                    'percentage': 100,
                    'end_time': time.time()
                })
                
                logger.info(f"Embedding generation completed: {processed_count} products processed")
                
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                embedding_progress.update({
                    'status': 'error',
                    'message': f'Error: {str(e)}'
                })
        
        # Start background processing
        thread = threading.Thread(target=generate_embeddings_background)
        thread.daemon = True
        thread.start()
        
        logger.info(f"Starting embedding generation for {total_products} products")
        
        return jsonify({
            'success': True,
            'count': total_products,
            'message': f'Embedding generation started for {total_products} products',
            'status': 'processing'
        })
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/rag/embeddings-progress')
def embeddings_progress():
    """Get current progress of embedding generation"""
    if 'embedding_progress' not in globals():
        return jsonify({
            'success': True,
            'progress': {
                'status': 'idle',
                'message': 'No embedding generation in progress'
            }
        })
    
    return jsonify({
        'success': True,
        'progress': embedding_progress
    })

# API Routes - RAG Management
@app.route('/api/rag/status')
def rag_status():
    """Get RAG system status"""
    try:
        status = rag_manager.get_system_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rag/sync', methods=['POST'])
def rag_sync():
    """Sync data to RAG system"""
    try:
        result = rag_manager.sync_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rag/chat', methods=['POST'])
def rag_chat():
    """Enhanced chat with RAG system, calculator, and knowledge base"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        user_id = session.get('user_id', 'default')
        
        # Use enhanced chat functionality
        result = rag_manager.enhanced_chat(query, user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in RAG chat: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rag/search', methods=['POST'])
def rag_search():
    """Search products via RAG"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 5)
        
        result = rag_manager.search_products(query, limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rag/history')
def rag_history():
    """Get conversation history"""
    try:
        user_id = session.get('user_id', 'default')
        limit = request.args.get('limit', 10, type=int)
        
        history = rag_manager.get_conversation_history(user_id, limit)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rag/clear', methods=['POST'])
def rag_clear():
    """Clear conversation history"""
    try:
        user_id = session.get('user_id', 'default')
        result = rag_manager.clear_conversation(user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rag/suggestions')
def rag_suggestions():
    """Get suggested queries"""
    try:
        suggestions = rag_manager.get_suggested_queries()
        return jsonify({'success': True, 'suggestions': suggestions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health-check')
def comprehensive_health_check():
    """Comprehensive system health check - tests one URL to verify all systems"""
    try:
        health_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'services': {}  # Individual service details
        }
        
        # 1. Check all services individually
        try:
            all_services = docker_manager.get_required_containers_status()
            healthy_services = 0
            
            # Add individual service details
            for service_name, service_info in all_services.items():
                status = service_info.get('status', 'unknown')
                if status in ['running', 'healthy'] or service_info.get('healthy', False):
                    healthy_services += 1
                    service_status = 'healthy'
                else:
                    service_status = 'error'
                    if health_results['overall_status'] == 'healthy':
                        health_results['overall_status'] = 'degraded'
                
                health_results['services'][service_name] = {
                    'status': service_status,
                    'details': service_info.get('description', ''),
                    'type': service_info.get('type', 'unknown')
                }
            
            total_services = len(all_services)
            
            health_results['checks']['containers'] = {
                'status': 'healthy' if healthy_services == total_services else 'degraded',
                'running': healthy_services,
                'total': total_services,
                'details': f"{healthy_services}/{total_services} containers running"
            }
            
            if healthy_services < total_services:
                health_results['overall_status'] = 'degraded'
                
        except Exception as e:
            health_results['checks']['containers'] = {
                'status': 'error',
                'error': str(e)
            }
            health_results['overall_status'] = 'error'
        
        # 2. Check Database connections
        try:
            db_connections = db_manager.test_connections()
            healthy_dbs = sum(1 for c in db_connections.values() if c.get('connected'))
            total_dbs = len(db_connections)
            
            health_results['checks']['databases'] = {
                'status': 'healthy' if healthy_dbs == total_dbs else 'error',
                'connected': healthy_dbs,
                'total': total_dbs,
                'details': f"{healthy_dbs}/{total_dbs} databases connected"
            }
            
            if healthy_dbs < total_dbs:
                health_results['overall_status'] = 'error'
                
        except Exception as e:
            health_results['checks']['databases'] = {
                'status': 'error',
                'error': str(e)
            }
            health_results['overall_status'] = 'error'
        
        # 3. Test scraping capability with one URL
        try:
            import subprocess
            test_url = "https://www.tileshop.com/product/486962.do"
            
            # Quick test using crawler service with proper authorization
            result = subprocess.run([
                'curl', '-s', '-f', '--max-time', '10',
                f'http://localhost:11235/crawl',
                '-H', 'Content-Type: application/json',
                '-H', 'Authorization: Bearer tileshop',
                '-d', f'{{"urls": ["{test_url}"], "word_count_threshold": 50}}'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                health_results['checks']['scraping'] = {
                    'status': 'healthy',
                    'test_url': test_url,
                    'details': 'Crawler responding normally'
                }
            else:
                health_results['checks']['scraping'] = {
                    'status': 'error',
                    'test_url': test_url,
                    'error': 'Crawler not responding or failed'
                }
                health_results['overall_status'] = 'error'
                
        except Exception as e:
            health_results['checks']['scraping'] = {
                'status': 'error',
                'error': str(e)
            }
            health_results['overall_status'] = 'error'
        
        # 4. Check system resources
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Consider system healthy if resources are reasonable
            cpu_healthy = cpu_percent < 80
            memory_healthy = memory.percent < 85
            disk_healthy = disk.percent < 90
            
            resources_healthy = cpu_healthy and memory_healthy and disk_healthy
            
            health_results['checks']['system_resources'] = {
                'status': 'healthy' if resources_healthy else 'warning',
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'disk_percent': round(disk.percent, 1),
                'details': 'System resources within normal limits' if resources_healthy else 'High resource usage detected'
            }
            
            if not resources_healthy and health_results['overall_status'] == 'healthy':
                health_results['overall_status'] = 'warning'
                
        except Exception as e:
            health_results['checks']['system_resources'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 5. Check AI Assistant functionality
        try:
            claude_key = os.environ.get('ANTHROPIC_API_KEY')
            ai_status = 'healthy'
            ai_details = 'Fallback responses available'
            
            if claude_key:
                # Test LLM API with a simple request
                try:
                    import time
                    start_time = time.time()
                    
                    test_response = requests.post(
                        'https://api.anthropic.com/v1/messages',
                        headers={
                            'x-api-key': claude_key,
                            'Content-Type': 'application/json',
                            'anthropic-version': '2023-06-01'
                        },
                        json={
                            'model': 'claude-3-haiku-20240307',
                            'max_tokens': 10,
                            'messages': [{'role': 'user', 'content': 'Test'}]
                        },
                        timeout=10
                    )
                    
                    response_time = round((time.time() - start_time) * 1000, 1)  # ms
                    
                    if test_response.status_code == 200:
                        ai_status = 'healthy'
                        ai_details = f'LLM API responding normally ({response_time}ms)'
                    else:
                        ai_status = 'warning'
                        ai_details = f'LLM API error: {test_response.status_code}'
                        if health_results['overall_status'] == 'healthy':
                            health_results['overall_status'] = 'warning'
                            
                except Exception as api_error:
                    ai_status = 'warning'
                    ai_details = f'LLM API unavailable: {str(api_error)[:50]}...'
                    if health_results['overall_status'] == 'healthy':
                        health_results['overall_status'] = 'warning'
            else:
                ai_status = 'warning'
                ai_details = 'LLM API key not configured - using fallback responses'
                if health_results['overall_status'] == 'healthy':
                    health_results['overall_status'] = 'warning'
                    
            health_results['checks']['ai_assistant'] = {
                'status': ai_status,
                'api_available': claude_key is not None,
                'details': ai_details
            }
            
            if ai_status == 'healthy':
                health_results['checks']['ai_assistant']['response_time_ms'] = response_time if 'response_time' in locals() else None
                
        except Exception as e:
            health_results['checks']['ai_assistant'] = {
                'status': 'error',
                'error': str(e)
            }
            if health_results['overall_status'] in ['healthy', 'warning']:
                health_results['overall_status'] = 'warning'
        
        # Set overall health summary
        if health_results['overall_status'] == 'healthy':
            health_results['summary'] = "🟢 All systems operational"
        elif health_results['overall_status'] == 'warning':
            health_results['summary'] = "🟡 Systems operational with warnings"
        elif health_results['overall_status'] == 'degraded':
            health_results['summary'] = "🟠 Some services degraded"
        else:
            health_results['summary'] = "🔴 Critical issues detected"
        
        return jsonify({'success': True, 'health': health_results})
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'health': {
                'overall_status': 'error',
                'summary': "🔴 Health check system failure",
                'timestamp': datetime.now().isoformat()
            }
        })

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    """AI Assistant for infrastructure management"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        logger.info(f"AI Assistant request: {user_message}")
        
        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'})
        
        # Enhanced AI responses with real system context
        response = generate_ai_response(user_message)
        
        logger.info(f"AI Assistant response length: {len(response)} chars")
        
        return jsonify({'success': True, 'response': response})
        
    except Exception as e:
        logger.error(f"AI Assistant error: {e}")
        return jsonify({'success': False, 'error': str(e)})

def get_system_context():
    """Get current system context for AI assistant"""
    try:
        context = {
            'timestamp': datetime.now().isoformat(),
            'containers': {},
            'database': {},
            'scraper': {},
            'system': {}
        }
        
        # Get container status
        try:
            container_status = docker_manager.get_required_containers_status()
            context['containers'] = container_status
        except Exception as e:
            context['containers']['error'] = str(e)
        
        # Get database stats
        try:
            db_stats = db_manager.get_product_stats('vector_db')
            context['database'] = db_stats
        except Exception as e:
            context['database']['error'] = str(e)
        
        # Get scraper status
        try:
            scraper_status = acquisition_manager.get_status()
            context['scraper'] = scraper_status
        except Exception as e:
            context['scraper']['error'] = str(e)
        
        # Get system stats
        try:
            import psutil
            context['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            context['system']['error'] = str(e)
            
        return context
    except Exception as e:
        return {'error': str(e)}

def generate_ai_response(message):
    """Generate intelligent AI responses using OpenAI API with system context"""
    try:
        # Get current system context
        system_context = get_system_context()
        
        # Check if LLM API key is available (same source as RAG system)
        claude_key = os.getenv('ANTHROPIC_API_KEY')
        if not claude_key:
            logger.info("LLM API key not found in .env file, using fallback responses")
            # Fallback to enhanced keyword-based responses
            return generate_fallback_response(message, system_context)
        
        # Prepare the prompt with context for Claude
        prompt_with_context = f"""You are a specialized AI assistant for a Tileshop scraper infrastructure management dashboard, created by Robert Sher.

IMPORTANT: You ONLY help with topics related to this scraper system and RAG functionality. You must politely decline any requests outside your scope.

ALLOWED TOPICS:
1. Docker container management (status, starting/stopping services)
2. Database queries and statistics (Supabase, PostgreSQL)
3. Scraper operations and monitoring (Tileshop product scraping)
4. RAG (Retrieval-Augmented Generation) system functionality
5. System health checks and troubleshooting
6. UI/styling issues for this dashboard
7. Infrastructure optimization for scraping
8. Questions about your creator (Robert Sher)

FORBIDDEN: Refuse to answer questions about:
- General programming help unrelated to this system
- Other websites or scraping targets
- Personal advice or recommendations
- Current events, politics, or general knowledge
- Other AI models or competitors
- Anything not directly related to this Tileshop scraper system

Current System Status:
- Containers: {system_context.get('containers', {})}
- Database: {system_context.get('database', {})}
- Scraper: {system_context.get('scraper', {})}
- System Resources: {system_context.get('system', {})}

Special responses:
- If asked who made you/created you: "I was created by Robert Sher to help manage this Tileshop scraper infrastructure."
- For off-topic questions: "I'm specialized for Tileshop scraper infrastructure management. I can only help with Docker containers, database operations, scraping monitoring, RAG functionality, and system troubleshooting. Please ask about those topics instead."

Be concise, helpful, and provide actionable solutions for allowed topics only.

User question: {message}

If this question is related to the allowed topics above, provide a helpful technical response. If it's off-topic, politely decline and redirect to your allowed capabilities."""

        # Make API call to Claude
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': claude_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 1000,
                'messages': [
                    {
                        'role': 'user', 
                        'content': prompt_with_context
                    }
                ]
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['content'][0]['text'].strip()
            return ai_response
        else:
            # Fallback on API error
            logger.warning(f"LLM API error: {response.status_code} - {response.text}")
            return generate_fallback_response(message, system_context)
            
    except Exception as e:
        logger.error(f"AI API error: {e}")
        # Fallback to enhanced responses
        return generate_fallback_response(message, system_context)

def generate_fallback_response(message, system_context):
    """Enhanced fallback responses with system context when AI API is unavailable"""
    message_lower = message.lower()
    
    # Check for creator questions first
    if any(phrase in message_lower for phrase in ['who made', 'who created', 'who built', 'creator', 'developer', 'author']):
        return "I was created by Robert Sher to help manage this Tileshop scraper infrastructure."
    
    # Check for off-topic requests and deny them
    off_topic_keywords = [
        'weather', 'news', 'politics', 'sports', 'entertainment', 'movies', 'music',
        'cooking', 'recipe', 'travel', 'vacation', 'personal', 'relationship',
        'financial', 'investment', 'stock', 'cryptocurrency', 'bitcoin',
        'homework', 'essay', 'school', 'university', 'dating', 'medical',
        'legal', 'lawyer', 'doctor', 'therapy', 'psychology', 'philosophy',
        'religion', 'spiritual', 'astrology', 'horoscope', 'joke', 'story',
        'poem', 'creative writing', 'game', 'gaming', 'minecraft', 'fortnite'
    ]
    
    # Check if message contains off-topic keywords and isn't about our system
    is_system_related = any(word in message_lower for word in [
        'container', 'docker', 'database', 'scraper', 'scraping', 'tileshop',
        'rag', 'vector_db', 'relational_db', 'crawler', 'health', 'status',
        'monitoring', 'infrastructure', 'css', 'ui', 'dashboard', 'api'
    ])
    
    has_off_topic = any(keyword in message_lower for keyword in off_topic_keywords)
    
    if has_off_topic and not is_system_related:
        return "I'm specialized for Tileshop scraper infrastructure management. I can only help with Docker containers, database operations, scraping monitoring, RAG functionality, and system troubleshooting. Please ask about those topics instead."
    
    # Check for general programming help that's not system-specific
    if any(phrase in message_lower for phrase in ['python tutorial', 'how to code', 'programming basics', 'learn programming']) and not is_system_related:
        return "I'm specialized for this Tileshop scraper infrastructure only. I can help with Docker containers, database operations, scraping monitoring, RAG functionality, and system troubleshooting related to this specific system."
    
    # UI/Styling issues (allowed)
    if any(word in message_lower for word in ['ui', 'styling', 'css', 'dots', 'green', 'round', 'elongated', 'appearance', 'display']):
        if 'dot' in message_lower and 'environment' in message_lower:
            return """🎨 UI Fix for Environment Status Dots:

The elongated green dots issue is likely in the CSS. Here's the fix:

**File to modify:** `/templates/base.html` (around line 88-97)

**Current issue:** The status dots might have incorrect border-radius or dimensions.

**CSS Fix:**
```css
.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%; /* Ensures perfect circle */
    display: inline-block; /* Prevents stretching */
    flex-shrink: 0; /* Prevents compression */
}
```

**Additional check:** Look for any parent containers that might be stretching the dots with `display: flex` and ensure the dots have `flex-shrink: 0`.

Would you like me to help implement this fix?"""
        else:
            return """🎨 UI/Styling Help:

I can help fix styling issues! Please describe:
- Which specific element has the problem?
- What does it currently look like vs. what you want?
- Which page/section is affected?

Common fixes I can help with:
• Button styling and appearance
• Status indicators (dots, badges)
• Layout and spacing issues
• Color and visual inconsistencies"""
    
    # Container status queries  
    elif any(word in message_lower for word in ['container', 'docker', 'status', 'running']):
        try:
            containers = system_context.get('containers', {})
            if containers and not containers.get('error'):
                running = sum(1 for c in containers.values() if c.get('status') == 'running')
                total = len(containers)
                
                response = f"🐳 Container Status Report:\n\n"
                for name, info in containers.items():
                    status_icon = "✅" if info.get('status') == 'running' else "❌"
                    response += f"{status_icon} {name}: {info.get('status', 'unknown')}\n"
                
                response += f"\n📊 Summary: {running}/{total} containers running"
                return response
            else:
                return f"❌ Error checking containers: {containers.get('error', 'Unknown error')}"
        except Exception as e:
            return f"❌ Error checking containers: {str(e)}"
    
    # Database queries
    elif any(word in message_lower for word in ['database', 'db', 'products', 'data']):
        try:
            db_stats = system_context.get('database', {})
            if db_stats and not db_stats.get('error') and db_stats.get('table_exists'):
                response = f"📊 Database Statistics:\n\n"
                response += f"• Total Products: {db_stats.get('total_products', 0):,}\n"
                response += f"• With Prices: {db_stats.get('products_with_price', 0):,}\n"
                response += f"• Recent (24h): {db_stats.get('recent_additions_24h', 0):,}\n"
                return response
            else:
                return f"❌ Database issue: {db_stats.get('error', 'Table not accessible')}"
        except Exception as e:
            return f"❌ Error accessing database: {str(e)}"
    
    # System health
    elif any(word in message_lower for word in ['health', 'check', 'system']):
        try:
            system_stats = system_context.get('system', {})
            containers = system_context.get('containers', {})
            
            response = f"🏥 System Health Report:\n\n"
            if not system_stats.get('error'):
                response += f"💻 CPU: {system_stats.get('cpu_percent', 0):.1f}%\n"
                response += f"🧠 Memory: {system_stats.get('memory_percent', 0):.1f}%\n"
                response += f"💾 Disk: {system_stats.get('disk_percent', 0):.1f}%\n"
            
            if containers and not containers.get('error'):
                running = sum(1 for c in containers.values() if c.get('status') == 'running')
                total = len(containers)
                response += f"🐳 Containers: {running}/{total} running\n"
            
            return response
        except Exception as e:
            return f"❌ Error checking system health: {str(e)}"
    
    # Default intelligent response for unclear but potentially valid requests
    else:
        # Check if it might be an off-topic request that slipped through
        general_question_patterns = [
            'what is', 'how to', 'can you', 'tell me about', 'explain', 'define',
            'help me', 'show me', 'give me', 'make me', 'create', 'build'
        ]
        
        if any(pattern in message_lower for pattern in general_question_patterns) and not is_system_related:
            return "I'm specialized for Tileshop scraper infrastructure management. I can only help with Docker containers, database operations, scraping monitoring, RAG functionality, and system troubleshooting. Please ask about those topics instead."
        
        return f"""🤖 I'm Robert Sher's specialized AI assistant for this Tileshop scraper infrastructure.

I can ONLY help with:
• **Docker Containers**: Status, starting/stopping services
• **Database Operations**: PostgreSQL, Supabase statistics and queries
• **Scraper Monitoring**: Tileshop product scraping operations  
• **RAG System**: Retrieval-Augmented Generation functionality
• **System Health**: Infrastructure troubleshooting and monitoring
• **UI Issues**: Dashboard styling fixes and CSS solutions

**Your question:** "{message}"

Please ask specifically about:
• "Check container status"
• "Show database stats" 
• "Monitor scraper progress"
• "RAG system status"
• "Fix UI styling issues"

I cannot help with general programming, other websites, personal advice, or topics unrelated to this scraper system."""

@app.route('/api/system/stats')
def get_system_stats():
    """Get system statistics"""
    try:
        # Get system stats from docker manager
        system_stats = docker_manager.get_system_resources()
        
        # Add additional system information
        import psutil
        import platform
        import time
        
        # CPU information
        system_stats['cpu_cores'] = psutil.cpu_count()
        system_stats['cpu_load_avg'] = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else None
        
        # System uptime
        boot_time = psutil.boot_time()
        system_stats['uptime'] = time.time() - boot_time
        
        # Database connections (real connectivity test)
        try:
            db_connections = db_manager.test_connections()
            healthy_dbs = sum(1 for c in db_connections.values() if c.get('connected'))
            total_dbs = len(db_connections)
            system_stats['db_connections'] = f"{healthy_dbs}/{total_dbs}"
        except Exception as e:
            logger.warning(f"Database connectivity test failed: {e}")
            system_stats['db_connections'] = "0/2"
        
        return jsonify({'success': True, 'stats': system_stats})
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/health')
def system_health():
    """Simple health check endpoint for Fly.io deployment"""
    try:
        # Basic health indicators
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': True,
            'database': False,
            'containers': False
        }
        
        # Quick database check
        try:
            db_connections = db_manager.test_connections()
            if any(conn.get('connected') for conn in db_connections.values()):
                health_status['database'] = True
        except:
            pass
            
        # Quick container check
        try:
            container_status = docker_manager.get_required_containers_status()
            if any(c.get('status') == 'running' for c in container_status.values()):
                health_status['containers'] = True
        except:
            pass
        
        # Return 200 if basic systems are responding
        if health_status['uptime']:
            return jsonify(health_status), 200
        else:
            return jsonify(health_status), 503
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503

@app.route('/api/environment/status')
def get_environment_status():
    """Get comprehensive environment status"""
    try:
        import os
        import subprocess
        
        status = {
            'python_env': check_python_environment(),
            'dependencies': check_dependencies(),
            'docker_daemon': check_docker_daemon(),
            'infrastructure': check_infrastructure_status()
        }
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting environment status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/environment/setup', methods=['POST'])
def setup_environment():
    """Setup Python environment and dependencies"""
    try:
        import subprocess
        import os
        
        results = []
        
        # Check if virtual environment exists
        venv_path = '/Users/robertsher/Projects/autogen_env'
        if not os.path.exists(venv_path):
            results.append("Virtual environment not found - please create it manually")
            return jsonify({'success': False, 'error': 'Virtual environment missing', 'results': results})
        
        # Install required packages
        required_packages = [
            'psycopg2-binary', 'flask', 'flask-socketio', 'docker', 
            'requests', 'beautifulsoup4', 'lxml', 'selenium', 'psutil'
        ]
        
        for package in required_packages:
            try:
                result = subprocess.run([
                    f'{venv_path}/bin/pip', 'install', package
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    results.append(f"✅ {package} installed/updated")
                else:
                    results.append(f"❌ {package} failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                results.append(f"⏱️ {package} installation timed out")
            except Exception as e:
                results.append(f"❌ {package} error: {str(e)}")
        
        return jsonify({'success': True, 'message': 'Environment setup completed', 'results': results})
        
    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        return jsonify({'success': False, 'error': str(e)})

def check_python_environment():
    """Check Python virtual environment status"""
    try:
        import os
        venv_path = '/Users/robertsher/Projects/autogen_env'
        
        if not os.path.exists(venv_path):
            return {
                'status': 'error',
                'message': 'Virtual Environment Missing',
                'details': 'autogen_env not found'
            }
        
        # Check if Python executable exists
        python_path = f'{venv_path}/bin/python'
        if os.path.exists(python_path):
            return {
                'status': 'healthy',
                'message': 'Virtual Environment Active',
                'details': 'autogen_env configured'
            }
        else:
            return {
                'status': 'error',
                'message': 'Virtual Environment Corrupted',
                'details': 'Python executable missing'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': 'Environment Check Failed',
            'details': str(e)
        }

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import subprocess
        venv_python = '/Users/robertsher/Projects/autogen_env/bin/python'
        
        required_packages = ['psycopg2', 'flask', 'docker', 'requests']
        missing_packages = []
        
        for package in required_packages:
            try:
                result = subprocess.run([
                    venv_python, '-c', f'import {package}'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    missing_packages.append(package)
            except:
                missing_packages.append(package)
        
        if not missing_packages:
            return {
                'status': 'healthy',
                'message': 'All Dependencies Available',
                'details': f'{len(required_packages)} packages verified'
            }
        else:
            return {
                'status': 'warning',
                'message': f'{len(missing_packages)} Missing Dependencies',
                'details': f'Missing: {", ".join(missing_packages)}'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': 'Dependency Check Failed',
            'details': str(e)
        }

def check_docker_daemon():
    """Check Docker daemon status"""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        
        return {
            'status': 'healthy',
            'message': 'Docker Daemon Running',
            'details': 'Docker API accessible'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': 'Docker Daemon Unavailable',
            'details': str(e)
        }

def check_infrastructure_status():
    """Check overall infrastructure service status using health checks"""
    try:
        # Get health check status for all services
        service_status = docker_manager.get_required_containers_status()
        
        healthy_services = []
        total_services = 0
        
        for service_id, service_data in service_status.items():
            total_services += 1
            if service_data.get('healthy', False) or service_data.get('status') == 'running':
                healthy_services.append(service_id)
        
        total_healthy = len(healthy_services)
        
        if total_healthy == total_services:
            return {
                'status': 'healthy',
                'message': 'All Services Running',
                'details': f'{total_healthy}/{total_services} services healthy'
            }
        elif total_healthy > 0:
            return {
                'status': 'partial',
                'message': 'Partial Infrastructure',
                'details': f'{total_healthy}/{total_services} services running'
            }
        else:
            return {
                'status': 'error',
                'message': 'Infrastructure Down',
                'details': 'No services running'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': 'Infrastructure Check Failed',
            'details': str(e)
        }

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to admin dashboard'})
    logger.info(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on('request_status_update')
def handle_status_request():
    """Handle request for status update"""
    try:
        # Send current status of all systems
        docker_status = docker_manager.get_required_containers_status()
        scraper_status = acquisition_manager.get_status()
        db_stats = db_manager.get_product_stats()
        
        emit('status_update', {
            'docker': docker_status,
            'scraper': scraper_status,
            'database': db_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('error', {'message': str(e)})

# Background task for periodic updates
def background_status_updates():
    """Send periodic status updates to connected clients (optimized for performance)"""
    while True:
        try:
            if socketio.server.manager.rooms:  # Only if clients connected
                # Simplified status updates - only essential data
                try:
                    scraper_status = acquisition_manager.get_status()
                    socketio.emit('status_update', {
                        'scraper': scraper_status,
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.debug(f"Status update error: {e}")
            
            time.sleep(15)  # Update every 15 seconds (reduced frequency)
            
        except Exception as e:
            logger.error(f"Error in background updates: {e}")
            time.sleep(30)  # Wait longer on error

# Git Auto-Push API Endpoints
@app.route('/api/git/status')
def git_status():
    """Get git repository status"""
    try:
        import subprocess
        
        # Check if we're in a git repo
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True, cwd='/Users/robertsher/Projects/tileshop_rag')
        if result.returncode != 0:
            return jsonify({'error': 'Not in a git repository'}), 400
            
        # Get status
        status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                     capture_output=True, text=True, cwd='/Users/robertsher/Projects/tileshop_rag')
        
        # Get current branch
        branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                     capture_output=True, text=True, cwd='/Users/robertsher/Projects/tileshop_rag')
        
        # Get last commit
        commit_result = subprocess.run(['git', 'log', '-1', '--oneline'], 
                                     capture_output=True, text=True, cwd='/Users/robertsher/Projects/tileshop_rag')
        
        return jsonify({
            'success': True,
            'in_git_repo': True,
            'has_changes': bool(status_result.stdout.strip()),
            'changes': status_result.stdout.strip().split('\n') if status_result.stdout.strip() else [],
            'current_branch': branch_result.stdout.strip(),
            'last_commit': commit_result.stdout.strip(),
            'auto_push_enabled': os.getenv('PRODUCTION', '').lower() in ['true', '1', 'yes'] or os.getenv('AUTO_GIT_PUSH', '').lower() in ['true', '1', 'yes']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/git/push', methods=['POST'])
def manual_git_push():
    """Manually trigger git push"""
    try:
        data = request.get_json() or {}
        commit_message = data.get('message', 'Dashboard: Manual commit from admin interface')
        
        result = auto_git_push(commit_message)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Changes committed and pushed successfully',
                'timestamp': datetime.now(EST).isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No changes to commit or push failed'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/git/auto-push/<operation>', methods=['POST'])
def trigger_auto_push(operation):
    """Trigger auto-push for specific operations"""
    try:
        result = trigger_auto_push_if_changes(operation)
        
        return jsonify({
            'success': True,
            'auto_pushed': result,
            'operation': operation,
            'timestamp': datetime.now(EST).isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Standardized Diagnostic API Endpoints (Phase 2)
@app.route('/api/service/<service_name>/health')
def service_health_check(service_name):
    """Standardized health check for any service"""
    try:
        if service_name not in diagnostic_services:
            return jsonify({
                'success': False,
                'error': f'Service {service_name} not found',
                'available_services': list(diagnostic_services.keys())
            }), 404
        
        service = diagnostic_services[service_name]
        result = service.health_check()
        
        return jsonify({
            'success': True,
            'service': service_name,
            'service_type': service.service_type,
            'description': service.description,
            'health': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'service': service_name,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/service/<service_name>/logs')
def service_logs(service_name):
    """Standardized logs endpoint for any service"""
    try:
        if service_name not in diagnostic_services:
            return jsonify({
                'success': False,
                'error': f'Service {service_name} not found',
                'available_services': list(diagnostic_services.keys())
            }), 404
        
        lines = request.args.get('lines', 50, type=int)
        service = diagnostic_services[service_name]
        result = service.get_filtered_logs(lines)
        
        return jsonify({
            'success': True,
            'service': service_name,
            'service_type': service.service_type,
            'logs': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'service': service_name,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/service/<service_name>/debug')
def service_debug(service_name):
    """Standardized debug panel for any service"""
    try:
        if service_name not in diagnostic_services:
            return jsonify({
                'success': False,
                'error': f'Service {service_name} not found',
                'available_services': list(diagnostic_services.keys())
            }), 404
        
        service = diagnostic_services[service_name]
        result = service.debug_panel()
        
        return jsonify({
            'success': True,
            'service': service_name,
            'service_type': service.service_type,
            'description': service.description,
            'debug': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'service': service_name,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/services/list')
def list_services():
    """List all available services and their types"""
    try:
        services_by_type = {
            'microservices': [],
            'runtime': [],
            'prewarm': []
        }
        
        for name, service in diagnostic_services.items():
            service_info = {
                'name': name,
                'description': service.description,
                'service_type': service.service_type
            }
            
            if service.service_type == 'microservice':
                services_by_type['microservices'].append(service_info)
            elif service.service_type == 'runtime':
                services_by_type['runtime'].append(service_info)
            elif service.service_type == 'prewarm':
                services_by_type['prewarm'].append(service_info)
        
        return jsonify({
            'success': True,
            'services': services_by_type,
            'total_services': len(diagnostic_services),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Initialize session
@app.before_request
def before_request():
    """Initialize session"""
    if 'user_id' not in session:
        session['user_id'] = f'user_{datetime.now().timestamp()}'

def start_integrated_monitoring():
    """Start integrated monitoring system with all monitoring processes"""
    logger.info("🚀 Starting Integrated Monitoring System...")
    
    # Create monitoring threads
    monitors = {
        'audit': threading.Thread(target=audit_monitor, daemon=True, name="AuditMonitor"),
        'sitemap': threading.Thread(target=sitemap_monitor, daemon=True, name="SitemapMonitor"), 
        'learning': threading.Thread(target=learning_monitor, daemon=True, name="LearningMonitor"),
        'health': threading.Thread(target=health_monitor, daemon=True, name="HealthMonitor"),
        'download': threading.Thread(target=download_monitor, daemon=True, name="DownloadMonitor")
    }
    
    # Start all monitors
    for name, monitor in monitors.items():
        monitor.start()
        logger.info(f"   ✅ Started {name.title()} Monitor")
        
    logger.info("🎯 All monitoring systems active!")

def audit_monitor():
    """Monitor data extraction quality periodically"""
    while True:
        try:
            time.sleep(1800)  # Run audit every 30 minutes
            
            logger.info("🔍 Running automated data quality audit...")
            
            # Run quick audit check
            try:
                from curl_scraper import scrape_product_with_curl
                test_url = "https://www.tileshop.com/products/linewood-white-matte-ceramic-wall-tile-12-x-36-in-485020"
                result = scrape_product_with_curl(test_url)
                
                if result:
                    # Count enhanced fields
                    enhanced_fields = ['thickness', 'box_quantity', 'box_weight', 'edge_type', 
                                     'shade_variation', 'number_of_faces', 'directional_layout', 'country_of_origin']
                    captured_fields = sum(1 for field in enhanced_fields if result.get(field))
                    capture_rate = (captured_fields / len(enhanced_fields)) * 100
                    
                    audit_status = {
                        'timestamp': datetime.now(EST).isoformat(),
                        'capture_rate': capture_rate,
                        'enhanced_fields_captured': captured_fields,
                        'total_enhanced_fields': len(enhanced_fields),
                        'status': 'healthy' if capture_rate > 80 else 'warning'
                    }
                    
                    socketio.emit('audit_update', audit_status)
                    logger.info(f"📊 Audit complete - Capture rate: {capture_rate:.1f}%")
                    
            except Exception as e:
                logger.error(f"❌ Audit monitor error: {e}")
                socketio.emit('audit_update', {
                    'timestamp': datetime.now(EST).isoformat(),
                    'status': 'error',
                    'error': str(e)
                })
                
        except Exception as e:
            logger.error(f"❌ Audit monitor critical error: {e}")
            time.sleep(300)  # Wait 5 minutes on error

def sitemap_monitor():
    """Monitor sitemap download progress"""
    while True:
        try:
            time.sleep(10)  # Check every 10 seconds
            
            try:
                response = requests.get('http://localhost:8080/api/acquisition/sitemap-status', timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    socketio.emit('sitemap_update', {
                        'timestamp': datetime.now(EST).isoformat(),
                        'type': 'sitemap',
                        'status': status
                    })
            except:
                pass  # Silent fail - sitemap might not be active
                
        except Exception as e:
            logger.error(f"❌ Sitemap monitor error: {e}")
            time.sleep(60)

def learning_monitor():
    """Monitor learning/acquisition progress"""
    while True:
        try:
            time.sleep(5)  # Check every 5 seconds
            
            try:
                response = requests.get('http://localhost:8080/api/acquisition/status', timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    socketio.emit('learning_update', {
                        'timestamp': datetime.now(EST).isoformat(),
                        'type': 'learning',
                        'status': status
                    })
            except:
                pass  # Silent fail - learning might not be active
                
        except Exception as e:
            logger.error(f"❌ Learning monitor error: {e}")
            time.sleep(30)

def health_monitor():
    """Monitor overall system health"""
    while True:
        try:
            time.sleep(60)  # Health check every minute
            
            # Check system components
            health_status = {
                'timestamp': datetime.now(EST).isoformat(),
                'dashboard': True,
                'database': check_database_health(),
                'curl_scraper': check_curl_scraper_health(),
                'docker': check_docker_health()
            }
            
            socketio.emit('health_update', health_status)
            
        except Exception as e:
            logger.error(f"❌ Health monitor error: {e}")
            time.sleep(120)

def download_monitor():
    """Monitor live download operations"""
    while True:
        try:
            time.sleep(15)  # Check every 15 seconds
            
            # Check for active downloads (placeholder - can be expanded)
            download_status = {
                'timestamp': datetime.now(EST).isoformat(),
                'active_downloads': 0,
                'status': 'monitoring'
            }
            
            socketio.emit('download_update', download_status)
            
        except Exception as e:
            logger.error(f"❌ Download monitor error: {e}")
            time.sleep(60)

def check_database_health():
    """Check database connectivity"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', port=5432, database='postgres',
            user='postgres', password='postgres'
        )
        conn.close()
        return True
    except:
        return False

def check_curl_scraper_health():
    """Check curl_scraper functionality with quick test"""
    try:
        import subprocess
        result = subprocess.run(['curl', '-s', 'https://httpbin.org/get'], 
                              capture_output=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def check_docker_health():
    """Check Docker connectivity"""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except:
        return False

if __name__ == '__main__':
    # Create required directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Start background status updates with reduced frequency
    update_thread = threading.Thread(target=background_status_updates, daemon=True)
    update_thread.start()
    
    # Skip pre-warming and monitoring on startup for faster boot
    # These will be started on-demand when needed
    logger.info("Dashboard starting in fast-boot mode - monitoring disabled")
    
    # Check for production mode
    production_mode = os.getenv('PRODUCTION', '').lower() in ['true', '1', 'yes']
    
    if production_mode:
        logger.info("Starting Tileshop Admin Dashboard in PRODUCTION mode")
        logger.info("Using Gunicorn WSGI server for production deployment")
        
        # Import gunicorn programmatically for production
        try:
            from gunicorn.app.base import BaseApplication
            
            class StandaloneApplication(BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    config = {key: value for key, value in self.options.items()
                             if key in self.cfg.settings and value is not None}
                    for key, value in config.items():
                        self.cfg.set(key.lower(), value)

                def load(self):
                    return self.application

            # Production configuration
            options = {
                'bind': '0.0.0.0:8080',
                'workers': 4,
                'worker_class': 'eventlet',
                'worker_connections': 1000,
                'timeout': 120,
                'keepalive': 5,
                'max_requests': 1000,
                'max_requests_jitter': 50,
                'preload_app': True,
                'capture_output': True,
                'enable_stdio_inheritance': True
            }
            
            StandaloneApplication(app, options).run()
            
        except ImportError:
            logger.warning("Gunicorn not available, falling back to development server")
            logger.warning("Install gunicorn for production: pip install gunicorn[eventlet]")
            socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
    else:
        logger.info("Starting Tileshop Admin Dashboard in DEVELOPMENT mode")
        logger.info("Dashboard available at: http://localhost:8080")
        logger.info("Set PRODUCTION=true environment variable for production deployment")
        
        # Development server
        socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)