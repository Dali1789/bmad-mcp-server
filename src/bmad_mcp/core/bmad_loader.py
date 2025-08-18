"""
BMAD Loader - Load BMAD configuration files and resources
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class BMadLoader:
    """Loads BMAD configuration files and resources"""
    
    def __init__(self, default_bmad_path: Optional[str] = None, global_registry=None):
        self.global_registry = global_registry
        
        # Default to local .bmad-core or fallback paths
        self.default_paths = [
            default_bmad_path,
            ".bmad-core",
            os.path.expanduser("~/.bmad-core"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "bmad-core")
        ]
        self.default_paths = [p for p in self.default_paths if p is not None]
    
    def _find_bmad_path(self) -> Optional[Path]:
        """Find available .bmad-core directory with global registry priority"""
        # First try global registry if available
        if self.global_registry:
            universal_path = self.global_registry.get_universal_bmad_path()
            if universal_path and universal_path.exists():
                return universal_path
        
        # Fall back to default paths
        for path_str in self.default_paths:
            path = Path(path_str)
            if path.exists() and path.is_dir():
                return path
        return None
    
    async def load_file(self, category: str, filename: str) -> Optional[str]:
        """Load file from BMAD directory"""
        bmad_path = self._find_bmad_path()
        if not bmad_path:
            return None
        
        file_path = bmad_path / category / filename
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error loading {file_path}: {str(e)}"
    
    async def load_yaml(self, category: str, filename: str) -> Optional[Dict[str, Any]]:
        """Load YAML file from BMAD directory"""
        content = await self.load_file(category, filename)
        if not content:
            return None
        
        try:
            return yaml.safe_load(content)
        except Exception as e:
            return {"error": f"YAML parse error: {str(e)}"}
    
    async def load_agent(self, agent_name: str) -> Optional[str]:
        """Load agent definition"""
        return await self.load_file("agents", f"{agent_name}.md")
    
    async def load_task(self, task_name: str) -> Optional[str]:
        """Load task definition"""
        # Try with .md extension first
        content = await self.load_file("tasks", f"{task_name}.md")
        if content:
            return content
        
        # Try without extension
        return await self.load_file("tasks", task_name)
    
    async def load_template(self, template_name: str) -> Optional[str]:
        """Load template definition"""
        # Try with .yaml extension first
        content = await self.load_file("templates", f"{template_name}.yaml")
        if content:
            return content
        
        # Try with .yml extension
        content = await self.load_file("templates", f"{template_name}.yml")
        if content:
            return content
        
        # Try without extension
        return await self.load_file("templates", template_name)
    
    async def load_checklist(self, checklist_name: str) -> Optional[str]:
        """Load checklist definition"""
        # Try with .md extension first
        content = await self.load_file("checklists", f"{checklist_name}.md")
        if content:
            return content
        
        # Try without extension
        return await self.load_file("checklists", checklist_name)
    
    async def load_data(self, data_name: str) -> Optional[str]:
        """Load data file"""
        # Try with .md extension first
        content = await self.load_file("data", f"{data_name}.md")
        if content:
            return content
        
        # Try with .yaml extension
        content = await self.load_file("data", f"{data_name}.yaml")
        if content:
            return content
        
        # Try without extension
        return await self.load_file("data", data_name)
    
    async def load_config(self) -> Optional[Dict[str, Any]]:
        """Load core BMAD configuration"""
        return await self.load_yaml(".", "core-config.yaml")
    
    async def list_files(self, category: str) -> List[str]:
        """List files in specific category"""
        bmad_path = self._find_bmad_path()
        if not bmad_path:
            return []
        
        category_path = bmad_path / category
        if not category_path.exists():
            return []
        
        files = []
        try:
            for file_path in category_path.iterdir():
                if file_path.is_file():
                    files.append(file_path.name)
        except Exception:
            pass
        
        return sorted(files)
    
    async def get_available_resources(self) -> Dict[str, List[str]]:
        """Get all available BMAD resources"""
        categories = ["agents", "tasks", "templates", "checklists", "workflows", "data"]
        resources = {}
        
        for category in categories:
            resources[category] = await self.list_files(category)
        
        return resources