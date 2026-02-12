


"""Configuration management for HAWKEYE"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager"""
    
    def __init__(self, args=None):
        self.config_dir = Path.home() / '.hawkeye'
        self.config_file = self.config_dir / 'config.yaml'
        self.config = self._load_config()
        
        # Override with command line arguments
        if args:
            self._override_with_args(args)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        else:
            # Try to load from project config
            project_config = Path(__file__).parent.parent / 'config' / 'default.yaml'
            if project_config.exists():
                with open(project_config, 'r') as f:
                    return yaml.safe_load(f) or {}
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'target': '',
            'mode': 'full',
            'wordlist_tier': 2,
            'threads': 50,
            'rate_limit': 150,
            'timeout': 10,
            'udp_scan': False,
            'stealth': False,
            'interactive': False,
            'output_dir': './hawkeye-output',
            'report_format': ['txt', 'html'],
            'skip_tools': [],
            'only_tools': [],
            'notify': [],
            'custom_wordlists': {
                'subdomains': '',
                'directories': '',
                'files': '',
                'parameters': ''
            }
        }
    
    def _override_with_args(self, args):
        """Override config with command line arguments"""
        if hasattr(args, 'target') and args.target:
            self.config['target'] = args.target
        if hasattr(args, 'target_list') and args.target_list:
            self.config['target_list'] = args.target_list
        if hasattr(args, 'mode') and args.mode:
            self.config['mode'] = args.mode
        if hasattr(args, 'output') and args.output:
            self.config['output_dir'] = args.output
        if hasattr(args, 'wordlist') and args.wordlist:
            self.config['wordlist_tier'] = args.wordlist
        if hasattr(args, 'format') and args.format:
            if 'all' in args.format:
                self.config['report_format'] = ['txt', 'json', 'html', 'md', 'csv']
            else:
                self.config['report_format'] = args.format
        if hasattr(args, 'interactive') and args.interactive:
            self.config['interactive'] = args.interactive
        if hasattr(args, 'stealth') and args.stealth:
            self.config['stealth'] = args.stealth
        if hasattr(args, 'resume') and args.resume:
            self.config['resume'] = args.resume
        if hasattr(args, 'skip') and args.skip:
            self.config['skip_tools'] = args.skip
        if hasattr(args, 'only') and args.only:
            self.config['only_tools'] = args.only
        if hasattr(args, 'udp') and args.udp:
            self.config['udp_scan'] = args.udp
        if hasattr(args, 'threads') and args.threads:
            self.config['threads'] = args.threads
        if hasattr(args, 'rate') and args.rate:
            self.config['rate_limit'] = args.rate
        if hasattr(args, 'timeout') and args.timeout:
            self.config['timeout'] = args.timeout
        if hasattr(args, 'notify') and args.notify:
            self.config['notify'] = args.notify
        if hasattr(args, 'quick') and args.quick:
            self.config['wordlist_tier'] = 1
            self.config['quick_mode'] = True
        if hasattr(args, 'deep') and args.deep:
            self.config['wordlist_tier'] = 3
            self.config['deep_mode'] = True
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
    
    def save(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get_wordlist_path(self, wordlist_type):
        """Get path to wordlist file"""
        # Check custom wordlists first
        custom_path = self.config.get('custom_wordlists', {}).get(wordlist_type)
        if custom_path and Path(custom_path).exists():
            return Path(custom_path)
        
        # Use tier-based wordlist
        tier = self.config.get('wordlist_tier', 2)
        project_root = Path(__file__).parent.parent
        wordlist_path = project_root / 'wordlists' / f'tier{tier}' / f'{wordlist_type}.txt'
        
        if wordlist_path.exists():
            return wordlist_path
        
        return None
