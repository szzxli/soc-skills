#!/usr/bin/env python3
"""Static smoke check for the soc-skills web pages (stdlib only).

Run:  python3 tests/check_site.py
Checks that the main CTAs, the element ids the analytics hooks depend on, the
SEO/OG meta tags, and the service-worker wiring are still present; that the
verification wording stays honest; that rubric version numbers agree; that the
limitations / help-validate / gap-analysis / one-pager features exist; and runs
the verify-lib unit tests with node (tests/test_verify_lib.js). Exits 1 on any
failure. It does not run a browser or touch the network (see check_links.py).
"""
import json, re, shutil, subprocess, sys
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

# 7. Honest verification wording (site + docs): no "tamper-evident"/"untampered"
ver_src = (WEB / "verify.html").read_text(encoding="utf-8")
lib_src = (WEB / "verify-lib.js").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
for name, txt in [("index.html", idx_src), ("verify.html", ver_src), ("verify-lib.js", lib_src), ("README.md", readme)]:
    check(not re.search(r"tamper|untampered", txt, re.I), f"{name} makes no tamper-evident/untampered claim")
for name, txt in [("index.html", idx_src), ("verify.html", ver_src), ("README.md", readme)]:
    check("unchanged since" in txt, f"{name} says a hash match means the file is unchanged since the hash was made")
    check(re.search(r"not (a|a digital) signature|isn't a signature|It is not a signature", txt) is not None, f"{name} says the hash is not a signature")
check("truthful" in ver_src and "who made" in ver_src, "verify.html says the hash does not prove truthfulness or authorship")

# 8. Public anchor (gist) UI on the Verify page
verify_ids = verify.ids
for i in ["anchor", "anchor-url", "anchor-btn", "anchor-result", "anchor-copy"]:
    check(i in verify_ids, f"verify.html anchor element #{i} exists")
check("SocVerify.fetchGistAnchor" in ver_src and "SocVerify.anchorText" in ver_src, "verify.html wires fetchGistAnchor + anchorText")
check("https://gist.github.com/" in ver_src, "verify.html links to gist.github.com for anchoring")
check("verify.html#anchor" in idx_src, "homepage points package users at the anchor how-to")
node = shutil.which("node")
if node:
    r = subprocess.run([node, str(ROOT / "tests" / "test_verify_lib.js")], capture_output=True, text=True)
    tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
    check(r.returncode == 0, f"verify-lib unit tests (node): {tail}")
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
else:
    check(False, "node is required to run tests/test_verify_lib.js")

# 9. One rubric version everywhere (current = rubric-prompt.md header)
prompt = (ROOT / "grader" / "rubric-prompt.md").read_text(encoding="utf-8")
cur = re.search(r"rubric-prompt (v\d+\.\d+)", prompt.splitlines()[0]).group(1)
m = re.search(r"const RUBRIC_VERSION = '(v[\d.]+)'", idx_src)
check(m is not None and m.group(1) == cur, f"index.html RUBRIC_VERSION matches rubric-prompt.md ({cur})")
emb = re.search(r"const GRADER_PROMPT = `([\s\S]*?)`;", idx_src)
norm = lambda t: "\n".join(l.rstrip() for l in t.replace("\\`", "`").strip().splitlines())
check(emb is not None and norm(emb.group(1)) == norm(prompt), "embedded GRADER_PROMPT is identical to grader/rubric-prompt.md")
grader_readme = (ROOT / "grader" / "README.md").read_text(encoding="utf-8")
check(f"Current rubric version: **{cur}**" in grader_readme, f"grader/README.md states current version {cur}")
for v in ["v1.0", "v1.1", "v1.2", "v1.3"]:
    check(f"- {v} ·" in grader_readme, f"grader/README.md changelog lists {v}")
check(f"Rubric version:** {cur}" in readme, f"README.md states rubric version {cur}")
check(f"<b>{cur}</b>" in idx_src and "rubric-changelog" in index.ids, f"site changelog lists current {cur}")
# every v1.x mention on the site is either the current version or explicitly historical
site_wo_prompt = re.sub(r"const GRADER_PROMPT = `[\s\S]*?`;", "", idx_src)
for mm in re.finditer(r"v1\.(\d)", site_wo_prompt):
    v = "v1." + mm.group(1)
    if v == cur: continue
    ctx = site_wo_prompt[max(0, mm.start()-160): mm.end()+160]
    check(re.search(r"earlier|2026-10-1[5-7]|validation-v1\.1|current|<b>v1\.[012]</b>|graded with|v1\.1 round|TAXONOMY", ctx) is not None,
          f"site mention of {v} is marked as historical/current context")

# 10. Limitations + help-validate
for i in ["validity", "limitations", "help-validate"]:
    check(i in index.ids, f"homepage #{i} exists")
lim = idx_src[idx_src.find('id="limitations"'):idx_src.find('id="help-validate"')]
for phrase in ["author's own 5", "No human-rater comparison", "inter-rater", "vary between runs"]:
    check(phrase in lim, f"limitations mention: {phrase}")
