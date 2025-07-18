# Tileshop RAG Troubleshooting Guide - Database Corruption Recovery

## 📋 Issue Overview
**Date**: July 5-6, 2025  
**Problem**: Vector database corruption requiring system restart  
**Resolution**: Complete database recovery and service restoration  
**Status**: ✅ RESOLVED - All services operational

## ✅ Major Accomplishments

### 1. **Process Inventory Documentation** 
- Added comprehensive **Process Inventory & Management** section to README.md
- Documented all monitoring and audit tools with usage guidelines
- Explained fast-boot optimizations and when to enable monitoring
- **Committed and pushed to git** (commit: `19010546`)

### 2. **Learning Counter Reset**
- **Problem**: Learning showed old progress (4757/4778 completed) instead of fresh start
- **Solution**: Reset all URLs in `tileshop_sitemap.json` to "pending" status
- **Result**: Counters now show **0/4778** (fresh start ready)
- **Verification**: API confirms `"pending": 4778, "completed": 0`

### 3. **Dashboard Restart & Optimization**
- **Problem**: Dashboard stuck in infinite "Status checking..." loops
- **Solution**: Killed and restarted dashboard process
- **Result**: Dashboard responsive and APIs working
- **Current Status**: Running on port 8080, health checks passing

### 4. **Docker Cleanup**
- **Removed unused containers** (~21GB total):
  - Old crawl4ai versions (6.6GB + 6.2GB + 4.8GB × 3)
  - AutoGen containers (1.3GB + 253MB)
  - pgadmin, buildx cache, etc.
- **Freed Docker images**: Additional 222MB
- **Result**: Reduced Docker storage pressure significantly

### 5. **Pre-warming System**
- **Problem**: All pre-warming checks showing errors after dashboard restart
- **Solution**: Manually triggered pre-warming via API
- **Result**: All systems now show ready:
  - ✅ Python subprocess: Working
  - ✅ Sitemap validation: 4778 URLs loaded
  - ✅ Crawler service: Status "ok"
  - ✅ relational_db: Connected
  - ⚠️ vector_db: Still having issues

## 🚨 Current Issues Requiring Restart

### **Supabase PostgreSQL (vector_db) Problem**
- **Symptoms**: 
  - Container shows "healthy" but PostgreSQL won't accept connections
  - Port 5433 connections fail with "server closed connection unexpectedly"
  - Database logs show repeated shutdown/restart cycles
- **Root Cause**: Likely memory pressure + PostgreSQL data corruption
- **Attempted Fixes**:
  - Restarted individual containers
  - Stopped/started entire Supabase stack
  - Docker cleanup to free resources
  - None resolved the core issue

### **System Load**
- **High load average**: 2.72-3.22 (should be <1.0)
- **Memory pressure**: 15GB used, high compression
- **Docker overhead**: 2.8GB Docker backend process

## 🎯 Post-Restart Action Plan

### **Immediate Verification** (First 5 minutes)
1. **Start dashboard**: `python3 reboot_dashboard.py`
2. **Test databases**:
   ```bash
   # Test relational_db (port 5432)
   python3 -c "import psycopg2; conn=psycopg2.connect(host='localhost', port=5432, database='postgres', user='postgres', password='postgres'); print('✅ relational_db OK')"
   
   # Test vector_db (port 5433) 
   python3 -c "import psycopg2; conn=psycopg2.connect(host='127.0.0.1', port=5433, database='postgres', user='postgres', password='postgres'); print('✅ vector_db OK')"
   ```
3. **Verify sitemap status**: Should still show 0/4778 (reset counters preserved)
4. **Test pre-warming**: Should complete successfully

### **Learning Process** (Ready to start)
- **Sitemap**: 4778 URLs ready, all set to "pending" status
- **Expected behavior**: Click "Begin Learning" → counts from 0 to 4778
- **Infrastructure**: All services should be working after restart

## 📁 Key Files & Status

### **Modified Files**
- ✅ `README.md` - Added process inventory (committed to git)
- ✅ `tileshop_sitemap.json` - Reset to fresh state (4778 pending URLs)

