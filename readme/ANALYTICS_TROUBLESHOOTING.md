# Analytics Troubleshooting Guide

## 🔍 **Common Analytics Issues & Solutions**

This guide covers troubleshooting procedures for Learning Analytics and dashboard metrics issues.

---

## 📊 **Analytics Dashboard Issues**

### Issue 1: Analytics Showing Zero Values
**Symptoms**: Total Acquired: 0, Success Rate: -, Avg Processing Time: -

**Diagnostic Steps**:
```bash
# 1. Check database connection
docker ps | grep -E "(relational_db|vector_db)"

# 2. Test database direct query
docker exec relational_db psql -U postgres -d postgres -c "SELECT COUNT(*) FROM product_data;"

# 3. Test API endpoint
curl -s http://127.0.0.1:8080/api/database/stats | jq .
```

**Common Causes & Solutions**:

1. **Wrong Database Target** ✅ **FIXED**
   - **Cause**: Dashboard querying vector_db instead of relational_db
   - **Solution**: Ensure `dashboard_app.py:887` uses `'relational_db'` parameter
   - **Fix**: `stats = db_manager.get_product_stats('relational_db')`

2. **Database Connection Issues**
   - **Cause**: relational_db container not running
   - **Solution**: Restart database containers
   ```bash
   docker restart relational_db
   docker restart vector_db
   ```

3. **Empty Product Table**
   - **Cause**: No data in product_data table
   - **Solution**: Check data acquisition status
   ```bash
   curl -s http://127.0.0.1:8080/api/acquisition/status
   ```

---

## 🔄 **Data Acquisition vs Analytics Mismatch**

### Issue 2: Learning Active but Analytics Not Updating
**Symptoms**: Acquisition shows "learning active" but analytics remain at 0

**Diagnostic Process**:
```bash
# 1. Check acquisition status
curl -s http://127.0.0.1:8080/api/acquisition/status | jq '.status.stats'

# 2. Check database product count
docker exec relational_db psql -U postgres -d postgres -c "SELECT COUNT(*) FROM product_data;"

# 3. Check dashboard database target
grep -n "get_product_stats" /Users/robertsher/Projects/tileshop_rag_prod/dashboard_app.py
```

**Solution Steps**:
1. **Verify Database Target**: Ensure dashboard queries relational_db
2. **Check Data Sync**: Verify acquisition data is being stored
3. **Restart Dashboard**: `./reboot_dashboard.sh`

---

## 🗄️ **Database Architecture Troubleshooting**

### Database Routing Issues
**Understanding the Dual Database System**:

```python
# CORRECT routing for analytics
db_manager.get_product_stats('relational_db')  # ✅ Product data
db_manager.get_product_stats('supabase')       # ❌ Vector embeddings only
```

**Verification Commands**:
```bash
# Relational DB (product data)
docker exec relational_db psql -U postgres -d postgres -c "SELECT COUNT(*) FROM product_data;"

# Vector DB (embeddings only)
docker exec vector_db psql -U postgres -d postgres -c "SELECT COUNT(*) FROM documents;"
```

---

## 📈 **Performance Metrics Issues**

### Issue 3: Incorrect Success Rate Calculation
**Symptoms**: Success rate shows unexpected values

**Diagnostic Query**:
```sql
SELECT 
    COUNT(*) as total_products,
    COUNT(*) FILTER (WHERE sku IS NULL OR title IS NULL) as failed_products,
    (COUNT(*) - COUNT(*) FILTER (WHERE sku IS NULL OR title IS NULL)) * 100.0 / COUNT(*) as success_rate
FROM product_data;
```

**Common Issues**:
- **Null SKUs**: Products without SKU identifiers
- **Missing Titles**: Products without title data
- **Parsing Failures**: Incomplete data extraction

---

## 🔧 **API Endpoint Troubleshooting**

### Issue 4: Analytics API Returning Errors
**Test API Endpoints**:
```bash
# Database stats
curl -s http://127.0.0.1:8080/api/database/stats

# Acquisition status
curl -s http://127.0.0.1:8080/api/acquisition/status

# System health
curl -s http://127.0.0.1:8080/api/system/stats
```

**Common Responses**:
```json
// ❌ WRONG: Vector DB response
{
  "stats": {
    "message": "Vector DB contains embeddings/documents, not product data"
  }
}

// ✅ CORRECT: Relational DB response
{
  "stats": {
    "total_products": 4763,
    "success_rate": 100,
    "available_urls": 4773
  }
}
```

