#!/usr/bin/env python3
"""把仓库里的 Clash/Loon `.list`/`.yaml` 规则文件转换为 sing-box rule-set JSON。

用法：
    python3 convert_clash_to_singbox.py <input> [-o <output.json>]
    python3 convert_clash_to_singbox.py loon/rule/                 # 批处理目录

生成的 JSON 是 sing-box `rule-set` 的 source 形式 (version 2)，可直接挂到
`route.rule_set` 的 `type: local` 项；也可用 `sing-box rule-set compile` 编为
`.srs` 二进制后再挂 `type: remote`/`type: local` 用。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 支持的 Clash/Loon 规则字段
SUPPORTED = {
    "DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-REGEX",
    "IP-CIDR", "IP-CIDR6", "PROCESS-NAME", "PROCESS-PATH",
    "URL-REGEX", "USER-AGENT", "SRC-IP-CIDR",
}

# Clash 字段 → sing-box 字段
FIELD_MAP = {
    "DOMAIN": "domain",
    "DOMAIN-SUFFIX": "domain_suffix",
    "DOMAIN-KEYWORD": "domain_keyword",
    "DOMAIN-REGEX": "domain_regex",
    "IP-CIDR": "ip_cidr",
    "IP-CIDR6": "ip_cidr",
    "PROCESS-NAME": "process_name",
    "PROCESS-PATH": "process_path",
    "SRC-IP-CIDR": "source_ip_cidr",
}

PAYLOAD_PREFIX = re.compile(r"^\s*-\s*")


def parse_lines(text: str) -> list[str]:
    """把 list/yaml 文本展开为单行规则。

    - YAML 形如 `payload: [...]` 也能识别（剥掉前缀的 `- `）
    - 注释/空行被忽略
    """
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.lower().startswith("payload:"):
            continue
        line = PAYLOAD_PREFIX.sub("", line)
        # 剥掉行尾注释
        if "#" in line and not line.startswith("DOMAIN-REGEX"):
            line = line.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def to_singbox(rules: list[str]) -> dict:
    buckets: dict[str, list[str]] = {}
    skipped: list[str] = []
    for rule in rules:
        parts = [p.strip() for p in rule.split(",")]
        head = parts[0].upper()
        if head not in SUPPORTED:
            skipped.append(rule)
            continue
        if len(parts) < 2:
            skipped.append(rule)
            continue
        value = parts[1]
        target_field = FIELD_MAP.get(head)
        if target_field is None:
            # URL-REGEX / USER-AGENT 在 sing-box 没有等价字段，跳过
            skipped.append(rule)
            continue
        buckets.setdefault(target_field, []).append(value)

    # 去重 + 保序
    rule_obj: dict[str, list[str]] = {}
    for field, values in buckets.items():
        seen = set()
        unique = []
        for v in values:
            if v not in seen:
                seen.add(v)
                unique.append(v)
        rule_obj[field] = unique

    payload = {"version": 2, "rules": [rule_obj] if rule_obj else []}
    if skipped:
        payload["_skipped"] = skipped  # 仅供人工排查，sing-box 会忽略未知键
    return payload


def convert_file(src: Path, dst: Path) -> tuple[int, int]:
    text = src.read_text(encoding="utf-8")
    rules = parse_lines(text)
    payload = to_singbox(rules)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rule_count = sum(len(v) for k, v in (payload["rules"][0] if payload["rules"] else {}).items()
                     if isinstance(v, list))
    return rule_count, len(payload.get("_skipped", []))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="单个 .list/.yaml 文件 或 目录")
    ap.add_argument("-o", "--output", type=Path, help="输出 .json 路径（仅单文件时）")
    ap.add_argument("--out-dir", type=Path, default=Path("singbox/rule"),
                    help="批处理时的输出目录（默认 singbox/rule）")
    args = ap.parse_args()

    src: Path = args.input
    if src.is_dir():
        files = sorted([p for p in src.iterdir() if p.suffix.lower() in {".list", ".yaml"}])
        if not files:
            print(f"目录中没有 .list/.yaml 文件: {src}", file=sys.stderr)
            return 1
        for f in files:
            out = args.out_dir / (f.stem + ".json")
            n, skipped = convert_file(f, out)
            print(f"  {f.name:30s} -> {out}  ({n} 条, 跳过 {skipped})")
        return 0
    else:
        out = args.output or args.out_dir / (src.stem + ".json")
        n, skipped = convert_file(src, out)
        print(f"{src} -> {out}  ({n} 条, 跳过 {skipped})")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
