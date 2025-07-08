# Git Commit Instructions for Tileshop RAG Project

## 📤 Repository Information
- **GitHub**: https://github.com/1genadam/tileshop-rag
- **Main Branch**: `master` (Note: Uses master, not main)
- **License**: Public repository
- **Current Authentication**: Personal Access Token (configured in remote URL)

## 🔄 Creating Pull Requests

### Method 1: Using Personal Access Token & GitHub API (Recommended)
> **✅ This project is pre-configured with Personal Access Token authentication**
> 
> **Why This Method is Recommended:**
> - ✅ **Already configured** - No additional setup required
> - ✅ **Programmatic approach** - Works well with automation
> - ✅ **No extra dependencies** - Uses curl (built into most systems)
> - ✅ **Consistent with project setup** - Matches existing authentication

```bash
# Create and push feature branch
git checkout -b feature/your-feature-name
git add .
git commit -m "Your commit message"
git push -u origin feature/your-feature-name

# Create pull request using GitHub API
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/1genadam/tileshop-rag/pulls \
  -d '{
    "title": "Your PR Title",
    "head": "feature/your-feature-name",
    "base": "master",
    "body": "Description of your changes"
  }'
```

### Method 2: Using GitHub Web Interface
```bash
# Push your feature branch
git checkout -b feature/your-feature-name
git add .
git commit -m "Your commit message"
git push -u origin feature/your-feature-name

# Then visit: https://github.com/1genadam/tileshop-rag/pulls
# Click "New pull request" and select your branch
```

### Method 3: Using GitHub CLI (Optional - Not Pre-configured)
```bash
# Only if you want to install GitHub CLI
brew install gh

# Create feature branch and push changes
git checkout -b feature/your-feature-name
git add .
git commit -m "Your commit message"
git push -u origin feature/your-feature-name

# Create pull request
gh pr create --title "Your PR Title" --body "Description of changes"
```

## ✅ Quick Push (Direct to Master - Use Sparingly)
```bash
# Only for urgent hotfixes - prefer pull requests for review
git add .
git commit -m "Your commit message"
git push origin master
```

## 📋 Easy GitHub Commit Instructions

### Step 1: Check Status
```bash
# View current changes
git status

# See what files have been modified
git diff --name-only
```

### Step 2: Stage Changes
```bash
git add .
# Or add specific files
git add tileshop_scraper.py simple_rag.py static/chat.js
```

### Step 3: Create Commit with Descriptive Message
```bash
# Create commit with detailed message
git commit -m "Brief description of changes

- Detailed bullet point 1
- Detailed bullet point 2  
- Detailed bullet point 3

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 4: Push to GitHub
```bash
# Push to the tileshop-rag repository
git push origin master

# Alternative: Push to origin if set up
git push origin master
```

## 🔐 Authentication Methods

### ✅ CURRENT METHOD: Personal Access Token (Working)
```bash
# This project is currently configured to use Personal Access Token
# Token is already configured in the remote URL
# Simply use: git push origin master
```

### Option 1: SSH Key (Alternative)
```bash
# 1. Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your-email@example.com"

# 2. Add key to SSH agent
ssh-add ~/.ssh/id_ed25519
# (Enter your passphrase when prompted)

# 3. Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub
# Add this key to GitHub → Settings → SSH and GPG keys

# 4. Test connection
ssh -T git@github.com

# 5. Ensure remote uses SSH
git remote set-url origin git@github.com:1genadam/tileshop-rag.git
```

### Option 2: Personal Access Token Setup (For New Users)
```bash
# 1. Create token at GitHub → Settings → Developer settings → Personal access tokens
# 2. Select 'repo' permissions
# 3. Use token in remote URL
git remote set-url origin https://YOUR_TOKEN@github.com/1genadam/tileshop-rag.git

# 4. Push normally
git push origin master
```

## 🚨 Troubleshooting Authentication
```bash
# SSH Permission denied?
# - Check if key is added: ssh-add -l
# - Verify key in GitHub: cat ~/.ssh/id_ed25519.pub
# - Test connection: ssh -T git@github.com

# HTTPS asking for username/password?
# - Use personal access token instead of password
# - Update remote URL with token (see Option 2 above)
```

## 📋 Example Complete Workflow
```bash
# 1. Check what changed
git status
git diff --name-only

# 2. Stage changes
git add .

# 3. Commit with message
git commit -m "Enhanced RAG system with image display

- Added markdown image parsing to chat interface
- Fixed SKU detection for contextual queries  
- Updated container references to use 'postgres'
- Improved per-piece pricing display

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Push to GitHub
git push origin master
```

## 🔧 Git Remote Configuration
If you need to set up the remote:
```bash
# Check current remotes
git remote -v

# Add origin remote (if not exists)
git remote add origin git@github.com:1genadam/tileshop-rag.git

# Or with HTTPS and token
git remote add origin https://YOUR_TOKEN@github.com/1genadam/tileshop-rag.git
```

## 🔐 Security Best Practices
```bash
# Security Best Practices:
- ❌ Never commit API keys to version control
- ✅ Use environment variables for all sensitive data
- ✅ Keep .env files local and use .env.example for templates
- ✅ Rotate keys regularly and revoke compromised keys
```

### Files Protected by .gitignore
- `.env` - Environment configuration
- `*.log` - Application logs
- `dashboard.log` - Dashboard runtime logs
- `recovery_*.json` - Scraper recovery files
- `sitemap.xml` - Downloaded sitemaps

## 🚀 Production Git Integration
```bash
# Start in production mode with auto git push
PRODUCTION=true python3 dashboard_app.py

# Alternative: Enable auto git push without full production mode
AUTO_GIT_PUSH=true python3 dashboard_app.py
```

## Common Troubleshooting
1. **Git push failures**: Use correct remote (`origin`) instead of other names
2. **SSH authentication errors**: Add SSH key to agent with `ssh-add ~/.ssh/id_ed25519`
3. **Permission denied (publickey)**: Ensure SSH key is added to GitHub account
4. **HTTPS credential errors**: Use personal access token instead of password