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

### 1. Web Dashboard (`dashboard_app.py`)

**Purpose**: Central management interface for the entire system
**Technology**: Flask, SocketIO, HTML/CSS/JavaScript
**Port**: 8080

**Key Features**:
- **Embedding Generation Progress Tracking**: Real-time progress monitoring with animated progress bars, elapsed time, batch information, and cancel/close controls
- **17 Service Monitoring**: Unified health checks across Microservices, Runtime, and Pre-warming categories
- **Database Sync Management**: Visual status tracking and comprehensive progress feedback for vector embedding generation

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

### 2. Database Layer - Dual Database Architecture

The system uses **two separate PostgreSQL databases** for different purposes:

#### Relational Database (`relational_db`)
**Technology**: PostgreSQL  
**Port**: 5432  
**Purpose**: Complete product data storage with pricing and specifications

**Schema**:
```sql
-- Complete product information
CREATE TABLE product_data (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL UNIQUE,
    sku VARCHAR(50),
    title TEXT,
    price_per_box NUMERIC(10,2),
    price_per_sqft NUMERIC(10,2), 
    price_per_piece NUMERIC(10,2),  -- For mortar, grout, single-unit products
    coverage TEXT,
    finish TEXT,
    color TEXT,
    size_shape TEXT,
    description TEXT,
    specifications JSONB,
    resources TEXT,
    primary_image TEXT,
    image_variants JSONB,
    brand VARCHAR(100),
    thickness VARCHAR(20),
    recommended_grout VARCHAR(100),
    -- 25+ additional fields for complete product data
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Vector Database (`vector_db`)
**Technology**: PostgreSQL (using FLOAT8[] arrays instead of pgvector)  
**Port**: 5433  
**Purpose**: Semantic search, embeddings storage, and RAG functionality

**Schema**:
```sql
-- Vector embeddings for semantic search
CREATE TABLE product_embeddings (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50),
    title TEXT,
    content TEXT,              -- Concatenated product information
    embedding FLOAT8[],        -- 1536-dimensional embedding array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Database Architecture: Why Two Databases?**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DUAL DATABASE SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐              ┌─────────────────────┐   │
│  │  RELATIONAL DB      │              │    VECTOR DB        │   │
│  │  (product_data)     │              │ (product_embeddings)│   │
│  │                     │              │                     │   │
│  │ • Complete product  │              │ • SKU + Title       │   │
│  │   specifications    │              │ • Content summary   │   │
│  │ • Pricing data      │   ←──JOIN──→ │ • Vector embeddings │   │
│  │ • Images & variants │              │ • Semantic search   │   │
│  │ • 25+ detailed      │              │ • RAG functionality │   │
│  │   fields            │              │                     │   │
│  │                     │              │                     │   │
│  │ Purpose:            │              │ Purpose:            │   │
│  │ • Structured data   │              │ • AI-powered search │   │
│  │ • Fast exact queries│              │ • Natural language  │   │
│  │ • Business logic    │              │ • Content discovery │   │
│  └─────────────────────┘              └─────────────────────┘   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                         SEARCH SYSTEM                          │
│                                                                 │
│  SKU Lookup: vector_db (primary) + relational_db (pricing)     │
│  Text Search: vector_db (semantic) + relational_db (details)   │
│  Product Details: relational_db (complete information)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### **Data Flow Architecture**

```
Tileshop.com Scraping
        ↓
┌─────────────────────┐
│  Intelligence       │ → Direct scraping results
│  Manager            │
└─────────────────────┘
        ↓
┌─────────────────────┐
│  relational_db      │ → Complete product data, pricing, specifications
│  (product_data)     │   images, technical details
└─────────────────────┘
        ↓
┌─────────────────────┐
│ Embedding Generator │ → Processes product data for AI search
└─────────────────────┘
        ↓
┌─────────────────────┐
│  vector_db          │ → SKU, title, content, embeddings
│ (product_embeddings)│   optimized for semantic search
└─────────────────────┘
        ↓
┌─────────────────────┐
│  Search System      │ → JOINs both databases for complete results
│  (simple_rag.py)    │   (content + pricing + images)
└─────────────────────┘
```

### 3. Intelligence Layer

#### RAG Manager (`simple_rag.py`)
**Purpose**: Retrieval-Augmented Generation system with integrated PDF knowledge base
**Features**:
- Claude API integration
- Vector similarity search
- Context-aware responses
- **PDF Knowledge Base Integration**: Real-time PDF document search
- **Combined Search**: Unified product + knowledge base search
- **Smart Response Generation**: Contextual responses with mixed content types

**Enhanced Components**:
- **Simple RAG**: Advanced question-answering with knowledge base integration
- **Knowledge Base Search**: Real-time PDF content search with relevance scoring
- **Combined Search Engine**: Unified search across products AND PDF documents
- **Response Formatting**: Professional responses mixing products and knowledge
- **Relevance Scoring**: Intelligent content matching (title: 10pts, headers: 5pts, content: 2pts)
- **PDF Content Extraction**: Structured document parsing with section-based retrieval

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
- `POST /api/rag/query` - Submit RAG query (now includes PDF knowledge base)
- `GET /api/rag/knowledge-base` - Knowledge base information and statistics
- `POST /api/rag/upload` - Upload documents
- **NEW**: `POST /api/rag/search-knowledge` - Direct PDF knowledge base search
- **NEW**: `POST /api/rag/search-combined` - Combined product + knowledge search
- **NEW**: `GET /api/rag/knowledge-stats` - PDF knowledge base statistics and coverage

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
python dashboard_app.py

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