tmpl = ROOT / ".github" / "ISSUE_TEMPLATE" / "blind-rating.yml"
check(tmpl.exists(), "blind-rating issue template exists")
check("issues/new?template=blind-rating.yml" in idx_src and "issues/new?template=blind-rating.yml" in readme, "site + README link to the blind-rating template")
if tmpl.exists():
    t = tmpl.read_text(encoding="utf-8")
    for f in re.findall(r"(evidence-0\d-[a-z0-9-]+\.json)", t):
        check((WEB / "samples" / f).exists(), f"template sample {f} exists")
    check(all(f"id: d{k}" in t for k in range(1, 9)), "template asks for a level per domain D1-D8")
    check("required: true" in t and "before seeing the AI grade" in t, "template enforces blind rating")
check((ROOT / "grader" / "HUMAN-RATING.md").exists(), "grader/HUMAN-RATING.md protocol exists")

# 11. Repositioning: gap analysis that complements certs
hero = idx_src[idx_src.find('<div class="hero"'):idx_src.find('<section class="how-steps"')]
sub = re.search(r'<p class="sub">(.*?)</p>', hero).group(1)
check("missing" in sub and "learn" in sub and ("alongside" in sub.lower() or "complement" in sub.lower()), "hero subline: what's missing + where to learn + complements certs")
check(len(re.sub(r"<[^>]+>", "", sub).split()) <= 30, "hero subline stays short (<= 30 words)")
check("Does this replace Security+" in idx_src, "FAQ answers 'does this replace certs'")
learn = re.search(r"const LEARN = \{([\s\S]*?)\n\};", idx_src)
check(learn is not None, "LEARN map defined")
if learn:
    body = learn.group(1)
    for k in range(1, 9):
        blk = re.search(rf"D{k}: \[([\s\S]*?)\]\](?:,|$)", body)
        n = len(re.findall(r"'https://", blk.group(1))) if blk else 0
        check(n >= 2, f"D{k} has >= 2 'where to learn' links ({n})")
    for must in ["tryhackme.com/path/outline/soclevel1", "letsdefend.io", "cyberdefenders.org", "blue-team-level-1", "comptia.org", "attack.mitre.org"]:
        check(must in body or must in idx_src[learn.end():learn.end()+600], f"learning links include {must}")
    check(not re.search(r"'http://", body), "all learning links are https")
check(idx_src.count("learnHtml(") >= 4, "learning links rendered in live grading, example and self-assessment gaps")
for i in ["assess-gaps", "onepager-btn", "onepager-latest"]:
    check(i in index.ids, f"homepage #{i} exists")
check("Honest disclaimer" in idx_src and "not a certification" in idx_src, "one-pager carries an honest disclaimer")

# 12. Page batch 2026-10-29: user-flow order, one hero CTA, honest privacy, gap→lab, share card
hero_end = idx_src.find('<section class="how-steps"')
check(hero_end > 0 and idx_src.find('<section class="panels"') > hero_end, "How-it-works steps sit directly under the hero")
check(len(re.findall(r'class="btn primary', idx_src[:hero_end])) == 1, "hero has exactly one primary CTA")
check('<details class="tools-more">' in idx_src[:hero_end], "secondary hero links are folded")
check("expand-all" not in idx_src and "Open any section" not in idx_src, "no 'Open any section / Expand all' on the first screen")
order = [idx_src.find(f'<details class="panel" id="{p}">') for p in ("assess", "labs", "grade", "progress")]
check(all(o > 0 for o in order) and order == sorted(order), "panels follow the flow: Assess, Build evidence (labs), Grade, Progress")
check("Employers buy future performance" not in idx_src, "no 'Employers buy future performance' line")
check("level-legend" in index.ids and all(t in idx_src[:hero_end] for t in ("L1+*", "L1+", "L2")), "level legend near the hero screenshot")
gl = idx_src[hero_end:idx_src.find('<section class="panels"')]
check("<b>NICE</b>" in gl and "<b>KEV</b>" in gl, "NICE and KEV glossed before first use")
check("soc-home-lab/web/?ref=socskills" in gl and "where you practice" in gl, "soc-home-lab relationship line with ?ref=socskills")
check(all("ref=socskills" in h for h in index.links if "szzxli.github.io/soc-home-lab" in h), "every soc-home-lab site link carries ?ref=socskills")
faq_priv = re.search(r"<dt>Where does my data go\?</dt>\s*<dd>(.*?)</dd>", idx_src, re.S)
check(faq_priv is not None and faq_priv.group(1).startswith("It stays in your browser") and "may log or retain" in faq_priv.group(1),
      "privacy answer leads with 'stays in your browser' + provider retention caveat")
check("practiceHtml(g.d.id) + learnHtml(g.d.id)" in idx_src, "gap list shows lab cards before external platforms")
check("share-btn" in index.ids and "self-assessed, not verified" in idx_src[idx_src.find("function shareCardFor"):][:600], "shareable result is labeled self-assessed")
one = re.search(r"function oneLinerFor\(levels, pledged\)\{([\s\S]*?)\n\}", idx_src).group(1)
check("pledged ?" in one and not re.search(r"Advanced|Independent", one), "one-liner: 'pledge' wording only when pledged, no inflated titles")

print(f"\n{'FAILED' if fails else 'OK'}: {len(fails)} failure(s)")
sys.exit(1 if fails else 0)
