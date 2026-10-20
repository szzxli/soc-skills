# M365 App-Identity Persistence — A Stolen SaaS Application Secret Becomes Tenant-Wide Backdoors

**Status: DETECTOR VALIDATED on synthetic log (TP=1 FP=0, 2026-10-20) · no live-tenant lab — detection runs on M365 / Entra ID audit-log exports only**
**Severity:** Critical (tenant-wide compromise path) · **Class:** application-identity credential theft + privilege escalation + persistence (MITRE ATT&CK T1098.003 Additional Cloud Roles, T1098.001 Additional Cloud Credentials, T1078.004 Cloud Accounts) · **No CVE — this is an operational incident pattern, not a software flaw** · **NOT in CISA KEV** (KEV catalogs vulnerabilities; there is no CVE to list)

> Anti-inflation: reading this card = L1 at most. Running the detection
> validation = evidence toward L2. The remediation lesson of this
> incident is an audit procedure, not a patch — nobody gets L-anything
> for "disabling the app," because disabling the app is the step that
> does *not* fix it.

## Verified facts (ConnectWise advisory 2026-10-16; Huntress incident write-up; checked 2026-10-20)

- **2026-10-15:** ConnectWise identified unauthorized access to
  application identities inside its **Cloud Backup** environment
  (Cloud Backup is the former SkyKick product). ConnectWise suspended
  **Cloud Backup, SaaS Security, and Cloud Management** — the latter
  two because they integrate with Cloud Backup — and the services
  remained suspended during the investigation.
- **Huntress confirmed active abuse:** a Microsoft 365 API secret
  belonging to ConnectWise Cloud Backup was compromised and was being
  used to gain unauthorized access to customers' M365 tenants.
- **In one customer tenant**, a second application — **ConnectWise
  Cloud Management - MS Teams** (Application ID
  `24205314-2b89-4e07-a2a4-579e898a5640`) — **granted itself Global
  Administrator** and then **added new credentials to two other
  applications** in that tenant, one of them a single-tenant
  application unique to that customer.
- **The persistence trap (the fact this lab exists for):** disabling
  the abused M365 applications does **not** remove credentials that
  were already added to other applications. Every application in the
  tenant must have its credentials reviewed — the backdoor survives
  the obvious remediation.
- ConnectWise published indicators of compromise (a set of IP
  addresses and third-party app integrations) and disabled some
  Cloud Backup integrations with Exchange, Teams, and SharePoint
  Online while the investigation continues.

## 1. Mechanics

A SaaS product that operates inside a customer's M365 tenant does so
as an **application identity** — a service principal holding an API
secret or certificate. That identity is, by design, a standing
credential with broad reach, and it sits outside the controls aimed
at humans: no MFA prompt, no conditional-access friction in many
tenants, often no named owner watching it.

Steal the secret and you don't get a user account — you get the
*application's* trusted position. The chain Huntress documented is
three administrative moves, each one a legitimate API operation:

1. **Authenticate as the application** (the stolen secret) — from
   wherever the attacker happens to be.
2. **Escalate:** a second application grants itself **Global
   Administrator**. No exploit, no malformed input — a role
   assignment.
3. **Persist sideways:** add fresh credentials (certificates /
   secrets) to *other* applications in the tenant. Now the attacker
   holds keys the victim doesn't know exist, on applications the
   victim isn't looking at. Removing or disabling the originally
   abused apps changes nothing about steps already taken.

Every step lands in the tenant's audit log as an ordinary
administrative event. The detection problem is therefore not payload
inspection — it is asking, of each directory-changing event: **who
did this, what kind of actor are they, what did they touch, and how
much of it happened at once?**

## 2. Hunt markers (use these, in order)

1. **A service principal is granted a privileged directory role**
   (M1) — Global Administrator above all, but also Privileged Role
   Administrator, Privileged Authentication Administrator,
   Application Administrator, Cloud Application Administrator,
   Exchange / SharePoint / Security / User Administrator. Legitimate
   instances exist (some backup products historically demand broad
   roles — which is part of how this incident class happens), but
   each one is a tenant-level decision that should be explainable.