## Embedding Generation System

### Progress Tracking Architecture
**Location**: Database Sync card in the main dashboard
**Implementation**: Real-time progress monitoring system

**Components**:
```
┌─────────────────────────────────────────────────────────────┐
│                 EMBEDDING GENERATION UI                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Progress Bar    │    │ Status Cards    │                │
│  │ - Percentage    │    │ - Current Status│                │
│  │ - Animation     │    │ - Progress Count│                │
│  │ - Color-coded   │    │ - Elapsed Time  │                │
│  └─────────────────┘    │ - Batch Info    │                │
│                         └─────────────────┘                │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Control Buttons │    │ Real-time API   │                │
│  │ - Cancel Process│    │ - 2sec Polling  │                │
│  │ - Close Modal   │    │ - Auto-complete │                │
│  │ - State Mgmt    │    │ - Error Handling│                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

**API Endpoints**:
- `POST /api/rag/generate-embeddings` - Start embedding generation
- `GET /api/rag/embeddings-progress` - Poll for progress updates
- `POST /api/rag/cancel-embeddings` - Cancel ongoing generation

**Progress Features**:
- **Real-time Updates**: Progress polling every 2 seconds
- **Comprehensive Metrics**: Percentage, elapsed time, batch information
- **Visual Feedback**: Animated progress bar with color-coded status cards
- **State Management**: Cancel/resume functionality with proper UI state handling
- **Error Handling**: Graceful failure recovery and user notification

## Monitoring and Observability

### Health Monitoring
- Real-time service health checks
- Container resource usage tracking
- Database connection monitoring
- API endpoint availability
- **Embedding generation progress tracking** with comprehensive UI feedback

### Logging
- Centralized logging via Flask logging
- Container logs aggregation
- Error tracking and alerting
- Performance metrics collection
- **Embedding generation process logging** with batch-level granularity

### Metrics Collection
- Service response times
- Database query performance
- Memory and CPU usage
- Network traffic analysis
- **Embedding generation metrics** (processing rate, completion time, error rates)

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
├── dashboard_app.py         # Main application
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

## Recent Updates (July 7, 2025)

### PDF Knowledge Base Integration - COMPLETE & OPERATIONAL
- **✅ Complete PDF Pipeline**: JSON-embedded PDF extraction from Tileshop's Scene7 CDN
- **✅ Resource Deduplication**: Shared PDFs automatically deduplicated by URL hash
- **✅ Database Persistence**: Fixed Docker container references and crawl_results handling
- **✅ Vector Integration**: PDF resources properly stored in relational database for RAG system
- **✅ RAG Search Integration**: PDF knowledge base fully integrated into search responses
- **✅ Combined Search**: Unified search across products AND knowledge base documents
- **✅ Knowledge Response Formatting**: Professional responses combining products + knowledge
- **Coverage**: Product Data Sheets, ANSI Test Results, Safety Data Sheets across all product types
- **✅ Knowledge Base Processing**: 4 PDFs with 2,271+ words each, structured JSON storage
- **✅ Data Point Verification**: Emergency contacts, supplier info, installation instructions extracted
- **✅ Relevance Scoring**: Intelligent content matching with title (10pts), header (5pts), content (2pts)
- **✅ Real-time Search**: Live PDF content search integrated into chat responses

### Specification-Driven Intelligence
- **✅ Dynamic RAG Keywords**: Keywords generated from actual product specifications
- **✅ Edge Type Detection**: Tileshop JSON pattern `"PDPInfo_EdgeType","Value":"([^"]+)"` 
- **✅ Smart Keyword Logic**: Only assigns keywords when supported by specifications
- **Example**: `edge_type: "Rectified"` → `"rectified tile"` keyword (not hardcoded)
- **Accuracy**: Eliminates false keyword assignments like "outdoor tile" for indoor-only products

### RAG System Enhancement - COMPLETE
- **✅ PDF Knowledge Base Integration**: Full integration of PDF documents into RAG search
- **✅ Combined Search Architecture**: Unified search across products and knowledge base
- **✅ Enhanced Response Generation**: Smart responses combining product and document data
- **✅ Relevance Scoring System**: Intelligent content matching with weighted scoring
- **✅ Knowledge Response Formatting**: Professional formatting for mixed content types
- **✅ Real-time Document Search**: Live PDF content search with section-based retrieval
- **Implementation**: `simple_rag.py` enhanced with `search_knowledge_base()`, `search_combined()`, and integrated response formatting

### System Reliability Improvements
- **Database Persistence**: Fixed acquire_from_sitemap.py to properly save all scraped products
- **Container Management**: Corrected Docker container names throughout the system
- **Embedding Generation**: Now processes all available products correctly
- **Pipeline Integration**: End-to-end data flow from scraping → database → vector embeddings
- **Knowledge Base Integration**: Seamless PDF document search integrated into all RAG queries

---

*System Architecture Version: 2.3*
*Last Updated: July 7, 2025*
*PDF Knowledge Base: Phase 2 Complete - Full RAG Integration*
*Specification-Driven RAG: Phase 1 Complete*
*Diagnostic Framework: Phase 2 Complete*
*RAG Enhancement: Phase 1 Complete*