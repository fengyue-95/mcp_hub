from mcp.server.fastmcp import FastMCP
from services.file_service import FileService  # 复用之前的服务类
from services.math_service import MathService
from services.system_service import SystemService
from services.web_search_service import WebSearch

# 创建 Hub
hub = FastMCP("HTTP-MCP-Hub")

# 注册子服务工具
FileService().register_tools(hub)
SystemService().register_tools(hub)
MathService().register_tools(hub)
WebSearch().register_tools(hub)

if __name__ == "__main__":
    # 使用 sse 运行模式
    # 这会启动一个服务器，默认监听 http://localhost:8000
    hub.run(transport="sse")