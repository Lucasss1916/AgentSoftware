function main(config) {
    config["proxy-groups"] = [
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Static.png",
            "include-all": true,
            name: "PROXY",
            type: "select",
            proxies: ["AUTO", "HK", "SG", "JP","KR", "US","TW","EU","AU"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Urltest.png",
            "include-all": true,
            name: "AUTO",
            type: "url-test",
            interval: 300,
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/OpenAI.png",
            name: "AIGC",
            type: "select",
            proxies: ["HK","SG", "JP","KR", "US","TW","EU","AU"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/steam.png",
            name: "Steam",  
            type: "select",
            proxies: ["DIRECT","HK","SG", "JP", "US","TW","EU","AU","KR"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/github.png",
            name: "Github",  
            type: "select",
            proxies: ["DIRECT","HK","SG", "JP", "US","TW","EU","AU","KR"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Spotify.png",
            name: "Spotify",
            type: "select",
            proxies: ["HK","SG", "JP", "US","TW","EU","AU","KR"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Telegram.png",
            name: "Telegram",
            type: "select",
            proxies: ["HK", "SG", "JP", "US","TW","EU","AU","KR"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Google.png",
            name: "Google",
            type: "select",
            proxies: ["HK", "SG", "JP", "US","TW","EU","AU","KR"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Microsoft.png",
            name: "Microsoft",  
            type: "select",
            proxies: ["DIRECT","HK", "SG", "JP", "US","TW","EU","AU"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/Apple.png",
            name: "Apple",    
            type: "select",
            proxies: ["DIRECT","HK", "SG", "JP", "US","TW","EU","AU"],
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/HK.png",
            "include-all": true,
            filter: "(?i)香港|Hong Kong|HK|🇭🇰",
            name: "HK",
            type: "url-test",
            interval: 300,
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/SG.png",
            "include-all": true,
            filter: "(?i)新加坡|Singapore|sg|🇸🇬",
            name: "SG",
            type: "url-test",
            interval: 300,
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/JP.png",
            "include-all": true,
            filter: "(?i)日本|Japan|jp|🇯🇵",
            name: "JP",
            type: "url-test",
            interval: 300,
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/TW.png",
            "include-all": true,
            filter: "(?i)台湾|Taiwan|taiwan|tw|tw",
            name: "TW",
            type: "url-test",
            interval: 300,
        },
        {
            icon: "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/flags/kr.svg",
            "include-all": true,
            filter: "(?i)韩国|Korea|KR|kr|kr",
            name: "KR",
            type: "url-test",
            interval: 300,
        },
        {
            icon: "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/flags/eu.svg",
            "include-all": true,

            filter: "(?i)法国|德国|英国",
            name: "EU",
            type: "url-test",
            interval: 300,
        },
        {
            icon: "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/flags/au.svg",
            "include-all": true,

            filter: "(?i)澳大利亚|Australia",
            name: "AU",
            type: "url-test",
            interval: 300,
        },
        {
            icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/US.png",
            "include-all": true,

            filter: "(?i)美国|USA|us-|🇺🇸",
            name: "US",
            type: "url-test",
            interval: 300,
        },
    ];
    if (!config['rule-providers']) {
        config['rule-providers'] = {};
    }
    config["rule-providers"] = Object.assign(config["rule-providers"], {
        CNKI: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/CNKI/CNKI.yaml",
            path: "./ruleset/CNKI.yaml",
            behavior: "domain",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        
        private: {
            url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/private.yaml",
            path: "./ruleset/private.yaml",
            behavior: "domain",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        cn_domain: {
            url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.yaml",
            path: "./ruleset/cn_domain.yaml",
            behavior: "domain",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        github: {
            url: "https://raw.githubusercontent.com/Lucasss1916/clash/refs/heads/main/rule/github.yaml",
            path: "./ruleset/github.yaml",
            behavior: "domain",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        microsoft: {  
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Microsoft/Microsoft.yaml",
            path: "./ruleset/microsoft.yaml",
            behavior: "domain",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        telegram_domain: {
            url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/telegram.yaml",
            path: "./ruleset/telegram_domain.yaml",
            behavior: "domain",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        google_domain: {
            url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/google.yaml",
            path: "./ruleset/google_domain.yaml",
            behavior: "domain",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        "geolocation-!cn": {
            url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/geolocation-!cn.yaml",
            path: "./ruleset/geolocation-!cn.yaml",
            behavior: "domain",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        cn_ip: {
            url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/cn.yaml",
            path: "./ruleset/cn_ip.yaml",
            behavior: "ipcidr",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        telegram_ip: {
            url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/telegram.yaml",
            path: "./ruleset/telegram_ip.yaml",
            behavior: "ipcidr",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        google_ip: {
            url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/google.yaml",
            path: "./ruleset/google_ip.yaml",
            behavior: "ipcidr",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        bing: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Bing/Bing.yaml",
            path: "./ruleset/bing.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        copilot: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Copilot/Copilot.yaml",
            path: "./ruleset/copilot.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        claude: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Claude/Claude.yaml",
            path: "./ruleset/claude.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        bard: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/BardAI/BardAI.yaml",
            path: "./ruleset/bard.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        openai: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/OpenAI/OpenAI.yaml",
            path: "./ruleset/openai.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        steam: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Steam/Steam.yaml",
            path: "./ruleset/steam.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        steamcn: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/SteamCN/SteamCN.yaml",
            path: "./ruleset/steamcn.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        spotify: {
            url: "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Spotify/Spotify.yaml",
            path: "./ruleset/Spotify.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        AppleRules: {
            url: "https://github.com/Lucasss1916/clash/raw/refs/heads/main/rule/AppleRules.yaml",
            path: "./ruleset/AppleRules.yaml",
            behavior: "classical",   
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        AppleAPIRules: {
            url: "https://github.com/Lucasss1916/clash/raw/refs/heads/main/rule/AppleAPIRules.yaml",
            path: "./ruleset/AppleAPIRules.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        AppleNoChinaCDNRules: {
            url: "https://github.com/Lucasss1916/clash/raw/refs/heads/main/rule/AppleNoChinaCDNRules.yaml",
            path: "./ruleset/AppleNoChinaCDNRules.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
        AppleCDNRules: {
            url: "https://github.com/Lucasss1916/clash/raw/refs/heads/main/rule/AppleCDNRules.yaml",
            path: "./ruleset/AppleCDNRules.yaml",
            behavior: "classical",
            interval: 86400,
            format: "yaml",
            type: "http",
        },
    });

    config["rules"] = [
        "RULE-SET,CNKI,DIRECT",
        "RULE-SET,microsoft,Microsoft",  
        "RULE-SET,github,Github",   
        "RULE-SET,spotify,Spotify",
        "RULE-SET,private,DIRECT",
        "RULE-SET,bing,Microsoft",
        "RULE-SET,copilot,AIGC",
        "RULE-SET,bard,AIGC",  
        "RULE-SET,openai,AIGC",
        "RULE-SET,claude,AIGC",
        "RULE-SET,steam,Steam",
        "RULE-SET,steamcn,DIRECT",
        
        "RULE-SET,AppleNoChinaCDNRules,PROXY",
        "RULE-SET,AppleRules,Apple",
        "RULE-SET,AppleAPIRules,Apple",
        "RULE-SET,AppleCDNRules,Apple",

        "RULE-SET,telegram_domain,Telegram",
        "RULE-SET,telegram_ip,Telegram",
        "RULE-SET,google_domain,Google",
        "RULE-SET,google_ip,Google",
        "RULE-SET,geolocation-!cn,PROXY",
        "RULE-SET,cn_domain,DIRECT",
        "RULE-SET,cn_ip,DIRECT",
        "MATCH,PROXY",
    ];

    return config;
}
