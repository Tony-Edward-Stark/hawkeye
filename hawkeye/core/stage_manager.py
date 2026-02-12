"""Stage execution manager"""

from hawkeye.ui.logger import get_logger

logger = get_logger()

class StageManager:
    """Manages execution of reconnaissance stages"""
    
    def __init__(self, config):
        self.config = config
        self.stages = {}
        self._initialize_stages()
    
    def _initialize_stages(self):
        """Initialize stage instances"""
        try:
            from hawkeye.stages.discovery import DiscoveryStage
            from hawkeye.stages.scanning import ScanningStage
            from hawkeye.stages.web import WebStage
            from hawkeye.stages.content import ContentStage
            from hawkeye.stages.vulnerability import VulnerabilityStage
            
            self.stages = {
                'discovery': DiscoveryStage(self.config),
                'scanning': ScanningStage(self.config),
                'web': WebStage(self.config),
                'content': ContentStage(self.config),
                'vulnerability': VulnerabilityStage(self.config)
            }
        except ImportError as e:
            logger.warning(f"[!] Could not import all stages: {e}")
            logger.info("[*] Some stages may not be available yet")
    
    def execute_stage(self, stage_name, output_dir):
        """
        Execute a specific stage
        
        Args:
            stage_name: Name of stage to execute
            output_dir: Output directory path
        
        Returns:
            dict: Stage results
        """
        if stage_name not in self.stages:
            logger.error(f"[!] Unknown stage: {stage_name}")
            return {}
        
        try:
            stage = self.stages[stage_name]
            results = stage.execute(output_dir)
            return results
        except Exception as e:
            logger.error(f"[!] Error executing stage {stage_name}: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_available_stages(self):
        """Get list of available stages"""
        return list(self.stages.keys())
