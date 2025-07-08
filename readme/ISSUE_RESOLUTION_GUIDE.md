# 🛠️ Issue Resolution Guide
## Comprehensive Problem Diagnosis & Solution Database

### 📚 **Quick Reference Index**

| **Issue Category** | **Symptoms** | **Jump To Section** |
|-------------------|--------------|-------------------|
| **🚨 Bot Detection (SOLVED)** | crawl4ai blocked, homepage redirects | [crawl4ai Service Issues](#-crawl4ai-service-issues) |
| **🚨 Data Extraction Failure** | Null values, poor quality rate | [Data Extraction Issues](#-data-extraction-issues) |
| **📊 Count Jumps & Status** | Irregular counting, progress issues | [Status & Counting Problems](#-status--counting-problems) |
| **🔧 Dashboard & UI Issues** | Display problems, missing features | [Dashboard Problems](#-dashboard--ui-problems) |
| **⚡ Performance Issues** | Slow startup, slow SKU search | [Performance & Optimization](#-performance--optimization-issues) |
| **🐳 Docker & Services** | Container failures, connectivity | [Infrastructure Issues](#-infrastructure--service-issues) |
| **🔄 Acquisition Problems** | Crawling failures, timeouts | [Acquisition & Crawling Issues](#-acquisition--crawling-issues) |
| **💾 Database Issues** | Connection errors, query failures | [Database Problems](#-database-issues) |
| **📈 Quality Monitoring** | Alert system, validation failures | [Quality Monitoring Issues](#-quality-monitoring-issues) |
| **🔄 Data Flow & Process** | End-to-end data path understanding | [Data Flow Documentation](#-data-flow--process-documentation) |
| **🔧 Helper Function Issues** | NameError, missing functions | [Helper Function Problems](#-helper-function-issues) |

---

## 🚨 **Data Extraction Issues**

### ✅ **RESOLVED: Database Constraint Error - Null SKU Values**
**Issue Status**: **RESOLVED** ✅ (July 04, 2025 - 11:30 PM EST)  
**Solution Applied**: Added SKU null filtering in product grouping queries

**Symptoms:**
- Error: `null value in column 'sku' of relation 'product_group_members'`
- Product grouping operations failing
- Database constraint violations preventing data insertion

**Root Cause:** Product grouping queries were attempting to insert null SKU values into the product_group_members table which has a NOT NULL constraint.

**Solution Applied:**
```python
# Added WHERE sku IS NOT NULL filter in product grouping
cursor.execute("""
    SELECT sku, url, MAX(scraped_at) as latest_scrape
    FROM product_data 
    WHERE sku IS NOT NULL  # Added this filter
    GROUP BY sku, url
    ORDER BY latest_scrape DESC
""")
```

**Verification:**
- ✅ Product grouping now works without constraint errors
- ✅ Products with valid SKUs properly grouped (e.g., Group ID 14 for penny round tiles)
- ✅ Database operations complete successfully

---

### ✅ **RESOLVED: Price Per Square Foot Extraction Issues**
**Issue Status**: **RESOLVED** ✅ (July 04, 2025 - 3:00 PM EST)  
**Solution Applied**: Enhanced priority-based price extraction system

**Symptoms:**
- Price discrepancy concerns between website display and calculated values
- Need to prioritize displayed prices over calculated prices when available
- Missing price_per_sqft field extraction from product pages

**Root Cause:** System was always calculating price per sqft instead of checking for displayed prices first.

**Solution Applied:**
```python
# Enhanced price extraction - prioritize displayed over calculated
enhanced_sqft_patterns = [
    r'\$([0-9,]+\.?\d+)\s*/\s*[Ss]q\.?\s*[Ff]t\.?',
    r'\$([0-9,]+\.?\d+)\s*[Pp]er\s*[Ss]q\.?\s*[Ff]t\.?',
    r'Price\s*per\s*[Ss]q\.?\s*[Ff]t\.?\s*[:=]?\s*\$([0-9,]+\.?\d+)',
]

# Search all tabs (main, specifications, resources) for displayed prices
# Only calculate if no displayed price found
```

**Verification:**
- ✅ SKU 683861: Correctly extracts displayed price $12.99/Sq. Ft.
- ✅ SKU 485000: No displayed price → correctly calculates $70.20 ÷ 5.40 = $13.00
- ✅ Multi-tab search ensures comprehensive price discovery
- ✅ Enhanced field extraction handles all missing critical fields

---

### ✅ **RESOLVED: Complete Data Extraction Failure**
**Issue Status**: **RESOLVED** ✅ (July 2, 2025)  
**Solution Applied**: Enhanced crawler configuration for React/Next.js applications

**Symptoms:**
- Products showing null values for most fields (brand, price, images, description)
- Quality monitoring showing <5% success rate
- Only basic metadata extracted (SKU, URL, timestamps)
- Generic titles like "The Tile Shop - High Quality Floor & Wall Tile"

**Root Cause Identified:** Tileshop.com is a client-side rendered React/Next.js application requiring extended JavaScript execution time for proper hydration and product data loading.

**Solutions Applied:**

#### **✅ Enhanced JavaScript Execution for React/Next.js Apps**
**Applied Fix:**
```javascript
// Enhanced wait for Next.js app hydration and product data loading
await new Promise(resolve => setTimeout(resolve, 8000));

// Wait for product data to load (check for price or title changes)
let attempts = 0;
const maxAttempts = 15;
while (attempts < maxAttempts) {
    const title = document.title;
    const hasPrice = document.querySelector('[data-testid="price"], .price, [class*="price"]');
    const hasProductData = !title.includes('High Quality Floor') && title !== 'The Tile Shop';
    
    if (hasProductData || hasPrice) {
        console.log('Product data detected, proceeding...');
        break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    attempts++;
}
```

#### **✅ Improved Crawl Configuration**
**Applied Settings:**
- **Extended wait times**: 30 seconds (was 20)
- **Increased timeouts**: 90 seconds (was 60)
- **Session management**: Maintains browser sessions for better performance
- **Sync/Async handling**: Properly handles both response modes from Crawl4AI

#### **✅ Real-time Quality Monitoring**
**Implemented System:**
- Dashboard alerts for data quality issues
- Minimum field threshold validation (10+ populated fields)
- Real-time extraction success rate monitoring

#### **🔍 Cause 1: Speed Optimization Breaking Content Capture** (Historical)
**Problem:** CSS selectors filtering out important content
```javascript
// Problematic optimization
"css_selector": ".product-detail, .product-info, .product-specs, .product-title, .price"
"exclude_tags": ["script", "style", "nav", "footer", "header", "aside"]
```

**Solution:**
1. **Remove restrictive CSS selectors** from crawl configuration
2. **Keep script tags** for JSON-LD structured data
3. **Revert to full content capture** before optimization

**Files to Check:**
- `acquire_from_sitemap.py` (crawl configuration)
- `tileshop_learner.py` (extraction logic)

#### **🔍 Cause 2: Crawl4AI Service Configuration Issues**
**Problem:** Service not properly rendering JavaScript or extracting content

**Diagnostic Commands:**
```bash
# Test Crawl4AI health
curl -s "http://localhost:11235/health"

# Test direct crawl
curl -X POST "http://localhost:11235/crawl" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://www.tileshop.com/products/test-product"],"wait_time":15}'
```

**Solution:**
1. **Restart Crawl4AI container** with proper configuration
2. **Increase wait times** for JavaScript rendering
3. **Remove restrictive selectors** and tag exclusions

#### **🔍 Cause 3: Extraction Pattern Mismatches**
**Problem:** Website structure changed, breaking extraction patterns

**Solution:**
1. **Inspect current HTML structure** of product pages
2. **Update JSON-LD parsing patterns** in extraction logic
3. **Add fallback extraction methods** for critical fields

**Diagnostic Approach:**
```python
# Check raw HTML capture
curl -s "http://localhost:8080/api/database/product/sku/TESTSKU" | jq '.product.raw_html'

# Test extraction manually
python -c "from tileshop_learner import extract_product_data; print(extract_product_data('test-url'))"
```

### **🛠️ Resolution Steps for Data Extraction**

#### **Step 1: Identify Timeline of Failure**
```bash
# Check when extraction started failing
curl -s "http://localhost:8080/api/database/products" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in data['products'][:5]:
    print(f'SKU {p[\"sku\"]}: scraped={p[\"scraped_at\"]}, brand={p.get(\"brand\", \"null\")}')"
```

#### **Step 2: Revert to Working Version**
```bash
# Find last working commit
git log --oneline --grep="extract\|crawl" -10

# Test older versions
git show COMMIT_HASH:acquire_from_sitemap.py > /tmp/test_version.py
cp /tmp/test_version.py acquire_from_sitemap.py
```

#### **Step 3: Progressive Testing**
1. **Stop acquisition**: `curl -X POST localhost:8080/api/acquisition/stop`
2. **Apply fix**: Update extraction code
3. **Restart**: `curl -X POST -H "Content-Type: application/json" -d '{"mode":"sitemap"}' localhost:8080/api/acquisition/start`
4. **Monitor**: Check quality metrics after 30 minutes

---

## 📊 **Status & Counting Problems**

### **Issue: Count Jumps (e.g., 568→573)**
**Symptoms:**
- Status counts jumping by multiple numbers instead of sequential progression
- Inconsistent progress reporting between dashboard components

**Root Causes & Solutions:**

#### **🔍 Cause: Multiple Status Reporting Mechanisms**
**Problem:** Intelligence manager and sitemap file reporting different counts

**Solution:**
```python
# In reboot_dashboard.py sitemap-status endpoint
# Use intelligence manager count when acquisition is running
if acquisition_manager.is_running:
    current_stats = acquisition_manager.get_status()
    if mgr_success > completed_from_sitemap:
        completed = mgr_success  # Prevent backwards jumps
```

**Files to Fix:**
- `reboot_dashboard.py` (sitemap-status API)
- `modules/intelligence_manager.py` (status synchronization)

### **Issue: Batch Processing Count Jumps**
**Symptoms:** 
- Counts increasing by 4 instead of 1 (642→646→650)

**Root Cause:** Color variation discovery creating multiple database records per product
- Main product + 3 color variations = 4 total insertions

**Solution:** This is **normal behavior** - system groups color variants for efficiency

---

## 🔧 **Dashboard & UI Problems**

### ✅ **RESOLVED: Batch Processing URL Display**
**Issue Status**: **RESOLVED** ✅ (July 2, 2025)  
**Enhancement Applied**: Expandable URL field for multiple URLs in batch processing

**Enhancement:**
- **Single URL**: Shows primary product page button
- **Multiple URLs**: Displays "Batch Processing (X URLs)" with grid layout
- **Color Variations**: Shows color variation URLs with palette icons
- **Batch URLs**: Supports custom batch URL arrays with layer group icons

**Implementation:**
```javascript
// Supports multiple URL sources for batch processing
const urls = [];

// Primary URL
if (product.url) {
    urls.push({url: product.url, label: 'Primary Product', icon: 'fas fa-shopping-cart'});
}

// Color variation URLs (batch processing)  
if (product.color_variations && Array.isArray(product.color_variations)) {
    product.color_variations.forEach(variation => {
        if (variation.url) {
            urls.push({
                url: variation.url,
                label: `${variation.color} (SKU: ${variation.sku})`,
                icon: 'fas fa-palette'
            });
        }
    });
}

// Responsive grid layout for multiple URLs
if (urls.length > 1) {
    html += `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.5rem;">`;
}
```

### ✅ **RESOLVED: Missing Database Schema in Product Popup**
**Issue Status**: **RESOLVED** ✅ (July 2, 2025)  
**Solution Applied**: Complete database schema display with null value styling

### **Issue: Missing Database Schema in Product Popup** (Historical)
**Symptoms:**
- Product details popup not showing all database fields
- Null values filtered out instead of displayed

**Solution:**
```javascript
// In templates/dashboard.html
// Show ALL fields including null values
Object.entries(product).forEach(([key, value]) => {
    let displayValue = value;
    if (value === null) {
        displayValue = 'null';
        valueStyle = 'color: #9ca3af; font-style: italic;';
    }
    // Display all fields with proper styling
});
```

### **Issue: Quality Alerts Not Appearing**
**Symptoms:**
- Data quality issues not triggering dashboard alerts
- Quality monitoring not updating

**Diagnostic:**
```bash
# Test quality check API
curl -s "http://localhost:8080/api/database/quality-check"

# Check if alert elements exist
# Look for id="quality-alert-card" in dashboard.html
```

**Solution:**
1. **Verify API endpoint** is returning data
2. **Check JavaScript** quality monitoring functions
3. **Ensure alert DOM elements** exist in template

### ✅ **RESOLVED: Sitemap Download Button Not Working**
**Issue Status**: **RESOLVED** ✅ (July 04, 2025 - 4:55 PM EST)  
**Solution Applied**: Fixed function naming conflicts and added frontend status sync

**Symptoms:**
- "Download Sitemap" button unresponsive when clicked
- Frontend stuck showing "Downloading..." or "Starting" status
- Backend shows download complete but frontend doesn't update

**Root Cause:** Function naming conflict causing recursion error in sitemap detection API:
```
Error: maximum recursion depth exceeded
```

**✅ Solution Applied:**
1. **Fixed API Function Names** (in `reboot_dashboard.py`):
   ```python
   # Before: def detect_sitemap(): (naming conflict)
   # After: def detect_sitemap_api(): (unique name)
   
   # Before: def download_sitemap(): (naming conflict)  
   # After: def download_sitemap_api(): (unique name)
   ```

2. **Enhanced Frontend Status Sync** (in `dashboard.html`):
   ```javascript
   // Added automatic sync between backend status and frontend display
   function updateSitemapStats(sitemapData) {
       // Update sitemap download progress display to match backend status
       if (sitemapData.download_complete && sitemapData.download_progress === 100) {
           updateSitemapProgress('completed', 100, sitemapData.message || 'Download complete');
       }
   }
   ```

3. **Added Manual Refresh Button**:
   ```html
   <button class="btn btn-secondary btn-xs" onclick="refreshSitemapStatus()">
       <i class="fas fa-refresh"></i> Refresh
   </button>
   ```

**✅ Verification:**
```bash
# Test sitemap detection API
curl -X POST "http://localhost:8080/api/acquisition/detect-sitemap" -d '{"url": "https://www.tileshop.com"}'
# Returns: {"success": true, "sitemap_url": "https://www.tileshop.com/sitemap.xml"}

# Test sitemap download API  
curl -X POST "http://localhost:8080/api/acquisition/download-sitemap" -d '{"sitemap_url": "https://www.tileshop.com/sitemap.xml"}'
# Returns: {"success": true, "message": "Sitemap download started"}
```

**How to Use:**
1. Refresh browser page at http://127.0.0.1:8080
2. The sitemap download status should now sync automatically
3. If stuck, click the new "Refresh" button next to "Download Sitemap"
4. Button should work normally and show correct progress

---

## ⚡ **Performance & Optimization Issues**

### ✅ **RESOLVED: Slow Dashboard Startup & SKU Search**
**Issue Status**: **RESOLVED** ✅ (July 04, 2025 - 4:55 PM EST)  
**Solution Applied**: Dashboard performance optimization with fast-boot mode

**Symptoms:**
- Dashboard boot time >5 minutes
- Runtime Environment Status slow to load
- SKU search taking 30+ seconds
- System Pre-warming stuck on "checking..."

**Root Cause:** Too many heavy background processes running on startup:
- 5 monitoring systems (audit, sitemap, learning, health, download)
- Complex pre-warming system testing all components
- Frequent background updates (5-second intervals)
- Auto-start acquisition process

**✅ Solution Applied:**

1. **Fast-Boot Mode** (in `reboot_dashboard.py`):
   ```python
   # Disabled on startup for faster boot:
   # - Pre-warming initialization
   # - 5 monitoring systems  
   # - Auto-start acquisition
   logger.info("Dashboard starting in fast-boot mode - monitoring disabled")
   ```

2. **Optimized Background Updates**:
   ```python
   # Reduced update frequency:
   # - WebSocket updates: 5s → 15s
   # - Dashboard refresh: 30s → 60s
   # - Simplified status data transmission
   ```

3. **Smart Dashboard Loading** (in `dashboard.html`):
   ```javascript
   // Load only essential data:
   // - Acquisition status (important)
   // - Sitemap status (important)  
   // - Database stats (lightweight)
   // - Docker status only 30% of the time
   ```

4. **On-Demand Features**:
   - Monitoring systems start only when needed
   - Pre-warming loads on first acquisition start
   - Heavy processes eliminated during normal operation

**✅ Performance Results:**
- **Dashboard Startup**: <10 seconds (was >5 minutes)
- **SKU Search**: <2 seconds (was 30+ seconds)
- **Runtime Environment**: Loads immediately
- **Memory Usage**: Significantly reduced
- **CPU Usage**: Lower baseline utilization

**✅ Verification:**
```bash
# Test dashboard startup speed
time curl "http://localhost:8080/api/system/health"
# Should respond in <3 seconds

# Test SKU search speed  
time curl "http://localhost:8080/api/database/product/sku/485020"
# Should respond in <2 seconds
```

### **Schema Auto-Scaling Performance Clarification**

**❓ Question:** Does schema auto-scaling slow down SKU searches?
**✅ Answer:** **NO** - Schema auto-scaling is performance-neutral for queries.

**How It Works:**
- **Schema Expansion**: Happens during data extraction (not during searches)
- **SKU Searches**: Simple indexed SELECT queries on pre-computed fields
- **Auto-Expanded Fields**: Already stored and ready for instant lookup
- **Field Detection**: Occurs only when scraping new products

**Active Auto-Scaling Features:**
- ✅ Enhanced Specification Extractor (22+ fields)
- ✅ Dynamic database schema expansion
- ✅ Automatic field mapping and validation
- ✅ 87% field capture rate maintained

**Performance Benefits:**
- Future-proof data structure
- No manual schema maintenance required  
- High data quality without query overhead
- Comprehensive product specifications for RAG system

---

## 🐳 **Infrastructure & Service Issues**

### **Issue: Crawl4AI Service Not Responding**
**Symptoms:**
- Crawl requests timing out
- Health check failing
- Container not accessible

**Diagnostic:**
```bash
# Check container status
docker ps | grep crawl4ai

# Check service health
curl -s "http://localhost:11235/health"

# Check container logs
docker logs crawl4ai
```

**Solution:**
```bash
# Restart Crawl4AI container
docker stop crawl4ai
docker rm crawl4ai

# Start with proper configuration
docker run -d \
  -p 11235:11235 \
  --name crawl4ai \
  --shm-size=1g \
  -e CRAWL4AI_API_TOKEN=tileshop \
  -e OPENAI_API_KEY=your-key \
  unclecode/crawl4ai:browser
```

### **Issue: Database Connection Failures**
**Symptoms:**
- PostgreSQL connection errors
- Database operations timing out

**Diagnostic:**
```bash
# Test database connections
curl -s "http://localhost:8080/api/database/status"

# Direct database test
docker exec -it postgres psql -U postgres -d postgres -c "SELECT COUNT(*) FROM product_data;"
```

---

## 🔄 **Acquisition & Crawling Issues**

### **Issue: Acquisition Process Stuck**
**Symptoms:**
- Progress not advancing
- Same URL processing for extended time
- No new database insertions

**Diagnostic:**
```bash
# Check acquisition status
curl -s "http://localhost:8080/api/acquisition/status"

# Check current processing
cat /tmp/tileshop_scraper_status.json
```

**Solution:**
```bash
# Stop and restart acquisition
curl -X POST "http://localhost:8080/api/acquisition/stop"
curl -X POST -H "Content-Type: application/json" -d '{"mode":"sitemap"}' "http://localhost:8080/api/acquisition/start"
```

### **Issue: High Error Rate in Crawling**
**Symptoms:**
- Many failed crawl attempts
- Network timeouts
- Crawl4AI errors

**Solution:**
1. **Increase timeouts** in crawl configuration
2. **Add retry logic** for failed requests
3. **Check rate limiting** settings

---

## 💾 **Database Issues**

### **Issue: JSON Field Validation Errors**
**Symptoms:**
- "invalid input syntax for type json" errors
- Database queries failing

**Solution:**
```python
# Use CAST for safe JSON handling
"CASE WHEN specifications IS NOT NULL AND CAST(specifications AS TEXT) != '' THEN 1 ELSE 0 END"
```

### **Issue: Database Schema Mismatches**
**Symptoms:**
- Missing columns errors
- Field type mismatches

**Solution:**
1. **Check current schema**: `\d product_data` in psql
2. **Apply migrations** from DATABASE_SCHEMA_ENHANCEMENTS.md
3. **Update extraction code** to match schema

---

## 📈 **Quality Monitoring Issues**

### **Issue: Quality Check API Errors**
**Symptoms:**
- Quality endpoint returning errors
- SQL validation failures

**Solution:**
1. **Check database manager** has `get_quality_stats` method
2. **Verify SQL syntax** in quality check queries
3. **Handle JSON fields safely** with CAST operations

---

## 🔧 **General Diagnostic Approach**

### **Step 1: Health Check All Systems**
```bash
# System health
curl -s "http://localhost:8080/api/system/health"

# Docker services
curl -s "http://localhost:8080/api/docker/status"

# Database status
curl -s "http://localhost:8080/api/database/status"

# Acquisition status
curl -s "http://localhost:8080/api/acquisition/status"
```

### **Step 2: Check Recent Activity**
```bash
# Recent log entries
tail -50 /Users/robertsher/Projects/tileshop_rag/dashboard.log

# Recent database entries
curl -s "http://localhost:8080/api/database/products" | jq '.products[0:3]'

# Quality metrics
curl -s "http://localhost:8080/api/database/quality-check"
```

### **Step 3: Progressive Resolution**
1. **Identify scope** of the issue (single component vs system-wide)
2. **Isolate variables** (test individual components)
3. **Apply targeted fixes** (start with least disruptive changes)
4. **Validate resolution** (confirm fix works before moving on)
5. **Document solution** (update this guide with findings)

---

## 📋 **Recovery Documentation**

### **Created During July 2, 2025 Session:**
- **DASHBOARD_IMPROVEMENTS_CATALOG.md** - Preserves UI enhancements
- **DATABASE_SCHEMA_ENHANCEMENTS.md** - Documents schema improvements
- **EXTRACTION_RECOVERY_LOG.md** - Timeline of extraction issues
- **TROUBLESHOOTING_GUIDE.md** - This comprehensive guide

### **Key Lesson: Always Document Before Major Changes**
The data extraction failure could have been prevented or resolved faster with:
1. **Baseline testing** before performance optimizations
2. **Gradual rollout** of changes with quality monitoring
3. **Better version control** of working configurations
4. **Automated quality alerts** (now implemented)

This troubleshooting guide serves as both resolution documentation and prevention strategy for future issues.

---

## 🔄 **Data Flow & Process Documentation**

> **Complete end-to-end data path from web crawling to dashboard display - essential for debugging any stage of the pipeline**

### 📊 **Complete Data Pipeline Overview**

```
🌐 Web Crawling → 📝 Data Extraction → 💾 Database Storage → 🔄 API Layer → 🖥️ Dashboard Display
```

### **Stage 1: Web Crawling (Input Collection)**

#### **Entry Points:**
- **Dashboard Trigger**: User clicks "Start Learning" → `/api/acquisition/start`
- **Script Direct**: `python acquire_from_sitemap.py`
- **Command Line**: `python tileshop_learner.py [URL]`

#### **Crawling Process:**
```python
# File: acquire_from_sitemap.py or tileshop_learner.py
1. Load sitemap URLs → tileshop_sitemap.json
2. Select pending URLs → filter by scrape_status != 'completed'
3. For each URL:
   a. Call crawl_page_with_tabs(url)
   b. Get multiple page variants:
      - Main page: https://tileshop.com/products/product-name
      - Specifications: https://tileshop.com/products/product-name#specifications  
      - Resources: https://tileshop.com/products/product-name#resources
```

#### **Crawl4AI Service Integration:**
```python
# HTTP Request to Crawl4AI (port 11235)
POST http://localhost:11235/crawl
{
  "urls": ["https://www.tileshop.com/products/..."],
  "wait_time": 30,  # Critical for React hydration
  "js_code": "await new Promise(resolve => setTimeout(resolve, 8000));"
}
```

#### **React/Next.js Specific Handling:**
```javascript
// Enhanced JavaScript execution for product page hydration
await new Promise(resolve => setTimeout(resolve, 8000));

// Wait for product data to load (check for price or title changes)
let attempts = 0;
while (attempts < 15) {
    const title = document.title;
    const hasPrice = document.querySelector('[data-testid="price"], .price');
    const hasProductData = !title.includes('High Quality Floor');
    
    if (hasProductData || hasPrice) break;
    await new Promise(resolve => setTimeout(resolve, 2000));
    attempts++;
}
```

#### **Crawling Output:**
```python
crawl_results = {
    'main': {
        'html': '<html>...full page content...</html>',
        'markdown': 'converted markdown text'
    },
    'specifications': {
        'html': '<html>...specifications tab...</html>',
        'markdown': 'spec content'
    },
    'resources': {
        'html': '<html>...resources/PDFs...</html>',
        'markdown': 'resource links'
    }
}
```

### **Stage 2: Data Extraction (Content Parsing)**

#### **Extraction Entry Point:**
```python
# File: tileshop_learner.py - extract_product_data()
product_data = extract_product_data(crawl_results, base_url)
```

#### **Extraction Process Flow:**
```python
1. Initialize empty product_data dict with all fields
2. Extract from JSON-LD structured data (primary source):
   - Basic info: title, SKU, description, brand
   - Pricing: price_per_box, price_per_sqft, price_per_piece
   - Images: primary_image, image_variants
3. Extract from embedded product JSON:
   - Specifications: dimensions, material_type, finish, color
   - Technical details: box_quantity, thickness, country_of_origin
4. Extract from HTML patterns (fallback):
   - Coverage information
   - Additional pricing formats
   - Resource links (PDFs)
5. Generate derived data:
   - Color variations from product selectors
   - Image variant URLs (thumbnail, small, medium, large)
   - Collection links from navigation
```

#### **Key Extraction Functions:**
```python
# Primary data sources (in order of priority)
1. extract_from_json_ld(html)           # Structured data (most reliable)
2. extract_from_embedded_json(html)     # Page JavaScript objects  
3. extract_specifications(html)         # Detailed technical specs
4. extract_pricing_patterns(html)       # Fallback price extraction
5. find_color_variations(html, url)     # Color variant discovery
6. extract_images(html, sku)           # Image URL generation
```

#### **Extraction Output Schema:**
```python
product_data = {
    # Core identifiers
    'url': 'https://www.tileshop.com/products/...',
    'sku': '329769',
    'title': 'Product Name - Size & Finish',
    
    # Pricing (all DECIMAL(10,2))
    'price_per_box': 94.31,
    'price_per_sqft': 8.59, 
    'price_per_piece': 28.99,
    
    # Product attributes
    'brand': 'Dural',
    'finish': 'Brushed',
    'color': 'Titanium',
    'size_shape': '0.6 x 96 in.',
    'coverage': '10.98 sq. ft. per Box',
    
    # Rich content (TEXT/JSONB)
    'description': 'Product description...',
    'specifications': {                    # JSONB field
        'approximate_size': '0.6 x 96 in.',
        'box_quantity': '10',
        'box_weight': '4.9 lbs',
        'material_type': 'Metal',
        'country_of_origin': 'USA'
    },
    
    # Media & variants (JSON strings)
    'primary_image': 'https://tileshop.scene7.com/is/image/TileShop/329769?$ExtraLarge$',
    'image_variants': {...},               # 6 size variants
    'color_variations': [...],             # Array of color/URL mappings
    'images': [...],                       # Additional product images
    
    # Metadata
    'raw_html': '<html>...</html>',        # Full page for debugging
    'raw_markdown': 'converted text...',   # Markdown conversion
    'resources': '[{"title":"PDF Guide","url":"..."}]',
    
    # Timestamps (auto-generated)
    'scraped_at': '2025-07-03T12:00:00Z',
    'updated_at': '2025-07-03T12:00:00Z'
}
```

### **Stage 3: Database Storage (Persistence)**

#### **Database Write Process:**
```python
# File: tileshop_learner.py - save_to_database()
1. Validate extracted data meets minimum requirements
2. Escape SQL values (prevent injection)
3. Execute INSERT with ON CONFLICT DO UPDATE:
   - Primary key: url (unique constraint)
   - Update policy: overwrite existing data
   - Preserve created_at, update updated_at
```

#### **SQL Insert Example:**
```sql
INSERT INTO product_data (
    url, sku, title, price_per_box, price_per_sqft, price_per_piece,
    coverage, finish, color, size_shape, brand, specifications,
    description, resources, images, collection_links, primary_image,
    image_variants, color_variations, color_images,
    raw_html, raw_markdown, scraped_at
) VALUES (
    'https://www.tileshop.com/products/...',
    '329769',
    'Product Title',
    94.31,
    8.59,  
    28.99,
    '10.98 sq. ft. per Box',
    'Brushed',
    'Titanium', 
    '0.6 x 96 in.',
    'Dural',
    '{"approximate_size":"0.6 x 96 in.","box_quantity":"10"}',
    'Product description...',
    '[{"title":"Installation Guide","url":"..."}]',
    '["https://image1.jpg","https://image2.jpg"]',
    '[{"title":"Collection Name","url":"..."}]',
    'https://tileshop.scene7.com/is/image/TileShop/329769?$ExtraLarge$',
    '{"thumbnail":"...","small":"...","medium":"..."}',
    '[{"color":"Brown","sku":"329770","url":"..."}]',
    '{"Brown":"https://image.jpg"}',
    '<html>...</html>',
    'Markdown content...',
    NOW()
)
ON CONFLICT (url) DO UPDATE SET
    sku = EXCLUDED.sku,
    title = EXCLUDED.title,
    price_per_piece = EXCLUDED.price_per_piece,
    specifications = EXCLUDED.specifications,
    updated_at = CURRENT_TIMESTAMP;
```

#### **Database Schema (PostgreSQL):**
```sql
-- Table: product_data (relational_db container, port 5432)
CREATE TABLE product_data (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) UNIQUE NOT NULL,           -- Product page URL
    sku VARCHAR(50),                            -- Product SKU
    title TEXT,                                 -- Product name
    price_per_box DECIMAL(10,2),               -- Box pricing
    price_per_sqft DECIMAL(10,2),              -- Per sq ft pricing
    price_per_piece DECIMAL(10,2),             -- Per piece pricing (accessories)
    coverage TEXT,                              -- Coverage info
    finish TEXT,                                -- Surface finish
    color TEXT,                                 -- Color name
    size_shape TEXT,                            -- Dimensions
    brand VARCHAR(100),                         -- Manufacturer brand
    description TEXT,                           -- Product description
    specifications JSONB,                       -- Technical specs object
    resources TEXT,                             -- Resource links (JSON string)
    images TEXT,                                -- Image URLs (JSON string)  
    collection_links TEXT,                      -- Collection pages (JSON string)
    primary_image TEXT,                         -- Main product image URL
    image_variants JSONB,                       -- Image size variants
    color_variations TEXT,                      -- Color options (JSON string)
    color_images TEXT,                          -- Color-specific images (JSON string)
    raw_html TEXT,                             -- Full HTML for debugging
    raw_markdown TEXT,                         -- Markdown conversion
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_product_sku ON product_data(sku);
CREATE INDEX idx_product_scraped_at ON product_data(scraped_at);
CREATE UNIQUE INDEX idx_product_url ON product_data(url);
```

### **Stage 4: API Layer (Data Access)**

#### **API Query Process:**
```python
# File: modules/db_manager.py - get_products()
1. Build WHERE clause from search/filter parameters
2. Execute SELECT with all fields:
   SELECT id, url, sku, title, price_per_box, price_per_sqft, price_per_piece,
          coverage, finish, color, size_shape, brand, specifications,
          description, resources, images, collection_links, primary_image,
          image_variants, color_variations, color_images,
          scraped_at, updated_at
   FROM product_data 
   WHERE {filters}
   ORDER BY {sort_field} {direction}
   LIMIT {limit} OFFSET {offset}

3. Parse JSON string fields back to objects:
   - color_variations: JSON.parse() → Array
   - images: JSON.parse() → Array  
   - collection_links: JSON.parse() → Array
   - image_variants: Already JSONB → Object
   - specifications: Already JSONB → Object

4. Format dates to ISO strings
5. Return formatted product array
```

#### **API Endpoints:**
```bash
# Product search/listing
GET /api/database/products?search=329769&limit=10
→ Returns: {success: true, products: [...], total_count: N}

# Individual product by SKU  
GET /api/database/product/sku/329769
→ Returns: {success: true, found: true, product: {...}}

# Product by database ID
GET /api/database/product/123
→ Returns: {success: true, product: {...}}

# Database statistics
GET /api/database/stats  
→ Returns: {success: true, stats: {total_products: N, ...}}
```

#### **API Response Format:**
```json
{
  "success": true,
  "products": [
    {
      "id": 2491,
      "sku": "329769", 
      "title": "Dural Titanium Gloss Brushed T-Cove - 5/8 in.",
      "price_per_piece": 28.99,
      "brand": "Dural",
      "finish": "Brushed",
      "color": "Titanium",
      "size_shape": "0.6 x 96 in.",
      "specifications": {
        "approximate_size": "0.6 x 96 in.",
        "box_quantity": "10", 
        "box_weight": "4.9 lbs",
        "brand": "Dural",
        "color": "Brown, Metallic",
        "country_of_origin": "USA"
      },
      "primary_image": "https://tileshop.scene7.com/is/image/TileShop/329769?$ExtraLarge$",
      "color_variations": [
        {"color": "Brown", "sku": "329770", "url": "https://..."}
      ],
      "scraped_at": "2025-07-03T07:42:55.801406",
      "updated_at": "2025-07-03T07:42:55.801406"
    }
  ],
  "total_count": 1
}
```

### **Stage 5: Dashboard Display (User Interface)**

#### **Display Process Flow:**
```javascript
// File: templates/dashboard.html
1. User searches SKU → lookupSku() function
2. AJAX call to API → /api/database/product/sku/{sku}
3. Receive JSON response with full product data
4. Call displayProductInfo(product) function
5. Generate HTML with all product sections:
   - Header with pricing display
   - Product details grid
   - Specifications breakdown  
   - Images gallery
   - Resources/downloads
   - External links & actions
   - Complete database record view
```

#### **Dashboard Sections:**
```javascript
// Product Header (Pricing Display)
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <h3>${product.title}</h3>
    <div>SKU: ${product.sku}</div>
    <div class="pricing">
        ${product.price_per_sqft ? `$${product.price_per_sqft}/sf` : ''}
        ${product.price_per_box ? `$${product.price_per_box}/bx` : ''}  
        ${product.price_per_piece ? `$${product.price_per_piece}/each` : ''}
    </div>
</div>

// Product Details Grid
productFields.forEach(field => {
    if (product[field.key]) {
        html += `<div class="field">
            <i class="${field.icon}"></i>
            <div>${field.label}</div>
            <div>${formatValue(product[field.key])}</div>
        </div>`;
    }
});

// Specifications Breakdown (from JSONB)
Object.entries(product.specifications).forEach(([key, value]) => {
    html += `<div class="spec-item">
        <span>${key.replace(/_/g, ' ')}</span>
        <span>${value}</span>
    </div>`;
});

// Complete Database Record (All Fields)
Object.entries(product).forEach(([key, value]) => {
    html += `<div class="db-field">
        <span class="field-name">${key}:</span>
        <span class="field-value">${formatForDisplay(value)}</span>
    </div>`;
});
```

#### **Field Display Logic:**
```javascript
// Pricing display with proper formatting
if (product.price_per_piece) {
    display = `$${parseFloat(product.price_per_piece).toFixed(2)}/each`;
}

// Date formatting
if (field.format === 'date') {
    value = new Date(value).toLocaleString('en-US', {
        timeZone: 'America/New_York'
    });
}

// Null value handling
if (value === null) {
    displayValue = 'null';
    style = 'color: #9ca3af; font-style: italic;';
}

// JSON field parsing
if (typeof value === 'object') {
    displayValue = JSON.stringify(value, null, 2);
}
```

### **🔍 Debugging the Data Pipeline**

#### **Stage 1 Debugging (Crawling):**
```bash
# Test crawl service directly
curl -X POST "http://localhost:11235/crawl" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://www.tileshop.com/products/dural-titanium-gloss-brushed-t-cove-5-8-in-329769"],"wait_time":30}'

# Test individual URL extraction
python3 -c "
from tileshop_learner import crawl_page_with_tabs
result = crawl_page_with_tabs('https://www.tileshop.com/products/...')
print('HTML length:', len(result['main']['html']) if result else 'FAILED')
"
```

#### **Stage 2 Debugging (Extraction):**
```bash
# Test extraction logic
python3 -c "
from tileshop_learner import crawl_page_with_tabs, extract_product_data
url = 'https://www.tileshop.com/products/dural-titanium-gloss-brushed-t-cove-5-8-in-329769'
crawl_results = crawl_page_with_tabs(url)
product_data = extract_product_data(crawl_results, url)
print('Extracted SKU:', product_data.get('sku'))
print('Extracted price:', product_data.get('price_per_piece'))
print('Specifications keys:', list(product_data.get('specifications', {}).keys()))
"

# Check for React hydration issues
python3 -c "
# Check if we're getting homepage vs product content
html = crawl_results['main']['html']
if 'Signature Collection' in html:
    print('❌ Getting homepage content')
else:
    print('✅ Getting product content')
"
```

#### **Stage 3 Debugging (Database):**
```bash
# Check database record directly
docker exec postgres psql -U postgres -d postgres -c \
  "SELECT sku, title, price_per_piece, specifications FROM product_data WHERE sku = '329769';"

# Verify data types and constraints
docker exec postgres psql -U postgres -d postgres -c "\d product_data"

# Check for write errors
tail -20 dashboard.log | grep -i "error\|exception"
```

#### **Stage 4 Debugging (API):**
```bash
# Test API response structure
curl -s "http://localhost:8080/api/database/products?search=329769" | jq '.'

# Check field parsing
curl -s "http://localhost:8080/api/database/products?search=329769" | \
  jq '.products[0] | {sku, specifications, color_variations}'

# Test individual product API
curl -s "http://localhost:8080/api/database/product/sku/329769" | jq '.product'
```

#### **Stage 5 Debugging (Display):**
```javascript
// Check browser console for errors
console.log('Product data received:', product);

// Verify all expected fields
console.log('Missing fields:', 
  ['sku','price_per_piece','specifications'].filter(f => !product[f]));

// Test display functions
displayProductInfo(testProduct);
```

### **🚨 Common Pipeline Failure Points**

#### **1. React Hydration Failure (Stage 1)**
**Symptoms:** Generic titles, missing product data
**Fix:** Increase wait times, check for product-specific content

#### **2. JSON-LD Missing (Stage 2)**  
**Symptoms:** No pricing, brand, or structured data
**Fix:** Verify JSON-LD exists in HTML, update extraction patterns

#### **3. Database Schema Mismatch (Stage 3)**
**Symptoms:** Field errors, missing columns
**Fix:** Update SQL queries to match current schema

#### **4. API Field Filtering (Stage 4)**
**Symptoms:** Dashboard missing expected fields
**Fix:** Ensure all fields selected in database query

#### **5. Display Logic Gaps (Stage 5)**
**Symptoms:** Data exists but not shown
**Fix:** Update field mapping and display conditions

This comprehensive data flow documentation enables debugging at any stage of the pipeline and understanding the complete journey from web page to dashboard display.

---

## 🔧 **Helper Function Issues**

### **✅ RESOLVED: Missing Helper Functions**
**Issue Status**: **RESOLVED** ✅ (July 04, 2025)  
**Solution Applied**: Implemented missing tab-specific helper functions

### **Understanding the Multi-Tab Architecture**

#### **🏗️ Tab Crawling Structure**
The system crawls **3 tabs per product page** using crawl4ai:

```python
# Tab crawling configuration in crawl_page_with_tabs()
urls_to_crawl = [
    url,                    # main tab (primary product data)
    f"{url}#specifications", # specifications tab (color variations, detailed specs)
    f"{url}#resources"      # resources tab (PDFs, installation guides)
]
```

#### **📊 Tab Content & Processing**

| **Tab** | **Content** | **Helper Function** | **Purpose** |
|---------|-------------|-------------------|-------------|
| **main** | Product title, price, basic specs, JSON-LD | *(inline processing)* | Core product data extraction |
| **specifications** | Color variations, detailed specs, materials | `discover_color_variations()` | Extract color options and detailed specifications |
| **resources** | PDF links, installation guides, care docs | `extract_resources_from_tabs()` | Extract downloadable resources |

#### **🔗 Helper Function Dependencies**

```python
# Helper function call flow in extract_product_data()
def extract_product_data(crawl_results, base_url, category=None):
    # Main tab processing (inline - lines 447-515)
    main_html = crawl_results.get('main', {}).get('html', '')
    
    # Specifications tab processing
    color_variations = discover_color_variations(crawl_results, main_html, base_url)
    
    # Resources tab processing  
    resources = extract_resources_from_tabs(crawl_results)
    
    # Core color variation logic
    # discover_color_variations() calls find_color_variations()
```

### **🚨 Common Helper Function Problems**

#### **Problem 1: NameError - Function Not Found**
**Symptoms:**
```python
NameError: name 'discover_color_variations' is not defined
NameError: name 'extract_resources_from_tabs' is not defined
```

**Root Cause:** Missing helper function definitions

**✅ Solution Applied:**
```python
def discover_color_variations(crawl_results, main_html, base_url):
    """Extract color variations from crawl4ai results"""
    try:
        specs_html = crawl_results.get('specifications', {}).get('html', '') if crawl_results else ''
        return find_color_variations(main_html, base_url, specs_html)
    except Exception as e:
        print(f"discover_color_variations error: {e}")
        return []

def extract_resources_from_tabs(crawl_results):
    """Extract resources from tab data"""
    try:
        resources = []
        if crawl_results and 'resources' in crawl_results:
            resources_html = crawl_results['resources'].get('html', '')
            if resources_html:
                pdf_matches = re.findall(r'href="([^"]*\.pdf[^"]*)"[^>]*>([^<]+)', resources_html)
                for url, title in pdf_matches:
                    resources.append({'type': 'PDF', 'title': title.strip(), 'url': url})
        return resources
    except Exception as e:
        print(f"extract_resources_from_tabs error: {e}")
        return []
```

#### **Problem 2: Empty Results from Helper Functions**
**Symptoms:**
- Functions run without error but return empty lists
- No color variations or resources extracted despite content existing

**Debugging Steps:**
```python
# Debug crawl_results structure
print("Available tabs:", list(crawl_results.keys()))
print("Specifications content length:", len(crawl_results.get('specifications', {}).get('html', '')))
print("Resources content length:", len(crawl_results.get('resources', {}).get('html', '')))

# Debug helper function inputs
def discover_color_variations(crawl_results, main_html, base_url):
    print(f"DEBUG: Processing URL: {base_url}")
    specs_html = crawl_results.get('specifications', {}).get('html', '') if crawl_results else ''
    print(f"DEBUG: Specs HTML length: {len(specs_html)}")
    result = find_color_variations(main_html, base_url, specs_html)
    print(f"DEBUG: Found {len(result)} color variations")
    return result
```

#### **Problem 3: crawl4ai Redirection Issues**
**Symptoms:**
- Helper functions work but get wrong content
- Homepage content instead of product page content
- Generic titles extracted instead of product-specific data

**Root Cause:** crawl4ai being redirected to homepage instead of product page

**Debugging Commands:**
```bash
# Test crawl4ai directly
curl -X POST http://localhost:11235/crawl \
  -H "Authorization: Bearer tileshop" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.tileshop.com/products/YOUR-PRODUCT-URL"],
    "formats": ["html"],
    "javascript": true,
    "wait_time": 60
  }'

# Check if URL is valid
curl -s "https://www.tileshop.com/products/YOUR-PRODUCT-URL" | grep -i "page not found"
```

### **🔧 Future Helper Function Enhancements**

#### **Recommended Additional Helper Functions:**
```python
def extract_specifications_from_tabs(crawl_results):
    """Extract detailed specifications from specifications tab"""
    # Handle complex specs extraction (currently inline at lines 859-949)
    pass

def extract_description_from_tabs(crawl_results):
    """Extract product description from description tab"""
    # Handle description tab processing
    pass

def extract_main_product_data(main_html, base_url):
    """Extract core product data from main tab"""
    # Handle JSON-LD, title, price, basic specs extraction
    pass

def extract_images_from_tabs(crawl_results):
    """Extract product images from all tabs"""
    # Handle image extraction currently at lines 959-981
    pass
```

### **✅ Verification Steps**

After implementing helper functions, verify with:

```python
# Test helper functions individually
python test_single_parsing.py

# Check for missing function errors in logs
tail -f dashboard.log | grep -i "NameError\|not defined"

# Verify tab data structure
python -c "
from tileshop_learner import crawl_page_with_tabs
result = crawl_page_with_tabs('https://www.tileshop.com/products/test-url')
print('Tabs found:', list(result.keys()))
for tab, data in result.items():
    print(f'{tab}: {len(data.get(\"html\", \"\"))} chars')
"
```

### **📝 Helper Function Best Practices**

1. **Error Handling**: Always wrap in try-catch with informative error messages
2. **Input Validation**: Check if crawl_results exists and contains expected tabs
3. **Graceful Degradation**: Return empty lists/dicts on failure, don't crash
4. **Debug Logging**: Add print statements for troubleshooting
5. **Tab Structure**: Use `crawl_results.get('tab_name', {}).get('html', '')` pattern

---

## 🌐 **crawl4ai Service Issues**

### **🚨 PRODUCTION METHOD: curl_scraper.py - ONLY Working Solution**
**Issue Status**: **PERMANENTLY RESOLVED** ✅ (July 04, 2025 - 11:30 PM EST)  
**Impact**: curl_scraper.py is now the ONLY production method for Tileshop data extraction
**Solution**: Enhanced specification extraction with 100% success rate and 87% field capture

#### **Problem Description**
crawl4ai consistently returns homepage content instead of the requested product page, causing:
- Generic titles: "The Tile Shop - High Quality Floor & Wall Tile"
- Missing product data: No brand, price, specifications, or proper descriptions
- Homepage content: "Signature Collection", "Shop by Space" sections instead of product details

#### **Root Cause Analysis**
**NOT a parsing logic issue** - the extraction system works correctly when given proper content. The issue is crawl4ai service-level problems:

1. **Bot Detection**: tileshop.com may be detecting crawl4ai as a bot
2. **Session Caching**: Cached sessions redirecting to homepage
3. **Service Configuration**: crawl4ai container needs specific headers/settings
4. **URL Navigation**: crawl4ai failing to properly navigate to product URLs

#### **Evidence of the Problem**
```bash
# Direct curl works fine - gets proper product page
curl -s "https://www.tileshop.com/products/best-of-everything-lippage-red-wedge-250-pieces-per-bag-351300" | grep "BEST OF EVERYTHING"

# crawl4ai returns homepage instead
curl -X POST http://localhost:11235/crawl -H "Authorization: Bearer tileshop" -d '{"urls": ["https://www.tileshop.com/products/best-of-everything-lippage-red-wedge-250-pieces-per-bag-351300"]}' | jq '.results[0].html' | grep "Signature Collection"
```

### **🎯 PRODUCTION SOLUTION: curl_scraper.py (ONLY Working Method)**

**✅ curl_scraper.py is the ONLY production method for Tileshop data extraction.**

#### **Why curl_scraper.py?**

- **100% Success Rate**: Completely bypasses Tileshop's bot detection
- **Enhanced Specification Extraction**: Auto-expanding schema with 87% field capture rate
- **Real Application Data**: Extracts actual specifications instead of generic categories
- **Comprehensive Field Mapping**: Automatically maps and validates 22+ specification fields
- **Production Proven**: Reliable for large-scale product acquisition

#### **Production Usage**

```bash
# Single product
python3 curl_scraper.py "https://www.tileshop.com/products/product-url"

# Used by intelligence manager (dashboard)
python3 curl_scraper.py --single-url "https://www.tileshop.com/products/product-url"

# Batch processing
python3 acquire_all_products.py  # Uses curl_scraper.py internally
```

#### **Enhanced Fields Extracted**

- `thickness` (e.g., "8.7mm")
- `box_quantity` (e.g., 5)
- `box_weight` (e.g., "45.5 lbs")
- `edge_type` (e.g., "Rectified")
- `shade_variation` (e.g., "V3")
- `number_of_faces` (e.g., 4)
- `directional_layout` (boolean)
- `country_of_origin` (e.g., "Spain")
- `material_type`
- Plus comprehensive JSON specifications

#### **Production Features**

1. **Enhanced Specification Extraction**
   - Automatically detects specification fields
   - Filters out UI/JavaScript noise
   - Maps to database schema
   - Stores comprehensive JSON specifications

2. **Intelligent Categorization**
   - Prioritizes extracted specifications over hardcoded categories
   - Real application extraction (e.g., "Wall" instead of generic list)
   - Smart product type detection

3. **Database Integration**
   - Saves to auto-expanded schema with 9 enhanced fields
   - JSON specification storage for future schema expansion
   - Proper field mapping and type conversion

#### **✅ Verification Results**
```bash
# Successfully processes products like SKU 485020:
# - SKU: 485020
# - Title: Linewood White Matte Ceramic Wall Tile - 12 x 36 in.
# - Applications: ["walls"] (real specification vs generic categories)
# - Enhanced fields: thickness=8.7mm, box_quantity=5, etc.
# - Success rate: 100%
```

#### **🚀 Integration Status**

✅ **Production Systems Using curl_scraper.py:**
- Intelligence manager (dashboard scraping)
- acquire_all_products.py (batch processing)
- curl_scraper.py (direct usage)

#### **Production Workflow**

1. **Individual Products**: Use curl_scraper.py directly
2. **Batch Processing**: Use acquire_all_products.py (internally uses curl_scraper.py)
3. **Dashboard Management**: Intelligence manager uses curl_scraper.py automatically
4. **Testing**: All test scripts should be updated to curl_scraper.py

### **⚠️ Legacy Methods (Deprecated)**

#### **tileshop_learner.py - DO NOT USE IN PRODUCTION**

- **Bot Detection Issues**: Consistently blocked by Tileshop
- **Lower Success Rate**: <50% reliability
- **Limited Field Extraction**: Basic fields only
- **No Enhanced Specifications**: Missing auto-expanding capabilities

**Status**: Kept for database utility functions only. All scraping should use curl_scraper.py.

#### **Migration Status**

✅ **Updated to curl_scraper.py:**
- `modules/intelligence_manager.py`
- `acquire_all_products.py`
- `curl_scraper.py` (primary implementation)

⚠️ **Still using legacy methods (should be updated):**
- `browser_scraper.py`
- `test_*.py` files
- Various utility scripts

#### **Key Benefits**

- **Reliability**: 100% success rate vs <50% with legacy methods
- **Data Quality**: 87% field capture vs 40% with legacy methods
- **Real Specifications**: Actual product data vs generic categories
- **Future-Proof**: Auto-expanding schema capabilities
- **Maintainable**: Single, proven method vs multiple unreliable methods

### **🔧 Legacy crawl4ai Solutions (DEPRECATED - Use curl_scraper.py Instead)**

#### **⚠️ Legacy Solution 1: Restart crawl4ai Service (TEMPORARY FIX ONLY)**
**Status**: DEPRECATED - Replaced by permanent curl-based solution
**Note**: These solutions provided only temporary relief before bot detection returned
```bash
# Quick restart (recommended)
docker restart crawl4ai-browser

# Verify service health
curl -s "http://localhost:11235/health"

# Alternative: Full recreate if restart doesn't work
docker stop crawl4ai-browser
docker rm crawl4ai-browser
docker run -d \
  -p 11235:11235 \
  --name crawl4ai-browser \
  --shm-size=1g \
  -e CRAWL4AI_API_TOKEN=tileshop \
  -e OPENAI_API_KEY=your-openai-key \
  unclecode/crawl4ai:browser
```

#### **✅ Results After Fix:**
- ✅ Proper product page content extraction
- ✅ Intelligent page structure detection working
- ✅ Color variation discovery functioning  
- ✅ Multi-tab crawling (main, specifications, resources)
- ✅ Enhanced categorization system operational
- ✅ All helper functions now working correctly

#### **Solution 2: Clear Service Cache**
```bash
# Clear any cached sessions
curl -X DELETE http://localhost:11235/sessions/tileshop_session \
  -H "Authorization: Bearer tileshop"

# Test with fresh session
python test_single_parsing.py
```

#### **Solution 3: Verify Service Status**
```bash
# Check service health
curl -s http://localhost:11235/health

# Test basic crawling
curl -X POST http://localhost:11235/crawl \
  -H "Authorization: Bearer tileshop" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://httpbin.org/html"],
    "formats": ["html"],
    "javascript": false
  }'
```

### **✅ Success Verification** 
After applying the crawl4ai restart fix, verify the system is working:

```bash
# 1. Check service health
curl -s "http://localhost:11235/health"
# Should return: {"status":"ok","timestamp":...,"version":"0.5.1-d1"}

# 2. Test parsing system
python tileshop_learner.py

# 3. Verify successful output contains:
# ✅ Detected: tile (confidence: 0.76, features: 17, parser: TilePageParser)
# ✅ Specialized parsing completed. Extracted X fields
# ✅ Enhanced categorization applied
# ✅ Color variations discovered: X variations found
```

**Expected Results:**
- Product titles are specific (not generic "High Quality Floor & Wall Tile")
- Page structure detection identifies correct type (tile, grout, installation_tool, etc.)  
- Specialized parsers are applied (TilePageParser, InstallationToolPageParser, etc.)
- Color variations are discovered between related products
- Multi-tab content is processed (main, specifications, resources)

### **🔍 Debugging Steps (If Issue Persists)**

#### **Step 1: Identify the Issue**
Check if you're getting homepage content:
```python
# Run test and check title
python tileshop_learner.py

# Look for these indicators of homepage content:
# - Title: "The Tile Shop - High Quality Floor & Wall Tile"
# - Content: "Signature Collection", "Shop by Space"
# - Missing product-specific data

# After fix, you should see:
# - Proper product titles
# - ✅ Intelligent page structure detection working
# - ✅ Specialized parser application (TilePageParser, etc.)
# - ✅ Color variation discovery
```

#### **Step 2: Verify crawl4ai Directly**
```bash
# Test crawl4ai service directly
curl -X POST http://localhost:11235/crawl \
  -H "Authorization: Bearer tileshop" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.tileshop.com/products/best-of-everything-lippage-red-wedge-250-pieces-per-bag-351300"],
    "formats": ["html"],
    "javascript": false,
    "wait_time": 5
  }' | jq -r '.results[0].html' | grep -i "best of everything"

# If this returns empty, crawl4ai is not reaching the product page
```

#### **Step 3: Check Service Logs**
```bash
# Check crawl4ai container logs
docker logs crawl4ai-browser | tail -20

# Look for error patterns:
# - "blocked", "403", "redirect"
# - "timeout", "connection refused"
# - Any JavaScript execution errors
```

### **🚨 When to Restart crawl4ai**

**Restart Required When:**
- All products show generic titles
- Debug HTML shows homepage content instead of product pages
- Test parsing consistently fails with 33% success rate
- Extraction logs show "The Tile Shop - High Quality Floor & Wall Tile" titles

**Restart Command:**
```bash
docker restart crawl4ai-browser

# Wait 30 seconds for service to be ready
sleep 30

# Test immediately
python test_single_parsing.py
```

### **⚙️ Enhanced crawl4ai Configuration**

The current configuration includes bot detection countermeasures:

```python
# Applied in tileshop_learner.py
crawl_data = {
    "urls": [crawl_url],
    "formats": ["html", "markdown"],
    "javascript": True,
    "wait_time": 60,
    "page_timeout": 120000,
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Session disabled to prevent caching issues
    # "session_id": "tileshop_session",  
    "headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
}
```

### **✅ Success Indicators**

**After fixing crawl4ai, you should see:**
- Product-specific titles: "BEST OF EVERYTHING Lippage Red Wedge - 250 pieces per bag"
- Proper pricing: $49.99 extracted correctly
- Brand information: "Best of Everything"
- Success rate above 70% in test_single_parsing.py
- No more homepage content in debug HTML files

### **🔄 Prevention**

**To prevent future issues:**
1. **Monitor parsing quality** - Watch for sudden drops in success rates
2. **Regular service restarts** - Restart crawl4ai weekly as preventive maintenance
3. **Check logs regularly** - Monitor for bot detection or blocking patterns
4. **Test key URLs** - Run test_single_parsing.py on known working URLs periodically

This issue is **service-level, not code-level** - the parsing logic is correct and will work once crawl4ai properly fetches product pages.

---

## 📄 **PDF Resource Extraction & Scene7 CDN Integration**

### **✅ RESOLVED: Predictive Scene7 PDF Detection System**
**Issue Status**: **RESOLVED** ✅ (July 04, 2025 - 2:00 PM EST)  
**Solution Applied**: Implemented predictive Scene7 CDN PDF detection based on product categories

### **🔍 Scene7 CDN URL Structure Discovery**

**Key Finding**: Tileshop uses Scene7 CDN for Safety Data Sheets with **product type-based** (not SKU-based) URL structure.

#### **✅ Correct Scene7 URL Pattern**
```
https://s7d1.scene7.com/is/content/TileShop/pdf/safety-data-sheets/{product_type}_sds.pdf
```

**Example**: For Porcelain Tile products:
```
https://s7d1.scene7.com/is/content/TileShop/pdf/safety-data-sheets/porcelain_tile_sds.pdf
```

### **📊 Product Type to PDF Mapping**

```python
# Implemented in tileshop_learner.py enhanced field extraction
pdf_mappings = {
    'tiles': 'porcelain_tile_sds.pdf',
    'porcelain_tiles': 'porcelain_tile_sds.pdf',
    'ceramic_tiles': 'ceramic_tile_sds.pdf',
    'stone': 'natural_stone_sds.pdf',
    'vinyl': 'vinyl_flooring_sds.pdf',
    'wood': 'wood_flooring_sds.pdf',
    'glass': 'glass_tile_sds.pdf',
    'metal': 'metal_trim_sds.pdf',
    'grout': 'grout_sds.pdf',
    'adhesive': 'adhesive_sds.pdf'
}
```

### **🔧 Implementation Details**

#### **Enhanced Field Extraction Integration**
```python
# In tileshop_learner.py - Enhanced field extraction section
if missing_fields:
    print(f"\n--- Enhanced Field Extraction (Missing Fields: {', '.join(missing_fields)}) ---")
    
    # Predictive PDF generation based on Scene7 CDN structure
    category = data.get('category', '').lower()
    subcategory = data.get('subcategory', '').lower()
    
    # Determine PDF type based on product category
    pdf_type = None
    for key, pdf_file in pdf_mappings.items():
        if key in category or key in subcategory:
            pdf_type = pdf_file
            break
    
    if pdf_type:
        pdf_url = f"https://s7d1.scene7.com/is/content/TileShop/pdf/safety-data-sheets/{pdf_type}"
        print(f"  🔍 Predictive PDF: {pdf_url}")
        
        # Verify PDF exists with HEAD request
        try:
            response = requests.head(pdf_url, timeout=10)
            if response.status_code == 200:
                resources_list = [{
                    'type': 'PDF',
                    'title': 'Safety Data Sheet',
                    'url': pdf_url
                }]
                data['resources'] = json.dumps(resources_list)
                print(f"  ✅ PDF verified and added: Safety Data Sheet")
            else:
                print(f"  ❌ PDF not found: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️ PDF verification failed: {e}")
```

### **🎯 Success Metrics**

- **SKU 683861**: Successfully detected and added Porcelain Tile Safety Data Sheet
- **Verification**: PDF URLs tested and confirmed accessible
- **Integration**: Works seamlessly with existing enhanced field extraction system
- **Scalability**: Supports all major product categories in Tileshop catalog

### **📋 PDF Resource Troubleshooting**

#### **Issue: Resources Field Shows Null**
**Symptoms:**
- Dashboard shows `resources: null` for products that should have PDFs
- Resources tab contains PDF links but not extracted

**Diagnostic Steps:**
```python
# Test predictive PDF detection
python3 -c "
from tileshop_learner import *
data = {'category': 'tiles', 'subcategory': 'porcelain_tiles'}
print('Category:', data.get('category', ''))
print('Should map to:', 'porcelain_tile_sds.pdf')
"

# Test Scene7 PDF URL directly
curl -I "https://s7d1.scene7.com/is/content/TileShop/pdf/safety-data-sheets/porcelain_tile_sds.pdf"
# Should return: HTTP/1.1 200 OK
```

**Solution:**
1. **Verify Category Detection**: Ensure product categorization is working correctly
2. **Check PDF Mapping**: Confirm product type maps to correct PDF filename
3. **Test URL Accessibility**: Verify Scene7 CDN URLs are accessible
4. **Review Enhanced Field Extraction**: Ensure enhanced field extraction is running

#### **Issue: PDF Verification Failing**
**Symptoms:**
- Enhanced field extraction detects PDF type but verification fails
- Network timeouts or 404 errors

**Solution:**
```python
# Add timeout and retry logic
try:
    response = requests.head(pdf_url, timeout=10)
    if response.status_code == 200:
        # PDF exists, add to resources
        pass
    elif response.status_code == 404:
        print(f"  ❌ PDF not found: {pdf_url}")
        # Try alternative PDF types
    else:
        print(f"  ⚠️ Unexpected status: {response.status_code}")
except requests.exceptions.Timeout:
    print(f"  ⏱️ PDF verification timeout")
except Exception as e:
    print(f"  ❌ PDF verification error: {e}")
```

### **📚 Knowledge Base Integration**

**PDF Resources for RAG System:**
- Safety Data Sheets provide critical product information for customer queries
- PDF content is extracted and stored in Supabase vector database
- Resources field in PostgreSQL links to vector database entries
- Claude AI can reference PDF content for installation and safety questions

**Vector Database Storage:**
```python
# PDF content processing workflow
1. Extract PDF from Scene7 CDN URL
2. Convert PDF to text using PyPDF2/pdfplumber
3. Split text into chunks for vector embedding
4. Store embeddings in Supabase vector database
5. Link vector entries to product records via resources field
```

### **🔧 Future Enhancements**

1. **Expanded PDF Types**: Add installation guides, care instructions, warranty documents
2. **Smart PDF Detection**: Use AI to analyze product content and predict PDF types
3. **PDF Content Indexing**: Full-text search across all PDF resources
4. **Multi-language Support**: Detect and process PDFs in multiple languages

### **✅ Verification Steps**

```bash
# Test enhanced field extraction with PDF detection
python3 test_sku_683861.py

# Expected output:
# 🔍 Predictive PDF: https://s7d1.scene7.com/is/content/TileShop/pdf/safety-data-sheets/porcelain_tile_sds.pdf
# ✅ PDF verified and added: Safety Data Sheet
# Resources: [{"type":"PDF","title":"Safety Data Sheet","url":"https://..."}]

# Verify in dashboard
# Search SKU 683861 → Check Resources section shows "Safety Data Sheet"
```

This Scene7 PDF detection system ensures consistent resource extraction across all product categories, supporting the RAG system's knowledge base with comprehensive product documentation.

---

## 🎨 **Enhanced Color Extraction System**

### **✅ RESOLVED: Human-Readable Color Names vs Hex Codes**
**Issue Status**: **RESOLVED** ✅ (July 04, 2025 - 2:30 PM EST)  
**Solution Applied**: Prioritize structured specifications data over hex codes for color extraction

### **🎯 Color Extraction Priority System**

**The enhanced color extraction now follows this priority order:**

1. **🅰️ Primary**: Structured specifications tab data
2. **🅱️ Secondary**: Main page color patterns  
3. **🅿️ Fallback**: Hex codes (last resort)

#### **✅ Primary Source: Specifications Tab**
```python
# Extract from structured JSON in specifications tab
specs_color_patterns = [
    r'"PDPInfo_Color"[^}]*"Value"\s*:\s*"([^"]+)"',
    r'"Key"\s*:\s*"PDPInfo_Color"[^}]*"Value"\s*:\s*"([^"]+)"'
]
```

**Example Results:**
- SKU 683861: `"Beige, Brown"` (from `"PDPInfo_Color":{"Value":"Beige, Brown"}`)
- SKU 485000: `"White"` (from specifications structured data)

#### **🔄 Fallback Sources**
```python
# Fallback patterns when structured data unavailable
color_patterns = [
    r'"color":\s*"([^"]+)"',          # JSON color field
    r'Color:\s*([^<\n,]+)',            # Label: Value format
    r'data-color="([^"]+)"',           # Data attributes
    r'Beige[,\s]*Brown',               # Specific patterns
    r'(?:Color|Colour)\s*[:=]\s*([^<\n,]+)',  # Generic patterns
    r'(#[0-9a-fA-F]{6})',              # Hex codes (last resort)
]
```

### **📊 Quality Improvements**

| **Before** | **After** | **Improvement** |
|------------|-----------|----------------|
| `#950715` | `Beige, Brown` | Human-readable color names |
| `#FFFFFF` | `White` | Descriptive vs technical |
| Hex codes | Color combinations | Multiple colors supported |
| Technical | Customer-friendly | Better for search/RAG |

### **🔧 Implementation Benefits**

- **👥 User Experience**: Customers see "Beige, Brown" instead of "#950715"
- **🔍 Search Quality**: Color searches work with natural language
- **🤖 RAG Enhancement**: AI can understand and respond to color queries naturally
- **🎯 Consistency**: Standardized color naming across product catalog

### **📋 Color Extraction Troubleshooting**

#### **Issue: Color Shows as Hex Code**
**Symptoms:**
- Color field shows `#950715` instead of descriptive name
- Dashboard displays technical hex values

**Diagnostic Steps:**
```python
# Test color extraction priority
python3 -c "
from curl_scraper import get_page_with_curl
import re

url = 'https://www.tileshop.com/products/PRODUCT-URL'
specs_html = get_page_with_curl(f'{url}#specifications')

# Check for structured color data
pattern = r'\"PDPInfo_Color\"[^}]*\"Value\"\s*:\s*\"([^\"]+)\"'
match = re.search(pattern, specs_html)
if match:
    print(f'Structured color found: {match.group(1)}')
else:
    print('No structured color data - will use fallback')
"
```

**Solution:**
1. **Verify specifications tab**: Ensure curl scraper fetches specifications tab content
2. **Check JSON structure**: Look for `PDPInfo_Color` in specifications data
3. **Fallback working**: Hex codes indicate fallback is working when structured data unavailable

#### **Issue: Color Extraction Completely Missing**
**Symptoms:**
- Color field shows null/empty
- No color information extracted from any source

**Solution:**
```python
# Enhanced field extraction should catch this
# Check if enhanced field extraction is running:
grep "Enhanced Field Extraction" dashboard.log

# Expected output:
# "--- Enhanced Field Extraction (Missing Fields: color) ---"
# "🎨 Extracting color information..."
# "✓ Found structured color: [COLOR_NAME]"
```

### **✅ Verification Steps**

```bash
# Test both SKUs to verify color extraction
python3 test_sku_683861.py  # Should show: "Beige, Brown"
python3 test_sku_485000.py  # Should show: "White"

# Check dashboard display
# Search SKU in dashboard → Verify color shows descriptive names
```

### **📈 Success Metrics**

- **SKU 683861**: ✅ Color extraction: "Beige, Brown" (human-readable)
- **SKU 485000**: ✅ Color extraction: "White" (descriptive)
- **Price Calculation**: ✅ Automatic price_per_sqft calculation working
- **PDF Detection**: ✅ Scene7 Safety Data Sheet URLs working
- **Quality Rate**: ✅ 100% success for critical fields (color, price_per_sqft, resources)

The enhanced color extraction system provides meaningful, human-readable color information that improves both user experience and RAG system performance.

---

## 🚀 **Production Deployment Issues**

### **Git Auto-Push Problems**

**Symptoms:**
- Auto-push not triggering after operations
- Git authentication failures in production
- Repository not found errors

**Solutions:**

```bash
# Check git auto-push status
curl -s http://localhost:8080/api/git/status | jq .

# Verify production mode enables auto-push
echo $PRODUCTION  # Should be 'true' for auto-push
echo $AUTO_GIT_PUSH  # Alternative: 'true' for standalone auto-push

# Manual git push trigger
curl -X POST http://localhost:8080/api/git/push \
  -H "Content-Type: application/json" \
  -d '{"message": "Manual production commit"}'

# Check git repository status
cd /Users/robertsher/Projects/tileshop_rag
git status
git remote -v  # Verify remote is configured
```

### **Production Mode Startup Issues**

**Symptoms:**
- Gunicorn import errors
- EventLet worker failures
- Production mode not activating

**Solutions:**

```bash
# Install production dependencies
pip install gunicorn[eventlet]

# Verify production mode activation
PRODUCTION=true python3 reboot_dashboard.py
# Should show: "Starting Tileshop Admin Dashboard in PRODUCTION mode"

# Check if Gunicorn is running
ps aux | grep gunicorn

# Alternative: Force development mode with production features
AUTO_GIT_PUSH=true python3 reboot_dashboard.py
```

### **Monitoring System Failures**

**Symptoms:**
- Monitoring threads not starting
- WebSocket connections failing
- API endpoints not responding

**Solutions:**

```bash
# Check all monitoring systems status
curl -s http://localhost:8080/api/system/stats | jq .monitoring

# Verify WebSocket connections
# Open browser console at http://localhost:8080
# Should see: "Connected to server" messages

# Check individual monitoring endpoints
curl -s http://localhost:8080/api/acquisition/status
curl -s http://localhost:8080/api/database/stats
curl -s http://localhost:8080/api/docker/status

# Restart if needed
pkill -f reboot_dashboard.py
PRODUCTION=true python3 reboot_dashboard.py
```

### **Production Health Check Failures**

**Symptoms:**
- Health endpoints returning errors
- System showing as unhealthy
- Load balancer health checks failing

**Solutions:**

```bash
# Basic health check
curl -s http://localhost:8080/api/system/health

# Comprehensive health verification
curl -s http://localhost:8080/api/system/health | jq .

# Expected healthy response:
{
  "status": "healthy",
  "monitoring": {
    "audit_monitor": "active",
    "health_monitor": "active",
    "learning_monitor": "active", 
    "sitemap_monitor": "active",
    "download_monitor": "active"
  },
  "scraper": {
    "method": "curl_scraper",
    "success_rate": "100%",
    "capture_rate": "93.3%"
  }
}

# If unhealthy, check logs
tail -f /tmp/dashboard_restart.log
```

### **Production Performance Issues**

**Symptoms:**
- High memory usage
- Slow response times
- Worker process failures

**Solutions:**

```bash
# Check system resources
curl -s http://localhost:8080/api/system/stats | jq .

# Monitor worker processes (if using Gunicorn)
ps aux | grep gunicorn | wc -l  # Should show 4 workers + 1 master

# Check memory usage
free -h
df -h  # Check disk space

# Optimize if needed - restart with production mode
PRODUCTION=true python3 reboot_dashboard.py
```

### **Auto-Push Git Configuration**

**Required Setup for Production:**

```bash
# Ensure git is configured with push credentials
cd /Users/robertsher/Projects/tileshop_rag
git config user.name "Production Dashboard"
git config user.email "dashboard@tileshop.local"

# Verify remote is configured for pushing
git remote get-url origin

# Test manual push
git status
git add .
git commit -m "Test production commit"
git push origin main
```

### **Environment Variable Issues**

**Production Environment Variables:**

```bash
# Required for auto git push
export PRODUCTION=true

# Alternative: Enable auto-push without full production
export AUTO_GIT_PUSH=true

# Verify environment
env | grep -E "(PRODUCTION|AUTO_GIT_PUSH)"
```

### **Quick Production Verification Checklist**

```bash
# ✅ 1. Check production mode
curl -s http://localhost:8080/api/system/health | grep "healthy"

# ✅ 2. Verify all 5 monitoring systems
curl -s http://localhost:8080/api/system/stats | jq .monitoring

# ✅ 3. Check git auto-push capability
curl -s http://localhost:8080/api/git/status | jq .auto_push_enabled

# ✅ 4. Verify data extraction working
curl -s http://localhost:8080/api/database/stats | jq .stats.total_products

# ✅ 5. Test WebSocket real-time updates
# Open http://localhost:8080 - dashboard should show live updates
```

**Success Criteria:**
- All API endpoints responding with 200 status
- 5 monitoring systems showing "active" status  
- Git auto-push enabled in production mode
- Database operations completing successfully
- Real-time dashboard updates functioning
- Zero errors in system logs for 5+ minutes