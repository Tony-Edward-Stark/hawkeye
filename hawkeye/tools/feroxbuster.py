"""Feroxbuster tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Feroxbuster:
    """Wrapper for feroxbuster recursive scanner"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "feroxbuster"
    
    def run(self, urls_file, wordlist, output_file):
        """
        Run feroxbuster for recursive directory discovery
        
        Args:
            urls_file: File with base URLs to scan
            wordlist: Wordlist file path
            output_file: Path to save results
        
        Returns:
            dict: Results with discovered paths
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: cargo install feroxbuster")
            logger.info("[*] Or: go install github.com/epi052/feroxbuster@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(urls_file).exists():
            logger.warning(f"[!] URLs file not found: {urls_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Check wordlist
        if not wordlist or not Path(wordlist).exists():
            logger.warning(f"[!] Wordlist not found: {wordlist}")
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
            
            # Build command
            command = [
                self.tool_name,
                '-u', url,
                '-w', str(wordlist),
                '-o', str(temp_output),
                '--threads', str(self.config.get('threads', 30)),
                '--rate-limit', str(self.config.get('rate_limit', 150)),
                '--silent',
                '--auto-tune',
                '--auto-bail'
            ]
            
            # Add depth control
            if self.config.get('quick_mode'):
                command.extend(['--depth', '1'])
            elif self.config.get('deep_mode'):
                command.extend(['--depth', '4'])
            else:
                command.extend(['--depth', '2'])
            
            # Status codes to show
            command.extend(['-C', '404,410'])  # Filter these out
            
            # Run feroxbuster
            success = self.runner.run_command(
                command,
                tool_name=f"{self.tool_name} ({url})"
            )
            
            # Parse output
            if success and temp_output.exists():
                with open(temp_output, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and ('200' in line or '301' in line or '302' in line or '401' in line or '403' in line):
                            discovered_paths.append(line)
        
        # Save combined results
        if discovered_paths:
            with open(output_file, 'w') as f:
                for path in discovered_paths:
                    f.write(f"{path}\n")
            
            logger.info(f"[✓] Found {len(discovered_paths)} paths")
            
            return {
                'status': 'success',
                'paths': discovered_paths,
                'count': len(discovered_paths),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] No paths discovered")
            Path(output_file).touch()
            return {
                'status': 'completed',
                'paths': [],
                'count': 0,
                'output_file': str(output_file)
            }


