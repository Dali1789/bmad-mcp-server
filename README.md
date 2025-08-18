# BMAD MCP Server 🚀

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive **Model Context Protocol (MCP) server** implementing the **BMAD (Business Modeling and Development)** methodology. Provides intelligent task management, multi-agent workflows, and cross-IDE project management through the MCP protocol.

## ✨ Features

### 🤖 **6 Specialized AI Agents**
- **📊 Analyst**: Business analysis, market research, requirement gathering
- **🏗️ Architect**: System design, architecture planning, tech stack selection  
- **💻 Developer**: Code implementation, debugging, technical development
- **📋 Project Manager**: Task coordination, timeline management, resource planning
- **🔍 QA**: Quality assurance, testing strategies, code review
- **🔍 Serena Bridge**: Semantic code intelligence via LSP integration ⭐ NEW!

### 📋 **Advanced Task Management**
- **Real-time Progress Tracking**: Live updates and notifications
- **Intelligent Scheduling**: Auto-allocation with capacity management
- **Follow-up Task Generation**: Automatic workflow progression
- **Notion Integration**: Bi-directional sync with Notion databases
- **TodoWrite Bridge**: Seamless Claude integration

### 🎨 **Template-System & Standardisierte Projektstrukturen** ⭐ NEW!
- **6 Projekt-Templates**: standard, web-app, api, mobile, data-science, infrastructure
- **Automatische Struktur-Erstellung**: Einheitliche `.bmad-core/` Verzeichnisse
- **Auto-Discovery**: Erkennt automatisch neue BMAD-Projekte
- **Migration-Tools**: Migriert bestehende Projekte auf BMAD v2.0 Standard
- **Zero-Setup**: Neue Projekte sind sofort produktiv mit kompletter Konfiguration

### 🔄 **Enhanced Features**
- **BMAD-METHOD Workflow System**: Complete implementation with intelligent orchestration ⭐ NEW!
- **Quality Gates (@qa commands)**: 6 comprehensive quality assurance commands ⭐ NEW!
- **Semantic Code Intelligence**: LSP-based code analysis via Serena Bridge ⭐ NEW!
- **Time-based Monitoring**: Scheduled reminders and progress checks
- **Work Day Simulation**: Demo modes and realistic progression testing
- **Live Console Output**: Beautiful formatted status displays
- **Project Context Integration**: Multi-project support with global registry
- **Performance Metrics**: Detailed tracking and reporting

### 🌐 **Universal IDE Access**
Compatible with any IDE supporting MCP:
- **Claude Code** ✅
- **VS Code** ✅ 
- **Cursor** ✅
- **Any MCP-compatible IDE** ✅

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **OpenRouter API Key** (for AI model routing)
- **Notion API Token** (optional, for database sync)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Add to your IDE's MCP configuration:

