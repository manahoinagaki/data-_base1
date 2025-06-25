from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3
import csv
import os

app = Flask(__name__)
DATABASE = 'test3.db' # データベースファイル名

def get_db():
    # アプリケーションコンテキスト内でデータベース接続を管理
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # カラム名でアクセスできるように設定
    return db

@app.teardown_appcontext
def close_connection(exception):
    # リクエスト終了時にデータベース接続を閉じる
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    # データベースの初期化（テーブル作成とCSVからのデータ挿入）
    with app.app_context():
        db = get_db()
        # スキーマを読み込んでテーブルを作成
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

        # CSVファイルからデータを挿入 (初回起動時のみ実行されるように考慮することも可能)
        # 既にデータがある場合は重複挿入になるので注意
        try:
            with open('test.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    db.execute("INSERT INTO EVENT (come, answer, tobiiri, kikenn, notcome, newevent, student) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (row['come'], row['answer'], row['tobiiri'], row['kikenn'], row['notcome'], row['newevent'], row['student']))
                db.commit()
            print("CSVデータがデータベースに挿入されました。")
        except FileNotFoundError:
            print("test.csvが見つかりませんでした。スキップします。")
        except sqlite3.IntegrityError:
            print("データが既に存在するため、CSVからの挿入をスキップしました。")

# アプリケーション起動時にデータベースを初期化
# これをコメントアウトすると、手動でinit_db()を呼び出すか、
# データベースがすでに存在することを前提とする
# if not os.path.exists(DATABASE):
#    init_db()


# アプリケーション起動時にデータベースを初期化（一度だけ実行されるべき）
@app.before_first_request
def initialize_database():
    if not os.path.exists(DATABASE):
        print("データベースが存在しないため、初期化します...")
        init_db()
    else:
        print("データベースは既に存在します。")

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    # フォームのデフォルト値を設定
    # これにより、GETリクエストで初めてページがロードされたときに、
    # フォームフィールドが正しく空になるか、デフォルト値が設定されます。
    form_values = {
        'free_word': '',
        'number_of_visitors': '',
        'number_of_visitors_op': '選んでださい',
        'number_of_answers': '',
        'number_of_answers_op': '選んでださい',
        'number_of_drop_ins': '',
        'number_of_drop_ins_op': '選んでださい',
        'abandonment': '',
        'abandonment_op': '選んでださい',
        'future_place': '',
        'future_place_op': '選んでださい',
        'new_event': '選んでださい',
        'event_name': '',
        'event_type': '選んでださい',
        'year': '',
        'year_op': '選んでください',
        'student_type': '選んでださい',
        'serch_mode': 'and' # デフォルトはAND検索
    }

    if request.method == 'GET':
        db = get_db()
        cursor = db.execute("SELECT * FROM EVENT")
        results = cursor.fetchall()
        # GETリクエストの場合、form_valuesをそのままテンプレートに渡す
        return render_template('opinion.html', results=results, **form_values)

    elif request.method == 'POST':
        # POSTリクエストの場合、フォームから値を取得し、form_valuesを更新
        form_values['free_word'] = request.form.get('free_word', '')
        form_values['number_of_visitors'] = request.form.get('number_of_visitors', '')
        form_values['number_of_visitors_op'] = request.form.get('number_of_visitors_op', '選んでださい')
        form_values['number_of_answers'] = request.form.get('number_of_answers', '')
        form_values['number_of_answers_op'] = request.form.get('number_of_answers_op', '選んでださい')
        form_values['number_of_drop_ins'] = request.form.get('number_of_drop_ins', '')
        form_values['number_of_drop_ins_op'] = request.form.get('number_of_drop_ins_op', '選んでださい')
        form_values['abandonment'] = request.form.get('abandonment', '')
        form_values['abandonment_op'] = request.form.get('abandonment_op', '選んでださい')
        form_values['future_place'] = request.form.get('future_place', '')
        form_values['future_place_op'] = request.form.get('future_place_op', '選んでださい')
        form_values['new_event'] = request.form.get('new_event', '選んでださい')
        form_values['event_name'] = request.form.get('event_name', '')
        form_values['event_type'] = request.form.get('event_type', '選んでださい')
        form_values['year'] = request.form.get('year', '')
        form_values['year_op'] = request.form.get('year_op', '選んでください')
        form_values['student_type'] = request.form.get('student_type', '選んでださい')
        form_values['serch_mode'] = request.form.get('serch_mode', 'and')

        # 検索条件を構築 (form_valuesの辞書から値を使用)
        conditions = []
        params = []

        def add_numeric_condition(field_name, value, operator):
            if value and value.isdigit():
                val_int = int(value)
                if operator == '回以上':
                    conditions.append(f"{field_name} >= ?")
                    params.append(val_int)
                elif operator == '回以下':
                    conditions.append(f"{field_name} <= ?")
                    params.append(val_int)
                elif operator == '回':
                    conditions.append(f"{field_name} = ?")
                    params.append(val_int)
                elif operator == '回以上を除く':
                    conditions.append(f"{field_name} < ?")
                    params.append(val_int)
                elif operator == '回以下を除く':
                    conditions.append(f"{field_name} > ?")
                    params.append(val_int)

        add_numeric_condition('come', form_values['number_of_visitors'], form_values['number_of_visitors_op'])
        add_numeric_condition('answer', form_values['number_of_answers'], form_values['number_of_answers_op'])
        add_numeric_condition('tobiiri', form_values['number_of_drop_ins'], form_values['number_of_drop_ins_op'])
        add_numeric_condition('kikenn', form_values['abandonment'], form_values['abandonment_op'])
        add_numeric_condition('notcome', form_values['future_place'], form_values['future_place_op'])

        if form_values['new_event'] == '◯':
            conditions.append("newevent = 1")
        elif form_values['new_event'] == '×':
            conditions.append("newevent = 0")

        # イベント名、年度の検索条件 (スキーマに合わせて調整)
        if form_values['event_name']: # もしDBにevent_nameカラムがあるなら
            conditions.append("event_name LIKE ?")
            params.append(f"%{form_values['event_name']}%")
        if form_values['year'] and form_values['year'].isdigit(): # もしDBにyear_valueカラムがあるなら
            conditions.append("year_value = ?")
            params.append(int(form_values['year']))

        if form_values['student_type'] == '一般生徒':
            conditions.append("student = 0")
        elif form_values['student_type'] == '執行委員':
            conditions.append("student = 1")
        elif form_values['student_type'] == '元執行委員':
            conditions.append("student = 2")

        # フリーワード検索 (既存のDBカラムに合わせるか、追加でカラムを用意)
        if form_values['free_word']:
            # ここでは例として come と answer カラムを検索対象にしています。
            # 実際のテキストカラム名に置き換えてください。
            conditions.append("(come LIKE ? OR answer LIKE ?)")
            params.extend([f"%{form_values['free_word']}%", f"%{form_values['free_word']}%"])


        query = "SELECT * FROM EVENT"
        if conditions:
            connector = " AND " if form_values['serch_mode'] == 'and' else " OR "
            query += " WHERE " + connector.join(conditions)

        db = get_db()
        try:
            cursor = db.execute(query, params)
            results = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            results = []

        # POSTリクエストの場合も、更新されたform_valuesをテンプレートに渡す
        return render_template('opinion.html', results=results, **form_values)

if __name__ == '__main__':
    # @app.before_first_request デコレーターを使うことで、
    # サーバー起動時に一度だけデータベースの初期化を試みます。
    # コマンドラインから直接実行する場合に便利です。
    app.run(debug=True)