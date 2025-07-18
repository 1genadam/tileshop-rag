# Tileshop RAG System - Production Environment

**🚀 PRODUCTION ENVIRONMENT** - Stable, tested system for live operations

**✅ SYSTEM STATUS**: Phase 2 Diagnostic Framework Complete (July 6, 2025)

## 📚 Documentation Index

This directory contains all system documentation and guides:

| File | Purpose | Use Case |
|------|---------|----------|
| **README.md** | Main project overview and quick start | First-time setup and daily operations |
| **ARCHITECTURE.md** | Complete system architecture | Understanding system design and components |
| **TROUBLESHOOTING.md** | Phase 2 diagnostic troubleshooting | Resolving service issues and errors |
| **VISUAL_SIMILARITY_SYSTEM.md** | Google Lens-style tile recognition | Visual similarity matching implementation |

## 🤖 AI Agent & Chat Systems

### Enhanced AOS-NEPQ Hybrid Agent
- **NEPQ_Objection_Handling_Guide.md** - Comprehensive objection handling reference (52 objections converted to structured markdown)
- **7-Question Framework**: Name → Room/Dimensions → Problem Awareness → Style → Installation → Timeline → Consequences → Budget
- **Emotional Discovery**: NEPQ problem awareness and consequence questions for internal tension creation
- **Facts vs Meanings**: Advanced objection handling using NEPQ methodology

### 3-Mode Chat Applications
- **Customer Mode** (`customer_chat_app.py`) - Port 8081: `/customer-chat` - Enhanced AOS-NEPQ customer consultation with **Google Lens-style visual tile recognition**
- **Salesperson Mode** (`salesperson_chat_app.py`) - Port 8082: `/sales-chat` - SKU search, project organization, upsell management
- **Contractor Mode** (`contractor_chat_app.py`) - Port 8083: `/pro-chat` - Technical specs, advanced calculations, installation guides

