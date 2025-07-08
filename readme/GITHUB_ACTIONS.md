# 🚀 GitHub Actions CI/CD

## Automated Deployment and Testing Pipeline

This document covers the complete CI/CD pipeline for the TileShop RAG project using GitHub Actions.

---

## 📋 **Overview**

The project uses GitHub Actions for:
- **Automated Testing** - Run tests on every push and pull request
- **Code Quality Checks** - Linting, formatting, and security scanning
- **Automated Deployment** - Deploy to Fly.io on successful master pushes
- **Security Scanning** - Regular vulnerability and secret scanning

---

## 🔄 **Workflow Files**

### **1. Deploy Workflow** (`.github/workflows/deploy.yml`)

**Triggers:**
- Push to `master` branch → Deploy to production
- Pull requests to `master` → Run tests only

**Jobs:**
- **Test Job** (Pull Requests):
  - Sets up Python environment
  - Installs dependencies
  - Runs test suite with coverage
  - Tests scraper functionality
  - Tests dashboard startup
  
- **Deploy Job** (Master Push):
  - Runs after successful tests
  - Deploys to Fly.io using `flyctl`
  - Performs health check on deployment
  - Notifies success/failure

### **2. Test Workflow** (`.github/workflows/tests.yml`)

**Triggers:**
- Push to `master` or `develop` branches
- Pull requests to `master` or `develop`

**Features:**
- **Matrix Testing**: Tests on Python 3.8, 3.9, and 3.10
- **Code Quality**: Linting with flake8, formatting with black
- **Coverage Reports**: Upload to Codecov
- **Database Testing**: PostgreSQL service container
- **Environment Testing**: Validates configuration

### **3. Security Workflow** (`.github/workflows/security.yml`)

**Triggers:**
- Push to `master` branch
- Pull requests to `master`
- Weekly schedule (Mondays at 6 AM)

**Security Checks:**
- **Bandit**: Python security vulnerability scanner
- **Safety**: Known vulnerability database check
- **TruffleHog**: Secret scanning
- **CodeQL**: GitHub's semantic code analysis
- **Dependency Review**: License and vulnerability checks

---

## 🔧 **Required Secrets**

### **GitHub Repository Secrets**

Set these in your GitHub repository settings (Settings → Secrets and variables → Actions):

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `FLY_API_TOKEN` | Fly.io API token for deployment | Deployment |
| `ANTHROPIC_API_KEY` | Claude API key for testing | Testing & Deployment |
| `POSTGRES_PASSWORD` | Production database password | Deployment |
| `CODECOV_TOKEN` | Code coverage reporting token | Testing (optional) |

### **Setting Up Secrets**

#### **1. Fly.io API Token**
```bash
# Get your Fly.io API token
fly auth token

# Add to GitHub secrets as FLY_API_TOKEN
```

#### **2. Anthropic API Key**
```bash
# Get your API key from https://console.anthropic.com/
# Add to GitHub secrets as ANTHROPIC_API_KEY
```

#### **3. Database Credentials**
```bash
# Use your production database password
# Add to GitHub secrets as POSTGRES_PASSWORD
```

---

## 🚀 **Deployment Process**

### **Automatic Deployment**

1. **Push to Master**:
   ```bash
   git push origin master
   ```

2. **GitHub Actions Workflow**:
   - Runs automated tests
   - If tests pass, deploys to Fly.io
   - Performs health check
   - Notifies of success/failure

3. **Production URL**:
   - https://tileshop-rag.fly.dev

### **Manual Deployment**

If you need to deploy manually:

```bash
# Using Fly.io CLI
flyctl deploy --remote-only

# Using the deploy script
python deploy.py full
```

---

## 🧪 **Testing Pipeline**

### **Test Categories**

#### **1. Unit Tests**
```bash
# Run locally
pytest tests/ -v

# What GitHub Actions runs
pytest tests/ -v --cov=. --cov-report=xml
```

#### **2. Integration Tests**
- Database connectivity
- API endpoint testing
- Scraper functionality
- Dashboard startup

#### **3. Code Quality**
```bash
# Linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Formatting
black --check --diff .

# Security scanning
bandit -r . -f txt
```

### **Test Environment Setup**

GitHub Actions automatically sets up:
- **PostgreSQL service** (localhost:5432)
- **Python environment** (3.8, 3.9, 3.10)
- **Environment variables** for testing
- **Dependencies** from requirements.txt

---

## 🔒 **Security Pipeline**

### **Security Scans**

#### **1. Bandit - Python Security**
- Scans for common security issues
- Identifies potential vulnerabilities
- Generates detailed reports

#### **2. Safety - Dependency Vulnerabilities**
- Checks for known security vulnerabilities
- Validates all installed packages
- Alerts on high-risk dependencies

#### **3. TruffleHog - Secret Scanning**
- Scans for exposed secrets
- Checks commit history
- Prevents credential leaks

#### **4. CodeQL - Semantic Analysis**
- Deep code analysis
- Identifies security vulnerabilities
- Supports Python and JavaScript