#### Claude Code (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "bmad": {
      "command": "python",
      "args": ["-m", "src.bmad_mcp.server"],
      "cwd": "/path/to/bmad-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/bmad-mcp-server",
        "OPENROUTER_API_KEY": "your_openrouter_api_key",
        "NOTION_TOKEN": "your_notion_token"
      }
    }
  }
}
```

#### VS Code / Cursor
```json
{
  "mcp.servers": {
    "bmad": {
      "command": "python",
      "args": ["-m", "src.bmad_mcp.server"],
      "cwd": "/path/to/bmad-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/bmad-mcp-server",
        "OPENROUTER_API_KEY": "your_openrouter_api_key"
      }
    }
  }
}
```

## 🛠️ Available MCP Tools

### 🤖 **Agent Management**
| Tool | Description | Example |
|------|-------------|---------|
| `bmad_list_agents` | List all available agents | Shows 5 specialized agents |
| `bmad_activate_agent` | Switch to specific agent | `agent: "dev"` |
| `bmad_get_agent_help` | Get agent-specific guidance | Context-aware help |

### 📋 **Task Management**
| Tool | Description | Example |
|------|-------------|---------|
| `bmad_get_task_summary` | Comprehensive task overview | Progress, metrics, status |
| `bmad_create_task` | Create new task with auto-scheduling | `task_id`, `name`, `hours` |
| `bmad_update_task_progress` | Update progress with real-time sync | `task_id`, `hours_completed` |
| `bmad_get_today_tasks` | Today's scheduled tasks | Daily workload view |
| `bmad_get_agent_tasks` | Agent-specific task list | Filter by agent |

### ⚡ **Enhanced Features**
| Tool | Description | Example |
|------|-------------|---------|
| `bmad_start_realtime_mode` | Enable live task monitoring | Background updates |
| `bmad_start_work_session` | Track work session for task | Time tracking |
| `bmad_simulate_work_day` | Demo realistic work progression | Testing & demos |
| `bmad_get_project_status` | Comprehensive project overview | Multi-project support |
| `bmad_sync_notion_tasks` | Sync with Notion databases | Bi-directional sync |

### 🔧 **Project Management** 
| Tool | Description | Example |
|------|-------------|---------|
| `bmad_detect_project` | Scan for BMAD configuration | Auto-discovery |
| `bmad_register_project` | Add project to global registry | Cross-IDE access |
| `bmad_execute_task` | Run BMAD methodology tasks | Template-based execution |
| `bmad_create_document` | Generate documents from templates | Automated documentation |
| `bmad_run_checklist` | Quality assurance checklists | QA workflows |

### 🚀 **BMAD-METHOD Workflow System** ⭐ NEW!
| Tool | Description | Example |
|------|-------------|---------|
| `bmad_workflow_start_project` | Start BMAD-METHOD project workflow | Full/planning/development modes |
| `bmad_workflow_advance` | Advance workflow to next state | Project/story state transitions |
| `bmad_workflow_start_story` | Create story in development cycle | Story creation & planning |
| `bmad_workflow_run_qa` | Execute quality gate (@qa commands) | *risk, *design, *trace, *nfr, *review, *gate |
| `bmad_workflow_execute_command` | Route agent commands intelligently | Context-aware agent routing |
| `bmad_workflow_get_status` | Get comprehensive workflow status | Real-time progress monitoring |
| `bmad_workflow_generate_report` | Generate detailed workflow reports | Analytics & recommendations |

### 🔍 **Serena Bridge Agent** ⭐ NEW!
| Tool | Description | Example |
|------|-------------|---------|
| `bmad_serena_initialize` | Initialize Serena MCP server | LSP server startup |
| `bmad_serena_activate_project` | Activate project for analysis | Semantic code intelligence |
| `bmad_serena_find_symbol` | Find code symbols semantically | Functions, classes, variables |
| `bmad_serena_get_symbols_overview` | Get file symbol overview | Code structure analysis |
| `bmad_serena_find_referencing_symbols` | Find symbol references | Cross-reference tracking |
| `bmad_serena_insert_after_symbol` | Insert code after symbol | Precise code insertion |
| `bmad_serena_replace_symbol_body` | Replace symbol implementation | Code modification |
| `bmad_serena_onboarding` | Automated project analysis | Comprehensive codebase review |
| `bmad_serena_search_for_pattern` | Advanced pattern search | Intelligent code search |
| `bmad_serena_write_memory` | Store project knowledge | Persistent insights |

### 🎨 **Template-System** ⭐ NEW!
| Tool | Description | Example |
|------|-------------|---------|
| `bmad_create_project` | Create project with standardized structure | `path`, `template` |
| `bmad_list_project_templates` | Show all available templates | 6 templates available |
| `bmad_get_project_template_info` | Detailed template information | Features, structure |
| `bmad_migrate_project_to_standard` | Migrate existing project | Auto-backup, structure |

## 📊 **Usage Examples**

### Basic Task Management
```python
# List available agents
bmad_list_agents()

