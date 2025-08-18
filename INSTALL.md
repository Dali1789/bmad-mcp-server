# BMAD MCP Server - Installation Guide

Complete installation guide for BMAD MCP Server across different platforms and IDEs.

## 📋 Prerequisites

### System Requirements
- **Python 3.8+** (Python 3.9+ recommended)
- **pip** package manager
- **Git** for repository cloning
- **IDE with MCP support** (Claude Code, VS Code, Cursor, etc.)

### API Keys Required
- **OpenRouter API Key** - For AI model access ([Get here](https://openrouter.ai))
- **Notion API Token** - Optional, for database sync ([Get here](https://developers.notion.com))

## 🚀 Quick Installation

### Option 1: Git Clone (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env file with your API keys
```

### Option 2: Direct Download
1. Download the latest release from GitHub
2. Extract to your preferred directory
3. Install dependencies: `pip install -r requirements.txt`
4. Configure environment variables

### Option 3: Docker Installation
```bash
# Clone and build with Docker
git clone https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server

# Build and run with Docker Compose
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

## 🔧 Environment Configuration

### Required Environment Variables
Create a `.env` file in the project root:

```bash
# Required: OpenRouter API key for model access
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Notion integration
NOTION_TOKEN=your_notion_integration_token

# Optional: Configuration
BMAD_MAX_DAILY_HOURS=10
BMAD_DEFAULT_AGENT=dev
BMAD_LOG_LEVEL=INFO
PYTHONPATH=/path/to/bmad-mcp-server
```

### Getting API Keys

#### OpenRouter API Key
1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up or log in
3. Go to "Keys" section
4. Create a new API key
5. Copy the key to your `.env` file

#### Notion API Token (Optional)
1. Visit [Notion Developers](https://developers.notion.com)
2. Create a new integration
3. Copy the integration token
4. Add to your `.env` file
5. Share relevant databases with your integration

## 🖥️ IDE Configuration

### Claude Code

#### Method 1: claude_desktop_config.json
Edit your Claude Desktop configuration file:

**Location:**
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "bmad": {
      "command": "python",
      "args": ["-m", "src.bmad_mcp.server"],
      "cwd": "/absolute/path/to/bmad-mcp-server",
      "env": {
        "PYTHONPATH": "/absolute/path/to/bmad-mcp-server",
        "OPENROUTER_API_KEY": "your_openrouter_api_key",
        "NOTION_TOKEN": "your_notion_token"
      }
    }
  }
}
```

#### Method 2: Environment Variables
Set system environment variables and use simpler config:
```json
{
  "mcpServers": {
    "bmad": {
      "command": "python",
      "args": ["-m", "src.bmad_mcp.server"],
      "cwd": "/absolute/path/to/bmad-mcp-server"
    }
  }
}
```

### VS Code

#### Prerequisites
Install MCP extension for VS Code (if available) or configure manually.

#### Configuration
Add to VS Code settings or workspace configuration:
```json
{
  "mcp.servers": {
    "bmad": {
      "command": "python",
      "args": ["-m", "src.bmad_mcp.server"],
      "cwd": "/absolute/path/to/bmad-mcp-server",
      "env": {
        "PYTHONPATH": "/absolute/path/to/bmad-mcp-server",
        "OPENROUTER_API_KEY": "your_api_key",
        "NOTION_TOKEN": "your_notion_token"
      }
    }
  }
}
```

### Cursor

Cursor uses similar configuration to VS Code:
```json
{
  "mcp.servers": {
    "bmad": {
      "command": "python",
      "args": ["-m", "src.bmad_mcp.server"],
      "cwd": "/absolute/path/to/bmad-mcp-server",
      "env": {
        "PYTHONPATH": "/absolute/path/to/bmad-mcp-server",
        "OPENROUTER_API_KEY": "your_api_key"
      }
    }
  }
}
```

### Other MCP-Compatible IDEs

For other IDEs supporting MCP, use the standard MCP server configuration format:
```json
{
  "servers": {
    "bmad": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src.bmad_mcp.server"],
      "cwd": "/absolute/path/to/bmad-mcp-server",
      "env": {
        "PYTHONPATH": "/absolute/path/to/bmad-mcp-server",
        "OPENROUTER_API_KEY": "your_api_key"
      }
    }
  }
}
```

## ✅ Verification

### 1. Test Python Installation
```bash
cd /path/to/bmad-mcp-server
python -m src.bmad_mcp.server --test
```

### 2. Verify MCP Tools Availability
In your IDE, try using:
```
bmad_list_agents
```

### 3. Test Agent Activation
```
bmad_activate_agent(agent="dev")
```

### 4. Verify OpenRouter Connection
```
bmad_query_with_model(query="Test connection", agent="dev")
```

## 🔧 Troubleshooting

### Common Issues

#### "Module not found" Error
**Problem**: Python can't find the BMAD modules
**Solution**: 
- Ensure `PYTHONPATH` is set correctly in configuration
- Use absolute paths in configuration
- Verify Python environment has required packages

#### "OPENROUTER_API_KEY not set" Warning
**Problem**: API key not configured
**Solution**:
- Check `.env` file exists and contains the key
- Verify environment variables in IDE configuration
- Test key validity at OpenRouter.ai

#### MCP Server Not Loading
**Problem**: IDE can't connect to MCP server
**Solution**:
- Check Python path in configuration
- Verify all dependencies installed: `pip install -r requirements.txt`
- Test server startup manually: `python -m src.bmad_mcp.server`
- Check IDE MCP configuration syntax

#### Permission Errors
**Problem**: Permission denied accessing files/directories
**Solution**:
- Ensure write permissions for task storage directory
- Check Python execution permissions
- Verify IDE has access to specified directories

### Debug Mode

Enable debug logging by setting:
```bash
BMAD_LOG_LEVEL=DEBUG
```

Or run server with debug output:
```bash
python -m src.bmad_mcp.server --debug
```

### Log Locations

Check IDE-specific MCP logs:
- **Claude Code**: `%APPDATA%\Claude\logs\mcp-server-bmad.log`
- **VS Code**: Check VS Code developer console
- **Manual**: Server outputs to stdout/stderr

## 🌐 Platform-Specific Instructions

### Windows

#### PowerShell Installation
```powershell
# Clone repository
git clone https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server

# Install dependencies
pip install -r requirements.txt

# Set environment variable
$env:OPENROUTER_API_KEY="your_api_key_here"

# Test installation
python -m src.bmad_mcp.server --test
```

#### Windows Path Example
```json
{
  "cwd": "C:\\Users\\YourName\\bmad-mcp-server",
  "env": {
    "PYTHONPATH": "C:\\Users\\YourName\\bmad-mcp-server"
  }
}
```

### macOS

#### Using Homebrew
```bash
# Install Python if needed
brew install python

# Clone and setup
git clone https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server
pip3 install -r requirements.txt

# Set environment variable
export OPENROUTER_API_KEY="your_api_key_here"
```

#### macOS Path Example
```json
{
  "cwd": "/Users/YourName/bmad-mcp-server",
  "env": {
    "PYTHONPATH": "/Users/YourName/bmad-mcp-server"
  }
}
```

### Linux

#### Ubuntu/Debian
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip git

# Clone and setup
git clone https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server
pip3 install -r requirements.txt

# Set environment variable
export OPENROUTER_API_KEY="your_api_key_here"
```

#### Linux Path Example
```json
{
  "cwd": "/home/yourname/bmad-mcp-server",
  "env": {
    "PYTHONPATH": "/home/yourname/bmad-mcp-server"
  }
}
```

## 🐳 Docker Installation

### Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Build and run
docker-compose up -d

# Check status
docker-compose ps
```

### Manual Docker Build

```bash
# Build image
docker build -t bmad-mcp-server .

# Run container
docker run -d \
  --name bmad-mcp \
  -e OPENROUTER_API_KEY=your_key \
  -e NOTION_TOKEN=your_token \
  -p 8080:8080 \
  bmad-mcp-server
```

### Docker Configuration for IDE

When using Docker, configure IDE to connect to container:
```json
{
  "mcpServers": {
    "bmad": {
      "command": "docker",
      "args": ["exec", "bmad-mcp", "python", "-m", "src.bmad_mcp.server"],
      "env": {
        "OPENROUTER_API_KEY": "your_api_key"
      }
    }
  }
}
```

## 📦 Development Installation

For development and contributing:

```bash
# Clone with development branch
git clone -b develop https://github.com/yourusername/bmad-mcp-server.git
cd bmad-mcp-server

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/

# Run in development mode
python -m src.bmad_mcp.server --dev
```

## 🔄 Updating

### Git Update
```bash
cd bmad-mcp-server
git pull origin main
pip install -r requirements.txt
```

### Docker Update
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

## 🆘 Getting Help

If you encounter issues during installation:

1. **Check Requirements**: Verify Python version and dependencies
2. **Review Logs**: Check IDE MCP logs for error details
3. **Test Components**: Test server startup and API connectivity separately
4. **Documentation**: Review [troubleshooting guide](docs/troubleshooting.md)
5. **Community Support**: Open an issue on GitHub with:
   - Operating system and Python version
   - IDE and version
   - Complete error messages
   - Configuration files (remove API keys)

## ✨ Next Steps

After successful installation:

1. **Read the [API Reference](docs/api-reference.md)** for complete tool documentation
2. **Try the [Getting Started Example](examples/getting-started.py)** for basic usage
3. **Explore [Real-World Project Example](examples/real-world-project.py)** for advanced workflows
4. **Configure [Project Setup](docs/project-setup.md)** for your specific projects
5. **Join the [Community Discussions](https://github.com/yourusername/bmad-mcp-server/discussions)** for tips and support

---

**Installation complete! Start building intelligent task management workflows with BMAD.** 🚀