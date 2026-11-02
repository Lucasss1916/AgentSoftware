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
# 单一事实来源：新增规则类型只需在这里加一行，七种格式同时生效。
# 值为 None 表示该格式无法表达此类型，会被显式统计为跳过，而不是静默丢弃。
# Anywhere 没有精确 DOMAIN 类型，转换为后缀匹配会额外匹配其子域名。
# honk 的值是 `匹配函数|参数前缀`，由 emit_honk 拼成 dae 的 `domain(suffix: x)` 形式。
#
TYPES: dict[str, dict[str, str | None]] = {
    "DOMAIN":         {"clash": "DOMAIN",         "qx": "HOST",         "egern": "domain_set",         "singbox": "domain",         "surge": "DOMAIN",         "anywhere": "2",  "honk": "domain|full"},
    "DOMAIN-SUFFIX":  {"clash": "DOMAIN-SUFFIX",  "qx": "HOST-SUFFIX",  "egern": "domain_suffix_set",  "singbox": "domain_suffix",  "surge": "DOMAIN-SUFFIX",  "anywhere": "2",  "honk": "domain|suffix"},
    "DOMAIN-KEYWORD": {"clash": "DOMAIN-KEYWORD", "qx": "HOST-KEYWORD", "egern": "domain_keyword_set", "singbox": "domain_keyword", "surge": "DOMAIN-KEYWORD", "anywhere": "3",  "honk": "domain|keyword"},
    "DOMAIN-REGEX":   {"clash": "DOMAIN-REGEX",   "qx": None,           "egern": "domain_regex_set",   "singbox": "domain_regex",   "surge": None,             "anywhere": None, "honk": "domain|regex"},
    "IP-CIDR":        {"clash": "IP-CIDR",        "qx": "IP-CIDR",      "egern": "ip_cidr_set",        "singbox": "ip_cidr",        "surge": "IP-CIDR",        "anywhere": "0",  "honk": "dip|"},
    "IP-CIDR6":       {"clash": "IP-CIDR6",       "qx": "IP6-CIDR",     "egern": "ip_cidr6_set",       "singbox": "ip_cidr",        "surge": "IP-CIDR6",       "anywhere": "1",  "honk": "dip|"},
    "GEOIP":          {"clash": "GEOIP",          "qx": "GEOIP",        "egern": "geoip_set",          "singbox": None,             "surge": "GEOIP",          "anywhere": None, "honk": "dip|geoip"},
    "ASN":            {"clash": "IP-ASN",         "qx": None,           "egern": "asn_set",            "singbox": None,             "surge": "IP-ASN",         "anywhere": None, "honk": None},
    "PROCESS-NAME":   {"clash": "PROCESS-NAME",   "qx": None,           "egern": None,                 "singbox": "process_name",   "surge": "PROCESS-NAME",   "anywhere": None, "honk": "pname|"},
    "USER-AGENT":     {"clash": "USER-AGENT",     "qx": "USER-AGENT",   "egern": None,                 "singbox": None,             "surge": "USER-AGENT",     "anywhere": None, "honk": None},
    "URL-REGEX":      {"clash": None,             "qx": "URL-REGEX",    "egern": "url_regex_set",      "singbox": None,             "surge": "URL-REGEX",      "anywhere": None, "honk": None},
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


# --------------------------------------------------- honk 规则集 → 出口策略
#
# 其余六家的规则文件只有「匹配」没有「策略」—— 策略写在客户端配置里。honk 没有
# 这种分离：dae 的一条 routing 规则就是「匹配 + 出口」，出口只能落在规则文件内。
# 所以这里把 clash/yaml/routes.yaml 里每个 RULE-SET 对应的策略组照搬过来。
# 组名定义见 honk/config.dae 的 group 段。
#
HONK_OUTBOUND: dict[str, str] = {
    # ---- Clash 侧实际在用的 8 个，出口与 routes.yaml 一一对应 ----
    "SailyAds":                 "block",      # RULE-SET,SailyAds,REJECT
    "Saily":                    "media",      # RULE-SET,Saily,🍿 国外媒体
    "TalktoneAds":              "block",      # RULE-SET,TalktoneAds,REJECT
    "TalktoneProxy":            "talktone",   # RULE-SET,TalktoneProxy,📞 TalkTone
    "TalktoneDirect":           "cn_direct",  # RULE-SET,TalktoneDirect,🌐 全球直连
    "MyAiport":                 "media",      # RULE-SET,Myairport,🍿 国外媒体
    "DirectDomain":             "cn_direct",  # RULE-SET,DirectDomain,🌐 全球直连
    "myvideorule":              "video",      # RULE-SET,MyVideo,🎥 视频
    # ---- Clash 侧没引用，honk/config.dae 的 include 也没开；出口按用途登记，
    #      文件照常生成，加进 include 才会生效 ----
    "AD":                       "block",
    "prevent_dns":              "block",
    "Apisub":                   "media",
    "ProxyDomain":              "media",
    "NeedHighQualityNodeDomain": "media",
    "HKProxyDomain":            "hk",
    "AppleRules":               "apple",
    "AppleAPIRules":            "apple",
    "AppleCDNRules":            "cn_direct",
    "AppleNoChinaCDNRules":     "media",
    "steamCDN":                 "cn_direct",
}

# 新增规则集若忘了登记，用这个占位出口并在文件头打警告，而不是静默选一个策略。
HONK_UNMAPPED_OUTBOUND = "proxy"

# dae 匹配参数里这些字节会改变断句（逗号分候选、括号闭合、& 与 | 参与分隔、
# # 起注释、空白截断），含其一就必须整体加引号。单个 - 是安全的，只有 -> 这个
# 箭头序列才会被当成动作分隔符，所以单独判。
HONK_NEEDS_QUOTE = set(",)('\"#&|") | {" ", "\t"}


def _honk_arg(value: str, force_quote: bool = False) -> str | None:
    """返回可直接写进 dae 的参数；无法表达时返回 None（由调用方计入跳过）。

    force_quote 用于 regex：正则最容易带上奇怪字节，一律加引号既安全又让产物
    一眼能看出边界在哪，而加引号本身不改变语义（解析时只剥一层）。
    """
    if not force_quote and not (set(value) & HONK_NEEDS_QUOTE) and "->" not in value:
        return value
    if "'" in value and '"' in value:
        # dae 的引号保护区间内没有转义语法，两种引号都出现就无法表达。
        return None
    return f'"{value}"' if "'" in value else f"'{value}'"


# ---------------------------------------------------------------- 各格式输出
# 每个 emit_* 返回 (文本内容, 跳过条数)；stem 是规则集名，只有 honk 需要用它查出口。


def _flat(rules: list[Rule], fmt: str, preserve_no_resolve: bool = True) -> tuple[list[str], int]:
    """行式格式（clash / qx / surge / anywhere）的共同逻辑。"""
    lines, skipped = [], 0
    for r in rules:
        t = TYPES[r.type][fmt]
        if t is None:
            skipped += 1
            continue
        suffix = ",no-resolve" if (preserve_no_resolve and r.no_resolve and r.type in IP_TYPES) else ""
        lines.append(f"{t},{r.value}{suffix}")
    return lines, skipped


def emit_clash(rules: list[Rule], stem: str = "") -> tuple[str, int]:
    lines, skipped = _flat(rules, "clash")
    return "\n".join(["payload:"] + [f"  - {l}" for l in lines]) + "\n", skipped


def emit_qx(rules: list[Rule], stem: str = "") -> tuple[str, int]:
    lines, skipped = _flat(rules, "qx")
    return "\n".join(lines) + "\n", skipped


def emit_surge(rules: list[Rule], stem: str = "") -> tuple[str, int]:
    lines, skipped = _flat(rules, "surge")
    return "\n".join(lines) + "\n", skipped


def emit_anywhere(rules: list[Rule], stem: str = "") -> tuple[str, int]:
    # .arrs 把首个逗号后的整段文本当作值，追加 no-resolve 会导致 CIDR 失效。
    lines, skipped = _flat(rules, "anywhere", preserve_no_resolve=False)
    comments = ["# Generated by sync_rules.py; edit loon/rule/*.list instead."]
    domain_count = sum(rule.type == "DOMAIN" for rule in rules)
    no_resolve_count = sum(rule.no_resolve and rule.type in {"IP-CIDR", "IP-CIDR6"}
                           for rule in rules)
    if domain_count:
        comments.append(f"# {domain_count} DOMAIN rules use suffix matching, including subdomains.")
    if no_resolve_count:
        comments.append(f"# {no_resolve_count} no-resolve modifiers omitted; configure DNS behavior in Anywhere.")
    if skipped:
        comments.append(f"# {skipped} unsupported rules omitted; see README.md for format limitations.")
    return "\n".join(comments + lines) + "\n", skipped


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


def emit_egern(rules: list[Rule], stem: str = "") -> tuple[str, int]:
    buckets, skipped = _grouped(rules, "egern")
    if not buckets:
        return "{}\n", skipped
    return yaml.dump(buckets, allow_unicode=True, sort_keys=False,
                     default_flow_style=False), skipped


def emit_singbox(rules: list[Rule], stem: str = "") -> tuple[str, int]:
    buckets, skipped = _grouped(rules, "singbox")
    payload = {"version": 2, "rules": [buckets] if buckets else []}
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n", skipped


def emit_honk(rules: list[Rule], stem: str = "") -> tuple[str, int]:
    """dae 语法的 routing 片段，由 honk/config.dae 的 include 块引用。"""
    outbound = HONK_OUTBOUND.get(stem, HONK_UNMAPPED_OUTBOUND)

    # 按匹配函数归类。domain / dip / pname 属于不同的 condition group，
    # 塞进同一条规则会被 AND 起来（要求同时命中），所以必须各占一条。
    buckets: dict[str, list[str]] = defaultdict(list)
    skipped = 0
    unquotable = 0
    for r in rules:
        spec = TYPES[r.type]["honk"]
        if spec is None:
            skipped += 1
            continue
        func, prefix = spec.split("|")
        arg = _honk_arg(r.value, force_quote=prefix == "regex")
        if arg is None:
            skipped += 1
            unquotable += 1
            continue
        buckets[func].append(f"{prefix}: {arg}" if prefix else arg)

    lines = [
        f"# {stem} —— 由 sync_rules.py 生成，请改 loon/rule/{stem}.list，勿直接编辑。",
        f"# 出口 `{outbound}` 取自 sync_rules.py 的 HONK_OUTBOUND 表，组名见 honk/config.dae。",
    ]
    if stem and stem not in HONK_OUTBOUND:
        lines.append("# ⚠ 未在 HONK_OUTBOUND 登记，出口是占位值；"
                     "加进 config.dae 的 include 前请先登记。")
    no_resolve = sum(r.no_resolve and r.type in IP_TYPES for r in rules)
    if no_resolve:
        lines.append(f"# {no_resolve} 条 no-resolve 修饰符已丢弃：honk 没有逐条开关，"
                     "解析行为由 dns 段统一决定。")
    if unquotable:
        lines.append(f"# {unquotable} 条值同时含单双引号，dae 引号内无转义语法，无法表达。")
    if skipped:
        lines.append(f"# {skipped} 条规则 honk 没有对应匹配函数，已跳过；"
                     "差异见仓库 README 的「格式能力差异」表。")

    if not buckets:
        lines.append("# 本规则集在 honk 下无可用规则，routing 段略。")
        return "\n".join(lines) + "\n", skipped

    lines.append("routing {")
    for func in ("domain", "dip", "pname"):
        args = buckets.get(func)
        if not args:
            continue
        if len(args) == 1:
            lines.append(f"    {func}({args[0]}) -> {outbound}")
            continue
        # 括号内的参数列表可以跨行，逐条一行比挤成一行好读也好 diff。
        lines.append(f"    {func}(")
        lines += [f"        {a}," for a in args[:-1]]
        lines.append(f"        {args[-1]}")
        lines.append(f"    ) -> {outbound}")
    lines.append("}")
    return "\n".join(lines) + "\n", skipped


TARGETS = [
    ("clash",   Path("clash")   / "rule", ".yaml", emit_clash),
    ("quanx",   Path("quanx")   / "rule", ".list", emit_qx),
    ("Egern",   Path("Egern")   / "rule", ".yaml", emit_egern),
    ("singbox", Path("singbox") / "rule", ".json", emit_singbox),
    ("Surge",   Path("Surge")   / "rule", ".list", emit_surge),
    ("Anywhere", Path("anywhere") / "rule", ".arrs", emit_anywhere),
    ("honk",    Path("honk")    / "rule", ".dae", emit_honk),
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
    ap.add_argument("--cloud", action="store_true",
                    help="云端同步模式：只生成产物，不自动提交")
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
            text, skipped = emit(rules, src.stem)
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

    if args.cloud:
        print("\n云端同步完成（产物已生成，不自动提交）")
        return 0

    print("\n同步完成")
    return 1 if all_warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())