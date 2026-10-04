"""Entry point for MCP clients: python run_server.py (stdio transport)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcmcp.server import main

if __name__ == "__main__":
    main()
