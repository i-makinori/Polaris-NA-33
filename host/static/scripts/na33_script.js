
function toggleView(btn) {
    // ボタンにより、表示方法を変更する。 markdown や text など。
    
    const postContainer = btn.closest('.ranference-post');
    const contentEl = postContainer.querySelector('.posted-content');
    
    if (!contentEl) return;

    // 現在の状態を確認（属性がなければ false とみなす）
    const isRaw = contentEl.getAttribute('data-is-raw') === 'true';
    // 属性から生データを取得（最優先）、なければ現在のテキスト
    const rawData = contentEl.getAttribute('data-raw-content') || contentEl.textContent;

    if (!isRaw) {
        // --- Rawモード (Text表示) へ ---
        contentEl.textContent = rawData; 
        contentEl.style.whiteSpace = 'pre-wrap';
        contentEl.classList.remove('markdown-body');
        
        contentEl.setAttribute('data-is-raw', 'true');
        btn.textContent = 'Render'; // 次に押すと整形表示に戻ることを示す
    } else {
        // --- レンダリングモードへ戻す ---
        renderByCodingType(contentEl); 
        
        contentEl.setAttribute('data-is-raw', 'false');
        btn.textContent = 'Text表示'; // 次に押すと生データ表示になることを示す
    }
}

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
    // conding-type 毎に表示方法を変更
    // markdown形式 や text形式 など。
    
    const type = el.getAttribute('data-coding-type');
    
    // 常に属性に隠した「生データ」を優先的に使う
    // これにより、innerHTMLが書き換わった後でも正しく再レンダリングできる
    const raw = el.getAttribute('data-raw-content') || el.textContent;

    if (type === 'text') {
        el.textContent = raw; 
        el.style.whiteSpace = 'pre-wrap';
        el.classList.remove('markdown-body');
    } else if (type === 'markdown') {
        // marked.parse に渡すのは常に「生」のデータ
        el.innerHTML = marked.parse(raw);
        el.classList.add('markdown-body');
        // Markdown時はブラウザの通常の折り返しルールに任せる
        el.style.whiteSpace = 'normal';
    } // else // 拡張用 latex とか HTML とか
}

document.addEventListener('DOMContentLoaded', () => {

    // 1. タイムゾーンの変換処理
    const timeElements = document.querySelectorAll('.posted-time');
    timeElements.forEach(formatLocalTime);

    // 2. コーディングタイプに応じた描画処理
    const postedContents = document.querySelectorAll('.posted-content');
    postedContents.forEach(renderByCodingType);
});