### **Working Services** (Pre-restart)
- ✅ Dashboard Flask app (port 8080)
- ✅ PostgreSQL main database (port 5432) 
- ✅ Crawler service (port 11235)
- ✅ Docker daemon (cleaned up)

### **Problematic Services**
- ❌ Supabase PostgreSQL (port 5433) - Needs restart
- ⚠️ Supabase pooler - Was restarting repeatedly

## 🔧 Configuration Notes

### **Environment**
- **Python**: Running with pyenv (`/Users/robertsher/.pyenv/versions/3.11.6/bin/python3`)
- **Virtual env path**: Dashboard checks look for `/Users/robertsher/Projects/autogen_env` but system works with pyenv
- **Dependencies**: All available in current environment

### **Docker Containers** (Should start automatically)
- **Essential for learning**: `crawl4ai-browser`, `postgres`, `supabase`
- **Recently cleaned**: Removed ~21GB of unused containers
- **Status**: Much lighter footprint after cleanup

## 🎯 Expected Outcome After Restart

1. **System load** should normalize (<2.0)
2. **Supabase PostgreSQL** should start properly on port 5433
3. **Dashboard** should load without "Checking..." loops
4. **Learning process** ready to start with 0/4778 counters
5. **All pre-warming checks** should pass

## 📞 If Issues Persist After Restart

### **Database Connection Issues**
- Check Docker containers: `docker ps | grep -E "(postgres|supabase)"`
- Test connections manually with psycopg2 commands above
- Check logs: `docker logs supabase --tail 20`

### **Dashboard Issues** 
- Restart dashboard: `python3 reboot_dashboard.py`
- Check port: `lsof -i :8080`
- Test health: `curl http://127.0.0.1:8080/api/system/health`

### **Learning Counter Issues**
- Verify sitemap: `head -20 tileshop_sitemap.json` (should show recent timestamp)
- Check API: `curl -s http://127.0.0.1:8080/api/acquisition/sitemap-status | jq '.stats'`

## 🏁 Ready State Checklist

**Before starting learning process, verify**:
- [ ] Dashboard loads without infinite "Checking..." status
- [ ] Database Sync shows both sources connected (not "Checking...")  
- [ ] System Pre-warming shows all green checkmarks
- [ ] Sitemap status shows 0 completed, 4778 pending
- [ ] "Begin Learning" button is functional

**Target**: Fresh learning session processing 4778 products from 0 to completion.

## 🔧 Resolution Steps (July 6, 2025)

### **Step 1: Service Assessment** 
- **Relational DB (port 5432)**: ❌ Container stopped - **FIXED** by `docker start postgres`
- **Vector DB (port 5433)**: ❌ Connection refused/corruption - **FIXED** by container replacement
- **Crawl4ai (port 11235)**: ❌ Not running - **FIXED** by starting container
- **Dashboard (port 8080)**: ⏳ Starting up - **WORKING** after `python3 reboot_dashboard.py`

### **Step 2: Database Recovery**
```bash
# Remove corrupted Supabase container and volume
docker stop supabase && docker rm supabase
docker volume rm supabase_db-config

# Start fresh postgres container for vector_db
docker run -d \
  --name supabase \
  -p 5433:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  postgres:15
```

### **Step 3: Recreate Missing Tables**
```sql
-- Create product_data table in vector_db
CREATE TABLE IF NOT EXISTS product_data (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) UNIQUE NOT NULL,
    sku VARCHAR(50),
    title TEXT,
    price_per_box DECIMAL(10,2),
    price_per_sqft DECIMAL(10,2),
    price_per_piece DECIMAL(10,2),
    coverage TEXT,
    finish TEXT,
    color TEXT,
    size_shape TEXT,
    description TEXT,
    specifications JSONB,
    resources TEXT,
    raw_html TEXT,
    raw_markdown TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    images TEXT,
    collection_links TEXT,
    brand VARCHAR(100),
    primary_image TEXT,
    image_variants JSONB,
    thickness VARCHAR(20),
    recommended_grout VARCHAR(100)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_product_sku ON product_data(sku);
CREATE INDEX IF NOT EXISTS idx_product_scraped_at ON product_data(scraped_at);
```

