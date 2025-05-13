// numberに飛ぶ
const move = () => {
    window.location.href = "file:///c%3A/Users/T24091/OneDrive%20-%20%E6%84%9B%E7%9F%A5%E5%B7%A5%E6%A5%AD%E5%A4%A7%E5%AD%A6/%E3%82%A2%E3%83%97%E3%83%AA%E9%96%8B%E7%99%BA/data-_base1/test2/templates/number.html";
}
console.log("hoge")

// 戻る
const back = () => {
    document.cookie = "username=back; max-age=3600; path=/; SameSite=None; Secure";
}
console.log("back")
