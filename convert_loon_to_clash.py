import os
from pathlib import Path

def convert_loon_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None

    TYPE_MAP = {
        'DOMAIN-SUFFIX': ('DOMAIN-SUFFIX', 2),
        'DOMAIN': ('DOMAIN', 2),
        'IP-CIDR': ('IP-CIDR', 2),
        'USER-AGENT': ('USER-AGENT', 2),
        'URL-REGEX': ('URL-REGEX', 2),
        'PROCESS-NAME': ('PROCESS-NAME', 2)
    }

    parts = [p.strip() for p in line.split(',')]
    if len(parts) < 2 or parts[0] not in TYPE_MAP:
        return None

    clash_type, min_params = TYPE_MAP.get(parts[0], (None, 0))
    if len(parts) < min_params:
        return None

    rule = f"{clash_type},{parts[1]}"
    if len(parts) > 2:
        rule += f",{','.join(parts[2:])}"
    return rule

def process_loon_dir(input_dir_path, output_dir_path):
    input_dir = Path(input_dir_path)
    output_dir = Path(output_dir_path)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.list'):
                input_path = Path(root) / file
                # 计算相对路径，保持目录层级
                relative_path = input_path.relative_to(input_dir)
                # 构造输出子目录路径
                output_subdir = output_dir / relative_path.parent
                # 创建目录
                output_subdir.mkdir(parents=True, exist_ok=True)
                # 构造输出文件路径（替换后缀为.yaml）
                output_path = output_subdir / f"{relative_path.stem}.yaml"

                valid_rules = []
                with open(input_path, 'r', encoding='utf-8') as f_in:
                    for line in f_in:
                        rule = convert_loon_line(line)
                        if rule:
                            valid_rules.append(rule)
                
                with open(output_path, 'w', encoding='utf-8') as f_out:
                    f_out.write("payload:\n")
                    for r in valid_rules:
                        f_out.write(f"  - {r}\n")

                print(f"Converted {input_path} → {output_path}")

if __name__ == "__main__":
    process_loon_dir('sources/loon-rules', 'sources/clash-rules')
