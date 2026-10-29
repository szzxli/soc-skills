/*
 * Privacy-friendly key-event counting with GoatCounter (https://www.goatcounter.com).
 *
 * Page views are counted by GoatCounter's own cookie-free count.js snippet
 * (loaded from gc.zgo.at, added before </body>; it sends the page path, title,
 * referrer and screen size, uses no cookies or localStorage, and does not check
 * Do Not Track). This file only adds fixed event names such as "soc-skills/grade-run".
 * What this never sends: anything you type, paste or upload (drafts, evidence,
 * logs, API keys), results, or file contents. Event hooks below only check
 * whether an input is empty; they never read its text.
 * No cookies, no fingerprinting (localStorage only holds the "skipgc" test opt-out
 * if you set it with ?nocount=1): one small request per key
 * action straight to GoatCounter. Events are skipped off szzxli.github.io
 * (local copies, forks), and when the browser sends Do Not Track or Global
 * Privacy Control.
 */
(function () {
  var GOATCOUNTER_CODE = 'szzxli'; // <- the ONE setting: your GoatCounter site code ('' turns counting off)

  var PROJECT = 'soc-skills';
  var SITE_HOST = 'szzxli.github.io';
  if (!GOATCOUNTER_CODE || location.hostname !== SITE_HOST || location.protocol !== 'https:') return;
  if (window.gcSkip) return;              // test visit (?nocount=1, ?v=, ?cb=, ...): see the GoatCounter loader in the page
  if (navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true) return;
  var ENDPOINT = 'https://' + GOATCOUNTER_CODE + '.goatcounter.com/count';

  function cleanRef() {
    try {
      if (!document.referrer) return '';
      var u = new URL(document.referrer);
      return u.origin + u.pathname;          // drop query + hash
    } catch (e) { return ''; }
  }
  function send(path, title, isEvent) {
    var q = {
      p: path,
      t: String(title || '').slice(0, 200),
      r: isEvent ? '' : cleanRef(),
      s: String(window.screen ? window.screen.width : ''),
      b: navigator.webdriver ? '153' : '',    // lets GoatCounter drop headless bots
      e: isEvent ? 'true' : '',
      rnd: Math.random().toString(36).slice(2, 7)
    };
    var parts = [];
    for (var k in q) if (q[k]) parts.push(k + '=' + encodeURIComponent(q[k]));
    var url = ENDPOINT + '?' + parts.join('&');
    try { if (navigator.sendBeacon && navigator.sendBeacon(url)) return; } catch (e) {}
    var img = new Image(); img.src = url;    // fallback (GET pixel)
  }
  // Fixed event names only, e.g. countEvent('grade-run') -> "soc-skills/grade-run".
  function countEvent(name) {
    name = String(name || '').replace(/[^a-z0-9\-\/]/gi, '').slice(0, 80);
    if (name) send(PROJECT + '/' + name, PROJECT + ': ' + name, true);
  }
  window.countEvent = countEvent;

  // Page views: counted by the official count.js snippet on each page (not here),
  // so nothing is double-counted.

  // Helpers for the per-site hooks below.
  function byId(id) { return document.getElementById(id); }
  function filled(id) { var el = byId(id); return !!(el && el.value && el.value.trim().length); } // emptiness only
  function onClick(fn) {           // real user clicks only (skips the pages' own programmatic .click())
    var h = function (e) { if (e.isTrusted) fn(e); };
    document.addEventListener('click', h, true);
    document.addEventListener('auxclick', h, true);
  }
  // Generic: <button data-count="see-example"> counts a fixed event on click.
  onClick(function (e) {
    var el = e.target && e.target.closest && e.target.closest('[data-count]');
    if (el) countEvent(el.getAttribute('data-count'));
  });

  // ---- soc-skills key events ----
  onClick(function (e) {
    var el = e.target && e.target.closest && e.target.closest('button,a');
    if (!el || !el.id) return;
    // "grade run": the Grade button with both a key and evidence present (lengths only, never content).
    if (el.id === 'grade-btn' && !el.disabled && filled('api-key') && filled('evidence')) countEvent('grade-run');
    // "export profile": any way a profile/grading leaves the page as a file or copy.
    var EXPORTS = { 'copy-btn': 'summary-copy', 'pkg-dl': 'package-download', 'pkg-copy': 'package-copy',
      'pkg-latest': 'package-latest', 'export-hist': 'history-export',
      'grade-pkg-dl': 'grading-package-download', 'grade-pkg-copy': 'grading-package-copy' };
    if (EXPORTS[el.id]) countEvent('export-profile/' + EXPORTS[el.id]);
    if (el.id === 'gen-btn') countEvent('profile-generate');
    if (el.id === 'verify-btn' && filled('pkg-input')) countEvent('verify-run');
  });
})();
