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
    reader = csv.reader(csvfile)
    next(reader, None)  # Skip header row
    for row in reader:
        cursor.execute("insert into EVENT (come, answer, tobiiri, kikenn, notcome, newevent, student) values (?, ?, ?, ?, ?, ?, ?)", row)
        conn.commit()

cursor.execute("select * from EVENT")
conn.commit()
rows = cursor.fetchall()
print("ROWS",rows)
for row in rows:
    print(row)

cursor.execute("select * from EVENT"print("print("")"))
conn.close()