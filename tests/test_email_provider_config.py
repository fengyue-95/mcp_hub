import os
import unittest

from services.email_service import _resolve_smtp_settings


class TestEmailProviderConfig(unittest.TestCase):
    def setUp(self):
        self._old_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._old_env)

    def test_resolve_gmail_uses_gmail_prefixed_creds(self):
        os.environ.pop("SMTP_USER", None)
        os.environ.pop("SMTP_PASS", None)
        os.environ["GMAIL_SMTP_USER"] = "u@gmail.com"
        os.environ["GMAIL_SMTP_PASS"] = "abcd efgh ijkl mnop"  # spaces should be removed

        settings = _resolve_smtp_settings(provider_override="gmail")
        self.assertEqual(settings["host"], "smtp.gmail.com")
        self.assertEqual(settings["port"], 587)
        self.assertFalse(settings["use_ssl"])
        self.assertEqual(settings["user"], "u@gmail.com")
        self.assertEqual(settings["password"], "abcdefghijklmnop")
        self.assertEqual(settings["from_addr"], "u@gmail.com")

    def test_resolve_qq_uses_qq_prefixed_creds(self):
        os.environ.pop("SMTP_USER", None)
        os.environ.pop("SMTP_PASS", None)
        os.environ["QQ_SMTP_USER"] = "u@qq.com"
        os.environ["QQ_SMTP_PASS"] = "qqauthcode"
        os.environ["QQ_SMTP_FROM"] = "u@qq.com"

        settings = _resolve_smtp_settings(provider_override="qq")
        self.assertEqual(settings["host"], "smtp.qq.com")
        self.assertEqual(settings["port"], 465)
        self.assertTrue(settings["use_ssl"])
        self.assertEqual(settings["user"], "u@qq.com")
        self.assertEqual(settings["password"], "qqauthcode")
        self.assertEqual(settings["from_addr"], "u@qq.com")


if __name__ == "__main__":
    unittest.main()

