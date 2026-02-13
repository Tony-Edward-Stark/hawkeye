
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
        """Run puredns to resolve subdomains"""
        if not self.runner.check_tool_installed(self.tool_name):
            logger.info("[*] puredns not installed, using fallback resolution")
            with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
                fout.write(fin.read())
            with open(output_file, 'r') as f:
                resolved = [line.strip() for line in f if line.strip()]
            return {
                'status': 'skipped',
                'resolved_domains': resolved,
                'count': len(resolved)
            }
        
        if not Path(input_file).exists():
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Create resolvers
        resolver_file = Path(output_file).parent / 'resolvers.txt'
        if not resolver_file.exists():
            with open(resolver_file, 'w') as f:
                for dns in ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '9.9.9.9']:
                    f.write(f"{dns}\n")
        
        command = [
            self.tool_name, 'resolve',
            str(input_file),
            '-r', str(resolver_file),
            '-w', str(output_file),
            '--skip-wildcard-filter'
        ]
        
        logger.info(f"[*] Resolving subdomains with puredns...")
        
        # Run but don't show exit code 1 as error (it's normal for puredns)
        import subprocess
        try:
            subprocess.run(command, capture_output=True, timeout=300)
        except:
            pass
        
        # Check if we got results
        if Path(output_file).exists() and output_file.stat().st_size > 0:
            with open(output_file, 'r') as f:
                resolved = [line.strip() for line in f if line.strip()]
            
            if resolved:
                logger.info(f"[✓] Resolved {len(resolved)} subdomains")
                return {
                    'status': 'success',
                    'resolved_domains': resolved,
                    'count': len(resolved)
                }
        
        # Fallback
        logger.info("[*] Using all subdomains as fallback")
        with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
            fout.write(fin.read())
        
        with open(output_file, 'r') as f:
            resolved = [line.strip() for line in f if line.strip()]
        
        return {
            'status': 'partial',
            'resolved_domains': resolved,
            'count': len(resolved)
        }

