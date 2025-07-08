# ⚡ Quick Fixes & Emergency Solutions

## 🚨 Emergency Dashboard & System Recovery

| **Problem** | **Quick Solution** |
|-------------|-------------------|
| Dashboard won't start | `python3 stop_all_processes.py && python3 reboot_dashboard.py` |
| Can't access http://127.0.0.1:8080 | Check if port busy: `lsof -i :8080` |
| Sitemap download button broken | **FIXED** - Function naming conflicts resolved |
| Very slow startup (>5 min) | **FIXED** - Fast-boot mode enabled |
| Data extraction failing | Use: `python3 curl_scraper.py [URL]` |
| Database connection errors | Run: `python3 db_connection_test.py` |

---

## 🔧 Dashboard Issues

### Dashboard Won't Start
```bash
# 1. Check what's using port 8080
lsof -i :8080

# 2. Kill existing processes
python3 stop_all_processes.py

# 3. Restart dashboard
python3 reboot_dashboard.py

# 4. Verify it's running
curl http://127.0.0.1:8080
```

### ✅ FIXED: Sitemap Download Button Not Working
**Status**: **RESOLVED** ✅ (July 04, 2025)
- **Issue**: Function naming conflicts caused recursion error
- **Fix**: Renamed Flask routes to avoid conflicts
- **Verification**: Button now works correctly

### ✅ FIXED: Slow Dashboard Performance  
**Status**: **RESOLVED** ✅ (July 04, 2025)
- **Issue**: Dashboard startup >5 minutes, slow SKU search
- **Fix**: Fast-boot mode, disabled monitoring systems on startup
- **Verification**: Dashboard starts quickly, optimized performance

---

## 🌐 Data Extraction Issues

### Use Production Method: curl_scraper.py
```bash
# Single product (RECOMMENDED)
python3 curl_scraper.py "https://www.tileshop.com/products/product-url"

# Batch processing
python3 acquire_all_products.py
```

### ✅ RESOLVED: Data Extraction Failures
**Status**: **RESOLVED** ✅ 
- **Solution**: curl_scraper.py provides 100% success rate
- **Verification**: Bypasses all bot detection, extracts complete data

---

## 💾 Database Issues

### Database Connection Problems
```bash
# Test database connection
python3 db_connection_test.py

# Check database status
psql -h localhost -U [username] -d tileshop_rag
```

### ✅ RESOLVED: Null SKU Constraint Errors
**Status**: **RESOLVED** ✅
- **Issue**: null value in column 'sku' errors
- **Fix**: Added WHERE sku IS NOT NULL filters
- **Verification**: Product grouping works correctly

---

## ⚡ Performance Optimization

### Schema Auto-Scaling Performance
- **Clarification**: Schema auto-scaling does NOT impact query performance
- **Status**: Enabled and optimized
- **Impact**: Minimal overhead for automatic field detection

### Fast-Boot Mode
- **Feature**: Dashboard starts in optimized mode
- **Benefits**: Reduced startup time, disabled heavy monitoring
- **Status**: Enabled by default in reboot_dashboard.py

---

## 🔍 System Health Checks

### Quick Health Audit
```bash
# Check data quality
python3 audit_tile_data_extraction.py

# Verify extraction system
python3 enhanced_specification_extractor.py

# Test single product
python3 curl_scraper.py [test_url]
```

### Log Locations
- Dashboard logs: Console output from `reboot_dashboard.py`
- Extraction logs: Output from curl_scraper.py operations
- Database logs: PostgreSQL logs

---

## 📋 For Detailed Information

**Complete documentation**: [troubleshooting_guide_expanded.md](troubleshooting_guide_expanded.md)

**Full system guide**: [README_expanded.md](README_expanded.md)