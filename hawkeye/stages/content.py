"""Stage 4: Content Discovery - Fixed to use SecLists directly"""

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

        # Read web apps
        web_apps = []
        with open(web_urls_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and (line.startswith('http://') or line.startswith('https://')):
                    web_apps.append(line)

        if not web_apps:
            logger.warning("[!] No valid web applications to scan")
            return {
                'status': 'skipped',
                'reason': 'no_apps',
                'stage_dir': str(stage_dir)
            }

        logger.info(f"[*] Scanning {len(web_apps)} web applications")
        logger.info("")

        # ✅ FIX: Get wordlist from SecLists (no local wordlists folder needed)
        wordlist = self._get_wordlist()
        if not wordlist:
            logger.error("[!] SecLists not found")
            logger.info("[*] Install SecLists: sudo apt install seclists")
            return {
                'status': 'failed',
                'reason': 'seclists_not_installed',
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
        logger.info(f"    • Wordlist used: {Path(wordlist).name}")
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
        """
        Get wordlist - uses SecLists directly (no local wordlists folder needed)
        
        Returns:
            str: Path to wordlist file, or None if SecLists not found
        """
        # ✅ FIX: SecLists wordlists by mode (no local wordlists needed!)
        seclists_wordlists = {
            'quick': '/usr/share/seclists/Discovery/Web-Content/common.txt',
            'default': '/usr/share/seclists/Discovery/Web-Content/common.txt',
            'deep': '/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt',
        }
        
        # ✅ FIX: Determine wordlist based on mode
        if self.config.get('quick_mode'):
            wordlist = seclists_wordlists['quick']
        elif self.config.get('deep_mode'):
            wordlist = seclists_wordlists['deep']
        else:
            wordlist = seclists_wordlists['default']
        
        # ✅ FIX: Check if SecLists wordlist exists
        if Path(wordlist).exists():
            return wordlist
        
        # ✅ FIX: Try alternative SecLists locations
        alternatives = [
            '/usr/share/wordlists/seclists/Discovery/Web-Content/common.txt',
            '/opt/SecLists/Discovery/Web-Content/common.txt',
            '/usr/share/wordlists/dirb/common.txt',  # Fallback to dirb if available
        ]
        
        for alt in alternatives:
            if Path(alt).exists():
                logger.info(f"[*] Using alternative wordlist: {alt}")
                return alt
        
        # ✅ FIX: SecLists not found - return None and show clear error
        return None
