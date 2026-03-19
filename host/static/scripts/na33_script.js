
// # markdown-it texmath

// md (markdown-it) instance
let md;

function initMarkdown() {
    if (window.markdownit && window.texmath && window.katex) {
        md = window.markdownit({
            html: true,
            linkify: true
        }).use(window.texmath, {
            engine: window.katex,
            delimiters: ['beg_end', 'brackets', 'dollars'],
            katexOptions: { strict: false }
        });

        console.log("Texmath loaded successfully");
    }
    return md;
}

// # ranferences , tolopica_show , ...

function renderAsText(el, raw_text){
    el.textContent = raw_text;
    el.classList.remove('markdown-body'); // and remove additional body classes
    el.style.whiteSpace = 'pre-wrap';
}

function renderAsMarkDown(el, raw_text) {
    // 描画実行
    el.innerHTML = md.render(raw_text);
    
    // スタイル調整
    el.classList.add('markdown-body');
    el.style.whiteSpace = 'normal';
    
    // ※ renderMathInElement は不要です（md.render 内で完了しています）
}


function toggleView(btn) {
    // ボタンにより、表示方法を変更する。 markdown や text など。
    // element の取得
    const post_container = btn.closest('.ranference-post');
    const content_el = post_container.querySelector('.posted-content');
    
    if (!content_el) return;

    // 現在の状態を確認（属性がなければ false とみなす）
    const is_raw = content_el.getAttribute('data-is-raw') === 'true';
    // 属性から生データを取得
    const raw_text = content_el.getAttribute('data-raw-content');

    if (!is_raw) {
        // --- Text表示 モード へ ---
        renderAsText(content_el, raw_text)
        
        content_el.setAttribute('data-is-raw', 'true');
        btn.textContent = 'Render'; // 次に押すと整形表示に戻ることを示す
    } else {
        // --- レンダリングモードへ戻す ---
        renderPostedContentByCodingType(content_el);
        // renderAsMarkDown(content_el, raw_text)
        
        content_el.setAttribute('data-is-raw', 'false');
        btn.textContent = 'Text表示'; // 次に押すと生データ表示になることを示す
    }
}


// ## reRender

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


function renderPostedContentByCodingType(el) {
    // conding-type 毎に表示方法を変更
    // markdown形式 や text形式 など。
    
    const type = el.getAttribute('data-coding-type');
    const raw_text = el.getAttribute('data-raw-content');

    if (type === 'text') {
        renderAsText(el, raw_text);
    } else if (type === 'markdown') {
        renderAsMarkDown(el, raw_text);
    } // else // 拡張用 latex とか HTML とか
}

// # After Load

document.addEventListener('DOMContentLoaded', () => {

    md = initMarkdown();

    // 1. タイムゾーンの変換処理
    const timeElements = document.querySelectorAll('.posted-time');
    timeElements.forEach(formatLocalTime);

    // 2. コーディングタイプに応じた描画処理
    const postedContents = document.querySelectorAll('.posted-content');
    postedContents.forEach(renderPostedContentByCodingType);
});
