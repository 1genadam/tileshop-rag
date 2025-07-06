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

## 🔄 Process Inventory & Management

### Dashboard Built-in Processes
| **Process** | **Status** | **Resource Impact** | **When to Enable** |
|-------------|------------|-------------------|-------------------|
| **Background Status Updates** | ✅ Always Active | LOW | Required for dashboard |
| **Integrated Monitoring System** | 🚫 Disabled (fast-boot) | MEDIUM | Production environments |
| **Pre-warming System** | 🚫 On-demand only | HIGH (brief) | Before bulk operations |
| **Audit Monitor** | 🚫 Disabled (fast-boot) | MEDIUM | During sitemap processing |

### Standalone Monitoring Tools
| **Script** | **Purpose** | **Usage** | **Resource Impact** |
|------------|-------------|-----------|-------------------|
| `monitor_sitemap.py` | Watch sitemap download progress | Manual execution | MEDIUM (300 API calls) |
| `monitor_full_process.py` | Complete workflow monitoring | Production validation | HIGH (30min monitoring) |
| `monitor_learning_start.py` | Learning process startup | Manual monitoring | MEDIUM (API polling) |
| `monitor_live_download.py` | Live download progress | Real-time monitoring | MEDIUM (active polling) |
| `audit_tile_data_extraction.py` | Data quality audit | Quality assurance | HIGH (full analysis) |
| `schema_expansion_summary.py` | Schema analysis report | Documentation | LOW (report only) |

### Process Usage Guidelines
```bash
# Fast startup (default - recommended)
python3 reboot_dashboard.py  # Monitoring disabled for speed

# Enable monitoring for production
# Edit reboot_dashboard.py line 2189: start_integrated_monitoring()

# Manual monitoring during operations
python3 monitor_sitemap.py           # Watch sitemap downloads
python3 monitor_full_process.py      # Full workflow validation
python3 audit_tile_data_extraction.py  # Quality audit

# On-demand system checks
python3 db_connection_test.py        # Database health
```

### Performance Optimizations
- **Fast-boot mode**: Monitoring disabled on startup for 5x faster initialization
- **On-demand activation**: Heavy processes only run when explicitly needed
- **Lightweight core**: Only essential WebSocket updates active by default
- **Manual tools**: All monitoring scripts require explicit execution

## 🆘 Troubleshooting Guides

### Available Troubleshooting Resources
- **`troubleshooting_guide_database_recovery.md`** - Database corruption recovery procedures
  - Vector database corruption resolution
  - Container replacement strategies  
  - Service restoration order
  - Prevention and monitoring tips

### Quick Troubleshooting Index
- **Database Issues**: See `troubleshooting_guide_database_recovery.md`
- **Container Problems**: Docker management commands and recovery
- **Service Connectivity**: Port conflicts and connection testing
- **Performance Issues**: Memory pressure and load optimization

### Emergency Recovery Commands
```bash
# Check all critical services
docker ps | grep -E "(postgres|crawl4ai)"

# Test database connections
python3 -c "import psycopg2; conn=psycopg2.connect(host='localhost', port=5432, database='postgres', user='postgres', password='postgres'); print('✅ relational_db OK')"

# Dashboard health check
curl -s http://127.0.0.1:8080/api/system/health
```

## 📋 Additional Documentation

For detailed issue resolution, see: [troubleshooting_guide.md](troubleshooting_guide.md)

For complete documentation, see: [README_expanded.md](README_expanded.md)