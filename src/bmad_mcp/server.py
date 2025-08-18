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
from mcp.server.sse import SseServerTransport
from fastapi import FastAPI, Request
from starlette.responses import Response
import uvicorn
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


async def main():
    """Main server entry point"""
    server_instance = BMadMCPServer()
    
    # Configure OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY not set. Some features may not work.")

    # Always run in web mode as stdio is unreliable
    logger.info("Starting BMAD MCP Server in WEB (SSE) mode...")
    
    app = FastAPI()
    
    # Initialize SSE transport with proper configuration
    sse_transport = SseServerTransport("/messages")

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "bmad-mcp-server", "version": "1.0.0"}

    @app.get("/sse")
    async def handle_sse(request: Request):
        """SSE endpoint for MCP communication"""
        logger.info("SSE connection established")
        try:
            async with sse_transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server_instance.server.run(
                    streams[0],
                    streams[1],
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
        except Exception as e:
            logger.error(f"Error in SSE connection: {e}")
            # Don't return a response here as SSE is a streaming protocol
            raise

    @app.post("/messages")
    async def handle_messages(request: Request):
        """Handle MCP messages"""
        try:
            # Handle the message without returning a response
            # The SSE transport will handle the response through the SSE connection
            await sse_transport.handle_post_message(
                request.scope, request.receive, request._send
            )
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            # Let FastAPI handle the error response properly
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=str(e))

    port = int(os.getenv("PORT", 3000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())