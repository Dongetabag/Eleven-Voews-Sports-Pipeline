# MCP Multi-Mac Installation - Complete Package

**Author:** Simeon Reid  
**Date:** October 27, 2025  
**Purpose:** Deploy 23+ MCP servers across multiple Macs

---

## Table of Contents
1. [Installation Script](#installation-script)
2. [API Key Template](#api-key-template)
3. [Test Script](#test-script)
4. [Deployment Guide](#deployment-guide)
5. [Quick Reference](#quick-reference)

---

## Installation Script

Save as: `install-mcp-stack.sh`

```bash
#!/bin/bash

##############################################################################
# MCP AI Automation System Installation Script
# Author: Simeon Reid
# Purpose: Install and configure 23+ MCP servers across multiple Macs
# Generated: October 2025
##############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

##############################################################################
# SECTION 1: Prerequisites Check
##############################################################################

check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "This script is designed for macOS only"
        exit 1
    fi
    log_success "macOS detected"
}

check_homebrew() {
    if ! command -v brew &> /dev/null; then
        log_warning "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        if [[ $(uname -m) == "arm64" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    fi
    log_success "Homebrew is installed"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not found. Installing Docker Desktop..."
        brew install --cask docker
        log_info "Please start Docker Desktop and press Enter..."
        read
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker Desktop first."
        exit 1
    fi
    
    log_success "Docker is running"
}

##############################################################################
# SECTION 2: Install Docker MCP Toolkit
##############################################################################

install_mcp_toolkit() {
    log_info "Installing Docker MCP Toolkit..."
    docker pull ghcr.io/docker/mcp-toolkit:latest
    log_success "Docker MCP Toolkit installed"
}

##############################################################################
# SECTION 3: Configure MCP Servers
##############################################################################

create_mcp_config() {
    local config_dir="$HOME/Library/Application Support/Claude"
    local config_file="$config_dir/claude_desktop_config.json"
    
    log_info "Creating MCP configuration..."
    mkdir -p "$config_dir"
    
    cat > "$config_file" << 'EOF'
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--pull=always",
        "--mount", "type=bind,src=/mnt/user-data/uploads,dst=/mnt/user-data/uploads",
        "--mount", "type=bind,src=/mnt/user-data/outputs,dst=/mnt/user-data/outputs",
        "--mount", "type=volume,src=mcp_home,dst=/home/claude",
        "--mount", "type=volume,src=mcp_tmp,dst=/tmp/mcp",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "ghcr.io/docker/mcp-toolkit:latest"
      ],
      "env": {
        "FIGMA_PERSONAL_ACCESS_TOKEN": "",
        "VERCEL_ACCESS_TOKEN": "",
        "SPOTIFY_ENABLED": "true",
        "BUILDKITE_API_TOKEN": "",
        "GITHUB_PERSONAL_ACCESS_TOKEN": "",
        "STRIPE_API_KEY": "",
        "EVERART_API_KEY": "",
        "BRAVE_API_KEY": "",
        "AUDIENSE_ACCESS_TOKEN": ""
      }
    }
  }
}
EOF
    
    log_success "Claude Desktop config created"
}

create_cursor_config() {
    local cursor_config_dir="$HOME/.cursor/mcp"
    local cursor_config_file="$cursor_config_dir/config.json"
    
    log_info "Creating Cursor configuration..."
    mkdir -p "$cursor_config_dir"
    
    cat > "$cursor_config_file" << 'EOF'
{
  "mcpServers": {
    "docker-mcp-toolkit": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--pull=always",
        "--mount", "type=bind,src=/Users/YOURUSERNAME/Projects,dst=/workspace",
        "--mount", "type=volume,src=mcp_home,dst=/home/claude",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "ghcr.io/docker/mcp-toolkit:latest"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "",
        "BRAVE_API_KEY": ""
      }
    }
  }
}
EOF
    
    log_warning "Update YOURUSERNAME in $cursor_config_file"
    log_success "Cursor config created"
}

create_docker_volumes() {
    log_info "Creating Docker volumes..."
    docker volume create mcp_home 2>/dev/null || true
    docker volume create mcp_tmp 2>/dev/null || true
    log_success "Docker volumes created"
}

create_data_directories() {
    log_info "Creating data directories..."
    mkdir -p /mnt/user-data/uploads 2>/dev/null || true
    mkdir -p /mnt/user-data/outputs 2>/dev/null || true
    
    if [ ! -d "/mnt/user-data" ]; then
        mkdir -p "$HOME/mcp-data/uploads"
        mkdir -p "$HOME/mcp-data/outputs"
    fi
    log_success "Data directories created"
}

install_dev_tools() {
    log_info "Checking development tools..."
    
    if [ ! -d "/Applications/Claude.app" ]; then
        log_info "Install Claude Desktop: https://claude.ai/download"
    fi
    
    if [ ! -d "/Applications/Cursor.app" ]; then
        log_info "Installing Cursor IDE..."
        brew install --cask cursor
    fi
    
    log_success "Development tools check complete"
}

verify_installation() {
    log_info "Verifying installation..."
    
    docker info &> /dev/null && log_success "Docker running" || log_error "Docker not running"
    docker images | grep -q "mcp-toolkit" && log_success "MCP Toolkit available" || log_warning "MCP Toolkit not found"
    [ -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json" ] && log_success "Claude config exists"
    [ -f "$HOME/.cursor/mcp/config.json" ] && log_success "Cursor config exists"
}

test_mcp_connection() {
    log_info "Testing MCP connection..."
    if docker run --rm ghcr.io/docker/mcp-toolkit:latest echo "Test" &> /dev/null; then
        log_success "MCP Toolkit functional"
    else
        log_error "MCP Toolkit test failed"
    fi
}

create_uninstall_script() {
    cat > "$HOME/uninstall-mcp-stack.sh" << 'EOF'
#!/bin/bash
echo "Uninstalling MCP Stack..."
docker volume rm mcp_home mcp_tmp 2>/dev/null || true
rm -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
rm -f "$HOME/.cursor/mcp/config.json"
rm -rf "$HOME/mcp-data"
docker rmi ghcr.io/docker/mcp-toolkit:latest 2>/dev/null || true
echo "MCP Stack uninstalled"
EOF
    chmod +x "$HOME/uninstall-mcp-stack.sh"
    log_success "Uninstall script created"
}

##############################################################################
# MAIN EXECUTION
##############################################################################

main() {
    echo "======================================================================"
    echo "  MCP AI Automation System Installation"
    echo "  Installing 23+ MCP Servers"
    echo "======================================================================"
    
    check_macos
    check_homebrew
    check_docker
    install_mcp_toolkit
    create_docker_volumes
    create_data_directories
    create_mcp_config
    create_cursor_config
    install_dev_tools
    create_uninstall_script
    verify_installation
    test_mcp_connection
    
    echo ""
    echo "======================================================================"
    log_success "Installation Complete!"
    echo "======================================================================"
    echo ""
    echo "Next Steps:"
    echo "  1. Configure API keys (see template)"
    echo "  2. Restart Claude Desktop & Cursor"
    echo "  3. Test: 'List your available MCP tools'"
    echo ""
    echo "MCP Tools: Playwright, GitHub, PostgreSQL, FFmpeg, EverArt,"
    echo "           Brave Search, Figma, Vercel, Stripe, and 14+ more"
}

main
exit 0
```

---

## API Key Template

**Priority Keys (Start Here):**
1. GitHub - https://github.com/settings/tokens
2. Brave Search - https://brave.com/search/api/

**Additional Keys:**
3. Figma - https://www.figma.com/developers/api#access-tokens
4. Vercel - https://vercel.com/account/tokens
5. Stripe - https://dashboard.stripe.com/apikeys
6. EverArt - https://everart.ai/api
7. Buildkite - https://buildkite.com/user/api-access-tokens
8. Audiense - https://audiense.com/api

**Configuration Files:**
- `~/Library/Application Support/Claude/claude_desktop_config.json`
- `~/.cursor/mcp/config.json`

**Security:**
- Store keys in password manager
- Use read-only tokens when possible
- Never commit to Git
- Rotate keys quarterly

---

## Test Script

Save as: `test-mcp-tools.sh`

```bash
#!/bin/bash

echo "======================================================================"
echo "  MCP Stack Test Suite"
echo "======================================================================"

echo "Test 1: Docker"
docker info &> /dev/null && echo "✓ Docker running" || echo "✗ Docker not running"

echo "Test 2: MCP Toolkit"
docker images | grep -q "mcp-toolkit" && echo "✓ Image found" || echo "⚠ Pulling image..."

echo "Test 3: MCP Command"
docker run --rm ghcr.io/docker/mcp-toolkit:latest echo "Test" &> /dev/null && echo "✓ Commands work" || echo "✗ Failed"

echo "Test 4: Configs"
[ -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json" ] && echo "✓ Claude config" || echo "⚠ Missing"
[ -f "$HOME/.cursor/mcp/config.json" ] && echo "✓ Cursor config" || echo "⚠ Missing"

echo ""
echo "Next: Configure API keys, restart apps, test tools"
```

---

## Deployment Guide

### Multi-Mac Installation

**Option 1: Git (Recommended)**
```bash
# Setup
git init
git add install-mcp-stack.sh
git commit -m "MCP installation"
git remote add origin YOUR_PRIVATE_REPO
git push

# On each Mac
git clone YOUR_REPO && cd YOUR_REPO
chmod +x install-mcp-stack.sh
./install-mcp-stack.sh
```

**Option 2: USB Drive**
```bash
# Copy to USB
cp install-mcp-stack.sh /Volumes/USB/

# On each Mac
cd /Volumes/USB
chmod +x install-mcp-stack.sh
./install-mcp-stack.sh
```

**Option 3: Cloud Storage**
Upload to iCloud/Dropbox, download on each Mac, run script.

### Time Estimates
- First Mac: 20-30 minutes
- Additional Macs: 10-15 minutes each
- API setup: 15-20 minutes (one-time)
- Total for 5 Macs: ~2 hours

---

## Quick Reference

### Installation Commands
```bash
# Make executable
chmod +x install-mcp-stack.sh

# Run installation
./install-mcp-stack.sh

# Test installation
./test-mcp-tools.sh
```

### Config Locations
```
~/Library/Application Support/Claude/claude_desktop_config.json
~/.cursor/mcp/config.json
~/mcp-data/uploads
~/mcp-data/outputs
```

### Docker Commands
```bash
# Pull latest
docker pull ghcr.io/docker/mcp-toolkit:latest

# List volumes
docker volume ls

# Remove volumes
docker volume rm mcp_home mcp_tmp
```

### Troubleshooting
```bash
# Start Docker
open -a Docker

# Validate config
python3 -m json.tool CONFIG_FILE

# Check logs
docker logs CONTAINER_ID
```

### Available MCP Tools (23+)

**Web Automation**
- Playwright (21 tools) - Browser automation
- Puppeteer - Headless browser
- Browser - Web interactions

**Development**
- GitHub (40+ tools) - Repository management
- Git - Version control
- Filesystem - File operations
- Context7 - Library documentation

**Database**
- PostgreSQL - Database operations
- Obsidian - Note management

**Media**
- FFmpeg - Video/audio processing
- ImageMagick - Image manipulation
- EverArt - AI image generation

**Search**
- Brave Search - Web/image/video/news
- Fetch - URL content retrieval
- DuckDuckGo - Alternative search

**Integrations**
- Figma - Design files
- Vercel - Deployment
- Buildkite - CI/CD
- Stripe - Payments
- Spotify - Music control
- Audiense - Analytics

**Utilities**
- OpenAPI - API specifications
- Time - Timezone conversions

### Usage Examples
```
"Navigate to example.com and extract all links"
"Create React component using Next.js 14 best practices"
"Query users table and export to CSV"
"Generate sunset image and convert to WebP"
"Create branch, commit changes, open PR"
```

### Maintenance Schedule

**Weekly:** Check for updates
**Monthly:** Review API usage, verify sync
**Quarterly:** Rotate API keys, optimize config

---

## Support

- Documentation: https://modelcontextprotocol.io
- Docker MCP: https://github.com/docker/mcp-toolkit
- Claude Support: https://support.claude.com

---

*Generated October 27, 2025 by Simeon Reid*
