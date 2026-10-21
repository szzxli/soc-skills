# Stored example (keyless demo)

The "See an example profile" / "Try with sample evidence" flow on the site shows a
**stored grading report, not a live run**, so visitors can see the output without an API key.

- **Reports:** copied verbatim from [`grader/validation-v1.1.md`](../../grader/validation-v1.1.md)
  (P1–P4, graded 2026-10-16 with rubric-prompt v1.1). They are embedded in `web/index.html`
  (`EXAMPLE_REPORTS`) so the example works offline.
- **Evidence bundles** (`evidence-*.json`): produced offline by the real harness,
  `grader/grade.py` (unchanged since v1.1), run on the
  [soc-home-lab](https://github.com/szzxli/soc-home-lab) projects at commit
  `f965d5c` (2026-10-16, the last commit before the v1.1 validation round):

  ```bash
  git -C soc-home-lab worktree add /tmp/shl-1016 f965d5c
  for p in 01-mini-soc 02-python-ioc-analyzer 03-phishing-analysis-lab 04-rea-triage; do
    python3 grader/grade.py /tmp/shl-1016/$p -o web/samples/evidence-$p.json
  done
  ```

  "Load this evidence into the grader" puts the bundle into the grading textarea, so anyone
  with a free key can re-grade the same evidence live (current rubric v1.3) and compare.

All data is the project founder's own home-lab work; synthetic / reconstructed data is
labeled as such inside the bundles.
