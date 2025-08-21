#!/usr/bin/env python3
"""
BMAD MCP Server - CLI Entry Point for Railway Deployment
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="BMAD MCP Server v2.0")
    parser.add_argument("--port", type=int, help="Port to run HTTP server on (for Railway deployment)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    # Set PORT environment variable if specified
    if args.port:
        os.environ["PORT"] = str(args.port)
    
    # Import and run the main server
    try:
        from .server import main as server_main
        asyncio.run(server_main())
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔍 Checking PYTHONPATH and dependencies...")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 BMAD MCP Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ BMAD MCP Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()