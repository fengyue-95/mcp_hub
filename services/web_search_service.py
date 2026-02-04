import os
import time
from urllib.parse import quote_plus

from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class WebSearch:
    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="web_search_url")
        async def web_search_url(url: str) -> str:
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

        @mcp.tool(name="web_search_query")
        async def web_search_query(query: str) -> str:
            """
            使用真实 Chrome 浏览器搜索关键词并返回前几条结果。
            默认使用 DuckDuckGo，可通过环境变量 WEB_SEARCH_QUERY_URL 自定义搜索引擎模板。
            模板示例：https://duckduckgo.com/?q={query}
            """
            if not query or not isinstance(query, str):
                return "参数错误：query 不能为空。"

            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            search_url_tpl = os.getenv("WEB_SEARCH_QUERY_URL", "https://duckduckgo.com/?q={query}")
            limit = int(os.getenv("WEB_SEARCH_QUERY_LIMIT", "5"))
            content_limit_bytes = int(os.getenv("WEB_SEARCH_QUERY_CONTENT_MAX_BYTES", "51200"))  # 50 KB
            fetch_timeout = int(os.getenv("WEB_SEARCH_QUERY_FETCH_TIMEOUT", "10"))

            driver = None
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.set_page_load_timeout(30)

                search_url = search_url_tpl.format(query=quote_plus(query))
                driver.get(search_url)
                time.sleep(3)

                results = _extract_search_results(driver, limit)
                if not results:
                    return f"未找到结果或解析失败：{query}"

                lines = []
                for idx, (title, url) in enumerate(results, start=1):
                    text = _fetch_page_text(driver, url, fetch_timeout, content_limit_bytes)
                    lines.append(f"{idx}. {title}\n   {url}\n   {text}")
                return f"--- 搜索结果 ({query}) ---\n\n" + "\n".join(lines)
            except Exception as e:
                return f"Chrome 搜索失败: {str(e)}"
            finally:
                if driver:
                    driver.quit()


def _extract_search_results(driver, limit: int):
    results = []
    selectors = [
        ("DuckDuckGo", "a.result__a"),
        ("Google", "div#search a h3"),
        ("Bing", "li.b_algo h2 a"),
    ]

    for _, selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for el in elements:
            try:
                title = el.text.strip()
                href = el.get_attribute("href")
                if not title or not href:
                    continue
                results.append((title, href))
                if len(results) >= limit:
                    return results
            except Exception:
                continue

    return results


def _fetch_page_text(driver, url: str, timeout: int, max_bytes: int) -> str:
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        time.sleep(2)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        data = body_text.encode("utf-8")
        if len(data) > max_bytes:
            data = data[:max_bytes]
            return data.decode("utf-8", errors="ignore") + "\n   [内容已截断]"
        return body_text
    except Exception as e:
        return f"[抓取失败: {str(e)}]"
