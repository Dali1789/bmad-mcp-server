"""
BMAD Core System Loader
Lädt und verwaltet die originale BMAD Core Struktur für MCP Server
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class BMadCoreStructure:
    """Repräsentiert die originale BMAD Core Struktur"""
    agent_teams: Dict[str, Any]
    agents: Dict[str, str]
    checklists: Dict[str, str] 
    data: Dict[str, str]
    tasks: Dict[str, str]
    templates: Dict[str, str]
    utils: Dict[str, str]
    workflows: Dict[str, Any]
    user_guide: str


class BMadCoreLoader:
    """
    Lädt das originale BMAD Core System in MCP-kompatible Struktur
    Stellt sicher, dass alle originalen BMAD Funktionen verfügbar sind
    """
    
    def __init__(self, core_path: Optional[str] = None):
        self.core_path = core_path or self._find_bmad_core_path()
        self.core_structure = None
        self._load_core_structure()
    
    def _find_bmad_core_path(self) -> str:
        """Findet automatisch BMAD Core Pfad"""
        # Production/Railway Environment - use bundled templates
        if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT'):
            templates_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "templates", "bmad-core")
            if os.path.exists(templates_path):
                return templates_path
                
        # Local Development Paths
        possible_paths = [
            "C:\\Users\\Faber\\AppData\\Roaming\\Claude\\gutachter-app\\.bmad-core",
            "C:\\Users\\Faber\\AppData\\Roaming\\Claude\\.bmad-core",
            "C:\\Users\\Faber\\AppData\\Roaming\\Claude\\Projekte\\_project-template\\.bmad-core",
            # Unix-like fallback paths
            "/app/templates/bmad-core",
            "./templates/bmad-core",
            "../templates/bmad-core"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # Production fallback - create minimal structure
        if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT'):
            return self._create_minimal_core_structure()
                
        raise FileNotFoundError("BMAD Core System nicht gefunden")
    
    def _create_minimal_core_structure(self) -> str:
        """Erstellt minimale BMAD Core Struktur für Production Environment"""
        import tempfile
        
        # Temporäres Verzeichnis in /tmp erstellen
        temp_dir = os.path.join(tempfile.gettempdir(), "bmad-core-minimal")
        
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
            
            # Minimale Agents erstellen
            agents_dir = os.path.join(temp_dir, "agents")
            os.makedirs(agents_dir, exist_ok=True)
            
            minimal_agents = {
                "analyst.md": "# BMAD Analyst Agent\nAnalysiert und bewertet Projektanforderungen.",
                "architect.md": "# BMAD Architect Agent\nEntwirft technische Architektur und Systemdesign.",
                "dev.md": "# BMAD Developer Agent\nImplementiert und entwickelt Software-Lösungen.",
                "pm.md": "# BMAD Project Manager Agent\nVerwaltet Projekte und koordiniert Teams.",
                "qa.md": "# BMAD Quality Assurance Agent\nPrüft Qualität und führt Tests durch.",
                "po.md": "# BMAD Product Owner Agent\nDefiniert Produktvision und Anforderungen."
            }
            
            for filename, content in minimal_agents.items():
                with open(os.path.join(agents_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Minimale Struktur für andere Verzeichnisse
            for dirname in ["checklists", "tasks", "templates", "utils", "workflows"]:
                dir_path = os.path.join(temp_dir, dirname)
                os.makedirs(dir_path, exist_ok=True)
                # Leere README für Struktur
                with open(os.path.join(dir_path, "README.md"), 'w', encoding='utf-8') as f:
                    f.write(f"# BMAD {dirname.title()}\nMinimal structure for production deployment.")
            
            # Data Verzeichnis mit BMAD Knowledge Base
            data_dir = os.path.join(temp_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            with open(os.path.join(data_dir, "bmad-kb.md"), 'w', encoding='utf-8') as f:
                f.write("# BMAD Knowledge Base\nMinimal BMAD methodology knowledge base for production deployment.\n\n## Core Principles\n- Agent-based development methodology\n- Quality-first approach\n- Iterative improvement\n- Automated workflow management")
            
            # User Guide erstellen
            with open(os.path.join(temp_dir, "user-guide.md"), 'w', encoding='utf-8') as f:
                f.write("# BMAD User Guide\nMinimal production version of BMAD methodology guide.")
        
        return temp_dir
    
    def _load_core_structure(self):
        """Lädt die komplette BMAD Core Struktur"""
        if not os.path.exists(self.core_path):
            raise FileNotFoundError(f"BMAD Core nicht gefunden: {self.core_path}")
        
        # Agent Teams laden
        agent_teams = self._load_agent_teams()
        
        # Einzelne Agents laden  
        agents = self._load_directory_files(os.path.join(self.core_path, "agents"), ".md")
        
        # Checklisten laden
        checklists = self._load_directory_files(os.path.join(self.core_path, "checklists"), ".md")
        
        # Data/Knowledge Base laden
        data = self._load_directory_files(os.path.join(self.core_path, "data"), ".md")
        
        # Tasks laden
        tasks = self._load_directory_files(os.path.join(self.core_path, "tasks"), ".md")
        
        # Templates laden
        templates = self._load_directory_files(os.path.join(self.core_path, "templates"))
        
        # Utils laden
        utils = self._load_directory_files(os.path.join(self.core_path, "utils"))
        
        # Workflows laden
        workflows = self._load_workflows()
        
        # User Guide laden
        user_guide = self._load_user_guide()
        
        self.core_structure = BMadCoreStructure(
            agent_teams=agent_teams,
            agents=agents,
            checklists=checklists,
            data=data,
            tasks=tasks,
            templates=templates,
            utils=utils,
            workflows=workflows,
            user_guide=user_guide
        )
    
    def _load_agent_teams(self) -> Dict[str, Any]:
        """Lädt Agent Team Konfigurationen"""
        teams_path = os.path.join(self.core_path, "agent-teams")
        teams = {}
        
        if os.path.exists(teams_path):
            for file in os.listdir(teams_path):
                if file.endswith('.yaml'):
                    team_name = file[:-5]  # Remove .yaml
                    with open(os.path.join(teams_path, file), 'r', encoding='utf-8') as f:
                        teams[team_name] = yaml.safe_load(f)
        
        return teams
    
    def _load_workflows(self) -> Dict[str, Any]:
        """Lädt Workflow-Definitionen"""
        workflows_path = os.path.join(self.core_path, "workflows")
        workflows = {}
        
        if os.path.exists(workflows_path):
            for file in os.listdir(workflows_path):
                if file.endswith('.yaml'):
                    workflow_name = file[:-5]
                    with open(os.path.join(workflows_path, file), 'r', encoding='utf-8') as f:
                        workflows[workflow_name] = yaml.safe_load(f)
        
        return workflows
    
    def _load_directory_files(self, directory: str, extension: str = None) -> Dict[str, str]:
        """Lädt alle Dateien aus einem Verzeichnis"""
        files = {}
        
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if extension and not file.endswith(extension):
                    continue
                    
                file_key = file
                if extension:
                    file_key = file[:-len(extension)]
                
                try:
                    with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
                        files[file_key] = f.read()
                except Exception as e:
                    print(f"Warnung: Konnte {file} nicht laden: {e}")
        
        return files
    
    def _load_user_guide(self) -> str:
        """Lädt das User Guide"""
        guide_path = os.path.join(self.core_path, "user-guide.md")
        
        if os.path.exists(guide_path):
            with open(guide_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Fallback: Suche in bmad-core Unterverzeichnis
        fallback_path = os.path.join(self.core_path, "bmad-core", "user-guide.md")
        if os.path.exists(fallback_path):
            with open(fallback_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return ""
    
    # Public Interface Methods
    
    def get_agent_definition(self, agent_name: str) -> Optional[str]:
        """Holt Agent-Definition"""
        return self.core_structure.agents.get(agent_name)
    
    def get_all_agents(self) -> Dict[str, str]:
        """Holt alle Agent-Definitionen"""
        return self.core_structure.agents
    
    def get_agent_team(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Holt Team-Konfiguration"""
        return self.core_structure.agent_teams.get(team_name)
    
    def get_all_teams(self) -> Dict[str, Any]:
        """Holt alle Teams"""
        return self.core_structure.agent_teams
    
    def get_checklist(self, checklist_name: str) -> Optional[str]:
        """Holt Checklist-Inhalt"""
        return self.core_structure.checklists.get(checklist_name)
    
    def get_all_checklists(self) -> Dict[str, str]:
        """Holt alle Checklisten"""
        return self.core_structure.checklists
    
    def get_task_definition(self, task_name: str) -> Optional[str]:
        """Holt Task-Definition"""
        return self.core_structure.tasks.get(task_name)
    
    def get_all_tasks(self) -> Dict[str, str]:
        """Holt alle Tasks"""
        return self.core_structure.tasks
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Holt Template-Inhalt"""
        return self.core_structure.templates.get(template_name)
    
    def get_all_templates(self) -> Dict[str, str]:
        """Holt alle Templates"""
        return self.core_structure.templates
    
    def get_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Holt Workflow-Definition"""
        return self.core_structure.workflows.get(workflow_name)
    
    def get_all_workflows(self) -> Dict[str, Any]:
        """Holt alle Workflows"""
        return self.core_structure.workflows
    
    def get_data_file(self, data_name: str) -> Optional[str]:
        """Holt Data/Knowledge Base Datei"""
        return self.core_structure.data.get(data_name)
    
    def get_knowledge_base(self) -> Optional[str]:
        """Holt BMAD Knowledge Base"""
        return self.core_structure.data.get("bmad-kb")
    
    def get_user_guide(self) -> str:
        """Holt User Guide"""
        return self.core_structure.user_guide
    
    def get_system_status(self) -> Dict[str, Any]:
        """Generiert System-Status Report"""
        return {
            "core_path": self.core_path,
            "agents_loaded": len(self.core_structure.agents),
            "teams_loaded": len(self.core_structure.agent_teams),
            "checklists_loaded": len(self.core_structure.checklists),
            "tasks_loaded": len(self.core_structure.tasks),
            "templates_loaded": len(self.core_structure.templates),
            "workflows_loaded": len(self.core_structure.workflows),
            "data_files_loaded": len(self.core_structure.data),
            "user_guide_available": bool(self.core_structure.user_guide),
            "loaded_agents": list(self.core_structure.agents.keys()),
            "loaded_teams": list(self.core_structure.agent_teams.keys()),
            "loaded_workflows": list(self.core_structure.workflows.keys())
        }
    
    def validate_core_structure(self) -> Dict[str, Any]:
        """Validiert die BMAD Core Struktur"""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "structure_check": {}
        }
        
        # Überprüfe kritische Komponenten
        required_agents = ["analyst", "architect", "dev", "pm", "qa", "po"]
        missing_agents = [agent for agent in required_agents 
                         if agent not in self.core_structure.agents]
        
        if missing_agents:
            validation["errors"].append(f"Fehlende Agents: {missing_agents}")
            validation["valid"] = False
        
        # Überprüfe erforderliche Templates
        if "prd-tmpl" not in self.core_structure.templates:
            validation["warnings"].append("PRD Template nicht gefunden")
        
        # Überprüfe Knowledge Base
        if not self.core_structure.data.get("bmad-kb"):
            validation["errors"].append("BMAD Knowledge Base fehlt")
            validation["valid"] = False
        
        # Überprüfe User Guide
        if not self.core_structure.user_guide:
            validation["warnings"].append("User Guide nicht gefunden")
        
        return validation


# Globale Instanz für MCP Server
_bmad_core_loader = None

def get_bmad_core_loader() -> BMadCoreLoader:
    """Singleton Pattern für BMAD Core Loader"""
    global _bmad_core_loader
    if _bmad_core_loader is None:
        _bmad_core_loader = BMadCoreLoader()
    return _bmad_core_loader