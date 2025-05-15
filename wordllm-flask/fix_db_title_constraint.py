"""
修复数据库表结构的脚本

这个脚本会移除 projects 表中 title 字段的 NOT NULL 约束
"""
import os
import sqlite3

# 数据库文件路径 - 根据项目实际的数据库位置
db_path = "app/wordllm.db"

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
    
    # 获取当前表结构
    cursor.execute("PRAGMA table_info(projects)")
    columns = cursor.fetchall()
    print("当前表结构:")
    for col in columns:
        print(f"  {col[1]}: {'NOT NULL' if col[3] else 'NULL'}")
    
    # 由于SQLite不支持直接更改列的NOT NULL约束，我们需要创建一个新表然后迁移数据
    
    # 1. 创建新表，但去掉title字段的NOT NULL约束
    create_table_sql = "CREATE TABLE new_projects (\n"
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        not_null = "NOT NULL" if col[3] and col_name != "title" else ""
        primary_key = "PRIMARY KEY" if col[5] else ""
        create_table_sql += f"  {col_name} {col_type} {not_null} {primary_key},\n"
    create_table_sql = create_table_sql.rstrip(",\n") + "\n)"
    
    print("\n创建新表SQL:")
    print(create_table_sql)
    cursor.execute(create_table_sql)
    
    # 2. 复制数据从原表到新表
    cursor.execute("SELECT * FROM projects")
    columns_names = [description[0] for description in cursor.description]
    columns_str = ", ".join(columns_names)
    
    cursor.execute(f"INSERT INTO new_projects SELECT {columns_str} FROM projects")
    
    # 3. 删除原表
    cursor.execute("DROP TABLE projects")
    
    # 4. 重命名新表为原表名
    cursor.execute("ALTER TABLE new_projects RENAME TO projects")
    
    # 检查新表结构
    cursor.execute("PRAGMA table_info(projects)")
    new_columns = cursor.fetchall()
    print("\n更新后的表结构:")
    for col in new_columns:
        print(f"  {col[1]}: {'NOT NULL' if col[3] else 'NULL'}")
    
    # 提交事务
    conn.commit()
    conn.close()
    
    print("\n成功移除 title 字段的 NOT NULL 约束！请重启应用程序。")

except sqlite3.Error as e:
    print(f"SQLite错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
