#!/usr/bin/env python3
"""
BMAD Project Migration Script
Migriert bestehende Projekte auf die neue BMAD-Standardstruktur
"""

import os
import sys
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Füge src-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bmad_mcp.core.project_templates import template_manager
from bmad_mcp.core.global_registry import global_registry


class BMadProjectMigrator:
    """Migration bestehender Projekte auf BMAD v2.0 Standard"""
    
    def __init__(self):
        self.backup_dir = Path.home() / ".bmad-global" / "migration-backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Bekannte Projekte aus vorheriger Analyse
        self.existing_projects = {
            "Claude Global": Path.home() / "AppData" / "Roaming" / "Claude",
            "BMAD MCP Infrastructure": Path.home() / "AppData" / "Roaming" / "Claude" / "bmad-mcp-infrastructure", 
            "Gutachter App": Path.home() / "AppData" / "Roaming" / "Claude" / "gutachter-app"
        }
    
    def create_backup(self, project_path: Path, project_name: str) -> Path:
        """Erstelle Backup vor Migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{project_name}_{timestamp}"
        
        print(f"Erstelle Backup: {backup_path}")
        
        # Kopiere nur wichtige Dateien (nicht node_modules, etc.)
        def ignore_patterns(dir_path, contents):
            ignore = {
                'node_modules', '__pycache__', '.git', '.vscode', '.idea',
                'venv', 'env', 'dist', 'build', '.cache', 'logs',
                'temp', 'tmp', '.DS_Store', 'Thumbs.db'
            }
            return [item for item in contents if item in ignore]
        
        shutil.copytree(project_path, backup_path, ignore=ignore_patterns)
        return backup_path
    
    def migrate_claude_global_project(self) -> Dict[str, Any]:
        """Migriere Claude Global Projekt"""
        project_path = self.existing_projects["Claude Global"]
        
        print(f"Migriere Claude Global Projekt: {project_path}")
        
        # Backup erstellen
        backup_path = self.create_backup(project_path, "claude-global")
        
        # .bmad-core erstellen falls nicht vorhanden
        bmad_core = project_path / ".bmad-core"
        if not bmad_core.exists():
            bmad_core.mkdir(parents=True, exist_ok=True)
        
        # Standard-Struktur erstellen
        template_config = template_manager._get_standard_template()
        structure = template_config["structure"][".bmad-core"]
        template_manager._create_directory_structure(bmad_core, structure)
        
        # Projekt-Konfiguration
        project_config = {
            "name": "BMAD Global System",
            "version": "2.0.0",
            "type": "global_configuration",
            "template": "standard",
            "description": "Zentrales BMAD-System mit globaler Konfiguration für alle Projekte",
            "migrated_from": "legacy_bmad_system",
            "migrated_at": datetime.now().isoformat(),
            "backup_location": str(backup_path),
            "features": [
                "Globale Agent-Konfigurationen",
                "OpenRouter Multi-Model Integration", 
                "Auto-Linting System",
                "Real-time Dashboard",
                "Cross-Project Context"
            ],
            "integrations": {
                "notion": {"enabled": True},
                "slack": {"enabled": True},
                "openrouter": {"enabled": True}
            },
            "agents": {
                "dev": {"enabled": True, "config_file": "bmad-dev-settings.json"},
                "analyst": {"enabled": True, "config_file": "bmad-analyst-settings.json"},
                "architect": {"enabled": True, "config_file": "bmad-architect-settings.json"},
                "pm": {"enabled": True, "config_file": "bmad-pm-settings.json"},
                "qa": {"enabled": True, "config_file": "bmad-qa.bat"}
            }
        }
        
        # Konfiguration schreiben
        with open(bmad_core / "project.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(project_config, f, default_flow_style=False, allow_unicode=True)
        
        # Bestehende bmad-global-config.json verlinken
        if (project_path / "bmad-global-config.json").exists():
            legacy_config_link = bmad_core / "memory" / "legacy-global-config.json"
            legacy_config_link.parent.mkdir(parents=True, exist_ok=True)
            
            # Relative Verlinkung erstellen
            with open(legacy_config_link, 'w', encoding='utf-8') as f:
                json.dump({
                    "note": "Legacy-Konfiguration für Rückwärtskompatibilität",
                    "legacy_config_path": "../bmad-global-config.json",
                    "migration_note": "Diese Datei wird schrittweise in die neue Struktur integriert"
                }, f, indent=2)
        
        # Agent-Konfigurationen migrieren
        self._migrate_agent_configs(project_path, bmad_core)
        
        # Task-Integration
        self._integrate_global_tasks(project_path, bmad_core)
        
        # Registriere Projekt
        global_registry.register_project(str(project_path), project_config)
        
        return {
            "project": "Claude Global",
            "status": "migrated",
            "backup": str(backup_path),
            "bmad_core": str(bmad_core),
            "config": project_config
        }
    
    def migrate_mcp_infrastructure_project(self) -> Dict[str, Any]:
        """Migriere MCP Infrastructure Projekt"""
        project_path = self.existing_projects["BMAD MCP Infrastructure"]
        
        print(f"🔄 Migriere MCP Infrastructure Projekt: {project_path}")
        
        # Backup erstellen
        backup_path = self.create_backup(project_path, "bmad-mcp-infrastructure")
        
        # .bmad-core erweitern
        bmad_core = project_path / ".bmad-core"
        
        # Infrastructure-Template nutzen
        template_config = template_manager._get_infrastructure_template()
        structure = template_config["structure"][".bmad-core"]
        template_manager._create_directory_structure(bmad_core, structure)
        
        # Projekt-Konfiguration
        project_config = {
            "name": "BMAD MCP Infrastructure",
            "version": "2.0.0", 
            "type": "mcp_infrastructure",
            "template": "infrastructure",
            "description": "Cross-IDE MCP server infrastructure für BMAD system integration",
            "migrated_from": "agent_access_config",
            "migrated_at": datetime.now().isoformat(),
            "backup_location": str(backup_path),
            "features": [
                "Agent access configuration",
                "Cross-IDE synchronization",
                "MCP server integration points",
                "Global registry functionality",
                "Quality gates infrastructure"
            ],
            "infrastructure": {
                "mcp_server": True,
                "docker_support": True,
                "ci_cd_pipeline": True,
                "monitoring": True
            }
        }
        
        # Bestehende agent-access-config.yaml integrieren
        if (project_path / "agent-access-config.yaml").exists():
            try:
                with open(project_path / "agent-access-config.yaml", 'r', encoding='utf-8') as f:
                    legacy_config = yaml.safe_load(f)
                    project_config["legacy_agent_config"] = legacy_config
            except Exception as e:
                print(f"⚠️  Warnung beim Laden der Legacy-Config: {e}")
        
        # Konfiguration schreiben
        with open(bmad_core / "project.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(project_config, f, default_flow_style=False, allow_unicode=True)
        
        # Registriere Projekt
        global_registry.register_project(str(project_path), project_config)
        
        return {
            "project": "BMAD MCP Infrastructure",
            "status": "migrated", 
            "backup": str(backup_path),
            "bmad_core": str(bmad_core),
            "config": project_config
        }
    
    def migrate_gutachter_project(self) -> Dict[str, Any]:
        """Migriere Gutachter App Projekt"""
        project_path = self.existing_projects["Gutachter App"]
        
        print(f"🔄 Migriere Gutachter App Projekt: {project_path}")
        
        # Backup erstellen  
        backup_path = self.create_backup(project_path, "gutachter-app")
        
        # .bmad-core erweitern
        bmad_core = project_path / ".bmad-core"
        
        # Web-App Template nutzen (Business-Anwendung)
        template_config = template_manager._get_webapp_template()
        structure = template_config["structure"][".bmad-core"]
        template_manager._create_directory_structure(bmad_core, structure)
        
        # Projekt-Konfiguration
        project_config = {
            "name": "Gutachter KFZ System",
            "version": "1.0.0",
            "type": "business_application",
            "template": "web-app",
            "description": "Vehicle assessment system mit Notion database integration",
            "migrated_from": "bmad_config",
            "migrated_at": datetime.now().isoformat(),
            "backup_location": str(backup_path),
            "business_domain": "automotive_assessment",
            "features": [
                "Specialized workflow für vehicle assessments",
                "Damage assessment und cost calculation",
                "Photo documentation und report generation",
                "Client portal integration",
                "Slack Canvas integration für team communication"
            ],
            "notion_databases": {
                "count": 10,
                "types": ["projects", "tasks", "resources", "timeTracking", "clients", "vehicles", "assessments"]
            },
            "workflow": {
                "phase": "operational",
                "timeline": "1-week per assessment",
                "required_agents": ["analyst", "qa"]
            }
        }
        
        # Bestehende bmad-config.json integrieren
        if (project_path / "bmad-config.json").exists():
            try:
                with open(project_path / "bmad-config.json", 'r', encoding='utf-8') as f:
                    legacy_config = json.load(f)
                    project_config["legacy_config"] = legacy_config
            except Exception as e:
                print(f"⚠️  Warnung beim Laden der Legacy-Config: {e}")
        
        # Konfiguration schreiben
        with open(bmad_core / "project.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(project_config, f, default_flow_style=False, allow_unicode=True)
        
        # Business-spezifische Workflows erstellen
        self._create_business_workflows(bmad_core)
        
        # Registriere Projekt
        global_registry.register_project(str(project_path), project_config)
        
        return {
            "project": "Gutachter KFZ System",
            "status": "migrated",
            "backup": str(backup_path), 
            "bmad_core": str(bmad_core),
            "config": project_config
        }
    
    def _migrate_agent_configs(self, project_path: Path, bmad_core: Path):
        """Migriere bestehende Agent-Konfigurationen"""
        agents_dir = bmad_core / "agents"
        
        # Mapping von Legacy-Dateien zu neuen Agent-Configs
        legacy_mappings = {
            "bmad-dev-settings.json": "dev.yaml",
            "bmad-analyst-settings.json": "analyst.yaml", 
            "bmad-architect-settings.json": "architect.yaml",
            "bmad-pm-settings.json": "pm.yaml"
        }
        
        for legacy_file, new_file in legacy_mappings.items():
            legacy_path = project_path / legacy_file
            if legacy_path.exists():
                try:
                    with open(legacy_path, 'r', encoding='utf-8') as f:
                        legacy_config = json.load(f)
                    
                    # Konvertiere zu neuem Format
                    agent_config = {
                        "name": f"bmad-{new_file.replace('.yaml', '')}",
                        "version": "2.0.0",
                        "enabled": True,
                        "migrated_from": legacy_file,
                        "legacy_config": legacy_config,
                        "model_preferences": {
                            "primary": "claude-3-sonnet",
                            "fallback": "claude-3-haiku",
                            "temperature": 0.1
                        },
                        "permissions": {
                            "file_access": True,
                            "api_access": True,
                            "git_access": True
                        }
                    }
                    
                    # Schreibe neue Agent-Config
                    with open(agents_dir / new_file, 'w', encoding='utf-8') as f:
                        yaml.dump(agent_config, f, default_flow_style=False, allow_unicode=True)
                    
                    print(f"Agent-Config migriert: {legacy_file} -> {new_file}")
                    
                except Exception as e:
                    print(f"Fehler bei Agent-Migration {legacy_file}: {e}")
    
    def _integrate_global_tasks(self, project_path: Path, bmad_core: Path):
        """Integriere globale Tasks in neue Struktur"""
        global_tasks_file = Path.home() / ".bmad-global" / "tasks.json"
        
        if global_tasks_file.exists():
            try:
                with open(global_tasks_file, 'r', encoding='utf-8') as f:
                    global_tasks = json.load(f)
                
                # Link zu globalen Tasks erstellen
                tasks_dir = bmad_core / "tasks"
                tasks_link = tasks_dir / "global_tasks_link.json"
                
                with open(tasks_link, 'w', encoding='utf-8') as f:
                    json.dump({
                        "note": "Link zu globalen BMAD-Tasks",
                        "global_tasks_path": str(global_tasks_file),
                        "active_tasks_count": len(global_tasks.get("tasks", [])),
                        "integration_note": "Diese Tasks sind global verfügbar für alle BMAD-Projekte"
                    }, f, indent=2)
                
                print("✅ Globale Tasks verlinkt")
                
            except Exception as e:
                print(f"⚠️  Fehler bei Task-Integration: {e}")
    
    def _create_business_workflows(self, bmad_core: Path):
        """Erstelle business-spezifische Workflows für Gutachter-App"""
        workflows_dir = bmad_core / "workflows"
        
        # Assessment Workflow
        assessment_workflow = {
            "name": "Vehicle Assessment Workflow",
            "type": "business_process",
            "stages": [
                {
                    "name": "initial_contact",
                    "description": "Erstkontakt mit Kunde",
                    "required_data": ["contact_info", "vehicle_info", "incident_details"],
                    "responsible_agent": "analyst"
                },
                {
                    "name": "on_site_inspection", 
                    "description": "Vor-Ort Begutachtung",
                    "required_data": ["photos", "damage_assessment", "cost_estimate"],
                    "responsible_agent": "analyst"
                },
                {
                    "name": "report_generation",
                    "description": "Gutachten-Erstellung",
                    "required_data": ["damage_analysis", "repair_costs", "depreciation"],
                    "responsible_agent": "analyst"
                },
                {
                    "name": "quality_review",
                    "description": "Qualitätskontrolle",
                    "required_data": ["review_checklist", "accuracy_check"],
                    "responsible_agent": "qa"
                },
                {
                    "name": "client_delivery",
                    "description": "Gutachten-Auslieferung",
                    "required_data": ["final_report", "client_communication"],
                    "responsible_agent": "pm"
                }
            ],
            "sla": {
                "standard_timeline": "7 days",
                "express_timeline": "3 days",
                "quality_gates": ["photo_documentation", "cost_verification", "legal_compliance"]
            }
        }
        
        with open(workflows_dir / "assessment.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(assessment_workflow, f, default_flow_style=False, allow_unicode=True)
        
        print("✅ Business-Workflows erstellt")
    
    def run_full_migration(self) -> Dict[str, Any]:
        """Führe komplette Migration aller Projekte durch"""
        print("🚀 Starte BMAD-Projekt Migration...")
        print(f"📦 Backups werden gespeichert in: {self.backup_dir}")
        
        migration_results = {
            "started_at": datetime.now().isoformat(),
            "projects": [],
            "errors": [],
            "summary": {}
        }
        
        # Migriere alle Projekte
        migrations = [
            ("Claude Global", self.migrate_claude_global_project),
            ("MCP Infrastructure", self.migrate_mcp_infrastructure_project), 
            ("Gutachter App", self.migrate_gutachter_project)
        ]
        
        for project_name, migration_func in migrations:
            try:
                print(f"\n📋 Migriere {project_name}...")
                result = migration_func()
                migration_results["projects"].append(result)
                print(f"✅ {project_name} erfolgreich migriert")
                
            except Exception as e:
                error_msg = f"❌ Fehler bei Migration von {project_name}: {str(e)}"
                print(error_msg)
                migration_results["errors"].append({
                    "project": project_name,
                    "error": str(e)
                })
        
        # Zusammenfassung
        migration_results["completed_at"] = datetime.now().isoformat()
        migration_results["summary"] = {
            "total_projects": len(migrations),
            "successful_migrations": len(migration_results["projects"]),
            "failed_migrations": len(migration_results["errors"]),
            "backup_location": str(self.backup_dir)
        }
        
        # Migrations-Bericht speichern
        report_file = self.backup_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(migration_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Migrations-Bericht: {report_file}")
        print(f"✅ Migration abgeschlossen: {migration_results['summary']['successful_migrations']}/{migration_results['summary']['total_projects']} Projekte erfolgreich")
        
        return migration_results


def main():
    """Haupt-Migrations-Skript"""
    # Fix Windows Console Encoding
    if os.name == 'nt':
        os.system('chcp 65001 > nul')
    
    print("BMAD Project Migration Tool v2.0")
    print("=" * 50)
    
    migrator = BMadProjectMigrator()
    
    # Prüfe ob Projekte existieren
    missing_projects = []
    for name, path in migrator.existing_projects.items():
        if not path.exists():
            missing_projects.append(f"{name}: {path}")
    
    if missing_projects:
        print("⚠️  Folgende Projekte wurden nicht gefunden:")
        for project in missing_projects:
            print(f"  • {project}")
        print("\nMigration wird trotzdem fortgesetzt...\n")
    
    # Führe Migration durch
    try:
        results = migrator.run_full_migration()
        
        if results["summary"]["successful_migrations"] > 0:
            print("\n🎉 Migration erfolgreich!")
            print("\n📋 Nächste Schritte:")
            print("1. Prüfe migrierte Projekt-Konfigurationen")
            print("2. Teste BMAD MCP Server: python -m src.bmad_mcp.server")
            print("3. Verwende neue Template-Tools: bmad_create_project")
            print("4. Alte Backup-Dateien nach Bedarf löschen")
            
        return 0
        
    except Exception as e:
        print(f"\n❌ Kritischer Fehler bei Migration: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())