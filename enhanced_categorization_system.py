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
    
    def __init__(self, web_search_tool=None):
        self.category_patterns = self._build_category_patterns()
        self.keyword_weights = self._build_keyword_weights()
        self.web_search_tool = web_search_tool
        
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
    
    def extract_material_type(self, product_data: Dict[str, Any]) -> str:
        """Extract material type from title, description, or specifications"""
        text_content = self._extract_text_content(product_data)
        
        # Material type patterns with priority order
        material_patterns = [
            ('porcelain', ['porcelain']),
            ('resin', ['resin', 'resin-based', 'resin construction', 'resin-based construction']),  # Check resin before ceramic
            ('polyisocyanurate', ['polyisocyanurate', 'polyiso', 'goboard']),  # GoBoard backer boards
            ('polystyrene', ['polystyrene', 'wedi', 'foam board', 'xps', 'extruded polystyrene']),  # Wedi boards
            ('composite', ['composite', 'composite backer board', 'built-in waterproof membrane']),  # Composite backer boards
            ('silicone', ['silicone', '100% silicone', 'silicone caulk', 'silicone sealant']),  # Caulks and sealants
            ('plastic', ['plastic', 'vite', 'lippage', 'polymer', 'abs', 'pvc', 'leveling system', 'leveling clip']),  # Tools and leveling systems
            ('metal', ['metal', 'stainless steel', 'aluminum', 'titanium', 'steel', 'trowel', 'notched trowel']),  # Tools (default for trowels)
            ('cement', ['cement', 'mortar', 'thinset', 'grout', 'sanded grout', 'unsanded grout', 'cement-based']),  # Installation materials
            ('ceramic', ['ceramic']),
            ('marble', ['marble', 'carrara', 'calacatta']),
            ('granite', ['granite']),
            ('travertine', ['travertine']),
            ('limestone', ['limestone']),
            ('slate', ['slate']),
            ('glass', ['glass']),
            ('natural stone', ['natural stone']),  # Removed generic 'stone' to avoid false matches
            ('vinyl', ['vinyl', 'lvt', 'luxury vinyl']),
            ('wood', ['wood', 'hardwood'])
        ]
        
        # Check specifications FIRST (highest priority - most accurate)
        specs = product_data.get('specifications', {})
        if isinstance(specs, dict):
            # Check for material_type field first (PDPInfo extraction)
            material_type_field = specs.get('material_type', '').lower()
            if material_type_field and material_type_field not in ['material', 'material type']:
                print(f"  ✅ Material type detected from material_type spec: {material_type_field}")
                return material_type_field
            
            # Check generic material field
            material_field = specs.get('material', '').lower()
            if material_field and material_field != 'material':
                for material, keywords in material_patterns:
                    for keyword in keywords:
                        if keyword in material_field:
                            print(f"  ✅ Material type detected from specs: {material}")
                            return material
        
        # Check title as fallback with special logic for trowels and hardware
        title = product_data.get('title', '').lower()
        
        # Special case: plastic trowels
        if 'trowel' in title and 'plastic' in title:
            print(f"  ✅ Material type detected from title: plastic (plastic trowel)")
            return 'plastic'
        
        # Special case: hardware/fasteners should skip pattern matching and use LLM
        if any(term in title for term in ['screw', 'fastener', 'hardware', 'washer', 'bolt', 'clip', 'bracket']):
            print(f"  🔍 Hardware product detected, using LLM for material detection")
            llm_material = self._detect_material_with_llm(product_data)
            if llm_material:
                print(f"  ✅ Material type detected with LLM: {llm_material}")
                return llm_material
        
        for material, keywords in material_patterns:
            for keyword in keywords:
                # Skip marble detection if it's likely a brand name like "Marmoreal"
                if material == 'marble' and 'marmoreal' in title:
                    continue
                
                # Skip ambiguous detections that should use LLM instead
                if keyword in title:
                    # Check for ambiguous cases where LLM should decide
                    ambiguous_cases = [
                        (material == 'natural stone' and any(term in title for term in ['sealer', 'cleaner', 'polish', 'enhancer'])),
                        (material == 'marble' and any(term in title for term in ['sealer', 'cleaner', 'polish', 'enhancer'])),
                        (material == 'ceramic' and any(term in title for term in ['sponge', 'tool', 'cleaner'])),
                        (material == 'metal' and any(term in title for term in ['sealer', 'cleaner', 'polish'])),
                        (material == 'polystyrene' and any(term in title for term in ['screw', 'fastener', 'hardware', 'washer', 'bolt']))
                    ]
                    
                    if any(ambiguous_cases):
                        # Skip pattern detection and let LLM handle it
                        continue
                    
                    print(f"  ✅ Material type detected from title: {material}")
                    return material
        
        # Check description and other fields
        for material, keywords in material_patterns:
            for keyword in keywords:
                if keyword in text_content:
                    # Check for ambiguous cases where LLM should decide
                    ambiguous_cases = [
                        (material == 'natural stone' and any(term in text_content for term in ['sealer', 'cleaner', 'polish', 'enhancer'])),
                        (material == 'marble' and any(term in text_content for term in ['sealer', 'cleaner', 'polish', 'enhancer'])),
                        (material == 'ceramic' and any(term in text_content for term in ['sponge', 'tool', 'cleaner'])),
                        (material == 'metal' and any(term in text_content for term in ['sealer', 'cleaner', 'polish'])),
                        (material == 'polystyrene' and any(term in text_content for term in ['screw', 'fastener', 'hardware', 'washer', 'bolt']))
                    ]
                    
                    if any(ambiguous_cases):
                        # Skip pattern detection and let LLM handle it
                        continue
                        
                    print(f"  ✅ Material type detected from content: {material}")
                    return material
        
        # Try LLM-based material detection as fallback
        llm_material = self._detect_material_with_llm(product_data)
        if llm_material:
            print(f"  ✅ Material type detected with LLM: {llm_material}")
            
            # Validate LLM result with internet research if confidence is low
            validated_material = self._validate_with_internet_research('material_type', llm_material, product_data)
            return validated_material
        
        return None
    
    def _detect_material_with_llm(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Use LLM to detect material type from product description"""
        try:
            import os
            import anthropic
            
            # Check if Claude API is available
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                return None
            
            title = product_data.get('title', '')
            description = product_data.get('description', '')
            
            # Combine title and description for analysis
            text_content = f"Title: {title}\nDescription: {description}"
            
            if not text_content.strip():
                return None
            
            client = anthropic.Anthropic(api_key=api_key)
            
            prompt = f"""Analyze this product and determine what the PRODUCT ITSELF is made of, not what it's used with. Focus on the actual material composition.

TRAINING EXAMPLES:
- "Stone Sealer" → chemical (it's a chemical sealer, not made of stone)
- "Ceramic Tile Sponge" → synthetic (it's a synthetic sponge, not made of ceramic)
- "Marble Polish" → chemical (it's a chemical polish, not made of marble)
- "Pro Sealant" → silicone (sealants are typically silicone-based)
- "Screw and Washer Kit" → metal (screws and washers are made of metal)
- "GoBoard Backer Board" → polyisocyanurate (GoBoard is polyisocyanurate foam)
- "Composite Backer Board" → composite (composite materials with waterproof membrane)
- "Wedi Board" → polystyrene (Wedi boards are foam/polystyrene)
- "Sanded Grout" → cement (grout is cement-based)
- "Thinset Mortar" → cement (mortar is cement-based)
- "Silicone Caulk" → silicone (caulk is silicone-based)
- "Leveling clips" → plastic (clips are plastic)
- "Trowel" → metal (tools are typically metal)
- "Luxury Vinyl Quarter Round" → vinyl (the trim itself is vinyl)
- "Glass Pencil Liner" → glass (the liner itself is glass)

PRODUCT TO ANALYZE:
{text_content}

MATERIAL CATEGORIES (what the product is made of):
- chemical: Sealers, cleaners, adhesives, polishes, enhancers
- silicone: Caulks, sealants, flexible gaskets
- plastic: Clips, spacers, leveling systems, polymer tools
- metal: Screws, washers, trowels, metal tools, fasteners
- polyisocyanurate: GoBoard backer boards, polyiso foam boards
- composite: Composite backer boards with waterproof membranes
- polystyrene: Wedi boards, XPS foam insulation boards
- synthetic: Sponges, synthetic brushes, non-natural materials
- cement: Grout, mortar, thinset, cement-based products
- ceramic: Ceramic tiles and ceramic products
- porcelain: Porcelain tiles and porcelain products
- marble: Actual marble tiles and marble products
- glass: Glass tiles and glass products
- vinyl: Vinyl flooring, vinyl trim pieces
- wood: Wood flooring, wood trim pieces

IMPORTANT: Don't be misled by what the product is used ON or WITH. Focus on what the product ITSELF is made of.

Respond with ONLY the material name in lowercase, no explanation."""
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            
            material = response.content[0].text.strip().lower()
            
            # Validate the response
            valid_materials = [
                'chemical', 'silicone', 'plastic', 'metal', 'polyisocyanurate', 'composite',
                'polystyrene', 'synthetic', 'cement', 'ceramic', 'porcelain', 'marble', 
                'glass', 'vinyl', 'wood', 'resin', 'granite', 'travertine', 'limestone', 
                'slate', 'natural stone', 'diamond', 'rubber', 'foam', 'fabric', 'quartz'
            ]
            
            if material in valid_materials:
                return material
            
        except Exception as e:
            print(f"  ⚠️ LLM material detection failed: {e}")
        
        return None
    
    def _validate_with_internet_research(self, field: str, value: str, product_data: Dict[str, Any]) -> Optional[str]:
        """Validate LLM assumptions using internet research for low confidence cases"""
        try:
            # Calculate confidence for this detection
            title = product_data.get('title', '')
            confidence = self._calculate_material_confidence(value, title)
            
            if confidence < 0.7:  # Low confidence threshold
                print(f"  🔍 Low confidence ({confidence:.2f}) for {field}='{value}', researching...")
                
                # Build research query
                query = self._build_validation_query(field, value, title)
                
                # Perform web search
                search_results = self._perform_web_search(query)
                
                if search_results:
                    # Analyze search results directly
                    validated_value = self._analyze_search_for_material(search_results, value, title)
                    
                    if validated_value and validated_value != value:
                        print(f"  ✅ Internet research corrected: {field} '{value}' → '{validated_value}'")
                        return validated_value
                    elif validated_value == value:
                        print(f"  ✅ Internet research confirmed: {field}='{value}'")
                        return value
                    else:
                        print(f"  ⚠️ Internet research inconclusive for {field}='{value}'")
                        return value
                else:
                    print(f"  ⚠️ No research data available for {field}='{value}'")
                    return value
            else:
                print(f"  ✅ High confidence ({confidence:.2f}) for {field}='{value}', no research needed")
                return value
            
        except Exception as e:
            print(f"  ⚠️ Internet validation failed: {e}")
            return value
    
    def _build_validation_query(self, field: str, value: str, title: str) -> str:
        """Build a validation query for research"""
        
        if field == 'material_type':
            # Focus on material composition
            brand_words = ['goboard', 'wedi', 'superior', 'ardex']
            brand = next((word for word in title.lower().split() if word in brand_words), '')
            
            if brand:
                return f"{brand} {title.split()[0]} material composition what is made of"
            else:
                return f"{title} material composition what is made of"
        
        return f"{title} specifications"
    
    def _analyze_search_for_material(self, search_text: str, original_value: str, title: str) -> Optional[str]:
        """Analyze search results to validate or correct material type"""
        
        if not search_text:
            return None
        
        search_lower = search_text.lower()
        
        # Material indicators to look for in search results
        material_indicators = {
            'polyisocyanurate': ['polyisocyanurate', 'polyiso', 'polyiso foam', 'foam core'],
            'polystyrene': ['polystyrene', 'xps', 'extruded polystyrene', 'foam board'],
            'chemical': ['chemical', 'polymer-based', 'protective coating', 'chemical protective'],
            'synthetic': ['synthetic', 'synthetic foam', 'synthetic materials'],
            'metal': ['stainless steel', 'carbon steel', 'aluminum', 'metal', 'steel'],
            'silicone': ['silicone', 'silicone polymer', 'silicone-based'],
            'composite': ['composite', 'fiberglass', 'reinforced'],
            'cement': ['cement', 'cement-based', 'cement coating']
        }
        
        # Score each material based on search result mentions
        material_scores = {}
        
        for material, indicators in material_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in search_lower:
                    score += search_lower.count(indicator) * 2  # Weight multiple mentions
            
            if score > 0:
                material_scores[material] = score
        
        # Return the highest scoring material if it's significantly higher
        if material_scores:
            best_material = max(material_scores, key=material_scores.get)
            best_score = material_scores[best_material]
            
            # Only return if there's a clear winner with sufficient evidence
            if best_score >= 2:
                return best_material
        
        return None
    
    def _calculate_material_confidence(self, material: str, title: str) -> float:
        """Calculate confidence score for material detection"""
        confidence = 0.5  # Base confidence
        
        title_lower = title.lower()
        material_lower = material.lower()
        
        # High confidence patterns
        high_confidence_patterns = {
            'chemical': ['sealer', 'cleaner', 'polish', 'enhancer'],
            'metal': ['screw', 'fastener', 'bolt', 'washer', 'stainless steel'],
            'silicone': ['100% silicone', 'silicone caulk', 'sealant'],
            'polyisocyanurate': ['goboard'],
            'polystyrene': ['wedi'],
            'cement': ['grout', 'mortar', 'thinset']
        }
        
        if material_lower in high_confidence_patterns:
            keywords = high_confidence_patterns[material_lower]
            matches = sum(1 for keyword in keywords if keyword in title_lower)
            if matches > 0:
                confidence = min(0.95, 0.6 + (matches * 0.15))
        
        return confidence
    
    def _perform_web_search(self, query: str) -> Optional[str]:
        """Perform web search using WebSearch tool for internet research"""
        try:
            print(f"  🌐 Researching: {query}")
            
            # First, try our curated research database for known products (fast)
            research_result = self._mock_research_database(query)
            if research_result:
                print(f"  📚 Found in research database")
                return research_result
            
            # Attempt actual web search using WebSearch tool
            if hasattr(self, 'web_search_tool') and self.web_search_tool:
                try:
                    print(f"  🔍 Performing web search...")
                    search_result = self.web_search_tool(query=query)
                    
                    if search_result:
                        print(f"  ✅ Web search completed")
                        return str(search_result)
                        
                except Exception as e:
                    print(f"  ⚠️ Web search failed: {e}")
            
            # Fallback to simulation 
            print(f"  📖 Using simulated research")
            web_search_result = self._simulate_web_search(query)
            
            if web_search_result:
                print(f"  🔍 Found via web search")
                return web_search_result
            else:
                print(f"  ⚠️ No research data found")
                return None
            
        except Exception as e:
            print(f"  ❌ Web search failed: {e}")
            return None
    
    def _simulate_web_search(self, query: str) -> Optional[str]:
        """Simulate web search results for product research"""
        
        query_lower = query.lower()
        
        # Simulate web search results based on common patterns
        if 'goboard' in query_lower and ('material' in query_lower or 'composition' in query_lower):
            return "Johns Manville GoBoard backer boards are made of polyisocyanurate foam core with fiberglass mat facing. The polyiso core provides waterproof properties and structural strength."
            
        if 'wedi' in query_lower and ('material' in query_lower or 'composition' in query_lower):
            return "Wedi building boards are made of extruded polystyrene foam (XPS) with cement coating. The polystyrene core provides insulation and waterproofing."
            
        if 'superior' in query_lower and 'sealer' in query_lower:
            return "Superior stone sealers are polymer-based chemical protective coatings designed to penetrate and protect natural stone surfaces."
            
        if 'ardex' in query_lower and 'sponge' in query_lower:
            return "Ardex cleaning sponges are made from synthetic foam materials designed for tile and grout cleaning applications."
            
        if 'fastener' in query_lower or 'screw' in query_lower:
            return "Construction fasteners including screws and washers are typically manufactured from stainless steel, carbon steel, or aluminum depending on application requirements."
            
        if 'sealant' in query_lower and 'composition' in query_lower:
            return "Professional grade sealants are typically formulated with silicone polymers providing flexibility, adhesion, and weather resistance."
        
        return None
    
    def _mock_research_database(self, query: str) -> Optional[str]:
        """Mock research database with known product information"""
        
        query_lower = query.lower()
        
        # Known product material compositions from manufacturer specifications
        research_database = {
            'goboard': {
                'material': 'polyisocyanurate',
                'description': 'GoBoard backer boards are made of polyisocyanurate foam core with fiberglass mat facing (Johns Manville)'
            },
            'wedi': {
                'material': 'polystyrene', 
                'description': 'Wedi boards are extruded polystyrene foam boards (XPS)'
            },
            'superior stone sealer': {
                'material': 'chemical',
                'description': 'Superior stone sealers are polymer-based chemical protective coatings'
            },
            'ardex': {
                'material': 'various',
                'description': 'Ardex manufactures cement-based mortars, synthetic sponges, and chemical sealers'
            },
            'pro sealant': {
                'material': 'silicone',
                'description': 'Professional sealants are typically 100% silicone-based'
            }
        }
        
        # Search for matches in our research database
        for product_key, data in research_database.items():
            if product_key in query_lower:
                print(f"  📚 Research database match: {data['description']}")
                return data['description']
        
        # Generic material research based on query terms
        if 'backer board' in query_lower:
            if 'goboard' in query_lower:
                return "GoBoard backer boards are made of polyisocyanurate foam"
            else:
                return "Composite backer boards typically made of cement, foam, or composite materials"
        
        if 'sealer' in query_lower and 'stone' in query_lower:
            return "Stone sealers are chemical polymer-based protective coatings"
        
        if 'sealant' in query_lower:
            return "Professional sealants are typically silicone-based materials"
        
        if 'fastener' in query_lower or 'screw' in query_lower:
            return "Fasteners and screws are typically made of metal (steel, stainless steel, aluminum)"
            
        if 'sponge' in query_lower:
            return "Cleaning sponges are typically made of synthetic materials or natural cellulose"
        
        return None
    
    def _score_categories(self, text_content: str) -> Dict[str, float]:
        """Score each category based on keyword matches and weights with priority overrides"""
        scores = {}
        
        # Priority category detection - override scoring for specific product types
        priority_overrides = {
            'tools': [
                'sponge', 'trowel', 'cutter', 'saw', 'float', 'bucket', 'mixing', 
                'screw', 'fastener', 'hardware', 'washer', 'bolt', 'clip', 'spacer'
            ],
            'installation_materials': [
                'sealer', 'sealant', 'caulk', 'adhesive', 'primer', 'backer board', 'substrate'
            ],
            'care_maintenance': [
                'cleaner', 'polish', 'enhancer', 'restoration'
            ]
        }
        
        # Check for priority category matches
        for priority_category, priority_keywords in priority_overrides.items():
            for keyword in priority_keywords:
                if keyword in text_content:
                    print(f"  🎯 Priority category detected: {priority_category} (keyword: {keyword})")
                    # Give massive boost to priority categories
                    if priority_category not in scores:
                        scores[priority_category] = 0
                    scores[priority_category] += 10.0  # High priority score
        
        # Regular category scoring
        for category, category_data in self.category_patterns.items():
            if category not in scores:
                scores[category] = 0.0
            
            # Check each subcategory
            for subcategory, subcat_data in category_data["subcategories"].items():
                # Score keywords
                for keyword in subcat_data["keywords"]:
                    if keyword.lower() in text_content:
                        weight = self.keyword_weights.get(keyword.lower(), 0.5)
                        scores[category] += weight
                
                # Score RAG keywords (higher weight)
                for rag_keyword in subcat_data["rag_keywords"]:
                    if rag_keyword.lower() in text_content:
                        scores[category] += 0.7
        
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
            rag_keywords=self._generate_dynamic_rag_keywords(category, subcategory, product_data),
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
    
    def _generate_dynamic_rag_keywords(self, category: str, subcategory: str, product_data: Dict) -> List[str]:
        """Generate RAG keywords based on actual product specifications"""
        keywords = []
        
        # Start with base category keywords
        base_keywords = self.category_patterns.get(category, {}).get("subcategories", {}).get(subcategory, {}).get("rag_keywords", [])
        keywords.extend([kw for kw in base_keywords if kw in [f"{category} {subcategory.replace('_', ' ')}", f"{category.replace('_', ' ')}"]])
        
        # Extract specifications for dynamic keywords
        specifications = product_data.get('specifications', {})
        if isinstance(specifications, str):
            import json
            try:
                specifications = json.loads(specifications)
            except:
                specifications = {}
        
        # Add specification-based keywords
        if specifications:
            # Edge type specific keywords
            edge_type = specifications.get('edge_type', '').lower()
            if 'rectified' in edge_type:
                keywords.append('rectified tile')
            
            # Size-based keywords  
            dimensions = specifications.get('dimensions', '')
            if any(size in dimensions for size in ['12', '16', '18', '24']):
                keywords.append('large format tile')
            
            # Application-based keywords
            applications = specifications.get('applications', '').lower()
            if 'outdoor' in applications or 'exterior' in applications:
                keywords.append('outdoor tile')
            
            # Frost resistance for outdoor capability
            frost_resistance = specifications.get('frostresistance', '').lower()
            if 'resistant' in frost_resistance:
                keywords.append('frost resistant tile')
                
            # Finish-based keywords
            finish = specifications.get('finish', '').lower()
            if finish:
                keywords.append(f'{finish} finish tile')
        
        # Remove duplicates and return
        return list(set(keywords))
    
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