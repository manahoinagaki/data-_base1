import sqlite3
import csv

conn = sqlite3.connect(
    'tast3.db',
)
cursor = conn.cursor()
cursor.execute("""
        create table if not exists EVENT (
                id integer primary key autoincrement,
                come integer,
                answer integer,
                tobiiri integer,
                kikenn integer,
                notcome integer,
                newevent integer,
                student integer
        )
""")

cursor.execute("select * from EVENT")
conn.commit()
rows = cursor.fetchall()
print("ROWS",rows)
for row in rows:
    print(row)