# Activate developer agent
bmad_activate_agent(agent="dev")

# Create a new task
bmad_create_task(
    task_id="feature-implementation",
    name="Implement user authentication",
    allocated_hours=8.0,
    agent="dev"
)

# Update progress
bmad_update_task_progress(
    task_id="feature-implementation", 
    hours_completed=2.5
)

# Get daily overview
bmad_get_today_tasks()
```

### Real-time Monitoring
```python
# Start live monitoring
bmad_start_realtime_mode()

# Begin work session
bmad_start_work_session(task_id="feature-implementation")

# Work on task...

# End session with automatic progress logging
bmad_end_work_session(
    task_id="feature-implementation",
    hours_worked=2.0
)

# Get comprehensive status
bmad_get_realtime_status()
```

### Project Context
```python
# Detect BMAD project
bmad_detect_project(path="./my-project")

# Register in global registry
bmad_register_project(
    project_path="./my-project",
    project_name="My Awesome Project"
)

# Get project overview
bmad_get_project_status()
```

### Template-System Usage ⭐ NEW!
```python
# List available templates
bmad_list_project_templates()

# Get template details
bmad_get_project_template_info(template_name="web-app")

# Create new project with template
bmad_create_project(
    project_path="./my-web-app",
    template="web-app",
    name="My Web Application",
    description="Modern React-based web application"
)

# Migrate existing project
bmad_migrate_project_to_standard(
    project_path="./legacy-project",
    backup=True
)
```

### Available Templates
- **standard**: Basic BMAD project with full structure
- **web-app**: Frontend/Backend with React/Vue/Angular support
- **api**: REST/GraphQL APIs with OpenAPI documentation
- **mobile**: React Native/Flutter cross-platform apps
- **data-science**: ML/Jupyter with notebooks and data pipelines
- **infrastructure**: Docker/Terraform/Kubernetes deployments

### Simulation & Testing
```python
# Simulate full work day
bmad_simulate_work_day(speed_factor=10.0)

# Test specific agent workflow
bmad_simulate_agent_workday(agent="qa", hours=6.0)

# Simulate crisis scenarios
bmad_simulate_crisis_scenario(crisis_type="blocked_task")
```

## 🏗️ **Architecture**

```
bmad-mcp-server/
├── src/
│   └── bmad_mcp/
│       ├── core/                    # Core functionality
│       │   ├── task_tracker.py      # Advanced task management
│       │   ├── console_formatter.py # Live output formatting  
│       │   ├── realtime_updater.py  # Real-time monitoring
│       │   ├── time_monitor.py      # Scheduled monitoring
│       │   ├── simulator.py         # Demo & testing
│       │   ├── notion_sync.py       # Notion integration
│       │   └── global_registry.py   # Cross-IDE projects
│       ├── agents/                  # Agent definitions
│       │   ├── analyst.py           # Business analysis
│       │   ├── architect.py         # System design
│       │   ├── developer.py         # Code implementation
│       │   ├── project_manager.py   # Project coordination
│       │   ├── qa.py               # Quality assurance
│       │   └── serena_bridge.py    # Semantic code intelligence
│       ├── workflows/              # BMAD-METHOD workflow system
│       │   ├── workflow_engine.py  # Central workflow orchestration
│       │   ├── orchestrator_agent.py # Project/Story lifecycle management
│       │   ├── quality_gates.py    # Quality assurance (@qa commands)
│       │   └── workflow_states.py  # State machine definitions
│       ├── tools/                   # MCP tool implementations
│       ├── routing/                 # OpenRouter integration
│       └── server.py               # MCP server
├── config/                         # Configuration templates
├── docs/                          # Documentation
├── examples/                      # Usage examples
└── tests/                        # Test suite
```

## 🔧 **Configuration**

### Environment Variables
```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional  
NOTION_TOKEN=your_notion_integration_token
BMAD_MAX_DAILY_HOURS=10
BMAD_DEFAULT_AGENT=dev
BMAD_LOG_LEVEL=INFO
```

### Agent Configuration
Each agent can be customized via configuration files:

```yaml
# config/bmad-global-config.yaml
agents:
  dev:
    model: "anthropic/claude-3.5-sonnet"
    temperature: 0.1
    max_tokens: 4000
  architect:
    model: "anthropic/claude-3-opus"
    temperature: 0.3
    max_tokens: 8000
