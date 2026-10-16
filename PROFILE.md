# Cybersecurity Skills Profile

**Career-changer → SOC Analyst track** · GSEC candidate (exam ~Dec 2026)
Amazon MRO (emergency medical response) · U.S. Air Force Reserve, E-4, active Secret clearance
📁 Lab portfolio: [github.com/szzxli/soc-home-lab](https://github.com/szzxli/soc-home-lab)

> Every claim below links to runnable code or written reports. All training data is
> synthetic or reconstructed and labeled as such — no real incidents claimed, no production
> experience claimed.

## Skill snapshot (NICE-aligned)

Skills mapped to the NIST NICE Cybersecurity Workforce Framework
(Cyber Defense Analyst PR-CDA-001 / Incident Responder PR-CIR-001).
Levels: **L1** guided · **L2** independent hands-on (scope noted) · **L3** production (none claimed).

| Skill domain | Level | Evidence |
|---|---|---|
| Security monitoring & alert triage | **L2** (lab) | Built AWS mini-SOC (Terraform); ran 3 attack simulations, triaged real GuardDuty findings end-to-end |
| Log analysis & detection engineering | **L2** (synthetic) | Wrote CloudTrail IOC analyzer: 3 heuristic detectors, tunable thresholds, 9 pytest tests |
| Incident response & reporting | **L2** (lab) | Containment playbooks + escalation criteria, all self-authored; structured incident reports |
| Phishing email analysis | **L2** (reconstructed) | Full header→auth→URL-deobfuscation→verdict walkthrough; self-phishing test guide (own mailbox only) |
| Binary / malware triage | **L2** (synthetic) | Wrote static ELF triage tool: heuristic scoring model, 10 pytest tests; triage-signals-not-convictions methodology |
| Cloud security (AWS) | **L2** (lab) | Multi-region CloudTrail, encrypted log bucket, least-privilege IAM — all as code, applied/destroyed by hand |
| Security automation & scripting | **L2** | Two original Python tools with tests, CLIs, READMEs others can run |

**Methodology asset:** distilled the above into 5 MIT-licensed agent skills
(alert triage, incident reporting, CloudTrail IOC, phishing analysis, binary triage) —
evidence of playbook-writing ability ("can document, can onboard others").

## Certification alignment (honest)

| Cert | Relevance |
|---|---|
| **GSEC** (in progress, SEC401) | Strong — labs cover incident handling, log analysis, phishing, malware basics; practice evidence for the exam |
| **Security+** | Moderate — partial domain overlap (threats, architecture, operations) |
| **OSCP** | None claimed — defensive track; attack simulations provide attacker perspective only |

## Target roles

SOC Analyst (Tier 1) · Associate Cybersecurity Analyst · Cyber Defense Analyst ·
Detection & Response (junior)

## What "L2 (lab)" means — read this before interviewing me

I have zero production SOC experience and I won't pretend otherwise. What I do have:
five self-built, self-run projects with code, tests, and reports you can inspect in
~15 minutes. Ask me what broke, what the detection blind spots are, and where my
heuristics fail — I documented all of it.
