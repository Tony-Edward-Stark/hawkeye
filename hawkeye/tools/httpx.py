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
        
        # Build command
        command = [
            self.tool_name,
            '-l', str(input_file),
            '-o', str(output_file),
            '-silent',
            '-status-code',  # Show status codes
            '-tech-detect',  # Detect technologies
            '-title',  # Get page titles
            '-web-server',  # Show web server
            '-follow-redirects',
            '-random-agent'
        ]
        
        # Add rate limiting
        rate_limit = self.config.get('rate_limit', 150)
        command.extend(['-rl', str(rate_limit)])
        
        # Add threads
        threads = self.config.get('threads', 50)
        command.extend(['-threads', str(threads)])
        
        # Run the tool
        logger.info(f"[*] Probing for live web applications with httpx...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if success and Path(output_file).exists():
            live_urls = []
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        live_urls.append(line.strip())
            
            logger.info(f"[✓] Found {len(live_urls)} live web applications")
            
            return {
                'status': 'success',
                'live_urls': live_urls,
                'count': len(live_urls),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] httpx failed or returned no results")
            return {
                'status': 'failed',
                'live_urls': [],
                'count': 0
            }

