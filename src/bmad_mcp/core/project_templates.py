"""
BMAD Project Template Generator - Standardisierte Projektstrukturen
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import shutil


class BMadProjectTemplates:
    """
    BMAD Template Generator für standardisierte Projektstrukturen
    Erstellt konsistente, vordefinierte Verzeichnisstrukturen
    """
    
    def __init__(self):
        self.templates_dir = Path.home() / ".bmad-global" / "shared-resources" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_default_templates()
    
    def _ensure_default_templates(self):
        """Erstelle Standard-Templates falls nicht vorhanden"""
        default_templates = {
            "standard": self._get_standard_template(),
            "web-app": self._get_webapp_template(),
            "api": self._get_api_template(),
            "mobile": self._get_mobile_template(),
            "data-science": self._get_datascience_template(),
            "infrastructure": self._get_infrastructure_template()
        }
        
        for template_name, template_config in default_templates.items():
            template_file = self.templates_dir / f"{template_name}.yaml"
            if not template_file.exists():
                with open(template_file, 'w', encoding='utf-8') as f:
                    yaml.dump(template_config, f, default_flow_style=False, allow_unicode=True)
    
    def create_project(self, project_path: str, template_name: str = "standard", 
                      project_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Erstelle neues BMAD-Projekt mit standardisierter Struktur
        
        Args:
            project_path: Pfad zum neuen Projekt
            template_name: Name des zu verwendenden Templates
            project_config: Zusätzliche Projekt-Konfiguration
            
        Returns:
            Dict mit Erstellungs-Informationen
        """
        project_path = Path(project_path)
        
        if project_path.exists():
            raise ValueError(f"Projekt-Pfad existiert bereits: {project_path}")
        
        # Template laden
        template_config = self._load_template(template_name)
        if not template_config:
            raise ValueError(f"Template nicht gefunden: {template_name}")
        
        # Projekt-Verzeichnis erstellen
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Verzeichnisstruktur erstellen
        self._create_directory_structure(project_path, template_config["structure"])
        
        # Konfigurations-Dateien erstellen
        self._create_config_files(project_path, template_config, project_config)
        
        # Template-Dateien kopieren
        self._create_template_files(project_path, template_config)
        
        # Projekt in Registry registrieren
        self._register_project(project_path, template_name, project_config)
        
        return {
            "project_path": str(project_path),
            "template": template_name,
            "created_at": datetime.now().isoformat(),
            "structure": template_config["structure"],
            "status": "created"
        }
    
    def _load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Lade Template-Konfiguration"""
        template_file = self.templates_dir / f"{template_name}.yaml"
        if not template_file.exists():
            return None
        
        with open(template_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_directory_structure(self, project_path: Path, structure: Dict[str, Any]):
        """Erstelle Verzeichnisstruktur basierend auf Template"""
        for item_name, item_config in structure.items():
            item_path = project_path / item_name
            
            if isinstance(item_config, dict):
                # Verzeichnis mit Unterstruktur
                item_path.mkdir(parents=True, exist_ok=True)
                if "children" in item_config:
                    self._create_directory_structure(item_path, item_config["children"])
            else:
                # Einfaches Verzeichnis
                item_path.mkdir(parents=True, exist_ok=True)
    
    def _create_config_files(self, project_path: Path, template_config: Dict[str, Any], 
                           user_config: Optional[Dict[str, Any]]):
        """Erstelle Konfigurations-Dateien"""
        bmad_core = project_path / ".bmad-core"
        
        # Haupt-Projekt-Konfiguration
        project_config = {
            "name": project_path.name,
            "version": "1.0.0",
            "type": template_config.get("type", "standard"),
            "template": template_config.get("name", "standard"),
            "created_at": datetime.now().isoformat(),
            "bmad_version": "2.0.0",
            "description": template_config.get("description", f"BMAD-Projekt: {project_path.name}"),
            "team": {
                "lead": "BMAD System",
                "agents": ["dev", "architect", "analyst", "pm", "qa"]
            },
            "integrations": {
                "notion": {"enabled": False},
                "slack": {"enabled": False},
                "openrouter": {"enabled": True}
            },
            "quality_gates": {
                "linting": True,
                "testing": True,
                "security": True,
                "performance": True
            }
        }
        
        # User-Config mergen
        if user_config:
            project_config.update(user_config)
        
        # project.yaml schreiben
        with open(bmad_core / "project.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(project_config, f, default_flow_style=False, allow_unicode=True)
        
        # Agent-Konfigurationen erstellen
        self._create_agent_configs(bmad_core / "agents", template_config)
        
        # Workflow-Konfigurationen erstellen
        self._create_workflow_configs(bmad_core / "workflows", template_config)
        
        # Integration-Konfigurationen erstellen
        self._create_integration_configs(bmad_core / "integrations", template_config)
        
        # Quality Gates erstellen
        self._create_quality_configs(bmad_core / "quality-gates", template_config)
    
    def _create_agent_configs(self, agents_path: Path, template_config: Dict[str, Any]):
        """Erstelle Agent-spezifische Konfigurationen"""
        agents = ["dev", "architect", "analyst", "pm", "qa"]
        
        for agent in agents:
            agent_config = {
                "name": f"bmad-{agent}",
                "version": "2.0.0",
                "enabled": True,
                "model_preferences": template_config.get("agents", {}).get(agent, {
                    "primary": "claude-3-sonnet",
                    "fallback": "claude-3-haiku",
                    "temperature": 0.1
                }),
                "workflows": template_config.get("workflows", {}).get(agent, []),
                "permissions": {
                    "file_access": True,
                    "api_access": True,
                    "git_access": True
                },
                "quality_gates": {
                    "code_review": agent == "qa",
                    "testing": agent in ["dev", "qa"],
                    "documentation": agent in ["architect", "pm"]
                }
            }
            
            with open(agents_path / f"{agent}.yaml", 'w', encoding='utf-8') as f:
                yaml.dump(agent_config, f, default_flow_style=False, allow_unicode=True)
    
    def _create_workflow_configs(self, workflows_path: Path, template_config: Dict[str, Any]):
        """Erstelle Workflow-Konfigurationen"""
        workflows = {
            "ci-cd.yaml": {
                "name": "CI/CD Pipeline",
                "triggers": ["push", "pull_request"],
                "stages": ["lint", "test", "build", "deploy"],
                "quality_gates": ["security_scan", "performance_test"],
                "notifications": ["slack", "email"]
            },
            "review.yaml": {
                "name": "Code Review Workflow",
                "automatic_assignment": True,
                "required_reviewers": 1,
                "agents": ["bmad-qa", "bmad-architect"],
                "checklist": [
                    "Code quality check",
                    "Security review",
                    "Performance impact",
                    "Documentation update"
                ]
            },
            "deployment.yaml": {
                "name": "Deployment Workflow",
                "environments": ["development", "staging", "production"],
                "approval_required": ["staging", "production"],
                "rollback_strategy": "immediate",
                "monitoring": ["health_check", "performance_metrics"]
            },
            "maintenance.yaml": {
                "name": "Maintenance Workflow",
                "schedule": "weekly",
                "tasks": [
                    "dependency_updates",
                    "security_patches",
                    "performance_optimization",
                    "documentation_review"
                ],
                "responsible_agent": "bmad-pm"
            }
        }
        
        for workflow_file, workflow_config in workflows.items():
            with open(workflows_path / workflow_file, 'w', encoding='utf-8') as f:
                yaml.dump(workflow_config, f, default_flow_style=False, allow_unicode=True)
    
    def _create_integration_configs(self, integrations_path: Path, template_config: Dict[str, Any]):
        """Erstelle Integration-Konfigurationen"""
        integrations = {
            "notion.yaml": {
                "enabled": False,
                "databases": {
                    "tasks": {"id": "", "sync": True},
                    "projects": {"id": "", "sync": True},
                    "resources": {"id": "", "sync": False}
                },
                "sync_interval": "15min",
                "conflict_resolution": "local_wins"
            },
            "slack.yaml": {
                "enabled": False,
                "channels": {
                    "general": "#bmad-general",
                    "notifications": "#bmad-notifications",
                    "alerts": "#bmad-alerts"
                },
                "bot_token": "",
                "notification_types": ["task_completion", "errors", "deployments"]
            },
            "git.yaml": {
                "provider": "github",
                "repository": "",
                "branch_strategy": "gitflow",
                "commit_conventions": "conventional_commits",
                "hooks": {
                    "pre_commit": ["lint", "test"],
                    "pre_push": ["security_scan"]
                }
            },
            "openrouter.yaml": {
                "enabled": True,
                "default_models": {
                    "dev": "anthropic/claude-3-sonnet",
                    "architect": "anthropic/claude-3-opus",
                    "analyst": "perplexity/sonar-large",
                    "pm": "google/gemini-pro",
                    "qa": "anthropic/claude-3-sonnet"
                },
                "cost_optimization": True,
                "fallback_enabled": True
            }
        }
        
        for integration_file, integration_config in integrations.items():
            with open(integrations_path / integration_file, 'w', encoding='utf-8') as f:
                yaml.dump(integration_config, f, default_flow_style=False, allow_unicode=True)
    
    def _create_quality_configs(self, quality_path: Path, template_config: Dict[str, Any]):
        """Erstelle Quality Gate Konfigurationen"""
        quality_gates = {
            "linting.yaml": {
                "enabled": True,
                "tools": ["eslint", "prettier", "flake8"],
                "rules": "strict",
                "auto_fix": True,
                "pre_commit": True
            },
            "testing.yaml": {
                "enabled": True,
                "frameworks": ["pytest", "jest"],
                "coverage_threshold": 80,
                "integration_tests": True,
                "performance_tests": False
            },
            "security.yaml": {
                "enabled": True,
                "tools": ["bandit", "safety", "semgrep"],
                "vulnerability_scan": True,
                "dependency_check": True,
                "secrets_detection": True
            },
            "performance.yaml": {
                "enabled": True,
                "metrics": ["response_time", "memory_usage", "cpu_usage"],
                "thresholds": {
                    "response_time": "200ms",
                    "memory_usage": "512MB",
                    "cpu_usage": "70%"
                },
                "monitoring": "continuous"
            }
        }
        
        for quality_file, quality_config in quality_gates.items():
            with open(quality_path / quality_file, 'w', encoding='utf-8') as f:
                yaml.dump(quality_config, f, default_flow_style=False, allow_unicode=True)
    
    def _create_template_files(self, project_path: Path, template_config: Dict[str, Any]):
        """Erstelle Template-spezifische Dateien"""
        # README.md erstellen
        readme_content = f"""# {project_path.name}

