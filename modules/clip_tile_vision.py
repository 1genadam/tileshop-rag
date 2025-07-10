"""
CLIP-based Tile Recognition System
Provides visual similarity matching for tile identification
"""

import torch
import clip
import cv2
import numpy as np
from PIL import Image
import base64
import io
import json
import logging
import faiss
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import sqlite3
import os

logger = logging.getLogger(__name__)

@dataclass
class TileMatch:
    """Represents a tile match result"""
    sku: str
    name: str
    similarity_score: float
    image_path: str
    price: float
    category: str
    description: str

class CLIPTileVision:
    """CLIP-based tile recognition and similarity matching system"""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing CLIP on device: {self.device}")
        
        # Load CLIP model
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        
        # Initialize embeddings storage
        self.tile_embeddings = None
        self.tile_metadata = []
        self.faiss_index = None
        
        # Create embeddings cache directory
        self.cache_dir = "vision_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info("CLIP Tile Vision system initialized")
    
    def preprocess_image(self, image_input) -> Image.Image:
        """Preprocess image for CLIP analysis"""
        try:
            # Handle different input types
            if isinstance(image_input, str):
                if image_input.startswith('data:image'):
                    # Base64 encoded image
                    header, data = image_input.split(',', 1)
                    image_data = base64.b64decode(data)
                    image = Image.open(io.BytesIO(image_data))
                else:
                    # File path
                    image = Image.open(image_input)
            elif isinstance(image_input, np.ndarray):
                # OpenCV image
                image = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
            elif isinstance(image_input, Image.Image):
                # PIL Image
                image = image_input
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply image enhancements for better tile recognition
            image = self._enhance_tile_image(image)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    def _enhance_tile_image(self, image: Image.Image) -> Image.Image:
        """Apply enhancements specific to tile recognition"""
        try:
            # Convert to numpy for OpenCV processing
            img_array = np.array(image)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            # Slight sharpening for texture details
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            # Blend original and sharpened (mild sharpening)
            final = cv2.addWeighted(enhanced, 0.7, sharpened, 0.3, 0)
            
            return Image.fromarray(final)
            
        except Exception as e:
            logger.warning(f"Image enhancement failed, using original: {e}")
            return image
    
    def encode_image(self, image_input) -> np.ndarray:
        """Encode image using CLIP to get feature vector"""
        try:
            # Preprocess image
            image = self.preprocess_image(image_input)
            
            # Apply CLIP preprocessing and encode
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().flatten()
            
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise
    
    def build_tile_database_embeddings(self, force_rebuild: bool = False) -> bool:
        """Build CLIP embeddings for all tiles in database"""
        try:
            cache_file = os.path.join(self.cache_dir, "tile_embeddings.npz")
            metadata_file = os.path.join(self.cache_dir, "tile_metadata.json")
            
            # Check if cache exists and is recent
            if not force_rebuild and os.path.exists(cache_file) and os.path.exists(metadata_file):
                logger.info("Loading cached tile embeddings")
                self._load_embeddings_cache()
                return True
            
            logger.info("Building tile database embeddings...")
            
            if not self.db_manager:
                logger.error("Database manager not available")
                return False
            
            # Get all products with images
            products = self._get_products_with_images()
            
            if not products:
                logger.warning("No products with images found")
                return False
            
            embeddings = []
            metadata = []
            
            for i, product in enumerate(products):
                try:
                    # Get product image path
                    image_path = self._get_product_image_path(product)
                    
                    if not image_path or not os.path.exists(image_path):
                        logger.warning(f"Image not found for product {product.get('sku', 'unknown')}")
                        continue
                    
                    # Encode image
                    embedding = self.encode_image(image_path)
                    embeddings.append(embedding)
                    
                    # Store metadata
                    metadata.append({
                        'sku': product.get('sku', ''),
                        'name': product.get('name', ''),
                        'price': product.get('price', 0.0),
                        'category': product.get('category', ''),
                        'description': product.get('description', ''),
                        'image_path': image_path,
                        'index': len(metadata)
                    })
                    
                    if (i + 1) % 50 == 0:
                        logger.info(f"Processed {i + 1}/{len(products)} products")
                        
                except Exception as e:
                    logger.error(f"Error processing product {product.get('sku', 'unknown')}: {e}")
                    continue
            
            if not embeddings:
                logger.error("No valid embeddings generated")
                return False
            
            # Convert to numpy array
            self.tile_embeddings = np.array(embeddings).astype('float32')
            self.tile_metadata = metadata
            
            # Build FAISS index for fast similarity search
            self._build_faiss_index()
            
            # Cache embeddings
            self._save_embeddings_cache()
            
            logger.info(f"Successfully built embeddings for {len(embeddings)} tiles")
            return True
            
        except Exception as e:
            logger.error(f"Error building tile database embeddings: {e}")
            return False
    
    def _get_products_with_images(self) -> List[Dict]:
        """Get all products that have associated images"""
        try:
            if not self.db_manager:
                return []
            
            # Query for products with images
            query = """
                SELECT DISTINCT 
                    p.sku,
                    p.name,
                    p.price,
                    p.category,
                    p.description,
                    p.image_url,
                    p.image_path
                FROM products p 
                WHERE p.image_url IS NOT NULL 
                   OR p.image_path IS NOT NULL
                ORDER BY p.sku
            """
            
            results = self.db_manager.execute_query(query)
            return [dict(row) for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Error getting products with images: {e}")
            return []
    
    def _get_product_image_path(self, product: Dict) -> Optional[str]:
        """Get the actual file path for a product image"""
        try:
            # Check for local image path first
            if product.get('image_path'):
                path = product['image_path']
                if os.path.exists(path):
                    return path
            
            # Check for image URL (might be downloaded locally)
            if product.get('image_url'):
                # Construct local path from URL
                sku = product.get('sku', '')
                image_dir = "product_images"
                os.makedirs(image_dir, exist_ok=True)
                
                # Try different common extensions
                for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    local_path = os.path.join(image_dir, f"{sku}{ext}")
                    if os.path.exists(local_path):
                        return local_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting image path for product: {e}")
            return None
    
    def _build_faiss_index(self):
        """Build FAISS index for fast similarity search"""
        try:
            if self.tile_embeddings is None or len(self.tile_embeddings) == 0:
                logger.error("No embeddings available for FAISS index")
                return
            
            # Create FAISS index (Inner Product for cosine similarity with normalized vectors)
            dimension = self.tile_embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)
            
            # Add embeddings to index
            self.faiss_index.add(self.tile_embeddings)
            
            logger.info(f"Built FAISS index with {self.faiss_index.ntotal} embeddings")
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
    
    def _save_embeddings_cache(self):
        """Save embeddings and metadata to cache"""
        try:
            cache_file = os.path.join(self.cache_dir, "tile_embeddings.npz")
            metadata_file = os.path.join(self.cache_dir, "tile_metadata.json")
            
            # Save embeddings
            np.savez_compressed(cache_file, embeddings=self.tile_embeddings)
            
            # Save metadata
            with open(metadata_file, 'w') as f:
                json.dump(self.tile_metadata, f, indent=2)
            
            logger.info("Embeddings cache saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving embeddings cache: {e}")
    
    def _load_embeddings_cache(self):
        """Load embeddings and metadata from cache"""
        try:
            cache_file = os.path.join(self.cache_dir, "tile_embeddings.npz")
            metadata_file = os.path.join(self.cache_dir, "tile_metadata.json")
            
            # Load embeddings
            data = np.load(cache_file)
            self.tile_embeddings = data['embeddings']
            
            # Load metadata
            with open(metadata_file, 'r') as f:
                self.tile_metadata = json.load(f)
            
            # Rebuild FAISS index
            self._build_faiss_index()
            
            logger.info(f"Loaded {len(self.tile_metadata)} cached embeddings")
            
        except Exception as e:
            logger.error(f"Error loading embeddings cache: {e}")
    
    def find_similar_tiles(self, image_input, top_k: int = 5, min_similarity: float = 0.3) -> List[TileMatch]:
        """Find tiles similar to the input image"""
        try:
            if self.faiss_index is None or len(self.tile_metadata) == 0:
                logger.error("Tile database not initialized. Call build_tile_database_embeddings() first.")
                return []
            
            # Encode input image
            query_embedding = self.encode_image(image_input)
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            # Search for similar embeddings
            similarities, indices = self.faiss_index.search(query_embedding, top_k)
            
            results = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if similarity < min_similarity:
                    continue
                
                if idx >= len(self.tile_metadata):
                    continue
                
                metadata = self.tile_metadata[idx]
                
                match = TileMatch(
                    sku=metadata['sku'],
                    name=metadata['name'],
                    similarity_score=float(similarity),
                    image_path=metadata['image_path'],
                    price=metadata['price'],
                    category=metadata['category'],
                    description=metadata['description']
                )
                
                results.append(match)
            
            logger.info(f"Found {len(results)} similar tiles with similarity > {min_similarity}")
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar tiles: {e}")
            return []
    
    def analyze_tile_image(self, image_input) -> Dict:
        """Comprehensive tile analysis including similarity matching"""
        try:
            # Find similar tiles
            similar_tiles = self.find_similar_tiles(image_input, top_k=5)
            
            if not similar_tiles:
                return {
                    "success": False,
                    "message": "No similar tiles found in database",
                    "matches": []
                }
            
            # Format results
            matches = []
            for tile in similar_tiles:
                matches.append({
                    "sku": tile.sku,
                    "name": tile.name,
                    "similarity": round(tile.similarity_score * 100, 1),  # Convert to percentage
                    "price": tile.price,
                    "category": tile.category,
                    "description": tile.description,
                    "confidence": "High" if tile.similarity_score > 0.8 else "Medium" if tile.similarity_score > 0.6 else "Low"
                })
            
            # Determine best match
            best_match = matches[0] if matches else None
            
            return {
                "success": True,
                "message": f"Found {len(matches)} similar tiles",
                "best_match": best_match,
                "matches": matches,
                "analysis": {
                    "total_matches": len(matches),
                    "best_similarity": matches[0]["similarity"] if matches else 0,
                    "categories_found": list(set(m["category"] for m in matches))
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing tile image: {e}")
            return {
                "success": False,
                "message": f"Error analyzing image: {str(e)}",
                "matches": []
            }
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the tile database"""
        try:
            if not self.tile_metadata:
                return {"error": "Database not initialized"}
            
            categories = {}
            for tile in self.tile_metadata:
                cat = tile.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                "total_tiles": len(self.tile_metadata),
                "categories": categories,
                "embeddings_shape": self.tile_embeddings.shape if self.tile_embeddings is not None else None,
                "faiss_index_size": self.faiss_index.ntotal if self.faiss_index else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}