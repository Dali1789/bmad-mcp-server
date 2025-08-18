# BMAD MCP Server 🚀

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive **Model Context Protocol (MCP) server** implementing the **BMAD (Business Modeling and Development)** methodology. Provides intelligent task management, multi-agent workflows, and cross-IDE project management through the MCP protocol.

## ✨ Features

### 🤖 **5 Specialized AI Agents**
- **📊 Analyst**: Business analysis, market research, requirement gathering
- **🏗️ Architect**: System design, architecture planning, tech stack selection  
- **💻 Developer**: Code implementation, debugging, technical development
- **📋 Project Manager**: Task coordination, timeline management, resource planning
- **🔍 QA**: Quality assurance, testing strategies, code review

### 📋 **Advanced Task Management**
- **Real-time Progress Tracking**: Live updates and notifications
- **Intelligent Scheduling**: Auto-allocation with capacity management
- **Follow-up Task Generation**: Automatic workflow progression
- **Notion Integration**: Bi-directional sync with Notion databases
- **TodoWrite Bridge**: Seamless Claude integration

### 🔄 **Enhanced Features**
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
│       │   └── qa.py               # Quality assurance
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

- **[API Reference](docs/api-reference.md)** - Complete tool documentation
- **[Agent Guide](docs/agent-guide.md)** - Working with specialized agents  
- **[Task Management](docs/task-management.md)** - Advanced task workflows
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

- [ ] **Web Dashboard**: Browser-based task management interface
- [ ] **Team Collaboration**: Multi-user project support  
- [ ] **Advanced Analytics**: Performance insights and reporting
- [ ] **Plugin System**: Custom agent and tool development
- [ ] **Mobile App**: Companion mobile application
- [ ] **Enterprise Features**: SSO, audit logs, advanced security

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