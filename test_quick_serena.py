#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
sys.path.append('src')

from bmad_mcp.agents.serena_bridge import BMadSerenaAgent

async def quick_test():
    """Quick Serena Test ohne lange Wartezeiten"""
    
    print("=" * 40)
    print("BMAD-Serena Quick Test")
    print("=" * 40)
    
    agent = BMadSerenaAgent()
    
    try:
        # Test 1: Initialization mit Timeout
        print("\n1. Serena Initialization...")
        init_result = await asyncio.wait_for(agent.initialize(), timeout=30.0)
        print(f"   Init Result: {init_result}")
        
        if init_result.get('serena_available'):
            print("   ✅ Serena Bridge successfully initialized!")
            print(f"   📊 Available Tools: {len(init_result.get('available_tools', []))}")
            
            # Test 2: Status Check
            print("\n2. Status Check...")
            status = agent.get_status()
            print(f"   MCP Active: {status['mcp_session_active']}")
            print(f"   Tools: {status['available_tools_count']}")
            
            # Test 3: Quick Tool Test (with mock project)
            print("\n3. Testing Find Symbol...")
            test_result = await asyncio.wait_for(
                agent.find_symbol("test_symbol", "function"), 
                timeout=10.0
            )
            print(f"   Tool Test: {test_result.get('success', False)}")
            
        else:
            print("   ❌ Serena not available")
            print(f"   Error: {init_result.get('error')}")
        
    except asyncio.TimeoutError:
        print("   ⏰ Test timed out - but initialization started")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    finally:
        # Cleanup
        print("\n4. Cleanup...")
        try:
            await agent.cleanup()
            print("   ✅ Cleanup completed")
        except Exception as e:
            print(f"   ⚠️  Cleanup error: {e}")
    
    print("\n" + "=" * 40)
    print("Quick Test Complete")
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(quick_test())