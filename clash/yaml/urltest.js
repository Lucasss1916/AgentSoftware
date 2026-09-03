// Mihomo 配置 — 通用版（type: url-test，官方 mihomo 内核即可）
// 由 gen.py 生成，勿手改。改完 common_head.yaml / common_rules.yaml / routes.yaml
// 后重跑： cd clash/yaml && python3 gen.py
//
// 用法：Clash Verge Rev / Clash Party「扩展脚本」，或 Stash / ClashX 的 JS 覆写。
// 订阅自带的 proxies 与 proxy-providers 原样保留，其余段落全部换成本仓库的配置。

const override = {
  "allow-lan": true,
  "mode": "rule",
  "log-level": "info",
  "ipv6": false,
  "unified-delay": true,
  "tcp-concurrent": true,
  "find-process-mode": "strict",
  "keep-alive-interval": 30,
  "profile": {
    "store-selected": true,
    "store-fake-ip": true
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
    "route-exclude-address": [],
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
  "dns": {
    "enable": true,
    "listen": "0.0.0.0:7874",
    "ipv6": false,
    "prefer-h3": false,
    "enhanced-mode": "fake-ip",
    "fake-ip-range": "198.18.0.0/16",
    "use-hosts": false,
    "use-system-hosts": false,
    "respect-rules": true,
    "default-nameserver": [
      "223.5.5.5",
      "119.29.29.29"
    ],
    "nameserver": [
      "https://223.5.5.5/dns-query",
      "https://doh.pub/dns-query"
    ],
    "proxy-server-nameserver": [
      "https://223.5.5.5/dns-query"
    ],
    "direct-nameserver": [
      "https://223.5.5.5/dns-query",
      "https://doh.pub/dns-query"
    ],
    "fallback": [],
    "nameserver-policy": {
      "rule-set:ChatGPT / Domain,GitHub / Domain,Telegram / Domain,Google / Domain,Youtube / Domain,Twitter / Domain,Facebook / Domain,Netflix / Domain,TikTok / Domain,Disney / Domain,Spotify / Domain,Reddit / Domain": [
        "https://dns.google/dns-query",
        "https://cloudflare-dns.com/dns-query"
      ],
      "rule-set:China / Domain,Apple-CN / Domain": [
        "https://223.5.5.5/dns-query",
        "https://doh.pub/dns-query"
      ],
      "rule-set:Private / Domain": [
        "system"
      ]
    },
    "fake-ip-filter": [
      "*.lan",
      "*.local",
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
      "msftconnecttest.com",
      "msftncsi.com",
      "+.msftconnecttest.com",
      "+.msftncsi.com",
      "captive.apple.com"
    ]
  },
  "proxy-groups": [
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "AIGC",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/OpenAI.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "GitHub",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/github.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "Telegram",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Telegram.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "Video",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Emby.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "国外媒体",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Google.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "Spotify",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Spotify.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "Apple",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Apple.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "Microsoft",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Microsoft.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "Steam",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Steam.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "Game",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/GAME.png"
    },
    {
      "type": "select",
      "proxies": [
        "所有-手选",
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "其他",
        "DIRECT",
        "REJECT"
      ],
      "name": "Test",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Urltest.png"
    },
    {
      "name": "Block",
      "type": "select",
      "icon": "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Adblock.png",
      "proxies": [
        "REJECT",
        "DIRECT"
      ]
    },
    {
      "name": "所有-手选",
      "type": "select",
      "include-all": true,
      "icon": "https://www.clashverge.dev/assets/icons/adjust.svg"
    },
    {
      "name": "漏网之鱼",
      "type": "fallback",
      "icon": "https://www.clashverge.dev/assets/icons/fish.svg",
      "proxies": [
        "香港-延时优选",
        "台湾-延时优选",
        "日本-延时优选",
        "新加坡-延时优选",
        "韩国-延时优选",
        "美国-延时优选",
        "英国-延时优选",
        "所有-手选",
        "其他",
        "DIRECT"
      ]
    },
    {
      "name": "香港-延时优选",
      "type": "url-test",
      "url": "https://www.gstatic.com/generate_204",
      "tolerance": 30,
      "lazy": true,
      "include-all": true,
      "interval": 300,
      "filter": "(?!.*(?i:10x))(?=.*(广港|香港|HK|Hong ?Kong|🇭🇰|HongKong)).*$",
      "icon": "https://fastly.jsdelivr.net/gh/Semporia/Hand-Painted-icon@master/Rounded_Rectangle/Hong_Kong.png"
    },
    {
      "name": "台湾-延时优选",
      "type": "url-test",
      "url": "https://www.gstatic.com/generate_204",
      "tolerance": 30,
      "lazy": true,
      "include-all": true,
      "interval": 300,
      "filter": "(?!.*(?i:10x))(?=.*(广台|台湾|台灣|TW|Tai ?Wan|🇹🇼|TaiWan|Taiwan)).*$",
      "icon": "https://fastly.jsdelivr.net/gh/Semporia/Hand-Painted-icon@master/Rounded_Rectangle/Taiwan.png"
    },
    {
      "name": "日本-延时优选",
      "type": "url-test",
      "url": "https://www.gstatic.com/generate_204",
      "tolerance": 30,
      "lazy": true,
      "include-all": true,
      "interval": 300,
      "filter": "(?!.*(?i:10x))(?=.*(广日|日本|JP|川日|东京|大阪|泉日|埼玉|沪日|深日|🇯🇵|Japan)).*$",
      "icon": "https://fastly.jsdelivr.net/gh/Semporia/Hand-Painted-icon@master/Rounded_Rectangle/Japan.png"
    },
    {
      "name": "新加坡-延时优选",
      "type": "url-test",
      "url": "https://www.gstatic.com/generate_204",
      "tolerance": 30,
      "lazy": true,
      "include-all": true,
      "interval": 300,
      "filter": "(?!.*(?i:10x))(?=.*(广新|新加坡|SG|坡|狮城|🇸🇬|Singapore)).*$",
      "icon": "https://fastly.jsdelivr.net/gh/Semporia/Hand-Painted-icon@master/Rounded_Rectangle/Singapore.png"
    },
    {
      "name": "韩国-延时优选",
      "type": "url-test",
      "url": "https://www.gstatic.com/generate_204",
      "tolerance": 30,
      "lazy": true,
      "include-all": true,
      "interval": 300,
      "filter": "(?!.*(?i:10x))(?=.*(广韩|韩国|韓國|KR|首尔|春川|🇰🇷|Korea)).*$",
      "icon": "https://fastly.jsdelivr.net/gh/Semporia/Hand-Painted-icon@master/Rounded_Rectangle/South_Korea.png"
    },
    {
      "name": "美国-延时优选",
      "type": "url-test",
      "url": "https://www.gstatic.com/generate_204",
      "tolerance": 30,
      "lazy": true,
      "include-all": true,
      "interval": 300,
      "filter": "(?!.*(?i:10x))(?=.*(广美|美国|US|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|拉斯|洛杉|圣何塞|圣克拉|西雅|芝加|🇺🇸|United ?States)).*$",
      "icon": "https://fastly.jsdelivr.net/gh/Semporia/Hand-Painted-icon@master/Rounded_Rectangle/United_States.png"
    },
    {
      "name": "英国-延时优选",
      "type": "url-test",
      "url": "https://www.gstatic.com/generate_204",
      "tolerance": 30,
      "lazy": true,
      "include-all": true,
      "interval": 300,
      "filter": "(?!.*(?i:10x))(?=.*(英国|伦敦|UK|United ?Kingdom|🇬🇧|London)).*$",
      "icon": "https://fastly.jsdelivr.net/gh/Semporia/Hand-Painted-icon@master/Rounded_Rectangle/England.png"
    },
    {
      "name": "其他",
      "type": "url-test",
      "url": "https://www.gstatic.com/generate_204",
      "tolerance": 30,
      "lazy": true,
      "include-all": true,
      "interval": 300,
      "filter": "^((?!(10x|10X|直连|拒绝|广港|香港|HK|Hong ?Kong|🇭🇰|HongKong|广台|台湾|台灣|TW|Tai ?Wan|🇹🇼|TaiWan|Taiwan|广日|日本|JP|川日|东京|大阪|泉日|埼玉|沪日|深日|🇯🇵|Japan|广新|新加坡|SG|坡|狮城|🇸🇬|Singapore|广韩|韩国|韓國|KR|首尔|春川|🇰🇷|Korea|广美|美国|US|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|拉斯|洛杉|圣何塞|圣克拉|西雅|芝加|🇺🇸|United ?States|英国|UK|United ?Kingdom|伦敦|London|🇬🇧|过期|剩余|流量|官网|套餐|机场|返利|订阅|重置)).)*$",
      "icon": "https://www.clashverge.dev/assets/icons/adjust.svg"
    }
  ],
  "rule-providers": {
    "MyVideo / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/refs/heads/main/clash/rule/myvideorule.yaml"
    },
    "DirectDomain / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/refs/heads/main/clash/rule/DirectDomain.yaml"
    },
    "ProxyDomain / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/refs/heads/main/clash/rule/ProxyDomain.yaml"
    },
    "NeedHighQualityNodeDomain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/refs/heads/main/clash/rule/NeedHighQualityNodeDomain.yaml"
    },
    "SteamCDN / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/refs/heads/main/clash/rule/steamCDN.yaml"
    },
    "TEST / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/liandu2024/clash/refs/heads/main/list/Check.list"
    },
    "Block / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/liandu2024/clash/refs/heads/main/list/Block.list"
    },
    "ChatGPT / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/openai.mrs"
    },
    "Claude / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Claude/Claude.list"
    },
    "Gemini / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/liandu2024/clash/refs/heads/main/list/Gemini.list"
    },
    "Copilot / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/liandu2024/clash/refs/heads/main/list/Copilot.list"
    },
    "Meta AI / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/liandu2024/clash/refs/heads/main/list/MetaAi.list"
    },
    "GitHub / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/github.mrs"
    },
    "Telegram / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/telegram.mrs"
    },
    "Telegram / IP": {
      "type": "http",
      "interval": 86400,
      "behavior": "ipcidr",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geoip/telegram.mrs"
    },
    "Twitter / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/x.mrs"
    },
    "Facebook / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/facebook.mrs"
    },
    "WhatsApp / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Whatsapp/Whatsapp.list"
    },
    "Reddit / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/reddit.mrs"
    },
    "Apple-CN / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/apple-cn.mrs"
    },
    "Apple / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/apple.mrs"
    },
    "Microsoft / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/microsoft.mrs"
    },
    "Amazon / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/amazon.mrs"
    },
    "Nvidia / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Nvidia/Nvidia.list"
    },
    "Unity / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/LM-Firefly/Rules/master/PROXY/Unity.list"
    },
    "Google / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/google.mrs"
    },
    "Google / IP": {
      "type": "http",
      "interval": 86400,
      "behavior": "ipcidr",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geoip/google.mrs"
    },
    "OKX / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/okx.mrs"
    },
    "Bybit / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/bybit.mrs"
    },
    "Binance / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/binance.mrs"
    },
    "Youtube / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/youtube.mrs"
    },
    "TikTok / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/tiktok.mrs"
    },
    "Netflix / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/netflix.mrs"
    },
    "Netflix / IP": {
      "type": "http",
      "interval": 86400,
      "behavior": "ipcidr",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geoip/netflix.mrs"
    },
    "Disney / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/disney.mrs"
    },
    "HBO / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/hbo.mrs"
    },
    "Crunchyroll / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/liandu2024/clash/refs/heads/main/list/Crunchyroll.list"
    },
    "Spotify / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/spotify.mrs"
    },
    "Steam / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/steam.mrs"
    },
    "Epic / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Epic/Epic.list"
    },
    "EA / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/EA/EA.list"
    },
    "Blizzard / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Blizzard/Blizzard.list"
    },
    "UBI / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/UBI/UBI.list"
    },
    "PlayStation / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/PlayStation/PlayStation.list"
    },
    "Nintend / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Nintendo/Nintendo.list"
    },
    "Discord / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Discord/Discord.list"
    },
    "Proxy / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/liandu2024/clash/refs/heads/main/list/Proxy.list"
    },
    "Globe / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Global/Global.list"
    },
    "Direct / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "classical",
      "format": "text",
      "url": "https://gh-proxy.com/raw.githubusercontent.com/liandu2024/clash/refs/heads/main/list/Direct.list"
    },
    "China / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/cn.mrs"
    },
    "China / IP": {
      "type": "http",
      "interval": 86400,
      "behavior": "ipcidr",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geoip/cn.mrs"
    },
    "Private / Domain": {
      "type": "http",
      "interval": 86400,
      "behavior": "domain",
      "format": "mrs",
      "url": "https://gh-proxy.com/github.com/metacubex/meta-rules-dat/raw/refs/heads/meta/geo/geosite/private.mrs"
    }
  },
  "rules": [
    "PROCESS-NAME,Weixin.exe,DIRECT",
    "PROCESS-NAME,WeChatAppEx.exe,DIRECT",
    "PROCESS-NAME,plastic.exe,DIRECT",
    "RULE-SET,Private / Domain,DIRECT",
    "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,172.16.0.0/12,DIRECT,no-resolve",
    "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve",
    "IP-CIDR,100.64.0.0/10,DIRECT,no-resolve",
    "RULE-SET,Block / Domain,Block",
    "RULE-SET,NeedHighQualityNodeDomain,所有-手选",
    "RULE-SET,DirectDomain / Domain,DIRECT",
    "RULE-SET,ProxyDomain / Domain,国外媒体",
    "RULE-SET,MyVideo / Domain,Video",
    "RULE-SET,TEST / Domain,Test",
    "DOMAIN-SUFFIX,linux.do,国外媒体",
    "RULE-SET,ChatGPT / Domain,AIGC",
    "RULE-SET,Claude / Domain,AIGC",
    "RULE-SET,Gemini / Domain,AIGC",
    "RULE-SET,Copilot / Domain,AIGC",
    "RULE-SET,Meta AI / Domain,AIGC",
    "RULE-SET,GitHub / Domain,GitHub",
    "RULE-SET,Telegram / Domain,Telegram",
    "RULE-SET,Telegram / IP,Telegram,no-resolve",
    "RULE-SET,Twitter / Domain,国外媒体",
    "RULE-SET,Facebook / Domain,国外媒体",
    "RULE-SET,WhatsApp / Domain,国外媒体",
    "RULE-SET,Reddit / Domain,国外媒体",
    "RULE-SET,Spotify / Domain,Spotify",
    "RULE-SET,Youtube / Domain,国外媒体",
    "RULE-SET,TikTok / Domain,国外媒体",
    "RULE-SET,Netflix / Domain,国外媒体",
    "RULE-SET,Netflix / IP,国外媒体,no-resolve",
    "RULE-SET,Disney / Domain,国外媒体",
    "RULE-SET,HBO / Domain,国外媒体",
    "RULE-SET,Crunchyroll / Domain,国外媒体",
    "RULE-SET,SteamCDN / Domain,DIRECT",
    "RULE-SET,Steam / Domain,Steam",
    "RULE-SET,Epic / Domain,Game",
    "RULE-SET,EA / Domain,Game",
    "RULE-SET,Blizzard / Domain,Game",
    "RULE-SET,UBI / Domain,Game",
    "RULE-SET,PlayStation / Domain,Game",
    "RULE-SET,Nintend / Domain,Game",
    "RULE-SET,Discord / Domain,Game",
    "RULE-SET,Apple-CN / Domain,DIRECT",
    "RULE-SET,Apple / Domain,Apple",
    "RULE-SET,Microsoft / Domain,Microsoft",
    "RULE-SET,Amazon / Domain,国外媒体",
    "RULE-SET,Nvidia / Domain,国外媒体",
    "RULE-SET,Unity / Domain,国外媒体",
    "RULE-SET,OKX / Domain,国外媒体",
    "RULE-SET,Bybit / Domain,国外媒体",
    "RULE-SET,Binance / Domain,国外媒体",
    "RULE-SET,Google / Domain,国外媒体",
    "RULE-SET,Google / IP,国外媒体,no-resolve",
    "RULE-SET,Proxy / Domain,国外媒体",
    "RULE-SET,Globe / Domain,国外媒体",
    "RULE-SET,Direct / Domain,DIRECT",
    "RULE-SET,China / Domain,DIRECT",
    "RULE-SET,China / IP,DIRECT,no-resolve",
    "GEOIP,CN,DIRECT,no-resolve",
    "MATCH,漏网之鱼"
  ]
};

function main(config) {
  return Object.assign({}, config, override);
}
