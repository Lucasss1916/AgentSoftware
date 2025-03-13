import yaml
from pathlib import Path

VALID_TYPES = {
    'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD',
    'IP-CIDR', 'IP-CIDR6', 'GEOIP', 
    'SRC-IP-CIDR', 'SRC-PORT', 'DST-PORT',
    'PROCESS-NAME', 'URL-REGEX', 'USER-AGENT'
}

def validate_clash_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 基础YAML格式验证
        try:
            rules = yaml.safe_load(content)
        except yaml.YAMLError as e:
            return False, f"Invalid YAML syntax: {str(e)}"

        # 结构验证（示例验证逻辑）
        if not isinstance(rules, list):
            return False, "Root element must be a list"
        
        error_lines = []
        for idx, rule in enumerate(rules):
            if not isinstance(rule, str):
                error_lines.append(f"Line {idx+1}: Rule must be string type")
                continue
                
            parts = rule.split(',')
            if len(parts) < 2:
                error_lines.append(f"Line {idx+1}: Rule requires at least 2 parameters")
                continue
                
            rule_type = parts[0].strip()
            if rule_type not in VALID_TYPES:
                error_lines.append(f"Line {idx+1}: Invalid rule type '{rule_type}'")
                
        return len(error_lines) == 0, '\n'.join(error_lines)
    except Exception as e:
        return False, f"Validation error: {str(e)}"

if __name__ == '__main__':
    import sys
    file_path = sys.argv[1]
    is_valid, message = validate_clash_file(file_path)
    if not is_valid:
        print(f"❌ Validation failed for {file_path}")
        print(message)
        exit(1)
    print(f"✅ {file_path} is valid")

