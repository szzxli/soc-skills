#!/usr/bin/env python3
"""m365-app-identity-persistence detector (draft): flag application-
identity persistence patterns in M365 / Entra ID audit-log exports —
service principals granted privileged directory roles, credentials
added to service principals, directory changes performed BY an
application actor, cross-application change bursts, and service-
principal sign-ins from non-allowlisted IPs.

Incident pattern (ConnectWise Cloud Backup, Oct 2026): an M365 API
secret belonging to a SaaS backup application was stolen and used to
enter customer tenants. In one tenant a second application granted
itself Global Administrator, then added new credentials to two other
applications — persistence that survives disabling the abused apps.
Every step is a legitimate API operation, so detection is actor/type/
scope analysis on the audit log, not payload inspection.
Detection only.
Usage: python3 m365-app-identity-persistence-detect.py <audit.jsonl>

Log line format (one JSON object per line, Entra ID audit-log style;
field names are the log keys):
  {"timestamp": "2026-10-15T03:13:02Z",
   "operation": "Add member to role",
   "initiatedByType": "app", "initiatedBy": "Vendor App - Teams",
   "actorId": "24205314-2b89-4e07-a2a4-579e898a5640",
   "actorIp": "203.0.113.66",
   "targetType": "servicePrincipal", "target": "Vendor App - Teams",
   "targetAppId": "24205314-2b89-4e07-a2a4-579e898a5640",
   "role": "Global Administrator", "result": "success"}
  operation: "Add member to role" | "Add service principal credentials"
             | "Service principal sign-in" (anything else is ignored)
  initiatedByType: "user" (human) | "app" (service principal actor)
  credentialType: "certificate" | "secret" (on credential-add lines)

NOTE: this assumes your tenant actually retains these audit records
(directory changes + service-principal sign-ins). Without them the
persistence moves in this pattern are invisible at this layer; the
compensating control is a periodic census of every credential on
every application in the tenant (see the lab card).
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ---- allowlist: (source IP, actor) pairs that perform directory
# changes on purpose — the change-controlled admin path. Their
# credential rotations are the control working and never raise
# markers. The same actor arriving from an unlisted IP is NOT
# expected and is scored like anyone else.
ALLOWLIST = {("10.0.6.20", "a.admin@contoso.com")}

# ---- egress IPs a managed application's sign-ins are expected from
# (vendor datacenters, your NAT). Sign-ins from anywhere else raise
# M5; sign-ins from here never do.
SP_SIGNIN_ALLOW_IPS = {"10.0.7.30", "10.0.7.31"}

# ---- M1: directory roles whose grant to a service principal is a
# tenant-level event. Judgment call, written down: each role can read
# all mail/files, reset any credential, or grant further roles.
PRIV_ROLES = {
    "Global Administrator",
    "Privileged Role Administrator",
    "Privileged Authentication Administrator",
    "Application Administrator",
    "Cloud Application Administrator",
    "Exchange Administrator",
    "SharePoint Administrator",
    "Security Administrator",
    "User Administrator",
}

ROLE_OP = "Add member to role"
CRED_OP = "Add service principal credentials"
SIGNIN_OP = "Service principal sign-in"
BURST_APPS, BURST_S = 3, 1800  # M4: >=3 distinct target apps in 30 min
TS = "%Y-%m-%dT%H:%M:%SZ"

def parse(line):
    try:
        f = json.loads(line)
    except ValueError:
        return None
    if not isinstance(f, dict) or "operation" not in f:
        return None
    try:
        f["ts"] = datetime.strptime(f["timestamp"], TS).replace(
            tzinfo=timezone.utc)
    except (KeyError, ValueError):
        return None
    f["ts_raw"] = f["timestamp"]
    f.setdefault("initiatedByType", "?")
    f.setdefault("initiatedBy", "?")
    f.setdefault("actorId", f["initiatedBy"])
    f.setdefault("actorIp", "?")
    return f

def main(path):
    by_actor = defaultdict(list)
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.lstrip().startswith("#") or not line.strip():
                continue
            ev = parse(line)
            if ev:
                by_actor[ev["actorId"]].append(ev)

    for actor, evs in sorted(by_actor.items()):
        evs.sort(key=lambda e: e["ts"])
        # drop the allowlisted admin path: (IP, actor) doing its job
        evs = [e for e in evs
               if (e["actorIp"], e["actorId"]) not in ALLOWLIST]
        hits, markers = [], set()
        changes = [e for e in evs if e["operation"] in (ROLE_OP, CRED_OP)]

        for e in changes:
            tgt = e.get("target", e.get("targetAppId", "-"))
            if (e["operation"] == ROLE_OP
                    and e.get("targetType") == "servicePrincipal"
                    and e.get("role") in PRIV_ROLES):
                markers.add("PRIV_ROLE_TO_SP")
                hits.append((e, "PRIV_ROLE_TO_SP",
                             f"role={e['role']} target={tgt}"))
            if e["operation"] == CRED_OP:
                markers.add("CRED_ADDED_TO_SP")
                hits.append((e, "CRED_ADDED_TO_SP",
                             f"target={tgt} "
                             f"credentialType={e.get('credentialType', '-')}"))
            if e["initiatedByType"] == "app":
                markers.add("APP_ACTOR")
                hits.append((e, "APP_ACTOR",
                             f"app performed '{e['operation']}'"))
        # cross-application burst: one actor, many target apps, fast
        for i, e0 in enumerate(changes):
            win = [e for e in changes
                   if 0 <= (e["ts"] - e0["ts"]).total_seconds() <= BURST_S]
            if len({e.get("targetAppId") for e in win}) >= BURST_APPS:
                markers.add("CROSS_APP_BURST")
                hits.append((e0, "CROSS_APP_BURST",
                             f"{BURST_APPS}+ distinct target apps within "
                             f"{BURST_S}s"))
                break
        for e in evs:
            if (e["operation"] == SIGNIN_OP
                    and e["actorIp"] not in SP_SIGNIN_ALLOW_IPS):
                markers.add("SP_SIGNIN_NEW_IP")
                hits.append((e, "SP_SIGNIN_NEW_IP",
                             f"ip={e['actorIp']}"))

        if not markers:
            continue  # clean actor: no output
        if ("PRIV_ROLE_TO_SP" in markers
                or {"CRED_ADDED_TO_SP", "APP_ACTOR"} <= markers):
            verdict = "INCIDENT"
        else:
            verdict = "SUSPICIOUS"
        name = evs[0]["initiatedBy"] if evs else actor
        ips = ", ".join(sorted({e["actorIp"] for e in evs}))
        print(f"[{verdict}] {name} actor={actor} ips={ips} "
              f"({len(hits)} hits, markers: {', '.join(sorted(markers))}):")
        for e, kind, detail in sorted(hits, key=lambda h: h[0]["ts"]):
            print(f"  {e['ts_raw']} {kind} {detail}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin")
