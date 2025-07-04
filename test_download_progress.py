#!/usr/bin/env python3
"""
Test Download Progress Monitoring
Monitor WebSocket events and API responses during sitemap download
"""

import requests
import time
import threading

def monitor_api_progress():
    """Monitor API endpoints for progress"""
    print('\n📡 API PROGRESS MONITORING:')
    
    last_status = None
    for i in range(60):  # Monitor for 1 minute
        try:
            response = requests.get('http://localhost:8080/api/acquisition/sitemap-status', timeout=3)
            if response.status_code == 200:
                status = response.json()
                
                current_status = {
                    'urls': status.get('stats', {}).get('total_urls', 0),
                    'progress': status.get('download_progress', 0),
                    'complete': status.get('download_complete', False),
                    'message': status.get('message', '')[:30]
                }
                
                if current_status != last_status:
                    print(f'   [{i+1:2d}s] URLs: {current_status["urls"]:,}, Progress: {current_status["progress"]}%, Complete: {current_status["complete"]}')
                    if current_status['message']:
                        print(f'        {current_status["message"]}...')
                    last_status = current_status.copy()
                    
                    if current_status['complete'] and current_status['urls'] > 0:
                        print(f'\n   ✅ Download detected as complete!')
                        break
                        
        except Exception as e:
            if i % 15 == 0:
                print(f'   [{i+1:2d}s] API error: {e}')
        
        time.sleep(1)

def main():
    print('🔍 DOWNLOAD PROGRESS TESTING')
    print('=' * 50)
    
    print('\n💡 TESTING APPROACH:')
    print('   1. Monitor API responses for progress changes')
    print('   2. Time how long download takes')
    print('   3. Check if progress updates are visible')
    
    print('\n🎯 EXPECTED OUTCOMES:')
    print('   • Fast download (1-10s): Progress may jump too quickly to see')
    print('   • Normal download (10-30s): Should see gradual progress')
    print('   • Slow download (30s+): Clear progress increments')
    
    print('\n⏱️ TIMING ANALYSIS:')
    
    # Test current sitemap access speed
    start_time = time.time()
    try:
        response = requests.get('https://www.tileshop.com/sitemap.xml', timeout=10)
        fetch_time = time.time() - start_time
        size_kb = len(response.content) / 1024 if response.status_code == 200 else 0
        
        print(f'   • Direct sitemap fetch: {fetch_time:.1f}s for {size_kb:.1f}KB')
        
        if fetch_time < 2:
            print(f'   • Prediction: Download will be very fast (< 5s total)')
            print(f'   • Progress updates may be too quick to see')
        elif fetch_time < 5:
            print(f'   • Prediction: Download will be fast (5-10s total)')
            print(f'   • Progress may update in large jumps')
        else:
            print(f'   • Prediction: Download will be gradual (10+ seconds)')
            print(f'   • Progress should be clearly visible')
            
    except Exception as e:
        print(f'   • Could not test direct access: {e}')
        print(f'   • Download timing unknown')
    
    print(f'\n📊 TO TEST PROGRESS VISIBILITY:')
    print(f'   1. Open browser Developer Tools (F12)')
    print(f'   2. Go to Console tab')
    print(f'   3. Click "Download Sitemap" in the dashboard')
    print(f'   4. Watch for progress updates or errors')
    print(f'   5. Check Network tab for WebSocket connections')
    
    print(f'\n🔧 START API MONITORING...')
    monitor_api_progress()
    
    print(f'\n✅ PROGRESS TEST COMPLETE')
    print(f'   Ready to proceed with curl scraper breakthrough test!')

if __name__ == "__main__":
    main()