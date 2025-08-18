"""
BMAD Serena Agent Wrapper
Wraps the Serena Bridge Agent to work with the standard BMAD Agent interface
"""

from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentConfig, AgentPersona
from .serena_bridge import BMadSerenaAgent


class SerenaAgentWrapper(BaseAgent):
    """Wrapper to integrate Serena Bridge Agent with BMAD Agent Manager"""
    
    def __init__(self):
        # Initialize with Serena-specific configuration
        config = AgentConfig(
            id="serena",
            name="serena",
            title="Serena Bridge Agent",
            icon="🔍",
            model="serena-lsp",
            temperature=0.1,
            max_tokens=4000,
            whenToUse="Semantic code analysis, symbol finding, code intelligence, LSP operations"
        )
        
        # Initialize Serena-specific persona
        persona = AgentPersona(
            role="Semantic Code Intelligence Specialist",
            style="Professional, precise, technical",
            identity="LSP-powered code analysis expert",
            focus="Semantic understanding, symbol management, precise code modification",
            core_principles=[
                "Use semantic analysis over regex-based pattern matching",
                "Provide precise symbol location and reference information",
                "Leverage LSP capabilities for accurate code intelligence",
                "Initialize projects before analysis for optimal results",
                "Focus on code structure and relationships understanding"
            ]
        )
        
        super().__init__(config, persona)
        
        # Create the actual Serena Bridge Agent instance
        self.serena_bridge = BMadSerenaAgent()
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process query using Serena Bridge Agent capabilities"""
        try:
            # For agent queries, provide guidance on Serena usage
            if any(keyword in query.lower() for keyword in ['help', 'what', 'how', 'guide']):
                return self._get_serena_usage_guide()
            
            # For technical queries, suggest appropriate Serena tools
            return self._suggest_serena_tools(query)
            
        except Exception as e:
            return f"❌ Serena Agent Error: {str(e)}"
    
    def _get_serena_usage_guide(self) -> str:
        """Return Serena usage guide"""
        return """
🔍 **Serena Bridge Agent - Semantic Code Intelligence**

**Primary Capabilities:**
• **LSP Integration**: Professional semantic code analysis
• **Symbol Finding**: Locate functions, classes, variables semantically  
• **Reference Tracking**: Follow symbol usage across entire codebase
• **Precision Editing**: Exact code modifications with full context
• **Project Analysis**: Comprehensive codebase understanding

**Essential Tools:**
1. `bmad_serena_initialize` - Start Serena MCP server
2. `bmad_serena_activate_project` - Load project for analysis
3. `bmad_serena_find_symbol` - Find code symbols semantically
4. `bmad_serena_onboarding` - Comprehensive project analysis

**Workflow:**
1. Initialize Serena: `bmad_serena_initialize`
2. Activate project: `bmad_serena_activate_project`
3. Use analysis tools as needed
4. Store insights: `bmad_serena_write_memory`

**Best For:**
• Code refactoring and modification
• Symbol dependency analysis  
• Large codebase navigation
• Semantic code search
• Architecture understanding
"""
    
    def _suggest_serena_tools(self, query: str) -> str:
        """Suggest appropriate Serena tools based on query"""
        query_lower = query.lower()
        
        suggestions = []
        
        if any(word in query_lower for word in ['find', 'search', 'locate', 'symbol']):
            suggestions.append("• `bmad_serena_find_symbol` - Find code symbols semantically")
            suggestions.append("• `bmad_serena_search_for_pattern` - Advanced pattern search")
        
        if any(word in query_lower for word in ['analyze', 'overview', 'structure']):
            suggestions.append("• `bmad_serena_get_symbols_overview` - File symbol overview") 
            suggestions.append("• `bmad_serena_onboarding` - Project analysis")
        
        if any(word in query_lower for word in ['reference', 'usage', 'where']):
            suggestions.append("• `bmad_serena_find_referencing_symbols` - Find symbol references")
        
        if any(word in query_lower for word in ['edit', 'modify', 'change', 'update']):
            suggestions.append("• `bmad_serena_insert_after_symbol` - Insert code after symbol")
            suggestions.append("• `bmad_serena_replace_symbol_body` - Replace symbol implementation")
        
        if any(word in query_lower for word in ['project', 'initialize', 'setup']):
            suggestions.append("• `bmad_serena_initialize` - Initialize Serena")
            suggestions.append("• `bmad_serena_activate_project` - Activate project")
        
        if suggestions:
            result = f"🔍 **Suggested Serena Tools for: '{query}'**\n\n"
            result += "\n".join(suggestions)
            result += "\n\n💡 **Tip**: Initialize Serena first with `bmad_serena_initialize`"
            return result
        else:
            return """
🔍 **Serena Bridge Agent Ready**

For semantic code analysis, I recommend starting with:
1. `bmad_serena_initialize` - Initialize the Serena MCP server
2. `bmad_serena_activate_project` - Load your project for analysis
3. Use specific tools based on your needs

Use `bmad_get_agent_help` for more detailed guidance!
"""
    
    def get_status(self) -> Dict[str, Any]:
        """Get Serena agent status via bridge"""
        return self.serena_bridge.get_status()
    
    def _get_commands(self) -> Dict[str, str]:
        """Get available commands for Serena agent"""
        return {
            "initialize": "Initialize Serena MCP server",
            "activate-project": "Activate project for analysis", 
            "find-symbol": "Find code symbols semantically",
            "analyze-file": "Get symbol overview of file",
            "search-pattern": "Advanced pattern search",
            "onboarding": "Comprehensive project analysis"
        }
    
    def _get_dependencies(self) -> Dict[str, List[str]]:
        """Get Serena agent dependencies"""
        return {
            "requirements": [
                "Serena MCP Server (uvx --from git+https://github.com/oraios/serena)",
                "LSP Server capabilities",
                "Project workspace access"
            ],
            "tools": [
                "bmad_serena_initialize",
                "bmad_serena_activate_project",
                "bmad_serena_find_symbol",
                "bmad_serena_onboarding"
            ]
        }
    
    async def activate(self) -> str:
        """Activate Serena agent"""
        return f"""
🔍 **Serena Bridge Agent Activated** 

**Status:** {self.serena_bridge.get_status()['bridge_version']}

**Next Steps:**
1. Initialize Serena: `bmad_serena_initialize`
2. Activate your project: `bmad_serena_activate_project`
3. Start semantic code analysis!

**Key Capabilities:**
• Semantic symbol finding & analysis
• Cross-reference tracking  
• Precision code editing
• Project onboarding & understanding
• LSP-powered code intelligence

Ready for professional code analysis! 🚀
"""