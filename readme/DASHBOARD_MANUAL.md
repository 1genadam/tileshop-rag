# 🖥️ Dashboard Manual

## TileShop Intelligence Platform - Complete Operations Guide

This manual covers all dashboard features and daily operations for the TileShop Intelligence Platform.

---

## 🚀 **Dashboard Overview**

The Admin Dashboard provides a unified control center for:
- **Service Management** - Start/stop/monitor all system services
- **Data Scraping** - Real-time scraping control and monitoring
- **Product Database** - Search, view, and manage product data
- **RAG Chat** - AI-powered product assistance
- **System Monitoring** - Health checks and performance metrics

**Dashboard URL**: http://127.0.0.1:8080

---

## 🔧 **Complete Infrastructure Management**

### **Unified Services Directory**
- **Single Control Panel**: Manage all scraper services from one interface
- **Docker Container Control**: Start/stop/restart individual or all dependencies  
- **Real-time Monitoring**: Live container status, CPU/memory usage
- **Service Health Checks**: Comprehensive system verification with one-click testing
- **One-click Setup**: "Start All Services" → ready to scrape
- **AI Assistant Terminal**: White-labeled AI assistant for infrastructure queries

### **Service Status Display**
| Service | Status Indicator | Function |
|---------|------------------|----------|
| **Docker Engine** | 🟢 Running / 🔴 Stopped | Container management |
| **PostgreSQL** | 🟢 Connected / 🔴 Disconnected | Primary database |
| **Supabase** | 🟢 Connected / 🔴 Disconnected | Vector database |
| **Crawl4AI** | 🟢 Active / 🔴 Inactive | Web scraping service |
| **Web Server** | 🟢 Running / 🔴 Stopped | Dashboard server |
| **LLM API** | 🟢 Connected / 🔴 Disconnected | Claude API |

---

## 🌐 **Universal URL Scraping System**

### **Dynamic Target URL Input**
- **Enter any website URL** for scraping
- **Automatic Sitemap Detection**: Real-time discovery and display of sitemaps
- **Pre-configured for Tileshop**: Defaults to https://www.tileshop.com  
- **Self-Healing Foundation**: Built for future expansion to any e-commerce site
- **URL Validation**: Real-time validation and feedback on entered URLs
- **Visual Sitemap Display**: Clean, readable sitemap URL presentation

### **Advanced Sitemap Download Status**
Multi-stage progress tracking with real-time WebSocket updates:
- **Download Progress**: Live byte-by-byte download monitoring with progress bars
- **XML Parsing Status**: Real-time parsing feedback and validation
- **URL Extraction**: Progressive URL extraction with running counts
- **Product Filtering**: Live filtering progress showing product URL identification
- **Results Summary**: Comprehensive completion statistics and file saving confirmation

### **Intelligent URL Filtering**
Automatically filters for product URLs (excludes samples, special pages)

**Current Filter Logic** (Tileshop-specific):
- ✅ **Include**: URLs containing `/products/` (main product pages)
- ❌ **Exclude**: Sample pages, special collections, non-product content
- 📊 **Result**: ~775 filtered product URLs from 4,700+ total sitemap entries

---

## 🔧 **Production Filtering Requirements**

For production deployment, the scraper will need **custom filter criteria** to handle:
- **Product-specific patterns**: Different e-commerce sites use various URL structures
- **Exclusion rules**: Skip promotional, sample, or non-product pages
- **Category filtering**: Optionally limit to specific product categories
- **Geographic filtering**: Handle regional or language-specific URLs
- **Custom regex patterns**: Site-specific filtering for optimal scraping efficiency

---

## 🎯 **Advanced Scraper Control**

### **Multiple Scraping Modes**

#### **1. Individual Product Scraping**
```bash
# Access via dashboard form
URL: https://www.tileshop.com/products/specific-product
Mode: Single Product
```

#### **2. Batch Processing**
```bash
# Multiple URLs at once
Mode: Batch Processing
Input: Upload file or paste URLs
```

#### **3. Sitemap Scraping**
```bash
# Full site crawl
Mode: Sitemap
Target: https://www.tileshop.com/sitemap.xml
```

