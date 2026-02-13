
"""Stage 1: Subdomain Discovery"""

from pathlib import Path
from hawkeye.tools.subfinder import Subfinder
from hawkeye.tools.puredns import Puredns
from hawkeye.tools.dnsx import Dnsx
from hawkeye.tools.dnsrecon import Dnsrecon
from hawkeye.ui.logger import get_logger

logger = get_logger()

class DiscoveryStage:
    """Subdomain discovery stage"""
    
    def __init__(self, config):
        self.config = config
        self.target = config.get('target')
        self.skip_tools = config.get('skip_tools', [])
        self.only_tools = config.get('only_tools', [])
    
    def execute(self, output_dir):
        """Execute subdomain discovery"""
        results = {}
        stage_dir = Path(output_dir) / '01-discovery'
        stage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[*] Stage 1: Subdomain Discovery")
        logger.info(f"[*] Target: {self.target}")
        logger.info(f"[*] Output: {stage_dir}")
        logger.info("")
        
        all_subdomains = set()
        
        # Step 1: Subdomain Enumeration with subfinder
        if self._should_run_tool('subfinder'):
            logger.info("[*] Step 1/4: Subdomain Enumeration")
            subfinder = Subfinder(self.config)
            subfinder_output = stage_dir / 'subfinder.txt'
            
            subfinder_results = subfinder.run(self.target, subfinder_output)
            results['subfinder'] = subfinder_results
            
            if subfinder_results.get('status') == 'success':
                all_subdomains.update(subfinder_results.get('subdomains', []))
            
            logger.info("")
        
        # Save all discovered subdomains before resolution
        all_subdomains_file = stage_dir / 'all_subdomains.txt'
        if all_subdomains:
            with open(all_subdomains_file, 'w') as f:
                for subdomain in sorted(all_subdomains):
                    f.write(f"{subdomain}\n")
            logger.info(f"[*] Total subdomains found: {len(all_subdomains)}")
        else:
            all_subdomains_file.touch()
            logger.warning("[!] No subdomains discovered")
        
        # Step 2: DNS Resolution with puredns
        resolved_output = stage_dir / 'resolved_subdomains.txt'
        
        if self._should_run_tool('puredns') and all_subdomains:
            logger.info("[*] Step 2/4: DNS Resolution")
            puredns = Puredns(self.config)
            
            puredns_results = puredns.run(all_subdomains_file, resolved_output)
            results['puredns'] = puredns_results
            logger.info("")
        else:
            # If puredns skipped, copy all subdomains as "resolved"
            if all_subdomains:
                with open(resolved_output, 'w') as f:
                    for subdomain in sorted(all_subdomains):
                        f.write(f"{subdomain}\n")
        
        # Step 3: DNS Enrichment with dnsx
        if self._should_run_tool('dnsx') and resolved_output.exists() and resolved_output.stat().st_size > 0:
            logger.info("[*] Step 3/4: DNS Enrichment")
            dnsx = Dnsx(self.config)
            dnsx_output = stage_dir / 'dnsx_output.txt'
            
            dnsx_results = dnsx.run(resolved_output, dnsx_output)
            results['dnsx'] = dnsx_results
            logger.info("")
        
        # Step 4: Comprehensive DNS Enumeration with dnsrecon
        if self._should_run_tool('dnsrecon'):
            logger.info("[*] Step 4/4: DNS Enumeration")
            dnsrecon = Dnsrecon(self.config)
            dnsrecon_output = stage_dir / 'dnsrecon_output.json'
            
            dnsrecon_results = dnsrecon.run(self.target, dnsrecon_output)
            results['dnsrecon'] = dnsrecon_results
            logger.info("")
        
        # Final summary
        resolved_count = 0
        if resolved_output.exists():
            with open(resolved_output, 'r') as f:
                resolved_count = len([line for line in f if line.strip()])
        
        results['total_subdomains'] = len(all_subdomains)
        results['resolved_subdomains'] = resolved_count
        results['subdomains_file'] = str(all_subdomains_file)
        results['resolved_file'] = str(resolved_output)
        results['stage_dir'] = str(stage_dir)
        
        logger.info("="*60)
        logger.info(f"[✓] Discovery Summary:")
        logger.info(f"    • Total subdomains found: {len(all_subdomains)}")
        logger.info(f"    • Resolved subdomains: {resolved_count}")
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
