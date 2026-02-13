
"""Nuclei tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Nuclei:
    """Wrapper for nuclei vulnerability scanner"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "nuclei"
    
    def run(self, input_file, output_file):
        """
        Run nuclei for vulnerability scanning
        
        Args:
            input_file: File with URLs to scan
            output_file: Path to save results
        
        Returns:
            dict: Results with vulnerabilities found
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Update templates first
        logger.info("[*] Updating nuclei templates...")
        update_cmd = [self.tool_name, '-update-templates', '-silent']
        self.runner.run_command(update_cmd, tool_name="nuclei-update")
        
        # Build command
        command = [
            self.tool_name,
            '-list', str(input_file),
            '-o', str(output_file),
            '-silent',
            '-json',
            '-stats'
        ]
        
        # Add severity filters based on mode
        if self.config.get('quick_mode'):
            command.extend(['-severity', 'critical,high'])
        elif self.config.get('deep_mode'):
            command.extend(['-severity', 'critical,high,medium,low,info'])
        else:
            command.extend(['-severity', 'critical,high,medium'])
        
        # Add tags for comprehensive scanning
        if self.config.get('deep_mode'):
            command.extend(['-tags', 'cve,exposure,misconfig,vuln'])
        
        # Add rate limiting
        rate_limit = self.config.get('rate_limit', 150)
        command.extend(['-rate-limit', str(rate_limit)])
        
        # Add concurrency
        threads = self.config.get('threads', 25)
        command.extend(['-c', str(threads)])
        
        # Run nuclei
        logger.info(f"[*] Running nuclei vulnerability scanner...")
        logger.info(f"[*] This may take several minutes...")
        
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        vulnerabilities = []
        critical = high = medium = low = info = 0
        
        if success and Path(output_file).exists():
            try:
                import json
                with open(output_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                vuln = json.loads(line)
                                vulnerabilities.append(vuln)
                                
                                # Count by severity
                                severity = vuln.get('info', {}).get('severity', '').lower()
                                if severity == 'critical':
                                    critical += 1
                                elif severity == 'high':
                                    high += 1
                                elif severity == 'medium':
                                    medium += 1
                                elif severity == 'low':
                                    low += 1
                                elif severity == 'info':
                                    info += 1
                            except json.JSONDecodeError:
                                continue
                
                logger.info(f"[✓] Nuclei scan completed")
                logger.info(f"    • Critical: {critical}")
                logger.info(f"    • High: {high}")
                logger.info(f"    • Medium: {medium}")
                logger.info(f"    • Low: {low}")
                logger.info(f"    • Info: {info}")
                
                return {
                    'status': 'success',
                    'vulnerabilities': vulnerabilities,
                    'total': len(vulnerabilities),
                    'critical': critical,
                    'high': high,
                    'medium': medium,
                    'low': low,
                    'info': info,
                    'output_file': str(output_file)
                }
            except Exception as e:
                logger.error(f"[!] Failed to parse nuclei output: {e}")
                return {
                    'status': 'partial',
                    'vulnerabilities': [],
                    'total': 0
                }
        else:
            logger.info(f"[✓] No vulnerabilities found")
            return {
                'status': 'completed',
                'vulnerabilities': [],
                'total': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }

