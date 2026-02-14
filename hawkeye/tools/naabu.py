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
        
        # ✅ OPTIMIZED: Smart port selection based on mode
        if self.config.get('quick_mode'):
            # Quick mode: top 100 ports only
            command.extend(['-top-ports', '100'])
            logger.info(f"[*] Quick mode: scanning top 100 ports on {len(hosts)} hosts")
        elif self.config.get('deep_mode'):
            # Deep mode: all 65535 ports (VERY SLOW - 30+ minutes)
            command.extend(['-p', '-'])
            logger.info(f"[*] Deep mode: scanning ALL 65535 ports on {len(hosts)} hosts")
            logger.warning("[!] This will take 30-60 minutes!")
        else:
            # ✅ DEFAULT (BALANCED): Top 1000 ports + common high ports
            # This is much faster (~5 mins) and finds most ports
            command.extend(['-top-ports', '1000'])
            logger.info(f"[*] Scanning top 1000 ports on {len(hosts)} hosts")
        
        # Add rate limiting (faster for balanced mode)
        if self.config.get('deep_mode'):
            rate_limit = self.config.get('rate_limit', 1000)
        else:
            rate_limit = self.config.get('rate_limit', 2000)  # Faster for top ports
        command.extend(['-rate', str(rate_limit)])
        
        # Add threads
        threads = self.config.get('threads', 50)
        command.extend(['-c', str(threads)])
        
        # Add retries and timeout
        command.extend(['-retries', '2'])
        command.extend(['-timeout', '5000'])  # 5 seconds (faster)
        
        # Run the tool
        logger.info(f"[*] Running fast port scan with naabu...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if success and Path(output_file).exists():
            open_ports = []
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        open_ports.append(line.strip())
            
            # Count unique hosts
            unique_hosts = set()
            for port_line in open_ports:
                if ':' in port_line:
                    host = port_line.split(':')[0]
                    unique_hosts.add(host)
            
            logger.info(f"[✓] Naabu found {len(open_ports)} open ports across {len(unique_hosts)} hosts")
            
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
