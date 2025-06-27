fetch('/api/users')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));

function search() {
  const free_word = document.getElementById('free_word').value;
  const number_of_visitors = document.getElementById('number_of_visitors').value;
  const number_of_answers = document.getElementById('number_of_answers').value;
  const number_of_drop_ins = document.getElementById('number_of_drop_ins').value;
  const abandonment = document.getElementById('abandonment').value;
  const future_place = document.getElementById('future_place').value;
  const event = document.getElementById('event').value;
  const year = document.getElementById('year').value;

  // 空の場合は何も表示しない
  if (free_word === "" && number_of_visitors === "" && number_of_answers === "" && number_of_drop_ins === "" && abandonment === "" && future_place === "" && event === "" && year === "") {
    resultsContainer.innerHTML = "";
    return;
  }

  // Ajaxで検索を実行
  const xhr = new XMLHttpRequest();
  xhr.open('GET', '/search?q=' + encodeURIComponent(free_word)); // 検索APIのエンドポイント
  xhr.onload = function() {
    if (xhr.status === 200) {
      resultsContainer.innerHTML = xhr.responseText; // 検索結果をHTMLで表示
    } else {
      resultsContainer.innerHTML = '検索エラー';
    }
  };
  xhr.send();
}

// 入力フィールドにイベントリスナーを追加
document.getElementById('searchInput').addEventListener('input', search);