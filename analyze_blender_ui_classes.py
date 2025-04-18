#!/usr/bin/env python3
"""
分析Blender项目中的UI相关类继承关系
"""

import os
import re
import sys
from collections import defaultdict

# 定义要搜索的文件类型
FILE_EXTENSIONS = ['.py', '.h', '.hh', '.c', '.cc', '.cpp']

# 定义正则表达式模式
PY_CLASS_PATTERN = re.compile(r'class\s+(\w+)\s*\(([^)]*)\):')
CPP_CLASS_PATTERN = re.compile(r'class\s+(\w+)\s*:\s*(?:public|private|protected)?\s*([^{]*)')

# 存储类继承关系
class_hierarchy = defaultdict(list)
class_files = {}

# 关注的核心类
CORE_CLASSES = [
    'bpy_struct', 'Panel', 'Operator', 'PropertyGroup', 'ID', 'UIList',
    'Menu', 'Header', 'Context', 'Window', 'Screen', 'Area', 'Space',
    'Region', 'UILayout'
]

def analyze_python_file(file_path):
    """分析Python文件中的类定义和继承关系"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    for match in PY_CLASS_PATTERN.finditer(content):
        class_name = match.group(1)
        parent_classes = match.group(2).strip().split(',')
        parent_classes = [p.strip() for p in parent_classes if p.strip()]
        
        if parent_classes:
            for parent in parent_classes:
                # 处理像bpy.types.Panel这样的完整路径
                if '.' in parent:
                    parent = parent.split('.')[-1]
                class_hierarchy[parent].append(class_name)
        
        # 记录类定义所在的文件
        class_files[class_name] = os.path.relpath(file_path)

def analyze_cpp_file(file_path):
    """分析C++文件中的类定义和继承关系"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    for match in CPP_CLASS_PATTERN.finditer(content):
        class_name = match.group(1)
        parent_classes_str = match.group(2).strip()
        
        # 处理多重继承
        parent_classes = []
        if parent_classes_str:
            # 分割多个父类（可能由逗号分隔）
            for parent_part in parent_classes_str.split(','):
                # 提取类名（去除public/private/protected关键字）
                parent_part = parent_part.strip()
                if 'public' in parent_part:
                    parent = parent_part.split('public')[-1].strip()
                elif 'private' in parent_part:
                    parent = parent_part.split('private')[-1].strip()
                elif 'protected' in parent_part:
                    parent = parent_part.split('protected')[-1].strip()
                else:
                    parent = parent_part
                
                if parent:
                    # 处理模板类
                    if '<' in parent:
                        parent = parent.split('<')[0].strip()
                    parent_classes.append(parent)
        
        for parent in parent_classes:
            class_hierarchy[parent].append(class_name)
        
        # 记录类定义所在的文件
        class_files[class_name] = os.path.relpath(file_path)

def analyze_directory(directory):
    """递归分析目录中的所有文件"""
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            if ext not in FILE_EXTENSIONS:
                continue
            
            try:
                if ext == '.py':
                    analyze_python_file(file_path)
                else:
                    analyze_cpp_file(file_path)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

def print_hierarchy(base_class, level=0, visited=None, max_depth=None):
    """打印类继承层次结构"""
    if visited is None:
        visited = set()
    
    if base_class in visited:
        return
    
    if max_depth is not None and level > max_depth:
        return
    
    visited.add(base_class)
    indent = "  " * level
    file_info = f" ({class_files.get(base_class, 'unknown file')})" if base_class in class_files else ""
    print(f"{indent}{base_class}{file_info}")
    
    for child in sorted(class_hierarchy.get(base_class, [])):
        print_hierarchy(child, level + 1, visited, max_depth)

def find_base_classes():
    """找出所有基类（没有父类的类）"""
    all_classes = set(class_hierarchy.keys())
    for children in class_hierarchy.values():
        all_classes.update(children)
    
    child_classes = set()
    for children in class_hierarchy.values():
        child_classes.update(children)
    
    return all_classes - child_classes

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_blender_ui_classes.py <directory>")
        return
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        return
    
    print(f"Analyzing directory: {directory}")
    analyze_directory(directory)
    
    # 打印核心类的继承层次结构
    print("\nBlender UI Class Hierarchy:")
    print("==========================")
    
    for base in CORE_CLASSES:
        if base in class_hierarchy or base in class_files:
            print(f"\n--- {base} Hierarchy ---")
            print_hierarchy(base, max_depth=3)  # 限制深度为3层，避免输出过多
    
    # 打印统计信息
    print("\nStatistics:")
    print(f"Total classes found: {len(class_files)}")
    
    # 计算UI相关类的数量
    ui_classes = 0
    for class_name in class_files:
        if any(class_name.startswith(prefix) for prefix in ['UI_', 'VIEW3D_PT_', 'PROPERTIES_', 'OBJECT_PT_']):
            ui_classes += 1
    
    print(f"UI related classes: {ui_classes}")

if __name__ == "__main__":
    main()
