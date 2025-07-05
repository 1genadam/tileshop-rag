# Tileshop RAG System - Maintenance Guide

**✅ PRODUCTION STATUS**: Optimized and stable (July 04, 2025)

## 🚀 Quick Start

```bash
# Start the system
python3 reboot_dashboard.py

# Access dashboard
http://127.0.0.1:8080
```

## 🔧 Key Maintenance Commands

### Dashboard Management
```bash
# Restart dashboard (optimized startup)
python3 reboot_dashboard.py

# Stop all processes
python3 stop_all_processes.py
```

### Data Acquisition
```bash
# Scrape single product (PRODUCTION METHOD)
python3 curl_scraper.py "https://www.tileshop.com/products/product-url"

# Batch acquisition
python3 acquire_all_products.py
```

### System Health
```bash
# Check database
python3 db_connection_test.py

# Audit data quality
python3 audit_tile_data_extraction.py
```

## 📁 Critical Files

### Core System
- `reboot_dashboard.py` - Main dashboard server (Flask)
- `curl_scraper.py` - Production scraper (100% reliable)
- `tileshop_learner.py` - Data extraction engine
- `enhanced_specification_extractor.py` - Auto-expanding schema

### Database
- `create_vector_tables.sql` - Database schema
- `product_data` table - Main product storage

### Configuration
- `templates/dashboard.html` - Dashboard UI
- Environment variables for database connection

## 🔧 Common Issues & Solutions

### Dashboard Won't Start
```bash
# Check if port 8080 is in use
lsof -i :8080

# Force restart
python3 stop_all_processes.py && python3 reboot_dashboard.py
```

### Sitemap Download Button Not Working
- **Fixed**: Function naming conflicts resolved
- **Status**: Working correctly

### Slow Performance
- **Optimized**: Fast-boot mode enabled
- **Status**: Dashboard starts quickly, monitoring disabled on startup

### Data Extraction Issues
- **Solution**: Use `curl_scraper.py` (100% success rate)
- **Backup**: crawl4ai available if needed

## 📊 System Architecture

```
Users → Dashboard (Flask) → curl_scraper.py → Database
                         ↓
                    Enhanced Extraction → Auto-Schema
```

## 🎯 Key Features

- **Fast-boot dashboard** with reduced overhead
- **100% reliable scraping** via curl_scraper.py
- **Auto-expanding schema** for new product fields
- **Real-time monitoring** of acquisition status
- **Schema auto-scaling** (performance optimized)

## 📋 Troubleshooting

For detailed issue resolution, see: [troubleshooting_guide.md](troubleshooting_guide.md)

For complete documentation, see: [README_expanded.md](README_expanded.md)