### NEPQ Knowledge Base
- **knowledge_base/NEPQ/** - Complete NEPQ methodology documents and objection frameworks
- **Structured for AI Reference** - All 52 objection responses converted from RTF to searchable markdown

## 🚀 Production Quick Start

```bash
# Navigate to production environment
cd /Users/robertsher/Projects/tileshop_rag_prod

# Start the production system
python reboot_dashboard.py

# Access production dashboard with all 17 services
http://localhost:8080

# Check all services health
Click "Health Check All (17 Services)" button
```

### 🤖 Start Enhanced AI Chat Systems

```bash
# Start Customer Chat (Enhanced AOS-NEPQ)
python customer_chat_app.py
# Access: http://localhost:8081/customer-chat

# Start Salesperson Tools
python salesperson_chat_app.py  
# Access: http://localhost:8082/sales-chat

# Start Contractor Tools
python contractor_chat_app.py
# Access: http://localhost:8083/pro-chat
```

## 🎯 Production System Overview

The Tileshop RAG Production System is a comprehensive intelligence platform featuring:

- **17 monitored services** across 3 categories (Microservices, Runtime, Pre-warming)
- **Enhanced AOS-NEPQ Hybrid AI Agent** with 7-question framework and emotional engagement
- **Google Lens-style Visual Tile Recognition** with multi-strategy similarity matching
- **3-Mode Chat System**: Customer (8081), Salesperson (8082), Contractor (8083)
- **NEPQ Objection Handling** with structured markdown reference guide
- **Real-time web scraping** with Crawl4AI integration
- **RAG (Retrieval-Augmented Generation)** with Claude API
- **Dual database architecture** (Relational + Vector)
- **Comprehensive monitoring** and management dashboard

## 🏗️ System Architecture

### Service Categories (17 Total)

**🔧 MICROSERVICES (6 services):**
- Docker Engine, Relational DB, Vector DB, Crawler, API Gateway, Web Server, LLM API

**⚙️ RUNTIME ENVIRONMENT (4 services):**
- Python Environment, System Dependencies, Docker Daemon, Infrastructure

**🔄 PRE-WARMING SYSTEMS (7 services):**
- Python Subprocess, Database Pre-warming (x2), Sitemap Validation, Crawler Pre-warming

### Core Components
- **Flask Dashboard** (Port 8080) - Central management interface
- **PostgreSQL** (Port 5432) - Primary relational database
- **Vector Database** (Port 5433) - PostgreSQL + pgvector for embeddings
- **Crawl4AI** (Port 11235) - Browser-based web scraping
- **Kong Gateway** (Ports 8000, 8001, 8443) - API management
- **Claude API** - AI-powered responses and analysis

## 🔧 Core Operations

### Production Dashboard Management
```bash
# Navigate to production directory
cd /Users/robertsher/Projects/tileshop_rag_prod

# Start production dashboard with all diagnostic services
python reboot_dashboard.py

# Stop production dashboard
pkill -f "python reboot_dashboard.py"

# Check production dashboard status
ps aux | grep reboot_dashboard.py
```

### Service Health Monitoring
```bash
# API endpoints for service management
curl -s "http://localhost:8080/api/services/list"
curl -s "http://localhost:8080/api/service/docker_engine/health"
curl -s "http://localhost:8080/api/service/relational_db/logs"
curl -s "http://localhost:8080/api/service/vector_db/debug"
```

### Database Operations
```bash
# Test database connections
python -c "
import psycopg2
# Test relational database
conn = psycopg2.connect(host='localhost', port=5432, database='postgres', user='robertsher')
print('✅ Relational DB connected')
conn.close()

# Test vector database  
conn = psycopg2.connect(host='localhost', port=5433, database='postgres', user='postgres', password='supabase123')
print('✅ Vector DB connected')
conn.close()
"
```

### Vector Database Setup
```bash
# Generate embeddings for all products (via dashboard)
# Click "🧠 Generate Embeddings" button in Database Sync section
# Features comprehensive progress tracking with:
# - Real-time percentage completion
# - Elapsed time and batch information  
# - Live status updates every 2 seconds
# - Cancel/resume functionality

# OR via API:
curl -X POST "http://localhost:8080/api/rag/generate-embeddings"

# Monitor progress:
curl -s "http://localhost:8080/api/rag/embeddings-progress"

# Check embedding count
docker exec vector_db psql -U postgres -d postgres -c "SELECT COUNT(*) FROM product_embeddings;"
```

### Container Management
```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Start core services
docker start relational_db vector_db crawler api_gateway

# Check logs
docker logs --tail 20 relational_db
docker logs --tail 20 vector_db
```

## 📊 Diagnostic Framework

### Service Status Types
- **Microservices**: `healthy` (green) / `issues` (red)
- **Runtime**: `healthy` (green) / `issues` (red)  
- **Pre-warming**: `ready` (green) / `not_ready` (yellow) / `error` (red)

### Health Check Interface
Each service provides:
- **Health Check** 🔍 - Current operational status
- **Logs** 📋 - Service-specific logs and information
- **Debug** 🔧 - Advanced troubleshooting data

### API Endpoints
- `GET /api/services/list` - List all 17 services
- `GET /api/service/{name}/health` - Service health status
- `GET /api/service/{name}/logs` - Service logs
- `GET /api/service/{name}/debug` - Debug information

## 🔧 Configuration

### Environment Variables (.env)
```env
# Claude API Configuration
ANTHROPIC_API_KEY=sk-ant-api03-...

# Relational Database
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=robertsher
POSTGRES_DB=postgres

# Vector Database (Supabase)
SUPABASE_HOST=127.0.0.1
SUPABASE_PORT=5433
SUPABASE_USER=postgres
SUPABASE_PASSWORD=supabase123
SUPABASE_DB=postgres

# Crawler Service
CRAWL4AI_URL=http://localhost:11235
CRAWL4AI_TOKEN=tileshop
```

### Docker Configuration
```bash
# Start Crawl4AI browser service
docker run -d \
  -p 11235:11235 \
  --name crawler \
  --shm-size=1g \
  -e CRAWL4AI_API_TOKEN=tileshop \
  unclecode/crawl4ai:browser
```

## 🚨 Common Issues & Quick Fixes

### Services Stuck at "Checking..."
```bash
# Restart dashboard
pkill -f "python reboot_dashboard.py"
python reboot_dashboard.py
```

### Database Connection Issues
```bash
# Check container status
docker ps | grep -E "(relational_db|vector_db)"

# Restart databases
docker restart relational_db vector_db
```

### Vector Database Shows 0 Embeddings
```bash
# Generate embeddings from product data
# Click "🧠 Generate Embeddings" button in Database Sync card
# Features comprehensive progress tracking:
# - Animated progress bar with percentage
# - Detailed status cards (Status, Progress, Elapsed, Batch)
# - Real-time updates every 2 seconds
# - Cancel/close controls with proper state management

# Monitor embedding generation progress:
curl -s "http://localhost:8080/api/rag/embeddings-progress" | jq '.progress'

# Check final embedding count:
curl -s "http://localhost:8080/api/sync/status" | jq '.status.connections.target'
```

### Container Not Found Errors
```bash
# Check actual container names
docker ps --format "table {{.Names}}\t{{.Status}}"

# Ensure names match expectations:
# - crawler (not crawl4ai-browser)
# - api_gateway (not supabase-kong)
```

### JavaScript Errors in Browser
- Check browser console (F12)
- Look for missing function errors
- Verify DOM element IDs match service names

## 📈 Performance Features

### Fast-Boot Mode
- Dashboard starts quickly with monitoring disabled initially
- Services load in parallel for optimal performance
- Resource usage optimized for development

### Real-Time Updates
- WebSocket-based status updates
- Automatic service health monitoring
- Live progress tracking for operations

### Scalable Architecture
- Container-based microservices
- Load balancer ready
- Database replication support

## 🛠️ Development Workflow

### Adding New Services
1. Create diagnostic class in `modules/service_diagnostic.py`
2. Register service in `reboot_dashboard.py`
3. Add UI elements in `templates/dashboard.html`
4. Test health check API endpoints

### Updating Service Logic
1. Modify appropriate diagnostic class
2. Update status mapping if needed
3. Test via dashboard health checks
4. Verify logs and debug information

### Database Changes
1. Update schema in both databases
2. Modify `modules/db_manager.py` 
3. Test connection and queries
4. Update pre-warming services

## 📋 Additional Resources

### Detailed Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture with diagrams, data flows, and technical specifications
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Comprehensive troubleshooting guide for Phase 2 diagnostic framework
- **[VISUAL_SIMILARITY_SYSTEM.md](VISUAL_SIMILARITY_SYSTEM.md)** - Google Lens-style visual tile recognition implementation

### Key Modules
- `modules/service_diagnostic.py` - Diagnostic framework classes
- `modules/simple_tile_agent.py` - Enhanced AOS-NEPQ hybrid AI agent with 7-question framework
- `modules/rag_manager.py` - RAG system and Claude API integration
- `modules/db_manager.py` - Database connection and query management
- `modules/intelligence_manager.py` - Web scraping and content processing
- `knowledge_base/NEPQ_Objection_Handling_Guide.md` - Comprehensive objection handling reference
- `reboot_dashboard.py` - Main dashboard application
- `templates/dashboard.html` - Web interface
- Chat Applications: `customer_chat_app.py`, `salesperson_chat_app.py`, `contractor_chat_app.py`

### Support and Maintenance
- All services monitored through unified dashboard
- Automated health checks every 30 seconds
- Error logging with detailed diagnostics
- Recovery procedures documented in troubleshooting guide

---

**🎯 Quick Links:**
- Dashboard: http://localhost:8080
- Health Check: Click "Health Check All (17 Services)"
- Service Logs: Individual service log buttons
- Debug Info: Individual service debug buttons

**📖 Full Documentation:**
- System Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Visual Recognition: [VISUAL_SIMILARITY_SYSTEM.md](VISUAL_SIMILARITY_SYSTEM.md)

---

## 🏗️ Environment Structure

**Production Environment** (`tileshop_rag_prod`):
- Stable, tested system for live operations
- Contains all parsing fixes and enhancements
- Deployed to Fly.io for production use
- Database schema includes all field fixes

**Development Environment** (`tileshop_rag_dev`):
- Development and testing environment
- Use for new feature development
- Safe environment for experimentation
- Isolated from production operations

**Backup** (`tileshop_rag_backup`):
- Complete backup of the original system
- Preserve original state before environment split
- Recovery point if needed

---

*Last Updated: July 11, 2025*  
*Environment: Production*  
*Status: All 17 services operational*  
*Latest: Google Lens-style Visual Tile Recognition System - Complete*  
*Previous: Edge Type, Box Quantity, Product Category, Pricing Logic - All Complete*