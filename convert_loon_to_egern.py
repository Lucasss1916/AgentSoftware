import os
import yaml
import argparse
from pathlib import Path
from collections import defaultdict

# 映射 loon 规则类型到 egern 字段名
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
    return egern_type, value if egern_type else (None, None)

def process_dir(input_dir_path, output_dir_path):
    input_dir = Path(input_dir_path)
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in input_dir.glob("*.list"):
        egern_data = defaultdict(set)

        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                egern_type, value = convert_line(line)
                if egern_type and value:
                    egern_data[egern_type].add(value)

        output_file = output_dir / f"{file.stem}.yaml"
        with open(output_file, "w", encoding="utf-8") as out:
            merged_dict = {k: sorted(v) for k, v in egern_data.items()}
            yaml.dump(merged_dict, out, allow_unicode=True, sort_keys=False)
        print(f"✅ {file.name} → {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to loon .list files")
    parser.add_argument("--output", required=True, help="Path to output egern rules")
    args = parser.parse_args()

    process_dir(args.input, Path(args.output))
