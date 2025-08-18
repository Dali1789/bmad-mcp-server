"""
BMAD Auto-Discovery - Automatische Erkennung und Integration von BMAD-Projekten
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
import time
import logging

logger = logging.getLogger(__name__)


class BMadAutoDiscovery:
    """
    Automatische Erkennung und Integration von BMAD-Projekten
    Überwacht Dateisystem nach neuen .bmad-core Verzeichnissen
    """
    
    def __init__(self, global_registry):
        self.global_registry = global_registry
        self.scan_paths = [
            Path.home(),
            Path.home() / "Documents",
            Path.home() / "Projects",
            Path.home() / "Development",
            Path.home() / "Code",
            Path.home() / "AppData" / "Roaming" / "Claude"
        ]
        self.monitoring_active = False
        self.monitor_thread = None
        self.scan_interval = 300  # 5 minutes
        self.known_projects = set()
        
        # Initialize known projects
        self._load_known_projects()
    
    def _load_known_projects(self):
        """Lade bekannte Projekte aus Registry"""
        try:
            projects = self.global_registry.list_projects()
            self.known_projects = {proj['path'] for proj in projects}
        except Exception as e:
            logger.error(f"Fehler beim Laden bekannter Projekte: {e}")
            self.known_projects = set()
    
    def add_scan_path(self, path: str):
        """Füge neuen Scan-Pfad hinzu"""
        scan_path = Path(path)
        if scan_path.exists() and scan_path not in self.scan_paths:
            self.scan_paths.append(scan_path)
            logger.info(f"Scan-Pfad hinzugefügt: {scan_path}")
    
    def remove_scan_path(self, path: str):
        """Entferne Scan-Pfad"""
        scan_path = Path(path)
        if scan_path in self.scan_paths:
            self.scan_paths.remove(scan_path)
            logger.info(f"Scan-Pfad entfernt: {scan_path}")
    
    def scan_for_projects(self, deep_scan: bool = False) -> List[Dict[str, Any]]:
        """
        Scanne nach BMAD-Projekten
        
        Args:
            deep_scan: Ob tief in Verzeichnisstrukturen gescannt werden soll
            
        Returns:
            Liste neu gefundener Projekte
        """
        new_projects = []
        
        for scan_path in self.scan_paths:
            if not scan_path.exists():
                continue
                
            try:
                found_projects = self._scan_directory(scan_path, deep_scan)
                new_projects.extend(found_projects)
            except Exception as e:
                logger.error(f"Fehler beim Scannen von {scan_path}: {e}")
        
        return new_projects
    
    def _scan_directory(self, directory: Path, deep_scan: bool = False) -> List[Dict[str, Any]]:
        """Scanne einzelnes Verzeichnis nach BMAD-Projekten"""
        found_projects = []
        max_depth = 3 if deep_scan else 2
        
        def scan_recursive(current_path: Path, depth: int = 0):
            if depth > max_depth:
                return
            
            try:
                # Prüfe auf .bmad-core Verzeichnis
                bmad_core = current_path / ".bmad-core"
                if bmad_core.exists() and bmad_core.is_dir():
                    project_path = str(current_path)
                    
                    # Prüfe ob Projekt bereits bekannt
                    if project_path not in self.known_projects:
                        project_info = self._analyze_project(current_path)
                        if project_info:
                            found_projects.append(project_info)
                            self.known_projects.add(project_path)
                
                # Rekursiv in Unterverzeichnisse
                if depth < max_depth:
                    for item in current_path.iterdir():
                        if item.is_dir() and not item.name.startswith('.'):
                            # Skip bekannte große Verzeichnisse
                            skip_dirs = {'node_modules', '__pycache__', '.git', 'venv', 'env', 'build', 'dist'}
                            if item.name not in skip_dirs:
                                scan_recursive(item, depth + 1)
                                
            except (PermissionError, OSError) as e:
                logger.debug(f"Überspringe {current_path}: {e}")
        
        scan_recursive(directory)
        return found_projects
    
    def _analyze_project(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Analysiere gefundenes BMAD-Projekt"""
        try:
            bmad_core = project_path / ".bmad-core"
            
            # Projekt-Konfiguration laden
            project_config = self._load_project_config(bmad_core)
            
            # Projekt-Typ ermitteln
            project_type = self._determine_project_type(project_path, bmad_core)
            
            # Dokumentation finden
            docs_info = self._scan_documentation(project_path)
            
            # Tasks analysieren
            tasks_info = self._scan_tasks(bmad_core)
            
            # Agent-Konfigurationen prüfen
            agents_info = self._scan_agents(bmad_core)
            
            project_info = {
                "path": str(project_path),
                "name": project_config.get("name", project_path.name),
                "type": project_type,
                "template": project_config.get("template", "unknown"),
                "version": project_config.get("version", "1.0.0"),
                "bmad_version": project_config.get("bmad_version", "2.0.0"),
                "discovered_at": datetime.now().isoformat(),
                "status": "discovered",
                "config": project_config,
                "documentation": docs_info,
                "tasks": tasks_info,
                "agents": agents_info,
                "auto_discovered": True
            }
            
            logger.info(f"BMAD-Projekt entdeckt: {project_info['name']} ({project_path})")
            return project_info
            
        except Exception as e:
            logger.error(f"Fehler bei Projekt-Analyse {project_path}: {e}")
            return None
    
    def _load_project_config(self, bmad_core: Path) -> Dict[str, Any]:
        """Lade Projekt-Konfiguration"""
        config_file = bmad_core / "project.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Projekt-Config: {e}")
        
        # Fallback: JSON-Config
        json_config = bmad_core / "config.json"
        if json_config.exists():
            try:
                with open(json_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Fehler beim Laden der JSON-Config: {e}")
        
        return {}
    
    def _determine_project_type(self, project_path: Path, bmad_core: Path) -> str:
        """Ermittle Projekt-Typ basierend auf Struktur"""
        # Prüfe package.json für Web-Projekte
        if (project_path / "package.json").exists():
            try:
                with open(project_path / "package.json", 'r', encoding='utf-8') as f:
                    package_json = json.load(f)
                    
                dependencies = package_json.get("dependencies", {})
                dev_dependencies = package_json.get("devDependencies", {})
                all_deps = {**dependencies, **dev_dependencies}
                
                if "react" in all_deps or "vue" in all_deps or "angular" in all_deps:
                    return "web-app"
                elif "express" in all_deps or "fastify" in all_deps:
                    return "api"
                elif "react-native" in all_deps:
                    return "mobile"
            except Exception:
                pass
        
        # Prüfe Python-Projekte
        if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            # Prüfe auf Data Science
            files = list(project_path.glob("*.ipynb"))
            if files or (project_path / "notebooks").exists():
                return "data-science"
            
            # Prüfe auf API
            if any((project_path / f).exists() for f in ["app.py", "main.py", "api.py"]):
                return "api"
        
        # Prüfe Infrastructure
        if any((project_path / f).exists() for f in ["Dockerfile", "docker-compose.yml", "terraform"]):
            return "infrastructure"
        
        # Default
        return "standard"
    
    def _scan_documentation(self, project_path: Path) -> Dict[str, Any]:
        """Scanne Projekt-Dokumentation"""
        docs_info = {
            "has_readme": False,
            "docs_dir": False,
            "api_docs": False,
            "changelog": False,
            "files": []
        }
        
        # README prüfen
        readme_files = ["README.md", "README.rst", "README.txt", "readme.md"]
        for readme in readme_files:
            if (project_path / readme).exists():
                docs_info["has_readme"] = True
                docs_info["files"].append(readme)
                break
        
        # Docs-Verzeichnis
        docs_dir = project_path / "docs"
        if docs_dir.exists() and docs_dir.is_dir():
            docs_info["docs_dir"] = True
            docs_info["files"].extend([str(f.relative_to(project_path)) for f in docs_dir.rglob("*.md")])
        
        # API-Dokumentation
        api_files = ["api.md", "API.md", "docs/api.md", "docs/API.md"]
        for api_file in api_files:
            if (project_path / api_file).exists():
                docs_info["api_docs"] = True
                break
        
        # Changelog
        changelog_files = ["CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md"]
        for changelog in changelog_files:
            if (project_path / changelog).exists():
                docs_info["changelog"] = True
                docs_info["files"].append(changelog)
                break
        
        return docs_info
    
    def _scan_tasks(self, bmad_core: Path) -> Dict[str, Any]:
        """Scanne Task-Definitionen"""
        tasks_info = {
            "has_tasks": False,
            "active_tasks": 0,
            "completed_tasks": 0,
            "task_files": []
        }
        
        tasks_dir = bmad_core / "tasks"
        if tasks_dir.exists():
            tasks_info["has_tasks"] = True
            
            # Aktive Tasks
            active_file = tasks_dir / "active.json"
            if active_file.exists():
                try:
                    with open(active_file, 'r', encoding='utf-8') as f:
                        active_tasks = json.load(f)
                        tasks_info["active_tasks"] = len(active_tasks.get("tasks", []))
                        tasks_info["task_files"].append("tasks/active.json")
                except Exception:
                    pass
            
            # Abgeschlossene Tasks
            completed_file = tasks_dir / "completed.json"
            if completed_file.exists():
                try:
                    with open(completed_file, 'r', encoding='utf-8') as f:
                        completed_tasks = json.load(f)
                        tasks_info["completed_tasks"] = len(completed_tasks.get("tasks", []))
                        tasks_info["task_files"].append("tasks/completed.json")
                except Exception:
                    pass
        
        return tasks_info
    
    def _scan_agents(self, bmad_core: Path) -> Dict[str, Any]:
        """Scanne Agent-Konfigurationen"""
        agents_info = {
            "configured_agents": [],
            "agent_files": []
        }
        
        agents_dir = bmad_core / "agents"
        if agents_dir.exists():
            agent_names = ["dev", "architect", "analyst", "pm", "qa"]
            
            for agent in agent_names:
                agent_file = agents_dir / f"{agent}.yaml"
                if agent_file.exists():
                    agents_info["configured_agents"].append(agent)
                    agents_info["agent_files"].append(f"agents/{agent}.yaml")
        
        return agents_info
    
    def auto_register_discovered_projects(self, projects: List[Dict[str, Any]]) -> List[str]:
        """Registriere automatisch entdeckte Projekte"""
        registered_projects = []
        
        for project in projects:
            try:
                self.global_registry.register_project(project["path"], project)
                registered_projects.append(project["name"])
                logger.info(f"Projekt auto-registriert: {project['name']}")
            except Exception as e:
                logger.error(f"Fehler bei Auto-Registrierung von {project['name']}: {e}")
        
        return registered_projects
    
    def start_monitoring(self):
        """Starte automatisches Monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Auto-Discovery Monitoring gestartet")
    
    def stop_monitoring(self):
        """Stoppe automatisches Monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Auto-Discovery Monitoring gestoppt")
    
    def _monitoring_loop(self):
        """Monitoring-Schleife"""
        while self.monitoring_active:
            try:
                # Schneller Scan alle 5 Minuten
                new_projects = self.scan_for_projects(deep_scan=False)
                
                if new_projects:
                    registered = self.auto_register_discovered_projects(new_projects)
                    if registered:
                        logger.info(f"Auto-Discovery: {len(registered)} neue Projekte registriert: {', '.join(registered)}")
                
                # Warte bis zum nächsten Scan
                for _ in range(self.scan_interval):
                    if not self.monitoring_active:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Fehler im Auto-Discovery Monitoring: {e}")
                time.sleep(60)  # Bei Fehler 1 Minute warten
    
    def manual_discovery_scan(self, path: Optional[str] = None, deep: bool = True) -> Dict[str, Any]:
        """Manueller Discovery-Scan"""
        if path:
            scan_paths = [Path(path)]
        else:
            scan_paths = self.scan_paths
        
        results = {
            "scanned_paths": [str(p) for p in scan_paths],
            "discovered_projects": [],
            "registered_projects": [],
            "scan_time": datetime.now().isoformat()
        }
        
        # Scanne alle Pfade
        for scan_path in scan_paths:
            if scan_path.exists():
                projects = self._scan_directory(scan_path, deep)
                results["discovered_projects"].extend(projects)
        
        # Auto-registriere gefundene Projekte
        if results["discovered_projects"]:
            registered = self.auto_register_discovered_projects(results["discovered_projects"])
            results["registered_projects"] = registered
        
        return results
    
    def get_discovery_status(self) -> Dict[str, Any]:
        """Hole aktuellen Discovery-Status"""
        return {
            "monitoring_active": self.monitoring_active,
            "scan_paths": [str(p) for p in self.scan_paths],
            "scan_interval": self.scan_interval,
            "known_projects_count": len(self.known_projects),
            "last_scan": datetime.now().isoformat()
        }


# Global Auto-Discovery Instanz
auto_discovery = None

def get_auto_discovery(global_registry):
    """Hole oder erstelle Auto-Discovery Instanz"""
    global auto_discovery
    if auto_discovery is None:
        auto_discovery = BMadAutoDiscovery(global_registry)
    return auto_discovery