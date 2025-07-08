# 🔐 Credentials Template

## TileShop RAG System - Secure Credential Management

This document provides a template for managing all passwords, API keys, and sensitive credentials for the TileShop RAG system.

---

## ⚠️ **SECURITY WARNING**

**✅ THIS TEMPLATE FILE IS SAFE TO COMMIT TO GIT**

- This is a TEMPLATE file with placeholder values only
- Contains NO actual credentials - only examples and structure
- Create a separate, secure credentials file for actual values (see .gitignore for excluded files)
- Keep actual credentials in password managers or secure vaults
- Use environment variables for all sensitive data

**🚨 NEVER COMMIT ACTUAL CREDENTIALS TO GIT**

---

## 📋 **Credentials Inventory**

### **🔑 API Keys**

#### **Anthropic Claude API**
```bash
# Description: Claude API for LLM functionality
# Used by: RAG system, categorization, chat interface
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-api03-[YOUR_KEY_HERE]

# Alternative test key (for development)
ANTHROPIC_API_KEY_TEST=sk-ant-api03-[TEST_KEY_HERE]
```

#### **GitHub API Token**
```bash
# Description: GitHub repository access and deployment
# Used by: Git operations, CI/CD, repository management
# Get from: GitHub Settings → Developer settings → Personal access tokens
GITHUB_TOKEN=ghp_[YOUR_GITHUB_TOKEN_HERE]

# Repository-specific token
GITHUB_REPO_TOKEN=ghp_[REPO_SPECIFIC_TOKEN_HERE]
```

#### **Fly.io API Token**
```bash
# Description: Fly.io deployment and management
# Used by: Automated deployments, CI/CD pipeline
# Get from: `fly auth token` command
FLY_API_TOKEN=[YOUR_FLY_API_TOKEN_HERE]
```

---

### **🗄️ Database Credentials**

#### **PostgreSQL (Primary Database)**
```bash
# Production Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[YOUR_POSTGRES_PASSWORD_HERE]
POSTGRES_DB=tileshop_rag

# Test Database
POSTGRES_TEST_HOST=localhost
POSTGRES_TEST_PORT=5432
POSTGRES_TEST_USER=postgres
POSTGRES_TEST_PASSWORD=[YOUR_TEST_PASSWORD_HERE]
POSTGRES_TEST_DB=tileshop_test
```

#### **Supabase (Vector Database)**
```bash
# Supabase Configuration
SUPABASE_HOST=localhost
SUPABASE_PORT=54321
SUPABASE_USER=postgres
SUPABASE_PASSWORD=[YOUR_SUPABASE_PASSWORD_HERE]
SUPABASE_DB=postgres

# Supabase API Keys (if using cloud)
SUPABASE_URL=https://[YOUR_PROJECT].supabase.co
SUPABASE_ANON_KEY=[YOUR_ANON_KEY_HERE]
SUPABASE_SERVICE_KEY=[YOUR_SERVICE_KEY_HERE]
```

---

### **🌐 Web Services**

#### **Crawl4AI Service**
```bash
# Crawl4AI Configuration
CRAWL4AI_URL=http://localhost:11235
CRAWL4AI_TOKEN=[YOUR_CRAWL4AI_TOKEN_HERE]
CRAWL4AI_API_KEY=[YOUR_CRAWL4AI_API_KEY_HERE]
```

#### **Flask Application**
```bash
# Flask Secret Key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
FLASK_SECRET_KEY=[YOUR_FLASK_SECRET_KEY_HERE]
SECRET_KEY=[YOUR_SECRET_KEY_HERE]
```

---

### **☁️ Cloud Services**

#### **Production Environment**
```bash
# Production Settings
PRODUCTION=true
FLASK_ENV=production
DEBUG=false
PORT=8080

# Database URL (production)
DATABASE_URL=postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]
```

