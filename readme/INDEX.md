# TileShop RAG Documentation Index

## 📁 Complete Documentation Directory

This index provides a comprehensive overview of all documentation files in the `/readme` directory with their purpose, key content, and deployment-related information.

---

## 🚀 **DEPLOYMENT & INFRASTRUCTURE**

### Primary Deployment Documentation
| File | Purpose | Key Content | Deployment Info |
|------|---------|-------------|----------------|
| **[DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md)** | TileScope AI deployment strategy and status tracker | Company branding, multi-agent coordination, performance targets, phase-based deployment | Manual Fly.io deployment |
| **[FLY_DEPLOYMENT_DELEGATION.md](FLY_DEPLOYMENT_DELEGATION.md)** | Fly.io deployment delegation framework | Multi-agent deployment coordination, Docker configuration, PostgreSQL setup, technical specifications | Fly.io deployment procedures |
| **[flyio-deployment-roadmap.md](flyio-deployment-roadmap.md)** | Comprehensive Fly.io migration strategy | Cloud migration from local services, database migration, cost analysis, risk assessment | Migration planning |
| **[GIT_COMMIT_INSTRUCTIONS.md](GIT_COMMIT_INSTRUCTIONS.md)** | Git workflow and commit procedures | GitHub repository info, personal access token setup, pull request creation, security best practices | **✅ Contains GitHub repo info** |
| **[DEPLOYMENT_STATUS_UPDATE.md](DEPLOYMENT_STATUS_UPDATE.md)** | Current deployment status and history | Production environment status, performance metrics, monitoring, recent deployments | **✅ Live deployment info** |

### **✅ NEW: GitHub Actions / CI/CD**
| File | Purpose | Key Content | Deployment Info |
|------|---------|-------------|----------------|
| **[GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)** | Complete CI/CD pipeline documentation | Automated testing, deployment workflows, security scanning, monitoring | **✅ Full CI/CD automation** |
| **[CREDENTIALS_TEMPLATE.md](CREDENTIALS_TEMPLATE.md)** | Secure credential management template | API keys, database passwords, GitHub secrets, security best practices | **✅ Security configuration** |

### **✅ IMPLEMENTED: Automated Deployment Pipeline**
- **✅ GitHub Actions workflows** for automated testing and deployment
- **✅ GitHub → Fly.io integration** with automated deployment on master push
- **✅ Automated testing** with coverage reporting and security scanning
- **✅ Repository**: https://github.com/1genadam/tileshop-rag

---

## 🎯 **AOS (APPROACH OF SALE) IMPLEMENTATION**

### **Professional Sales Methodology Documentation**
| File | Purpose | Key Content | Performance Status |
|------|---------|-------------|-------------------|
| **[AOS_STEPS_AND_SCORING_GUIDE.md](AOS_STEPS_AND_SCORING_GUIDE.md)** | Complete 9-step AOS framework with 1-4 scoring criteria | Professional sales methodology, mandatory requirements, scoring criteria | **Complete Framework** |
| **[AOS_SAMPLE_CONVERSATION.md](AOS_SAMPLE_CONVERSATION.md)** | Perfect 4/4 execution example for training reference | Complete conversation demonstrating all AOS steps professionally | **Gold Standard** |
| **[AOS_CURRENT_IMPLEMENTATION.md](AOS_CURRENT_IMPLEMENTATION.md)** | Technical implementation status and architecture | SimpleTileAgent + AOSConversationEngine technical details | **In Development** |
| **[AOS_QUESTION_LIBRARIES.md](AOS_QUESTION_LIBRARIES.md)** | Dynamic question management and selection system | Phase-based question organization, prioritization logic | **Implemented** |
| **[AOS_LEARNING_SCORING_SYSTEM.md](AOS_LEARNING_SCORING_SYSTEM.md)** | Performance measurement and optimization | Real-time scoring, effectiveness tracking, analytics | **In Development** |
| **[AOS_INTEGRATION_GUIDE.md](AOS_INTEGRATION_GUIDE.md)** | Chat system architecture integration | Tool calling sequences, database integration, flow management | **Implemented** |
| **[AOS_GAP_ANALYSIS.md](AOS_GAP_ANALYSIS.md)** | Current vs target performance analysis | Performance gaps, implementation roadmap, success metrics | **Active Analysis** |

