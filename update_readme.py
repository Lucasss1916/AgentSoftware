from pathlib import Path

REPO_BASE = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main"

def generate_section(dir_path, title):
    files = list(Path(dir_path).glob('**/*'))
    markdown = [f"### {title}\n"]
    markdown.append("| File Name | Raw Link |")
    markdown.append("|-----------|----------|")
    
    for file in files:
        if file.is_file():
            rel_path = file.relative_to(dir_path)
            raw_url = f"{REPO_BASE}/{dir_path}/{rel_path}"
            markdown.append(f"| `{rel_path}` | [Link]({raw_url}) |")
    
    return '\n'.join(markdown)

def update_readme():
    clash_section = generate_section("sources/clash-rules", "Clash Rules")
    loon_section = generate_section("sources/loon-rules", "Loon Rules")
    
    template = f"""
# Rules Repository

{clash_section}

{loon_section}

> 最后更新：%TIMESTAMP%
    """.strip()
    
    template = template.replace("%TIMESTAMP%", 
        datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(template)

if __name__ == "__main__":
    from datetime import datetime
    update_readme()

