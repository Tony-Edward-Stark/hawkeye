
"""Gospider tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Gospider:
    """Wrapper for gospider web crawler"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "gospider"
    
    def run(self, input_file, output_file):
        """
        Run gospider for web crawling
        
        Args:
            input_file: File with URLs to crawl
            output_file: Path to save discovered URLs
        
        Returns:
            dict: Results with crawled URLs
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install github.com/jaeles-project/gospider@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Build command
        command = [
            self.tool_name,
            '-S', str(input_file),
            '-o', str(Path(output_file).parent),
            '-c', str(self.config.get('threads', 10)),
            '-d', '3',
            '--quiet'
        ]
        
        # Adjust depth
        if self.config.get('quick_mode'):
            command[command.index('-d') + 1] = '2'
        elif self.config.get('deep_mode'):
            command[command.index('-d') + 1] = '5'
        
        # Run the tool
        logger.info(f"[*] Crawling with gospider...")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Gospider creates its own output structure, try to find results
        gospider_dir = Path(output_file).parent
        urls = []
        
        # Look for gospider output files
        for file in gospider_dir.glob('*'):
            if file.is_file() and 'gospider' in file.name.lower():
                try:
                    with open(file, 'r') as f:
                        for line in f:
                            if line.strip().startswith('http'):
                                urls.append(line.strip())
                except:
                    pass
        
        # Save combined results
        if urls:
            with open(output_file, 'w') as f:
                for url in sorted(set(urls)):
                    f.write(f"{url}\n")
            
            logger.info(f"[✓] Crawled {len(urls)} URLs")
            
            return {
                'status': 'success',
                'urls': urls,
                'count': len(urls),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] gospider failed or returned no results")
            return {
                'status': 'failed',
                'urls': [],
                'count': 0
            }
