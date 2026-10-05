# -*- coding: utf-8 -*-
"""生成分流一致、地区组选路方式不同的两份 Mihomo 配置。"""
from pathlib import Path
import yaml

BUILD = Path(__file__).resolve().parent

# 使用同一组名，切换内核时业务规则不需要随之修改。
REGIONS = [
    ("🇭🇰 香港节点", r"🇭🇰|香港|Hong|HK"),
    ("🇯🇵 日本节点", r"🇯🇵|日本|Japan|JP"),
    ("🇨🇳 台湾节点", r"🇹🇼|台湾|臺灣|台灣|Taiwan|Tai|TW|mv"),
    ("🇸🇬 新加坡节点", r"🇸🇬|新加坡|Singapore|SG"),
    ("🇰🇷 韩国节点", r"🇰🇷|韩国|韓國|Korea|KR"),
    ("🇺🇲 北美节点", r"🇺🇸|🇨🇦|🇲🇽|美国|美國|加拿大|墨西哥|States|Canada|Mexico|USA|(^|[^A-Za-z])US([^A-Za-z]|$)|(^|[^A-Za-z])CA([^A-Za-z]|$)|洛杉矶|圣何塞|西雅图|达拉斯|纽约|芝加哥|硅谷|凤凰城|亚特兰大|迈阿密|拉斯维加斯|波特兰|费利蒙|阿什本|多伦多|温哥华|蒙特利尔|Los Angeles|San Jose|Seattle|Dallas|New York|Chicago|Miami|Ashburn|Phoenix|Fremont|Portland|Las Vegas|Atlanta|Silicon Valley|Toronto|Vancouver|Montreal"),
    ("🌏 其他亚洲节点", r"🇲🇾|马来|大马|吉隆坡|Malaysia|🇹🇭|泰国|曼谷|Thailand|🇻🇳|越南|胡志明|Vietnam|🇵🇭|菲律宾|马尼拉|Philippines|🇮🇩|印尼|印度尼西亚|雅加达|Indonesia|🇮🇳|印度|孟买|India|🇰🇭|柬埔寨|金边|Cambodia|🇱🇦|老挝|Laos|🇲🇲|缅甸|Myanmar|🇧🇳|文莱|Brunei|🇧🇩|孟加拉|Bangladesh|🇵🇰|巴基斯坦|Pakistan|🇳🇵|尼泊尔|Nepal|🇱🇰|斯里兰卡|Lanka"),
    ("🇪🇺 欧洲节点", r"🇬🇧|英国|伦敦|United Kingdom|Britain|London|(^|[^A-Za-z])UK([^A-Za-z]|$)|🇩🇪|德国|德國|法兰克福|Germany|Frankfurt|🇫🇷|法国|法國|巴黎|France|Paris|🇳🇱|荷兰|荷蘭|阿姆斯特丹|Netherlands|Amsterdam|🇷🇺|俄罗斯|俄羅斯|莫斯科|Russia|Moscow|🇹🇷|土耳其|Turkey|Istanbul|🇮🇹|意大利|米兰|Italy|Milan|🇪🇸|西班牙|马德里|Spain|Madrid|🇸🇪|瑞典|Sweden|🇨🇭|瑞士|Switzerland|Zurich|🇵🇱|波兰|Poland|Warsaw|🇺🇦|乌克兰|Ukraine|🇮🇪|爱尔兰|Ireland|Dublin|🇫🇮|芬兰|Finland|🇳🇴|挪威|Norway|🇩🇰|丹麦|Denmark|🇧🇪|比利时|Belgium|🇦🇹|奥地利|Austria|Vienna|🇵🇹|葡萄牙|Portugal|Lisbon|🇨🇿|捷克|Czech|Prague|🇷🇴|罗马尼亚|Romania|🇭🇺|匈牙利|Hungary|🇬🇷|希腊|Greece|Athens|🇷🇸|塞尔维亚|Serbia|🇧🇬|保加利亚|Bulgaria|🇱🇻|拉脱维亚|Latvia|🇱🇹|立陶宛|Lithuania|🇪🇪|爱沙尼亚|Estonia|🇲🇩|摩尔多瓦|Moldova|🇮🇸|冰岛|Iceland|欧洲|Europe"),
]
NODE_EXCLUDE = "过期|剩余|流量|官网|套餐|返利|订阅|重置"


def select_group(name, proxies):
    return {"name": name, "type": "select", "proxies": proxies}


def regional_group(name, pattern, kind):
    group = {"name": name, "type": kind, "include-all": True,
             "filter": "(?i)(" + pattern + ")", "exclude-filter": NODE_EXCLUDE,
             "hidden": True, "interval": 300}
    if name == "🇯🇵 日本节点":
        group["exclude-filter"] += "|美国|美國"
    if kind == "smart":
        # Egern 的成本系数越小越优先；Smart 的评分系数越大越优先，取倒数保留偏好方向。
        group.update({"uselightgbm": True, "collectdata": True,
                      "policy-priority": "Mitce:3.333;iku:3.333;kitty:1.667"})
    else:
        group.update({"url": "https://www.gstatic.com/generate_204",
                      "tolerance": 30, "lazy": True})
    return group


