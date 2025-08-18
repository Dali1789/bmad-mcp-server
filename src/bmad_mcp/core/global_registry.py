"""
BMAD Global Registry - Zentralisierte Projektverwaltung für universelle IDE-Zugänglichkeit
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil


class BMadGlobalRegistry:
    """
    Zentralisierte BMAD-Registry für einheitliche Projektzugriffe
    Ermöglicht konsistente .bmad-core Zugriffe von jedem IDE aus
    """
    
    def __init__(self):
        # Globale BMAD-Registry Pfade
        self.global_bmad_home = Path.home() / ".bmad-global"
        self.registry_file = self.global_bmad_home / "project-registry.json"
        self.global_config_file = self.global_bmad_home / "global-config.yaml"
        self.shared_resources = self.global_bmad_home / "shared-resources"
        
        # Projekt-spezifische Pfade
        self.projects_dir = self.global_bmad_home / "projects"
        self.templates_dir = self.shared_resources / "templates"
        self.agents_dir = self.shared_resources / "agents"
        self.workflows_dir = self.shared_resources / "workflows"
        
        self._ensure_structure()
    
    def _ensure_structure(self):
        """Erstelle globale BMAD-Struktur falls nicht vorhanden"""
        directories = [
            self.global_bmad_home,
            self.projects_dir,
            self.shared_resources,
            self.templates_dir,
            self.agents_dir,
            self.workflows_dir,
            self.shared_resources / "tasks",
            self.shared_resources / "checklists",
            self.shared_resources / "data"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Erstelle Standard-Registry falls nicht vorhanden
        if not self.registry_file.exists():
            self._create_default_registry()
        
        # Erstelle globale Konfiguration
        if not self.global_config_file.exists():
            self._create_global_config()
    
    def _create_default_registry(self):
        """Erstelle Standard-Projekt-Registry"""
        default_registry = {
            "version": "1.0.0",
            "projects": {},
            "active_project": None,
            "global_settings": {
                "auto_sync": True,
                "shared_resources_enabled": True,
                "default_agent": "dev"
            }
        }
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(default_registry, f, indent=2)
    
    def _create_global_config(self):
        """Erstelle globale BMAD-Konfiguration"""
        global_config = {
            "bmad_global": {
                "version": "1.0.0",
                "registry_path": str(self.global_bmad_home),
                "shared_resources_path": str(self.shared_resources),
                "auto_discover_projects": True
            },
            "default_agents": {
                "analyst": {
                    "model": "perplexity/llama-3.1-sonar-large-128k-online",
                    "temperature": 0.2
                },
                "architect": {
                    "model": "anthropic/claude-3-opus", 
                    "temperature": 0.3
                },
                "dev": {
                    "model": "anthropic/claude-3.5-sonnet",
                    "temperature": 0.1
                },
                "pm": {
                    "model": "google/gemini-pro-1.5",
                    "temperature": 0.4
                },
                "qa": {
                    "model": "anthropic/claude-3-haiku",
                    "temperature": 0.1
                }
            },
            "ide_integration": {
                "kilo_code": True,
                "claude_code": True,
                "vscode": True,
                "cursor": True
            }
        }
        
        with open(self.global_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(global_config, f, default_flow_style=False)
    
    def register_project(self, project_path: str, project_name: str = None) -> Dict[str, Any]:
        """Registriere Projekt in globaler Registry"""
        project_path = Path(project_path).resolve()
        bmad_core_path = project_path / ".bmad-core"
        
        if not bmad_core_path.exists():
            raise ValueError(f"Kein .bmad-core Verzeichnis gefunden in: {project_path}")
        
        # Automatischer Projektname falls nicht angegeben
        if not project_name:
            project_name = project_path.name
        
        # Lade aktuelle Registry
        registry = self._load_registry()
        
        # Projekt-Info erstellen
        project_info = {
            "name": project_name,
            "path": str(project_path),
            "bmad_core_path": str(bmad_core_path),
            "registered_at": self._get_timestamp(),
            "last_accessed": self._get_timestamp(),
            "active": False,
            "sync_status": "synced"
        }
        
        # Projekt registrieren
        registry["projects"][project_name] = project_info
        
        # Registry speichern
        self._save_registry(registry)
        
        # Projekt-spezifische Struktur erstellen
        self._create_project_structure(project_name, project_info)
        
        return project_info
    
    def _create_project_structure(self, project_name: str, project_info: Dict[str, Any]):
        """Erstelle projekt-spezifische Struktur in globaler Registry"""
        project_dir = self.projects_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Symlinks zu Original-.bmad-core erstellen (falls möglich)
        original_bmad = Path(project_info["bmad_core_path"])
        target_bmad = project_dir / ".bmad-core"
        
        try:
            if target_bmad.exists():
                if target_bmad.is_symlink():
                    target_bmad.unlink()
                else:
                    shutil.rmtree(target_bmad)
            
            # Symlink erstellen (Windows: mklink /D, Unix: ln -s)
            if os.name == 'nt':  # Windows
                os.system(f'mklink /D "{target_bmad}" "{original_bmad}"')
            else:  # Unix/Linux/Mac
                target_bmad.symlink_to(original_bmad)
                
        except Exception:
            # Fallback: Kopiere Struktur
            shutil.copytree(original_bmad, target_bmad, dirs_exist_ok=True)
    
    def get_active_project(self) -> Optional[Dict[str, Any]]:
        """Hole aktives Projekt"""
        registry = self._load_registry()
        active_project_name = registry.get("active_project")
        
        if active_project_name and active_project_name in registry["projects"]:
            return registry["projects"][active_project_name]
        
        return None
    
    def set_active_project(self, project_name: str) -> bool:
        """Setze aktives Projekt"""
        registry = self._load_registry()
        
        if project_name not in registry["projects"]:
            return False
        
        # Alle Projekte inaktiv setzen
        for project in registry["projects"].values():
            project["active"] = False
        
        # Gewähltes Projekt aktivieren
        registry["projects"][project_name]["active"] = True
        registry["projects"][project_name]["last_accessed"] = self._get_timestamp()
        registry["active_project"] = project_name
        
        self._save_registry(registry)
        return True
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Liste alle registrierten Projekte"""
        registry = self._load_registry()
        return list(registry["projects"].values())
    
    def get_project_path(self, project_name: str) -> Optional[str]:
        """Hole Projekt-Pfad"""
        registry = self._load_registry()
        project = registry["projects"].get(project_name)
        return project["path"] if project else None
    
    def get_universal_bmad_path(self, project_name: str = None) -> Optional[Path]:
        """
        Hole universellen .bmad-core Pfad
        Funktioniert von jedem IDE aus gleich
        """
        if project_name:
            project_dir = self.projects_dir / project_name
            bmad_path = project_dir / ".bmad-core"
            return bmad_path if bmad_path.exists() else None
        
        # Aktives Projekt verwenden
        active_project = self.get_active_project()
        if active_project:
            project_dir = self.projects_dir / active_project["name"]
            bmad_path = project_dir / ".bmad-core"
            return bmad_path if bmad_path.exists() else None
        
        return None
    
    def sync_shared_resources(self):
        """Synchronisiere geteilte Ressourcen mit lokalem System"""
        # Kopiere aus aktivem .bmad-core zu shared resources
        local_bmad_path = Path.home() / "AppData" / "Roaming" / "Claude" / ".bmad-core"
        
        if local_bmad_path.exists():
            # Agents synchronisieren
            local_agents = local_bmad_path / "agents"
            if local_agents.exists():
                shutil.copytree(local_agents, self.agents_dir, dirs_exist_ok=True)
            
            # Templates synchronisieren
            local_templates = local_bmad_path / "templates"
            if local_templates.exists():
                shutil.copytree(local_templates, self.templates_dir, dirs_exist_ok=True)
            
            # Workflows synchronisieren
            local_workflows = local_bmad_path / "workflows"
            if local_workflows.exists():
                shutil.copytree(local_workflows, self.workflows_dir, dirs_exist_ok=True)
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Hole Registry-Informationen für IDE-Integration"""
        return {
            "global_bmad_home": str(self.global_bmad_home),
            "registry_file": str(self.registry_file),
            "shared_resources": str(self.shared_resources),
            "projects_dir": str(self.projects_dir),
            "active_project": self.get_active_project()
        }
    
    def _load_registry(self) -> Dict[str, Any]:
        """Lade Registry-Datei"""
        if not self.registry_file.exists():
            self._create_default_registry()
        
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_registry(self, registry: Dict[str, Any]):
        """Speichere Registry-Datei"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def _get_timestamp(self) -> str:
        """Hole aktuellen Timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Globale Registry-Instanz
global_registry = BMadGlobalRegistry()