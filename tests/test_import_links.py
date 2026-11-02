"""一键导入链接的回归检查：跳转页白名单、链接往返、手写 README 的注入。"""
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import gen_readme


def allowed_schemes() -> set[str]:
    """从 docs/import.html 里读出协议白名单。"""
    html = (gen_readme.ROOT / "docs/import.html").read_text(encoding="utf-8")
    block = re.search(r"var ALLOWED = \[(.*?)\];", html, re.S)
    assert block, "docs/import.html 里找不到 ALLOWED 白名单"
    return set(re.findall(r'"([^"]+)"', block.group(1)))


def sample_urls(d: dict) -> list[str]:
    """按目录配置造一个有代表性的地址 —— 扩展名会影响 Anywhere 的动作分派。"""
    if d.get("only"):
        return [f"https://example.com/{name}" for name in d["only"]]
    return [f"https://example.com/sample{ext}" for ext in (d["ext"] or [".txt"])]


class BridgeTests(unittest.TestCase):
    def test_every_scheme_without_universal_link_is_whitelisted(self):
        allowed = allowed_schemes()
        for d in gen_readme.DIRS:
            if d["link"] is None:
                continue
            for url in sample_urls(d):
                scheme, universal = d["link"](url, "sample")
                if universal is not None:
                    continue  # 有 Universal Link 的不走跳转页
                head = scheme.split(":", 1)[0] + ":"
                with self.subTest(path=d["path"], scheme=head):
                    self.assertIn(head, allowed)

    def test_bridge_link_round_trips_the_whole_scheme(self):
        scheme = ("anywhere://add-module?link=https%3A%2F%2Fexample.com%2Fa.amod"
                  "&ignored=1#frag")
        parsed = urlsplit(gen_readme.bridge(scheme))
        self.assertEqual(f"{parsed.scheme}://{parsed.netloc}{parsed.path}",
                         gen_readme.BRIDGE)
        # 整条 scheme 必须落在单个参数里，它自带的 & 和 # 不能把跳转页的 URL 截断
        self.assertEqual(parse_qs(parsed.query), {"s": [scheme]})
        self.assertEqual(parsed.fragment, "")

    def test_anywhere_action_follows_the_file_extension(self):
        module, _ = gen_readme.anywhere_bundle("https://example.com/a.amod", "a")
        rules, _ = gen_readme.anywhere_bundle("https://example.com/a.amrs", "a")
        self.assertEqual(urlsplit(module).netloc, "add-module")
        self.assertEqual(urlsplit(rules).netloc, "add-rule-set")


class InjectTests(unittest.TestCase):
    def setUp(self):
        self.config = next(d for d in gen_readme.DIRS if d["path"] == "singbox/config")

    def rendered_block(self, root: Path) -> str:
        (root / self.config["path"]).mkdir(parents=True)
        for name in self.config["only"]:
            (root / self.config["path"] / name).write_text("{}", encoding="utf-8")
        old = (f"# 手写标题\n\n正文上半.\n\n{gen_readme.MARK_BEGIN}\n"
               f"旧内容\n{gen_readme.MARK_END}\n\n正文下半.\n")
        with patch.object(gen_readme, "ROOT", root):
            return old, gen_readme.inject(self.config, old)

    def test_injection_replaces_only_the_marked_block(self):
        with tempfile.TemporaryDirectory() as directory:
            old, new = self.rendered_block(Path(directory))
            self.assertIn("# 手写标题", new)
            self.assertIn("正文上半.", new)
            self.assertIn("正文下半.", new)
            self.assertNotIn("旧内容", new)
            self.assertIn("sing-box://import-remote-profile?url=", new)
            self.assertIn(gen_readme.BRIDGE, new)
            # 幂等：再注入一次结果不变
            with patch.object(gen_readme, "ROOT", Path(directory)):
                self.assertEqual(gen_readme.inject(self.config, new), new)
            self.assertNotEqual(old, new)

    def test_missing_marker_fails_loudly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / self.config["path"]).mkdir(parents=True)
            with patch.object(gen_readme, "ROOT", root):
                with self.assertRaises(SystemExit):
                    gen_readme.inject(self.config, "# 没有标记的手写文档\n")


if __name__ == "__main__":
    unittest.main()
