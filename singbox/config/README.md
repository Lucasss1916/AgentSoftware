# sing-box 配置

本目录的 `config.json` **由 `sync_config.py` 生成，请勿手改**。

- 改分流：编辑仓库根目录 `routes.yaml`，再跑 `python3 sync_config.py`
- 已经手改了 `config.json`：跑 `python3 sync_config.py --from-singbox` 回写，再跑一次正向同步铺到 clash 侧

## 填入机场节点

配置默认不含任何节点，各策略组暂时指向 `direct`，**直接使用不会走代理**。
用 sub-store 等工具按下面的正则过滤订阅节点，把节点 outbound 追加进 `outbounds`，再把它们的 tag 填进各地区 urltest 组：

| 地区组 | filter 正则 |
| --- | --- |
| `香港-智选` | `(?=.*(广港|香港|HK|Hong ?Kong|🇭🇰|HongKong)).*$` |
| `台湾-智选` | `(?=.*(广台|台湾|台灣|TW|Tai ?Wan|🇹🇼|TaiWan|Taiwan)).*$` |
| `日本-智选` | `(?=.*(广日|日本|JP|川日|东京|大阪|泉日|埼玉|沪日|深日|🇯🇵|Japan)).*$` |
| `新加坡-智选` | `(?=.*(广新|新加坡|SG|坡|狮城|🇸🇬|Singapore)).*$` |
| `韩国-智选` | `(?=.*(广韩|韩国|韓國|KR|首尔|春川|🇰🇷|Korea)).*$` |
| `美国-智选` | `(?=.*(广美|美国|US|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|拉斯|洛杉|圣何塞|圣克拉|西雅|芝加|🇺🇸|United ?States)).*$` |
| `英国-智选` | `(?=.*(英国|伦敦|UK|United ?Kingdom|🇬🇧|London)).*$` |

业务组（AIGC / GitHub / …）已自动引用各地区组，填完节点无需再动。

## 与 clash 的差异

以下规则集上游没有 sing-box `.srs` 格式，仅在 clash 侧生效：

- `TEST / Domain` → `Test`
- `Meta AI / Domain` → `AIGC`
- `Crunchyroll / Domain` → `国外媒体`
- `Proxy / Domain` → `国外媒体`
- `Globe / Domain` → `国外媒体`
- `Direct / Domain` → `DIRECT`

其中 `Block / Domain` 在 sing-box 侧改用上游通用广告表 `geosite/category-ads-all` 替代（内容与 clash 侧不同源）。
