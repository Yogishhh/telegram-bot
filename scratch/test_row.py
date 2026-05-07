import sqlite3

conn = sqlite3.connect(':memory:')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('SELECT 1 as id')
row = cursor.fetchone()

print(f"Type: {type(row)}")
print(f"isinstance(row, dict): {isinstance(row, dict)}")
print(f"row['id']: {row['id']}")
print(f"row[0]: {row[0]}")
