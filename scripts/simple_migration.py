#!/usr/bin/env python3
"""
Einfache BMAD Migration ohne Unicode für Windows-Kompatibilität
"""

import os
import sys
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime

# Füge src-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bmad_mcp.core.project_templates import template_manager
from bmad_mcp.core.global_registry import global_registry


def main():
    """Einfache Migration"""
    print("BMAD Project Migration Tool v2.0")
    print("=" * 40)
    
    # Bekannte Projekte
    projects = {
        "Claude Global": Path.home() / "AppData" / "Roaming" / "Claude",
        "BMAD MCP Server": Path.home() / "AppData" / "Roaming" / "Claude" / "bmad-mcp-server",
        "Gutachter App": Path.home() / "AppData" / "Roaming" / "Claude" / "gutachter-app"
    }
    
    backup_dir = Path.home() / ".bmad-global" / "migration-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    migrated_count = 0
    
    for name, path in projects.items():
        if not path.exists():
            print(f"SKIP: {name} (Pfad existiert nicht: {path})")
            continue
            
        print(f"\nMigriere: {name}")
        print(f"Pfad: {path}")
        
        try:
            # .bmad-core erstellen falls nicht vorhanden
            bmad_core = path / ".bmad-core"
            if not bmad_core.exists():
                print("Erstelle .bmad-core Struktur...")
                bmad_core.mkdir(parents=True, exist_ok=True)
                
                # Standard-Struktur erstellen
                template_config = template_manager._get_standard_template()
                structure = template_config["structure"][".bmad-core"]
                template_manager._create_directory_structure(bmad_core, structure)
                
                # Basis-Konfiguration
                project_config = {
                    "name": name,
                    "version": "2.0.0",
                    "type": "standard",
                    "template": "standard",
                    "description": f"Migriertes BMAD-Projekt: {name}",
                    "migrated_at": datetime.now().isoformat(),
                    "bmad_version": "2.0.0"
                }
                
                # Konfiguration schreiben
                with open(bmad_core / "project.yaml", 'w', encoding='utf-8') as f:
                    yaml.dump(project_config, f, default_flow_style=False, allow_unicode=True)
                
                print("OK: .bmad-core erstellt")
                migrated_count += 1
            else:
                print("OK: .bmad-core bereits vorhanden")
            
            # In Registry registrieren
            try:
                global_registry.register_project(str(path), {
                    "name": name,
                    "path": str(path),
                    "type": "standard",
                    "migrated": True
                })
                print("OK: Projekt registriert")
            except Exception as e:
                print(f"WARN: Registry-Fehler: {e}")
                
        except Exception as e:
            print(f"ERROR: Migration fehlgeschlagen: {e}")
    
    print(f"\n" + "=" * 40)
    print(f"Migration abgeschlossen: {migrated_count} Projekte migriert")
    print("Naechste Schritte:")
    print("1. MCP Server testen: python -m src.bmad_mcp.server")
    print("2. Neue Tools nutzen: bmad_create_project")
    print("3. Projekte anzeigen: bmad_list_projects")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())