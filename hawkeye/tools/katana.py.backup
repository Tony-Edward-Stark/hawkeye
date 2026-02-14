
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
        
        # Count URLs
        with open(input_file, 'r') as f:
            urls_to_crawl = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
        
        if not urls_to_crawl:
            logger.warning("[!] No valid URLs to crawl")
            return {'status': 'failed', 'reason': 'no_urls'}
        
        # Build command
        command = [
            self.tool_name,
            '-list', str(input_file),
            '-o', str(output_file),
            '-d', '3',  # Depth
            '-jc',  # JavaScript crawling
            '-kf', 'all',  # Known files
            '-ef', 'css,png,jpg,jpeg,gif,svg,ico,woff,woff2',  # Exclude common static files
            '-timeout', '10'
        ]
        
        # Adjust depth for quick/deep mode
        if self.config.get('quick_mode'):
            command[command.index('-d') + 1] = '2'
        elif self.config.get('deep_mode'):
            command[command.index('-d') + 1] = '4'
        
        # Add rate limiting
        rate_limit = self.config.get('rate_limit', 150)
        command.extend(['-rl', str(rate_limit)])
        
        # Add concurrency (lower for stability)
        threads = min(self.config.get('threads', 50), 20)
        command.extend(['-c', str(threads)])
        
        # Run the tool
        logger.info(f"[*] Crawling {len(urls_to_crawl)} web applications...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results
        if Path(output_file).exists() and output_file.stat().st_size > 0:
            urls = set()
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        urls.add(line)
            
            if urls:
                logger.info(f"[✓] Crawled {len(urls)} unique URLs")
                
                return {
                    'status': 'success',
                    'urls': list(urls),
                    'count': len(urls),
                    'output_file': str(output_file)
                }
        
        # If katana found nothing, at least return the input URLs
        logger.warning(f"[!] Katana found no new URLs")
        
        with open(output_file, 'w') as f:
            for url in urls_to_crawl:
                f.write(f"{url}\n")
        
        return {
            'status': 'completed',
            'urls': urls_to_crawl,
            'count': len(urls_to_crawl),
            'output_file': str(output_file)
        }

