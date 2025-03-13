import os
import re
from pathlib import Path

def convert_loon_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None  # 忽略注释和空行

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
        return None  # 无效规则：参数不足

    loon_type = parts[0].strip()  # 处理可能出现的空格
    if loon_type not in TYPE_MAP:
        return None  # 不支持的规则类型

    clash_type, min_params = TYPE_MAP[loon_type]
    if len(parts) < min_params:
        return None  # 参数不足
    
    # 构建Clash格式规则
    rule = f"{clash_type},{parts[1]}"  
    if len(parts) > 2:
        # 保留原始策略参数（如"Don't Use Proxy"）
        rule += f",{','.join(parts[2:])}"
    return rule

def process_loon_dir(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if not file.endswith('.list'):
                continue

            input_path = Path(root) / file
            output_subdir = output_dir / root.relative_to(input_dir)
            output_subdir.mkdir(parents=True, exist_ok=True)
            output_path = output_subdir / f"{file[:-5]}.yaml"

            valid_rules = []
            with open(input_path, 'r', encoding='utf-8') as f_in:
                for line in f_in:
                    rule = convert_loon_line(line)
                    if rule:
                        valid_rules.append(rule)
            
            # ✨ 核心修改：生成标准化YAML格式
            with open(output_path, 'w', encoding='utf-8') as f_out:
                # 写入payload头部
                f_out.write("payload:\n")  
                # 写入规则列表
                for r in valid_rules:
                    f_out.write(f"  - {r}\n")
                # 确保结尾有换行符（IDE友好）
                f_out.write("\n") if not valid_rules else None

            print(f" Converted {input_path} → {output_path}")

if __name__ == "__main__":
    process_loon_dir('sources/loon-rules', 'sources/clash-rules')
