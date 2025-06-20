// ここにJavaScriptコードを記述します

// 例: ページがロードされたときに何かを実行する場合
document.addEventListener('DOMContentLoaded', function() {
    console.log('ページが完全に読み込まれました。');

    // リセットボタンのクリックイベントを監視する例
    const resetButton = document.querySelector('input[type="submit"][value="リセット"]');
    if (resetButton) {
        resetButton.addEventListener('click', function(event) {
            // ここにリセット時の追加のJavaScript処理を書くことができます
            // 例えば、フォームのフィールドをすべてクリアするなど
            // event.preventDefault(); // デフォルトのフォーム送信をキャンセルしたい場合
            console.log('リセットボタンがクリックされました。');
        });
    }

    // フォーム送信前にバリデーションを行う例 (オプション)
    const searchForm = document.querySelector('form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            // 例: フリーワードが空でないことを確認
            // const freeWordInput = document.querySelector('input[name="free_word"]');
            // if (freeWordInput && freeWordInput.value.trim() === '') {
            //     alert('フリーワードを入力してください。');
            //     event.preventDefault(); // フォーム送信をキャンセル
            // }

            console.log('フォームが送信されました。');
        });
    }
});