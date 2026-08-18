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

## Clash 主配置

见 [`clash/yaml/README.md`](clash/yaml/README.md)。两份配置（`smart.yaml` / `urltest.yaml`）
由 `clash/yaml/gen.py` 配合 `common_head.yaml`、`common_rules.yaml` 生成。

## 目录

| 目录 | 内容 |
| --- | --- |
| `loon/` | 规则源、插件 |
| `clash/` | 规则、主配置与生成脚本 |
| `quanx/` | 规则、重写、任务脚本 |
| `Egern/` | 规则、模块 |
| `singbox/` | 规则、配置 |
| `Surge/` | 规则、配置、模块、BoxJS |
