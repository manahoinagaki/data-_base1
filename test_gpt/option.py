from flask import Flask, render_template, request, g, jsonify, redirect, url_for
import sqlite3
import os

# Flaskアプリケーションの初期化
app = Flask(__name__)

# データベースファイル名
DATABASE = 'test3.db'

# データベース接続の初期化と取得
def get_db():
    # g.dbが存在しない場合（新しいリクエストの場合）のみ接続を確立
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        # 行を辞書形式（キーでアクセス可能）で取得できるように設定
        g.db.row_factory = sqlite3.Row
    return g.db

# アプリケーションコンテキストが終了する際にデータベース接続を閉じる
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- データベースの初期化 ---
def init_db():
    with app.app_context():
        db = get_db()
        # users テーブルの作成
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        # EVENT テーブルの作成 (仮の構造)
        db.execute('''
            CREATE TABLE IF NOT EXISTS EVENT (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                location TEXT,
                description TEXT,
                number_of_visitors INTEGER,
                date TEXT
            )
        ''')
        db.commit()
        # サンプルデータの挿入 (既に存在しない場合)
        cursor = db.execute("SELECT COUNT(*) FROM EVENT")
        if cursor.fetchone()[0] == 0:
            db.execute("INSERT INTO EVENT (event_name, location, description, number_of_visitors, date) VALUES (?, ?, ?, ?, ?)",
                       ("Tech Conference 2024", "Tokyo", "Latest tech trends", 1500, "2024-10-20"))
            db.execute("INSERT INTO EVENT (event_name, location, description, number_of_visitors, date) VALUES (?, ?, ?, ?, ?)",
                       ("Art Exhibition", "Osaka", "Modern art showcase", 300, "2024-11-15"))
            db.execute("INSERT INTO EVENT (event_name, location, description, number_of_visitors, date) VALUES (?, ?, ?, ?, ?)",
                       ("Local Food Festival", "Nagoya", "Local delicacies and music", 800, "2025-01-25"))
            db.commit()
        print("Database initialized and sample data added.")

# --- API エンドポイント ---

# 全ユーザーを取得するAPI
@app.route('/api/users', methods=['GET'])
def get_users():
    db = get_db()
    users = db.execute('SELECT * FROM users').fetchall()
    return jsonify([dict(user) for user in users])

# 新しいユーザーを追加するAPI
@app.route('/api/users', methods=['POST'])
def add_user():
    new_user = request.json
    name = new_user.get('name')
    email = new_user.get('email')

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    db = get_db()
    try:
        db.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
        db.commit()
        return jsonify({'message': 'User added successfully', 'user': new_user}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'User with this email already exists'}), 409
    except Exception as e:
        # その他のエラーを捕捉
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


# --- イベント検索ページ ---

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    # フォームのデフォルト値を設定
    # POSTリクエスト時には、ユーザーの入力値で更新されます。
    form_values = {
        'free_word': '',
        'number_of_visitors': '',
        'number_of_visitors_op': 'none', # 'none', 'gt', 'lt', 'eq'
        'search_mode': 'and' # デフォルトはAND検索
    }

    if request.method == 'POST':
        # POSTリクエスト（検索ボタンを押してフォームを送信したとき）
        # ブラウザから送られてきた値を受け取り、form_valuesを更新
        form_values['free_word'] = request.form.get('free_word', '')
        form_values['number_of_visitors'] = request.form.get('number_of_visitors', '')
        form_values['number_of_visitors_op'] = request.form.get('number_of_visitors_op', 'none')
        form_values['search_mode'] = request.form.get('search_mode', 'and')

        db = get_db()
        query_parts = []
        params = []

        # フリーワード検索
        if form_values['free_word']:
            search_words = form_values['free_word'].split() # スペースで分割
            if form_values['search_mode'] == 'and':
                # AND検索: 全てのキーワードを含む
                for word in search_words:
                    query_parts.append("(event_name LIKE ? OR description LIKE ? OR location LIKE ?)")
                    params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])
                logical_operator = ' AND '
            else: # OR検索
                # OR検索: いずれかのキーワードを含む
                or_conditions = []
                for word in search_words:
                    or_conditions.append("(event_name LIKE ? OR description LIKE ? OR location LIKE ?)")
                    params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])
                if or_conditions:
                    query_parts.append(f"({' OR '.join(or_conditions)})")
                logical_operator = ' AND ' # フリーワード自体はORだが、他の条件とはAND

        # 訪問者数検索
        if form_values['number_of_visitors'] and form_values['number_of_visitors_op'] != 'none':
            try:
                num_visitors = int(form_values['number_of_visitors'])
                op = form_values['number_of_visitors_op']
                if op == 'gt': # より大きい
                    query_parts.append("number_of_visitors > ?")
                elif op == 'lt': # より小さい
                    query_parts.append("number_of_visitors < ?")
                elif op == 'eq': # 等しい
                    query_parts.append("number_of_visitors = ?")
                params.append(num_visitors)
            except ValueError:
                # 数字でない場合は無視するか、エラーメッセージを返す
                pass

        # クエリの構築
        if query_parts:
            where_clause = logical_operator.join(query_parts)
            sql_query = f"SELECT * FROM EVENT WHERE {where_clause}"
        else:
            sql_query = "SELECT * FROM EVENT" # 条件がない場合は全件取得

        cursor = db.execute(sql_query, params)
        results = cursor.fetchall()
        # fetchall() の結果は sqlite3.Row オブジェクトのリストなので、辞書のリストに変換
        results = [dict(row) for row in results]

    else: # request.method == 'GET'
        # GETリクエスト（初めてページを開いたときやリセットボタンを押したとき）
        # デフォルトのform_values（すべて空または初期値）をHTMLに渡す
        # ここで全件表示したい場合は以下のようにする
        db = get_db()
        cursor = db.execute("SELECT * FROM EVENT")
        results = cursor.fetchall()
        results = [dict(row) for row in results] # 辞書のリストに変換

    # 更新されたform_values（ユーザーが入力した値が含まれる）と検索結果をHTMLに渡す
    return render_template('opinion.html', results=results, **form_values)

if __name__ == '__main__':
    # アプリケーション起動時にデータベースを初期化
    init_db()
    # Flaskアプリを実行
    # debug=True は開発用です。本番環境では使用しないでください。
    app.run(debug=True, port=5000) # ポートを指定して実行することも可能