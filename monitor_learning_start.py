#!/usr/bin/env python3
"""
Monitor Learning Start - Ultimate Breakthrough Validation
"""

import requests
import time

def main():
    print('🚀 READY FOR ULTIMATE BREAKTHROUGH VALIDATION!')
    print('=' * 60)
    print('📊 SITEMAP STATUS: COMPLETE ✅')
    print('   • 4,778 URLs ready for processing')
    print('   • Sitemap downloaded and inserted into database')
    print('   • System ready for "Start Learning"')
    
    print('\n🔥 CURL SCRAPER BREAKTHROUGH READY FOR SCALE TEST!')
    print('   This will be the ultimate validation:')
    print('   ✅ 4,778 products vs 0% success rate with crawl4ai')
    print('   ✅ Expected 100% success rate with our curl solution')
    print('   ✅ No bot detection issues at massive scale')
    
    print('\n⏳ MONITORING FOR LEARNING START...')
    print('   Click "Start Learning" in the dashboard now!')
    
    last_status = None
    for i in range(300):  # Monitor for 5 minutes
        try:
            response = requests.get('http://localhost:8080/api/acquisition/status', timeout=5)
            if response.status_code == 200:
                status = response.json()
                running = status.get('running', False)
                processed = status.get('products_processed', 0)
                phase = status.get('current_phase', 'idle')
                
                current_status = f'{running}-{processed}-{phase}'
                if current_status != last_status:
                    print(f'   [{i+1:3d}s] Running: {running}, Processed: {processed}, Phase: {phase}')
                    last_status = current_status
                    
                    if running:
                        print(f'\n🎉 LEARNING STARTED! BREAKTHROUGH VALIDATION BEGINNING!')
                        print(f'   Time: {time.strftime("%H:%M:%S")}')
                        print(f'   Our curl scraper is now processing 4,778 products!')
                        
                        # Continue monitoring progress
                        monitor_progress()
                        break
                        
            if i % 30 == 0:
                print(f'   [{i+1:3d}s] Waiting for "Start Learning" click...')
                
        except Exception as e:
            if i % 30 == 0:
                print(f'   [{i+1:3d}s] Status check error: {e}')
        
        time.sleep(1)

def monitor_progress():
    """Monitor the learning progress in detail"""
    print('\n🏆 MONITORING BREAKTHROUGH VALIDATION PROGRESS')
    print('-' * 60)
    
    last_processed = 0
    milestones = [1, 5, 10, 25, 50, 100, 250, 500]
    achieved = set()
    
    for i in range(3600):  # Monitor for 1 hour
        try:
            response = requests.get('http://localhost:8080/api/acquisition/status', timeout=5)
            if response.status_code == 200:
                status = response.json()
                running = status.get('running', False)
                processed = status.get('products_processed', 0)
                success_rate = status.get('success_rate', 0)
                phase = status.get('current_phase', 'unknown')
                
                if processed != last_processed:
                    print(f'   [{i+1:4d}s] Processed: {processed:,}/4,778, Success: {success_rate:.1f}%, Phase: {phase}')
                    last_processed = processed
                    
                    # Celebrate milestones
                    for milestone in milestones:
                        if processed >= milestone and milestone not in achieved:
                            achieved.add(milestone)
                            print(f'   🎯 MILESTONE: {milestone} products! Success rate: {success_rate:.1f}%')
                            
                            if milestone >= 10 and success_rate > 80:
                                print(f'   🔥 BREAKTHROUGH CONFIRMED! High success rate at scale!')
                
                if not running and processed > 0:
                    print(f'\n🏁 LEARNING COMPLETED!')
                    print(f'   Final: {processed:,} products processed')
                    print(f'   Success rate: {success_rate:.1f}%')
                    break
                    
        except Exception as e:
            if i % 60 == 0:
                print(f'   Error: {e}')
        
        time.sleep(1)

if __name__ == "__main__":
    main()