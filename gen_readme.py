#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为各客户端目录生成 README：原始订阅地址 + 一键导入链接。

原先这段逻辑写在 workflow 的内联 shell 里，只会吐一串裸 URL。
挪到脚本里是为了能按客户端拼各自的 URL Scheme，并且本地可先跑一遍看效果。

用法：
    python3 gen_readme.py            # 重新生成
    python3 gen_readme.py --check    # 只校验（CI 用，不一致退出码非 0）

注意 clash/yaml 与 singbox/config 不在此列 —— 那两处是手写说明文档。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
RAW = "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main"


def enc(url: str) -> str:
    return quote(url, safe="")


# ------------------------------------------------------------------ 各家 Scheme
#
# 均取自官方文档：
#   Loon      https://nsloon.app/docs/Scheme/
#   Egern     https://egernapp.com/docs/url-scheme/
#   Surge     https://manual.nssurge.com/tools/url-scheme.html
#   QX        https://github.com/crossutility/Quantumult-X/blob/master/url-scheme.md
#
# 返回 (scheme_url, universal_url | None)。universal 为 None 表示该客户端
# 没有 Universal Link，只能复制 scheme 手动打开 —— GitHub 会把非 http(s)
# 链接过滤掉，所以这类只能以代码块形式展示，无法做成可点击的。


def loon(kind: str):
    def f(url: str, name: str):
        s = f"loon://import?{kind}={enc(url)}"
        return s, s.replace("loon://", "https://www.nsloon.com/openloon/")
    return f


def egern_module(url: str, name: str):
    q = f"modules/new?name={quote(name)}&url={enc(url)}"
    return f"egern:/{q}", f"https://egernapp.com/{q}"


def egern_ruleset(url: str, name: str):
    q = f"rules/new?type=rule_set&match={enc(url)}"
    return f"egern:/{q}", f"https://egernapp.com/{q}"


def surge(action: str):
    def f(url: str, name: str):
        return f"surge:///{action}?url={enc(url)}", None
    return f


def quanx(field: str):
    def f(url: str, name: str):
        payload = json.dumps({field: [f"{url}, tag={name}"]}, ensure_ascii=False)
        q = f"add-resource?remote-resource={enc(payload)}"
        return f"quantumult-x:///{q}", f"https://quantumult.app/x/open-app/{q}"
    return f


# ------------------------------------------------------------------ 目录配置
#
# ext:    参与生成的扩展名；None 表示除 README 外全收
# link:   拼导入链接的函数；None 表示该客户端没有对应的导入 Scheme，
#         只列原始地址（例如 Surge 只能导入配置和模块，规则集得手动写 RULE-SET）
# note:   写在表格下方的补充说明
#
DIRS: list[dict] = [
    {
        "path": "loon/rule",
        "title": "Loon 规则集",
        "ext": [".list"],
        "link": loon("rules"),
        "note": "本目录是全仓库唯一的规则源，其余客户端的规则由 `sync_rules.py` 从这里生成。",
    },
    {
        "path": "loon/plugin",
        "title": "Loon 插件",
        "ext": [".plugin"],
        "link": loon("plugin"),
        "note": "`redirectTG.js` 是插件内部引用的脚本，不单独导入，故不在表内。",
    },
    {
        "path": "quanx/rule",
        "title": "Quantumult X 分流规则",
        "ext": [".list"],
        "link": quanx("filter_remote"),
        "note": "导入后需在 QX 里给该资源指定策略（`force-policy`），链接中未预设。",
    },
    {
        "path": "quanx/rewrite",
        "title": "Quantumult X 重写脚本",
        "ext": None,
        "link": None,
        "note": "这些是 `.js` 脚本本体而非 rewrite 片段，需在脚本头部注释所示的"
                " `[rewrite_local]` 里引用，不能直接作为资源导入。",
    },
    {
        "path": "quanx/task",
        "title": "Quantumult X 定时任务",
        "ext": None,
        "link": None,
        "note": "任务脚本需在 QX 的 `[task_local]` 中配置 cron 后引用。",
    },
    {
        "path": "Egern/rule",
        "title": "Egern 规则集",
        "ext": [".yaml"],
        "link": egern_ruleset,
        "note": "导入后需在 Egern 里为该规则集选择策略。",
    },
    {
        "path": "Egern/module",
        "title": "Egern 模块",
        "ext": [".yaml"],
        "link": egern_module,
        "note": "含 MITM 的模块导入后，还需在「工具 → 证书」生成并信任证书才会生效。",
    },
    {
        "path": "Surge/config",
        "title": "Surge 配置",
        "ext": [".conf"],
        "link": surge("install-config"),
        "note": "`test.list` 是配置引用的规则文件，不单独导入。",
    },
    {
        "path": "Surge/module",
        "title": "Surge 模块",
        "ext": [".sgmodule"],
        "link": surge("install-module"),
        "note": None,
    },
    {
        "path": "Surge/rule",
        "title": "Surge 规则集",
        "ext": None,
        "link": None,
        "note": "Surge 的 URL Scheme 只支持导入配置和模块，规则集需手动写进配置的"
                " `[Rule]` 段：`RULE-SET,<地址>,<策略>`。",
    },
    {
        "path": "Surge/boxjs",
        "title": "Surge BoxJS 订阅",
        "ext": None,
        "link": None,
        "note": "在 BoxJS 的「订阅」页面粘贴地址添加。",
    },
    {
        "path": "clash/rule",
        "title": "Clash / mihomo 规则集",
        "ext": None,
        "link": None,
        "note": "Clash 系没有导入单个规则集的 Scheme，需写进主配置的 `rule-providers`"
                "（`behavior: classical` + `format: yaml`）。主配置见 [`clash/yaml`](../yaml/README.md)。",
    },
    {
        "path": "singbox/rule",
        "title": "sing-box 规则集",
        "ext": None,
        "link": None,
        "note": "sing-box 没有导入单个规则集的 Scheme，需写进主配置的 `route.rule_set`"
                "（`type: remote` + `format: source`）。主配置见 [`singbox/config`](../config/README.md)。",
    },
]

