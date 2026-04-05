from config.database import get_db
import os

print("Testing database connection...")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")

try:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"Connection successful! Result: {result}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")