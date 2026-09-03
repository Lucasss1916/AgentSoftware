# -*- coding: utf-8 -*-
"""由同一份数据生成 smart / url-test 两份 Clash 配置，保证规则段完全一致。"""
from pathlib import Path

BUILD = Path(__file__).resolve().parent

REGIONS = [
    # (中文名, 图标名, filter 正则, 是否给 policy-priority)
    ("香港", "Hong_Kong",
     r"(?!.*(?i:10x))(?=.*(广港|香港|HK|Hong ?Kong|🇭🇰|HongKong)).*$", True),
    ("台湾", "Taiwan",
     r"(?!.*(?i:10x))(?=.*(广台|台湾|台灣|TW|Tai ?Wan|🇹🇼|TaiWan|Taiwan)).*$", True),
    ("日本", "Japan",
     r"(?!.*(?i:10x))(?=.*(广日|日本|JP|川日|东京|大阪|泉日|埼玉|沪日|深日|🇯🇵|Japan)).*$", True),
    ("新加坡", "Singapore",
     r"(?!.*(?i:10x))(?=.*(广新|新加坡|SG|坡|狮城|🇸🇬|Singapore)).*$", True),
    ("韩国", "South_Korea",
     r"(?!.*(?i:10x))(?=.*(广韩|韩国|韓國|KR|首尔|春川|🇰🇷|Korea)).*$", False),
    ("美国", "United_States",
     r"(?!.*(?i:10x))(?=.*(广美|美国|US|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|拉斯|洛杉|圣何塞|圣克拉|西雅|芝加|🇺🇸|United ?States)).*$", False),
    ("英国", "England",
     r"(?!.*(?i:10x))(?=.*(英国|伦敦|UK|United ?Kingdom|🇬🇧|London)).*$", False),
]

# “其他”组：排除上面所有地区关键词
_EXCLUDE = ("10x|10X|直连|拒绝|广港|香港|HK|Hong ?Kong|🇭🇰|HongKong|广台|台湾|台灣|TW|Tai ?Wan|🇹🇼|TaiWan|Taiwan|"
            "广日|日本|JP|川日|东京|大阪|泉日|埼玉|沪日|深日|🇯🇵|Japan|广新|新加坡|SG|坡|狮城|🇸🇬|Singapore|"
            "广韩|韩国|韓國|KR|首尔|春川|🇰🇷|Korea|广美|美国|US|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|拉斯|洛杉|"
            "圣何塞|圣克拉|西雅|芝加|🇺🇸|United ?States|英国|UK|United ?Kingdom|伦敦|London|🇬🇧|"
            "过期|剩余|流量|官网|套餐|机场|返利|订阅|重置")
OTHERS_FILTER = "^((?!(" + _EXCLUDE + ")).)*$"

ICON = "https://raw.githubusercontent.com/Orz-3/mini/master/Color/{}.png"
FLAG = "https://fastly.jsdelivr.net/gh/Semporia/Hand-Painted-icon@master/Rounded_Rectangle/{}.png"

# 业务分流组：(组名, 图标)
BIZ = [
    ("AIGC", ICON.format("OpenAI")),
    ("GitHub", ICON.format("github")),
    ("Telegram", ICON.format("Telegram")),
    ("Video", ICON.format("Emby")),
    ("国外媒体", ICON.format("Google")),
    ("Spotify", ICON.format("Spotify")),
    ("Apple", ICON.format("Apple")),
    ("Microsoft", ICON.format("Microsoft")),
    ("Steam", ICON.format("Steam")),
    ("Game", ICON.format("GAME")),
    ("Test", ICON.format("Urltest")),
]


