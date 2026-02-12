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

# HAWKEYE - Automated Reconnaissance Framework

**Precision Reconnaissance for Security Professionals**

HAWKEYE is a comprehensive, automated reconnaissance framework that combines the power of multiple industry-standard tools into a streamlined workflow.

## Features

- All-in-One Reconnaissance - Combines 15+ tools
- Parallel Execution - Maximum speed
- Newbie-Friendly Reports - Easy to understand
- Resume Capability - Continue interrupted scans
- Multiple Modes - Quick to comprehensive scans
- Multiple Formats - TXT, JSON, HTML, MD, CSV

## Tools Integrated

**Discovery:** subfinder, puredns, dnsx, dnsrecon  
**Scanning:** naabu, nmap  
**Web:** httpx, katana, gau, gospider  
**Content:** ffuf, feroxbuster  
**Vulnerability:** nuclei, enum4linux-ng  
**Utilities:** gf, anew, notify

## Installation

### Quick Install
```bash
git clone https://github.com/yourusername/hawkeye.git
cd hawkeye
chmod +x install.sh
sudo ./install.sh
```

### Manual Installation

**1. Install System Dependencies:**
```bash
sudo apt update
sudo apt install -y golang-go python3 python3-pip git
```

**2. Install Tools:**
```bash
# From apt
sudo apt install -y dnsrecon nmap

# Go tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/ffuf/ffuf/v2@latest
go install github.com/tomnomnom/gf@latest
go install github.com/tomnomnom/anew@latest
go install github.com/d3mondev/puredns/v2@latest

# Add to PATH
export PATH=$PATH:~/go/bin
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
```

**3. Install HAWKEYE:**
```bash
pip3 install -e .
```

## Quick Start
```bash
# Full scan
hawkeye -t example.com

# Quick scan
hawkeye -t example.com -q

# Only subdomain discovery
hawkeye -t example.com -m discover

# Deep scan
hawkeye -t example.com -d

# Interactive mode
hawkeye -t example.com --interactive
```

## Usage

### Scan Modes
```
discover    Subdomain discovery
scan        Port scanning
web         Web discovery
content     Content discovery
vuln        Vulnerability scanning
passive     Passive recon
active      Active recon
full        Complete scan (default)
```

### Common Options
```
-t <domain>      Target domain
-tL <file>       Target list
-m <mode>        Scan mode
-w <1|2|3>       Wordlist tier
-q, --quick      Quick scan
-d, --deep       Deep scan
-o <dir>         Output directory
-f <format>      Report format
--interactive    Interactive mode
--resume         Resume scan
```

## Workflow

1. **Discovery** - Find subdomains
2. **Scanning** - Port and service detection
3. **Web** - HTTP probing and crawling
4. **Content** - Directory discovery
5. **Vulnerability** - Security scanning

## Reports

HAWKEYE generates easy-to-read reports:
```
RECONNAISSANCE REPORT
═══════════════════════════════════════════
SUBDOMAINS FOUND: 23
OPEN PORTS: 48
WEB APPS: 15
VULNERABILITIES: 12
```

Formats: TXT, JSON, HTML, Markdown, CSV

## Disclaimer

**For authorized security testing only.**

- Use on systems you own
- Authorized penetration testing
- Bug bounty programs
- Unauthorized access is illegal

## License

MIT License

## Credits

Built with tools from ProjectDiscovery, tomnomnom, and the security community.

---

**Made with ❤️ for security researchers**
