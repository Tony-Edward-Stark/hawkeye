"""Parallel execution engine"""

import concurrent.futures
from typing import List, Callable, Any
from hawkeye.ui.logger import get_logger

logger = get_logger()

class ParallelExecutor:
    """Execute tasks in parallel"""
    
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
    
    def execute(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """
        Execute multiple tasks in parallel
        
        Args:
            tasks: List of callable functions
            *args, **kwargs: Arguments to pass to each task
        
        Returns:
            List of results from each task
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for task in tasks:
                future = executor.submit(task, *args, **kwargs)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"[!] Task failed: {e}")
                    results.append(None)
        
        return results
    
    def execute_with_args(self, task_args_list: List[tuple]) -> List[Any]:
        """
        Execute tasks with different arguments
        
        Args:
            task_args_list: List of (function, args, kwargs) tuples
        
        Returns:
            List of results
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for task, args, kwargs in task_args_list:
                future = executor.submit(task, *args, **kwargs)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"[!] Task failed: {e}")
                    results.append(None)
        
        return results
