"""
BMAD Time Monitor - Time tracking and monitoring for BMAD tasks
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BMadTimeMonitor:
    """
    Monitors time spent on BMAD tasks and projects
    """
    
    def __init__(self, task_tracker=None, console_formatter=None):
        self.task_tracker = task_tracker
        self.console_formatter = console_formatter
        self.active_sessions = {}
        self.completed_sessions = []
        self.start_time = datetime.now()
        
    def start_task_tracking(self, task_id: str, task_name: str) -> str:
        """Start tracking time for a specific task"""
        session = {
            'task_id': task_id,
            'task_name': task_name,
            'start_time': datetime.now(),
            'status': 'active'
        }
        
        self.active_sessions[task_id] = session
        logger.info(f"Started time tracking for task: {task_name}")
        return f"⏱️ Time tracking started for: {task_name}"
        
    def stop_task_tracking(self, task_id: str) -> str:
        """Stop tracking time for a specific task"""
        if task_id not in self.active_sessions:
            return f"❌ No active session found for task: {task_id}"
            
        session = self.active_sessions[task_id]
        session['end_time'] = datetime.now()
        session['duration'] = session['end_time'] - session['start_time']
        session['status'] = 'completed'
        
        self.completed_sessions.append(session)
        del self.active_sessions[task_id]
        
        duration_str = str(session['duration']).split('.')[0]  # Remove microseconds
        logger.info(f"Completed time tracking for task: {session['task_name']} - Duration: {duration_str}")
        return f"✅ Task completed in {duration_str}: {session['task_name']}"
        
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all currently active time tracking sessions"""
        active = []
        for session in self.active_sessions.values():
            current_duration = datetime.now() - session['start_time']
            active.append({
                'task_id': session['task_id'],
                'task_name': session['task_name'],
                'start_time': session['start_time'],
                'current_duration': str(current_duration).split('.')[0]
            })
        return active
        
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of all tracking sessions"""
        total_completed = len(self.completed_sessions)
        total_active = len(self.active_sessions)
        
        if self.completed_sessions:
            total_time = sum([s['duration'] for s in self.completed_sessions], timedelta())
            avg_time = total_time / total_completed if total_completed > 0 else timedelta()
        else:
            total_time = timedelta()
            avg_time = timedelta()
            
        return {
            'total_completed_tasks': total_completed,
            'total_active_tasks': total_active,
            'total_time_spent': str(total_time).split('.')[0],
            'average_task_time': str(avg_time).split('.')[0],
            'session_start': self.start_time,
            'uptime': str(datetime.now() - self.start_time).split('.')[0]
        }
        
    def format_time_report(self) -> str:
        """Generate a formatted time tracking report"""
        summary = self.get_session_summary()
        active = self.get_active_sessions()
        
        report = "⏱️ **BMAD Time Tracking Report**\n\n"
        
        # Summary
        report += f"📊 **Summary**\n"
        report += f"- Total Completed Tasks: {summary['total_completed_tasks']}\n"
        report += f"- Active Tasks: {summary['total_active_tasks']}\n"
        report += f"- Total Time Spent: {summary['total_time_spent']}\n"
        report += f"- Average Task Time: {summary['average_task_time']}\n"
        report += f"- Session Uptime: {summary['uptime']}\n\n"
        
        # Active Sessions
        if active:
            report += f"🔄 **Active Sessions**\n"
            for session in active:
                report += f"- {session['task_name']}: {session['current_duration']}\n"
            report += "\n"
        
        # Recent Completed
        if self.completed_sessions:
            report += f"✅ **Recently Completed** (Last 5)\n"
            recent = self.completed_sessions[-5:]
            for session in recent:
                duration_str = str(session['duration']).split('.')[0]
                report += f"- {session['task_name']}: {duration_str}\n"
                
        return report


class BMadWorkDaySimulator:
    """
    Simulates work day scenarios for BMAD task planning
    """
    
    def __init__(self, task_tracker=None, console_formatter=None, time_monitor=None):
        self.task_tracker = task_tracker
        self.console_formatter = console_formatter
        self.time_monitor = time_monitor
        self.simulation_scenarios = []
        
    def simulate_task_timeline(self, tasks: List[Dict[str, Any]], work_hours: int = 8) -> Dict[str, Any]:
        """Simulate how tasks would fit into a work day"""
        total_estimated_time = sum([task.get('estimated_hours', 1) for task in tasks])
        
        if total_estimated_time <= work_hours:
            status = "feasible"
            remaining_time = work_hours - total_estimated_time
        else:
            status = "overloaded"
            remaining_time = 0
            
        return {
            'status': status,
            'total_estimated_hours': total_estimated_time,
            'available_hours': work_hours,
            'remaining_hours': remaining_time,
            'tasks_count': len(tasks),
            'recommendation': self._get_recommendation(status, remaining_time)
        }
        
    def _get_recommendation(self, status: str, remaining_time: float) -> str:
        """Get recommendation based on simulation"""
        if status == "feasible" and remaining_time > 2:
            return "✅ Schedule looks good with buffer time"
        elif status == "feasible" and remaining_time <= 2:
            return "⚠️ Tight schedule but achievable"
        else:
            return "❌ Overloaded - consider prioritizing or splitting tasks"
            
    def generate_work_plan(self, tasks: List[Dict[str, Any]]) -> str:
        """Generate a formatted work plan"""
        simulation = self.simulate_task_timeline(tasks)
        
        plan = "📅 **BMAD Work Day Simulation**\n\n"
        plan += f"**Status**: {simulation['recommendation']}\n"
        plan += f"**Estimated Time**: {simulation['total_estimated_hours']}h\n"
        plan += f"**Available Time**: {simulation['available_hours']}h\n"
        plan += f"**Buffer Time**: {simulation['remaining_hours']}h\n\n"
        
        plan += "**Task Timeline**:\n"
        current_time = 9  # 9 AM start
        for i, task in enumerate(tasks, 1):
            estimated = task.get('estimated_hours', 1)
            end_time = current_time + estimated
            plan += f"{i}. {task.get('name', 'Unknown Task')} ({current_time}:00 - {end_time}:00)\n"
            current_time = end_time
            
        return plan