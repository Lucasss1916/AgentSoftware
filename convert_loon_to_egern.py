import os
from pathlib import Path
import yaml
from collections import defaultdict

# 映射 Loon 类型到 egern 类型
LOON_TO_EGERN_MAP = {
    "DOMAIN": "domain_set",
    "DOMAIN-SUFFIX": "domain_suffix_set",
    "DOMAIN_KEYWORD": "domain_keyword_set",
    "DOMAIN-REGEX": "domain_regex_set",
    "IP-CIDR": "ip_cidr_set",
    "IP-CIDR6": "ip_cidr6_set",
    "URL-REGEX": "url_regex_set",
    "GEOIP": "geoip_set",
    "ASN": "asn_set"
}

def convert_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None

    parts = [p.strip() for p in line.split(',')]
    if len(parts) < 2:
        return None, None

    loon_type = parts[0]
    value = parts[1]
    egern_type = LOON_TO_EGERN_MAP.get(loon_type)
    if not egern_type:
        return None, None

    return egern_type, value

def process_dir(input_dir_path, output_dir_path):
    input_dir = Path(input_dir_path)
    output_base = Path(output_dir_path)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.list'):
                input_path = Path(root) / file
                entries = defaultdict(set)

                with open(input_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        egern_type, value = convert_line(line)
                        if egern_type and value:
                            entries[egern_type].add(value)

                for egern_type, values in entries.items():
                    # 输出到对应的子目录中，如 domain_set/adult.yaml
                    subdir = output_base / egern_type
                    subdir.mkdir(parents=True, exist_ok=True)
                    output_file = subdir / f"{input_path.stem}.yaml"

                    with open(output_file, 'w', encoding='utf-8') as out:
                        yaml.dump(
                            {egern_type: sorted(values)},
                            out,
                            allow_unicode=True,
                            sort_keys=False
                        )

                    print(f"✅ {input_path} → {output_file}")

if __name__ == "__main__":
    process_dir("loon/rule", "Egern/rule")
