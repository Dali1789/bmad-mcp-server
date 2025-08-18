# BMAD MCP Server

🏗️ **Breakthrough Method for Agile AI-driven Development - MCP Server**

Advanced agent routing with OpenRouter integration for multi-model AI development workflows.

## Overview

The BMAD MCP Server exposes the complete BMAD methodology through the Model Context Protocol, enabling any MCP-compatible IDE (Kilo Code, Claude Code, etc.) to leverage intelligent agent routing and specialized AI models for different development tasks.

## Features

### 🤖 **Intelligent Agent Routing**
- **Analyst (Mary)**: Market research, brainstorming, competitive analysis
- **Architect (Winston)**: System design, architecture documents, technical planning  
- **Developer**: Implementation, coding standards, technical execution
- **Project Manager**: Story management, project planning, validation
- **QA**: Quality assurance, testing, validation checklists

### 🔄 **Multi-Model Intelligence**
- **OpenRouter Integration**: Automatic model selection per agent type
- **Perplexity**: Real-time research and analysis (Analyst)
- **Claude Opus**: Complex reasoning and architecture (Architect)
- **Claude Sonnet**: Development and implementation (Developer)
- **Gemini Pro**: Project management and coordination (PM)
- **Claude Haiku**: Quick validation and QA (QA)

### 📁 **Project-Aware Context**
- **Automatic .bmad-core detection**: Project-specific configurations
- **Template System**: 47+ pre-built templates and workflows
- **Task Automation**: Structured BMAD methodology execution
- **Document Generation**: Automated PRDs, architectures, stories

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server

# Install dependencies
pip install -r requirements.txt

# Configure OpenRouter API
export OPENROUTER_API_KEY="your-api-key-here"

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

#### Claude Code
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

## Available Tools

### Agent Management
- `bmad_activate_agent`: Switch to specific agent (analyst, architect, dev, pm, qa)
- `bmad_list_agents`: Show available agents and capabilities
- `bmad_get_agent_help`: Get agent-specific commands

### Project Operations  
- `bmad_detect_project`: Scan for .bmad-core configuration
- `bmad_load_templates`: Access project templates
- `bmad_execute_task`: Run BMAD tasks with agent context

### Document Generation
- `bmad_create_document`: Generate docs using templates
- `bmad_validate_document`: Run quality checklists
- `bmad_shard_document`: Split large documents

### Workflow Management
- `bmad_create_story`: Generate user stories
- `bmad_validate_story`: Check story completion
- `bmad_run_checklist`: Execute BMAD checklists

## Architecture

```
BMAD MCP Server
├── Agent Router (5 specialized agents)
├── OpenRouter Integration (multi-model routing)
├── Project Detection (.bmad-core scanning)
├── Template Engine (47+ workflows)
├── MCP Protocol Layer (standard tools/resources)
└── Context Management (project-aware sessions)
```

## Configuration

### OpenRouter Models
```yaml
agents:
  analyst: "perplexity/llama-3.1-sonar-large-128k-online"
  architect: "anthropic/claude-3-opus"
  dev: "anthropic/claude-3.5-sonnet"
  pm: "google/gemini-pro-1.5"
  qa: "anthropic/claude-3-haiku"
```

### BMAD Core Structure
```
.bmad-core/
├── agents/          # Agent definitions
├── tasks/           # Executable workflows
├── templates/       # Document templates
├── checklists/      # Quality validation
├── workflows/       # Process definitions
└── core-config.yaml # Project configuration
```

## Deployment

### Docker
```bash
docker build -t bmad-mcp-server .
docker run -p 3000:3000 -e OPENROUTER_API_KEY=your-key bmad-mcp-server
```

### Cloud Deployment
See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed cloud deployment instructions.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/yourusername/bmad-mcp-server/issues)
- 💬 [Discussions](https://github.com/yourusername/bmad-mcp-server/discussions)