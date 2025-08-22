#!/usr/bin/env python3
"""Get list of easy tasks from terminal-bench."""

import re
from pathlib import Path

def get_easy_tasks(tasks_dir="/Users/alicehau/personal_projects/terminal-bench/tasks"):
    """Find all tasks with difficulty: easy using simple regex."""
    easy_tasks = []
    
    tasks_path = Path(tasks_dir)
    for task_dir in tasks_path.iterdir():
        if task_dir.is_dir():
            task_yaml = task_dir / "task.yaml"
            if task_yaml.exists():
                try:
                    with open(task_yaml, 'r') as f:
                        content = f.read()
                        # Simple regex to find difficulty: easy
                        if re.search(r'^difficulty:\s*easy\s*$', content, re.MULTILINE):
                            easy_tasks.append(task_dir.name)
                except Exception as e:
                    print(f"Error reading {task_yaml}: {e}", file=sys.stderr)
    
    return sorted(easy_tasks)

if __name__ == "__main__":
    import sys
    tasks = get_easy_tasks()
    # Print space-separated list for use in shell
    print(" ".join(tasks))