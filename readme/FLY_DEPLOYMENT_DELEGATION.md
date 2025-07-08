# Tileshop RAG System - Fly.io Deployment Delegation Document

## 🎯 **Mission Overview**
Deploy the Tileshop RAG Intelligence Platform to Fly.io cloud infrastructure for production hosting, based on proven architecture from n8n_dfy_autopilot system.

## 📋 **System Analysis Complete**

### **Current Architecture (Local)**
```
🖥️  Tileshop RAG Local Environment:
├── Flask Dashboard (reboot_dashboard.py) - Port 8080
├── PostgreSQL Database (product_data table + vectors)
├── curl_scraper.py (Production data acquisition - 100% reliable)
├── Enhanced Specification Extractor (Auto-expanding schema)
├── Docker Integration (crawl4ai browser service)
├── WebSocket Real-time Updates (Flask-SocketIO)
├── Claude AI Integration (RAG queries)
├── Fast-boot Performance Optimizations
└── Comprehensive Admin Dashboard
```

### **Target Fly.io Architecture**
```
☁️  Fly.io Production Environment:
├── Docker Container (Python 3.11 + Flask + Gunicorn)
├── Fly.io PostgreSQL (managed database with vector extensions)
├── Persistent Volumes (scraped data + logs)
├── Auto-scaling Machines (1-3 instances)
├── Custom Domain + SSL
├── Health Monitoring (Flask health endpoint)
└── CI/CD Pipeline (automated deployments)
```

## 🤝 **Multi-Agent Deployment Coordination**

### **Agent Assignment Strategy**

#### **Agent 1 (Primary - Infrastructure & Backend)**
**Responsibility**: Core system deployment and database management
**Tasks**:
- [ ] Create Dockerfile for Python Flask application
- [ ] Configure fly.toml with proper resource allocation
- [ ] Set up Fly.io PostgreSQL with vector extensions
- [ ] Deploy Flask dashboard with Gunicorn WSGI server
- [ ] Configure persistent volumes for scraped data
- [ ] Implement health checks and monitoring
- [ ] Set up environment variables and secrets
- [ ] Test core API endpoints and dashboard functionality

**Deliverables**:
- `Dockerfile` - Multi-stage Python container build
- `fly.toml` - Fly.io configuration with auto-scaling
- `docker-compose.yml` - Local testing environment
- Production environment variables documentation

#### **Agent 2 (Data & Processing)**
**Responsibility**: Data acquisition system and performance optimization
**Tasks**:
- [ ] Deploy curl_scraper.py with proper dependencies
- [ ] Configure crawl4ai Docker service integration
- [ ] Set up enhanced specification extractor
- [ ] Implement data migration from local to cloud database
- [ ] Configure background processing for large scraping jobs
- [ ] Optimize database queries for cloud performance
- [ ] Set up automated data quality monitoring
- [ ] Configure schema auto-scaling for production

**Deliverables**:
- Data migration scripts
- Production scraping configuration
- Performance optimization documentation
- Data quality monitoring setup

#### **Agent 3 (Frontend & Operations)**
**Responsibility**: Dashboard optimization and operational readiness
**Tasks**:
- [ ] Optimize dashboard templates for production
- [ ] Configure static asset serving
- [ ] Set up WebSocket support for real-time updates
- [ ] Implement production logging and error handling
- [ ] Configure backup and recovery procedures
- [ ] Set up monitoring and alerting
- [ ] Create operational runbooks
- [ ] Test end-to-end user workflows

**Deliverables**:
- Production-ready dashboard templates
- Operational documentation and runbooks
- Monitoring and alerting configuration
- User workflow testing results

## 📊 **Technical Specifications**

### **Resource Requirements** (Based on n8n_dfy_autopilot)
```toml
[vm]
  cpu_kind = "shared"
  cpus = 2
  memory = "4gb"

[[mounts]]
  source = "tileshop_data"
  destination = "/app/storage"
  initial_size = "50gb"
```

### **Key Dependencies**
```python
# From requirements.txt analysis
psycopg2-binary==2.9.10    # PostgreSQL adapter
flask>=3.0.0               # Web framework
flask-socketio>=5.5.0      # Real-time updates
gunicorn>=21.0.0           # WSGI server
anthropic>=0.20.0          # Claude AI integration
docker>=7.0.0              # Container management
requests==2.32.3           # HTTP client
beautifulsoup4             # HTML parsing
lxml                       # XML/HTML processing
```

### **Critical Ports & Services**
- **Main Application**: Port 8080 (Flask dashboard)
- **Database**: Fly.io managed PostgreSQL
- **Health Check**: GET `/health` endpoint
- **WebSocket**: Real-time dashboard updates

