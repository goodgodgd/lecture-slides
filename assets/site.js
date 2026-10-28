// 밝기 선택. 세 단이다 — 자동(시스템을 따름) · 밝게 · 어둡게.
// 깜빡임을 막는 초기화는 각 페이지 <head> 안의 한 줄이 먼저 한다.
(function () {
  var KEY = 'theme';
  function apply(mode) {
    if (mode === 'auto') delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = mode;
    try { mode === 'auto' ? localStorage.removeItem(KEY) : localStorage.setItem(KEY, mode); }
    catch (e) { /* 시크릿 창 등 저장이 막힌 경우 — 이번 방문에만 적용된다 */ }
    document.querySelectorAll('[data-theme-switch] button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.mode === mode));
    });
  }
  function current() {
    try { return localStorage.getItem(KEY) || 'auto'; } catch (e) { return 'auto'; }
  }
  function init() {
    document.querySelectorAll('[data-theme-switch]').forEach(function (seg) {
      seg.addEventListener('click', function (e) {
        var b = e.target.closest('button[data-mode]');
        if (b) apply(b.dataset.mode);
      });
    });
    apply(current());
  }
  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', init)
    : init();
})();

// 프롬프트 상자의 「복사」 버튼. 자료 페이지마다 같은 함수가 들어 있던 것을 여기로 모았다.
// 상자 안의 문구만 복사한다 — 「🤖 그대로 복사해서 쓰세요」는 CSS 가 그리는 것이라 따라오지 않는다.
function copyPrompt(btn) {
  var box = btn.parentElement.cloneNode(true);
  var b = box.querySelector('button');
  if (b) b.remove();
  navigator.clipboard.writeText(box.textContent.trim()).then(function () {
    var old = btn.textContent;
    btn.textContent = '복사됨';
    setTimeout(function () { btn.textContent = old; }, 1200);
  });
}

// 서식판 보고서 양식의 「복사」 버튼. 워드·한글에 붙이면 제목·표가 서식째 들어가도록 text/html 로 복사한다.
// 화면의 색(어두운 테마)이 따라가지 않게 검은 글자·흰 바탕의 HTML 을 새로 만들고,
// 화면에서 h3·h4·h5 로 쓴 제목은 문서의 제목 1·2·3 으로 올린다.
function copyRich(btn) {
  var src = btn.parentElement.querySelector('.richform');
  if (!src) return;
  var box = src.cloneNode(true);
  var LEVEL = { H3: 'h1', H4: 'h2', H5: 'h3' };
  box.querySelectorAll('h3, h4, h5').forEach(function (h) {
    var n = document.createElement(LEVEL[h.tagName]);
    n.innerHTML = h.innerHTML;
    h.replaceWith(n);
  });
  box.querySelectorAll('table').forEach(function (t) {
    var slot = t.classList.contains('slot'), code = t.classList.contains('code');
    t.setAttribute('border', '1');
    t.style.cssText = 'border-collapse:collapse;width:100%';
    t.querySelectorAll('th, td').forEach(function (c) {
      c.style.cssText += ';border:1px solid #000;padding:4pt 6pt;vertical-align:top;text-align:left' +
        (c.tagName === 'TH' ? ';background:#eee' : '') +
        (slot ? ';height:48pt;color:#888' : '') + (code ? ';font-family:Consolas,monospace' : '');
    });
  });
  box.querySelectorAll('[class]').forEach(function (e) { e.removeAttribute('class'); });
  var html = '<div style="color:#000;background:#fff">' + box.innerHTML + '</div>';
  function done() {
    var old = btn.textContent;
    btn.textContent = '복사됨';
    setTimeout(function () { btn.textContent = old; }, 1200);
  }
  function fallback() {   // ClipboardItem 이 없는 브라우저 — 화면 밖에 잠깐 놓고 선택해 복사한다
    var tmp = document.createElement('div');
    tmp.innerHTML = html;
    tmp.style.cssText = 'position:fixed;left:-9999px;top:0';
    document.body.appendChild(tmp);
    var r = document.createRange(), sel = window.getSelection();
    r.selectNodeContents(tmp);
    sel.removeAllRanges();
    sel.addRange(r);
    try { if (document.execCommand('copy')) done(); }
    finally { sel.removeAllRanges(); tmp.remove(); }
  }
  if (window.ClipboardItem && navigator.clipboard && navigator.clipboard.write) {
    navigator.clipboard.write([new ClipboardItem({
      'text/html': new Blob([html], { type: 'text/html' }),
      'text/plain': new Blob([box.textContent], { type: 'text/plain' })
    })]).then(done, fallback);
  } else fallback();
}

// 📄 전체 코드 상자의 「복사」 버튼. 같은 .codefile 안의 <pre> 내용만 복사한다.
function copyCode(btn) {
  var pre = btn.parentElement.querySelector('pre');
  if (!pre) return;
  navigator.clipboard.writeText(pre.textContent.replace(/\s+$/, '') + '\n').then(function () {
    var old = btn.textContent;
    btn.textContent = '복사됨';
    setTimeout(function () { btn.textContent = old; }, 1200);
  });
}

