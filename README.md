**mcp_hub** - An MCP (Model Context Protocol) Hub project that provides multiple services through a FastMCP server.

### Structure:
- **main.py** - Entry point that creates the MCP Hub and registers all services
- **services/** - Service modules:
  - `file_service.py` - File read/write operations
  - `math_service.py` - Mathematical operations (add, subtract, multiply, divide)
  - `system_service.py` - System information retrieval
  - `web_search_service.py` - Chrome-based web scraping
- **requirements.txt** - Dependencies (mcp, selenium, webdriver_manager)

### How to Run:
```bash
python3 main.py
```

This starts an SSE server on `http://localhost:8000` exposing all registered tools.

### Current Status:
- Git repository initialized on `main` branch
- Untracked: `services/__pycache__/` (Python cache files)

Is there anything specific you'd like to do with this project?


```bash
#导出你在 .py 文件里真正 import 过的包。# mcp_hub  2313123123
pipreqs . --encoding=utf8 --force  
```
