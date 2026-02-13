"""Stage 2: Port Scanning"""

from pathlib import Path
from hawkeye.tools.naabu import Naabu
from hawkeye.tools.nmap import Nmap
from hawkeye.ui.logger import get_logger

logger = get_logger()

class ScanningStage:
    """Port and service scanning stage"""
    
    def __init__(self, config):
        self.config = config
        self.skip_tools = config.get('skip_tools', [])
        self.only_tools = config.get('only_tools', [])
    
    def execute(self, output_dir):
        """Execute port scanning"""
        results = {}
        stage_dir = Path(output_dir) / '02-scanning'
        stage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[*] Stage 2: Port Scanning")
        logger.info(f"[*] Output: {stage_dir}")
        logger.info("")
        
        # Get subdomains from previous stage
        discovery_dir = Path(output_dir) / '01-discovery'
        subdomains_file = discovery_dir / 'resolved_subdomains.txt'
        
        # Fallback to all_subdomains if resolved doesn't exist
        if not subdomains_file.exists():
            subdomains_file = discovery_dir / 'all_subdomains.txt'
        
        if not subdomains_file.exists():
            logger.warning("[!] No subdomains found from discovery stage")
            logger.info("[*] Run discovery stage first or provide a hosts file")
            return {
                'status': 'skipped',
                'reason': 'no_input',
                'stage_dir': str(stage_dir)
            }
        
        # Count hosts to scan
        with open(subdomains_file, 'r') as f:
            host_count = len([line for line in f if line.strip()])
        
        if host_count == 0:
            logger.warning("[!] No hosts to scan")
            return {
                'status': 'skipped',
                'reason': 'no_hosts',
                'stage_dir': str(stage_dir)
            }
        
        logger.info(f"[*] Scanning {host_count} hosts")
        logger.info("")
        
        # Step 1: Fast port scan with naabu
        if self._should_run_tool('naabu'):
            logger.info("[*] Step 1/2: Fast Port Discovery")
            naabu = Naabu(self.config)
            naabu_output = stage_dir / 'naabu_output.txt'
            
            naabu_results = naabu.run(subdomains_file, naabu_output)
            results['naabu'] = naabu_results
            logger.info("")
        
        # Step 2: Detailed scan with nmap
        if self._should_run_tool('nmap'):
            logger.info("[*] Step 2/2: Detailed Service Detection")
            
            # Use naabu results if available, otherwise use all subdomains
            nmap_input = stage_dir / 'naabu_output.txt'
            if not nmap_input.exists() or nmap_input.stat().st_size == 0:
                logger.info("[*] Using all subdomains for nmap scan")
                nmap_input = subdomains_file
            else:
                # Extract unique hosts from naabu output (format: host:port)
                unique_hosts = set()
                with open(nmap_input, 'r') as f:
                    for line in f:
                        if ':' in line:
                            host = line.split(':')[0].strip()
                            unique_hosts.add(host)
                
                # Create new file with unique hosts
                hosts_for_nmap = stage_dir / 'hosts_with_open_ports.txt'
                with open(hosts_for_nmap, 'w') as f:
                    for host in sorted(unique_hosts):
                        f.write(f"{host}\n")
                
                nmap_input = hosts_for_nmap
                logger.info(f"[*] Scanning {len(unique_hosts)} hosts with open ports")
            
            nmap = Nmap(self.config)
            nmap_output = stage_dir / 'nmap_output.xml'
            
            nmap_results = nmap.run(nmap_input, nmap_output)
            results['nmap'] = nmap_results
            logger.info("")
        
        # Summary
        total_open_ports = 0
        if 'naabu' in results and results['naabu'].get('status') == 'success':
            total_open_ports = results['naabu'].get('count', 0)
        
        nmap_ports = 0
        if 'nmap' in results and results['nmap'].get('status') == 'success':
            nmap_ports = results['nmap'].get('open_ports', 0)
        
        results['total_open_ports'] = total_open_ports
        results['services_detected'] = nmap_ports
        results['stage_dir'] = str(stage_dir)
        
        logger.info("="*60)
        logger.info(f"[✓] Scanning Summary:")
        logger.info(f"    • Hosts scanned: {host_count}")
        logger.info(f"    • Open ports found: {total_open_ports}")
        logger.info(f"    • Services detected: {nmap_ports}")
        logger.info(f"    • Output directory: {stage_dir}")
        logger.info("="*60)
        
        return results
    
    def _should_run_tool(self, tool_name):
        """Check if tool should be run"""
        if self.only_tools and tool_name not in self.only_tools:
            return False
        if tool_name in self.skip_tools:
            return False
        return True
