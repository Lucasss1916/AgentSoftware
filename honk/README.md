# honk 配置

[honk](https://github.com/daeuniverse/honk) 是 daeuniverse 用 Rust 写的 Linux 透明代理
（TC eBPF + `dae0`/`daens`），配置语言是 **dae 方言**，不是 YAML。本目录这份配置
由 [`clash/yaml/urltest.yaml`](../clash/yaml/README.md) 移植而来，分流顺序与之逐条对应。

> honk 自称 early-alpha，1.0 前的小版本可能改配置或行为。本配置按
> 2026-11-02 的 `main` 文档编写。

## 运行前提

honk 与 Clash 的部署模型不同，这几点是硬要求：

- **Linux，内核 6.12+，root，挂载 bpffs**。没有 macOS / Windows / iOS 版本。
- **接管范围由网卡决定，没有 TUN**。`global.wan_interface` 管本机发出的流量，
  `lan_interface` 管转发流量。`lan_interface` 留空是字面意义的「不装 LAN 钩子」。
- **geosite.dat 必须用 Loyalsoldier 版**。`routing-tail.dae` 用到的 `gfw` 以及
  `apple-cn` 这类分类只有它有，v2fly 上游没有。`config.dae` 的 `assets` 段已钉住
  下载地址；换成 v2fly 版会让那几条规则静默失效，只留一条「缺分类」告警。
- **默认不含任何节点**，和 Clash 侧注释掉 `proxy-providers` 的做法一致。
  不填节点时各组为空，honk 对代理流量 fail-closed（丢弃，而不是偷偷直连）。

```sh
honk -c /etc/honk/config.dae      # 启动（需 root）
honk reload                       # 改完配置重载（发 SIGHUP）
honk-tool diagnose                # 只读体检：eBPF、map、API、网络管线
```

> honk **没有** `validate` / `check` 子命令：`mode` 虽然会校验，但它明确拒绝改写
> `.dae`（写不回 dae 的语法、注释和 include）。所以这份配置没法离线机器校验，
> 第一次用请先 `honk-tool diagnose`，并用 `log_level: debug` 看实际选路。

## 文件结构

```
honk/
├── config.dae         入口：global / assets / dns / group / routing / experimental / include
├── routing-tail.dae   路由尾段：geosite 大表与 fallback，必须最后 include
└── rule/*.dae         自有规则集，由 sync_rules.py 从 loon/rule/*.list 生成
```

### 为什么要拆出 routing-tail.dae

honk 不支持远程规则集（只认 `geosite:`/`geoip:` 的 dat 文件，加内联 `domain()`），
所以 `loon/rule/*.list` 由 `sync_rules.py` 预编译成 dae 的 `routing` 片段。

而 honk 的合并顺序是固定的：**入口文件的 section 先合并，被 include 的片段依次追加
在后面**。`geosite: gfw`、`geosite: cn` 这些口径动辄数万条，一旦排在自有规则集前面，
机场域名、Emby 站、Talktone 这些就会先被它们吃掉、再也到不了自己的规则。

所以分三层，顺序即优先级：

| 层 | 内容 | 对应 Clash 规则位置 |
| --- | --- | --- |
| `config.dae` 的 `routing` | 自我保护 + 具体域名 / IP / geosite 精确规则 | 第 1–57 条 |
| `include` 列出的 `rule/*.dae` | 8 个自有规则集，拦截类排在功能类之前 | 第 3、31、40–44、58 条 |
| `routing-tail.dae` | geosite 大表 + `fallback` | 第 59–64 条 |

`include` 块逐个列出文件而不用 `rule/*.dae` 通配，就是因为通配按字典序
（`Saily.dae` 会排在 `SailyAds.dae` 前面，正好把拦截列表挤到功能列表之后）。

`honk/rule/` 下另有 11 个 Clash 侧没引用的规则集，默认不在 `include` 里；要启用就
加进去，并先在 `sync_rules.py` 的 `HONK_OUTBOUND` 表里确认出口。

## 策略组对应关系

组名换成了 ASCII —— honk 的组名同时是 `routing` 里的出口标识符，而
`-> 🍿 国外媒体` 这种带空格的目标会和 dae 的动作解析打架。

| Clash 策略组 | honk 组 | 策略 |
| --- | --- | --- |
| ✈️ 节点选择 | `proxy` | selector |
| 🚀 我的节点 | `manual` | selector（全部节点） |
| 🌐 全球直连 | `cn_direct` | selector（内置 direct） |
| 🍿 国外媒体 | `media` | selector |
| 🎥 视频 | `video` | selector |
| 📟 智能助理 | `ai` | selector |
| 📲 电报信息 | `telegram` | selector |
| 📞 TalkTone | `talktone` | selector（全部节点） |
| Ⓜ️ 微软服务 | `microsoft` | selector |
| 🍎 苹果服务 | `apple` | selector |
| 🎮 游戏平台 | `games` | selector |
| 🐟 漏网之鱼 | `leftover` | selector（`fallback` 指向它） |
| 🇭🇰/🇯🇵/🇹🇼/🇸🇬/🇰🇷/🇺🇲/🌏/🇪🇺 地区组 | `hk` `jp` `tw` `sg` `kr` `na` `asia` `eu` | urltest |

地区组的过滤正则照搬 `clash/yaml/gen.py` 的 `REGIONS`。honk 的
`name(regex: ...)` 只按逗号拆候选项，正则里的 `|` 原样保留，`(?i)` 与 Clash 同义；
用的是 Rust `regex`，**不支持 `(?!...)` 之类的环视**（这几条都没用到）。

想要 `smart.yaml` 那种自适应选路，把地区组的 `policy: urltest` 改成 `policy: score`
即可 —— honk 的 score 按真实流量的可靠性与目标质量选节点，不需要 LightGBM 模型。

## 未能等价移植的部分

这些不是偷工减料，是 honk 与 Clash 的能力边界差异，逐条列明：

| Clash 侧 | honk 侧 | 说明 |
| --- | --- | --- |
| `RULE-SET,AI-fmz200` | **已丢弃** | fmz200 的 AI.list 没有 geosite 对应物，也不是本仓库规则源。`category-ai-!cn` 已覆盖大部分 |
| `RULE-SET,WeChat` | `geosite: tencent` | geosite 没有 wechat 分类，用同集团分类近似，**口径更宽** |
| `RULE-SET,GlobalMedia` | `geosite: category-media` | 近似，非同源 |
| `RULE-SET,Proxy` | `geosite: gfw` | 近似，非同源 |
| `RULE-SET,ChinaMax` | `geosite: cn` + `geolocation-cn` | 近似，非同源 |
| `RULE-SET,ChinaDNS` | `geosite: cn` + `geolocation-cn` | 同上，用在 DNS 请求路由里 |
| `enhanced-mode: fake-ip` | **无对应物** | honk 走真实解析加路由投影，`fake-ip-range` / `fake-ip-filter` 整段无需移植 |
| `hosts:` 前两条 | **无法表达** | `updates.g.aaplimg.com` → 另一个**域名**；honk 的 hosts 只接受 IP |
| `hosts:` 后四条 DoH IP | 已内联进 upstream | 改用 `https://IP/dns-query?tls_server_name=域名`，顺带消掉引导依赖 |
| `ipv6: false` | `ipversion_prefer: 4` | 近似：两个族都仍可查，有 IPv4 结果时抑制 AAAA |
| 逐条 `no-resolve` | **已丢弃** | honk 没有逐条开关，解析行为由 `dns` 段统一决定；各 `rule/*.dae` 头部注明丢弃条数 |
| 22 条 `USER-AGENT` 规则 | **跳过** | honk 无对应匹配函数，与 Egern / sing-box / Anywhere 一致 |
| `IP-ASN` / `URL-REGEX` | **跳过** | 同上 |
| `tun:` | `wan_interface` / `lan_interface` | 部署模型不同，见上文 |
| `proxy-groups` 的 `hidden` | **无对应物** | honk 的组一律可见 |
| emoji 组名 | ASCII 组名 | 见上文对应表 |

反过来，这几条是 honk 侧**新增**的、Clash 不需要的：

| honk 配置 | 为什么必须有 |
| --- | --- |
| `pname(...) -> direct(must)` 自我保护段 | honk 不再自动插入本机地址的 direct 规则，漏写会让网关自身的 DNS / DHCP / 路由管理流量被自己接管，容易锁死机器 |
| `dip(geoip: private, ...) && !dport(53)` | 宽泛的 private `direct(must)` 会把内网 DNS 一起放过去，加上这条否定才保留 DNS 由 honk 接管（官方文档明确提示） |
| `qtype(https, svcb) -> reject` | honk 靠嗅探 TLS 明文 SNI 决定域名路由，HTTPS/SVCB 记录里的 ECH 会加密 ClientHello，嗅探就拿不到域名、域名规则集体失效。不需要可删 |
| `assets.geodata` 钉住 Loyalsoldier | 见上文「运行前提」 |

## Clash API

`experimental.clash_api` 默认绑 `127.0.0.1:9090`，而 Clash 侧是 `0.0.0.0:9090`。
honk 的 Clash API 只有明文 HTTP、不提供 TLS，官方文档明确要求绑回环或前置带认证的
TLS 反代。要从内网访问就改成 `0.0.0.0:9090`，并**务必**设置 `secret`。

> `secret` 是占位值，需自己填（至少 8 字节，短于 8 字节不会被 API 响应遮蔽）。
> 不要照抄 `clash/yaml/common_head.yaml` 里那个 —— 它已经明文进了 git 历史，应当轮换。

## 订阅地址

<!-- gen:import -->
| 文件 | 原始地址 |
| --- | --- |
| `config.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/config.dae> |
| `routing-tail.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/routing-tail.dae> |

> honk 是 Linux 守护进程，用 `-c` 读本地文件，没有 URL Scheme 可一键导入。`config.dae` 是入口，`routing-tail.dae` 由它的 `include` 块引入且必须排在最后。两份都是手写的，不由脚本生成。
<!-- /gen:import -->

## 维护方式

`rule/*.dae` 由 `sync_rules.py` 生成，**不要直接编辑**；改规则请改
`loon/rule/*.list`，然后在仓库根运行：

```sh
python3 sync_rules.py          # 生成全部七种格式，含 honk/rule/*.dae
python3 gen_readme.py          # 更新各目录的订阅清单
```

`config.dae` 与 `routing-tail.dae` 是手写的，不在生成范围内。规则集与出口的对应
关系在 `sync_rules.py` 的 `HONK_OUTBOUND` 表里 —— 其余六家的规则文件只有「匹配」
没有「策略」，honk 没有这种分离：dae 的一条 `routing` 规则就是「匹配 + 出口」。
