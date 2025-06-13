# app.py
from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = 'data.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS event_participation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            visitors_count INTEGER,
            answers_count INTEGER,
            walkin_count INTEGER,
            withdrawal_count INTEGER,
            no_show_count INTEGER,
            new_event TEXT,
            role TEXT,
            event_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    mode = data.get('mode', 'AND').upper()
    keyword = data.get('keyword', '').strip()
    filters = []
    values = []

    if keyword:
        filters.append("(" + " OR ".join([f"{col} LIKE ?" for col in ["student_id", "event_name", "role", "new_event"]]) + ")")
        values.extend([f"%{keyword}%"] * 4)

    for field in ["visitors_count", "answers_count", "walkin_count", "withdrawal_count", "no_show_count"]:
        min_val = data.get(f"{field}_min")
        max_val = data.get(f"{field}_max")
        if min_val:
            filters.append(f"{field} >= ?")
            values.append(int(min_val))
        if max_val:
            filters.append(f"{field} <= ?")
            values.append(int(max_val))

    if data.get("new_event"):
        filters.append("new_event = ?")
        values.append(data["new_event"])

    if data.get("role"):
        filters.append("role = ?")
        values.append(data["role"])

    where_clause = (f" {mode} ".join(filters)) if filters else "1"
    query = f"SELECT * FROM event_participation WHERE {where_clause}"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, values)
    rows = c.fetchall()
    conn.close()

    return jsonify(rows)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