## 🔧 **Deployment Configuration Files Needed**

### **Priority 1 (Infrastructure)**
1. `Dockerfile` - Python 3.11 Alpine base with Flask/Gunicorn
2. `fly.toml` - Fly.io app configuration with auto-scaling
3. `.dockerignore` - Optimize build context
4. `gunicorn.conf.py` - Production WSGI configuration

### **Priority 2 (Application)**
5. `docker-compose.yml` - Local testing environment
6. `migrate.py` - Database migration script for production
7. `health_check.py` - Comprehensive health monitoring
8. `production_config.py` - Environment-specific settings

### **Priority 3 (Operations)**
9. `backup_script.sh` - Automated backup procedures
10. `deploy.sh` - Deployment automation script
11. `monitoring.py` - Performance and error monitoring
12. `rollback.sh` - Emergency rollback procedures

## 🚀 **Deployment Phases**

### **Phase 1: Infrastructure Setup** (Agent 1 Lead)
- [ ] Create Fly.io app and PostgreSQL database
- [ ] Configure basic Docker container
- [ ] Deploy minimal Flask application
- [ ] Verify connectivity and health checks

### **Phase 2: Core System Migration** (Agent 2 Lead)
- [ ] Deploy curl_scraper.py and dependencies
- [ ] Migrate existing database schema and data
- [ ] Configure enhanced specification extractor
- [ ] Test data acquisition pipeline

### **Phase 3: Dashboard & UI** (Agent 3 Lead)
- [ ] Deploy complete dashboard with real-time features
- [ ] Configure WebSocket support
- [ ] Implement production logging
- [ ] Perform end-to-end testing

### **Phase 4: Optimization & Monitoring** (All Agents)
- [ ] Performance tuning and resource optimization
- [ ] Set up comprehensive monitoring
- [ ] Create operational documentation
- [ ] Conduct load testing and validation

## 📋 **Coordination Protocol**

### **Communication Standards**
- **Status Updates**: Each agent updates this document with progress
- **Blockers**: Immediate notification in shared documentation
- **Testing**: Cross-agent validation of integrations
- **Handoffs**: Clear documentation of completed components

### **File Naming Convention**
- `AGENT1_[component]_[status].md` - Infrastructure documentation
- `AGENT2_[component]_[status].md` - Data pipeline documentation  
- `AGENT3_[component]_[status].md` - Frontend/ops documentation

### **Testing Checkpoints**
- [ ] **Checkpoint 1**: Basic Flask app deployed and accessible
- [ ] **Checkpoint 2**: Database connected with sample data
- [ ] **Checkpoint 3**: Scraping pipeline functional
- [ ] **Checkpoint 4**: Dashboard fully operational
- [ ] **Checkpoint 5**: Production-ready with monitoring

## 🔍 **Success Criteria**

### **Functional Requirements**
- ✅ Dashboard accessible at production URL
- ✅ Database migrations completed successfully
- ✅ Data acquisition (curl_scraper.py) working reliably
- ✅ Real-time updates via WebSocket functional
- ✅ Schema auto-scaling operational
- ✅ Performance optimizations active

### **Performance Requirements**
- ✅ Dashboard loads in < 3 seconds
- ✅ API responses in < 2 seconds
- ✅ Database queries optimized for cloud latency
- ✅ Auto-scaling triggers properly configured
- ✅ Resource utilization within budget

### **Operational Requirements**
- ✅ Health monitoring and alerting active
- ✅ Backup and recovery procedures tested
- ✅ Deployment automation functional
- ✅ Rollback procedures documented and tested
- ✅ Production documentation complete

## 📚 **Reference Architecture**
Based on proven deployment from `/Users/robertsher/Projects/n8n_dfy_autopilot/` which successfully deployed a similar Python application with:
- Multi-agent coordination
- PostgreSQL + Redis
- Docker containerization
- Auto-scaling configuration
- Production monitoring

## ⚠️ **IMPORTANT: Deployment Gate**
**DO NOT BEGIN DEPLOYMENT** until explicit authorization from user. This document serves as preparation and coordination framework only.

---

## 📝 **Agent Status Tracking**

### **Agent 1 (Infrastructure & Backend)**
- Status: **READY FOR ASSIGNMENT**
- Last Update: 
- Current Task: 
- Next Task: 
- Blockers: 

### **Agent 2 (Data & Processing)**
- Status: **READY FOR ASSIGNMENT**
- Last Update: 
- Current Task: 
- Next Task: 
- Blockers: 

### **Agent 3 (Frontend & Operations)**
- Status: **READY FOR ASSIGNMENT**
- Last Update: 
- Current Task: 
- Next Task: 
- Blockers: