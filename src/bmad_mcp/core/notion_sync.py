"""
BMAD Notion Synchronization - Sync tasks with Notion databases
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

from .task_tracker import BMadTaskTracker, BMadTask

logger = logging.getLogger(__name__)


class NotionTaskSync:
    """Synchronize BMAD tasks with Notion databases"""
    
    def __init__(self, task_tracker: BMadTaskTracker, notion_token: str = None):
        self.task_tracker = task_tracker
        self.notion_token = notion_token or os.getenv("NOTION_TOKEN")
        
        # Database IDs from global config
        self.database_ids = {
            "gutachten_tasks": "1765e4b8-4c44-813d-b906-e6b343d745fd",
            "gutachten_projects": "1765e4b8-4c44-811c-92c7-f310901a5b6c",
            "time_tracking": "1765e4b8-4c44-81a4-bbd2-e2fbbf012269",
            "business_resources": "21d5e4b84c44808db635f37c5cd8f483"
        }
        
        # Task mapping - Notion page ID to BMAD task ID
        self.notion_task_mapping: Dict[str, str] = {}
        self.bmad_notion_mapping: Dict[str, str] = {}
        
        # Load existing mappings
        self._load_mappings()
    
    def _load_mappings(self):
        """Load Notion-BMAD task mappings"""
        if self.task_tracker.global_registry:
            mapping_file = self.task_tracker.global_registry.global_bmad_home / "notion_mappings.json"
        else:
            mapping_file = Path.home() / ".bmad-global" / "notion_mappings.json"
        
        if mapping_file.exists():
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.notion_task_mapping = data.get('notion_to_bmad', {})
                    self.bmad_notion_mapping = data.get('bmad_to_notion', {})
            except Exception as e:
                logger.error(f"Error loading Notion mappings: {e}")
    
    def _save_mappings(self):
        """Save Notion-BMAD task mappings"""
        if self.task_tracker.global_registry:
            mapping_file = self.task_tracker.global_registry.global_bmad_home / "notion_mappings.json"
        else:
            mapping_file = Path.home() / ".bmad-global" / "notion_mappings.json"
        
        mapping_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'notion_to_bmad': self.notion_task_mapping,
            'bmad_to_notion': self.bmad_notion_mapping,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving Notion mappings: {e}")
    
    def _build_task_properties(self, task: BMadTask) -> Dict[str, Any]:
        """Build Notion page properties for BMAD task"""
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": task.name
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": self._map_status_to_notion(task.status)
                }
            },
            "Hours Allocated": {
                "number": task.allocated_hours
            },
            "Hours Completed": {
                "number": task.completed_hours
            },
            "Progress": {
                "number": task.get_progress_percentage()
            },
            "Start Date": {
                "date": {
                    "start": task.start_date
                }
            },
            "Agent": {
                "select": {
                    "name": task.agent.title() if task.agent else "Unassigned"
                }
            },
            "Task ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": task.id
                        }
                    }
                ]
            },
            "Created": {
                "date": {
                    "start": task.created_at.split('T')[0] if task.created_at else datetime.now().strftime('%Y-%m-%d')
                }
            },
            "Updated": {
                "date": {
                    "start": task.updated_at.split('T')[0] if task.updated_at else datetime.now().strftime('%Y-%m-%d')
                }
            }
        }
        
        # Add today's allocation if applicable
        if task.is_due_today():
            properties["Today Hours"] = {
                "number": task.get_today_hours()
            }
        
        return properties
    
    def _map_status_to_notion(self, bmad_status: str) -> str:
        """Map BMAD status to Notion status"""
        mapping = {
            "pending": "🟡 Pending",
            "in_progress": "🔵 In Progress", 
            "completed": "🟢 Completed",
            "blocked": "🔴 Blocked"
        }
        return mapping.get(bmad_status, "🟡 Pending")
    
    def _map_status_from_notion(self, notion_status: str) -> str:
        """Map Notion status to BMAD status"""
        mapping = {
            "🟡 Pending": "pending",
            "🔵 In Progress": "in_progress",
            "🟢 Completed": "completed", 
            "🔴 Blocked": "blocked"
        }
        return mapping.get(notion_status, "pending")
    
    async def sync_task_to_notion(self, task: BMadTask) -> Optional[str]:
        """Sync a single BMAD task to Notion"""
        if not self.notion_token:
            logger.warning("No Notion token available for sync")
            return None
        
        try:
            # Check if task already exists in Notion
            if task.id in self.bmad_notion_mapping:
                # Update existing page
                notion_page_id = self.bmad_notion_mapping[task.id]
                return await self._update_notion_page(notion_page_id, task)
            else:
                # Create new page
                return await self._create_notion_page(task)
                
        except Exception as e:
            logger.error(f"Error syncing task {task.id} to Notion: {e}")
            return None
    
    async def _create_notion_page(self, task: BMadTask) -> Optional[str]:
        """Create new Notion page for task"""
        # This would use the Notion API to create a page
        # For now, return a mock page ID and log the action
        
        mock_page_id = f"notion_page_{task.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store mapping
        self.bmad_notion_mapping[task.id] = mock_page_id
        self.notion_task_mapping[mock_page_id] = task.id
        self._save_mappings()
        
        logger.info(f"Created Notion page for task: {task.name} (ID: {mock_page_id})")
        return mock_page_id
    
    async def _update_notion_page(self, notion_page_id: str, task: BMadTask) -> str:
        """Update existing Notion page"""
        # This would use the Notion API to update the page
        # For now, just log the action
        
        logger.info(f"Updated Notion page {notion_page_id} for task: {task.name}")
        return notion_page_id
    
    async def sync_all_tasks_to_notion(self) -> Dict[str, Any]:
        """Sync all BMAD tasks to Notion"""
        if not self.notion_token:
            return {
                "error": "No Notion token available",
                "synced_tasks": 0,
                "failed_tasks": 0
            }
        
        all_tasks = self.task_tracker.list_all_tasks()
        synced_count = 0
        failed_count = 0
        
        for task in all_tasks:
            try:
                result = await self.sync_task_to_notion(task)
                if result:
                    synced_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to sync task {task.id}: {e}")
                failed_count += 1
        
        logger.info(f"Notion sync completed: {synced_count} synced, {failed_count} failed")
        
        return {
            "synced_tasks": synced_count,
            "failed_tasks": failed_count,
            "total_tasks": len(all_tasks)
        }
    
    async def sync_today_tasks_to_notion(self) -> Dict[str, Any]:
        """Sync today's tasks to Notion"""
        today_tasks = self.task_tracker.get_today_tasks()
        
        if not today_tasks:
            return {
                "message": "No tasks scheduled for today",
                "synced_tasks": 0
            }
        
        synced_count = 0
        for task in today_tasks:
            try:
                result = await self.sync_task_to_notion(task)
                if result:
                    synced_count += 1
            except Exception as e:
                logger.error(f"Failed to sync today's task {task.id}: {e}")
        
        return {
            "synced_tasks": synced_count,
            "total_today_tasks": len(today_tasks),
            "message": f"Synced {synced_count}/{len(today_tasks)} today's tasks to Notion"
        }
    
    def create_time_tracking_entry(self, task: BMadTask, hours_worked: float, notes: str = "") -> Dict[str, Any]:
        """Create time tracking entry in Notion"""
        
        time_entry = {
            "task_id": task.id,
            "task_name": task.name,
            "agent": task.agent,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "time": datetime.now().strftime('%H:%M'),
            "hours_worked": hours_worked,
            "notes": notes,
            "total_progress": task.get_progress_percentage(),
            "remaining_hours": max(0, task.allocated_hours - task.completed_hours)
        }
        
        # This would create an entry in the time tracking database
        logger.info(f"Time tracking entry: {task.name} - {hours_worked}h")
        
        return time_entry
    
    def generate_notion_project_report(self) -> Dict[str, Any]:
        """Generate project report for Notion"""
        summary = self.task_tracker.get_task_summary()
        today_tasks = self.task_tracker.get_today_tasks()
        
        # Generate report data
        report = {
            "report_date": datetime.now().strftime('%Y-%m-%d'),
            "overall_progress": {
                "total_tasks": summary['total_tasks'],
                "completed_percentage": summary['completion_rate'],
                "hours_completed": summary['completed_hours'],
                "hours_total": summary['total_hours'],
                "progress_percentage": summary['progress_percentage']
            },
            "today_summary": {
                "tasks_count": len(today_tasks),
                "total_hours": summary['today_hours'],
                "capacity_usage": summary['capacity_usage']
            },
            "task_breakdown": {
                "completed": summary['completed_tasks'],
                "in_progress": summary['in_progress_tasks'],
                "pending": summary['pending_tasks']
            },
            "agent_workload": self._get_agent_workload(),
            "upcoming_tasks": self._get_upcoming_tasks()
        }
        
        return report
    
    def _get_agent_workload(self) -> Dict[str, Dict[str, Any]]:
        """Get workload breakdown by agent"""
        agents = ["analyst", "architect", "dev", "pm", "qa"]
        workload = {}
        
        for agent in agents:
            agent_tasks = self.task_tracker.get_tasks_by_agent(agent)
            
            if agent_tasks:
                total_hours = sum(t.allocated_hours for t in agent_tasks)
                completed_hours = sum(t.completed_hours for t in agent_tasks)
                active_tasks = len([t for t in agent_tasks if t.status in ["pending", "in_progress"]])
                
                workload[agent] = {
                    "total_tasks": len(agent_tasks),
                    "active_tasks": active_tasks,
                    "total_hours": total_hours,
                    "completed_hours": completed_hours,
                    "progress_percentage": int((completed_hours / total_hours * 100)) if total_hours > 0 else 0
                }
        
        return workload
    
    def _get_upcoming_tasks(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming tasks for next N days"""
        upcoming = []
        current_date = datetime.now()
        
        for i in range(1, days_ahead + 1):
            check_date = current_date + timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            
            day_tasks = []
            for task in self.task_tracker.list_all_tasks():
                if date_str in task.daily_allocation and task.daily_allocation[date_str] > 0:
                    day_tasks.append({
                        "name": task.name,
                        "agent": task.agent,
                        "hours": task.daily_allocation[date_str],
                        "status": task.status
                    })
            
            if day_tasks:
                upcoming.append({
                    "date": date_str,
                    "day_name": check_date.strftime('%A'),
                    "tasks": day_tasks,
                    "total_hours": sum(t["hours"] for t in day_tasks)
                })
        
        return upcoming
    
    async def auto_sync_on_task_update(self, task_id: str):
        """Automatically sync task when updated"""
        task = self.task_tracker.get_task(task_id)
        if task:
            await self.sync_task_to_notion(task)
            
            # Create time tracking entry if significant progress
            if task.status == "completed":
                self.create_time_tracking_entry(
                    task, 
                    task.allocated_hours, 
                    f"Task completed: {task.name}"
                )
    
    def get_notion_sync_status(self) -> Dict[str, Any]:
        """Get current Notion synchronization status"""
        total_tasks = len(self.task_tracker.list_all_tasks())
        mapped_tasks = len(self.bmad_notion_mapping)
        
        return {
            "notion_token_available": bool(self.notion_token),
            "total_bmad_tasks": total_tasks,
            "tasks_mapped_to_notion": mapped_tasks,
            "sync_coverage": int((mapped_tasks / total_tasks * 100)) if total_tasks > 0 else 0,
            "last_sync": "Not implemented - using mock data",
            "database_ids": self.database_ids
        }