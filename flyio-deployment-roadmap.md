# Fly.io Independent Server Deployment Roadmap
## Tileshop RAG Intelligence Platform - Cloud Migration Strategy

### Executive Summary

This roadmap outlines the complete migration of the Tileshop RAG Intelligence Platform from local development to a fully independent Fly.io server deployment. The current system relies on local Docker containers for core services (PostgreSQL, Supabase, Crawl4AI), which must be replaced with cloud-native solutions for true production readiness.

**Current State**: Dashboard deployed to Fly.io but dependent on local services  
**Target State**: Fully independent cloud deployment with integrated database and crawling services  
**Timeline**: 4-6 weeks for complete migration  
**Investment**: $200-400/month operational costs  

---

## Current Architecture Analysis

### ✅ **Already Deployed to Fly.io**
- **Web Application**: Dashboard and RAG chat interface
- **Docker Configuration**: Multi-stage Dockerfile with Poetry
- **Health Monitoring**: `/api/system/health` endpoint
- **Resource Allocation**: 2GB RAM, 1 shared CPU
- **Auto-scaling**: Machine start/stop capabilities

### ❌ **Local Dependencies (Blocking Independent Function)**
- **PostgreSQL Database** (relational_db): Currently runs in local Docker container
- **Supabase Stack** (vector_db): Full suite of local containers for vector operations
- **Crawl4AI Service**: Web scraping service running locally on port 11235
- **Sitemap Storage**: Local JSON files with acquisition progress
- **Recovery Data**: Local checkpoint files for scraping recovery

### 🔧 **Identified Gaps for Independent Operation**
1. **Database Services**: No cloud PostgreSQL or vector database
2. **Web Scraping Infrastructure**: No cloud-based crawling capability
3. **Data Persistence**: No persistent volume strategy for sitemaps/logs
4. **Service Discovery**: Hard-coded localhost URLs throughout codebase
5. **Environment Configuration**: Mixed local/cloud environment variables

---

## Phase 1: Database Migration & Cloud Infrastructure (Weeks 1-2)

### 1.1 PostgreSQL Cloud Migration
**Objective**: Replace local PostgreSQL with managed cloud database

**Implementation Options:**
- **Option A**: Fly.io PostgreSQL Cluster (Recommended)
  - Native integration with Fly.io platform
  - Automatic backups and scaling
  - Cost: ~$30-50/month for development tier
  
- **Option B**: External managed service (Neon, Supabase Cloud, RDS)
  - Higher performance and reliability
  - More expensive but production-ready
  - Cost: ~$50-100/month

**Required Changes:**
```python
# modules/db_manager.py - Update connection configuration
self.relational_db_config = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'database': os.getenv('DATABASE_NAME', 'postgres'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD')
}
```

**Deployment Steps:**
1. **Create Fly.io PostgreSQL cluster**: `fly postgres create`
2. **Migrate existing data** using pg_dump/pg_restore
3. **Update environment variables** in Fly.io secrets
4. **Test database connectivity** from deployed application

### 1.2 Vector Database Migration
**Objective**: Replace local Supabase containers with cloud vector database

**Implementation Options:**
- **Option A**: Supabase Cloud (Recommended for MVP)
  - Managed vector database with full API
  - Built-in authentication and real-time features
  - Cost: ~$25-50/month for Pro tier
  
- **Option B**: Pinecone Vector Database
  - Specialized vector database for AI applications
  - Better performance for large-scale vector operations
  - Cost: ~$70-100/month for production tier

**Required Changes:**
```python
# modules/db_manager.py - Add cloud vector database support
def get_supabase_client(self):
    """Get Supabase cloud client instead of docker exec"""
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    return create_client(url, key)
```

### 1.3 Persistent Volume Strategy
**Objective**: Implement proper data persistence for sitemaps and logs

**Implementation:**
- **Fly.io Volumes**: Create persistent volumes for application data
- **Volume Structure**:
  ```
  /app/data/
  ├── sitemaps/           # Sitemap JSON files
  ├── recovery/           # Recovery checkpoint files
  ├── logs/              # Application logs
  └── cache/             # Temporary processing cache
  ```