### **🏆 AOS Performance Status** (Updated: July 10, 2025)
| Test Phase | Current Score | Target | Status |
|------------|---------------|--------|--------|
| **Test 1 - Greeting & Credibility** | **4.0/4** | 4/4 | ✅ **EXCELLENT** |
| **Test 2 - Needs Assessment Start** | **4.0/4** | 4/4 | ✅ **EXCELLENT** |
| **Test 3 - Dimension Collection** | **2.7/4** | 4/4 | ⚠️ **NEEDS IMPROVEMENT** |
| **Test 4 - Complete Assessment** | **1.3/4** | 4/4 | ❌ **REQUIRES ATTENTION** |
| **Overall Progress** | **3.0/4** | 4/4 | 🎯 **75% TO TARGET** |

### **✅ Recent AOS Improvements** (July 10, 2025)
- **Enhanced system prompt** with professional AOS methodology and 4/4 targets
- **Mandatory requirement enforcement** blocks product search until name, dimensions, budget collected
- **Professional calculation engine** with waste factors and project costing
- **Validation fixes** for dimension detection ("8 feet by 10 feet" format)
- **Achieved 4/4 performance** on Greeting & Credibility and initial Needs Assessment

## 📖 **CORE DOCUMENTATION**

### Primary Documentation
| File | Purpose | Key Content |
|------|---------|-------------|
| **[README.md](README.md)** | Main project overview and quick start guide | 17-service monitoring system, production environment guide, Docker setup instructions |
| **[README_expanded.md](README_expanded.md)** | Extended comprehensive documentation | Full system documentation (extensive file) |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Complete system architecture documentation | Dual database architecture, service diagnostic framework, API endpoints, deployment considerations |

### **✅ NEW: User-Focused Documentation**
| File | Purpose | Key Content |
|------|---------|-------------|
| **[QUICK_START.md](QUICK_START.md)** | Getting started guide for new users | One-command startup, service overview, first steps, troubleshooting |
| **[DASHBOARD_MANUAL.md](DASHBOARD_MANUAL.md)** | Complete dashboard operations guide | Service management, scraping control, database management, RAG chat interface |
| **[SCRAPING_SYSTEM.md](SCRAPING_SYSTEM.md)** | Production data acquisition system | curl_scraper.py documentation, batch processing, technical implementation |
| **[URL_FILTER_MAINTENANCE.md](URL_FILTER_MAINTENANCE.md)** | URL filtering system maintenance guide | Filter criteria management, multi-file updates, error prevention procedures |
| **[CONVERSATION_FLOW_ENHANCEMENT.md](CONVERSATION_FLOW_ENHANCEMENT.md)** | RAG chat system conversation flow improvements | Persistent conversation state, dynamic content saving, natural conversation maintenance, phase detection enhancements |
| **[PURCHASE_VERIFICATION_SYSTEM.md](PURCHASE_VERIFICATION_SYSTEM.md)** | Purchase verification and smart product matching | Customer purchase history verification, intelligent product matching, installation guidance based on verified purchases |
| **[SIMPLE_TILE_AGENT.md](SIMPLE_TILE_AGENT.md)** | Natural LLM-based customer assistant | AI agent with proper components (System Prompt + Message History + User Input + Tools), replaces complex rule-based systems |

---

## 🔧 **TECHNICAL IMPLEMENTATION**

