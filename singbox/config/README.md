# sing-box 配置

本目录的 `config.json` **由 `sync_config.py` 生成，请勿手改**。

- 改分流：编辑仓库根目录 `routes.yaml`，再跑 `python3 sync_config.py`
- 已经手改了 `config.json`：跑 `python3 sync_config.py --from-singbox` 回写，再跑一次正向同步铺到 clash 侧

## 填入机场节点

配置默认不含任何节点，各策略组暂时指向 `direct`，**直接使用不会走代理**。
用 sub-store 等工具按下面的正则过滤订阅节点，把节点 outbound 追加进 `outbounds`，再把它们的 tag 填进各地区 urltest 组：

| 地区组 | filter 正则 |
| --- | --- |
| `香港-智选` | `(?!.*(?i:10x))(?=.*(广港|香港|HK|Hong ?Kong|🇭🇰|HongKong)).*$` |
| `台湾-智选` | `(?!.*(?i:10x))(?=.*(广台|台湾|台灣|TW|Tai ?Wan|🇹🇼|TaiWan|Taiwan)).*$` |
| `日本-智选` | `(?!.*(?i:10x))(?=.*(广日|日本|JP|川日|东京|大阪|泉日|埼玉|沪日|深日|🇯🇵|Japan)).*$` |
| `新加坡-智选` | `(?!.*(?i:10x))(?=.*(广新|新加坡|SG|坡|狮城|🇸🇬|Singapore)).*$` |
| `韩国-智选` | `(?!.*(?i:10x))(?=.*(广韩|韩国|韓國|KR|首尔|春川|🇰🇷|Korea)).*$` |
| `美国-智选` | `(?!.*(?i:10x))(?=.*(广美|美国|US|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|拉斯|洛杉|圣何塞|圣克拉|西雅|芝加|🇺🇸|United ?States)).*$` |
| `英国-智选` | `(?!.*(?i:10x))(?=.*(英国|伦敦|UK|United ?Kingdom|🇬🇧|London)).*$` |

业务组(AIGC / GitHub / ...)已自动引用各地区组,填完节点无需再动。

## sub-store 自动拉取节点(方式 1)

sing-box **内核不支持** clash 那种 `proxy-providers` 远程节点订阅,
节点必须写死在 `outbounds`。想要“订阅 URL 自动拉节点”,正确做法是:
让 sub-store(或 SFM 客户端的订阅)以**本份 `config.json` 为模板**,
把机场订阅节点注入进 `outbounds` 的各地区 urltest 组,
输出一份**完整 sing-box 配置**托管到固定 URL,再把该 URL 给客户端定时拉取。

接线步骤:

1. 在 sub-store 输出端选 **sing-box 模板** 格式,模板 URL 指向本文件:
   `https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/singbox/config/config.json`
2. sub-store 会用机场订阅节点替换/填充 `香港-智选`…`其他` 等 urltest 组的 
`outbounds`(把 `["direct"]` 换成你节点的 tag)。
3. 把 sub-store 生成的**完整配置托管地址**(而不是本仓库这个地址)填进客户端订阅,
sub-store 定时刷新节点。

取舍:节点自动更新的同时,**分流以 sub-store 编排产出的那份为准**;
本仓库 `routes.yaml` 仍负责 `config.json` 模板本身的分流。两者各自独立。

## 导入

订阅地址:<https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/singbox/config/config.json>

一键导入(官方 SFI / SFM / SFA)。sing-box 只有自定义协议头,
GitHub 会过滤掉非 http(s) 链接,需复制到地址栏或快捷指令打开:

```
sing-box://import-remote-profile?url=https%3A%2F%2Fraw.githubusercontent.com%2FLucasss1916%2FAgentSoftware%2Fmain%2Fsingbox%2Fconfig%2Fconfig.json
#AgentSoftware
```

## 与 clash 的差异

以下规则集上游没有 sing-box `.srs` 格式，仅在 clash 侧生效：

- `TEST / Domain` → `Test`
- `Meta AI / Domain` → `AIGC`
- `Crunchyroll / Domain` → `国外媒体`
- `Proxy / Domain` → `国外媒体`
- `Globe / Domain` → `国外媒体`
- `Direct / Domain` → `DIRECT`

其中 `Block / Domain` 在 sing-box 侧改用上游通用广告表 `geosite/category-ads-all` 替代（内容与 clash 侧不同源）。
