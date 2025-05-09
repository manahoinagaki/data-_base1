import sqlite3

dbname1 = 'test.db'
conn = sqlite3.connect(dbname1,isolation_level=None)
cursor = conn.cursor()

sql = """create table if not exists test(id, name, date)"""

sql = """select name from splite_master where type='table'"""

sql = """INSERT INTO test VALUES(?,?,?)"""

data = [
   (1, "Taro", 19800810),
   (2, "Bob", 19921015),
   (3, "Masa", 20050505),
   (4, "Jiro", 19910510),
   (5, "Satoshi", 19880117)
]

for t in cursor.executemany(sql,data):
    print(t)   

corsor.executemany(sql, data)
conn.commit()

spl = """SELECT * FROM test"""
corsor.execute(spl)
print(corsor.fetchall())
conn.close()