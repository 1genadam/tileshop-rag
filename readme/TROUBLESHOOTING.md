# Tileshop RAG System - Troubleshooting Guide

## Overview
This guide provides comprehensive troubleshooting steps for the Tileshop RAG system, including the standardized diagnostic framework implemented in Phase 2.

## Quick Status Check

### Dashboard Health Check
1. **Access Dashboard**: Navigate to `http://localhost:8080`
2. **Check All Services**: Click "Health Check All (17 Services)" button
3. **View Status**: All services should show "Ready" status with green indicators

### Service Categories
- **Microservices (0-5)**: Container-based services
- **Runtime Environment (6-9)**: System dependencies 
- **Pre-warming Systems (10-16)**: Initialization services

## Common Issues and Solutions

### 1. Services Stuck at "Checking..." Status

**Symptoms:**
- Services show "Checking..." indefinitely
- Status never updates to "Ready" or "Issues"

**Root Cause:**
- JavaScript function conflicts
- Missing API endpoints
- DOM element ID mismatches

**Solution:**
```bash
# Check if dashboard is running
ps aux | grep reboot_dashboard.py

# Restart dashboard
pkill -f "python reboot_dashboard.py"
python reboot_dashboard.py
```

**Prevention:**
- Avoid removing `updateAllServiceStatus()` function
- Don't modify DOM element IDs without updating JavaScript
- Keep service type routing logic intact

### 2. Database Connection Issues

**Symptoms:**
- Services 1 (relational_db) and 2 (vector_db) show "Issues"
- Services 13 (relational_db_prewarm) and 15 (vector_db_prewarm) show "Not Ready"

**Diagnosis:**
```bash
# Check database containers
docker ps | grep -E "(relational_db|vector_db)"

# Test connections
docker exec relational_db pg_isready
docker exec vector_db pg_isready
```

**Solution:**
```bash
# Start database containers
docker start relational_db vector_db

# Check logs
docker logs relational_db
docker logs vector_db
```

### 3. Container Name Mismatches

**Symptoms:**
- Microservices show "container_not_found" status
- Health checks fail for running containers

**Root Cause:**
- Dashboard expects different container names than actual running containers

**Solution:**
```bash
# Check actual container names
docker ps --format "table {{.Names}}\t{{.Status}}"

# Update diagnostic services in reboot_dashboard.py
# Ensure container names match actual Docker containers
```

**Common Mismatches:**
- `crawl4ai-browser` → `crawler`
- `supabase-kong` → `api_gateway`

### 4. JavaScript Errors

**Symptoms:**
- Browser console shows "TypeError: Cannot read properties of null"
- Status updates fail
- Button clicks don't work

**Common Errors:**
```javascript
// Error: updatePrewarmStatus function missing
TypeError: updatePrewarmStatus is not a function

// Error: DOM element not found
TypeError: Cannot read properties of null (reading 'style')
```

**Solution:**
1. **Check Browser Console** (F12 → Console)
2. **Verify Function Existence:**
   ```javascript
   // These functions must exist:
   - updateServiceStatus()
   - updateRuntimeStatus() 
   - updatePrewarmStatus()
   - updateAllServiceStatus()
   ```

3. **Fix Missing Functions:**
   ```javascript
   function updatePrewarmStatus(systemName, status, message) {
       const dot = document.getElementById(`${systemName}-dot`);
       const text = document.getElementById(`${systemName}-text`);
       const info = document.getElementById(`${systemName}-info`);
       
       if (dot) {
           dot.className = `status-dot ${status === 'ready' ? 'green' : 'yellow'}`;
       }
       if (text) {
           text.textContent = status === 'ready' ? 'Ready' : 'Not Ready';
       }
       if (info) {
           info.textContent = message;
       }
   }
   ```

### 5. API Endpoint Failures

**Symptoms:**
- Services fail to load status
- Health/Logs/Debug buttons don't work
- Network errors in browser console

**Diagnosis:**
```bash
# Test API endpoints
curl -s "http://localhost:8080/api/services/list" | jq '.'
curl -s "http://localhost:8080/api/service/docker_engine/health" | jq '.'
```

**Solution:**
```bash
# Check if diagnostic services are initialized
grep -n "initialize_diagnostic_services" reboot_dashboard.py

# Verify API routes are registered
grep -n "@app.route.*api/service" reboot_dashboard.py
```

