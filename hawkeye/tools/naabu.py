"""Naabu tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Naabu:
    """Wrapper for naabu port scanner"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "naabu"
    
    def run(self, input_file, output_file):
        """
        Run naabu for fast port scanning
        
        Args:
            input_file: File with hosts to scan
            output_file: Path to save results
        
        Returns:
            dict: Results with open ports
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Count hosts for logging
        with open(input_file, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]
        
        # Build command
        command = [
            self.tool_name,
            '-list', str(input_file),
            '-o', str(output_file),
            '-silent'
        ]
        
        # ✅ FIX: Add port range - scan ALL ports or top ports
        if self.config.get('quick_mode'):
            command.extend(['-top-ports', '100'])
            logger.info(f"[*] Quick mode: scanning top 100 ports on {len(hosts)} hosts")
        else:
            # ✅ CRITICAL FIX: Scan ALL 65535 ports (matches manual execution)
            command.extend(['-p', '-'])
            logger.info(f"[*] Scanning ALL ports (1-65535) on {len(hosts)} hosts")
        
        # Add rate limiting
        rate_limit = self.config.get('rate_limit', 1000)  # ✅ FIX: Increased default
        command.extend(['-rate', str(rate_limit)])
        
        # Add threads
        threads = self.config.get('threads', 50)
        command.extend(['-c', str(threads)])
        
        # ✅ FIX: Add retries and timeout
        command.extend(['-retries', '2'])
        command.extend(['-timeout', '10000'])  # 10 seconds per probe
        
        # Run the tool with longer timeout
        logger.info(f"[*] Running fast port scan with naabu...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name,
            timeout=900  # ✅ FIX: 15 min timeout for all ports
        )
        
        # Parse results
        if success and Path(output_file).exists():
            open_ports = []
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        open_ports.append(line.strip())
            
            logger.info(f"[✓] Naabu found {len(open_ports)} open ports across {len(hosts)} hosts")
            
            return {
                'status': 'success',
                'open_ports': open_ports,
                'count': len(open_ports),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] naabu failed or returned no results")
            return {
                'status': 'failed',
                'open_ports': [],
                'count': 0
            }
