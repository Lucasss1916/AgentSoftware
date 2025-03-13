import os
import re
from pathlib import Path

def convert_clash_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return line

    TYPE_MAP = {
        'DOMAIN-SUFFIX': ('DOMAIN-SUFFIX', 2),
        'DOMAIN': ('DOMAIN', 2),
        'IP-CIDR': ('IP-CIDR', 2),
        'USER-AGENT': ('USER-AGENT', 2),
        'URL-REGEX': ('URL-REGEX', 2),
        'PROCESS-NAME': ('PROCESS-NAME', 2)
    }

    parts = [p.strip() for p in line.split(',')]
    if len(parts) < 2:
        return f"# INVALID RULE: {line}"

    clash_type = parts[0]
    if clash_type not in TYPE_MAP:
        return f"# UNSUPPORTED TYPE: {line}"

    loon_type, min_params = TYPE_MAP[clash_type]
    if len(parts) < min_params:
        return f"# INCOMPLETE RULE: {line}"

    # 转换策略参数（示例策略映射）
    policy = None
    if len(parts) >= 3:
        policy_map = {
            'DIRECT': 'DIRECT',
            'PROXY': 'Proxy',
            'REJECT': 'REJECT'
        }
        policy = policy_map.get(parts[2], parts[2])

    # 构建Loon规则
    loon_rule = f"{loon_type},{parts[1]}"
    if policy:
        loon_rule += f",{policy}"
        if len(parts) > 3:
            loon_rule += f",{','.join(parts[3:])}"
    
    return loon_rule

def process_clash_dir(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.yaml'):
                input_path = Path(root) / file
                relative_path = input_path.relative_to(input_dir)
                output_path = output_dir / relative_path.with_suffix('.list')
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(input_path, 'r', encoding='utf-8') as f_in:
                    with open(output_path, 'w', encoding='utf-8') as f_out:
                        for line in f_in:
                            converted = convert_clash_line(line)
                            f_out.write(converted + '\n')
                print(f"Converted {input_path} ➔ {output_path}")

if __name__ == '__main__':
    process_clash_dir('sources/clash-rules', 'sources/loon-rules')

