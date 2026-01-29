from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from mcp.server.fastmcp import FastMCP
import time


class WebSearch:
    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="chrome_fetch")
        async def chrome_fetch(url: str) -> str:
            """
            使用真实 Chrome 浏览器打开网页并提取文本。
            适用于含有大量 JavaScript 渲染或有反爬限制的网站（如今日头条）。
            """
            # 配置 Chrome 选项
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            # 伪装成普通用户浏览器
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            driver = None
            try:
                # 自动下载并启动 ChromeDriver
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)

                # 设置页面加载超时
                driver.set_page_load_timeout(30)
                driver.get(url)

                # 等待几秒让动态内容（JavaScript）加载完成
                time.sleep(5)

                # 获取网页主体文字
                body_text = driver.find_element("tag name", "body").text

                return f"--- 浏览器抓取成功 ({url}) ---\n\n{body_text[:10000]}"

            except Exception as e:
                return f"Chrome 抓取失败: {str(e)}"
            finally:
                if driver:
                    driver.quit()  # 必须关闭浏览器进程，否则会占用大量内存