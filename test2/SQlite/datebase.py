import sqlite3

dbname1 = 'test.db'
conn = sqlite3.connect(dbname1,isolation_level=None)
cursor = conn.cursor()

cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL UNIQUE)
            ''')

cursor.execute("seLECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.commit()
conn.close()