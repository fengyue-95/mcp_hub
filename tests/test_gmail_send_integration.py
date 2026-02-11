import os
import unittest
from pathlib import Path
import smtplib

from services.email_service import _build_message, _resolve_smtp_settings, _send_via_smtp


def _load_dotenv(dotenv_path: str = ".env") -> None:
    """
    Minimal .env loader (no external dependency).
    - Ignores empty lines and comments (# ...)
    - Supports KEY=VALUE (VALUE may be quoted with single/double quotes)
    - Does not override existing non-empty environment variables
    """
    p = Path(dotenv_path)
    candidates: list[Path]
    if p.is_absolute():
        candidates = [p]
    else:
        candidates = [
            Path.cwd() / p,
            Path(__file__).resolve().parent.parent / p,  # repo root
        ]

    path = next((c for c in candidates if c.exists() and c.is_file()), None)
    if path is None:
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if key in os.environ and os.environ.get(key, "") != "":
            continue
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        os.environ[key] = value


class TestGmailSendIntegration(unittest.TestCase):
    def test_send_gmail_to_qq(self):
        """
        Sends a real email via Gmail SMTP to a QQ mailbox.

        Required env vars:
        - EMAIL_PROVIDER=gmail (or will be set for this test)
        - SMTP_USER=<your gmail address>
        - SMTP_PASS=<gmail app password>
        Optional:
        - SMTP_FROM=<from address> (defaults to SMTP_USER)
        """
        if os.getenv("RUN_GMAIL_SEND_TEST") != "1":
            self.skipTest("Integration test disabled. Set RUN_GMAIL_SEND_TEST=1 to enable.")

        _load_dotenv()

        gmail_user = os.getenv("GMAIL_SMTP_USER") or os.getenv("SMTP_USER")
        gmail_pass = os.getenv("GMAIL_SMTP_PASS") or os.getenv("SMTP_PASS")
        if not gmail_user or not gmail_pass:
            self.skipTest("Missing GMAIL_SMTP_USER/GMAIL_SMTP_PASS (or SMTP_USER/SMTP_PASS) in environment.")
        if not gmail_user.lower().endswith(("@gmail.com", "@googlemail.com")):
            self.skipTest(f"SMTP user does not look like a Gmail address: {gmail_user}")

        old_provider = os.getenv("EMAIL_PROVIDER")
        old_user = os.getenv("SMTP_USER")
        old_pass = os.getenv("SMTP_PASS")
        os.environ["EMAIL_PROVIDER"] = "gmail"
        os.environ["SMTP_USER"] = gmail_user
        os.environ["SMTP_PASS"] = gmail_pass
        try:
            recipient = "1339148474@qq.com"
            subject = "测试邮件"
            content = "测试邮件"

            settings = _resolve_smtp_settings()
            msg = _build_message(
                sender=settings["from_addr"],
                to=[recipient],
                cc=[],
                subject=subject,
                content=content,
                attachment_paths=[],
            )
            try:
                _send_via_smtp(msg, settings, recipients=[recipient])
            except smtplib.SMTPAuthenticationError as e:
                self.fail(
                    "Gmail SMTP authentication failed (535). Common causes:\n"
                    "- SMTP_PASS is not the App Password, or includes spaces (should be 16 chars, no spaces)\n"
                    "- App Password generated for a different Google account\n"
                    "- Google blocked SMTP sign-in: check Google Account -> Security -> Recent activity, "
                    'or try "DisplayUnlockCaptcha" then retry after a few minutes\n'
                    f"SMTP_USER={gmail_user}, SMTP_PASS_LEN={len(gmail_pass)}\n"
                    f"Original error: {e}"
                )
        finally:
            if old_provider is None:
                os.environ.pop("EMAIL_PROVIDER", None)
            else:
                os.environ["EMAIL_PROVIDER"] = old_provider
            if old_user is None:
                os.environ.pop("SMTP_USER", None)
            else:
                os.environ["SMTP_USER"] = old_user
            if old_pass is None:
                os.environ.pop("SMTP_PASS", None)
            else:
                os.environ["SMTP_PASS"] = old_pass


if __name__ == "__main__":
    unittest.main()
