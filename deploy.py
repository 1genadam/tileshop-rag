#!/usr/bin/env python3
"""
Tileshop Scraper Deployment Script for Fly.io
Based on the genadam-avatar deployment pattern
"""

import os
import subprocess
import sys

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"🚀 {description}")
    
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    else:
        print(f"✅ Success: {description}")
        if result.stdout:
            print(result.stdout)
    
    return result

def deploy_to_fly():
    """Deploy Tileshop scraper to Fly.io"""
    
    print("🏗️  Starting Tileshop Scraper deployment to Fly.io...")
    
    # Check if fly CLI is available
    try:
        run_command("fly version", "Checking Fly CLI")
    except:
        print("❌ Fly CLI not found. Please install: https://fly.io/docs/hands-on/install-flyctl/")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists("admin_dashboard.py"):
        print("❌ Error: admin_dashboard.py not found. Please run from the tileshop_scraper directory.")
        sys.exit(1)
    
    # Check if Docker is running
    try:
        run_command("docker version", "Checking Docker")
    except:
        print("❌ Docker not found or not running. Please start Docker.")
        sys.exit(1)
    
    # Build and push Docker image
    print("\n📦 Building Docker image for linux/amd64...")
    build_command = "docker buildx build --platform linux/amd64 -t registry.fly.io/tileshop-scraper:latest . --push"
    run_command(build_command, "Building and pushing Docker image")
    
    # Deploy to Fly.io
    print("\n🚀 Deploying to Fly.io...")
    deploy_command = "fly deploy --strategy immediate"
    run_command(deploy_command, "Deploying to Fly.io")
    
    print("\n✅ Deployment completed successfully!")
    print("🌐 Your Tileshop scraper should be available at: https://tileshop-scraper.fly.dev")
    print("📊 Dashboard: https://tileshop-scraper.fly.dev")
    print("💬 RAG Chat: https://tileshop-scraper.fly.dev/chat")
    
    # Show status
    print("\n📈 Checking deployment status...")
    run_command("fly status", "Getting deployment status")

def setup_secrets():
    """Set up secrets for production deployment"""
    print("\n🔐 Setting up production secrets...")
    
    # Read local .env file for reference
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"📄 Found local {env_file} file")
        with open(env_file, 'r') as f:
            env_content = f.read()
            if "ANTHROPIC_API_KEY" in env_content:
                print("✅ ANTHROPIC_API_KEY found in .env")
                # Extract the key
                for line in env_content.split('\n'):
                    if line.startswith('ANTHROPIC_API_KEY='):
                        api_key = line.split('=', 1)[1]
                        print("🔑 Setting ANTHROPIC_API_KEY secret...")
                        run_command(f"fly secrets set ANTHROPIC_API_KEY={api_key}", "Setting Claude API key")
                        break
            else:
                print("⚠️  ANTHROPIC_API_KEY not found in .env file")
    else:
        print("⚠️  No .env file found. You may need to set secrets manually with:")
        print("   fly secrets set ANTHROPIC_API_KEY=your-api-key")

def main():
    """Main deployment function"""
    if len(sys.argv) > 1 and sys.argv[1] == "secrets":
        setup_secrets()
    elif len(sys.argv) > 1 and sys.argv[1] == "deploy":
        deploy_to_fly()
    elif len(sys.argv) > 1 and sys.argv[1] == "full":
        setup_secrets()
        deploy_to_fly()
    else:
        print("Tileshop Scraper Deployment Script")
        print("Usage:")
        print("  python deploy.py secrets   - Set up production secrets")
        print("  python deploy.py deploy    - Deploy to Fly.io")
        print("  python deploy.py full      - Set secrets and deploy")

if __name__ == "__main__":
    main()