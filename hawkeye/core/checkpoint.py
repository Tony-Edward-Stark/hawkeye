
"""Checkpoint and resume functionality"""

import json
from pathlib import Path
from datetime import datetime
from hawkeye.ui.logger import get_logger

logger = get_logger()

class CheckpointManager:
    """Manage scan checkpoints for resume functionality"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.checkpoint_file = self.output_dir / '.checkpoint.json'
    
    def save_checkpoint(self, stage, data):
        """
        Save checkpoint
        
        Args:
            stage: Current stage name
            data: Data to save
        """
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'data': data
        }
        
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            logger.debug(f"[*] Checkpoint saved: {stage}")
        except Exception as e:
            logger.error(f"[!] Failed to save checkpoint: {e}")
    
    def load_checkpoint(self):
        """
        Load last checkpoint
        
        Returns:
            dict: Checkpoint data or None
        """
        if not self.checkpoint_file.exists():
            return None
        
        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            logger.info(f"[*] Found checkpoint from: {checkpoint['timestamp']}")
            logger.info(f"[*] Last completed stage: {checkpoint['stage']}")
            return checkpoint
        except Exception as e:
            logger.error(f"[!] Failed to load checkpoint: {e}")
            return None
    
    def clear_checkpoint(self):
        """Clear checkpoint file"""
        try:
            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
                logger.debug("[*] Checkpoint cleared")
        except Exception as e:
            logger.error(f"[!] Failed to clear checkpoint: {e}")
    
    def get_completed_stages(self):
        """Get list of completed stages"""
        checkpoint = self.load_checkpoint()
        if checkpoint:
            return checkpoint.get('data', {}).get('completed_stages', [])
        return []
