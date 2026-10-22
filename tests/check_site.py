#!/usr/bin/env python3
"""Static smoke check for the soc-skills web pages (stdlib only).

Run:  python3 tests/check_site.py
Checks that the main CTAs, the element ids the analytics hooks depend on, the
SEO/OG meta tags, and the service-worker wiring are still present. Exits 1 on
any failure. It does not run a browser.
"""
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
fails = []

def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

class Collect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.metas, self.scripts, self.links, self.dupes = {}, [], [], [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            if a["id"] in self.ids: self.dupes.append(a["id"])
            self.ids[a["id"]] = (tag, a)
        if tag == "meta": self.metas.append(a)
        if tag == "script" and a.get("src"): self.scripts.append(a["src"])
        if tag == "a" and a.get("href"): self.links.append(a["href"])

def parse(path):
    c = Collect(); c.feed(path.read_text(encoding="utf-8")); return c

index, verify = parse(WEB / "index.html"), parse(WEB / "verify.html")
idx_src = (WEB / "index.html").read_text(encoding="utf-8")
analytics = (WEB / "analytics.js").read_text(encoding="utf-8")
sw = (WEB / "sw.js").read_text(encoding="utf-8")

# 1. Main CTAs on the homepage
cta = index.ids.get("hero-example")
check(cta is not None and cta[1].get("href") == "#example" and cta[1].get("data-count") == "see-example",
      "hero primary CTA #hero-example -> #example (keyless demo, counts see-example)")
for href in ["#assess", "#grade", "verify.html", "#progress", "#labs"]:
    check(href in index.links, f"homepage links to {href}")
check(any(a.get("data-count") == "grade-own-cta" for _, a in index.ids.values()) or 'data-count="grade-own-cta"' in idx_src,
      "grade-own-cta event hook still present")
for pid in ["example", "assess", "grade", "labs", "progress", "domains", "sample", "support", "faq"]:
    check(pid in index.ids, f"section/panel #{pid} exists")
check(not index.dupes, f"no duplicate ids on homepage {index.dupes or ''}")
# every in-page anchor resolves
for h in index.links:
    if h.startswith("#") and len(h) > 1:
        check(h[1:] in index.ids, f"in-page link {h} has a target")

# 2. Keyless demo wiring
for i in ["ex-tabs", "ex-card", "ex-levels", "ex-load", "try-sample"]:
    check(i in index.ids, f"keyless demo element #{i} exists")
for p in sorted(set(re.findall(r"dir:\s*'([^']+)'", idx_src))):
    check((WEB / "samples" / f"evidence-{p}.json").exists(), f"sample evidence bundle {p} exists")

# 3. Analytics hooks: every id analytics.js listens for exists on its page
check("analytics.js" in index.scripts and "analytics.js" in verify.scripts, "analytics.js loaded on both pages")
hook_ids = set(re.findall(r"el\.id === '([^']+)'", analytics)) | set(re.findall(r"filled\('([^']+)'\)", analytics))
hook_ids |= set(re.findall(r"'([a-z\-]+)': '[a-z\-]+'", analytics))
for i in sorted(hook_ids):
    where = verify if i in ("verify-btn", "pkg-input") else index
    check(i in where.ids, f"analytics hook target #{i} exists ({'verify' if where is verify else 'index'}.html)")
for ev in ["grade-run", "export-profile/", "profile-generate", "verify-run"]:
    check(ev in analytics, f"analytics event '{ev}' defined")

# 4. SEO / OG meta
for page, c in [("index", index), ("verify", verify)]:
    names = {m.get("name") or m.get("property") for m in c.metas}
    for n in ["description", "og:title", "og:description", "og:url", "og:image", "twitter:card"]:
        check(n in names, f"{page}.html has meta {n}")
check('rel="canonical"' in idx_src and "application/ld+json" in idx_src, "homepage keeps canonical + JSON-LD")

# 5. Service worker
m = re.search(r"const C='soc-skills-v(\d+)'", sw)
check(m is not None, "sw.js cache version present")
check("serviceWorker" in idx_src and "sw.js" in idx_src, "homepage registers sw.js")
if m:
    check(f"App version: v{m.group(1)} (web)" in idx_src, f"bug-report app version matches sw cache v{m.group(1)}")
for asset in re.findall(r"'([^']+)'", sw.split("addAll(")[1].split(")")[0]):
    check((WEB / asset).exists(), f"sw cached asset {asset} exists")

# 6. Images have alt text; sample package verifies structurally
for tag in re.findall(r"<img\b[^>]*>", idx_src + (WEB / "verify.html").read_text()):
    check(re.search(r'\balt="[^"]+"', tag) is not None, "img has alt text: " + tag[:60])
pkg = json.loads((WEB / "samples" / "sample-package.json").read_text())
check(pkg.get("type") == "soc-skills-verification-package" and re.fullmatch(r"[0-9a-f]{64}", pkg.get("sha256", "")),
      "sample verification package is well-formed")

print(f"\n{'FAILED' if fails else 'OK'}: {len(fails)} failure(s)")
sys.exit(1 if fails else 0)
