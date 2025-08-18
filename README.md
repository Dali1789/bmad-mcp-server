# BMAD MCP Server

🏗️ **Breakthrough Method for Agile AI-driven Development - MCP Server**

Advanced agent routing with OpenRouter integration - Vollständige Integration bestehender BMAD-Systemkonfigurationen.

## Overview

Der BMAD MCP Server integriert die komplette BMAD-Methodologie über das Model Context Protocol und ermöglicht **einheitliche Struktur** - egal von welchem IDE aus gearbeitet wird, jedes IDE hat Zugriff auf die gleichen Projektdateien.

## 🎯 Core Features

- **Multi-Model Agent Routing**: Intelligent model selection based on task type
- **OpenRouter Integration**: Seamless access to multiple AI models with existing system configs
- **Agent Specialization**: 5 specialized agents (analyst, architect, dev, pm, qa) with proven configurations
- **Project Detection**: Automatic `.bmad-core` configuration detection with global registry
- **Universal IDE Access**: Consistent project access across all IDEs - "einheitliche Struktur"
- **Existing System Integration**: Vollständige Übernahme bestehender BMAD-Konfigurationen
- **Task Management**: Integrierte Workflows, Templates und Quality Gates
- **Docker Support**: Production-ready containerized deployment

## 🤖 Intelligent Agent System

### Bestehende Agent-Konfigurationen (übernommen)

#### 📊 **BMAD Analyst**
- **Model**: `perplexity/llama-3.1-sonar-large-128k-online`
- **Temperature**: `0.2` | **Max Tokens**: `8000` | **Timeout**: `90s`
- **Einsatz**: Market research, competitive analysis, data gathering, trend analysis
- **Tools**: Web research, data analysis, Notion integration, Playwright

#### 🏗️ **BMAD Architect** 
- **Model**: `anthropic/claude-3-opus`
- **Temperature**: `0.3` | **Max Tokens**: `8000` | **Timeout**: `120s`
- **Einsatz**: System architecture, technical design, infrastructure planning
- **Tools**: System design, documentation, GitHub integration, performance analysis

#### 💻 **BMAD Dev**
- **Model**: `anthropic/claude-3.5-sonnet`
- **Temperature**: `0.1` | **Max Tokens**: `4000` | **Timeout**: `60s`
- **Einsatz**: Coding, bug fixes, implementation, code reviews
- **Tools**: Auto-linting, testing frameworks, GitHub integration, code analysis

#### 📋 **BMAD PM**
- **Model**: `google/gemini-pro-1.5`
- **Temperature**: `0.4` | **Max Tokens**: `3000` | **Timeout**: `45s`
- **Einsatz**: Project planning, resource management, timeline coordination
- **Tools**: Task management, reporting, Notion integration, calendar

#### 🧪 **BMAD QA**
- **Model**: `anthropic/claude-3-haiku`
- **Temperature**: `0.1` | **Max Tokens**: `4000` | **Timeout**: `60s`
- **Einsatz**: Testing, quality checks, validation, bug reporting
- **Tools**: Test automation, bug tracking, performance testing, security testing

## 🌐 Einheitliche Struktur - Global Registry

**Das Hauptziel**: Egal von welchem IDE aus - jedes IDE hat Zugriff auf die gleichen Projektdateien!

### Global Registry Features
- **Zentrale Projektverwaltung**: Alle BMAD-Projekte global registriert
- **Cross-IDE Synchronisation**: Symlinks für universellen Zugriff
- **Active Project Management**: Globales aktives Projekt für alle IDEs
- **Shared Resources**: Gemeinsame Templates, Agents, Workflows

### Unterstützte IDEs
- ✅ **Kilo Code** - Native MCP Integration
- ✅ **Claude Code** - Vollständige Tool-Unterstützung
- ✅ **VS Code** - Über MCP Extensions
- ✅ **Cursor** - MCP-kompatibel

## 📁 Bestehende System-Integration

### Notion-Datenbanken (übernommen)
```yaml
notion_databases:
  business_resources: "21d5e4b84c44808db635f37c5cd8f483"
  gutachten_projects: "1765e4b8-4c44-811c-92c7-f310901a5b6c"
  gutachten_tasks: "1765e4b8-4c44-813d-b906-e6b343d745fd"
  services: "17648f3e-4cb0-8108-acdb-c7e2b2c604e2"
  # ... weitere bestehende Datenbanken
```

### Project Templates (erweitert)
- **Website**: 4 Wochen Standard-Workflow
- **App**: 8 Wochen Full-Stack Development
- **Automation**: 3 Wochen Automatisierung
- **Gutachten**: 1 Woche Gutachten-Workflow

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/FaberDS/bmad-mcp-server.git
cd bmad-mcp-server

# Install dependencies
pip install -r requirements.txt

# Configure OpenRouter API (bestehende Konfiguration)
export OPENROUTER_API_KEY="your-openrouter-key"

