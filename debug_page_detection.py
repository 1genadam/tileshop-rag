#!/usr/bin/env python3
"""
Debug page structure detection for SKU 351300
"""

from page_structure_detector import PageStructureDetector
import json

def debug_page_detection():
    """Debug why SKU 351300 is detected as tile instead of installation tool"""
    
    # Sample content that would come from the crawl
    sample_content = """
    best-of-everything-lippage-red-wedge-250-pieces-per-bag-351300
    Best of Everything Lippage Red Wedge 250 Pieces per Bag
    installation tool wedge leveling system lippage
    $49.99 per piece
    250 pieces per box
    """
    
    url = "https://www.tileshop.com/products/best-of-everything-lippage-red-wedge-250-pieces-per-bag-351300"
    
    detector = PageStructureDetector()
    
    # Test with minimal content
    result = detector.detect_page_structure(sample_content, url)
    
    print("=== Page Structure Detection Debug ===")
    print(f"URL: {url}")
    print(f"Detected Type: {result.page_type}")
    print(f"Confidence: {result.confidence}")
    print(f"Recommended Parser: {result.recommended_parser}")
    print(f"Features: {result.detected_features}")
    print()
    
    # Test each type manually
    print("=== Manual Pattern Testing ===")
    patterns = detector.detection_patterns
    
    for page_type, pattern_data in patterns.items():
        keywords = pattern_data.get("keywords", {})
        high_conf = keywords.get("high_confidence", [])
        med_conf = keywords.get("medium_confidence", [])
        
        high_matches = [kw for kw in high_conf if kw.lower() in sample_content.lower()]
        med_matches = [kw for kw in med_conf if kw.lower() in sample_content.lower()]
        
        print(f"\n{page_type.value}:")
        print(f"  High confidence matches: {high_matches}")
        print(f"  Medium confidence matches: {med_matches}")
    
    print("\n=== URL Analysis ===")
    print(f"URL contains 'lippage': {'lippage' in url.lower()}")
    print(f"URL contains 'wedge': {'wedge' in url.lower()}")
    print(f"URL contains 'leveling': {'leveling' in url.lower()}")

if __name__ == "__main__":
    debug_page_detection()