### System Implementation
| File | Purpose | Key Content |
|------|---------|-------------|
| **[COORDINATION_PROMPT.md](COORDINATION_PROMPT.md)** | Multi-agent coordination framework | System coordination, task delegation, communication protocols |
| **[INTELLIGENT_PARSING_IMPLEMENTATION_COMPLETE.md](INTELLIGENT_PARSING_IMPLEMENTATION_COMPLETE.md)** | Parsing system implementation details | Enhanced parsing capabilities, schema improvements, data quality fixes |
| **[ENHANCED_CATEGORIZATION_SUMMARY.md](ENHANCED_CATEGORIZATION_SUMMARY.md)** | Product categorization system | LLM-powered categorization, accuracy improvements, system integration |
| **[LLM_ENHANCEMENT_DOCUMENTATION.md](LLM_ENHANCEMENT_DOCUMENTATION.md)** | LLM integration improvements | Claude API integration, response optimization, error handling |
| **[DATABASE_SCHEMA_ENHANCEMENTS.md](DATABASE_SCHEMA_ENHANCEMENTS.md)** | Database architecture improvements | Schema optimizations, performance enhancements, data integrity |
| **[DUPLICATE_FIELD_CLEANUP.md](DUPLICATE_FIELD_CLEANUP.md)** | Technical Specifications duplicate field removal | Database cleanup, frontend filtering, field display name improvements |

---

## 🛠️ **SYSTEM MANAGEMENT & SUPPORT**

### System Management & Support
| File | Purpose | Key Content |
|------|---------|-------------|
| **[SYSTEM_DIAGNOSTICS.md](SYSTEM_DIAGNOSTICS.md)** | 17-service health monitoring framework | Service status checks, diagnostic procedures, system health validation |
| **[QUICK_FIXES.md](QUICK_FIXES.md)** | Emergency solutions and rapid recovery | Dashboard restart, service recovery, common problem resolution |
| **[ISSUE_RESOLUTION_GUIDE.md](ISSUE_RESOLUTION_GUIDE.md)** | Comprehensive problem solution database | Detailed error diagnosis, step-by-step solutions, root cause analysis |
| **[DATABASE_RECOVERY_PROCEDURES.md](DATABASE_RECOVERY_PROCEDURES.md)** | Database recovery and maintenance | Data backup, recovery strategies, database troubleshooting |
| **[DATA_ACQUISITION_RESET.md](DATA_ACQUISITION_RESET.md)** | Scraping session reset and counter management | Acquisition counter reset, fresh session setup, data pipeline cleanup |

### **✅ NEW: Analytics & Troubleshooting**
| File | Purpose | Key Content |
|------|---------|-------------|
| **[LEARNING_ANALYTICS_FIX.md](LEARNING_ANALYTICS_FIX.md)** | Critical analytics database routing fix | Complete fix documentation, root cause analysis, prevention measures |
| **[ANALYTICS_TROUBLESHOOTING.md](ANALYTICS_TROUBLESHOOTING.md)** | Comprehensive analytics troubleshooting guide | Diagnostic procedures, common issues, emergency recovery, monitoring |

---

## 📊 **FEATURE ENHANCEMENTS**

### System Improvements
| File | Purpose | Key Content |
|------|---------|-------------|
| **[DASHBOARD_IMPROVEMENTS_CATALOG.md](DASHBOARD_IMPROVEMENTS_CATALOG.md)** | Dashboard feature enhancements | UI improvements, real-time updates, user experience optimizations |
| **[RECOMMENDATION_SYSTEM_ENHANCEMENTS.md](RECOMMENDATION_SYSTEM_ENHANCEMENTS.md)** | Product recommendation improvements | AI-powered recommendations, user behavior analysis, conversion optimization |
| **[PRODUCT_RECOMMENDATION_LOGIC.md](PRODUCT_RECOMMENDATION_LOGIC.md)** | Recommendation algorithm documentation | Logic implementation, scoring systems, personalization features |
| **[PER_PIECE_PRICING_IMPROVEMENTS.md](PER_PIECE_PRICING_IMPROVEMENTS.md)** | Pricing system enhancements | Pricing logic, calculation improvements, display optimization |
| **[SALES_ASSOCIATE_SYSTEM_PROMPT.md](SALES_ASSOCIATE_SYSTEM_PROMPT.md)** | Sales support system documentation | Customer service automation, inquiry handling, response templates |

---

## 📈 **ANALYSIS & MONITORING**