**Required Changes:**
```toml
# fly.toml - Add volume configuration
[[mounts]]
  source = "tileshop_data"
  destination = "/app/data"
  
[[mounts]]
  source = "tileshop_logs"
  destination = "/app/logs"
```

---

## Phase 2: Web Scraping Infrastructure (Weeks 2-3)

### 2.1 Crawl4AI Cloud Deployment
**Objective**: Deploy independent Crawl4AI service on Fly.io

**Implementation Strategy:**
- **Dedicated Fly.io App** for Crawl4AI service
- **Internal networking** between dashboard and crawler
- **Shared authentication** using Fly.io service discovery

**Required Files:**
```dockerfile
# crawler/Dockerfile - Specialized Crawl4AI container
FROM unclecode/crawl4ai:browser

ENV CRAWL4AI_API_TOKEN=tileshop_production
EXPOSE 11235

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "11235"]
```

```toml
# crawler/fly.toml - Crawler service configuration
app = "tileshop-crawler"

[env]
  PORT = "11235"
  CRAWL4AI_API_TOKEN = "tileshop_production"

[[vm]]
  memory = "4gb"  # More memory for browser automation
  cpu_kind = "performance"
  cpus = 2
```

**Service Discovery Implementation:**
```python
# modules/intelligence_manager.py - Dynamic crawler URL
def get_crawler_url(self):
    """Get crawler URL based on environment"""
    if os.getenv('FLY_APP_NAME'):
        # Production: Use Fly.io internal networking
        return "http://tileshop-crawler.internal:11235"
    else:
        # Development: Use localhost
        return "http://localhost:11235"
```

### 2.2 Alternative Scraping Solutions
**Objective**: Reduce infrastructure complexity with managed services

**Option A**: Replace Crawl4AI with cloud APIs
- **ScrapingBee**: Managed web scraping with JavaScript rendering
- **Apify**: Cloud platform for web scraping automation
- **Browserless**: Headless browser as a service

**Option B**: Serverless scraping functions
- **Fly.io Machines**: On-demand scraping containers
- **AWS Lambda**: Event-driven scraping functions
- **Vercel Functions**: Edge-based scraping capabilities

**Cost Comparison:**
- **Self-hosted Crawl4AI**: ~$50-100/month (compute costs)
- **Managed APIs**: ~$0.002-0.01 per request (~$100-500/month for heavy usage)
- **Serverless**: ~$0.001 per execution (~$50-200/month)

---

## Phase 3: Application Configuration & Environment Management (Week 3-4)

### 3.1 Environment Variable Migration
**Objective**: Centralize all environment configuration for cloud deployment

**Required Environment Variables:**
```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# AI Services
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-... (if needed for future features)

# Web Scraping
CRAWLER_URL=http://tileshop-crawler.internal:11235
CRAWLER_TOKEN=tileshop_production

# Application Configuration
FLASK_ENV=production
DEBUG=false
PORT=8080
DATA_PATH=/app/data
LOG_LEVEL=INFO
```

**Secrets Management:**
```bash
# Set production secrets
fly secrets set DATABASE_URL="postgresql://..."
fly secrets set SUPABASE_URL="https://..."
fly secrets set ANTHROPIC_API_KEY="sk-ant-..."
fly secrets set CRAWLER_TOKEN="tileshop_production"
```

### 3.2 Service Health Check Updates
**Objective**: Update health checks to verify cloud service connectivity

**Enhanced Health Checks:**
```python
# modules/docker_manager.py - Cloud service health checks
def _health_check_cloud_database(self):
    """Health check for cloud PostgreSQL"""
    try:
        db_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {
            'healthy': True,
            'message': f'Cloud PostgreSQL connected: {version}'
        }
    except Exception as e:
        return {
            'healthy': False,
            'message': f'Cloud database connection failed: {str(e)}'
        }

def _health_check_cloud_crawler(self):
    """Health check for cloud Crawl4AI service"""
    try:
        crawler_url = self.get_crawler_url()
        response = requests.get(f'{crawler_url}/health', timeout=10)
        if response.status_code == 200:
            return {
                'healthy': True,
                'message': f'Crawler service accessible at {crawler_url}'
            }
    except Exception as e:
        return {
            'healthy': False,
            'message': f'Crawler service check failed: {str(e)}'
        }
```

