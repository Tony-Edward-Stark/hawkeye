"""Feroxbuster tool wrapper - Optimized based on manual usage"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Feroxbuster:
    """Wrapper for feroxbuster recursive scanner"""
    
    # ✅ OPTIMIZED: Use common.txt by default (faster, still comprehensive)
    DEFAULT_WORDLISTS = {
        'quick': '/usr/share/seclists/Discovery/Web-Content/common.txt',           # 4.6K (1-2 min)
        'default': '/usr/share/seclists/Discovery/Web-Content/common.txt',         # 4.6K (1-2 min) ← DEFAULT
        'deep': '/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt',  # 30K (5-15 min)
    }
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "feroxbuster"
    
    def _get_wordlist(self, wordlist_path):
        """Get wordlist path, fallback to SecLists if not found"""
        
        # Check if provided wordlist exists and is not empty
        if wordlist_path and Path(wordlist_path).exists():
            size = Path(wordlist_path).stat().st_size
            if size > 0:
                logger.info(f"[*] Using wordlist: {wordlist_path}")
                return wordlist_path
            else:
                logger.warning(f"[!] Wordlist is empty: {wordlist_path}")
        
        # ✅ OPTIMIZED: Choose wordlist based on mode
        if self.config.get('quick_mode'):
            default_wordlist = self.DEFAULT_WORDLISTS['quick']
        elif self.config.get('deep_mode'):
            default_wordlist = self.DEFAULT_WORDLISTS['deep']
        else:
            default_wordlist = self.DEFAULT_WORDLISTS['default']
        
        if Path(default_wordlist).exists():
            logger.info(f"[*] Using SecLists wordlist: {Path(default_wordlist).name}")
            return default_wordlist
        else:
            # Try alternatives
            alternatives = [
                '/usr/share/wordlists/seclists/Discovery/Web-Content/common.txt',
                '/opt/SecLists/Discovery/Web-Content/common.txt',
            ]
            
            for alt in alternatives:
                if Path(alt).exists():
                    logger.info(f"[*] Using alternative wordlist: {alt}")
                    return alt
            
            logger.error("[!] No valid wordlist found!")
            logger.error("[!] Install SecLists: sudo apt install seclists")
            return None
    
    def run(self, urls_file, wordlist, output_file):
        """
        Run feroxbuster for recursive directory discovery
        
        Args:
            urls_file: File with base URLs to scan
            wordlist: Wordlist file path (can be None/empty)
            output_file: Path to save results
        
        Returns:
            dict: Results with discovered paths
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: cargo install feroxbuster")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(urls_file).exists():
            logger.warning(f"[!] URLs file not found: {urls_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Get valid wordlist (with SecLists fallback)
        wordlist = self._get_wordlist(wordlist)
        if not wordlist:
            return {'status': 'failed', 'reason': 'no_wordlist'}
        
        # Read URLs
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
        
        if not urls:
            logger.warning("[!] No valid URLs to scan")
            return {'status': 'failed', 'reason': 'no_urls'}
        
        logger.info(f"[*] Scanning {len(urls)} URLs with feroxbuster...")
        
        discovered_paths = []
        
        # Scan each URL (limit to 3 for reasonable time)
        for idx, url in enumerate(urls[:3], 1):
            logger.info(f"[*] Scanning [{idx}/{min(3, len(urls))}]: {url}")
            
            temp_output = Path(output_file).parent / f'ferox_temp_{idx}.txt'
            
            # ✅ OPTIMIZED: Build command based on manual usage
            command = [
                self.tool_name,
                '-u', url,
                '-w', str(wordlist),
                '-o', str(temp_output),
            ]
            
            # ✅ OPTIMIZED: Specific status codes (not all)
            # 200: OK, 204: No content
            # 301,302,307,308: Redirects (valid findings)
            # 401: Auth required (valid endpoint!)
            # 403: Forbidden (valid directory/file!)
            # 405: Method not allowed (valid endpoint!)
            command.extend(['-s', '200,204,301,302,307,308,401,403,405'])
            
            # ✅ OPTIMIZED: Add extensions (like manual command)
            command.extend(['-x', 'php,html,htm,txt,js,json,xml,bak,old'])
            
            # ✅ OPTIMIZED: Extract links from responses (finds more content)
            command.append('--extract-links')
            
            # ✅ OPTIMIZED: Follow redirects
            command.append('--redirects')
            
            # Performance settings
            threads = self.config.get('threads', 50)  # ✅ Increased from 30
            command.extend(['--threads', str(threads)])
            
            rate_limit = self.config.get('rate_limit', 200)  # ✅ Increased from 150
            command.extend(['--rate-limit', str(rate_limit)])
            
            # Smart features
            command.append('--silent')
            command.append('--auto-tune')
            command.append('--auto-bail')
            
            # ✅ OPTIMIZED: Depth control
            if self.config.get('quick_mode'):
                command.extend(['--depth', '1'])
            elif self.config.get('deep_mode'):
                command.extend(['--depth', '3'])
            else:
                command.extend(['--depth', '2'])
            
            # Run feroxbuster
            success = self.runner.run_command(
                command,
                tool_name=f"{self.tool_name} ({url})"
            )
            
            # Parse output - feroxbuster saves full results to file
            if success and temp_output.exists():
                with open(temp_output, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Feroxbuster output format: "200 ... /path"
                        if line and any(code in line for code in ['200', '301', '302', '401', '403']):
                            discovered_paths.append(line)
        
        # Save combined results
        if discovered_paths:
            with open(output_file, 'w') as f:
                for path in discovered_paths:
                    f.write(f"{path}\n")
            
            logger.info(f"[✓] Feroxbuster found {len(discovered_paths)} paths")
            
            return {
                'status': 'success',
                'paths': discovered_paths,
                'count': len(discovered_paths),
                'output_file': str(output_file)
            }
        else:
            logger.info(f"[!] No paths discovered")
            Path(output_file).touch()
            return {
                'status': 'completed',
                'paths': [],
                'count': 0,
                'output_file': str(output_file)
            }
