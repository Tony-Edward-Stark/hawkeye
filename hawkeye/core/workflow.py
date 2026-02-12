


"""Workflow orchestration engine"""

import os
import sys
from pathlib import Path
from datetime import datetime
from hawkeye.config import Config
from hawkeye.core.stage_manager import StageManager
from hawkeye.core.checkpoint import CheckpointManager
from hawkeye.ui.logger import get_logger

logger = get_logger()

class WorkflowEngine:
    """Main workflow orchestration engine"""
    
    def __init__(self, args):
        self.config = Config(args)
        self.stage_manager = StageManager(self.config)
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Setup output directory
        self.output_dir = Path(self.config.get('output_dir'))
        self.target = self.config.get('target')
        if self.target:
            # Create subdirectory for target
            safe_target = self.target.replace('/', '_').replace(':', '_')
            self.output_dir = self.output_dir / safe_target
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Checkpoint manager
        self.checkpoint_mgr = CheckpointManager(self.output_dir)
    
    def run(self):
        """Execute the workflow"""
        logger.info(f"[*] Target: {self.target}")
        logger.info(f"[*] Mode: {self.config.get('mode')}")
        logger.info(f"[*] Output: {self.output_dir}")
        logger.info("")
        
        self.start_time = datetime.now()
        
        try:
            # Check for resume
            if self.config.get('resume'):
                checkpoint = self.checkpoint_mgr.load_checkpoint()
                if checkpoint:
                    logger.info("[*] Resuming from checkpoint...")
                    completed = checkpoint.get('data', {}).get('completed_stages', [])
                    logger.info(f"[*] Completed stages: {', '.join(completed)}")
            
            # Determine stages to run
            stages = self._get_stages_for_mode()
            
            # Execute stages
            for stage_name in stages:
                if self.config.get('interactive'):
                    response = input(f"\n[?] Execute {stage_name}? [Y/n]: ")
                    if response.lower() == 'n':
                        logger.info(f"[*] Skipping {stage_name}")
                        continue
                
                logger.info(f"\n{'='*60}")
                logger.info(f"[*] Starting Stage: {stage_name.upper()}")
                logger.info(f"{'='*60}\n")
                
                try:
                    stage_results = self.stage_manager.execute_stage(stage_name, self.output_dir)
                    self.results[stage_name] = stage_results
                    
                    # Save checkpoint
                    completed_stages = list(self.results.keys())
                    self.checkpoint_mgr.save_checkpoint(
                        stage_name,
                        {'completed_stages': completed_stages}
                    )
                    
                    logger.info(f"\n[✓] Stage {stage_name} completed")
                except Exception as e:
                    logger.error(f"[!] Stage {stage_name} failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            self.end_time = datetime.now()
            
            # Generate reports
            self._generate_reports()
            
            # Clear checkpoint on successful completion
            self.checkpoint_mgr.clear_checkpoint()
            
            # Print summary
            self._print_summary()
            
        except KeyboardInterrupt:
            logger.warning("\n[!] Scan interrupted by user")
            logger.info("[*] Progress saved. Use --resume to continue")
            sys.exit(1)
        except Exception as e:
            logger.error(f"[!] Workflow error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _get_stages_for_mode(self):
        """Get list of stages based on mode"""
        mode = self.config.get('mode')
        
        mode_mapping = {
            'discover': ['discovery'],
            'scan': ['scanning'],
            'web': ['web'],
            'content': ['content'],
            'vuln': ['vulnerability'],
            'passive': ['discovery'],
            'active': ['scanning', 'web', 'content'],
            'full': ['discovery', 'scanning', 'web', 'content', 'vulnerability']
        }
        
        stages = mode_mapping.get(mode, ['discovery', 'scanning', 'web', 'content', 'vulnerability'])
        
        # Filter completed stages if resuming
        if self.config.get('resume'):
            completed = self.checkpoint_mgr.get_completed_stages()
            stages = [s for s in stages if s not in completed]
        
        return stages
    
    def _generate_reports(self):
        """Generate reports in requested formats"""
        logger.info(f"\n{'='*60}")
        logger.info("[*] Generating Reports")
        logger.info(f"{'='*60}\n")
        
        formats = self.config.get('report_format', ['txt'])
        
        report_data = {
            'target': self.target,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            'results': self.results,
            'config': self.config.config
        }
        
        # For now, just create a simple text report
        try:
            report_file = self.output_dir / 'report.txt'
            with open(report_file, 'w') as f:
                f.write(f"HAWKEYE Reconnaissance Report\n")
                f.write(f"{'='*60}\n\n")
                f.write(f"Target: {self.target}\n")
                f.write(f"Scan Date: {self.start_time}\n")
                f.write(f"Duration: {report_data['duration']:.2f} seconds\n\n")
                f.write(f"{'='*60}\n\n")
                
                for stage, results in self.results.items():
                    f.write(f"\n{stage.upper()} RESULTS:\n")
                    f.write(f"{'-'*40}\n")
                    f.write(f"{results}\n\n")
            
            logger.info(f"[✓] Report saved: {report_file}")
        except Exception as e:
            logger.error(f"[!] Failed to generate report: {e}")
    
    def _print_summary(self):
        """Print scan summary"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        logger.info(f"\n{'='*60}")
        logger.info("[✓] SCAN COMPLETED")
        logger.info(f"{'='*60}")
        logger.info(f"Target: {self.target}")
        logger.info(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
        logger.info(f"Output: {self.output_dir}")
        logger.info(f"{'='*60}\n")
