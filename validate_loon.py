from pathlib import Path

VALID_TYPES = {
    'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD',
    'IP-CIDR', 'IP-CIDR6', 'GEOIP',
    'USER-AGENT', 'URL-REGEX', 'PROCESS-NAME'
}

def validate_loon_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        error_lines = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split(',')
            if len(parts) < 2:
                error_lines.append(f"Line {line_num}: Requires at least 2 parameters")
                continue
                
            rule_type = parts[0].strip()
            if rule_type not in VALID_TYPES:
                error_lines.append(f"Line {line_num}: Invalid rule type '{rule_type}'")
                
            # 策略验证（可选）
            if len(parts) >=3:
                policy = parts[2].strip()
                if not policy.isupper():
                    error_lines.append(f"Line {line_num}: Policy '{policy}' should be uppercase")
                    
        return len(error_lines) == 0, '\n'.join(error_lines)
    except Exception as e:
        return False, f"Validation error: {str(e)}"

if __name__ == '__main__':
    import sys
    file_path = sys.argv[1]
    is_valid, message = validate_loon_file(file_path)
    if not is_valid:
        print(f"❌ Validation failed for {file_path}")
        print(message)
        exit(1)
    print(f"✅ {file_path} is valid")

