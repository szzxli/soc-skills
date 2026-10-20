#!/usr/bin/env python3
"""agent-tool-unauth-rce detector (draft): flag unauthenticated calls to
AI-agent tool-execution endpoints in enriched HTTP access / proxy logs.
One shared pattern behind five CVEs published 2026-10-20:

  CVE-2026-77936  Letta <= 0.16.8            POST /v1/tools/run
  CVE-2026-75128  Langchain-Chatchat <= 0.3.1.3  POST /tools/call
  CVE-2026-77932  DB-GPT <= 0.8.2           POST /api/v1/chat/react-agent
  CVE-2026-109442 piflow 2.0.0-2.0.1        POST /chat, /chat/stream
  CVE-2026-109437 Cognition < 0.13.0        POST /sessions,
                                            POST /sessions/{id}/messages

In every case the endpoint that can run shell commands or arbitrary code
for the agent is reachable with NO authentication, so a single request
executes as the server user (root in several shipped Docker images).
Detection only.
Usage: python3 agent-tool-unauth-rce-detect.py <access.log>

Log line format (combined access log + two enrichment fields, as logged
by a reverse proxy / WAF in front of the agent service):
  203.0.113.66 - - [20/Oct/2026:03:14:07 +0000] "POST /v1/tools/run HTTP/1.1" 200 812 "-" "python-requests/2.32" auth=none body="..."
  auth=  : none | bearer | cookie | basic | apikey — whether the request
           carried any credential at all.
  body=  : request-body excerpt (truncated by the proxy is fine).

NOTE: a stock web-server access log has neither field. Without the
auth= enrichment you cannot separate the CVE pattern (no credentials)
from legitimate authenticated tool use — deploy this behind a proxy
that logs header presence and a body excerpt, and treat the endpoint
hits alone as leads, not verdicts.
"""
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ---- allowlist: the (source IP, authenticated user) pairs that drive
# the agent API on purpose — the application server / orchestrator.
# Their AUTHENTICATED tool calls are the product working as intended
# and never raise markers. An allowlisted pair arriving with auth=none
# is NOT expected (spoofed source or a proxy that stopped forwarding
# credentials) and is scored like anyone else.
ALLOWLIST = {("10.0.4.15", "svc-agent")}

BURST_N, BURST_S = 3, 600    # M5: >=3 endpoint hits from one source in 10 min

# ---- M1: known agent tool-execution / agent-drive endpoints (POST only).
# Paths are the exact routes named in the NVD entries / vendor code.
EXEC_ENDPOINTS = [
    (re.compile(r"^/v1/tools/run$"), "Letta tools/run (CVE-2026-77936)"),
    (re.compile(r"^/v1/admin(/|$)"), "Letta admin API (CVE-2026-77936)"),
    (re.compile(r"^/tools/call$"), "Langchain-Chatchat tools/call (CVE-2026-75128)"),
    (re.compile(r"^/api/v1/chat/react-agent$"), "DB-GPT react-agent (CVE-2026-77932)"),
    (re.compile(r"^/chat(/stream)?$"), "piflow chat agent (CVE-2026-109442)"),
    (re.compile(r"^/sessions$"), "Cognition sessions (CVE-2026-109437)"),
    (re.compile(r"^/sessions/[^/]+/messages$"), "Cognition session messages (CVE-2026-109437)"),
]

# ---- M3: body markers — shell/code-interpreter tool names and
# code-execution payload strings. Deliberately specific: ordinary
# data-analysis code (imports, print, file reads of working data) does
# NOT match; OS-command plumbing does.
PAYLOAD = re.compile(
    r"(exec_shell|code_interpreter|shell_interpreter|run_terminal_cmd"
    r"|[\"']tool[\"']\s*:\s*[\"']shell[\"']|[\"']name[\"']\s*:\s*[\"']shell[\"']"
    r"|os\.system|subprocess|__import__|\beval\s*\(|\bexec\s*\("
    r"|/bin/(ba)?sh|/dev/tcp/|\$\(|`[^`]+`|&&|\|\s*(ba)?sh\b"
    r"|curl\s+https?://|wget\s+https?://|base64\s+(--decode|-d)\b"
    r"|os\.environ|printenv|cat\s+/etc/(passwd|shadow))",
    re.IGNORECASE)

LOG = re.compile(
    r'^(\S+) \S+ (\S+) \[([^\]]+)\] "(\S+) (\S+)[^"]*" (\d{3})')
AUTH = re.compile(r"\bauth=(\S+)")
BODY = re.compile(r'\bbody="([^"]*)"')
TS = "%d/%b/%Y:%H:%M:%S %z"

def endpoint_label(path):
    for rx, label in EXEC_ENDPOINTS:
        if rx.search(path):
            return label
    return None

def main(path):
    by_src = defaultdict(list)
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.lstrip().startswith("#") or not line.strip():
                continue
            m = LOG.match(line)
            if not m:
                continue
            ip, user, ts_raw, method, uri, status = m.groups()
            if method.upper() != "POST":
                continue
            label = endpoint_label(uri.split("?")[0])
            if not label:
                continue
            am = AUTH.search(line)
            auth = am.group(1).lower() if am else "unknown"
            bm = BODY.search(line)
            body = bm.group(1) if bm else ""
            try:
                ts = datetime.strptime(ts_raw, TS)
            except ValueError:
                ts = None
            by_src[ip].append({
                "ts_raw": ts_raw, "ts": ts, "user": user, "auth": auth,
                "status": int(status), "uri": uri, "label": label,
                "payload": bool(PAYLOAD.search(body)),
                "expected": (ip, user) in ALLOWLIST and auth != "none",
            })

    for ip, evs in sorted(by_src.items()):
        evs = [e for e in evs if not e["expected"]]
        if not evs:
            continue  # allowlisted, authenticated: the product working
        markers = {"EXEC_ENDPOINT"}
        hits = []
        for e in evs:
            tags = []
            if e["auth"] == "none":
                markers.add("NO_AUTH"); tags.append("NO_AUTH")
            if e["payload"]:
                markers.add("PAYLOAD"); tags.append("PAYLOAD")
            if 200 <= e["status"] < 300:
                markers.add("SUCCESS_2XX")
            hits.append((e, tags))
        # burst: sliding window over this source's endpoint-hit times
        times = sorted(e["ts"] for e in evs if e["ts"] is not None)
        for i, t in enumerate(times):
            win = [x for x in times
                   if 0 <= (x - t).total_seconds() <= BURST_S]
            if len(win) >= BURST_N:
                markers.add("BURST")
                break

        if "PAYLOAD" in markers and "NO_AUTH" in markers:
            verdict = "INCIDENT"      # the CVE pattern, weaponized
        elif {"NO_AUTH", "SUCCESS_2XX", "BURST"} <= markers:
            verdict = "INCIDENT"      # unauthenticated session flow, repeated
        elif "NO_AUTH" in markers or "PAYLOAD" in markers:
            verdict = "SUSPICIOUS"
        else:
            continue  # authenticated, no payload markers: legitimate use

        print(f"[{verdict}] {ip} ({len(hits)} endpoint hits, "
              f"markers: {', '.join(sorted(markers))}):")
        for e, tags in hits:
            tag = (" [" + ",".join(tags) + "]") if tags else ""
            print(f"  {e['ts_raw']} {e['label']} user={e['user']} "
                  f"auth={e['auth']} status={e['status']} {e['uri'][:80]}{tag}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin")
