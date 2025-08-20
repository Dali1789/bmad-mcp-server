"""
BMAD Project Template System
Erstellt standardisierte Projekt-Strukturen mit Instant Context Support
"""

import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BMadProjectTemplate:
    """Erstellt standardisierte BMAD-Projekte mit einheitlicher Struktur"""
    
    def __init__(self):
        self.templates_path = Path(__file__).parent.parent.parent / "templates" / "project-structure"
        self.bmad_core_template = self.templates_path / ".bmad-core-template"
    
    def create_project(self, project_name: str, project_type: str, target_path: str) -> Dict[str, Any]:
        """Erstellt neues BMAD-Projekt mit Standard-Struktur"""
        try:
            target_dir = Path(target_path) / project_name
            
            # Erstelle Projektverzeichnis
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Erstelle Standard-Struktur
            self._create_standard_structure(target_dir, project_name, project_type)
            
            # Kopiere BMAD Core Template
            self._setup_bmad_core(target_dir, project_name, project_type)
            
            # Erstelle initiale Dateien
            self._create_initial_files(target_dir, project_name, project_type)
            
            # Git initialisieren
            self._init_git(target_dir)
            
            return {
                "success": True,
                "project_path": str(target_dir),
                "message": f"✅ Projekt '{project_name}' erfolgreich erstellt",
                "next_steps": [
                    f"cd \"{target_dir}\"",
                    "bmad instant_context",
                    "*agent analyst"
                ]
            }
            
        except Exception as e:
            logger.error(f"Project creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Fehler beim Erstellen von Projekt '{project_name}'"
            }
    
    def _create_standard_structure(self, target_dir: Path, project_name: str, project_type: str):
        """Erstellt einheitliche Projekt-Struktur"""
        
        # Standard Verzeichnisse
        directories = [
            "docs",
            "src", 
            "tests",
            "scripts",
            "config"
        ]
        
        # Projekt-typ spezifische Verzeichnisse
        if project_type == "web-app":
            directories.extend(["public", "components", "pages"])
        elif project_type == "api":
            directories.extend(["routes", "middleware", "models"])
        elif project_type == "library":
            directories.extend(["lib", "examples"])
        
        for directory in directories:
            (target_dir / directory).mkdir(exist_ok=True)
    
    def _setup_bmad_core(self, target_dir: Path, project_name: str, project_type: str):
        """Kopiert und konfiguriert BMAD Core System"""
        bmad_core_dir = target_dir / ".bmad-core"
        
        # Kopiere Template wenn vorhanden
        if self.bmad_core_template.exists():
            shutil.copytree(self.bmad_core_template, bmad_core_dir, dirs_exist_ok=True)
        else:
            # Erstelle minimale BMAD Core Struktur
            bmad_core_dir.mkdir(exist_ok=True)
        
        # Aktualisiere project-status.yaml mit echten Werten
        status_file = bmad_core_dir / "project-status.yaml"
        self._update_project_status(status_file, project_name, project_type)
        
        # Erstelle development-log.md
        log_file = bmad_core_dir / "development-log.md"
        self._create_development_log(log_file, project_name, project_type)
    
    def _update_project_status(self, status_file: Path, project_name: str, project_type: str):
        """Aktualisiert project-status.yaml mit Projekt-spezifischen Werten"""
        
        status_data = {
            "project": {
                "name": project_name,
                "type": project_type,
                "created": datetime.now().isoformat()
            },
            "current_state": {
                "phase": "planning",
                "active_agent": "analyst", 
                "current_task": "Initial project analysis and requirements gathering",
                "progress": 5
            },
            "development": {
                "current_branch": "main",
                "last_commit": "Initial project setup",
                "current_feature": "project-initialization"
            },
            "next_steps": {
                "immediate": "Complete requirements analysis with *agent analyst",
                "this_week": [
                    "Define product requirements document (PRD)",
                    "Create initial technical architecture",
                    "Set up development environment"
                ],
                "blockers": []
            },
            "context": {
                "tech_stack": [],
                "project_path": str(status_file.parent.parent),
                "has_docs": True,
                "has_src": True,
                "has_tests": True,
                "git_repo": True
            },
            "quality_gates": {
                "prd_approved": False,
                "architecture_approved": False,
                "code_review_passed": False,
                "tests_passing": False
            },
            "workflows": {
                "current": "",
                "available": [
                    "bmad-web-app-development",
                    "bmad-api-development",
                    "bmad-library-development"
                ]
            },
            "recommended_actions": [
                "Use '*agent analyst' to start requirements analysis",
                "Create PRD with '*task create-prd'",
                "Define architecture with '*agent architect'"
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            yaml.dump(status_data, f, default_flow_style=False, allow_unicode=True)
    
    def _create_development_log(self, log_file: Path, project_name: str, project_type: str):
        """Erstellt initiales Development Log"""
        
        log_content = f"""# Development Log - {project_name}

*Kontinuierliches Log aller wichtigen Entwicklungsschritte*

## {datetime.now().strftime('%Y-%m-%d')} - Project Setup
**Agent:** orchestrator  
**Task:** Initial project creation  
**Status:** Completed  

### Actions Taken
- [x] Created standardized project structure
- [x] Initialized BMAD Core system  
- [x] Set up development environment template
- [x] Configured project-status.yaml for instant context loading
- [ ] Requirements gathering (next step)

### Next Steps
- Switch to analyst agent for requirements gathering: `*agent analyst`
- Create Product Requirements Document (PRD): `*task create-prd`
- Define core user stories and acceptance criteria

### Notes
Project created with BMAD template system v2.0. Features instant context loading for immediate productivity.
Type: {project_type}

**Quick Start Commands:**
- `bmad instant_context` - Get current status and recommendations
- `*agent analyst` - Start requirements analysis phase
- `*workflow-guidance` - Explore available workflows

---

*This log is automatically parsed by the instant context system for progress tracking*
"""
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
    
    def _create_initial_files(self, target_dir: Path, project_name: str, project_type: str):
        """Erstellt initiale Projekt-Dateien"""
        
        # README.md
        readme_content = f"""# {project_name}

*Generated with BMAD Method - Instant Context Ready*

## Quick Start

1. **Get Project Status:** `bmad instant_context`
2. **Start Development:** `*agent analyst`  
3. **Explore Workflows:** `*workflow-guidance`

## BMAD Development Phases

1. **Planning** - Requirements and analysis (`*agent analyst`)
2. **Architecture** - System design (`*agent architect`) 
3. **Development** - Implementation (`*agent dev`)
4. **Testing** - Quality assurance (`*agent qa`)
5. **Deployment** - Release management (`*agent pm`)

## Project Structure

- `docs/` - Documentation and requirements
- `src/` - Source code
- `tests/` - Test files
- `.bmad-core/` - BMAD configuration and status

## Current Status

Phase: Planning (5%)
Next Action: `*agent analyst` for requirements gathering
"""
        
        with open(target_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # .gitignore
        gitignore_content = \"\"\"node_modules/
.env
.env.local
dist/
build/
.DS_Store
*.log
.bmad-session-cache.json
\"\"\"
        
        with open(target_dir / ".gitignore", 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
    
    def _init_git(self, target_dir: Path):
        """Initialisiert Git Repository"""
        try:
            os.system(f'cd "{target_dir}" && git init')
            os.system(f'cd "{target_dir}" && git add .')
            os.system(f'cd "{target_dir}" && git commit -m "Initial project setup with BMAD template"')
        except Exception as e:
            logger.warning(f"Git initialization failed: {e}")

# Global instance
_project_template = None

def get_project_template() -> BMadProjectTemplate:
    """Singleton für Project Template"""
    global _project_template
    if _project_template is None:
        _project_template = BMadProjectTemplate()
    return _project_template