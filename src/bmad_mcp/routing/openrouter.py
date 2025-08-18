"""
OpenRouter API Client for BMAD MCP Server
"""

import asyncio
import os
from typing import Dict, Any, Optional, List
import aiohttp
import json
import logging

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """OpenRouter API client for model routing"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Agent to model mapping based on existing BMAD system configuration
        self.agent_models = {
            "analyst": "perplexity/llama-3.1-sonar-large-128k-online",
            "architect": "anthropic/claude-3-opus", 
            "dev": "anthropic/claude-3.5-sonnet",
            "pm": "google/gemini-pro-1.5",
            "qa": "anthropic/claude-3-haiku"
        }
        
        # Agent-specific configuration from existing system
        self.agent_configs = {
            "analyst": {
                "temperature": 0.2,
                "max_tokens": 8000,
                "timeout": 90000,
                "headers": {
                    "HTTP-Referer": "https://bmad-Claude.local",
                    "X-Title": "BMAD Agent: analyst"
                }
            },
            "architect": {
                "temperature": 0.3,
                "max_tokens": 8000,
                "timeout": 120000,
                "headers": {
                    "HTTP-Referer": "https://bmad-Claude.local",
                    "X-Title": "BMAD Agent: architect"
                }
            },
            "dev": {
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 60000,
                "headers": {
                    "HTTP-Referer": "https://bmad-Claude.local",
                    "X-Title": "BMAD Agent: dev"
                }
            },
            "pm": {
                "temperature": 0.4,
                "max_tokens": 3000,
                "timeout": 45000,
                "headers": {
                    "HTTP-Referer": "https://bmad-Claude.local",
                    "X-Title": "BMAD Agent: pm"
                }
            },
            "qa": {
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 60000,
                "headers": {
                    "HTTP-Referer": "https://bmad-Claude.local",
                    "X-Title": "BMAD Agent: qa"
                }
            }
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/yourusername/bmad-mcp-server",
                "X-Title": "BMAD MCP Server"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def query_model(
        self,
        prompt: str,
        agent: str = "dev",
        context: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Query a model via OpenRouter"""
        
        if not self.api_key:
            return "❌ OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable."
        
        model = self.agent_models.get(agent, self.agent_models["dev"])
        
        # Get agent-specific configuration
        agent_config = self.agent_configs.get(agent, self.agent_configs["dev"])
        
        # Use agent-specific values or provided parameters
        final_max_tokens = max_tokens if max_tokens is not None else agent_config["max_tokens"]
        final_temperature = temperature if temperature is not None else agent_config["temperature"]
        
        try:
            # Create session with agent-specific headers
            if self.session is None or self.session.closed:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    **agent_config["headers"]
                }
                self.session = aiohttp.ClientSession(headers=headers)
            
            session = self.session
            
            # Prepare messages
            messages = []
            
            # Add context if provided
            if context:
                context_text = "\\n".join([f"{k}: {v}" for k, v in context.items()])
                messages.append({
                    "role": "system",
                    "content": f"Context:\\n{context_text}"
                })
            
            # Add main prompt
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            # Prepare request payload
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": final_max_tokens,
                "temperature": final_temperature,
                "stream": False
            }
            
            logger.info(f"Querying {model} for agent {agent}")
            
            async with session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    else:
                        return "❌ No response from model"
                        
                else:
                    error_text = await response.text()
                    logger.error(f"OpenRouter API error {response.status}: {error_text}")
                    return f"❌ API Error {response.status}: {error_text}"
                    
        except Exception as e:
            logger.error(f"Error querying OpenRouter: {str(e)}")
            return f"❌ Error: {str(e)}"
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        if not self.api_key:
            return []
        
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Error fetching models: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            return []
    
    def get_agent_model(self, agent: str) -> str:
        """Get model for specific agent"""
        return self.agent_models.get(agent, self.agent_models["dev"])
    
    async def test_connection(self) -> bool:
        """Test OpenRouter connection"""
        try:
            result = await self.query_model("Test connection", "dev", max_tokens=10)
            return not result.startswith("❌")
        except:
            return False