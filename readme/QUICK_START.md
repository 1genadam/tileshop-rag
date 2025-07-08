# 🚀 Quick Start Guide

## TileShop Intelligence Platform - Getting Started

This guide will get you up and running with the TileShop Intelligence Platform in minutes.

---

## 🎯 **Prerequisites**

Before starting, ensure you have:
- **Python 3.8+** installed
- **Docker** running (for external services)
- **Git** configured for repository access

---

## ⚡ **One-Command Startup**

### **Optimized Dashboard Management**
```bash
# Start dashboard (optimized for fast boot)
python3 dashboard_app.py

# Access dashboard (should load in ~5 seconds)
open http://127.0.0.1:8080

# Monitor logs if needed
tail -f dashboard.log
```

---

## 🌐 **Available Services**

Once started, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://127.0.0.1:8080 | Main management interface (fast-boot mode) |
| **RAG Chat** | http://127.0.0.1:8080/chat | Product search and assistance |
| **PostgreSQL** | http://localhost:5050 | pgAdmin (if available) |
| **Supabase** | http://localhost:54323 | Vector database studio (if available) |
| **Crawler API** | http://localhost:11235 | Crawl4AI service |
| **API Gateway** | http://localhost:8000 | Service routing |

---

## 🚀 **Performance Features**

The system includes several optimizations for immediate productivity:

- **⚡ Fast Boot**: Dashboard starts in seconds with optimized loading
- **🔍 Instant SKU Search**: Optimized database queries for immediate results
- **📊 Smart Updates**: Reduced background processing for better responsiveness
- **🎯 On-Demand Monitoring**: Heavy systems start only when needed
- **🚀 Schema Auto-Scaling**: Automatic field detection without performance impact

---

## 🎯 **First Steps After Startup**

### 1. **Verify System Health**
```bash
# Check all services status
curl -s http://127.0.0.1:8080/api/system/health

# Or use the dashboard health check
# Navigate to: http://127.0.0.1:8080/admin
```

### 2. **Test Product Search**
```bash
# Test RAG chat system
curl -X POST http://127.0.0.1:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show me subway tiles"}'

# Or use the web interface
# Navigate to: http://127.0.0.1:8080/chat
```

### 3. **Access Admin Dashboard**
```bash
# Open the main dashboard
open http://127.0.0.1:8080

# Key features:
# - Real-time system monitoring
# - Product database viewer
# - Scraping progress tracking
# - Service health checks
```

---

## 🔧 **Common Commands**

### **System Management**
```bash
# Restart dashboard
python3 dashboard_app.py

# Fast reboot (development)
./fast_reboot.sh

# Full system reboot
./reboot_dashboard.sh

# Check system status
python3 health_check.py
```

### **Data Operations**
```bash
# Start product scraping
python3 acquire_all_products.py

# Single product extraction
python3 curl_scraper.py "https://www.tileshop.com/products/product-url"

# Database operations
python3 -c "from dashboard_app import get_product_count; print(f'Products: {get_product_count()}')"
```

---

## 🚨 **Troubleshooting Quick Fixes**

### **Dashboard Won't Start**
```bash
# Check for port conflicts
lsof -i :8080

# Kill conflicting processes
pkill -f dashboard_app.py

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### **Services Not Available**
```bash
# Check Docker services
docker ps

# Start required containers
docker-compose up -d

# Test service connectivity
curl -s http://localhost:11235/health  # Crawl4AI
curl -s http://localhost:5432  # PostgreSQL
```

### **Database Issues**
```bash
# Check database connection
python3 -c "import psycopg2; print('DB OK')"

# Verify tables exist
python3 -c "from dashboard_app import get_db_stats; print(get_db_stats())"
```

---

## 📚 **Next Steps**

After getting the system running:

1. **📖 Read the Documentation**: Check [INDEX.md](INDEX.md) for comprehensive guides
2. **🎯 Learn the Dashboard**: See [DASHBOARD_MANUAL.md](DASHBOARD_MANUAL.md) for detailed operations
3. **🚀 Deploy to Production**: Follow [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md) for cloud deployment
4. **🔧 Troubleshoot Issues**: Use [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common problems

---

## 💡 **Tips for Success**

### **Development Workflow**
- Use `fast_reboot.sh` for quick development cycles
- Monitor `dashboard.log` for real-time debugging
- Keep Docker services running for best performance

### **Performance Optimization**
- The system auto-scales based on usage patterns
- Heavy processing runs in background to maintain responsiveness
- Use on-demand scraping for immediate results

### **Best Practices**
- Always check system health before major operations
- Use the dashboard for visual monitoring
- Keep the database optimized with regular maintenance

---

*For detailed documentation, see [INDEX.md](INDEX.md) | For issues, check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)*