### 3.3 Monitoring & Logging Strategy
**Objective**: Implement comprehensive monitoring for production deployment

**Logging Configuration:**
```python
# Configure structured logging for cloud deployment
import logging
import json

class CloudLogger:
    def __init__(self):
        self.logger = logging.getLogger('tileshop_rag')
        handler = logging.StreamHandler()
        
        # JSON formatter for better log aggregation
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
```

**Health Monitoring Dashboard:**
```python
# Add comprehensive health endpoint
@app.route('/api/system/detailed-health')
def detailed_health():
    """Comprehensive health check for all cloud services"""
    health_status = {
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': check_database_health(),
            'vector_db': check_vector_db_health(),
            'crawler': check_crawler_health(),
            'ai_services': check_ai_services_health(),
            'storage': check_storage_health()
        }
    }
    
    all_healthy = all(
        service.get('healthy', False) 
        for service in health_status['services'].values()
    )
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'details': health_status
    }), 200 if all_healthy else 503
```

---

## Phase 4: Testing & Production Readiness (Week 4-5)

### 4.1 Integration Testing Strategy
**Objective**: Comprehensive testing of cloud-deployed system

**Test Categories:**

1. **Database Integration Tests**
   ```python
   def test_cloud_database_connection():
       """Test cloud PostgreSQL connectivity"""
       db_manager = DatabaseManager()
       result = db_manager.test_connections()
       assert result['relational_db']['connected'] is True
   
   def test_vector_database_operations():
       """Test Supabase cloud operations"""
       # Test vector storage and retrieval
       # Test real-time subscriptions
       # Test authentication
   ```

2. **Scraping Service Tests**
   ```python
   def test_cloud_crawler_availability():
       """Test cloud Crawl4AI service"""
       response = requests.get(f'{CRAWLER_URL}/health')
       assert response.status_code == 200
   
   def test_end_to_end_scraping():
       """Test complete scraping workflow"""
       # Test sitemap download
       # Test product page scraping
       # Test data storage in cloud database
   ```

3. **RAG System Tests**
   ```python
   def test_rag_chat_functionality():
       """Test RAG chat with cloud services"""
       # Test Claude API integration
       # Test database query generation
       # Test response formatting
   ```

### 4.2 Performance Optimization
**Objective**: Ensure production-level performance

**Database Connection Pooling:**
```python
# modules/db_manager.py - Connection pooling for cloud database
from psycopg2 import pool

class DatabaseManager:
    def __init__(self):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            host=os.getenv('DATABASE_HOST'),
            port=os.getenv('DATABASE_PORT')
        )
```

**Caching Strategy:**
```python
# Add Redis for caching (optional)
import redis

class CacheManager:
    def __init__(self):
        redis_url = os.getenv('REDIS_URL')
        self.redis_client = redis.from_url(redis_url) if redis_url else None
    
    def cache_sitemap_data(self, sitemap_data, ttl=3600):
        """Cache sitemap data to reduce database load"""
        if self.redis_client:
            self.redis_client.setex(
                'sitemap_cache', 
                ttl, 
                json.dumps(sitemap_data)
            )
```

### 4.3 Security Hardening
**Objective**: Implement production security standards

**Security Measures:**
1. **API Authentication**: Rate limiting and token validation
2. **Database Security**: SSL connections and access control
3. **Secrets Management**: Proper rotation and access policies
4. **Network Security**: Private networks and firewall rules

```python
# Security middleware
from functools import wraps
import time

def rate_limit(max_requests=100, window=3600):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Implement rate limiting logic
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/api/acquisition/start', methods=['POST'])
@rate_limit(max_requests=10, window=3600)  # Limit scraping starts
def start_acquisition():
    """Rate-limited scraping endpoint"""
    pass
```

