"""
BMAD Agent Manager - Orchestrates all BMAD agents
"""

from typing import Dict, Optional, List
from .analyst import AnalystAgent
from .architect import ArchitectAgent
from .developer import DeveloperAgent
from .pm import ProjectManagerAgent
from .qa import QAAgent
from .base_agent import BaseAgent


class AgentManager:
    """Manages all BMAD agents and routing"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {
            "analyst": AnalystAgent(),
            "architect": ArchitectAgent(),
            "dev": DeveloperAgent(),
            "pm": ProjectManagerAgent(), 
            "qa": QAAgent()
        }
        self.current_agent: Optional[str] = None
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, str]]:
        """List all available agents"""
        return [
            {
                "id": agent_id,
                "name": agent.config.name,
                "title": agent.config.title,
                "icon": agent.config.icon,
                "whenToUse": agent.config.whenToUse,
                "model": agent.config.model
            }
            for agent_id, agent in self.agents.items()
        ]
    
    async def activate_agent(self, agent_id: str) -> str:
        """Activate specific agent"""
        if agent_id not in self.agents:
            available = ", ".join(self.agents.keys())
            return f"❌ Unknown agent: {agent_id}. Available agents: {available}"
        
        self.current_agent = agent_id
        agent = self.agents[agent_id]
        return await agent.activate()
    
    async def get_agent_help(self, agent_id: Optional[str] = None) -> str:
        """Get help for agent"""
        target_agent = agent_id or self.current_agent
        
        if not target_agent:
            return "❌ No agent specified and no current agent active. Use bmad_activate_agent first."
        
        if target_agent not in self.agents:
            available = ", ".join(self.agents.keys()) 
            return f"❌ Unknown agent: {target_agent}. Available agents: {available}"
        
        agent = self.agents[target_agent]
        return await agent.get_help()
    
    def get_current_agent(self) -> Optional[BaseAgent]:
        """Get currently active agent"""
        if self.current_agent:
            return self.agents.get(self.current_agent)
        return None
    
    def get_agent_model(self, agent_id: str) -> Optional[str]:
        """Get model for specific agent"""
        agent = self.get_agent(agent_id)
        return agent.config.model if agent else None