// 코드 색상. pre.lang-cpp / lang-cmake / lang-sh / lang-py / lang-matlab 안의 <code> 에 .hl-* span 을 붙인다.
// 외부 라이브러리 없이 정규식으로 토큰을 나눈다. 색은 site.css 의 --hl-* 토큰이라 밝기를 따라간다.
// 언어 클래스는 robotics/src/tag_lang.py(본문 조각)와 expand_fullcode.py(📄 상자)가 붙인다.
(function () {
  function esc(t) { return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  var CPP_KW = 'alignas|auto|bool|break|case|catch|char|class|const|constexpr|const_cast|continue|default|delete|do|double|dynamic_cast|else|enum|explicit|export|extern|false|final|float|for|friend|goto|if|inline|int|long|mutable|namespace|new|noexcept|nullptr|operator|override|private|protected|public|reinterpret_cast|return|short|signed|sizeof|static|static_cast|struct|switch|template|this|throw|true|try|typedef|typename|union|unsigned|using|virtual|void|volatile|while';
  var M_KW = 'break|case|catch|classdef|continue|else|elseif|end|for|function|global|if|otherwise|parfor|persistent|return|switch|try|while';
  var PY_KW = 'and|as|assert|async|await|break|class|continue|def|del|elif|else|except|False|finally|for|from|global|if|import|in|is|lambda|None|nonlocal|not|or|pass|raise|return|True|try|while|with|yield';
  var RULES = {
    'lang-cpp': [
      [/\/\/[^\n]*|\/\*[\s\S]*?\*\//y, 'hl-cmt'],
      [/"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'/y, 'hl-str'],
      [/#[ \t]*\w+[^\n]*/y, 'hl-pre'],
      [/\b\d+(?:\.\d+)?(?:e[+-]?\d+)?[fFuUlL]*\b/y, 'hl-num'],
      [new RegExp('\\b(?:' + CPP_KW + ')\\b', 'y'), 'hl-kw'],
      [/\b[A-Za-z_]\w*(?=::)/y, 'hl-ns'],
      [/\b[A-Z][A-Za-z0-9_]*\b/y, 'hl-type'],
      [/\b[a-z_]\w*(?=\s*\()/y, 'hl-fn']
    ],
    'lang-cmake': [
      [/#[^\n]*/y, 'hl-cmt'],
      [/"(?:[^"\\\n]|\\.)*"/y, 'hl-str'],
      [/\$\{[^}]*\}/y, 'hl-ns'],
      [/\b[A-Z][A-Z0-9_]+\b/y, 'hl-kw'],
      [/\b\d+(?:\.\d+)*\b/y, 'hl-num'],
      [/\b[a-z_]\w*(?=\s*\()/y, 'hl-fn']
    ],
    // MATLAB — 작은따옴표는 문자열일 수도, 전치(A')일 수도 있다. 앞 글자가 이름·괄호·따옴표·점이면 전치로 본다
    'lang-matlab': [
      [/%%[^\n]*/y, 'hl-sec'],
      [/%[^\n]*/y, 'hl-cmt'],
      [/(?<![\w)\]}'.])'(?:[^'\n]|'')*'|"(?:[^"\n]|"")*"/y, 'hl-str'],
      [/\b\d+(?:\.\d+)?(?:e[+-]?\d+)?[ij]?\b/y, 'hl-num'],
      [new RegExp('\\b(?:' + M_KW + ')\\b', 'y'), 'hl-kw'],
      [/\b[A-Za-z_]\w*(?=\()/y, 'hl-fn']
    ],
    'lang-py': [
      [/#[^\n]*/y, 'hl-cmt'],
      [/"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'/y, 'hl-str'],
      [/\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b/y, 'hl-num'],
      [new RegExp('\\b(?:' + PY_KW + ')\\b', 'y'), 'hl-kw'],
      [/\b[A-Z][A-Za-z0-9_]*\b/y, 'hl-type'],
      [/\b[a-z_]\w*(?=\s*\()/y, 'hl-fn']
    ]
  };
  var WORD = /[A-Za-z0-9_]/;
  function tokenize(text, rules) {
    var out = '', i = 0, n = text.length;
    while (i < n) {
      var hit = null, cls = null;
      // 낱말 한가운데서 시작하지 않게 한다 (예: "my_const" 안의 const)
      var atWordStart = !(i > 0 && WORD.test(text[i - 1]) && WORD.test(text[i]));
      if (atWordStart) {
        for (var r = 0; r < rules.length; r++) {
          var re = rules[r][0]; re.lastIndex = i;
          var m = re.exec(text);
          if (m && m.index === i && m[0].length) { hit = m[0]; cls = rules[r][1]; break; }
        }
      }
      if (hit) { out += '<span class="' + cls + '">' + esc(hit) + '</span>'; i += hit.length; }
      else { out += esc(text[i]); i++; }
    }
    return out;
  }
  function shell(text) {
    // "$ 명령 …" 줄만 색을 입힌다. 나머지 줄은 출력이라 그대로 둔다.
    return text.split('\n').map(function (line) {
      var m = /^(\$ )(\S+)(.*)$/.exec(line);
      if (!m) return esc(line);
      return '<span class="hl-prompt">' + esc(m[1]) + '</span><span class="hl-cmd">' + esc(m[2]) + '</span>' + esc(m[3]);
    }).join('\n');
  }
  function highlightCode() {
    document.querySelectorAll('pre[class*="lang-"] > code').forEach(function (code) {
      if (code.children.length) return;            // 이미 안에 태그가 있으면 손대지 않는다
      var pre = code.parentElement, text = code.textContent;
      if (pre.classList.contains('lang-sh')) { code.innerHTML = shell(text); return; }
      var lang = ['lang-cpp', 'lang-cmake', 'lang-py', 'lang-matlab'].filter(function (l) { return pre.classList.contains(l); })[0];
      if (lang) code.innerHTML = tokenize(text, RULES[lang]);
    });
  }
  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', highlightCode)
    : highlightCode();
})();
