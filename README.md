# BMAD MCP Server

A Model Context Protocol (MCP) server implementation for the BMAD (Business Modeling and Development) methodology.

## Features

- **Agent System**: Currently implements 2 specialized agents:
  - 📊 **Mary (Analyst)**: Business analysis, market research, brainstorming
  - 🏗️ **Winston (Architect)**: System design, architecture, technology selection

- **MCP Tools**: Full set of BMAD tools accessible through MCP protocol
- **Global Registry**: Cross-IDE project management
- **OpenRouter Integration**: Intelligent model routing based on agent context

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Dali1789/bmad-mcp-server.git
cd bmad-mcp-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Configuration

Add to your MCP configuration file (e.g., `.kilocode/mcp.json` for Claude):

```json
{
  "mcpServers": {
    "bmad": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "src.bmad_mcp.server"
      ],
      "cwd": "path/to/bmad-mcp-server",
      "env": {
        "PYTHONPATH": "path/to/bmad-mcp-server",
        "OPENROUTER_API_KEY": "your_api_key"
      }
    }
  }
}
```

## Usage

Once configured, the following MCP tools are available:

- `bmad_list_agents` - List all available BMAD agents
- `bmad_activate_agent` - Activate a specific agent (analyst, architect)
- `bmad_get_agent_help` - Get help for current/specified agent
- `bmad_detect_project` - Scan for .bmad-core configuration
- `bmad_execute_task` - Execute BMAD tasks
- `bmad_create_document` - Create documents using templates
- `bmad_run_checklist` - Run quality checklists
- `bmad_query_with_model` - Query using agent-specific models
- `bmad_register_project` - Register project in global registry
- `bmad_set_active_project` - Set active project
- `bmad_list_projects` - List all registered projects
- `bmad_get_registry_info` - Get registry information

## Development Status

- ✅ Core MCP server implementation
- ✅ Analyst and Architect agents
- ✅ Global project registry
- ⏳ Developer agent (planned)
- ⏳ Project Manager agent (planned)
- ⏳ QA agent (planned)

## Requirements

- Python 3.8+
- MCP 1.13.0+
- OpenRouter API key (for model routing)

## Troubleshooting

If you encounter connection issues:

1. Ensure the server is configured as `stdio` type (not `remote`)
2. Check that Python path is correctly set in the configuration
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Check the `.env` file contains valid API keys

## License

[Add your license here]