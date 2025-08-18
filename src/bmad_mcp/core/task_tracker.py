"""
BMAD Task Tracker - Comprehensive task management and monitoring system
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import time

logger = logging.getLogger(__name__)


@dataclass
class BMadTask:
    """Represents a BMAD task"""
    id: str
    name: str
    start_date: str
    allocated_hours: float
    completed_hours: float = 0.0
    status: str = "pending"  # pending, in_progress, completed, blocked
    daily_allocation: Dict[str, float] = None
    agent: Optional[str] = None
    project: Optional[str] = None
    dependencies: List[str] = None
    follow_ups: List[Dict[str, Any]] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.daily_allocation is None:
            self.daily_allocation = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.follow_ups is None:
            self.follow_ups = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BMadTask':
        return cls(**data)

    def get_progress_percentage(self) -> int:
        if self.allocated_hours == 0:
            return 0
        return int((self.completed_hours / self.allocated_hours) * 100)

    def is_due_today(self) -> bool:
        today = datetime.now().strftime("%Y-%m-%d")
        return today in self.daily_allocation and self.daily_allocation[today] > 0

    def get_today_hours(self) -> float:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.daily_allocation.get(today, 0.0)


class BMadTaskTracker:
    """Advanced task tracking and management system for BMAD"""
    
    def __init__(self, global_registry=None):
        self.global_registry = global_registry
        self.max_daily_hours = 10.0
        self.tasks: Dict[str, BMadTask] = {}
        self.active_phases: Dict[str, List[str]] = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Phase definitions
        self.phases = {
            "BMAD Integration": ["bmad-pm", "central-hub", "mcp-integration", "pipeline"],
            "Agent Development": ["dev-agent", "pm-agent", "qa-agent", "agent-testing"],
            "Testing": ["system-tests", "integration-tests", "user-acceptance"],
            "Features": ["pdf-export", "templates", "foto-integration"],
            "Deployment": ["staging-deploy", "prod-deploy", "monitoring-setup"]
        }
        
        # Load existing tasks
        self._load_tasks()
        
        # Initialize with current tasks if empty
        if not self.tasks:
            self._initialize_default_tasks()
    
    def _get_tasks_file(self) -> Path:
        """Get the tasks storage file path"""
        if self.global_registry:
            return Path(self.global_registry.global_bmad_home) / "tasks.json"
        else:
            return Path.home() / ".bmad-global" / "tasks.json"
    
    def _load_tasks(self):
        """Load tasks from storage"""
        tasks_file = self._get_tasks_file()
        
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.tasks = {
                    task_id: BMadTask.from_dict(task_data)
                    for task_id, task_data in data.get('tasks', {}).items()
                }
                self.active_phases = data.get('active_phases', {})
                
            except Exception as e:
                logger.error(f"Error loading tasks: {e}")
                self.tasks = {}
                self.active_phases = {}
    
    def _save_tasks(self):
        """Save tasks to storage"""
        tasks_file = self._get_tasks_file()
        tasks_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'tasks': {
                task_id: task.to_dict()
                for task_id, task in self.tasks.items()
            },
            'active_phases': self.active_phases,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
    
    def _initialize_default_tasks(self):
        """Initialize with default BMAD tasks"""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        default_tasks = [
            BMadTask(
                id="mcp-task-management",
                name="MCP Task Management Integration",
                start_date=today,
                allocated_hours=8.0,
                status="in_progress",
                agent="dev",
                daily_allocation={today: 4.0, tomorrow: 4.0}
            ),
            BMadTask(
                id="bmad-agents-completion",
                name="Complete All BMAD Agents",
                start_date=today,
                allocated_hours=6.0,
                status="completed",
                agent="dev",
                daily_allocation={today: 6.0}
            ),
            BMadTask(
                id="notion-integration",
                name="Notion Database Integration",
                start_date=tomorrow,
                allocated_hours=8.0,
                status="pending",
                agent="dev",
                daily_allocation={tomorrow: 4.0}
            )
        ]
        
        for task in default_tasks:
            self.tasks[task.id] = task
        
        self._save_tasks()
    
    def create_task(
        self,
        task_id: str,
        name: str,
        allocated_hours: float,
        agent: Optional[str] = None,
        start_date: Optional[str] = None,
        daily_allocation: Optional[Dict[str, float]] = None
    ) -> BMadTask:
        """Create a new task"""
        
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")
        
        if daily_allocation is None:
            # Auto-allocate evenly starting from start_date
            daily_allocation = self._auto_allocate_hours(allocated_hours, start_date)
        
        task = BMadTask(
            id=task_id,
            name=name,
            start_date=start_date,
            allocated_hours=allocated_hours,
            agent=agent,
            daily_allocation=daily_allocation
        )
        
        self.tasks[task_id] = task
        self._save_tasks()
        
        logger.info(f"Created task: {name} ({task_id})")
        return task
    
    def _auto_allocate_hours(self, total_hours: float, start_date: str) -> Dict[str, float]:
        """Automatically allocate hours across available days"""
        allocation = {}
        remaining_hours = total_hours
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        while remaining_hours > 0:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                daily_load = self.get_daily_load(date_str)
                available_hours = max(0, self.max_daily_hours - daily_load)
                
                if available_hours > 0:
                    hours_to_allocate = min(remaining_hours, available_hours, 4.0)  # Max 4h per day per task
                    allocation[date_str] = hours_to_allocate
                    remaining_hours -= hours_to_allocate
            
            current_date += timedelta(days=1)
            
            # Safety check to prevent infinite loop
            if current_date > datetime.now() + timedelta(days=30):
                break
        
        return allocation
    
    def update_task_progress(self, task_id: str, hours_completed: float) -> Optional[BMadTask]:
        """Update task progress"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        task.completed_hours += hours_completed
        task.updated_at = datetime.now().isoformat()
        
        # Check if task is completed
        if task.completed_hours >= task.allocated_hours:
            task.status = "completed"
            self._generate_follow_up_tasks(task_id)
            self._check_phase_completion()
        elif task.status == "pending":
            task.status = "in_progress"
        
        self._save_tasks()
        
        logger.info(f"Updated task {task.name}: {task.completed_hours}/{task.allocated_hours}h")
        return task
    
    def set_task_status(self, task_id: str, status: str) -> Optional[BMadTask]:
        """Set task status"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        old_status = task.status
        task.status = status
        task.updated_at = datetime.now().isoformat()
        
        if status == "completed" and old_status != "completed":
            self._generate_follow_up_tasks(task_id)
            self._check_phase_completion()
        
        self._save_tasks()
        
        logger.info(f"Task {task.name} status: {old_status} → {status}")
        return task
    
    def get_today_tasks(self) -> List[BMadTask]:
        """Get tasks scheduled for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_tasks = []
        
        for task in self.tasks.values():
            if task.is_due_today():
                today_tasks.append(task)
        
        # Sort by status priority and hours
        today_tasks.sort(key=lambda t: (
            0 if t.status == "in_progress" else 1 if t.status == "pending" else 2,
            -t.get_today_hours()
        ))
        
        return today_tasks
    
    def get_daily_load(self, date_str: str) -> float:
        """Get total hours allocated for a specific date"""
        total_hours = 0.0
        
        for task in self.tasks.values():
            if date_str in task.daily_allocation:
                total_hours += task.daily_allocation[date_str]
        
        return total_hours
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get comprehensive task summary"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == "completed"])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == "in_progress"])
        pending_tasks = len([t for t in self.tasks.values() if t.status == "pending"])
        
        total_hours = sum(t.allocated_hours for t in self.tasks.values())
        completed_hours = sum(t.completed_hours for t in self.tasks.values())
        
        today_tasks = self.get_today_tasks()
        today_hours = sum(t.get_today_hours() for t in today_tasks)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0,
            "total_hours": total_hours,
            "completed_hours": completed_hours,
            "progress_percentage": int((completed_hours / total_hours * 100)) if total_hours > 0 else 0,
            "today_tasks_count": len(today_tasks),
            "today_hours": today_hours,
            "capacity_usage": int((today_hours / self.max_daily_hours * 100)) if self.max_daily_hours > 0 else 0
        }
    
    def _generate_follow_up_tasks(self, completed_task_id: str):
        """Generate follow-up tasks for completed task"""
        task = self.tasks.get(completed_task_id)
        if not task or not task.follow_ups:
            return
        
        next_date = self._find_next_available_date()
        
        for i, follow_up in enumerate(task.follow_ups):
            follow_up_id = f"{completed_task_id}-followup-{i}"
            
            if follow_up_id not in self.tasks:  # Avoid duplicates
                allocation_date = self._add_workdays(next_date, i)
                
                follow_up_task = BMadTask(
                    id=follow_up_id,
                    name=follow_up.get("name", f"Follow-up for {task.name}"),
                    start_date=allocation_date,
                    allocated_hours=follow_up.get("hours", 2.0),
                    agent=task.agent,
                    daily_allocation={allocation_date: follow_up.get("hours", 2.0)}
                )
                
                self.tasks[follow_up_id] = follow_up_task
                logger.info(f"Generated follow-up task: {follow_up_task.name}")
    
    def _find_next_available_date(self) -> str:
        """Find next available date with capacity"""
        current_date = datetime.now() + timedelta(days=1)
        
        while True:
            # Skip weekends
            if current_date.weekday() < 5:
                date_str = current_date.strftime("%Y-%m-%d")
                daily_load = self.get_daily_load(date_str)
                
                if daily_load < self.max_daily_hours:
                    return date_str
            
            current_date += timedelta(days=1)
            
            # Safety check
            if current_date > datetime.now() + timedelta(days=60):
                return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    def _add_workdays(self, date_str: str, days: int) -> str:
        """Add workdays to a date (skip weekends)"""
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
        added_days = 0
        
        while added_days < days:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5:  # Workday
                added_days += 1
        
        return current_date.strftime("%Y-%m-%d")
    
    def _check_phase_completion(self):
        """Check if any project phases are completed"""
        for phase_name, task_ids in self.phases.items():
            relevant_tasks = [self.tasks.get(tid) for tid in task_ids if tid in self.tasks]
            
            if relevant_tasks:
                all_completed = all(task.status == "completed" for task in relevant_tasks if task)
                
                if all_completed and phase_name not in self.active_phases.get("completed", []):
                    if "completed" not in self.active_phases:
                        self.active_phases["completed"] = []
                    
                    self.active_phases["completed"].append(phase_name)
                    logger.info(f"Phase completed: {phase_name}")
                    
                    # Start next phase if available
                    self._start_next_phase(phase_name)
    
    def _start_next_phase(self, completed_phase: str):
        """Start the next phase after completion"""
        phase_order = ["BMAD Integration", "Agent Development", "Testing", "Features", "Deployment"]
        
        try:
            current_index = phase_order.index(completed_phase)
            if current_index + 1 < len(phase_order):
                next_phase = phase_order[current_index + 1]
                logger.info(f"Starting next phase: {next_phase}")
                
                # Could trigger automatic task creation for next phase here
                
        except ValueError:
            pass  # Phase not in standard order
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Task monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
        
        logger.info("Task monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                current_hour = datetime.now().hour
                
                # Progress checks during work hours
                if 9 <= current_hour <= 18:
                    self._check_progress()
                
                # End of day report at 18:00
                if current_hour == 18 and datetime.now().minute == 0:
                    self._generate_daily_report()
                
                # Sleep for 30 minutes
                time.sleep(1800)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def _check_progress(self):
        """Check current progress"""
        in_progress_tasks = [t for t in self.tasks.values() if t.status == "in_progress"]
        
        if in_progress_tasks:
            logger.info(f"Progress check: {len(in_progress_tasks)} tasks in progress")
    
    def _generate_daily_report(self) -> str:
        """Generate daily task report"""
        summary = self.get_task_summary()
        today_tasks = self.get_today_tasks()
        
        report = f"""
📊 BMAD Daily Task Report - {datetime.now().strftime('%Y-%m-%d')}
════════════════════════════════════════════════════════════════

📈 Overall Progress:
• Total Tasks: {summary['total_tasks']} ({summary['completion_rate']}% complete)
• Completed: {summary['completed_tasks']} | In Progress: {summary['in_progress_tasks']} | Pending: {summary['pending_tasks']}
• Hours: {summary['completed_hours']:.1f}/{summary['total_hours']:.1f} ({summary['progress_percentage']}%)

📅 Today's Summary:
• Tasks: {summary['today_tasks_count']} tasks scheduled
• Hours: {summary['today_hours']:.1f}h ({summary['capacity_usage']}% capacity)

🎯 Today's Tasks:
"""
        
        for task in today_tasks:
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}.get(task.status, "❓")
            report += f"• {status_emoji} {task.name} ({task.get_today_hours():.1f}h)\n"
        
        report += "\n════════════════════════════════════════════════════════════════"
        
        logger.info("Daily report generated")
        return report
    
    def get_tasks_by_agent(self, agent: str) -> List[BMadTask]:
        """Get all tasks for a specific agent"""
        return [task for task in self.tasks.values() if task.agent == agent]
    
    def get_tasks_by_status(self, status: str) -> List[BMadTask]:
        """Get all tasks with specific status"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            logger.info(f"Deleted task: {task_id}")
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[BMadTask]:
        """Get a specific task"""
        return self.tasks.get(task_id)
    
    def list_all_tasks(self) -> List[BMadTask]:
        """Get all tasks"""
        return list(self.tasks.values())