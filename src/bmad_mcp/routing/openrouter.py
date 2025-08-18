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
        
        # Agent to model mapping
        self.agent_models = {
            "analyst": "perplexity/llama-3.1-sonar-large-128k-online",
            "architect": "anthropic/claude-3-opus", 
            "dev": "anthropic/claude-3.5-sonnet",
            "pm": "google/gemini-pro-1.5",
            "qa": "anthropic/claude-3-haiku"
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
        max_tokens: int = 4000,
        temperature: float = 0.1
    ) -> str:
        """Query a model via OpenRouter"""
        
        if not self.api_key:
            return "❌ OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable."
        
        model = self.agent_models.get(agent, self.agent_models["dev"])
        
        try:
            session = await self._get_session()
            
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
                "max_tokens": max_tokens,
                "temperature": temperature,
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