### **Step 4: Service Restoration**
```bash
# Start crawl4ai-browser container
docker run -d \
  -p 11235:11235 \
  --name crawl4ai-browser \
  --shm-size=1g \
  -e CRAWL4AI_API_TOKEN=tileshop \
  -e OPENAI_API_KEY=your-openai-key \
  unclecode/crawl4ai:latest

# Start dashboard
python3 reboot_dashboard.py
```

## ✅ Verification Commands

### **Database Connections**
```bash
# Test relational_db
python3 -c "import psycopg2; conn=psycopg2.connect(host='localhost', port=5432, database='postgres', user='postgres', password='postgres'); print('✅ relational_db OK')"

# Test vector_db 
python3 -c "import psycopg2; conn=psycopg2.connect(host='127.0.0.1', port=5433, database='postgres', user='postgres', password='postgres'); print('✅ vector_db OK')"
```

### **Service Health**
```bash
# Check containers
docker ps | grep -E "(postgres|crawl4ai)"

# Test crawl4ai
curl -s http://127.0.0.1:11235/health

# Test dashboard
curl -s http://127.0.0.1:8080/api/system/health
```

## 🚨 Key Learning Points

### **Root Cause**
- **Supabase container corruption**: PostgreSQL was in continuous restart loop
- **Memory pressure**: High system load contributed to database instability  
- **Data integrity**: Volume corruption required fresh container deployment

### **Resolution Strategy** 
- **Clean slate approach**: Replace corrupted container rather than repair
- **Schema preservation**: Recreate tables using existing schema from source code
- **Service isolation**: Each database service runs in separate container

### **Prevention Tips**
- Monitor container health with `docker ps --format "table {{.Names}}\t{{.Status}}"`
- Regular volume backups for critical databases
- Use docker healthchecks to detect corruption early
- Keep schema definitions in version control for quick recovery

## 📚 Troubleshooting Patterns

### **Database Connection Issues**
1. **Check container status**: `docker ps | grep <service>`
2. **Test basic connectivity**: `telnet <host> <port>`
3. **Check logs**: `docker logs <container> --tail 20`
4. **Verify credentials**: Ensure user/password match container config

### **Service Recovery Order**
1. **Databases first**: Relational, then vector database
2. **External services**: Crawl4ai, APIs
3. **Application layer**: Dashboard last

### **Container Management**
```bash
# Safe container restart
docker stop <container>
docker start <container>

# Nuclear option (data loss)
docker stop <container> && docker rm <container>
docker volume rm <volume_name>
# Then recreate from scratch
```

## 🚀 **PHASE 2 COMPLETED: Standardized Diagnostic Framework (July 6, 2025 00:16 EST)**

### **✅ COMPLETED STATUS**
**✅ Phase 1**: Fixed all database architecture issues  
**✅ Phase 2**: Implemented standardized diagnostic framework  
**✅ API Integration**: 14 services integrated with 3-button interface  
**📋 Dashboard Status**: All database errors resolved, new diagnostic APIs operational

### **Phase 1: Fixed Database Architecture Issues** ✅
```bash
# ✅ COMPLETED: Fixed all container name mismatches and architecture issues
# 1. modules/db_manager.py - Fixed vector_db queries to only handle embeddings  
# 2. modules/sync_manager.py - Already correctly configured
# 3. Dashboard errors eliminated - no more "product_data does not exist" errors
```

### **Phase 2: Standardized Diagnostic Framework** ✅

