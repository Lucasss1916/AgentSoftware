# Clash / Mihomo 配置

## 两份主配置（二选一，规则段完全一致）

| 文件 | 策略组类型 | 需要的内核 |
| --- | --- | --- |
| `urltest.yaml` | `url-test` 延时优选 | 官方 mihomo 内核即可 |
| `smart.yaml` | `smart` 智选（LightGBM 加权） | vernesong/mihomo 的 smart 内核，官方内核会报 `unsupported type: smart` |

订阅地址与一键导入：

| 文件 | 地址 / Scheme |
| --- | --- |
| `urltest.yaml` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/clash/yaml/urltest.yaml> |
| | `mihomo://install-config?url=https%3A%2F%2Fraw.githubusercontent.com%2FLucasss1916%2FAgentSoftware%2Fmain%2Fclash%2Fyaml%2Furltest.yaml&name=AgentSoftware-urltest` |
| `smart.yaml` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/clash/yaml/smart.yaml> |
| | `mihomo://install-config?url=https%3A%2F%2Fraw.githubusercontent.com%2FLucasss1916%2FAgentSoftware%2Fmain%2Fclash%2Fyaml%2Fsmart.yaml&name=AgentSoftware-smart` |

`mihomo://` 是 Clash Party（原 Mihomo Party）的 URL Scheme，ClashX 系可把协议头换成
`clash://`。GitHub 会过滤非 http(s) 链接，所以只能复制上面的整行到地址栏打开。
其余客户端（ClashMeta for Android、Stash 等）直接粘贴订阅地址即可。

## JS 覆写（扩展脚本）

已经在客户端里挂了机场订阅、只想套用本仓库的分流规则时，用覆写脚本，别用整份配置：

| 文件 | 对应配置 |
| --- | --- |
| `urltest.js` | `urltest.yaml` |
| `smart.js` | `smart.yaml` |

Clash Verge Rev / Clash Party 使用 `function main(config)` 扩展脚本；
Stash / ClashX 不支持这里的 JS 覆写。脚本只覆盖 DNS、TUN、嗅探、策略组、规则这些段落，
订阅带来的 `proxies` 与 `proxy-providers` 原样保留。

端口、`external-controller`、`secret` **故意不覆写** —— 那几项由客户端自己管，
盖掉会让客户端连不上内核。

## 维护方式

两份配置由脚本生成，**不要直接编辑 smart.yaml / urltest.yaml / *.js**：

- `common_head.yaml` — 端口、TUN、DNS、嗅探等通用头部
- `routes.yaml` — Clash 专用 rule-providers 与 rules 分流源
- `common_rules.yaml` — 由上述分流源生成，两份配置共用
- `gen.py` — 策略组定义（地区列表、filter 正则、图标）

改完任一源文件后重新生成：

```sh
python3 sync_config.py  # 在仓库根目录运行
```

## TUN 场景切换

`common_head.yaml` 中默认启用「本机接管」（`stack: mixed` + `auto-route: true`），
适合 Mac / Windows 本机直接全局代理。若作旁路由 / 网关使用，注释掉该段、
取消下方「旁路由」段的注释后重新生成。

## 其他文件

- `sample.yaml` / `clashmisample.yaml` — 旧的覆写片段，保留备查
- `Overwrite.yaml` — 旧的自动转换产物，保留备查；其生成脚本 `convert.py`
  已并入仓库根目录的 `sync_rules.py`

## 与 Egern 的对应关系

业务组沿用 Egern 名称和默认顺序：Telegram、漏网之鱼默认新加坡，苹果、微软、游戏默认直连。
GitHub / YouTube 统一走国外媒体，TalkTone 独立手选。地区组为香港、日本、台湾、新加坡、韩国、北美、其他亚洲、欧洲。
北美包含美国、加拿大、墨西哥；欧洲覆盖原来的英国组。其他亚洲和欧洲也加入业务组备选项。

- `urltest` 地区组全部使用 `url-test`；`smart` 地区组全部使用 `smart`。
- Smart 权重为 `Mitce:3.333;iku:3.333;kitty:1.667`，按**节点名**匹配；订阅应给节点名加对应机场前缀。
  Egern 的系数越小越优先，Mihomo Smart 的系数越大越优先，因此对 Egern 的 `0.3 / 0.3 / 0.6` 取倒数作为起点。
  未匹配节点的系数为 `1`；相同基础评分下，偏好为 Mitce＝iku＞kitty＞未匹配节点。
  两边评分算法不同，倒数仅保留偏好方向，不保证选出相同节点，也不代表流量占比。
- DNS 默认 Cloudflare / Google DoH；`cn` 与 ChinaDNS 规则集使用阿里 / 腾讯 DoH。
  ChinaDNS 使用 MetaCubeX 国内域名集替代 Egern 的 Repcz 规则集，覆盖范围可能略有不同。
- `*.linux.do` 使用指定 DoH；`linux.do` 本身的连接按原配置精确匹配到新加坡。
- `api64.ipify.org` 使用 Google IPv6 DNS 服务器，并非固定 hosts；这项需要设备具备可用 IPv6 出站。
  保留原配置全局 `ipv6: false`，不主动启用 IPv6 目标连接。
- Apple CDN hosts、DNS 服务域名 hosts、游戏真实 IP 域名与私网 TUN 绕行已对应迁移；TLS 校验保留默认开启。
- Mihomo 没有通用的 Egern `flatten` 对应项；通过 `include-all` 提供节点直选，地区组用节点过滤器聚合。
- Kelee 的 AI / WeChat 链接在验证时返回 403 拦截页，分别改用 MetaCubeX AI 分类集和 blackmatrix7 WeChat 集；AI 仍叠加 fmz200 规则。
- 规则顺序与 Egern 尽量一致，具体域名例外优先于通用规则集；通用规则使用对应的 Clash 格式。

完整 YAML 是模板，需要填入节点或启用 `proxy-providers`。已有订阅时可使用 JS 覆写保留节点。
分组名称变更后，客户端之前保存的手选结果不会自动迁移，请重新选择一次。

Clash 的分流源现在是本目录 `routes.yaml`；根目录 `routes.yaml` 保留给 sing-box，
本阶段不改变 sing-box 分流。`sync_config.py --from-clash` 只回写 Clash 源，
`--from-singbox` 只回写根目录源，`--check` 校验各自产物。
