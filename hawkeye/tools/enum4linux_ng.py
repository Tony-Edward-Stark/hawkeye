"""Enum4linux-ng tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Enum4linuxNg:
    """Wrapper for enum4linux-ng SMB enumeration tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "enum4linux-ng"
    
    def run(self, hosts_file, output_dir):
        """
        Run enum4linux-ng for SMB enumeration
        
        Args:
            hosts_file: File with hosts to enumerate
            output_dir: Directory to save results
        
        Returns:
            dict: Results with SMB enumeration data
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: git clone https://github.com/cddmp/enum4linux-ng.git /opt/enum4linux-ng")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(hosts_file).exists():
            logger.warning(f"[!] Hosts file not found: {hosts_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Read hosts
        with open(hosts_file, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]
        
        if not hosts:
            logger.warning("[!] No hosts to enumerate")
            return {'status': 'failed', 'reason': 'no_hosts'}
        
        logger.info(f"[*] Enumerating {len(hosts)} SMB hosts...")
        
        results = []
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Enumerate each host
        for idx, host in enumerate(hosts, 1):
            logger.info(f"[*] Enumerating [{idx}/{len(hosts)}]: {host}")
            
            output_file = output_dir / f'enum4linux_{host.replace(":", "_")}.json'
            
            # Build command
            command = [
                self.tool_name,
                host,
                '-A',  # All simple enumeration
                '-oJ', str(output_file)  # JSON output
            ]
            
            # Run enum4linux-ng
            success = self.runner.run_command(
                command,
                tool_name=f"{self.tool_name} ({host})"
            )
            
            if success and output_file.exists():
                try:
                    import json
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                        results.append({
                            'host': host,
                            'data': data,
                            'output_file': str(output_file)
                        })
                except Exception as e:
                    logger.warning(f"[!] Failed to parse output for {host}: {e}")
        
        if results:
            logger.info(f"[✓] Enumerated {len(results)} SMB hosts")
            
            return {
                'status': 'success',
                'hosts_enumerated': len(results),
                'results': results,
                'output_dir': str(output_dir)
            }
        else:
            logger.warning(f"[!] No SMB enumeration results")
            return {
                'status': 'completed',
                'hosts_enumerated': 0,
                'results': []
            }