{template_config.get('description', 'BMAD-Projekt mit standardisierter Struktur')}

## 🚀 Schnellstart

```bash
# Projekt-Setup
cd {project_path.name}

# BMAD-System initialisieren
bmad init

# Erste Task erstellen
bmad create-task "Setup abschließen"
```

## 📁 Projektstruktur

```
{project_path.name}/
├── .bmad-core/          # BMAD Konfiguration
├── docs/               # Dokumentation
├── src/                # Source Code
├── tests/              # Tests
├── config/             # Konfiguration
└── scripts/            # Utility Scripts
```

## 🤖 BMAD Agents

- **bmad-dev**: Entwicklung und Code-Implementation
- **bmad-architect**: System-Design und Architektur
- **bmad-analyst**: Requirements und Business-Analyse
- **bmad-pm**: Projekt-Management und Koordination
- **bmad-qa**: Quality Assurance und Testing

## 📋 Verfügbare Tasks

```bash
# Tasks anzeigen
bmad list-tasks

# Neue Task erstellen
bmad create-task "Task Name" --agent dev --hours 4

# Task starten
bmad start-task <task-id>
```

## 🔧 Konfiguration

Die Projekt-Konfiguration befindet sich in `.bmad-core/project.yaml`.

## 📚 Dokumentation

