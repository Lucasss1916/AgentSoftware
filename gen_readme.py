#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为各客户端目录生成 README：原始订阅地址 + 一键导入链接。

原先这段逻辑写在 workflow 的内联 shell 里，只会吐一串裸 URL。
挪到脚本里是为了能按客户端拼各自的 URL Scheme，并且本地可先跑一遍看效果。

用法：
    python3 gen_readme.py            # 重新生成
    python3 gen_readme.py --check    # 只校验（CI 用，不一致退出码非 0）

clash/yaml 与 singbox/config 是手写说明文档，只把导入表格注入到其中的
`<!-- gen:import -->` 标记块里，正文不动。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
RAW = "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main"

# 自建跳转页。GitHub 会过滤非 http(s) 链接，没有 Universal Link 的客户端
# （Surge、Anywhere、Clash、sing-box）只能先点到这个 https 页面，再由它
# location.replace 到真正的 scheme。源文件是 docs/import.html，需要在仓库
# Settings → Pages 把源设为 main 分支的 /docs 目录才会生效。
BRIDGE = "https://lucasss1916.github.io/AgentSoftware/import.html"

# 注入模式的标记；手写 README 里成对出现，中间的内容由本脚本接管。
MARK_BEGIN = "<!-- gen:import -->"
MARK_END = "<!-- /gen:import -->"


def enc(url: str) -> str:
    return quote(url, safe="")


def bridge(scheme: str) -> str:
    return f"{BRIDGE}?s={enc(scheme)}"


# ------------------------------------------------------------------ 各家 Scheme
#
# 均取自官方文档：
#   Loon      https://nsloon.app/docs/Scheme/
#   Egern     https://egernapp.com/docs/url-scheme/
#   Surge     https://manual.nssurge.com/tools/url-scheme.html
#   QX        https://github.com/crossutility/Quantumult-X/blob/master/url-scheme.md
#   Anywhere  https://github.com/NodePassProject/Anywhere#deep-links
#   Surge     https://manual.nssurge.com/tools/url-scheme.html
#   mihomo    Clash Party（原 Mihomo Party）的 mihomo://install-config
#   sing-box  官方 SFI / SFM / SFA 的 sing-box://import-remote-profile
#
# 返回 (scheme_url, universal_url | None)。universal 为 None 表示该客户端
# 没有 Universal Link，这类链接由 docs/import.html 跳转页代为唤起。


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


def anywhere_ruleset(url: str, name: str):
    return f"anywhere://add-rule-set?link={enc(url)}", None


def anywhere_bundle(url: str, name: str):
    # 同一目录混放 .amod（模块）与 .amrs（MITM 规则集），按扩展名分派动作。
    action = "add-module" if url.endswith(".amod") else "add-rule-set"
    return f"anywhere://{action}?link={enc(url)}", None


def mihomo_config(url: str, name: str):
    # ClashX 系把协议头换成 clash:// 即可，参数相同。
    return f"mihomo://install-config?url={enc(url)}&name=AgentSoftware-{name}", None


def singbox_profile(url: str, name: str):
    # 井号后面是配置在客户端里的显示名；本目录只有一份配置，沿用原来的 AgentSoftware。
    return f"sing-box://import-remote-profile?url={enc(url)}#AgentSoftware", None


