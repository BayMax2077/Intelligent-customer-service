#!/usr/bin/env python3
"""
批量修复SQLAlchemy query用法
"""
import os
import re

def fix_queries_in_file(file_path):
    """修复单个文件中的query用法"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复模式
    patterns = [
        # Model.query.method() -> db.session.query(Model).method()
        (r'(\w+)\.query\.', r'db.session.query(\1).'),
        # Model.query.get() -> db.session.get(Model, )
        (r'db\.session\.query\((\w+)\)\.get\(([^)]+)\)', r'db.session.get(\1, \2)'),
        # Model.query.get_or_404() -> db.session.get_or_404(Model, )
        (r'db\.session\.query\((\w+)\)\.get_or_404\(([^)]+)\)', r'db.session.get_or_404(\1, \2)'),
    ]
    
    original_content = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    return False

def main():
    """主函数"""
    api_dir = "houduan/api"
    fixed_files = []
    
    for filename in os.listdir(api_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(api_dir, filename)
            if fix_queries_in_file(file_path):
                fixed_files.append(file_path)
    
    print(f"Fixed {len(fixed_files)} files:")
    for file_path in fixed_files:
        print(f"  - {file_path}")

if __name__ == "__main__":
    main()
