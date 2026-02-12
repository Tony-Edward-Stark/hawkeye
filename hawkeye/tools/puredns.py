
"""Puredns tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Puredns:
    """Wrapper for puredns tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "puredns"
    
    def run(self, input_file, output_file):
        """
        Run puredns to resolve subdomains
        
        Args:
            input_file: File with subdomains to resolve
            output_file: Path to save resolved subdomains
        
        Returns:
            dict: Results with status and resolved domains
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install github.com/d3mondev/puredns/v2@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Build command
        command = [
            self.tool_name,
            'resolve',
            str(input_file),
            '-w', str(output_file),
            '--skip-wildcard-filter'
        ]
        
        # Run the tool
        logger.info(f"[*] Resolving subdomains with puredns...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if success and Path(output_file).exists():
            with open(output_file, 'r') as f:
                resolved = [line.strip() for line in f if line.strip()]
            
            logger.info(f"[✓] Resolved {len(resolved)} subdomains")
            
            return {
                'status': 'success',
                'resolved_domains': resolved,
                'count': len(resolved),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] puredns failed or returned no results")
            return {
                'status': 'failed',
                'resolved_domains': [],
                'count': 0
            }