Siehe `docs/` Verzeichnis für detaillierte Dokumentation.

---
*Generiert mit BMAD Template System v2.0*
"""
        
        with open(project_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # .gitignore erstellen
        gitignore_content = """# BMAD
.bmad-core/memory/temp/
.bmad-core/cache/
*.bmad-tmp

# Dependencies
node_modules/
__pycache__/
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Build outputs
dist/
build/
*.min.js
*.min.css
"""
        
        with open(project_path / ".gitignore", 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        # Leere Starter-Dateien erstellen
        starter_files = {
            "docs/setup/installation.md": "# Installation\n\nTODO: Installationsanweisungen",
            "docs/api/README.md": "# API Dokumentation\n\nTODO: API-Dokumentation",
            "scripts/setup.sh": "#!/bin/bash\n# Setup-Script\necho 'Setting up project...'",
            "config/development.yaml": "# Development Konfiguration\ndebug: true",
            "data/.gitkeep": "",
            "temp/.gitkeep": "",
            "assets/.gitkeep": ""
        }
        
        for file_path, content in starter_files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _register_project(self, project_path: Path, template_name: str, 
                         project_config: Optional[Dict[str, Any]]):
        """Registriere Projekt in globaler Registry"""
        from .global_registry import global_registry
        
        registry_entry = {
            "name": project_path.name,
            "path": str(project_path),
            "template": template_name,
            "type": template_name,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "bmad_version": "2.0.0",
            "status": "active"
        }
        
        if project_config:
            registry_entry.update(project_config)
        
        global_registry.register_project(str(project_path), registry_entry)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """Liste alle verfügbaren Templates"""
        templates = []
        
        for template_file in self.templates_dir.glob("*.yaml"):
            template_name = template_file.stem
            template_config = self._load_template(template_name)
            
            if template_config:
                templates.append({
                    "name": template_name,
                    "description": template_config.get("description", ""),
                    "type": template_config.get("type", "standard"),
                    "features": template_config.get("features", [])
                })
        
        return templates
    
    def _get_standard_template(self) -> Dict[str, Any]:
        """Standard-Template Konfiguration"""
        return {
            "name": "standard",
            "description": "Standard BMAD-Projekt mit vollständiger Struktur",
            "type": "standard",
            "features": [
                "Vollständige .bmad-core Konfiguration",
                "Alle 5 BMAD Agents",
                "CI/CD Pipeline",
                "Quality Gates",
                "Dokumentations-Framework"
            ],
            "structure": {
                ".bmad-core": {
                    "children": {
                        "tasks": {},
                        "agents": {},
                        "workflows": {},
                        "integrations": {},
                        "quality-gates": {},
                        "memory": {}
                    }
                },
                "docs": {
                    "children": {
                        "setup": {},
                        "api": {},
                        "architecture": {},
                        "user-guides": {},
                        "troubleshooting": {},
                        "changelog": {}
                    }
                },
                "src": {},
                "tests": {},
                "config": {},
                "scripts": {},
                "assets": {},
                "data": {},
                "temp": {}
            }
        }
    
    def _get_webapp_template(self) -> Dict[str, Any]:
        """Web-App Template"""
        template = self._get_standard_template()
        template.update({
            "name": "web-app",
            "description": "Web-Anwendung mit Frontend/Backend Struktur",
            "type": "web-app",
            "features": template["features"] + [
                "Frontend/Backend Separation",
                "API-First Design",
                "Responsive UI Framework",
                "Database Integration"
            ]
        })
        
        template["structure"]["src"]["children"] = {
            "frontend": {
                "children": {
                    "components": {},
                    "pages": {},
                    "styles": {},
                    "utils": {}
                }
            },
            "backend": {
                "children": {
                    "api": {},
                    "models": {},
                    "services": {},
                    "middleware": {}
                }
            },
            "shared": {}
        }
        
        return template
    
    def _get_api_template(self) -> Dict[str, Any]:
        """API-Template"""
        template = self._get_standard_template()
        template.update({
            "name": "api",
            "description": "REST/GraphQL API mit OpenAPI-Dokumentation",
            "type": "api",
            "features": template["features"] + [
                "OpenAPI/Swagger Integration",
                "Authentication & Authorization",
                "Rate Limiting",
                "API Versioning"
            ]
        })
        
        return template
    
    def _get_mobile_template(self) -> Dict[str, Any]:
        """Mobile-App Template"""
        template = self._get_standard_template()
        template.update({
            "name": "mobile",
            "description": "Mobile App (React Native/Flutter)",
            "type": "mobile",
            "features": template["features"] + [
                "Cross-Platform Development",
                "Native Integration",
                "App Store Deployment",
                "Push Notifications"
            ]
        })
        
        return template
    
    def _get_datascience_template(self) -> Dict[str, Any]:
        """Data Science Template"""
        template = self._get_standard_template()
        template.update({
            "name": "data-science",
            "description": "Data Science/ML Projekt mit Jupyter Integration",
            "type": "data-science",
            "features": template["features"] + [
                "Jupyter Notebooks",
                "ML Pipeline",
                "Data Visualization",
                "Model Deployment"
            ]
        })
        
        template["structure"]["notebooks"] = {}
        template["structure"]["models"] = {}
        template["structure"]["datasets"] = {}
        
        return template
    
    def _get_infrastructure_template(self) -> Dict[str, Any]:
        """Infrastructure Template"""
        template = self._get_standard_template()
        template.update({
            "name": "infrastructure",
            "description": "Infrastructure as Code (Terraform/Docker)",
            "type": "infrastructure",
            "features": template["features"] + [
                "Infrastructure as Code",
                "Container Orchestration",
                "Monitoring & Logging",
                "Security Hardening"
            ]
        })
        
        template["structure"]["terraform"] = {}
        template["structure"]["kubernetes"] = {}
        template["structure"]["monitoring"] = {}
        
        return template


# Global Template-Manager Instanz
template_manager = BMadProjectTemplates()