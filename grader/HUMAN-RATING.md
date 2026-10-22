# Blind human rating — protocol (help validate the rubric)

**Why this exists.** So far the rubric has only been checked against the
author's own 5 home-lab projects, rated by the author with the author's own
rubric. There is no independent human-rater comparison and no inter-rater
reliability data yet. This protocol collects that data in public.

## Who

Anyone who works (or has worked) in security operations: SOC analysts at any
tier, incident responders, detection engineers, SOC leads and hiring managers.

## Steps (about 20–30 minutes per sample)

1. **Pick one sample** evidence bundle (raw JSON, produced by `grader/grade.py`):
   - P1 [`evidence-01-mini-soc.json`](../web/samples/evidence-01-mini-soc.json)
   - P2 [`evidence-02-python-ioc-analyzer.json`](../web/samples/evidence-02-python-ioc-analyzer.json)
   - P3 [`evidence-03-phishing-analysis-lab.json`](../web/samples/evidence-03-phishing-analysis-lab.json)
   - P4 [`evidence-04-rea-triage.json`](../web/samples/evidence-04-rea-triage.json)
2. **Stay blind.** Before you submit, do not open the stored AI report for that
   sample: `grader/validation*.md`, `MAPPING.md`, `grader/BENCHMARK.md`,
   `PROFILE.md`, or the "Example" panel on the site.
3. **Rate with the rubric** in [`TAXONOMY.md`](../TAXONOMY.md) (domain levels;
   current rubric v1.3). For each domain the sample touches, give the level the
   *observable* evidence supports: `—`, `L1`, `L1+` (beyond L1, short of L2),
   `L2`, or `L3`. Mark domains the sample doesn't touch as "not rated".
4. **Cite the evidence** — the file or line that earned each level.
5. **Submit** with the issue form:
   [New blind rating](https://github.com/szzxli/soc-skills/issues/new?template=blind-rating.yml).
   The issue is public; use a handle you're comfortable publishing.

## What happens with the ratings

- Every rating stays public in its issue, agreeing or not.
- Once there are at least 3 independent ratings per sample, the project will
  publish per-domain agreement (human vs human, human vs AI, human vs author)
  in `grader/`, including disagreements and any rubric changes they cause.
- Until then, treat soc-skills levels as an unvalidated, advisory gap analysis.

## Known limits of this protocol

- Raters are self-selected and self-reported; experience is not verified.
- The samples are the author's own projects, so they are not a representative
  set of candidates.
- Bundles are excerpts (README + file inventory + first lines of key files),
  the same view the AI grader gets — not the full repositories.
