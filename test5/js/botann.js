document.addEventListener('DOMContentLoaded', function () {
    // 検索ボタンの処理
    const searchButton = document.getElementById('search-button');
    searchButton.addEventListener('click', function (event) {
        event.preventDefault(); // フォームのデフォルト送信を防ぐ（もしフォーム内にある場合）
        console.log('検索ボタンがクリックされました！');
        // ここに検索処理のコードを書きます
        // 例: 検索クエリを取得してAPIに送信するなど
    });

    // リセットボタンの処理
    const resetButton = document.getElementById('reset-button');
    resetButton.addEventListener('click', function () {
        document.getElementById('free_word').value = ''; // 値を空にする
        document.getElementById('visitors').value = ''; // 値を空にする
        document.getElementById('answer').value = ''; // 値を空にする
        document.getElementById('drop').value = ''; // 値を空にする
        document.getElementById('abstention').value = ''; // 値を空にする
        document.getElementById('notcome').value = ''; // 値を空にする
        document.getElementById('new_event').value = ''; // 値を空にする
        document.getElementById('event_name_op').value = 'none'; // 値を空にする
        document.getElementById('event_date').value = 'none'; // 値を空にする
        document.getElementById('student_type').value = 'none'; // 値を空にする
        document.getElementById('search_mode').value = 'and'; // 値を空にする

        console.log('リセットボタンがクリックされました！');
        // ここにリセット処理のコードを書きます
        // 例: 検索フォームの入力欄をクリアする、表示されている検索結果を消すなど
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // ① HTML要素をJavaScriptで操作できるように取得
    const searchInput = document.getElementById('free_word'); // 検索入力欄
    const visitorsInput = document.getElementById('visitors'); // 来場者数入力欄
    const answerInput = document.getElementById('answer'); // 回答数入力   
    const dropInput = document.getElementById('drop'); // 飛び入り数入力欄
    const abstentionInput = document.getElementById('abstention'); // 棄権数入力欄
    const notcomeInput = document.getElementById('notcome'); // 欠席数入力欄
    const newEventInput = document.getElementById('new_event'); // 新規イベント入力欄
    const eventNameOpSelect = document.getElementById('event_name_op'); // イベント名オプション選択
    const eventDateSelect = document.getElementById('event_date'); // イベント日付選択
    const studentTypeSelect = document.getElementById('student_type'); // 学生タイプ選択
    const searchModeSelect = document.getElementById('search_mode'); // 検索モード選択
    const searchButton = document.getElementById('search-button'); // 検索ボタン
    const searchResultsDiv = document.getElementById('searchResults'); // 結果表示エリア

    // ② 検索ボタンがクリックされたときの処理を設定
    searchButton.addEventListener('click', async function () {
        const query = searchInput.value; // 入力されたキーワードを取得

        // キーワードが空だったら警告して終了
        if (query.trim() === '') {
            searchResultsDiv.innerHTML = '<p style="color: orange;">検索キーワードを入力してください。</p>';
            return;
        }

        // 検索中のメッセージを表示
        searchResultsDiv.innerHTML = '<p>検索中...</p>';

        try {
            // ③ サーバーのAPI（/search_items）にリクエストを送信
            // fetch()は、非同期でURLにアクセスしてデータを取得する機能
            // encodeURIComponent()は、日本語や特殊文字をURLで安全に送るための変換
            const response = await fetch(`/search_items?q=${encodeURIComponent(query)}`);

            // HTTPエラー（例: 404 Not Found, 500 Internal Server Error）が発生したかチェック
            if (!response.ok) {
                throw new Error(`サーバーエラー: ${response.status} ${response.statusText}`);
            }

            // ④ サーバーから返ってきたデータをJSON形式で解析
            const data = await response.json(); // 例: [{name: 'ペン', price: 120}, ...]

            // ⑤ 検索結果を表示エリアに反映
            searchResultsDiv.innerHTML = ''; // まず既存の結果をクリア

            if (data.length > 0) { // データがあれば表示
                const ul = document.createElement('ul'); // 箇条書きリストを作成
                data.forEach(item => { // データ一つ一つについて処理
                    const li = document.createElement('li'); // リストの項目を作成
                    li.textContent = `商品名: ${item.name}, 価格: ${item.price}円`;
                    ul.appendChild(li); // リストに項目を追加
                });
                searchResultsDiv.appendChild(ul); // 結果エリアにリストを追加
            } else { // データがなければ「見つかりませんでした」と表示
                searchResultsDiv.innerHTML = '<p>該当する商品が見つかりませんでした。</p>';
            }

        } catch (error) {
            // 通信や処理中にエラーが発生した場合
            console.error('データの取得中にエラーが発生しました:', error);
            searchResultsDiv.innerHTML = '<p style="color: red;">データの取得に失敗しました。</p>';
        }
    });
});