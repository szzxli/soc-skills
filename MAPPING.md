# Project → Skill Mapping (MAPPING)

> Skeleton v1.0 · 2026-10-15
> Subject: 5 projects under `~/workspace/soc-home-lab/` (completed by hand by
> the author).
> Grading iron rules: evidence first, scope suffix, L3 stays empty, downgrade
> on ambiguity.
> Cert mapping note: GSEC (author preparing; SEC401/GSEC ~2026-12-28),
> Security+, OSCP. "Mapping" means skill content overlaps cert domains and can
> aid preparation; **it does NOT mean "at cert level"**.

---

## P1 · 01-mini-soc (AWS Mini SOC)

**What was done**: Terraform-built CloudTrail → encrypted S3 → GuardDuty →
Security Hub from scratch; ran 3 attack simulations by hand (S3 exfiltration,
IAM privilege escalation, EC2 cryptomining); wrote a triage guide (GuardDuty
finding triage) and an incident report template; includes an attack runbook
(ATT&CK mapping) and architecture decision docs.

| Skill domain | Level | One-line evidence |
|---|---|---|
| D1 Security monitoring & alert triage | **L2 (lab)** | Ran attacks by hand → saw real findings in GuardDuty → triaged/dispositioned per self-written guide, full chain done independently |
| D2 Log analysis & detection engineering | L1+ | Reads CloudTrail to answer who/what/where; explains GuardDuty vs CloudTrail coverage blind spots, but never wrote production detection rules |
| D3 Incident response & reporting | **L1+** | Containment playbook + escalation criteria self-written, but incident-reports/ holds only a blank template — no filled report yet (grader rule 6: template ≠ output). Restore to L2 (lab) after hand-filling one detonation report. Downgraded 2026-10-16 per v1.0/v1.1 validation |
| D6 Cloud security (AWS) | **L2 (lab)** | Full IaC stack self-built, multi-region Trail, encrypted log bucket, least-privilege IAM roles — all applied/destroyed by hand |
| D7 Security automation & scripting | L1 | Used Terraform and off-the-shelf tools; no self-written analysis code (see P2/P4 for code) |

**Cert mapping**: GSEC — covers the incident-handling / log-analysis hands-on
surface, strong prep aid; Security+ — covers architecture & operations domains;
OSCP — attacker-perspective primer only (knows what attacks look like),
**no substantive mapping**.

---

## P2 · 02-python-ioc-analyzer (Python IOC analyzer)

**What was done**: hand-written Python CLI tool: parses CloudTrail JSON,
3 heuristic detectors (impossible travel, brute-force sliding window,
high-risk IAM/EC2 APIs), AbuseIPDB enrichment (graceful degradation without a
key), Markdown incident-report output; 9 pytest tests; tunable thresholds via
CLI args.

| Skill domain | Level | One-line evidence |
|---|---|---|
| D7 Security automation & scripting | **L2** | Independently wrote a usable tool with CLI, error handling, 9 tests, and a README others can reproduce — hard evidence |
| D2 Log analysis & detection engineering | **L2 (synthetic)** | Self-written detection logic, tunable thresholds, positive/negative test cases; but all training data synthetic, geo heuristic explicitly demo-grade |
| D1 Security monitoring & alert triage | L1 | Knows triage concepts; the tool outputs findings, not triage decisions |

**Cert mapping**: GSEC — Python/log analysis is a GSEC hands-on plus;
Security+ — overlaps the automation/scripting domain.
**No inflation**: heuristics are simple, single data source (CloudTrail only),
limitations stated plainly in the README.

---

## P3 · 03-phishing-analysis-lab (phishing email analysis)

**What was done**: header-analysis cheatsheet (SPF/DKIM/DMARC quick reference);
an end-to-end walkthrough of one **reconstructed sample** (explicitly labeled
reconstructed): Received chain → sender spoofing → line-by-line auth results →
multi-layer URL decoding → attachment IOCs → severity → Tier-1 handling;
self-phishing test guide via GoPhish (own mailbox only, with compliance
boundaries); blank report template (refuses pre-filled fictional cases).

| Skill domain | Level | One-line evidence |
|---|---|---|
| D4 Phishing email analysis | **L2 (reconstructed)** | Walked the full "headers → auth → URL decoding → IOCs → verdict" flow independently with an evidence-weighted analysis; but the sample is reconstructed, not real phish volume |
| D3 Incident response & reporting | L1+ | Knows containment/forensics/escalation flow, wrote a handling playbook, no live-fire practice |

**Cert mapping**: GSEC / Security+ — phishing analysis is a shared Tier-1 core
skill for both, strong prep aid.
**Honesty note**: a Tier-1 analyst triages dozens of real phishes daily; the
author currently trains on reconstructed samples, not at real throughput.

---

## P4 · 04-rea-triage (ELF binary triage)

**What was done**: hand-written Python static-analysis tool: section entropy,
high-entropy segments, suspicious W^X segments, suspicious imports
(ptrace/memfd_create etc.), string-IOC regexes; weighted scoring → three-tier
verdict (benign/suspicious/malicious); 10 pytest tests; self-written synthetic
ELF generator for demos; methodology red line: triage signals ≠ conviction,
never execute samples.

| Skill domain | Level | One-line evidence |
|---|---|---|
| D5 Binary / malware triage | **L2 (synthetic)** | Independently wrote a triage tool with a scoring model and 10 tests; but ELF-only, static-only, all-synthetic samples, no real-malware analysis |
| D7 Security automation & scripting | **L2** | Second independent Python tool, pyelftools + pytest, complete evidence chain |

**Cert mapping**: GSEC — overlaps malware-analysis basics; OSCP — **no
mapping** (purely defensive, no exploitation content).
**Honesty note**: heuristics are coarse, obfuscated strings slip through;
README states "a starting point, not an AV verdict".

---

## P5 · 05-soc-skills (5 MIT agent skills)

**What was done**: distilled P1–P4's methodology into 5 agent skills
(alert-triage / incident-report / cloudtrail-ioc / phishing-analysis /
binary-triage), each declaring trigger conditions, workflow, output contract,
and refusal boundaries.

| Skill domain | Level | One-line evidence |
|---|---|---|
| — (meta capability) | — | Maps to no D1–D7 directly; evidences "methodology systematization + docs engineering", supporting the credibility of the P1–P4 L2 ratings |

**Why it matters**: P5 proves the author can turn hands-on practice into
reusable knowledge assets — exactly the trait SOC teams look for in Tier-1 →
Tier-2 promotion. HR-readable translation: "writes playbooks, can onboard
newcomers."

---

## Cert mapping summary (honest version)

| Cert | Relevance | Notes |
|---|---|---|
| **GSEC** (preparing) | Strong | 5 projects cover incident handling, log analysis, phishing, malware basics hands-on; **practice evidence** for prep, not "at GSEC level" |
| **Security+** | Medium | Covers threats/attacks, architecture, operations domains; missing governance/compliance and the multiple-choice knowledge surface |
| **OSCP** | Weak / none | Author's work is purely defensive; only P1's attack simulations give attacker-perspective primer; **the letters OSCP must not appear on the resume** |

## Anti-inflation checklist (pre-interview self-check)

- [ ] Never said "real incidents" — all samples labeled synthetic / reconstructed
- [ ] Never said "production experience" — L3 stays empty
- [ ] Never mentioned OSCP — a defensive author mentioning OSCP is interview suicide
- [ ] Every L2 has code / report / run-record evidence
- [ ] Has a concrete answer for "what was the hardest part" (P2's sliding window / P4's scoring model / P1's coverage-blind-spot analysis)
