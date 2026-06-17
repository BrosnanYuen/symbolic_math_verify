"""CLI entry point for the symbolic math MCP server."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import choose_port, load_config
from .server import create_mcp_server


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run the symbolic math MCP server.")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "config.json"),
        help="Path to the JSON config file.",
    )
    parser.add_argument(
        "--show-banner",
        action="store_true",
        help="Show the FastMCP startup banner.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the configured MCP server."""
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config(args.config)
    server = create_mcp_server(config)

    if config.transport() == "stdio":
        server.run(transport="stdio", show_banner=args.show_banner)
        return 0

    host = config.http_host()
    port = choose_port(host, config.http_port())
    path = config.http_path()
    if path == "/":
        path = "/mcp"
    server.run(
        transport="http",
        host=host,
        port=port,
        path=path,
        show_banner=args.show_banner,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
