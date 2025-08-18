"""
Base Agent Class for BMAD MCP Server
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Agent configuration model"""
    name: str
    id: str
    title: str
    icon: str
    whenToUse: str
    model: str
    temperature: float = 0.1
    max_tokens: int = 4000
    customization: Optional[str] = None


class AgentPersona(BaseModel):
    """Agent persona model"""
    role: str
    style: str
    identity: str
    focus: str
    core_principles: List[str]


class BaseAgent(ABC):
    """Base class for all BMAD agents"""
    
    def __init__(self, config: AgentConfig, persona: AgentPersona):
        self.config = config
        self.persona = persona
        self.commands = self._get_commands()
        self.dependencies = self._get_dependencies()
    
    @abstractmethod
    def _get_commands(self) -> Dict[str, str]:
        """Get agent-specific commands"""
        pass
    
    @abstractmethod  
    def _get_dependencies(self) -> Dict[str, List[str]]:
        """Get agent dependencies (tasks, templates, etc.)"""
        pass
    
    @abstractmethod
    async def activate(self) -> str:
        """Activate the agent and return greeting"""
        pass
    
    async def get_help(self) -> str:
        """Get agent help information"""
        help_text = f"""
🎭 **{self.config.title} ({self.config.name})**
{self.config.icon} *{self.persona.role}*

**When to Use**: {self.config.whenToUse}

**Style**: {self.persona.style}
**Focus**: {self.persona.focus}

**Available Commands**:
"""
        for i, (cmd, desc) in enumerate(self.commands.items(), 1):
            help_text += f"\n{i}. `*{cmd}`: {desc}"
        
        help_text += f"\n\n**Model**: {self.config.model}"
        help_text += f"\n**Core Principles**:"
        for principle in self.persona.core_principles:
            help_text += f"\n- {principle}"
            
        return help_text
    
    async def execute_command(self, command: str, parameters: Dict[str, Any]) -> str:
        """Execute agent-specific command"""
        if command not in self.commands:
            return f"Unknown command: {command}. Use *help to see available commands."
        
        # Command execution logic would be implemented here
        # This would integrate with the BMAD task system
        return f"Executing {command} with parameters: {parameters}"
    
    def get_activation_prompt(self) -> str:
        """Get the agent activation prompt"""
        return f"""
# /{self.config.id} Command

When this command is used, adopt the following agent persona:

# {self.config.id}

ACTIVATION-NOTICE: This file contains your full agent operating guidelines.

## COMPLETE AGENT DEFINITION

```yaml
agent:
  name: {self.config.name}
  id: {self.config.id}
  title: {self.config.title}
  icon: {self.config.icon}
  whenToUse: {self.config.whenToUse}
  model: {self.config.model}
  temperature: {self.config.temperature}
  customization: {self.config.customization}

persona:
  role: {self.persona.role}
  style: {self.persona.style}
  identity: {self.persona.identity}
  focus: {self.persona.focus}
  core_principles:
{chr(10).join(f'    - {principle}' for principle in self.persona.core_principles)}

commands:
{chr(10).join(f'  - {cmd}: {desc}' for cmd, desc in self.commands.items())}

dependencies:
{chr(10).join(f'  {category}:' + chr(10) + chr(10).join(f'    - {item}' for item in items) for category, items in self.dependencies.items())}
```

**Activation Instructions**:
1. Read this complete agent definition
2. Adopt the persona defined above
3. Greet user with your name/role and mention `*help` command
4. Stay in character and await user commands
"""