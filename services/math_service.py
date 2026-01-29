import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

class MathService:
    """处理文件相关操作的服务模块"""

    def register_tools(self, mcp: FastMCP):


        @mcp.tool()
        def add(a: float, b: float) -> float:
            """Add two numbers"""
            logger.info("The add method is called: a=%d, b=%d", a, b)  # 记录加法调用日志
            return a + b

        @mcp.tool()
        def multiply(a: float, b: float) -> float:
            """Multiply two numbers"""
            logger.info("The multiply method is called: a=%d, b=%d", a, b)  # 记录乘法调用日志
            return a * b

        # 定义减法工具函数
        @mcp.tool()
        async def subtract(a: float, b: float) -> float:
            """执行减法运算

            Args:
                a: 第一个数字
                b: 第二个数字
            """
            logger.info("The subtract method is called: a=%d, b=%d", a, b)  # 记录减法调用日志
            return a - b

        # 定义除法工具函数
        @mcp.tool()
        async def divide(a: float, b: float) -> float:
            """执行除法运算

            Args:
                a: 第一个数字
                b: 第二个数字
            """
            logger.info("The divide method is called: a=%d, b=%d", a, b)  # 记录减法调用日志
            if b == 0:
                raise ValueError("Division by zero is not allowed")
            return a / b