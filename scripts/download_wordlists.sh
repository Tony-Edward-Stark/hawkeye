
#!/bin/bash

# Wordlist Download Script for HAWKEYE

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_info() { echo -e "${BLUE}[*]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

TIER=${1:-2}

BASE_DIR="wordlists"

download_tier1() {
    print_info "Downloading Tier 1 wordlists (Minimal ~50MB)..."
    
    mkdir -p $BASE_DIR/tier1
    cd $BASE_DIR/tier1
    
    # Subdomains
    print_info "Downloading subdomain wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt -O subdomains.txt
    
    # Directories
    print_info "Downloading directory wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O directories.txt
    
    # Files
    print_info "Downloading file wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-small-files.txt -O files.txt
    
    cd ../..
    print_success "Tier 1 wordlists downloaded"
}

download_tier2() {
    print_info "Downloading Tier 2 wordlists (Balanced ~500MB)..."
    
    mkdir -p $BASE_DIR/tier2
    cd $BASE_DIR/tier2
    
    # Subdomains - using best-dns-wordlist
    print_info "Downloading subdomain wordlist (large, may take time)..."
    wget -q https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt -O subdomains.txt
    
    # Directories
    print_info "Downloading directory wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt -O directories.txt
    
    # Files
    print_info "Downloading file wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-medium-files.txt -O files.txt
    
    # Parameters
    print_info "Downloading parameter wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -O parameters.txt
    
    cd ../..
    print_success "Tier 2 wordlists downloaded"
}

download_tier3() {
    print_info "Downloading Tier 3 wordlists (Comprehensive ~2GB)..."
    print_warning "This will take a while and use significant disk space"
    
    mkdir -p $BASE_DIR/tier3
    cd $BASE_DIR/tier3
    
    # Subdomains
    print_info "Downloading comprehensive subdomain wordlist..."
    wget -q https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt -O subdomains.txt
    
    # Directories
    print_info "Downloading large directory wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-big.txt -O directories.txt
    
    # Files
    print_info "Downloading large file wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-large-files.txt -O files.txt
    
    # Parameters
    print_info "Downloading parameter wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -O parameters.txt
    
    cd ../..
    print_success "Tier 3 wordlists downloaded"
}

case $TIER in
    1)
        download_tier1
        ;;
    2)
        download_tier2
        ;;
    3)
        download_tier3
        ;;
    *)
        print_warning "Invalid tier. Use 1, 2, or 3"
        exit 1
        ;;
esac

print_success "Wordlist download complete!"
