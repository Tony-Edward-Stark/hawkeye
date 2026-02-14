

"""Subfinder tool wrapper"""

from pathlib import Path
from hawkeye.core.tool_runner import ToolRunner
from hawkeye.ui.logger import get_logger

logger = get_logger()

class Subfinder:
    """Wrapper for subfinder tool"""
    
    def __init__(self, config):
        self.config = config
        self.runner = ToolRunner(config)
        self.tool_name = "subfinder"
        self.target_domain = None
    
    def run(self, target, output_file):
        """
        Run subfinder
        
        Args:
            target: Domain to scan
            output_file: Path to save results
        
        Returns:
            dict: Results with status and file path
        """
        self.target_domain = target
        
        # Check if tool is installed
        if not self.runner.check_tool_installed(self.tool_name):
            logger.error(f"[!] {self.tool_name} is not installed")
            logger.info("[*] Install it with: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest")
            return {'status': 'failed', 'reason': 'tool_not_found'}
        
        # Build command
        command = [
            self.tool_name,
            '-d', target,
            '-o', str(output_file),
            '-all',  # ✅ FIX: Use ALL sources (not just default)
            '-silent'
        ]
        
        # Add rate limiting if configured
        rate_limit = self.config.get('rate_limit')
        if rate_limit:
            command.extend(['-rl', str(rate_limit)])
        
        # Run the tool
        logger.info(f"[*] Running subfinder on {target}")
        success = self.runner.run_command(
            command,
            tool_name=self.tool_name
        )
        
        # Parse results - count actual domains, not log messages
        if success and Path(output_file).exists():
            with open(output_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            # Filter out log messages (lines starting with [)
            subdomains = [line for line in lines if not line.startswith('[')]
            
            # Remove duplicates
            unique_subdomains = list(set(subdomains))
            
            # ✅ FIX: Add common subdomains that might be missed
            # These are standard cPanel/hosting subdomains
            common_subdomains = [
                f'autodiscover.{target}',
                f'cpanel.{target}',
                f'webmail.{target}',
                f'mail.{target}',
                f'www.{target}',
                f'ftp.{target}',
                f'localhost.{target}',
                f'webdisk.{target}',
                f'cpcalendars.{target}',
                f'cpcontacts.{target}',
            ]
            
            # Check which common subdomains are missing
            missing_common = []
            for common_sub in common_subdomains:
                if common_sub not in unique_subdomains:
                    missing_common.append(common_sub)
            
            if missing_common:
                logger.info(f"[*] Checking {len(missing_common)} common subdomains...")
                # Note: We're just adding them to the list
                # Puredns will validate which ones actually exist
                for subdomain in missing_common:
                    unique_subdomains.append(subdomain)
                logger.info(f"[+] Added {len(missing_common)} common subdomains for validation")
            
            # Add root domain if not present
            if target not in unique_subdomains:
                unique_subdomains.append(target)
                logger.info(f"[+] Added root domain: {target}")
            
            # Write back to file with all domains
            with open(output_file, 'w') as f:
                for subdomain in sorted(unique_subdomains):
                    f.write(f"{subdomain}\n")
            
            # Log count (before puredns validation)
            logger.info(f"[✓] Subfinder found {len(subdomains)} subdomains")
            logger.info(f"[*] Total domains to validate: {len(unique_subdomains)} (including common subdomains)")
            
            return {
                'status': 'success',
                'subdomains': unique_subdomains,
                'count': len(unique_subdomains),
                'output_file': str(output_file)
            }
        else:
            logger.warning(f"[!] subfinder failed or returned no results")
            
            # ✅ FIX: Even if subfinder fails, add common subdomains + root
            common_subdomains = [
                target,
                f'www.{target}',
                f'mail.{target}',
                f'webmail.{target}',
                f'ftp.{target}',
                f'cpanel.{target}',
                f'autodiscover.{target}',
            ]
            
            with open(output_file, 'w') as f:
                for subdomain in common_subdomains:
                    f.write(f"{subdomain}\n")
            
            logger.info(f"[*] Added {len(common_subdomains)} common subdomains for validation")
            
            return {
                'status': 'partial',
                'subdomains': common_subdomains,
                'count': len(common_subdomains)
            }

