import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from services.calendar_service import CalendarService
from services.file_service import FileService
from services.git_service import GitService
# from services.math_service import MathService
# from services.system_service import SystemService
from services.web_search_service import WebSearch
from services.email_service import EmailService


def _load_env_file(path: str = ".env") -> None:
    """Minimal .env loader to populate os.environ if not already set."""
    env_path = Path(path)
    if not env_path.exists() or not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if key in os.environ and os.environ[key]:
            continue
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        os.environ[key] = value


_load_env_file()

# 创建 Hub
hub = FastMCP("HTTP-MCP-Hub")

# 注册子服务工具

# SystemService().register_tools(hub)
# MathService().register_tools(hub)
FileService().register_tools(hub)
WebSearch().register_tools(hub)
GitService().register_tools(hub)
CalendarService().register_tools(hub)
EmailService().register_tools(hub)

if __name__ == "__main__":
    # 使用 sse 运行模式
    # 这会启动一个服务器，默认监听 http://localhost:8000
    hub.run(transport="sse")
