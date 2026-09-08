"""Anywhere 订阅格式、兼容性差异与生成流程的回归检查。"""
import io
import ipaddress
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import gen_readme
import sync_rules


class AnywhereRulesTests(unittest.TestCase):
    def test_rule_ids_and_cidr_values_follow_anywhere_format(self):
        rules = [
            sync_rules.Rule("DOMAIN", "api.example.com", []),
            sync_rules.Rule("DOMAIN-SUFFIX", "example.org", []),
            sync_rules.Rule("DOMAIN-KEYWORD", "stream", []),
            sync_rules.Rule("IP-CIDR", "192.0.2.0/24", ["no-resolve"]),
            sync_rules.Rule("IP-CIDR6", "2001:db8::/32", ["no-resolve"]),
        ]
        text, skipped = sync_rules.emit_anywhere(rules)
        lines = [line for line in text.splitlines() if not line.startswith("#")]
        self.assertEqual(lines, [
            "2,api.example.com", "2,example.org", "3,stream",
            "0,192.0.2.0/24", "1,2001:db8::/32",
        ])
        self.assertEqual(skipped, 0)
        self.assertIn("1 DOMAIN rules use suffix matching, including subdomains.", text)
        self.assertIn("2 no-resolve modifiers omitted", text)
        for line in lines:
            rule_type, value = line.split(",", 1)
            if rule_type in {"0", "1"}:
                self.assertEqual(ipaddress.ip_network(value).version, 4 if rule_type == "0" else 6)

    def test_unsupported_rules_are_counted_and_not_emitted(self):
        unsupported = {
            "DOMAIN-REGEX": r"^api\.example\.com$", "GEOIP": "CN", "ASN": "64500",
            "PROCESS-NAME": "example", "USER-AGENT": "Example*", "URL-REGEX": "^https://",
        }
        rules = [sync_rules.Rule(kind, value, []) for kind, value in unsupported.items()]
        text, skipped = sync_rules.emit_anywhere(rules)
        self.assertEqual(skipped, len(rules))
        self.assertTrue(all(line.startswith("#") for line in text.splitlines()))
        self.assertIn("6 unsupported rules omitted", text)

    def test_other_line_formats_keep_no_resolve(self):
        rules = [sync_rules.Rule("IP-CIDR", "192.0.2.0/24", ["no-resolve"])]
        for emitter in (sync_rules.emit_clash, sync_rules.emit_qx, sync_rules.emit_surge):
            with self.subTest(format=emitter.__name__):
                text, skipped = emitter(rules)
                self.assertIn("IP-CIDR,192.0.2.0/24,no-resolve", text)
                self.assertEqual(skipped, 0)

    def run_sync(self, root, check=False):
        arguments = ["sync_rules.py", "--check"] if check else ["sync_rules.py"]
        with (patch.object(sync_rules, "ROOT", root),
              patch.object(sync_rules, "SRC_DIR", root / "loon/rule"),
              patch("sys.argv", arguments),
              redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO())):
            return sync_rules.main()

    def test_generation_and_check_handle_missing_stale_and_orphaned_subscriptions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "loon/rule/sample.list"
            source.parent.mkdir(parents=True)
            source.write_text("HOST-SUFFIX,example.com\n", encoding="utf-8")
            target = root / "anywhere/rule/sample.arrs"
            self.assertEqual(self.run_sync(root, check=True), 1)
            self.assertFalse(target.parent.exists())
            self.assertEqual(self.run_sync(root), 0)
            expected = target.read_text(encoding="utf-8")
            self.assertIn("2,example.com\n", expected)
            self.assertEqual(self.run_sync(root, check=True), 0)
            target.write_text("stale\n", encoding="utf-8")
            orphan = target.with_name("removed.arrs")
            orphan.write_text("orphan\n", encoding="utf-8")
            self.assertEqual(self.run_sync(root, check=True), 1)
            self.assertEqual(target.read_text(encoding="utf-8"), "stale\n")
            self.assertEqual(orphan.read_text(encoding="utf-8"), "orphan\n")
            self.assertEqual(self.run_sync(root), 0)
            self.assertEqual(target.read_text(encoding="utf-8"), expected)
            self.assertFalse(orphan.exists())
            self.assertEqual(self.run_sync(root, check=True), 0)


class AnywhereImportTests(unittest.TestCase):
    def test_import_link_keeps_the_entire_subscription_url(self):
        url = "https://example.com/custom.arrs?token=a%2Fb&name=rules#section"
        scheme, universal = gen_readme.anywhere_ruleset(url, "custom")
        parsed = urlsplit(scheme)
        self.assertEqual((parsed.scheme, parsed.netloc), ("anywhere", "add-rule-set"))
        self.assertEqual(parse_qs(parsed.query), {"link": [url]})
        self.assertIsNone(universal)

    def test_readme_contains_only_arrs_subscription_links(self):
        config = next(entry for entry in gen_readme.DIRS if entry["path"] == "anywhere/rule")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rules = root / config["path"]
            rules.mkdir(parents=True)
            for name in ("sample.arrs", "unsupported.list", "README.md"):
                (rules / name).write_text("", encoding="utf-8")
            with patch.object(gen_readme, "ROOT", root):
                text = gen_readme.render(config)
            self.assertIn(f"{gen_readme.RAW}/anywhere/rule/sample.arrs", text)
            self.assertIn("anywhere://add-rule-set?link=", text)
            self.assertNotIn("unsupported.list", text)


if __name__ == "__main__":
    unittest.main()
