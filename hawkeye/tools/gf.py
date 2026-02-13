
"""GF (grep patterns) tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Gf:
    """Wrapper for gf pattern matching tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "gf"
    
    def run(self, urls_file, output_dir):
        """
        Run gf to find vulnerable patterns in URLs
        
        Args:
            urls_file: File with URLs to analyze
            output_dir: Directory to save pattern matches
        
        Returns:
            dict: Results with pattern matches
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install github.com/tomnomnom/gf@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(urls_file).exists():
            logger.warning(f"[!] URLs file not found: {urls_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Check if gf patterns are installed
        gf_patterns_dir = Path.home() / '.gf'
        if not gf_patterns_dir.exists() or not any(gf_patterns_dir.iterdir()):
            logger.warning("[!] GF patterns not found")
            logger.info("[*] Install: git clone https://github.com/1ndianl33t/Gf-Patterns ~/.gf")
            return {'status': 'failed', 'reason': 'no_patterns'}
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Common vulnerability patterns to search for
        patterns = [
            'xss',
            'sqli',
            'ssrf',
            'redirect',
            'rce',
            'lfi',
            'ssti',
            'idor'
        ]
        
        logger.info(f"[*] Searching for vulnerable patterns with gf...")
        
        results = {}
        total_matches = 0
        
        for pattern in patterns:
            output_file = output_dir / f'gf_{pattern}.txt'
            
            # Build command: cat urls | gf pattern > output
            command = f"cat {urls_file} | {self.tool_name} {pattern} > {output_file}"
            
            # Run gf
            success = self.runner.run_command(
                command,
                tool_name=f"gf-{pattern}",
                shell=True
            )
            
            # Count matches
            if output_file.exists():
                with open(output_file, 'r') as f:
                    matches = [line.strip() for line in f if line.strip()]
                
                if matches:
                    results[pattern] = {
                        'count': len(matches),
                        'output_file': str(output_file)
                    }
                    total_matches += len(matches)
                    logger.info(f"    • {pattern}: {len(matches)} matches")
        
        if total_matches > 0:
            logger.info(f"[✓] Found {total_matches} potential vulnerable patterns")
            
            return {
                'status': 'success',
                'patterns_found': results,
                'total_matches': total_matches,
                'output_dir': str(output_dir)
            }
        else:
            logger.info(f"[✓] No vulnerable patterns detected")
            return {
                'status': 'completed',
                'patterns_found': {},
                'total_matches': 0
            }
