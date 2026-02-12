
#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from hawkeye.core.workflow import WorkflowEngine
from hawkeye.ui.logger import setup_logger
from hawkeye import __version__

LOGO = """
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
      
       HAWKEYE v{}
    ─────────────────────────
    Precision Reconnaissance
""".format(__version__)

def create_parser():
    parser = argparse.ArgumentParser(
        description='HAWKEYE - Automated Reconnaissance Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hawkeye -t example.com                    # Full scan
  hawkeye -t example.com -q                 # Quick scan
  hawkeye -t example.com -m discover        # Subdomain discovery
  hawkeye -t example.com -m full -w 3       # Deep scan
  hawkeye -tL domains.txt -m vuln           # Vuln scan
  hawkeye -t example.com --interactive      # Interactive mode

Scan Modes:
  discover    Subdomain discovery only
  scan        Port scanning only
  web         Web application discovery only
  content     Directory/file discovery only
  vuln        Vulnerability scanning only
  passive     Passive recon (discover only)
  active      Active recon (scan + web + content)
  full        Complete reconnaissance (all stages)
        """
    )
    
    # Target options
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('-t', '--target', help='Target domain (example.com)')
    target_group.add_argument('-tL', '--target-list', help='File with target list')
    
    # Mode selection
    parser.add_argument('-m', '--mode', 
                       choices=['discover', 'scan', 'web', 'content', 'vuln', 
                               'passive', 'active', 'full'],
                       default='full',
                       help='Scan mode (default: full)')
    
    # Quick options
    parser.add_argument('-q', '--quick', action='store_true',
                       help='Quick scan (minimal wordlists)')
    parser.add_argument('-d', '--deep', action='store_true',
                       help='Deep scan (comprehensive wordlists)')
    
    # Output options
    parser.add_argument('-o', '--output', default='./hawkeye-output',
                       help='Output directory (default: ./hawkeye-output)')
    parser.add_argument('-w', '--wordlist', type=int, choices=[1, 2, 3], default=2,
                       help='Wordlist tier: 1=minimal, 2=balanced, 3=full (default: 2)')
    parser.add_argument('-f', '--format', nargs='+',
                       choices=['txt', 'json', 'html', 'md', 'csv', 'all'],
                       default=['txt', 'html'],
                       help='Report format (default: txt html)')
    
    # Execution control
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive stage-by-stage mode')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from last checkpoint')
    parser.add_argument('-s', '--stealth', action='store_true',
                       help='Stealth mode (slower, quieter)')
    
    # Tool control
    parser.add_argument('--skip', nargs='+',
                       help='Skip specific tools (e.g., --skip feroxbuster nuclei)')
    parser.add_argument('--only', nargs='+',
                       help='Only run specific tools (e.g., --only subfinder httpx)')
    parser.add_argument('--no-udp', dest='udp', action='store_false', default=False,
                       help='Disable UDP port scanning (default)')
    parser.add_argument('--udp', action='store_true',
                       help='Enable UDP port scanning (slow)')
    
    # Performance
    parser.add_argument('-th', '--threads', type=int, default=50,
                       help='Number of threads (default: 50)')
    parser.add_argument('-r', '--rate', type=int, default=150,
                       help='Rate limit req/sec (default: 150)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    
    # Notifications
    parser.add_argument('-n', '--notify', nargs='+',
                       choices=['slack', 'discord', 'telegram'],
                       help='Notifications: slack, discord, telegram')
    
    # Info
    parser.add_argument('-v', '--version', action='version',
                       version=f'HAWKEYE v{__version__}')
    parser.add_argument('--list-tools', action='store_true',
                       help='List all tools and their status')
    parser.add_argument('--update', action='store_true',
                       help='Update all tools and wordlists')
    
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Show logo
    print(LOGO)
    
    # Setup logger
    logger = setup_logger()
    
    # Handle special commands
    if args.list_tools:
        print("[*] Tool list feature coming soon...")
        sys.exit(0)
    
    if args.update:
        print("[*] Update feature coming soon...")
        sys.exit(0)
    
    # Initialize workflow engine
    try:
        engine = WorkflowEngine(args)
        engine.run()
    except KeyboardInterrupt:
        logger.warning("\n[!] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
