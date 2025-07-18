//    const sqlite3 = require('sqlite3').verbose();
//    const dbPath = 'your_database.db'; // データベースファイルへのパス
//    const tableName = 'your_table'; // 表示したいテーブル名

//    // データベース接続
//    const db = new sqlite3.Database(dbPath, (err) => {
//        if (err) {
//            console.error(err.message);
//            return;
//        }
//        console.log('Connected to the SQLite database.');
//    });

//    // テーブルデータの取得
//    db.all(`SELECT * FROM ${tableName}`, [], (err, rows) => {
//        if (err) {
//            throw err;
//        }
//        // HTMLテーブルの作成
//        let tableHtml = '<table>';
//        if (rows.length > 0) {
//            // ヘッダー行
//            tableHtml += '<thead><tr>';
//            for (const key in rows[0]) {
//                tableHtml += `<th>${key}</th>`;
//            }
//            tableHtml += '</tr></thead>';

//            // データ行
//            tableHtml += '<tbody>';
//            rows.forEach((row) => {
//                tableHtml += '<tr>';
//                for (const key in row) {
//                    tableHtml += `<td>${row[key]}</td>`;
//                }
//                tableHtml += '</tr>';
//            });
//            tableHtml += '</tbody>';
//        } else {
//            tableHtml += '<tr><td>No data found</td></tr>';
//        }
//        tableHtml += '</table>';

//        // HTMLにテーブルを挿入
//        document.getElementById('table-container').innerHTML = tableHtml;

//        // データベース接続を閉じる
//        db.close((err) => {
//            if (err) {
//                console.error(err.message);
//            }
//            console.log('Closed the database connection.');
//        });
//    });

//    // HTMLの読み込みが完了したら実行する
//         document.addEventListener('DOMContentLoaded', function() {
//             // JavaScriptが操作するHTML要素を取得
//             // ここでIDが間違っていると「Cannot set properties of null」エラーになります
//             const searchInput = document.getElementById('searchInput');
//             const searchButton = document.getElementById('searchButton');
//             const searchResultsDiv = document.getElementById('searchResults'); // これがエラーの原因だった箇所！

//             // 検索ボタンがクリックされたときの処理
//             searchButton.addEventListener('click', async function() {
//                 const query = searchInput.value; // 入力されたキーワードを取得

//                 // キーワードが空の場合はメッセージを表示して処理を中断
//                 if (query.trim() === '') {
//                     searchResultsDiv.innerHTML = '<p style="color: orange;">検索キーワードを入力してください。</p>';
//                     return;
//                 }

//                 // 検索中のメッセージを表示
//                 searchResultsDiv.innerHTML = '<p>検索中...</p>';

//                 try {
//                     // サーバーのAPIエンドポイントにリクエストを送信
//                     // `/search_items?q=キーワード` の形式でデータを送ります
//                     const response = await fetch(`/search_items?q=${encodeURIComponent(query)}`);

//                     // HTTPステータスコードが200番台以外の場合（例: 404, 500）はエラーとして処理
//                     if (!response.ok) {
//                         throw new Error(`サーバーエラーが発生しました: ${response.status} ${response.statusText}`);
//                     }

//                     // レスポンスのデータをJSON形式で解析
//                     const data = await response.json();

//                     // 検索結果の表示を更新
//                     searchResultsDiv.innerHTML = ''; // まず、以前の結果をクリア

//                     if (data.length > 0) { // データがある場合
//                         const ul = document.createElement('ul'); // 新しいリスト要素を作成
//                         data.forEach(item => { // 各検索結果をリストアイテムとして追加
//                             const li = document.createElement('li');
//                             li.innerHTML = `<strong>${item.name}</strong> - ${item.price}円`;
//                             ul.appendChild(li);
//                         });
//                         searchResultsDiv.appendChild(ul); // リストを結果表示エリアに追加
//                     } else { // データが見つからなかった場合
//                         searchResultsDiv.innerHTML = '<p>該当する商品が見つかりませんでした。</p>';
//                     }

//                 } catch (error) {
//                     // ネットワークエラーやJSON解析エラーなど、予期せぬエラーが発生した場合
//                     console.error('データの取得中にエラーが発生しました:', error);
//                     searchResultsDiv.innerHTML = '<p style="color: red;">データの取得に失敗しました。後でもう一度お試しください。</p>';
//                 }
//             });
//         });