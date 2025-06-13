import sqlite3
import csv

conn = sqlite3.connect(
    'tast3.db',
)

cursor.execute("select * from EVENT")
conn.commit()
rows = cursor.fetchall()
print("ROWS",rows)
for row in rows:
    print(row)