#### **Development Environment**
```bash
# Development Settings
DEVELOPMENT=true
FLASK_ENV=development
DEBUG=true
PORT=8080

# Local services
REDIS_URL=redis://localhost:6379
ELASTICSEARCH_URL=http://localhost:9200
```

---

## 🔧 **Configuration Files**

### **Environment File (.env)**
```bash
# Copy this template to .env and fill in actual values
# Location: /Users/robertsher/Projects/tileshop_rag_prod/.env

# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GITHUB_TOKEN=your_github_token_here
FLY_API_TOKEN=your_fly_api_token_here

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password_here
POSTGRES_DB=tileshop_rag

# Supabase
SUPABASE_HOST=localhost
SUPABASE_PORT=54321
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your_supabase_password_here
SUPABASE_DB=postgres

# Web Services
CRAWL4AI_URL=http://localhost:11235
CRAWL4AI_TOKEN=your_crawl4ai_token_here
FLASK_SECRET_KEY=your_flask_secret_key_here

# Application Settings
PRODUCTION=false
DEBUG=true
PORT=8080
```

### **Docker Environment File (.env.docker)**
```bash
# Docker-specific environment variables
# Location: /Users/robertsher/Projects/tileshop_rag_prod/.env.docker

# Database Configuration
POSTGRES_PASSWORD=your_postgres_password_here
POSTGRES_USER=postgres
POSTGRES_DB=tileshop_rag

# Supabase Configuration
SUPABASE_POSTGRES_PASSWORD=your_supabase_password_here
SUPABASE_JWT_SECRET=your_jwt_secret_here
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

---

## 🚀 **GitHub Secrets**

### **Repository Secrets**
Configure these in GitHub Settings → Secrets and variables → Actions:

```bash
# Required for CI/CD
FLY_API_TOKEN              # Fly.io deployment token
ANTHROPIC_API_KEY          # Claude API key
POSTGRES_PASSWORD          # Production database password
CODECOV_TOKEN             # Code coverage reporting (optional)

# Optional for enhanced functionality
SLACK_WEBHOOK_URL         # Slack notifications
DOCKER_HUB_USERNAME       # Docker Hub access
DOCKER_HUB_TOKEN          # Docker Hub access token
```

### **Environment Secrets**
Configure these in GitHub Settings → Environments:

```bash
# Production Environment
PRODUCTION_DATABASE_URL    # Full production database URL
PRODUCTION_REDIS_URL      # Production Redis URL
PRODUCTION_API_KEYS       # Production API keys

# Staging Environment
STAGING_DATABASE_URL      # Staging database URL
STAGING_API_KEYS          # Staging API keys
```

---

## 🔒 **Security Best Practices**

### **Password Requirements**
- **Minimum 16 characters**
- **Mix of uppercase, lowercase, numbers, symbols**
- **No dictionary words**
- **Unique for each service**

### **API Key Management**
- **Rotate keys regularly** (every 90 days)
- **Use different keys for different environments**
- **Monitor key usage and access logs**
- **Revoke unused or compromised keys immediately**

### **Secret Storage**
```bash
# Use a password manager (recommended)
1Password, LastPass, Bitwarden, etc.

# Or use secure environment variables
export ANTHROPIC_API_KEY="your_key_here"

# Or use encrypted files
gpg --symmetric --cipher-algo AES256 credentials.txt
```

---

## 🛡️ **Access Control**

### **Development Team Access**
```bash
# Database Access
Developer 1: Read/Write access to development DB
Developer 2: Read/Write access to development DB
Admin: Full access to all environments

# API Key Access
Developers: Development/staging keys only
Admin: Production keys
CI/CD: Automated deployment keys
```

### **Service Account Permissions**
```bash
# GitHub Actions Service Account
- Repository: Read/Write
- Secrets: Read
- Actions: Execute
- Packages: Read/Write

