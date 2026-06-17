"""Configuration helpers for the symbolic math MCP server."""

from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class ServerConfig:
    """Configuration for the MCP server runtime."""

    mcp_server_name: str
    mcp_server_url: str
    yaml_must_have: tuple[str, ...]
    max_requests: int
    total_timeout: float

    def parsed_url(self):
        return urlparse(self.mcp_server_url)

    def transport(self) -> str:
        scheme = self.parsed_url().scheme.lower()
        if scheme == "stdio":
            return "stdio"
        if scheme in {"http", "https"}:
            return "http"
        raise ValueError(f"unsupported mcp_server_url scheme: {scheme}")

    def http_host(self) -> str:
        parsed = self.parsed_url()
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("http_host is only valid for http/https transports")
        return parsed.hostname or "127.0.0.1"

    def http_port(self) -> int:
        parsed = self.parsed_url()
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("http_port is only valid for http/https transports")
        if parsed.port is not None:
            return parsed.port
        return 443 if parsed.scheme.lower() == "https" else 80

    def http_path(self) -> str:
        parsed = self.parsed_url()
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("http_path is only valid for http/https transports")
        path = parsed.path or "/"
        return path if path.startswith("/") else f"/{path}"


def load_config(config_path: str | Path) -> ServerConfig:
    """Load and validate a JSON configuration file."""
    path = Path(config_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    config = ServerConfig(
        mcp_server_name=str(data["mcp_server_name"]),
        mcp_server_url=str(data["mcp_server_url"]),
        yaml_must_have=tuple(str(item) for item in data.get("yaml_must_have", [])),
        max_requests=int(data["max_requests"]),
        total_timeout=float(data["total_timeout"]),
    )
    if not config.mcp_server_name.strip():
        raise ValueError("mcp_server_name must be non-empty")
    if config.max_requests <= 0:
        raise ValueError("max_requests must be greater than zero")
    if config.total_timeout <= 0:
        raise ValueError("total_timeout must be greater than zero")
    if any(not item for item in config.yaml_must_have):
        raise ValueError("yaml_must_have must only contain non-empty strings")
    config.transport()
    return config


def choose_port(host: str, preferred_port: int) -> int:
    """Use the preferred port when possible, otherwise return a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, preferred_port))
        except OSError:
            sock.bind((host, 0))
            return int(sock.getsockname()[1])
        return preferred_port