### System Analysis
| File | Purpose | Key Content |
|------|---------|-------------|
| **[PRODUCTION_SYSTEM_ANALYSIS.md](PRODUCTION_SYSTEM_ANALYSIS.md)** | Production system health analysis | System performance metrics, error analysis, operational status |
| **[BATCH_PROCESSING_ANALYSIS.md](BATCH_PROCESSING_ANALYSIS.md)** | Batch processing system analysis | Data processing optimization, performance improvements, throughput analysis |
| **[DATA_QUALITY_IMPROVEMENTS_SUMMARY.md](DATA_QUALITY_IMPROVEMENTS_SUMMARY.md)** | Data quality enhancement summary | Data validation, quality metrics, improvement strategies |
| **[DATA_GAPS_ANALYSIS.md](DATA_GAPS_ANALYSIS.md)** | Missing data analysis | Data gaps identification, extraction opportunities, implementation priorities |
| **[DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)** | Development roadmap and strategic planning | Business impact analysis, feature prioritization, implementation timeline |

---

## 🔄 **PROCESS & RECOVERY**

### System Processes
| File | Purpose | Key Content |
|------|---------|-------------|
| **[EXTRACTION_RECOVERY_LOG.md](EXTRACTION_RECOVERY_LOG.md)** | Data extraction recovery procedures | Recovery strategies, error handling, data integrity maintenance |
| **[PARSING_FIXES_LOG.md](PARSING_FIXES_LOG.md)** | Recent parsing system fixes | Bug fixes, improvements, system updates |
| **[PARSING_MONITORING.md](PARSING_MONITORING.md)** | Parsing system monitoring | Performance tracking, error logging, system health monitoring |

---

## ✅ **DOCUMENTATION REORGANIZATION COMPLETED**

### **Phase 1: File Organization**
1. **`troubleshooting_guide_expanded.md`** → **`TROUBLESHOOTING_COMPREHENSIVE.md`** ✅
2. **`troubleshooting_guide_database_recovery.md`** → **`DATABASE_RECOVERY_PROCEDURES.md`** ✅
3. **`production_system_analysis_report.md`** → **`PRODUCTION_SYSTEM_ANALYSIS.md`** ✅
4. **`missing_data_summary.md`** → **`DATA_GAPS_ANALYSIS.md`** ✅
5. **`dev_roadmap.md`** → **`DEVELOPMENT_ROADMAP.md`** ✅
6. **`parsing-fixes-2025-07-08.md`** → **`PARSING_FIXES_LOG.md`** ✅
7. **`parsing_monitor_log.md`** → **`PARSING_MONITORING.md`** ✅

### **Phase 2: README_expanded.md Breakdown**
1. **`README_expanded.md`** (2,681 lines) → **3 focused files**:
   - **`QUICK_START.md`** → Getting started guide ✅
   - **`DASHBOARD_MANUAL.md`** → Complete dashboard operations ✅
   - **`SCRAPING_SYSTEM.md`** → Production data acquisition ✅

### **Phase 3: CI/CD Implementation**
1. **`.github/workflows/deploy.yml`** → Automated deployment pipeline ✅
2. **`.github/workflows/tests.yml`** → Comprehensive testing pipeline ✅
3. **`.github/workflows/security.yml`** → Security scanning pipeline ✅
4. **`GITHUB_ACTIONS.md`** → Complete CI/CD documentation ✅
5. **`CREDENTIALS_TEMPLATE.md`** → Secure credential management ✅

---

## ✅ **IMPLEMENTATION COMPLETED**

### GitHub Deployment Integration
- **✅ GitHub Actions workflows** for automated deployment, testing, and security
- **✅ CI/CD automation** with comprehensive pipeline
- **✅ Automated deployment pipelines** with health checks
- **✅ GitHub → Fly.io integration** on master branch pushes

### Current Deployment Process:
1. **Push to GitHub** → Triggers automated pipeline
2. **Automated testing** → Runs comprehensive test suite
3. **Security scanning** → Validates code security
4. **Automated deployment** → Deploys to Fly.io if tests pass
5. **Health checks** → Verifies deployment success

### Implemented Features:
1. **✅ GitHub Actions workflows** for automated deployment
2. **✅ CI/CD pipeline** with Fly.io integration
3. **✅ Automated testing** with coverage reporting
4. **✅ Security scanning** with vulnerability detection
5. **✅ Environment management** for staging/production
6. **✅ Credential management** with secure templates

---

## 📊 **DEPLOYMENT STATUS SUMMARY**

