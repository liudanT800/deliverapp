import sqlite3
import os

db_path = os.path.join('backend', 'test.db')
print(f'检查数据库: {db_path}')
print(f'文件存在: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('数据库表:')
        for table in tables:
            print(f'  - {table[0]}')

        # 检查各个表
        table_names = ['user', 'task', 'message', 'evaluation', 'wallet', 'transactions', 'appeal']
        for table_name in table_names:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f'{table_name}表记录数: {count}')
            except Exception as e:
                print(f'{table_name}表不存在或查询失败: {e}')

        conn.close()
    except Exception as e:
        print(f'数据库连接失败: {e}')
else:
    print('数据库文件不存在')
