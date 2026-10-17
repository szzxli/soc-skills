# Grader v1 — AI Grader

Phase 2 deliverable: the TAXONOMY rubric encoded as an executable grading
prompt, plus an evidence-bundle collection harness, cross-validated against
the 5 home-lab projects.

## Files

| File | Purpose |
|---|---|
| `rubric-prompt.md` | Executable grading prompt: 7-domain rubric + 7 grading iron rules + output format + counter-examples. Paste the full text + evidence-bundle JSON into any LLM to grade |
| `grade.py` | Harness: given a project directory, collects the full README + file inventory (code/test/doc/data/config) + first N lines of key files, outputs a standardized evidence-bundle JSON |
| `validation.md` | v1.0 validation report: LLM graded the 5 projects per the prompt vs MAPPING.md human ratings — 14/15 domains matched, 1 deviation (P1-D3) within tolerance |
| `validation-v1.1.md` | v1.1 round (2026-10-16): re-graded with the behavioral dimension (§3b). Key finding: B2 (composure under injects) is "untested" across all 5 projects — the biggest evidence gap. P1-D3 downgrade to L1+ applied to MAPPING.md |
| `BENCHMARK.md` | Calibration anchors: 7 fixed evidence→grade cases (5 from the real validation round, 2 synthetic edge cases incl. injection). Run the grader on these to check for drift |

## Usage

```bash
# 1. Collect the evidence bundle
python3 grade.py ~/workspace/soc-home-lab/02-python-ioc-analyzer -o /tmp/p2.json

# 2. Paste rubric-prompt.md in full + /tmp/p2.json into an LLM; grade per §5 output format
# 3. Compare against existing human ratings (if any); deviations beyond ±1 band need explanation
```

`grade.py` flags: `--head-lines N` (excerpt line count, default 60), `-o/--output` (output path, default stdout).
venv / __pycache__ / .git auto-excluded.

## Output format (LLM outputs per prompt)

```
D<k> | <L1|L1+|L2>[(lab|synthetic|reconstructed)] | evidence: <file path>: <one-line evidence point> | upgrade: <what's missing for the next level, one line>
## Overall
## Honesty check
```

## Limitations (v1)

1. **No semantic verification**: the harness collects files only; it doesn't verify "the code actually runs" (e.g., whether tests pass). Spot-check `pytest` results manually.
2. **README honesty depends on the author**: if the author inflates "ran it by hand" in the README, the prompt can only take the evidence at face value. Mitigation: iron rules 6/7 (template ≠ output, expected ≠ observed) already block the two most common inflations; §4a (v1.2) blocks direct prompt-injection — but prompt hardening reduces, never eliminates, injection risk against a motivated adversary.
3. **D7 scope-suffix exemption**: see validation.md — D7 grades code craft, not lab/synthetic suffixes (to be formalized in TAXONOMY v1.1).
4. **L1+ is informal**: v1 prompt allows L1+ output, but TAXONOMY hasn't formally defined it (v1.1 candidate).
5. **No LLM API integration**: v1 is a "prompt + manual paste" flow; API integration (auto-calling models, batch runs) is later Phase 2 work.

## Versions

- v1.2 · 2026-10-17 · §4a injection resistance (evidence = untrusted data); BENCHMARK.md calibration anchors
- v1.0 · 2026-10-15 · first prompt + harness + 5-project cross-validation passed