def build_groups(suffix, kind):
    """kind: 'smart' | 'url-test'"""
    regions = [f"{n}-{suffix}" for n, _, _, _ in REGIONS]
    L = []
    a = L.append

    a("# ========================")
    a("# 策略组定义")
    a("# ========================")
    a("default: &default")
    a("  type: select")
    a("  proxies:")
    a("    - 所有-手选")
    for r in regions:
        a(f"    - {r}")
    a("    - 其他")
    a("    - DIRECT")
    a("    - REJECT")
    a("")
    a("proxy-groups:")
    a("")
    a("  # ---- 业务分流组 ----")
    for name, icon in BIZ:
        a(f"  - {{name: {name}, icon: {icon}, <<: *default}}")
    a("")
    a("  # 广告拦截：只在 REJECT / DIRECT 间选，不继承 *default")
    a("  - name: Block")
    a("    type: select")
    a(f"    icon: {ICON.format('Adblock')}")
    a("    proxies:")
    a("      - REJECT")
    a("      - DIRECT")
    a("")
    a("  # ---- 全部节点手选 ----")
    a("  - name: 所有-手选")
    a("    type: select")
    a("    include-all: true")
    a("    icon: https://www.clashverge.dev/assets/icons/adjust.svg")
    a("")
    a("  # ---- 兜底 ----")
    a("  - name: 漏网之鱼")
    a("    type: fallback")
    a("    icon: https://www.clashverge.dev/assets/icons/fish.svg")
    a("    proxies:")
    for r in regions:
        a(f"      - {r}")
    a("      - 所有-手选")
    a("      - 其他")
    a("      - DIRECT")
    a("")
    a("  # ---- 地区组 ----")

    for cn, flag, filt, prio in REGIONS:
        a("")
        a(f"  # {cn}")
        a(f"  - name: {cn}-{suffix}")
        if kind == "smart":
            a("    type: smart")
            a("    uselightgbm: true")
            a("    collectdata: true")
            if prio:
                a('    policy-priority: "Mitce:0.7"')
            else:
                a('#   policy-priority: "机场名:0.8"')
        else:
            a("    type: url-test")
            a("    url: https://www.gstatic.com/generate_204")
            a("    tolerance: 30")
            a("    lazy: true")
        a("    include-all: true")
        a("    interval: 300")
        a(f'    filter: "{filt}"')
        a(f"    icon: {FLAG.format(flag)}")

    a("")
    a("  # 其他（未匹配到上述地区的节点）")
    a("  - name: 其他")
    if kind == "smart":
        a("    type: smart")
        a("    uselightgbm: true")
        a("    collectdata: true")
    else:
        a("    type: url-test")
        a("    url: https://www.gstatic.com/generate_204")
        a("    tolerance: 30")
        a("    lazy: true")
    a("    include-all: true")
    a("    interval: 300")
    a(f'    filter: "{OTHERS_FILTER}"')
    a("    icon: https://www.clashverge.dev/assets/icons/adjust.svg")
    a("")
    return "\n".join(L)


HEADER = ("# ============================================================\n"
          "#  {title}\n"
          "#  由 gen.py + common_head.yaml + common_rules.yaml 生成\n"
          "#  修改请编辑上述三个源文件后重跑： python3 gen.py\n"
          "# ============================================================\n\n")


# 覆写脚本里不该出现的键：
#   default / rule-anchor 只是 YAML 锚点容器，转成 JS 后没有意义；
#   端口和 external-controller/secret 由客户端自己管，覆写掉会让客户端连不上内核。
JS_DROP = {"default", "rule-anchor",
           "port", "socks-port", "redir-port", "mixed-port", "tproxy-port",
           "external-controller", "secret"}

JS_TMPL = """// {title}
// 由 gen.py 生成，勿手改。改完 common_head.yaml / common_rules.yaml / routes.yaml
// 后重跑： cd clash/yaml && python3 gen.py
//
// 用法：Clash Verge Rev / Clash Party「扩展脚本」，或 Stash / ClashX 的 JS 覆写。
// 订阅自带的 proxies 与 proxy-providers 原样保留，其余段落全部换成本仓库的配置。

const override = {body};

function main(config) {{
  return Object.assign({{}}, config, override);
}}
"""


def build_js(yaml_text, title):
    import yaml, json
    cfg = yaml.safe_load(yaml_text)          # safe_load 会把 <<: *default 展开成实值
    cfg = {k: v for k, v in cfg.items() if k not in JS_DROP}
    return JS_TMPL.format(title=title,
                          body=json.dumps(cfg, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    head = (BUILD / "common_head.yaml").read_text(encoding="utf-8")
    rules = (BUILD / "common_rules.yaml").read_text(encoding="utf-8")
    targets = [
        ("智选", "smart", "smart.yaml",
         "Mihomo 配置 — Smart 内核版（type: smart，需 vernesong/mihomo smart 内核）"),
        ("延时优选", "url-test", "urltest.yaml",
         "Mihomo 配置 — 通用版（type: url-test，官方 mihomo 内核即可）"),
    ]
    for suffix, kind, out, title in targets:
        body = HEADER.format(title=title) + head + "\n\n" + build_groups(suffix, kind) + "\n" + rules
        (BUILD / out).write_text(body, encoding="utf-8")
        print("wrote", out)
        js = out.replace(".yaml", ".js")
        (BUILD / js).write_text(build_js(body, title), encoding="utf-8")
        print("wrote", js)
