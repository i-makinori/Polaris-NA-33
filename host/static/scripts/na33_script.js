
function formatLocalTime(el) {
    // UTC文字列をブラウザのローカル日時に変換して整形する
    // @param {HTMLElement} el - 対象のDOM要素

    const utcStr = el.getAttribute('data-utc');

    if (!utcStr) return;
    
    const date = new Date(utcStr + 'Z'); 

    // ブラウザ設定に合わせた日時文字列
    const localTime = date.toLocaleString(undefined, {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });

    // タイムゾーンオフセットの計算
    const offset = -date.getTimezoneOffset();
    const sign = offset >= 0 ? '+' : '-';
    const hours = String(Math.floor(Math.abs(offset) / 60)).padStart(2, '0');
    const minutes = String(Math.abs(offset) % 60).padStart(2, '0');

    el.textContent = `(${localTime} (${sign}${hours}${minutes} 換算))`;
}

function renderByCodingType(el) {
    //* 要素の data-coding-type 属性に応じて、コンテンツを適切に描画する
    // @param {HTMLElement} el - 対象のDOM要素

    const type = el.getAttribute('data-coding-type');

    if (type === 'text') {
        // 'text' 形式: ほとんど、何もしない（ブラウザのデフォルト表示に任せる）が、
        // ;
        // 必要に応じて改行を有効にするためのスタイル付与のみ行う。
        el.style.whiteSpace = 'pre-wrap'; // 'pre-wrap': textをそのまま(白字や改行もそのまま表示。)
    } else if (type === 'markdown') {
        const raw = el.textContent;
        // 'Markdown' 形式: HTMLに変換。
        el.innerHTML = marked.parse(raw);
        el.classList.add('markdown-body');
    } // else { ... } 将来の拡張用 latex とか javascript とか、、、。
}


document.addEventListener('DOMContentLoaded', () => {

    // 1. タイムゾーンの変換処理
    const timeElements = document.querySelectorAll('.posted-time');
    timeElements.forEach(formatLocalTime);

    // 2. コーディングタイプに応じた描画処理
    const postedContents = document.querySelectorAll('.posted-content');
    postedContents.forEach(renderByCodingType);
});
