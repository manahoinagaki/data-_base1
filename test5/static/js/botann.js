document.addEventListener('DOMContentLoaded', function () {
    const searchButton = document.getElementById('search-button');
    const resetButton = document.getElementById('reset-button');
    // 検索結果表示エリアの要素を正しく取得
    const searchResultsDiv = document.getElementById('search-results'); 

    // 検索フォーム要素の取得（省略、前の回答を参照）
    const searchForm = document.getElementById('search-form');

    // 検索ボタンがクリックされたときの処理
    searchButton.addEventListener('click', async function (event) {
        event.preventDefault();

        const formData = new FormData(searchForm);
        const params = new URLSearchParams();

        for (let [key, value] of formData.entries()) {
            if (value && value !== 'none' && value !== 'all') { // 'none'/'all'は送信しない
                params.append(key, value);
            } else if (key === 'free_word' && value) { // フリーワードは空文字列でも送る
                 params.append(key, value);
            }
        }
        
        searchResultsDiv.innerHTML = '<p>検索中...</p>'; // 検索中メッセージ

        try {
            const response = await fetch(`/search_items?${params.toString()}`);

            if (!response.ok) {
                throw new Error(`サーバーエラーが発生しました: ${response.status} ${response.statusText}`);
            }

            const data = await response.json(); // ここでJSONデータを受け取る

            searchResultsDiv.innerHTML = ''; // 以前の結果をクリア

            if (data.length > 0) {
                const ul = document.createElement('ul'); // 検索結果をリスト形式で表示
                data.forEach(item => {
                    const li = document.createElement('li');
                    // ここで、受け取ったJSONデータの各項目を整形して表示します
                    // 例: 商品名と価格だけ表示する場合
                    // li.textContent = `商品名: ${item.name}, 価格: ${item.price}円`;

                    // 今回のフォーム項目に合わせて表示をカスタマイズ
                    // item オブジェクトのキーが、データベースのカラム名と一致することを確認してください
                    let displayHtml = `
                        <strong>ID: ${item.id}</strong><br>
                        フリーワード: ${item.free_word || 'N/A'}<br>
                        来場数: ${item.visitors || 'N/A'} ${item.visitors_op || ''}<br>
                        回答数: ${item.answer || 'N/A'} ${item.answer_op || ''}<br>
                        飛び入り数: ${item.drop_count || 'N/A'} ${item.drop_op || ''}<br>
                        棄権: ${item.abstention || 'N/A'} ${item.abstention_op || ''}<br>
                        未来場: ${item.notcome || 'N/A'} ${item.notcome_op || ''}<br>
                        新イベント: ${item.new_event_op === 'ok' ? '○' : item.new_event_op === 'nt' ? '×' : 'N/A'}<br>
                        イベント名: ${item.event_name_op || 'N/A'}<br>
                        年度: ${item.event_date || 'N/A'}<br>
                        学生: ${item.student_type || 'N/A'}
                    `;
                    li.innerHTML = displayHtml; // HTMLとして挿入
                    ul.appendChild(li);
                });
                searchResultsDiv.appendChild(ul);
            } else {
                searchResultsDiv.innerHTML = '<p>該当する項目が見つかりませんでした。</p>';
            }

        } catch (error) {
            console.error('データの取得中にエラーが発生しました:', error);
            searchResultsDiv.innerHTML = '<p style="color: red;">データの取得に失敗しました。後でもう一度お試しください。</p>';
        }
    });
    // リセットボタンの処理
    resetButton.addEventListener('click', function () {
        // 各入力フィールドの値をクリア
        freeWordInput.value = '';
        visitorsInput.value = '';
        answerInput.value = '';
        dropInput.value = '';
        abstentionInput.value = '';
        notcomeInput.value = '';

        // select要素は最初のoption（value="none" や "all"）を選択状態にする
        visitorsOpSelect.value = 'none';
        answerOpSelect.value = 'none';
        dropOpSelect.value = 'none';
        abstentionOpSelect.value = 'none';
        notcomeOpSelect.value = 'none';
        newEventOpSelect.value = 'none';
        eventNameOpSelect.value = 'all'; // イベント名は'all'が初期値
        studentTypeSelect.value = 'none';

        // 日付入力は空文字列に
        eventDateInput.value = '';

        // ラジオボタンのデフォルト値（AND検索）を選択状態にする
        searchModeAnd.checked = true;

        // 検索結果表示エリアもクリア
        searchResultsDiv.innerHTML = '<p>検索結果はまだありません。</p>';

        console.log('リセットボタンがクリックされました！');
    });
});