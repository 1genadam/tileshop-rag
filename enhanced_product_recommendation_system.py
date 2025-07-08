#!/usr/bin/env python3
"""
Enhanced Product Recommendation System
Based on expert tile installation knowledge and complete project thinking
Integrates with enhanced LLM categorization for accurate recommendations
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enhanced_categorization_system import EnhancedCategorizer

@dataclass
class ProductRecommendation:
    """Structured product recommendation with installation context"""
    sku: str
    name: str
    category: str
    subcategory: str
    purpose: str
    installation_step: str
    essential: bool
    price_range: str
    quantity_guidance: str
    application_notes: str

@dataclass
class InstallationProject:
    """Complete installation project with all required materials"""
    primary_product: Dict[str, Any]
    substrate_prep: List[ProductRecommendation]
    installation_materials: List[ProductRecommendation]
    tools_equipment: List[ProductRecommendation]
    finishing_materials: List[ProductRecommendation]
    specialty_products: List[ProductRecommendation]
    installation_sequence: List[str]
    total_estimated_cost: float
    project_complexity: str

class EnhancedProductRecommendationSystem:
    """Enhanced product recommendation system with expert installation knowledge"""
    
    def __init__(self):
        self.categorizer = EnhancedCategorizer()
        self.installation_knowledge = self._build_installation_knowledge()
        self.product_database = self._build_product_database()
        
    def _build_installation_knowledge(self) -> Dict[str, Any]:
        """Build comprehensive installation knowledge base"""
        return {
            "tile_size_categories": {
                "large_format": {
                    "sizes": ["24x", "18x", "16x", "15x", "14x", "13x"],
                    "thinset": "LFT (Latex-Fortified Thinset)",
                    "trowel_size": "1/2 inch or Euro trowel",
                    "special_requirements": ["leveling_system", "back_butter"]
                },
                "standard_format": {
                    "sizes": ["12x", "6x", "4x", "3x"],
                    "thinset": "Premium Thinset",
                    "trowel_size": "1/4 inch",
                    "special_requirements": []
                },
                "mosaic_small": {
                    "sizes": ["2x", "1x", "penny", "hex"],
                    "thinset": "Premium Thinset",
                    "trowel_size": "3/16 inch",
                    "special_requirements": ["mesh_backing"]
                }
            },
            
            "application_areas": {
                "bathroom_floor": {
                    "waterproofing": "Backer-Lite Underlayment",
                    "substrate_prep": "1/4 inch trowel under backer-lite",
                    "additional_protection": "Waterproof membrane",
                    "drainage": "Slope requirements",
                    "special_products": ["slip_resistant_sealer"]
                },
                "bathroom_wall": {
                    "waterproofing": "Backer-Lite or Wedi Panels",
                    "substrate_prep": "Proper fastening",
                    "additional_protection": "Waterproof membrane",
                    "special_products": ["silicone_sealant"]
                },
                "shower_floor": {
                    "pan_system": "Wedi Shower Pan",
                    "tile_size_limit": "3 inches for center drain",
                    "linear_drain": "Large format acceptable",
                    "waterproofing": "Complete system approach",
                    "special_products": ["wedi_sealant", "drain_integration"]
                },
                "shower_walls": {
                    "panel_system": "Wedi Shower Panels",
                    "niche_integration": "Wedi Niche with threshold",
                    "waterproofing": "Complete system approach",
                    "design_principle": "Niche floor matches shower floor",
                    "special_products": ["wedi_sealant", "niche_threshold"]
                },
                "kitchen_backsplash": {
                    "substrate_prep": "Clean, level drywall",
                    "thinset": "Premium Thinset",
                    "special_considerations": "Heat resistance",
                    "finishing": "Silicone at countertop"
                },
                "kitchen_floor": {
                    "durability": "High traffic rated",
                    "slip_resistance": "Textured surface",
                    "maintenance": "Easy cleaning",
                    "special_products": ["slip_resistant_sealer"]
                }
            },
            
            "material_specific_requirements": {
                "natural_stone": {
                    "sealing": "Before and after grouting",
                    "grout_type": "Non-acidic grout",
                    "special_cleaners": "Stone-safe products",
                    "maintenance": "Regular sealing schedule"
                },
                "porcelain": {
                    "cutting": "Diamond blade required",
                    "drilling": "Diamond core bits",
                    "thinset": "LFT recommended",
                    "special_tools": ["euro_trowel"]
                },
                "ceramic": {
                    "standard_installation": "Premium thinset",
                    "cutting": "Standard tile cutter",
                    "drilling": "Carbide bits",
                    "maintenance": "Standard cleaning"
                },
                "glass": {
                    "thinset": "Non-sag thinset",
                    "cutting": "Score and snap",
                    "special_tools": ["glass_cutter"],
                    "handling": "Careful transport"
                }
            },
            
            "installation_sequence": [
                "1. Substrate preparation and leveling",
                "2. Waterproofing installation (if required)",
                "3. Layout and measurement",
                "4. Thinset application",
                "5. Tile installation with leveling system",
                "6. Cleanup and curing (24 hours)",
                "7. Grout application",
                "8. Grout cleanup and curing (72 hours)",
                "9. Sealer application",
                "10. Final cleanup and inspection"
            ]
        }
    
    def _build_product_database(self) -> Dict[str, Any]:
        """Build comprehensive product database with SKUs and specifications"""
        return {
            "thinset_mortars": {
                "lft_thinset": {
                    "sku": "LFT-001",
                    "name": "LFT Latex-Fortified Thinset",
                    "applications": ["large_format", "porcelain", "natural_stone"],
                    "coverage": "50 sq ft per bag",
                    "cure_time": "24 hours",
                    "price_range": "$35-45"
                },
                "premium_thinset": {
                    "sku": "PT-001", 
                    "name": "Premium Thinset Mortar",
                    "applications": ["ceramic", "standard_format"],
                    "coverage": "60 sq ft per bag",
                    "cure_time": "24 hours",
                    "price_range": "$25-35"
                }
            },
            
            "underlayments": {
                "backer_lite": {
                    "sku": "329809",
                    "name": "Superior Backer-Lite Underlayment",
                    "applications": ["bathroom", "wet_areas", "waterproofing"],
                    "coverage": "50 sq ft per sheet",
                    "thickness": "1/4 inch",
                    "price_range": "$45-55"
                },
                "permat": {
                    "sku": "PM-001",
                    "name": "Permat Crack Isolation Membrane",
                    "applications": ["dry_areas", "crack_prevention"],
                    "coverage": "100 sq ft per roll",
                    "thickness": "1/8 inch",
                    "price_range": "$35-45"
                }
            },
            
            "tools_equipment": {
                "quarter_inch_trowel": {
                    "sku": "T-025",
                    "name": "1/4 Inch Notched Trowel",
                    "applications": ["backer_lite", "small_format"],
                    "material": "Stainless steel",
                    "price_range": "$25-35"
                },
                "half_inch_trowel": {
                    "sku": "T-050",
                    "name": "1/2 Inch Notched Trowel",
                    "applications": ["large_format", "over_backer_lite"],
                    "material": "Stainless steel",
                    "price_range": "$35-45"
                },
                "euro_trowel": {
                    "sku": "ET-001",
                    "name": "Euro Trowel System",
                    "applications": ["large_format", "professional"],
                    "material": "Premium steel",
                    "price_range": "$75-95"
                }
            },
            
            "leveling_systems": {
                "lippage_system": {
                    "sku": "LS-001",
                    "name": "Tile Leveling System",
                    "applications": ["all_tiles", "lippage_prevention"],
                    "components": ["caps", "straps", "pliers"],
                    "price_range": "$45-65"
                },
                "vite_system": {
                    "sku": "VS-001",
                    "name": "Vite Leveling System",
                    "applications": ["professional", "large_format"],
                    "components": ["bases", "caps", "pliers"],
                    "price_range": "$65-85"
                }
            },
            
            "grout_products": {
                "excel_standard_white": {
                    "sku": "ESW-001",
                    "name": "Excel Standard White Grout",
                    "type": "Sanded",
                    "applications": ["standard_joints", "most_tiles"],
                    "coverage": "100 sq ft per bag",
                    "price_range": "$25-35"
                }
            },
            
            "sealers": {
                "liquid_sealer": {
                    "sku": "LS-SEAL",
                    "name": "Liquid Tile & Grout Sealer",
                    "applications": ["slip_resistance", "protection"],
                    "coverage": "200 sq ft per bottle",
                    "price_range": "$25-35"
                }
            },
            
            "finishing_products": {
                "silicone_white": {
                    "sku": "SIL-W",
                    "name": "Excel Standard White 100% Silicone",
                    "applications": ["edges", "transitions", "waterproofing"],
                    "coverage": "Linear feet per tube",
                    "price_range": "$15-25"
                }
            },
            
            "thresholds": {
                "bianco_puro": {
                    "sku": "BP-TH",
                    "name": "Bianco Puro Threshold",
                    "applications": ["transitions", "doorways"],
                    "sizes": ["Various lengths"],
                    "price_range": "$45-75"
                }
            },
            
            "shower_systems": {
                "wedi_shower_pan": {
                    "sku": "WEDI-PAN",
                    "name": "Wedi Waterproof Shower Pan",
                    "applications": ["shower_floor", "waterproofing"],
                    "sizes": ["Custom sizes available"],
                    "price_range": "$200-400"
                },
                "wedi_panels": {
                    "sku": "WEDI-PANEL",
                    "name": "Wedi Shower Wall Panels",
                    "applications": ["shower_walls", "waterproofing"],
                    "sizes": ["4x8 ft standard"],
                    "price_range": "$150-250"
                },
                "wedi_niche": {
                    "sku": "WEDI-NICHE",
                    "name": "Wedi Shower Niche",
                    "applications": ["shower_storage", "waterproof"],
                    "sizes": ["Multiple sizes"],
                    "price_range": "$100-200"
                },
                "wedi_sealant": {
                    "sku": "WEDI-SEAL",
                    "name": "Wedi Sealant",
                    "applications": ["wedi_system", "waterproofing"],
                    "coverage": "50 linear feet",
                    "price_range": "$25-35"
                }
            },
            
            "cleaning_supplies": {
                "grout_sponge": {
                    "sku": "GS-001",
                    "name": "Grout Cleaning Sponge",
                    "applications": ["grout_cleanup", "sealer_application"],
                    "material": "High-density foam",
                    "price_range": "$5-15"
                }
            }
        }
    
    def analyze_primary_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze primary product to determine installation requirements"""
        analysis = {
            "tile_size_category": self._determine_tile_size_category(product_data),
            "material_type": product_data.get('material_type', '').lower(),
            "application_area": self._infer_application_area(product_data),
            "special_requirements": [],
            "installation_complexity": "basic"
        }
        
        # Determine tile size category
        title = product_data.get('title', '').lower()
        size_info = product_data.get('size_shape', '').lower()
        
        # Check for large format
        for size in self.installation_knowledge["tile_size_categories"]["large_format"]["sizes"]:
            if size in title or size in size_info:
                analysis["tile_size_category"] = "large_format"
                analysis["installation_complexity"] = "intermediate"
                break
        
        # Check for special materials
        if analysis["material_type"] in ["marble", "travertine", "granite", "limestone"]:
            analysis["special_requirements"].append("natural_stone_sealing")
            analysis["installation_complexity"] = "advanced"
        
        # Check for application context
        if any(term in title for term in ["bathroom", "shower", "wet"]):
            analysis["application_area"] = "bathroom"
            analysis["special_requirements"].append("waterproofing")
        
        return analysis
    
    def _determine_tile_size_category(self, product_data: Dict[str, Any]) -> str:
        """Determine tile size category from product data"""
        size_info = (product_data.get('size_shape', '') + ' ' + 
                    product_data.get('title', '')).lower()
        
        for category, info in self.installation_knowledge["tile_size_categories"].items():
            for size in info["sizes"]:
                if size in size_info:
                    return category
        
        return "standard_format"
    
    def _infer_application_area(self, product_data: Dict[str, Any]) -> str:
        """Infer application area from product data"""
        title = product_data.get('title', '').lower()
        description = product_data.get('description', '').lower()
        combined_text = f"{title} {description}"
        
        # Check for specific application indicators
        if any(term in combined_text for term in ["bathroom", "shower", "wet"]):
            return "bathroom_floor"
        elif any(term in combined_text for term in ["kitchen", "backsplash"]):
            return "kitchen_backsplash"
        elif "floor" in combined_text:
            return "general_floor"
        elif "wall" in combined_text:
            return "general_wall"
        
        return "general_floor"  # Default assumption
    
    def generate_complete_project_recommendations(self, 
                                                product_data: Dict[str, Any],
                                                customer_context: Dict[str, Any] = None) -> InstallationProject:
        """Generate complete installation project recommendations"""
        
        # Analyze primary product
        analysis = self.analyze_primary_product(product_data)
        
        # Build recommendations based on analysis
        project = InstallationProject(
            primary_product=product_data,
            substrate_prep=[],
            installation_materials=[],
            tools_equipment=[],
            finishing_materials=[],
            specialty_products=[],
            installation_sequence=self.installation_knowledge["installation_sequence"],
            total_estimated_cost=0.0,
            project_complexity=analysis["installation_complexity"]
        )
        
        # Add substrate preparation recommendations
        project.substrate_prep = self._recommend_substrate_prep(analysis, customer_context)
        
        # Add installation materials
        project.installation_materials = self._recommend_installation_materials(analysis)
        
        # Add tools and equipment
        project.tools_equipment = self._recommend_tools_equipment(analysis)
        
        # Add finishing materials
        project.finishing_materials = self._recommend_finishing_materials(analysis)
        
        # Add specialty products
        project.specialty_products = self._recommend_specialty_products(analysis, customer_context)
        
        # Calculate total estimated cost
        project.total_estimated_cost = self._calculate_total_cost(project)
        
        return project
    
    def _recommend_substrate_prep(self, analysis: Dict[str, Any], 
                                 customer_context: Dict[str, Any] = None) -> List[ProductRecommendation]:
        """Recommend substrate preparation products"""
        recommendations = []
        
        # Check for waterproofing requirements
        if "waterproofing" in analysis["special_requirements"] or \
           analysis["application_area"] in ["bathroom_floor", "bathroom_wall", "shower_floor", "shower_walls"]:
            
            backer_lite = self.product_database["underlayments"]["backer_lite"]
            recommendations.append(ProductRecommendation(
                sku=backer_lite["sku"],
                name=backer_lite["name"],
                category="Underlayment",
                subcategory="Waterproofing",
                purpose="Waterproof substrate protection",
                installation_step="Step 2: Substrate preparation",
                essential=True,
                price_range=backer_lite["price_range"],
                quantity_guidance="Calculate based on square footage",
                application_notes="Install with 1/4 inch trowel, ensure proper overlap"
            ))
        
        # Check for heated floor requirements
        if customer_context and customer_context.get("heated_floor"):
            recommendations.append(ProductRecommendation(
                sku="HF-001",
                name="Heated Floor System",
                category="Heating",
                subcategory="Radiant Floor",
                purpose="Floor warming system",
                installation_step="Step 1: Before substrate prep",
                essential=False,
                price_range="$300-500",
                quantity_guidance="Based on heated area",
                application_notes="Install before thinset application"
            ))
        
        return recommendations
    
    def _recommend_installation_materials(self, analysis: Dict[str, Any]) -> List[ProductRecommendation]:
        """Recommend installation materials based on analysis"""
        recommendations = []
        
        # Recommend appropriate thinset
        size_category = analysis["tile_size_category"]
        if size_category == "large_format":
            thinset = self.product_database["thinset_mortars"]["lft_thinset"]
        else:
            thinset = self.product_database["thinset_mortars"]["premium_thinset"]
        
        recommendations.append(ProductRecommendation(
            sku=thinset["sku"],
            name=thinset["name"],
            category="Thinset",
            subcategory="Mortar",
            purpose="Tile adhesive - latex-based for large format",
            installation_step="Step 4: Thinset application",
            essential=True,
            price_range=thinset["price_range"],
            quantity_guidance=f"Coverage: {thinset['coverage']}",
            application_notes="Mix according to manufacturer instructions"
        ))
        
        # Recommend grout
        grout = self.product_database["grout_products"]["excel_standard_white"]
        recommendations.append(ProductRecommendation(
            sku=grout["sku"],
            name=grout["name"],
            category="Grout",
            subcategory="Sanded",
            purpose="Joint filling and sealing",
            installation_step="Step 7: Grout application",
            essential=True,
            price_range=grout["price_range"],
            quantity_guidance=f"Coverage: {grout['coverage']}",
            application_notes="Wait 24 hours after tile installation"
        ))
        
        return recommendations
    
    def _recommend_tools_equipment(self, analysis: Dict[str, Any]) -> List[ProductRecommendation]:
        """Recommend tools and equipment"""
        recommendations = []
        
        # Recommend appropriate trowels
        size_category = analysis["tile_size_category"]
        
        # 1/4 inch trowel for backer-lite
        quarter_trowel = self.product_database["tools_equipment"]["quarter_inch_trowel"]
        recommendations.append(ProductRecommendation(
            sku=quarter_trowel["sku"],
            name=quarter_trowel["name"],
            category="Tools",
            subcategory="Trowels",
            purpose="Thinset application under backer-lite",
            installation_step="Step 2: Substrate preparation",
            essential=True,
            price_range=quarter_trowel["price_range"],
            quantity_guidance="One per installer",
            application_notes="Clean immediately after use"
        ))
        
        # Appropriate trowel for tile installation
        if size_category == "large_format":
            trowel = self.product_database["tools_equipment"]["half_inch_trowel"]
            recommendations.append(ProductRecommendation(
                sku=trowel["sku"],
                name=trowel["name"],
                category="Tools",
                subcategory="Trowels",
                purpose="Thinset application over backer-lite",
                installation_step="Step 4: Tile installation",
                essential=True,
                price_range=trowel["price_range"],
                quantity_guidance="One per installer",
                application_notes="1/2 inch or Euro trowel for large format"
            ))
            
            # Recommend Euro trowel as upgrade
            euro_trowel = self.product_database["tools_equipment"]["euro_trowel"]
            recommendations.append(ProductRecommendation(
                sku=euro_trowel["sku"],
                name=euro_trowel["name"],
                category="Tools",
                subcategory="Professional Trowels",
                purpose="Professional large format installation",
                installation_step="Step 4: Tile installation",
                essential=False,
                price_range=euro_trowel["price_range"],
                quantity_guidance="Professional upgrade option",
                application_notes="Better adhesive distribution for large format"
            ))
        
        # Recommend leveling system
        leveling = self.product_database["leveling_systems"]["lippage_system"]
        recommendations.append(ProductRecommendation(
            sku=leveling["sku"],
            name=leveling["name"],
            category="Tools",
            subcategory="Leveling Systems",
            purpose="Prevent lippage and ensure level installation",
            installation_step="Step 5: Tile installation",
            essential=True,
            price_range=leveling["price_range"],
            quantity_guidance="Based on tile spacing requirements",
            application_notes="Use during tile installation, remove after cure"
        ))
        
        return recommendations
    
    def _recommend_finishing_materials(self, analysis: Dict[str, Any]) -> List[ProductRecommendation]:
        """Recommend finishing materials"""
        recommendations = []
        
        # Recommend sealer
        sealer = self.product_database["sealers"]["liquid_sealer"]
        recommendations.append(ProductRecommendation(
            sku=sealer["sku"],
            name=sealer["name"],
            category="Sealers",
            subcategory="Liquid Sealer",
            purpose="Slip-resistant floor protection and grout sealing",
            installation_step="Step 9: Sealer application",
            essential=True,
            price_range=sealer["price_range"],
            quantity_guidance=f"Coverage: {sealer['coverage']}",
            application_notes="Apply with sponge, seal grout after installation"
        ))
        
        # Recommend silicone sealant
        silicone = self.product_database["finishing_products"]["silicone_white"]
        recommendations.append(ProductRecommendation(
            sku=silicone["sku"],
            name=silicone["name"],
            category="Sealants",
            subcategory="Silicone",
            purpose="Edge sealing where tiles meet walls",
            installation_step="Step 10: Final sealing",
            essential=True,
            price_range=silicone["price_range"],
            quantity_guidance="Based on linear feet of edges",
            application_notes="Apply after grout cures, smooth finish"
        ))
        
        # Recommend threshold
        threshold = self.product_database["thresholds"]["bianco_puro"]
        recommendations.append(ProductRecommendation(
            sku=threshold["sku"],
            name=threshold["name"],
            category="Trim",
            subcategory="Thresholds",
            purpose="Transition between floor surfaces",
            installation_step="Step 5: During tile installation",
            essential=False,
            price_range=threshold["price_range"],
            quantity_guidance="One per doorway transition",
            application_notes="Install level with tile surface"
        ))
        
        # Recommend cleaning supplies
        sponge = self.product_database["cleaning_supplies"]["grout_sponge"]
        recommendations.append(ProductRecommendation(
            sku=sponge["sku"],
            name=sponge["name"],
            category="Cleaning",
            subcategory="Sponges",
            purpose="Grout cleanup and sealer application",
            installation_step="Step 7 & 9: Grout cleanup and sealer",
            essential=True,
            price_range=sponge["price_range"],
            quantity_guidance="Multiple sponges recommended",
            application_notes="Use separate sponges for grout and sealer"
        ))
        
        return recommendations
    
    def _recommend_specialty_products(self, analysis: Dict[str, Any], 
                                     customer_context: Dict[str, Any] = None) -> List[ProductRecommendation]:
        """Recommend specialty products for specific applications"""
        recommendations = []
        
        # Shower-specific products
        if analysis["application_area"] in ["shower_floor", "shower_walls"] or \
           (customer_context and customer_context.get("shower_application")):
            
            # Wedi shower pan
            shower_pan = self.product_database["shower_systems"]["wedi_shower_pan"]
            recommendations.append(ProductRecommendation(
                sku=shower_pan["sku"],
                name=shower_pan["name"],
                category="Waterproofing",
                subcategory="Shower Systems",
                purpose="Complete waterproof shower floor system",
                installation_step="Step 1: Before tile installation",
                essential=True,
                price_range=shower_pan["price_range"],
                quantity_guidance="One per shower",
                application_notes="Custom sizes available, includes drain integration"
            ))
            
            # Wedi shower panels
            shower_panels = self.product_database["shower_systems"]["wedi_panels"]
            recommendations.append(ProductRecommendation(
                sku=shower_panels["sku"],
                name=shower_panels["name"],
                category="Waterproofing",
                subcategory="Shower Systems",
                purpose="Waterproof shower wall system",
                installation_step="Step 2: Wall preparation",
                essential=True,
                price_range=shower_panels["price_range"],
                quantity_guidance="Based on shower wall area",
                application_notes="Complete waterproof system integration"
            ))
            
            # Wedi niche
            shower_niche = self.product_database["shower_systems"]["wedi_niche"]
            recommendations.append(ProductRecommendation(
                sku=shower_niche["sku"],
                name=shower_niche["name"],
                category="Waterproofing",
                subcategory="Shower Systems",
                purpose="Waterproof shower storage niche",
                installation_step="Step 2: During wall installation",
                essential=False,
                price_range=shower_niche["price_range"],
                quantity_guidance="One or more per shower",
                application_notes="Requires threshold, niche floor matches shower floor"
            ))
            
            # Wedi sealant
            wedi_sealant = self.product_database["shower_systems"]["wedi_sealant"]
            recommendations.append(ProductRecommendation(
                sku=wedi_sealant["sku"],
                name=wedi_sealant["name"],
                category="Sealants",
                subcategory="Waterproofing",
                purpose="Wedi system sealing compound",
                installation_step="Step 2: System installation",
                essential=True,
                price_range=wedi_sealant["price_range"],
                quantity_guidance=f"Coverage: {wedi_sealant['coverage']}",
                application_notes="Use with all Wedi system components"
            ))
            
            # Special considerations for shower floors
            if customer_context and customer_context.get("drain_type") == "center":
                recommendations.append(ProductRecommendation(
                    sku="TILE-LIMIT",
                    name="Tile Size Limitation Notice",
                    category="Installation Notes",
                    subcategory="Design Constraints",
                    purpose="Center drain requires 3 inch or smaller tiles",
                    installation_step="Step 3: Layout planning",
                    essential=True,
                    price_range="Design consideration",
                    quantity_guidance="Applies to all shower floor tiles",
                    application_notes="Large format acceptable with linear drain only"
                ))
        
        return recommendations
    
    def _calculate_total_cost(self, project: InstallationProject) -> float:
        """Calculate total estimated project cost"""
        total_cost = 0.0
        
        # Sum up all product recommendations
        all_recommendations = (
            project.substrate_prep + 
            project.installation_materials + 
            project.tools_equipment + 
            project.finishing_materials + 
            project.specialty_products
        )
        
        for rec in all_recommendations:
            if rec.essential and rec.price_range != "Design consideration":
                # Extract average price from range
                if "-" in rec.price_range:
                    prices = rec.price_range.replace("$", "").split("-")
                    if len(prices) == 2:
                        avg_price = (float(prices[0]) + float(prices[1])) / 2
                        total_cost += avg_price
        
        return total_cost
    
    def format_project_recommendation(self, project: InstallationProject) -> str:
        """Format complete project recommendation for customer"""
        
        primary_product = project.primary_product
        
        response = f"""
🏗️ **COMPLETE INSTALLATION PROJECT FOR {primary_product.get('title', 'Selected Tile')}**

**Project Complexity:** {project.project_complexity.title()}
**Estimated Materials Cost:** ${project.total_estimated_cost:.2f}

## 📋 **SUBSTRATE PREPARATION**
"""
        
        for rec in project.substrate_prep:
            response += f"""
**{rec.name}** (SKU: {rec.sku})
- **Purpose:** {rec.purpose}
- **Installation Step:** {rec.installation_step}
- **Essential:** {'Yes' if rec.essential else 'Optional'}
- **Price Range:** {rec.price_range}
- **Notes:** {rec.application_notes}
"""
        
        response += f"""
## 🔧 **INSTALLATION MATERIALS**
"""
        
        for rec in project.installation_materials:
            response += f"""
**{rec.name}** (SKU: {rec.sku})
- **Purpose:** {rec.purpose}
- **Installation Step:** {rec.installation_step}
- **Quantity:** {rec.quantity_guidance}
- **Price Range:** {rec.price_range}
- **Notes:** {rec.application_notes}
"""
        
        response += f"""
## 🛠️ **TOOLS & EQUIPMENT**
"""
        
        for rec in project.tools_equipment:
            response += f"""
**{rec.name}** (SKU: {rec.sku})
- **Purpose:** {rec.purpose}
- **Installation Step:** {rec.installation_step}
- **Essential:** {'Yes' if rec.essential else 'Professional Upgrade'}
- **Price Range:** {rec.price_range}
- **Notes:** {rec.application_notes}
"""
        
        response += f"""
## ✨ **FINISHING MATERIALS**
"""
        
        for rec in project.finishing_materials:
            response += f"""
**{rec.name}** (SKU: {rec.sku})
- **Purpose:** {rec.purpose}
- **Installation Step:** {rec.installation_step}
- **Coverage:** {rec.quantity_guidance}
- **Price Range:** {rec.price_range}
- **Notes:** {rec.application_notes}
"""
        
        if project.specialty_products:
            response += f"""
## 🌟 **SPECIALTY PRODUCTS**
"""
            
            for rec in project.specialty_products:
                response += f"""
**{rec.name}** (SKU: {rec.sku})
- **Purpose:** {rec.purpose}
- **Installation Step:** {rec.installation_step}
- **Essential:** {'Yes' if rec.essential else 'Optional'}
- **Price Range:** {rec.price_range}
- **Notes:** {rec.application_notes}
"""
        
        response += f"""
## 📚 **INSTALLATION SEQUENCE**
"""
        
        for step in project.installation_sequence:
            response += f"- {step}\n"
        
        response += f"""
## 💡 **PROFESSIONAL TIPS**
- Purchase 10-15% extra tile for cuts and repairs
- Allow 24 hours cure time before grouting
- Allow 72 hours cure time before heavy use
- Use appropriate trowel size for your tile format
- Clean tools immediately after use
- Follow manufacturer's mixing instructions exactly

## 📞 **NEED HELP?**
Our team can provide detailed quantity calculations and professional installation guidance. Reference our PDF knowledge base for specific product installation instructions and technical specifications.

**Total Project Investment:** ${project.total_estimated_cost:.2f} (materials only)
"""
        
        return response

# Example usage function
def demonstrate_recommendation_system():
    """Demonstrate the enhanced recommendation system"""
    
    # Example product data (Linho Off-White Ceramic Floor Tile)
    example_product = {
        "sku": "680258",
        "title": "Linho Off-White Ceramic Floor Tile 12 x 24 in",
        "description": "Wood plank style ceramic tile for bathroom flooring",
        "material_type": "Ceramic",
        "size_shape": "12 x 24 in",
        "product_category": "Tile",
        "subcategory": "Ceramic",
        "application_areas": ["bathroom", "floor"],
        "price_per_sqft": 4.99
    }
    
    # Customer context for bathroom installation
    customer_context = {
        "application_area": "bathroom_floor",
        "heated_floor": False,
        "shower_application": True,
        "drain_type": "center"
    }
    
    # Initialize recommendation system
    recommender = EnhancedProductRecommendationSystem()
    
    # Generate complete project recommendations
    project = recommender.generate_complete_project_recommendations(
        example_product, 
        customer_context
    )
    
    # Format and display recommendations
    formatted_response = recommender.format_project_recommendation(project)
    print(formatted_response)

if __name__ == "__main__":
    demonstrate_recommendation_system()