### **Security Best Practices**

1. **Never commit secrets**:
   ```bash
   # Use environment variables
   api_key = os.getenv('ANTHROPIC_API_KEY')
   
   # Not hardcoded values
   # api_key = 'sk-ant-api03-...'  # ❌ DON'T DO THIS
   ```

2. **Regular dependency updates**:
   ```bash
   # Update dependencies regularly
   pip install --upgrade -r requirements.txt
   ```

3. **Monitor security alerts**:
   - Check GitHub security tab
   - Review security workflow results
   - Act on vulnerability reports

---

## 🔧 **Configuration**

### **Environment Variables**

#### **Testing Environment**
```bash
# .env file for testing
TESTING=true
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tileshop_test
ANTHROPIC_API_KEY=test_key
```

#### **Production Environment**
```bash
# Production environment (set in Fly.io)
PRODUCTION=true
POSTGRES_HOST=your-db-host
POSTGRES_PORT=5432
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=tileshop_prod
ANTHROPIC_API_KEY=your-api-key
```

### **Fly.io Configuration**

The `fly.toml` file configures deployment:

```toml
app = "tileshop-rag"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[env]
  PRODUCTION = "true"
  PORT = "8080"
```

---

## 📊 **Monitoring and Alerts**

### **Workflow Status**

Monitor workflow status:
1. **GitHub Actions Tab**: View all workflow runs
2. **Status Badges**: Add to README for visual status
3. **Email Notifications**: GitHub sends failure notifications
4. **Slack Integration**: Optional webhook notifications

### **Status Badges**

Add these to your README:

```markdown
![Deploy](https://github.com/1genadam/tileshop-rag/workflows/Deploy%20to%20Fly.io/badge.svg)
![Tests](https://github.com/1genadam/tileshop-rag/workflows/Run%20Tests/badge.svg)
![Security](https://github.com/1genadam/tileshop-rag/workflows/Security%20Scan/badge.svg)
```

### **Deployment Health**

Monitor deployment health:
- **Health Check Endpoint**: https://tileshop-rag.fly.dev/health
- **Fly.io Dashboard**: Monitor app performance
- **Application Logs**: `flyctl logs`

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Deployment Failures**
```bash
# Check deployment logs
flyctl logs

# Check secrets configuration
flyctl secrets list

# Manual deployment test
flyctl deploy --remote-only
```

#### **2. Test Failures**
```bash
# Run tests locally
pytest tests/ -v

# Check environment setup
python -c "import os; print(os.getenv('POSTGRES_HOST'))"

# Database connection test
python -c "import psycopg2; print('DB OK')"
```

#### **3. Security Scan Issues**
```bash
# Run security scans locally
bandit -r . -f txt
safety check

# Check for secrets
git log --oneline | head -10
```

### **Debug Steps**

1. **Check Workflow Logs**:
   - Go to Actions tab in GitHub
   - Click on failed workflow
   - Review step-by-step logs

2. **Test Locally**:
   - Run the same commands locally
   - Check environment variables
   - Verify dependencies

3. **Check Secrets**:
   - Verify all required secrets are set
   - Check secret names match exactly
   - Ensure secrets are not expired

---

## 🎯 **Best Practices**

### **Development Workflow**

1. **Feature Branch Development**:
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git push origin feature/new-feature
   # Create pull request
   ```

2. **Pull Request Process**:
   - Tests run automatically
   - Code review required
   - Merge only after tests pass

3. **Production Deployment**:
   - Merge to master triggers deployment
   - Health check validates deployment
   - Rollback if issues detected

### **Code Quality**

1. **Before Committing**:
   ```bash
   # Run tests
   pytest tests/
   
   # Check formatting
   black --check .
   
   # Check linting
   flake8 .
   
   # Security scan
   bandit -r .
   ```

2. **Environment Management**:
   - Use `.env` files for local development
   - Never commit secrets
   - Use environment variables for configuration

3. **Documentation**:
   - Update documentation with changes
   - Include deployment notes
   - Document configuration changes

---

## 🔄 **Continuous Improvement**

### **Pipeline Enhancements**

1. **Add More Tests**:
   - Integration tests
   - End-to-end tests
   - Performance tests

2. **Improve Security**:
   - Add more security scanners
   - Implement secret rotation
   - Add compliance checks

3. **Optimize Performance**:
   - Parallel test execution
   - Docker layer caching
   - Dependency caching

### **Monitoring Improvements**

1. **Add Metrics**:
   - Deployment frequency
   - Test success rates
   - Security scan results

2. **Alerting**:
   - Slack notifications
   - Email alerts
   - Dashboard monitoring

3. **Reporting**:
   - Weekly status reports
   - Performance metrics
   - Security summaries

---

*This CI/CD pipeline ensures reliable, secure, and automated deployment of the TileShop RAG system.*

*For deployment details, see [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)*
*For security practices, see [GIT_COMMIT_INSTRUCTIONS.md](GIT_COMMIT_INSTRUCTIONS.md)*