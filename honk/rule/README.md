# honk 规则集

| 文件 | 原始地址 |
| --- | --- |
| `AD.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/AD.dae> |
| `Apisub.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/Apisub.dae> |
| `AppleAPIRules.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/AppleAPIRules.dae> |
| `AppleCDNRules.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/AppleCDNRules.dae> |
| `AppleNoChinaCDNRules.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/AppleNoChinaCDNRules.dae> |
| `AppleRules.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/AppleRules.dae> |
| `DirectDomain.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/DirectDomain.dae> |
| `HKProxyDomain.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/HKProxyDomain.dae> |
| `MyAiport.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/MyAiport.dae> |
| `NeedHighQualityNodeDomain.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/NeedHighQualityNodeDomain.dae> |
| `ProxyDomain.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/ProxyDomain.dae> |
| `Saily.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/Saily.dae> |
| `SailyAds.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/SailyAds.dae> |
| `TalktoneAds.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/TalktoneAds.dae> |
| `TalktoneDirect.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/TalktoneDirect.dae> |
| `TalktoneProxy.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/TalktoneProxy.dae> |
| `myvideorule.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/myvideorule.dae> |
| `prevent_dns.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/prevent_dns.dae> |
| `steamCDN.dae` | <https://raw.githubusercontent.com/Lucasss1916/AgentSoftware/main/honk/rule/steamCDN.dae> |

> honk 不支持远程规则集（只认 `geosite:`/`geoip:` 的 dat 文件加内联 `domain()`），所以这些是预编译好的 dae `routing` 片段，出口已写在文件里，由 [`honk/config.dae`](../README.md) 的 `include` 块按顺序引入 —— 顺序即优先级，默认只引入 Clash 侧实际在用的 8 个。出口对应关系见 `sync_rules.py` 的 `HONK_OUTBOUND` 表。

<sub>本文件由 `gen_readme.py` 生成，勿直接编辑。</sub>
