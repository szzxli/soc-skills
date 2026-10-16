#!/usr/bin/env python3
"""每周漏洞情报抓取：CISA KEV 新增 + NVD 高危/Critical CVE。
输出: intel/snapshots/YYYY-MM-DD.json
只读公开源，无需 key。"""
import json, ssl, sys, urllib.request
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
SNAP = BASE / "snapshots"
SNAP.mkdir(exist_ok=True)
ctx = ssl.create_default_context()

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "soc-skills-weekly-intel/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
        return json.load(r)

today = date.today()
week_ago = today - timedelta(days=7)
out = {"date": today.isoformat(), "window_start": week_ago.isoformat(), "kev_new": [], "nvd_critical": [], "nvd_high": []}

# 1. CISA KEV：取 dateAdded 落在窗口内的
try:
    kev = get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    for v in kev.get("vulnerabilities", []):
        if v.get("dateAdded", "") >= week_ago.isoformat():
            out["kev_new"].append({
                "cve": v["cveID"], "vendor": v["vendorProject"], "product": v["product"],
                "name": v["vulnerabilityName"], "added": v["dateAdded"],
                "desc": v["shortDescription"], "action": v["requiredAction"],
                "due": v["dueDate"], "notes": v.get("notes", ""),
            })
    out["kev_new"].sort(key=lambda x: x["added"], reverse=True)
except Exception as e:
    out["kev_error"] = str(e)

# 2. NVD：近 7 天发布的 Critical / High
fmt = lambda d: d.strftime("%Y-%m-%dT00:00:00.000Z")
for sev, key in (("CRITICAL", "nvd_critical"), ("HIGH", "nvd_high")):
    try:
        url = ("https://services.nvd.nist.gov/rest/json/cves/2.0/?resultsPerPage=100"
               f"&cvssV3Severity={sev}&pubStartDate={fmt(week_ago)}&pubEndDate={fmt(today + timedelta(days=1))}")
        data = get(url)
        for item in data.get("vulnerabilities", []):
            c = item["cve"]
            m = c.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {})
            descs = [d["value"] for d in c.get("descriptions", []) if d.get("lang") == "en"]
            out[key].append({
                "cve": c["id"], "published": c["published"][:10],
                "score": m.get("baseScore"), "vector": m.get("vectorString", ""),
                "desc": (descs[0] if descs else "")[:300],
            })
        out[key].sort(key=lambda x: -(x["score"] or 0))
    except Exception as e:
        out[key + "_error"] = str(e)

p = SNAP / f"{today.isoformat()}.json"
p.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {p}")
print(f"KEV new: {len(out['kev_new'])}, NVD critical: {len(out['nvd_critical'])}, NVD high: {len(out['nvd_high'])}")
