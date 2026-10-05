"""Clash 配置引用、分流顺序和覆写隔离回归检查。"""
import importlib.util
import json
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLASH = ROOT / "clash" / "yaml"
spec = importlib.util.spec_from_file_location("clash_gen", CLASH / "gen.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class ClashConfigTest(unittest.TestCase):
    def test_references_and_core_types(self):
        for filename, kind in [("urltest.yaml", "url-test"), ("smart.yaml", "smart")]:
            config = yaml.safe_load((CLASH / filename).read_text())
            groups = {group["name"]: group for group in config["proxy-groups"]}
            self.assertEqual(len(groups), len(config["proxy-groups"]))
            targets = set(groups) | {"DIRECT", "REJECT"}
            for group in groups.values():
                self.assertTrue(set(group.get("proxies", [])) <= targets)
            for name, _ in generator.REGIONS:
                self.assertEqual(groups[name]["type"], kind)
            for rule in config["rules"]:
                parts = rule.split(",")
                target = parts[-2] if parts[-1] == "no-resolve" else parts[-1]
                self.assertIn(target, targets)
                if parts[0] == "RULE-SET":
                    self.assertIn(parts[1], config["rule-providers"])
            for key in config["dns"]["nameserver-policy"]:
                if key.startswith("rule-set:"):
                    provider = config["rule-providers"][key.removeprefix("rule-set:")]
                    self.assertEqual(provider["behavior"], "domain")

    def test_exceptions_precede_general_rules(self):
        config = yaml.safe_load((CLASH / "urltest.yaml").read_text())
        rules = config["rules"]
        for specific, general in [
            ("DOMAIN-SUFFIX,fnos.991600.xyz,✈️ 节点选择", "DOMAIN-SUFFIX,991600.xyz,🍿 国外媒体"),
            ("DOMAIN-SUFFIX,testflight.apple.com,🍿 国外媒体", "RULE-SET,Apple,🍎 苹果服务,no-resolve"),
            ("RULE-SET,TalktoneAds,REJECT", "RULE-SET,Proxy,🍿 国外媒体,no-resolve"),
            ("RULE-SET,MyVideo,🎥 视频", "RULE-SET,GlobalMedia,🍿 国外媒体,no-resolve"),
        ]:
            self.assertLess(rules.index(specific), rules.index(general))
        smart = yaml.safe_load((CLASH / "smart.yaml").read_text())
        self.assertEqual(rules, smart["rules"])
        self.assertEqual(config["dns"], smart["dns"])
        self.assertEqual(rules[-1], "MATCH,🐟漏网之鱼")

    def test_js_preserves_subscription_and_client_settings(self):
        config = yaml.safe_load((CLASH / "urltest.yaml").read_text())
        # 通过生成器检查覆写边界，无需依赖 Node 安装来运行仓库 CI。
        script = generator.build_js(yaml.safe_dump(config), "test")
        override = json.loads(script.split("const override = ", 1)[1].split(";\n", 1)[0])
        for key in ["proxies", "proxy-providers", "external-controller", "secret", "mixed-port"]:
            self.assertNotIn(key, override)

if __name__ == "__main__":
    unittest.main()
