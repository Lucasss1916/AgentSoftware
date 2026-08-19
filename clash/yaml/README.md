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

## 维护方式

两份配置由脚本生成，**不要直接编辑 smart.yaml / urltest.yaml**：

- `common_head.yaml` — 端口、TUN、DNS、嗅探等通用头部
- `common_rules.yaml` — rule-providers 与 rules（两份共用，保证分流行为一致）
- `gen.py` — 策略组定义（地区列表、filter 正则、图标）

改完任一源文件后重新生成：

```sh
cd clash/yaml && python3 gen.py
```

## TUN 场景切换

`common_head.yaml` 中默认启用「本机接管」（`stack: mixed` + `auto-route: true`），
适合 Mac / Windows 本机直接全局代理。若作旁路由 / 网关使用，注释掉该段、
取消下方「旁路由」段的注释后重新生成。

## 其他文件

- `sample.yaml` / `clashmisample.yaml` — 旧的覆写片段，保留备查
- `Overwrite.yaml` — 旧的自动转换产物，保留备查；其生成脚本 `convert.py`
  已并入仓库根目录的 `sync_rules.py`
