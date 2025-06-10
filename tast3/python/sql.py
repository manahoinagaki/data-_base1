import sqlite3
import csv

db = sqlite3.connect(
    'tast3.db',
    isolation_level=None,
)

sql = """
        create table if not exists EVENT (
                id integer primary key autoincrement,
                come integer,
                answer integer,
                tobiiri integer,
                kikenn integer,
                notcome integer,
                newevent integer,
                student integer
        )"""
with open('tast3.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)  # Skip header row
    for row in reader:
        db.execute("insert into EVENT (come, answer, tobiiri, kikenn, notcome, newevent, student) values (?, ?, ?, ?, ?, ?, ?)", row)
        db.commit()

db.execute(sql)
db.close();
db.execute(sql)
db.close()