```

## 🐳 **Docker Deployment**

```bash
# Build and run with Docker Compose
docker-compose up -d

# Environment variables via .env file
cp .env.example .env
# Edit .env file with your API keys
docker-compose up -d
```

## 🧪 **Testing**

```bash
# Run test suite
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_task_management.py

# Run with coverage
python -m pytest --cov=src/bmad_mcp tests/
```

## 📚 **Documentation**

- **[BMAD Workflow System](BMAD_WORKFLOW_SYSTEM.md)** - Complete workflow implementation guide ⭐ NEW!
- **[API Reference](docs/api-reference.md)** - Complete tool documentation
- **[Agent Guide](docs/agent-guide.md)** - Working with specialized agents  
- **[Task Management](docs/task-management.md)** - Advanced task workflows
- **[Quality Gates Guide](docs/quality-gates.md)** - @qa commands and quality assurance ⭐ NEW!
- **[Serena Integration](SERENA_INTEGRATION.md)** - LSP-based code intelligence ⭐ NEW!
- **[Project Setup](docs/project-setup.md)** - BMAD project configuration
- **[Integration Guide](docs/integration-guide.md)** - IDE setup instructions
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📈 **Roadmap**

### ✅ **Recently Completed (v2.1)**
- [x] **BMAD-METHOD Workflow System**: Complete workflow implementation with intelligent orchestration
- [x] **Quality Gates System**: All 6 @qa commands (*risk, *design, *trace, *nfr, *review, *gate)
- [x] **Serena Bridge Agent**: LSP-based semantic code intelligence integration
- [x] **Agent Coordination**: 6-agent ecosystem with smart routing and collaboration
- [x] **Template-System**: 6 standardized project templates
- [x] **Auto-Discovery**: Automatic project detection and integration
- [x] **Migration Tools**: Legacy project migration to BMAD v2.0
- [x] **Standardized Structure**: Unified `.bmad-core/` project layout

### 🔄 **In Progress (v2.2)**
- [ ] **Workflow Automation**: Advanced automation rules and triggers
- [ ] **Multi-Project Workflows**: Cross-project dependency management
- [ ] **Enhanced Analytics**: Workflow performance insights and optimization
- [ ] **Custom Quality Gates**: User-definable quality criteria and checks

### 🚀 **Planned Features (v3.0)**
- [ ] **Web Dashboard**: Browser-based workflow management interface
- [ ] **Team Collaboration**: Multi-user project support with role-based access
- [ ] **Enterprise Workflows**: Advanced enterprise features and compliance
- [ ] **Serena Enhancements**: Multi-language LSP support and AI-assisted refactoring
- [ ] **Plugin System**: Custom agent and quality gate development
- [ ] **Mobile App**: Companion mobile application for workflow monitoring
- [ ] **Template Marketplace**: Community-driven template sharing platform

## 🔐 **Security**

- All API keys managed via environment variables
- No secrets stored in code or configuration files
- Secure MCP protocol communication
- Optional token rotation and audit logging

See [SECURITY.md](SECURITY.md) for security guidelines.

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 **Support**

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/bmad-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bmad-mcp-server/discussions)

## 🙏 **Acknowledgments**

- [Model Context Protocol](https://modelcontextprotocol.io) - For the excellent MCP specification
- [OpenRouter](https://openrouter.ai) - For multi-model API access
- [Notion](https://notion.so) - For database integration capabilities

---

**Made with ❤️ for developers who love intelligent task management**