**mcp_hub** - An MCP (Model Context Protocol) Hub project that provides multiple services through a FastMCP server.

### Structure:
- **main.py** - Entry point that creates the MCP Hub and registers all services
- **services/** - Service modules:
  - `file_service.py` - File read/write operations
  - `math_service.py` - Mathematical operations (add, subtract, multiply, divide)
  - `system_service.py` - System information retrieval
  - `web_search_service.py` - Chrome-based web scraping
  - `email_service.py` - Send email via SMTP (multi-recipient + attachments)
- **requirements.txt** - Dependencies (mcp, selenium, webdriver_manager)

### How to Run:
```bash
python3 main.py
```

This starts an SSE server on `http://localhost:8000` exposing all registered tools.

### Email (send_email)

See `.env.example` for a commented config template.

Environment variables:
- `EMAIL_PROVIDER`: `qq` / `163` / `gmail` / `custom` (default: `gmail`)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USE_SSL` (`true`/`false`)
- `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`
- `SMTP_TIMEOUT` (seconds, default: `15`)
- Per-provider (recommended, can configure multiple channels at once):
  - Gmail: `GMAIL_SMTP_USER`, `GMAIL_SMTP_PASS`, `GMAIL_SMTP_FROM`
  - QQ: `QQ_SMTP_USER`, `QQ_SMTP_PASS`, `QQ_SMTP_FROM`
- Attachment limits:
  - `EMAIL_ATTACH_MAX_BYTES` (per file, default: `10485760` = 10MB)
  - `EMAIL_ATTACH_TOTAL_MAX_BYTES` (sum of all attachments, default: `10485760` = 10MB)

Tool args:
- `to`: supports multiple recipients separated by `,` or `;`
- `cc`/`bcc`: optional, also supports multiple recipients separated by `,` or `;`
- `attachment_paths`: optional list of local file paths
- `provider`: optional, override channel for this call (e.g. `gmail` / `qq`)

### Current Status:
- Git repository initialized on `main` branch
- Untracked: `services/__pycache__/` (Python cache files)

Is there anything specific you'd like to do with this project?


```bash
#导出你在 .py 文件里真正 import 过的包。# mcp_hub  2313123123
pipreqs . --encoding=utf8 --force  
```
