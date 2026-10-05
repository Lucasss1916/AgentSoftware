// Mihomo 配置 — Smart 内核版（type: smart，需 vernesong/mihomo smart 内核）
// 由 gen.py 生成，勿手改。改完 common_head.yaml / routes.yaml / gen.py
// 后重跑： cd clash/yaml && python3 gen.py
//
// 用法：Clash Verge Rev「扩展脚本」/ Mihomo Party(Clash Party)「覆写」。
// 这两家的 JS 接口一致：入口 main，拿到解析后的 config 对象，返回改完的它。
// Stash 的「覆写」是 .stoverride（YAML，非 JS），ClashX 没有覆写机制，都用不了本文件。
//
// 订阅自带的 proxies / proxy-providers 不在 override 里（见 JS_DROP），故原样保留；
// 其余段落整段替换成本仓库的配置。

const override = {
  "allow-lan": true,
  "mode": "rule",
  "log-level": "info",
  "ipv6": false,
  "unified-delay": true,
  "tcp-concurrent": true,
  "find-process-mode": "strict",
  "keep-alive-interval": 30,
  "lgbm-auto-update": true,
  "lgbm-update-interval": 72,
  "lgbm-url": "https://github.com/vernesong/mihomo/releases/download/LightGBM-Model/Model.bin",
  "profile": {
    "store-selected": true,
    "store-fake-ip": true,
    "smart-collector-size": 100
  },
  "tun": {
    "enable": true,
    "stack": "mixed",
    "device": "Mihomo",
    "endpoint-independent-nat": true,
    "auto-route": true,
    "auto-detect-interface": true,
    "auto-redirect": false,
    "strict-route": false,
    "dns-hijack": [
      "any:53"
    ],
    "route-exclude-address": [
      "192.168.0.0/16",
      "10.0.0.0/8",
      "172.16.0.0/12",
      "127.0.0.0/8"
    ],
    "mtu": 1350
  },
  "sniffer": {
    "enable": true,
    "parse-pure-ip": true,
    "force-dns-mapping": true,
    "override-destination": true,
    "sniff": {
      "HTTP": {
        "ports": [
          80,
          443
        ],
        "override-destination": true
      },
      "TLS": {
        "ports": [
          443
        ]
      },
      "QUIC": {
        "ports": [
          443
        ]
      }
    },
    "skip-domain": [
      "+.push.apple.com",
      "+.apple.com",
      "Mijia Cloud"
    ],
    "force-domain": [],
    "skip-src-address": []
  },
  "hosts": {
    "updates.g.aaplimg.com": "updates.cdn-apple.com.download.ks-cdn.com",
    "iosapps.itunes.apple.com": "iosapps.itunes.apple.com.download.ks-cdn.com",
    "dns.alidns.com": [
      "223.5.5.5",
      "223.6.6.6"
    ],
    "doh.pub": [
      "1.12.12.12",
      "120.53.53.53"
    ],
    "cloudflare-dns.com": [
      "104.16.249.249",
      "104.16.248.249"
    ],
    "dns.google": [
      "8.8.8.8",
      "8.8.4.4"
    ]
  },
  "dns": {
    "enable": true,
    "listen": "0.0.0.0:7874",
    "ipv6": false,
    "prefer-h3": false,
    "enhanced-mode": "fake-ip",
    "fake-ip-range": "198.18.0.0/16",
    "use-hosts": true,
    "use-system-hosts": true,
    "respect-rules": true,
    "default-nameserver": [
      "system",
      "223.5.5.5",
      "119.29.29.29"
    ],
    "nameserver": [
      "https://cloudflare-dns.com/dns-query",
      "https://dns.google/dns-query"
    ],
    "proxy-server-nameserver": [
      "223.5.5.5",
      "119.29.29.29"
    ],
    "nameserver-policy": {
      "*.linux.do": "https://stellafortuna.ddd.oaifree.com/query-dns",
      "api64.ipify.org": "udp://[2001:4860:4860::8888]:53",
      "rule-set:ChinaDNS": [
        "https://dns.alidns.com/dns-query",
        "https://doh.pub/dns-query"
      ],
      "+.cn": [
        "https://dns.alidns.com/dns-query",
        "https://doh.pub/dns-query"
      ],
      "+.local": [
        "system"
      ],
      "localhost": [
        "system"
      ],
      "rule-set:PrivateDNS": [
        "system"
      ]
    },
    "fake-ip-filter": [
      "*.lan",
      "*.local",
      "*.orb.local",
      "localhost",
      "+.market.xiaomi.com",
      "+.weixin.qq.com",
      "+.qpic.cn",
      "+.qq.com",
      "localhost.ptlogin2.qq.com",
      "time.*.com",
      "time.*.gov",
      "ntp.*.com",
      "+.pool.ntp.org",
      "*.stun.*",
      "*.stun.*.*",
      "stun.l.google.com",
      "stun1.l.google.com",
      "stun2.l.google.com",
      "+.srv.nintendo.net",
      "+.stun.playstation.net",
      "xbox.*.microsoft.com",
      "+.xboxlive.com",
      "+.battlenet.com.cn",
      "+.battlenet.com",
      "+.blzstatic.cn",
      "+.battle.net",
      "stun.ugreengroup.com",
      "+.msftconnecttest.com",
      "+.msftncsi.com",
      "captive.apple.com"
    ]
  },
  "proxy-groups": [
    {
      "name": "✈️ 节点选择",
      "type": "select",
      "proxies": [
        "🚀 我的节点",
        "🌐 全球直连"
      ]
    },
    {
      "name": "🚀 我的节点",
      "type": "select",
      "include-all": true,
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置"
    },
    {
      "name": "🌐 全球直连",
      "type": "select",
      "proxies": [
        "DIRECT"
      ]
    },
    {
      "name": "📲 电报信息",
      "type": "select",
      "proxies": [
        "🇸🇬 新加坡节点",
        "🇯🇵 日本节点",
        "🇨🇳 台湾节点",
        "🇭🇰 香港节点",
        "✈️ 节点选择",
        "🇺🇲 北美节点",
        "🇰🇷 韩国节点",
        "🚀 我的节点",
        "🌏 其他亚洲节点",
        "🇪🇺 欧洲节点"
      ]
    },
    {
      "name": "📞 TalkTone",
      "type": "select",
      "include-all": true,
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置"
    },
    {
      "name": "🎥 视频",
      "type": "select",
      "include-all": true,
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置",
      "proxies": [
        "🚀 我的节点",
        "✈️ 节点选择",
        "🇰🇷 韩国节点",
        "🇺🇲 北美节点",
        "🇨🇳 台湾节点",
        "🇸🇬 新加坡节点",
        "🇯🇵 日本节点",
        "🌐 全球直连",
        "🌏 其他亚洲节点",
        "🇪🇺 欧洲节点"
      ]
    },
    {
      "name": "🍿 国外媒体",
      "type": "select",
      "proxies": [
        "✈️ 节点选择",
        "🇭🇰 香港节点",
        "🇺🇲 北美节点",
        "🇯🇵 日本节点",
        "🇰🇷 韩国节点",
        "🇸🇬 新加坡节点",
        "🇨🇳 台湾节点",
        "🌏 其他亚洲节点",
        "🇪🇺 欧洲节点"
      ]
    },
    {
      "name": "📟 智能助理",
      "type": "select",
      "proxies": [
        "✈️ 节点选择",
        "🇺🇲 北美节点",
        "🇯🇵 日本节点",
        "🇰🇷 韩国节点",
        "🇸🇬 新加坡节点",
        "🇨🇳 台湾节点",
        "🌏 其他亚洲节点",
        "🇪🇺 欧洲节点"
      ]
    },
    {
      "name": "Ⓜ️ 微软服务",
      "type": "select",
      "proxies": [
        "🌐 全球直连",
        "✈️ 节点选择",
        "🇭🇰 香港节点",
        "🇺🇲 北美节点",
        "🇯🇵 日本节点",
        "🇰🇷 韩国节点",
        "🇸🇬 新加坡节点",
        "🇨🇳 台湾节点",
        "🌏 其他亚洲节点",
        "🇪🇺 欧洲节点"
      ]
    },
    {
      "name": "🍎 苹果服务",
      "type": "select",
      "proxies": [
        "🌐 全球直连",
        "✈️ 节点选择",
        "🇭🇰 香港节点",
        "🇺🇲 北美节点",
        "🇯🇵 日本节点",
        "🇰🇷 韩国节点",
        "🇸🇬 新加坡节点",
        "🇨🇳 台湾节点",
        "🌏 其他亚洲节点",
        "🇪🇺 欧洲节点"
      ]
    },
    {
      "name": "🎮 游戏平台",
      "type": "select",
      "proxies": [
        "🌐 全球直连",
        "✈️ 节点选择",
        "🇭🇰 香港节点",
        "🇺🇲 北美节点",
        "🇯🇵 日本节点",
        "🇰🇷 韩国节点",
        "🇸🇬 新加坡节点",
        "🇨🇳 台湾节点",
        "🌏 其他亚洲节点",
        "🇪🇺 欧洲节点"
      ]
    },
    {
      "name": "🐟漏网之鱼",
      "type": "select",
      "proxies": [
        "🇸🇬 新加坡节点",
        "🇯🇵 日本节点",
        "🇨🇳 台湾节点",
        "🇭🇰 香港节点",
        "🚀 我的节点",
        "🇺🇲 北美节点",
        "🇰🇷 韩国节点",
        "🌏 其他亚洲节点",
        "🇪🇺 欧洲节点"
      ]
    },
    {
      "name": "🇭🇰 香港节点",
      "type": "smart",
      "include-all": true,
      "filter": "(?i)(🇭🇰|香港|Hong|HK)",
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置",
      "hidden": true,
      "interval": 300,
      "uselightgbm": true,
      "collectdata": true,
      "policy-priority": "Mitce:0.3;iku:0.3;kitty:0.6"
    },
    {
      "name": "🇯🇵 日本节点",
      "type": "smart",
      "include-all": true,
      "filter": "(?i)(🇯🇵|日本|Japan|JP)",
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置|美国|美國",
      "hidden": true,
      "interval": 300,
      "uselightgbm": true,
      "collectdata": true,
      "policy-priority": "Mitce:0.3;iku:0.3;kitty:0.6"
    },
    {
      "name": "🇨🇳 台湾节点",
      "type": "smart",
      "include-all": true,
      "filter": "(?i)(🇹🇼|台湾|臺灣|台灣|Taiwan|Tai|TW|mv)",
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置",
      "hidden": true,
      "interval": 300,
      "uselightgbm": true,
      "collectdata": true,
      "policy-priority": "Mitce:0.3;iku:0.3;kitty:0.6"
    },
    {
      "name": "🇸🇬 新加坡节点",
      "type": "smart",
      "include-all": true,
      "filter": "(?i)(🇸🇬|新加坡|Singapore|SG)",
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置",
      "hidden": true,
      "interval": 300,
      "uselightgbm": true,
      "collectdata": true,
      "policy-priority": "Mitce:0.3;iku:0.3;kitty:0.6"
    },
    {
      "name": "🇰🇷 韩国节点",
      "type": "smart",
      "include-all": true,
      "filter": "(?i)(🇰🇷|韩国|韓國|Korea|KR)",
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置",
      "hidden": true,
      "interval": 300,
      "uselightgbm": true,
      "collectdata": true,
      "policy-priority": "Mitce:0.3;iku:0.3;kitty:0.6"
    },
    {
      "name": "🇺🇲 北美节点",
      "type": "smart",
      "include-all": true,
      "filter": "(?i)(🇺🇸|🇨🇦|🇲🇽|美国|美國|加拿大|墨西哥|States|Canada|Mexico|USA|(^|[^A-Za-z])US([^A-Za-z]|$)|(^|[^A-Za-z])CA([^A-Za-z]|$)|洛杉矶|圣何塞|西雅图|达拉斯|纽约|芝加哥|硅谷|凤凰城|亚特兰大|迈阿密|拉斯维加斯|波特兰|费利蒙|阿什本|多伦多|温哥华|蒙特利尔|Los Angeles|San Jose|Seattle|Dallas|New York|Chicago|Miami|Ashburn|Phoenix|Fremont|Portland|Las Vegas|Atlanta|Silicon Valley|Toronto|Vancouver|Montreal)",
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置",
      "hidden": true,
      "interval": 300,
      "uselightgbm": true,
      "collectdata": true,
      "policy-priority": "Mitce:0.3;iku:0.3;kitty:0.6"
    },
    {
      "name": "🌏 其他亚洲节点",
      "type": "smart",
      "include-all": true,
      "filter": "(?i)(🇲🇾|马来|大马|吉隆坡|Malaysia|🇹🇭|泰国|曼谷|Thailand|🇻🇳|越南|胡志明|Vietnam|🇵🇭|菲律宾|马尼拉|Philippines|🇮🇩|印尼|印度尼西亚|雅加达|Indonesia|🇮🇳|印度|孟买|India|🇰🇭|柬埔寨|金边|Cambodia|🇱🇦|老挝|Laos|🇲🇲|缅甸|Myanmar|🇧🇳|文莱|Brunei|🇧🇩|孟加拉|Bangladesh|🇵🇰|巴基斯坦|Pakistan|🇳🇵|尼泊尔|Nepal|🇱🇰|斯里兰卡|Lanka)",
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置",
      "hidden": true,
      "interval": 300,
      "uselightgbm": true,
      "collectdata": true,
      "policy-priority": "Mitce:0.3;iku:0.3;kitty:0.6"
    },
    {
      "name": "🇪🇺 欧洲节点",
      "type": "smart",
      "include-all": true,
      "filter": "(?i)(🇬🇧|英国|伦敦|United Kingdom|Britain|London|(^|[^A-Za-z])UK([^A-Za-z]|$)|🇩🇪|德国|德國|法兰克福|Germany|Frankfurt|🇫🇷|法国|法國|巴黎|France|Paris|🇳🇱|荷兰|荷蘭|阿姆斯特丹|Netherlands|Amsterdam|🇷🇺|俄罗斯|俄羅斯|莫斯科|Russia|Moscow|🇹🇷|土耳其|Turkey|Istanbul|🇮🇹|意大利|米兰|Italy|Milan|🇪🇸|西班牙|马德里|Spain|Madrid|🇸🇪|瑞典|Sweden|🇨🇭|瑞士|Switzerland|Zurich|🇵🇱|波兰|Poland|Warsaw|🇺🇦|乌克兰|Ukraine|🇮🇪|爱尔兰|Ireland|Dublin|🇫🇮|芬兰|Finland|🇳🇴|挪威|Norway|🇩🇰|丹麦|Denmark|🇧🇪|比利时|Belgium|🇦🇹|奥地利|Austria|Vienna|🇵🇹|葡萄牙|Portugal|Lisbon|🇨🇿|捷克|Czech|Prague|🇷🇴|罗马尼亚|Romania|🇭🇺|匈牙利|Hungary|🇬🇷|希腊|Greece|Athens|🇷🇸|塞尔维亚|Serbia|🇧🇬|保加利亚|Bulgaria|🇱🇻|拉脱维亚|Latvia|🇱🇹|立陶宛|Lithuania|🇪🇪|爱沙尼亚|Estonia|🇲🇩|摩尔多瓦|Moldova|🇮🇸|冰岛|Iceland|欧洲|Europe)",
      "exclude-filter": "过期|剩余|流量|官网|套餐|返利|订阅|重置",
      "hidden": true,
      "interval": 300,
      "uselightgbm": true,
      "collectdata": true,
      "policy-priority": "Mitce:0.3;iku:0.3;kitty:0.6"
    }
  ],
  "rule-providers": {
    "Myairport": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/clash/rule/MyAiport.yaml"
    },
    "DirectDomain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/clash/rule/DirectDomain.yaml"
    },
    "TalktoneProxy": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/clash/rule/TalktoneProxy.yaml"
    },
    "TalktoneAds": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/clash/rule/TalktoneAds.yaml"
    },
    "TalktoneDirect": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/clash/rule/TalktoneDirect.yaml"
    },
    "MyVideo": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/clash/rule/myvideorule.yaml"
    },
    "AI-category": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ai-!cn.mrs"
    },
    "AI-fmz200": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/fmz200/wool_scripts/main/Loon/rule/AI.list"
    },
    "Duolingo": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Duolingo/Duolingo.list"
    },
    "Apple": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Apple/Apple.list"
    },
    "GitHub": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GitHub/GitHub.list"
    },
    "Microsoft": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Microsoft/Microsoft.list"
    },
    "Telegram": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Telegram/Telegram.list"
    },
    "Epic": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Epic/Epic.list"
    },
    "Sony": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Sony/Sony.list"
    },
    "Steam": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Steam/Steam.list"
    },
    "Nintendo": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Nintendo/Nintendo.list"
    },
    "YouTube": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/YouTube/YouTube.list"
    },
    "GlobalMedia": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GlobalMedia/GlobalMedia.list"
    },
    "Proxy": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Proxy/Proxy.list"
    },
    "ChinaMedia": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/ChinaMedia/ChinaMedia.list"
    },
    "ChinaMax": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/ChinaMax/ChinaMax.list"
    },
    "WeChat": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/WeChat/WeChat.list"
    },
    "ChinaDNS": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://raw.githubusercontent.com/metacubex/meta-rules-dat/meta/geo/geosite/cn.mrs"
    },
    "PrivateDNS": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://raw.githubusercontent.com/metacubex/meta-rules-dat/meta/geo/geosite/private.mrs"
    }
  },
  "rules": [
    "DOMAIN,linux.do,🇸🇬 新加坡节点",
    "DOMAIN,agentrouter.org,🍿 国外媒体",
    "RULE-SET,Myairport,🍿 国外媒体",
    "DOMAIN-SUFFIX,alidns.com,DIRECT",
    "DOMAIN-SUFFIX,doh.pub,DIRECT",
    "DOMAIN-SUFFIX,cloudflare-dns.com,🍿 国外媒体",
    "DOMAIN-SUFFIX,dns.google,🍿 国外媒体",
    "RULE-SET,PrivateDNS,DIRECT",
    "DOMAIN,localhost,DIRECT",
    "DOMAIN-SUFFIX,local,DIRECT",
    "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve",
    "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,172.16.0.0/12,DIRECT,no-resolve",
    "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,100.64.0.0/10,DIRECT,no-resolve",
    "IP-CIDR6,::1/128,DIRECT,no-resolve",
    "IP-CIDR6,fc00::/7,DIRECT,no-resolve",
    "IP-CIDR6,fe80::/10,DIRECT,no-resolve",
    "DOMAIN-KEYWORD,emby.991600.xyz,DIRECT",
    "DOMAIN-KEYWORD,osaka.991600.xyz,DIRECT",
    "IP-CIDR,141.147.153.168/32,DIRECT,no-resolve",
    "DOMAIN-SUFFIX,oraclecloud.com,✈️ 节点选择",
    "DOMAIN-SUFFIX,muyuan.do,🍿 国外媒体",
    "DOMAIN-SUFFIX,anyrouter.top,✈️ 节点选择",
    "DOMAIN-SUFFIX,hgemby.qzz.io,🎥 视频",
    "RULE-SET,AI-category,📟 智能助理",
    "RULE-SET,AI-fmz200,📟 智能助理",
    "DOMAIN-SUFFIX,lucky.991600.xyz,🌐 全球直连",
    "DOMAIN-SUFFIX,e5.991600.xyz,🌐 全球直连",
    "DOMAIN-SUFFIX,fnos.991600.xyz,✈️ 节点选择",
    "RULE-SET,DirectDomain,🌐 全球直连",
    "DOMAIN-SUFFIX,991600.xyz,🍿 国外媒体",
    "DOMAIN-SUFFIX,netflav.com,🎥 视频",
    "DOMAIN-SUFFIX,surrit.com,🎥 视频",
    "RULE-SET,Duolingo,🌐 全球直连",
    "RULE-SET,WeChat,DIRECT",
    "DOMAIN-SUFFIX,macapp.org.cn,🍿 国外媒体",
    "DOMAIN-SUFFIX,cloudflare.com,🌐 全球直连",
    "DOMAIN-SUFFIX,sharepoint.com,Ⓜ️ 微软服务",
    "RULE-SET,TalktoneProxy,📞 TalkTone",
    "RULE-SET,TalktoneAds,REJECT",
    "RULE-SET,TalktoneDirect,🌐 全球直连",
    "DOMAIN-SUFFIX,testflight.apple.com,🍿 国外媒体",
    "DOMAIN,beta.itunes.apple.com,🍿 国外媒体",
    "DOMAIN,iosapps.itunes.apple.com,🌐 全球直连",
    "DOMAIN-SUFFIX,mzstatic.com,🌐 全球直连",
    "RULE-SET,Apple,🍎 苹果服务,no-resolve",
    "RULE-SET,GitHub,🍿 国外媒体",
    "RULE-SET,Microsoft,Ⓜ️ 微软服务",
    "RULE-SET,Telegram,📲 电报信息",
    "RULE-SET,Epic,🎮 游戏平台",
    "RULE-SET,Sony,🎮 游戏平台",
    "RULE-SET,Steam,🎮 游戏平台",
    "RULE-SET,Nintendo,🎮 游戏平台",
    "RULE-SET,YouTube,🍿 国外媒体",
    "RULE-SET,MyVideo,🎥 视频",
    "RULE-SET,GlobalMedia,🍿 国外媒体,no-resolve",
    "RULE-SET,Proxy,🍿 国外媒体,no-resolve",
    "RULE-SET,ChinaMedia,🌐 全球直连",
    "RULE-SET,ChinaMax,🌐 全球直连",
    "GEOIP,CN,🌐 全球直连",
    "MATCH,🐟漏网之鱼"
  ]
};

function main(config, profileName) {
  // 文档要求「返回修改后的该参数」，所以就地改 config 再返回，不要返回新对象。
  return Object.assign(config, override);
}
