import sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()

cur.execute('''
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL UNIQUE)
            ''')

cur.execute("seLECT * FROM users")
rows = cur.fetchall()
for row in rows:
    print(row)

conn.commit()
conn.close()