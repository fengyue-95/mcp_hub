import platform
from mcp.server.fastmcp import FastMCP
import datetime

class SystemService:
    """处理系统信息查看的服务模块"""

    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="sys_info")
        async def get_system_info() -> str:
            """获取当前运行环境的系统信息"""
            return f"OS: {platform.system()}, Node: {platform.node()}"

        @mcp.tool(name="get_current_time")
        async def get_current_time() -> str:
            """获取本地系统的当前日期和时间。"""
            now = datetime.datetime.now()
            return now.strftime("今天是：%Y-%m-%d, 星期%w (0是周日), 当前时间：%H:%M:%S")