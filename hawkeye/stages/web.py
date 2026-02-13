
"""Stage 3: Web Discovery"""

from pathlib import Path
from hawkeye.tools.httpx import Httpx
from hawkeye.tools.katana import Katana
from hawkeye.tools.gau import Gau
from hawkeye.tools.gospider import Gospider
from hawkeye.ui.logger import get_logger

logger = get_logger()

class WebStage:
    """Web application discovery stage"""
    
    def __init__(self, config):
        self.config = config
        self.skip_tools = config.get('skip_tools', [])
        self.only_tools = config.get('only_tools', [])
    
    def execute(self, output_dir):
        """Execute web discovery"""
        results = {}
        stage_dir = Path(output_dir) / '03-web'
        stage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[*] Stage 3: Web Discovery")
        logger.info(f"[*] Output: {stage_dir}")
        logger.info("")
        
        # Get subdomains from discovery stage
        discovery_dir = Path(output_dir) / '01-discovery'
        subdomains_file = discovery_dir / 'resolved_subdomains.txt'
        
        if not subdomains_file.exists():
            subdomains_file = discovery_dir / 'all_subdomains.txt'
        
        if not subdomains_file.exists():
            logger.warning("[!] No subdomains found from discovery stage")
            return {
                'status': 'skipped',
                'reason': 'no_input',
                'stage_dir': str(stage_dir)
            }
        
        # Step 1: HTTP Probing
        live_urls_file = stage_dir / 'httpx_output.txt'
        
        if self._should_run_tool('httpx'):
            logger.info("[*] Step 1/4: HTTP Probing")
            httpx = Httpx(self.config)
            
            httpx_results = httpx.run(subdomains_file, live_urls_file)
            results['httpx'] = httpx_results
            logger.info("")
        
        # Fallback: Create URLs from open web ports if httpx found nothing
        if not live_urls_file.exists() or live_urls_file.stat().st_size == 0:
            logger.info("[*] Creating URLs from open ports (httpx fallback)...")
            scanning_dir = Path(output_dir) / '02-scanning'
            naabu_file = scanning_dir / 'naabu_output.txt'
            
            if naabu_file.exists():
                live_urls = set()
                with open(naabu_file, 'r') as f:
                    for line in f:
                        if ':80' in line or ':443' in line or ':8080' in line or ':8443' in line:
                            parts = line.strip().split(':')
                            if len(parts) == 2:
                                host, port = parts
                                if port == '443' or port == '8443':
                                    live_urls.add(f'https://{host}')
                                else:
                                    live_urls.add(f'http://{host}')
                
                if live_urls:
                    with open(live_urls_file, 'w') as f:
                        for url in sorted(live_urls):
                            f.write(f"{url}\n")
                    logger.info(f"[✓] Created {len(live_urls)} URLs from open ports")
        
        # Check if we have live URLs to crawl
        if not live_urls_file.exists() or live_urls_file.stat().st_size == 0:
            logger.warning("[!] No web applications found")
            return {
                'status': 'completed',
                'live_apps': 0,
                'total_urls': 0,
                'stage_dir': str(stage_dir)
            }
        
        # Count live apps
        with open(live_urls_file, 'r') as f:
            live_apps = len([line for line in f if line.strip()])
        
        logger.info(f"[*] Found {live_apps} web applications to scan")
        logger.info("")
        
        all_urls = set()
        
        # Add the base URLs
        with open(live_urls_file, 'r') as f:
            for line in f:
                if line.strip():
                    all_urls.add(line.strip())
        
        # Step 2: Active Crawling with Katana (skip if too many URLs or quick mode)
        if self._should_run_tool('katana') and live_apps <= 10 and not self.config.get('quick_mode'):
            logger.info("[*] Step 2/4: Active Crawling (Katana)")
            katana = Katana(self.config)
            katana_output = stage_dir / 'katana_output.txt'
            
            katana_results = katana.run(live_urls_file, katana_output)
            results['katana'] = katana_results
            
            if katana_results.get('status') == 'success':
                all_urls.update(katana_results.get('urls', []))
            
            logger.info("")
        else:
            if live_apps > 10:
                logger.info("[*] Skipping katana (too many targets)")
            results['katana'] = {'status': 'skipped', 'reason': 'too_many_targets'}
        
        # Step 3: Archive Mining with GAU (limit domains)
        if self._should_run_tool('gau') and not self.config.get('quick_mode'):
            logger.info("[*] Step 3/4: Archive Mining (GAU)")
            
            with open(subdomains_file, 'r') as f:
                domains = [line.strip() for line in f if line.strip()][:5]  # Limit to 5
            
            gau = Gau(self.config)
            gau_output = stage_dir / 'gau_output.txt'
            
            gau_results = gau.run(domains, gau_output)
            results['gau'] = gau_results
            
            if gau_results.get('status') == 'success':
                all_urls.update(gau_results.get('urls', []))
            
            logger.info("")
        
        # Step 4: Skip gospider (often problematic)
        results['gospider'] = {'status': 'skipped', 'reason': 'unstable'}
        
        # Save combined URLs
        combined_urls_file = stage_dir / 'all_urls.txt'
        if all_urls:
            with open(combined_urls_file, 'w') as f:
                for url in sorted(all_urls):
                    f.write(f"{url}\n")
        else:
            combined_urls_file.touch()
        
        results['live_apps'] = live_apps
        results['total_urls'] = len(all_urls)
        results['urls_file'] = str(combined_urls_file)
        results['stage_dir'] = str(stage_dir)
        
        logger.info("="*60)
        logger.info(f"[✓] Web Discovery Summary:")
        logger.info(f"    • Web applications: {live_apps}")
        logger.info(f"    • Total URLs: {len(all_urls)}")
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
