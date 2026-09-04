#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主配置双向同步：routes.yaml  <->  clash/yaml/*.yaml + singbox/config/config.json

正向（默认）  python3 sync_config.py
    routes.yaml + clash/yaml/common_head.yaml + gen.py  ->  两份 clash 配置 + sing-box 配置

反向          python3 sync_config.py --from-clash
              python3 sync_config.py --from-singbox
    把手改回的分流顺序 / 规则集抽回 routes.yaml，再由正向重新铺开到两侧。

校验          python3 sync_config.py --check      产物与源不一致则退出码 1
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROUTES = ROOT / "routes.yaml"
CLASH_DIR = ROOT / "clash" / "yaml"
COMMON_RULES = CLASH_DIR / "common_rules.yaml"
SB_CONFIG = ROOT / "singbox" / "config" / "config.json"
SB_RAW = ("https://raw.githubusercontent.com/Lucasss1916/AgentSoftware"
          "/main/singbox/config/config.json")

MRS = "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/"
SRS = "https://gh-proxy.com/github.com/MetaCubeX/meta-rules-dat/raw/sing/geo/"
SELF_JSON_URL = ("https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/"
                 "refs/heads/main/singbox/rule/{}.json")

# clash 策略组 -> sing-box outbound tag。两侧组名保持一致，仅内置目标需映射。
BUILTIN = {"DIRECT": "direct", "REJECT": "block"}

# ---------------------------------------------------------------- 读 routes
def load_routes():
    import yaml
    txt = ROUTES.read_text(encoding="utf-8")
    d = yaml.safe_load(txt)
    return d["rule_sets"], d["rules"]


def load_comments():
    """解析 routes.yaml 里的 '# ---- 分节 ----' 注释，附到其后第一个条目。
    这些注释记录了排序理由（如 Apple-CN 必须早于 Apple），必须随产物一起保留。"""
    pc, rc, pending, in_rules = {}, {}, [], False
    for line in ROUTES.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s == "rules:":
            in_rules, pending = True, []; continue
        if s.startswith("#"):
            # 只收 "---- 分节 ----" 形式，且排除 routes.yaml 自身的说明性表头
            if "----" in s and "一个条目同时描述" not in s:
                pending.append(s.lstrip("# ").rstrip())
            continue
        if not s:
            continue
        if in_rules and s.startswith("- "):
            if pending: rc[s[2:].strip()] = pending; pending = []
        elif not in_rules and s.startswith("- name:"):
            n = s.split("- name:", 1)[1].strip().strip("'\"")
            if pending: pc[n] = pending; pending = []
    return pc, rc

def rs_index(rule_sets):
    return {r["name"]: r for r in rule_sets}

# ---------------------------------------------------------------- clash 侧
ANCHOR_DECL = """# ========================
# 规则集提供者
# ========================
rule-anchor:
  ip: &ip {type: http, interval: 86400, behavior: ipcidr, format: mrs}
  domain: &domain {type: http, interval: 86400, behavior: domain, format: mrs}
  class: &class {type: http, interval: 86400, behavior: classical, format: text}
  yamlclass: &yamlclass {type: http, interval: 86400, behavior: classical, format: yaml}

rule-providers:
"""

def build_common_rules(rule_sets, rules) -> str:
    pc, rc = load_comments()
    out = [ANCHOR_DECL.rstrip("\n")]
    first = True
    for r in rule_sets:
        c = r["clash"]
        for cm in pc.get(r["name"], []):
            if not first:
                out.append("")
            out.append(f"  # {cm}")
        first = False
        out.append(f"  {r['name']}: {{<<: *{c['anchor']}, url: \"{c['url']}\"}}")
    out.append("")
    out.append("# ========================")
    out.append("# 规则引擎")
    out.append("# ========================")
    out.append("# 顺序原则：进程直连 > 局域网 > 广告拦截 > 个人自定义 > 业务分流 > 国内直连 > 兜底")
    out.append("# 本段由 sync_config.py 依 routes.yaml 生成，勿直接编辑。")
    out.append("rules:")
    for x in rules:
        for cm in rc.get(x, []):
            out.append("")
            out.append(f"  # {cm}")
        out.append(f"  - {x}")
    out.append("")
    return "\n".join(out)

