#!/usr/bin/env python3
"""
Page Structure Detection System for Tileshop
Intelligently detects product page types to apply appropriate parsing logic
"""

import json
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class PageType(Enum):
    """Product page types based on structure analysis"""
    TILE = "tile"
    GROUT = "grout"  
    TRIM_MOLDING = "trim_molding"
    LUXURY_VINYL = "luxury_vinyl"
    INSTALLATION_TOOL = "installation_tool"
    UNKNOWN = "unknown"

@dataclass
class PageStructure:
    """Page structure information for parser selection"""
    page_type: PageType
    confidence: float
    detected_features: Dict[str, Any]
    recommended_parser: str

class PageStructureDetector:
    """Intelligent page structure detection system"""
    
    def __init__(self):
        self.detection_patterns = self._build_detection_patterns()
        self.feature_weights = self._build_feature_weights()
    
    def _build_detection_patterns(self) -> Dict[str, Dict]:
        """Build comprehensive detection patterns for each page type"""
        return {
            PageType.TILE: {
                "keywords": {
                    "high_confidence": ["marble", "ceramic", "porcelain", "natural stone", "travertine", "granite", "limestone"],
                    "medium_confidence": ["wall tile", "floor tile", "wall and floor", "mosaic", "penny round"],
                    "measurement_patterns": [r"(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*in", r"sq\.?\s*ft\.?\s*per\s*box"]
                },
                "pricing_indicators": ["sq. ft.", "per box", "coverage"],
                "specification_keywords": ["material origin", "finish", "honed", "polished", "rectified"],
                "resource_patterns": ["safety data sheet", "natural_stone.*sds"],
                "json_ld_clues": ["marble", "ceramic", "porcelain", "tile"]
            },
            
            PageType.GROUT: {
                "keywords": {
                    "high_confidence": ["grout", "sanded", "unsanded", "epoxy grout", "urethane grout"],
                    "medium_confidence": ["mortar", "joint", "mapei", "custom", "superior"],
                    "measurement_patterns": [r"(\d+)\s*lb", r"(\d+)\s*lbs", r"(\d+)\s*pounds?"]
                },
                "pricing_indicators": ["per package", "per lb", "weight"],
                "specification_keywords": ["sanded", "unsanded", "color", "grey", "white", "beige"],
                "resource_patterns": ["product data sheet", "sell sheet", "safety data"],
                "json_ld_clues": ["grout", "superior", "mapei", "custom"]
            },
            
            PageType.TRIM_MOLDING: {
                "keywords": {
                    "high_confidence": ["t-molding", "quarter round", "reducer", "stair nose", "threshold", "trim"],
                    "medium_confidence": ["molding", "transition", "bullnose", "edge trim", "cove"],
                    "measurement_patterns": [r"(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*in", r"(\d+)\s*pieces?"]
                },
                "pricing_indicators": ["per box", "pieces", "linear"],
                "specification_keywords": ["box quantity", "linear", "installation", "transition"],
                "resource_patterns": ["installation guidelines", "molding.*installation"],
                "json_ld_clues": ["molding", "t-molding", "quarter", "reducer", "trim"]
            },
            
            PageType.LUXURY_VINYL: {
                "keywords": {
                    "high_confidence": ["luxury vinyl", "lvt", "lvp", "vinyl plank", "vinyl tile"],
                    "medium_confidence": ["click-and-lock", "floating", "wear layer", "mil"],
                    "measurement_patterns": [r"(\d+)\s*mil", r"(\d+\.?\d*)mm", r"click.*lock"]
                },
                "pricing_indicators": ["per box", "sq. ft.", "coverage"],
                "specification_keywords": ["wear layer", "thickness", "installation", "floating", "click"],
                "resource_patterns": ["installation.*guidelines", "lvt.*installation"],
                "json_ld_clues": ["luxury vinyl", "vinyl", "plank", "lvt", "lvp"]
            },
            
            PageType.INSTALLATION_TOOL: {
                "keywords": {
                    "high_confidence": ["trowel", "spacer", "leveling", "backer board", "membrane", "thinset", "wedge", "lippage"],
                    "medium_confidence": ["installation", "tool", "equipment", "accessory", "goboard"],
                    "measurement_patterns": [r"(\d+)\s*piece", r"per\s*piece", r"(\d+\.?\d*)\s*ft\.?\s*x"]
                },
                "pricing_indicators": ["per piece", "each", "single unit"],
                "specification_keywords": ["waterproof", "installation", "construction", "technical"],
                "resource_patterns": ["technical.*specifications", "product.*data"],
                "json_ld_clues": ["board", "tool", "installation", "equipment"]
            }
        }
    
    def _build_feature_weights(self) -> Dict[str, float]:
        """Build feature importance weights for detection scoring"""
        return {
            "high_confidence_keywords": 0.4,
            "medium_confidence_keywords": 0.2,
            "measurement_patterns": 0.15,
            "pricing_indicators": 0.1,
            "specification_keywords": 0.08,
            "resource_patterns": 0.05,
            "json_ld_clues": 0.02
        }
    
    def detect_page_structure(self, html_content: str, url: str, json_ld_data: Dict = None) -> PageStructure:
        """
        Detect page structure and recommend appropriate parser
        Returns PageStructure with type, confidence, and recommended parser
        """
        
        # Prepare content for analysis
        content_lower = html_content.lower()
        url_lower = url.lower()
        
        # Score each page type
        page_scores = {}
        detailed_features = {}
        
        for page_type, patterns in self.detection_patterns.items():
            score, features = self._score_page_type(
                content_lower, url_lower, patterns, json_ld_data
            )
            page_scores[page_type] = score
            detailed_features[page_type] = features
        
        # Determine best match
        best_type = max(page_scores, key=page_scores.get)
        best_score = page_scores[best_type]
        
        # Apply confidence thresholds
        if best_score < 0.3:
            original_type = best_type
            best_type = PageType.UNKNOWN
            confidence = 0.0
            # Use features from the best scoring type even if below threshold
            features_to_use = detailed_features[original_type]
        else:
            confidence = min(best_score, 1.0)
            features_to_use = detailed_features[best_type]
        
        # Recommend parser based on detected type
        parser_map = {
            PageType.TILE: "TilePageParser",
            PageType.GROUT: "GroutPageParser", 
            PageType.TRIM_MOLDING: "TrimMoldingPageParser",
            PageType.LUXURY_VINYL: "LuxuryVinylPageParser",
            PageType.INSTALLATION_TOOL: "InstallationToolPageParser",
            PageType.UNKNOWN: "DefaultPageParser"
        }
        
        return PageStructure(
            page_type=best_type,
            confidence=confidence,
            detected_features=features_to_use,
            recommended_parser=parser_map[best_type]
        )
    
    def _score_page_type(self, content: str, url: str, patterns: Dict, json_ld_data: Dict = None) -> Tuple[float, Dict]:
        """Score how well content matches a specific page type"""
        score = 0.0
        detected_features = {}
        
        # Score high confidence keywords
        high_keywords = patterns["keywords"]["high_confidence"]
        high_matches = [kw for kw in high_keywords if kw in content or kw in url]
        if high_matches:
            keyword_score = len(high_matches) / len(high_keywords)
            score += keyword_score * self.feature_weights["high_confidence_keywords"]
            detected_features["high_confidence_keywords"] = high_matches
        
        # Score medium confidence keywords  
        med_keywords = patterns["keywords"]["medium_confidence"]
        med_matches = [kw for kw in med_keywords if kw in content or kw in url]
        if med_matches:
            keyword_score = len(med_matches) / len(med_keywords)
            score += keyword_score * self.feature_weights["medium_confidence_keywords"]
            detected_features["medium_confidence_keywords"] = med_matches
        
        # Score measurement patterns
        measurement_patterns = patterns["keywords"]["measurement_patterns"]
        measurement_matches = []
        for pattern in measurement_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                measurement_matches.extend(matches)
        if measurement_matches:
            pattern_score = min(len(measurement_matches) / 3, 1.0)  # Cap at 3 matches
            score += pattern_score * self.feature_weights["measurement_patterns"]
            detected_features["measurement_patterns"] = measurement_matches[:5]  # Limit for readability
        
        # Score pricing indicators
        pricing_indicators = patterns["pricing_indicators"]
        pricing_matches = [pi for pi in pricing_indicators if pi in content]
        if pricing_matches:
            pricing_score = len(pricing_matches) / len(pricing_indicators)
            score += pricing_score * self.feature_weights["pricing_indicators"]
            detected_features["pricing_indicators"] = pricing_matches
        
        # Score specification keywords
        spec_keywords = patterns["specification_keywords"]
        spec_matches = [sk for sk in spec_keywords if sk in content]
        if spec_matches:
            spec_score = len(spec_matches) / len(spec_keywords)
            score += spec_score * self.feature_weights["specification_keywords"]
            detected_features["specification_keywords"] = spec_matches
        
        # Score resource patterns
        resource_patterns = patterns["resource_patterns"]
        resource_matches = []
        for pattern in resource_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                resource_matches.append(pattern)
        if resource_matches:
            resource_score = len(resource_matches) / len(resource_patterns)
            score += resource_score * self.feature_weights["resource_patterns"]
            detected_features["resource_patterns"] = resource_matches
        
        # Score JSON-LD clues
        if json_ld_data:
            json_content = json.dumps(json_ld_data).lower()
            json_clues = patterns["json_ld_clues"]
            json_matches = [clue for clue in json_clues if clue in json_content]
            if json_matches:
                json_score = len(json_matches) / len(json_clues)
                score += json_score * self.feature_weights["json_ld_clues"]
                detected_features["json_ld_clues"] = json_matches
        
        return score, detected_features
    
    def get_page_type_summary(self, page_structure: PageStructure) -> str:
        """Get human-readable summary of detected page structure"""
        if page_structure.page_type == PageType.UNKNOWN:
            return f"Unknown page type (confidence: {page_structure.confidence:.2f})"
        
        features_count = sum(len(v) if isinstance(v, list) else 1 
                           for v in page_structure.detected_features.values())
        
        return (f"Detected: {page_structure.page_type.value} "
                f"(confidence: {page_structure.confidence:.2f}, "
                f"features: {features_count}, "
                f"parser: {page_structure.recommended_parser})")

