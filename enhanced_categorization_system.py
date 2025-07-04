#!/usr/bin/env python3
"""
Enhanced Product Categorization System for Tileshop RAG
Provides comprehensive categorization for better knowledge retrieval and semantic search
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class CategoryInfo:
    """Category information with RAG metadata"""
    primary_category: str
    subcategory: str
    product_type: str
    application_areas: List[str]
    related_products: List[str]
    rag_keywords: List[str]
    installation_complexity: str  # "basic", "intermediate", "advanced"
    typical_use_cases: List[str]

class EnhancedCategorizer:
    """Enhanced categorization system optimized for RAG retrieval"""
    
    def __init__(self):
        self.category_patterns = self._build_category_patterns()
        self.keyword_weights = self._build_keyword_weights()
        
    def _build_category_patterns(self) -> Dict[str, Dict]:
        """Build comprehensive category patterns for product classification"""
        return {
            # TILES - Primary building material
            "tiles": {
                "subcategories": {
                    "ceramic_tiles": {
                        "keywords": ["ceramic", "glazed ceramic", "unglazed ceramic"],
                        "applications": ["walls", "floors", "backsplash", "bathroom", "kitchen"],
                        "rag_keywords": ["ceramic tile", "wall tile", "floor tile", "bathroom tile", "kitchen tile"]
                    },
                    "porcelain_tiles": {
                        "keywords": ["porcelain", "rectified porcelain", "through-body porcelain"],
                        "applications": ["floors", "walls", "outdoor", "high-traffic", "wet areas"],
                        "rag_keywords": ["porcelain tile", "rectified tile", "large format tile", "outdoor tile"]
                    },
                    "natural_stone": {
                        "keywords": ["marble", "granite", "travertine", "limestone", "slate", "quartzite"],
                        "applications": ["floors", "walls", "countertops", "outdoor", "luxury"],
                        "rag_keywords": ["natural stone", "marble tile", "granite tile", "stone care", "sealing"]
                    },
                    "glass_tiles": {
                        "keywords": ["glass", "recycled glass", "frosted glass", "iridescent"],
                        "applications": ["backsplash", "accent walls", "pools", "decorative"],
                        "rag_keywords": ["glass tile", "mosaic glass", "backsplash tile", "pool tile"]
                    },
                    "mosaic_tiles": {
                        "keywords": ["mosaic", "penny round", "hexagon", "subway", "mesh mounted"],
                        "applications": ["accent walls", "backsplash", "decorative", "shower walls"],
                        "rag_keywords": ["mosaic tile", "penny tile", "hexagon tile", "subway tile", "mesh tile"]
                    }
                }
            },
            
            # INSTALLATION MATERIALS - Critical for RAG queries
            "installation_materials": {
                "subcategories": {
                    "thinset_mortar": {
                        "keywords": ["thinset", "mortar", "adhesive mortar", "modified thinset", "unmodified thinset"],
                        "applications": ["tile installation", "floor prep", "wall prep", "large format"],
                        "rag_keywords": ["thinset adhesive", "tile mortar", "floor adhesive", "wall adhesive", "large format thinset"]
                    },
                    "grout": {
                        "keywords": ["grout", "sanded grout", "unsanded grout", "epoxy grout", "urethane grout"],
                        "applications": ["tile joints", "floor grout", "wall grout", "wet areas"],
                        "rag_keywords": ["tile grout", "grout color", "waterproof grout", "grout sealer", "grout repair"]
                    },
                    "adhesives": {
                        "keywords": ["construction adhesive", "tile adhesive", "wood adhesive", "subfloor adhesive"],
                        "applications": ["bonding", "structural", "flooring", "wall mounting"],
                        "rag_keywords": ["construction adhesive", "flooring adhesive", "wall adhesive", "structural adhesive"]
                    },
                    "primers_sealers": {
                        "keywords": ["primer", "sealer", "penetrating sealer", "stone sealer", "grout sealer"],
                        "applications": ["substrate prep", "stone protection", "grout protection", "waterproofing"],
                        "rag_keywords": ["stone sealer", "grout sealer", "tile primer", "substrate primer", "waterproof sealer"]
                    },
                    "caulk_sealants": {
                        "keywords": ["caulk", "sealant", "silicone caulk", "acrylic caulk", "color-matched caulk"],
                        "applications": ["joints", "corners", "transitions", "waterproofing"],
                        "rag_keywords": ["tile caulk", "bathroom caulk", "kitchen caulk", "color matched caulk", "silicone sealant"]
                    }
                }
            },
            
            # TOOLS - Essential for installation queries
            "tools": {
                "subcategories": {
                    "trowels": {
                        "keywords": ["trowel", "notched trowel", "margin trowel", "float trowel", "v-notch", "square notch"],
                        "applications": ["adhesive application", "tile installation", "finishing"],
                        "rag_keywords": ["tile trowel", "notched trowel", "adhesive trowel", "mortar trowel", "installation tools"]
                    },
                    "leveling_systems": {
                        "keywords": ["leveling system", "lippage control", "leveling clips", "wedges", "pliers"],
                        "applications": ["tile leveling", "lippage prevention", "large format tiles"],
                        "rag_keywords": ["tile leveling", "lippage control", "leveling clips", "tile alignment", "large format installation"]
                    },
                    "cutting_tools": {
                        "keywords": ["tile saw", "wet saw", "tile cutter", "nibbling tool", "hole saw"],
                        "applications": ["tile cutting", "hole cutting", "edge cutting", "fitting"],
                        "rag_keywords": ["tile cutting", "wet saw", "tile cutter", "ceramic cutting", "porcelain cutting"]
                    },
                    "installation_accessories": {
                        "keywords": ["spacers", "mixing equipment", "buckets", "sponges", "knee pads"],
                        "applications": ["tile spacing", "material mixing", "installation support"],
                        "rag_keywords": ["tile spacers", "mixing tools", "installation accessories", "tile installation kit"]
                    }
                }
            },
            
            # TRIM & MOLDING - Finishing materials
            "trim_molding": {
                "subcategories": {
                    "tile_trim": {
                        "keywords": ["tile trim", "edge trim", "corner trim", "bullnose", "pencil trim", "t-cove", "cove", "dural", "metal trim", "aluminum", "stainless steel"],
                        "applications": ["tile edges", "corners", "transitions", "finishing"],
                        "rag_keywords": ["tile trim", "edge trim", "corner trim", "tile finishing", "bullnose trim", "metal trim", "t-cove", "cove trim"]
                    },
                    "transition_strips": {
                        "keywords": ["transition strip", "t-molding", "reducer", "threshold", "end cap"],
                        "applications": ["floor transitions", "height changes", "doorways"],
                        "rag_keywords": ["floor transition", "t-molding", "reducer strip", "threshold strip", "doorway transition"]
                    },
                    "baseboards": {
                        "keywords": ["baseboard", "base molding", "quarter round", "shoe molding"],
                        "applications": ["wall base", "floor finishing", "corners"],
                        "rag_keywords": ["baseboard", "base molding", "quarter round", "floor trim", "wall base"]
                    }
                }
            },
            
            # FLOORING - Non-tile flooring options
            "flooring": {
                "subcategories": {
                    "laminate": {
                        "keywords": ["laminate", "laminate plank", "laminate flooring", "click lock"],
                        "applications": ["residential floors", "commercial floors", "floating floors"],
                        "rag_keywords": ["laminate flooring", "click lock flooring", "floating floor", "laminate installation"]
                    },
                    "luxury_vinyl": {
                        "keywords": ["luxury vinyl", "lvt", "lvp", "vinyl plank", "vinyl tile"],
                        "applications": ["residential", "commercial", "wet areas", "basements"],
                        "rag_keywords": ["luxury vinyl", "vinyl plank", "vinyl tile", "waterproof flooring", "lvt flooring"]
                    },
                    "hardwood": {
                        "keywords": ["hardwood", "engineered wood", "solid wood", "wood flooring"],
                        "applications": ["residential", "traditional", "refinishable"],
                        "rag_keywords": ["hardwood flooring", "engineered wood", "wood installation", "wood finishing"]
                    }
                }
            },
            
            # CARE & MAINTENANCE - Important for customer service
            "care_maintenance": {
                "subcategories": {
                    "cleaners": {
                        "keywords": ["cleaner", "tile cleaner", "grout cleaner", "stone cleaner", "daily cleaner"],
                        "applications": ["maintenance", "cleaning", "restoration"],
                        "rag_keywords": ["tile cleaner", "grout cleaner", "stone cleaner", "daily maintenance", "tile care"]
                    },
                    "restoration": {
                        "keywords": ["restoration", "polish", "enhancer", "color enhancer", "shine"],
                        "applications": ["stone enhancement", "grout restoration", "shine restoration"],
                        "rag_keywords": ["stone restoration", "grout restoration", "tile polish", "stone enhancer"]
                    }
                }
            }
        }
    
    def _build_keyword_weights(self) -> Dict[str, float]:
        """Build keyword importance weights for better categorization"""
        return {
            # High importance - product type identifiers
            "thinset": 0.9, "mortar": 0.9, "grout": 0.9, "adhesive": 0.8,
            "porcelain": 0.8, "ceramic": 0.8, "marble": 0.8, "granite": 0.8,
            "trowel": 0.8, "leveling": 0.8, "trim": 0.7, "molding": 0.7,
            "t-cove": 0.9, "cove": 0.8, "dural": 0.8, "metal trim": 0.9,
            "aluminum": 0.7, "stainless steel": 0.7, "brushed": 0.6,
            "quarter round": 0.8, "reducer": 0.8, "threshold": 0.8,
            
            # Medium importance - application areas
            "floor": 0.6, "wall": 0.6, "backsplash": 0.6, "bathroom": 0.5,
            "kitchen": 0.5, "shower": 0.5, "outdoor": 0.5,
            
            # Lower importance - general terms
            "tile": 0.4, "installation": 0.4, "tool": 0.3, "accessory": 0.3
        }
    
    def categorize_product(self, product_data: Dict[str, Any]) -> CategoryInfo:
        """
        Categorize a product based on title, description, and other attributes
        Returns comprehensive category information for RAG optimization
        """
        # Extract text for analysis
        text_content = self._extract_text_content(product_data)
        
        # Score each category
        category_scores = self._score_categories(text_content)
        
        # Determine best category
        best_category = max(category_scores, key=category_scores.get)
        best_subcategory = self._determine_subcategory(text_content, best_category)
        
        # Generate comprehensive category info
        return self._build_category_info(best_category, best_subcategory, text_content, product_data)
    
    def _extract_text_content(self, product_data: Dict[str, Any]) -> str:
        """Extract all relevant text content for analysis"""
        text_parts = []
        
        # Add title (most important)
        if product_data.get('title'):
            text_parts.append(product_data['title'].lower())
        
        # Add description
        if product_data.get('description'):
            text_parts.append(product_data['description'].lower())
        
        # Add specifications if available
        if product_data.get('specifications'):
            if isinstance(product_data['specifications'], dict):
                for key, value in product_data['specifications'].items():
                    text_parts.append(f"{key} {value}".lower())
            else:
                text_parts.append(str(product_data['specifications']).lower())
        
        # Add brand and other attributes
        for field in ['brand', 'color', 'finish', 'material', 'size_shape']:
            if product_data.get(field):
                text_parts.append(str(product_data[field]).lower())
        
        return ' '.join(text_parts)
    
    def _score_categories(self, text_content: str) -> Dict[str, float]:
        """Score each category based on keyword matches and weights"""
        scores = {}
        
        for category, category_data in self.category_patterns.items():
            score = 0.0
            
            # Check each subcategory
            for subcategory, subcat_data in category_data["subcategories"].items():
                # Score keywords
                for keyword in subcat_data["keywords"]:
                    if keyword.lower() in text_content:
                        weight = self.keyword_weights.get(keyword.lower(), 0.5)
                        score += weight
                
                # Score RAG keywords (higher weight)
                for rag_keyword in subcat_data["rag_keywords"]:
                    if rag_keyword.lower() in text_content:
                        score += 0.7
            
            scores[category] = score
        
        return scores
    
    def _determine_subcategory(self, text_content: str, category: str) -> str:
        """Determine the best subcategory within a category"""
        if category not in self.category_patterns:
            return "other"
        
        subcategory_scores = {}
        
        for subcategory, subcat_data in self.category_patterns[category]["subcategories"].items():
            score = 0.0
            
            # Score keywords
            for keyword in subcat_data["keywords"]:
                if keyword.lower() in text_content:
                    weight = self.keyword_weights.get(keyword.lower(), 0.5)
                    score += weight
            
            subcategory_scores[subcategory] = score
        
        if not subcategory_scores or max(subcategory_scores.values()) == 0:
            return "other"
        
        return max(subcategory_scores, key=subcategory_scores.get)
    
    def _build_category_info(self, category: str, subcategory: str, text_content: str, product_data: Dict[str, Any] = None) -> CategoryInfo:
        """Build comprehensive category information"""
        if category not in self.category_patterns:
            return CategoryInfo(
                primary_category="uncategorized",
                subcategory="other",
                product_type="unknown",
                application_areas=["general"],
                related_products=[],
                rag_keywords=["product"],
                installation_complexity="basic",
                typical_use_cases=["general use"]
            )
        
        subcat_data = self.category_patterns[category]["subcategories"].get(subcategory, {})
        
        # Determine installation complexity
        complexity = "basic"
        if any(keyword in text_content for keyword in ["large format", "natural stone", "mosaic"]):
            complexity = "intermediate"
        if any(keyword in text_content for keyword in ["epoxy", "structural", "commercial"]):
            complexity = "advanced"
        
        # Generate related products
        related_products = self._generate_related_products(category, subcategory)
        
        # Prioritize extracted applications over hardcoded ones
        extracted_applications = product_data.get('_extracted_applications') if product_data else None
        
        if extracted_applications:
            # Use real extracted applications from specifications
            use_cases = extracted_applications
            application_areas = extracted_applications
            print(f"  🎯 Using extracted applications: {extracted_applications}")
        else:
            # Fall back to hardcoded applications from category patterns
            use_cases = subcat_data.get("applications", ["general use"])
            application_areas = subcat_data.get("applications", ["general"])
            print(f"  🔄 Using hardcoded applications: {application_areas}")
        
        return CategoryInfo(
            primary_category=category,
            subcategory=subcategory,
            product_type=f"{category}_{subcategory}",
            application_areas=application_areas,
            related_products=related_products,
            rag_keywords=subcat_data.get("rag_keywords", []),
            installation_complexity=complexity,
            typical_use_cases=use_cases
        )
    
    def _generate_related_products(self, category: str, subcategory: str) -> List[str]:
        """Generate related products for cross-selling and RAG enhancement"""
        related_map = {
            "tiles": ["grout", "thinset", "spacers", "trowels", "sealer"],
            "installation_materials": ["tiles", "tools", "primers"],
            "tools": ["installation_materials", "accessories"],
            "trim_molding": ["tiles", "adhesives", "cutting_tools"],
            "flooring": ["trim_molding", "installation_materials"],
            "care_maintenance": ["tiles", "grout", "stone_products"]
        }
        
        return related_map.get(category, [])
    
    def get_rag_keywords_for_category(self, category: str, subcategory: str = None) -> List[str]:
        """Get RAG keywords for a specific category/subcategory"""
        if category not in self.category_patterns:
            return []
        
        keywords = []
        
        if subcategory and subcategory in self.category_patterns[category]["subcategories"]:
            keywords.extend(self.category_patterns[category]["subcategories"][subcategory]["rag_keywords"])
        else:
            # Get all keywords for the category
            for subcat_data in self.category_patterns[category]["subcategories"].values():
                keywords.extend(subcat_data["rag_keywords"])
        
        return list(set(keywords))  # Remove duplicates
    
    def get_products_for_query(self, query: str) -> List[str]:
        """Get relevant product categories for a RAG query"""
        query_lower = query.lower()
        relevant_categories = []
        
        for category, category_data in self.category_patterns.items():
            for subcategory, subcat_data in category_data["subcategories"].items():
                # Check if query matches any RAG keywords
                for rag_keyword in subcat_data["rag_keywords"]:
                    if rag_keyword.lower() in query_lower:
                        relevant_categories.append(f"{category}_{subcategory}")
                        break
        
        return relevant_categories

def test_categorization():
    """Test the enhanced categorization system"""
    categorizer = EnhancedCategorizer()
    
    # Test products
    test_products = [
        {
            "title": "Ardex X4 Modified Thinset Mortar - 50 lb",
            "description": "Premium modified thinset adhesive for large format tiles",
            "brand": "Ardex"
        },
        {
            "title": "Mapei Keracolor U Unsanded Grout - Warm Gray",
            "description": "Unsanded grout for narrow joints up to 1/8 inch",
            "brand": "Mapei"
        },
        {
            "title": "Carrara Marble Polished Tile - 12x24 in",
            "description": "Natural Carrara marble tiles with polished finish",
            "brand": "Natural Stone"
        }
    ]
    
    print("Enhanced Categorization Test Results:")
    print("=" * 50)
    
    for i, product in enumerate(test_products, 1):
        category_info = categorizer.categorize_product(product)
        print(f"\nProduct {i}: {product['title']}")
        print(f"Category: {category_info.primary_category}")
        print(f"Subcategory: {category_info.subcategory}")
        print(f"RAG Keywords: {', '.join(category_info.rag_keywords[:3])}")
        print(f"Applications: {', '.join(category_info.application_areas)}")
        print(f"Related Products: {', '.join(category_info.related_products)}")

if __name__ == "__main__":
    test_categorization()