# ---------------------------------------------------------------- sing-box 侧
def sb_rule_sets(rule_sets, used: set[str]):
    items = []
    for r in rule_sets:
        if r["name"] not in used:
            continue
        sb = r.get("singbox")
        if not sb:
            continue
        tag = sb_tag(r["name"])
        if sb["kind"] == "self":
            items.append({"type": "remote", "tag": tag, "format": "source",
                          "url": SELF_JSON_URL.format(sb["name"]),
                          "download_detour": "direct", "update_interval": "24h"})
        else:
            items.append({"type": "remote", "tag": tag, "format": "binary",
                          "url": SRS + sb["path"] + ".srs",
                          "download_detour": "direct", "update_interval": "24h"})
    return items

def sb_tag(name: str) -> str:
    """'Telegram / IP' -> 'telegram-ip'，保证 tag 合法且稳定。"""
    s = name.strip().lower().replace(" / ", "-").replace(" ", "-")
    return re.sub(r"[^a-z0-9_.-]", "-", s)

def out_tag(target: str) -> str:
    return BUILTIN.get(target, target)

def build_sb_route(rule_sets, rules):
    idx = rs_index(rule_sets)
    used, sb_rules, skipped = set(), [], []
    # sniff / DNS 劫持必须在最前
    sb_rules.append({"action": "sniff"})
    sb_rules.append({"protocol": "dns", "action": "hijack-dns"})

    for raw in rules:
        parts = [p.strip() for p in raw.split(",")]
        typ = parts[0].upper()

        if typ == "PROCESS-NAME":
            sb_rules.append({"process_name": [parts[1]], "outbound": out_tag(parts[2])})
        elif typ in ("IP-CIDR", "IP-CIDR6"):
            sb_rules.append({"ip_cidr": [parts[1]], "outbound": out_tag(parts[2])})
        elif typ == "DOMAIN-SUFFIX":
            sb_rules.append({"domain_suffix": [parts[1]], "outbound": out_tag(parts[2])})
        elif typ == "DOMAIN":
            sb_rules.append({"domain": [parts[1]], "outbound": out_tag(parts[2])})
        elif typ == "DOMAIN-KEYWORD":
            sb_rules.append({"domain_keyword": [parts[1]], "outbound": out_tag(parts[2])})
        elif typ == "GEOIP":
            # sing-box 已移除内置 geoip，用等价 .srs 规则集
            tag = "geoip-" + parts[1].lower()
            sb_rules.append({"rule_set": [tag], "outbound": out_tag(parts[2])})
            used.add("__geoip__" + parts[1].lower())
        elif typ == "RULE-SET":
            name, target = parts[1], parts[2]
            r = idx.get(name)
            if r is None:
                raise SystemExit(f"routes.yaml 缺少规则集定义: {name}")
            if not r.get("singbox"):
                skipped.append((name, target)); continue
            used.add(name)
            sb_rules.append({"rule_set": [sb_tag(name)], "outbound": out_tag(target)})
        elif typ == "MATCH":
            pass  # -> route.final
        else:
            raise SystemExit(f"未知规则类型: {raw}")
    return sb_rules, used, skipped

def merge_sb_rules(sb_rules):
    """相邻同 outbound 的 rule_set 规则合并，缩小配置体积且不改变语义。"""
    merged = []
    for r in sb_rules:
        if (merged and "rule_set" in r and "rule_set" in merged[-1]
                and set(r) == set(merged[-1]) == {"rule_set", "outbound"}
                and r["outbound"] == merged[-1]["outbound"]):
            merged[-1]["rule_set"] = merged[-1]["rule_set"] + r["rule_set"]
        else:
            merged.append(dict(r))
    return merged

# ---------------------------------------------------------------- sing-box 骨架
REGIONS = ["香港", "台湾", "日本", "新加坡", "韩国", "美国", "英国"]
BIZ = ["AIGC", "GitHub", "Telegram", "Video", "国外媒体", "Spotify",
       "Apple", "Microsoft", "Steam", "Game", "Test"]
