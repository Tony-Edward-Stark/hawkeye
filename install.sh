
#!/bin/bash

# HAWKEYE Installation Script
# Automated setup for all dependencies and tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
print_logo() {
    echo -e "${BLUE}"
    cat << "EOF"
           /\
          /  \
         / ^^ \
        /  ||  \
       /   ||   \
      |    ||    |
       \   ||   /
        \  ||  /
         \_||_/
           ||
          /  \
         /    \
      
       HAWKEYE
    ─────────────
    Installation Script
EOF
    echo -e "${NC}"
}

# Helper functions
print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. Some tools will be installed system-wide."
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS. This script supports Debian/Ubuntu/Kali/Parrot."
        exit 1
    fi
    
    print_info "Detected OS: $OS $VER"
}

# Install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    sudo apt update || {
        print_error "Failed to update package lists"
        exit 1
    }
    
    # Essential packages
    sudo apt install -y \
        git \
        curl \
        wget \
        unzip \
        python3 \
        python3-pip \
        python3-venv \
        golang-go \
        build-essential \
        libpcap-dev \
        2>&1 | grep -v "^Reading" || true
    
    if [ $? -eq 0 ]; then
        print_success "System dependencies installed"
    else
        print_error "Failed to install system dependencies"
        exit 1
    fi
}

# Setup Go environment
setup_go() {
    print_info "Setting up Go environment..."
    
    # Add Go bin to PATH if not already there
    if ! grep -q "export PATH=\$PATH:\$HOME/go/bin" ~/.bashrc; then
        echo '' >> ~/.bashrc
        echo '# Go binaries' >> ~/.bashrc
        echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
        print_info "Added Go bin to ~/.bashrc"
    fi
    
    # Also add to zshrc if it exists
    if [ -f ~/.zshrc ]; then
        if ! grep -q "export PATH=\$PATH:\$HOME/go/bin" ~/.zshrc; then
            echo '' >> ~/.zshrc
            echo '# Go binaries' >> ~/.zshrc
            echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.zshrc
            print_info "Added Go bin to ~/.zshrc"
        fi
    fi
    
    export PATH=$PATH:$HOME/go/bin
    
    print_success "Go environment configured"
}

# Install reconnaissance tools
install_recon_tools() {
    print_info "Installing reconnaissance tools..."
    echo ""
    
    # Tools available in repos
    print_info "Installing tools from apt repositories..."
    sudo apt install -y \
        dnsrecon \
        nmap \
        masscan \
        2>&1 | grep -v "^Reading" || true
    
    print_success "Repository tools installed"
    echo ""
    
    # Go-based tools
    print_info "Installing Go-based tools (this may take 5-10 minutes)..."
    echo ""
    
    # Array of tools to install
    declare -A tools=(
        ["subfinder"]="github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        ["dnsx"]="github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
        ["naabu"]="github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
        ["httpx"]="github.com/projectdiscovery/httpx/cmd/httpx@latest"
        ["nuclei"]="github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
        ["katana"]="github.com/projectdiscovery/katana/cmd/katana@latest"
        ["gau"]="github.com/lc/gau/v2/cmd/gau@latest"
        ["gospider"]="github.com/jaeles-project/gospider@latest"
        ["ffuf"]="github.com/ffuf/ffuf/v2@latest"
        ["feroxbuster"]="github.com/epi052/feroxbuster@latest"
        ["anew"]="github.com/tomnomnom/anew@latest"
        ["gf"]="github.com/tomnomnom/gf@latest"
        ["puredns"]="github.com/d3mondev/puredns/v2@latest"
    )
    
    for tool in "${!tools[@]}"; do
        print_info "Installing $tool..."
        if go install -v ${tools[$tool]} 2>&1 | tail -1; then
            print_success "$tool installed"
        else
            print_warning "$tool installation failed (will continue)"
        fi
    done
    
    echo ""
    print_success "Go-based tools installation completed"
    echo ""
    
    # Install enum4linux-ng
    print_info "Installing enum4linux-ng..."
    if [ ! -d "/opt/enum4linux-ng" ]; then
        sudo git clone https://github.com/cddmp/enum4linux-ng.git /opt/enum4linux-ng 2>&1 | grep -v "^Cloning" || true
        if [ -f /opt/enum4linux-ng/requirements.txt ]; then
            sudo pip3 install -q -r /opt/enum4linux-ng/requirements.txt
            sudo ln -sf /opt/enum4linux-ng/enum4linux-ng.py /usr/local/bin/enum4linux-ng
            sudo chmod +x /usr/local/bin/enum4linux-ng
            print_success "enum4linux-ng installed"
        else
            print_warning "enum4linux-ng clone succeeded but requirements.txt not found"
        fi
    else
        print_warning "enum4linux-ng already installed at /opt/enum4linux-ng"
    fi
    
    # Install gf-patterns
    print_info "Installing gf-patterns..."
    mkdir -p ~/.gf
    if [ ! -d ~/.gf/.git ]; then
        git clone https://github.com/1ndianl33t/Gf-Patterns ~/.gf/ 2>&1 | grep -v "^Cloning" || true
        print_success "gf-patterns installed"
    else
        print_warning "gf-patterns already installed"
    fi
}