#### **4. Resume Scraping**
```bash
# Continue interrupted scraping
Mode: Resume
Last Position: Automatic detection
```

### **Live Progress Monitoring**
- **Real-time Progress Bars**: Visual progress indicators
- **Statistics Display**: Items processed, success rate, errors
- **Time Estimates**: Remaining time and completion estimates
- **Error Management**: Live error logs and recovery options
- **Intelligent Dependencies**: Auto-check requirements before starting

---

## 🗄️ **Database Sync Management**

### **Real-time Sync Status**
- **Live Connection Monitoring**: Both n8n-postgres and Supabase
- **One-click Data Sync**: Fast bulk data transfer using PostgreSQL COPY commands
- **Data Comparison**: Compare source vs target counts and sync percentage
- **Force Full Sync**: Option for complete data refresh when needed
- **Sync Statistics**: Track sync history, timing, and success rates

### **Sync Operations**
```bash
# Access from dashboard
1. Navigate to "Database Sync" tab
2. Check connection status
3. Compare data counts
4. Click "Sync Data" for incremental sync
5. Use "Force Full Sync" if needed
```

---

## 📊 **Database Management**

### **Product Data Viewer**
- **Sortable Table**: Click column headers to sort
- **Search Functionality**: Real-time search across all fields
- **Filterable Data**: Filter by brand, category, price range
- **Price per Sq Ft Display**: Primary pricing metric
- **Enhanced Timestamps**: Full date and time for scraping timestamps
- **Export Tools**: CSV/JSON export with custom filters

### **Quick Statistics**
- **Live Counts**: Total products, recent additions
- **Averages**: Average prices, specifications
- **Recent Activity**: Latest scraping results
- **Multi-database Support**: Switch between n8n-postgres and Supabase

### **Data Export**
```bash
# Export options
1. Select data range
2. Choose format (CSV/JSON)
3. Apply filters if needed
4. Click "Export Data"
5. Download processed file
```

---

## 🤖 **RAG Chat Interface**

### **AI Product Assistant**
- **Natural Language Queries**: Ask about tiles in plain English
- **Claude 3.5 Sonnet Power**: Advanced analytical query processing
- **Full-text Search**: PostgreSQL-powered product searches
- **Visual Product Display**: High-quality product images in chat
- **Enhanced Markdown Support**: Rich formatting with images and links

### **Dual-Mode Processing**
1. **Search Queries**: PostgreSQL full-text search ("ceramic subway tiles")
2. **Analytical Queries**: Claude-powered analysis ("what's the lowest cost tile per sq ft")

### **Features**
- **Rich Product Display**: Product cards with images, prices, specifications
- **Per-Piece Pricing Support**: Displays accessories as "$X.XX/each" vs tiles as "$X.XX/sq ft"
- **Real-time Database Access**: Direct PostgreSQL queries for instant results
- **Smart Query Detection**: Automatically detects analytical vs. search intent
- **Suggestion System**: Pre-built query examples for common tile searches

### **Usage Examples**
```bash
# Search queries
"Show me subway tiles"
"Find ceramic tiles under $5 per sq ft"
"What brands do you carry?"

# Analytical queries
"What's the most expensive tile?"
"Compare prices between brands"
"Show me installation accessories"
```

---

## ✅ **Claude API Configuration Status**

### **Current Configuration**
- **🔑 API Key**: Updated and configured in `.env` file (`ANTHROPIC_API_KEY`)
- **🆕 Current Key**: Configured in .env (secure storage)
- **📚 RAG Library**: `anthropic>=0.20.0` installed and functional
- **🧠 Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **🔄 Auto-Load**: Dashboard automatically loads API key on startup
- **💾 Persistence**: Configuration persists across sessions

### **Integration Points**
- **🤖 AI Assistant**: Uses same API key for infrastructure management queries
- **🔄 RAG Chat**: Uses same API key for product analysis queries with LLM-first priority
- **✅ Frontend Integration**: JavaScript event listeners properly initialized
- **✅ Database Integration**: Supabase container connectivity resolved
- **🔄 Fallback System**: Automatic fallback to search when Claude API unavailable

---

## 📈 **System Monitoring**