def build_groups(kind):
    regions = [name for name, _ in REGIONS]
    hk, jp, tw, sg, kr, na, asia, eu = regions
    node, manual, direct = "✈️ 节点选择", "🚀 我的节点", "🌐 全球直连"
    foreign = [node, hk, na, jp, kr, sg, tw, asia, eu]
    groups = [
        select_group(node, [manual, direct]),
        {"name": manual, "type": "select", "include-all": True,
         "exclude-filter": NODE_EXCLUDE},
        select_group(direct, ["DIRECT"]),
        select_group("📲 电报信息", [sg, jp, tw, hk, node, na, kr, manual, asia, eu]),
        {"name": "📞 TalkTone", "type": "select", "include-all": True,
         "exclude-filter": NODE_EXCLUDE},
        {"name": "🎥 视频", "type": "select", "include-all": True,
         "exclude-filter": NODE_EXCLUDE,
         "proxies": [manual, node, kr, na, tw, sg, jp, direct, asia, eu]},
        select_group("🍿 国外媒体", foreign),
        select_group("📟 智能助理", [node, na, jp, kr, sg, tw, asia, eu]),
        select_group("Ⓜ️ 微软服务", [direct] + foreign),
        select_group("🍎 苹果服务", [direct] + foreign),
        select_group("🎮 游戏平台", [direct] + foreign),
        select_group("🐟漏网之鱼", [sg, jp, tw, hk, manual, na, kr, asia, eu]),
    ]
    groups.extend(regional_group(name, pattern, kind) for name, pattern in REGIONS)
    return "# 策略组：业务组手选，地区组按所选内核自动选路。\n" + yaml.safe_dump(
        {"proxy-groups": groups}, allow_unicode=True, sort_keys=False, width=10000)


HEADER = ("# ============================================================\n"
          "#  {title}\n"
          "#  由 gen.py + common_head.yaml + common_rules.yaml 生成\n"
          "#  修改 Clash routes.yaml / common_head.yaml / gen.py 后在仓库根运行 sync_config.py\n"
          "# ============================================================\n\n")


# 覆写脚本里不该出现的键：
#   default / rule-anchor 只是 YAML 锚点容器，转成 JS 后没有意义；
#   端口和 external-controller/secret 由客户端自己管，覆写掉会让客户端连不上内核。
#   proxies / proxy-providers 必须留给订阅自己 —— 覆写掉等于把节点清空。
#   （现在 common_head.yaml 里 proxy-providers 是注释掉的，但一旦启用就会踩到，
#     所以在这里显式排除，而不是指望它恰好不存在。）
JS_DROP = {"default", "rule-anchor",
           "port", "socks-port", "redir-port", "mixed-port", "tproxy-port",
           "proxies", "proxy-providers", "external-controller", "secret"}

JS_TMPL = """// {title}
// 由 gen.py 生成，勿手改。改完 common_head.yaml / routes.yaml / gen.py
// 后重跑： cd clash/yaml && python3 gen.py
//
// 用法：Clash Verge Rev「扩展脚本」/ Mihomo Party(Clash Party)「覆写」。
// 这两家的 JS 接口一致：入口 main，拿到解析后的 config 对象，返回改完的它。
// Stash 的「覆写」是 .stoverride（YAML，非 JS），ClashX 没有覆写机制，都用不了本文件。
//
// 订阅自带的 proxies / proxy-providers 不在 override 里（见 JS_DROP），故原样保留；
// 其余段落整段替换成本仓库的配置。

const override = {body};

function main(config, profileName) {{
  // 文档要求「返回修改后的该参数」，所以就地改 config 再返回，不要返回新对象。
  return Object.assign(config, override);
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
        ("smart", "smart.yaml",
         "Mihomo 配置 — Smart 内核版（type: smart，需 vernesong/mihomo smart 内核）"),
        ("url-test", "urltest.yaml",
         "Mihomo 配置 — 通用版（type: url-test，官方 mihomo 内核即可）"),
    ]
    for kind, out, title in targets:
        # LightGBM 模型配置仅属于 Smart 内核，避免污染通用 url-test 配置。
        target_head = head
        if kind == "smart":
            smart_model_config = """# Smart LightGBM 模型自动更新
lgbm-auto-update: true
lgbm-update-interval: 72
lgbm-url: "https://github.com/vernesong/mihomo/releases/download/LightGBM-Model/Model.bin"

"""
            target_head = target_head.replace("profile:\n", smart_model_config + "profile:\n", 1)
            target_head = target_head.replace(
                "  store-fake-ip: true\n",
                "  store-fake-ip: true\n  smart-collector-size: 100\n",
                1,
            )
        body = HEADER.format(title=title) + target_head + "\n\n" + build_groups(kind) + "\n" + rules
        (BUILD / out).write_text(body, encoding="utf-8")
        print("wrote", out)
        js = out.replace(".yaml", ".js")
        (BUILD / js).write_text(build_js(body, title), encoding="utf-8")
        print("wrote", js)
