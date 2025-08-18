"""
BMAD Tools Implementation - Core MCP tools for BMAD methodology
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from mcp.types import TextContent

from ..agents import AgentManager
from ..core import BMadLoader, ProjectDetector, BMadTaskTracker, TodoWriteBridge, NotionTaskSync
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
        
        # Initialize task management components
        self.task_tracker = BMadTaskTracker(global_registry)
        self.todowrite_bridge = TodoWriteBridge(self.task_tracker)
        self.notion_sync = NotionTaskSync(self.task_tracker)
    
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