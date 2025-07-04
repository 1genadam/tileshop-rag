#!/usr/bin/env python3
"""
Monitor Live Download Progress
"""

import requests
import time

def main():
    print('📥 LIVE DOWNLOAD MONITORING')
    print('=' * 40)
    
    start_time = time.time()
    last_status = None
    
    for i in range(60):  # Monitor for 1 minute
        try:
            response = requests.get('http://localhost:8080/api/acquisition/sitemap-status', timeout=3)
            if response.status_code == 200:
                status = response.json()
                
                stats = status.get('stats', {})
                urls = stats.get('total_urls', 0)
                progress = stats.get('download_progress', 0)
                complete = status.get('download_complete', False)
                message = status.get('message', '')
                
                current_status = f'{urls}-{progress}-{complete}'
                
                if current_status != last_status:
                    elapsed = time.time() - start_time
                    print(f'[{elapsed:5.1f}s] URLs: {urls:,}, Progress: {progress}%, Complete: {complete}')
                    print(f'          {message}')
                    last_status = current_status
                    
                    if complete and urls > 0:
                        print(f'\n✅ DOWNLOAD COMPLETE - {elapsed:.1f}s total')
                        print(f'   URLs discovered: {urls:,}')
                        break
                        
        except Exception as e:
            print(f'[{i+1:2d}s] Error: {e}')
        
        time.sleep(1)
    
    print(f'\n🎯 READY FOR BREAKTHROUGH TEST!')

if __name__ == "__main__":
    main()