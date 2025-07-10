#!/usr/bin/env python3
"""
Setup script for CLIP tile vision system
Installs dependencies and initializes the vision database
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_requirements():
    """Install required packages for vision system"""
    try:
        logger.info("Installing vision system requirements...")
        
        # Install from requirements file
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_vision.txt"
        ])
        
        logger.info("✅ Vision requirements installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install requirements: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    try:
        directories = [
            "vision_cache",
            "product_images",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create directories: {e}")
        return False

def test_clip_installation():
    """Test CLIP installation"""
    try:
        logger.info("Testing CLIP installation...")
        
        import torch
        import clip
        
        # Load CLIP model to test
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)
        
        logger.info(f"✅ CLIP loaded successfully on device: {device}")
        return True
        
    except Exception as e:
        logger.error(f"❌ CLIP test failed: {e}")
        return False

def initialize_vision_system():
    """Initialize the vision system"""
    try:
        logger.info("Initializing vision system...")
        
        from modules.db_manager import DatabaseManager
        from modules.clip_tile_vision import CLIPTileVision
        
        # Initialize components
        db_manager = DatabaseManager()
        clip_vision = CLIPTileVision(db_manager)
        
        # Get database stats
        stats = clip_vision.get_database_stats()
        
        if stats.get('error'):
            logger.info("Vision database not yet built - this is normal for first setup")
        else:
            logger.info(f"✅ Vision system initialized: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize vision system: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Setting up CLIP Tile Vision System")
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Setup directories
    if not setup_directories():
        success = False
    
    # Test CLIP installation
    if not test_clip_installation():
        success = False
    
    # Initialize vision system
    if not initialize_vision_system():
        success = False
    
    if success:
        logger.info("🎉 Vision system setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start the customer chat app: python customer_chat_app.py")
        logger.info("2. Visit: http://localhost:8081/customer-chat")
        logger.info("3. Click 'Scan Tile' to test the vision system")
        logger.info("")
        logger.info("Note: The vision database will be built automatically when you first")
        logger.info("use the vision features. This may take a few minutes depending on")
        logger.info("the number of product images in your database.")
    else:
        logger.error("❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()