"""
BMAD Tools Implementation - Core MCP tools for BMAD methodology
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from mcp.types import TextContent

from ..agents import AgentManager
from ..core import (
    BMadLoader, ProjectDetector, BMadTaskTracker, TodoWriteBridge, 
    NotionTaskSync, BMadConsoleFormatter, BMadTimeMonitor, 
    BMadWorkDaySimulator, BMadRealtimeUpdater
)
from ..core.project_templates import template_manager
from ..core.bmad_core_loader import get_bmad_core_loader
from ..routing import OpenRouterClient


class BMadTools:
    """Implementation of BMAD MCP tools"""
    
    def __init__(
        self,
        agent_manager: AgentManager,
        bmad_loader: 'BMadLoader',
        project_detector: 'ProjectDetector', 
        openrouter_client: OpenRouterClient,
        global_registry=None
    ):
        self.agent_manager = agent_manager
        self.bmad_loader = bmad_loader
        self.project_detector = project_detector
        self.openrouter_client = openrouter_client
        self.global_registry = global_registry
        
        # Initialize BMAD Core Loader
        self.bmad_core = get_bmad_core_loader()
        
        # Initialize task management components
        self.task_tracker = BMadTaskTracker(global_registry)
        self.todowrite_bridge = TodoWriteBridge(self.task_tracker)
        self.notion_sync = NotionTaskSync(self.task_tracker)
        
        # Initialize enhanced features
        self.console_formatter = BMadConsoleFormatter(self.task_tracker)
        self.time_monitor = BMadTimeMonitor(self.task_tracker, self.console_formatter)
        self.simulator = BMadWorkDaySimulator(self.task_tracker, self.console_formatter, self.time_monitor)
        self.realtime_updater = BMadRealtimeUpdater(self.task_tracker, self.console_formatter)
    
    async def activate_agent(self, agent: str) -> List[TextContent]:
        """Activate a BMAD agent"""
        result = await self.agent_manager.activate_agent(agent)
        return [TextContent(type="text", text=result)]
    
    async def list_agents(self) -> List[TextContent]:
        """List all available BMAD agents"""
        agents = self.agent_manager.list_agents()
        
        result = "🤖 **Available BMAD Agents**\\n\\n"
        for i, agent in enumerate(agents, 1):
            result += f"{i}. **{agent['icon']} {agent['title']} ({agent['name']})**\\n"
            result += f"   - **ID**: `{agent['id']}`\\n"
            result += f"   - **Model**: `{agent['model']}`\\n"
            result += f"   - **Use For**: {agent['whenToUse']}\\n\\n"
        
        result += "Use `bmad_activate_agent` with the agent ID to switch agents."
        
        return [TextContent(type="text", text=result)]
    
    async def get_agent_help(self, agent: Optional[str] = None) -> List[TextContent]:
        """Get help for specific agent"""
        result = await self.agent_manager.get_agent_help(agent)
        return [TextContent(type="text", text=result)]
    
    async def detect_project(self, path: str = ".") -> List[TextContent]:
        """Detect BMAD project configuration"""
        project_info = await self.project_detector.detect_project(path)
        
        if project_info:
            result = f"""🎯 **BMAD Project Detected**
            
**Path**: `{project_info['path']}`
**Configuration**: `{project_info['config_file']}`

**Project Settings**:
"""
            for key, value in project_info['config'].items():
                result += f"- **{key}**: {value}\\n"
            
            result += f"\\n**Available Templates**: {len(project_info.get('templates', []))}"
            result += f"\\n**Available Tasks**: {len(project_info.get('tasks', []))}"
            result += f"\\n**Available Agents**: {len(project_info.get('agents', []))}"
            
        else:
            result = f"""❌ **No BMAD Project Found**
            
Searched in: `{os.path.abspath(path)}`

To initialize a BMAD project:
1. Create `.bmad-core/` directory
2. Add `core-config.yaml` configuration
3. Add agent definitions, templates, and tasks

