"""Stage 4: Content Discovery"""

from pathlib import Path
from hawkeye.tools.ffuf import Ffuf
from hawkeye.tools.feroxbuster import Feroxbuster
from hawkeye.ui.logger import get_logger

logger = get_logger()

class ContentStage:
    """Content and directory discovery stage"""
    
    def __init__(self, config):
        self.config = config
        self.skip_tools = config.get('skip_tools', [])
        self.only_tools = config.get('only_tools', [])
    
    def execute(self, output_dir):
        """Execute content discovery"""
        results = {}
        stage_dir = Path(output_dir) / '04-content'
        stage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[*] Stage 4: Content Discovery")
        logger.info(f"[*] Output: {stage_dir}")
        logger.info("")
        
        # Get live web apps from web stage
        web_dir = Path(output_dir) / '03-web'
        web_urls_file = web_dir / 'httpx_output.txt'
        
        if not web_urls_file.exists():
            logger.warning("[!] No web applications found from web stage")
            logger.info("[*] Run web discovery stage first")
            return {
                'status': 'skipped',
                'reason': 'no_input',
                'stage_dir': str(stage_dir)
            }
        
        # Count web apps
        with open(web_urls_file, 'r') as f:
            web_apps = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
        
        if not web_apps:
            logger.warning("[!] No valid web applications to scan")
            return {
                'status': 'skipped',
                'reason': 'no_apps',
                'stage_dir': str(stage_dir)
            }
        
        logger.info(f"[*] Scanning {len(web_apps)} web applications")
        logger.info("")
        
        # Get wordlist
        wordlist = self._get_wordlist()
        if not wordlist:
            logger.error("[!] No wordlist found")
            logger.info("[*] Download wordlists: bash scripts/download_wordlists.sh")
            return {
                'status': 'failed',
                'reason': 'no_wordlist',
                'stage_dir': str(stage_dir)
            }
        
        logger.info(f"[*] Using wordlist: {wordlist}")
        logger.info("")
        
        all_paths = set()
        
        # Step 1: Fast fuzzing with ffuf
        if self._should_run_tool('ffuf'):
            logger.info("[*] Step 1/2: Fast Fuzzing (ffuf)")
            ffuf = Ffuf(self.config)
            ffuf_output = stage_dir / 'ffuf_output.txt'
            
            ffuf_results = ffuf.run(web_urls_file, wordlist, ffuf_output)
            results['ffuf'] = ffuf_results
            
            if ffuf_results.get('status') == 'success':
                all_paths.update(ffuf_results.get('paths', []))
            
            logger.info("")
        
        # Step 2: Recursive discovery with feroxbuster
        if self._should_run_tool('feroxbuster'):
            logger.info("[*] Step 2/2: Recursive Discovery (feroxbuster)")
            feroxbuster = Feroxbuster(self.config)
            feroxbuster_output = stage_dir / 'feroxbuster_output.txt'
            
            feroxbuster_results = feroxbuster.run(web_urls_file, wordlist, feroxbuster_output)
            results['feroxbuster'] = feroxbuster_results
            
            if feroxbuster_results.get('status') == 'success':
                all_paths.update(feroxbuster_results.get('paths', []))
            
            logger.info("")
        
        # Save combined paths
        combined_paths_file = stage_dir / 'all_discovered_paths.txt'
        if all_paths:
            with open(combined_paths_file, 'w') as f:
                for path in sorted(all_paths):
                    f.write(f"{path}\n")
        else:
            combined_paths_file.touch()
        
        results['discovered_paths'] = len(all_paths)
        results['paths_file'] = str(combined_paths_file)
        results['stage_dir'] = str(stage_dir)
        
        logger.info("="*60)
        logger.info(f"[✓] Content Discovery Summary:")
        logger.info(f"    • Web apps scanned: {len(web_apps)}")
        logger.info(f"    • Paths discovered: {len(all_paths)}")
        logger.info(f"    • Wordlist used: {wordlist.name}")
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
    
    def _get_wordlist(self):
        """Get appropriate wordlist based on tier"""
        from hawkeye.config import Config
        config = Config()
        
        wordlist = config.get_wordlist_path('directories')
        
        if wordlist and wordlist.exists():
            return wordlist
        
        # Fallback: try to find any wordlist
        project_root = Path(__file__).parent.parent.parent
        for tier in [2, 1, 3]:
            wordlist_path = project_root / 'wordlists' / f'tier{tier}' / 'directories.txt'
            if wordlist_path.exists():
                logger.info(f"[*] Using fallback wordlist: tier{tier}")
                return wordlist_path
        
        return None
