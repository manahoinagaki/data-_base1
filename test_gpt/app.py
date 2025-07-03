from flask import Flask, render_template, request, g, jsonify, redirect, url_for
import sqlite3
import csv
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
        print("データベーススキーマを初期化中...")
        # users テーブルの作成 (API用)
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        # EVENT テーブルの作成
        # 全ての検索条件に対応するカラムを含むスキーマ
        db.execute('''
            CREATE TABLE IF NOT EXISTS EVENT (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                location TEXT,
                description TEXT,
                date TEXT,
                number_of_visitors INTEGER, -- 来場者数 (previous 'come')
                answer INTEGER,             -- 回答数
                tobiiri INTEGER,            -- 飛び入り数
                kikenn INTEGER,             -- 危険数 (abandonment)
                notcome INTEGER,            -- 来ない数 (future_place)
                newevent INTEGER,           -- 新イベント (0:×, 1:◯)
                student INTEGER,            -- 生徒タイプ (0:一般生徒, 1:執行委員, 2:元執行委員)
                event_type TEXT,            -- イベントタイプ
                event_year INTEGER          -- イベント開催年 (previous 'year')
            )
        ''')
        db.commit()
        print("データベーススキーマの初期化が完了しました。")

        # サンプルデータの挿入 (EVENTテーブルが空の場合のみ)
        # CSVからデータを読み込むためのサンプルデータも追加
        cursor = db.execute("SELECT COUNT(*) FROM EVENT")
        if cursor.fetchone()[0] == 0:
            print("EVENTテーブルにサンプルデータを挿入中...")
            db.execute("INSERT INTO EVENT (event_name, location, description, date, number_of_visitors, answer, tobiiri, kikenn, notcome, newevent, student, event_type, event_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("Tech Conference 2024", "Tokyo", "Latest tech trends", "2024-10-20", 1500, 1200, 50, 10, 20, 1, 0, "Conference", 2024))
            db.execute("INSERT INTO EVENT (event_name, location, description, date, number_of_visitors, answer, tobiiri, kikenn, notcome, newevent, student, event_type, event_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("Art Exhibition", "Osaka", "Modern art showcase", "2024-11-15", 300, 250, 5, 2, 5, 0, 1, "Exhibition", 2024))
            db.execute("INSERT INTO EVENT (event_name, location, description, date, number_of_visitors, answer, tobiiri, kikenn, notcome, newevent, student, event_type, event_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("Local Food Festival", "Nagoya", "Local delicacies and music", "2025-01-25", 800, 750, 20, 5, 10, 1, 0, "Festival", 2025))
            db.execute("INSERT INTO EVENT (event_name, location, description, date, number_of_visitors, answer, tobiiri, kikenn, notcome, newevent, student, event_type, event_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("Student Gala", "Kyoto", "Annual student gathering", "2025-03-01", 100, 90, 2, 1, 0, 0, 2, "Party", 2025))
            db.commit()
            print("サンプルデータの挿入が完了しました。")

        # test.csvからのデータ挿入 (ファイルが存在し、まだデータがない場合のみ)
        # CSVのカラム名とDBのカラム名が一致するように仮定します。
        # 'come', 'answer', 'tobiiri', 'kikenn', 'notcome', 'newevent', 'student'
        # これらのカラムを 'event_name', 'location', 'description', 'date', 'number_of_visitors', 'event_type', 'event_year' とは別に定義しました。
        # CSVの列名とデータベースの列名を調整してください。
        # ここでは、CSVの列名がDBの列名と一致すると仮定しています。
        # 'come' -> 'number_of_visitors' にマッピングしています。
        if os.path.exists('test.csv'):
            try:
                # 既にデータが存在するか確認 (CSVからの重複挿入を防ぐ)
                cursor = db.execute("SELECT COUNT(*) FROM EVENT WHERE event_name IS NULL OR event_name = ''") # 仮のチェック
                if cursor.fetchone()[0] == 0: # もしCSVから挿入されたデータがなければ
                    with open('test.csv', 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for i, row in enumerate(reader):
                            # CSVのカラム名とDBのカラム名をマッピング
                            # CSVに存在しないカラムはデフォルト値やNoneを使用
                            try:
                                db.execute("INSERT INTO EVENT (event_name, location, description, date, number_of_visitors, answer, tobiiri, kikenn, notcome, newevent, student, event_type, event_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                        (row.get('event_name', f"CSV Event {i+1}"), # CSVにevent_nameがない場合のフォールバック
                                         row.get('location', ''),
                                         row.get('description', ''),
                                         row.get('date', 'Unknown'),
                                         int(row.get('come', 0)), # CSVの'come'をnumber_of_visitorsにマッピング
                                         int(row.get('answer', 0)),
                                         int(row.get('tobiiri', 0)),
                                         int(row.get('kikenn', 0)),
                                         int(row.get('notcome', 0)),
                                         1 if row.get('newevent') == '◯' else 0, # '◯'を1に変換
                                         int(row.get('student', 0)),
                                         row.get('event_type', ''),
                                         int(row.get('year', 0)) # CSVの'year'をevent_yearにマッピング
                                        ))
                            except ValueError as ve:
                                print(f"CSVデータの型変換エラー (行 {i+1}): {ve} - 行をスキップします: {row}")
                            except KeyError as ke:
                                print(f"CSVヘッダーに不足があります: {ke} - 行 {i+1} をスキップします: {row}")
                    db.commit()
                    print("CSVデータがデータベースに挿入されました。")
                else:
                    print("EVENTテーブルに既存のCSVデータがあるため、CSVからの挿入をスキップしました。")
            except FileNotFoundError:
                print("test.csvが見つかりませんでした。CSVからのデータ挿入をスキップします。")
            except sqlite3.IntegrityError:
                print("CSVデータに重複があるか、データが既に存在するため、CSVからの挿入をスキップしました。")
            except Exception as e:
                print(f"CSVデータ挿入中に予期せぬエラーが発生しました: {e}")
        else:
            print("test.csvが見つかりません。CSVからのデータ挿入は行われませんでした。")


# --- API エンドポイント (変更なし) ---

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
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


# --- イベント検索ページ ---

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    # フォームのデフォルト値を設定
    form_values = {
        'free_word': '',
        'number_of_visitors': '',
        'number_of_visitors_op': 'none', # 'none', 'gt', 'lt', 'eq'
        'number_of_answers': '',
        'number_of_answers_op': 'none',
        'number_of_drop_ins': '',
        'number_of_drop_ins_op': 'none',
        'abandonment': '',
        'abandonment_op': 'none',
        'future_place': '',
        'future_place_op': 'none',
        'new_event': 'any', # 'any', 'yes', 'no'
        'event_type': 'any', # 'any' or specific type
        'year': '',
        'year_op': 'none', # 'none', 'gt', 'lt', 'eq'
        'student_type': 'any', # 'any', 'general', 'executive', 'former_executive'
        'search_mode': 'and' # 'and' or 'or'
    }

    if request.method == 'POST':
        # フォームから送られてきた値を取得し、form_valuesを更新
        form_values['free_word'] = request.form.get('free_word', '')
        form_values['number_of_visitors'] = request.form.get('number_of_visitors', '')
        form_values['number_of_visitors_op'] = request.form.get('number_of_visitors_op', 'none')
        form_values['number_of_answers'] = request.form.get('number_of_answers', '')
        form_values['number_of_answers_op'] = request.form.get('number_of_answers_op', 'none')
        form_values['number_of_drop_ins'] = request.form.get('number_of_drop_ins', '')
        form_values['number_of_drop_ins_op'] = request.form.get('number_of_drop_ins_op', 'none')
        form_values['abandonment'] = request.form.get('abandonment', '')
        form_values['abandonment_op'] = request.form.get('abandonment_op', 'none')
        form_values['future_place'] = request.form.get('future_place', '')
        form_values['future_place_op'] = request.form.get('future_place_op', 'none')
        form_values['new_event'] = request.form.get('new_event', 'any')
        form_values['event_type'] = request.form.get('event_type', 'any')
        form_values['year'] = request.form.get('year', '')
        form_values['year_op'] = request.form.get('year_op', 'none')
        form_values['student_type'] = request.form.get('student_type', 'any')
        form_values['search_mode'] = request.form.get('search_mode', 'and')

        # デバッグ用: 受け取ったフォームデータを表示
        print(f"受け取ったフォームデータ: {form_values}")

        db = get_db()
        conditions = []
        params = []
        logical_operator = " AND " if form_values['search_mode'] == 'and' else " OR "

        # 数値条件を追加するヘルパー関数
        def add_numeric_condition(field_name, value, operator, target_conditions, target_params):
            if value and value.isdigit() and operator != 'none':
                val_int = int(value)
                if operator == 'gt':
                    target_conditions.append(f"{field_name} > ?")
                elif operator == 'lt':
                    target_conditions.append(f"{field_name} < ?")
                elif operator == 'eq':
                    target_conditions.append(f"{field_name} = ?")
                target_params.append(val_int)
                # 日本語オプションは未使用なので削除


        add_numeric_condition('number_of_visitors', form_values['number_of_visitors'], form_values['number_of_visitors_op'], conditions, params)
        add_numeric_condition('answer', form_values['number_of_answers'], form_values['number_of_answers_op'], conditions, params)
        add_numeric_condition('tobiiri', form_values['number_of_drop_ins'], form_values['number_of_drop_ins_op'], conditions, params)
        add_numeric_condition('kikenn', form_values['abandonment'], form_values['abandonment_op'], conditions, params)
        add_numeric_condition('notcome', form_values['future_place'], form_values['future_place_op'], conditions, params)
        add_numeric_condition('event_year', form_values['year'], form_values['year_op'], conditions, params) # イベント開催年

        # フリーワード検索
        if form_values['free_word']:
            search_words = form_values['free_word'].split()
            free_word_conditions = []
            for word in search_words:
                free_word_conditions.append("(event_name LIKE ? OR description LIKE ? OR location LIKE ?)")
                params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])
            if free_word_conditions:
                conditions.append(f"({' OR '.join(free_word_conditions)})") # フリーワードは常にOR

        # 新イベントの条件
        if form_values['new_event'] == 'yes':
            conditions.append("newevent = 1")
        elif form_values['new_event'] == 'no':
            conditions.append("newevent = 0")

        # イベントタイプの条件
        if form_values['event_type'] != 'any':
            conditions.append("event_type = ?")
            params.append(form_values['event_type'])

        # 生徒タイプの条件
        if form_values['student_type'] == 'general':
            conditions.append("student = 0")
        elif form_values['student_type'] == 'executive':
            conditions.append("student = 1")
        elif form_values['student_type'] == 'former_executive':
            conditions.append("student = 2")

        query = "SELECT * FROM EVENT"
        if conditions:
            query += " WHERE " + logical_operator.join(conditions)

        # デバッグ用: 構築されたSQLクエリとパラメータを表示
        print(f"実行されるSQLクエリ: {query}")
        print(f"パラメータ: {params}")

        try:
            cursor = db.execute(query, params)
            results = cursor.fetchall()
            results = [dict(row) for row in results] # 辞書のリストに変換
            print(f"検索結果の件数: {len(results)}")
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            results = [] # エラー時は空の結果を返す
            # 必要に応じてユーザーにエラーメッセージを表示
            # flash(f"検索中にエラーが発生しました: {e}", "error")

    else: # request.method == 'GET' (ページ初回ロード時)
        db = get_db()
        cursor = db.execute("SELECT * FROM EVENT")
        results = cursor.fetchall()
        results = [dict(row) for row in results]

    # 更新されたform_values（ユーザーが入力した値が含まれる）と検索結果をHTMLに渡す
    return render_template('opinion.html', results=results, **form_values)

if __name__ == '__main__':
    # データベースファイルが存在しない場合のみ初期化
    if not os.path.exists(DATABASE):
        print(f"データベースファイル '{DATABASE}' が存在しないため、初期化します...")
        init_db()
    else:
        print(f"データベースファイル '{DATABASE}' は既に存在します。")
        # 既存のDBでカラムが足りない場合のために、起動時にスキーマ更新を試みる (開発時のみ有効化推奨)
        # with app.app_context():
        #     db = get_db()
        #     db.execute("ALTER TABLE EVENT ADD COLUMN IF NOT EXISTS answer INTEGER")
        #     db.execute("ALTER TABLE EVENT ADD COLUMN IF NOT EXISTS tobiiri INTEGER")
        #     db.execute("ALTER TABLE EVENT ADD COLUMN IF NOT EXISTS kikenn INTEGER")
        #     db.execute("ALTER TABLE EVENT ADD COLUMN IF NOT EXISTS notcome INTEGER")
        #     db.execute("ALTER TABLE EVENT ADD COLUMN IF NOT EXISTS newevent INTEGER")
        #     db.execute("ALTER TABLE EVENT ADD COLUMN IF NOT EXISTS student INTEGER")
        #     db.execute("ALTER TABLE EVENT ADD COLUMN IF NOT EXISTS event_type TEXT")
        #     db.execute("ALTER TABLE EVENT ADD COLUMN IF NOT EXISTS event_year INTEGER")
        #     db.commit()
        #     print("既存データベースのスキーマ更新を試みました。")

    app.run(debug=True, port=5000) # debug=True は開発用です。本番環境ではFalseにしてください。