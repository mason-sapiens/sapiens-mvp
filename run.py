#!/usr/bin/env python3
"""
Simple script to run the Sapiens MVP API server.

Usage:
    python run.py
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Check for required environment variables
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY environment variable is not set")
    print("\nPlease set it with:")
    print("  export OPENAI_API_KEY=your_api_key_here")
    print("\nOr add it to a .env file in the project root")
    print("\nGet your API key at: https://platform.openai.com/api-keys")
    sys.exit(1)

# Create data directories
os.makedirs("./data/chroma", exist_ok=True)
os.makedirs("./data/logs", exist_ok=True)

print("Starting Sapiens MVP API server...")
print("API will be available at: http://localhost:8000")
print("API docs available at: http://localhost:8000/docs")
print("\nPress Ctrl+C to stop the server\n")

# Run uvicorn
import uvicorn

uvicorn.run(
    "backend.api.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="info"
)