def test_page_structure_detection():
    """Test page structure detection with sample data"""
    detector = PageStructureDetector()
    
    # Test cases with different page types
    test_cases = [
        {
            "name": "Marble Tile Page",
            "content": "Volakas Honed Marble Wall and Floor Tile - 12 x 24 in. Natural stone from Greece. 12.02 sq. ft. per Box. Safety data sheet available.",
            "url": "https://www.tileshop.com/products/volakas-honed-marble-wall-and-floor-tile-681294",
            "json_ld": {"name": "Volakas Honed Marble Wall and Floor Tile", "brand": "Rush River"}
        },
        {
            "name": "Grout Product Page", 
            "content": "Superior Sanded Pro-Grout Natural - 25 lb. Sanded grout for joints. Color: Grey. Product data sheet and sell sheet available.",
            "url": "https://www.tileshop.com/products/superior-sanded-pro-grout-natural-25-lb-052001",
            "json_ld": {"name": "Superior Sanded Pro-Grout Natural", "brand": "Superior"}
        },
        {
            "name": "T-Molding Page",
            "content": "Luxury Vinyl Floor Tile T-Molding - 1.77 x 94 in. Box contains 20 pieces. Installation guidelines included.",
            "url": "https://www.tileshop.com/products/luxury-vinyl-t-molding-682003",
            "json_ld": {"name": "T-Molding", "brand": "Andover"}
        },
        {
            "name": "Luxury Vinyl Page",
            "content": "Luxury Vinyl Plank - 7.1 x 48 in. 6mm thickness. 22 MIL wear layer. 18.93 sq. ft. per Box. Click-and-lock installation.",
            "url": "https://www.tileshop.com/products/luxury-vinyl-plank-683847",
            "json_ld": {"name": "Luxury Vinyl Plank", "brand": "Arbour"}
        },
        {
            "name": "Installation Tool Page",
            "content": "GoBoard Backer Board - 4 ft. x 8 ft. x ½ in. Waterproof construction. Single piece per package. Technical specifications included.",
            "url": "https://www.tileshop.com/products/goboard-backer-board-350067", 
            "json_ld": {"name": "GoBoard Backer Board", "brand": "GoBoard"}
        }
    ]
    
    print("Page Structure Detection Test Results:")
    print("=" * 60)
    
    for test_case in test_cases:
        structure = detector.detect_page_structure(
            test_case["content"], 
            test_case["url"], 
            test_case["json_ld"]
        )
        
        print(f"\n{test_case['name']}:")
        print(f"  {detector.get_page_type_summary(structure)}")
        print(f"  Key Features: {list(structure.detected_features.keys())}")

if __name__ == "__main__":
    test_page_structure_detection()