### 6. Claude API Configuration Issues

**Symptoms:**
- Service 5 (llm_api) shows "Issues"
- "Claude API not configured" message

**Solution:**
```bash
# Check .env file
cat .env | grep ANTHROPIC_API_KEY

# Verify API key format
# Should start with: sk-ant-api03-...
```

### 7. Pre-warming Services Not Ready

**Symptoms:**
- Services 12-16 show "Not Ready" status
- Database pre-warming fails

**Root Cause:**
- PrewarmServiceDiagnostic logic expects wrong result format
- Database connection results not properly parsed

**Solution:**
Check `modules/service_diagnostic.py` PrewarmServiceDiagnostic.health_check():
```python
# Ensure this logic is present:
elif any(key in result for key in ['relational_db', 'vector_db']):
    db_results = [v for k, v in result.items() if k in ['relational_db', 'vector_db']]
    is_ready = all(db.get('connected', False) for db in db_results if isinstance(db, dict))
```

### 8. Vector Database Shows 0 Embeddings

**Symptoms:**
- Database Sync shows "Target (Vector DB): ✓ Connected (0 embeddings, 0 docs)"
- Vector database is empty despite having product data

**Root Cause:**
- Embeddings have not been generated from product data
- Vector database stores embeddings, not duplicate product data

**Solution:**
```bash
# Generate embeddings via dashboard
# Click "🧠 Generate Embeddings" button in Database Sync section

# OR via API
curl -X POST "http://localhost:8080/api/rag/generate-embeddings"

# Verify embedding generation
docker exec vector_db psql -U postgres -d postgres -c "SELECT COUNT(*) FROM product_embeddings;"
```

**Important Notes:**
- Do NOT use "Sync Data" button (violates architecture)
- Vector DB should contain embeddings, not product data
- Process takes 10-15 minutes for 4,785 products

### 9. RAG Chat Returns "No Products Found" or Wrong Results

**Symptoms:**
- Chat queries like "list 3 blue tile" return no results
- Chat finds wrong products (e.g., tools instead of tiles)
- Queries like "slip-resistant tile" or "LFT thinset" fail
- Error: "I couldn't find any products matching your query"

**Root Cause:**
- Search term extraction not optimized for tile-specific queries
- SQL queries prioritizing wrong results (by SKU instead of relevance)
- OpenAI API key missing (system falls back to text search)
- Query routing sending product searches to analytical engine

**Solution 1 - Search Term Enhancement:**

Check `simple_rag.py` `_extract_search_terms()` function:
```python
# Should include these special case handlers:
if 'slip' in query and ('resistant' in query or 'resist' in query):
    return 'textured matte honed'  # Search for textured surfaces

if 'lft' in query:
    return 'lft'  # Search for LFT products (mortar/thinset)
```

**Solution 2 - Query Prioritization Fix:**

In `_search_products_text_fallback()`, ensure proper ORDER BY:
```python
# Should prioritize titles with search terms, not just SKU order
ORDER BY 
    CASE WHEN ({title_priority_clause}) THEN 1 ELSE 2 END,
    sku
```

**Solution 3 - Query Routing Fix:**

In `chat()` method, ensure installation materials are detected as product searches:
```python
# Override: If asking about specific products, treat as product search
specific_products = ['lft', 'thinset', 'mortar', 'grout', 'sealer', 'adhesive']
if any(product in query_lower for product in specific_products):
    is_product_search = True
    is_analytical = False
```

**Solution 4 - Non-Tile Product Support:**

Ensure non-tile queries (LFT, mortar, etc.) don't require tile filter:
```python
# Different filters for tile vs non-tile queries
non_tile_terms = ['lft', 'thinset', 'mortar', 'adhesive', 'grout', 'sealer']
is_non_tile_query = any(term in query.lower() for term in non_tile_terms)

if is_non_tile_query:
    filter_clause = ""  # No tile requirement for installation materials
```

**Testing the Fix:**
```bash
# Test all query types
python3 -c "
from simple_rag import SimpleTileShopRAG
rag = SimpleTileShopRAG()

queries = [
    'list 3 blue tile',
    'list 3 slip-resistant tile under 12$', 
    'suggest building materials for porcelain floor tile',
    'find best DCOF rated tile',
    'what can you tell me about your LFT thinset'
]

for query in queries:
    print(f'Testing: {query}')
    response = rag.chat(query)
    print('✅ SUCCESS' if 'couldn\\'t find' not in response else '❌ FAILED')
"
```

