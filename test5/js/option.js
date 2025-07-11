   const sqlite3 = require('sqlite3').verbose();
   const dbPath = 'your_database.db'; // データベースファイルへのパス
   const tableName = 'your_table'; // 表示したいテーブル名

   // データベース接続
   const db = new sqlite3.Database(dbPath, (err) => {
       if (err) {
           console.error(err.message);
           return;
       }
       console.log('Connected to the SQLite database.');
   });

   // テーブルデータの取得
   db.all(`SELECT * FROM ${tableName}`, [], (err, rows) => {
       if (err) {
           throw err;
       }
       // HTMLテーブルの作成
       let tableHtml = '<table>';
       if (rows.length > 0) {
           // ヘッダー行
           tableHtml += '<thead><tr>';
           for (const key in rows[0]) {
               tableHtml += `<th>${key}</th>`;
           }
           tableHtml += '</tr></thead>';

           // データ行
           tableHtml += '<tbody>';
           rows.forEach((row) => {
               tableHtml += '<tr>';
               for (const key in row) {
                   tableHtml += `<td>${row[key]}</td>`;
               }
               tableHtml += '</tr>';
           });
           tableHtml += '</tbody>';
       } else {
           tableHtml += '<tr><td>No data found</td></tr>';
       }
       tableHtml += '</table>';

       // HTMLにテーブルを挿入
       document.getElementById('table-container').innerHTML = tableHtml;

       // データベース接続を閉じる
       db.close((err) => {
           if (err) {
               console.error(err.message);
           }
           console.log('Closed the database connection.');
       });
   });