---

## Phase 5: Migration Execution & Monitoring (Week 5-6)

### 5.1 Migration Execution Plan
**Objective**: Execute migration with minimal downtime

**Migration Steps:**

1. **Database Migration (Day 1-2)**
   ```bash
   # Create cloud databases
   fly postgres create tileshop-postgres
   
   # Export local data
   pg_dump -h localhost -p 5432 -U postgres postgres > tileshop_backup.sql
   
   # Import to cloud
   psql $DATABASE_URL < tileshop_backup.sql
   
   # Verify data integrity
   python verify_migration.py
   ```

2. **Service Deployment (Day 3-4)**
   ```bash
   # Deploy crawler service
   cd crawler/
   fly deploy
   
   # Update main application
   fly secrets set DATABASE_URL=$CLOUD_DATABASE_URL
   fly secrets set CRAWLER_URL=http://tileshop-crawler.internal:11235
   fly deploy
   ```

3. **Cutover & Testing (Day 5)**
   ```bash
   # Scale up cloud deployment
   fly scale count 2
   
   # Run comprehensive tests
   python test_production_deployment.py
   
   # Monitor health checks
   fly logs
   ```

### 5.2 Post-Migration Monitoring
**Objective**: Ensure stable operation after migration

**Monitoring Checklist:**
- [ ] **Database Performance**: Query response times <100ms
- [ ] **Scraping Success Rate**: >95% success rate for product pages
- [ ] **RAG Response Time**: <3 seconds for complex queries
- [ ] **Error Rates**: <1% application errors
- [ ] **Resource Utilization**: <80% CPU/memory usage

**Monitoring Tools:**
```python
# Custom monitoring dashboard
@app.route('/admin/monitoring')
def monitoring_dashboard():
    """Internal monitoring dashboard"""
    metrics = {
        'database_connections': get_db_connection_count(),
        'scraping_queue_size': get_scraping_queue_size(),
        'error_rate_24h': get_error_rate(),
        'response_time_p95': get_response_time_percentile(95),
        'active_users': get_active_user_count()
    }
    return render_template('monitoring.html', metrics=metrics)
```

---

## Cost Analysis & Resource Planning

### Monthly Operational Costs

**Infrastructure Costs:**
- **Fly.io Web App**: $30-50/month (2GB RAM, 1 CPU)
- **PostgreSQL Database**: $30-50/month (managed service)
- **Vector Database (Supabase)**: $25-50/month (Pro tier)
- **Crawl4AI Service**: $50-100/month (4GB RAM, 2 CPU)
- **Storage & Bandwidth**: $10-20/month
- **Monitoring & Logs**: $10-20/month

**Total Estimated Cost: $155-290/month**

**Alternative Cost-Optimized Configuration:**
- **Single Fly.io App**: $50-70/month (larger instance)
- **External PostgreSQL**: $25-40/month (Neon, PlanetScale)
- **Managed Scraping API**: $100-200/month (usage-based)
- **Total: $175-310/month**

### Performance Expectations

**Scalability Targets:**
- **Concurrent Users**: 50-100 simultaneous dashboard users
- **Scraping Throughput**: 1,000-2,000 products/day
- **RAG Chat Volume**: 500-1,000 queries/day
- **Database Load**: 10,000-50,000 queries/day

**SLA Commitments:**
- **Uptime**: 99.5% availability
- **Response Time**: <2 seconds for dashboard, <5 seconds for RAG
- **Data Durability**: 99.999% with automated backups

---

## Risk Assessment & Mitigation

### High-Risk Items
1. **Database Migration Complexity**
   - **Risk**: Data loss or corruption during migration
   - **Mitigation**: Multiple backups, staged migration, rollback plan

2. **Crawl4AI Service Reliability**
   - **Risk**: Browser automation failures in cloud environment
   - **Mitigation**: Alternative scraping solutions, robust error handling

3. **Cost Overruns**
   - **Risk**: Unexpected cloud costs from high usage
   - **Mitigation**: Usage monitoring, cost alerts, resource limits