**Expected Results:**
- Blue tile: Marrakesh Blue, Hackney Dark Blue, Track Art Blue tiles
- Slip-resistant: Matte/textured ceramic tiles suitable for slip resistance
- Building materials: Tile protection kits, installation materials
- DCOF/slip-resistant: Anti-slip porcelain tiles (alternative to DCOF ratings)
- LFT thinset: Superior White LFT Bond Mortar with detailed specifications

## Diagnostic Framework Details

### Service Types and Their Status Logic

**Microservices (ContainerServiceDiagnostic):**
- Status: `healthy` (green) / `issues` (red)
- Checks: Container status, port accessibility, uptime
- DOM IDs: `${serviceName}-dot`, `${serviceName}-text`, `${serviceName}-info`

**Runtime Services (RuntimeServiceDiagnostic):**
- Status: `healthy` (green) / `issues` (red)  
- Checks: Environment dependencies, system resources
- DOM IDs: `${serviceName}-runtime-dot`, `${serviceName}-runtime-text`, `${serviceName}-runtime-info`

**Pre-warming Services (PrewarmServiceDiagnostic):**
- Status: `ready` (green) / `not_ready` (yellow) / `error` (red)
- Checks: Service initialization, database connections
- DOM IDs: `${serviceName}-dot`, `${serviceName}-text`, `${serviceName}-info`

### API Endpoints

**Service Management:**
- `GET /api/services/list` - List all registered services
- `GET /api/service/{name}/health` - Get service health status
- `GET /api/service/{name}/logs` - Get service logs
- `GET /api/service/{name}/debug` - Get debug information

**Service Categories:**
- **Microservices**: docker_engine, relational_db, vector_db, crawler, api_gateway, web_server, llm_api
- **Runtime**: python_env, system_dependencies, docker_daemon, infrastructure
- **Pre-warming**: python_subprocess, relational_db_prewarm, sitemap_validation, vector_db_prewarm, crawler_service_prewarm

## Recovery Procedures

### Full System Reset
```bash
# Stop all services
pkill -f "python reboot_dashboard.py"
docker stop $(docker ps -q)

# Start core services
docker start relational_db vector_db crawler api_gateway

# Restart dashboard
python reboot_dashboard.py
```

### Database Reset
```bash
# Reset database containers
docker stop relational_db vector_db
docker rm relational_db vector_db

# Recreate from docker-compose
docker-compose up -d relational_db vector_db
```

### Dashboard-Only Reset
```bash
# Quick restart
pkill -f "python reboot_dashboard.py"
python reboot_dashboard.py

# Access dashboard
open http://localhost:8080
```

## Performance Optimization

### Reduce Dashboard Load Time
- Services load in parallel using `updateAllServiceStatus()`
- Fast-boot mode enabled by default
- Monitoring disabled in development mode

### Optimize Service Health Checks
- Timeouts set to 5-10 seconds
- Container checks use single Docker inspect command
- Database connections pooled and reused

## Maintenance

### Regular Checks
1. **Weekly**: Run "Health Check All (17 Services)"
2. **Monthly**: Review container logs for errors
3. **Quarterly**: Update diagnostic thresholds

### Log Management
```bash
# Check dashboard logs
tail -f /var/log/tileshop_dashboard.log

# Check container logs
docker logs --tail 50 relational_db
docker logs --tail 50 vector_db
```

### Update Procedures
1. **Stop Dashboard**: `pkill -f "python reboot_dashboard.py"`
2. **Update Code**: `git pull origin master`
3. **Test Changes**: `python reboot_dashboard.py`
4. **Verify Status**: Check all 17 services show "Ready"

## Support

### Debug Information Collection
```bash
# System info
python --version
docker --version
docker-compose --version

# Service status
curl -s "http://localhost:8080/api/services/list" | jq '.'

# Container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Recent logs
docker logs --tail 20 relational_db
docker logs --tail 20 vector_db
```

### Common File Locations
- **Dashboard**: `reboot_dashboard.py`
- **Diagnostic Framework**: `modules/service_diagnostic.py`
- **Templates**: `templates/dashboard.html`
- **Configuration**: `.env`
- **Database Manager**: `modules/db_manager.py`

---

*Last Updated: July 6, 2025*
*Phase 2 Diagnostic Framework: Complete*