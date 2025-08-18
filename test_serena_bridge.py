#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
sys.path.append('src')

from bmad_mcp.agents.serena_bridge import BMadSerenaAgent

async def test_serena_bridge():
    """Test the Serena Bridge Agent"""
    
    print("=" * 50)
    print("BMAD-Serena Bridge Test")
    print("=" * 50)
    
    # Initialize agent
    agent = BMadSerenaAgent()
    
    print("\n1. Testing Agent Initialization...")
    try:
        result = await agent.initialize()
        print(f"   Result: {result}")
        
        serena_available = result.get('serena_available', False)
        print(f"   Serena Available: {serena_available}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Testing Agent Status...")
    try:
        status = agent.get_status()
        print(f"   Status: {status}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Testing Serena Command...")
    try:
        cmd = agent._get_serena_command()
        print(f"   Command: {' '.join(cmd)}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing Serena Availability...")
    try:
        availability = await agent._test_serena_availability()
        print(f"   Availability: {availability}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Testing Tool List...")
    try:
        tools = await agent._get_available_serena_tools()
        print(f"   Available Tools ({len(tools)}):")
        for i, tool in enumerate(tools[:5], 1):
            print(f"     {i}. {tool}")
        if len(tools) > 5:
            print(f"     ... and {len(tools) - 5} more")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n6. Testing Mock Tool Call...")
    try:
        result = await agent._call_serena_tool("find_symbol", {"symbol_name": "test"})
        print(f"   Mock Tool Result: {result}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows
    if os.name == 'nt':
        os.system('chcp 65001 > nul')
    
    asyncio.run(test_serena_bridge())