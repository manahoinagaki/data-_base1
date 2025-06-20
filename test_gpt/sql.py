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


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    # 初回アクセス時またはリセット時
    if request.method == 'GET':
        db = get_db()
        cursor = db.execute("SELECT * FROM EVENT")
        results = cursor.fetchall()
        return render_template('opinion.html', results=results)

    # フォームが送信された時 (POSTリクエスト)
    elif request.method == 'POST':
        # フォームデータを取得
        free_word = request.form.get('free_word')
        come_num = request.form.get('number_of_visitors')
        come_op = request.form.get('number_of_visitors_op') # 来場数の比較演算子
        answer_num = request.form.get('number_of_answers')
        answer_op = request.form.get('number_of_answers_op')
        tobiiri_num = request.form.get('number_of_drop_ins')
        tobiiri_op = request.form.get('number_of_drop_ins_op')
        kikenn_num = request.form.get('abandonment')
        kikenn_op = request.form.get('abandonment_op')
        notcome_num = request.form.get('future_place')
        notcome_op = request.form.get('future_place_op')
        new_event = request.form.get('new_event')
        event_type = request.form.get('event_type') # イベントタイプ
        year = request.form.get('year')
        student_type = request.form.get('student_type') # 生徒タイプ
        search_mode = request.form.get('serch_mode') # AND/OR検索

        # 検索条件を構築
        conditions = []
        params = []

        # 数値条件をヘルパー関数で追加
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

        add_numeric_condition('come', come_num, come_op)
        add_numeric_condition('answer', answer_num, answer_op)
        add_numeric_condition('tobiiri', tobiiri_num, tobiiri_op)
        add_numeric_condition('kikenn', kikenn_num, kikenn_op)
        add_numeric_condition('notcome', notcome_num, notcome_op)

        # 新イベントの条件
        if new_event == '◯':
            conditions.append("newevent = 1")
        elif new_event == '×':
            conditions.append("newevent = 0")

        # イベントタイプの条件 (ここではテキスト検索を想定、必要に応じてIDに変換)
        # 注意: EVENTテーブルに 'event_type' や 'year' カラムがないため、
        # このHTMLフォームの項目とDBスキーマを合わせる必要があります。
        # 今回は 'event' カラムがないため、この部分はコメントアウトまたは適宜修正が必要です。
        # 例: if event_type: conditions.append("event_type = ?"); params.append(event_type)

        # 生徒タイプの条件
        if student_type == '一般生徒':
            conditions.append("student = 0") # studentカラムが0が一般生徒、1が執行委員などと仮定
        elif student_type == '執行委員':
            conditions.append("student = 1")
        elif student_type == '元執行委員':
            conditions.append("student = 2") # 例えば2を元執行委員と仮定

        # フリーワード検索 (ここでは具体的なカラムがないため、仮の実装)
        # 実際には、複数のテキストカラムに対してLIKE検索を適用します。
        # 例: if free_word: conditions.append("(column1 LIKE ? OR column2 LIKE ?)"); params.extend([f'%{free_word}%', f'%{free_word}%'])

        query = "SELECT * FROM EVENT"
        if conditions:
            connector = " AND " if search_mode == 'and' else " OR "
            query += " WHERE " + connector.join(conditions)

        db = get_db()
        try:
            cursor = db.execute(query, params)
            results = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            results = [] # エラー時は空の結果を返す

        return render_template('opinion.html', results=results,
                                free_word=free_word,
                                number_of_visitors=come_num, number_of_visitors_op=come_op,
                                number_of_answers=answer_num, number_of_answers_op=answer_op,
                                number_of_drop_ins=tobiiri_num, number_of_drop_ins_op=tobiiri_op,
                                abandonment=kikenn_num, abandonment_op=kikenn_op,
                                future_place=notcome_num, future_place_op=notcome_op,
                                new_event=new_event,
                                event_type=event_type,
                                year=year,
                                student_type=student_type,
                                search_mode=search_mode) # フォームの入力値を保持して表示

if __name__ == '__main__':
    # データベースファイルが存在しない場合のみ初期化
    if not os.path.exists(DATABASE):
        print("データベースが存在しないため、初期化します...")
        init_db()
    else:
        print("データベースは既に存在します。")
    app.run(debug=True) # debug=True は開発用です。本番環境ではFalseにしてください。