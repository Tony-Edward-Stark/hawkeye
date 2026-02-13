
"""GAU (GetAllUrls) tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Gau:
    """Wrapper for gau (GetAllUrls) tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "gau"
    
    def run(self, domains, output_file):
        """
        Run gau to fetch URLs from archives
        
        Args:
            domains: List of domains or file path
            output_file: Path to save URLs
        
        Returns:
            dict: Results with archived URLs
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install github.com/lc/gau/v2/cmd/gau@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Handle input
        if isinstance(domains, (list, tuple)):
            # Create temp file
            temp_input = Path(output_file).parent / 'gau_input.txt'
            with open(temp_input, 'w') as f:
                for domain in domains:
                    f.write(f"{domain}\n")
            input_file = temp_input
        else:
            input_file = domains
        
        if not Path(input_file).exists():
            logger.warning(f"[!] Input not found")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Build command
        command = f"{self.tool_name} --threads {self.config.get('threads', 10)} < {input_file} > {output_file}"
        
        # Run the tool
        logger.info(f"[*] Fetching archived URLs with gau...")
        logger.info(f"[*] Searching Wayback Machine, Common Crawl, AlienVault...")
        
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name,
            shell=True
        )
        
        # Parse results
        if success and Path(output_file).exists():
            urls = []
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        urls.append(line.strip())
            
            logger.info(f"[✓] Found {len(urls)} archived URLs")
            
            return {
                'status': 'success',
                'urls': urls,
                'count': len(urls),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] gau failed or returned no results")
            return {
                'status': 'failed',
                'urls': [],
                'count': 0
            }

