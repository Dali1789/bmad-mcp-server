"""
BMAD Global System Tools - MCP Integration for Global BMAD System v2.0
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BMadGlobalSystem:
    """Global BMAD System Management for MCP Server"""
    
    def __init__(self):
        self.global_path = Path(os.path.expanduser("~/.bmad-global"))
        self.config_path = self.global_path / "bmad-global-config.json"
        self.projects_path = self.global_path / "projects"
        self.agents_path = self.global_path / "agents"
        
        self._ensure_global_structure()
        self.config = self._load_global_config()
    
    def _ensure_global_structure(self):
        """Ensure global BMAD directory structure exists"""
        directories = [
            self.global_path,
            self.projects_path,
            self.agents_path,
            self.global_path / "configs",
            self.global_path / "logs",
            self.global_path / "shared-resources",
            self.global_path / "templates",
            self.global_path / "bin",
            self.global_path / "migration-backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_global_config(self) -> Dict[str, Any]:
        """Load or create global configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading global config: {e}")
                return self._get_default_config()
        else:
            config = self._get_default_config()
            self._save_global_config(config)
            return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default global configuration"""
        return {
            "version": "2.0.0",
            "system_name": "BMAD Global System",
            "openrouter_api_base": "https://openrouter.ai/api/v1",
            "model_routing": {
                "development": {
                    "model": "anthropic/claude-3.5-sonnet",
                    "temperature": 0.1
                },
                "analysis": {
                    "model": "perplexity/sonar-pro",
                    "temperature": 0.2
                },
                "architecture": {
                    "model": "anthropic/claude-3-opus",
                    "temperature": 0.3
                },
                "pm": {
                    "model": "google/gemini-pro",
                    "temperature": 0.4
                },
                "quick": {
                    "model": "anthropic/claude-3-haiku",
                    "temperature": 0.1
                }
            },
            "global_agents": ["dev", "analyst", "architect", "pm", "qa"],
            "integrations": {
                "notion": {"enabled": True},
                "slack": {"enabled": True},
                "github": {"enabled": True}
            },
            "projects": {}
        }
    
    def _save_global_config(self, config: Dict[str, Any]):
        """Save global configuration"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            logger.info("Global config saved successfully")
        except Exception as e:
            logger.error(f"Error saving global config: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "version": self.config.get("version", "2.0.0"),
            "system_name": self.config.get("system_name", "BMAD Global System"),
            "global_path": str(self.global_path),
            "projects_registered": len(self.config.get("projects", {})),
            "available_agents": self.config.get("global_agents", []),
            "integrations": self.config.get("integrations", {}),
            "model_routing": self.config.get("model_routing", {})
        }
    
    def register_project(self, project_path: str, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new project with the global system"""
        try:
            project_path_obj = Path(project_path).resolve()
            project_id = project_path_obj.name
            
            # Add project to global config
            self.config["projects"][project_id] = {
                "name": project_config.get("project_name", project_id),
                "path": str(project_path_obj),
                "type": project_config.get("project_type", "unknown"),
                "version": project_config.get("version", "1.0.0"),
                "tech_stack": project_config.get("tech_stack", []),
                "agents": project_config.get("agents", []),
                "registered_at": datetime.now().isoformat()
            }
            
            self._save_global_config(self.config)
            
            # Create .bmad-core file in project
            bmad_core = {
                "bmad_version": "2.0.0",
                "project_id": project_id,
                "global_config_path": str(self.config_path),
                "agents": project_config.get("agents", []),
                "initialized_at": datetime.now().isoformat()
            }
            
            bmad_core_path = project_path_obj / ".bmad-core"
            with open(bmad_core_path, 'w', encoding='utf-8') as f:
                json.dump(bmad_core, f, indent=2)
            
            logger.info(f"Project '{project_config.get('project_name', project_id)}' registered successfully")
            return {
                "success": True,
                "project_id": project_id,
                "message": f"Project registered successfully with ID: {project_id}"
            }
            
        except Exception as e:
            logger.error(f"Error registering project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all registered projects"""
        projects = []
        for project_id, project_data in self.config.get("projects", {}).items():
            projects.append({
                "id": project_id,
                "name": project_data.get("name", project_id),
                "type": project_data.get("type", "unknown"),
                "path": project_data.get("path", ""),
                "agents": project_data.get("agents", []),
                "tech_stack": project_data.get("tech_stack", []),
                "registered_at": project_data.get("registered_at", "")
            })
        return projects
    
    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific project"""
        return self.config.get("projects", {}).get(project_id)
    
    def select_model(self, task_type: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Select appropriate model for task type and project"""
        routing = self.config.get("model_routing", {})
        
        # Check project-specific overrides
        if project_id and project_id in self.config.get("projects", {}):
            project = self.config["projects"][project_id]
            if "model_overrides" in project and task_type in project["model_overrides"]:
                return project["model_overrides"][task_type]
        
        # Return global routing or default
        return routing.get(task_type, routing.get("development", {
            "model": "anthropic/claude-3.5-sonnet",
            "temperature": 0.1
        }))
    
    def initialize_agent(self, agent_type: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Initialize an agent with appropriate model selection"""
        model_config = self.select_model(agent_type, project_id)
        
        result = {
            "agent": agent_type,
            "model": model_config,
            "project": project_id,
            "initialized_at": datetime.now().isoformat()
        }
        
        if project_id:
            project = self.config.get("projects", {}).get(project_id)
            if project:
                result["project_info"] = {
                    "name": project.get("name"),
                    "path": project.get("path"),
                    "type": project.get("type"),
                    "tech_stack": project.get("tech_stack", [])
                }
        
        logger.info(f"Agent {agent_type} initialized with model {model_config.get('model')}")
        return result


# Global instance
global_system = BMadGlobalSystem()