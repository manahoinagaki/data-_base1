from flask import Flask, render_template, request, g, redirect, url_for, jsonify
import sqlite3
import csv
import os

app = Flask(__name__)
DATABASE = 'test3.db' # データベースファイル名

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 行を辞書形式で取得できるようにする
    return conn

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

@app.route('/api/users', methods=['POST'])
def add_user():
    new_user = request.json
    name = new_user.get('name')
    email = new_user.get('email')

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
        conn.commit()
        return jsonify({'message': 'User added successfully', 'user': new_user}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'User with this email already exists'}), 409
    finally:
        conn.close()

if __name__ == '__main__':
    # データベースの初期化 (初回のみ実行)
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    app.run(debug=True)
    
@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    # フォームのデフォルト値を設定
    # これが「事前に何も入っていなかったら空欄にする」ための設定です。
    # 各入力フィールドの初期値を空文字列 '' や '選んでださい' にしています。
    form_values = {
        'free_word': '',
        'number_of_visitors': '',
        'number_of_visitors_op': '選んでださい',
        # ... 他のフォーム要素も同様にデフォルト値を設定 ...
        'serch_mode': 'and' # デフォルトはAND検索
    }

    if request.method == 'GET':
        # GETリクエスト（初めてページを開いたときやリセットボタンを押したとき）
        # デフォルトのform_values（すべて空または初期値）をHTMLに渡します。
        db = get_db()
        cursor = db.execute("SELECT * FROM EVENT")
        results = cursor.fetchall()
        return render_template('opinion.html', results=results, **form_values)

    elif request.method == 'POST':
        # POSTリクエスト（検索ボタンを押してフォームを送信したとき）
        # ブラウザから送られてきた値を受け取り、form_valuesを更新します。
        # ここが「事前に文字が入っていたらそのまま維持する」ための部分です。
        form_values['free_word'] = request.form.get('free_word', '')
        form_values['number_of_visitors'] = request.form.get('number_of_visitors', '')
        form_values['number_of_visitors_op'] = request.form.get('number_of_visitors_op', '選んでださい')
        # ... 他のフォーム要素も request.form.get() で値を取得し、form_valuesを更新 ...

        # ... (検索ロジック) ...

        # 更新されたform_values（ユーザーが入力した値が含まれる）をHTMLに渡します。
        return render_template('opinion.html', results=results, **form_values)
