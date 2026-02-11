import os
import smtplib
from email.message import EmailMessage
from email.utils import getaddresses
from pathlib import Path
from typing import Iterable, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:  # Allows importing this module in minimal envs (e.g. unit tests)
    FastMCP = object  # type: ignore

_PROVIDERS = {
    "qq": {"host": "smtp.qq.com", "port": 465, "use_ssl": True},
    "163": {"host": "smtp.163.com", "port": 465, "use_ssl": True},
    "gmail": {"host": "smtp.gmail.com", "port": 587, "use_ssl": False},
}


class EmailService:
    """发送邮件服务"""

    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="send_email")
        async def send_email(
            to: str,
            subject: str,
            content: str,
            attachment_paths: Optional[list[str]] = None,
            cc: Optional[str] = None,
            bcc: Optional[str] = None,
            provider: Optional[str] = None,
        ) -> str:
            """
            发送邮件（支持附件）。
            依赖环境变量：EMAIL_PROVIDER/SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASS/SMTP_FROM

            - 多收件人：to/cc/bcc 支持用英文逗号或分号分隔多个邮箱
            - bcc 不会写入邮件头，仅用于投递
            - 多渠道：可在调用时通过 provider 指定（如 "gmail"/"qq"），未指定则使用环境变量 EMAIL_PROVIDER
            """
            if not subject or not content:
                return "参数错误：subject/content 不能为空。"

            to_list = _parse_recipients(to)
            cc_list = _parse_recipients(cc or "")
            bcc_list = _parse_recipients(bcc or "")
            all_recipients = _dedupe_preserve_order([*to_list, *cc_list, *bcc_list])
            if not all_recipients:
                return "参数错误：收件人不能为空（to/cc/bcc 至少一个）。"

            settings = _resolve_smtp_settings(provider_override=provider)
            msg = _build_message(
                sender=settings["from_addr"],
                to=to_list,
                cc=cc_list,
                subject=subject,
                content=content,
                attachment_paths=attachment_paths or [],
            )

            _send_via_smtp(msg, settings, recipients=all_recipients)
            return f"邮件发送成功：{', '.join(all_recipients)}"


def _resolve_smtp_settings(provider_override: Optional[str] = None) -> dict:
    provider = (provider_override or os.getenv("EMAIL_PROVIDER", "gmail")).strip().lower()
    if provider in _PROVIDERS:
        host = _PROVIDERS[provider]["host"]
        port = _PROVIDERS[provider]["port"]
        use_ssl = _PROVIDERS[provider]["use_ssl"]
    else:
        host = os.getenv("SMTP_HOST", "")
        port = int(os.getenv("SMTP_PORT", "587"))
        use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

    host = (host or "").strip()
    user, password, from_addr = _resolve_auth_settings(provider)
    # Treat empty SMTP_FROM as unset
    timeout = int(os.getenv("SMTP_TIMEOUT", "15"))

    if not host or not user or not password or not from_addr:
        if provider in _PROVIDERS:
            raise ValueError(
                "SMTP 配置缺失：请设置 Gmail/QQ 等渠道的账号密码（例如 GMAIL_SMTP_USER/GMAIL_SMTP_PASS），"
                "或设置通用 SMTP_USER/SMTP_PASS（以及可选 SMTP_FROM）。"
            )
        raise ValueError("SMTP 配置缺失：请设置 SMTP_HOST/SMTP_USER/SMTP_PASS（以及可选 SMTP_FROM）。")

    return {
        "host": host,
        "port": port,
        "use_ssl": use_ssl,
        "user": user,
        "password": password,
        "from_addr": from_addr,
        "timeout": timeout,
    }


def _resolve_auth_settings(provider: str) -> tuple[str, str, str]:
    """
    Resolve SMTP auth settings, supporting per-provider credentials.

    Supported per-provider env vars:
    - Gmail: GMAIL_SMTP_USER / GMAIL_SMTP_PASS / GMAIL_SMTP_FROM
    - QQ:    QQ_SMTP_USER / QQ_SMTP_PASS / QQ_SMTP_FROM

    Falls back to generic:
    - SMTP_USER / SMTP_PASS / SMTP_FROM
    """
    provider = (provider or "").strip().lower()
    prefix = {"gmail": "GMAIL", "qq": "QQ"}.get(provider)

    def get_env(key: str) -> str:
        return (os.getenv(key, "") or "").strip()

    user = get_env(f"{prefix}_SMTP_USER") if prefix else ""
    password = get_env(f"{prefix}_SMTP_PASS") if prefix else ""
    from_addr = get_env(f"{prefix}_SMTP_FROM") if prefix else ""

    if not user:
        user = get_env("SMTP_USER")
    if not password:
        password = get_env("SMTP_PASS")
    # Common: App Password is displayed with spaces like "xxxx xxxx xxxx xxxx"
    password = password.replace(" ", "")

    if not from_addr:
        # Treat empty SMTP_FROM as unset
        from_addr = get_env("SMTP_FROM")
    if not from_addr:
        from_addr = user

    return user, password, from_addr


def _build_message(
    sender: str,
    to: list[str],
    cc: list[str],
    subject: str,
    content: str,
    attachment_paths: Iterable[str],
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    if to:
        msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg["Subject"] = subject
    msg.set_content(content)

    # 附件大小限制（默认 10MB）。注意：实际 SMTP 传输中会有 base64 膨胀。
    default_max_bytes = 10 * 1024 * 1024
    max_bytes = int(os.getenv("EMAIL_ATTACH_MAX_BYTES", str(default_max_bytes)))
    total_max_bytes = int(os.getenv("EMAIL_ATTACH_TOTAL_MAX_BYTES", str(default_max_bytes)))
    total_size = 0
    for path_str in attachment_paths:
        path = Path(path_str).expanduser().resolve()
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"附件不存在：{path}")
        size = path.stat().st_size
        total_size += size
        if size > max_bytes:
            raise ValueError(f"附件过大：{path} ({size} bytes)")
        if total_size > total_max_bytes:
            raise ValueError(f"附件总大小超限：{total_size} bytes（限制 {total_max_bytes} bytes）")
        data = path.read_bytes()
        msg.add_attachment(
            data,
            maintype="application",
            subtype="octet-stream",
            filename=path.name,
        )

    return msg


def _send_via_smtp(msg: EmailMessage, settings: dict, recipients: list[str]) -> None:
    host = settings["host"]
    port = settings["port"]
    use_ssl = settings["use_ssl"]
    timeout = settings["timeout"]

    if use_ssl:
        with smtplib.SMTP_SSL(host, port, timeout=timeout) as server:
            server.login(settings["user"], settings["password"])
            server.send_message(msg, to_addrs=recipients)
    else:
        with smtplib.SMTP(host, port, timeout=timeout) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings["user"], settings["password"])
            server.send_message(msg, to_addrs=recipients)


def _parse_recipients(raw: str) -> list[str]:
    raw = (raw or "").strip()
    if not raw:
        return []
    normalized = raw.replace(";", ",")
    recipients: list[str] = []
    for _name, addr in getaddresses([normalized]):
        addr = (addr or "").strip()
        if not addr:
            continue
        if " " in addr or "@" not in addr:
            raise ValueError(f"收件人邮箱格式不正确：{addr}")
        recipients.append(addr)
    return recipients


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
