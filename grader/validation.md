# Phase 2 Validation Report

> Method: the grader (LLM) executed `rubric-prompt.md` §3–§6 strictly;
> evidence taken only from `grade.py` evidence bundles (full README + file
> inventory + excerpts). Baseline: `../MAPPING.md` human ratings (ground
> truth). Pass bar: per-item deviation within ±1 band (L1+ counts as a half
> band between L1 and L2).

---

## P1 · 01-mini-soc

| Domain | rubric-prompt grade | MAPPING | Match |
|---|---|---|---|
| D1 | **L2 (lab)** ｜ evidence: README states 3 attack simulations run by hand with findings seen in GuardDuty; self-written triage-guide.md | L2 (lab) | ✅ match |
| D2 | **L1+** ｜ evidence: reads CloudTrail, explains GuardDuty vs CloudTrail coverage blind spots (architecture.md/triage-guide.md), never wrote detection logic | L1+ | ✅ match |
| D3 | **L1+** ｜ evidence: incident-reports/ holds **only blank templates** (report-template.md), no filled incident reports; rule 6 (template ≠ output) blocks L2 | L2 (lab) | ⚠️ half-band deviation |
| D6 | **L2 (lab)** ｜ evidence: terraform/main.tf full-stack IaC; README states hand-run apply/destroy; multi-region Trail + encrypted log bucket + least-privilege IAM | L2 (lab) | ✅ match |
| D7 | **L1** ｜ evidence: used Terraform and off-the-shelf tools, no self-written analysis code | L1 | ✅ match |

**P1-D3 deviation note**: MAPPING's L2 (lab) rested on "self-written containment playbook + escalation criteria, report template up to bar". But rubric rule 6 is explicit: a blank template is not evidence of "having produced a structured incident report"; the attack-runbook's own "expected findings…expected, not observed" (rule 7) further weakens "loop completed". **Recommended fix**: downgrade MAPPING to L1+ until the author hand-fills one detonation incident report, then restore L2 (lab). This is the rubric working as intended — not tuning scores to pass, but exposing an evidence gap.

## P2 · 02-python-ioc-analyzer

| Domain | rubric-prompt grade | MAPPING | Match |
|---|---|---|---|
| D7 | **L2** ｜ evidence: self-written ioc_analyzer.py CLI (args, error handling); tests/test_analyzer.py, 9 tests; README reproducible by others | L2 | ✅ match |
| D2 | **L2 (synthetic)** ｜ evidence: 3 self-written heuristic detectors, tunable thresholds, positive/negative tests; sample_data explicitly synthetic | L2 (synthetic) | ✅ match |
| D1 | **L1** ｜ evidence: tool outputs findings, not triage decisions; knows triage concepts but never triaged | L1 | ✅ match |

## P3 · 03-phishing-analysis-lab

| Domain | rubric-prompt grade | MAPPING | Match |
|---|---|---|---|
| D4 | **L2 (reconstructed)** ｜ evidence: sample-walkthrough.md walks the full headers→auth→URL decoding→IOCs→verdict flow independently with evidence weighting; sample explicitly labeled reconstructed | L2 (reconstructed) | ✅ match |
| D3 | **L1+** ｜ evidence: knows the IR flow, wrote a handling playbook, no live-fire practice, no filled reports | L1+ | ✅ match |

Upgrade suggestion (D4 → stronger L2): actually run one self-phishing test per the gophish-selftest-guide and write it up — graduate from "reconstructed sample" to "real delivery + real analysis".

## P4 · 04-rea-triage

| Domain | rubric-prompt grade | MAPPING | Match |
|---|---|---|---|
| D5 | **L2 (synthetic)** ｜ evidence: self-written triage.py static triage tool (entropy/W^X/suspicious imports/string IOCs + weighted scoring, three-tier verdict); tests/test_triage.py, 10 tests; README holds "triage signals ≠ conviction" | L2 (synthetic) | ✅ match |
| D7 | **L2** ｜ evidence: second independent Python tool, pyelftools + pytest, complete evidence chain | L2 | ✅ match |

## P5 · 05-soc-skills

| Domain | rubric-prompt grade | MAPPING | Match |
|---|---|---|---|
| — | **Not gradable by domain** ｜ the 5 SKILL.md files are methodology distillations; they don't map to D1–D7 directly; they support the credibility of the P1–P4 L2 ratings | — (meta capability) | ✅ match |

---

## Summary

- 14 of 15 comparable domains **fully matched**; 1 deviation (P1-D3: L1+ vs L2 (lab)), within the ±1 band tolerance.
- **Verdict: PASS.** The rubric-prompt reproduces MAPPING's human ratings and was **stricter** at D3 — exactly what we want: the AI grader should be an evidence-gap detector, not a human-rating parrot.
- The deviating item has a clear fix path (fill one real detonation report → L2); no score-tuning to pass.

## Honesty check (this round)
- [x] Every L2 cites evidence (file path + point)
- [x] No L3
- [x] No OSCP mentioned
- [x] Templates/expected results not counted as output evidence (P1-D3 was blocked for exactly this)

## Rubric revision candidates (v1.1)

1. **D7 scope-suffix exemption** (already landed as the §4 rule 3 exception in this round): TAXONOMY iron rule 2 requires "every L2 carries a scope suffix", but lab/synthetic/reconstructed describe **data/environment** properties while D7 grades **code craft** — tagging "wrote a CLI tool" as (synthetic) is a semantic mismatch. Recommend formalizing in TAXONOMY v1.1.
2. **Formalize "L1+"**: used 3 times this round (P1-D2, P1-D3, P3-D3) — "beyond L1 but short of L2" is a high-frequency state. Recommend a v1.1 definition: "meets all of L1 + touches some L2 criteria but lacks key output evidence", with the missing criterion named (e.g., P1-D3 lacks "a filled report").
