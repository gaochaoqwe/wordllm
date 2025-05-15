"""
数据库迁移脚本：添加project_name列，并将title列改名为template_name

使用方法：
1. 备份数据库
2. 确保应用程序停止运行
3. 执行脚本 python migrations/add_project_name_column.py
"""
import os
import sys
import sqlite3
from datetime import datetime

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从配置加载数据库URI
from app import db, create_app

app = create_app()

# 确保在应用上下文中运行
with app.app_context():
    # 获取数据库URI
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    print(f"数据库URI: {db_uri}")
    
    # 如果是SQLite数据库
    if db_uri.startswith('sqlite:///'):
        # 提取文件路径
        db_path = db_uri.replace('sqlite:///', '')
        
        if not os.path.isabs(db_path):
            # 如果是相对路径，转换为绝对路径
            db_path = os.path.join(app.root_path, db_path)
        
        print(f"数据库路径: {db_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 projects 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        if not cursor.fetchone():
            print("错误: projects 表不存在")
            sys.exit(1)
        
        # 检查列结构
        cursor.execute("PRAGMA table_info(projects)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # 如果 project_name 列已存在，则跳过创建
        if 'project_name' in columns:
            print("project_name 列已存在，跳过创建")
        else:
            # 添加 project_name 列
            cursor.execute("ALTER TABLE projects ADD COLUMN project_name TEXT")
            print("已添加 project_name 列")
        
        # 如果 template_name 列已存在，则跳过创建
        if 'template_name' in columns:
            print("template_name 列已存在，跳过创建")
        else:
            # 添加 template_name 列
            cursor.execute("ALTER TABLE projects ADD COLUMN template_name TEXT")
            print("已添加 template_name 列")
        
        # 将现有数据从 title 字段复制到新字段
        if 'title' in columns:
            # 复制 title 到 template_name (如果 template_name 为空)
            cursor.execute("""
                UPDATE projects 
                SET template_name = title 
                WHERE template_name IS NULL OR template_name = ''
            """)
            print("已将 title 字段的值复制到 template_name 字段")
            
            # 复制 title 到 project_name (如果 project_name 为空)
            cursor.execute("""
                UPDATE projects 
                SET project_name = title 
                WHERE project_name IS NULL OR project_name = ''
            """)
            print("已将 title 字段的值复制到 project_name 字段")
        
        # 提交事务
        conn.commit()
        conn.close()
        
        print("迁移成功完成！")
    else:
        print(f"不支持的数据库类型: {db_uri}")
        print("该脚本仅支持 SQLite 数据库。请手动修改其他类型的数据库。")
        sys.exit(1)
