

// function toggleView(btn) {
//     // ボタンから見て一番近い投稿枠 (.ranference-post) を取得
//     const post = btn.closest('.ranference-post');
//     // その枠の中にある本文エリアを取得
//     const contentEl = post.querySelector('.posted-content');
    
//     if (!contentEl) return;

//     // 現在の状態をチェック
//     const isRaw = contentEl.getAttribute('data-is-raw') === 'true';
//     const rawData = contentEl.getAttribute('data-raw-content') || contentEl.textContent;

//     if (!isRaw) {
//         // --- Rawモードへ切り替え ---
//         contentEl.textContent = rawData; // タグを無効化して生文字を表示
//         contentEl.style.whiteSpace = 'pre-wrap';
//         contentEl.classList.remove('markdown-body');
        
//         contentEl.setAttribute('data-is-raw', 'true');
//         btn.textContent = 'Render'; // ボタン表示を「戻す」用に変更
//     } else {
//         // --- 元のレンダリングモードへ戻す ---
//         renderByCodingType(contentEl); // 定義済みの関数を再利用
        
//         contentEl.setAttribute('data-is-raw', 'false');
//         btn.textContent = 'Raw';
//     }
// }


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
