"""
BMAD Project Detection - Scan for .bmad-core configurations
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class ProjectDetector:
    """Detects and analyzes BMAD projects"""
    
    def __init__(self, global_registry=None):
        self.global_registry = global_registry
        self.bmad_dir_name = ".bmad-core"
        self.config_file_name = "core-config.yaml"
    
    async def detect_project(self, start_path: str = ".") -> Optional[Dict[str, Any]]:
        """
        Detect BMAD project by scanning for .bmad-core directory
        
        Returns project info if found, None otherwise
        """
        # First check if there's an active project in global registry
        if self.global_registry:
            active_project = self.global_registry.get_active_project()
            if active_project:
                bmad_path = Path(active_project['bmad_core_path'])
                if bmad_path.exists():
                    return await self._analyze_project(bmad_path)
        
        # Fall back to local detection
        current_path = Path(start_path).resolve()
        
        # Search up the directory tree
        for path in [current_path] + list(current_path.parents):
            bmad_path = path / self.bmad_dir_name
            
            if bmad_path.exists() and bmad_path.is_dir():
                # Auto-register discovered projects if registry is available
                if self.global_registry:
                    try:
                        self.global_registry.register_project(str(path))
                    except Exception:
                        pass  # Ignore registration errors
                
                return await self._analyze_project(bmad_path)
        
        return None
    
    async def _analyze_project(self, bmad_path: Path) -> Dict[str, Any]:
        """Analyze BMAD project structure"""
        config_file = bmad_path / self.config_file_name
        
        # Load configuration
        config = {}
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            except Exception as e:
                config = {"error": f"Failed to load config: {str(e)}"}
        
        # Scan for resources
        project_info = {
            "path": str(bmad_path.parent),
            "bmad_path": str(bmad_path),
            "config_file": str(config_file),
            "config": config,
            "agents": await self._scan_directory(bmad_path / "agents"),
            "tasks": await self._scan_directory(bmad_path / "tasks"),
            "templates": await self._scan_directory(bmad_path / "templates"),
            "checklists": await self._scan_directory(bmad_path / "checklists"),
            "workflows": await self._scan_directory(bmad_path / "workflows"),
            "data": await self._scan_directory(bmad_path / "data")
        }
        
        return project_info
    
    async def _scan_directory(self, dir_path: Path) -> List[str]:
        """Scan directory for files"""
        if not dir_path.exists():
            return []
        
        files = []
        try:
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    files.append(file_path.name)
        except Exception:
            pass
        
        return sorted(files)
    
    def find_bmad_file(self, project_path: str, category: str, filename: str) -> Optional[Path]:
        """Find specific BMAD file in project"""
        bmad_path = Path(project_path) / self.bmad_dir_name
        file_path = bmad_path / category / filename
        
        return file_path if file_path.exists() else None
    
    async def get_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Get complete project structure"""
        project_info = await self.detect_project(project_path)
        
        if not project_info:
            return {"error": "No BMAD project found"}
        
        # Add file counts and details
        structure = {
            "project_path": project_info["path"],
            "config": project_info["config"],
            "resources": {
                "agents": {
                    "count": len(project_info["agents"]),
                    "files": project_info["agents"]
                },
                "tasks": {
                    "count": len(project_info["tasks"]),
                    "files": project_info["tasks"]
                },
                "templates": {
                    "count": len(project_info["templates"]),
                    "files": project_info["templates"]
                },
                "checklists": {
                    "count": len(project_info["checklists"]),
                    "files": project_info["checklists"]
                },
                "workflows": {
                    "count": len(project_info["workflows"]),
                    "files": project_info["workflows"]
                },
                "data": {
                    "count": len(project_info["data"]),
                    "files": project_info["data"]
                }
            }
        }
        
        return structure