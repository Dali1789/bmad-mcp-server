"""
BMAD MCP Server - Main server implementation
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.types import (
    CallToolRequest,
    GetPromptRequest,
    ListPromptsRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
    Tool,
    Prompt,
    Resource,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import BaseModel

from .agents import AgentManager
from .agents.coder import BMadCoderAgent
from .core import BMadLoader, ProjectDetector
from .core.global_registry import global_registry
from .routing import OpenRouterClient
from .tools import BMadTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BMadMCPServer:
    """Main BMAD MCP Server class"""
    
    def __init__(self):
        self.server = Server("bmad-mcp-server")
        self.global_registry = global_registry
        self.agent_manager = AgentManager()
        self.bmad_loader = BMadLoader(global_registry=self.global_registry)
        self.project_detector = ProjectDetector(global_registry=self.global_registry)
        self.openrouter_client = OpenRouterClient()
        self.bmad_tools = BMadTools(
            agent_manager=self.agent_manager,
            bmad_loader=self.bmad_loader,
            project_detector=self.project_detector,
            openrouter_client=self.openrouter_client,
            global_registry=self.global_registry
        )
        
        # Coder Agent
        self.coder_agent = BMadCoderAgent()
        
        # Current context
        self.current_agent = None
        self.current_project_path = None
        
        # Sync shared resources on startup
        self.global_registry.sync_shared_resources()
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return available BMAD tools"""
            return [
                Tool(
                    name="bmad_activate_agent",
                    description="Activate a specific BMAD agent (analyst, architect, dev, pm, qa)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent": {
                                "type": "string",
                                "enum": ["analyst", "architect", "dev", "pm", "qa"],
                                "description": "Agent to activate"
                            }
                        },
                        "required": ["agent"]
                    }
                ),
                Tool(
                    name="bmad_list_agents",
                    description="List all available BMAD agents and their capabilities",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_get_agent_help",
                    description="Get help for the current or specified agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent": {
                                "type": "string",
                                "enum": ["analyst", "architect", "dev", "pm", "qa"],
                                "description": "Agent to get help for (optional, uses current agent if not specified)"
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_detect_project",
                    description="Scan for .bmad-core configuration in current or specified directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to scan (optional, uses current directory if not specified)"
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_execute_task",
                    description="Execute a BMAD task with current agent context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Task name to execute"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Task parameters (optional)"
                            }
                        },
                        "required": ["task"]
                    }
                ),
                Tool(
                    name="bmad_create_document",
                    description="Create a document using BMAD templates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template": {
                                "type": "string",
                                "description": "Template name to use"
                            },
                            "data": {
                                "type": "object",
                                "description": "Template data"
                            }
                        },
                        "required": ["template"]
                    }
                ),
                Tool(
                    name="bmad_run_checklist",
                    description="Run a BMAD quality checklist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "checklist": {
                                "type": "string",
                                "description": "Checklist name to run"
                            },
                            "target": {
                                "type": "string",
                                "description": "Target document or artifact to check"
                            }
                        },
                        "required": ["checklist"]
                    }
                ),
                Tool(
                    name="bmad_query_with_model",
                    description="Execute a query using agent-specific model routing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Query to execute"
                            },
                            "agent": {
                                "type": "string",
                                "enum": ["analyst", "architect", "dev", "pm", "qa"],
                                "description": "Agent/model to use for query (optional, uses current agent)"
                            },
                            "context": {
                                "type": "object",
                                "description": "Additional context for the query"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="bmad_register_project",
                    description="Register a project in the global BMAD registry for cross-IDE access",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path to project containing .bmad-core"
                            },
                            "project_name": {
                                "type": "string",
                                "description": "Optional project name (uses directory name if not specified)"
                            }
                        },
                        "required": ["project_path"]
                    }
                ),
                Tool(
                    name="bmad_set_active_project",
                    description="Set the active project for universal access across IDEs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Name of registered project to activate"
                            }
                        },
                        "required": ["project_name"]
                    }
                ),
                Tool(
                    name="bmad_list_projects",
                    description="List all registered projects in the global registry",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_get_registry_info",
                    description="Get global registry information and status",
                    inputSchema={"type": "object", "properties": {}}
                ),
                # Task Management Tools
                Tool(
                    name="bmad_get_task_summary",
                    description="Get comprehensive task summary with progress and stats",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_get_today_tasks",
                    description="Get today's scheduled tasks",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_create_task",
                    description="Create a new BMAD task with automatic scheduling",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Unique task identifier"
                            },
                            "name": {
                                "type": "string",
                                "description": "Task name/title"
                            },
                            "allocated_hours": {
                                "type": "number",
                                "description": "Total hours allocated for this task"
                            },
                            "agent": {
                                "type": "string",
                                "enum": ["analyst", "architect", "dev", "pm", "qa"],
                                "description": "Agent responsible for this task (optional)"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format (optional, defaults to today)"
                            }
                        },
                        "required": ["task_id", "name", "allocated_hours"]
                    }
                ),
                Tool(
                    name="bmad_update_task_progress",
                    description="Update task progress by adding completed hours",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task identifier"
                            },
                            "hours_completed": {
                                "type": "number",
                                "description": "Hours of work completed to add to the task"
                            }
                        },
                        "required": ["task_id", "hours_completed"]
                    }
                ),
                Tool(
                    name="bmad_set_task_status",
                    description="Set task status (pending, in_progress, completed, blocked)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task identifier"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "blocked"],
                                "description": "New task status"
                            }
                        },
                        "required": ["task_id", "status"]
                    }
                ),
                Tool(
                    name="bmad_get_agent_tasks",
                    description="Get all tasks assigned to a specific agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent": {
                                "type": "string",
                                "enum": ["analyst", "architect", "dev", "pm", "qa"],
                                "description": "Agent name"
                            }
                        },
                        "required": ["agent"]
                    }
                ),
                Tool(
                    name="bmad_sync_notion_tasks",
                    description="Sync all tasks to Notion databases",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_get_task_report",
                    description="Get formatted task report (summary, today, or detailed)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_type": {
                                "type": "string",
                                "enum": ["summary", "today", "detailed"],
                                "description": "Type of report to generate (default: detailed)"
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_suggest_next_tasks",
                    description="Get task suggestions based on current context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent": {
                                "type": "string",
                                "enum": ["analyst", "architect", "dev", "pm", "qa"],
                                "description": "Agent to get suggestions for (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_delete_task",
                    description="Delete a task from the system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task identifier to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="bmad_start_task_monitoring",
                    description="Start background task monitoring with progress checks and reminders",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_stop_task_monitoring",
                    description="Stop background task monitoring",
                    inputSchema={"type": "object", "properties": {}}
                ),
                # Project Template Management Tools
                Tool(
                    name="bmad_create_project",
                    description="Create new BMAD project with standardized structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path where to create the project"
                            },
                            "template": {
                                "type": "string",
                                "description": "Template to use (standard, web-app, api, mobile, data-science, infrastructure)",
                                "default": "standard"
                            },
                            "name": {
                                "type": "string",
                                "description": "Custom project name (defaults to directory name)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Project description"
                            }
                        },
                        "required": ["project_path"]
                    }
                ),
                Tool(
                    name="bmad_list_project_templates",
                    description="List all available project templates",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_get_project_template_info",
                    description="Get detailed information about a specific template",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_name": {
                                "type": "string",
                                "description": "Name of the template to get info for"
                            }
                        },
                        "required": ["template_name"]
                    }
                ),
                Tool(
                    name="bmad_migrate_project_to_standard",
                    description="Migrate existing project to BMAD standard structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path to existing project"
                            },
                            "backup": {
                                "type": "boolean",
                                "description": "Create backup before migration",
                                "default": True
                            }
                        },
                        "required": ["project_path"]
                    }
                ),
                # Coder Agent Tools (Serena-inspired semantic code analysis)
                Tool(
                    name="bmad_coder_activate_project",
                    description="Activate a project for semantic code analysis with Serena-inspired features",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Absolute path to the project"
                            },
                            "project_name": {
                                "type": "string",
                                "description": "Optional project name"
                            }
                        },
                        "required": ["project_path"]
                    }
                ),
                Tool(
                    name="bmad_coder_find_symbol",
                    description="Semantic symbol search (inspired by Serena's find_symbol)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol_name": {
                                "type": "string",
                                "description": "Name of the symbol to search for"
                            },
                            "symbol_type": {
                                "type": "string",
                                "description": "Type of symbol (function, class, variable, etc.)"
                            },
                            "local_only": {
                                "type": "boolean",
                                "description": "Search only in current file",
                                "default": False
                            }
                        },
                        "required": ["symbol_name"]
                    }
                ),
                Tool(
                    name="bmad_coder_get_symbols_overview",
                    description="Get overview of top-level symbols in a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="bmad_coder_find_referencing_symbols",
                    description="Find all references to a symbol (Go to References)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol_location": {
                                "type": "string",
                                "description": "Position of the symbol (file:line:column)"
                            },
                            "symbol_type": {
                                "type": "string",
                                "description": "Optional - type of the symbol"
                            }
                        },
                        "required": ["symbol_location"]
                    }
                ),
                Tool(
                    name="bmad_coder_insert_after_symbol",
                    description="Insert code after a symbol (precise symbol-based editing)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol_location": {
                                "type": "string",
                                "description": "Position of the symbol (file:line:column)"
                            },
                            "content": {
                                "type": "string",
                                "description": "Code to insert"
                            }
                        },
                        "required": ["symbol_location", "content"]
                    }
                ),
                Tool(
                    name="bmad_coder_replace_symbol_body",
                    description="Replace the complete body of a symbol",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol_location": {
                                "type": "string",
                                "description": "Position of the symbol (file:line:column)"
                            },
                            "new_content": {
                                "type": "string",
                                "description": "New symbol content"
                            }
                        },
                        "required": ["symbol_location", "new_content"]
                    }
                ),
                Tool(
                    name="bmad_coder_execute_shell_command",
                    description="Execute shell commands for testing, building, etc.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Command to execute"
                            },
                            "working_dir": {
                                "type": "string",
                                "description": "Working directory"
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="bmad_coder_search_for_pattern",
                    description="Search for pattern in project (advanced grep functionality)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Search pattern"
                            },
                            "file_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "File types to search"
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Case sensitive search",
                                "default": False
                            }
                        },
                        "required": ["pattern"]
                    }
                ),
                Tool(
                    name="bmad_coder_write_memory",
                    description="Store project-specific memories (Serena feature)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_name": {
                                "type": "string",
                                "description": "Name of the memory"
                            },
                            "content": {
                                "type": "string",
                                "description": "Memory content"
                            }
                        },
                        "required": ["memory_name", "content"]
                    }
                ),
                Tool(
                    name="bmad_coder_read_memory",
                    description="Read project-specific memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_name": {
                                "type": "string",
                                "description": "Name of the memory"
                            }
                        },
                        "required": ["memory_name"]
                    }
                ),
                Tool(
                    name="bmad_coder_list_memories",
                    description="List all available memories",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "bmad_activate_agent":
                    return await self.bmad_tools.activate_agent(arguments["agent"])
                
                elif name == "bmad_list_agents":
                    return await self.bmad_tools.list_agents()
                
                elif name == "bmad_get_agent_help":
                    agent = arguments.get("agent", self.current_agent)
                    return await self.bmad_tools.get_agent_help(agent)
                
                elif name == "bmad_detect_project":
                    path = arguments.get("path", ".")
                    return await self.bmad_tools.detect_project(path)
                
                elif name == "bmad_execute_task":
                    task = arguments["task"]
                    parameters = arguments.get("parameters", {})
                    return await self.bmad_tools.execute_task(task, parameters)
                
                elif name == "bmad_create_document":
                    template = arguments["template"]
                    data = arguments.get("data", {})
                    return await self.bmad_tools.create_document(template, data)
                
                elif name == "bmad_run_checklist":
                    checklist = arguments["checklist"]
                    target = arguments.get("target")
                    return await self.bmad_tools.run_checklist(checklist, target)
                
                elif name == "bmad_query_with_model":
                    query = arguments["query"]
                    agent = arguments.get("agent", self.current_agent)
                    context = arguments.get("context", {})
                    return await self.bmad_tools.query_with_model(query, agent, context)
                
                elif name == "bmad_register_project":
                    project_path = arguments["project_path"]
                    project_name = arguments.get("project_name")
                    return await self._register_project(project_path, project_name)
                
                elif name == "bmad_set_active_project":
                    project_name = arguments["project_name"]
                    return await self._set_active_project(project_name)
                
                elif name == "bmad_list_projects":
                    return await self._list_projects()
                
                elif name == "bmad_get_registry_info":
                    return await self._get_registry_info()
                
                # Task Management Tools
                elif name == "bmad_get_task_summary":
                    return await self.bmad_tools.get_task_summary()
                
                elif name == "bmad_get_today_tasks":
                    return await self.bmad_tools.get_today_tasks()
                
                elif name == "bmad_create_task":
                    task_id = arguments["task_id"]
                    name = arguments["name"]
                    allocated_hours = arguments["allocated_hours"]
                    agent = arguments.get("agent")
                    start_date = arguments.get("start_date")
                    return await self.bmad_tools.create_task(task_id, name, allocated_hours, agent, start_date)
                
                elif name == "bmad_update_task_progress":
                    task_id = arguments["task_id"]
                    hours_completed = arguments["hours_completed"]
                    return await self.bmad_tools.update_task_progress(task_id, hours_completed)
                
                elif name == "bmad_set_task_status":
                    task_id = arguments["task_id"]
                    status = arguments["status"]
                    return await self.bmad_tools.set_task_status(task_id, status)
                
                elif name == "bmad_get_agent_tasks":
                    agent = arguments["agent"]
                    return await self.bmad_tools.get_agent_tasks(agent)
                
                elif name == "bmad_sync_notion_tasks":
                    return await self.bmad_tools.sync_notion_tasks()
                
                elif name == "bmad_get_task_report":
                    report_type = arguments.get("report_type", "detailed")
                    return await self.bmad_tools.get_task_report(report_type)
                
                elif name == "bmad_suggest_next_tasks":
                    agent = arguments.get("agent")
                    return await self.bmad_tools.suggest_next_tasks(agent)
                
                elif name == "bmad_delete_task":
                    task_id = arguments["task_id"]
                    return await self.bmad_tools.delete_task(task_id)
                
                elif name == "bmad_start_task_monitoring":
                    return await self.bmad_tools.start_task_monitoring()
                
                elif name == "bmad_stop_task_monitoring":
                    return await self.bmad_tools.stop_task_monitoring()
                
                # Project Template Management Tools
                elif name == "bmad_create_project":
                    return await self.bmad_tools.create_project(
                        arguments["project_path"],
                        arguments.get("template", "standard"),
                        arguments.get("name"),
                        arguments.get("description")
                    )
                
                elif name == "bmad_list_project_templates":
                    return await self.bmad_tools.list_project_templates()
                
                elif name == "bmad_get_project_template_info":
                    return await self.bmad_tools.get_project_template_info(arguments["template_name"])
                
                elif name == "bmad_migrate_project_to_standard":
                    return await self.bmad_tools.migrate_project_to_standard(
                        arguments["project_path"],
                        arguments.get("backup", True)
                    )
                
                # Coder Agent Tools Handler
                elif name.startswith("bmad_coder_"):
                    return await self._handle_coder_tool(name, arguments)
                
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available BMAD resources"""
            resources = []
            
            # Add agent definitions
            for agent_name in ["analyst", "architect", "dev", "pm", "qa"]:
                resources.append(Resource(
                    uri=f"bmad://agents/{agent_name}",
                    name=f"BMAD Agent: {agent_name.title()}",
                    description=f"Agent definition and capabilities for {agent_name}",
                    mimeType="text/yaml"
                ))
            
            # Add templates if project detected
            if self.current_project_path:
                templates_path = Path(self.current_project_path) / ".bmad-core" / "templates"
                if templates_path.exists():
                    for template_file in templates_path.glob("*.yaml"):
                        resources.append(Resource(
                            uri=f"bmad://templates/{template_file.stem}",
                            name=f"Template: {template_file.stem}",
                            description=f"BMAD template: {template_file.stem}",
                            mimeType="text/yaml"
                        ))
            
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read BMAD resource content"""
            try:
                if uri.startswith("bmad://agents/"):
                    agent_name = uri.split("/")[-1]
                    return await self.bmad_tools.get_agent_definition(agent_name)
                
                elif uri.startswith("bmad://templates/"):
                    template_name = uri.split("/")[-1]
                    return await self.bmad_tools.get_template_content(template_name)
                
                else:
                    return f"Unknown resource: {uri}"
                    
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {str(e)}")
                return f"Error reading resource: {str(e)}"
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> List[Prompt]:
            """List available BMAD prompts"""
            return [
                Prompt(
                    name="bmad_agent_activation",
                    description="Activate and configure a BMAD agent",
                    arguments=[
                        {
                            "name": "agent",
                            "description": "Agent to activate",
                            "required": True
                        }
                    ]
                ),
                Prompt(
                    name="bmad_project_analysis",
                    description="Analyze a project using BMAD methodology",
                    arguments=[
                        {
                            "name": "project_path",
                            "description": "Path to project directory",
                            "required": False
                        }
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: Dict[str, str]) -> str:
            """Get BMAD prompt content"""
            if name == "bmad_agent_activation":
                agent = arguments["agent"]
                return await self.bmad_tools.get_agent_activation_prompt(agent)
            
            elif name == "bmad_project_analysis":
                project_path = arguments.get("project_path", ".")
                return await self.bmad_tools.get_project_analysis_prompt(project_path)
            
            else:
                return f"Unknown prompt: {name}"
    
    async def _register_project(self, project_path: str, project_name: str = None) -> List[TextContent]:
        """Register a project in the global registry"""
        try:
            project_info = self.global_registry.register_project(project_path, project_name)
            
            result = f"✅ Projekt registriert: {project_info['name']}\n"
            result += f"📁 Pfad: {project_info['path']}\n"
            result += f"🔗 BMAD Core: {project_info['bmad_core_path']}\n"
            result += f"🕐 Registriert: {project_info['registered_at']}\n\n"
            result += "ℹ️  Das Projekt ist jetzt von jedem IDE aus zugänglich."
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Fehler bei Projekt-Registrierung: {str(e)}")]
    
    async def _set_active_project(self, project_name: str) -> List[TextContent]:
        """Set the active project"""
        try:
            success = self.global_registry.set_active_project(project_name)
            
            if success:
                result = f"✅ Aktives Projekt gesetzt: {project_name}\n"
                result += "🌐 Universeller Zugriff aktiviert - funktioniert von jedem IDE aus!"
                return [TextContent(type="text", text=result)]
            else:
                return [TextContent(type="text", text=f"❌ Projekt '{project_name}' nicht gefunden. Nutze bmad_list_projects zum Anzeigen verfügbarer Projekte.")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Fehler beim Setzen des aktiven Projekts: {str(e)}")]
    
    async def _list_projects(self) -> List[TextContent]:
        """List all registered projects"""
        try:
            projects = self.global_registry.list_projects()
            
            if not projects:
                return [TextContent(type="text", text="📝 Keine Projekte registriert. Nutze bmad_register_project um ein Projekt zu registrieren.")]
            
            result = "📋 Registrierte BMAD-Projekte:\n\n"
            
            for project in projects:
                status = "🟢 AKTIV" if project.get('active') else "⚫ Inaktiv"
                result += f"• {project['name']} ({status})\n"
                result += f"  📁 {project['path']}\n"
                result += f"  🕐 Zuletzt genutzt: {project['last_accessed']}\n\n"
            
            result += "💡 Nutze bmad_set_active_project um ein Projekt zu aktivieren."
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Fehler beim Auflisten der Projekte: {str(e)}")]
    
    async def _get_registry_info(self) -> List[TextContent]:
        """Get global registry information"""
        try:
            registry_info = self.global_registry.get_registry_info()
            active_project = registry_info.get('active_project')
            
            result = "🏗️ BMAD Global Registry Status:\n\n"
            result += f"📂 Registry Home: {registry_info['global_bmad_home']}\n"
            result += f"📋 Registry Datei: {registry_info['registry_file']}\n"
            result += f"🔧 Shared Resources: {registry_info['shared_resources']}\n"
            result += f"📁 Projekte Verzeichnis: {registry_info['projects_dir']}\n\n"
            
            if active_project:
                result += f"🟢 Aktives Projekt: {active_project['name']}\n"
                result += f"📁 Projekt Pfad: {active_project['path']}\n"
                result += f"🔗 Universal Zugriff: Verfügbar von jedem IDE\n"
            else:
                result += "⚫ Kein aktives Projekt gesetzt\n"
                result += "💡 Nutze bmad_set_active_project um ein Projekt zu aktivieren\n"
            
            result += "\n✨ Einheitliche Struktur: Alle IDEs haben Zugriff auf die gleichen Projektdateien!"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Fehler beim Abrufen der Registry-Informationen: {str(e)}")]
    
    async def _handle_coder_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle coder agent tool calls"""
        try:
            if name == "bmad_coder_activate_project":
                project_path = arguments["project_path"]
                project_name = arguments.get("project_name")
                result = await self.coder_agent.activate_project(project_path, project_name)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_find_symbol":
                symbol_name = arguments["symbol_name"]
                symbol_type = arguments.get("symbol_type")
                local_only = arguments.get("local_only", False)
                result = await self.coder_agent.find_symbol(symbol_name, symbol_type, local_only)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_get_symbols_overview":
                file_path = arguments["file_path"]
                result = await self.coder_agent.get_symbols_overview(file_path)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_find_referencing_symbols":
                symbol_location = arguments["symbol_location"]
                symbol_type = arguments.get("symbol_type")
                result = await self.coder_agent.find_referencing_symbols(symbol_location, symbol_type)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_insert_after_symbol":
                symbol_location = arguments["symbol_location"]
                content = arguments["content"]
                result = await self.coder_agent.insert_after_symbol(symbol_location, content)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_replace_symbol_body":
                symbol_location = arguments["symbol_location"]
                new_content = arguments["new_content"]
                result = await self.coder_agent.replace_symbol_body(symbol_location, new_content)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_execute_shell_command":
                command = arguments["command"]
                working_dir = arguments.get("working_dir")
                result = await self.coder_agent.execute_shell_command(command, working_dir)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_search_for_pattern":
                pattern = arguments["pattern"]
                file_types = arguments.get("file_types")
                case_sensitive = arguments.get("case_sensitive", False)
                result = await self.coder_agent.search_for_pattern(pattern, file_types, case_sensitive)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_write_memory":
                memory_name = arguments["memory_name"]
                content = arguments["content"]
                result = await self.coder_agent.write_memory(memory_name, content)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_read_memory":
                memory_name = arguments["memory_name"]
                result = await self.coder_agent.read_memory(memory_name)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_coder_list_memories":
                result = await self.coder_agent.list_memories()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            else:
                return [TextContent(type="text", text=f"❌ Unbekanntes Coder-Tool: {name}")]
                
        except Exception as e:
            logger.error(f"Fehler beim Ausführen von Coder-Tool {name}: {str(e)}")
            return [TextContent(type="text", text=f"❌ Fehler beim Ausführen von {name}: {str(e)}")]


async def main():
    """Main server entry point"""
    server_instance = BMadMCPServer()
    
    # Configure OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY not set. Some features may not work.")

    # Run the server using stdio transport (standard for MCP)
    logger.info("Starting BMAD MCP Server...")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="bmad-mcp-server",
                server_version="1.0.0",
                capabilities={
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                }
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())