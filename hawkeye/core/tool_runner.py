
"""Tool execution runner"""

import subprocess
import shlex
from pathlib import Path
from hawkeye.ui.logger import get_logger

logger = get_logger()

class ToolRunner:
    """Executes external tools"""
    
    def __init__(self, config):
        self.config = config
        # Tools that use exit code 2 for "no results" (not errors)
        self.exit_code_2_ok = ['nuclei', 'httpx', 'feroxbuster']
    
    def run_command(self, command, output_file=None, tool_name="", shell=False):
        """
        Run a shell command
        
        Args:
            command: Command string or list
            output_file: Path to save output
            tool_name: Name of tool for logging
            shell: Use shell execution
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"[*] Running: {tool_name if tool_name else 'command'}")
            
            # Prepare command
            if isinstance(command, str) and not shell:
                cmd = shlex.split(command)
            else:
                cmd = command
            
            # Run command
            if output_file:
                with open(output_file, 'w') as f:
                    process = subprocess.Popen(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=shell
                    )
                    _, stderr = process.communicate()
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=shell
                )
                stdout, stderr = process.communicate()
            
            # Check result
            # Exit code 2 is OK for some tools (means "no results found")
            base_tool_name = tool_name.split()[0].split('(')[0].strip()
            
            if process.returncode == 0:
                logger.info(f"[✓] {tool_name} completed successfully")
                return True
            elif process.returncode == 2 and base_tool_name in self.exit_code_2_ok:
                logger.info(f"[✓] {tool_name} completed (no results)")
                return True
            else:
                logger.warning(f"[!] {tool_name} exited with code {process.returncode}")
                if stderr and len(stderr) < 200:
                    logger.debug(f"Error: {stderr}")
                return False
            
        except FileNotFoundError:
            logger.error(f"[!] Tool not found: {tool_name}")
            logger.info(f"[*] Install it or check PATH")
            return False
        except Exception as e:
            logger.error(f"[!] Error running {tool_name}: {e}")
            return False
    
    def check_tool_installed(self, tool_name):
        """Check if a tool is installed and in PATH"""
        try:
            result = subprocess.run(
                ['which', tool_name],
                capture_output=True,
                text=True
            )
            installed = result.returncode == 0
            
            if not installed:
                logger.warning(f"[!] Tool not found: {tool_name}")
            
            return installed
        except Exception:
            return False
    
    def get_tool_version(self, tool_name, version_flag='--version'):
        """Get version of installed tool"""
        try:
            result = subprocess.run(
                [tool_name, version_flag],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception:
            return "Unknown"
