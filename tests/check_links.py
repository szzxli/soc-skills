#!/usr/bin/env python3
"""Network check: every "where to learn" / cert link on the homepage returns 200.

Run:  python3 tests/check_links.py
Extracts every https URL from the LEARN and CERT_LINKS maps in web/index.html
and requests it (GET, redirects followed, browser User-Agent). Exits 1 if any
link ends in a 4xx/5xx/connection error. A 403/429 from a site that blocks
automated clients is reported as BLOCKED and does not fail the run by default
(pass --strict to fail); confirm those by hand in a browser.
Not part of check_site.py because it needs the network.
"""
import re, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
learn = re.search(r"const LEARN = \{([\s\S]*?)\n\};", src)
certs = re.search(r"const CERT_LINKS = (\[[\s\S]*?\]\]);", src)
if not learn or not certs:
    sys.exit("LEARN / CERT_LINKS not found in web/index.html")
text = learn.group(1) + certs.group(1)
urls = sorted(set(re.findall(r"'(https?://[^']+)'", text)))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
strict = "--strict" in sys.argv
bad, blocked = [], []
for u in urls:
    req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            code, final = r.status, r.geturl()
    except urllib.error.HTTPError as e:
        code, final = e.code, u
    except Exception as e:  # DNS, TLS, timeout
        code, final = 0, f"{u} ({e.__class__.__name__})"
    tag = "OK     " if code == 200 else "BLOCKED" if code in (403, 429) else "FAIL   "
    print(f"{tag} {code} {u}" + (f" -> {final}" if final != u else ""))
    if code in (403, 429): blocked.append(u)
    elif code != 200: bad.append(u)
print(f"\n{len(urls)} links · {len(bad)} failed · {len(blocked)} blocked by bot protection")
sys.exit(1 if bad or (strict and blocked) else 0)
