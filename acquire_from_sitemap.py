#!/usr/bin/env python3
"""
Scrape products using pre-downloaded sitemap data
Includes status tracking and resume capability
"""

import json
import time
import sys
import signal
from datetime import datetime
from tileshop_learner import extract_product_data, save_to_database, crawl_page_with_tabs
from download_sitemap import load_sitemap_data, update_url_status, get_pending_urls, get_scraping_statistics, main as refresh_sitemap

# Configuration
CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"
SITEMAP_MAX_AGE_DAYS = 7

# Global variables for graceful shutdown
interrupted = False
current_url = None

def signal_handler(signum, frame):
    """Handle interruption signals gracefully"""
    global interrupted, current_url
    interrupted = True
    print(f"\n⚠️  Interrupt signal received (Ctrl+C)")
    print(f"📝 Current URL being processed: {current_url}")
    print(f"💾 Progress will be saved automatically...")
    print(f"🔄 You can resume later by running the same command")

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def create_recovery_checkpoint(url, error_msg, stats):
    """Create a recovery checkpoint file"""
    checkpoint = {
        'timestamp': datetime.now().isoformat(),
        'failed_url': url,
        'error_message': error_msg,
        'statistics': stats,
        'recovery_instructions': [
            'Run the same scraper command to resume',
            'The scraper will automatically skip completed URLs',
            'Failed URLs will be retried'
        ]
    }
    
    with open('recovery_checkpoint.json', 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    print(f"💾 Recovery checkpoint saved to recovery_checkpoint.json")

def load_recovery_info():
    """Load recovery information if available"""
    try:
        with open('recovery_checkpoint.json', 'r') as f:
            recovery = json.load(f)
        
        print(f"🔄 Recovery information found:")
        print(f"   Last failure: {recovery['timestamp']}")
        print(f"   Failed URL: {recovery['failed_url']}")
        print(f"   Error: {recovery['error_message']}")
        
        return recovery
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def validate_sitemap_freshness():
    """Ensure sitemap is fresh, auto-refresh if needed"""
    print("📅 Checking sitemap freshness...")
    
    try:
        # This will auto-refresh if older than SITEMAP_MAX_AGE_DAYS
        sitemap_data = refresh_sitemap(max_age_days=SITEMAP_MAX_AGE_DAYS)
        if sitemap_data:
            return True
        else:
            print("❌ Failed to ensure fresh sitemap")
            return False
    except Exception as e:
        print(f"⚠️  Error checking sitemap: {e}")
        print("🔄 Attempting to use existing sitemap...")
        return True  # Continue with existing sitemap

def crawl_single_page(url, progress_callback=None):
    """Optimized crawling with real-time progress updates"""
    import requests
    
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    print(f"  🔄 Starting crawl: {url}")
    if progress_callback:
        progress_callback('crawl_start', {'url': url, 'stage': 'submitting'})
    
    try:
        # Optimized crawl configuration for speed
        crawl_data = {
            "urls": [url],
            "formats": ["html", "markdown"],
            "javascript": True,
            "wait_time": 8,  # Reduced from 15 to 8 seconds
            "page_timeout": 30000,  # Reduced from 45s to 30s
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "css_selector": ".product-detail, .product-info, .product-specs, .product-title, .price",  # Target specific content
            "exclude_tags": ["script", "style", "nav", "footer", "header", "aside"]  # Skip unnecessary content
        }
        
        submit_start = time.time()
        response = requests.post(f"{CRAWL4AI_URL}/crawl", headers=headers, json=crawl_data, timeout=60)
        
        if response.status_code != 200:
            error_msg = f"HTTP {response.status_code}"
            print(f"  ✗ Failed to submit crawl request: {error_msg}")
            if progress_callback:
                progress_callback('crawl_error', {'url': url, 'error': error_msg, 'stage': 'submission'})
            return None, error_msg
        
        task_id = response.json().get('task_id')
        submit_time = time.time() - submit_start
        print(f"  📋 Task submitted: {task_id} ({submit_time:.2f}s)")
        if progress_callback:
            progress_callback('crawl_submitted', {'url': url, 'task_id': task_id, 'submit_time': submit_time})
        
        # Adaptive polling - start checking immediately with shorter intervals
        poll_start = time.time()
        check_intervals = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]  # Progressive back-off
        
        for attempt, interval in enumerate(check_intervals):
            if attempt > 0:  # Skip initial sleep
                time.sleep(interval)
            
            try:
                check_start = time.time()
                result_response = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", headers=headers, timeout=10)
                check_time = time.time() - check_start
                
                if result_response.status_code == 200:
                    result = result_response.json()
                    status = result.get('status')
                    elapsed = time.time() - poll_start
                    
                    print(f"  🔍 Status check #{attempt+1}: {status} ({elapsed:.1f}s elapsed, {check_time:.2f}s check)")
                    if progress_callback:
                        progress_callback('crawl_status', {
                            'url': url, 
                            'status': status, 
                            'attempt': attempt+1, 
                            'elapsed': elapsed,
                            'check_time': check_time
                        })
                    
                    if status == 'completed':
                        main_result = result.get('results', [{}])[0] if result.get('results') else None
                        if main_result:
                            total_time = time.time() - submit_start
                            print(f"  ✅ Crawl completed in {total_time:.2f}s")
                            if progress_callback:
                                progress_callback('crawl_complete', {
                                    'url': url, 
                                    'total_time': total_time,
                                    'submit_time': submit_time,
                                    'poll_time': elapsed
                                })
                            return {'main': main_result}, None
                        else:
                            error_msg = "No results returned"
                            print(f"  ✗ {error_msg}")
                            if progress_callback:
                                progress_callback('crawl_error', {'url': url, 'error': error_msg, 'stage': 'results'})
                            return None, error_msg
                    elif status == 'failed':
                        error_msg = result.get('error', 'Unknown crawl error')
                        print(f"  ✗ Crawl failed: {error_msg}")
                        if progress_callback:
                            progress_callback('crawl_error', {'url': url, 'error': error_msg, 'stage': 'processing'})
                        return None, error_msg
                    elif status in ['pending', 'processing']:
                        # Continue polling
                        continue
                else:
                    print(f"  ⚠ Status check failed: {result_response.status_code}")
                    if progress_callback:
                        progress_callback('crawl_warning', {
                            'url': url, 
                            'message': f'Status check failed: {result_response.status_code}',
                            'attempt': attempt+1
                        })
                
            except requests.RequestException as e:
                print(f"  ⚠ Request error during status check #{attempt+1}: {e}")
                if progress_callback:
                    progress_callback('crawl_warning', {
                        'url': url, 
                        'message': f'Request error: {e}',
                        'attempt': attempt+1
                    })
        
        timeout_msg = f"Crawl timeout after {len(check_intervals)} attempts"
        print(f"  ⏰ {timeout_msg}")
        if progress_callback:
            progress_callback('crawl_timeout', {'url': url, 'attempts': len(check_intervals)})
        return None, timeout_msg
        
    except requests.RequestException as e:
        print(f"  ✗ Network error: {e}")
        return None, f"Network error: {e}"
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return None, f"Unexpected error: {e}"

