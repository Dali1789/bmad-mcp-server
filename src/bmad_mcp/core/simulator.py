"""
BMAD Work Day Simulator - Demo and simulation functions like local system
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .task_tracker import BMadTaskTracker, BMadTask
from .console_formatter import BMadConsoleFormatter
from .time_monitor import BMadTimeMonitor

logger = logging.getLogger(__name__)


class BMadWorkDaySimulator:
    """Simulate work day scenarios for demo and testing purposes"""
    
    def __init__(
        self, 
        task_tracker: BMadTaskTracker, 
        console_formatter: BMadConsoleFormatter,
        time_monitor: BMadTimeMonitor
    ):
        self.task_tracker = task_tracker
        self.console_formatter = console_formatter
        self.time_monitor = time_monitor
        self.simulation_active = False
        self.simulation_log: List[str] = []
    
    async def simulate_work_day(self, speed_factor: float = 1.0) -> str:
        """Simulate a complete work day with realistic task progression"""
        if self.simulation_active:
            return "⚠️ Simulation already running"
        
        self.simulation_active = True
        self.simulation_log = []
        
        try:
            # Start simulation
            start_output = self.console_formatter.format_simulation_start()
            self._log_output(start_output)
            
            # Morning startup (9:00)
            await self._simulate_morning_startup()
            await self._sleep_scaled(2, speed_factor)
            
            # Morning work session (9:30 - 12:00)
            await self._simulate_morning_work()
            await self._sleep_scaled(3, speed_factor)
            
            # Midday check (13:00)
            await self._simulate_midday_check()
            await self._sleep_scaled(2, speed_factor)
            
            # Afternoon work session (13:30 - 16:00)
            await self._simulate_afternoon_work()
            await self._sleep_scaled(3, speed_factor)
            
            # Late afternoon push (16:30 - 18:00)
            await self._simulate_evening_work()
            await self._sleep_scaled(2, speed_factor)
            
            # End of day report (18:00)
            await self._simulate_end_of_day()
            
            # Complete simulation
            completion_msg = "\n🎬 **Work Day Simulation Complete**\n"
            completion_msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            completion_msg += f"📊 Total events simulated: {len(self.simulation_log)}\n"
            completion_msg += f"⏱️ Simulation completed in {datetime.now().strftime('%H:%M:%S')}\n"
            completion_msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            self._log_output(completion_msg)
            
            return self._get_simulation_report()
            
        except Exception as e:
            logger.error(f"Error in work day simulation: {e}")
            return f"❌ Simulation error: {str(e)}"
        finally:
            self.simulation_active = False
    
    async def simulate_task_progression(self, task_id: str, target_hours: float) -> str:
        """Simulate realistic task progression over time"""
        task = self.task_tracker.get_task(task_id)
        if not task:
            return f"❌ Task not found: {task_id}"
        
        output = f"🎬 **Simulating Task Progression**: {task.name}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Simulate work in realistic increments
        increments = [0.5, 1.0, 0.5, 1.5, 1.0, 2.0, 1.0]  # Realistic work sessions
        total_added = 0.0
        
        for i, increment in enumerate(increments):
            if total_added + increment > target_hours:
                increment = target_hours - total_added
            
            if increment <= 0:
                break
            
            # Update task
            updated_task = self.task_tracker.update_task_progress(task_id, increment)
            if updated_task:
                update_output = self.console_formatter.format_task_update(updated_task, increment)
                output += f"\n**Session {i+1}**: {update_output}"
                
                total_added += increment
                
                # Check if task completed
                if updated_task.status == "completed":
                    completion_output = self.console_formatter.format_task_completion(updated_task)
                    output += f"\n{completion_output}"
                    break
            
            # Small delay between sessions
            await asyncio.sleep(0.5)
        
        output += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"📊 **Total Progress**: {total_added:.1f}h added\n"
        
        return output
    
    async def simulate_reminder_cycle(self) -> str:
        """Simulate a full reminder cycle (all 4 daily reminders)"""
        output = "🔔 **Simulating Daily Reminder Cycle**\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        reminder_times = ["09:00", "13:00", "16:00", "18:00"]
        reminder_types = ["morning", "midday", "afternoon", "evening"]
        
        for time_str, reminder_type in zip(reminder_times, reminder_types):
            # Simulate time advancement
            advance_output = self.time_monitor.simulate_time_advance(time_str)
            output += f"\n⏰ **{time_str}**:\n{advance_output}\n"
            
            await asyncio.sleep(1)  # Small delay between reminders
        
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += "✅ **Reminder cycle simulation complete**\n"
        
        return output
    
    async def simulate_phase_completion(self, phase_name: str = "BMAD Integration") -> str:
        """Simulate completing an entire project phase"""
        phase_tasks = self.task_tracker.phases.get(phase_name, [])
        
        if not phase_tasks:
            return f"❌ Phase not found: {phase_name}"
        
        output = f"🎯 **Simulating Phase Completion**: {phase_name}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        completed_count = 0
        
        for task_id in phase_tasks:
            task = self.task_tracker.get_task(task_id)
            if task and task.status != "completed":
                # Complete the task
                remaining_hours = task.allocated_hours - task.completed_hours
                if remaining_hours > 0:
                    updated_task = self.task_tracker.update_task_progress(task_id, remaining_hours)
                    if updated_task and updated_task.status == "completed":
                        completion_output = self.console_formatter.format_task_completion(updated_task)
                        output += f"\n{completion_output}"
                        completed_count += 1
                        
                        await asyncio.sleep(0.5)
        
        # Check phase completion
        self.task_tracker._check_phase_completion()
        
        phase_output = self.console_formatter.format_phase_completion(phase_name)
        output += f"\n{phase_output}"
        
        output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"📊 **Completed {completed_count} tasks in phase: {phase_name}**\n"
        
        return output
    
    async def simulate_agent_workday(self, agent: str, hours: float = 8.0) -> str:
        """Simulate a full workday for a specific agent"""
        agent_tasks = self.task_tracker.get_tasks_by_agent(agent)
        active_tasks = [t for t in agent_tasks if t.status in ["pending", "in_progress"]]
        
        if not active_tasks:
            return f"🤖 **{agent.upper()}**: No active tasks to simulate"
        
        output = f"🤖 **Simulating {agent.upper()} Workday** ({hours}h)\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        remaining_hours = hours
        session_count = 0
        
        while remaining_hours > 0 and active_tasks:
            session_count += 1
            
            # Pick a task (prioritize in_progress, then pending)
            in_progress = [t for t in active_tasks if t.status == "in_progress"]
            current_task = in_progress[0] if in_progress else active_tasks[0]
            
            # Work session (1-3 hours)
            session_hours = min(remaining_hours, 2.5)
            
            output += f"\n**Session {session_count}**: Working on {current_task.name} ({session_hours:.1f}h)\n"
            
            # Update task progress
            updated_task = self.task_tracker.update_task_progress(current_task.id, session_hours)
            if updated_task:
                update_output = self.console_formatter.format_task_update(updated_task, session_hours)
                output += update_output
                
                # Check if completed
                if updated_task.status == "completed":
                    completion_output = self.console_formatter.format_task_completion(updated_task)
                    output += completion_output
                    active_tasks.remove(current_task)
            
            remaining_hours -= session_hours
            await asyncio.sleep(0.3)
        
        # Agent summary
        final_workload = self.console_formatter.format_agent_workload(agent)
        output += f"\n{final_workload}"
        
        output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"✅ **{agent.upper()} workday simulation complete** ({session_count} sessions)\n"
        
        return output
    
    async def simulate_crisis_scenario(self, crisis_type: str = "blocked_task") -> str:
        """Simulate crisis scenarios and recovery"""
        output = f"🚨 **Simulating Crisis Scenario**: {crisis_type}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if crisis_type == "blocked_task":
            # Find an in-progress task and block it
            in_progress_tasks = self.task_tracker.get_tasks_by_status("in_progress")
            if in_progress_tasks:
                task = in_progress_tasks[0]
                self.task_tracker.set_task_status(task.id, "blocked")
                
                output += f"🚫 **Task Blocked**: {task.name}\n"
                output += "📋 Creating workaround task...\n"
                
                # Create workaround task
                workaround_id = f"workaround-{task.id}"
                workaround_task = self.task_tracker.create_task(
                    task_id=workaround_id,
                    name=f"Workaround for {task.name}",
                    allocated_hours=2.0,
                    agent=task.agent
                )
                
                output += f"✅ **Workaround Created**: {workaround_task.name}\n"
                
                await asyncio.sleep(1)
                
                # Simulate working on workaround
                self.task_tracker.update_task_progress(workaround_id, 2.0)
                output += "🔧 **Workaround Completed**\n"
                
                # Unblock original task
                self.task_tracker.set_task_status(task.id, "in_progress")
                output += f"✅ **Task Unblocked**: {task.name}\n"
        
        elif crisis_type == "urgent_request":
            # Create urgent task
            urgent_id = f"urgent-{datetime.now().strftime('%H%M%S')}"
            urgent_task = self.task_tracker.create_task(
                task_id=urgent_id,
                name="URGENT: Critical Bug Fix",
                allocated_hours=4.0,
                agent="dev"
            )
            
            output += f"🔥 **Urgent Task Created**: {urgent_task.name}\n"
            output += "⚡ Prioritizing and working immediately...\n"
            
            await asyncio.sleep(1)
            
            # Fast completion simulation
            self.task_tracker.update_task_progress(urgent_id, 4.0)
            completion_output = self.console_formatter.format_task_completion(urgent_task)
            output += completion_output
        
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += "✅ **Crisis scenario resolved**\n"
        
        return output
    
    def get_simulation_options(self) -> str:
        """Get list of available simulation options"""
        return """🎬 **Available BMAD Simulations**:

1. **simulate_work_day()** - Full work day with realistic progression
2. **simulate_task_progression(task_id, hours)** - Focus on single task
3. **simulate_reminder_cycle()** - All daily reminders (9:00-18:00)
4. **simulate_phase_completion(phase_name)** - Complete project phase
5. **simulate_agent_workday(agent, hours)** - Agent-specific workday
6. **simulate_crisis_scenario(type)** - Crisis handling scenarios

**Crisis Types**:
- 'blocked_task' - Task blocking and workaround
- 'urgent_request' - Emergency task handling

**Example Usage**:
```
bmad_simulate_work_day
bmad_simulate_task_progression('bmad-pm', 4.0)
bmad_simulate_agent_workday('dev', 6.0)
```"""
    
    async def _simulate_morning_startup(self):
        """Simulate morning startup routine"""
        startup_output = "🌅 **Morning Startup (9:00)**\n"
        startup_output += self.time_monitor.simulate_time_advance("09:00")
        self._log_output(startup_output)
        
        # Start some tasks
        pending_tasks = self.task_tracker.get_tasks_by_status("pending")
        if pending_tasks:
            task = pending_tasks[0]
            self.task_tracker.set_task_status(task.id, "in_progress")
            self._log_output(f"🔄 Started working on: {task.name}")
    
    async def _simulate_morning_work(self):
        """Simulate morning work session"""
        work_output = "☕ **Morning Work Session (9:30-12:00)**\n"
        
        # Progress on active tasks
        in_progress = self.task_tracker.get_tasks_by_status("in_progress")
        for task in in_progress[:2]:  # Work on up to 2 tasks
            progress = 1.5
            updated_task = self.task_tracker.update_task_progress(task.id, progress)
            if updated_task:
                update_output = self.console_formatter.format_task_update(updated_task, progress)
                work_output += update_output
        
        self._log_output(work_output)
    
    async def _simulate_midday_check(self):
        """Simulate midday progress check"""
        midday_output = self.time_monitor.simulate_time_advance("13:00")
        self._log_output(midday_output)
    
    async def _simulate_afternoon_work(self):
        """Simulate afternoon work session"""
        work_output = "🌞 **Afternoon Work Session (13:30-16:00)**\n"
        
        # Continue progress on tasks
        in_progress = self.task_tracker.get_tasks_by_status("in_progress")
        for task in in_progress:
            progress = 2.0
            updated_task = self.task_tracker.update_task_progress(task.id, progress)
            if updated_task:
                update_output = self.console_formatter.format_task_update(updated_task, progress)
                work_output += update_output
                
                if updated_task.status == "completed":
                    completion_output = self.console_formatter.format_task_completion(updated_task)
                    work_output += completion_output
        
        self._log_output(work_output)
    
    async def _simulate_evening_work(self):
        """Simulate evening work session"""
        evening_output = "🌆 **Evening Push (16:30-18:00)**\n"
        
        # Final push on remaining tasks
        in_progress = self.task_tracker.get_tasks_by_status("in_progress")
        pending = self.task_tracker.get_tasks_by_status("pending")
        
        # Start a pending task if needed
        if not in_progress and pending:
            task = pending[0]
            self.task_tracker.set_task_status(task.id, "in_progress")
            evening_output += f"🔄 Started: {task.name}\n"
            in_progress = [task]
        
        # Work on active tasks
        for task in in_progress:
            progress = 1.0
            updated_task = self.task_tracker.update_task_progress(task.id, progress)
            if updated_task:
                update_output = self.console_formatter.format_task_update(updated_task, progress)
                evening_output += update_output
        
        self._log_output(evening_output)
    
    async def _simulate_end_of_day(self):
        """Simulate end of day reporting"""
        eod_output = self.time_monitor.simulate_time_advance("18:00")
        self._log_output(eod_output)
    
    def _log_output(self, output: str):
        """Log simulation output"""
        self.simulation_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {output}")
        logger.info(f"Simulation: {output[:100]}...")
    
    def _get_simulation_report(self) -> str:
        """Get complete simulation report"""
        return "\n".join(self.simulation_log)
    
    async def _sleep_scaled(self, seconds: float, speed_factor: float):
        """Sleep with speed scaling for simulations"""
        actual_sleep = seconds / speed_factor
        await asyncio.sleep(actual_sleep)