### Medium-Risk Items
1. **Performance Degradation**
   - **Risk**: Slower response times compared to local deployment
   - **Mitigation**: Performance testing, caching strategies, optimization

2. **Service Dependencies**
   - **Risk**: Vendor lock-in or service availability issues
   - **Mitigation**: Multi-cloud strategy, service abstractions

### Low-Risk Items
1. **Security Vulnerabilities**
   - **Risk**: Cloud deployment exposes new attack vectors
   - **Mitigation**: Security audits, regular updates, monitoring

---

## Success Criteria & Acceptance Testing

### Technical Acceptance Criteria
- [ ] **Zero Local Dependencies**: All services running in cloud
- [ ] **Health Checks Pass**: All 8 services showing healthy status
- [ ] **Data Persistence**: Scraping progress survives restarts
- [ ] **Performance Targets**: Response times within SLA
- [ ] **Monitoring Coverage**: Comprehensive visibility into all services

### Business Acceptance Criteria
- [ ] **Feature Parity**: All dashboard and RAG functionality working
- [ ] **Data Integrity**: No loss of existing product data or sitemap progress
- [ ] **User Experience**: No degradation in user interface or response times
- [ ] **Cost Efficiency**: Monthly costs within approved budget
- [ ] **Scalability**: System handles expected user load

### Rollback Plan
If migration fails or performance is unacceptable:

1. **Immediate Rollback** (1-2 hours)
   - Restore local environment
   - Point DNS back to local development
   - Resume operations with existing setup

2. **Data Recovery** (2-4 hours)
   - Restore database from pre-migration backup
   - Verify data integrity and completeness
   - Resume scraping operations

3. **Issue Analysis** (1-2 days)
   - Identify root cause of migration failure
   - Develop remediation plan
   - Schedule retry with fixes

---

## Implementation Timeline

### Week 1: Database Infrastructure
- **Days 1-2**: Set up cloud PostgreSQL and Supabase
- **Days 3-4**: Migrate existing data and test connectivity
- **Days 5-7**: Update application configuration and test database operations

### Week 2: Crawler Service Migration
- **Days 1-3**: Deploy Crawl4AI service to Fly.io
- **Days 4-5**: Implement service discovery and authentication
- **Days 6-7**: Test end-to-end scraping workflow

### Week 3: Application Configuration
- **Days 1-2**: Update environment variables and secrets
- **Days 3-4**: Implement cloud health checks and monitoring
- **Days 5-7**: Performance testing and optimization

### Week 4: Integration Testing
- **Days 1-3**: Comprehensive testing of all features
- **Days 4-5**: Security hardening and compliance
- **Days 6-7**: Performance optimization and scaling tests

### Week 5: Production Migration
- **Days 1-2**: Execute database migration
- **Days 3-4**: Deploy all services to production
- **Days 5-7**: Monitor and stabilize deployment

### Week 6: Optimization & Documentation
- **Days 1-3**: Performance monitoring and tuning
- **Days 4-5**: Update documentation and procedures
- **Days 6-7**: Team training and knowledge transfer

---

## Next Steps

### Immediate Actions (This Week)
1. **Create Fly.io PostgreSQL cluster** and test connectivity
2. **Set up Supabase cloud project** with vector database configuration
3. **Update local environment** to support cloud/local dual configuration
4. **Create migration scripts** for database export/import

### Short-term Goals (Next 2 Weeks)
1. **Deploy crawler service** to separate Fly.io application
2. **Implement service discovery** for dynamic URL configuration
3. **Test basic functionality** with cloud databases
4. **Create monitoring dashboard** for health checks

### Long-term Objectives (Next Month)
1. **Complete production migration** with zero local dependencies
2. **Implement comprehensive monitoring** and alerting
3. **Optimize performance** for production workloads
4. **Document procedures** for maintenance and scaling

This roadmap provides a comprehensive path to achieving a fully independent Fly.io deployment while maintaining system reliability and performance. The staged approach minimizes risk while ensuring all dependencies are properly addressed.