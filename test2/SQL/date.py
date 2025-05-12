import sqlite3
import random
import string

# DB作成
conn = sqlite3.connect("school.db")
cur = conn.cursor()

# テーブル作成
cur.execute('''
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT,
    grade INTEGER,
    gender TEXT
)
''')

# ランダムな名前生成関数
def random_name(length=5):
    return ''.join(random.choices(string.ascii_lowercase, k=length)).capitalize()

# 400人分のデータを挿入
students = []
for i in range(1, 401):
    student_id = f"S{i:04d}"  # S0001〜S0400
    name = random_name()
    grade = random.randint(1, 4)  # 1〜4年生
    gender = random.choice(["男", "女"])
    students.append((student_id, name, grade, gender))

cur.executemany('INSERT INTO students (student_id, name, grade, gender) VALUES (?, ?, ?, ?)', students)

conn.commit()
conn.close()

print("400人分のデータを作成しました。")

conn = sqlite3.connect("school.db")
cur = conn.cursor()

# イベント参加履歴用テーブル作成
cur.execute('''
CREATE TABLE IF NOT EXISTS event_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    event_name TEXT,
    event_date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)
''')

conn.commit()
conn.close()

import datetime

conn = sqlite3.connect("school.db")
cur = conn.cursor()

# ランダムで50人をイベント参加させる
participants = random.sample([f"S{i:04d}" for i in range(1, 401)], 50)

event_data = []
for student_id in participants:
    event_name = "春のオリエンテーション"
    event_date = datetime.date.today().isoformat()
    event_data.append((student_id, event_name, event_date))

cur.executemany('INSERT INTO event_attendance (student_id, event_name, event_date) VALUES (?, ?, ?)', event_data)

conn.commit()
conn.close()

print("イベント参加者50人分を追加しました。")

conn = sqlite3.connect("school.db")
cur = conn.cursor()

keyword = input("検索ワード（学籍番号 or 名前）を入力してください： ")

cur.execute('''
SELECT s.student_id, s.name, s.grade, s.gender, e.event_name, e.event_date
FROM students s
LEFT JOIN event_attendance e ON s.student_id = e.student_id
WHERE s.student_id LIKE ? OR s.name LIKE ?
''', (f"%{keyword}%", f"%{keyword}%"))

results = cur.fetchall()

for row in results:
    print(row)

conn.close()