# Install HAWKEYE Python package
install_hawkeye() {
    print_info "Installing HAWKEYE Python package..."
    
    # Install Python dependencies
    if [ -f requirements.txt ]; then
        print_info "Installing Python dependencies..."
        pip3 install -q -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping Python dependencies"
    fi
    
    # Install HAWKEYE in development mode
    if [ -f setup.py ]; then
        pip3 install -q -e .
        print_success "HAWKEYE package installed"
    else
        print_warning "setup.py not found, skipping package installation"
    fi
    
    # Create config directory
    mkdir -p ~/.hawkeye
    
    # Copy default config if not exists
    if [ -f config/default.yaml ] && [ ! -f ~/.hawkeye/config.yaml ]; then
        cp config/default.yaml ~/.hawkeye/config.yaml
        print_success "Config file created at ~/.hawkeye/config.yaml"
    fi
    
    print_success "HAWKEYE installed successfully"
}

# Download wordlists
download_wordlists() {
    echo ""
    print_info "Wordlist Setup"
    echo "────────────────────────────────────────"
    echo ""
    echo "Choose wordlist tier to download:"
    echo ""
    echo "  1) Minimal (~50MB)        - Fast scans, basic coverage"
    echo "  2) Balanced (~500MB)      - Recommended for most users"
    echo "  3) Comprehensive (~2GB)   - Thorough scans, takes longer"
    echo "  4) Skip for now           - Download manually later"
    echo ""
    read -p "Enter choice [1-4]: " tier_choice
    
    case $tier_choice in
        1|2|3)
            if [ -f scripts/download_wordlists.sh ]; then
                bash scripts/download_wordlists.sh $tier_choice
            else
                print_warning "Wordlist download script not found"
                print_info "You can download wordlists manually later"
            fi
            ;;
        4)
            print_warning "Skipping wordlist download"
            print_info "Run 'bash scripts/download_wordlists.sh' later to download"
            ;;
        *)
            print_warning "Invalid choice. Skipping wordlist download"
            ;;
    esac
}

# Verify installation
verify_installation() {
    echo ""
    print_info "Verifying installation..."
    echo ""
    
    MISSING_TOOLS=()
    INSTALLED_TOOLS=()
    
    # Check critical tools
    tools_to_check=("subfinder" "nuclei" "httpx" "nmap" "ffuf" "naabu" "dnsx" "katana")
    
    for tool in "${tools_to_check[@]}"; do
        if command -v $tool >/dev/null 2>&1; then
            INSTALLED_TOOLS+=("$tool")
        else
            MISSING_TOOLS+=("$tool")
        fi
    done
    
    # Print results
    if [ ${#INSTALLED_TOOLS[@]} -gt 0 ]; then
        print_success "Installed tools (${#INSTALLED_TOOLS[@]}/${#tools_to_check[@]}):"
        for tool in "${INSTALLED_TOOLS[@]}"; do
            echo "  ✓ $tool"
        done
    fi
    
    echo ""
    
    if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
        print_warning "Missing tools (${#MISSING_TOOLS[@]}/${#tools_to_check[@]}):"
        for tool in "${MISSING_TOOLS[@]}"; do
            echo "  ✗ $tool"
        done
        echo ""
        print_info "Missing tools can be installed manually"
    fi
    
    echo ""
    
    # Check HAWKEYE command
    if command -v hawkeye >/dev/null 2>&1; then
        print_success "HAWKEYE command is available!"
        echo ""
        hawkeye --version 2>/dev/null || echo "HAWKEYE v1.0.0"
    else
        print_warning "HAWKEYE command not found in PATH"
        print_info "You may need to reload your shell:"
        echo "  source ~/.bashrc"
        echo ""
        print_info "Or try running directly:"
        echo "  python3 -m hawkeye --help"
    fi
}

# Print completion message
print_completion() {
    echo ""
    echo "════════════════════════════════════════════════════════"
    print_success "  HAWKEYE INSTALLATION COMPLETE!  "
    echo "════════════════════════════════════════════════════════"
    echo ""
    print_info "Quick start:"
    echo "  1. Reload your shell:    source ~/.bashrc"
    echo "  2. Test the tool:        hawkeye --help"
    echo "  3. Run a scan:           hawkeye -t example.com"
    echo ""
    print_info "Documentation:"
    echo "  • README.md for usage guide"
    echo "  • docs/ directory for detailed docs"
    echo ""
    print_info "Report issues:"
    echo "  https://github.com/yourusername/hawkeye/issues"
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo ""
}

# Main installation flow
main() {
    print_logo
    
    echo ""
    print_info "This script will install HAWKEYE and all required tools"
    print_warning "Installation requires sudo privileges"
    echo ""
    read -p "Continue with installation? [Y/n]: " continue_install
    
    if [[ $continue_install =~ ^[Nn]$ ]]; then
        print_error "Installation cancelled by user"
        exit 0
    fi
    
    echo ""
    echo "════════════════════════════════════════════════════════"
    print_info "Starting HAWKEYE installation..."
    echo "════════════════════════════════════════════════════════"
    echo ""
    
    check_root
    detect_os
    
    echo ""
    install_system_deps
    echo ""
    setup_go
    echo ""
    install_recon_tools
    echo ""
    install_hawkeye
    echo ""
    download_wordlists
    echo ""
    verify_installation
    echo ""
    print_completion
}

# Run main function
main
