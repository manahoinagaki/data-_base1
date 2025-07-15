from flask import Flask, render_template, request, jsonify # Flask関連の機能を読み込み
import sqlite3 # データベース（SQLite）を扱う機能を読み込み

app = Flask(__name__) # Flaskアプリケーションを作成

# --- データベースの準備 ---
def init_db():
    conn = sqlite3.connect('data.db') # data.dbというファイルに接続（なければ作成）
    cursor = conn.cursor() # データベース操作用のカーソルを作成

    # itemsテーブルがなければ作成するSQL命令
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER
        )
    ''')
    # サンプルデータをいくつか追加（もしデータがなければ）
    cursor.execute("INSERT OR IGNORE INTO items (id, visitors, answer ,drop, abstention, notcome, new_event_op, option_type) VALUES (1, 1, 2, 1, 1, 3, 0, '一般生徒')")
    cursor.execute("INSERT OR IGNORE INTO items (id, visitors, answer ,drop, abstention, notcome, new_event_op, option_type) VALUES (2, 4, 2, 2, 0, 4, 0, '執行委員')")
    cursor.execute("INSERT OR IGNORE INTO items (id, visitors, answer ,drop, abstention, notcome, new_event_op, option_type) VALUES (3, 8, 8, 0, 0, 2, 0, '一般生徒')")
    cursor.execute("INSERT OR IGNORE INTO items (id, visitors, answer ,drop, abstention, notcome, new_event_op, option_type) VALUES (4, 2, 5, 0, 3, 5, 0, '一般生徒')")

    conn.commit() # 変更を保存
    conn.close() # データベース接続を閉じる

# アプリケーションが起動する際に、一度だけデータベースを準備する
with app.app_context():
    init_db()

# --- ウェブページを表示するルート ---
@app.route('/')
def option():
    # 'templates/option.html' を読み込んでユーザーのブラウザに表示する
    return render_template('.../templates/option.html')

# --- 検索APIのエンドポイント（ここがAPIの「入り口」） ---
@app.route('/search_items', methods=['GET']) # /search_items というURLにGETリクエストが来たらこの関数を実行
def search_items():
    # ウェブページから送られてきた検索キーワード（'q'という名前で渡される）を取得
    query = request.args.get('q', '').strip() # なければ空文字列、両端の空白も削除

    conn = sqlite3.connect('database.db') # データベースに接続
    cursor = conn.cursor()

    results = [] # 検索結果を保存するリスト

    if query: # 検索キーワードが空でなければ
        # SQLで部分一致検索（例: 'ペン' で '鉛筆' も 'ペン' も見つける）
        # ? を使うことで、ユーザーの入力が安全にSQLに渡されます（SQLインジェクション対策）
        cursor.execute("SELECT name, price FROM items WHERE name LIKE ?", ('%' + query + '%',))

        # 検索結果を1行ずつ取得し、リストに追加
        for row in cursor.fetchall():
            results.append({'name': row[0], 'price': row[1]}) # 辞書形式で追加

    conn.close() # データベース接続を閉じる

    # 検索結果をJSON形式にしてウェブページに返す
    return jsonify(results) # jsonifyはPythonのリストや辞書をJSONに変換してくれる

# --- アプリケーションの実行 ---
if __name__ == '__main__':
    app.run(debug=True) # アプリケーションを実行。debug=Trueで変更が自動で反映される