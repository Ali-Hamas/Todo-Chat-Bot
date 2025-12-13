import sqlite3

# Connect to the database
conn = sqlite3.connect('todo.db')
cursor = conn.cursor()

# Get table info for users
cursor.execute("PRAGMA table_info(users);")
table_info = cursor.fetchall()

print("Users table schema:")
for column in table_info:
    print(f"  {column}")

# Also check the SQL used to create the table
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users';")
create_sql = cursor.fetchone()
if create_sql:
    print(f"\nCREATE statement for users table:")
    print(create_sql[0])
else:
    print("\nUsers table not found in sqlite_master")

conn.close()