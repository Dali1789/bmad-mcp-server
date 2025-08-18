"""
BMAD Console Formatter - Live console output with beautiful formatting
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .task_tracker import BMadTaskTracker, BMadTask

logger = logging.getLogger(__name__)


class BMadConsoleFormatter:
    """Beautiful console output formatter for BMAD system"""
    
    def __init__(self, task_tracker: BMadTaskTracker):
        self.task_tracker = task_tracker
        
    def format_startup_banner(self) -> str:
        """Format startup banner like local system"""
        current_date = datetime.now().strftime('%d.%m.%Y')
        current_time = datetime.now().strftime('%H:%M')
        
        banner = f"""
🎯 BMAD Task Tracker Active (MCP Server)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {current_date}
⏰ Time: {current_time}
⏱️ Max Daily: {self.task_tracker.max_daily_hours}h
🔧 Mode: MCP Integration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        return banner
    
    def format_todays_tasks(self) -> str:
        """Format today's tasks display"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_tasks = self.task_tracker.get_today_tasks()
        total_hours = sum(t.get_today_hours() for t in today_tasks)
        
        output = f"📋 Today's Tasks ({today}):\n"
        output += "─────────────────────────────────────────────────────\n"
        
        if not today_tasks:
            output += "   No tasks scheduled for today\n"
        else:
            for task in today_tasks:
                progress = task.get_progress_percentage()
                status_emoji = self._get_status_emoji(task.status)
                agent_info = f" [{task.agent.upper()}]" if task.agent else ""
                today_hours = task.get_today_hours()
                
                output += f"• {task.name}{agent_info}\n"
                output += f"  Hours: {today_hours:.1f}h | Progress: {progress}%\n"
                output += f"  Status: {status_emoji} {task.status}\n"
                output += f"  Total: {task.completed_hours:.1f}/{task.allocated_hours:.1f}h\n\n"
        
        capacity_usage = int((total_hours / self.task_tracker.max_daily_hours) * 100)
        output += "─────────────────────────────────────────────────────\n"
        output += f"📊 Total: {total_hours:.1f}h ({capacity_usage}% capacity)\n"
        
        return output
    
    def format_progress_check(self) -> str:
        """Format progress check output"""
        current_time = datetime.now().strftime('%H:%M:%S')
        in_progress_tasks = self.task_tracker.get_tasks_by_status("in_progress")
        
        output = f"\n⏰ Progress Check - {current_time}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if in_progress_tasks:
            output += f"🔄 Tasks in progress ({len(in_progress_tasks)}):\n"
            for task in in_progress_tasks:
                progress = task.get_progress_percentage()
                remaining = task.allocated_hours - task.completed_hours
                output += f"  • {task.name} - {progress}% ({remaining:.1f}h remaining)\n"
        else:
            output += "   No active tasks currently in progress\n"
        
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return output
    
    def format_task_completion(self, task: BMadTask) -> str:
        """Format task completion announcement"""
        output = f"\n✅ Task Completed: {task.name}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"📊 Total Hours: {task.completed_hours:.1f}/{task.allocated_hours:.1f}h\n"
        output += f"🤖 Agent: {task.agent.upper() if task.agent else 'Unassigned'}\n"
        output += f"📅 Completed: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        
        if task.follow_ups:
            output += f"\n🔮 Follow-up tasks generated ({len(task.follow_ups)}):\n"
            for i, follow_up in enumerate(task.follow_ups, 1):
                output += f"  {i}. {follow_up.get('name', 'Unnamed')} ({follow_up.get('hours', 0):.1f}h)\n"
        
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return output
    
    def format_task_update(self, task: BMadTask, hours_added: float) -> str:
        """Format task progress update"""
        progress = task.get_progress_percentage()
        
        output = f"\n📝 Task Update: {task.name}\n"
        output += f"   Progress: {task.completed_hours:.1f}/{task.allocated_hours:.1f}h ({progress}%)\n"
        output += f"   Added: +{hours_added:.1f}h\n"
        
        if task.status == "completed":
            output += "   🎉 Task completed!\n"
        
        return output
    
    def format_daily_report(self) -> str:
        """Format comprehensive daily report"""
        current_date = datetime.now().strftime('%d.%m.%Y')
        summary = self.task_tracker.get_task_summary()
        today_tasks = self.task_tracker.get_today_tasks()
        
        output = f"\n📊 BMAD Daily Report - {current_date}\n"
        output += "════════════════════════════════════════════════════════════════\n\n"
        
        # Overall Progress
        output += "📈 Overall Progress:\n"
        output += f"• Total Tasks: {summary['total_tasks']} ({summary['completion_rate']}% complete)\n"
        output += f"• Completed: {summary['completed_tasks']} | In Progress: {summary['in_progress_tasks']} | Pending: {summary['pending_tasks']}\n"
        output += f"• Hours: {summary['completed_hours']:.1f}/{summary['total_hours']:.1f} ({summary['progress_percentage']}%)\n\n"
        
        # Today's Summary
        output += f"📅 Today's Summary:\n"
        output += f"• Tasks: {summary['today_tasks_count']} tasks scheduled\n"
        output += f"• Hours: {summary['today_hours']:.1f}h ({summary['capacity_usage']}% capacity)\n\n"
        
        # Today's Tasks Detail
        if today_tasks:
            output += "🎯 Today's Tasks:\n"
            for task in today_tasks:
                status_emoji = self._get_status_emoji(task.status)
                today_hours = task.get_today_hours()
                progress = task.get_progress_percentage()
                
                output += f"• {status_emoji} {task.name} ({today_hours:.1f}h) - {progress}%\n"
            
            output += "\n"
        
        # Tomorrow Preview
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_tasks = []
        for task in self.task_tracker.list_all_tasks():
            if tomorrow in task.daily_allocation and task.daily_allocation[tomorrow] > 0:
                tomorrow_tasks.append(task)
        
        if tomorrow_tasks:
            tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')
            output += f"📅 Tomorrow ({tomorrow_date}):\n"
            for task in tomorrow_tasks:
                hours = task.daily_allocation[tomorrow]
                output += f"  • {task.name} ({hours:.1f}h)\n"
            output += "\n"
        
        output += "════════════════════════════════════════════════════════════════\n"
        
        return output
    
    def format_reminder(self, reminder_type: str) -> str:
        """Format reminder messages"""
        current_time = datetime.now().strftime('%H:%M')
        
        reminders = {
            "morning": "🌅 Morning: Start your tasks!",
            "midday": "🍽️ Midday: Check your progress!",
            "afternoon": "☕ Afternoon: Final push!",
            "evening": "🌆 Evening: Update task status!"
        }
        
        message = reminders.get(reminder_type, "🔔 Task Reminder")
        
        output = f"\n🔔 {current_time} - {message}\n"
        output += "─────────────────────────────────────\n"
        
        # Show current active tasks
        in_progress = self.task_tracker.get_tasks_by_status("in_progress")
        today_tasks = [t for t in self.task_tracker.get_today_tasks() if t.status != "completed"]
        
        if today_tasks:
            output += "Current tasks:\n"
            for task in today_tasks[:3]:  # Show top 3
                remaining_today = task.get_today_hours()
                if task.status == "in_progress":
                    remaining_today = max(0, remaining_today - (task.completed_hours % 1))  # Rough estimate
                
                if remaining_today > 0:
                    output += f"  • {task.name} ({remaining_today:.1f}h remaining)\n"
        
        output += "─────────────────────────────────────\n"
        
        return output
    
    def format_phase_completion(self, phase_name: str) -> str:
        """Format phase completion announcement"""
        output = f"\n🎉 Phase Completed: {phase_name}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"📅 Completed: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        output += f"📌 Ready to start next phase\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return output
    
    def format_agent_workload(self, agent: str) -> str:
        """Format agent workload summary"""
        agent_tasks = self.task_tracker.get_tasks_by_agent(agent)
        
        if not agent_tasks:
            return f"🤖 **{agent.upper()}**: No assigned tasks\n"
        
        total_hours = sum(t.allocated_hours for t in agent_tasks)
        completed_hours = sum(t.completed_hours for t in agent_tasks)
        active_tasks = len([t for t in agent_tasks if t.status in ["pending", "in_progress"]])
        progress = int((completed_hours / total_hours * 100)) if total_hours > 0 else 0
        
        output = f"🤖 **{agent.upper()}**: {len(agent_tasks)} tasks | {active_tasks} active\n"
        output += f"   Progress: {completed_hours:.1f}/{total_hours:.1f}h ({progress}%)\n"
        
        return output
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for task status"""
        emojis = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'blocked': '🚫'
        }
        return emojis.get(status, '❓')
    
    def format_simulation_start(self) -> str:
        """Format simulation start message"""
        output = "\n🎬 Starting BMAD Work Day Simulation...\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += "This will simulate a typical work day with task updates\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return output
    
    def format_project_status(self, project_id: str) -> str:
        """Format project status overview"""
        project_tasks = [t for t in self.task_tracker.list_all_tasks() if t.project == project_id]
        
        if not project_tasks:
            return f"📁 Project {project_id}: No tasks found\n"
        
        total_hours = sum(t.allocated_hours for t in project_tasks)
        completed_hours = sum(t.completed_hours for t in project_tasks)
        completed_tasks = len([t for t in project_tasks if t.status == "completed"])
        progress = int((completed_hours / total_hours * 100)) if total_hours > 0 else 0
        
        output = f"📁 **Project Status**: {project_id[:8]}...\n"
        output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"📊 Progress: {completed_tasks}/{len(project_tasks)} tasks ({progress}%)\n"
        output += f"⏱️ Hours: {completed_hours:.1f}/{total_hours:.1f}h\n"
        output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return output