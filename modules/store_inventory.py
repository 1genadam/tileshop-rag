"""
Store Inventory and Location Management System
Provides aisle locations and inventory counts for tile products
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StoreLocation:
    """Store location information for a product"""
    sku: str
    aisle: str
    bay: str
    shelf: str
    display_board: Optional[str] = None
    inventory_count: int = 0
    last_updated: str = ""

@dataclass
class StoreInventory:
    """Store inventory information"""
    sku: str
    name: str
    in_stock: bool
    quantity: int
    location: StoreLocation
    reorder_level: int = 5
    next_shipment: Optional[str] = None

class StoreInventoryManager:
    """Manages store inventory and location data"""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        
        # Sample store layout - In production, this would come from database
        self.store_layout = {
            "ceramic_tiles": {
                "aisles": ["A1", "A2", "A3"],
                "display_boards": ["DB-01", "DB-02", "DB-03"],
                "description": "Ceramic & Porcelain Tiles"
            },
            "natural_stone": {
                "aisles": ["B1", "B2"],
                "display_boards": ["DB-04", "DB-05"],
                "description": "Natural Stone & Marble"
            },
            "mosaic_tiles": {
                "aisles": ["C1"],
                "display_boards": ["DB-06", "DB-07"],
                "description": "Mosaic & Glass Tiles"
            },
            "subway_tiles": {
                "aisles": ["A2", "A3"],
                "display_boards": ["DB-02", "DB-08"],
                "description": "Subway & Metro Tiles"
            },
            "large_format": {
                "aisles": ["D1", "D2"],
                "display_boards": ["DB-09", "DB-10"],
                "description": "Large Format Tiles (12x24+)"
            },
            "outdoor_tiles": {
                "aisles": ["E1"],
                "display_boards": ["DB-11"],
                "description": "Outdoor & Patio Tiles"
            }
        }
        
        logger.info("Store Inventory Manager initialized")
    
    def get_product_location(self, sku: str) -> Optional[StoreLocation]:
        """Get store location for a specific SKU"""
        try:
            if not self.db_manager:
                return self._get_mock_location(sku)
            
            # Query database for location information
            query = """
                SELECT 
                    p.sku,
                    sl.aisle,
                    sl.bay,
                    sl.shelf,
                    sl.display_board,
                    si.quantity as inventory_count,
                    si.last_updated
                FROM products p
                LEFT JOIN store_locations sl ON p.sku = sl.sku
                LEFT JOIN store_inventory si ON p.sku = si.sku
                WHERE p.sku = ?
            """
            
            result = self.db_manager.execute_query(query, (sku,))
            
            if result and len(result) > 0:
                row = result[0]
                return StoreLocation(
                    sku=row['sku'],
                    aisle=row['aisle'] or self._get_default_aisle_by_sku(sku),
                    bay=row['bay'] or "01",
                    shelf=row['shelf'] or "A",
                    display_board=row['display_board'],
                    inventory_count=row['inventory_count'] or 0,
                    last_updated=row['last_updated'] or "Unknown"
                )
            else:
                return self._get_mock_location(sku)
                
        except Exception as e:
            logger.error(f"Error getting product location for SKU {sku}: {e}")
            return self._get_mock_location(sku)
    
    def _get_mock_location(self, sku: str) -> StoreLocation:
        """Generate mock location data for testing"""
        # Determine category based on SKU patterns
        sku_lower = sku.lower()
        
        if any(keyword in sku_lower for keyword in ['ceramic', 'porcelain', 'por']):
            category = "ceramic_tiles"
        elif any(keyword in sku_lower for keyword in ['marble', 'stone', 'travertine']):
            category = "natural_stone"
        elif any(keyword in sku_lower for keyword in ['mosaic', 'glass', 'penny']):
            category = "mosaic_tiles"
        elif any(keyword in sku_lower for keyword in ['subway', 'metro', '3x6', '4x8']):
            category = "subway_tiles"
        elif any(keyword in sku_lower for keyword in ['12x24', '24x24', '12x48', 'large']):
            category = "large_format"
        elif any(keyword in sku_lower for keyword in ['outdoor', 'patio', 'deck']):
            category = "outdoor_tiles"
        else:
            category = "ceramic_tiles"  # Default
        
        layout = self.store_layout[category]
        
        # Generate location based on category
        import random
        random.seed(hash(sku))  # Consistent locations for same SKU
        
        aisle = random.choice(layout["aisles"])
        bay = f"{random.randint(1, 8):02d}"
        shelf = random.choice(["A", "B", "C", "D"])
        display_board = random.choice(layout["display_boards"]) if layout["display_boards"] else None
        inventory = random.randint(15, 85)
        
        return StoreLocation(
            sku=sku,
            aisle=aisle,
            bay=bay,
            shelf=shelf,
            display_board=display_board,
            inventory_count=inventory,
            last_updated="2025-07-10"
        )
    
    def _get_default_aisle_by_sku(self, sku: str) -> str:
        """Get default aisle assignment based on SKU"""
        sku_lower = sku.lower()
        
        if any(keyword in sku_lower for keyword in ['ceramic', 'porcelain']):
            return "A1"
        elif any(keyword in sku_lower for keyword in ['stone', 'marble']):
            return "B1"
        elif any(keyword in sku_lower for keyword in ['mosaic', 'glass']):
            return "C1"
        elif any(keyword in sku_lower for keyword in ['subway']):
            return "A2"
        elif any(keyword in sku_lower for keyword in ['large', '12x24', '24x24']):
            return "D1"
        else:
            return "A1"  # Default ceramic aisle
    
    def get_inventory_info(self, sku: str) -> Optional[StoreInventory]:
        """Get complete inventory information for a SKU"""
        try:
            location = self.get_product_location(sku)
            if not location:
                return None
            
            # Get product details
            product = self._get_product_details(sku)
            if not product:
                return None
            
            return StoreInventory(
                sku=sku,
                name=product.get('name', 'Unknown Product'),
                in_stock=location.inventory_count > 0,
                quantity=location.inventory_count,
                location=location,
                reorder_level=5,
                next_shipment=self._get_next_shipment_date(sku)
            )
            
        except Exception as e:
            logger.error(f"Error getting inventory info for SKU {sku}: {e}")
            return None
    
    def _get_product_details(self, sku: str) -> Optional[Dict]:
        """Get basic product details"""
        try:
            if not self.db_manager:
                return {"name": f"Sample Tile {sku}", "category": "ceramic"}
            
            query = "SELECT name, category, price FROM products WHERE sku = ?"
            result = self.db_manager.execute_query(query, (sku,))
            
            if result and len(result) > 0:
                return dict(result[0])
            else:
                return {"name": f"Tile {sku}", "category": "ceramic"}
                
        except Exception as e:
            logger.error(f"Error getting product details for SKU {sku}: {e}")
            return {"name": f"Tile {sku}", "category": "ceramic"}
    
    def _get_next_shipment_date(self, sku: str) -> Optional[str]:
        """Get next expected shipment date"""
        # In production, this would query shipment database
        # For now, return mock data
        import datetime
        next_week = datetime.datetime.now() + datetime.timedelta(days=7)
        return next_week.strftime("%Y-%m-%d")
    
    def find_in_store(self, sku: str) -> Dict:
        """Complete store lookup for a tile SKU"""
        try:
            inventory = self.get_inventory_info(sku)
            
            if not inventory:
                return {
                    "success": False,
                    "message": f"Product {sku} not found in store system"
                }
            
            location = inventory.location
            
            # Build store directions
            directions = self._build_store_directions(location)
            
            # Determine availability status
            if inventory.quantity > 20:
                availability = "In Stock - Good Availability"
                availability_color = "green"
            elif inventory.quantity > 5:
                availability = "In Stock - Limited Quantity"
                availability_color = "yellow"
            elif inventory.quantity > 0:
                availability = "Low Stock - Hurry!"
                availability_color = "orange"
            else:
                availability = "Out of Stock"
                availability_color = "red"
            
            return {
                "success": True,
                "sku": sku,
                "name": inventory.name,
                "location": {
                    "aisle": location.aisle,
                    "bay": location.bay,
                    "shelf": location.shelf,
                    "display_board": location.display_board,
                    "directions": directions
                },
                "inventory": {
                    "quantity": inventory.quantity,
                    "availability": availability,
                    "availability_color": availability_color,
                    "next_shipment": inventory.next_shipment,
                    "last_updated": location.last_updated
                },
                "store_info": {
                    "department": self._get_department_by_aisle(location.aisle),
                    "category_description": self._get_category_description(location.aisle)
                }
            }
            
        except Exception as e:
            logger.error(f"Error finding product in store: {e}")
            return {
                "success": False,
                "message": f"Error looking up store information: {str(e)}"
            }
    
    def _build_store_directions(self, location: StoreLocation) -> str:
        """Build human-friendly directions to the product"""
        directions = f"📍 **Aisle {location.aisle}**"
        
        if location.bay:
            directions += f", Bay {location.bay}"
        
        if location.shelf:
            directions += f", Shelf {location.shelf}"
        
        if location.display_board:
            directions += f"\n🎨 **Display Board**: {location.display_board}"
        
        # Add department context
        department = self._get_department_by_aisle(location.aisle)
        if department:
            directions += f"\n🏢 **Department**: {department}"
        
        return directions
    
    def _get_department_by_aisle(self, aisle: str) -> str:
        """Get department name based on aisle"""
        if aisle.startswith('A'):
            return "Ceramic & Porcelain Tiles"
        elif aisle.startswith('B'):
            return "Natural Stone"
        elif aisle.startswith('C'):
            return "Mosaic & Specialty"
        elif aisle.startswith('D'):
            return "Large Format Tiles"
        elif aisle.startswith('E'):
            return "Outdoor & Patio"
        else:
            return "General Tiles"
    
    def _get_category_description(self, aisle: str) -> str:
        """Get friendly category description"""
        if aisle.startswith('A'):
            return "Perfect for bathrooms, kitchens, and most indoor applications"
        elif aisle.startswith('B'):
            return "Elegant natural materials for luxury installations"
        elif aisle.startswith('C'):
            return "Decorative accents and artistic installations"
        elif aisle.startswith('D'):
            return "Modern large tiles for contemporary spaces"
        elif aisle.startswith('E'):
            return "Weather-resistant tiles for outdoor use"
        else:
            return "Quality tiles for various applications"
    
    def get_nearby_alternatives(self, sku: str, category: str = None) -> List[Dict]:
        """Find similar products in nearby aisles"""
        try:
            location = self.get_product_location(sku)
            if not location:
                return []
            
            # Find products in same or adjacent aisles
            nearby_aisles = self._get_nearby_aisles(location.aisle)
            
            alternatives = []
            for aisle in nearby_aisles[:3]:  # Limit to 3 nearby options
                alternatives.append({
                    "aisle": aisle,
                    "department": self._get_department_by_aisle(aisle),
                    "description": self._get_category_description(aisle)
                })
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error getting nearby alternatives: {e}")
            return []
    
    def _get_nearby_aisles(self, current_aisle: str) -> List[str]:
        """Get aisles near the current location"""
        all_aisles = []
        for category_data in self.store_layout.values():
            all_aisles.extend(category_data["aisles"])
        
        # Sort by proximity to current aisle
        all_aisles.sort()
        
        try:
            current_index = all_aisles.index(current_aisle)
            nearby = []
            
            # Add current aisle
            nearby.append(current_aisle)
            
            # Add adjacent aisles
            if current_index > 0:
                nearby.append(all_aisles[current_index - 1])
            if current_index < len(all_aisles) - 1:
                nearby.append(all_aisles[current_index + 1])
            
            return nearby
            
        except ValueError:
            return [current_aisle]