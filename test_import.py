#!/usr/bin/env python3
"""
BMAD MCP Server Test Script
"""

import sys
import os
from pathlib import Path

def test_bmad_import():
    """Test if BMAD modules can be imported"""
    
    # Add the project root to Python path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")
    print(f"Source path: {src_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # First 3 entries
    print()
    
    try:
        print("Testing imports...")
        
        # Test basic import
        import bmad_mcp
        print("✅ bmad_mcp imported successfully")
        
        # Test server import
        from bmad_mcp.server import BMadMCPServer
        print("✅ BMadMCPServer imported successfully")
        
        # Test agents import
        from bmad_mcp.agents import AgentManager
        print("✅ AgentManager imported successfully")
        
        # Test core import
        from bmad_mcp.core import BMadLoader
        print("✅ BMadLoader imported successfully")
        
        print("\n🎉 All imports successful!")
        
        # Try to create server instance
        print("\nTesting server instantiation...")
        server = BMadMCPServer()
        print("✅ BMadMCPServer instance created successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

if __name__ == "__main__":
    success = test_bmad_import()
    sys.exit(0 if success else 1)