Use `bmad_create_project` to set up a new BMAD project."""
        
        return [TextContent(type="text", text=result)]
    
    async def execute_task(self, task: str, parameters: Dict[str, Any] = None) -> List[TextContent]:
        """Execute a BMAD task"""
        current_agent = self.agent_manager.get_current_agent()
        
        if not current_agent:
            return [TextContent(type="text", text="❌ No agent activated. Use `bmad_activate_agent` first.")]
        
        # Load task definition
        task_content = await self.bmad_loader.load_task(task)
        
        if not task_content:
            return [TextContent(type="text", text=f"❌ Task not found: {task}")]
        
        # Execute task with current agent context
        result = f"""🔧 **Executing Task: {task}**
        
**Agent**: {current_agent.config.title} ({current_agent.config.name})
**Model**: {current_agent.config.model}

**Task Definition**:
{task_content}

**Parameters**: {json.dumps(parameters or {}, indent=2)}

*Task execution would be implemented here with agent context*
"""
        
        return [TextContent(type="text", text=result)]
    
    async def create_document(self, template: str, data: Dict[str, Any] = None) -> List[TextContent]:
        """Create document using BMAD template"""
        template_content = await self.bmad_loader.load_template(template)
        
        if not template_content:
            return [TextContent(type="text", text=f"❌ Template not found: {template}")]
        
        current_agent = self.agent_manager.get_current_agent()
        agent_info = f"Agent: {current_agent.config.title}" if current_agent else "No agent active"
        
        result = f"""📄 **Creating Document: {template}**
        
**{agent_info}**
**Template**: {template}

**Template Content**:
```yaml
{template_content}
```

**Data**: {json.dumps(data or {}, indent=2)}

*Document generation would be implemented here*
"""
        
        return [TextContent(type="text", text=result)]
    
    async def run_checklist(self, checklist: str, target: Optional[str] = None) -> List[TextContent]:
        """Run BMAD quality checklist"""
        checklist_content = await self.bmad_loader.load_checklist(checklist)
        
        if not checklist_content:
            return [TextContent(type="text", text=f"❌ Checklist not found: {checklist}")]
        
        result = f"""✅ **Running Checklist: {checklist}**
        
**Target**: {target or 'Not specified'}

**Checklist Content**:
{checklist_content}

*Checklist execution would be implemented here*
"""
        
        return [TextContent(type="text", text=result)]
    
    async def query_with_model(
        self, 
        query: str, 
        agent: Optional[str] = None, 
        context: Dict[str, Any] = None
    ) -> List[TextContent]:
        """Execute query using agent-specific model routing"""
        
        # Determine agent to use
        target_agent = agent or (self.agent_manager.current_agent if self.agent_manager.current_agent else "dev")
        
        # Get agent info
        agent_obj = self.agent_manager.get_agent(target_agent)
        if not agent_obj:
            return [TextContent(type="text", text=f"❌ Unknown agent: {target_agent}")]
        
        # Execute query via OpenRouter
        result = await self.openrouter_client.query_model(
            prompt=query,
            agent=target_agent,
            context=context,
            temperature=agent_obj.config.temperature,
            max_tokens=agent_obj.config.max_tokens
        )
        
        response = f"""🤖 **{agent_obj.config.icon} {agent_obj.config.title} Response**
        
**Model**: {agent_obj.config.model}
**Query**: {query}

**Response**:
{result}
"""
        
        return [TextContent(type="text", text=response)]
    
    async def get_agent_definition(self, agent: str) -> str:
        """Get agent definition content"""
        agent_obj = self.agent_manager.get_agent(agent)
        if not agent_obj:
            return f"Agent not found: {agent}"
        
        return agent_obj.get_activation_prompt()
    
    async def get_template_content(self, template: str) -> str:
        """Get template content"""
        content = await self.bmad_loader.load_template(template)
        return content or f"Template not found: {template}"
    
    async def get_agent_activation_prompt(self, agent: str) -> str:
        """Get agent activation prompt"""
        agent_obj = self.agent_manager.get_agent(agent)
        if not agent_obj:
            return f"Agent not found: {agent}"
        
        return agent_obj.get_activation_prompt()
    
    async def get_project_analysis_prompt(self, project_path: str) -> str:
        """Get project analysis prompt"""
        project_info = await self.project_detector.detect_project(project_path)
        
        if not project_info:
            return f"No BMAD project found at: {project_path}"
        
        return f"""# BMAD Project Analysis

Analyze the BMAD project at: `{project_path}`

## Project Configuration
{json.dumps(project_info['config'], indent=2)}

