
"""Httpx tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Httpx:
    """Wrapper for httpx HTTP probing tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "httpx"
    
    def run(self, input_file, output_file):
        """
        Run httpx for HTTP probing
        
        Args:
            input_file: File with hosts/subdomains to probe
            output_file: Path to save live web applications
        
        Returns:
            dict: Results with live URLs
        """
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Check if input file exists
        if not Path(input_file).exists():
            logger.warning(f"[!] Input file not found: {input_file}")
            return {'status': 'failed', 'reason': 'no_input'}
        
        # Check if input has content
        with open(input_file, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]
        
        if not hosts:
            logger.warning("[!] No hosts to probe")
            return {'status': 'failed', 'reason': 'no_hosts'}
        
        # Build command - simpler version
        command = [
            self.tool_name,
            '-l', str(input_file),
            '-o', str(output_file),
            '-silent',
            '-timeout', '10',
            '-retries', '1',
            '-no-color'
        ]
        
        # Add threads
        threads = min(self.config.get('threads', 50), 25)  # Limit to 25 for stability
        command.extend(['-threads', str(threads)])
        
        # Run the tool - ignore exit code, check output file instead
        logger.info(f"[*] Probing {len(hosts)} hosts for live web applications...")
        
        # Run without checking exit code
        import subprocess
        try:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=300  # 5 minute timeout
            )
        except subprocess.TimeoutExpired:
            logger.warning("[!] httpx timed out")
        except Exception as e:
            logger.warning(f"[!] httpx error: {e}")
        
        # Check if output file has results
        if Path(output_file).exists() and output_file.stat().st_size > 0:
            live_urls = []
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and (line.startswith('http://') or line.startswith('https://')):
                        live_urls.append(line)
            
            if live_urls:
                logger.info(f"[✓] Found {len(live_urls)} live web applications")
                
                return {
                    'status': 'success',
                    'live_urls': live_urls,
                    'count': len(live_urls),
                    'output_file': str(output_file)
                }
        
        # If httpx produced nothing, manually test with curl
        logger.info("[*] httpx found nothing, trying manual HTTP checks...")
        live_urls = []
        
        for host in hosts[:10]:  # Test first 10
            for protocol in ['https', 'http']:
                try:
                    import subprocess
                    result = subprocess.run(
                        ['curl', '-sI', '-m', '5', f'{protocol}://{host}'],
                        capture_output=True,
                        text=True,
                        timeout=6
                    )
                    if 'HTTP/' in result.stdout:
                        url = f'{protocol}://{host}'
                        live_urls.append(url)
                        logger.info(f"    [✓] {url}")
                        break  # Found working protocol, move to next host
                except:
                    pass
        
        if live_urls:
            # Save manual results
            with open(output_file, 'w') as f:
                for url in live_urls:
                    f.write(f"{url}\n")
            
            logger.info(f"[✓] Found {len(live_urls)} live web applications (manual check)")
            
            return {
                'status': 'success',
                'live_urls': live_urls,
                'count': len(live_urls),
                'output_file': str(output_file)
            }
        
        logger.warning(f"[!] No live web applications found")
        Path(output_file).touch()
        return {
            'status': 'completed',
            'live_urls': [],
            'count': 0
        }
