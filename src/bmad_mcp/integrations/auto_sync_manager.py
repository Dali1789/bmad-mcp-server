"""
BMAD Auto-Sync Manager
Koordiniert automatische Synchronisation zwischen GitHub, Notion und anderen Services
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class AutoSyncManager:
    """
    Zentraler Manager für automatische Synchronisation zwischen verschiedenen Services.
    
    Löst das Problem der manuellen Synchronisation und MCP-Reconnections.
    """
    
    def __init__(self):
        self.sync_queue = []
        self.sync_history = []
        self.is_monitoring = False
        self.sync_interval = 30  # seconds
        
        # Service connection status
        self.services = {
            "notion": {"connected": False, "last_sync": None, "retry_count": 0},
            "github": {"connected": False, "last_sync": None, "retry_count": 0},
            "bmad_mcp": {"connected": False, "last_sync": None, "retry_count": 0}
        }
        
        logger.info("AutoSyncManager initialized")
    
    async def start_auto_sync_monitoring(self) -> Dict[str, Any]:
        """Startet die automatische Synchronisation und Überwachung"""
        try:
            if self.is_monitoring:
                return {"success": False, "error": "Monitoring already active"}
            
            self.is_monitoring = True
            
            logger.info("Starting auto-sync monitoring...")
            
            # Start monitoring loop in background
            asyncio.create_task(self._monitoring_loop())
            
            return {
                "success": True,
                "monitoring_active": True,
                "sync_interval": self.sync_interval,
                "services_monitored": list(self.services.keys()),
                "message": "Auto-sync monitoring started successfully"
            }
            
        except Exception as e:
            logger.error(f"Error starting auto-sync monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_auto_sync_monitoring(self) -> Dict[str, Any]:
        """Stoppt die automatische Synchronisation"""
        try:
            self.is_monitoring = False
            
            logger.info("Auto-sync monitoring stopped")
            
            return {
                "success": True,
                "monitoring_active": False,
                "final_status": self.get_sync_status(),
                "message": "Auto-sync monitoring stopped"
            }
            
        except Exception as e:
            logger.error(f"Error stopping auto-sync monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    async def _monitoring_loop(self):
        """Hauptschleife für automatische Synchronisation"""
        while self.is_monitoring:
            try:
                # Check service connections
                await self._check_service_connections()
                
                # Process sync queue
                await self._process_sync_queue()
                
                # Wait for next cycle
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Error in auto-sync monitoring loop: {e}")
                await asyncio.sleep(self.sync_interval)
    
    async def _check_service_connections(self):
        """Überprüft Verbindungen zu allen Services"""
        for service_name in self.services.keys():
            try:
                is_connected = await self._test_service_connection(service_name)
                
                if is_connected != self.services[service_name]["connected"]:
                    logger.info(f"Service {service_name} connection status changed: {is_connected}")
                    self.services[service_name]["connected"] = is_connected
                    
                    if not is_connected:
                        # Attempt reconnection
                        await self._attempt_service_reconnection(service_name)
                
            except Exception as e:
                logger.error(f"Error checking connection for {service_name}: {e}")
                self.services[service_name]["connected"] = False
    
    async def _test_service_connection(self, service_name: str) -> bool:
        """Testet Verbindung zu einem spezifischen Service"""
        try:
            if service_name == "notion":
                return await self._test_notion_connection()
            elif service_name == "github":
                return await self._test_github_connection()
            elif service_name == "bmad_mcp":
                return await self._test_bmad_mcp_connection()
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error testing {service_name} connection: {e}")
            return False
    
    async def _test_notion_connection(self) -> bool:
        """Testet Notion MCP Verbindung"""
        try:
            # This would test the actual MCP connection
            # For now, simulate the test
            return True  # Assume connected for demo
            
        except Exception:
            return False
    
    async def _test_github_connection(self) -> bool:
        """Testet GitHub MCP Verbindung"""
        try:
            # This would test the actual MCP connection
            # For now, simulate the test
            return True  # Assume connected for demo
            
        except Exception:
            return False
    
    async def _test_bmad_mcp_connection(self) -> bool:
        """Testet BMAD MCP Verbindung"""
        try:
            # This would test the actual MCP connection
            # For now, simulate the test
            return True  # Assume connected for demo
            
        except Exception:
            return False
    
    async def _attempt_service_reconnection(self, service_name: str):
        """Versucht Service-Reconnection"""
        try:
            self.services[service_name]["retry_count"] += 1
            
            if self.services[service_name]["retry_count"] > 3:
                logger.error(f"Max retry attempts reached for {service_name}")
                return False
            
            logger.info(f"Attempting to reconnect {service_name} (attempt {self.services[service_name]['retry_count']})")
            
            # This would trigger the actual reconnection logic
            # For now, simulate successful reconnection
            await asyncio.sleep(2)  # Simulate reconnection delay
            
            # Reset retry count on successful reconnection
            self.services[service_name]["retry_count"] = 0
            self.services[service_name]["connected"] = True
            
            logger.info(f"Successfully reconnected {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error reconnecting {service_name}: {e}")
            return False
    
    async def queue_sync_task(self, task_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fügt eine Synchronisationsaufgabe zur Queue hinzu"""
        try:
            task = {
                "id": f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.sync_queue)}",
                "type": task_type,
                "data": data,
                "created_at": datetime.now().isoformat(),
                "status": "queued",
                "retry_count": 0
            }
            
            self.sync_queue.append(task)
            
            logger.info(f"Queued sync task: {task_type} (ID: {task['id']})")
            
            return {
                "success": True,
                "task_id": task["id"],
                "queue_position": len(self.sync_queue),
                "message": f"Sync task '{task_type}' added to queue"
            }
            
        except Exception as e:
            logger.error(f"Error queuing sync task: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_sync_queue(self):
        """Verarbeitet alle Synchronisationsaufgaben in der Queue"""
        if not self.sync_queue:
            return
        
        # Process up to 5 tasks per cycle
        tasks_to_process = self.sync_queue[:5]
        self.sync_queue = self.sync_queue[5:]
        
        for task in tasks_to_process:
            try:
                task["status"] = "processing"
                result = await self._execute_sync_task(task)
                
                if result["success"]:
                    task["status"] = "completed"
                    task["completed_at"] = datetime.now().isoformat()
                    logger.info(f"Sync task {task['id']} completed successfully")
                else:
                    task["retry_count"] += 1
                    if task["retry_count"] < 3:
                        task["status"] = "queued"
                        self.sync_queue.append(task)  # Re-queue for retry
                        logger.warning(f"Sync task {task['id']} failed, re-queued (attempt {task['retry_count']})")
                    else:
                        task["status"] = "failed"
                        logger.error(f"Sync task {task['id']} failed after max retries")
                
                # Add to history
                self.sync_history.append(task)
                
                # Keep history limited to last 100 tasks
                if len(self.sync_history) > 100:
                    self.sync_history = self.sync_history[-100:]
                
            except Exception as e:
                logger.error(f"Error processing sync task {task['id']}: {e}")
                task["status"] = "error"
                task["error"] = str(e)
                self.sync_history.append(task)
    
    async def _execute_sync_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Führt eine spezifische Synchronisationsaufgabe aus"""
        try:
            task_type = task["type"]
            data = task["data"]
            
            if task_type == "notion_document":
                return await self._sync_to_notion(data)
            elif task_type == "github_commit":
                return await self._sync_to_github(data)
            elif task_type == "bmad_summary":
                return await self._sync_bmad_summary(data)
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Error executing sync task: {e}")
            return {"success": False, "error": str(e)}
    
    async def _sync_to_notion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronisiert Dokument zu Notion"""
        try:
            if not self.services["notion"]["connected"]:
                return {"success": False, "error": "Notion service not connected"}
            
            # This would use the actual Notion MCP API
            logger.info(f"Syncing document to Notion: {data.get('title', 'Unknown')}")
            
            # Simulate successful sync
            await asyncio.sleep(1)
            
            self.services["notion"]["last_sync"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "service": "notion",
                "document_id": f"notion_doc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "message": "Document successfully synced to Notion"
            }
            
        except Exception as e:
            logger.error(f"Error syncing to Notion: {e}")
            return {"success": False, "error": str(e)}
    
    async def _sync_to_github(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronisiert Änderungen zu GitHub"""
        try:
            if not self.services["github"]["connected"]:
                return {"success": False, "error": "GitHub service not connected"}
            
            # This would use the actual GitHub MCP API
            logger.info(f"Syncing changes to GitHub: {data.get('repository', 'Unknown')}")
            
            # Simulate successful sync
            await asyncio.sleep(1)
            
            self.services["github"]["last_sync"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "service": "github",
                "commit_sha": f"abc123_{datetime.now().strftime('%H%M%S')}",
                "message": "Changes successfully synced to GitHub"
            }
            
        except Exception as e:
            logger.error(f"Error syncing to GitHub: {e}")
            return {"success": False, "error": str(e)}
    
    async def _sync_bmad_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronisiert BMAD Summary zu allen Services"""
        try:
            results = {}
            
            # Sync to Notion
            notion_result = await self._sync_to_notion({
                "title": f"BMAD Summary - {data.get('phase', 'Unknown')}",
                "content": data.get("summary_data", {}),
                "project_id": data.get("project_id")
            })
            results["notion"] = notion_result
            
            # Sync to GitHub (as commit)
            github_result = await self._sync_to_github({
                "repository": data.get("repository", "bmad-lead-generation-system"),
                "message": f"Auto-update: BMAD {data.get('phase', 'Unknown')} summary",
                "files": data.get("files", [])
            })
            results["github"] = github_result
            
            success_count = sum(1 for result in results.values() if result["success"])
            total_count = len(results)
            
            return {
                "success": success_count > 0,
                "results": results,
                "synced_services": success_count,
                "total_services": total_count,
                "message": f"BMAD summary synced to {success_count}/{total_count} services"
            }
            
        except Exception as e:
            logger.error(f"Error syncing BMAD summary: {e}")
            return {"success": False, "error": str(e)}
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Gibt aktuellen Synchronisationsstatus zurück"""
        return {
            "monitoring_active": self.is_monitoring,
            "sync_queue_length": len(self.sync_queue),
            "completed_tasks": len([t for t in self.sync_history if t["status"] == "completed"]),
            "failed_tasks": len([t for t in self.sync_history if t["status"] == "failed"]),
            "services": self.services,
            "last_check": datetime.now().isoformat()
        }
    
    async def manual_sync_all(self, project_id: str) -> Dict[str, Any]:
        """Führt manuelle Synchronisation aller Projektdaten durch"""
        try:
            # Queue tasks for all project documents
            tasks = []
            
            # Sync project documents to Notion
            notion_task = await self.queue_sync_task("notion_document", {
                "title": "BMAD Lead Generation - Full Project Sync",
                "project_id": project_id,
                "type": "project_sync"
            })
            tasks.append(notion_task)
            
            # Sync project files to GitHub
            github_task = await self.queue_sync_task("github_commit", {
                "repository": "bmad-lead-generation-system",
                "message": f"Manual sync: Complete project update {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "project_id": project_id
            })
            tasks.append(github_task)
            
            return {
                "success": True,
                "queued_tasks": len(tasks),
                "task_ids": [t.get("task_id") for t in tasks if t["success"]],
                "message": f"Manual sync initiated for project {project_id}"
            }
            
        except Exception as e:
            logger.error(f"Error in manual sync: {e}")
            return {"success": False, "error": str(e)}


# Global instance
auto_sync_manager = AutoSyncManager()