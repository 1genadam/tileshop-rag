# Tileshop RAG System - Architecture Documentation

## System Overview

The Tileshop RAG (Retrieval-Augmented Generation) system is a comprehensive intelligence platform that combines web scraping, database management, vector search, and AI-powered analysis capabilities. The system is built with a microservices architecture and features a unified diagnostic framework for monitoring and management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    TILESHOP RAG SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   Web Dashboard │    │   API Gateway   │    │   LLM API   │  │
│  │   (Flask/HTML)  │    │   (Kong/HTTP)   │    │  (Claude)   │  │
│  │   Port: 8080    │    │   Port: 8000    │    │   Remote    │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│           │                       │                       │     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Docker Engine  │    │  Web Scraper    │    │  Crawler    │  │
│  │  (Container     │    │  (Intelligence  │    │  (Crawl4AI) │  │
│  │   Management)   │    │   Manager)      │    │ Port: 11235 │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│           │                       │                       │     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │ Relational DB   │    │   Vector DB     │    │ Sync Manager│  │
│  │ (PostgreSQL)    │    │ (PostgreSQL +   │    │ (Database   │  │
│  │  Port: 5432     │    │  pgvector)      │    │  Sync)      │  │
│  │                 │    │  Port: 5433     │    │             │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    DIAGNOSTIC FRAMEWORK                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Microservices  │    │ Runtime Environ │    │ Pre-warming │  │
│  │   (6 services)  │    │  (4 services)   │    │ (7 services)│  │
│  │                 │    │                 │    │             │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Web Dashboard (`reboot_dashboard.py`)

**Purpose**: Central management interface for the entire system
**Technology**: Flask, SocketIO, HTML/CSS/JavaScript
**Port**: 8080

**Features**:
- Unified service monitoring dashboard
- Real-time status updates
- Health checks for all 17 services
- Logs and debug information access
- Data acquisition control interface
- AI-powered customer service chat

**Key Modules**:
- Service diagnostic framework integration
- Docker container management
- Database connection monitoring
- RAG system interface

### 2. Database Layer

#### Relational Database (`relational_db`)
**Technology**: PostgreSQL
**Port**: 5432
**Purpose**: Primary data storage for structured information

**Schema**:
```sql
-- Product catalog
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL,
    category VARCHAR(100),
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scraped content
CREATE TABLE scraped_content (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500),
    title TEXT,
    content TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System logs
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100),
    log_level VARCHAR(20),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Vector Database (`vector_db`)
**Technology**: PostgreSQL + pgvector extension
**Port**: 5433
**Purpose**: Semantic search and embeddings storage

**Schema**:
```sql
-- Vector embeddings
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES scraped_content(id),
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER,
    chunk_text TEXT,
    chunk_embedding vector(1536),
    chunk_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Intelligence Layer

#### RAG Manager (`modules/rag_manager.py`)
**Purpose**: Retrieval-Augmented Generation system
**Features**:
- Claude API integration
- Vector similarity search
- Context-aware responses
- Knowledge base management

**Components**:
- **Simple RAG**: Basic question-answering
- **Knowledge Base**: File-based information storage
- **PDF Processor**: Document parsing and chunking
- **Embedding Generator**: Vector representation creation

#### Intelligence Manager (`modules/intelligence_manager.py`)
**Purpose**: Web scraping and content processing
**Features**:
- Multi-threaded scraping
- Content extraction and cleaning
- Progress tracking with callbacks
- Error handling and retry logic

### 4. Container Services

#### Crawler Service (`crawler`)
**Technology**: Crawl4AI
**Port**: 11235
**Purpose**: Browser-based web scraping

**Configuration**:
```python
docker run -d \
  -p 11235:11235 \
  --name crawler \
  --shm-size=1g \
  -e CRAWL4AI_API_TOKEN=tileshop \
  unclecode/crawl4ai:browser
```

#### API Gateway (`api_gateway`)
**Technology**: Kong
**Ports**: 8000, 8001, 8443
**Purpose**: Request routing and API management

### 5. Diagnostic Framework

#### Service Diagnostic Classes (`modules/service_diagnostic.py`)

**Base Class**: `ServiceDiagnostic`
- Abstract base for all diagnostic services
- Standardized interface: `health_check()`, `get_filtered_logs()`, `debug_panel()`

**Specialized Classes**:

1. **ContainerServiceDiagnostic**
   - Docker container health monitoring
   - Port accessibility checks
   - Resource usage tracking
   - Container lifecycle management

2. **ConceptualServiceDiagnostic**
   - System-level service monitoring
   - API availability checks
   - Configuration validation

3. **RuntimeServiceDiagnostic**
   - Environment dependency checks
   - System resource monitoring
   - Python environment validation

4. **PrewarmServiceDiagnostic**
   - Service initialization checks
   - Database connection validation
   - System readiness verification

## Service Registry

### Microservices (6 services)
0. **docker_engine** - Container orchestration platform
1. **relational_db** - PostgreSQL primary database
2. **vector_db** - Vector database for embeddings
3. **crawler** - Crawl4AI browser service
4. **api_gateway** - Kong API gateway
5. **web_server** - Flask web application
6. **llm_api** - Claude API integration

