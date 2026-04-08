
import sqlite3
import os

# Database file path
DB_FILE = "healthwatch_v2.db"

def fix_schema():
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "ethereum_address" not in columns:
            print("Adding 'ethereum_address' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN ethereum_address VARCHAR(42)")
            conn.commit()
            print("Successfully added 'ethereum_address'.")
        else:
            print("'ethereum_address' column already exists.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