## Available Resources
- **Templates**: {len(project_info.get('templates', []))}
- **Tasks**: {len(project_info.get('tasks', []))}
- **Agents**: {len(project_info.get('agents', []))}
- **Checklists**: {len(project_info.get('checklists', []))}

Provide a comprehensive analysis of this BMAD project structure and suggest improvements or next steps.
"""
    
    # Task Management Tools
    async def get_task_summary(self) -> List[TextContent]:
        """Get comprehensive task summary"""
        summary = self.task_tracker.get_task_summary()
        formatted_report = self.todowrite_bridge.get_formatted_task_report("detailed")
        
        return [TextContent(type="text", text=formatted_report)]
    
    async def get_today_tasks(self) -> List[TextContent]:
        """Get today's scheduled tasks"""
        today_report = self.todowrite_bridge.get_formatted_task_report("today")
        return [TextContent(type="text", text=today_report)]
    
    async def create_task(
        self, 
        task_id: str, 
        name: str, 
        allocated_hours: float, 
        agent: Optional[str] = None,
        start_date: Optional[str] = None
    ) -> List[TextContent]:
        """Create a new BMAD task"""
        
        task = self.task_tracker.create_task(
            task_id=task_id,
            name=name,
            allocated_hours=allocated_hours,
            agent=agent,
            start_date=start_date
        )
        
        # Sync to Notion if available
        await self.notion_sync.sync_task_to_notion(task)
        
        result = f"""✅ **Task Created Successfully**

**Task ID**: `{task.id}`
**Name**: {task.name}
**Allocated Hours**: {task.allocated_hours}h
**Agent**: {task.agent or 'Unassigned'}
**Start Date**: {task.start_date}
**Status**: {task.status}

📅 **Daily Allocation**:
"""
        
        for date, hours in task.daily_allocation.items():
            result += f"- {date}: {hours}h\n"
        
        return [TextContent(type="text", text=result)]
    
    async def update_task_progress(self, task_id: str, hours_completed: float) -> List[TextContent]:
        """Update task progress"""
        
        task = self.task_tracker.update_task_progress(task_id, hours_completed)
        
        if not task:
            return [TextContent(type="text", text=f"❌ Task not found: {task_id}")]
        
        # Sync to Notion
        await self.notion_sync.sync_task_to_notion(task)
        
        # Auto-sync TodoWrite if applicable
        if task.status == "completed":
            self.todowrite_bridge.sync_from_claude_update(f"bmad_{task_id}", "completed")
        
        progress_percentage = task.get_progress_percentage()
        
        result = f"""📈 **Task Progress Updated**

**Task**: {task.name}
**Progress**: {task.completed_hours:.1f}/{task.allocated_hours:.1f}h ({progress_percentage}%)
**Status**: {task.status}
**Hours Added**: +{hours_completed:.1f}h

"""
        
        if task.status == "completed":
            result += "🎉 **Task Completed!** Follow-up tasks may have been generated.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def set_task_status(self, task_id: str, status: str) -> List[TextContent]:
        """Set task status"""
        
        valid_statuses = ["pending", "in_progress", "completed", "blocked"]
        if status not in valid_statuses:
            return [TextContent(type="text", text=f"❌ Invalid status. Use: {', '.join(valid_statuses)}")]
        
        task = self.task_tracker.set_task_status(task_id, status)
        
        if not task:
            return [TextContent(type="text", text=f"❌ Task not found: {task_id}")]
        
        # Sync to Notion
        await self.notion_sync.sync_task_to_notion(task)
        
        result = f"""✅ **Task Status Updated**

**Task**: {task.name}
**New Status**: {status}
**Progress**: {task.completed_hours:.1f}/{task.allocated_hours:.1f}h ({task.get_progress_percentage()}%)
"""
        
        return [TextContent(type="text", text=result)]
    
    async def get_agent_tasks(self, agent: str) -> List[TextContent]:
        """Get all tasks for a specific agent"""
        
        agent_tasks = self.task_tracker.get_tasks_by_agent(agent)
        
        if not agent_tasks:
            return [TextContent(type="text", text=f"📋 **No tasks found for agent: {agent}**")]
        
        result = f"🤖 **Tasks for Agent: {agent.upper()}**\n\n"
        
        for i, task in enumerate(agent_tasks, 1):
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}.get(task.status, "❓")
            progress = task.get_progress_percentage()
            
            result += f"{i}. {status_emoji} **{task.name}**\n"
            result += f"   - Progress: {task.completed_hours:.1f}/{task.allocated_hours:.1f}h ({progress}%)\n"
            result += f"   - Status: {task.status}\n"
            result += f"   - Start: {task.start_date}\n\n"
        
        total_hours = sum(t.allocated_hours for t in agent_tasks)
        completed_hours = sum(t.completed_hours for t in agent_tasks)
        overall_progress = int((completed_hours / total_hours * 100)) if total_hours > 0 else 0
        
        result += f"📊 **Summary**: {completed_hours:.1f}/{total_hours:.1f}h ({overall_progress}%)"
        
        return [TextContent(type="text", text=result)]
    
    async def sync_notion_tasks(self) -> List[TextContent]:
        """Sync all tasks to Notion"""
        
        sync_result = await self.notion_sync.sync_all_tasks_to_notion()
        
        result = f"""🔄 **Notion Sync Completed**

✅ **Synced**: {sync_result['synced_tasks']} tasks
❌ **Failed**: {sync_result['failed_tasks']} tasks
📊 **Total**: {sync_result['total_tasks']} tasks

"""
        
        if sync_result.get('error'):
            result += f"⚠️ **Error**: {sync_result['error']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_task_report(self, report_type: str = "detailed") -> List[TextContent]:
        """Get formatted task report"""
        
        valid_types = ["summary", "today", "detailed"]
        if report_type not in valid_types:
            report_type = "detailed"
        
        formatted_report = self.todowrite_bridge.get_formatted_task_report(report_type)
        return [TextContent(type="text", text=formatted_report)]
    
    async def suggest_next_tasks(self, agent: Optional[str] = None) -> List[TextContent]:
        """Get task suggestions"""
        
        suggestions = self.todowrite_bridge.suggest_next_tasks(agent)
        
        if not suggestions:
            return [TextContent(type="text", text="📋 **No task suggestions available**")]
        
        result = f"💡 **Task Suggestions**\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            result += f"{i}. {suggestion}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def delete_task(self, task_id: str) -> List[TextContent]:
        """Delete a task"""
        
        success = self.task_tracker.delete_task(task_id)
        
        if success:
            result = f"✅ **Task deleted**: {task_id}"
        else:
            result = f"❌ **Task not found**: {task_id}"
        
        return [TextContent(type="text", text=result)]
    
    async def start_task_monitoring(self) -> List[TextContent]:
        """Start background task monitoring"""
        
        self.task_tracker.start_monitoring()
        
        result = """🔍 **Task Monitoring Started**

Background monitoring is now active:
- Progress checks every 30 minutes
- Daily reports at 18:00
- Automatic follow-up task generation
- Phase completion tracking

Use `bmad_stop_task_monitoring` to disable.
"""
        
        return [TextContent(type="text", text=result)]
    
    async def stop_task_monitoring(self) -> List[TextContent]:
        """Stop background task monitoring"""
        
        self.task_tracker.stop_monitoring()
        
        result = "⏹️ **Task Monitoring Stopped**"
        
        return [TextContent(type="text", text=result)]
    
    # Enhanced Features from Local System
    async def get_project_status(self) -> List[TextContent]:
        """Get comprehensive project status overview"""
        project_status = self.task_tracker.get_project_status()
        formatted_status = self.console_formatter.format_project_status(project_status["project_id"])
        
        return [TextContent(type="text", text=formatted_status)]
    
    async def start_realtime_mode(self) -> List[TextContent]:
        """Start real-time task monitoring with live updates"""
        result = self.realtime_updater.start_realtime_updates()
        return [TextContent(type="text", text=result)]
    
    async def stop_realtime_mode(self) -> List[TextContent]:
        """Stop real-time monitoring"""
        result = self.realtime_updater.stop_realtime_updates()
        return [TextContent(type="text", text=result)]
    
    async def start_work_session(self, task_id: str) -> List[TextContent]:
        """Start tracking a work session for a task"""
        result = self.realtime_updater.start_work_session(task_id)
        return [TextContent(type="text", text=result)]
    
    async def end_work_session(self, task_id: str, hours_worked: Optional[float] = None) -> List[TextContent]:
        """End work session and log hours"""
        result = self.realtime_updater.end_work_session(task_id, hours_worked)
        return [TextContent(type="text", text=result)]
    
    async def get_active_sessions(self) -> List[TextContent]:
        """Get information about active work sessions"""
        result = self.realtime_updater.get_active_sessions()
        return [TextContent(type="text", text=result)]
    
    async def simulate_work_day(self, speed_factor: float = 1.0) -> List[TextContent]:
        """Simulate a complete work day with realistic progression"""
        result = await self.simulator.simulate_work_day(speed_factor)
        return [TextContent(type="text", text=result)]
    
    async def simulate_task_progression(self, task_id: str, target_hours: float) -> List[TextContent]:
        """Simulate realistic task progression"""
        result = await self.simulator.simulate_task_progression(task_id, target_hours)
        return [TextContent(type="text", text=result)]
    
    async def simulate_reminder_cycle(self) -> List[TextContent]:
        """Simulate daily reminder cycle"""
        result = await self.simulator.simulate_reminder_cycle()
        return [TextContent(type="text", text=result)]
    
    async def simulate_agent_workday(self, agent: str, hours: float = 8.0) -> List[TextContent]:
        """Simulate a full workday for specific agent"""
        result = await self.simulator.simulate_agent_workday(agent, hours)
        return [TextContent(type="text", text=result)]
    
    async def simulate_crisis_scenario(self, crisis_type: str = "blocked_task") -> List[TextContent]:
        """Simulate crisis scenarios and recovery"""
        result = await self.simulator.simulate_crisis_scenario(crisis_type)
        return [TextContent(type="text", text=result)]
    
    async def get_simulation_options(self) -> List[TextContent]:
        """Get list of available simulation options"""
        result = self.simulator.get_simulation_options()
        return [TextContent(type="text", text=result)]
    
    async def manual_reminder_check(self) -> List[TextContent]:
        """Manually trigger reminder check"""
        result = self.time_monitor.manual_reminder_check()
        return [TextContent(type="text", text=result)]
    
    async def manual_progress_check(self) -> List[TextContent]:
        """Manually trigger progress check"""
        result = self.time_monitor.manual_progress_check()
        return [TextContent(type="text", text=result)]
    
    # Project Template Management Tools
    
    async def create_project(self, project_path: str, template: str = "standard", 
                           name: Optional[str] = None, description: Optional[str] = None) -> List[TextContent]:
        """
        Create new BMAD project with standardized structure
        
        Args:
            project_path: Path where to create the project
            template: Template to use (standard, web-app, api, mobile, data-science, infrastructure)
            name: Custom project name (defaults to directory name)
            description: Project description
        """
        try:
            project_config = {}
            if name:
                project_config["name"] = name
            if description:
                project_config["description"] = description
            
            result = template_manager.create_project(project_path, template, project_config)
            
            # Format success message
            success_msg = f"""
🎯 BMAD-Projekt erfolgreich erstellt!

📁 Projekt: {result['project_path']}
🎨 Template: {result['template']}
📅 Erstellt: {result['created_at']}

📋 Nächste Schritte:
1. cd {Path(project_path).name}
2. Konfiguration anpassen: .bmad-core/project.yaml
3. Erste Task erstellen: bmad_create_task
4. Agent aktivieren: bmad_activate_agent

🏗️ Struktur:
{self._format_project_structure(result['structure'])}

✅ Projekt ist bereit für BMAD-Workflows!
"""
            return [TextContent(type="text", text=success_msg)]
            
        except Exception as e:
            error_msg = f"❌ Fehler beim Erstellen des Projekts: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    async def list_project_templates(self) -> List[TextContent]:
        """List all available project templates"""
        try:
            templates = template_manager.list_templates()
            
            if not templates:
                return [TextContent(type="text", text="Keine Templates verfügbar.")]
            
            result = "🎨 Verfügbare BMAD-Projekt-Templates:\n\n"
            
            for template in templates:
                result += f"📋 **{template['name']}**\n"
                result += f"   Typ: {template['type']}\n"
                result += f"   Beschreibung: {template['description']}\n"
                result += f"   Features:\n"
                for feature in template.get('features', []):
                    result += f"     • {feature}\n"
                result += "\n"
            
            result += "💡 Verwendung: bmad_create_project('/pfad/zum/projekt', 'template-name')"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ Fehler beim Laden der Templates: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    async def get_project_template_info(self, template_name: str) -> List[TextContent]:
        """Get detailed information about a specific template"""
        try:
            template_config = template_manager._load_template(template_name)
            
            if not template_config:
                return [TextContent(type="text", text=f"❌ Template '{template_name}' nicht gefunden.")]
            
            result = f"""
🎨 Template: {template_config['name']}

📋 Details:
• Typ: {template_config.get('type', 'standard')}
• Beschreibung: {template_config.get('description', 'Keine Beschreibung')}

✨ Features:
{chr(10).join(f'• {feature}' for feature in template_config.get('features', []))}

🏗️ Verzeichnisstruktur:
{self._format_project_structure(template_config.get('structure', {}))}

💡 Erstellen mit:
bmad_create_project('/pfad/zum/projekt', '{template_name}')
"""
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ Fehler beim Laden der Template-Info: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    async def migrate_project_to_standard(self, project_path: str, backup: bool = True) -> List[TextContent]:
        """
        Migrate existing project to BMAD standard structure
        
        Args:
            project_path: Path to existing project
            backup: Create backup before migration
        """
        try:
            project_path = Path(project_path)
            
            if not project_path.exists():
                return [TextContent(type="text", text=f"❌ Projekt-Pfad existiert nicht: {project_path}")]
            
            # Check if already BMAD project
            bmad_core = project_path / ".bmad-core"
            if bmad_core.exists():
                return [TextContent(type="text", text=f"✅ Projekt verwendet bereits BMAD-Standard-Struktur: {project_path}")]
            
            # Create backup if requested
            if backup:
                backup_path = project_path.parent / f"{project_path.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copytree(project_path, backup_path)
                backup_msg = f"💾 Backup erstellt: {backup_path}\n"
            else:
                backup_msg = ""
            
            # Create .bmad-core structure
            template_config = template_manager._get_standard_template()
            template_manager._create_directory_structure(project_path, {".bmad-core": template_config["structure"][".bmad-core"]})
            template_manager._create_config_files(project_path, template_config, {"name": project_path.name})
            
            # Register project
            template_manager._register_project(project_path, "standard", None)
            
            result = f"""
🔄 Projekt erfolgreich migriert!

{backup_msg}📁 Projekt: {project_path}
🎨 Template: BMAD Standard
⏰ Migriert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Hinzugefügt:
• .bmad-core/ - BMAD Konfiguration
• Agent-Konfigurationen (dev, architect, analyst, pm, qa)
• Workflow-Definitionen (CI/CD, Review, Deployment)
• Quality Gates (Linting, Testing, Security)
• Integration-Konfigurationen (Notion, Slack, Git)

📋 Nächste Schritte:
1. Konfiguration anpassen: .bmad-core/project.yaml
2. Erste Task erstellen: bmad_create_task
3. Agent aktivieren: bmad_activate_agent

🎯 Projekt ist jetzt BMAD-kompatibel!
"""
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ Fehler bei der Migration: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    def _format_project_structure(self, structure: Dict[str, Any], indent: int = 0) -> str:
        """Format project structure for display"""
        result = ""
        prefix = "  " * indent
        
        for name, config in structure.items():
            result += f"{prefix}├── {name}/\n"
            
            if isinstance(config, dict) and "children" in config:
                result += self._format_project_structure(config["children"], indent + 1)
        
        return result
    
    async def manual_daily_report(self) -> List[TextContent]:
        """Manually generate daily report"""
        result = self.time_monitor.manual_daily_report()
        return [TextContent(type="text", text=result)]
    
    async def simulate_time_advance(self, target_time: str) -> List[TextContent]:
        """Simulate advancing time to trigger reminders"""
        result = self.time_monitor.simulate_time_advance(target_time)
        return [TextContent(type="text", text=result)]
    
    async def get_todays_schedule(self) -> List[TextContent]:
        """Get today's complete reminder schedule"""
        result = self.time_monitor.get_todays_schedule()
        return [TextContent(type="text", text=result)]
    
    async def get_realtime_status(self) -> List[TextContent]:
        """Get real-time monitoring status"""
        status = self.realtime_updater.get_realtime_status()
        
        result = f"""🔴 **Real-time Status**:
        
**Active**: {status['realtime_active']}
**Session Duration**: {status['session_duration']:.1f}h
**Active Work Sessions**: {status['active_sessions']}
**Work Hours**: {status['work_hours_active']}
**Last Auto Progress**: {status['last_auto_progress']}

**Daily Metrics**:
• Tasks Started: {status['daily_metrics']['tasks_started']}
• Tasks Completed: {status['daily_metrics']['tasks_completed']}
• Progress Updates: {status['daily_metrics']['progress_updates']}
• Total Work Time: {status['daily_metrics']['total_work_time']:.1f}h
"""
        
        return [TextContent(type="text", text=result)]
    
    # Original BMAD Core System Integration Methods
    
    async def get_original_agent_definition(self, agent_name: str) -> List[TextContent]:
        """Get original agent definition from BMAD Core system"""
        agent_content = self.bmad_core.get_agent_definition(agent_name)
        
        if not agent_content:
            available_agents = list(self.bmad_core.get_all_agents().keys())
            result = f"❌ **Agent nicht gefunden**: {agent_name}\n\n📋 **Verfügbare Agents**: {', '.join(available_agents)}"
        else:
            result = f"🤖 **BMAD Agent: {agent_name}**\n\n{agent_content}"
        
        return [TextContent(type="text", text=result)]
    
    async def get_original_checklist(self, checklist_name: str) -> List[TextContent]:
        """Get original checklist from BMAD Core system"""
        checklist_content = self.bmad_core.get_checklist(checklist_name)
        
        if not checklist_content:
            available_checklists = list(self.bmad_core.get_all_checklists().keys())
            result = f"❌ **Checklist nicht gefunden**: {checklist_name}\n\n📋 **Verfügbare Checklisten**: {', '.join(available_checklists)}"
        else:
            result = f"✅ **BMAD Checklist: {checklist_name}**\n\n{checklist_content}"
        
        return [TextContent(type="text", text=result)]
    
    async def get_original_workflow(self, workflow_name: str) -> List[TextContent]:
        """Get original workflow from BMAD Core system"""
        workflow_data = self.bmad_core.get_workflow(workflow_name)
        
        if not workflow_data:
            available_workflows = list(self.bmad_core.get_all_workflows().keys())
            result = f"❌ **Workflow nicht gefunden**: {workflow_name}\n\n📋 **Verfügbare Workflows**: {', '.join(available_workflows)}"
        else:
            import yaml
            workflow_yaml = yaml.dump(workflow_data, indent=2, default_flow_style=False)
            result = f"🔄 **BMAD Workflow: {workflow_name}**\n\n```yaml\n{workflow_yaml}\n```"
        
        return [TextContent(type="text", text=result)]
    
    async def get_original_agent_team(self, team_name: str) -> List[TextContent]:
        """Get original agent team configuration from BMAD Core system"""
        team_data = self.bmad_core.get_agent_team(team_name)
        
        if not team_data:
            available_teams = list(self.bmad_core.get_all_teams().keys())
            result = f"❌ **Agent Team nicht gefunden**: {team_name}\n\n📋 **Verfügbare Teams**: {', '.join(available_teams)}"
        else:
            import yaml
            team_yaml = yaml.dump(team_data, indent=2, default_flow_style=False)
            result = f"👥 **BMAD Agent Team: {team_name}**\n\n```yaml\n{team_yaml}\n```"
        
        return [TextContent(type="text", text=result)]
    
    async def get_original_task_definition(self, task_name: str) -> List[TextContent]:
        """Get original task definition from BMAD Core system"""
        task_content = self.bmad_core.get_task_definition(task_name)
        
        if not task_content:
            available_tasks = list(self.bmad_core.get_all_tasks().keys())
            result = f"❌ **Task nicht gefunden**: {task_name}\n\n📋 **Verfügbare Tasks**: {', '.join(available_tasks)}"
        else:
            result = f"🔧 **BMAD Task: {task_name}**\n\n{task_content}"
        
        return [TextContent(type="text", text=result)]
    
    async def get_original_template(self, template_name: str) -> List[TextContent]:
        """Get original template from BMAD Core system"""
        template_content = self.bmad_core.get_template(template_name)
        
        if not template_content:
            available_templates = list(self.bmad_core.get_all_templates().keys())
            result = f"❌ **Template nicht gefunden**: {template_name}\n\n📋 **Verfügbare Templates**: {', '.join(available_templates)}"
        else:
            result = f"📄 **BMAD Template: {template_name}**\n\n{template_content}"
        
        return [TextContent(type="text", text=result)]
    
    async def get_bmad_knowledge_base(self) -> List[TextContent]:
        """Get BMAD Knowledge Base from original Core system"""
        kb_content = self.bmad_core.get_knowledge_base()
        
        if not kb_content:
            result = "❌ **BMAD Knowledge Base nicht gefunden**"
        else:
            # Truncate if too long for display
            if len(kb_content) > 8000:
                kb_preview = kb_content[:8000] + "\n\n... [Inhalt gekürzt - vollständige KB im Original verfügbar]"
            else:
                kb_preview = kb_content
                
            result = f"📚 **BMAD Knowledge Base**\n\n{kb_preview}"
        
        return [TextContent(type="text", text=result)]
    
    async def get_bmad_user_guide(self) -> List[TextContent]:
        """Get BMAD User Guide from original Core system"""
        guide_content = self.bmad_core.get_user_guide()
        
        if not guide_content:
            result = "❌ **BMAD User Guide nicht gefunden**"
        else:
            # Truncate if too long for display
            if len(guide_content) > 10000:
                guide_preview = guide_content[:10000] + "\n\n... [User Guide gekürzt - vollständiger Inhalt im Original verfügbar]"
            else:
                guide_preview = guide_content
                
            result = f"📖 **BMAD User Guide**\n\n{guide_preview}"
        
        return [TextContent(type="text", text=result)]
    
    async def list_original_bmad_components(self) -> List[TextContent]:
        """List all components available in original BMAD Core system"""
        status = self.bmad_core.get_system_status()
        
        result = f"""🏗️ **Original BMAD Core System Status**

**Core Path**: `{status['core_path']}`

📊 **Komponenten Übersicht**:
• **Agents**: {status['agents_loaded']} geladen
• **Agent Teams**: {status['teams_loaded']} geladen
• **Checklisten**: {status['checklists_loaded']} geladen
• **Tasks**: {status['tasks_loaded']} geladen
• **Templates**: {status['templates_loaded']} geladen
• **Workflows**: {status['workflows_loaded']} geladen
• **Data Files**: {status['data_files_loaded']} geladen
• **User Guide**: {'✅ Verfügbar' if status['user_guide_available'] else '❌ Nicht verfügbar'}

🤖 **Verfügbare Agents**:
{', '.join(status['loaded_agents'])}

👥 **Verfügbare Teams**:
{', '.join(status['loaded_teams'])}

🔄 **Verfügbare Workflows**:
{', '.join(status['loaded_workflows'])}

💡 **Verwendung**:
- `bmad_get_original_agent_definition <agent_name>`
- `bmad_get_original_checklist <checklist_name>`
- `bmad_get_original_workflow <workflow_name>`
- `bmad_get_original_agent_team <team_name>`
- `bmad_get_original_task_definition <task_name>`
- `bmad_get_original_template <template_name>`
"""
        
        return [TextContent(type="text", text=result)]
    
    async def validate_bmad_core_system(self) -> List[TextContent]:
        """Validate original BMAD Core system integrity"""
        validation = self.bmad_core.validate_core_structure()
        
        if validation['valid']:
            status_emoji = "✅"
            status_text = "GÜLTIG"
        else:
            status_emoji = "❌"
            status_text = "FEHLER GEFUNDEN"
        
        result = f"""{status_emoji} **BMAD Core System Validierung: {status_text}**

"""
        
        if validation['errors']:
            result += "❌ **Kritische Fehler**:\n"
            for error in validation['errors']:
                result += f"• {error}\n"
            result += "\n"
        
        if validation['warnings']:
            result += "⚠️ **Warnungen**:\n"
            for warning in validation['warnings']:
                result += f"• {warning}\n"
            result += "\n"
        
        if validation['valid']:
            result += "🎯 **System bereit für BMAD-Operationen**"
        else:
            result += "🔧 **Konfiguration erforderlich für vollständige Funktionalität**"
        
        return [TextContent(type="text", text=result)]