### **Network Status**
- **app-network Connectivity**: Monitor Docker network health
- **Service Interconnection**: Track service-to-service communication
- **External API Status**: Monitor Claude API and other external services

### **Performance Metrics**
- **Scrape Speeds**: Products per minute, success rates
- **Resource Usage**: CPU, memory, storage utilization
- **Response Times**: Dashboard performance, query speeds
- **Error Rates**: Track and monitor system errors

### **Configuration Management**
- **Update Settings**: Change configuration through UI
- **Environment Variables**: Modify system settings
- **Service Configuration**: Update service parameters
- **Log Streaming**: Real-time logs from all components

---

## 🔄 **Proper Dashboard Reboot Protocol**

### **Important Startup Notes**
- ✅ **Environment**: Dashboard uses `/Users/robertsher/Projects/autogen_env` virtual environment
- 🧹 **Cache Clearing Required**: Browser cache must be cleared after code changes for UI updates to display

### **Standard Reboot Process**
```bash
# 1. Stop current dashboard
pkill -f dashboard_app.py

# 2. Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# 3. Start dashboard
python3 dashboard_app.py

# 4. Clear browser cache (important!)
# Chrome: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
# Firefox: Cmd+Shift+R (Mac) or Ctrl+F5 (Windows)
```

### **Fast Reboot (Development)**
```bash
# Use the fast reboot script
./fast_reboot.sh
```

### **Full System Reboot**
```bash
# Complete system restart
./reboot_dashboard.sh
```

---

## 🚨 **Troubleshooting Dashboard Issues**

### **Dashboard Won't Start**
```bash
# Check for port conflicts
lsof -i :8080

# Kill conflicting processes
pkill -f dashboard_app.py

# Verify environment
source /Users/robertsher/Projects/autogen_env/bin/activate
python3 -c "import flask; print('Flask OK')"
```

### **Services Not Connecting**
```bash
# Check Docker services
docker ps

# Restart Docker containers
docker-compose down && docker-compose up -d

# Test service connectivity
curl -s http://localhost:11235/health  # Crawl4AI
curl -s http://localhost:5432  # PostgreSQL
```

### **Claude API Issues**
```bash
# Check API key configuration
grep ANTHROPIC_API_KEY .env

# Test API connectivity
python3 -c "import os; from anthropic import Anthropic; print('API OK')"
```

### **Database Connection Problems**
```bash
# Test PostgreSQL connection
python3 -c "import psycopg2; print('PostgreSQL OK')"

# Test Supabase connection
python3 -c "from dashboard_app import test_supabase; test_supabase()"
```

---

## 💡 **Best Practices**

### **Daily Operations**
1. **Check Service Status** before starting any operations
2. **Monitor Resource Usage** during heavy scraping
3. **Regular Database Syncs** to keep data current
4. **Clear Browser Cache** after system updates

### **Performance Optimization**
1. **Use Batch Processing** for multiple products
2. **Schedule Heavy Operations** during off-peak hours
3. **Monitor Progress** and stop/restart if needed
4. **Regular Maintenance** of database and logs

### **Data Management**
1. **Export Data Regularly** for backup
2. **Monitor Data Quality** through statistics
3. **Clean Up Old Data** periodically
4. **Validate Scraping Results** before processing

---

## 🎯 **Advanced Features**

### **Webhook Integration**
- **Real-time Notifications**: Get alerts for scraping completion
- **Status Updates**: Receive status changes via webhook
- **Error Alerts**: Immediate notification of system issues

### **API Access**
- **REST API**: Programmatic access to dashboard functions
- **Webhook Events**: Subscribe to system events
- **Data Export API**: Automated data retrieval

### **Custom Filters**
- **Product Filtering**: Create custom product filters
- **Site-specific Rules**: Configure rules for different sites
- **Exclusion Patterns**: Set up exclusion rules for specific content

---

*For deployment information, see [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)*
*For troubleshooting, see [QUICK_FIXES.md](QUICK_FIXES.md) and [SYSTEM_DIAGNOSTICS.md](SYSTEM_DIAGNOSTICS.md)*
*For quick start, see [QUICK_START.md](QUICK_START.md)*