# Start server
python -m bmad_mcp.server
```

### IDE Integration

#### Kilo Code
```json
{
  "mcpServers": {
    "bmad": {
      "command": "python",
      "args": ["-m", "bmad_mcp.server"],
      "env": {
        "OPENROUTER_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### Claude Code (claude_desktop_config.json)
```json
{
  "mcpServers": {
    "bmad": {
      "command": "python",
      "args": ["-m", "bmad_mcp.server"]
    }
  }
}
```

## 🛠️ Available Tools

### Global Registry Management
- `bmad_register_project`: Projekt in globaler Registry registrieren
- `bmad_set_active_project`: Aktives Projekt für universellen Zugriff setzen
- `bmad_list_projects`: Alle registrierten Projekte anzeigen
- `bmad_get_registry_info`: Registry-Status und -Informationen

### Agent Management
- `bmad_activate_agent`: Agent wechseln (analyst, architect, dev, pm, qa)
- `bmad_list_agents`: Verfügbare Agents und Capabilities anzeigen
- `bmad_get_agent_help`: Agent-spezifische Hilfe

### Project Operations
- `bmad_detect_project`: .bmad-core Konfiguration scannen
- `bmad_execute_task`: BMAD-Tasks mit Agent-Kontext ausführen
- `bmad_query_with_model`: Agent-spezifische Model-Anfragen

### Document & Workflow Management
- `bmad_create_document`: Dokumente mit Templates erstellen
- `bmad_run_checklist`: Quality Checklists ausführen
- `bmad_load_templates`: Projekt-Templates laden

## 🏗️ Architecture

```
BMAD MCP Server
├── 🌐 Global Registry (einheitliche Struktur)
├── 🤖 Agent Router (5 spezialisierte Agents)
├── 🔄 OpenRouter Integration (bestehende Configs)
├── 📁 Project Detection (.bmad-core scanning)
├── 📋 Task Management (Workflows, Templates)
├── 🔧 MCP Protocol Layer (Standard Tools/Resources)
└── 📊 Context Management (projekt-übergreifend)
```

## ⚙️ Configuration

### Agent-Konfiguration (aus bestehendem System)
```yaml
agents:
  analyst:
    model: "perplexity/llama-3.1-sonar-large-128k-online"
    temperature: 0.2
    max_tokens: 8000
    timeout: 90000
    
  architect:
    model: "anthropic/claude-3-opus"
    temperature: 0.3
    max_tokens: 8000
    timeout: 120000
    
  dev:
    model: "anthropic/claude-3.5-sonnet"
    temperature: 0.1
    max_tokens: 4000
    timeout: 60000
```

### Global BMAD Structure
```
~/.bmad-global/
├── project-registry.json    # Globale Projekt-Registry
├── global-config.yaml      # System-weite Konfiguration
├── projects/               # Projekt-Symlinks für universellen Zugriff
└── shared-resources/       # Gemeinsame Templates & Workflows

config/bmad-core/
├── agents/                 # Agent-Definitionen
├── tasks/                  # Task-Templates
├── templates/              # Dokument-Templates
├── checklists/            # Quality Gates
├── workflows/             # Prozess-Definitionen
└── core-config.yaml       # Core-Konfiguration
```

## 🐳 Deployment

### Docker
```bash
docker build -t bmad-mcp-server .
docker run -p 3000:3000 -e OPENROUTER_API_KEY=your-key bmad-mcp-server
```

### Docker Compose
```bash
docker-compose up -d
```

## 📊 Task Management Integration

### Workflow States (übernommen)
- `backlog` → `todo` → `in_progress` → `review` → `testing` → `done`

### Quality Gates
- ✅ Auto-Linting aktiviert
- ✅ Code Coverage > 80%
- ✅ Performance Benchmarks
- ✅ Security Scans

### Notion Integration
- Automatische Task-Synchronisation
- Projekt-übergreifende Dokumentation
- Performance Metrics Tracking

## 🎯 Success Metrics

- **Cross-IDE Consistency**: Gleiche Projektdateien überall verfügbar
- **Agent Performance**: Model-spezifische Optimierung
- **Development Velocity**: Beschleunigte Entwicklungszyklen
- **Quality Improvement**: Reduzierte Bug-Rate durch Quality Gates

## 💡 Usage Examples

### Projekt registrieren
```bash
# Bestehende .bmad-core Projekte automatisch registrieren
bmad_register_project /path/to/project "mein-projekt"
bmad_set_active_project "mein-projekt"
```

### Agent-spezifische Arbeit
```bash
# Marktanalyse mit Analyst
bmad_activate_agent analyst
bmad_query_with_model "Analysiere den KI-Markt 2025"

# Architektur mit Architect
bmad_activate_agent architect
bmad_query_with_model "Designe Microservices-Architektur"
```

## 📈 Roadmap

- [ ] **Weitere Agents**: Hinzufügung zusätzlicher spezialisierter Agents
- [ ] **Performance Optimization**: Model-Caching und Response-Optimierung
- [ ] **Extended IDE Support**: Weitere IDE-Integrationen
- [ ] **Advanced Workflows**: Komplexe Multi-Agent Workflows
- [ ] **Analytics Dashboard**: Real-time Performance Monitoring

## 🤝 Contributing

1. Fork das Repository
2. Feature Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen committen (`git commit -m 'Add amazing feature'`)
4. Push to Branch (`git push origin feature/amazing-feature`)
5. Pull Request öffnen

## 📄 License

MIT License - siehe [LICENSE](LICENSE) für Details.

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/FaberDS/bmad-mcp-server/issues)
- 💬 [Discussions](https://github.com/FaberDS/bmad-mcp-server/discussions)

---

**🌟 Einheitliche Struktur erreicht**: Projektdateien von jedem IDE aus zugänglich!