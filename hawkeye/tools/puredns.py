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
        
        # Create resolver file (Google DNS as fallback)
        resolver_file = Path(output_file).parent / 'resolvers.txt'
        if not resolver_file.exists():
            with open(resolver_file, 'w') as f:
                f.write("8.8.8.8\n")
                f.write("8.8.4.4\n")
                f.write("1.1.1.1\n")
                f.write("1.0.0.1\n")
        
        # Build command
        command = [
            self.tool_name,
            'resolve',
            str(input_file),
            '-r', str(resolver_file),
            '-w', str(output_file)
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
            # Copy all subdomains as fallback
            logger.info(f"[*] Using all subdomains as fallback")
            with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
                fout.write(fin.read())
            
            with open(output_file, 'r') as f:
                resolved = [line.strip() for line in f if line.strip()]
            
            return {
                'status': 'partial',
                'resolved_domains': resolved,
                'count': len(resolved),
                'output_file': str(output_file)
            }


