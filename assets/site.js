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
