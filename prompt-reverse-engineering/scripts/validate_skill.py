#!/usr/bin/env python3
"""
提示词反推技能验证脚本

用于验证技能文件结构和基本格式是否正确。
"""

import os
import sys
import yaml
from pathlib import Path

def validate_skill(skill_path):
    """验证技能目录结构是否符合规范"""
    skill_dir = Path(skill_path)

    print(f"正在验证技能: {skill_dir.name}")
    print("=" * 50)

    # 1. 检查必需文件
    required_files = ["SKILL.md", "LICENSE.txt"]
    missing_files = []

    for file in required_files:
        if not (skill_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"[错误] 缺少必需文件: {missing_files}")
        return False
    else:
        print("[成功] 必需文件检查通过")

    # 2. 检查SKILL.md的YAML frontmatter
    skill_md_path = skill_dir / "SKILL.md"
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取YAML frontmatter
    if not content.startswith('---\n'):
        print("❌ SKILL.md必须以YAML frontmatter开头 (---)")
        return False

    yaml_end = content.find('\n---', 4)
    if yaml_end == -1:
        print("❌ 无法找到YAML frontmatter结束标记(---)")
        return False

    yaml_content = content[4:yaml_end]

    try:
        metadata = yaml.safe_load(yaml_content)

        # 检查必需字段
        required_fields = ["name", "description"]
        missing_fields = []

        for field in required_fields:
            if field not in metadata:
                missing_fields.append(field)

        if missing_fields:
            print(f"❌ YAML frontmatter缺少必需字段: {missing_fields}")
            return False

        print(f"[成功] YAML frontmatter检查通过")
        print(f"   技能名称: {metadata['name']}")
        print(f"   技能描述: {metadata['description'][:100]}...")

        if 'license' in metadata:
            print(f"   许可证: {metadata['license']}")

    except yaml.YAMLError as e:
        print(f"[错误] YAML解析错误: {e}")
        return False

    # 3. 检查目录结构
    optional_dirs = ["scripts", "references", "assets"]
    existing_dirs = []

    for dir_name in optional_dirs:
        dir_path = skill_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            existing_dirs.append(dir_name)

    if existing_dirs:
        print(f"[成功] 可选的目录结构: {existing_dirs}")
    else:
        print("[信息] 没有创建可选的目录(scripts/references/assets)，这是可选的")

    # 4. 检查文件大小
    skill_md_size = skill_md_path.stat().st_size
    if skill_md_size > 5000:  # 大约5KB
        print(f"[信息] SKILL.md文件偏大({skill_md_size} bytes)，建议保持精简")
    else:
        print(f"[成功] SKILL.md文件大小合适({skill_md_size} bytes)")

    # 5. 额外的技能特定检查
    print("\n[检查] 进行技能特定检查...")

    # 检查是否有references文件
    references_dir = skill_dir / "references"
    if references_dir.exists():
        ref_files = list(references_dir.glob("*.md"))
        if ref_files:
            print(f"[成功] 找到参考文件: {[f.name for f in ref_files]}")
        else:
            print("[信息] references目录存在但没有.md文件")

    # 检查关键术语
    necessary_terms = ["面部一致性", "提示词", "分析"]
    missing_terms = []

    for term in necessary_terms:
        if term not in content:
            missing_terms.append(term)

    if missing_terms:
        print(f"[警告] 未找到关键术语: {missing_terms}")
    else:
        print("[成功] 关键术语检查通过")

    print("\n" + "=" * 50)
    print("[完成] 技能验证完成！")

    # 给出改进建议
    suggestions = []

    # 检查是否有实用示例
    if "示例" not in content and "example" not in content.lower():
        suggestions.append("考虑添加实用示例以增强技能可用性")

    # 检查是否有明确的工作流程
    if "工作流程" not in content and "workflow" not in content.lower():
        suggestions.append("考虑添加明确的工作流程图解或步骤说明")

    if suggestions:
        print("\n[建议] 改进建议:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f" {i}. {suggestion}")

    return True

def main():
    # 自动检测当前目录是否为技能目录
    current_dir = Path.cwd()

    # 如果从脚本目录运行，则向上找技能目录
    if current_dir.name == "scripts":
        skill_dir = current_dir.parent
    else:
        skill_dir = current_dir

    print(f"[目录] 技能目录: {skill_dir}")

    if not validate_skill(skill_dir):
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())