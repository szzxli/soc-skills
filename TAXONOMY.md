# SOC Skill Taxonomy (TAXONOMY)

> Skeleton v1.0 · 2026-10-15
> Basis: NIST NICE Cybersecurity Workforce Framework (published by the U.S.
> Department of Commerce, NIST; current v2.0.0). NICE describes cybersecurity
> work in a common language: Work Role Category → Work Role → Task / Knowledge
> / Skill (TKS statements). This taxonomy takes the subset directly relevant to
> **SOC analyst / detection & response** job-seeking and rewrites it as
> observable, gradable hands-on dimensions. Direct NICE quotations are marked;
> the rest is this project's job-seeker-oriented rewrite.

## NICE anchors

| This taxonomy | NICE Work Role (ID) | NICE category |
|---|---|---|
| D1 Security monitoring & alert triage | Cyber Defense Analyst (PR-CDA-001) | Protect and Defend |
| D2 Log analysis & detection engineering | Cyber Defense Analyst (PR-CDA-001) | Protect and Defend |
| D3 Incident response & reporting | Cyber Defense Incident Responder (PR-CIR-001) | Protect and Defend |
| D4 Phishing email analysis | Cyber Defense Analyst (PR-CDA-001) | Protect and Defend |
| D5 Binary / malware triage | Cyber Defense Analyst (PR-CDA-001) | Protect and Defend |
| D6 Cloud security (AWS) hands-on | Cyber Defense Analyst (PR-CDA-001) | Protect and Defend |
| D7 Security automation & scripting | Cross-role capability (programming/scripting KSAs across NICE roles) | — |

Source: NICE Framework v2.0.0 work role listing (niccs.cisa.gov / NIST NICE
pages); PR-CDA-001 / PR-CIR-001 definitions per official NICE work role
descriptions.

## Level definitions (three tiers)

### L1 · Foundational
Can explain concepts, follow a runbook end to end, complete labs with guidance.
**Observable evidence**: lab notes, cheatsheets, guided walkthroughs,
course/training completion records.
**One-line test**: "Hand her a playbook and she can walk through it."

### L2 · Independent
Completes end-to-end workflows with no guidance; handles unseen data/samples;
output meets analyst-readable bar; writes tested code tools. **Scope must be
labeled**: lab (self-built environment) / synthetic (generated data) /
reconstructed (reproduced samples) — strictly distinguished from production
(real alerts/incidents).
**Observable evidence**: original tools (with tests), independently completed
analysis reports, self-built lab environments + run records.
**One-line test**: "Hand her a new sample and she produces a report alone."

### L3 · Production
Has carried on-call / SLA / real alert volume in a production environment;
handled real incidents; mentored people or shipped production detections.
**Observable evidence**: employment records, real incident retrospectives
(sanitized), production detection rules shipped.
**One-line test**: "She has pulled shifts in a real SOC."
> Project v1 rule: the L3 column stays permanently empty. This is the honesty
> line — a zero-experience career changer's profile must never show L3.

## Seven skill domains × three-tier rubric

### D1 · Security monitoring & alert triage
- **L1**: Can describe the triage flow (receive → prioritize → assess →
  contain/escalate); uses a severity model (low/medium/high/critical); can work
  sample alerts from a triage guide.
- **L2**: Has built a monitoring environment with real detection sources
  (SIEM/cloud-native detection) independently; completed the full
  "alert → logs → severity → contain/escalate" chain alone; written triage
  playbooks.
- **L3**: Worked a real alert queue in a production SOC (including false
  positives and alert fatigue); participated in on-call rotations.

### D2 · Log analysis & detection engineering
- **L1**: Reads common audit-log fields (who / what / when / where); does basic
  retrieval with grep / jq / consoles.
- **L2**: Has written runnable detection logic against audit logs (heuristic
  rules/scripts); logic has tunable thresholds and test cases; can explain
  sensor coverage blind spots (what attacks current detections miss).
- **L3**: Wrote/tuned detection rules in production; traded off rule false-
  positive rates against coverage.

### D3 · Incident response & reporting
- **L1**: Can describe the IR lifecycle; fills report templates.
- **L2**: Independently completed a "simulated attack → forensics →
  containment → retrospective" loop with a structured incident report
  (timeline, evidence, root cause, improvements); report meets the "readable by
  someone who wasn't there" bar.
- **L3**: Participated in real incident response (containment-decision pressure,
  cross-team coordination).

### D4 · Phishing email analysis
- **L1**: Reads key email-header fields; explains SPF / DKIM / DMARC; walks an
  analysis flow from a cheatsheet.
- **L2**: Independently completed full phishing analysis (headers →
  authentication → URL decoding → attachment IOCs → severity → handling
  recommendation) with evidence-weighted, confidence-scored verdicts; ran
  self-phishing tests compliantly (own mailbox only).
- **L3**: Triaged real phishing mail at production volume; ran phishing
  simulations or user education.

### D5 · Binary / malware triage
- **L1**: Explains static vs dynamic analysis; knows common suspicious
  indicators (packing, high entropy, sensitive APIs).
- **L2**: Has written a runnable static triage tool (with scoring/grading logic
  and tests); holds the "triage signals ≠ conviction" methodology; can explain
  heuristic false-positive boundaries.
- **L3**: Analyzed real malware samples (sandbox dynamic analysis, family
  attribution).

### D6 · Cloud security (AWS) hands-on
- **L1**: Explains what CloudTrail / GuardDuty / Security Hub each do.
- **L2**: Built an audited, threat-detected cloud environment from IaC
  independently; ran attack simulations by hand and saw real detections;
  configured least privilege.
- **L3**: Production cloud security operations (multi-account, real threats,
  cost and compliance constraints).

### D7 · Security automation & scripting
- **L1**: Writes basic Python scripts for text/JSON; knows what requests /
  pytest do.
- **L2**: Independently wrote tools solving real analysis pain points (CLI
  args, error handling, test coverage); code has a README others can run to
  reproduce.
- **L3**: Production-grade automation (CI, code review, long-term maintenance,
  multi-person collaboration).

## Grading iron rules

1. **Evidence first**: every level needs observable evidence; no evidence, no
   credit.
2. **Scope suffix**: L2 must carry `(lab)` / `(synthetic)` / `(reconstructed)`,
   never omitted. **Exception (v1.1)**: D7 (automation & scripting) grades code
   craft, not data/environment properties — bare L2, no suffix. Tagging "wrote
   a CLI tool" as (synthetic) is a semantic mismatch.
3. **L3 stays empty**: in v1, nobody (including the project author) self-rates L3.
4. **Downgrade on ambiguity**: when evidence is fuzzy, take the lower grade.
