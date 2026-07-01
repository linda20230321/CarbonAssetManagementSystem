# update_password.py
import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'carbon_asset.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 更新 admin 用户密码
new_password = hash_password('admin123')
cursor.execute('''
    UPDATE users SET password = ? WHERE username = 'admin'
''', (new_password,))

conn.commit()
conn.close()

print("✅ 密码已更新为加密格式")
print(f"加密后的密码: {new_password}")