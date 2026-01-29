import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [r[0] for r in cur.fetchall()]

print(f"Total Tables: {len(tables)}")
print("\nTable List:")
for i, t in enumerate(tables, 1):
    # Get row count
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"{i}. {t} ({count} rows)")
    except:
        print(f"{i}. {t}")

conn.close()
