"""
BMAD TodoWrite Bridge - Integration with Claude's TodoWrite functionality
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .task_tracker import BMadTaskTracker, BMadTask

logger = logging.getLogger(__name__)


class TodoWriteBridge:
    """Bridge between BMAD Task Tracker and Claude's TodoWrite system"""
    
    def __init__(self, task_tracker: BMadTaskTracker):
        self.task_tracker = task_tracker
        self.claude_todo_mapping: Dict[str, str] = {}  # Claude todo ID -> BMAD task ID
        self.bmad_todo_mapping: Dict[str, str] = {}    # BMAD task ID -> Claude todo ID
    
    def sync_to_claude_todos(self, tasks: List[BMadTask]) -> List[Dict[str, Any]]:
        """Convert BMAD tasks to Claude TodoWrite format"""
        claude_todos = []
        
        for task in tasks:
            # Create Claude-compatible todo item
            claude_todo = {
                "id": f"bmad_{task.id}",
                "content": self._format_task_content(task),
                "status": self._map_status_to_claude(task.status)
            }
            
            claude_todos.append(claude_todo)
            
            # Track mapping
            self.bmad_todo_mapping[task.id] = claude_todo["id"]
            self.claude_todo_mapping[claude_todo["id"]] = task.id
        
        return claude_todos
    
    def _format_task_content(self, task: BMadTask) -> str:
        """Format BMAD task as Claude todo content"""
        content_parts = [task.name]
        
        # Add agent if specified
        if task.agent:
            content_parts.append(f"[{task.agent.upper()}]")
        
        # Add time allocation
        if task.allocated_hours > 0:
            content_parts.append(f"({task.allocated_hours:.1f}h)")
        
        # Add progress if in progress
        if task.status == "in_progress" and task.completed_hours > 0:
            progress = task.get_progress_percentage()
            content_parts.append(f"{progress}%")
        
        # Add today's allocation if due today
        if task.is_due_today():
            today_hours = task.get_today_hours()
            content_parts.append(f"Today: {today_hours:.1f}h")
        
        return " ".join(content_parts)
    
    def _map_status_to_claude(self, bmad_status: str) -> str:
        """Map BMAD status to Claude TodoWrite status"""
        mapping = {
            "pending": "pending",
            "in_progress": "in_progress", 
            "completed": "completed",
            "blocked": "pending"  # Treat blocked as pending in Claude
        }
        return mapping.get(bmad_status, "pending")
    
    def _map_status_from_claude(self, claude_status: str) -> str:
        """Map Claude TodoWrite status to BMAD status"""
        mapping = {
            "pending": "pending",
            "in_progress": "in_progress",
            "completed": "completed"
        }
        return mapping.get(claude_status, "pending")
    
    def sync_from_claude_update(self, claude_todo_id: str, new_status: str, new_content: str = None):
        """Update BMAD task based on Claude TodoWrite changes"""
        bmad_task_id = self.claude_todo_mapping.get(claude_todo_id)
        
        if not bmad_task_id:
            logger.warning(f"No BMAD task found for Claude todo: {claude_todo_id}")
            return
        
        bmad_status = self._map_status_from_claude(new_status)
        
        # Update BMAD task
        updated_task = self.task_tracker.set_task_status(bmad_task_id, bmad_status)
        
        if updated_task:
            logger.info(f"Synced Claude todo update: {claude_todo_id} -> {bmad_task_id} ({bmad_status})")
            
            # If marked as completed in Claude, auto-complete in BMAD
            if new_status == "completed" and updated_task.completed_hours < updated_task.allocated_hours:
                self.task_tracker.update_task_progress(bmad_task_id, updated_task.allocated_hours - updated_task.completed_hours)
    
    def create_claude_todos_for_today(self) -> List[Dict[str, Any]]:
        """Create Claude todos for today's BMAD tasks"""
        today_tasks = self.task_tracker.get_today_tasks()
        return self.sync_to_claude_todos(today_tasks)
    
    def create_claude_todos_for_agent(self, agent: str) -> List[Dict[str, Any]]:
        """Create Claude todos for specific agent's tasks"""
        agent_tasks = self.task_tracker.get_tasks_by_agent(agent)
        active_tasks = [t for t in agent_tasks if t.status in ["pending", "in_progress"]]
        return self.sync_to_claude_todos(active_tasks)
    
    def create_claude_todos_for_project_phase(self, phase_name: str) -> List[Dict[str, Any]]:
        """Create Claude todos for specific project phase"""
        phase_task_ids = self.task_tracker.phases.get(phase_name, [])
        phase_tasks = [self.task_tracker.get_task(tid) for tid in phase_task_ids]
        active_tasks = [t for t in phase_tasks if t and t.status in ["pending", "in_progress"]]
        return self.sync_to_claude_todos(active_tasks)
    
    def get_formatted_task_report(self, format_type: str = "detailed") -> str:
        """Get formatted task report for Claude display"""
        summary = self.task_tracker.get_task_summary()
        
        if format_type == "summary":
            return self._format_summary_report(summary)
        elif format_type == "today":
            return self._format_today_report()
        else:
            return self._format_detailed_report(summary)
    
    def _format_summary_report(self, summary: Dict[str, Any]) -> str:
        """Format a concise summary report"""
        return f"""🎯 **BMAD Task Summary**
        
✅ Progress: {summary['completed_tasks']}/{summary['total_tasks']} tasks ({summary['completion_rate']}%)
⏱️ Hours: {summary['completed_hours']:.1f}/{summary['total_hours']:.1f}h ({summary['progress_percentage']}%)
📅 Today: {summary['today_tasks_count']} tasks ({summary['today_hours']:.1f}h - {summary['capacity_usage']}% capacity)"""
    
    def _format_today_report(self) -> str:
        """Format today's tasks report"""
        today_tasks = self.task_tracker.get_today_tasks()
        
        if not today_tasks:
            return "📅 **No tasks scheduled for today**"
        
        report = f"📅 **Today's BMAD Tasks ({len(today_tasks)} tasks)**\n\n"
        
        for i, task in enumerate(today_tasks, 1):
            status_emoji = {
                "pending": "⏳", 
                "in_progress": "🔄", 
                "completed": "✅", 
                "blocked": "🚫"
            }.get(task.status, "❓")
            
            agent_info = f" [{task.agent.upper()}]" if task.agent else ""
            hours_info = f" ({task.get_today_hours():.1f}h)"
            progress_info = f" - {task.get_progress_percentage()}%" if task.completed_hours > 0 else ""
            
            report += f"{i}. {status_emoji} **{task.name}**{agent_info}{hours_info}{progress_info}\n"
        
        total_hours = sum(t.get_today_hours() for t in today_tasks)
        capacity = int((total_hours / self.task_tracker.max_daily_hours) * 100)
        
        report += f"\n📊 **Total: {total_hours:.1f}h ({capacity}% capacity)**"
        
        return report
    
    def _format_detailed_report(self, summary: Dict[str, Any]) -> str:
        """Format detailed task report"""
        report = f"""📋 **BMAD Task Management Report**
══════════════════════════════════════════════════════

📊 **Overall Progress:**
• Total Tasks: {summary['total_tasks']}
• Completed: {summary['completed_tasks']} ({summary['completion_rate']}%)
• In Progress: {summary['in_progress_tasks']}
• Pending: {summary['pending_tasks']}
• Total Hours: {summary['completed_hours']:.1f}/{summary['total_hours']:.1f} ({summary['progress_percentage']}%)

📅 **Today's Workload:**
• Tasks: {summary['today_tasks_count']}
• Hours: {summary['today_hours']:.1f}h ({summary['capacity_usage']}% capacity)

"""
        
        # Add today's tasks
        today_tasks = self.task_tracker.get_today_tasks()
        if today_tasks:
            report += "🎯 **Today's Tasks:**\n"
            for task in today_tasks:
                status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}.get(task.status, "❓")
                agent_info = f" [{task.agent}]" if task.agent else ""
                report += f"• {status_emoji} {task.name}{agent_info} ({task.get_today_hours():.1f}h)\n"
            report += "\n"
        
        # Add in-progress tasks
        in_progress_tasks = self.task_tracker.get_tasks_by_status("in_progress")
        if in_progress_tasks:
            report += "🔄 **In Progress:**\n"
            for task in in_progress_tasks:
                progress = task.get_progress_percentage()
                agent_info = f" [{task.agent}]" if task.agent else ""
                report += f"• {task.name}{agent_info} - {progress}% ({task.completed_hours:.1f}/{task.allocated_hours:.1f}h)\n"
            report += "\n"
        
        # Add pending high-priority tasks
        pending_tasks = [t for t in self.task_tracker.get_tasks_by_status("pending") if t.allocated_hours >= 4.0]
        if pending_tasks:
            report += "⏳ **Upcoming Major Tasks:**\n"
            for task in pending_tasks[:5]:  # Show top 5
                agent_info = f" [{task.agent}]" if task.agent else ""
                report += f"• {task.name}{agent_info} ({task.allocated_hours:.1f}h)\n"
        
        report += "\n══════════════════════════════════════════════════════"
        
        return report
    
    def auto_update_task_from_agent_context(self, agent: str, task_description: str, hours_spent: float = None):
        """Automatically update task progress based on agent activity"""
        # Find matching task for agent
        agent_tasks = [t for t in self.task_tracker.get_tasks_by_agent(agent) if t.status == "in_progress"]
        
        if not agent_tasks:
            # No active tasks for agent - create a new one
            task_id = f"auto_{agent}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.task_tracker.create_task(
                task_id=task_id,
                name=task_description,
                allocated_hours=hours_spent or 2.0,
                agent=agent
            )
            logger.info(f"Auto-created task for {agent}: {task_description}")
            return
        
        # Update the first matching in-progress task
        target_task = agent_tasks[0]
        if hours_spent:
            self.task_tracker.update_task_progress(target_task.id, hours_spent)
            logger.info(f"Auto-updated task progress for {agent}: +{hours_spent}h")
    
    def suggest_next_tasks(self, agent: str = None) -> List[str]:
        """Suggest next tasks based on current context"""
        suggestions = []
        
        if agent:
            # Get agent-specific suggestions
            agent_tasks = self.task_tracker.get_tasks_by_agent(agent)
            pending_tasks = [t for t in agent_tasks if t.status == "pending"]
            
            if pending_tasks:
                next_task = min(pending_tasks, key=lambda t: t.start_date)
                suggestions.append(f"Continue with {next_task.name} ({next_task.allocated_hours:.1f}h)")
        
        # Get today's suggestions
        today_tasks = self.task_tracker.get_today_tasks()
        incomplete_today = [t for t in today_tasks if t.status != "completed"]
        
        if incomplete_today:
            for task in incomplete_today[:3]:  # Top 3 suggestions
                status_text = "Continue" if task.status == "in_progress" else "Start"
                suggestions.append(f"{status_text}: {task.name} ({task.get_today_hours():.1f}h today)")
        
        return suggestions[:5]  # Return top 5 suggestions