import sqlite3

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

db.execute(sql)
db.close()