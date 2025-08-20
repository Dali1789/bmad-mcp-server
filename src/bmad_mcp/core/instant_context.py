"""
BMAD Instant Context Loader
Automatische Projekt-Erkennung und Kontext-Loading für sofortigen Start
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from .universal_schema import get_universal_schema

logger = logging.getLogger(__name__)

@dataclass
class ProjectStatus:
    """Live Projekt Status"""
    name: str
    current_phase: str
    active_agent: str
    current_task: str
    progress: int
    next_steps: Dict[str, Any]
    context: Dict[str, Any]
    last_updated: str

class BMadInstantContext:
    """
    Lädt sofort Projekt-Context beim ersten MCP-Zugriff
    Eliminiert Discovery-Zeit durch intelligente Auto-Detection
    """
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self.project_cache = {}
        self.universal_schema = get_universal_schema()
        self._load_session_cache()
    
    def get_instant_context(self) -> Dict[str, Any]:
        """Hauptfunktion: Lädt sofort verfügbaren Projekt-Context"""
        try:
            # 1. Prüfe Session Cache für schnellen Access
            cached_project = self._get_cached_project()
            if cached_project:
                return self._build_context_response(cached_project)
            
            # 2. Auto-detect aktuelles Projekt
            project = self._auto_detect_project()
            if project:
                # Cache für nächsten Zugriff
                self._cache_project(project)
                return self._build_context_response(project)
            
            # 3. Fallback: Zeige verfügbare Projekte
            available_projects = self._scan_available_projects()
            return {
                "status": "no_active_project",
                "message": "Kein aktives Projekt gefunden. Verfügbare Projekte:",
                "available_projects": available_projects,
                "action_required": "Wechseln Sie in ein Projektverzeichnis oder wählen Sie ein Projekt aus"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Context Loading Fehler: {str(e)}",
                "fallback": "Manueller Agent-Start erforderlich"
            }
    
    def _auto_detect_project(self) -> Optional[ProjectStatus]:
        """Erkennt automatisch aktuelles BMAD-Projekt"""
        current_path = Path(self.current_directory)
        
        # Suche nach .bmad-core in aktueller und Parent-Directories
        for path in [current_path] + list(current_path.parents):
            bmad_core_path = path / ".bmad-core"
            if bmad_core_path.exists():
                return self._load_project_status(bmad_core_path)
        
        # Nutze Universal Schema für Projekt-Erkennung
        detected_project = self.universal_schema.auto_detect_current_project(self.current_directory)
        if detected_project:
            bmad_path = Path(detected_project["bmad_core"])
            return self._load_project_status(bmad_path)
        
        return None
    
    def _load_project_status(self, bmad_core_path: Path) -> ProjectStatus:
        """Lädt Projekt-Status aus .bmad-core"""
        project_name = bmad_core_path.parent.name
        
        # Prüfe project-status.yaml
        status_file = bmad_core_path / "project-status.yaml"
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = yaml.safe_load(f)
                return ProjectStatus(**status_data)
        
        # Fallback: Erstelle Standard-Status
        return self._create_default_status(project_name, bmad_core_path)
    
    def _create_default_status(self, project_name: str, bmad_core_path: Path) -> ProjectStatus:
        """Erstellt Standard-Status falls keiner vorhanden"""
        
        # Analysiere Projekt-Struktur für intelligente Defaults
        context = self._analyze_project_structure(bmad_core_path.parent)
        
        # Bestimme aktuelle Phase basierend auf Dateien
        current_phase = self._detect_project_phase(bmad_core_path.parent)
        
        # Empfehle Agent basierend auf Phase
        recommended_agent = self._suggest_agent_for_phase(current_phase)
        
        status = ProjectStatus(
            name=project_name,
            current_phase=current_phase,
            active_agent=recommended_agent,
            current_task=f"Continue {current_phase} work",
            progress=0,
            next_steps={
                "immediate": f"Resume {current_phase} development",
                "action": f"Use *agent {recommended_agent} to continue"
            },
            context=context,
            last_updated=datetime.now().isoformat()
        )
        
        # Speichere für nächsten Zugriff
        self._save_project_status(bmad_core_path, status)
        
        return status
    
    def _analyze_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analysiert Projekt-Struktur für Context"""
        context = {
            "project_path": str(project_path),
            "has_docs": (project_path / "docs").exists(),
            "has_src": (project_path / "src").exists(),
            "has_tests": (project_path / "tests").exists(),
            "has_package_json": (project_path / "package.json").exists(),
            "has_requirements": (project_path / "requirements.txt").exists(),
            "git_repo": (project_path / ".git").exists()
        }
        
        # Erkenne Tech Stack
        tech_stack = []
        if context["has_package_json"]:
            tech_stack.append("Node.js")
        if context["has_requirements"]:
            tech_stack.append("Python")
        if (project_path / "Cargo.toml").exists():
            tech_stack.append("Rust")
        
        context["tech_stack"] = tech_stack
        return context
    
    def _detect_project_phase(self, project_path: Path) -> str:
        """Erkennt aktuelle Projekt-Phase"""
        # Prüfe auf PRD
        if (project_path / "docs" / "prd.md").exists():
            # Prüfe auf Code
            if (project_path / "src").exists() and any((project_path / "src").iterdir()):
                # Prüfe auf Tests
                if (project_path / "tests").exists() and any((project_path / "tests").iterdir()):
                    return "testing"
                else:
                    return "development"
            else:
                return "architecture"
        else:
            return "planning"
    
    def _suggest_agent_for_phase(self, phase: str) -> str:
        """Schlägt passenden Agent für Phase vor"""
        phase_to_agent = {
            "planning": "analyst",
            "architecture": "architect", 
            "development": "dev",
            "testing": "qa",
            "deployment": "pm"
        }
        return phase_to_agent.get(phase, "dev")
    
    def _build_context_response(self, project: ProjectStatus) -> Dict[str, Any]:
        """Baut vollständige Context-Response"""
        return {
            "status": "project_detected",
            "project": {
                "name": project.name,
                "phase": project.current_phase,
                "progress": f"{project.progress}%"
            },
            "recommendation": {
                "agent": project.active_agent,
                "command": f"*agent {project.active_agent}",
                "current_task": project.current_task
            },
            "next_steps": project.next_steps,
            "context": project.context,
            "quick_start": f"Verwende '*agent {project.active_agent}' um sofort loszulegen"
        }
    
    def _scan_available_projects(self) -> List[Dict[str, str]]:
        """Scannt verfügbare BMAD-Projekte über Universal Schema"""
        projects = self.universal_schema.scan_for_projects()
        
        # Konvertiere zu erwartetes Format
        formatted_projects = []
        for project in projects:
            formatted_projects.append({
                "name": project["name"],
                "path": project["path"],
                "status": project.get("status", "unknown"),
                "command": f"cd \"{project['path']}\" && bmad instant_context"
            })
        
        return formatted_projects
    
    def _get_cached_project(self) -> Optional[ProjectStatus]:
        """Holt gecachtes Projekt für aktuelles Directory"""
        cache_key = str(Path(self.current_directory).resolve())
        return self.project_cache.get(cache_key)
    
    def _cache_project(self, project: ProjectStatus):
        """Cached Projekt für schnellen Zugriff"""
        cache_key = str(Path(self.current_directory).resolve())
        self.project_cache[cache_key] = project
        self._save_session_cache()
    
    def _load_session_cache(self):
        """Lädt Session Cache über Universal Schema"""
        cache_file = self.universal_schema.get_base_directory() / ".bmad-session-cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Convert cache data back to ProjectStatus objects
                    for key, data in cache_data.items():
                        if isinstance(data, dict) and 'name' in data:
                            self.project_cache[key] = ProjectStatus(**data)
            except Exception as e:
                logger.warning(f"Cache loading failed: {e}")
    
    def _save_session_cache(self):
        """Speichert Session Cache über Universal Schema"""
        cache_file = self.universal_schema.get_base_directory() / ".bmad-session-cache.json"
        try:
            # Convert ProjectStatus objects to dict for JSON serialization
            cache_data = {}
            for key, project in self.project_cache.items():
                if isinstance(project, ProjectStatus):
                    cache_data[key] = {
                        "name": project.name,
                        "current_phase": project.current_phase,
                        "active_agent": project.active_agent,
                        "current_task": project.current_task,
                        "progress": project.progress,
                        "next_steps": project.next_steps,
                        "context": project.context,
                        "last_updated": project.last_updated
                    }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Cache saving failed: {e}")
    
    def _save_project_status(self, bmad_core_path: Path, status: ProjectStatus):
        """Speichert Projekt-Status in .bmad-core"""
        status_file = bmad_core_path / "project-status.yaml"
        status_data = {
            "name": status.name,
            "current_phase": status.current_phase,
            "active_agent": status.active_agent,
            "current_task": status.current_task,
            "progress": status.progress,
            "next_steps": status.next_steps,
            "context": status.context,
            "last_updated": status.last_updated
        }
        
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                yaml.dump(status_data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            logger.error(f"Failed to save project status: {e}")

# Global instance
_instant_context = None

def get_instant_context() -> BMadInstantContext:
    """Singleton für Instant Context"""
    global _instant_context
    if _instant_context is None:
        _instant_context = BMadInstantContext()
    return _instant_context