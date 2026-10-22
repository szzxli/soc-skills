#!/usr/bin/env python3
"""Headless-Chrome end-to-end check of the credibility flows (optional; needs `pip install playwright` and Chrome).

Run:  python3 tests/e2e_flows.py http://localhost:8000/web   (or the live https://szzxli.github.io/soc-skills/web)
Covers: hero copy, SW cache version, limitations/changelog/help-validate, learning links in all three gap views,
one-pager, package download, Verify wording, gist anchor (mocked GitHub API for positive/edited/secret cases,
live GitHub API for not-found cases), and the edited-package failure path.
"""
import json, os, sys, re, urllib.request
from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip('/')  # e.g. http://localhost:8000/web or https://szzxli.github.io/soc-skills/web
results = []
def check(c, msg):
    results.append((bool(c), msg)); print(('PASS ' if c else 'FAIL ') + msg, flush=True)

def real_public_gist():
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.github.com/gists/public?per_page=1', headers={'User-Agent':'e2e'}), timeout=20) as r:
            return json.load(r)[0]['html_url']
    except Exception as e:
        print('could not fetch a public gist:', e); return None

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME') or None, args=['--no-sandbox'])
    ctx = b.new_context(accept_downloads=True, viewport={'width':1280,'height':800}, service_workers='block')
    ctx.grant_permissions(['clipboard-read','clipboard-write'])
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('response', lambda r: r.status >= 400 and not r.url.endswith('favicon.ico') and errors.append(f'{r.status} {r.url}'))

    page.goto(BASE + '/index.html?e2e=1', wait_until='networkidle')
    h1 = page.inner_text('.hero h1'); sub = page.inner_text('.hero .sub')
    check('gaps' in h1.lower(), f'hero h1: {h1!r}')
    check('missing' in sub and 'Security+' in sub, f'hero sub: {sub!r}')
    check(page.locator('.hero .sub').is_visible() and page.locator('#hero-example').is_visible(), 'hero sub + primary CTA visible on first screen')
    c2 = b.new_context(); p2 = c2.new_page(); p2.goto(BASE + '/index.html', wait_until='networkidle')
    p2.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.ready.then(()=>true)", timeout=20000)
    keys = p2.evaluate("new Promise(r=>setTimeout(()=>caches.keys().then(r),1500))")
    check('soc-skills-v23' in keys, f'service worker installed cache {keys}')
    c2.close()

    # validity panel via hash
    page.goto(BASE + '/index.html#validity', wait_until='networkidle')
    check(page.evaluate("document.getElementById('validity').open"), '#validity opens from hash')
    lim = page.inner_text('#limitations')
    check("author's own 5" in lim and 'inter-rater' in lim and 'vary between runs' in lim, 'limitations text rendered')
    check('v1.3' in page.inner_text('#rubric-changelog'), 'changelog shows v1.3')
    href = page.get_attribute('#help-validate a.btn', 'href')
    check(href.endswith('issues/new?template=blind-rating.yml'), f'help-validate link: {href}')

    # example gaps with learn links
    page.click('#ex-tabs button[data-p="P1"]') if page.locator('#ex-tabs button[data-p="P1"]').is_visible() else page.evaluate("openPanel('example')")
    page.evaluate("openPanel('example')")
    n = page.locator('#ex-gaps .learn a').count()
    check(n >= 2, f'example gap analysis has learning links ({n})')

    # self-assessment
    page.evaluate("openPanel('assess')")
    groups = page.locator('#quiz .opts')
    for i in range(groups.count()):
        val = ['1','0.5','0'][i % 3]
        groups.nth(i).locator(f'button[data-v="{val}"]').click()
    page.check('#evidence-check')
    page.on('dialog', lambda d: d.accept())
    page.click('#gen-btn')
    page.wait_for_selector('#assess-gaps .learn a')
    gaps_n = page.locator('#assess-gaps [data-learn]').count()
    check(gaps_n >= 1, f'self-assessment gap analysis lists {gaps_n} domains with learning links')
    check('complements certifications' in page.inner_text('#summary'), '30-second summary carries the complement disclaimer')

    with ctx.expect_page() as pi:
        page.click('#onepager-btn')
    op = pi.value; op.wait_for_load_state()
    t = op.inner_text('body')
    check('Honest disclaimer' in t and 'not a certification' in t and 'v1.3' in t, 'one-pager opens with disclaimer + rubric v1.3')
    check(op.locator('table tr').count() == 8, 'one-pager lists 8 domains')
    op.close()

    with page.expect_download() as di:
        page.click('#pkg-dl')
    path = di.value.path(); pkg_text = open(path).read(); pkg = json.loads(pkg_text)
    st = page.inner_text('#pkg-status')
    check(pkg['payload']['rubric'] == 'v1.3' and re.fullmatch(r'[0-9a-f]{64}', pkg['sha256']), 'downloaded package: rubric v1.3 + sha256')
    check('sha256' in st and page.locator('#pkg-status a[href="verify.html#anchor"]').count() == 1, 'package status shows hash + anchor how-to link')

    # live grading prescription via stored sample (no key)
    page.evaluate("openPanel('grade')")
    page.click('#try-sample')
    page.wait_for_selector('#grade-prescription .learn a', timeout=15000)
    check(page.locator('#grade-prescription .learn a').count() >= 2, 'grading "next moves" show learning links')
    check('earlier rubric v1.1' in page.inner_text('#grade-status'), 'stored example labeled as earlier rubric v1.1')
    check(not errors, f'no console/page errors on homepage {errors[:3]}')

    # Verify page
    errors.clear()
    v = ctx.new_page(); v.on('pageerror', lambda e: errors.append(str(e)))
    v.goto(BASE + '/verify.html', wait_until='networkidle')
    v.click('#sample-btn')
    v.wait_for_selector('#verdict.pass')
    vt = v.inner_text('#verdict')
    check('unchanged since the hash was made' in vt and 'not a signature' in vt, f'verify pass wording: {vt[:90]!r}')
    check(v.is_enabled('#anchor-copy'), 'Copy gist text enabled after a pass')
    v.click('#anchor-copy')
    clip = v.evaluate('navigator.clipboard.readText()')
    sample_hash = json.loads(v.input_value('#pkg-input'))['sha256']
    check(f'sha256: {sample_hash}' in clip, 'gist text copied with the package hash')

    gid = 'aa5a315d61ae9438b18d00000000abcd'
    def fake(route, public=True, content=None, updated='2026-10-21T10:00:00Z'):
        body = {'id': gid, 'html_url': f'https://gist.github.com/demo/{gid}', 'public': public,
                'created_at': '2026-10-21T10:00:00Z', 'updated_at': updated, 'owner': {'login': 'demo'},
                'files': {'soc-skills.txt': {'content': content if content is not None else clip}}}
        route.fulfill(status=200, content_type='application/json', body=json.dumps(body), headers={'access-control-allow-origin': '*'})
    v.route(f'https://api.github.com/gists/{gid}', lambda r: fake(r))
    v.fill('#anchor-url', f'https://gist.github.com/demo/{gid}')
    v.click('#anchor-btn'); v.wait_for_selector('#anchor-result .verdict')
    at = v.inner_text('#anchor-result')
    check('Hash was public by 2026-10-21 10:00:00 UTC' in at and 'never edited' in at, f'anchor positive (mocked gist): {at[:80]!r}')
    v.unroute(f'https://api.github.com/gists/{gid}')
    v.route(f'https://api.github.com/gists/{gid}', lambda r: fake(r, updated='2026-10-25T08:00:00Z'))
    v.click('#anchor-btn'); v.wait_for_function("document.getElementById('anchor-result').innerText.includes('2026-10-25')")
    check('public by 2026-10-25 08:00:00 UTC' in v.inner_text('#anchor-result'), 'anchor edited gist -> date of last edit')
    v.unroute(f'https://api.github.com/gists/{gid}')
    v.route(f'https://api.github.com/gists/{gid}', lambda r: fake(r, public=False))
    v.click('#anchor-btn'); v.wait_for_function("document.getElementById('anchor-result').innerText.includes('secret')")
    check('secret' in v.inner_text('#anchor-result'), 'anchor secret gist -> warning')
    v.unroute(f'https://api.github.com/gists/{gid}')

    real = real_public_gist()
    if real:
        v.fill('#anchor-url', real); v.click('#anchor-btn')
        v.wait_for_selector('#anchor-result .verdict', timeout=20000)
        rt = v.inner_text('#anchor-result')
        check('No public anchor' in rt and ('does not contain' in rt or 'rate limit' in rt), f'anchor vs a real public gist via live GitHub API -> not found: {rt[:90]!r}')
    v.fill('#anchor-url', 'https://gist.github.com/nobody/0000000000000000000000000000dead')
    v.click('#anchor-btn'); v.wait_for_function("/not found|rate limit/i.test(document.getElementById('anchor-result').innerText)", timeout=20000)
    check(True, 'anchor vs nonexistent gist (live API) -> "' + v.inner_text('#anchor-result').split('\n')[-1][:60] + '"')

    # own downloaded package verifies; top-level anchor field auto-fills; edited fails
    pkg2 = dict(pkg); pkg2['anchor'] = f'https://gist.github.com/demo/{gid}'
    v.route(f'https://api.github.com/gists/{gid}', lambda r: fake(r, content='sha256: ' + pkg['sha256']))
    v.fill('#anchor-url', '')
    v.fill('#pkg-input', json.dumps(pkg2)); v.click('#verify-btn'); v.wait_for_selector('#verdict.pass')
    v.wait_for_function("document.getElementById('anchor-result').innerText.includes('Hash was public')")
    check(v.input_value('#anchor-url') == pkg2['anchor'], 'own package verifies; top-level "anchor" auto-fills and auto-checks')
    bad = json.loads(pkg_text); bad['payload']['domains'][0]['level'] = 'L3'
    v.fill('#pkg-input', json.dumps(bad)); v.click('#verify-btn'); v.wait_for_selector('#verdict.fail')
    check('changed after the hash was made' in v.inner_text('#verdict'), 'edited package fails with honest reason')
    check(v.inner_text('#anchor-result') == '', 'anchor result cleared on failed verification')
    check(not errors, f'no page errors on verify {errors[:3]}')
    b.close()

fails = [m for ok, m in results if not ok]
print(f"\n{'FAILED' if fails else 'OK'}: {len(results)-len(fails)}/{len(results)} passed")
sys.exit(1 if fails else 0)
