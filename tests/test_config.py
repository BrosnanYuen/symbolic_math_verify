from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from symbolic_math_mcp.config import ServerConfig, choose_port, load_config


class TestConfig(unittest.TestCase):
    def test_load_config_accepts_stdio(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "mcp_server_name": "Server",
                        "mcp_server_url": "stdio://local",
                        "yaml_must_have": ["axioms:"],
                        "max_requests": 2,
                        "total_timeout": 5,
                    }
                ),
                encoding="utf-8",
            )
            config = load_config(path)
        self.assertEqual("stdio", config.transport())
        self.assertEqual(("axioms:",), config.yaml_must_have)

    def test_load_config_accepts_http_variants(self) -> None:
        config = ServerConfig("Server", "https://localhost:9443/custom", ("axioms:",), 1, 10)
        self.assertEqual("http", config.transport())
        self.assertEqual("localhost", config.http_host())
        self.assertEqual(9443, config.http_port())
        self.assertEqual("/custom", config.http_path())

    def test_choose_port_uses_fallback_when_preferred_is_taken(self) -> None:
        class FakeSocket:
            def __init__(self, *_args, **_kwargs) -> None:
                self.bound = None

            def setsockopt(self, *_args, **_kwargs) -> None:
                return None

            def bind(self, address) -> None:
                host, port = address
                if port == 8753:
                    raise OSError("taken")
                self.bound = (host, 9911)

            def getsockname(self):
                return self.bound

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        with patch("symbolic_math_mcp.config.socket.socket", return_value=FakeSocket()):
            chosen_port = choose_port("127.0.0.1", 8753)

        self.assertEqual(9911, chosen_port)
