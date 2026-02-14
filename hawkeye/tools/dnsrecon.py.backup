

"""Dnsrecon tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Dnsrecon:
    """Wrapper for dnsrecon tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "dnsrecon"
    
    def run(self, target, output_file):
        """
        Run dnsrecon for comprehensive DNS enumeration
        
        Args:
            target: Domain to scan
            output_file: Path to save results
        
        Returns:
            dict: Results with DNS enumeration data
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: sudo apt install dnsrecon")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Build command - standard enumeration
        command = [
            self.tool_name,
            '-d', target,
            '-t', 'std',  # Standard enumeration
            '--json', str(output_file)
        ]
        
        # Run the tool
        logger.info(f"[*] Running DNS enumeration with dnsrecon...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if success and Path(output_file).exists():
            try:
                import json
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                record_count = len(data) if isinstance(data, list) else 0
                logger.info(f"[✓] Found {record_count} DNS records")
                
                return {
                    'status': 'success',
                    'records': data,
                    'count': record_count,
                    'output_file': str(output_file)
                }
            except Exception as e:
                logger.warning(f"[!] Failed to parse dnsrecon output: {e}")
                return {
                    'status': 'partial',
                    'count': 0,
                    'output_file': str(output_file)
                }
        else:
            logger.warning(f"[!] dnsrecon failed or returned no results")
            return {
                'status': 'failed',
                'records': [],
                'count': 0
            }