2. **New credentials added to a service principal** (M2) — a
   certificate or secret appearing on an application. This is the
   persistence move itself; it is also, unfortunately, a routine
   admin operation, which is why it cannot carry a verdict alone.
3. **The actor making directory changes is an application, not a
   human admin** (M3) — role assignments and credential changes
   initiated by a service principal. Human admins rotate credentials;
   applications granting roles and minting credentials is the
   incident's signature.
4. **Cross-application burst** (M4) — role/credential changes touching
   **≥3 distinct applications inside 30 minutes** from one actor.
   Admins work on one app at a time, in a change window, with a
   ticket. Campaigns sweep.
5. **Service-principal sign-in from a non-allowlisted IP** (M5) — the
   application authenticating from somewhere that is not its known
   egress (vendor datacenter, your NAT). The stolen secret is used
   from the attacker's infrastructure, not the vendor's.

## 3. Triage decision tree

- Marker (1) from any actor → incident: a service principal holds a
  privileged role as of this event. Establish whether a human
  approved it, then hunt markers (2)–(5) across the whole tenant —
  assume the role grant was step one, not the whole story.
- Markers (2)+(3) → incident: an application is minting credentials.
  **Enumerate every credential on every application in the tenant**
  (the Huntress lesson: the abused app is not where the backdoors
  live). Remove credentials you cannot attribute to a named human
  and a change record; rotate the rest.
- Markers (3), (4), or (5) alone → suspicious: an application doing
  admin-shaped things, a burst, or an application signing in from a
  new network location. Correlate with the vendor's status page and
  your change calendar before escalating — and if the vendor is
  mid-incident (as ConnectWise was), escalate anyway.
- Marker (2) alone, actor is a human admin outside the allowlist →
  suspicious by design: probably a legitimate rotation by someone
  who isn't on the change-controlled path. Confirm the ticket; then
  fix the process, not the person — the allowlist is where rotations
  are supposed to happen.
- Credential rotation by the allowlisted (IP, admin) pair, and
  service-principal sign-ins from allowlisted egress → expected.
  That is the control working; spend detection budget elsewhere.

## 4. Lab exercises (do them yourself)

1. Run `m365-app-identity-persistence-detect.py` against
   `samples/m365-app-identity-audit.log` (in the companion
   soc-home-lab repo, `07-kev-hunting/`); confirm it flags the
   application actor as INCIDENT with all five markers, the second
   abused application's sign-in and the unlisted human's credential
   add as SUSPICIOUS, and none of the benign traffic — including the
   allowlisted admin's certificate rotation (FP=0).
2. The detector's privileged-role list is a judgment call written
   down. Take your own tenant's role model (or the public Entra ID
   role documentation) and argue each entry: which roles let an
   application read all mail, reset any password, or grant itself
   more roles? Adjust the list and note what each change does to
   the verdicts on the sample.
3. Write the incident report for the INCIDENT actor as if it were
   your tenant: the containment step everyone reaches for first
   (disable the vendor's apps) and why it is insufficient, the
   credential census you would run instead, and how you would prove
   — from the audit log, not from hope — that no unattributed
   credential remains.

## Honest limitations

- **Audit-log coverage is the prerequisite.** This detector reads
  Entra ID / M365 audit-log style records (directory role changes,
  application credential changes, service-principal sign-ins).
  Tenants without the licensing or retention to keep those records —
  or where the attacker had time and rights to matter — will have
  gaps. A clean run means "no markers in the log you gave it," not
  "tenant is clean."
- **The sample is one documented chain, generalized.** The markers
  encode the moves Huntress observed (self-granted Global Admin,
  credentials added to other apps). An actor who only *uses* a
  stolen secret for data access, without touching roles or
  credentials, trips marker 5 at most — data-plane detection (what
  the app read, from where, how much) is a different lab.
- **Allowlist quality decides FP rate.** The (IP, actor) allowlist
  and the sign-in egress list are tenant-specific facts. Ship this
  detector with the sample allowlist and it will be wrong in both
  directions; the exercises are where you replace them with yours.
- No live tenant and no real credentials in this lab — detection
  runs on the synthetic audit log only.