# ------------------------------------------------------------------ 目录配置
#
# ext:    参与生成的扩展名；None 表示除 README 外全收
# only:   只收这几个文件名，按给定顺序；给了就不看 ext（目录里混着源文件和产物时用）
# link:   拼导入链接的函数；None 表示该客户端没有对应的导入 Scheme，
#         只列原始地址（例如 Surge 只能导入配置和模块，规则集得手动写 RULE-SET）
# inject: True 表示 README 由人手写，只替换 `<!-- gen:import -->` 标记块里的内容
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
        "path": "clash/yaml",
        "title": "Clash / mihomo 主配置",
        "ext": None,
        "only": ["urltest.yaml", "smart.yaml"],
        "link": mihomo_config,
        "inject": True,
        "note": "`mihomo://` 是 Clash Party（原 Mihomo Party）的 Scheme，ClashX 系把协议头换成"
                " `clash://` 即可。其余客户端（ClashMeta for Android、Stash 等）直接粘贴原始地址。"
                "目录里其他文件是生成源或备查件，不单独导入。",
    },
    {
        "path": "clash/rule",
        "title": "Clash / mihomo 规则集",
        "ext": None,
        "link": None,
        "note": "Clash 系没有导入单个规则集的 Scheme，需写进主配置的 `rule-providers`"
                "（`behavior: classical` + `format: yaml`）。主配置见 [`clash/yaml`](../yaml/README.md)，"
                "那两份已经把本目录全部引用好了，一键导入主配置即可。",
    },
    {
        "path": "singbox/config",
        "title": "sing-box 主配置",
        "ext": None,
        "only": ["config.json"],
        "link": singbox_profile,
        "inject": True,
        "note": "官方 SFI / SFM / SFA 均支持。导入的是**不含节点的模板**，"
                "需按本页「填入机场节点」一节补上节点才会真正走代理。",
    },
    {
        "path": "singbox/rule",
        "title": "sing-box 规则集",
        "ext": None,
        "link": None,
        "note": "sing-box 没有导入单个规则集的 Scheme，需写进主配置的 `route.rule_set`"
                "（`type: remote` + `format: source`）。主配置见 [`singbox/config`](../config/README.md)。",
    },
    {
        "path": "anywhere/rule",
        "title": "Anywhere 分流规则",
        "ext": [".arrs"],
        "link": anywhere_ruleset,
        "note": "本目录由 `loon/rule/*.list` 自动生成，每个 `.arrs` 文件是一个可独立订阅的规则集。"
                "在 Anywhere 的「分流 / Routing」页面用原始地址添加订阅，或复制上方对应 Scheme 导入；"
                "文件名会作为默认规则集名称。请使用规则模式，并按用途为每个规则集选择"
                " DIRECT、REJECT、PROXY 或具体节点 / 链；订阅刷新会保留本地名称与策略。"
                "转换差异与更新方法见[仓库说明](../../README.md#anywhere-规则订阅)。",
    },
    {
        "path": "anywhere/module",
        "title": "Anywhere 模块与 MITM 规则集",
        "ext": [".amod", ".amrs"],
        "link": anywhere_bundle,
        "note": "`.amod` 是模块（打包了分流 + MITM 规则集，走 `add-module`），"
                "`.amrs` 是单独的 MITM 规则集（走 `add-rule-set`）；两者导入前都会先给预览。"
                "同名的 `.amod` 与 `.amrs` 是同一套改写的两种投递方式，**按需选一个**，别都装。"
                "含 MITM 的内容生效前需在 Anywhere 里开启 TLS 解密并信任证书。"
                "`Duolingo_Max_解锁.amrs.txt` 后缀不是 `.amrs`，Anywhere 拒收，故不在表内。",
    },
    {
        "path": "honk",
        "title": "honk 主配置",
        "ext": None,
        "only": ["config.dae", "routing-tail.dae"],
        "link": None,
        "inject": True,
        "note": "honk 是 Linux 守护进程，用 `-c` 读本地文件，没有 URL Scheme 可一键导入。"
                "`config.dae` 是入口，`routing-tail.dae` 由它的 `include` 块引入且必须排在最后。"
                "两份都是手写的，不由脚本生成。",
    },
    {
        "path": "honk/rule",
        "title": "honk 规则集",
        "ext": [".dae"],
        "link": None,
        "note": "honk 不支持远程规则集（只认 `geosite:`/`geoip:` 的 dat 文件加内联 `domain()`），"
                "所以这些是预编译好的 dae `routing` 片段，出口已写在文件里，"
                "由 [`honk/config.dae`](../README.md) 的 `include` 块按顺序引入 —— "
                "顺序即优先级，默认只引入 Clash 侧实际在用的 8 个。"
                "出口对应关系见 `sync_rules.py` 的 `HONK_OUTBOUND` 表。",
    },
]

