import argparse
import os
import sys
from pathlib import Path

from services.email_service import _build_message, _resolve_smtp_settings, _send_via_smtp


def _load_dotenv(dotenv_path: str = ".env") -> None:
    """
    Minimal .env loader (no external dependency).
    - Ignores empty lines and comments (# ...)
    - Supports KEY=VALUE (VALUE may be quoted with single/double quotes)
    - Does not override existing environment variables
    """
    candidates: list[Path] = []
    p = Path(dotenv_path)
    if p.is_absolute():
        candidates = [p]
    else:
        # Try CWD first, then repo root (script's parent directory)
        candidates = [
            Path.cwd() / p,
            Path(__file__).resolve().parent.parent / p,
        ]

    path = next((c for c in candidates if c.exists() and c.is_file()), None)
    if path is None:
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        # Don't override non-empty env vars, but allow .env to fill empty ones.
        if key in os.environ and os.environ.get(key, "") != "":
            continue
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        os.environ[key] = value


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a test email using EmailService SMTP settings.")
    parser.add_argument("--provider", default=None, help='Email provider/channel, e.g. "gmail" or "qq"')
    parser.add_argument("--to", default="yuefeng.0617@gmail.com", help="Recipient email address")
    parser.add_argument("--subject", default="测试邮件", help="Email subject")
    parser.add_argument("--content", default="你好啊fengyue", help="Email content (plain text)")
    parser.add_argument(
        "--dotenv",
        default=".env",
        help="Path to .env (only used if variables are not already in environment)",
    )
    args = parser.parse_args()

    _load_dotenv(args.dotenv)

    try:
        settings = _resolve_smtp_settings(provider_override=args.provider)
        msg = _build_message(
            sender=settings["from_addr"],
            to=[args.to],
            cc=[],
            subject=args.subject,
            content=args.content,
            attachment_paths=[],
        )
        _send_via_smtp(msg, settings, recipients=[args.to])
    except Exception as e:
        print(f"Send failed: {e}", file=sys.stderr)
        return 1

    print(f"Send OK: {args.to}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
