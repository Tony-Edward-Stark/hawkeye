"""Progress indicators for HAWKEYE"""

from tqdm import tqdm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

class ProgressManager:
    """Manage progress bars and spinners"""
    
    def __init__(self):
        self.progress = None
        self.tasks = {}
    
    def start(self):
        """Start rich progress display"""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )
        self.progress.start()
    
    def stop(self):
        """Stop progress display"""
        if self.progress:
            self.progress.stop()
    
    def add_task(self, name, total=100):
        """Add a new task"""
        if self.progress:
            task_id = self.progress.add_task(name, total=total)
            self.tasks[name] = task_id
            return task_id
        return None
    
    def update_task(self, name, advance=1):
        """Update task progress"""
        if self.progress and name in self.tasks:
            self.progress.update(self.tasks[name], advance=advance)
    
    def complete_task(self, name):
        """Mark task as complete"""
        if self.progress and name in self.tasks:
            self.progress.update(self.tasks[name], completed=True)

def simple_progress(iterable, desc="Processing"):
    """Simple tqdm progress bar"""
    return tqdm(iterable, desc=desc, ncols=100)
