import yaml
from pathlib import Path

# 路径
BASE_DIR = Path("clash/yaml")
INPUT_FILE = BASE_DIR / "smart.yaml"
OUTPUT_FILE = BASE_DIR / "Overwrite.yaml"

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)

    # === 构建新的 Clash Meta 格式 ===
    new_config = {
        "experimental": {},
        "hosts": {},
        "profile": {"store-selected": True, "store-fake-ip": True},
        "ntp": {},
        "sniffer": {},
        "tun": raw_config.get("tun", {}),
        "dns": raw_config.get("dns", {}),
        "proxy-groups": raw_config.get("proxy-groups", []),
        "rule-providers": raw_config.get("rule-providers", {}),
        "rules": raw_config.get("rules", []),
    }

    # 保留端口 & 基础设置
    base_keys = [
        "port", "socks-port", "redir-port", "mixed-port", "tproxy-port",
        "allow-lan", "mode", "log-level", "external-controller", "secret"
    ]
    for key in base_keys:
        if key in raw_config:
            new_config[key] = raw_config[key]

    # 输出新文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(new_config, f, sort_keys=False, allow_unicode=True)

    print(f"✅ 已转换并保存到 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
