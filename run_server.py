#!/usr/bin/env python

import asyncio
import os
import sys
from pathlib import Path

def main():
    """
    Server launcher script to correctly configure sys.path.
    This ensures that imports within the 'src' directory are resolved correctly
    regardless of how the script is invoked.
    """
    # Add the 'src' directory to the Python path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Now that the path is configured, we can import and run the server
    from bmad_mcp.server import main as run_server_main
    
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("dotenv not found, skipping .env file loading.", file=sys.stderr)

    print("Starting BMAD MCP Server from launcher...", file=sys.stderr)
    asyncio.run(run_server_main())

if __name__ == "__main__":
    main()