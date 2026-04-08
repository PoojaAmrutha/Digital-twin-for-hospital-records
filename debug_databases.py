"""
Check doctor credentials in ALL found database files
"""
import sqlite3
import os

DB_FILES = [
    'healthwatch_v2.db',
    'backend/healthwatch_v2.db',
    'healthwatch.db',
    'backend/healthwatch.db'
]

def check_db(db_path):
    print(f"\n🔍 Checking: {db_path}")
    if not os.path.exists(db_path):
        print("   ❌ File not found")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, email, password_hash, user_type FROM users WHERE email LIKE '%hospital%'")
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(f"   ✅ Found User:")
                print(f"      Name:  {row[0]}")
                print(f"      Email: {row[1]}")
                print(f"      Hash:  {row[2][:20]}... (Algo: {'pbkdf2' if 'pbkdf2' in str(row[2]) else 'bcrypt' if 'bcrypt' in str(row[2]) else 'unknown'})")
        else:
            print("   ⚠️  No doctor found in this DB")
            
        conn.close()
    except Exception as e:
        print(f"   ❌ Error reading DB: {e}")

if __name__ == "__main__":
    print(f"CWD: {os.getcwd()}")
    for db in DB_FILES:
        check_db(db)
