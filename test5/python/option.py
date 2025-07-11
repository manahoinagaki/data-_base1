from flask import Flask, render_template, request, g, redirect, url_for, jsonify
import sqlite3
import csv
import os

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    # フォームのデフォルト値を設定
    # これが「リセット」されたときにフォームを空にするための初期値です。
    form_values = {
        'free_word': '',
        'number_of_visitors': '',
        'number_of_visitors_op': '選んでださい',
        # ... 他のフォーム要素も同様にデフォルト値を設定 ...
        'serch_mode': 'and' # デフォルトはAND検索
    }

    if request.method == 'GET':
        # GETリクエストの場合（初めてページを開いたときや「リセット」ボタンが押されたとき）
        # デフォルトのform_values（すべて空または初期値）をHTMLに渡します。
        # これにより、フォームがリセットされます。
        db = get_db()
        cursor = db.execute("SELECT * FROM EVENT")
        results = cursor.fetchall()
        return render_template('opinion.html', results=results, **form_values)

    elif request.method == 'POST':
        # POSTリクエストの場合（「検索」ボタンが押されたとき）
        # ブラウザから送られてきた値を受け取り、form_valuesを更新します。
        # これにより、検索後にフォームに元の入力値が維持されます。
        form_values['free_word'] = request.form.get('free_word', '')
        form_values['number_of_visitors'] = request.form.get('number_of_visitors', '')
        # ... 他のフォーム要素も request.form.get() で値を取得し、form_valuesを更新 ...

        # ここで、更新されたform_valuesを使ってSQLクエリを構築し、データベースからデータを取得します。
        conditions = []
        params = []
        # ... (検索ロジック: 前回のapp.pyの内容と同じ) ...

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

        # 検索結果と、ユーザーが入力した値で更新されたform_valuesをHTMLに渡します。
        return render_template('opinion.html', results=results, **form_values)