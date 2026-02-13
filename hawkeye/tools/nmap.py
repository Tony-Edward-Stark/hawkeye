
"""Nmap tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Nmap:
    """Wrapper for nmap scanner"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "nmap"
    
    def run(self, input_file, output_file):
        """
        Run nmap for detailed service detection
        
        Args:
            input_file: File with hosts to scan
            output_file: Path to save results (XML format)
        
        Returns:
            dict: Results with service information
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: sudo apt install nmap")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Build command
        command = [
            'sudo',  # nmap often needs sudo for SYN scan
            self.tool_name,
            '-iL', str(input_file),  # Input list
            '-sV',  # Service version detection
            '-sC',  # Default scripts
            '-T4',  # Timing template (aggressive)
            '-oX', str(output_file),  # XML output
            '-oN', str(output_file).replace('.xml', '.txt')  # Also text output
        ]
        
        # Add UDP scan if enabled (slow!)
        if self.config.get('udp_scan'):
            command.insert(2, '-sU')
            logger.warning("[!] UDP scan enabled - this will be SLOW")
        
        # Stealth mode
        if self.config.get('stealth'):
            command.extend(['-T2', '--max-rate', '50'])
            logger.info("[*] Stealth mode enabled")
        
        # NSE scripts for comprehensive scanning
        if self.config.get('deep_mode'):
            command.extend([
                '--script', 'default,discovery,vuln,exploit,auth'
            ])
            logger.info("[*] Deep mode: Running comprehensive NSE scripts")
        
        # Run the tool
        logger.info(f"[*] Running detailed service detection with nmap...")
        logger.info(f"[*] This may take several minutes...")
        
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results (basic parsing - XML parsing can be added later)
        if success and Path(output_file).exists():
            logger.info(f"[✓] Nmap scan completed")
            logger.info(f"[*] Results saved to: {output_file}")
            
            # Try to count open ports from text output
            text_output = str(output_file).replace('.xml', '.txt')
            open_ports = 0
            if Path(text_output).exists():
                with open(text_output, 'r') as f:
                    for line in f:
                        if '/tcp' in line and 'open' in line:
                            open_ports += 1
                        elif '/udp' in line and 'open' in line:
                            open_ports += 1
            
            logger.info(f"[✓] Found {open_ports} open ports with services")
            
            return {
                'status': 'success',
                'open_ports': open_ports,
                'output_file': str(output_file),
                'text_output': text_output
            }
        else:
            logger.warning(f"[!] nmap failed or returned no results")
            return {
                'status': 'failed',
                'open_ports': 0
            }
