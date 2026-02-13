
"""Ffuf tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Ffuf:
    """Wrapper for ffuf fuzzing tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "ffuf"
    
    def run(self, urls_file, wordlist, output_file):
        """
        Run ffuf for directory/file fuzzing
        
        Args:
            urls_file: File with base URLs to fuzz
            wordlist: Wordlist file path
            output_file: Path to save results
        
        Returns:
            dict: Results with discovered paths
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install github.com/ffuf/ffuf/v2@latest")
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
            logger.warning("[!] No valid URLs to fuzz")
            return {'status': 'failed', 'reason': 'no_urls'}
        
        logger.info(f"[*] Fuzzing {len(urls)} URLs with ffuf...")
        
        discovered_paths = []
        
        # Fuzz each URL
        for idx, url in enumerate(urls[:5], 1):  # Limit to 5 URLs for reasonable time
            logger.info(f"[*] Fuzzing [{idx}/{min(5, len(urls))}]: {url}")
            
            # Build command
            fuzz_url = url.rstrip('/') + '/FUZZ'
            temp_output = Path(output_file).parent / f'ffuf_temp_{idx}.json'
            
            command = [
                self.tool_name,
                '-u', fuzz_url,
                '-w', str(wordlist),
                '-mc', '200,204,301,302,307,401,403',  # Match codes
                '-fc', '404',  # Filter 404s
                '-o', str(temp_output),
                '-of', 'json',
                '-t', str(self.config.get('threads', 40)),
                '-rate', str(self.config.get('rate_limit', 150)),
                '-s'  # Silent mode
            ]
            
            # Add recursion for deep mode
            if self.config.get('deep_mode'):
                command.extend(['-recursion', '-recursion-depth', '2'])
            
            # Run ffuf
            success = self.runner.run_command(
                command,
                tool_name=f"{self.tool_name} ({url})"
            )
            
            # Parse JSON output
            if success and temp_output.exists():
                try:
                    import json
                    with open(temp_output, 'r') as f:
                        data = json.load(f)
                        results = data.get('results', [])
                        for result in results:
                            path = result.get('url', '')
                            status = result.get('status', '')
                            length = result.get('length', 0)
                            discovered_paths.append(f"{path} [{status}] ({length})")
                except Exception as e:
                    logger.warning(f"[!] Failed to parse ffuf output: {e}")
        
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

