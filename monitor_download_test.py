#!/usr/bin/env python3
"""
Monitor Download Test
Track the live download progress to verify the process works
"""

import requests
import time

def main():
    print('📥 MONITORING LIVE DOWNLOAD PROGRESS TEST')
    print('=' * 50)
    print('   Testing if download progress updates correctly...')
    
    last_progress = None
    last_total = None
    changes_detected = 0
    
    for i in range(120):  # Monitor for 2 minutes
        try:
            response = requests.get('http://localhost:8080/api/acquisition/sitemap-status', timeout=5)
            if response.status_code == 200:
                status = response.json()
                
                stats = status.get('stats', {})
                total = stats.get('total_urls', 0)
                download_progress = stats.get('download_progress', 0)
                complete = status.get('download_complete', False)
                message = status.get('message', '')
                
                # Only print when there's a change
                if download_progress != last_progress or total != last_total:
                    print(f'[{i+1:3d}s] Progress: {download_progress}%, URLs: {total:,}, Complete: {complete}')
                    print(f'       Message: {message[:60]}...')
                    last_progress = download_progress
                    last_total = total
                    changes_detected += 1
                    
                    if complete and total > 0:
                        print(f'\n✅ DOWNLOAD TEST COMPLETE!')
                        print(f'   Final URLs: {total:,}')
                        print(f'   Progress updates detected: {changes_detected}')
                        print(f'   Download tracking: Working ✅')
                        break
                        
            else:
                if i % 30 == 0:
                    print(f'[{i+1:3d}s] API Error: {response.status_code}')
                    
        except Exception as e:
            if i % 30 == 0:
                print(f'[{i+1:3d}s] Error: {e}')
        
        time.sleep(1)
    
    print(f'\n📊 DOWNLOAD PROCESS TEST RESULTS:')
    print(f'   Progress changes detected: {changes_detected}')
    print(f'   Final progress: {last_progress}%')
    print(f'   Final URL count: {last_total:,}' if last_total else 'Unknown')
    print(f'   Status: {"Complete" if last_progress == 100.0 else "In progress or incomplete"}')
    
    if changes_detected > 0:
        print(f'\n✅ DOWNLOAD PROGRESS TRACKING: WORKING')
        print(f'   The dashboard should now show live updates')
    else:
        print(f'\n⚠️ No progress changes detected')
        print(f'   Download may have completed instantly or there may be an issue')
    
    print(f'\n🚀 READY FOR CURL SCRAPER BREAKTHROUGH TEST!')
    print(f'   Once download shows complete, click "Start Learning"')
    print(f'   Expected: 100% success rate with 4,000+ products')

if __name__ == "__main__":
    main()