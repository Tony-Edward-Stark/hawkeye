
"""Httpx tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Httpx:
    """Wrapper for httpx HTTP probing tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "httpx"
    
    def run(self, input_file, output_file):
        """
        Run httpx for HTTP probing
        
        Args:
            input_file: File with hosts/subdomains to probe
            output_file: Path to save live web applications
        
        Returns:
            dict: Results with live URLs
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Check if input has content
        with open(input_file, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]
        
        if not hosts:
            logger.warning("[!] No hosts to probe")
            return {'status': 'failed', 'reason': 'no_hosts'}
        
        # Build command
        command = [
            self.tool_name,
            '-l', str(input_file),
            '-o', str(output_file),
            '-status-code',
            '-title',
            '-tech-detect',
            '-follow-redirects',
            '-random-agent',
            '-timeout', '10'
        ]
        
        # Add rate limiting
        rate_limit = self.config.get('rate_limit', 150)
        command.extend(['-rl', str(rate_limit)])
        
        # Add threads
        threads = self.config.get('threads', 50)
        command.extend(['-threads', str(threads)])
        
        # Run the tool
        logger.info(f"[*] Probing {len(hosts)} hosts for live web applications...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if Path(output_file).exists() and output_file.stat().st_size > 0:
            live_urls = []
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip() and line.strip().startswith('http'):
                        # Extract just the URL part (before status code)
                        url = line.strip().split()[0]
                        live_urls.append(url)
            
            if live_urls:
                logger.info(f"[✓] Found {len(live_urls)} live web applications")
                
                return {
                    'status': 'success',
                    'live_urls': live_urls,
                    'count': len(live_urls),
                    'output_file': str(output_file)
                }
        
        logger.warning(f"[!] No live web applications found")
        Path(output_file).touch()
        return {
            'status': 'completed',
            'live_urls': [],
            'count': 0
        }

