from mcp.server.fastmcp import FastMCP


class FileService:
    """处理文件相关操作的服务模块"""

    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="file_read")
        async def read_file(path: str) -> str:
            """读取本地文件内容"""
            return f"内容来自 {path}: 这是一个模拟的文件内容。"

        @mcp.tool(name="file_write")
        async def write_file(path: str, content: str) -> str:
            """写入内容到本地文件"""
            return f"成功写入 {len(content)} 字符到 {path}。"