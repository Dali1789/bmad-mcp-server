"""
BMAD Universal Directory Schema
Gewährleistet einheitliche Ordnerstruktur für jeden User/System
"""

import os
import platform
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class BMadUniversalSchema:
    """
    Definiert universelle BMAD Ordnerstruktur für alle User/Systeme
    Automatische Erkennung von OS-spezifischen Pfaden
    """
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.user_home = Path.home()
        self.schema = self._define_universal_schema()
    
    def _define_universal_schema(self) -> Dict[str, Path]:
        """Definiert OS-unabhängige BMAD Struktur"""
        
        # Base Directory Detection
        if self.os_type == "windows":
            base_dir = self.user_home / "AppData" / "Roaming" / "Claude"
        elif self.os_type == "darwin":  # macOS
            base_dir = self.user_home / ".config" / "claude"
        else:  # Linux/Unix
            base_dir = self.user_home / ".config" / "claude"
        
        return {
            # Core BMAD Directories
            "base": base_dir,
            "projects": base_dir / "projects",
            "templates": base_dir / "templates", 
            "global_config": base_dir / "bmad-global-config.yaml",
            "session_cache": base_dir / ".bmad-session-cache.json",
            
            # Project Sub-Structure (für jedes Projekt)
            "project_core": ".bmad-core",  # Relative path
            "project_docs": "docs",
            "project_src": "src", 
            "project_tests": "tests",
            
            # BMAD Core Files (in jedem .bmad-core/)
            "core_status": "project-status.yaml",
            "core_log": "development-log.md",
            "core_config": "core-config.yaml",
            "core_agents": "agents",
            "core_workflows": "workflows", 
            "core_checklists": "checklists",
            "core_templates": "templates"
        }
    
    def get_base_directory(self) -> Path:
        """Holt Base Directory für aktuellen User"""
        return self.schema["base"]
    
    def get_projects_directory(self) -> Path:
        """Holt Projekte-Verzeichnis"""
        return self.schema["projects"]
    
    def ensure_directories_exist(self) -> Dict[str, bool]:
        """Erstellt alle notwendigen Verzeichnisse"""
        results = {}
        
        # Hauptverzeichnisse erstellen
        main_dirs = ["base", "projects", "templates"]
        
        for dir_name in main_dirs:
            dir_path = self.schema[dir_name]
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                results[dir_name] = True
                logger.info(f"✅ Directory ensured: {dir_path}")
            except Exception as e:
                results[dir_name] = False
                logger.error(f"❌ Failed to create {dir_name}: {e}")
        
        return results
    
    def get_project_structure(self, project_name: str) -> Dict[str, Path]:
        """Holt vollständige Projekt-Struktur für gegebenen Projektnamen"""
        project_base = self.schema["projects"] / project_name
        
        return {
            "project_root": project_base,
            "bmad_core": project_base / self.schema["project_core"],
            "docs": project_base / self.schema["project_docs"],
            "src": project_base / self.schema["project_src"],
            "tests": project_base / self.schema["project_tests"],
            
            # BMAD Core Files
            "status_file": project_base / self.schema["project_core"] / self.schema["core_status"],
            "log_file": project_base / self.schema["project_core"] / self.schema["core_log"],
            "config_file": project_base / self.schema["project_core"] / self.schema["core_config"],
            "agents_dir": project_base / self.schema["project_core"] / self.schema["core_agents"],
            "workflows_dir": project_base / self.schema["project_core"] / self.schema["core_workflows"],
            "checklists_dir": project_base / self.schema["project_core"] / self.schema["core_checklists"],
            "templates_dir": project_base / self.schema["project_core"] / self.schema["core_templates"]
        }
    
    def scan_for_projects(self) -> List[Dict[str, str]]:
        """Scannt nach allen BMAD-Projekten in Standard-Verzeichnissen"""
        projects = []
        
        # Scan primäres Projekte-Verzeichnis
        if self.schema["projects"].exists():
            projects.extend(self._scan_directory_for_projects(self.schema["projects"]))
        
        # Scan Base Directory für legacy Projekte
        if self.schema["base"].exists():
            projects.extend(self._scan_directory_for_projects(self.schema["base"]))
        
        # Scan Current Working Directory
        current_dir = Path.cwd()
        projects.extend(self._scan_directory_for_projects(current_dir, max_depth=2))
        
        # Duplikate entfernen
        unique_projects = {}
        for project in projects:
            key = project["name"]
            if key not in unique_projects:
                unique_projects[key] = project
        
        return list(unique_projects.values())
    
    def _scan_directory_for_projects(self, directory: Path, max_depth: int = 1) -> List[Dict[str, str]]:
        """Scannt Verzeichnis nach BMAD-Projekten"""
        projects = []
        
        if not directory.exists():
            return projects
        
        def scan_recursive(path: Path, current_depth: int = 0):
            if current_depth > max_depth:
                return
            
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        # Prüfe auf .bmad-core
                        bmad_core_path = item / ".bmad-core"
                        if bmad_core_path.exists():
                            projects.append({
                                "name": item.name,
                                "path": str(item),
                                "bmad_core": str(bmad_core_path),
                                "status": "active" if (bmad_core_path / "project-status.yaml").exists() else "legacy"
                            })
                        
                        # Rekursiv scannen wenn noch nicht max depth
                        if current_depth < max_depth:
                            scan_recursive(item, current_depth + 1)
                            
            except PermissionError:
                logger.warning(f"Permission denied scanning: {path}")
        
        scan_recursive(directory)
        return projects
    
    def auto_detect_current_project(self, current_path: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Automatische Projekt-Erkennung basierend auf aktuellem Pfad"""
        if current_path is None:
            current_path = os.getcwd()
        
        current_dir = Path(current_path).resolve()
        
        # Suche nach .bmad-core in aktueller und Parent-Directories
        for path in [current_dir] + list(current_dir.parents):
            bmad_core_path = path / ".bmad-core"
            if bmad_core_path.exists():
                return {
                    "name": path.name,
                    "path": str(path),
                    "bmad_core": str(bmad_core_path),
                    "status": "active"
                }
        
        return None
    
    def validate_project_structure(self, project_path: str) -> Dict[str, bool]:
        """Validiert ob Projekt der BMAD Struktur entspricht"""
        project = Path(project_path)
        structure = self.get_project_structure(project.name)
        
        validation = {}
        
        # Prüfe Hauptverzeichnisse
        for key, path in structure.items():
            if key.endswith("_dir") or key in ["project_root", "bmad_core", "docs", "src", "tests"]:
                validation[key] = path.exists()
        
        # Prüfe kritische Dateien
        critical_files = ["status_file", "log_file"]
        for file_key in critical_files:
            validation[file_key] = structure[file_key].exists()
        
        return validation
    
    def get_schema_info(self) -> Dict[str, str]:
        """Gibt Schema-Informationen für Debugging zurück"""
        return {
            "os_type": self.os_type,
            "user_home": str(self.user_home),
            "base_directory": str(self.schema["base"]),
            "projects_directory": str(self.schema["projects"]),
            "schema_version": "2.0.0"
        }

# Global Singleton
_universal_schema = None

def get_universal_schema() -> BMadUniversalSchema:
    """Singleton für Universal Schema"""
    global _universal_schema
    if _universal_schema is None:
        _universal_schema = BMadUniversalSchema()
        # Erstelle Verzeichnisse beim ersten Zugriff
        _universal_schema.ensure_directories_exist()
    return _universal_schema