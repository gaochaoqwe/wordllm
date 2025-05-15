"""
直接更新数据库结构的脚本

这个脚本会直接连接SQLite数据库，添加新的列并迁移数据。
"""
import os
import sqlite3

# 数据库文件路径 - 根据您实际的数据库位置进行调整
db_path = "app/wordllm.db"  # 数据库文件在app目录下

# 确保数据库文件存在
if not os.path.exists(db_path):
    print(f"错误: 找不到数据库文件 {db_path}")
    print("请调整脚本中的 db_path 变量以指向正确的数据库文件位置")
    exit(1)

try:
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"成功连接到数据库: {db_path}")
    
    # 检查 projects 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
    if not cursor.fetchone():
        print("错误: projects 表不存在")
        exit(1)
    
    # 检查列结构
    cursor.execute("PRAGMA table_info(projects)")
    columns = {row[1] for row in cursor.fetchall()}
    print(f"当前的列: {', '.join(columns)}")
    
    # 如果 project_name 列不存在，则添加
    if 'project_name' not in columns:
        print("正在添加 project_name 列...")
        cursor.execute("ALTER TABLE projects ADD COLUMN project_name TEXT")
        print("已添加 project_name 列")
    else:
        print("project_name 列已存在，跳过")
    
    # 如果 template_name 列不存在，则添加
    if 'template_name' not in columns:
        print("正在添加 template_name 列...")
        cursor.execute("ALTER TABLE projects ADD COLUMN template_name TEXT")
        print("已添加 template_name 列")
    else:
        print("template_name 列已存在，跳过")
    
    # 重新检查列结构，确认添加成功
    cursor.execute("PRAGMA table_info(projects)")
    updated_columns = {row[1] for row in cursor.fetchall()}
    print(f"更新后的列: {', '.join(updated_columns)}")
    
    # 如果存在 title 列，则将其值复制到新列
    if 'title' in columns:
        # 复制 title 到 template_name
        cursor.execute("""
            UPDATE projects 
            SET template_name = title 
            WHERE (template_name IS NULL OR template_name = '') AND title IS NOT NULL
        """)
        
        # 复制 title 到 project_name
        cursor.execute("""
            UPDATE projects 
            SET project_name = title 
            WHERE (project_name IS NULL OR project_name = '') AND title IS NOT NULL
        """)
        
        print("已将 title 字段的值复制到 project_name 和 template_name 字段")
        
        # 查看迁移后的数据
        cursor.execute("SELECT id, title, project_name, template_name FROM projects LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            print("\n前5条数据示例:")
            for row in rows:
                print(f"ID: {row[0]}, title: {row[1]}, project_name: {row[2]}, template_name: {row[3]}")
    
    # 提交事务
    conn.commit()
    conn.close()
    
    print("\n数据库结构更新成功！请重启应用程序。")

except sqlite3.Error as e:
    print(f"SQLite错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