FILTERS = {
 "香港": r"(?!.*(?i:10x))(?=.*(广港|香港|HK|Hong ?Kong|🇭🇰|HongKong)).*$",
 "台湾": r"(?!.*(?i:10x))(?=.*(广台|台湾|台灣|TW|Tai ?Wan|🇹🇼|TaiWan|Taiwan)).*$",
 "日本": r"(?!.*(?i:10x))(?=.*(广日|日本|JP|川日|东京|大阪|泉日|埼玉|沪日|深日|🇯🇵|Japan)).*$",
 "新加坡": r"(?!.*(?i:10x))(?=.*(广新|新加坡|SG|坡|狮城|🇸🇬|Singapore)).*$",
 "韩国": r"(?!.*(?i:10x))(?=.*(广韩|韩国|韓國|KR|首尔|春川|🇰🇷|Korea)).*$",
 "美国": r"(?!.*(?i:10x))(?=.*(广美|美国|US|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|拉斯|洛杉|圣何塞|圣克拉|西雅|芝加|🇺🇸|United ?States)).*$",
 "英国": r"(?!.*(?i:10x))(?=.*(英国|伦敦|UK|United ?Kingdom|🇬🇧|London)).*$",
}
SUFFIX = "智选"   # 与 clash smart.yaml 的地区组后缀保持一致

def region_tags():
    return [f"{r}-{SUFFIX}" for r in REGIONS]

def build_singbox(rule_sets, rules, old: dict | None):
    regions = region_tags()
    sb_rules, used, skipped = build_sb_route(rule_sets, rules)
    sb_rules = merge_sb_rules(sb_rules)

    # 保留用户已填好的机场节点（非本脚本管理的 outbound）
    managed = set(regions) | set(BIZ) | {"Block", "所有-手选", "漏网之鱼",
                                        "direct", "block", "dns-out", "select"}
    user_nodes = []
    if old:
        for o in old.get("outbounds", []):
            if o.get("tag") not in managed and o.get("type") not in ("selector", "urltest"):
                user_nodes.append(o)
    node_tags = [o["tag"] for o in user_nodes]

    def sel(tag, extra=()):
        outs = list(extra) + regions + ["其他", "所有-手选", "direct", "block"]
        return {"type": "selector", "tag": tag, "outbounds": outs}

    outbounds = []
    for b in BIZ:
        outbounds.append(sel(b))
    outbounds.append({"type": "selector", "tag": "Block", "outbounds": ["block", "direct"]})
    outbounds.append({"type": "selector", "tag": "所有-手选",
                      "outbounds": (node_tags or ["direct"])})
    outbounds.append({"type": "selector", "tag": "漏网之鱼",
                      "outbounds": regions + ["其他", "所有-手选", "direct"]})
    for r in REGIONS:
        outbounds.append({"type": "urltest", "tag": f"{r}-{SUFFIX}",
                          "outbounds": (node_tags or ["direct"]),
                          "url": "https://www.gstatic.com/generate_204",
                          "interval": "5m", "tolerance": 30})
    outbounds.append({"type": "urltest", "tag": "其他",
                      "outbounds": (node_tags or ["direct"]),
                      "url": "https://www.gstatic.com/generate_204",
                      "interval": "5m", "tolerance": 30})
    outbounds += user_nodes
    outbounds.append({"type": "direct", "tag": "direct"})
    outbounds.append({"type": "block", "tag": "block"})

    rsets = sb_rule_sets(rule_sets, used)
    # GEOIP,CN -> 等价 .srs
    for u in sorted(x for x in used if x.startswith("__geoip__")):
        cc = u.replace("__geoip__", "")
        rsets.append({"type": "remote", "tag": f"geoip-{cc}", "format": "binary",
                      "url": f"{SRS}geoip/{cc}.srs",
                      "download_detour": "direct", "update_interval": "24h"})

    cfg = {
      "log": {"level": "info", "timestamp": True},
      "dns": {
        "servers": [
          {"type": "https", "tag": "dns_cn", "server": "223.5.5.5", "detour": "direct"},
          {"type": "https", "tag": "dns_proxy", "server": "dns.google", "detour": "漏网之鱼"},
          {"type": "fakeip", "tag": "dns_fake", "inet4_range": "198.18.0.0/16"},
          {"type": "local", "tag": "dns_local"},
        ],
        "rules": [
          {"query_type": ["A", "AAAA"], "server": "dns_fake", "rewrite_ttl": 1},
        ],
        "final": "dns_cn",
        "independent_cache": True,
        "strategy": "ipv4_only",
      },
      "inbounds": [
        {"type": "mixed", "tag": "mixed-in", "listen": "0.0.0.0", "listen_port": 7893},
        {"type": "tun", "tag": "tun-in", "address": ["172.19.0.1/30"],
         "auto_route": True, "strict_route": False, "stack": "mixed", "mtu": 1350},
      ],
      "outbounds": outbounds,
      "route": {
        "rule_set": rsets,
        "rules": sb_rules,
        "final": "漏网之鱼",
        "auto_detect_interface": True,
        "default_domain_resolver": {"server": "dns_cn"},
      },
      "experimental": {
        "clash_api": {"external_controller": "0.0.0.0:9090",
                      "secret": "anv4SIzOSEWGMXcIoT-hGT-5LigNk9v0"},
        "cache_file": {"enabled": True, "store_fakeip": True},
      },
    }
    return cfg, skipped, node_tags

