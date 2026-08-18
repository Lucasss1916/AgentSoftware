# AgentSoftware

各代理客户端的规则与配置集合。

## 规则同步

`loon/rule/*.list` 是**唯一的规则源**，其余规则目录全部由 `sync_rules.py` 生成。

```
loon/rule/*.list  ──sync_rules.py──┬──►  clash/rule/*.yaml      Clash / mihomo
                                   ├──►  quanx/rule/*.list      Quantumult X
                                   ├──►  Egern/rule/*.yaml      Egern
                                   ├──►  singbox/rule/*.json    sing-box
                                   └──►  Surge/rule/*.list      Surge
```

**修改规则时只改 `loon/rule/` 下的文件**，然后：

```sh
python3 sync_rules.py          # 生成全部格式
python3 sync_rules.py --check  # 只校验不写入（CI 用）
```

推送到 main 后 GitHub Actions 会自动同步并回填提交；PR 则只做校验，
若产物与源不一致会直接失败。

新增规则类型时，只需在 `sync_rules.py` 的 `TYPES` 表里加一行，五种格式同时生效。

### 格式能力差异

部分规则类型在某些客户端没有对应字段，同步时会被跳过并在输出中统计：

| 类型 | Clash | QX | Egern | sing-box | Surge |
| --- | :-: | :-: | :-: | :-: | :-: |
| DOMAIN / -SUFFIX / -KEYWORD | ✓ | ✓ | ✓ | ✓ | ✓ |
| DOMAIN-REGEX | ✓ | — | ✓ | ✓ | — |
| IP-CIDR / IP-CIDR6 | ✓ | ✓ | ✓ | ✓ | ✓ |
| GEOIP | ✓ | ✓ | ✓ | — | ✓ |
| ASN | ✓ | — | ✓ | — | ✓ |
| PROCESS-NAME | ✓ | — | — | ✓ | ✓ |
| USER-AGENT | ✓ | ✓ | — | — | ✓ |
| URL-REGEX | — | ✓ | ✓ | — | ✓ |

目前 Apple 三件套里的 22 条 USER-AGENT 规则在 Egern 与 sing-box 中会被跳过，属预期行为。

### 不参与同步的文件

`GFWRules`（5546 条）体量较大且仅 QX / Egern 使用，未纳入统一源，
由 `sync_rules.py` 的 `KEEP` 列表保护，不会被清理。

## 主配置同步（Clash ↔ sing-box）

规则**内容**由 `sync_rules.py` 同步；分流**顺序与策略**则由 `routes.yaml`
这一份源同时铺到 Clash 与 sing-box：

```
                    ┌──►  clash/yaml/common_rules.yaml ──gen.py──┬──► smart.yaml
   routes.yaml ─────┤                                            └──► urltest.yaml
   （唯一源）        └──►  singbox/config/config.json
```

```sh
python3 sync_config.py                 # 正向：routes.yaml → 两侧
python3 sync_config.py --check         # 只校验（CI 用）
python3 sync_config.py --from-clash    # 反向：clash 侧改动 → routes.yaml
python3 sync_config.py --from-singbox  # 反向：sing-box 侧改动 → routes.yaml
```

两个方向都是无损的：反向同步用 difflib 只应用真正的增删，未改动的行原样保留，
因此 `no-resolve` 修饰符、以及 sing-box 侧不存在的规则集都不会被抹掉。
惯常用法仍是直接改 `routes.yaml`；`--from-*` 是给「已经手改了某一侧」时收尾用的。

### 两侧的差异

sing-box 用 `.srs` 规则集，与 Clash 的 `.mrs` 并非一一对应。以下 6 个规则集
上游没有 sing-box 格式，**仅在 Clash 侧生效**（`routes.yaml` 中标记为 `singbox: null`）：

`TEST / Domain`、`Meta AI / Domain`、`Crunchyroll / Domain`、
`Proxy / Domain`、`Globe / Domain`、`Direct / Domain`

`Block / Domain` 在 sing-box 侧改用上游通用广告表 `geosite/category-ads-all` 替代
（与 Clash 侧不同源，但保证 sing-box 不会完全失去广告拦截）。

Clash 两份配置的说明见 [`clash/yaml/README.md`](clash/yaml/README.md)，
sing-box 配置的节点填法见 [`singbox/config/README.md`](singbox/config/README.md)。

> sing-box 配置**不含任何机场节点**，各策略组默认指向 `direct`，需按
> `singbox/config/README.md` 的正则过滤订阅并填入后才会真正走代理。

## 目录

| 目录 | 内容 |
| --- | --- |
| `loon/` | 规则源、插件 |
| `clash/` | 规则、主配置与生成脚本 |
| `quanx/` | 规则、重写、任务脚本 |
| `Egern/` | 规则、模块 |
| `singbox/` | 规则、配置 |
| `Surge/` | 规则、配置、模块、BoxJS |
