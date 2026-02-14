"""FFUF tool wrapper with SecLists defaults"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Ffuf:
    """Wrapper for ffuf fuzzer"""
    
    # ✅ FIX: Default SecLists wordlists
    DEFAULT_WORDLISTS = {
        'directories': '/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt',
        'files': '/usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt',
        'common': '/usr/share/seclists/Discovery/Web-Content/common.txt',
        'big': '/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt',
    }
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "ffuf"
    
    def _get_wordlist(self, wordlist_path):
        """
        Get wordlist path, fallback to SecLists if not found
        
        Args:
            wordlist_path: Requested wordlist path
            
        Returns:
            str: Valid wordlist path
        """
        # ✅ FIX: Check if provided wordlist exists and is not empty
        if wordlist_path and Path(wordlist_path).exists():
            size = Path(wordlist_path).stat().st_size
            if size > 0:
                logger.info(f"[*] Using wordlist: {wordlist_path} ({size} bytes)")
                return wordlist_path
            else:
                logger.warning(f"[!] Wordlist is empty: {wordlist_path}")
        
        # ✅ FIX: Fall back to SecLists
        default_wordlist = self.DEFAULT_WORDLISTS['directories']
        
        if Path(default_wordlist).exists():
            logger.info(f"[*] Using default SecLists wordlist: {default_wordlist}")
            return default_wordlist
        else:
            # Try alternative locations
            alternatives = [
                '/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt',
                '/opt/SecLists/Discovery/Web-Content/raft-medium-directories.txt',
                self.DEFAULT_WORDLISTS['common'],  # Smaller fallback
            ]
            
            for alt in alternatives:
                if Path(alt).exists():
                    logger.info(f"[*] Using alternative wordlist: {alt}")
                    return alt
            
            logger.error("[!] No valid wordlist found!")
            logger.error("[!] Install SecLists: sudo apt install seclists")
            return None
    
    def run(self, url, wordlist, output_file):
        """
        Run FFUF for directory/file discovery
        
        Args:
            url: Target URL
            wordlist: Wordlist file path (can be None/empty)
            output_file: Path to save results
        
        Returns:
            dict: Results with discovered paths
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install github.com/ffuf/ffuf/v2@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # ✅ FIX: Get valid wordlist (with SecLists fallback)
        wordlist = self._get_wordlist(wordlist)
        if not wordlist:
            return {'status': 'failed', 'reason': 'no_wordlist'}
        
        # Build command
        command = [
            self.tool_name,
            '-u', url,
            '-w', wordlist,
            '-mc', 'all',                   # Match all status codes
            '-fc', '404',                   # Filter 404
            '-recursion',                   # Enable recursion
            '-recursion-depth', '2',
            '-e', '.php,.html,.htm,.txt,.js,.json,.xml,.bak,.old,.zip',
            '-o', str(output_file),
            '-of', 'json',
            '-t', '50',
            '-timeout', '10',
            '-maxtime', '1800',
            '-rate', '150',
            '-s',                           # Silent
            '-noninteractive',
        ]
        
        # Run the tool
        logger.info(f"[*] Running: ffuf ({url})")
        success = self.runner.run_command(
            command,
            tool_name=f"{self.tool_name} ({url})"
        )
        
        # Parse results
        if success and Path(output_file).exists():
            try:
                import json
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                results = data.get('results', [])
                
                if results:
                    logger.info(f"[✓] ffuf ({url}) found {len(results)} paths")
                else:
                    logger.info(f"[✓] ffuf ({url}) completed (no results)")
                
                return {
                    'status': 'success',
                    'paths': results,
                    'count': len(results),
                    'output_file': str(output_file)
                }
            except Exception as e:
                logger.warning(f"[!] Error parsing ffuf output: {e}")
                return {'status': 'failed', 'paths': [], 'count': 0}
        else:
            logger.warning(f"[!] ffuf ({url}) failed or returned no results")
            return {'status': 'failed', 'paths': [], 'count': 0}
