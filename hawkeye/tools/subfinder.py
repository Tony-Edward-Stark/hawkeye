

"""Subfinder tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Subfinder:
    """Wrapper for subfinder tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "subfinder"
    
    def run(self, target, output_file):
        """
        Run subfinder
        
        Args:
            target: Domain to scan
            output_file: Path to save results
        
        Returns:
            dict: Results with status and file path
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install it with: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Build command
        command = [
            self.tool_name,
            '-d', target,
            '-o', str(output_file),
            '-silent'
        ]
        
        # Add rate limiting if configured
        rate_limit = self.config.get('rate_limit')
        if rate_limit:
            command.extend(['-rl', str(rate_limit)])
        
        # Run the tool
        logger.info(f"[*] Running subfinder on {target}")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if success and Path(output_file).exists():
            with open(output_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
            
            logger.info(f"[✓] Found {len(subdomains)} subdomains")
            
            return {
                'status': 'success',
                'subdomains': subdomains,
                'count': len(subdomains),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] subfinder failed or returned no results")
            return {
                'status': 'failed',
                'subdomains': [],
                'count': 0
            }

