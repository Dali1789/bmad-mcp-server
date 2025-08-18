# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-18

### ⭐ Hauptfeatures hinzugefügt

#### 🎨 Template-System
- **6 Projekt-Templates** implementiert:
  - `standard`: Basis BMAD-Projekt mit vollständiger Struktur
  - `web-app`: Frontend/Backend mit React/Vue/Angular Support
  - `api`: REST/GraphQL APIs mit OpenAPI-Dokumentation  
  - `mobile`: React Native/Flutter Cross-Platform Apps
  - `data-science`: ML/Jupyter mit Notebooks und Data Pipelines
  - `infrastructure`: Docker/Terraform/Kubernetes Deployments

#### 📁 Standardisierte Projektstrukturen
- **Einheitliche `.bmad-core/` Verzeichnisse** für alle Projekte
- **Vordefinierte Ordnerstrukturen:** agents/, workflows/, integrations/, quality-gates/
- **Automatische Konfiguration:** Sofort produktive Projekte ohne Setup
- **Universal kompatibel:** Funktioniert mit allen IDEs und Tools

#### 🔍 Auto-Discovery System
- **Automatische Projekt-Erkennung:** Findet neue .bmad-core Verzeichnisse
- **Background-Monitoring:** Scannt alle 5 Minuten nach neuen Projekten
- **Intelligente Typ-Erkennung:** Erkennt Web-Apps, APIs, Mobile Apps automatisch
- **Registry-Integration:** Neue Projekte werden automatisch registriert

#### 🔄 Migration-Tools
- **Legacy-Projekt-Migration:** Migriert bestehende Projekte auf BMAD v2.0
- **Backup-System:** Automatische Backups vor Migration
- **Rückwärtskompatibilität:** Erhält bestehende Konfigurationen
- **Zero-Downtime:** Nahtlose Migration ohne Datenverlust

### 🛠️ Neue MCP Tools

- `bmad_create_project`: Erstelle neues Projekt mit standardisierter Struktur
- `bmad_list_project_templates`: Zeige alle verfügbaren Templates
- `bmad_get_project_template_info`: Detaillierte Template-Information
- `bmad_migrate_project_to_standard`: Migriere bestehende Projekte

### 🔧 Technische Verbesserungen

#### Core-Module erweitert
- **project_templates.py**: Vollständiges Template-Management System
- **auto_discovery.py**: Automatische Projekt-Erkennung und -Integration
- **Integration in bmad_tools.py** mit allen MCP Tool-Handlern
- **Server.py** um neue Tool-Definitionen erweitert

#### Migration Scripts
- **migrate_existing_projects.py**: Vollständige Migration mit Backup
- **simple_migration.py**: Windows-kompatible einfache Migration
- **Automatische .bmad-core Struktur-Erstellung**
- **Legacy-Konfiguration-Preservation**

### 📚 Dokumentation

- **README.md** vollständig aktualisiert mit Template-System Features
- **RELEASE_NOTES_v2.0.md** mit detaillierter Feature-Beschreibung
- **Neue Beispiele** für Template-Nutzung
- **Roadmap** um Template-Features erweitert

### 🏗️ Infrastruktur

- **CI/CD Pipeline** um Template-Tests erweitert
- **Docker-Setup** für Template-Entwicklung
- **Cross-Platform** Kompatibilität sichergestellt
- **Git Tags** und Release-Management

### 💡 Vorteile

#### Für Entwickler
- **Sofortige Orientierung:** Jedes BMAD-Projekt hat gleiche Struktur
- **Zero-Setup:** Neue Projekte sind sofort produktiv
- **Konsistenz:** Einheitliche Erfahrung über alle Projekte
- **Tool-Integration:** IDEs erkennen Struktur automatisch

#### Für Teams
- **Standardisierung:** Alle folgen gleichen Konventionen
- **Onboarding:** Neue Teammitglieder finden sich sofort zurecht
- **Collaboration:** Einheitliche Workflows und Strukturen
- **Skalierbarkeit:** Einfache Erweiterung um neue Projekt-Typen

#### Für Wartung
- **Automatisierung:** Weniger manuelle Konfiguration
- **Qualität:** Vordefinierte Quality Gates und Workflows
- **Dokumentation:** Standardisierte Dokumentationsstrukturen
- **Migration:** Einfache Updates auf neue BMAD-Versionen

### 📈 Performance-Verbesserungen

- **Schnellere Projekt-Erstellung:** Template-basiert statt manuell
- **Automatische Registrierung:** Keine manuelle Registry-Verwaltung
- **Background-Discovery:** Findet neue Projekte automatisch
- **Optimierte Struktur:** Bessere Tool-Performance durch Standards

### 🔄 Migration von v1.x

Bestehende BMAD-Projekte können nahtlos migriert werden:

```python
# Automatische Migration mit Backup
bmad_migrate_project_to_standard(
    project_path="./mein-altes-projekt",
    backup=True  # Erstellt automatisch Backup
)
```

## [1.0.0] - 2025-01-15

### Hinzugefügt
- **Vollständiges BMAD MCP Server System**
- **5 Spezialisierte AI-Agents:** Analyst, Architect, Developer, PM, QA
- **Erweiterte Task-Management Features**
- **Real-time Progress Tracking** mit Live-Updates
- **Notion Integration** mit bi-direktionaler Synchronisation
- **TodoWrite Bridge** für nahtlose Claude-Integration
- **Zeit-basiertes Monitoring** mit geplanten Erinnerungen
- **Work Day Simulation** für Demo und Testing
- **Live Console Output** mit schöner Formatierung
- **Projekt-Context Integration** mit globaler Registry
- **Performance Metrics** mit detailliertem Tracking
- **Universal IDE Access** über MCP-Protokoll
- **Repository-Professionalisierung** mit umfassender Dokumentation
- **CI/CD Pipeline** mit automatisierten Tests
- **Security Policy** und Best Practices
- **Docker Multi-Service Setup**
- **Comprehensive API Documentation**

### Technische Details
- **35+ MCP Tools** für vollständige BMAD-Funktionalität
- **MCP Protocol v1.1** Support
- **Python 3.8+ Kompatibilität**
- **Cross-Platform:** Windows, macOS, Linux
- **IDE-Universal:** Claude Code, VS Code, Cursor, etc.

---

**Vollständige Repository:** [GitHub](https://github.com/Dali1789/bmad-mcp-server)