### Runtime Environment (4 services)
7. **python_env** - Python environment validation
8. **system_dependencies** - Required packages check
9. **docker_daemon** - Docker daemon connectivity
10. **infrastructure** - System infrastructure check

### Pre-warming Systems (7 services)
11. **python_subprocess** - Python subprocess startup
12. **relational_db_prewarm** - Database connection pre-warming
13. **sitemap_validation** - Sitemap validation service
14. **vector_db_prewarm** - Vector database pre-warming
15. **crawler_service_prewarm** - Crawler service readiness

## Data Flow

### 1. Web Scraping Pipeline
```
User Request → Intelligence Manager → Crawler Service → Content Extraction → Database Storage
```

### 2. Vector Embedding Pipeline
```
Product Data (Relational DB) → Generate Embeddings → Vector Storage (Vector DB) → Semantic Search Ready
```

### 3. RAG Query Pipeline
```
User Query → RAG Manager → Vector Search → Context Retrieval → Claude API → Response Generation
```

### 4. Diagnostic Pipeline
```
Health Check Request → Service Diagnostic → Container/System Check → Status Update → Dashboard Display
```

## API Endpoints

### Service Management
- `GET /api/services/list` - List all registered services
- `GET /api/service/{name}/health` - Service health check
- `GET /api/service/{name}/logs` - Service logs
- `GET /api/service/{name}/debug` - Debug information

### Data Acquisition
- `POST /api/acquisition/start` - Start scraping process
- `GET /api/acquisition/status` - Check scraping status
- `GET /api/acquisition/prewarm-status` - Pre-warming status

### Database Sync & Embeddings
- `GET /api/sync/status` - Database sync status
- `POST /api/rag/generate-embeddings` - Generate embeddings for all products
- `GET /api/sync/test-connections` - Test database connections
- `GET /api/sync/comparison` - Compare relational vs vector data

### System Statistics
- `GET /api/system/stats` - System resource usage
- `GET /api/database/stats` - Database statistics

### RAG System
- `POST /api/rag/query` - Submit RAG query
- `GET /api/rag/knowledge-base` - Knowledge base information
- `POST /api/rag/upload` - Upload documents

## Security Architecture

### Authentication
- Session-based authentication
- API key management for external services
- Environment variable configuration

### Network Security
- Internal service communication
- Port restriction and firewall rules
- Container network isolation

### Data Protection
- Database connection encryption
- API key encryption at rest
- Secure configuration management

## Deployment Architecture

### Development Environment
```bash
# Start core services
docker-compose up -d relational_db vector_db crawler api_gateway

# Start dashboard
python reboot_dashboard.py

# Access dashboard
http://localhost:8080
```

### Production Considerations
- Load balancing for web dashboard
- Database replication and backup
- Container orchestration with Kubernetes
- Monitoring and logging aggregation
- SSL/TLS termination

## Configuration Management

### Environment Variables (`.env`)
```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-...

# Database Configuration
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=robertsher
POSTGRES_DB=postgres

# Vector Database
SUPABASE_HOST=127.0.0.1
SUPABASE_PORT=5433
SUPABASE_USER=postgres
SUPABASE_PASSWORD=supabase123
SUPABASE_DB=postgres

# Crawler Configuration
CRAWL4AI_URL=http://localhost:11235
CRAWL4AI_TOKEN=tileshop
```

### Docker Compose Configuration
```yaml
version: '3.8'
services:
  relational_db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: robertsher
      
  vector_db:
    image: pgvector/pgvector:pg15
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: supabase123
```

## Monitoring and Observability

### Health Monitoring
- Real-time service health checks
- Container resource usage tracking
- Database connection monitoring
- API endpoint availability

### Logging
- Centralized logging via Flask logging
- Container logs aggregation
- Error tracking and alerting
- Performance metrics collection

### Metrics Collection
- Service response times
- Database query performance
- Memory and CPU usage
- Network traffic analysis

## Scalability Considerations

### Horizontal Scaling
- Multiple dashboard instances behind load balancer
- Database read replicas
- Container service clustering
- API gateway load balancing

### Vertical Scaling
- Container resource limits
- Database connection pooling
- Memory optimization
- CPU core allocation

### Performance Optimization
- Asynchronous processing
- Caching strategies
- Database query optimization
- Vector search performance tuning

## Development Guidelines

### Code Organization
```
tileshop_rag/
├── modules/                 # Core business logic
│   ├── service_diagnostic.py
│   ├── rag_manager.py
│   ├── db_manager.py
│   └── intelligence_manager.py
├── templates/               # HTML templates
│   ├── dashboard.html
│   └── base.html
├── static/                  # CSS, JS, assets
├── reboot_dashboard.py      # Main application
├── docker-compose.yml       # Container orchestration
└── .env                     # Configuration
```

### Testing Strategy
- Unit tests for core modules
- Integration tests for API endpoints
- Container health check validation
- End-to-end workflow testing

### Deployment Process
1. Code review and testing
2. Docker container updates
3. Database migrations
4. Service restart coordination
5. Health check validation

---

*System Architecture Version: 2.0*
*Last Updated: July 6, 2025*
*Diagnostic Framework: Phase 2 Complete*