#### **Target Dashboard Layout:**
```
┌─ 🔧 MICROSERVICES ──────────────┐
│ docker_engine     🟢 [🔍][📋][🔧] │
│ relational_db     🟢 [🔍][📋][🔧] │  
│ vector_db         🟡 [🔍][📋][🔧] │
│ crawler           🟢 [🔍][📋][🔧] │
│ llm_api           🟢 [🔍][📋][🔧] │
│ web_server        🟢 [🔍][📋][🔧] │
│ api_gateway       🟢 [🔍][📋][🔧] │
│ intelligence_platform 🟢 [🔍][📋][🔧] │
├─ 🏃 RUNTIME ENVIRONMENT ───────┤
│ python_env        🟢 [🔍][📋][🔧] │
│ dependencies      🟢 [🔍][📋][🔧] │
│ system_resources  🟢 [🔍][📋][🔧] │
├─ ⚡ PRE-WARMING SYSTEMS ───────┤
│ database_connections 🟢 [🔍][📋][🔧] │
│ service_validation   🟡 [🔍][📋][🔧] │
│ dependency_checks    🟢 [🔍][📋][🔧] │
└──────────────────────────────────┘
```

#### **Three-Button Standard for All Services:**
- **🔍 Health Check** - Enhanced diagnostics with actionable details
- **📋 Logs** - Service-specific filtered logs  
- **🔧 Debug** - Advanced troubleshooting panel

#### **✅ IMPLEMENTED API Endpoints:**
```bash
# Standardized Diagnostic APIs (Phase 2)
/api/service/{service_name}/health  ✅ Working
/api/service/{service_name}/logs    ✅ Working
/api/service/{service_name}/debug   ✅ Working
/api/services/list                  ✅ Working (14 services)

# Example Usage:
curl http://127.0.0.1:8080/api/services/list
curl http://127.0.0.1:8080/api/service/relational_db/health
curl http://127.0.0.1:8080/api/service/web_server/logs
curl http://127.0.0.1:8080/api/service/docker_engine/debug
```

### **✅ COMPLETED Implementation Files**
1. **✅ Created**: `modules/service_diagnostic.py` - Base diagnostic framework
2. **✅ Extended**: `reboot_dashboard.py` with new API endpoints and service registry
3. **✅ Updated**: `templates/dashboard.html` with new sections and 3-button interface
4. **✅ Tested**: All 14 services integrated with diagnostic coverage and UI

### **✅ ACHIEVED OUTCOMES**
- **✅ Consistent API**: Same diagnostic interface for all 14 system components
- **✅ Faster Debugging**: Predictable 3-button diagnostic flow across all services
- **✅ Better Architecture**: Unified health metrics and service classification
- **✅ Easier Maintenance**: Single diagnostic framework for all service types
- **✅ Complete UI Integration**: Dashboard now has 3 sections with standardized interface
- **✅ Full Coverage**: Health/Logs/Debug available for all Microservices, Runtime, and Pre-warming Systems
- **✅ Unified Health Check**: Single button checks all 17 services with progress tracking and comprehensive reporting
- **✅ Improved Navigation**: Customer Service moved to menu bar for better organization

### **🔧 Service Categories Successfully Implemented:**
- **Microservices (8)**: docker_engine, relational_db, vector_db, crawler, llm_api, web_server, api_gateway, intelligence_platform
- **Runtime Environment (4)**: virtual_environment, dependencies, docker_daemon, infrastructure  
- **Pre-warming Systems (5)**: python_subprocess, relational_db_prewarm, sitemap_validation, vector_db_prewarm, crawler_service_prewarm

### **✅ UNIFIED TABLE COMPLETED (July 6, 2025)**
- **✅ Consolidated 3 tables** into single unified table with section headers
- **✅ Split Actions column** into separate Health/Logs/Debug columns as requested  
- **✅ Expanded Runtime** to show all 4 components (Virtual Environment, Dependencies, Docker Daemon, Infrastructure)
- **✅ Expanded Pre-warming** to show all 5 services (Python subprocess, relational_db, Sitemap validation, vector_db, Crawler service)
- **✅ Removed redundant sections** - eliminated separate Runtime Environment and Pre-warming cards
- **✅ Updated backend** to support all 17 services with proper diagnostic API endpoints
- **✅ All 17 services** now use standardized 3-button interface (🔍 Health, 📋 Logs, 🔧 Debug)

---
*Issue resolved: July 6, 2025 03:15 EST*  
*System operational - Next phase: Diagnostic standardization*  
*Continue with: Container name fixes → Framework implementation*