HEAD = "| 文件 | 一键导入 | 原始地址 |\n| --- | --- | --- |\n"
HEAD_NOLINK = "| 文件 | 原始地址 |\n| --- | --- |\n"


def files_of(d: dict) -> list[Path]:
    p = ROOT / d["path"]
    if d.get("only"):
        return [p / n for n in d["only"] if (p / n).is_file()]
    out = []
    for f in sorted(p.iterdir()):
        # 点文件（.DS_Store 等）不是规则，且 .gitignore 已忽略 —— 列进来只会让 CI 与本地打架
        if not f.is_file() or f.name == "README.md" or f.name.startswith("."):
            continue
        if d["ext"] is not None and f.suffix not in d["ext"]:
            continue
        out.append(f)
    return out


def body(d: dict) -> list[str]:
    """导入表格那一段：整份生成和注入模式共用。"""
    lines = []
    rows, schemes = [], []

    for f in files_of(d):
        rel = f"{d['path']}/{f.name}"
        url = f"{RAW}/{rel}"
        if d["link"] is None:
            rows.append(f"| `{f.name}` | <{url}> |")
            continue
        scheme, universal = d["link"](url, f.stem)
        # 没有 Universal Link 的走自建跳转页，这样 GitHub 上一样是可点的。
        rows.append(f"| `{f.name}` | [导入]({universal or bridge(scheme)}) | <{url}> |")
        if not universal:
            schemes.append((f.name, scheme))

    lines.append(HEAD_NOLINK if d["link"] is None else HEAD)
    lines[-1] += "\n".join(rows)
    lines.append("")

    if schemes:
        lines += [
            f"上面的「导入」经 [跳转页]({BRIDGE}) 唤起客户端 —— GitHub 会过滤非 http(s)"
            " 链接，自定义协议没法直接做成可点的。不想走跳转页的话，复制下面的原始"
            " Scheme 到地址栏或快捷指令打开，效果相同：",
            "",
            "```",
            *[f"{n}\n{s}" for n, s in schemes],
            "```",
            "",
        ]

    if d["note"]:
        lines += [f"> {d['note']}", ""]
    return lines


def render(d: dict) -> str:
    lines = [f"# {d['title']}", "", *body(d)]
    lines += [
        "<sub>本文件由 `gen_readme.py` 生成，勿直接编辑。</sub>",
        "",
    ]
    return "\n".join(lines)


def inject(d: dict, old: str) -> str:
    """把导入表格塞进手写 README 的标记块里，标记外的正文原样保留。"""
    head, sep, rest = old.partition(MARK_BEGIN)
    if not sep:
        raise SystemExit(f"✗ {d['path']}/README.md 缺少 {MARK_BEGIN} 标记，无法注入")
    _, sep, tail = rest.partition(MARK_END)
    if not sep:
        raise SystemExit(f"✗ {d['path']}/README.md 缺少 {MARK_END} 标记，无法注入")
    block = "\n".join(["", *body(d), ""]).rstrip("\n")
    return f"{head}{MARK_BEGIN}{block}\n{MARK_END}{tail}"


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
        old = target.read_text(encoding="utf-8") if target.exists() else ""
        text = inject(d, old) if d.get("inject") else render(d)
        if args.check:
            if old != text:
                print(f"✗ {target.relative_to(ROOT)} 与源不一致，请跑 python3 gen_readme.py")
                bad += 1
        else:
            target.write_text(text, encoding="utf-8")
            print(f"✓ {target.relative_to(ROOT)}  ({len(files_of(d))} 个文件)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
