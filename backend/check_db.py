import sqlite3

def check_schema():
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users';")
    schema = cursor.fetchone()
    if schema:
        print("Schema for users table:")
        print(schema[0])
    else:
        print("Table users not found.")
    conn.close()

if __name__ == "__main__":
    check_schema()