HEAD = "| 文件 | 一键导入 | 原始地址 |\n| --- | --- | --- |\n"
HEAD_NOLINK = "| 文件 | 原始地址 |\n| --- | --- |\n"


def files_of(d: dict) -> list[Path]:
    p = ROOT / d["path"]
    out = []
    for f in sorted(p.iterdir()):
        if not f.is_file() or f.name == "README.md":
            continue
        if d["ext"] is not None and f.suffix not in d["ext"]:
            continue
        out.append(f)
    return out


def render(d: dict) -> str:
    lines = [f"# {d['title']}", ""]
    rows, schemes = [], []

    for f in files_of(d):
        rel = f"{d['path']}/{f.name}"
        url = f"{RAW}/{rel}"
        if d["link"] is None:
            rows.append(f"| `{f.name}` | <{url}> |")
            continue
        scheme, universal = d["link"](url, f.stem)
        cell = f"[导入]({universal})" if universal else f"[导入](#) 见下"
        if not universal:
            cell = "见下方 Scheme"
            schemes.append((f.name, scheme))
        rows.append(f"| `{f.name}` | {cell} | <{url}> |")

    lines.append(HEAD_NOLINK if d["link"] is None else HEAD)
    lines[-1] += "\n".join(rows)
    lines.append("")

    if schemes:
        lines += [
            "以上「导入」需手动复制下面的 URL Scheme 到地址栏或快捷指令打开"
            "（GitHub 会过滤非 http(s) 链接，做不成可点击的）：",
            "",
            "```",
            *[f"{n}\n{s}" for n, s in schemes],
            "```",
            "",
        ]

    if d["note"]:
        lines += [f"> {d['note']}", ""]

    lines += [
        "<sub>本文件由 `gen_readme.py` 生成，勿直接编辑。</sub>",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    bad = 0
    for d in DIRS:
        p = ROOT / d["path"]
        if not p.is_dir():
            continue
        target = p / "README.md"
        text = render(d)
        if args.check:
            old = target.read_text(encoding="utf-8") if target.exists() else ""
            if old != text:
                print(f"✗ {target.relative_to(ROOT)} 与源不一致，请跑 python3 gen_readme.py")
                bad += 1
        else:
            target.write_text(text, encoding="utf-8")
            print(f"✓ {target.relative_to(ROOT)}  ({len(files_of(d))} 个文件)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
