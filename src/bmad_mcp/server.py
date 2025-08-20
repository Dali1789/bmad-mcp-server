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
from fastapi import FastAPI, Response
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import uvicorn
from starlette.middleware.cors import CORSMiddleware
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
from .core.instant_context import get_instant_context
from .routing import OpenRouterClient
from .tools import BMadTools
from .tools.time_tracking import TimeTrackingTools
from .workflows.workflow_engine import BMadWorkflowEngine
from .core.mcp_auto_reconnect import auto_reconnector
from .integrations.auto_sync_manager import auto_sync_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BMadMCPServer:
    """Main BMAD MCP Server class"""
    
    def __init__(self):
        self.server = Server("bmad-mcp-server")
        self.global_registry = global_registry
        
        # FastAPI instance for Railway health endpoint
        self.app = FastAPI(title="BMAD MCP Server", description="Railway Deployment Health Check")
        self.setup_fastapi_routes()
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
        self.time_tracking_tools = TimeTrackingTools(self.global_registry)
        
        # Coder Agents
        self.coder_agent = BMadCoderAgent()  # Fallback Basic Agent
        
        # Workflow Engine
        self.workflow_engine = BMadWorkflowEngine(
            global_registry=self.global_registry,
            persistence_path="./workflows"
        )
        
        # Register agents with workflow engine
        self.workflow_engine.register_agent("coder", self.coder_agent)
        
        # Current context
        self.current_agent = None
        self.current_project_path = None
        
        # Sync shared resources on startup
        self.global_registry.sync_shared_resources()
        
        # Initialize auto-sync and reconnection systems
        self.auto_reconnector = auto_reconnector
        self.auto_sync_manager = auto_sync_manager
        
        self._setup_handlers()
    
    def setup_fastapi_routes(self):
        """Setup FastAPI routes for Railway deployment"""
        
        # Add CORS middleware for Railway compatibility
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint for Railway deployment"""
            return {
                "status": "healthy",
                "service": "bmad-mcp-server",
                "version": "2.0.0",
                "timestamp": asyncio.get_event_loop().time(),
                "deployment": "railway"
            }
        
        @self.app.get("/status")
        async def status_check():
            """Detailed status endpoint"""
            return {
                "status": "operational",
                "mcp_server": "active",
                "global_registry": "initialized",
                "agents": {
                    "coder": "available",
                    "workflow_engine": "initialized"
                }
            }
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {"message": "BMAD MCP Server v2.0 - Railway Deployment"}
    
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
                    name="bmad_instant_context",
                    description="Get instant project context and status - eliminates discovery time by auto-detecting current project and recommended next actions",
                    inputSchema={"type": "object", "properties": {}}
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
                # Coder Agent Tools (semantic code analysis)
                Tool(
                    name="bmad_coder_activate_project",
                    description="Activate a project for semantic code analysis",
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
                    description="Semantic symbol search for code analysis",
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
                    description="Store project-specific memories and context",
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
                ),
                
                # Workflow Engine Tools
                Tool(
                    name="bmad_workflow_start_project",
                    description="Start a new BMAD-METHOD project workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Name of the project"
                            },
                            "initial_idea": {
                                "type": "string",
                                "description": "Optional initial project idea"
                            },
                            "workflow_type": {
                                "type": "string",
                                "enum": ["full", "planning_only", "development_only"],
                                "description": "Type of workflow to start"
                            }
                        },
                        "required": ["project_name"]
                    }
                ),
                Tool(
                    name="bmad_workflow_advance",
                    description="Advance workflow to next state or specific target",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Workflow identifier"
                            },
                            "target_state": {
                                "type": "string",
                                "description": "Optional specific target state"
                            },
                            "agent_override": {
                                "type": "string",
                                "description": "Optional agent to handle advancement"
                            }
                        },
                        "required": ["workflow_id"]
                    }
                ),
                Tool(
                    name="bmad_workflow_execute_agent_command",
                    description="Execute agent command within workflow context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Workflow identifier"
                            },
                            "agent_type": {
                                "type": "string",
                                "enum": ["analyst", "architect", "pm", "dev", "qa"],
                                "description": "Type of agent"
                            },
                            "command": {
                                "type": "string",
                                "description": "Agent command (e.g., *risk, *design, *review)"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Command parameters"
                            }
                        },
                        "required": ["workflow_id", "agent_type", "command"]
                    }
                ),
                Tool(
                    name="bmad_workflow_start_story",
                    description="Start story development cycle within workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Parent workflow identifier"
                            },
                            "story_title": {
                                "type": "string",
                                "description": "Story title"
                            },
                            "story_description": {
                                "type": "string",
                                "description": "Story description"
                            },
                            "epic_id": {
                                "type": "string",
                                "description": "Optional parent epic ID"
                            }
                        },
                        "required": ["workflow_id", "story_title"]
                    }
                ),
                Tool(
                    name="bmad_workflow_run_quality_gate",
                    description="Run quality gate check for story (@qa commands)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Workflow identifier"
                            },
                            "story_id": {
                                "type": "string",
                                "description": "Story identifier"
                            },
                            "gate_type": {
                                "type": "string",
                                "enum": ["risk", "design", "trace", "nfr", "review", "gate", "comprehensive"],
                                "description": "Type of quality gate"
                            }
                        },
                        "required": ["workflow_id", "story_id"]
                    }
                ),
                Tool(
                    name="bmad_workflow_status",
                    description="Get comprehensive workflow status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Optional specific workflow ID"
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_workflow_generate_report",
                    description="Generate comprehensive workflow report",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Workflow identifier"
                            }
                        },
                        "required": ["workflow_id"]
                    }
                ),
                
                # Auto-Sync and Reconnection Tools
                Tool(
                    name="bmad_start_auto_sync",
                    description="Start automatic synchronization monitoring for Notion and GitHub",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_stop_auto_sync",
                    description="Stop automatic synchronization monitoring",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_start_mcp_monitoring",
                    description="Start automatic MCP server reconnection monitoring",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "servers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific servers to monitor (optional, monitors all if not provided)"
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_stop_mcp_monitoring",
                    description="Stop automatic MCP server monitoring",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_get_sync_status",
                    description="Get current auto-sync and MCP connection status",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_manual_reconnect_mcp",
                    description="Manually reconnect a specific MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_name": {
                                "type": "string",
                                "description": "Name of MCP server to reconnect"
                            }
                        },
                        "required": ["server_name"]
                    }
                ),
                Tool(
                    name="bmad_queue_sync_task",
                    description="Queue a manual synchronization task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_type": {
                                "type": "string",
                                "enum": ["notion_document", "github_commit", "bmad_summary"],
                                "description": "Type of sync task"
                            },
                            "data": {
                                "type": "object",
                                "description": "Task data"
                            }
                        },
                        "required": ["task_type", "data"]
                    }
                ),
                # Original BMAD Core System Integration Tools
                Tool(
                    name="bmad_get_original_agent_definition",
                    description="Get agent definition from original BMAD Core system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "Name of the agent (analyst, architect, dev, pm, qa, po, etc.)"
                            }
                        },
                        "required": ["agent_name"]
                    }
                ),
                Tool(
                    name="bmad_get_original_checklist",
                    description="Get checklist from original BMAD Core system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "checklist_name": {
                                "type": "string",
                                "description": "Name of the checklist (e.g., po-master-checklist, architect-checklist)"
                            }
                        },
                        "required": ["checklist_name"]
                    }
                ),
                Tool(
                    name="bmad_get_original_workflow",
                    description="Get workflow definition from original BMAD Core system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_name": {
                                "type": "string",
                                "description": "Name of the workflow (e.g., greenfield-fullstack, brownfield-service)"
                            }
                        },
                        "required": ["workflow_name"]
                    }
                ),
                Tool(
                    name="bmad_get_original_agent_team",
                    description="Get agent team configuration from original BMAD Core system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_name": {
                                "type": "string",
                                "description": "Name of the team (e.g., team-fullstack, team-minimal)"
                            }
                        },
                        "required": ["team_name"]
                    }
                ),
                Tool(
                    name="bmad_get_original_task_definition",
                    description="Get task definition from original BMAD Core system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_name": {
                                "type": "string",
                                "description": "Name of the task (e.g., create-doc, shard-doc, execute-checklist)"
                            }
                        },
                        "required": ["task_name"]
                    }
                ),
                Tool(
                    name="bmad_get_original_template",
                    description="Get template from original BMAD Core system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_name": {
                                "type": "string",
                                "description": "Name of the template (e.g., prd-tmpl, architecture-tmpl)"
                            }
                        },
                        "required": ["template_name"]
                    }
                ),
                Tool(
                    name="bmad_get_bmad_knowledge_base",
                    description="Get BMAD Knowledge Base from original Core system",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_get_bmad_user_guide",
                    description="Get BMAD User Guide from original Core system",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_list_original_bmad_components",
                    description="List all components available in original BMAD Core system",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_validate_bmad_core_system",
                    description="Validate original BMAD Core system integrity",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_start_timer",
                    description="Start time tracking for a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to track time for"
                            },
                            "agent": {
                                "type": "string", 
                                "description": "Agent working on the task"
                            },
                            "session_type": {
                                "type": "string",
                                "description": "Type of work session (development, analysis, testing, etc.)",
                                "default": "development"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional session description"
                            }
                        },
                        "required": ["task_id", "agent"]
                    }
                ),
                Tool(
                    name="bmad_stop_timer",
                    description="Stop time tracking for a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to stop tracking"
                            },
                            "ai_model_used": {
                                "type": "string",
                                "description": "AI model used during session"
                            },
                            "tokens_input": {
                                "type": "integer",
                                "description": "Number of input tokens used",
                                "default": 0
                            },
                            "tokens_output": {
                                "type": "integer", 
                                "description": "Number of output tokens used",
                                "default": 0
                            },
                            "mark_completed": {
                                "type": "boolean",
                                "description": "Mark task as completed",
                                "default": false
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="bmad_get_active_timers",
                    description="Get all currently active time tracking sessions",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="bmad_get_task_time_summary",
                    description="Get time tracking summary for a specific task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to get summary for"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="bmad_get_daily_time_report",
                    description="Get daily time tracking report",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Date in YYYY-MM-DD format (defaults to today)"
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_get_project_billing",
                    description="Get project billing report with time and cost breakdown",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project ID (defaults to current project)"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format"
                            },
                            "export_format": {
                                "type": "string",
                                "description": "Export format: json, csv, or invoice",
                                "default": "json"
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_auto_end_stale_sessions",
                    description="Automatically end sessions that have been running too long",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_hours": {
                                "type": "integer",
                                "description": "Maximum hours before session is considered stale",
                                "default": 8
                            }
                        }
                    }
                ),
                Tool(
                    name="bmad_update_model_costs",
                    description="Update AI model cost configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_costs": {
                                "type": "object",
                                "description": "Dictionary of model names to cost per 1K tokens {input: float, output: float}"
                            }
                        },
                        "required": ["model_costs"]
                    }
                ),
                Tool(
                    name="bmad_get_model_costs",
                    description="Get current AI model cost configuration",
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
                
                elif name == "bmad_instant_context":
                    # Get instant project context without discovery delay
                    context = get_instant_context()
                    context_data = context.get_instant_context()
                    
                    if context_data["status"] == "project_detected":
                        response = f"🚀 **Projekt erkannt: {context_data['project']['name']}**\n\n"
                        response += f"📊 **Status:** {context_data['project']['phase']} ({context_data['project']['progress']})\n"
                        response += f"🤖 **Empfohlener Agent:** {context_data['recommendation']['agent']}\n"
                        response += f"📋 **Aktuelle Aufgabe:** {context_data['recommendation']['current_task']}\n\n"
                        response += f"⚡ **Quick Start:** `{context_data['quick_start']}`\n\n"
                        
                        if context_data['next_steps']:
                            response += f"📋 **Nächste Schritte:**\n"
                            if isinstance(context_data['next_steps'], dict):
                                for key, value in context_data['next_steps'].items():
                                    if isinstance(value, list):
                                        response += f"• **{key}:**\n"
                                        for item in value:
                                            response += f"  - {item}\n"
                                    else:
                                        response += f"• **{key}:** {value}\n"
                        
                        # Auto-activate recommended agent if desired
                        self.current_agent = context_data['recommendation']['agent']
                        
                    elif context_data["status"] == "no_active_project":
                        response = f"❌ **{context_data['message']}**\n\n"
                        if context_data.get('available_projects'):
                            response += "📁 **Verfügbare Projekte:**\n"
                            for project in context_data['available_projects']:
                                response += f"• **{project['name']}** - `{project['command']}`\n"
                    else:
                        response = f"⚠️ **Fehler:** {context_data['message']}\n"
                        response += f"🔄 **Fallback:** {context_data.get('fallback', 'Manueller Start erforderlich')}"
                    
                    return [TextContent(type="text", text=response)]
                
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
                
                
                # Workflow Engine Tools Handler
                elif name.startswith("bmad_workflow_"):
                    return await self._handle_workflow_tool(name, arguments)
                
                # Auto-Sync and MCP Monitoring Tools Handler
                elif name.startswith("bmad_start_auto_sync"):
                    return await self._handle_auto_sync_start()
                elif name.startswith("bmad_stop_auto_sync"):
                    return await self._handle_auto_sync_stop()
                elif name.startswith("bmad_start_mcp_monitoring"):
                    return await self._handle_mcp_monitoring_start(arguments.get("servers"))
                elif name.startswith("bmad_stop_mcp_monitoring"):
                    return await self._handle_mcp_monitoring_stop()
                elif name.startswith("bmad_get_sync_status"):
                    return await self._handle_get_sync_status()
                elif name.startswith("bmad_manual_reconnect_mcp"):
                    return await self._handle_manual_reconnect(arguments["server_name"])
                elif name.startswith("bmad_queue_sync_task"):
                    return await self._handle_queue_sync_task(arguments["task_type"], arguments["data"])
                
                # Original BMAD Core System Integration Handlers
                elif name == "bmad_get_original_agent_definition":
                    return await self.bmad_tools.get_original_agent_definition(arguments["agent_name"])
                
                elif name == "bmad_get_original_checklist":
                    return await self.bmad_tools.get_original_checklist(arguments["checklist_name"])
                
                elif name == "bmad_get_original_workflow":
                    return await self.bmad_tools.get_original_workflow(arguments["workflow_name"])
                
                elif name == "bmad_get_original_agent_team":
                    return await self.bmad_tools.get_original_agent_team(arguments["team_name"])
                
                elif name == "bmad_get_original_task_definition":
                    return await self.bmad_tools.get_original_task_definition(arguments["task_name"])
                
                elif name == "bmad_get_original_template":
                    return await self.bmad_tools.get_original_template(arguments["template_name"])
                
                elif name == "bmad_get_bmad_knowledge_base":
                    return await self.bmad_tools.get_bmad_knowledge_base()
                
                elif name == "bmad_get_bmad_user_guide":
                    return await self.bmad_tools.get_bmad_user_guide()
                
                elif name == "bmad_list_original_bmad_components":
                    return await self.bmad_tools.list_original_bmad_components()
                
                elif name == "bmad_validate_bmad_core_system":
                    return await self.bmad_tools.validate_bmad_core_system()
                
                # Time Tracking Tools
                elif name == "bmad_start_timer":
                    result = await self.time_tracking_tools.start_timer(
                        arguments["task_id"],
                        arguments["agent"],
                        arguments.get("session_type", "development"),
                        arguments.get("description")
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "bmad_stop_timer":
                    result = await self.time_tracking_tools.stop_timer(
                        arguments["task_id"],
                        arguments.get("ai_model_used"),
                        arguments.get("tokens_input", 0),
                        arguments.get("tokens_output", 0),
                        arguments.get("mark_completed", False)
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "bmad_get_active_timers":
                    result = await self.time_tracking_tools.get_active_timers()
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "bmad_get_task_time_summary":
                    result = await self.time_tracking_tools.get_task_time_summary(arguments["task_id"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "bmad_get_daily_time_report":
                    result = await self.time_tracking_tools.get_daily_report(arguments.get("date"))
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "bmad_get_project_billing":
                    result = await self.time_tracking_tools.get_project_billing(
                        arguments.get("project_id"),
                        arguments.get("start_date"),
                        arguments.get("end_date"),
                        arguments.get("export_format", "json")
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "bmad_auto_end_stale_sessions":
                    result = await self.time_tracking_tools.auto_end_stale_sessions(
                        arguments.get("max_hours", 8)
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "bmad_update_model_costs":
                    result = await self.time_tracking_tools.update_model_costs(arguments["model_costs"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "bmad_get_model_costs":
                    result = await self.time_tracking_tools.get_model_costs()
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
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
    
    
    async def _handle_workflow_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle Workflow Engine tool calls - BMAD-METHOD Implementation"""
        try:
            if name == "bmad_workflow_start_project":
                result = await self.workflow_engine.start_project_workflow(
                    project_name=arguments.get("project_name"),
                    initial_idea=arguments.get("initial_idea"),
                    workflow_type=arguments.get("workflow_type", "full")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_workflow_advance":
                result = await self.workflow_engine.advance_workflow(
                    workflow_id=arguments.get("workflow_id"),
                    target_state=arguments.get("target_state"),
                    agent_override=arguments.get("agent_override")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_workflow_execute_agent_command":
                result = await self.workflow_engine.execute_agent_command(
                    workflow_id=arguments.get("workflow_id"),
                    agent_type=arguments.get("agent_type"),
                    command=arguments.get("command"),
                    parameters=arguments.get("parameters", {})
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_workflow_start_story":
                result = await self.workflow_engine.start_story_cycle(
                    workflow_id=arguments.get("workflow_id"),
                    story_title=arguments.get("story_title"),
                    story_description=arguments.get("story_description"),
                    epic_id=arguments.get("epic_id")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_workflow_run_quality_gate":
                result = await self.workflow_engine.run_quality_gate(
                    workflow_id=arguments.get("workflow_id"),
                    story_id=arguments.get("story_id"),
                    gate_type=arguments.get("gate_type", "comprehensive")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_workflow_status":
                result = await self.workflow_engine.get_workflow_status(
                    workflow_id=arguments.get("workflow_id")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "bmad_workflow_generate_report":
                result = await self.workflow_engine.generate_workflow_report(
                    workflow_id=arguments.get("workflow_id")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            else:
                return [TextContent(type="text", text=f"❌ Unbekanntes Workflow-Tool: {name}")]
                
        except Exception as e:
            logger.error(f"Fehler beim Ausführen von Workflow-Tool {name}: {str(e)}")
            return [TextContent(type="text", text=f"❌ Fehler beim Ausführen von {name}: {str(e)}")]
    
    # Auto-Sync and MCP Monitoring Handlers
    async def _handle_auto_sync_start(self) -> List[TextContent]:
        """Start automatic synchronization monitoring"""
        try:
            result = await self.auto_sync_manager.start_auto_sync_monitoring()
            
            if result["success"]:
                response = f"✅ Auto-Sync Monitoring gestartet!\n\n"
                response += f"📊 Monitoring Status: {'Aktiv' if result['monitoring_active'] else 'Inaktiv'}\n"
                response += f"⏱️  Sync Interval: {result['sync_interval']} Sekunden\n"
                response += f"🔧 Überwachte Services: {', '.join(result['services_monitored'])}\n\n"
                response += f"💡 {result['message']}\n\n"
                response += "Das System überwacht jetzt automatisch alle Service-Verbindungen und führt Auto-Syncs durch!"
            else:
                response = f"❌ Fehler beim Starten des Auto-Sync Monitoring:\n{result.get('error', 'Unbekannter Fehler')}"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Error starting auto-sync: {e}")
            return [TextContent(type="text", text=f"❌ Fehler beim Starten des Auto-Sync: {str(e)}")]
    
    async def _handle_auto_sync_stop(self) -> List[TextContent]:
        """Stop automatic synchronization monitoring"""
        try:
            result = await self.auto_sync_manager.stop_auto_sync_monitoring()
            
            if result["success"]:
                response = f"⏹️  Auto-Sync Monitoring gestoppt!\n\n"
                response += f"📊 Final Status: {result.get('message', 'Erfolgreich gestoppt')}\n"
                
                final_status = result.get('final_status', {})
                if final_status:
                    response += f"\n📈 Finale Statistiken:\n"
                    response += f"  • Queue Länge: {final_status.get('sync_queue_length', 0)} Aufgaben\n"
                    response += f"  • Erfolgreich: {final_status.get('completed_tasks', 0)} Aufgaben\n"
                    response += f"  • Fehlgeschlagen: {final_status.get('failed_tasks', 0)} Aufgaben\n"
            else:
                response = f"❌ Fehler beim Stoppen des Auto-Sync Monitoring:\n{result.get('error', 'Unbekannter Fehler')}"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Error stopping auto-sync: {e}")
            return [TextContent(type="text", text=f"❌ Fehler beim Stoppen des Auto-Sync: {str(e)}")]
    
    async def _handle_mcp_monitoring_start(self, servers: List[str] = None) -> List[TextContent]:
        """Start MCP server reconnection monitoring"""
        try:
            result = await self.auto_reconnector.start_monitoring(servers)
            
            if result["success"]:
                response = f"🔄 MCP Auto-Reconnection gestartet!\n\n"
                response += f"📡 Überwachte Server: {', '.join(result['monitored_servers'])}\n"
                response += f"⏱️  Monitoring Interval: {result['monitoring_interval']}\n"
                response += f"🔄 Max Retry Versuche: {result['max_retries']}\n\n"
                response += f"💡 {result['message']}\n\n"
                response += "🚀 Das System überwacht jetzt automatisch MCP-Verbindungen und führt bei Bedarf Reconnections durch!"
            else:
                response = f"❌ Fehler beim Starten des MCP Monitoring:\n{result.get('error', 'Unbekannter Fehler')}"
                if 'message' in result:
                    response += f"\n💡 {result['message']}"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Error starting MCP monitoring: {e}")
            return [TextContent(type="text", text=f"❌ Fehler beim Starten des MCP Monitoring: {str(e)}")]
    
    async def _handle_mcp_monitoring_stop(self) -> List[TextContent]:
        """Stop MCP server monitoring"""
        try:
            result = await self.auto_reconnector.stop_monitoring()
            
            if result["success"]:
                response = f"⏹️  MCP Auto-Reconnection gestoppt!\n\n"
                response += f"💡 {result['message']}\n"
                
                final_status = result.get('final_status', {})
                if final_status and final_status.get('connection_status'):
                    response += f"\n📊 Finale Server Status:\n"
                    for server, status in final_status['connection_status'].items():
                        status_icon = "🟢" if status.get('status') == 'connected' else "🔴"
                        response += f"  {status_icon} {server}: {status.get('status', 'unknown')}\n"
            else:
                response = f"❌ Fehler beim Stoppen des MCP Monitoring:\n{result.get('error', 'Unbekannter Fehler')}"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Error stopping MCP monitoring: {e}")
            return [TextContent(type="text", text=f"❌ Fehler beim Stoppen des MCP Monitoring: {str(e)}")]
    
    async def _handle_get_sync_status(self) -> List[TextContent]:
        """Get current sync and MCP status"""
        try:
            # Get sync status
            sync_status = self.auto_sync_manager.get_sync_status()
            
            # Get MCP status
            mcp_status = self.auto_reconnector.get_connection_status()
            
            response = f"🔍 BMAD Auto-Sync & MCP Status Report\n"
            response += f"=" * 50 + "\n\n"
            
            # Auto-Sync Status
            response += f"📊 Auto-Sync Monitoring:\n"
            response += f"  Status: {'🟢 Aktiv' if sync_status['monitoring_active'] else '🔴 Inaktiv'}\n"
            response += f"  Queue Länge: {sync_status['sync_queue_length']} Aufgaben\n"
            response += f"  Erfolgreich: {sync_status['completed_tasks']} Aufgaben\n"
            response += f"  Fehlgeschlagen: {sync_status['failed_tasks']} Aufgaben\n\n"
            
            # Service Status
            if sync_status.get('services'):
                response += f"🔧 Service Verbindungen:\n"
                for service, info in sync_status['services'].items():
                    status_icon = "🟢" if info.get('connected') else "🔴"
                    response += f"  {status_icon} {service.title()}: {'Verbunden' if info.get('connected') else 'Getrennt'}\n"
                    if info.get('last_sync'):
                        response += f"    Letzter Sync: {info['last_sync']}\n"
                    if info.get('retry_count', 0) > 0:
                        response += f"    Retry Versuche: {info['retry_count']}\n"
                response += "\n"
            
            # MCP Status
            response += f"📡 MCP Server Monitoring:\n"
            response += f"  Status: {'🟢 Aktiv' if mcp_status['monitoring_active'] else '🔴 Inaktiv'}\n"
            response += f"  Überwachte Server: {', '.join(mcp_status.get('monitored_servers', []))}\n\n"
            
            # MCP Connection Status
            if mcp_status.get('connection_status'):
                response += f"🔌 MCP Server Verbindungen:\n"
                for server, status in mcp_status['connection_status'].items():
                    status_icon = "🟢" if status.get('status') == 'connected' else "🔴"
                    response += f"  {status_icon} {server}: {status.get('status', 'unknown').title()}\n"
                    if status.get('last_check'):
                        response += f"    Letzter Check: {status['last_check']}\n"
                    if status.get('consecutive_failures', 0) > 0:
                        response += f"    Konsekutive Fehler: {status['consecutive_failures']}\n"
                response += "\n"
            
            response += f"🕐 Letztes Update: {mcp_status.get('last_updated', 'Unbekannt')}"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return [TextContent(type="text", text=f"❌ Fehler beim Abrufen des Sync Status: {str(e)}")]
    
    async def _handle_manual_reconnect(self, server_name: str) -> List[TextContent]:
        """Manually reconnect a specific MCP server"""
        try:
            result = await self.auto_reconnector.manual_reconnect(server_name)
            
            if result["success"]:
                response = f"✅ MCP Server Reconnection erfolgreich!\n\n"
                response += f"🔌 Server: {result['server_name']}\n"
                response += f"💡 {result['message']}\n\n"
                
                if result.get('connection_status'):
                    status = result['connection_status']
                    response += f"📊 Connection Status:\n"
                    response += f"  Status: {status.get('status', 'unknown').title()}\n"
                    response += f"  Letzter Check: {status.get('last_check', 'Unbekannt')}\n"
                    response += f"  Fehleranzahl: {status.get('consecutive_failures', 0)}\n"
            else:
                response = f"❌ MCP Server Reconnection fehlgeschlagen!\n\n"
                response += f"🔌 Server: {server_name}\n"
                response += f"❌ Fehler: {result.get('error', 'Unbekannter Fehler')}\n"
                
                if result.get('available_servers'):
                    response += f"\n📡 Verfügbare Server: {', '.join(result['available_servers'])}"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Error in manual reconnect: {e}")
            return [TextContent(type="text", text=f"❌ Fehler beim manuellen Reconnect: {str(e)}")]
    
    async def _handle_queue_sync_task(self, task_type: str, data: dict) -> List[TextContent]:
        """Queue a manual synchronization task"""
        try:
            result = await self.auto_sync_manager.queue_sync_task(task_type, data)
            
            if result["success"]:
                response = f"✅ Sync Task erfolgreich in Queue eingereiht!\n\n"
                response += f"🆔 Task ID: {result['task_id']}\n"
                response += f"📝 Task Type: {task_type}\n"
                response += f"📍 Queue Position: {result['queue_position']}\n"
                response += f"💡 {result['message']}\n\n"
                response += "⏱️  Der Task wird automatisch vom Auto-Sync System verarbeitet."
            else:
                response = f"❌ Fehler beim Einreihen des Sync Tasks:\n{result.get('error', 'Unbekannter Fehler')}"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Error queuing sync task: {e}")
            return [TextContent(type="text", text=f"❌ Fehler beim Einreihen des Sync Tasks: {str(e)}")]


async def main():
    """Main server entry point - supports both Railway and MCP modes"""
    server_instance = BMadMCPServer()
    
    # Initialize workflow engine asynchronously
    await server_instance.workflow_engine.initialize()
    
    # Configure OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY not set. Some features may not work.")
    
    # Start auto-sync and MCP monitoring systems
    logger.info("Starting auto-sync and MCP monitoring systems...")
    try:
        # Start auto-sync monitoring
        sync_result = await server_instance.auto_sync_manager.start_auto_sync_monitoring()
        if sync_result["success"]:
            logger.info("✅ Auto-Sync Monitoring started successfully")
        else:
            logger.warning(f"⚠️  Auto-Sync Monitoring startup issue: {sync_result.get('error')}")
        
        # Start MCP reconnection monitoring - focus on Notion servers
        mcp_result = await server_instance.auto_reconnector.start_monitoring(["makenotion-notion-mcp-server"])
        if mcp_result["success"]:
            logger.info("✅ MCP Auto-Reconnection started successfully")
        else:
            logger.warning(f"⚠️  MCP Monitoring startup issue: {mcp_result.get('error')}")
        
    except Exception as e:
        logger.error(f"❌ Error starting monitoring systems: {e}")

    # Check if running on Railway (PORT env var exists)
    port = os.getenv("PORT")
    if port:
        # Railway deployment mode - run FastAPI HTTP server
        logger.info(f"🚀 Railway Deployment Mode - Starting HTTP server on port {port}")
        config = uvicorn.Config(
            server_instance.app,
            host="0.0.0.0",
            port=int(port),
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
    else:
        # Standard MCP mode - run with stdio transport
        logger.info("📡 Standard MCP Mode - Starting stdio server...")
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="bmad-mcp-server",
                    server_version="2.0.0",
                    capabilities={
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    }
                ),
            )

if __name__ == "__main__":
    asyncio.run(main())