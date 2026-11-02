# AgentSoftware

[![GitHub Pulse](https://github-pulse-git-main-lucasss1916s-projects.vercel.app/r/Lucasss1916/AgentSoftware?theme=phosphor)](https://github-pulse-git-main-lucasss1916s-projects.vercel.app)

各代理客户端的规则与配置集合。

## 规则同步

`loon/rule/*.list` 是**唯一的规则源**，其余规则目录全部由 `sync_rules.py` 生成。

```
loon/rule/*.list  ──sync_rules.py──┬──►  clash/rule/*.yaml      Clash / mihomo
                                   ├──►  quanx/rule/*.list      Quantumult X
                                   ├──►  Egern/rule/*.yaml      Egern
                                   ├──►  singbox/rule/*.json    sing-box
                                   ├──►  Surge/rule/*.list      Surge
                                   ├──►  anywhere/rule/*.arrs  Anywhere
                                   └──►  honk/rule/*.dae        honk（dae 语法）
```

**修改规则时只改 `loon/rule/` 下的文件**，然后：

```sh
python3 sync_rules.py          # 生成全部格式
python3 gen_readme.py          # 新增或删除规则集后更新订阅目录
python3 sync_rules.py --check  # 只校验不写入（CI 用）
```

GitHub Actions 在 main 推送和 PR 中都只做校验，不会回填提交；
若产物与源不一致会直接失败，需要在本地生成后一并提交。

新增规则类型时，只需在 `sync_rules.py` 的 `TYPES` 表里加一行，七种格式同时生效。

### 格式能力差异

部分规则类型在某些客户端没有对应字段，同步时会被跳过并在输出中统计：

| 类型 | Clash | QX | Egern | sing-box | Surge | Anywhere | honk |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| DOMAIN | ✓ | ✓ | ✓ | ✓ | ✓ | 转为后缀匹配 | ✓ |
| DOMAIN-SUFFIX / DOMAIN-KEYWORD | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| DOMAIN-REGEX | ✓ | — | ✓ | ✓ | — | — | ✓ |
| IP-CIDR / IP-CIDR6 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| GEOIP | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| ASN | ✓ | — | ✓ | — | ✓ | — | — |
| PROCESS-NAME | ✓ | — | — | ✓ | ✓ | — | ✓ |
| USER-AGENT | ✓ | ✓ | — | — | ✓ | — | — |
| URL-REGEX | — | ✓ | ✓ | — | ✓ | — | — |

目前 Apple 三件套里的 22 条 USER-AGENT 规则在 Egern、sing-box、Anywhere 与 honk 中会被跳过，属预期行为。

honk 的规则文件比其余六家多带一样东西：**出口**。dae 语法的一条 `routing` 规则就是
「匹配 + 出口」，没有「规则集」这层可以让策略留在客户端配置里，所以 `honk/rule/*.dae`
里的出口由 `sync_rules.py` 的 `HONK_OUTBOUND` 表决定，对应 Clash 侧 `routes.yaml` 的策略组。

### 不参与同步的文件

`GFWRules`（5546 条）体量较大且仅 QX / Egern 使用，未纳入统一源，
由 `sync_rules.py` 的 `KEEP` 列表保护，不会被清理。

### Anywhere 规则订阅

订阅地址与导入 Scheme 见 [`anywhere/rule/README.md`](anywhere/rule/README.md)。
每个 Loon 源文件生成一个同名 `.arrs` 规则集，可按需分别订阅。

1. 在 Anywhere 的「分流 / Routing」页面添加订阅，粘贴对应文件的原始地址；
   也可复制目录说明中的 `anywhere://add-rule-set?link=...` 到地址栏或快捷指令打开。
2. 使用规则模式，并为每个规则集指定 DIRECT、REJECT、PROXY 或具体节点 / 链。
   文件不预设策略，首次导入为 Default，默认名称取自文件名。
3. 后续只修改 `loon/rule/*.list`，运行上述生成命令并推送到 main，
   再在 Anywhere 中刷新订阅。刷新只更新规则内容，保留 App 内设置的名称与策略。

Anywhere 的格式和匹配方式有以下差异：

- `DOMAIN,api.example.com` 转成 `2,api.example.com`，会同时匹配该域名及其子域名，
  **不是精确域名匹配**。生成文件会注明转换条数。
- `DOMAIN-SUFFIX`、`DOMAIN-KEYWORD`、`IP-CIDR`、`IP-CIDR6` 分别使用类型 ID `2`、`3`、`0`、`1`。
  上表中不支持的类型会跳过，并计入同步输出与文件头注释。
- `.arrs` 不支持逐条 `no-resolve`，转换时会移除该修饰符，保留 IP 规则本身。
  Anywhere 的 DNS 设置是全局行为，无法等价保留源规则的逐条解析限制。
- 策略按规则集设置，匹配先比较来源层级，再比较具体程度，不能照搬 Loon 的逐行优先顺序。
  显式指定策略的内置 ADBlock / 服务规则优先于自定义规则；Default 与显式 PROXY 的优先级也不同。

格式依据：[Anywhere 官方分流文档](https://github.com/NodePassProject/Anywhere/blob/main/Documentations/Routing.md)
与[规则解析器](https://github.com/NodePassProject/Anywhere/blob/main/Anywhere/Views/Pages/Routing/RoutingRuleParser.swift)。

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

## 一键导入

各客户端目录的 `README.md` 里列出了本目录每个文件的原始地址与对应的一键导入链接，
由 `gen_readme.py` 生成（`--check` 供 CI 校验）：

| 客户端 | 目录 |
| --- | --- |
| Loon | [规则](loon/rule/README.md) · [插件](loon/plugin/README.md) |
| Quantumult X | [规则](quanx/rule/README.md) · [重写](quanx/rewrite/README.md) · [任务](quanx/task/README.md) |
| Egern | [规则](Egern/rule/README.md) · [模块](Egern/module/README.md) |
| Surge | [配置](Surge/config/README.md) · [模块](Surge/module/README.md) · [规则](Surge/rule/README.md) · [BoxJS](Surge/boxjs/README.md) |
| Clash / mihomo | [主配置](clash/yaml/README.md) · [规则](clash/rule/README.md) |
| sing-box | [主配置](singbox/config/README.md) · [规则](singbox/rule/README.md) |
| Anywhere | [规则订阅](anywhere/rule/README.md) · [模块与 MITM](anywhere/module/README.md) |
| honk | [主配置](honk/README.md) · [规则集](honk/rule/README.md) |

### 跳转页

只有 Loon、Quantumult X、Egern 有 Universal Link。Surge、Clash、sing-box、Anywhere
只有自定义协议头（`surge:///`、`mihomo://`、`sing-box://`、`anywhere://`），会被 GitHub 的
markdown 过滤掉，没法直接做成可点的链接，于是加了一层自己的跳转页：

```
docs/import.html?s=<整条 scheme 经 encodeURIComponent>
```

页面校验协议头在白名单内后 `location.replace` 过去。表格里的「导入」指向
<https://lucasss1916.github.io/AgentSoftware/import.html>，原始 scheme 仍在表格下方
以代码块给出，不想经过跳转页就复制那一条。

> 跳转页需在仓库 **Settings → Pages** 里把 Source 设为 `main` 分支的 `/docs` 目录才会生效，
> 否则「导入」链接会 404。改动 `docs/import.html` 的协议白名单后记得同步
> `gen_readme.py` 里新增的 scheme，`tests/` 有一条用例在卡这个一致性。

### 导入粒度

各家能导入的粒度不同，这不是本仓库的取舍，而是客户端 Scheme 的能力边界：

| 客户端 | 可一键导入 | 只能手工接入 |
| --- | --- | --- |
| Loon | 规则集、插件 | — |
| Quantumult X | 分流规则 | 重写 / 任务脚本（需在 `[rewrite_local]`、`[task_local]` 里引用） |
| Egern | 规则集、模块 | — |
| Surge | 配置、模块 | 规则集（手写 `RULE-SET`）、BoxJS 订阅 |
| Clash / mihomo | 主配置 | 规则集（手写 `rule-providers`） |
| sing-box | 主配置 | 规则集（手写 `route.rule_set`） |
| Anywhere | 分流规则集、模块、MITM 规则集 | — |
| honk | — | 全部（Linux 守护进程，`-c` 读本地文件，无 URL Scheme） |

Surge / Clash / sing-box 的规则集没有对应的 Scheme（[Surge 官方只有 `install-config`
与 `install-module`](https://manual.nssurge.com/tools/url-scheme.html)），但本仓库的
Clash 主配置已把 `clash/rule/` 全部引用好，导入主配置即可；Surge 侧仍需手写一行。

## 目录

| 目录 | 内容 |
| --- | --- |
| `loon/` | 规则源、插件 |
| `clash/` | 规则、主配置与生成脚本 |
| `quanx/` | 规则、重写、任务脚本 |
| `Egern/` | 规则、模块 |
| `singbox/` | 规则、配置 |
| `Surge/` | 规则、配置、模块、BoxJS |
| `anywhere/` | Anywhere `.arrs` 分流规则订阅 |
| `honk/` | honk 主配置与 dae 语法规则集 |
