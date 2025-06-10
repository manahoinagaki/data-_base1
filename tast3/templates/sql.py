import sqlite3

db = sqlite3.connect(
    'tast3.db'
    isolation_level=None,
)

sql = """
        create table if not exists TAX (
                id integer primary key autoincrement,
                proce integer
        )"""

db.execute(sql)
db.close()