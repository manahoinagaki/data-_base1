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


with open('tast3.csv', 'r', encoding='utf-8') as csvfile:
    reader = test.csv.DictReader(csvfile)
    for row in reader:
        cursor.execute("insert into EVENT (come, answer, tobiiri, kikenn, notcome, newevent, student) values (?, ?, ?, ?, ?, ?, ?)", (row['come'], row['answer'], row['tobiiri'], row['kikenn'], row['notcome'], row['newevent'], row['student']))
        conn.commit()

cursor.execute("select * from EVENT")
conn.commit()
rows = cursor.fetchall()
print("ROWS",rows)
for row in rows:
    print(row)

# Removed invalid line with syntax error
conn.close()