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
           free_word TEXT,
            visitors INTEGER,
            answer INTEGER,
            drop_count INTEGER, -- 'drop' はSQLの予約語の可能性があるため変更
            abstention INTEGER,
            notcome INTEGER,
            new_event_op TEXT, -- 'ok' / 'nt' を格納
            event_name_op TEXT, -- イベント名を格納
            event_date TEXT,    -- 日付を格納 (YYYY-MM-DD形式)
            student_type TEXT   -- '一般生徒' / '執行委員' を格納
            -- name TEXT, price INTEGER はこのフォームにはないため削除するか、用途によって追加
        )
    ''')

    # サンプルデータをいくつか追加（もしデータがなければ）
    cursor.execute("INSERT OR IGNORE INTO items (id, visitors, answer ,drop_count, abstention, notcome, new_event_op, event_name_op, event_date, student_type) VALUES (1, 1, 2, 1, 1, 3, 0, '一般生徒', '2023-01-01', '一般生徒')")
    cursor.execute("INSERT OR IGNORE INTO items (id, visitors, answer ,drop_count, abstention, notcome, new_event_op, event_name_op, event_date, student_type) VALUES (2, 4, 2, 2, 0, 4, 0, '執行委員', '2023-01-02', '執行委員')")
    cursor.execute("INSERT OR IGNORE INTO items (id, visitors, answer ,drop_count, abstention, notcome, new_event_op, event_name_op, event_date, student_type) VALUES (3, 8, 8, 0, 0, 2, 0, '一般生徒', '2023-01-03', '一般生徒')")
    cursor.execute("INSERT OR IGNORE INTO items (id, visitors, answer ,drop_count, abstention, notcome, new_event_op, event_name_op, event_date, student_type) VALUES (4, 2, 5, 0, 3, 5, 0, '一般生徒', '2023-01-04', '一般生徒')")

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
@app.route('/search_items', methods=['GET'])
def search_items():
    # フォームから送られてくる全パラメータを取得
    free_word = request.args.get('free_word', '').strip()
    visitors = request.args.get('visitors')
    visitors_op = request.args.get('visitors_op', 'none')
    answer = request.args.get('answer')
    answer_op = request.args.get('answer_op', 'none')
    drop = request.args.get('drop')
    drop_op = request.args.get('drop_op', 'none')
    abstention = request.args.get('abstention')
    abstention_op = request.args.get('abstention_op', 'none')
    notcome = request.args.get('notcome')
    notcome_op = request.args.get('notcome_op', 'none')
    new_event_op = request.args.get('new_event_op', 'none')
    event_name_op = request.args.get('event_name_op', 'all')
    event_date = request.args.get('event_date')
    student_type = request.args.get('student_type', 'none')
    search_mode = request.args.get('search_mode', 'and') # デフォルトはAND検索

    conn = sqlite3.connect('data.db') # ファイル名を統一
    cursor = conn.cursor()

    conditions = []
    params = []

    if free_word:
        conditions.append("free_word LIKE ?")
        params.append(f"%{free_word}%")

    # 数値条件の追加ヘルパー関数
    def add_numeric_condition(value_str, op, column_name):
        if value_str:
            try:
                value = int(value_str)
                if op == 'gt':
                    conditions.append(f"{column_name} >= ?")
                    params.append(value)
                elif op == 'lt':
                    conditions.append(f"{column_name} <= ?")
                    params.append(value)
                elif op == 'eq': # HTMLのeqは「以上を除く」なので、実際は < value
                    conditions.append(f"{column_name} < ?")
                    params.append(value)
                elif op == 'ne': # HTMLのneは「以下を除く」なので、実際は > value
                    conditions.append(f"{column_name} > ?")
                    params.append(value)
                elif op == 'none': # 「回」は完全一致と仮定
                    conditions.append(f"{column_name} = ?")
                    params.append(value)
            except ValueError:
                pass # 数値に変換できない場合は無視

    add_numeric_condition(visitors, visitors_op, 'visitors')
    add_numeric_condition(answer, answer_op, 'answer')
    add_numeric_condition(drop, drop_op, 'drop_count') # カラム名を修正
    add_numeric_condition(abstention, abstention_op, 'abstention')
    add_numeric_condition(notcome, notcome_op, 'notcome')

    if new_event_op != 'none':
        # HTMLの'ok'は○、'nt'は×
        if new_event_op == 'ok':
            conditions.append("new_event_op = ?")
            params.append('ok')
        elif new_event_op == 'nt':
            conditions.append("new_event_op = ?")
            params.append('nt')

    if event_name_op != 'all':
        # イベント名の検索ロジック (HTMLのoption valueに応じて調整)
        # 現在のHTMLのvalueがそのまま検索条件として使えるか要確認。
        # 例: contains -> LIKE %value%, exact -> = value
        # ここでは単純に文字列一致と仮定
        conditions.append("event_name_op = ?")
        params.append(event_name_op) # HTMLのvalueがそのままイベント名に対応すると仮定

    if event_date:
        conditions.append("event_date = ?") # 日付の完全一致
        params.append(event_date)

    if student_type != 'none':
        conditions.append("student_type = ?")
        # HTMLのvalue '1'/'2' を実際の表示文字列 '一般生徒'/'執行委員' に変換して検索
        if student_type == '1':
            params.append('一般生徒')
        elif student_type == '2':
            params.append('執行委員')

    sql_query = "SELECT * FROM items" # 全カラム取得に変更

    if conditions:
        join_operator = " AND " if search_mode == 'and' else " OR "
        sql_query += " WHERE " + join_operator.join(conditions)

    cursor.execute(sql_query, tuple(params))

    # カラム名を取得して辞書形式で結果を返す
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return jsonify(results)

# --- アプリケーションの実行 ---
if __name__ == '__main__':
    app.run(debug=True) # アプリケーションを実行。debug=Trueで変更が自動で反映される