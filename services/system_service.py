import platform
from mcp.server.fastmcp import FastMCP

class SystemService:
    """处理系统信息查看的服务模块"""

    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="sys_info")
        async def get_system_info() -> str:
            """获取当前运行环境的系统信息"""
            return f"OS: {platform.system()}, Node: {platform.node()}"