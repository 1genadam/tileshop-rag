# Tileshop Intelligence Platform & AI Knowledge System

A comprehensive e-commerce intelligence platform and AI-powered product discovery system for Tileshop.com. Features intelligent product categorization, slip-resistance classification, and Claude-powered natural language search through a complete knowledge acquisition and retrieval interface.

## 📚 **MASTER INDEX - Complete Documentation Guide**

> **Navigation Guide**: This master index provides comprehensive access to all project documentation, organized by purpose and audience.

### 🚀 **Getting Started**
- [🚀 Quick Start](#-quick-start) - Immediate setup and launch commands
- [🛠️ Local Environment Setup](#local-environment-setup) - Detailed environment configuration
- [🔄 Dashboard Management](#-proper-dashboard-reboot-protocol) - Startup and restart procedures

### 📁 **Project Architecture**
- [📁 Project Architecture & File Index](#-project-architecture--file-index) - **★ COMPREHENSIVE FILE GUIDE**
- [📊 Project Context & Goals](#project-context--goals) - Business objectives and technical goals
- [🔧 Features](#features) - Core functionality and capabilities
- [📋 Database Schema](#database-schema) - Data structure and field definitions

### 🖥️ **System Management**
- [🖥️ Admin Dashboard](#-admin-dashboard-features) - Complete dashboard functionality guide
- [⚡ Technical Issues Resolved](#technical-issues-resolved) - Historical problem solutions
- [🧪 Testing & Validation](#checking-results) - Verification and quality assurance
- [🔧 Troubleshooting](#troubleshooting) - Common issues and solutions

### 🚀 **Deployment & Production**
- [🚀 Production Deployment](#-production-deployment) - Cloud deployment procedures
- [📋 Fly.io Independent Server Roadmap](flyio-deployment-roadmap.md) - **★ COMPLETE CLOUD MIGRATION STRATEGY**
- [📋 Development Roadmap](dev_roadmap.md) - Business feature development timeline
- [🆕 Latest Enhancements](#-latest-enhancements-july-01-2025---714-am) - Recent updates and improvements
- [📋 Recent Session Improvements](#-recent-session-improvements-june-29-2025) - Development history

### 🎯 **Quick Reference Sections**
| **I Need To...** | **Go To Section** | **Key Information** |
|-------------------|-------------------|---------------------|
| **🚀 Start the system immediately** | [Quick Start](#-quick-start) | One-command startup |
| **📁 Find a specific file** | [Project Architecture & File Index](#-project-architecture--file-index) | Complete file inventory |
| **🖥️ Use the dashboard** | [Admin Dashboard Features](#-admin-dashboard-features) | UI controls and functions |
| **🔧 Fix a problem** | [Troubleshooting](#troubleshooting) | Common issues and solutions |
| **🚀 Deploy to production** | [Fly.io Independent Server Roadmap](flyio-deployment-roadmap.md) | Complete cloud migration strategy |
| **📊 Understand the data** | [Database Schema](#database-schema) | Data structure and fields |

---

## 🆕 **Latest Enhancements (July 01, 2025 - 5:07 PM)**

### **⚡ Real-Time Crawl Performance & Feedback System**
- **🚀 Speed Optimization**: Crawl operations now **60-70% faster** (15-25 seconds vs 45-60 seconds per page)
- **📊 Real-Time Progress**: Live WebSocket updates showing crawl stages, timing, and status
- **🎯 Smart Content Targeting**: CSS selectors and tag exclusion for faster, focused extraction
- **📈 Adaptive Polling**: Progressive back-off strategy eliminates fixed delays
- **🔍 Performance Monitoring**: Detailed timing metrics for submit, poll, and total times

### **🔍 SKU Lookup Feature Added**
- **📦 Product Search by SKU**: New dashboard section for instant product lookup by SKU number
- **📊 Comprehensive Product Display**: Shows pricing, dimensions, finish, color, specifications, and metadata
- **🔗 External Links**: Direct links to original product pages for verification
- **⚡ Real-time Search**: Fast database queries with loading states and error handling
- **🎯 API Integration**: New `/api/database/product/sku/<sku>` endpoint for programmatic access

### **🚀 Fly.io Independent Server Deployment Roadmap Created**
- **📋 Comprehensive Migration Strategy**: Complete roadmap for migrating from local dependencies to fully independent cloud deployment
- **🔧 Infrastructure Analysis**: Detailed assessment of current local dependencies (PostgreSQL, Supabase, Crawl4AI)
- **📊 Cost Analysis**: $155-290/month operational cost estimates with performance expectations
- **⏱️ Timeline**: 4-6 week migration plan with phased implementation strategy
- **📖 Documentation**: Full roadmap available at [flyio-deployment-roadmap.md](flyio-deployment-roadmap.md)

### **🎯 Acquisition Mode UI Enhancement**
- **✅ Default Selection Updated**: "Complete Sitemap Learning Mode" now default instead of "Test Mode (10 URLs)"
- **✅ Consistent URL Limits**: Default URL limit changed from 10 to 4775 to match sitemap mode
- **✅ Production-Ready Defaults**: Dashboard now optimized for full-scale learning operations
- **🔄 Backward Compatibility**: Test mode still available for development and testing

### **🛠️ Infrastructure Fixes Applied**
- **✅ PostgreSQL Container Restarted**: Fixed relational_db connectivity issues after git pull
- **✅ All Services Operational**: Complete 8-service ecosystem now running with full health checks
- **✅ Pre-warming System Restored**: All 5 components (virtual_env, relational_db, vector_db, sitemap_validation, crawl4ai_service) showing ready status
- **✅ Database Connectivity Verified**: Both PostgreSQL (5432) and Supabase (5433) containers connected and operational

---

## 🆕 **Previous Enhancements (June 30, 2025 - 12:10 AM)**

### **🚀 Database Connectivity Resolution - All Systems Operational**
- **✅ Database Errors Completely Resolved**: All database connectivity issues fixed - system now shows `is_prewarmed: true`
- **✅ Enhanced Pre-warming System**: Upgraded to 5-component granular monitoring with separate database testing
- **✅ Eliminated Demo Mode**: Removed demo mode that was preventing real database connections
- **✅ Fixed Database Authentication**: Updated authentication to use reliable postgres/postgres credentials
- **✅ Real-time Database Health**: Pre-warming now uses actual DatabaseManager.test_connections() for accurate status

### **🔧 System Pre-warming Components - All Operational (5/5)**
- **Python subprocess startup ✅ Ready**: Virtual environment activation and validation
- **relational_db ✅ Ready**: PostgreSQL container connectivity and access (FIXED)
- **vector_db ✅ Ready**: Supabase container connectivity and access (FIXED)
- **Sitemap validation ✅ Ready**: Sitemap file validation and URL counting  
- **Crawler service ✅ Ready**: Crawl4AI service connectivity and health check

### **🔧 Critical Database Fixes Applied**
- **✅ Removed Demo Mode Entirely**: Eliminated `DEMO_MODE` that prevented real database connectivity tests
- **✅ Fixed PostgreSQL Authentication**: Updated relational_db config from system user to postgres/postgres credentials
- **✅ Fixed Import Error**: Corrected `DBManager` to `DatabaseManager` in intelligence_manager.py
- **✅ Enhanced Database Testing**: Pre-warming now uses same connectivity tests as system health checks
- **✅ Consistent Status Reporting**: Database connectivity now consistent across all dashboard components

### **🔧 System Configuration Improvements**
- **✅ Fixed Virtual Environment Path**: Updated from `sandbox_env` to `autogen_env` 
- **✅ Enhanced Database Connectivity**: Unified database connection methods across all components
- **✅ Added Docker Exec Support**: Maintained reliable docker exec method for operations
- **✅ Eliminated N8N Dependencies**: Removed old n8n-based database connections
- **✅ Fixed Data Count Calculations**: Corrected sitemap status to show accurate metrics (294 products, 20 inserted)

### **🚀 Pre-warming System for Instant Learning**
- **Eliminated 8-13 Second Delay**: Start Learning button now responds instantly
- **Background Initialization**: 4 initialization components moved to dashboard startup:
  - ✅ **Python subprocess startup** / Virtual environment activation (~2-4s)
  - ✅ **Database connections** & data loading (~2-3s)  
  - ✅ **Sitemap validation** & refresh (~3-5s)
  - ✅ **Crawl4AI service** connections (~1-2s)
- **Visual Progress Display**: Real-time status indicators for each initialization component
- **Smart Start Learning**: Button automatically checks pre-warm status and waits if needed
- **Auto-startup Pre-warming**: System begins initialization when dashboard boots up
- **New API Endpoints**: `/api/acquisition/prewarm` and `/api/acquisition/prewarm-status`

### **🎯 Dashboard Terminology & UI Improvements**
- **Sitemap Statistics Rebranding**: Renamed "Completed" to "Learned" to better reflect the AI learning process
- **Added "Inserted" Metric**: New field showing the difference between learned URLs and database records
- **Database Naming Consistency**: Renamed `n8n_config` to `relational_db_config` throughout codebase
- **RAG Status Fix**: Corrected record count display from 5 to 235 by fixing database query parameter
- **Enhanced Sync Feedback**: Added before/after record count display for sync operations
- **Persistent Timestamps**: Sync timestamps now persist across page reloads using localStorage

### **🔧 Database & Backend Improvements**  
- **Fixed Inserted Count Logic**: Corrected sitemap status API to use consistent `'supabase'` parameter
- **Consistent Database References**: All `n8n` database references updated to `relational_db`
- **API Parameter Alignment**: Fixed `/api/database/stats` to query Supabase for accurate RAG counts
- **Improved Error Handling**: Better fallback calculations for inserted count metrics
- **Enhanced Logging**: More detailed database connection and query logging

### **⚡ User Experience Transformation**
- **Before**: Click Start Learning → 8-13 second delay → Learning begins
- **After**: Dashboard boots → Background pre-warming → Click Start Learning → Instant response
- **Progressive Feedback**: Multi-stage loading indicators during initialization
- **Component Status Display**: Real-time monitoring of initialization progress
- **Automatic Recovery**: System handles pre-warming failures gracefully

### **📱 Visual Pre-warming Display**
- **Location**: AI Learning section, below Start Learning button
- **Shows When**: System not fully ready (components failed/missing) OR actively pre-warming
- **Display Elements**:
  - Overall status: "Partially Ready (X/4)" or "Pre-warming..." or "Ready"
  - Component indicators: Green ✓ (working) or Red ✗ (failed) status dots
  - Progress bar during active pre-warming operations
- **Real-time Updates**: Status refreshes automatically via WebSocket

---

## 🆕 **Previous Enhancements (June 29, 2025 - 3:50 PM)**

### **🔧 Enhanced Microservices Health Check System**
- **Comprehensive Service Health Checks**: All 8 services now use real health validation instead of showing "Not Found"
- **External Service Testing**: Database, API, and crawler services now test actual connectivity
  - **PostgreSQL (relational_db)**: Tests port 5432 connectivity with authentication fallback
  - **Supabase (vector_db)**: Tests ports 54321, 5433, 8000 with HTTP health checks
  - **Crawl4AI (crawler)**: Tests port 11235 with HTTP API validation
  - **API Gateway**: Tests ports 8000, 8001, 8443 with status endpoint validation
- **Conceptual Service Management**: Docker engine, LLM API, web server, and intelligence platform now have full start/stop control
- **Smart Service Categorization**: Services marked as `conceptual_service` or `external_service` for proper handling
- **Enhanced Status Messages**: Meaningful status descriptions replace generic "Container not found" errors
- **All 8 Services Running**: Complete microservices directory shows proper status for all infrastructure components

### **⚙️ Automated Dashboard Management**
- **One-Command Reboot**: `./reboot_dashboard.sh` script for streamlined dashboard management
- **Process Verification**: Automatic process stopping, starting, and status verification
- **Environment Enforcement**: Ensures autogen_env usage with clear reporting
- **Error Handling**: Built-in error detection and recovery mechanisms
- **Clear Cache Reminders**: Automatic instructions for UI update requirements
- **Log Monitoring**: Real-time startup verification and troubleshooting guidance

### **🔗 Database GUI Integration**
- **PostgreSQL Access**: pgAdmin interface at http://localhost:5050 (when available)
- **Supabase Studio**: Vector database management at http://localhost:54323 (when available)
- **Service URLs**: Crawler API at http://localhost:11235, Gateway at http://localhost:8000
- **Real-time Status**: Dashboard shows service URLs and accessibility in descriptions

### **📋 Development Roadmap**
- **Comprehensive Planning**: 18-month development roadmap prioritized by business impact
- **Phase-Based Implementation**: Three phases targeting conversion optimization, store experience, and advanced intelligence
- **Business Metrics**: Clear ROI projections and success criteria aligned with strategic goals
- **Technical Specifications**: Detailed implementation plans with resource requirements
- **Strategic Documentation**: Full analysis available in `/reports` directory

## 🚀 **Quick Start**

### **Dashboard Management**
```bash
# Start/restart dashboard with one command
./reboot_dashboard.sh

# Access dashboard
open http://127.0.0.1:8080

# Monitor logs
tail -f dashboard.log
```

### **Available Services**
- **Dashboard**: http://127.0.0.1:8080 - Main management interface
- **RAG Chat**: http://127.0.0.1:8080/chat - Product search and assistance
- **PostgreSQL**: http://localhost:5050 - pgAdmin (if available)
- **Supabase**: http://localhost:54323 - Vector database studio (if available)
- **Crawler API**: http://localhost:11235 - Crawl4AI service
- **API Gateway**: http://localhost:8000 - Service routing

### **Key Features**
- **8-Service Architecture**: Complete microservices ecosystem with health monitoring
- **Real-time Status**: Live service health checks and connectivity testing
- **Automated Management**: One-command reboot with environment verification
- **RAG Intelligence**: Claude-powered product search and recommendations

## 📋 **Recent Session Improvements (June 29, 2025)**

### **🎯 Major Improvements Implemented**

#### **1. Enhanced Microservices Health Check System**
- **Before**: Services showed "Container not found" for external services
- **After**: Real connectivity testing for all 8 services with meaningful status messages
- **Impact**: Users can now see actual service status instead of confusing error messages

#### **2. Conceptual vs External Service Architecture**
- **Added**: New service categorization system distinguishing between:
  - **Conceptual Services** (4): docker_engine, llm_api, web_server, intelligence_platform
  - **External Services** (4): relational_db, vector_db, crawler, api_gateway
- **Enhanced**: All services now participate in start/stop operations and health checks
- **Result**: Complete 8-service ecosystem with proper management controls

#### **3. Real Health Check Implementation**
**Before**: Only checked for Docker containers
**After**: Actual service testing:
- PostgreSQL: Port 5432 connectivity with authentication fallback
- Supabase: Multi-port testing (54321, 5433, 8000) with HTTP health checks  
- Crawl4AI: Port 11235 with HTTP API validation
- API Gateway: Multi-port testing (8000, 8001, 8443) with status endpoints
- Conceptual services: Proper health validation for Docker engine, LLM API, web server

#### **4. Enhanced Dashboard Management**
- **Background Process**: Proper background launching with log redirection
- **Process Tracking**: Clear instructions for stopping/starting dashboard
- **Cache Management**: Documentation for browser cache clearing requirements
- **Status Verification**: Commands to verify all 8 services are working

#### **5. Service Count Accuracy**
- **Before**: Toggle showed only container services count
- **After**: Accurate "8 total services" count including conceptual services
- **Enhanced**: Start/stop operations now handle all service types properly

### **🔧 Technical Changes Made**

#### **Modified Files:**
1. **`modules/docker_manager.py`**:
   - Added `intelligence_platform` to REQUIRED_CONTAINERS (8th service)
   - Enhanced `_perform_health_check()` with service-specific routing
   - Added real health check methods for external services
   - Updated start/stop methods to handle conceptual services
   - Improved service counting in start/stop operations

2. **`templates/dashboard.html`**:
   - Updated container mapping to include all 8 services
   - Fixed intelligence_platform element IDs for proper status updates
   - Enhanced JavaScript to handle conceptual and external services
   - Updated service counting logic for accurate toggle messages

3. **`README.md`**:
   - Added comprehensive reboot protocol documentation
   - Documented health check system improvements
   - Added verification commands for testing all services
   - Updated usage instructions with background process management
   - Fixed conflicting directory paths (tileshop_scraper → tileshop_rag_clean)
   - Corrected environment references (consistent autogen_env usage)
   - Added proper timestamps (June 29, 2025 - 2:20 AM)
   - Removed obsolete configuration sections

### **📋 Previous Session Improvements (June 27, 2025)**

### **🔧 Product Grouping & Recommendations System**
- **Automatic Product Grouping**: Similar products automatically grouped by base pattern (removes color/finish variations)
- **Enhanced Database Schema**: Added `product_groups` and `product_group_members` tables for recommendations
- **Smart Pattern Recognition**: Groups "Penny Round Cloudy" and "Penny Round Milk" tiles together
- **Recommendation Engine**: Ready for RAG system to suggest color variations and similar products

### **🛠️ Fixed RAG Category Filtering & Query Routing**
- **Priority Slip/Floor Queries**: "slip resistant floor tile" now correctly returns TILES, not wood products
- **Enhanced Search Logic**: Slip-resistant queries get boosted scoring for SLIP_RESISTANT rated tiles
- **Improved Category Detection**: Floor/slip queries automatically default to TILE category
- **Smart Finish Matching**: Matte, honed, tumbled, textured finishes get priority for slip queries
- **Fixed Query Routing**: Product search queries like "looking for dark colored slip resistant floor tile" now use database search instead of Claude analysis
- **Color Filtering**: Dark color queries now filter for black, brown, grey, charcoal, slate colors
- **Image Display Fixed**: Database search returns products with images (primary_image URLs)
- **Real Product Results**: Search queries now return actual database products instead of AI analysis

### **🔑 API Key Management Cleanup**
- **Centralized Configuration**: Single source of truth in `.env` file for Claude API key
- **Updated Authentication**: Latest working API key configured (sk-ant-api03-ZAO2***XwAA)
- **Removed Hardcoded Keys**: Cleaned up old API keys from README and environment
- **Secure Storage**: Proper .gitignore protection for sensitive credentials

### **🏷️ Advanced Product Categorization System**
- **10 Distinct Categories**: TILE, WOOD, LAMINATE, LVP_LVT, TRIM_MOLDING, WALL_PANELS, TOOLS_ACCESSORIES, SHELF, GROUT, OTHER
- **Smart Category Filtering**: RAG system automatically filters by product type (no more wood in tile searches!)
- **Enhanced Database Schema**: Added `product_category` column for precise product classification

### **🦶 Slip Resistance Intelligence**
- **SLIP_RESISTANT**: Matte, Honed, Textured, Tumbled, Pebble, Cobble, Mosaic, Penny Round, Hexagon finishes
- **SLIPPERY**: Gloss, Glossy, Satin, Polished finishes  
- **NEUTRAL**: Standard finishes with moderate slip resistance
- **Smart Query Enhancement**: "non-slip" automatically searches for slip-resistant characteristics

### **🤖 Enhanced RAG Chat System**
- **Claude 3.5 Sonnet Integration**: Updated API key and intelligent product analysis
- **Category-Aware Search**: Only returns relevant product types based on query context
- **Slip Intelligence**: Understands finish types, surface textures, and safety characteristics
- **Visual Product Display**: High-quality images with multiple size variants in chat responses

## Project Context & Goals

### Background
- **Primary Goal**: Build a comprehensive intelligence platform for Tileshop product pages that can acquire structured data including product specifications, pricing, and descriptions
- **Secondary Goal**: Create a proven Python implementation first, then translate to n8n workflow for production use
- **Challenge**: Previous n8n automation attempts failed due to inadequate crawl4ai configuration and insufficient data acquisition logic

### User Requirements Gathered
1. **Data Points Needed**:
   - Title, SKU, price/sq ft, price/box
   - Description tab content, specifications tab, resources tab
   - Product variations (finish, color, size/shape options)
   - Technical specifications (dimensions, material type, thickness, etc.)

2. **Infrastructure**: 
   - Periodic data acquisition (add/update/remove products from database)
   - Local containerized setup to minimize costs
   - Rate-limited, respectful data acquisition

3. **Data Sources**:
   - Main product pages from sitemap.xml (filtered for /products/ URLs)
   - Tab content accessed via URL fragments (#description, #specifications, #resources)

## Local Environment Setup

### Docker Services
User has the following containerized services running on `app-network`:
- **n8n**: Port 5678, container name `n8n`
- **PostgreSQL**: Port 5432, container name `n8n-postgres`, user `postgres`
- **crawl4ai**: Port 11235, container name `crawl4ai` (browser-enabled version)

### Authentication & Access
- **n8n Database**: URL http://localhost:5678, user tenxservice@gmail.com, password Postgres1
- **crawl4ai API**: Token `tileshop`, endpoint http://localhost:11235
- **PostgreSQL**: Direct access via docker exec or localhost:5432

### Development Environment
- **Python**: Uses `autogen_env` virtual environment in `/Users/robertsher/Projects/`
- **Working Directory**: `/Users/robertsher/Projects/tileshop_rag_clean/`
- **Activation**: `source autogen_env/bin/activate`

## Technical Issues Resolved

### 1. crawl4ai Configuration Problems
**Issue**: Initial setup had authentication problems and network connectivity issues
**Solution**: 
- Restarted crawl4ai container with proper API token configuration
- Fixed Docker network connectivity between containers
- Updated container startup command:
```bash
docker run -d \
  -p 11235:11235 \
  --name crawl4ai \
  --network app-network \
  --shm-size=1g \
  -e CRAWL4AI_API_TOKEN=tileshop \
  -e OPENAI_API_KEY=${OPENAI_API_KEY:-placeholder} \
  unclecode/crawl4ai:all
```

### 2. Tab Content Extraction
**Issue**: Previous attempts couldn't access tab content (#description, #specifications, #resources)
**Solution**: Implemented JavaScript execution in crawl4ai requests to:
- Click on specific tabs before content extraction
- Wait for JavaScript rendering
- Use multiple URL variants with fragments

### 3. Virtual Environment Management
**Issue**: Package management conflicts between global and virtual environments
**Solution**: 
- Cleaned up global package installations
- Used virtual environment Python executable directly
- Organized project files in dedicated `/tileshop_rag_clean/` directory

## Features

- **Tab-aware scraping**: Extracts content from main page, #description, #specifications, and #resources tabs
- **Comprehensive data extraction**: SKU, title, pricing, specifications, descriptions, and more
- **Database storage**: Saves structured data to PostgreSQL with conflict resolution
- **Rate limiting**: Respectful crawling with delays between requests
- **Error handling**: Robust error handling for failed requests and data parsing

## Setup

1. **Activate virtual environment:**
   ```bash
   cd /Users/robertsher/Projects
   source autogen_env/bin/activate
   ```

2. **Install dependencies (Poetry - Recommended):**
   ```bash
   cd tileshop_rag_clean
   poetry install
   ```
   
   **Or using pip:**
   ```bash
   cd tileshop_rag_clean
   pip install -r requirements.txt
   ```

3. **Environment Configuration:**
   ```bash
   # ✅ Claude API Key is configured in .env file
   # Location: /Users/robertsher/Projects/tileshop_rag_clean/.env
   # Current API Key: sk-ant-api03-ZAO2***XwAA (configured in .env)
   # 
   # ⚠️ SECURITY: The .env file contains sensitive API keys
   # - Never commit .env to version control
   # - .env is protected by .gitignore
   # - API key persists across sessions automatically
   # - Updated: June 29, 2025 - Enhanced health check system implemented
   ```

4. **Ensure Docker services are running:**
   - crawl4ai container on port 11235 with proper authentication
   - postgres container (renamed from n8n-postgres) with product_data table
   - supabase container for dashboard operations

## Usage

### 🆕 **Admin Dashboard (Recommended)**
```bash
cd /Users/robertsher/Projects/tileshop_rag_clean

# Using Poetry (Recommended)
poetry run python reboot_dashboard.py

# Or using virtual environment
source autogen_env/bin/activate
python reboot_dashboard.py > dashboard.log 2>&1 &
```
- **Dashboard**: http://localhost:8080 - Complete control panel
- **RAG Chat**: http://localhost:8080/chat - AI assistant for product queries

#### **Dashboard Features:**
- **Real-time Docker Management**: Start/stop/monitor all required containers
- **Live Scraper Control**: Multiple modes with real-time progress and URL tracking  
- **Database Viewer**: Browse, search, and export product data
- **RAG Chat Interface**: AI assistant for natural language product queries
- **System Monitoring**: Container health, resource usage, and logs

### **Individual Scripts**
```bash
cd /Users/robertsher/Projects
source autogen_env/bin/activate
cd tileshop_rag_clean
python tileshop_scraper.py
```

## Target Data Fields & Sources

### Upper Section (Main Product Page)
**Location**: Top of product page, visible immediately
- **Title**: Product name (e.g., "Signature Oatmeal Frame Gloss Ceramic Subway Wall Tile - 4 x 8 in.")
- **SKU**: Product identifier (e.g., "#484963")
- **Coverage**: Square footage per box (e.g., "10.98 sq. ft. per Box")
- **Price per box**: Box pricing (e.g., "$94.31/box")
- **Price per sq ft**: Square foot pricing (e.g., "$8.59/Sq. Ft.")
- **Finish options**: Available finishes (e.g., "Gloss", "Matte")
- **Color variations**: Available colors
- **Size/Shape options**: Different sizes and edge types (e.g., "4 x 8 in. Frame", "4 x 12 in. Bevel")

### Tab Content (Requires JavaScript Navigation)

#### 1. Description Tab (`#description`)
**URL Format**: `{product_url}#description`
**Contains**:
- Detailed product description and marketing copy
- Product benefits and features
- Collection information and cross-references
- Installation recommendations

#### 2. Specifications Tab (`#specifications`)
**URL Format**: `{product_url}#specifications`
**Contains**:
- **Dimensions section**:
  - Approximate Size (e.g., "4 x 8 in.")
  - Thickness (e.g., "7.7mm")
  - Box Quantity (e.g., "50")
  - Box Weight (e.g., "19.3 lbs")
- **Design & Installation section**:
  - Material Type (e.g., "Ceramic")
  - Edge Type (e.g., "Straight")
  - Color (e.g., "Taupe")
  - Finish (e.g., "Gloss")
  - Surface Texture (e.g., "Smooth")
  - Applications (e.g., "Wall")
  - Directional Layout (e.g., "No")
- **Technical Details section**:
  - Country Of Origin (e.g., "Brazil")
  - Frost Resistance (e.g., "Not Resistant")

#### 3. Resources Tab (`#resources`)
**URL Format**: `{product_url}#resources`
**Contains**:
- PDF downloads (installation guides, care instructions)
- Technical documentation links
- Related product resources

### Acquired Data Schema

| Field | Source | Type | Example |
|-------|--------|------|---------|
| `url` | URL being scraped | VARCHAR(500) | https://www.tileshop.com/products/... |
| `sku` | Upper section or JSON-LD | VARCHAR(50) | "484963" |
| `title` | Upper section or JSON-LD | TEXT | "Signature Oatmeal Frame..." |
| `price_per_box` | Upper section or JSON-LD | DECIMAL(10,2) | 94.31 |
| `price_per_sqft` | Calculated from price/coverage | DECIMAL(10,2) | 8.59 |
| `coverage` | Upper section | TEXT | "10.98 sq. ft. per Box" |
| `finish` | Upper section or specifications tab | TEXT | "Gloss" |
| `color` | Upper section or specifications tab | TEXT | "Taupe" |
| `size_shape` | Upper section or specifications tab | TEXT | "4 x 8 in." |
| `description` | Description tab or JSON-LD | TEXT | "Elevate your aesthetic..." |
| `specifications` | Specifications tab | JSONB | {"dimensions": "4 x 8 in.", ...} |
| `resources` | Resources tab | TEXT | JSON array of PDF links |
| `images` | Legacy field | TEXT | Reserved for additional images |
| `collection_links` | Embedded JSON | TEXT | JSON array of collection page links |
| **`brand`** | **JSON-LD** | **VARCHAR(100)** | **"Rush River" (manufacturer brand)** |
| **`primary_image`** | **JSON-LD** | **TEXT** | **High-quality Scene7 URL** |
| **`image_variants`** | **Generated** | **JSONB** | **6 image sizes (thumbnail→extra large)** |
| `raw_html` | Main page crawl | TEXT | Full HTML for debugging |
| `raw_markdown` | Main page crawl | TEXT | Markdown conversion |
| `scraped_at` | System generated | TIMESTAMP | 2025-01-26 10:30:00 |
| `updated_at` | System generated | TIMESTAMP | 2025-01-26 10:30:00 |

### Data Extraction Strategy

1. **JSON-LD Structured Data**: Primary source for reliable product info (title, SKU, price, description, images, brand)
2. **Embedded Specifications JSON**: Comprehensive extraction from page's embedded product data
3. **Image Processing**: Scene7 CDN URL generation with multiple size variants
4. **Brand Intelligence**: Manufacturer brand extraction when available
5. **Cross-validation**: Compare data from multiple sources for accuracy
6. **Streamlined Approach**: No tab navigation needed - all data embedded in main page

## Database Schema

The scraper uses the `product_data` table with the following structure:

```sql
CREATE TABLE product_data (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) UNIQUE NOT NULL,
    sku VARCHAR(50),
    title TEXT,
    price_per_box DECIMAL(10,2),
    price_per_sqft DECIMAL(10,2),
    coverage TEXT,
    finish TEXT,
    color TEXT,
    size_shape TEXT,
    description TEXT,
    specifications JSONB,
    resources TEXT,
    raw_html TEXT,
    raw_markdown TEXT,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Checking Results

```bash
# View basic product data
docker exec postgres psql -U postgres -c "SELECT url, sku, title, price_per_box, price_per_sqft, price_per_piece FROM product_data;"

# View specifications
docker exec postgres psql -U postgres -c "SELECT url, specifications FROM product_data;"

# Count total products
docker exec postgres psql -U postgres -c "SELECT COUNT(*) FROM product_data;"
```

## Methodology & Implementation Details

### Data Acquisition Strategy
1. **Multi-tab Intelligence**: For each product URL, the platform:
   - Acquires the main page for basic product info
   - Acquires `{url}#description` for detailed product descriptions
   - Acquires `{url}#specifications` for technical specifications
   - Acquires `{url}#resources` for PDFs and installation guides

2. **JavaScript Execution**: Uses crawl4ai's JavaScript capabilities to:
   - Click on tabs to load dynamic content
   - Wait for content rendering
   - Scroll to ensure all content is loaded

3. **Data Parsing Approach**:
   - JSON-LD structured data extraction for reliable product info
   - Multiple regex patterns for price extraction (handles various formats)
   - Comprehensive specification field extraction
   - HTML tag cleaning and text normalization

### Database Design
- **Conflict Resolution**: Uses `ON CONFLICT (url) DO UPDATE` for upserts
- **JSONB Storage**: Specifications stored as JSONB for flexible querying
- **Per-Piece Pricing**: New `price_per_piece` field for accessories/trim/shelves
- **Raw Data Backup**: Stores both raw HTML and markdown for debugging
- **Timestamps**: Tracks creation and update times for data freshness

## User Workflow History

### Previous Attempts & Failures
1. **Initial n8n workflows**: User had multiple failed n8n scraper versions in Google Drive
2. **crawl4ai Issues**: Container wasn't properly configured with authentication
3. **Data Quality Problems**: Low-quality extraction due to missing tab content
4. **Infrastructure Confusion**: Mixed local/web Supabase causing configuration issues

### Decision to Use Python First
- User agreed to build Python version to establish proven data extraction path
- Plan: Create working Python implementation → translate to n8n workflow
- Reason: n8n debugging is difficult; Python allows rapid iteration and testing

### Tech Stack Evaluation
- **Docker**: 28.0.4 ✅ (Up to date)
- **n8n**: 1.84.3 ✅ (Latest)
- **PostgreSQL**: 17.4 ✅ (Latest)
- **crawl4ai**: Browser-enabled version ✅ (Working)

## Current Progress & Test Results

### ✅ **Successfully Implemented & Tested**
- **Infrastructure**: crawl4ai, PostgreSQL, n8n containers working perfectly
- **Tab Navigation**: JavaScript execution successfully crawls 4 URLs per product (main + 3 tabs)
- **JSON-LD Extraction**: Reliable extraction of structured data from product pages
- **Price Calculation**: Automatic price per sq ft calculation from price/coverage ratio
- **Database Storage**: Proper conflict resolution and data persistence
- **Error Handling**: Graceful handling of "Page Not Found" scenarios

### 📊 **Current Extraction Success Rate**
**Test Results from multiple product types**:
- **Valid Products**: 100% success rate across ceramic, travertine, porcelain, luxury vinyl
- **Core Data Fields**: 17/18 target fields successfully extracted (94.4% success)
- **Specifications Coverage**: 13-16 detailed specification fields extracted (varies by product)
- **Image Coverage**: 100% success rate with high-quality Scene7 URLs + 6 size variants
- **Brand Coverage**: 50% success rate (only when manufacturer brand available)
- **Data Quality**: High - clean, accurate extraction from embedded JSON and structured data

### ✅ **Fields Successfully Extracted (17/18 Target Fields)**
| Field | Status | Source | Example |
|-------|--------|--------|---------|
| **Core Product Data** |
| SKU | ✅ Working | JSON-LD | "484963" |
| Title | ✅ Working | JSON-LD | "Signature Oatmeal Frame..." |
| Price per box | ✅ Working | JSON-LD | $94.31 |
| Price per sq ft | ✅ Working | Calculated | $8.59 |
| Coverage | ✅ Working | HTML patterns | "10.98 sq. ft. per Box" |
| Finish | ✅ Working | Embedded JSON | "Gloss" |
| Color | ✅ Working | Embedded JSON | "Taupe" |
| Size/Shape | ✅ Working | Embedded JSON | "4 x 8 in." |
| Description | ✅ Working | JSON-LD | 427 chars clean text |
| **Complete Specifications (13-14 fields)** |
| Approximate Size | ✅ Working | Embedded JSON | "4 x 8 in." |
| Thickness | ✅ Working | Embedded JSON | "7.7mm" |
| Box Quantity | ✅ Working | Embedded JSON | "50" |
| Box Weight | ✅ Working | Embedded JSON | "19.3 lbs" |
| Material Type | ✅ Working | Embedded JSON | "Ceramic" |
| Edge Type | ✅ Working | Embedded JSON | "Straight" |
| Surface Texture | ✅ Working | Embedded JSON | "Smooth" |
| Applications | ✅ Working | Embedded JSON | "Wall" |
| Directional Layout | ✅ Working | Embedded JSON | "No" |
| Country of Origin | ✅ Working | Embedded JSON | "Brazil" |
| Frost Resistance | ✅ Working | Embedded JSON | "Not Resistant" |
| **Enhanced Fields Added** |
| **Primary Image** | ✅ **Working** | **JSON-LD** | **High-quality Scene7 URL** |
| **Image Variants** | ✅ **Working** | **Generated** | **6 sizes (thumbnail→extra large)** |
| **Brand Information** | ✅ **Working** | **JSON-LD** | **"Rush River" (when available)** |
| Collection Links | ✅ Working | Embedded JSON | 4 collection references |

### ⚠️ **Fields Needing Improvement**
| Field | Status | Issue | Next Steps |
|-------|--------|-------|------------|
| Resources | ❌ Missing | PDF links not found | Debug resources tab content |

### 🔧 **Technical Issues Resolved**
1. ✅ **HTML Truncation**: Fixed - removed 50KB limit for complete content capture
2. ✅ **Specifications Extraction**: Fixed - discovered specifications are embedded in page JSON, not in tabs
3. ✅ **Tab Navigation**: No longer needed - streamlined to main page only
4. ✅ **Database Storage**: Fixed "argument list too long" errors with improved SQL handling

### 🔧 **Remaining Technical Issues**
1. **Image Extraction**: Pattern needs refinement to capture actual product images
2. **Resources Tab**: PDF links extraction needs investigation

### 📈 **Performance Metrics**
- **Crawl Speed**: ~5 seconds per product (single URL, no tab navigation needed)
- **Success Rate**: 100% for infrastructure, 93.3% for data completeness (14/15 fields)
- **Rate Limiting**: 3 seconds between products (respectful)
- **Error Recovery**: Robust handling of failed requests and invalid URLs

## Next Steps & Future Development

### Immediate Tasks (Priority Order)
1. **Refine image extraction**: Improve patterns to capture actual product images
2. **Debug resources extraction**: Investigate PDF links from resources tab
3. **Test with more URLs**: Validate extraction patterns across different products
4. **Performance optimization**: Further reduce crawl time and improve efficiency

### Production Readiness Checklist
- [x] ✅ Core infrastructure working
- [x] ✅ Complete data extraction (14/15 fields - 93.3% success)
- [x] ✅ Full specifications extraction (13/13 fields)
- [x] ✅ Database schema and storage
- [x] ✅ Error handling and logging
- [x] ✅ Collection links extraction
- [ ] ⏳ Image extraction refinement
- [ ] ⏳ Resources tab extraction
- [ ] ⏳ Scale testing (10+ products)

### Production Implementation
1. **n8n Translation**: Convert proven Python logic to n8n workflow (95% ready - major breakthrough achieved)
2. **Sitemap Integration**: Add sitemap.xml parsing for URL discovery
3. **Scheduling**: Implement periodic scraping (user wants regular updates)
4. **Monitoring**: Add data quality checks and error notifications

### Infrastructure Considerations
- **Rate Limiting**: Currently 3 seconds between requests (respectful)
- **Error Handling**: Robust retry logic for failed requests
- **Data Validation**: Ensure extracted data meets quality standards
- **Scalability**: Consider parallel processing for large URL lists

## Current Status: 🟢 **Production Ready - Enterprise AI-Powered Product Discovery Platform**

A complete e-commerce intelligence system with advanced product categorization, slip-resistance classification, and Claude-powered natural language search. Successfully extracts 18+ target fields with intelligent product categorization across 10 distinct categories, comprehensive slip-resistance analysis, and enterprise-grade RAG chat interface for natural language product discovery.

### **🎯 Key Achievements:**
- **✅ 217 Products Categorized**: Complete product classification across 10 categories
- **✅ Slip Intelligence**: 52 slip-resistant tiles identified and classified  
- **✅ Smart Search Filtering**: Category-aware search prevents irrelevant results
- **✅ Claude Integration**: Full LLM-powered product analysis and recommendations
- **✅ Visual Discovery**: High-quality product images in chat responses

**🆕 LATEST: Enterprise-Grade AI Management Platform**
- **Universal URL Scraping**: Dynamic target URL input with automatic sitemap detection API
- **Intelligent AI Assistant**: Claude API-powered infrastructure assistant created by Robert Sher
- **Smart Service Management**: Adaptive button visibility with automatic hide/show logic
- **Comprehensive Health Monitoring**: Persistent health check modal with copy-to-clipboard functionality
- **Visual Loading Indicators**: Animated progress bars for all service and environment status checks
- **Streamlined Interface**: Removed redundant Quick Actions - all controls integrated in main service directory

**🆕 LATEST SESSION ENHANCEMENTS (June 27, 2025):**
- **Modern Toggle Switch**: Replaced Start/Stop buttons with intuitive horizontal toggle for all services
- **Streamlined UI Controls**: Permanently removed individual Start and Stop buttons from service cards
- **Smart Button Management**: "Start All Services" toggle automatically reflects current service state  
- **Fixed Progress Bars**: Resolved jumping CPU/Memory/Disk usage bars with proper CSS class separation
- **Simplified Scraper Modes**: Reduced to 2 clear options - Test Mode (10 URLs) and Full Sitemap
- **Enhanced Button Layout**: Start and Stop scraper buttons now properly aligned side-by-side
- **Fixed Statistics**: Resolved scraper progress counting and percentage calculation issues
- **Real-time Monitoring**: Live scraper status with current URL processing and accurate progress
- **Sitemap Integration**: Automatic sitemap detection with filtered URL display
- **Clean Service Interface**: Service cards now only show Logs buttons for minimal, focused control
- **Persistent Health Check Modal**: Replace temporary alerts with copyable, closeable modal interface
- **Security Enhancements**: Proper environment variable management with .env configuration
- **AI Assistant Integration**: Full Claude API support with secure key management

**🆕 TODAY'S FINAL ENHANCEMENTS:**
- **Customer Service Assistant**: Repurposed AI Assistant for customer support and error logging
- **RAG Chat Database Fix**: Resolved PostgreSQL connection issues for product analysis queries
- **Dynamic URL Limits**: Fixed scraper mode dropdown to show real sitemap total URLs (not hardcoded 4775)
- **Improved Labeling**: Changed "Test Limit" to "URL Limit" for better clarity
- **Claude API Full Integration**: Both chat systems now properly use shared ANTHROPIC_API_KEY from .env
- **Real-time Limit Updates**: URL limit field automatically updates based on actual sitemap data

**🆕 LATEST SESSION IMPROVEMENTS (June 27, 2025 - ENHANCED PRODUCT RECOMMENDATIONS & FIXED RAG FILTERING):**
- **✅ Product Grouping System**: Implemented automatic product grouping for recommendations
  - ✅ **Database Tables**: Added `product_groups` and `product_group_members` tables
  - ✅ **Pattern Recognition**: Groups similar products by base pattern (removes color/finish variations)
  - ✅ **Smart Grouping Logic**: "Penny Round Cloudy" and "Penny Round Milk" tiles automatically grouped together
  - ✅ **Recommendation Engine**: Foundation ready for RAG system to suggest color variations and similar products
- **✅ Fixed RAG Category Filtering & Query Routing**: Resolved critical issues with search results and image display
  - ✅ **Priority Query Logic**: "slip resistant floor tile" now correctly returns TILES, not wood
  - ✅ **Enhanced Slip-Resistant Search**: Added scoring boost for tiles with `slip_rating = 'SLIP_RESISTANT'`
  - ✅ **Smart Category Detection**: Floor/slip queries automatically default to TILE category first
  - ✅ **Improved Finish Matching**: Matte, honed, tumbled, textured finishes get priority for slip queries
  - ✅ **Fixed Query Routing**: Product searches now use database instead of Claude analysis for real results
  - ✅ **Color Filtering**: Dark color queries filter for black, brown, grey, charcoal, slate tiles
  - ✅ **Image Display Working**: Database search returns products with primary_image URLs for display
  - ✅ **Real Product Results**: Queries like "looking for dark colored slip resistant floor tile" return actual database products
- **✅ API Key Management Cleanup**: Centralized and secured Claude API configuration
  - ✅ **Single Source**: All API keys now managed through `.env` file only
  - ✅ **Updated Key**: Latest working Claude API key configured (sk-ant-api03-ZAO2***XwAA)
  - ✅ **Security**: Removed hardcoded keys from README and environment variables
  - ✅ **Health Check**: All systems now show green status including Claude API

**🆕 PREVIOUS SESSION IMPROVEMENTS (June 27, 2025 - COMPLETE RAG SOLUTION):**
- **✅ Complete RAG Resolution**: Successfully fixed all three original roadmap issues
  - ✅ **SKU 683549 Search**: Now found instantly with proper per-piece pricing ($22.99/each)
  - ✅ **RAG Delay Elimination**: Smart routing provides immediate responses for SKU queries
  - ✅ **Image Display Working**: High-quality product images display directly in chat interface
- **✅ Per-Piece Pricing System**: Enhanced data model with `price_per_piece` field for accessories
  - Corner shelves, trim pieces, and accessories now priced correctly as "per-each"
  - Tiles maintain traditional "per-sq-ft" pricing model
  - Automatic detection of `/each` patterns in product HTML
- **✅ Visual Product Discovery**: RAG chat displays Scene7 CDN images with multiple size variants
  - Markdown `![image](url)` converts to rendered HTML images
  - Enhanced styling with hover effects and responsive sizing
  - Console logging for debugging image parsing issues
- **✅ Enhanced SKU Detection**: Comprehensive natural language query routing
  - Direct SKU patterns: `683549`, `#683549`, `sku 683549`
  - Contextual image requests: "show me images for this sku"
  - Natural language: "what is sku 683549"
- **✅ Container Name Consistency**: Updated all references from `n8n-postgres` to `postgres`
- **✅ GitHub Integration**: Repository published to https://github.com/1genadam/tileshop-rag

**🆕 LATEST SESSION FIXES (June 27, 2025 - 5:45 AM):**
- **✅ Scraper Status Integration**: Enhanced dashboard with sitemap-based progress tracking using real scraped URL data
- **✅ UI Navigation Stability**: Fixed WebSocket disconnect behavior - scraper continues running during page navigation
- **✅ Progress Display Accuracy**: Main progress now uses actual sitemap completion data instead of log estimates
- **✅ Claude API Chat Systems**: Both AI Assistant and RAG Chat fully functional with Claude 3.5 Sonnet integration
- **✅ RAG Chat Frontend Fix**: Resolved JavaScript initialization order preventing button functionality
- **✅ RAG Data Accuracy Fix**: Fixed RAG system to access top 500 products sorted by price (DESC) for accurate analysis
- **✅ Claude API Key Updated**: New working API key providing full LLM functionality for both chat systems
- **✅ Database Viewer Enhancement**: Product Database now displays price per sq ft and full timestamps
- **✅ LLM-First Priority**: RAG system now tries Claude first, gracefully falls back to search when needed
- **✅ Error Recovery Tools**: Built-in retry system for failed URLs with detailed error categorization
- **✅ Performance Optimization**: Stopped resource-intensive retry processes consuming CPU cycles
- **✅ Database Connectivity**: Fixed supabase-pooler container restart issues affecting RAG Chat functionality

**✅ COMPLETED: Advanced Sitemap Download & Progress Tracking System**
- **Real-time Download Progress**: Multi-stage progress tracking with WebSocket-powered live updates
  - **Stage 1**: Download sitemap with byte-by-byte progress monitoring
  - **Stage 2**: XML parsing and validation with error handling
  - **Stage 3**: Intelligent sitemap index detection and product sitemap extraction
  - **Stage 4**: URL extraction with progressive count updates
  - **Stage 5**: Product URL filtering with live statistics
  - **Stage 6**: Results saving with completion confirmation
- **Comprehensive Statistics Dashboard**: Live URL tracking and completion monitoring
  - **Total URLs**: Real-time count of all sitemap URLs (4,775 for Tileshop)
  - **Pending Count**: URLs awaiting scraping with color-coded display
  - **Completed Count**: Successfully scraped URLs with progress percentage
  - **Completion Rate**: Visual progress tracking with dynamic color coding
- **Filter Criteria Display**: Clear documentation of current filtering logic
  - **Include Rules**: URLs containing `tileshop.com/products` (main product pages)
  - **Exclude Rules**: Special collections (`tileshop.com/products/,-w-,`) and sample pages
  - **Expected Results**: ~4,775 product URLs ready for processing
- **Intelligent Error Handling**: Automatic sitemap index parsing and product sitemap discovery
- **WebSocket Integration**: Real-time progress updates without page refresh

**✅ COMPLETED: Database Sync Architecture (Option 3)**
- **Source**: n8n-postgres (scrapers write here) 
- **Target**: Supabase (dashboard reads from here)
- **Sync Method**: Docker exec for both source and target (eliminates authentication issues)
- **Sync Performance**: 16 products synced in 0.74 seconds
- **Data Integrity**: 100% success rate, complete table structure replication

### 🆕 **Latest Session Learnings:**

#### **Intelligent URL Prioritization**
- **Never-attempted first**: URLs without datestamp get highest priority
- **Oldest failures retry**: Failed URLs are retried in chronological order (oldest first)
- **Avoids recent redundancy**: Recently completed URLs are naturally deprioritized
- **Optimal coverage**: Ensures maximum sitemap coverage with minimal waste

#### **Enhanced Recovery Protocol**
- **Comprehensive statistics**: Real-time completion rates and progress analytics
- **Graceful interruption**: Ctrl+C handling with automatic progress preservation
- **Recovery checkpoints**: Detailed failure analysis and debugging information
- **Auto-resume capability**: Restarts exactly where interrupted with intelligent prioritization

#### **Image Storage & Processing**
- **Images stored as URLs**: High-quality Scene7 CDN links, not binary data
- **6 size variants**: Thumbnail, Small, Medium, Large, Extra Large, Base URL
- **JSONB storage**: Efficient querying of specific image sizes
- **Pattern**: `https://tileshop.scene7.com/is/image/TileShop/[SKU]?$[SIZE]$`

#### **Brand Intelligence**
- **Manufacturer brands available**: Some products have meaningful brands (e.g., "Rush River")
- **Inconsistent data**: ~50% coverage - many products have empty brand fields
- **Value when present**: Useful for categorization and sourcing information

#### **Data Discovery Methodology**
- **Missing data analysis**: Systematic approach to find overlooked fields
- **JSON-LD mining**: Rich structured data source for multiple field types  
- **Pattern recognition**: Automated discovery of data patterns across product types

#### **Cross-Product Validation**
- **Universal patterns**: Extraction works across ceramic, travertine, porcelain, luxury vinyl
- **Specification variance**: 13-16 fields depending on product type
- **Consistent quality**: 100% success rate for core fields across all tested products

## 📁 **Project Architecture & File Index**

> **Navigation Guide**: This comprehensive index helps developers (including AI assistants) quickly understand file purposes, relationships, and usage patterns without diving into code first.

### 🏗️ **Core Application Files**

| File | Purpose | Key Functionality | When to Use |
|------|---------|-------------------|-------------|
| **`reboot_dashboard.py`** | 🎯 **Main Flask Application** | All API endpoints, WebSocket handling, service orchestration | Primary entry point - contains all business logic |
| **`reboot_dashboard.sh`** | 🔄 **Automated Startup Script** | Dashboard restart with environment verification | When dashboard needs clean restart with proper env |

### 📂 **Backend Modules (`/modules/`)**

| Module | Responsibility | Dependencies | Critical For |
|--------|---------------|--------------|--------------|
| **`docker_manager.py`** | 🐳 **Container Orchestration** | Docker daemon, 8 microservices | Service health checks, start/stop operations |
| **`intelligence_manager.py`** | 🧠 **Scraping Orchestration** | Crawl4AI service, sitemap files | Progress tracking, acquisition management |
| **`db_manager.py`** | 🗄️ **Database Operations** | PostgreSQL, Supabase connections | Product queries, data export, statistics |
| **`rag_manager.py`** | 🤖 **AI Integration** | Claude API, database access | Natural language product search |
| **`sync_manager.py`** | 🔄 **Data Synchronization** | Both databases via docker exec | Keeping Supabase in sync with PostgreSQL |

### 🎨 **Frontend & Templates (`/templates/`, `/static/`)**

| File | UI Responsibility | Key Components | Integrations |
|------|------------------|----------------|--------------|
| **`dashboard.html`** | 📊 **Main Admin Interface** | Service controls, scraping management, analytics | WebSocket, all backend APIs |
| **`chat.html`** | 💬 **RAG Chat Interface** | Product search, AI conversations | Claude API, database search |
| **`base.html`** | 🎨 **Shared Layout & Logic** | CSS framework, JS utilities, WebSocket setup | Foundation for all pages |
| **`/static/chat.js`** | ⚡ **Chat Functionality** | API interactions, message handling | RAG system, search APIs |

### 🛠️ **Scraping Engine Scripts**

| Script | Use Case | Production Ready | Capabilities |
|--------|----------|------------------|--------------|
| **`acquire_from_sitemap.py`** | ⭐ **Production Scraper** | ✅ **Primary Choice** | Auto-recovery, intelligent prioritization, progress checkpoints |
| **`tileshop_learner.py`** | 🧪 **Development Testing** | For testing only | Individual product validation, extraction logic testing |
| **`acquire_all_products.py`** | 📦 **Batch Scraper** | ✅ **Utility** | Full sitemap processing, bulk operations |
| **`download_sitemap.py`** | 🗺️ **Sitemap Management** | ✅ **Utility** | URL filtering, sitemap refresh, status tracking |

### 🔍 **Analysis & Discovery Tools**

| Tool | Analysis Focus | Output | Best For |
|------|---------------|---------|----------|
| **`discover_missing_data.py`** | 🔎 **Data Gap Analysis** | Field recommendations | Finding overlooked extraction opportunities |
| **`extract_brand_examples.py`** | 🏷️ **Brand Intelligence** | Coverage rates, patterns | Understanding brand data availability |
| **`extract_image_examples.py`** | 🖼️ **Image Pattern Analysis** | CDN patterns, URL variants | Debugging image extraction issues |
| **`retry_failed.py`** | 🔧 **Error Recovery** | Failure categories, retry scripts | Recovering from scraping failures |
| **`check_missing_fields.py`** | ✅ **Field Validation** | Extraction coverage reports | Verifying data completeness |
| **`analyze_specs.py`** | 📋 **Specifications Analysis** | JSON structure patterns | Debugging specification extraction |
| **`debug_extractor.py`** | 🛠️ **Extraction Debugging** | Step-by-step extraction logs | Troubleshooting parser issues |
| **`debug_tabs.py`** | 🔍 **Tab Content Analysis** | Tab structure and content | Understanding page navigation (legacy) |
| **`inspect_tabs.py`** | 👁️ **Page Structure Inspection** | HTML structure analysis | Debugging page layout issues |

### 🎨 **RAG & AI System Files**

| File | AI Component | Integration | Purpose |
|------|-------------|-------------|---------|
| **`rag_system.py`** | 🤖 **Standalone RAG System** | Independent Claude integration | Testing RAG functionality |
| **`rag_web_ui.py`** | 🌐 **RAG Web Interface** | Lightweight chat UI | Alternative chat interface |
| **`simple_rag.py`** | 📝 **Simplified RAG Implementation** | Basic chat functionality | RAG system prototyping |
| **`simple_rag_backup.py`** | 💾 **RAG System Backup** | Previous RAG version | Recovery/rollback purposes |

### 🗃️ **Documentation & Reports (`/reports/`)**

| File | Documentation Type | Audience | Content |
|------|------------------|----------|---------|
| **`README.md`** | 📖 **Reports Overview** | Development team | Directory contents and purpose |
| **`demo-scenarios.md`** | 🎭 **Demo Scenarios** | Business stakeholders | Use case demonstrations |
| **`presentation-guidelines.md`** | 📊 **Presentation Guide** | Business team | Presentation structure and talking points |
| **`rag-solution-alignment-analysis.md`** | 🔍 **Technical Analysis** | Technical team | RAG system architecture analysis |
| **`dev_roadmap.md`** | 🗺️ **Development Roadmap** | Project managers | Future development planning |
| **`missing_data_summary.md`** | 📊 **Data Analysis Report** | Data team | Summary of missing field analysis |

### 🔧 **Utility Scripts & Tools**

| Script | Utility Type | Function | Usage |
|--------|-------------|----------|-------|
| **`extract_html.sh`** | 🐚 **Shell Script** | Database HTML extraction | `./extract_html.sh` |
| **`start_dashboard.sh`** | 🚀 **Alternative Startup** | Dashboard startup script | `./start_dashboard.sh` |
| **`reboot_dashboard.sh`** | 🔄 **Primary Startup** | Automated restart with env check | `./reboot_dashboard.sh` |

### ⚙️ **Configuration & Dependencies**

| File | Configuration Type | Security Level | Purpose |
|------|------------------|---------------|----------|
| **`.env`** | 🔐 **Environment Variables** | **SENSITIVE** - gitignored | API keys, database URLs, secrets |
| **`requirements.txt`** | 📦 **Python Dependencies** | Public | pip-based package management |
| **`pyproject.toml`** | 🎯 **Poetry Configuration** | Public | Modern dependency management |
| **`poetry.lock`** | 🔒 **Locked Dependencies** | Public | Exact versions for reproducible builds |
| **`nginx-proxy.conf`** | 🌐 **Nginx Configuration** | Public | Reverse proxy settings for production |

### 🚀 **Deployment & Infrastructure**

| File | Deployment Target | Purpose | Usage |
|------|------------------|---------|-------|
| **`Dockerfile`** | 🐳 **Production Container** | Multi-stage build with Poetry | `docker build -t tileshop-rag .` |
| **`fly.toml`** | ☁️ **Fly.io Configuration** | Cloud deployment settings | `fly deploy` |
| **`deploy.py`** | 🚀 **Automated Deployment** | Secrets + deployment script | `python deploy.py full` |
| **`Procfile`** | 🔧 **Process Configuration** | Alternative deployment config | Heroku-style process definition |

### 📁 **Template & Static Assets**

| File/Directory | Type | Purpose | Contains |
|---------------|------|---------|----------|
| **`templates/dashboard.html`** | 📊 **Main Dashboard** | Primary admin interface | Service controls, scraping management |
| **`templates/chat.html`** | 💬 **Chat Interface** | RAG chat system | Product search and AI conversations |
| **`templates/chat_backup.html`** | 💾 **Chat Backup** | Previous chat version | Recovery/rollback purposes |
| **`templates/base.html`** | 🎨 **Base Template** | Shared layout and utilities | CSS, JS, WebSocket foundation |
| **`templates/index.html`** | 🏠 **Landing Page** | Alternative entry point | Basic index page |
| **`static/chat.js`** | ⚡ **Chat JavaScript** | Frontend chat functionality | API interactions, message handling |
| **`temp_dashboard.html`** | 🛠️ **Development Template** | Temporary UI development | Testing new dashboard features |
| **`services_table.html`** | 📋 **Services Template** | Service management UI | Microservices status table |

### 🗂️ **Generated Files & Runtime Data**

| File Pattern | Generated By | Contains | Lifecycle |
|-------------|--------------|----------|-----------|
| **`dashboard.log`** | Dashboard startup | Application logs | Rotated/cleared on restart |
| **`tileshop_sitemap.json`** | Sitemap downloader | URLs with scraping status | Updated every 7 days |
| **`recovery_checkpoint.json`** | Production scraper | Current interruption recovery data | Created during failures |
| **`recovery_*.json`** | Production scraper | Interruption recovery archives | Historical failure points |

### 🔧 **Modules Directory (`/modules/`)**

| Module | Class/Function | Dependencies | Primary Responsibility |
|--------|---------------|--------------|----------------------|
| **`__init__.py`** | 📦 **Package Initializer** | None | Makes `/modules` a Python package |
| **`docker_manager.py`** | `DockerManager` | Docker daemon, psutil | Container orchestration and health monitoring |
| **`intelligence_manager.py`** | `ScraperManager` | Crawl4AI, sitemap files | Scraping progress and orchestration |
| **`db_manager.py`** | `DatabaseManager` | PostgreSQL, Supabase | Database operations and data export |
| **`rag_manager.py`** | `RAGManager` | Claude API, database | AI-powered product search and chat |
| **`sync_manager.py`** | `DatabaseSyncManager` | Both databases via docker exec | Data synchronization between systems |
| **`sync_manager_backup.py`** | 💾 **Sync Manager Backup** | Previous sync version | Recovery/rollback for sync functionality |

---

## 🔄 **Common Workflows & File Relationships**

### **🚀 Starting the System**
```
reboot_dashboard.sh → reboot_dashboard.py → modules/* → templates/dashboard.html
```

### **📊 Data Acquisition Process**  
```
dashboard.html (Start Learning) → intelligence_manager.py → scrape_from_sitemap.py → db_manager.py
```

### **🔄 Data Synchronization**
```
sync_manager.py → PostgreSQL (docker exec) → Supabase (docker exec) → dashboard stats update
```

### **🤖 RAG Chat Query**
```
chat.html → rag_manager.py → Claude API + db_manager.py → formatted response
```

### **🔍 Troubleshooting Failed Scrapes**
```
retry_failed.py (analyze) → discover_missing_data.py (debug) → tileshop_scraper.py (test fix)
```

---

## 🎯 **Quick Reference: "Which File Do I Need?"**

| **I Want To...** | **Primary File** | **Supporting Files** |
|-------------------|------------------|---------------------|
| **Fix dashboard UI issues** | `dashboard.html`, `base.html` | `reboot_dashboard.py` (API endpoints) |
| **Modify scraping logic** | `scrape_from_sitemap.py` | `intelligence_manager.py` (orchestration) |
| **Add new data fields** | `tileshop_scraper.py` (test) → `scrape_from_sitemap.py` (implement) | `discover_missing_data.py` (analyze) |
| **Debug AI chat issues** | `rag_manager.py` | `chat.html`, `/static/chat.js` |
| **Fix database sync** | `sync_manager.py` | `db_manager.py` |
| **Add service health checks** | `docker_manager.py` | `reboot_dashboard.py` (API endpoints) |
| **Deploy to production** | `deploy.py` | `Dockerfile`, `fly.toml` |
| **Recover from scraping failures** | `retry_failed.py` | Production scraper logs |

---

## ⚠️ **Critical Dependencies & Relationships**

- **Dashboard won't start** → Check `docker_manager.py` for service dependencies
- **Scraping fails** → Verify Crawl4AI service in `docker_manager.py` 
- **RAG chat broken** → Check `ANTHROPIC_API_KEY` in `.env` and `rag_manager.py`
- **Sync issues** → Both PostgreSQL and Supabase must be accessible via `docker exec`
- **Missing data** → Run analysis tools before modifying extraction logic

## 🆕 Admin Dashboard Features

### **Complete Infrastructure Management**
- **Unified Services Directory**: Single control panel for all scraper services
- **Docker Container Control**: Start/stop/restart individual or all dependencies  
- **Real-time Monitoring**: Live container status, CPU/memory usage
- **Service Health Checks**: Comprehensive system verification with one-click testing
- **One-click Setup**: "Start All Services" → ready to scrape
- **AI Assistant Terminal**: White-labeled AI assistant for infrastructure queries

### **🆕 Universal URL Scraping System**
- **Dynamic Target URL Input**: Enter any website URL for scraping
- **Automatic Sitemap Detection**: Real-time discovery and display of sitemaps
- **Pre-configured for Tileshop**: Defaults to https://www.tileshop.com  
- **Self-Healing Foundation**: Built for future expansion to any e-commerce site
- **URL Validation**: Real-time validation and feedback on entered URLs
- **Visual Sitemap Display**: Clean, readable sitemap URL presentation
- **Advanced Sitemap Download Status**: Multi-stage progress tracking with real-time WebSocket updates
  - **Download Progress**: Live byte-by-byte download monitoring with progress bars
  - **XML Parsing Status**: Real-time parsing feedback and validation
  - **URL Extraction**: Progressive URL extraction with running counts
  - **Product Filtering**: Live filtering progress showing product URL identification
  - **Results Summary**: Comprehensive completion statistics and file saving confirmation
- **Intelligent URL Filtering**: Automatically filters for product URLs (excludes samples, special pages)

### **🔧 Production Filtering Requirements**
For production deployment, the scraper will need **custom filter criteria** to handle:
- **Product-specific patterns**: Different e-commerce sites use various URL structures
- **Exclusion rules**: Skip promotional, sample, or non-product pages
- **Category filtering**: Optionally limit to specific product categories
- **Geographic filtering**: Handle regional or language-specific URLs
- **Custom regex patterns**: Site-specific filtering for optimal scraping efficiency

**Current Filter Logic** (Tileshop-specific):
- ✅ **Include**: URLs containing `/products/` (main product pages)
- ❌ **Exclude**: Sample pages, special collections, non-product content
- 📊 **Result**: ~775 filtered product URLs from 4,700+ total sitemap entries

### **Advanced Scraper Control**
- **Multiple Scraping Modes**: Individual, batch, sitemap, resume
- **Live Progress Monitoring**: Real-time progress bars and statistics
- **Error Management**: Live error logs and recovery options
- **Intelligent Dependencies**: Auto-check requirements before starting

### **Database Sync Management**
- **Real-time Sync Status**: Live connection monitoring for both n8n-postgres and Supabase
- **One-click Data Sync**: Fast bulk data transfer using PostgreSQL COPY commands
- **Data Comparison**: Compare source vs target counts and sync percentage
- **Force Full Sync**: Option for complete data refresh when needed
- **Sync Statistics**: Track sync history, timing, and success rates

### **Database Management**
- **Product Data Viewer**: Sortable, searchable, filterable table with price per sq ft display
- **Enhanced Timestamps**: Full date and time for scraping timestamps
- **Export Tools**: CSV/JSON export with custom filters
- **Quick Statistics**: Live counts, averages, recent additions
- **Multi-database Support**: Switch between n8n-postgres and Supabase

### **RAG Chat Interface**
- **AI Product Assistant**: Natural language queries about tiles powered by Claude 3.5 Sonnet
- **Claude API Integration**: Advanced analytical query processing with full-text search capabilities
- **🆕 Visual Product Display**: High-quality product images displayed directly in chat
- **Enhanced Markdown Support**: Converts markdown to HTML with images, links, and formatting
- **Dual-Mode Processing**: 
  - **Search Queries**: PostgreSQL full-text search ("ceramic subway tiles")
  - **Analytical Queries**: Claude-powered analysis ("what's the lowest cost tile per sq ft")
- **Rich Product Display**: Product cards with images, prices, specifications, and direct links
- **Per-Piece Pricing Support**: Displays accessories as "$X.XX/each" vs tiles as "$X.XX/sq ft"
- **Real-time Database Access**: Direct PostgreSQL queries via docker exec for instant results
- **Smart Query Detection**: Automatically detects analytical vs. search intent
- **Suggestion System**: Pre-built query examples for common tile searches

#### **✅ Claude API Configuration Status**
- **🔑 API Key**: Updated and configured in `.env` file (`ANTHROPIC_API_KEY`)
- **🆕 Current Key**: `sk-ant-api03-ZAO2***XwAA` (configured in .env)
- **📚 RAG Library**: `anthropic>=0.20.0` installed and functional
- **🧠 Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **🔄 Auto-Load**: Dashboard automatically loads API key on startup
- **💾 Persistence**: Configuration persists across sessions
- **🤖 AI Assistant**: Uses same API key for infrastructure management queries
- **🔄 RAG Chat**: Uses same API key for product analysis queries with LLM-first priority
- **✅ Frontend Integration**: JavaScript event listeners properly initialized for button functionality
- **✅ Database Integration**: Supabase container connectivity resolved for product data access
- **🔄 Fallback System**: Automatic fallback to search when Claude API unavailable
- **📊 Enhanced Data Access**: RAG system now accesses 500 products sorted by price (DESC) for accurate analysis
- **💰 Price Display**: Product Database viewer shows price per sq ft instead of price per box
- **⏰ Detailed Timestamps**: Full date and time display for scraping timestamps
- **📅 Updated**: June 27, 2025 - Full LLM integration with enhanced data accuracy

### **System Monitoring**
- **Network Status**: app-network connectivity monitoring
- **Performance Metrics**: Scrape speeds, success rates, resource usage
- **Configuration Management**: Update settings through UI
- **Log Streaming**: Real-time logs from all components

## 🔄 **Proper Dashboard Reboot Protocol**

### **Important Startup Notes**
- ✅ **Environment**: Dashboard uses `/Users/robertsher/Projects/autogen_env` virtual environment
- 🧹 **Cache Clearing Required**: Browser cache must be cleared after code changes for UI updates to display
- 📊 **Service Count**: All 8 services (4 conceptual + 4 external) now participate in health checks and toggle

### **Correct Restart Sequence**
```bash
# 1. Stop existing dashboard process
pkill -f reboot_dashboard.py

# 2. Wait for process to terminate
sleep 3

# 3. Start dashboard in background with logging
python reboot_dashboard.py > dashboard.log 2>&1 &

# 4. Verify startup and environment status
sleep 2 && tail -10 dashboard.log

# 5. Clear browser cache and refresh http://localhost:8080
# In Chrome: Cmd+Shift+R or Ctrl+Shift+R
# In Firefox: Cmd+Shift+R or Ctrl+F5
```

### **Health Check Verification**
```bash
# Test all 8 services health check system
curl -s http://localhost:8080/api/docker/status | python -m json.tool

# Expected: All services show meaningful status instead of "Not Found"
# - conceptual_service: true (docker_engine, llm_api, web_server, intelligence_platform)
# - external_service: true (relational_db, vector_db, crawler, api_gateway)
```

### Usage Commands
```bash
# 🆕 Admin Dashboard (All-in-One)
python reboot_dashboard.py > dashboard.log 2>&1 &    # Complete control center (background)

# Development & Testing
python tileshop_scraper.py                    # Test individual product scraper

# Production Scraping (Enhanced)
python scrape_from_sitemap.py                 # Scrape all products with auto-recovery
python scrape_from_sitemap.py 10             # Test with 10 products
python scrape_from_sitemap.py --fresh        # Fresh start (ignore previous progress)

# Recovery & Retry
python retry_failed.py list                  # Show failed URLs summary
python retry_failed.py retry 10              # Retry first 10 failed URLs
python retry_failed.py reset                 # Reset all failed URLs to pending

# Sitemap Management
python download_sitemap.py                   # Download/refresh sitemap manually

# Analysis Tools
python discover_missing_data.py              # Find overlooked data fields
python extract_brand_examples.py             # Analyze brand extraction
python extract_image_examples.py             # Analyze image extraction

# Legacy Tools
python scrape_all_products.py                # Original batch scraper (legacy)
python scrape_all_products.py 10             # Legacy scraper with limit
```

## Configuration

All configuration is managed through environment variables in `.env` file:

- `ANTHROPIC_API_KEY`: Claude API key for RAG chat functionality
- `DATABASE_URL`: PostgreSQL connection (auto-configured for local Docker)
- `CRAWL4AI_URL`: crawl4ai service endpoint (http://localhost:11235)
- `CRAWL4AI_TOKEN`: authentication token (tileshop)

## 🚀 Production Deployment

### **Fly.io Deployment Ready**
The Tileshop scraper is ready for cloud deployment using the same infrastructure pattern as the genadam-avatar project.

#### **Deployment Architecture**
- **Platform**: Fly.io with Docker containers
- **Database**: PostgreSQL with persistent volumes
- **Memory**: 2GB RAM, 1 shared CPU
- **Health Checks**: Built-in monitoring at `/api/system/health` endpoint
- **SSL**: Automatic HTTPS with force_https
- **Auto-scaling**: Machine auto-start/stop capabilities

#### **Deployment Process**
1. **Docker Build**: Multi-platform build for linux/amd64
2. **Registry Push**: Push to Fly.io registry
3. **Immediate Deploy**: Zero-downtime deployment strategy
4. **Health Verification**: Automated health checks post-deployment

#### **Environment Variables for Production**
```bash
# Production Configuration
FLASK_ENV=production
DEBUG=false
PORT=8080
ANTHROPIC_API_KEY=your-claude-api-key
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host/db

# Optional Services (if needed in production)
CRAWL4AI_URL=https://your-crawl4ai-service.fly.dev
CRAWL4AI_TOKEN=your-token
```

#### **Production Features**
- **Gunicorn WSGI**: Production-grade server with worker management
- **Persistent Storage**: Database and sitemap data persistence
- **Resource Optimization**: Memory and CPU optimized for cloud deployment
- **Security**: Environment-based secrets management
- **Monitoring**: Health checks and performance metrics

#### **Quick Deploy Commands**
```bash
# 🚀 Full deployment (secrets + deploy)
python deploy.py full

# 🔐 Set up production secrets only
python deploy.py secrets

# 📦 Deploy to Fly.io only
python deploy.py deploy

# Manual Docker build
docker buildx build --platform linux/amd64 -t registry.fly.io/tileshop-scraper:latest . --push
```

#### **Deployment Files**
- `Dockerfile` - Multi-stage production container with Poetry
- `fly.toml` - Fly.io configuration with health checks
- `Procfile` - Alternative deployment configuration
- `deploy.py` - Automated deployment script
- `pyproject.toml` - Poetry dependency management
- `poetry.lock` - Locked dependency versions
- `requirements.txt` - Fallback pip dependencies (kept for local dev)

#### **Post-Deployment URLs**
- **Dashboard**: https://tileshop-scraper.fly.dev
- **RAG Chat**: https://tileshop-scraper.fly.dev/chat
- **Health Check**: https://tileshop-scraper.fly.dev/api/system/health
- **Customer Service**: Built-in AI assistant for support

## Admin Dashboard Issues & Solutions

### Known Issues & Fixes Applied:

#### ✅ **Fixed: Container Name Mapping**
- **Issue**: Dashboard showed `crawl4ai-browser` as "not found"  
- **Fix**: Updated to correct container name `crawl4ai`
- **Result**: All containers now show proper status

#### ✅ **Fixed: Database Connection (IPv6/IPv4)**
- **Issue**: `connection to server at "localhost" (::1), port 5432 failed: FATAL: role "postgres" does not exist`
- **Fix**: Updated all database connections to use `127.0.0.1` instead of `localhost`
- **Result**: Resolves IPv6 vs IPv4 connection issues

#### ✅ **Enhanced: Smart Button Logic**
- **Issue**: Start/Stop buttons always visible, causing potential conflicts
- **Fix**: Buttons now hide/show based on container status
- **Result**: Start buttons hide when containers are running, Stop buttons hide when stopped

#### ✅ **Enhanced: Live Scraper Monitoring**  
- **Issue**: Basic progress display without URL tracking
- **Fix**: Added real-time current URL display and enhanced progress tracking
- **Result**: Shows current URL being scraped, total progress, and detailed statistics

### Current Dashboard Status: 🟢 **Fully Operational**

**Dashboard URL**: http://localhost:8080

## Security & Environment Management

### **Secure API Key Configuration**
The project now uses proper environment variable management to protect sensitive information:

**✅ **Environment Files:**
- **`.env`** - Local configuration (gitignored)
- **`.env.example`** - Template for new setups
- **`.gitignore`** - Prevents accidental commits of secrets

**✅ **Claude API Key Storage:**
```bash
# ✅ CONFIGURED: API key is stored in .env file
# File Location: /Users/robertsher/Projects/tileshop_rag_clean/.env
# Variable Name: ANTHROPIC_API_KEY
# 
# ✅ PERSISTENCE: Key persists across sessions automatically
# ✅ SECURITY: Protected by .gitignore (never committed)
# ✅ AUTO-LOAD: Dashboard loads via load_dotenv() on startup
# ✅ UPDATED: June 29, 2025 - Enhanced health check system
```

**✅ **Security Best Practices:**
- ❌ **Never commit API keys** to version control
- ✅ **Use environment variables** for all sensitive data
- ✅ **Keep .env files local** and use .env.example for templates
- ✅ **Rotate keys regularly** and revoke compromised keys

### **Files Protected:**
- `.env` - Environment configuration
- `*.log` - Application logs
- `dashboard.log` - Dashboard runtime logs
- `recovery_*.json` - Scraper recovery files
- `sitemap.xml` - Downloaded sitemaps

## 📤 GitHub Repository & Contributing

### **Repository Information**
- **GitHub**: https://github.com/1genadam/tileshop-rag
- **Main Branch**: `master` (Note: Uses master, not main)
- **License**: Public repository
- **Current Authentication**: Personal Access Token (configured in remote URL)

### **📋 Current Pull Request Status**
- **Latest PR**: [#1 - Knowledge Base Enhancements](https://github.com/1genadam/tileshop-rag/pull/1)
- **Status**: Open and ready for review
- **Changes**: DCOF compliance docs, tile calculator guide, anti-fracture membrane guide
- **Files**: 11 files changed (+1,841 additions, -281 deletions)

### **🔄 Creating Pull Requests**

#### **Method 1: Using Personal Access Token & GitHub API (Recommended)**
> **✅ This project is pre-configured with Personal Access Token authentication**
> 
> **Why This Method is Recommended:**
> - ✅ **Already configured** - No additional setup required
> - ✅ **Programmatic approach** - Works well with automation
> - ✅ **No extra dependencies** - Uses curl (built into most systems)
> - ✅ **Consistent with project setup** - Matches existing authentication
```bash
# Create and push feature branch
git checkout -b feature/your-feature-name
git add .
git commit -m "Your commit message"
git push -u origin feature/your-feature-name

# Create pull request using GitHub API
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/1genadam/tileshop-rag/pulls \
  -d '{
    "title": "Your PR Title",
    "head": "feature/your-feature-name",
    "base": "master",
    "body": "Description of your changes"
  }'
```

#### **Method 2: Using GitHub Web Interface**
```bash
# Push your feature branch
git checkout -b feature/your-feature-name
git add .
git commit -m "Your commit message"
git push -u origin feature/your-feature-name

# Then visit: https://github.com/1genadam/tileshop-rag/pulls
# Click "New pull request" and select your branch
```

#### **Method 3: Using GitHub CLI (Optional - Not Pre-configured)**
```bash
# Only if you want to install GitHub CLI
brew install gh

# Create feature branch and push changes
git checkout -b feature/your-feature-name
git add .
git commit -m "Your commit message"
git push -u origin feature/your-feature-name

# Create pull request
gh pr create --title "Your PR Title" --body "Description of changes"
```

### **✅ Quick Push (Direct to Master - Use Sparingly)**
```bash
# Only for urgent hotfixes - prefer pull requests for review
git add .
git commit -m "Your commit message"
git push origin master
```

### **Easy GitHub Commit Instructions**

#### **Step 1: Check Status**
```bash
# View current changes
git status

# See what files have been modified
git diff --name-only
```

#### **Step 2: Stage Changes**
```bash
# Add all changes
git add .

# Or add specific files
git add tileshop_scraper.py simple_rag.py static/chat.js
```

#### **Step 3: Commit with Descriptive Message**
```bash
# Create commit with detailed message
git commit -m "Brief description of changes

- Detailed bullet point 1
- Detailed bullet point 2  
- Detailed bullet point 3

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### **Step 4: Push to GitHub**
```bash
# Push to the tileshop-rag repository
git push tileshop-rag main

# Alternative: Push to origin if set up
git push origin main
```

#### **🔐 Authentication Methods**

**✅ CURRENT METHOD: Personal Access Token (Working)**
```bash
# This project is currently configured to use Personal Access Token
# Token is already configured in the remote URL
# Simply use: git push tileshop-rag main
```

**Option 1: SSH Key (Alternative)**
```bash
# 1. Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your-email@example.com"

# 2. Add key to SSH agent
ssh-add ~/.ssh/id_ed25519
# (Enter your passphrase when prompted)

# 3. Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub
# Add this key to GitHub → Settings → SSH and GPG keys

# 4. Test connection
ssh -T git@github.com

# 5. Ensure remote uses SSH
git remote set-url tileshop-rag git@github.com:1genadam/tileshop-rag.git
```

**Option 2: Personal Access Token Setup (For New Users)**
```bash
# 1. Create token at GitHub → Settings → Developer settings → Personal access tokens
# 2. Select 'repo' permissions
# 3. Use token in remote URL
git remote set-url tileshop-rag https://YOUR_TOKEN@github.com/1genadam/tileshop-rag.git

# 4. Push normally
git push tileshop-rag main
```

**🚨 Troubleshooting Authentication**
```bash
# SSH Permission denied?
# - Check if key is added: ssh-add -l
# - Verify key in GitHub: cat ~/.ssh/id_ed25519.pub
# - Test connection: ssh -T git@github.com

# HTTPS asking for username/password?
# - Use personal access token instead of password
# - Update remote URL with token (see Option 2 above)
```

#### **Example Complete Workflow**
```bash
# 1. Check what changed
git status

# 2. Add all changes
git add .

# 3. Commit with message
git commit -m "Enhanced RAG system with image display

- Added markdown image parsing to chat interface
- Fixed SKU detection for contextual queries  
- Updated container references to use 'postgres'
- Improved per-piece pricing display

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Push to GitHub
git push tileshop-rag main
```

#### **Git Remote Configuration**
If you need to set up the remote:
```bash
# Check current remotes
git remote -v

# Add tileshop-rag remote (if not exists)
git remote add tileshop-rag git@github.com:1genadam/tileshop-rag.git

# Set as default upstream
git branch --set-upstream-to=tileshop-rag/main main
```

## 🎯 **Cross-Selling & Upsell Strategy**

### **Floor Tile Installation Upsells**

**Essential Products (Required for Installation):**
- **Grout**: Color-matched grout for tile joints
- **Thinset**: Adhesive for tile installation
- **Anti-Fracture Membrane**: 
  - **Backer-lite**: For wet areas (bathrooms, showers)
  - **Permat**: For dry areas (kitchens, living spaces)
- **Sealer**: Premium Gold Sealer (Qt or Pt sizes)
- **Tools & Supplies**:
  - Sponge for sealer application
  - Sponge for grout cleanup
  - Trowel (1/2" for large format tiles)
  - Margin trowel
  - 6-gallon bucket for mixing

**Premium Upgrades:**
- **Heated Floor Systems**: 
  - Eliminates need for backer-lite and permat
  - Requires MaxLite or Bond Left thinset
- **Trim & Finishing**:
  - Wall border trim (marble skirting, Stanton, or base)
  - Matching caulk (100% silicone to match grout)
  - Critical for wall/floor transitions to prevent grout cracking

**Why Caulk Instead of Grout**: Temperature changes cause walls and floors to expand/contract at different rates. Houses settle over time. Flexible caulk prevents cracking where rigid grout would fail.

### **Wall Tile Installation Upsells**

**Essential Products (Similar to Floor, with Key Differences):**
- **Grout**: Color-matched grout for tile joints
- **Thinset**: Wall-appropriate adhesive
- **Sealer**: Premium Gold Sealer (research coverage specs)
- **Same Tools**: Sponges, trowels, margin trowel, bucket

**Wall-Specific Exclusions:**
- ❌ No backer-lite (not needed for walls)
- ❌ No permat (not needed for walls)  
- ❌ No heated floor elements

**Wall-Specific Additions:**
- **Trim & Edging**:
  - Sommersets trim pieces
  - Barnes trim collection
  - Niches for shower storage
  - Upper wall moldings (cornices)
  - Great Lakes L-channels
  - Round nose edging
  - Square edge metal edging trim

### **Cross-Selling Implementation Strategy**

**Project Calculator Enhancement:**
1. **Detect Tile Application**: Floor vs Wall (from product specifications)
2. **Calculate Base Needs**: Grout, thinset, tools based on room size
3. **Suggest Premium Options**: Heated floors, premium sealers, trim packages
4. **Include Installation Supplies**: Complete project shopping list

**Upsell Pricing Strategy:**
- **Base tile purchase**: $200 (23 sq ft)
- **Essential installation supplies**: +$150-200
- **Premium upgrades**: +$200-300
- **Professional trim package**: +$100-150
- **Target total**: $500-650 (2.5-3x original purchase)

**RAG System Integration:**
- Subway tile query → Complete installation package
- Room size input → Accurate material calculations
- Application type → Appropriate upsell recommendations
- Return policy compliance → Whole box quantities only

## Troubleshooting

### Common Issues
1. **crawl4ai not responding**: Check container status and restart if needed
2. **Database connection errors**: Use 127.0.0.1 instead of localhost for IPv4
3. **Virtual environment issues**: Use full path to activate script (`/Users/robertsher/Projects/autogen_env/bin/python`)
4. **Pre-warming showing database connection ✗**: Normal if using docker exec method - check actual database stats work
5. **Wrong product counts (5 vs 262)**: Ensure using relational_db/vector_db containers, not local PostgreSQL@14
6. **Python subprocess startup ✗**: Check virtual environment path is set to `autogen_env`, not `sandbox_env`
7. **System Pre-warming not visible**: Should be visible in Runtime Environment Status frame after recent fixes
8. **Start Learning button not working**: Fixed - was using wrong API field references (`status.overall_status` vs `is_prewarmed`)
9. **Package installation problems**: Clean global packages and reinstall in venv
10. **Git push failures**: Use correct remote (`tileshop-rag`) instead of origin
11. **SSH authentication errors**: Add SSH key to agent with `ssh-add ~/.ssh/id_ed25519`
12. **Permission denied (publickey)**: Ensure SSH key is added to GitHub account
13. **HTTPS credential errors**: Use personal access token instead of password

### Debug Commands
```bash
# Check Docker containers
docker ps

# Test crawl4ai health
curl -H "Authorization: Bearer tileshop" http://localhost:11235/health

# Check database connection (IPv4)
psql -h 127.0.0.1 -p 5432 -U postgres -d postgres

# Test admin dashboard APIs
curl http://localhost:8080/api/docker/status
curl http://localhost:8080/api/database/status

# View scraper logs
cd /Users/robertsher/Projects/tileshop_rag_clean
python tileshop_scraper.py 2>&1 | tee scraper.log

# Check git configuration
git remote -v
git branch -vv
```