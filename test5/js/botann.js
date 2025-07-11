document.addEventListener('DOMContentLoaded', function() {
    // 検索ボタンの処理
    const searchButton = document.getElementById('search-button');
    searchButton.addEventListener('click', function(event) {
        event.preventDefault(); // フォームのデフォルト送信を防ぐ（もしフォーム内にある場合）
        console.log('検索ボタンがクリックされました！');
        // ここに検索処理のコードを書きます
        // 例: 検索クエリを取得してAPIに送信するなど
    });

    // リセットボタンの処理
    const resetButton = document.getElementById('reset-button');
    resetButton.addEventListener('click', function(event) {
        event.preventDefault(); // フォームのデフォルト送信を防ぐ（もしフォーム内にある場合）
        console.log('リセットボタンがクリックされました！');
        // ここにリセット処理のコードを書きます
        // 例: 検索フォームの入力欄をクリアする、表示されている検索結果を消すなど
    });
});