# Contributing to BMAD MCP Server

Thank you for your interest in contributing to BMAD MCP Server! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions Welcome

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new features and improvements
- **📖 Documentation**: Improve docs, examples, and guides
- **🔧 Code Contributions**: Implement features, fix bugs, optimize performance
- **🧪 Testing**: Add tests, improve test coverage
- **🎨 UI/UX**: Improve user experience and interface design
- **🌐 Localization**: Add support for additional languages

## 🚀 Getting Started

### 1. Fork the Repository
```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/your-username/bmad-mcp-server.git
cd bmad-mcp-server

# Add upstream remote
git remote add upstream https://github.com/original-owner/bmad-mcp-server.git
```

### 2. Set Up Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Create a .env file for development
cp .env.example .env
# Add your API keys for testing
```

### 3. Create a Feature Branch
```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

## 📋 Development Guidelines

### Code Style

We follow Python best practices and PEP 8:

- **Formatting**: Use `black` for code formatting
- **Linting**: Use `flake8` for linting
- **Type Hints**: Include type hints for all functions
- **Docstrings**: Use Google-style docstrings

```python
def example_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """Example function with proper documentation.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with default value
        
    Returns:
        Dictionary containing the result
        
    Raises:
        ValueError: When param1 is empty
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    return {"result": f"{param1}_{param2}"}
```

### Git Commit Messages

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Add real-time task monitoring feature"
git commit -m "Fix: Resolve import error in core module"
git commit -m "Docs: Update API reference for new tools"
git commit -m "Test: Add unit tests for task tracker"

# Format: <type>: <description>
# Types: feat, fix, docs, test, refactor, style, chore
```

### Branch Naming

Use descriptive branch names:
- `feature/agent-collaboration-system`
- `fix/notion-sync-timeout-issue`
- `docs/improved-installation-guide`
- `test/task-management-coverage`

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src/bmad_mcp

# Run specific test file
python -m pytest tests/test_task_management.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

Create comprehensive tests for new features:

```python
import pytest
from src.bmad_mcp.core.task_tracker import BMadTaskTracker, BMadTask

class TestTaskTracker:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.tracker = BMadTaskTracker()
    
    def test_create_task(self):
        """Test task creation functionality."""
        task = self.tracker.create_task(
            task_id="test-task",
            name="Test Task",
            allocated_hours=8.0,
            agent="dev"
        )
        
        assert task.id == "test-task"
        assert task.name == "Test Task"
        assert task.allocated_hours == 8.0
        assert task.status == "pending"
    
    def test_update_task_progress(self):
        """Test task progress updates."""
        # Create task first
        task = self.tracker.create_task("test", "Test", 10.0)
        
        # Update progress
        updated_task = self.tracker.update_task_progress("test", 3.0)
        
        assert updated_task.completed_hours == 3.0
        assert updated_task.status == "in_progress"
    
    @pytest.mark.parametrize("hours,expected_status", [
        (5.0, "in_progress"),
        (10.0, "completed"),
        (15.0, "completed")
    ])
    def test_task_status_transitions(self, hours, expected_status):
        """Test task status transitions based on progress."""
        task = self.tracker.create_task("test", "Test", 10.0)
        updated_task = self.tracker.update_task_progress("test", hours)
        assert updated_task.status == expected_status
```

## 📁 Project Structure

Understanding the codebase structure:

```
bmad-mcp-server/
├── src/
│   └── bmad_mcp/
│       ├── core/              # Core functionality
│       │   ├── task_tracker.py
│       │   ├── realtime_updater.py
│       │   └── ...
│       ├── agents/            # Agent implementations  
│       ├── tools/             # MCP tool implementations
│       ├── routing/           # Model routing logic
│       └── server.py          # Main MCP server
├── tests/                     # Test suite
├── docs/                      # Documentation
├── examples/                  # Usage examples
├── config/                    # Configuration templates
└── requirements*.txt          # Dependencies
```

### Adding New Features

#### 1. Core Functionality
For core features (task management, monitoring, etc.):
- Add implementation to `src/bmad_mcp/core/`
- Create comprehensive unit tests
- Update relevant documentation

#### 2. New MCP Tools
For new MCP tools:
- Add implementation to `src/bmad_mcp/tools/bmad_tools.py`
- Register in `src/bmad_mcp/server.py`
- Add to API documentation
- Include usage examples

#### 3. New Agents
For new agent types:
- Create agent definition in `src/bmad_mcp/agents/`
- Add to agent manager configuration
- Include agent-specific documentation
- Add example workflows

## 🔍 Code Review Process

### Before Submitting a PR

1. **Self-Review Checklist**:
   - [ ] Code follows style guidelines
   - [ ] All tests pass locally
   - [ ] New features have tests
   - [ ] Documentation is updated
   - [ ] No sensitive data in commits
   - [ ] Commit messages are clear

2. **Pre-commit Checks**:
   ```bash
   # Format code
   black src/ tests/
   
   # Check linting
   flake8 src/ tests/
   
   # Run tests
   python -m pytest
   
   # Check types
   mypy src/
   ```

### Pull Request Guidelines

Create detailed pull requests:

```markdown
## Summary
Brief description of changes and motivation.

