"""
BMAD Real-time Task Updater - Live task updates and notifications
"""

import asyncio
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any
from .task_tracker import BMadTaskTracker, BMadTask
from .console_formatter import BMadConsoleFormatter

logger = logging.getLogger(__name__)


class BMadRealtimeUpdater:
    """Real-time task update system with live progress tracking"""
    
    def __init__(self, task_tracker: BMadTaskTracker, console_formatter: BMadConsoleFormatter):
        self.task_tracker = task_tracker
        self.console_formatter = console_formatter
        self.realtime_active = False
        self.update_thread = None
        self.update_callbacks: List[Callable] = []
        
        # Real-time tracking settings
        self.update_interval = 30  # Check every 30 seconds for changes
        self.auto_progress_interval = 900  # Auto-progress every 15 minutes during work
        self.work_hours = (9, 18)  # Work hours 9:00 - 18:00
        
        # State tracking
        self.last_task_states: Dict[str, Dict[str, Any]] = {}
        self.last_auto_progress = datetime.now()
        self.session_start_time = datetime.now()
        self.active_work_sessions: Dict[str, datetime] = {}  # task_id -> session_start
        
        # Performance metrics
        self.daily_metrics = {
            "session_start": datetime.now(),
            "total_work_time": 0.0,
            "tasks_completed": 0,
            "tasks_started": 0,
            "progress_updates": 0,
            "interruptions": 0
        }
    
    def start_realtime_updates(self) -> str:
        """Start real-time task monitoring and updates"""
        if self.realtime_active:
            return "⚠️ Real-time updates already active"
        
        self.realtime_active = True
        self.session_start_time = datetime.now()
        self.update_thread = threading.Thread(target=self._realtime_loop, daemon=True)
        self.update_thread.start()
        
        # Initialize task states
        self._capture_initial_states()
        
        startup_msg = self.console_formatter.format_startup_banner()
        startup_msg += "\n🔴 **LIVE MODE ACTIVATED**\n"
        startup_msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        startup_msg += "• Real-time task monitoring active\n"
        startup_msg += "• Auto-progress during work hours\n"
        startup_msg += "• Live status updates every 30 seconds\n"
        startup_msg += "• Performance metrics tracking\n"
        startup_msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        logger.info("Real-time task updates started")
        return startup_msg
    
    def stop_realtime_updates(self) -> str:
        """Stop real-time monitoring"""
        self.realtime_active = False
        if self.update_thread:
            self.update_thread.join(timeout=2)
        
        # Generate session summary
        session_duration = (datetime.now() - self.session_start_time).total_seconds() / 3600
        summary = self._generate_session_summary(session_duration)
        
        logger.info("Real-time task updates stopped")
        return f"⏹️ **LIVE MODE DEACTIVATED**\n\n{summary}"
    
    def add_update_callback(self, callback: Callable[[str, Dict], None]):
        """Add callback for real-time update notifications"""
        self.update_callbacks.append(callback)
    
    def manual_progress_update(self, task_id: str, hours: float, notes: str = "") -> str:
        """Manually update task progress with real-time tracking"""
        task = self.task_tracker.get_task(task_id)
        if not task:
            return f"❌ Task not found: {task_id}"
        
        # Record work session
        if task_id not in self.active_work_sessions:
            self.active_work_sessions[task_id] = datetime.now()
        
        # Update task
        updated_task = self.task_tracker.update_task_progress(task_id, hours)
        if not updated_task:
            return f"❌ Failed to update task: {task_id}"
        
        # Update metrics
        self.daily_metrics["progress_updates"] += 1
        self.daily_metrics["total_work_time"] += hours
        
        # Format live update
        update_output = self._format_live_update(updated_task, hours, notes)
        
        # Notify callbacks
        self._notify_callbacks("progress_update", {
            "task_id": task_id,
            "task_name": updated_task.name,
            "hours_added": hours,
            "total_progress": updated_task.get_progress_percentage(),
            "status": updated_task.status,
            "notes": notes
        })
        
        # Check for task completion
        if updated_task.status == "completed":
            self.daily_metrics["tasks_completed"] += 1
            completion_output = self.console_formatter.format_task_completion(updated_task)
            update_output += f"\n{completion_output}"
        
        return update_output
    
    def start_work_session(self, task_id: str) -> str:
        """Start tracking a work session for a task"""
        task = self.task_tracker.get_task(task_id)
        if not task:
            return f"❌ Task not found: {task_id}"
        
        # Set task to in_progress if not already
        if task.status == "pending":
            self.task_tracker.set_task_status(task_id, "in_progress")
            self.daily_metrics["tasks_started"] += 1
        
        # Record session start
        self.active_work_sessions[task_id] = datetime.now()
        
        output = f"🔄 **Work Session Started**: {task.name}\n"
        output += f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}\n"
        
        if task.agent:
            output += f"🤖 Agent: {task.agent.upper()}\n"
        
        # Show remaining work
        remaining = task.allocated_hours - task.completed_hours
        output += f"📊 Remaining: {remaining:.1f}h ({task.get_progress_percentage()}% complete)\n"
        
        # Notify callbacks
        self._notify_callbacks("session_start", {
            "task_id": task_id,
            "task_name": task.name,
            "start_time": datetime.now().isoformat(),
            "agent": task.agent
        })
        
        return output
    
    def end_work_session(self, task_id: str, hours_worked: Optional[float] = None) -> str:
        """End work session and optionally log hours"""
        if task_id not in self.active_work_sessions:
            return f"❌ No active session for task: {task_id}"
        
        session_start = self.active_work_sessions.pop(task_id)
        session_duration = (datetime.now() - session_start).total_seconds() / 3600
        
        task = self.task_tracker.get_task(task_id)
        if not task:
            return f"❌ Task not found: {task_id}"
        
        # Use provided hours or calculate from session duration
        actual_hours = hours_worked if hours_worked is not None else session_duration
        
        output = f"⏹️ **Work Session Ended**: {task.name}\n"
        output += f"⏰ Duration: {session_duration:.1f}h\n"
        
        if actual_hours > 0:
            # Update progress
            updated_task = self.task_tracker.update_task_progress(task_id, actual_hours)
            if updated_task:
                output += f"📈 Progress Added: {actual_hours:.1f}h\n"
                output += f"📊 Total Progress: {updated_task.completed_hours:.1f}/{updated_task.allocated_hours:.1f}h ({updated_task.get_progress_percentage()}%)\n"
                
                self.daily_metrics["total_work_time"] += actual_hours
                self.daily_metrics["progress_updates"] += 1
        
        # Notify callbacks
        self._notify_callbacks("session_end", {
            "task_id": task_id,
            "task_name": task.name,
            "duration": session_duration,
            "hours_logged": actual_hours,
            "end_time": datetime.now().isoformat()
        })
        
        return output
    
    def get_active_sessions(self) -> str:
        """Get information about currently active work sessions"""
        if not self.active_work_sessions:
            return "📋 **No active work sessions**"
        
        output = f"🔄 **Active Work Sessions** ({len(self.active_work_sessions)}):\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for task_id, start_time in self.active_work_sessions.items():
            task = self.task_tracker.get_task(task_id)
            if task:
                duration = (datetime.now() - start_time).total_seconds() / 3600
                output += f"• **{task.name}**\n"
                output += f"  Started: {start_time.strftime('%H:%M:%S')}\n"
                output += f"  Duration: {duration:.1f}h\n"
                output += f"  Agent: {task.agent.upper() if task.agent else 'Unassigned'}\n"
                output += f"  Progress: {task.get_progress_percentage()}%\n\n"
        
        return output
    
    def get_realtime_status(self) -> Dict[str, Any]:
        """Get current real-time monitoring status"""
        current_time = datetime.now()
        session_duration = (current_time - self.session_start_time).total_seconds() / 3600
        
        return {
            "realtime_active": self.realtime_active,
            "session_duration": session_duration,
            "active_sessions": len(self.active_work_sessions),
            "work_hours_active": self._is_work_hours(current_time),
            "last_auto_progress": self.last_auto_progress.strftime("%H:%M:%S"),
            "daily_metrics": self.daily_metrics.copy(),
            "monitoring_intervals": {
                "update_check": self.update_interval,
                "auto_progress": self.auto_progress_interval
            }
        }
    
    def _realtime_loop(self):
        """Main real-time monitoring loop"""
        logger.info("Real-time update loop started")
        
        while self.realtime_active:
            try:
                current_time = datetime.now()
                
                # Check for task state changes
                self._check_task_changes()
                
                # Auto-progress during work hours
                if self._is_work_hours(current_time):
                    self._check_auto_progress(current_time)
                
                # Update active sessions
                self._update_active_sessions()
                
                # Sleep until next check
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in real-time loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _check_task_changes(self):
        """Check for changes in task states"""
        current_states = {}
        changes_detected = []
        
        for task in self.task_tracker.list_all_tasks():
            current_state = {
                "status": task.status,
                "completed_hours": task.completed_hours,
                "progress": task.get_progress_percentage()
            }
            current_states[task.id] = current_state
            
            # Compare with last known state
            if task.id in self.last_task_states:
                last_state = self.last_task_states[task.id]
                
                # Check for status changes
                if last_state["status"] != current_state["status"]:
                    changes_detected.append({
                        "type": "status_change",
                        "task_id": task.id,
                        "task_name": task.name,
                        "old_status": last_state["status"],
                        "new_status": current_state["status"]
                    })
                
                # Check for progress changes
                if last_state["completed_hours"] != current_state["completed_hours"]:
                    hours_added = current_state["completed_hours"] - last_state["completed_hours"]
                    changes_detected.append({
                        "type": "progress_change",
                        "task_id": task.id,
                        "task_name": task.name,
                        "hours_added": hours_added,
                        "new_progress": current_state["progress"]
                    })
        
        # Update stored states
        self.last_task_states = current_states
        
        # Notify about changes
        for change in changes_detected:
            self._notify_callbacks("task_change", change)
    
    def _check_auto_progress(self, current_time: datetime):
        """Check if auto-progress should be applied"""
        time_since_last = (current_time - self.last_auto_progress).total_seconds()
        
        if time_since_last >= self.auto_progress_interval:
            # Apply small progress to active tasks
            in_progress_tasks = self.task_tracker.get_tasks_by_status("in_progress")
            
            for task in in_progress_tasks:
                if task.id in self.active_work_sessions:
                    # Small incremental progress (0.25h = 15 minutes)
                    self.task_tracker.update_task_progress(task.id, 0.25)
                    
                    self._notify_callbacks("auto_progress", {
                        "task_id": task.id,
                        "task_name": task.name,
                        "hours_added": 0.25,
                        "progress": task.get_progress_percentage()
                    })
            
            self.last_auto_progress = current_time
    
    def _update_active_sessions(self):
        """Update active session information"""
        current_time = datetime.now()
        
        # Check for long-running sessions (>4 hours)
        long_sessions = []
        for task_id, start_time in self.active_work_sessions.items():
            duration = (current_time - start_time).total_seconds() / 3600
            if duration > 4.0:
                long_sessions.append({
                    "task_id": task_id,
                    "duration": duration
                })
        
        # Notify about long sessions
        for session in long_sessions:
            self._notify_callbacks("long_session", session)
    
    def _capture_initial_states(self):
        """Capture initial task states for change detection"""
        for task in self.task_tracker.list_all_tasks():
            self.last_task_states[task.id] = {
                "status": task.status,
                "completed_hours": task.completed_hours,
                "progress": task.get_progress_percentage()
            }
    
    def _format_live_update(self, task: BMadTask, hours_added: float, notes: str) -> str:
        """Format live progress update"""
        progress = task.get_progress_percentage()
        
        output = f"🔴 **LIVE UPDATE**: {task.name}\n"
        output += f"📈 Progress: +{hours_added:.1f}h\n"
        output += f"📊 Total: {task.completed_hours:.1f}/{task.allocated_hours:.1f}h ({progress}%)\n"
        output += f"⏰ Updated: {datetime.now().strftime('%H:%M:%S')}\n"
        
        if notes:
            output += f"📝 Notes: {notes}\n"
        
        if task.agent:
            output += f"🤖 Agent: {task.agent.upper()}\n"
        
        return output
    
    def _is_work_hours(self, current_time: datetime) -> bool:
        """Check if current time is within work hours"""
        return self.work_hours[0] <= current_time.hour < self.work_hours[1]
    
    def _notify_callbacks(self, event_type: str, data: Dict[str, Any]):
        """Notify all registered callbacks"""
        for callback in self.update_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"Error in update callback: {e}")
    
    def _generate_session_summary(self, duration: float) -> str:
        """Generate summary of the real-time session"""
        metrics = self.daily_metrics
        
        summary = f"📊 **Real-time Session Summary**\n"
        summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        summary += f"⏱️ **Duration**: {duration:.1f}h\n"
        summary += f"🎯 **Tasks Started**: {metrics['tasks_started']}\n"
        summary += f"✅ **Tasks Completed**: {metrics['tasks_completed']}\n"
        summary += f"📈 **Progress Updates**: {metrics['progress_updates']}\n"
        summary += f"⏰ **Total Work Time**: {metrics['total_work_time']:.1f}h\n"
        
        if metrics['tasks_completed'] > 0:
            avg_completion_time = metrics['total_work_time'] / metrics['tasks_completed']
            summary += f"📊 **Avg. Task Time**: {avg_completion_time:.1f}h\n"
        
        efficiency = (metrics['total_work_time'] / duration * 100) if duration > 0 else 0
        summary += f"⚡ **Work Efficiency**: {efficiency:.1f}%\n"
        
        summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return summary