
"""Katana tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Katana:
    """Wrapper for katana web crawler"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "katana"
    
    def run(self, input_file, output_file):
        """
        Run katana for web crawling
        
        Args:
            input_file: File with URLs to crawl
            output_file: Path to save discovered URLs
        
        Returns:
            dict: Results with crawled URLs
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install github.com/projectdiscovery/katana/cmd/katana@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Build command
        command = [
            self.tool_name,
            '-list', str(input_file),
            '-o', str(output_file),
            '-silent',
            '-jc',  # JavaScript crawling
            '-kf', 'all',  # Known files
            '-d', '3'  # Depth
        ]
        
        # Adjust depth for quick/deep mode
        if self.config.get('quick_mode'):
            command[-1] = '2'  # Shallow crawl
        elif self.config.get('deep_mode'):
            command[-1] = '5'  # Deep crawl
        
        # Add rate limiting
        rate_limit = self.config.get('rate_limit', 150)
        command.extend(['-rl', str(rate_limit)])
        
        # Add concurrency
        threads = self.config.get('threads', 50)
        command.extend(['-c', str(threads)])
        
        # Run the tool
        logger.info(f"[*] Crawling web applications with katana...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if success and Path(output_file).exists():
            urls = []
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        urls.append(line.strip())
            
            logger.info(f"[✓] Crawled {len(urls)} URLs")
            
            return {
                'status': 'success',
                'urls': urls,
                'count': len(urls),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] katana failed or returned no results")
            return {
                'status': 'failed',
                'urls': [],
                'count': 0
            }
