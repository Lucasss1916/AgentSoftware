"""honk 产物与 dae 配置的回归检查。

honk 没有 validate 子命令、也只能跑在 Linux 上，所以这份配置无法用官方工具离线
校验。这里卡的是能在仓库内自证的部分：出口引用不悬空、include 顺序不被打乱、
地区组正则能编译且不用 Rust regex 不支持的环视。
"""
import re
import unittest
import warnings
from pathlib import Path

import sync_rules

HONK = Path(sync_rules.ROOT) / "honk"
CONFIG = HONK / "config.dae"
TAIL = HONK / "routing-tail.dae"
BUILTIN_OUTBOUNDS = {"direct", "block"}


def defined_groups() -> list[str]:
    """config.dae 的 group 段里声明的组名，按声明顺序。"""
    text = CONFIG.read_text(encoding="utf-8")
    block = re.search(r"\ngroup \{\n(.*?)\n\}\n", text, re.S)
    assert block, "config.dae 里找不到 group 段"
    return re.findall(r"^    ([A-Za-z0-9_]+) \{$", block.group(1), re.M)


def routing_outbounds(text: str) -> set[str]:
    """一份 .dae 里 routing 段用到的全部出口（含 fallback），已剥掉 (must)。"""
    found = set()
    for body in re.findall(r"\nrouting \{\n(.*?)\n\}", text, re.S):
        found |= set(re.findall(r"->\s*([^\s#]+)", body))
        found |= set(re.findall(r"^\s*fallback:\s*([^\s#]+)", body, re.M))
    return {o.replace("(must)", "") for o in found}


class OutboundReferenceTests(unittest.TestCase):
    """出口必须是已定义的组或内置出口 —— 悬空出口会让整条规则被拒。"""

    def setUp(self):
        self.groups = set(defined_groups())

    def test_config_and_tail_outbounds_are_defined(self):
        for path in (CONFIG, TAIL):
            for outbound in routing_outbounds(path.read_text(encoding="utf-8")):
                with self.subTest(file=path.name, outbound=outbound):
                    self.assertIn(outbound, self.groups | BUILTIN_OUTBOUNDS)

    def test_generated_rule_outbounds_are_defined(self):
        rules = sorted((HONK / "rule").glob("*.dae"))
        self.assertTrue(rules, "honk/rule 下没有产物，先跑 python3 sync_rules.py")
        for path in rules:
            for outbound in routing_outbounds(path.read_text(encoding="utf-8")):
                with self.subTest(file=path.name, outbound=outbound):
                    self.assertIn(outbound, self.groups | BUILTIN_OUTBOUNDS)

    def test_outbound_table_only_names_real_groups(self):
        # 改组名时最容易漏掉的就是这张表；它一错，整个规则集静默失效。
        table = set(sync_rules.HONK_OUTBOUND.values())
        table.add(sync_rules.HONK_UNMAPPED_OUTBOUND)
        self.assertEqual(table - self.groups - BUILTIN_OUTBOUNDS, set())

    def test_nested_group_references_are_defined(self):
        block = re.search(r"\ngroup \{\n(.*?)\n\}\n", CONFIG.read_text(encoding="utf-8"), re.S)
        nested = set()
        for call in re.findall(r"filter:\s*group\(([^)]*)\)", block.group(1)):
            nested |= {arg.strip().strip("'\"") for arg in call.split(",")}
        self.assertEqual(nested - self.groups, set())

    def test_every_source_rule_set_has_a_registered_outbound(self):
        stems = {p.stem for p in (sync_rules.SRC_DIR).glob("*.list")}
        self.assertEqual(stems - set(sync_rules.HONK_OUTBOUND), set(),
                         "新规则集请在 sync_rules.py 的 HONK_OUTBOUND 里登记出口")


class IncludeOrderTests(unittest.TestCase):
    """include 顺序即规则优先级，顺序错了是静默的错路由，不会报错。"""

    def setUp(self):
        text = CONFIG.read_text(encoding="utf-8")
        block = re.search(r"\ninclude \{\n(.*?)\n\}", text, re.S)
        assert block, "config.dae 里找不到 include 段"
        self.entries = [line.strip() for line in block.group(1).splitlines()
                        if line.strip() and not line.strip().startswith("#")]

    def test_included_files_exist(self):
        for entry in self.entries:
            with self.subTest(entry=entry):
                self.assertTrue((HONK / entry).is_file())

    def test_routing_tail_is_included_last(self):
        # geosite 大表口径极宽，排在自有规则集前面会把它们整体吃掉。
        self.assertEqual(self.entries[-1], TAIL.name)

    def test_block_lists_precede_their_functional_counterparts(self):
        for blocker, functional in (("rule/SailyAds.dae", "rule/Saily.dae"),
                                    ("rule/TalktoneAds.dae", "rule/TalktoneProxy.dae")):
            with self.subTest(blocker=blocker):
                self.assertLess(self.entries.index(blocker),
                                self.entries.index(functional))

    def test_glob_would_order_blocklists_wrong(self):
        # 这条用来钉住「为什么不写 rule/*.dae」：字典序恰好把拦截列表排到后面。
        self.assertLess("rule/Saily.dae", "rule/SailyAds.dae")


