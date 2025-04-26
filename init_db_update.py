#!/usr/bin/env python3

from components.db_utils import init_db, update_db_structure

print("开始初始化或更新数据库...")
init_db()  # 这个函数将会创建新数据库或更新现有数据库结构
print("数据库初始化或更新完成!")

print("\n如果您是首次运行系统且数据库为空，可能需要运行数据生成脚本以创建测试数据。") 