| Component | Status | Method |
|-----------|--------|---------|
| **GitHub Repository** | ✅ Active | Automated push triggers |
| **Fly.io Deployment** | ✅ Active | Automated via GitHub Actions |
| **CI/CD Pipeline** | ✅ Active | GitHub Actions workflows |
| **Automated Testing** | ✅ Active | Python 3.8, 3.9, 3.10 matrix |
| **Security Scanning** | ✅ Active | Bandit, Safety, CodeQL, TruffleHog |
| **Environment Management** | ✅ Active | Staging/Production environments |

**Current Production URL**: https://tileshop-rag.fly.dev/
**Repository URL**: https://github.com/1genadam/tileshop-rag

---

## 🎯 **Quick Navigation**

### **New Users**
- Start here: [QUICK_START.md](QUICK_START.md)
- Dashboard guide: [DASHBOARD_MANUAL.md](DASHBOARD_MANUAL.md)
- Emergency fixes: [QUICK_FIXES.md](QUICK_FIXES.md)

### **Developers**
- CI/CD setup: [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)
- Deployment guide: [DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)

### **System Administrators**
- System diagnostics: [SYSTEM_DIAGNOSTICS.md](SYSTEM_DIAGNOSTICS.md)
- Issue resolution: [ISSUE_RESOLUTION_GUIDE.md](ISSUE_RESOLUTION_GUIDE.md)
- Analytics troubleshooting: [ANALYTICS_TROUBLESHOOTING.md](ANALYTICS_TROUBLESHOOTING.md)
- Credentials management: [CREDENTIALS_TEMPLATE.md](CREDENTIALS_TEMPLATE.md)
- Production analysis: [PRODUCTION_SYSTEM_ANALYSIS.md](PRODUCTION_SYSTEM_ANALYSIS.md)

---

*Last Updated: 2025-07-10*
*Total Documentation Files: 47*
*Deployment Method: **Automated GitHub Actions → Fly.io deployment***

### **🎯 AOS IMPLEMENTATION MILESTONE**
**Major Achievement**: Comprehensive AOS (Approach of Sale) methodology implementation with professional Tile Shop sales standards. System now achieves 4/4 performance on greeting and initial needs assessment phases, with active development toward full 4/4 consistency across all sales phases.

### **✅ LATEST UPDATES**
- **[AOS_STEPS_AND_SCORING_GUIDE.md](AOS_STEPS_AND_SCORING_GUIDE.md)** - Complete 9-step AOS framework with professional scoring criteria (July 10, 2025)
- **[AOS_SAMPLE_CONVERSATION.md](AOS_SAMPLE_CONVERSATION.md)** - Perfect 4/4 execution example demonstrating gold standard (July 10, 2025)
- **[AOS_CURRENT_IMPLEMENTATION.md](AOS_CURRENT_IMPLEMENTATION.md)** - Technical implementation analysis and architecture overview (July 10, 2025)
- **[AOS_QUESTION_LIBRARIES.md](AOS_QUESTION_LIBRARIES.md)** - Dynamic question management and selection system (July 10, 2025)
- **[AOS_LEARNING_SCORING_SYSTEM.md](AOS_LEARNING_SCORING_SYSTEM.md)** - Performance measurement and optimization framework (July 10, 2025)
- **[AOS_INTEGRATION_GUIDE.md](AOS_INTEGRATION_GUIDE.md)** - Chat system architecture integration guide (July 10, 2025)
- **[AOS_GAP_ANALYSIS.md](AOS_GAP_ANALYSIS.md)** - Current vs target performance analysis and roadmap (July 10, 2025)
- **[SIMPLE_TILE_AGENT.md](SIMPLE_TILE_AGENT.md)** - Natural LLM-based customer assistant with proper AI agent architecture (July 10, 2025)
- **[PURCHASE_VERIFICATION_SYSTEM.md](PURCHASE_VERIFICATION_SYSTEM.md)** - Purchase verification and smart product matching system (July 10, 2025)
- **[CONVERSATION_FLOW_ENHANCEMENT.md](CONVERSATION_FLOW_ENHANCEMENT.md)** - RAG chat system conversation flow improvements (July 10, 2025)