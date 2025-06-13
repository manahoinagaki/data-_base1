import csv
import sqlite3

# ファイル名とDB設定
CSV_FILE = 'event_data.csv'
DB_FILE = 'data.db'

# データベースに接続
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# CSV読み込みと挿入
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = [
        (
            row['student_id'],
            int(row['visitors_count']),
            int(row['answers_count']),
            int(row['walkin_count']),
            int(row['withdrawal_count']),
            int(row['no_show_count']),
            row['new_event'],
            row['role'],
            row['event_name']
        )
        for row in reader
    ]

c.executemany('''
    INSERT INTO event_participation (
        student_id,
        visitors_count,
        answers_count,
        walkin_count,
        withdrawal_count,
        no_show_count,
        new_event,
        role,
        event_name
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', rows)

conn.commit()
conn.close()

print("✅ CSVデータをデータベースに読み込み完了しました。")
