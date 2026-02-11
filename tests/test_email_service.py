import os
import tempfile
import unittest

from services.email_service import _build_message, _dedupe_preserve_order, _parse_recipients


class TestEmailService(unittest.TestCase):
    def test_parse_recipients_supports_multiple(self):
        recipients = _parse_recipients("a@example.com; b@example.com, Name <c@example.com>")
        self.assertEqual(recipients, ["a@example.com", "b@example.com", "c@example.com"])

    def test_parse_recipients_rejects_invalid(self):
        with self.assertRaises(ValueError):
            _parse_recipients("not-an-email")

    def test_dedupe_preserves_order(self):
        self.assertEqual(
            _dedupe_preserve_order(["a@example.com", "b@example.com", "a@example.com"]),
            ["a@example.com", "b@example.com"],
        )

    def test_build_message_enforces_attachment_limits(self):
        old_env = dict(os.environ)
        try:
            os.environ["EMAIL_ATTACH_MAX_BYTES"] = "5"
            os.environ["EMAIL_ATTACH_TOTAL_MAX_BYTES"] = "8"

            with tempfile.NamedTemporaryFile(delete=False) as f1:
                f1.write(b"12345")  # 5 bytes
                p1 = f1.name
            with tempfile.NamedTemporaryFile(delete=False) as f2:
                f2.write(b"1234")  # 4 bytes
                p2 = f2.name

            with self.assertRaises(ValueError):
                _build_message(
                    sender="sender@example.com",
                    to=["a@example.com"],
                    cc=[],
                    subject="sub",
                    content="body",
                    attachment_paths=[p1, p2],  # total 9 > 8
                )
        finally:
            os.environ.clear()
            os.environ.update(old_env)
            for p in [locals().get("p1"), locals().get("p2")]:
                if p and os.path.exists(p):
                    os.unlink(p)


if __name__ == "__main__":
    unittest.main()

