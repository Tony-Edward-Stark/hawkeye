
"""Stage 1: Subdomain Discovery"""

from pathlib import Path
from hawkeye.tools.subfinder import Subfinder
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
        
        all_subdomains = set()
        
        # Run subfinder if not skipped
        if self._should_run_tool('subfinder'):
            subfinder = Subfinder(self.config)
            subfinder_output = stage_dir / 'subfinder.txt'
            
            subfinder_results = subfinder.run(self.target, subfinder_output)
            results['subfinder'] = subfinder_results
            
            if subfinder_results.get('status') == 'success':
                all_subdomains.update(subfinder_results.get('subdomains', []))
        
        # Save combined results
        combined_file = stage_dir / 'all_subdomains.txt'
        if all_subdomains:
            with open(combined_file, 'w') as f:
                for subdomain in sorted(all_subdomains):
                    f.write(f"{subdomain}\n")
            
            logger.info(f"[✓] Total unique subdomains: {len(all_subdomains)}")
            logger.info(f"[✓] Saved to: {combined_file}")
        else:
            logger.warning("[!] No subdomains found")
            # Create empty file
            combined_file.touch()
        
        results['total_subdomains'] = len(all_subdomains)
        results['subdomains_file'] = str(combined_file)
        results['stage_dir'] = str(stage_dir)
        
        return results
    
    def _should_run_tool(self, tool_name):
        """Check if tool should be run"""
        if self.only_tools and tool_name not in self.only_tools:
            return False
        if tool_name in self.skip_tools:
            return False
        return True

