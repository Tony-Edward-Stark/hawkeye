
"""Dnsx tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Dnsx:
    """Wrapper for dnsx tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "dnsx"
    
    def run(self, input_file, output_file):
        """
        Run dnsx for DNS enrichment
        
        Args:
            input_file: File with domains to probe
            output_file: Path to save results
        
        Returns:
            dict: Results with DNS information
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Build command - get A records and CNAMEs
        command = [
            self.tool_name,
            '-l', str(input_file),
            '-a',  # A records
            '-cname',  # CNAME records
            '-resp',  # Show response
            '-silent',
            '-o', str(output_file)
        ]
        
        # Run the tool
        logger.info(f"[*] Enriching DNS data with dnsx...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if success and Path(output_file).exists():
            with open(output_file, 'r') as f:
                results = [line.strip() for line in f if line.strip()]
            
            logger.info(f"[✓] Enriched {len(results)} DNS records")
            
            return {
                'status': 'success',
                'dns_records': results,
                'count': len(results),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] dnsx failed or returned no results")
            return {
                'status': 'failed',
                'dns_records': [],
                'count': 0
            }
