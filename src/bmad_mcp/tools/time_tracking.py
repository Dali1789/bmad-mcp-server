"""
BMAD Time Tracking Tools - MCP tools for time and cost tracking
"""

from typing import Dict, Any, Optional
from ..core.time_cost_tracker import BMadTimeCostTracker
from ..core.task_tracker import BMadTaskTracker


class TimeTrackingTools:
    """MCP tools for time and cost tracking"""
    
    def __init__(self, global_registry):
        self.global_registry = global_registry
        self.task_tracker = BMadTaskTracker(global_registry)
        self.time_tracker = BMadTimeCostTracker(global_registry)
    
    async def start_timer(
        self,
        task_id: str,
        agent: str,
        session_type: str = "development",
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start time tracking for a task"""
        try:
            session = self.task_tracker.start_task_timer(
                task_id=task_id,
                agent=agent,
                session_type=session_type,
                description=description
            )
            
            if session:
                return {
                    "success": True,
                    "message": f"Started timer for task: {task_id}",
                    "session_id": session.id,
                    "task_id": task_id,
                    "agent": agent,
                    "start_time": session.start_time,
                    "session_type": session_type
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to start timer for task: {task_id}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error starting timer: {str(e)}"
            }
    
    async def stop_timer(
        self,
        task_id: str,
        ai_model_used: Optional[str] = None,
        tokens_input: int = 0,
        tokens_output: int = 0,
        mark_completed: bool = False
    ) -> Dict[str, Any]:
        """Stop time tracking for a task"""
        try:
            session = self.task_tracker.stop_task_timer(
                task_id=task_id,
                ai_model_used=ai_model_used,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                mark_completed=mark_completed
            )
            
            if session:
                return {
                    "success": True,
                    "message": f"Stopped timer for task: {task_id}",
                    "session_id": session.id,
                    "duration_hours": session.get_duration_hours(),
                    "cost_usd": session.cost_usd,
                    "tokens_used": {
                        "input": session.tokens_input,
                        "output": session.tokens_output
                    },
                    "ai_model": session.ai_model_used
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to stop timer for task: {task_id}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping timer: {str(e)}"
            }
    
    async def get_active_timers(self) -> Dict[str, Any]:
        """Get all currently active timers"""
        try:
            timers = self.task_tracker.get_active_timers()
            
            return {
                "success": True,
                "active_timers": timers,
                "count": len(timers)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting active timers: {str(e)}"
            }
    
    async def get_task_time_summary(self, task_id: str) -> Dict[str, Any]:
        """Get time tracking summary for a specific task"""
        try:
            summary = self.task_tracker.get_task_time_summary(task_id)
            
            if "error" in summary:
                return {
                    "success": False,
                    "message": summary["error"]
                }
            
            return {
                "success": True,
                **summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting task summary: {str(e)}"
            }
    
    async def get_daily_report(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get daily time tracking report"""
        try:
            report = self.task_tracker.get_daily_time_report(date)
            
            return {
                "success": True,
                **report
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating daily report: {str(e)}"
            }
    
    async def get_project_billing(
        self,
        project_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """Get project billing report"""
        try:
            report = self.task_tracker.get_project_billing_report(
                project_id=project_id,
                start_date=start_date,
                end_date=end_date,
                export_format=export_format
            )
            
            return {
                "success": True,
                "format": export_format,
                "report": report
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating billing report: {str(e)}"
            }
    
    async def auto_end_stale_sessions(self, max_hours: int = 8) -> Dict[str, Any]:
        """End sessions that have been running too long"""
        try:
            ended_sessions = self.task_tracker.auto_end_stale_sessions(max_hours)
            
            return {
                "success": True,
                "message": f"Ended {len(ended_sessions)} stale sessions",
                "ended_sessions": [
                    {
                        "session_id": s.id,
                        "task_id": s.task_id,
                        "duration_hours": s.get_duration_hours(),
                        "agent": s.agent
                    }
                    for s in ended_sessions
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error ending stale sessions: {str(e)}"
            }
    
    async def update_model_costs(self, model_costs: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Update AI model costs"""
        try:
            self.time_tracker.ai_model_costs.update(model_costs)
            
            return {
                "success": True,
                "message": "Model costs updated successfully",
                "updated_models": list(model_costs.keys())
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating model costs: {str(e)}"
            }
    
    async def get_model_costs(self) -> Dict[str, Any]:
        """Get current AI model costs"""
        try:
            return {
                "success": True,
                "model_costs": self.time_tracker.ai_model_costs
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting model costs: {str(e)}"
            }
    
    async def cleanup_old_data(self, days_to_keep: int = 365) -> Dict[str, Any]:
        """Clean up old tracking data"""
        try:
            deleted_count = self.time_tracker.cleanup_database(days_to_keep)
            
            return {
                "success": True,
                "message": f"Cleaned up {deleted_count} old records",
                "deleted_count": deleted_count,
                "days_kept": days_to_keep
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error cleaning up data: {str(e)}"
            }