class RegionFilterTests(unittest.TestCase):
    def setUp(self):
        self.patterns = re.findall(r"name\(regex:\s*'([^']*)'\)",
                                   CONFIG.read_text(encoding="utf-8"))

    def test_filters_exist_and_compile(self):
        self.assertTrue(self.patterns)
        for pattern in self.patterns:
            with self.subTest(pattern=pattern[:32]):
                # honk 把 regex: 的值包成 (?:value) 后再用 | 拼接所有候选项。
                # Python 的 re 对「(?i) 不在表达式开头」会告警，Rust 的 regex 允许
                # 行内标志出现在任意位置，所以这里只借 Python 做语法冒烟，压掉告警。
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", DeprecationWarning)
                    re.compile(f"(?:{pattern})")

    def test_filters_avoid_constructs_rust_regex_rejects(self):
        for pattern in self.patterns:
            with self.subTest(pattern=pattern[:32]):
                for construct in ("(?=", "(?!", "(?<=", "(?<!", r"\1"):
                    self.assertNotIn(construct, pattern)

    def test_filters_contain_no_comma(self):
        # name() 的参数按逗号拆候选项，正则里出现逗号会被截断（| 则不会）。
        for pattern in self.patterns:
            with self.subTest(pattern=pattern[:32]):
                self.assertNotIn(",", pattern)


class EmitHonkTests(unittest.TestCase):
    def emit(self, rules, stem="DirectDomain"):
        return sync_rules.emit_honk(rules, stem)

    def test_condition_groups_become_separate_rules(self):
        # domain / dip / pname 属于不同 condition group，写进一条会变成 AND。
        text, skipped = self.emit([
            sync_rules.Rule("DOMAIN", "a.example", []),
            sync_rules.Rule("DOMAIN-SUFFIX", "b.example", []),
            sync_rules.Rule("DOMAIN-KEYWORD", "cee", []),
            sync_rules.Rule("DOMAIN-REGEX", r"^d[0-9]+\.example$", []),
            sync_rules.Rule("IP-CIDR", "192.0.2.0/24", ["no-resolve"]),
            sync_rules.Rule("GEOIP", "CN", []),
            sync_rules.Rule("PROCESS-NAME", "curl", []),
        ])
        self.assertEqual(skipped, 0)
        body = [line.strip() for line in text.splitlines()]
        self.assertIn("full: a.example,", body)
        self.assertIn("suffix: b.example,", body)
        self.assertIn("keyword: cee,", body)
        self.assertIn(r"regex: '^d[0-9]+\.example$'", body)
        self.assertIn("192.0.2.0/24,", body)
        self.assertIn("geoip: CN", body)
        self.assertEqual(text.count("-> cn_direct"), 3)   # domain / dip / pname 各一条
        self.assertIn("pname(curl) -> cn_direct", text)
        self.assertIn("no-resolve", text.splitlines()[2])  # 丢弃条数写在文件头

    def test_unsupported_types_are_skipped_and_counted(self):
        rules = [sync_rules.Rule(kind, value, []) for kind, value in (
            ("USER-AGENT", "Example*"), ("URL-REGEX", "^https://"), ("ASN", "64500"))]
        text, skipped = self.emit(rules)
        self.assertEqual(skipped, 3)
        self.assertNotIn("routing {", text)
        self.assertIn("3 条规则 honk 没有对应匹配函数", text)

    def test_values_with_separators_are_quoted(self):
        self.assertEqual(sync_rules._honk_arg("plain-value.com"), "plain-value.com")
        self.assertEqual(sync_rules._honk_arg("a,b"), "'a,b'")
        self.assertEqual(sync_rules._honk_arg("a->b"), "'a->b'")
        self.assertEqual(sync_rules._honk_arg("it's"), '"it\'s"')
        # 两种引号都出现时 dae 无从表达（引号内没有转义语法）
        self.assertIsNone(sync_rules._honk_arg("""a'b"c"""))

    def test_unquotable_value_is_skipped_with_a_note(self):
        text, skipped = self.emit([sync_rules.Rule("DOMAIN-REGEX", """a'b"c""", [])])
        self.assertEqual(skipped, 1)
        self.assertIn("同时含单双引号", text)

    def test_unregistered_rule_set_is_flagged(self):
        text, _ = self.emit([sync_rules.Rule("DOMAIN-SUFFIX", "a.example", [])],
                            stem="BrandNewSet")
        self.assertIn(f"-> {sync_rules.HONK_UNMAPPED_OUTBOUND}", text)
        self.assertIn("未在 HONK_OUTBOUND 登记", text)

    def test_registered_rule_set_has_no_warning(self):
        text, _ = self.emit([sync_rules.Rule("DOMAIN-SUFFIX", "a.example", [])],
                            stem="SailyAds")
        self.assertIn("-> block", text)
        self.assertNotIn("未在 HONK_OUTBOUND 登记", text)


if __name__ == "__main__":
    unittest.main()