# Fly.io Service Account
- App: Deploy
- Secrets: Read/Write
- Logs: Read
- Monitoring: Read
```

---

## 📋 **Credential Rotation Schedule**

### **Quarterly Rotation (Every 90 Days)**
- [ ] Anthropic API Keys
- [ ] GitHub Personal Access Tokens
- [ ] Fly.io API Tokens
- [ ] Database Passwords (production)

### **Annual Rotation (Every 365 Days)**
- [ ] Flask Secret Keys
- [ ] JWT Secrets
- [ ] Encryption Keys
- [ ] SSL Certificates

### **Rotation Checklist**
1. **Generate new credential**
2. **Update all environment files**
3. **Update GitHub secrets**
4. **Update production deployment**
5. **Test all services**
6. **Revoke old credential**
7. **Document rotation date**

---

## 🚨 **Emergency Procedures**

### **Credential Compromise**
```bash
# Immediate Actions
1. Revoke compromised credential immediately
2. Generate new credential
3. Update all systems
4. Check access logs for unauthorized usage
5. Notify team and stakeholders
6. Document incident

# Recovery Steps
1. Assess impact and exposure
2. Change all related credentials
3. Review and update security policies
4. Implement additional monitoring
5. Conduct security audit
```

### **Emergency Contacts**
```bash
# Security Team
Security Lead: security@company.com
System Admin: admin@company.com

# Service Providers
Anthropic Support: support@anthropic.com
GitHub Support: https://support.github.com/
Fly.io Support: https://fly.io/support/
```

---

## 🔧 **Setup Instructions**

### **Local Development Setup**
```bash
# 1. Copy template to .env
cp .env.example .env

# 2. Fill in actual values
nano .env

# 3. Verify configuration
python -c "from dotenv import load_dotenv; load_dotenv(); print('Config loaded')"

# 4. Test connections
python -c "import os; print(f'API Key: {os.getenv(\"ANTHROPIC_API_KEY\")[:10]}...')"
```

### **Production Deployment Setup**
```bash
# 1. Set Fly.io secrets
flyctl secrets set ANTHROPIC_API_KEY=your_key_here
flyctl secrets set POSTGRES_PASSWORD=your_password_here

# 2. Set GitHub secrets
# Go to repository Settings → Secrets and variables → Actions
# Add each secret manually

# 3. Verify deployment
curl -f https://tileshop-rag.fly.dev/health
```

---

## 📊 **Credential Audit Log**

### **Creation Log**
```bash
# Track when credentials were created
ANTHROPIC_API_KEY: Created 2025-07-08, Expires 2025-10-08
GITHUB_TOKEN: Created 2025-07-08, Expires 2026-07-08
FLY_API_TOKEN: Created 2025-07-08, No expiration
POSTGRES_PASSWORD: Created 2025-07-08, Expires 2025-10-08
```

### **Usage Log**
```bash
# Track credential usage
ANTHROPIC_API_KEY: Used by RAG system, chat interface
GITHUB_TOKEN: Used by CI/CD, repository management
FLY_API_TOKEN: Used by deployment pipeline
POSTGRES_PASSWORD: Used by application, backups
```

### **Access Log**
```bash
# Track who has access to what
Admin: All credentials
Developer 1: Development credentials only
Developer 2: Development credentials only
CI/CD System: Deployment credentials only
```

---

## 💡 **Tips and Reminders**

### **Development Tips**
- Use `.env` files for local development
- Never commit `.env` files to git
- Use `.env.example` for templates
- Test credential changes in development first

### **Production Tips**
- Use environment variables in production
- Implement credential rotation
- Monitor credential usage
- Regular security audits

### **Security Reminders**
- **Check .gitignore** includes `.env`
- **Review commit history** for exposed secrets
- **Use GitHub secret scanning** protection
- **Implement least privilege access**

---

**🔐 Remember: This template should be customized for your specific security requirements and kept secure at all times.**

*For deployment information, see [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)*
*For GitHub Actions setup, see [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)*
*For git security, see [GIT_COMMIT_INSTRUCTIONS.md](GIT_COMMIT_INSTRUCTIONS.md)*