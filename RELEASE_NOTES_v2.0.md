# 🚀 BMAD MCP Server v2.0

## ⭐ Hauptfeatures

### 🎨 **Template-System**
**Brandneues Feature für standardisierte Projekt-Erstellung!**

- **6 Projekt-Templates verfügbar:**
  - `standard`: Basis BMAD-Projekt mit vollständiger Struktur
  - `web-app`: Frontend/Backend mit React/Vue/Angular Support
  - `api`: REST/GraphQL APIs mit OpenAPI-Dokumentation
  - `mobile`: React Native/Flutter Cross-Platform Apps
  - `data-science`: ML/Jupyter mit Notebooks und Data Pipelines
  - `infrastructure`: Docker/Terraform/Kubernetes Deployments

### 📁 **Standardisierte Projektstrukturen**
- **Einheitliche `.bmad-core/` Verzeichnisse** für alle Projekte
- **Vordefinierte Ordnerstrukturen:** agents/, workflows/, integrations/, quality-gates/
- **Automatische Konfiguration:** Sofort produktive Projekte ohne Setup
- **Universal kompatibel:** Funktioniert mit allen IDEs und Tools

### 🔍 **Auto-Discovery System**
- **Automatische Projekt-Erkennung:** Findet neue .bmad-core Verzeichnisse
- **Background-Monitoring:** Scannt alle 5 Minuten nach neuen Projekten
- **Intelligente Typ-Erkennung:** Erkennt Web-Apps, APIs, Mobile Apps automatisch
- **Registry-Integration:** Neue Projekte werden automatisch registriert

### 🔄 **Migration-Tools**
- **Legacy-Projekt-Migration:** Migriert bestehende Projekte auf BMAD v2.0
- **Backup-System:** Automatische Backups vor Migration
- **Rückwärtskompatibilität:** Erhält bestehende Konfigurationen
- **Zero-Downtime:** Nahtlose Migration ohne Datenverlust

## 🛠️ **Neue MCP Tools (4 Tools)**

### Projekt-Template-Management
- `bmad_create_project`: Erstelle neues Projekt mit Template
- `bmad_list_project_templates`: Zeige verfügbare Templates
- `bmad_get_project_template_info`: Detaillierte Template-Information  
- `bmad_migrate_project_to_standard`: Migriere bestehende Projekte

## 📊 **Beispiel-Nutzung**

```python
# Verfügbare Templates anzeigen
bmad_list_project_templates()

# Neues Web-App Projekt erstellen
bmad_create_project(
    project_path="./meine-web-app",
    template="web-app", 
    name="Meine Web Application",
    description="Moderne React-basierte Webanwendung"
)

# Bestehendes Projekt migrieren
bmad_migrate_project_to_standard(
    project_path="./legacy-projekt",
    backup=True
)
```

## 🏗️ **Projekt-Struktur**

Alle neuen BMAD-Projekte folgen dieser standardisierten Struktur:

```
mein-projekt/
├── .bmad-core/              # 🎯 BMAD Konfiguration
│   ├── project.yaml         # Projekt-Metadaten & Konfiguration
│   ├── tasks/              # Task-Definitionen & Templates
│   ├── agents/             # Agent-spezifische Konfigurationen
│   ├── workflows/          # Automatisierte Workflows (CI/CD, Review)
│   ├── integrations/       # Service-Integrationen (Notion, Slack, Git)
│   ├── quality-gates/      # Qualitätskontrolle (Linting, Testing, Security)
│   └── memory/             # Projekt-Memory & Entscheidungsdokumentation
├── docs/                   # 📚 Dokumentation (setup/, api/, architecture/)
├── src/                    # 💻 Source Code
├── tests/                  # 🧪 Tests
├── config/                 # ⚙️ Konfigurationsdateien
├── scripts/                # 🔧 Utility Scripts
├── assets/                 # 🎨 Medien & Design Assets
└── README.md               # 📋 Projekt-Overview
```

## 💡 **Vorteile**

### Für Entwickler
- **Sofortige Orientierung:** Jedes BMAD-Projekt hat gleiche Struktur
- **Zero-Setup:** Neue Projekte sind sofort produktiv
- **Konsistenz:** Einheitliche Erfahrung über alle Projekte
- **Tool-Integration:** IDEs erkennen Struktur automatisch

### Für Teams
- **Standardisierung:** Alle folgen gleichen Konventionen
- **Onboarding:** Neue Teammitglieder finden sich sofort zurecht
- **Collaboration:** Einheitliche Workflows und Strukturen
- **Skalierbarkeit:** Einfache Erweiterung um neue Projekt-Typen

### Für Wartung
- **Automatisierung:** Weniger manuelle Konfiguration
- **Qualität:** Vordefinierte Quality Gates und Workflows
- **Dokumentation:** Standardisierte Dokumentationsstrukturen
- **Migration:** Einfache Updates auf neue BMAD-Versionen

## 🔧 **Technische Details**

- **Python 3.8+ Kompatibilität**
- **MCP Protocol v1.1** Support
- **6 Vordefinierte Templates** mit Erweiterbarkeit
- **Cross-Platform:** Windows, macOS, Linux
- **IDE-Universal:** Claude Code, VS Code, Cursor, etc.

## 🎯 **Migration von v1.x**

Bestehende BMAD-Projekte können nahtlos migriert werden:

```python
# Automatische Migration mit Backup
bmad_migrate_project_to_standard(
    project_path="./mein-altes-projekt",
    backup=True  # Erstellt automatisch Backup
)
```

Die Migration behält alle bestehenden Konfigurationen und erweitert sie um die neue Standardstruktur.

## 📈 **Performance**

- **Schnellere Projekt-Erstellung:** Template-basiert statt manuell
- **Automatische Registrierung:** Keine manuelle Registry-Verwaltung
- **Background-Discovery:** Findet neue Projekte automatisch
- **Optimierte Struktur:** Bessere Tool-Performance durch Standards

---

**BMAD v2.0 macht Projekt-Management noch einfacher, konsistenter und professioneller!** 🚀

Vollständige Dokumentation: [GitHub Repository](https://github.com/Dali1789/bmad-mcp-server)