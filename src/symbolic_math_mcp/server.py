"""FastMCP server wiring."""

from __future__ import annotations

from fastmcp import FastMCP

from .config import ServerConfig
from .service import SymbolicMathService


def create_mcp_server(config: ServerConfig, service: SymbolicMathService | None = None) -> FastMCP:
    """Build the FastMCP server instance."""
    active_service = service or SymbolicMathService(
        max_requests=config.max_requests,
        total_timeout=config.total_timeout,
        yaml_must_have=config.yaml_must_have,
    )
    mcp = FastMCP(
        config.mcp_server_name,
        instructions=(
            "Use check_symbolic_math(filename) to synchronously validate one symbolic math YAML file, "
            "or check_symbolic_math_parallel(dir_path) to synchronously validate every YAML file in an "
            "absolute directory path. This server returns structured status fields and verifier results."
        ),
    )

    @mcp.tool(name="check_symbolic_math", description="Validate a .yaml symbolic math proof file.", run_in_thread=True)
    def check_symbolic_math(filename: str) -> dict[str, str]:
        return active_service.check_symbolic_math(filename)

    @mcp.tool(
        name="check_symbolic_math_parallel",
        description="Validate every .yaml symbolic math proof file in an absolute directory path.",
        run_in_thread=True,
    )
    def check_symbolic_math_parallel(dir_path: str) -> dict[str, object]:
        return active_service.check_symbolic_math_parallel(dir_path)

    return mcp