def write_sb_readme(skipped) -> str:
    """生成 sing-box 配置说明（返回文本，不落盘）。

    原先塞在 config.json 的 _notes 里，但 sing-box 1.13 拒绝未知顶层字段，
    故改为独立文档。返回而非直接写，是为了让 --check 能只比不写 ——
    早先它无条件写盘，等于校验模式会悄悄改工作区。"""
    L = ["# sing-box 配置", "",
         "本目录的 `config.json` **由 `sync_config.py` 生成，请勿手改**。", "",
         "- 改分流：编辑仓库根目录 `routes.yaml`，再跑 `python3 sync_config.py`",
         "- 已经手改了 `config.json`：跑 `python3 sync_config.py --from-singbox` 回写，"
         "再跑一次正向同步铺到 clash 侧", "",
         "## 填入机场节点", "",
         "配置默认不含任何节点，各策略组暂时指向 `direct`，**直接使用不会走代理**。",
         "用 sub-store 等工具按下面的正则过滤订阅节点，把节点 outbound 追加进 "
         "`outbounds`，再把它们的 tag 填进各地区 urltest 组：", "",
         "| 地区组 | filter 正则 |", "| --- | --- |"]
    for r in REGIONS:
        L.append(f"| `{r}-{SUFFIX}` | `{FILTERS[r]}` |")
    L += ["", "业务组(AIGC / GitHub / ...)已自动引用各地区组,填完节点无需再动。", "",
          "## sub-store 自动拉取节点(方式 1)", "",
          "sing-box **内核不支持** clash 那种 `proxy-providers` 远程节点订阅,",
          "节点必须写死在 `outbounds`。想要“订阅 URL 自动拉节点”,正确做法是:",
          "让 sub-store(或 SFM 客户端的订阅)以**本份 `config.json` 为模板**,",
          "把机场订阅节点注入进 `outbounds` 的各地区 urltest 组,",
          "输出一份**完整 sing-box 配置**托管到固定 URL,再把该 URL 给客户端定时拉取。", "",
          "接线步骤:", "",
          "1. 在 sub-store 输出端选 **sing-box 模板** 格式,模板 URL 指向本文件:",
          f"   `{SB_RAW}`",
          "2. sub-store 会用机场订阅节点替换/填充 `香港-智选`…`其他` 等 urltest 组的 ",
          "`outbounds`(把 `[\"direct\"]` 换成你节点的 tag)。",
          "3. 把 sub-store 生成的**完整配置托管地址**(而不是本仓库这个地址)填进客户端订阅,",
          "sub-store 定时刷新节点。", "",
          "取舍:节点自动更新的同时,**分流以 sub-store 编排产出的那份为准**;",
          "本仓库 `routes.yaml` 仍负责 `config.json` 模板本身的分流。两者各自独立。", "",
          "## 导入", "",
          f"订阅地址:<{SB_RAW}>", "",
          "一键导入(官方 SFI / SFM / SFA)。sing-box 只有自定义协议头,",
          "GitHub 会过滤掉非 http(s) 链接,需复制到地址栏或快捷指令打开:", "",
          "```",
          f"sing-box://import-remote-profile?url={quote(SB_RAW, safe='')}",
          f"#{quote('AgentSoftware')}",
          "```", ""]
    if skipped:
        L += ["## 与 clash 的差异", "",
              "以下规则集上游没有 sing-box `.srs` 格式，仅在 clash 侧生效：", ""]
        for n, t in skipped:
            L.append(f"- `{n}` → `{t}`")
        L += ["", "其中 `Block / Domain` 在 sing-box 侧改用上游通用广告表 "
              "`geosite/category-ads-all` 替代（内容与 clash 侧不同源）。", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 反向同步
def parse_clash_rules(text: str):
    """从 common_rules.yaml 抽回 rule_sets 与 rules。"""
    prov = {}
    for m in re.finditer(r'^\s{2}([^\s#][^:]*?):\s*\{<<:\s*\*(\w+),\s*url:\s*"([^"]+)"\}',
                         text, re.M):
        prov[m.group(1).strip()] = {"anchor": m.group(2), "url": m.group(3)}
    rules, in_rules = [], False
    for line in text.splitlines():
        s = line.strip()
        if s == "rules:":
            in_rules = True; continue
        if in_rules and s.startswith("- "):
            rules.append(s[2:].strip())
    return prov, rules

def parse_singbox_rules(cfg: dict, rule_sets):
    """从 config.json 抽回分流顺序（转成 clash 语法）。"""
    idx = {sb_tag(r["name"]): r["name"] for r in rule_sets}
    inv = {v: k for k, v in BUILTIN.items()}
    out = []
    for r in cfg.get("route", {}).get("rules", []):
        if "action" in r or r.get("protocol") == "dns":
            continue
        tgt = inv.get(r.get("outbound"), r.get("outbound"))
        if "process_name" in r:
            out += [f"PROCESS-NAME,{v},{tgt}" for v in r["process_name"]]
        elif "ip_cidr" in r:
            out += [f"IP-CIDR,{v},{tgt}" for v in r["ip_cidr"]]
        elif "domain_suffix" in r:
            out += [f"DOMAIN-SUFFIX,{v},{tgt}" for v in r["domain_suffix"]]
        elif "domain" in r:
            out += [f"DOMAIN,{v},{tgt}" for v in r["domain"]]
        elif "domain_keyword" in r:
            out += [f"DOMAIN-KEYWORD,{v},{tgt}" for v in r["domain_keyword"]]
        elif "rule_set" in r:
            for t in r["rule_set"]:
                if t.startswith("geoip-"):
                    out.append(f"GEOIP,{t.split('-',1)[1].upper()},{tgt},no-resolve")
                elif t in idx:
                    out.append(f"RULE-SET,{idx[t]},{tgt}")
                else:
                    raise SystemExit(f"config.json 引用了 routes.yaml 未定义的规则集: {t}")
    return out

def write_routes(rule_sets, rules):
    """把 rule_sets/rules 回写 routes.yaml，保留原有注释头与分节注释。"""
    pc, rc = load_comments()
    old = ROUTES.read_text(encoding="utf-8")
    head = old.split("rule_sets:")[0]
    L = [head.rstrip("\n"), "rule_sets:"]
    first = True
    for r in rule_sets:
        c = r["clash"]
        for cm in pc.get(r["name"], []):
            if not first:
                L.append("")
            L.append(f"  # {cm}")
        first = False
        L.append(f"  - name: {r['name']!r}")
        L.append(f"    clash: {{anchor: {c['anchor']}, url: {c['url']!r}}}")
        sb = r.get("singbox")
        if not sb:
            L.append("    singbox: null   # 上游无 .srs，sing-box 侧跳过")
        elif sb["kind"] == "self":
            L.append(f"    singbox: {{kind: self, name: {sb['name']!r}}}")
        elif sb.get("substitute"):
            L.append(f"    singbox: {{kind: remote, path: {sb['path']!r}, substitute: true}}"
                     "  # 上游无同源 .srs，改用通用广告表")
        else:
            L.append(f"    singbox: {{kind: remote, path: {sb['path']!r}}}")
    L += ["", "# ---- 分流顺序：两侧严格一致 ----",
          "# 顺序原则：进程直连 > 局域网 > 广告拦截 > 个人自定义 > 业务分流 > 国内直连 > 兜底",
          "rules:"]
    for x in rules:
        for cm in rc.get(x, []):
            L.append("")
            L.append(f"  # {cm}")
        L.append(f"  - {x}")
    L.append("")
    ROUTES.write_text("\n".join(L), encoding="utf-8")

def reconcile_from_singbox(orig_rules, sb_rules_text, rule_sets):
    """把 sing-box 侧的改动合并回 routes.yaml。

    sing-box 的表示是有损的：它没有 no-resolve，也不含上游无 .srs 的规则集。
    所以不能直接用它重建规则表，否则会把 no-resolve 和那 6 条 clash-only 规则抹掉。
    做法：把原规则投影成 sing-box 形态后与实际做 difflib 比对，
    只把「真正的增删」应用回原表，未变动的原始行原样保留（含修饰符）。
    """
    import difflib
    idx = rs_index(rule_sets)

    def is_sb_invisible(r):
        if not r.startswith("RULE-SET,"):
            return False
        e = idx.get(r.split(",")[1].strip())
        return e is not None and not e.get("singbox")

    # 原规则 -> sing-box 可见投影（丢掉 no-resolve、丢掉不可见项），并记住来源下标
    proj, src_i = [], []
    for i, r in enumerate(orig_rules):
        if is_sb_invisible(r) or r.startswith("MATCH,"):
            continue
        proj.append(strip_modifiers(r)); src_i.append(i)

    out, used_orig = [], set()
    sm = difflib.SequenceMatcher(a=proj, b=sb_rules_text, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i1, i2):
                out.append(("orig", src_i[k])); used_orig.add(src_i[k])
        elif tag in ("replace", "delete"):
            for k in range(j1, j2):
                out.append(("new", sb_rules_text[k]))
        if tag == "insert":
            for k in range(j1, j2):
                out.append(("new", sb_rules_text[k]))

    # 把 sing-box 不可见的原始规则按原位置插回
    result, pos = [], 0
    inserted = set()
    for kind, val in out:
        if kind == "orig":
            for i in range(pos, val):
                if is_sb_invisible(orig_rules[i]) and i not in inserted:
                    result.append(orig_rules[i]); inserted.add(i)
            result.append(orig_rules[val]); pos = val + 1
        else:
            result.append(val)
    for i in range(pos, len(orig_rules)):
        if is_sb_invisible(orig_rules[i]) and i not in inserted:
            result.append(orig_rules[i])
    # MATCH 永远收尾
    result = [r for r in result if not r.startswith("MATCH,")]
    match = next((r for r in orig_rules if r.startswith("MATCH,")), "MATCH,漏网之鱼")
    result.append(match)
    return result


def strip_modifiers(r):
    """去掉 no-resolve 等 sing-box 无对应的修饰符，用于投影比对。"""
    parts = [p.strip() for p in r.split(",")]
    return ",".join(p for p in parts if p != "no-resolve")


# ---------------------------------------------------------------- 正向
def forward(check: bool) -> int:
    rule_sets, rules = load_routes()
    drift = []

    new_common = build_common_rules(rule_sets, rules)
    if check:
        if COMMON_RULES.read_text(encoding="utf-8") != new_common:
            drift.append(str(COMMON_RULES.relative_to(ROOT)))
    else:
        COMMON_RULES.write_text(new_common, encoding="utf-8")

    old_sb = json.loads(SB_CONFIG.read_text(encoding="utf-8")) if SB_CONFIG.exists() else None
    cfg, skipped, nodes = build_singbox(rule_sets, rules, old_sb)
    # 注意：sing-box 1.13 会拒绝未知顶层字段，配置里不能放 _notes。
    # 地区 filter 正则、节点填法、与 clash 的差异一并写进 singbox/config/README.md。
    sb_readme = SB_CONFIG.parent / "README.md"
    new_readme = write_sb_readme(skipped)
    if check:              # --check 必须只读，不得改动工作区
        if not sb_readme.exists() or sb_readme.read_text(encoding="utf-8") != new_readme:
            drift.append(str(sb_readme.relative_to(ROOT)))
    else:
        sb_readme.write_text(new_readme, encoding="utf-8")
    new_json = json.dumps(cfg, ensure_ascii=False, indent=2) + "\n"
    if check:
        if not SB_CONFIG.exists() or SB_CONFIG.read_text(encoding="utf-8") != new_json:
            drift.append(str(SB_CONFIG.relative_to(ROOT)))
    else:
        SB_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        SB_CONFIG.write_text(new_json, encoding="utf-8")

    # clash 两份主配置由既有 gen.py 生成
    # gen.py 同时产出 .yaml 和 .js，两种都得快照。漏掉 .js 的后果是双重的：
    # --check 检测不到 .js 漂移，还会把工作区里的手改静默覆盖掉（--check 必须只读）。
    GENERATED = ("smart.yaml", "urltest.yaml", "smart.js", "urltest.js")
    before = {p: p.read_bytes() for p in CLASH_DIR.iterdir() if p.name in GENERATED}
    subprocess.run([sys.executable, "gen.py"], cwd=CLASH_DIR, check=True,
                   stdout=subprocess.DEVNULL)
    if check:
        for p, b in before.items():
            if p.read_bytes() != b:
                drift.append(str(p.relative_to(ROOT)))
        for p, b in before.items():
            p.write_bytes(b)

    if check:
        if drift:
            print("校验失败：以下产物与 routes.yaml 不一致，请运行 python3 sync_config.py")
            for d in drift:
                print("  -", d)
            return 1
        print("校验通过：clash 与 sing-box 配置均与 routes.yaml 一致")
        return 0

    print(f"已生成： common_rules.yaml / smart.yaml / urltest.yaml / singbox/config/config.json")
    print(f"  规则集 {len(rule_sets)}  分流规则 {len(rules)}")
    if skipped:
        print(f"  sing-box 跳过 {len(skipped)} 条（上游无 .srs）：")
        for n, t in skipped:
            print(f"    - {n} -> {t}")
    if not nodes:
        print("  提示：sing-box 配置尚无机场节点，各组暂指向 direct；"
              "按 singbox/config/README.md 填入节点后再用。")
    return 0

# ---------------------------------------------------------------- 反向
def backward(src: str) -> int:
    rule_sets, rules = load_routes()
    _orig_rules = list(rules)
    if src == "clash":
        prov, new_rules = parse_clash_rules(COMMON_RULES.read_text(encoding="utf-8"))
        idx = rs_index(rule_sets)
        merged, added = [], []
        for name, c in prov.items():
            if name in idx:
                r = dict(idx[name]); r["clash"] = c
            else:
                r = {"name": name, "clash": c, "singbox": None}
                added.append(name)
            merged.append(r)
        removed = [n for n in idx if n not in prov]
        rule_sets, rules = merged, new_rules
    else:
        cfg = json.loads(SB_CONFIG.read_text(encoding="utf-8"))
        sb_rules = parse_singbox_rules(cfg, rule_sets)
        added, removed = [], []
        rules = reconcile_from_singbox(_orig_rules, sb_rules, rule_sets)
    write_routes(rule_sets, rules)
    print(f"已从 {src} 回写 routes.yaml：规则集 {len(rule_sets)}  分流规则 {len(rules)}")
    if added:   print("  新增规则集：", ", ".join(added))
    if removed: print("  删除规则集：", ", ".join(removed))
    print("现在运行 python3 sync_config.py 把改动铺到两侧。")
    return 0

def main():
    ap = argparse.ArgumentParser(description="clash / sing-box 主配置双向同步")
    ap.add_argument("--check", action="store_true", help="只校验，不写文件")
    ap.add_argument("--from-clash", action="store_true", help="由 clash 侧回写 routes.yaml")
    ap.add_argument("--from-singbox", action="store_true", help="由 sing-box 侧回写 routes.yaml")
    a = ap.parse_args()
    if a.from_clash and a.from_singbox:
        sys.exit("--from-clash 与 --from-singbox 只能二选一")
    if a.from_clash:   sys.exit(backward("clash"))
    if a.from_singbox: sys.exit(backward("singbox"))
    sys.exit(forward(a.check))

if __name__ == "__main__":
    main()
