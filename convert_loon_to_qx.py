import argparse
from pathlib import Path

# Loon → Quantumult X 映射
LOON_TO_QX_MAP = {
    "DOMAIN": "HOST",
    "DOMAIN-SUFFIX": "HOST-SUFFIX",
    "DOMAIN_KEYWORD": "HOST-KEYWORD",
    "USER-AGENT": "USER-AGENT",
    "IP-CIDR": "IP-CIDR",
    "IP-CIDR6": "IP6-CIDR",
    "GEOIP": "GEOIP",
}

def convert_line_to_qx(line: str):
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 2:
        return None

    loon_type = parts[0]
    value = parts[1]

    qx_type = LOON_TO_QX_MAP.get(loon_type)
    if not qx_type:
        return None

    return f"{qx_type},{value}"

def process_dir(input_dir_path, output_dir_path):
    input_dir = Path(input_dir_path)
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in input_dir.glob("*.list"):
        qx_rules = []

        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                rule = convert_line_to_qx(line)
                if rule:
                    qx_rules.append(rule)

        output_file = output_dir / f"{file.stem}.list"
        with open(output_file, "w", encoding="utf-8") as out:
            out.write("\n".join(qx_rules))

        print(f"✅ {file.name} → {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Loon .list rules to Quantumult X format")
    parser.add_argument("--input", required=True, help="Path to Loon .list files")
    parser.add_argument("--output", required=True, help="Path to output QX rules")
    args = parser.parse_args()

    process_dir(args.input, args.output)