## Changes Made
- List of specific changes
- New features added
- Bugs fixed
- Documentation updates

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Breaking Changes
List any breaking changes and migration notes.

## Screenshots/Examples
Include examples of new functionality.
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Code Review**: Maintainers review code quality and design
3. **Testing**: Reviewers test functionality
4. **Documentation**: Verify documentation is complete and accurate
5. **Approval**: Maintainer approval required for merge

## 🐛 Bug Reports

### Before Reporting
1. **Search Existing Issues**: Check if the bug is already reported
2. **Try Latest Version**: Ensure you're using the latest version
3. **Minimal Reproduction**: Create a minimal example that reproduces the issue

### Bug Report Template
```markdown
**Bug Description**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots/Logs**
If applicable, add screenshots or error logs.

**Environment:**
- OS: [e.g. Windows 11, macOS Monterey, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- BMAD Version: [e.g. 1.2.3]
- IDE: [e.g. Claude Code, VS Code]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the feature you'd like to see.

**Problem/Motivation**
What problem does this solve? Why is this feature needed?

**Proposed Solution**
Describe your preferred solution.

**Alternatives Considered**
Alternative solutions or features you've considered.

**Implementation Ideas**
If you have ideas about implementation approach.

**Additional Context**
Screenshots, mockups, or examples that help explain the feature.
```

## 📖 Documentation

### Documentation Standards

- **Clear and Concise**: Write for your audience
- **Examples**: Include practical examples
- **Up-to-Date**: Keep docs synchronized with code
- **Accessible**: Use inclusive language

### Types of Documentation

1. **API Reference**: Complete function/tool documentation
2. **Guides**: Step-by-step tutorials and how-tos
3. **Examples**: Real-world usage examples
4. **Architecture**: System design and technical details

### Documentation Workflow
```bash
# Make documentation changes
git checkout -b docs/improve-api-reference

# Edit relevant files in docs/ or README
# Add examples to examples/

# Test documentation
# Ensure links work and examples are correct

# Commit and push
git commit -m "docs: Improve API reference with more examples"
git push origin docs/improve-api-reference
```

## 🔐 Security

### Security Guidelines

- **No Secrets in Code**: Never commit API keys, passwords, or tokens
- **Environment Variables**: Use environment variables for sensitive data
- **Input Validation**: Validate all user inputs
- **Error Handling**: Don't expose sensitive information in error messages

### Reporting Security Issues

For security vulnerabilities:
1. **Don't create public issues**
2. **Email maintainers directly**: security@bmad-project.com
3. **Include detailed description** and reproduction steps
4. **Allow time for fix** before public disclosure

## 🏆 Recognition

### Contributors

We recognize contributions in several ways:
- **Contributors List**: Listed in README and repository
- **Release Notes**: Major contributions highlighted
- **Special Thanks**: Recognition for exceptional contributions

### Types of Recognition

- **Code Contributors**: Feature development, bug fixes
- **Documentation Contributors**: Docs, examples, guides
- **Community Contributors**: Issue triage, user support
- **Testing Contributors**: Test coverage, quality assurance

## 📞 Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community interaction
- **Documentation**: Check docs/ for guides and references

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be Respectful**: Treat all community members with respect
- **Be Collaborative**: Work together towards common goals
- **Be Inclusive**: Welcome people of all backgrounds and skill levels
- **Be Professional**: Maintain professional communication

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community chat
- **Pull Requests**: Code review and collaboration

## 🎯 Development Roadmap

### Current Priorities

1. **Core Stability**: Bug fixes and performance improvements
2. **Enhanced Agents**: Additional specialized agents
3. **Advanced Features**: Team collaboration, advanced analytics
4. **Documentation**: Comprehensive guides and examples
5. **Testing**: Improved test coverage and quality

### Future Plans

- **Web Dashboard**: Browser-based interface
- **Mobile App**: Companion mobile application
- **Enterprise Features**: SSO, audit logs, advanced security
- **Plugin System**: Extensible architecture for custom tools

## 📋 Release Process

### Version Numbers

We use [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 2.1.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Release Workflow

1. **Development**: Features developed in feature branches
2. **Testing**: Comprehensive testing on develop branch
3. **Release Candidate**: RC testing with community
4. **Release**: Tagged release with changelog
5. **Documentation**: Updated docs and examples

## 🙏 Thank You

Thank you for contributing to BMAD MCP Server! Your contributions help make intelligent task management accessible to developers worldwide.

### Questions?

If you have questions about contributing:
1. Check existing documentation
2. Search GitHub discussions
3. Create a new discussion
4. Reach out to maintainers

---

**Happy coding! 🚀**