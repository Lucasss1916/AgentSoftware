#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 loon/rule/*.list 同步为各代理客户端的规则格式。

loon/rule 是全仓库唯一的规则源，其余规则目录均由本脚本生成，请勿手工编辑。

用法：
    python3 sync_rules.py            # 同步全部格式
    python3 sync_rules.py --check    # 只校验不写入（CI 用，不一致时退出码非 0）

输出：
    clash/rule/*.yaml     Clash / mihomo   (payload: 结构，behavior: classical)
    quanx/rule/*.list     Quantumult X     (HOST 系写法)
    Egern/rule/*.yaml     Egern            (xxx_set 分组)
    singbox/rule/*.json   sing-box         (rule-set source v2)
    Surge/rule/*.list     Surge            (与 Loon 语法基本一致)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "loon" / "rule"

# ---------------------------------------------------------------- 规则类型表
#
# 单一事实来源：新增规则类型只需在这里加一行，五种格式同时生效。
# 值为 None 表示该格式无法表达此类型，会被显式统计为跳过，而不是静默丢弃。
#
TYPES: dict[str, dict[str, str | None]] = {
    "DOMAIN":         {"clash": "DOMAIN",         "qx": "HOST",         "egern": "domain_set",         "singbox": "domain",         "surge": "DOMAIN"},
    "DOMAIN-SUFFIX":  {"clash": "DOMAIN-SUFFIX",  "qx": "HOST-SUFFIX",  "egern": "domain_suffix_set",  "singbox": "domain_suffix",  "surge": "DOMAIN-SUFFIX"},
    "DOMAIN-KEYWORD": {"clash": "DOMAIN-KEYWORD", "qx": "HOST-KEYWORD", "egern": "domain_keyword_set", "singbox": "domain_keyword", "surge": "DOMAIN-KEYWORD"},
    "DOMAIN-REGEX":   {"clash": "DOMAIN-REGEX",   "qx": None,           "egern": "domain_regex_set",   "singbox": "domain_regex",   "surge": None},
    "IP-CIDR":        {"clash": "IP-CIDR",        "qx": "IP-CIDR",      "egern": "ip_cidr_set",        "singbox": "ip_cidr",        "surge": "IP-CIDR"},
    "IP-CIDR6":       {"clash": "IP-CIDR6",       "qx": "IP6-CIDR",     "egern": "ip_cidr6_set",       "singbox": "ip_cidr",        "surge": "IP-CIDR6"},
    "GEOIP":          {"clash": "GEOIP",          "qx": "GEOIP",        "egern": "geoip_set",          "singbox": None,             "surge": "GEOIP"},
    "ASN":            {"clash": "IP-ASN",         "qx": None,           "egern": "asn_set",            "singbox": None,             "surge": "IP-ASN"},
    "PROCESS-NAME":   {"clash": "PROCESS-NAME",   "qx": None,           "egern": None,                 "singbox": "process_name",   "surge": "PROCESS-NAME"},
    "USER-AGENT":     {"clash": "USER-AGENT",     "qx": "USER-AGENT",   "egern": None,                 "singbox": None,             "surge": "USER-AGENT"},
    "URL-REGEX":      {"clash": None,             "qx": "URL-REGEX",    "egern": "url_regex_set",      "singbox": None,             "surge": "URL-REGEX"},
}

# 别名 → 标准类型。QX 的 HOST 系写法与旧脚本的下划线误写都在这里归一。
ALIASES = {
    "HOST": "DOMAIN",
    "HOST-SUFFIX": "DOMAIN-SUFFIX",
    "HOST-KEYWORD": "DOMAIN-KEYWORD",
    "IP6-CIDR": "IP-CIDR6",
    "DOMAIN_KEYWORD": "DOMAIN-KEYWORD",   # 旧转换脚本的错误拼写，兼容历史数据
    "DOMAIN_SUFFIX": "DOMAIN-SUFFIX",
    "IP_CIDR": "IP-CIDR",
}

# 只有 IP 类规则带 no-resolve 才有意义
IP_TYPES = {"IP-CIDR", "IP-CIDR6", "GEOIP", "ASN"}


class Rule:
    __slots__ = ("type", "value", "extras")

    def __init__(self, rtype: str, value: str, extras: list[str]):
        self.type = rtype
        self.value = value
        self.extras = extras

    @property
    def no_resolve(self) -> bool:
        return any(e.lower() == "no-resolve" for e in self.extras)


def parse_source(path: Path) -> tuple[list[Rule], list[str]]:
    """解析一个 .list 源文件，返回 (规则, 告警)。"""
    rules: list[Rule] = []
    warnings: list[str] = []
    seen: set[tuple[str, str]] = set()

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        # 剥掉行尾注释；正则类规则可能含 # ，故排除
        if "#" in line and not line.upper().startswith(("URL-REGEX", "DOMAIN-REGEX")):
            line = line.split("#", 1)[0].strip()
        if not line:
            continue

        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            warnings.append(f"{path.name}:{lineno} 参数不足，已跳过： {line}")
            continue

        rtype = ALIASES.get(parts[0].upper(), parts[0].upper())
        if rtype not in TYPES:
            warnings.append(f"{path.name}:{lineno} 未知规则类型 {parts[0]}，已跳过")
            continue

        value = parts[1]
        if not value:
            warnings.append(f"{path.name}:{lineno} 值为空，已跳过： {line}")
            continue

        key = (rtype, value)
        if key in seen:
            continue                     # 同文件内重复，静默去重
        seen.add(key)
        rules.append(Rule(rtype, value, parts[2:]))

    return rules, warnings


# ---------------------------------------------------------------- 各格式输出
# 每个 emit_* 返回 (文本内容, 跳过条数)


def _flat(rules: list[Rule], fmt: str) -> tuple[list[str], int]:
    """行式格式（clash / qx / surge）的共同逻辑。"""
    lines, skipped = [], 0
    for r in rules:
        t = TYPES[r.type][fmt]
        if t is None:
            skipped += 1
            continue
        suffix = ",no-resolve" if (r.no_resolve and r.type in IP_TYPES) else ""
        lines.append(f"{t},{r.value}{suffix}")
    return lines, skipped


def emit_clash(rules: list[Rule]) -> tuple[str, int]:
    lines, skipped = _flat(rules, "clash")
    return "\n".join(["payload:"] + [f"  - {l}" for l in lines]) + "\n", skipped


def emit_qx(rules: list[Rule]) -> tuple[str, int]:
    lines, skipped = _flat(rules, "qx")
    return "\n".join(lines) + "\n", skipped


def emit_surge(rules: list[Rule]) -> tuple[str, int]:
    lines, skipped = _flat(rules, "surge")
    return "\n".join(lines) + "\n", skipped


def _grouped(rules: list[Rule], fmt: str) -> tuple[dict[str, list[str]], int]:
    """分组格式（egern / singbox）的共同逻辑。"""
    buckets: dict[str, list[str]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    skipped = 0
    for r in rules:
        field = TYPES[r.type][fmt]
        if field is None:
            skipped += 1
            continue
        key = (field, r.value)
        if key in seen:
            continue
        seen.add(key)
        buckets[field].append(r.value)
    return {k: buckets[k] for k in sorted(buckets)}, skipped


def emit_egern(rules: list[Rule]) -> tuple[str, int]:
    buckets, skipped = _grouped(rules, "egern")
    if not buckets:
        return "{}\n", skipped
    return yaml.dump(buckets, allow_unicode=True, sort_keys=False,
                     default_flow_style=False), skipped


def emit_singbox(rules: list[Rule]) -> tuple[str, int]:
    buckets, skipped = _grouped(rules, "singbox")
    payload = {"version": 2, "rules": [buckets] if buckets else []}
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n", skipped


TARGETS = [
    ("clash",   Path("clash")   / "rule", ".yaml", emit_clash),
    ("quanx",   Path("quanx")   / "rule", ".list", emit_qx),
    ("Egern",   Path("Egern")   / "rule", ".yaml", emit_egern),
    ("singbox", Path("singbox") / "rule", ".json", emit_singbox),
    ("Surge",   Path("Surge")   / "rule", ".list", emit_surge),
]

# 这些文件只存在于个别客户端、不由 loon/rule 生成，同步时不得删除。
KEEP = {
    "quanx/rule": {"GFWRules.list"},
    "Egern/rule": {"GFWRules.yaml"},
}


def main() -> int:
    ap = argparse.ArgumentParser(description="把 loon/rule 同步到各客户端格式")
    ap.add_argument("--check", action="store_true",
                    help="只校验产物是否与源一致，不写入（CI 用）")
    args = ap.parse_args()

    sources = sorted(SRC_DIR.glob("*.list"))
    if not sources:
        print(f"错误：源目录没有 .list 文件：{SRC_DIR}", file=sys.stderr)
        return 1

    all_warnings: list[str] = []
    stale: list[str] = []
    total = 0
    skip_stat: dict[str, int] = defaultdict(int)

    print(f"源：loon/rule（{len(sources)} 个文件）\n")
    header = f"{'规则文件':<30}{'条数':>6}   " + "  ".join(f"{n:>10}" for n, _, _, _ in TARGETS)
    print(header)
    print("-" * len(header))

    for src in sources:
        rules, warnings = parse_source(src)
        all_warnings.extend(warnings)
        total += len(rules)

        cells = []
        for name, out_dir, ext, emit in TARGETS:
            text, skipped = emit(rules)
            skip_stat[name] += skipped
            dst = ROOT / out_dir / f"{src.stem}{ext}"

            if args.check:
                if not dst.exists() or dst.read_text(encoding="utf-8") != text:
                    stale.append(str(dst.relative_to(ROOT)))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(text, encoding="utf-8")

            kept = len(rules) - skipped
            cells.append(f"{kept:>10}" if not skipped else f"{kept:>6}(-{skipped:<3})")
        print(f"{src.stem:<30}{len(rules):>6}   " + "  ".join(cells))

    print("-" * len(header))
    print(f"{'合计':<30}{total:>6}")

    # 清理源已删除、产物还留着的文件
    valid = {s.stem for s in sources}
    for name, out_dir, ext, _ in TARGETS:
        d = ROOT / out_dir
        if not d.is_dir():
            continue
        keep = KEEP.get(out_dir.as_posix(), set())
        for f in sorted(d.glob(f"*{ext}")):
            if f.stem in valid or f.name in keep or f.name == "README.md":
                continue
            if args.check:
                stale.append(f"{f.relative_to(ROOT)}（源已删除，应移除）")
            else:
                f.unlink()
                print(f"  已删除孤立产物：{f.relative_to(ROOT)}")

    if any(skip_stat.values()):
        print("\n跳过统计（目标格式无对应字段，属预期行为）：")
        for name, n in skip_stat.items():
            if n:
                print(f"  {name:<10} 跳过 {n} 条")

    if all_warnings:
        print(f"\n源文件告警（{len(all_warnings)} 条）：")
        for w in all_warnings[:20]:
            print(f"  {w}")
        if len(all_warnings) > 20:
            print(f"  … 另有 {len(all_warnings) - 20} 条")

    if args.check:
        if stale:
            print(f"\n校验失败：{len(stale)} 个产物与源不一致，"
                  f"请本地运行 python3 sync_rules.py 后提交", file=sys.stderr)
            for s in stale[:20]:
                print(f"  {s}", file=sys.stderr)
            return 1
        print("\n校验通过：所有产物与源一致")
        return 1 if all_warnings else 0

    print("\n同步完成")
    return 1 if all_warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