---

## 🚨 **Emergency Recovery Procedures**

### Complete Analytics Reset
```bash
# 1. Stop dashboard
pkill -f "python dashboard_app.py"

# 2. Clear Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 3. Restart containers
docker restart relational_db vector_db

# 4. Restart dashboard
./reboot_dashboard.sh

# 5. Verify fix
curl -s http://127.0.0.1:8080/api/database/stats | jq '.stats.total_products'
```

### Dashboard Health Check
```bash
# Check dashboard process
ps aux | grep dashboard_app.py

# Check log for errors
tail -f dashboard.log | grep -i error

# Check database connections
docker exec relational_db psql -U postgres -d postgres -c "SELECT 1;"
```

---

## 🔍 **Diagnostic Checklist**

### Analytics Not Updating
- [ ] Dashboard running (check process)
- [ ] Database containers running
- [ ] Correct database target in code
- [ ] API endpoints responding
- [ ] Product data exists in relational_db
- [ ] No errors in dashboard.log

### Data Acquisition Issues
- [ ] Acquisition process running
- [ ] URLs being processed
- [ ] Data being inserted to product_data
- [ ] No crawling errors
- [ ] Sitemap accessible

### Performance Issues
- [ ] Database queries completing
- [ ] No connection timeouts
- [ ] Reasonable response times
- [ ] No memory issues
- [ ] Docker containers healthy

---

## 📋 **Monitoring Commands**

### Real-time Monitoring
```bash
# Monitor dashboard logs
tail -f dashboard.log

# Monitor database activity
docker exec relational_db psql -U postgres -d postgres -c "SELECT COUNT(*) FROM product_data;" 

# Monitor API responses
watch -n 5 'curl -s http://127.0.0.1:8080/api/database/stats | jq .stats.total_products'
```

### Health Checks
```bash
# Service health
curl -s http://127.0.0.1:8080/api/services/list

# Database health
curl -s http://127.0.0.1:8080/api/service/relational_db/health
curl -s http://127.0.0.1:8080/api/service/vector_db/health
```

---

## 🛠️ **Prevention Best Practices**

### Code Review Points
1. **Database Parameter Validation**: Always verify database target
2. **Error Handling**: Implement proper exception handling
3. **Logging**: Add debug logging for database operations
4. **Testing**: Include analytics in integration tests

### Monitoring Setup
1. **Health Checks**: Regular API endpoint monitoring
2. **Data Validation**: Check product counts consistency
3. **Alert System**: Monitor for zero-value analytics
4. **Performance Metrics**: Track response times

---

## 📝 **Known Issues & Workarounds**

### 1. Vector DB Fallback
- **Issue**: Code falls back to vector DB when relational DB fails
- **Workaround**: Always check database target in API calls
- **Fix**: Implement proper database routing validation

### 2. Gunicorn Context Issues
- **Issue**: Flask application context errors with eventlet
- **Workaround**: Use development server for local testing
- **Fix**: Proper eventlet monkey patching

### 3. Cache Invalidation
- **Issue**: Browser cache showing old analytics
- **Workaround**: Force browser refresh (Cmd+Shift+R)
- **Fix**: Implement cache headers for API responses

---

## 🔗 **Related Documentation**

- **[LEARNING_ANALYTICS_FIX.md](LEARNING_ANALYTICS_FIX.md)** - Complete fix documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Database architecture
- **[DASHBOARD_MANUAL.md](DASHBOARD_MANUAL.md)** - Dashboard operations
- **[SYSTEM_DIAGNOSTICS.md](SYSTEM_DIAGNOSTICS.md)** - Service diagnostics
- **[QUICK_FIXES.md](QUICK_FIXES.md)** - Emergency solutions

---

## 🎯 **Quick Reference**

### Most Common Fix
```bash
# Analytics showing zeros
./reboot_dashboard.sh
curl -s http://127.0.0.1:8080/api/database/stats | jq .stats.total_products
```

### Emergency Reset
```bash
# Complete system reset
docker restart relational_db vector_db
./reboot_dashboard.sh
```

### Verification
```bash
# Check everything is working
curl -s http://127.0.0.1:8080/api/database/stats | jq '.stats | {total_products, success_rate: ((.total_products - .failed_products) / .total_products * 100)}'
```

---

*Last Updated: July 9, 2025*  
*Primary Fix: dashboard_app.py database routing*  
*Status: Analytics fully operational*