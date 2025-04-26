#!/usr/bin/env python3

import os
from components.db_utils import update_db_structure, init_db
from generate_data import generate_all_data

print("=" * 50)
print("项目管理系统数据库更新与重新生成")
print("=" * 50)

# 检查是否已存在数据库文件
db_exists = os.path.exists('project_manager.db')

if db_exists:
    print("\n1. 数据库文件已存在，正在更新数据库结构...")
    update_db_structure()
else:
    print("\n1. 数据库文件不存在，将创建新数据库...")
    init_db()

print("\n2. 正在重新生成测试数据...")
generate_all_data()

print("\n3. 数据库更新和数据重新生成已完成！")
print("\n现在您可以启动应用程序使用新的数据结构和测试数据。")
print("=" * 50) 