
"""Stage 3: Web Discovery"""

from pathlib import Path
from hawkeye.tools.httpx import Httpx
from hawkeye.tools.katana import Katana
from hawkeye.tools.gau import Gau
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
        
        # Get subdomains
        discovery_dir = Path(output_dir) / '01-discovery'
        subdomains_file = discovery_dir / 'resolved_subdomains.txt'
        
        if not subdomains_file.exists():
            subdomains_file = discovery_dir / 'all_subdomains.txt'
        
        if not subdomains_file.exists():
            logger.warning("[!] No subdomains found")
            return {'status': 'skipped', 'reason': 'no_input', 'stage_dir': str(stage_dir)}
        
        # Step 1: HTTP Probing
        live_urls_file = stage_dir / 'httpx_output.txt'
        
        if self._should_run_tool('httpx'):
            logger.info("[*] Step 1/4: HTTP Probing")
            httpx = Httpx(self.config)
            httpx_results = httpx.run(subdomains_file, live_urls_file)
            results['httpx'] = httpx_results
            logger.info("")
        
        # Read live URLs
        live_urls = []
        if live_urls_file.exists():
            with open(live_urls_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and (line.startswith('http://') or line.startswith('https://')):
                        live_urls.append(line)
        
        # Fallback: Create from open ports
        if not live_urls:
            logger.info("[*] Creating URLs from open ports...")
            scanning_dir = Path(output_dir) / '02-scanning'
            naabu_file = scanning_dir / 'naabu_output.txt'
            
            if naabu_file.exists():
                created = set()
                with open(naabu_file, 'r') as f:
                    for line in f:
                        if ':80' in line or ':443' in line or ':8080' in line or ':8443' in line:
                            parts = line.strip().split(':')
                            if len(parts) >= 2:
                                host = parts[0]
                                port = parts[-1]
                                if port in ['443', '8443']:
                                    created.add(f'https://{host}')
                                elif port in ['80', '8080']:
                                    created.add(f'http://{host}')
                
                if created:
                    live_urls = sorted(created)
                    with open(live_urls_file, 'w') as f:
                        for url in live_urls:
                            f.write(f"{url}\n")
                    logger.info(f"[✓] Created {len(live_urls)} URLs from open ports")
        
        if not live_urls:
            logger.warning("[!] No web applications found")
            return {'status': 'completed', 'live_apps': 0, 'total_urls': 0, 'stage_dir': str(stage_dir)}
        
        # Count unique web applications (unique hosts)
        unique_hosts = set()
        for url in live_urls:
            # Extract host from URL
            host = url.split('//')[1].split('/')[0].split(':')[0]
            unique_hosts.add(host)
        
        web_apps_count = len(unique_hosts)
        logger.info(f"[*] Found {len(live_urls)} URLs from {web_apps_count} web applications")
        logger.info("")
        
        all_urls = set(live_urls)
        
        # Step 2: Katana - based on NUMBER OF WEB APPS, not URLs
        if self._should_run_tool('katana') and web_apps_count <= 20 and not self.config.get('quick_mode'):
            logger.info("[*] Step 2/4: Active Crawling (Katana)")
            katana = Katana(self.config)
            katana_output = stage_dir / 'katana_output.txt'
            
            katana_results = katana.run(live_urls_file, katana_output)
            results['katana'] = katana_results
            
            if katana_results.get('status') == 'success':
                katana_urls = katana_results.get('urls', [])
                all_urls.update(katana_urls)
                logger.info(f"[*] Katana added {len(katana_urls)} URLs")
            
            logger.info("")
        else:
            if web_apps_count > 20:
                logger.info(f"[*] Skipping katana ({web_apps_count} web apps > 20 limit)")
            results['katana'] = {'status': 'skipped', 'reason': 'too_many_apps'}
        
        # Step 3: GAU
        if self._should_run_tool('gau') and not self.config.get('quick_mode'):
            logger.info("[*] Step 3/4: Archive Mining (GAU)")
            
            with open(subdomains_file, 'r') as f:
                domains = [line.strip() for line in f if line.strip()][:10]
            
            if domains:
                gau = Gau(self.config)
                gau_output = stage_dir / 'gau_output.txt'
                gau_results = gau.run(domains, gau_output)
                results['gau'] = gau_results
                
                if gau_results.get('status') == 'success':
                    gau_urls = gau_results.get('urls', [])
                    all_urls.update(gau_urls)
                    logger.info(f"[*] GAU added {len(gau_urls)} URLs")
            
            logger.info("")
        
        results['gospider'] = {'status': 'skipped', 'reason': 'unstable'}
        
        # Save combined URLs
        combined_urls_file = stage_dir / 'all_urls.txt'
        with open(combined_urls_file, 'w') as f:
            for url in sorted(all_urls):
                f.write(f"{url}\n")
        
        results['live_apps'] = web_apps_count
        results['total_urls'] = len(all_urls)
        results['urls_file'] = str(combined_urls_file)
        results['stage_dir'] = str(stage_dir)
        
        logger.info("="*60)
        logger.info(f"[✓] Web Discovery Summary:")
        logger.info(f"    • Web applications: {web_apps_count}")
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