def scrape_from_sitemap(max_products=None, resume=True):
    """Scrape products using pre-downloaded sitemap with resume capability"""
    global current_url, interrupted
    
    print("Tileshop Scraper - Enhanced Recovery & Auto-Refresh")
    print("=" * 60)
    
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()
    
    # Check for previous recovery information
    recovery_info = load_recovery_info()
    if recovery_info:
        print("📋 Previous session was interrupted")
        print("✅ Auto-resume enabled - will continue from where it left off")
    
    # Validate sitemap freshness (auto-refresh if > 7 days old)
    if not validate_sitemap_freshness():
        print("❌ Cannot proceed without valid sitemap")
        return
    
    # Load sitemap data
    sitemap_data = load_sitemap_data()
    if not sitemap_data:
        print("✗ No sitemap data found. This should not happen after validation.")
        return
    
    # Show current statistics
    stats = get_scraping_statistics()
    print(f"\n📊 Current Scraping Statistics:")
    print(f"   Total URLs: {stats['total_urls']:,}")
    print(f"   Completed: {stats['completed']:,} ({stats['completion_rate']:.1f}%)")
    print(f"   Failed: {stats['failed']:,}")
    print(f"   Pending: {stats['pending']:,}")
    print(f"   Never attempted: {stats['never_attempted']:,}")
    
    if stats['oldest_completion'] and stats['newest_completion']:
        print(f"   Scraping range: {stats['oldest_completion'][:10]} to {stats['newest_completion'][:10]}")
    
    # Get pending URLs with intelligent prioritization
    if resume:
        print(f"\n📋 Resume mode: Getting pending URLs (prioritized)...")
        print(f"   Priority: Never attempted first, then oldest failures")
        product_urls = get_pending_urls(max_products)
        if not product_urls:
            print("✅ All products already scraped!")
            return
    else:
        print(f"\n🔄 Fresh start: Getting all URLs...")
        # Reset all URLs to pending for fresh start
        for url_data in sitemap_data['urls']:
            url_data['scrape_status'] = 'pending'
            url_data['scraped_at'] = None
        
        # Save updated sitemap
        with open('tileshop_sitemap.json', 'w', encoding='utf-8') as f:
            json.dump(sitemap_data, f, indent=2, ensure_ascii=False)
        
        product_urls = [url_data['url'] for url_data in sitemap_data['urls']]
        if max_products:
            product_urls = product_urls[:max_products]
    
    print(f"\n🎯 Will process {len(product_urls):,} products in optimized order")
    
    # Statistics
    successful_scrapes = 0
    failed_scrapes = 0
    start_time = time.time()
    
    for i, url in enumerate(product_urls, 1):
        # Check for interruption
        if interrupted:
            print(f"\n🛑 Graceful shutdown initiated")
            break
            
        current_url = url  # Track current URL for signal handler
        
        print(f"\n{'='*80}")
        print(f"Processing {i:,}/{len(product_urls):,}: {url.split('/')[-1]}")
        print('='*80)
        
        try:
            # Crawl the page with progress callback
            def crawl_progress_callback(event_type, data):
                print(f"    📊 {event_type}: {data.get('stage', data.get('status', 'update'))}")
            
            crawl_results, error_msg = crawl_single_page(url, crawl_progress_callback)
            
            if not crawl_results:
                print(f"  ✗ Failed to crawl: {error_msg}")
                failed_scrapes += 1
                update_url_status(url, 'failed', error_msg)
                
                # Create recovery checkpoint for critical failures
                stats = {
                    'processed': i,
                    'successful': successful_scrapes,
                    'failed': failed_scrapes
                }
                create_recovery_checkpoint(url, error_msg, stats)
                continue
            
            # Extract product data
            product_data = extract_product_data(crawl_results, url)
            
            if not product_data:
                error_msg = 'Data extraction failed'
                print(f"  ✗ {error_msg}")
                failed_scrapes += 1
                update_url_status(url, 'failed', error_msg)
                continue
            
            # Print summary
            print(f"  📊 Extracted data for SKU {product_data.get('sku', 'unknown')}:")
            print(f"    Title: {product_data.get('title', 'N/A')[:50]}...")
            print(f"    Price: ${product_data.get('price_per_box', 'N/A')}")
            print(f"    Specs: {len(product_data.get('specifications', {})) if product_data.get('specifications') else 0} fields")
            print(f"    Image: {'✓' if product_data.get('primary_image') else '✗'}")
            print(f"    Brand: {product_data.get('brand', 'N/A')}")
            
            # Save to database
            save_to_database(product_data, crawl_results)
            successful_scrapes += 1
            
            # Update status in sitemap
            update_url_status(url, 'completed')
            
            # Clear current URL after successful completion
            current_url = None
            
            # Rate limiting - be respectful
            if not interrupted:  # Skip delay if interrupted
                print(f"  ⏳ Waiting 3 seconds before next request...")
                time.sleep(3)
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Keyboard interrupt detected")
            interrupted = True
            break
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"  ✗ {error_msg}")
            failed_scrapes += 1
            update_url_status(url, 'failed', error_msg)
            
            # Create recovery checkpoint for unexpected errors
            stats = {
                'processed': i,
                'successful': successful_scrapes,
                'failed': failed_scrapes
            }
            create_recovery_checkpoint(url, error_msg, stats)
            continue
        
        # Progress update every 5 products
        if i % 5 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(product_urls) - i) * avg_time
            success_rate = successful_scrapes / i * 100
            
            print(f"\n📈 Progress Update:")
            print(f"   Processed: {i:,}/{len(product_urls):,} ({i/len(product_urls)*100:.1f}%)")
            print(f"   Successful: {successful_scrapes:,}, Failed: {failed_scrapes:,}")
            print(f"   Success rate: {success_rate:.1f}%")
            print(f"   Time elapsed: {elapsed/60:.1f}m, Est. remaining: {remaining/60:.1f}m")
            print(f"   Avg time per product: {avg_time:.1f}s")
    
    # Final statistics
    elapsed = time.time() - start_time
    session_type = "interrupted" if interrupted else "completed"
    
    print(f"\n🎉 Scraping session {session_type}!")
    print(f"   Products processed: {len(product_urls):,}")
    print(f"   Successful: {successful_scrapes:,}")
    print(f"   Failed: {failed_scrapes:,}")
    if len(product_urls) > 0:
        print(f"   Success rate: {successful_scrapes/len(product_urls)*100:.1f}%")
    print(f"   Total time: {elapsed/60:.1f} minutes")
    if len(product_urls) > 0:
        print(f"   Average time per product: {elapsed/len(product_urls):.1f} seconds")
    
    # Show remaining work and recovery instructions
    remaining_urls = get_pending_urls()
    if remaining_urls:
        print(f"\n📋 Remaining work: {len(remaining_urls):,} products still pending")
        
        if interrupted:
            print(f"\n🔄 RECOVERY INSTRUCTIONS:")
            print(f"   ✅ All progress has been automatically saved")
            print(f"   ✅ Run the same command to resume: python acquire_from_sitemap.py")
            print(f"   ✅ The scraper will skip completed URLs and retry failed ones")
            print(f"   ✅ Recovery checkpoint saved for debugging")
        else:
            print(f"   Run again to continue: python acquire_from_sitemap.py")
    else:
        print(f"\n✅ All products completed!")
        # Clean up recovery file if everything is done
        try:
            import os
            if os.path.exists('recovery_checkpoint.json'):
                os.remove('recovery_checkpoint.json')
                print(f"🧹 Cleaned up recovery checkpoint file")
        except:
            pass
    
    # Final recovery checkpoint if interrupted with pending work
    if interrupted and remaining_urls:
        final_stats = {
            'total_products': len(product_urls),
            'successful': successful_scrapes,
            'failed': failed_scrapes,
            'remaining': len(remaining_urls),
            'session_duration_minutes': elapsed/60
        }
        create_recovery_checkpoint(current_url or 'session_interrupted', 'User interruption', final_stats)

if __name__ == "__main__":
    # Parse command line arguments
    max_products = None
    resume = True
    
    if len(sys.argv) > 1:
        try:
            max_products = int(sys.argv[1])
            print(f"Limiting to {max_products:,} products")
        except ValueError:
            if sys.argv[1] == '--fresh':
                resume = False
                print("Fresh start mode (ignoring previous progress)")
            else:
                print("Usage: python acquire_from_sitemap.py [max_products] [--fresh]")
                sys.exit(1)
    
    if len(sys.argv) > 2 and sys.argv[2] == '--fresh':
        resume = False
        print("Fresh start mode")
    
    scrape_from_sitemap(max_products, resume)