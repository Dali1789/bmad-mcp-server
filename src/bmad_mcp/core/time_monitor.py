"""
BMAD Time Monitor - Time-based monitoring and reminders system
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
from .task_tracker import BMadTaskTracker
from .console_formatter import BMadConsoleFormatter

logger = logging.getLogger(__name__)


class BMadTimeMonitor:
    """Time-based monitoring system with reminders like the local system"""
    
    def __init__(self, task_tracker: BMadTaskTracker, console_formatter: BMadConsoleFormatter):
        self.task_tracker = task_tracker
        self.console_formatter = console_formatter
        self.monitoring_active = False
        self.monitoring_thread = None
        self.reminder_callbacks: List[Callable] = []
        
        # Reminder schedule (like local system)
        self.reminder_schedule = [
            {"time": "09:00", "type": "morning", "message": "🌅 Morning: Start your tasks!"},
            {"time": "13:00", "type": "midday", "message": "🍽️ Midday: Check your progress!"},
            {"time": "16:00", "type": "afternoon", "message": "☕ Afternoon: Final push!"},
            {"time": "18:00", "type": "evening", "message": "🌆 Evening: Update task status!"}
        ]
        
        self.daily_report_time = "18:00"
        self.progress_check_interval = 1800  # 30 minutes like local system
        
        # Track last execution times to prevent duplicates
        self.last_reminder_times: Dict[str, datetime] = {}
        self.last_progress_check = datetime.now()
        self.last_daily_report = None
    
    def start_monitoring(self) -> str:
        """Start the time-based monitoring system"""
        if self.monitoring_active:
            return "⚠️ Monitoring already active"
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        startup_output = self.console_formatter.format_startup_banner()
        today_tasks = self.console_formatter.format_todays_tasks()
        
        logger.info("BMAD Time Monitor started")
        
        return startup_output + "\n" + today_tasks + "\n🔍 **Time Monitor Active**\n" + self._format_monitoring_info()
    
    def stop_monitoring(self) -> str:
        """Stop the monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
        
        logger.info("BMAD Time Monitor stopped")
        return "⏹️ **Time Monitor Stopped**\n   Background monitoring disabled."
    
    def add_reminder_callback(self, callback: Callable[[str, str], None]):
        """Add callback for reminder notifications"""
        self.reminder_callbacks.append(callback)
    
    def _monitoring_loop(self):
        """Main monitoring loop (runs in background thread)"""
        logger.info("Time monitoring loop started")
        
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Check for scheduled reminders
                self._check_reminders(current_time)
                
                # Progress checks during work hours (9-18)
                if 9 <= current_time.hour <= 18:
                    self._check_progress_interval(current_time)
                
                # Daily report check
                self._check_daily_report(current_time)
                
                # Sleep for 1 minute (check frequently for precision)
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _check_reminders(self, current_time: datetime):
        """Check if any reminders should be triggered"""
        current_time_str = current_time.strftime("%H:%M")
        current_date = current_time.date()
        
        for reminder in self.reminder_schedule:
            reminder_time = reminder["time"]
            reminder_type = reminder["type"]
            
            # Check if it's time for this reminder
            if current_time_str == reminder_time:
                # Check if we already sent this reminder today
                last_sent = self.last_reminder_times.get(reminder_type)
                if last_sent and last_sent.date() == current_date:
                    continue  # Already sent today
                
                # Send reminder
                self._send_reminder(reminder_type, reminder["message"])
                self.last_reminder_times[reminder_type] = current_time
    
    def _check_progress_interval(self, current_time: datetime):
        """Check if it's time for a progress check"""
        time_since_last = (current_time - self.last_progress_check).total_seconds()
        
        if time_since_last >= self.progress_check_interval:
            self._send_progress_check()
            self.last_progress_check = current_time
    
    def _check_daily_report(self, current_time: datetime):
        """Check if it's time for the daily report"""
        current_time_str = current_time.strftime("%H:%M")
        current_date = current_time.date()
        
        if current_time_str == self.daily_report_time:
            # Check if we already sent the report today
            if self.last_daily_report and self.last_daily_report.date() == current_date:
                return
            
            self._send_daily_report()
            self.last_daily_report = current_time
    
    def _send_reminder(self, reminder_type: str, message: str):
        """Send a reminder notification"""
        formatted_reminder = self.console_formatter.format_reminder(reminder_type)
        
        logger.info(f"Reminder: {message}")
        
        # Notify callbacks (could be used for UI updates, notifications, etc.)
        for callback in self.reminder_callbacks:
            try:
                callback(reminder_type, formatted_reminder)
            except Exception as e:
                logger.error(f"Error in reminder callback: {e}")
    
    def _send_progress_check(self):
        """Send a progress check notification"""
        progress_output = self.console_formatter.format_progress_check()
        
        logger.info("Progress check performed")
        
        # Notify callbacks
        for callback in self.reminder_callbacks:
            try:
                callback("progress_check", progress_output)
            except Exception as e:
                logger.error(f"Error in progress check callback: {e}")
    
    def _send_daily_report(self):
        """Send the daily report"""
        daily_report = self.console_formatter.format_daily_report()
        
        logger.info("Daily report generated")
        
        # Notify callbacks
        for callback in self.reminder_callbacks:
            try:
                callback("daily_report", daily_report)
            except Exception as e:
                logger.error(f"Error in daily report callback: {e}")
    
    def _format_monitoring_info(self) -> str:
        """Format monitoring status information"""
        next_reminders = self._get_next_reminders()
        
        info = "Background monitoring active:\n"
        info += "• Progress checks every 30 minutes (9:00-18:00)\n"
        info += "• Daily report at 18:00\n"
        info += "• Automatic reminders at:\n"
        
        for reminder in self.reminder_schedule:
            info += f"  - {reminder['time']}: {reminder['message']}\n"
        
        if next_reminders:
            info += f"\n⏰ **Next reminder**: {next_reminders[0]['time']} - {next_reminders[0]['message']}"
        
        return info
    
    def _get_next_reminders(self) -> List[Dict]:
        """Get upcoming reminders for today"""
        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M")
        
        upcoming = []
        for reminder in self.reminder_schedule:
            if reminder["time"] > current_time_str:
                upcoming.append(reminder)
        
        return upcoming
    
    def manual_reminder_check(self) -> str:
        """Manually trigger reminder check (for testing)"""
        current_time = datetime.now()
        self._check_reminders(current_time)
        
        return f"✅ Manual reminder check completed at {current_time.strftime('%H:%M:%S')}"
    
    def manual_progress_check(self) -> str:
        """Manually trigger progress check"""
        progress_output = self.console_formatter.format_progress_check()
        return progress_output
    
    def manual_daily_report(self) -> str:
        """Manually generate daily report"""
        daily_report = self.console_formatter.format_daily_report()
        return daily_report
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status"""
        current_time = datetime.now()
        next_reminders = self._get_next_reminders()
        
        return {
            "active": self.monitoring_active,
            "current_time": current_time.strftime("%H:%M:%S"),
            "work_hours": 9 <= current_time.hour <= 18,
            "next_reminder": next_reminders[0] if next_reminders else None,
            "last_progress_check": self.last_progress_check.strftime("%H:%M:%S") if self.last_progress_check else None,
            "last_daily_report": self.last_daily_report.strftime("%H:%M:%S") if self.last_daily_report else None,
            "reminder_schedule": self.reminder_schedule
        }
    
    def simulate_time_advance(self, target_time: str) -> str:
        """Simulate advancing time to trigger reminders (for testing)"""
        try:
            # Parse target time
            target_hour, target_minute = map(int, target_time.split(':'))
            
            # Create a datetime for today with target time
            now = datetime.now()
            target_datetime = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            
            # Check what would trigger at this time
            results = []
            
            # Check reminders
            for reminder in self.reminder_schedule:
                if reminder["time"] == target_time:
                    formatted_reminder = self.console_formatter.format_reminder(reminder["type"])
                    results.append(f"🔔 **Reminder Triggered**: {reminder['message']}\n{formatted_reminder}")
            
            # Check daily report
            if target_time == self.daily_report_time:
                daily_report = self.console_formatter.format_daily_report()
                results.append(f"📊 **Daily Report Triggered**:\n{daily_report}")
            
            # Check progress check (if during work hours)
            if 9 <= target_hour <= 18:
                progress_check = self.console_formatter.format_progress_check()
                results.append(f"⏰ **Progress Check** (work hours):\n{progress_check}")
            
            if results:
                return f"🎬 **Simulated time advance to {target_time}**:\n\n" + "\n\n".join(results)
            else:
                return f"🎬 **Simulated time advance to {target_time}**: No scheduled events at this time."
                
        except ValueError:
            return f"❌ Invalid time format. Use HH:MM (e.g., '14:30')"
    
    def get_todays_schedule(self) -> str:
        """Get today's complete schedule"""
        output = "📅 **Today's Schedule**:\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Add reminders
        for reminder in self.reminder_schedule:
            output += f"{reminder['time']} - {reminder['message']}\n"
        
        # Add daily report
        output += f"{self.daily_report_time} - 📊 Daily Report\n"
        
        # Add progress checks info
        output += f"\nEvery 30min (9-18h) - ⏰ Progress Check\n"
        
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return output