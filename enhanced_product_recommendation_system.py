#!/usr/bin/env python3
"""
Enhanced Product Recommendation System for Tileshop RAG
Integrates expert installation knowledge with comprehensive project planning
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InstallationProject:
    """Complete installation project with all components"""
    project_type: str
    primary_products: List[Dict[str, Any]]
    substrate_preparation: List[Dict[str, Any]]
    installation_materials: List[Dict[str, Any]]
    tools_required: List[Dict[str, Any]]
    waterproofing_system: List[Dict[str, Any]]
    finishing_materials: List[Dict[str, Any]]
    estimated_cost: float
    installation_complexity: str
    project_timeline: str
    special_considerations: List[str]

class ExpertRecommendationSystem:
    """Expert-driven product recommendation system"""
    
    def __init__(self, rag_system=None):
        self.rag_system = rag_system
        self.expert_knowledge = self._load_expert_knowledge()
        
    def _load_expert_knowledge(self) -> Dict[str, Any]:
        """Load expert installation knowledge base"""
        return {
            "heated_floor_installation": {
                "cable_spacing": "6-8 inches from walls",
                "basement_spacing": "2 spaces apart (increased heat diffusion)",
                "standard_spacing": "3-4 spaces apart",
                "components": [
                    "Heated floor mat",
                    "Thermostat with sensor wire",
                    "Appropriate cable length",
                    "Plastic trowel (cable protection)",
                    "Relays and higher amp wire (>160 sq ft)",
                    "1/4 inch trowel (under mat)",
                    "Appropriate trowel size for tile"
                ],
                "restrictions": "No cables under furniture (benches, tables, couches)"
            },
            "waterproofing_systems": {
                "wedi_system": {
                    "cost_estimate": 350,
                    "components": [
                        {"sku": "348968", "name": "Wedi Subliner Dry Waterproof Sealing Tape 5in x 32.8ft", "usage": "3-4 inch overlap on backer-lite/heat mat, 2-3 inch up wall"},
                        {"sku": "348951", "name": "Wedi Joint Sealant Cartridge 10.5oz", "usage": "Seal and adhere waterproof connections"},
                        {"name": "Wedi Shower Pan", "usage": "Complete waterproof base system"},
                        {"name": "Wedi Wall Panels", "usage": "Waterproof wall system"}
                    ],
                    "methodology": "Pool-like water retention system capable of holding water up to lowest surface height (typically threshold)"
                },
                "traditional_system": {
                    "cost_estimate": 415,
                    "components": [
                        {"name": "Michigan Mud (Dry Pack Mortar)", "usage": "Shower base construction"},
                        {"name": "Tar Paper", "usage": "Moisture barrier under mud"},
                        {"name": "Wire Lath", "usage": "Reinforcement for mud base"},
                        {"name": "Rubber Shower Pan Liner", "usage": "Primary waterproofing membrane"},
                        {"name": "Pre-slope Kit", "usage": "Proper drainage slope"},
                        {"name": "Easy Pitch Shower Kit", "usage": "Optional for larger projects"},
                        {"name": "Weep Hole Guard", "usage": "Drain protection"},
                        {"name": "Shower Liner Solvent", "usage": "Liner installation"}
                    ],
                    "drain_systems": "Traditional drain assembly with weep holes"
                }
            },
            "wood_plank_tile_installation": {
                "substrate_preparation": [
                    "Backer-lite or heated floor system",
                    "Waterproof sealing tape installation",
                    "Joint sealant application"
                ],
                "installation_sequence": [
                    "Substrate preparation and leveling",
                    "Waterproofing system installation",
                    "Layout and planning",
                    "Tile installation with proper adhesive",
                    "Grouting and sealing",
                    "Final inspection and cleanup"
                ],
                "critical_considerations": [
                    "Proper substrate preparation prevents future failures",
                    "Waterproofing is essential for wet areas",
                    "Layout planning prevents awkward cuts",
                    "Proper adhesive selection for substrate type"
                ]
            }
        }
    
    def generate_complete_project_recommendation(self, query: str, room_type: str = "bathroom") -> InstallationProject:
        """Generate comprehensive project recommendation with expert knowledge"""
        
        # Detect project type and requirements
        project_type = self._detect_project_type(query)
        
        # Base project components
        if project_type == "wood_plank_tile_bathroom":
            return self._generate_wood_plank_bathroom_project(query)
        elif project_type == "heated_floor_installation":
            return self._generate_heated_floor_project(query)
        elif project_type == "shower_installation":
            return self._generate_shower_installation_project(query)
        else:
            return self._generate_standard_tile_project(query)
    
    def _detect_project_type(self, query: str) -> str:
        """Detect project type from query"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["wood plank", "wood look", "plank tile"]):
            return "wood_plank_tile_bathroom"
        elif any(term in query_lower for term in ["heated floor", "radiant heat", "floor heating"]):
            return "heated_floor_installation"
        elif any(term in query_lower for term in ["shower", "shower pan", "shower base"]):
            return "shower_installation"
        else:
            return "standard_tile_project"
    
    def _generate_wood_plank_bathroom_project(self, query: str) -> InstallationProject:
        """Generate complete wood plank tile bathroom project"""
        
        # Primary products - wood plank tiles
        primary_products = [
            {
                "category": "Wood Plank Tiles",
                "description": "Porcelain wood plank tiles for bathroom use",
                "size_options": ["6x48", "8x48", "9x48"],
                "finish": "Matte or textured for slip resistance",
                "quantity_calculation": "Square footage + 10% waste"
            }
        ]
        
        # Substrate preparation
        substrate_preparation = [
            {
                "product": "Backer-lite Board",
                "sku": "To be determined",
                "usage": "Moisture-resistant substrate for wet areas",
                "installation": "Proper fastening and sealing"
            },
            {
                "product": "Waterproof Sealing Tape",
                "sku": "348968",
                "usage": "3-4 inch overlap on backer-lite, 2-3 inch up wall",
                "critical": True
            }
        ]
        
        # Installation materials
        installation_materials = [
            {
                "product": "Modified Thinset Mortar",
                "usage": "Large format tile adhesive",
                "trowel_size": "1/4 x 3/8 x 1/4 square notch"
            },
            {
                "product": "Wedi Joint Sealant",
                "sku": "348951",
                "usage": "Waterproof sealing of tape connections"
            },
            {
                "product": "Sanded Grout",
                "usage": "For joints wider than 1/8 inch"
            }
        ]
        
        # Tools required
        tools_required = [
            {"tool": "Wet saw", "usage": "Cutting tiles to size"},
            {"tool": "Trowel (1/4 x 3/8 x 1/4)", "usage": "Adhesive application"},
            {"tool": "Level", "usage": "Ensuring flat installation"},
            {"tool": "Spacers", "usage": "Consistent joint spacing"},
            {"tool": "Grout float", "usage": "Grout application"},
            {"tool": "Sponges", "usage": "Grout cleanup"}
        ]
        
        # Waterproofing system
        waterproofing_system = [
            {
                "product": "Wedi Subliner Dry Waterproof Sealing Tape",
                "sku": "348968",
                "coverage": "Linear feet of seams and edges"
            },
            {
                "product": "Wedi Joint Sealant Cartridge",
                "sku": "348951",
                "coverage": "Approximately 50 linear feet per cartridge"
            }
        ]
        
        # Finishing materials
        finishing_materials = [
            {
                "product": "Grout Sealer",
                "usage": "Protect grout from moisture and stains"
            },
            {
                "product": "Transition Strips",
                "usage": "Smooth transitions to adjacent flooring"
            },
            {
                "product": "Caulk",
                "usage": "Flexible joints at walls and fixtures"
            }
        ]
        
        return InstallationProject(
            project_type="Wood Plank Tile Bathroom Installation",
            primary_products=primary_products,
            substrate_preparation=substrate_preparation,
            installation_materials=installation_materials,
            tools_required=tools_required,
            waterproofing_system=waterproofing_system,
            finishing_materials=finishing_materials,
            estimated_cost=850.0,
            installation_complexity="Intermediate",
            project_timeline="2-3 days",
            special_considerations=[
                "Proper substrate preparation prevents future failures",
                "Waterproofing is critical in wet areas",
                "Layout planning prevents awkward cuts at walls",
                "Allow proper cure time between steps"
            ]
        )
    
    def _generate_heated_floor_project(self, query: str) -> InstallationProject:
        """Generate heated floor installation project"""
        
        # Detect if basement installation
        is_basement = "basement" in query.lower()
        spacing = "2 spaces apart" if is_basement else "3-4 spaces apart"
        
        primary_products = [
            {
                "category": "Heated Floor System",
                "description": "Electric radiant floor heating system",
                "spacing": spacing,
                "cable_clearance": "6-8 inches from walls"
            }
        ]
        
        installation_materials = [
            {
                "product": "Heated Floor Mat",
                "usage": "Primary heating element",
                "spacing": spacing
            },
            {
                "product": "Thermostat with Sensor Wire",
                "usage": "Temperature control and monitoring"
            },
            {
                "product": "Appropriate Cable Length",
                "usage": "Based on room square footage"
            },
            {
                "product": "Relays and Higher Amp Wire",
                "usage": "Required for installations >160 sq ft"
            }
        ]
        
        tools_required = [
            {
                "tool": "Plastic Trowel",
                "usage": "Cable protection during installation",
                "critical": True
            },
            {
                "tool": "1/4 Inch Trowel",
                "usage": "Under mat installation"
            },
            {
                "tool": "Appropriate Trowel Size",
                "usage": "For tile installation over heated mat"
            }
        ]
        
        return InstallationProject(
            project_type="Heated Floor Installation",
            primary_products=primary_products,
            substrate_preparation=[],
            installation_materials=installation_materials,
            tools_required=tools_required,
            waterproofing_system=[],
            finishing_materials=[],
            estimated_cost=1200.0,
            installation_complexity="Advanced",
            project_timeline="1-2 days",
            special_considerations=[
                f"Cable spacing: {spacing} ({'basement' if is_basement else 'standard'} installation)",
                "Maintain 6-8 inch clearance from walls",
                "Do not install under furniture (benches, tables, couches)",
                "Use plastic trowel to protect cables from scratching",
                "Require relays and higher amp wire for >160 sq ft"
            ]
        )
    
    def _generate_shower_installation_project(self, query: str) -> InstallationProject:
        """Generate shower installation project with dual system options"""
        
        # Detect preference for Wedi vs traditional
        prefers_traditional = any(term in query.lower() for term in ["mud", "traditional", "michigan mud"])
        
        if prefers_traditional:
            return self._generate_traditional_shower_project()
        else:
            return self._generate_wedi_shower_project()
    
    def _generate_wedi_shower_project(self) -> InstallationProject:
        """Generate Wedi shower system project"""
        
        wedi_system = self.expert_knowledge["waterproofing_systems"]["wedi_system"]
        
        primary_products = [
            {
                "category": "Wedi Shower System",
                "description": "Complete waterproof shower system",
                "cost_estimate": wedi_system["cost_estimate"]
            }
        ]
        
        waterproofing_system = [
            {
                "product": component["name"],
                "sku": component.get("sku", "TBD"),
                "usage": component["usage"]
            }
            for component in wedi_system["components"]
        ]
        
        return InstallationProject(
            project_type="Wedi Shower Installation",
            primary_products=primary_products,
            substrate_preparation=[],
            installation_materials=[],
            tools_required=[],
            waterproofing_system=waterproofing_system,
            finishing_materials=[],
            estimated_cost=wedi_system["cost_estimate"],
            installation_complexity="Intermediate",
            project_timeline="1-2 days",
            special_considerations=[
                "Pool-like water retention system",
                "Capable of holding water up to threshold height",
                "Professional installation recommended",
                "Complete waterproof warranty"
            ]
        )
    
    def _generate_traditional_shower_project(self) -> InstallationProject:
        """Generate traditional Michigan mud shower project"""
        
        traditional_system = self.expert_knowledge["waterproofing_systems"]["traditional_system"]
        
        primary_products = [
            {
                "category": "Traditional Shower System",
                "description": "Michigan mud pan shower construction",
                "cost_estimate": traditional_system["cost_estimate"]
            }
        ]
        
        installation_materials = [
            {
                "product": component["name"],
                "usage": component["usage"]
            }
            for component in traditional_system["components"]
        ]
        
        return InstallationProject(
            project_type="Traditional Michigan Mud Shower Installation",
            primary_products=primary_products,
            substrate_preparation=[],
            installation_materials=installation_materials,
            tools_required=[],
            waterproofing_system=[],
            finishing_materials=[],
            estimated_cost=traditional_system["cost_estimate"],
            installation_complexity="Advanced",
            project_timeline="3-4 days",
            special_considerations=[
                "Requires experienced installer",
                "Proper slope critical for drainage",
                "Weep holes must be protected",
                "Curing time between steps essential"
            ]
        )
    
    def _generate_standard_tile_project(self, query: str) -> InstallationProject:
        """Generate standard tile installation project"""
        
        return InstallationProject(
            project_type="Standard Tile Installation",
            primary_products=[],
            substrate_preparation=[],
            installation_materials=[],
            tools_required=[],
            waterproofing_system=[],
            finishing_materials=[],
            estimated_cost=500.0,
            installation_complexity="Basic",
            project_timeline="1-2 days",
            special_considerations=[]
        )
    
    def calculate_total_project_cost(self, project: InstallationProject) -> Dict[str, float]:
        """Calculate comprehensive project cost breakdown"""
        
        cost_breakdown = {
            "materials": project.estimated_cost,
            "labor": project.estimated_cost * 0.6,  # 60% of materials
            "tools": project.estimated_cost * 0.1,   # 10% of materials
            "misc": project.estimated_cost * 0.05    # 5% miscellaneous
        }
        
        cost_breakdown["total"] = sum(cost_breakdown.values())
        
        return cost_breakdown
    
    def format_project_recommendation(self, project: InstallationProject) -> str:
        """Format project recommendation with expert knowledge"""
        
        cost_breakdown = self.calculate_total_project_cost(project)
        
        response = f"""
## {project.project_type}

**Project Overview:**
- **Complexity:** {project.installation_complexity}
- **Timeline:** {project.project_timeline}
- **Total Cost:** ${cost_breakdown['total']:,.2f}

### Cost Breakdown:
- **Materials:** ${cost_breakdown['materials']:,.2f}
- **Labor:** ${cost_breakdown['labor']:,.2f}
- **Tools:** ${cost_breakdown['tools']:,.2f}
- **Miscellaneous:** ${cost_breakdown['misc']:,.2f}

### Special Considerations:
"""
        
        for consideration in project.special_considerations:
            response += f"- {consideration}\n"
        
        response += "\n### Would you like to be connected to a local contractor for this project?\n"
        
        return response

# Example usage
if __name__ == "__main__":
    system = ExpertRecommendationSystem()
    
    # Test wood plank tile project
    project = system.generate_complete_project_recommendation(
        "I want to install wood plank tiles in my bathroom with heated floors"
    )
    
    print(system.format_project_recommendation(project))