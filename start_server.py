"""
Starts only the uvicorn API server (no CLI loop).
Used by test.ps1 and for headless/production-style runs.

Usage:
    python start_server.py [--port 8000] [--host 127.0.0.1]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from api.server import app, set_runtime
from simulation import create_runtime


def main() -> None:
    parser = argparse.ArgumentParser(description="Divinity Sim API Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--log-level", default="warning")
    args = parser.parse_args()

    load_dotenv()
    runtime = create_runtime(str(Path(__file__).resolve().parent))
    set_runtime(runtime)

    print(f"Starting Divinity Sim API on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)


if __name__ == "__main__":
    main()
