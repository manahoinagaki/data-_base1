import sqlite3

con = sqlite3.connect('tast3.db')
cur = con.cursor()
cur.execute(sql, data)
con.commit()
cur.close()
 