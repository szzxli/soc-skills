# Evaluator Independence Benchmark · Protocol v0.1

> Question: when an AI judge grades work produced inside its own model
> family, how much higher are the grades than when an independent
> (cross-family) judge grades the same work with the same prompt?
> This benchmark exists to put a number on that gap, so the
> evaluator-independence rule carried in rubric domain D8 ("the operator
> never grades their own agent") rests on measured data instead of
> intuition.

## Status

- **Apparatus: ready.** Samples, judge prompt, and analysis script are
  complete and self-tested.
- **Measured results: none yet.** No cross-family judge has scored the
  sample set, so there is no measured uplift figure to report.
- `results-illustrative/` contains a worked example built from
  **hand-constructed, illustrative judge outputs (NOT measured data)**.
  It proves the pipeline runs end to end and shows the output format.
  It must never be quoted as a result.
- Real measurement is **awaiting cross-family judge scores** (see
  "Running a real measurement").

## Hypothesis

- H1: a judge from the same model family as the work's producer awards
  systematically higher levels than the sealed reference verdicts
  (positive mean grade delta).
- H2: a cross-family judge's mean grade delta against the same
  reference verdicts is closer to zero.
- The **same-family uplift** = mean delta (same-family judge) −
  mean delta (cross-family judge). Uplift > 0 supports H1/H2.

## Design

Two judge groups grade the identical sample set with the identical
judge prompt (`judge-prompt.md`). The only variable is the judge:

| Group | Judge | Input |
|---|---|---|
| same-family | a model from the same family that produced the samples | judge view of `samples.json` |
| cross-family | a model from a different family | judge view of `samples.json` |

Controls:

- **Blinding.** Judges receive only the judge view (`id`, `domain`,
  `evidence`). Producer identity, quality tier, and reference verdicts
  are stripped before anything is sent to a judge.
- **Sealed references.** Reference verdicts live only in `samples.json`
  (fields `tier`, `reference_verdict`, `reference_rationale`). They are
  written before any judge run and are never shown to a judge.
- **One prompt.** Both groups use `judge-prompt.md` verbatim. Any prompt
  change invalidates prior runs; re-run both groups.
- **Fixed scale.** Judges output one level per sample on the rubric
  scale in "Scoring scale".

## Samples

`samples.json` holds 12 short evidence excerpts in SOC-project style,
each targeting one rubric domain (D1–D8 represented). Reference
composition:

| Reference tier | Count | Reference levels |
|---|---|---|
| Meets the bar | 4 | L2 (with scope suffix where the rubric requires one) |
| Inflated presentation, partial substance | 4 | L1+ |
| Clearly insufficient | 4 | L1 or none |

The inflated tier is the diagnostic core: polished claims whose
observable evidence only supports L1/L1+ (template-only artifacts,
"expected" findings presented as observed, self-declared proof). A
judge that rewards presentation over evidence shows its inflation
exactly there.

## Scoring scale

Levels follow `../rubric-prompt.md` (§3, §4). Numeric mapping used by
`analyze.py`:

| Level | Value | Meaning |
|---|---|---|
| none (not covered) | 0.0 | no creditable evidence |
| L1 | 1.0 | describes / follows a guide |
| L1+ | 1.5 | beyond L1, short of L2 (rubric rule 2) |
| L2 | 2.0 | independent, runnable, evidenced work |

**Pass** = level ≥ 2.0 (meets the L2 bar). L3 is never a valid judge
output (rubric rule 4); a run that emits L3 is discarded as a protocol
violation.

## Metrics (`analyze.py`)

For each judge group, against the sealed references:

- **Mean level** — average numeric level awarded.
- **Mean grade delta** — mean of (judged − reference); positive =
  inflation, negative = harshness.
- **Pass rate** — share of samples judged ≥ L2; compared with the
  reference pass rate (4/12).
- **Reference hit rate** — share of samples whose judged level exactly
  equals the reference level (scope suffix ignored).

Headline outputs: the **same-family uplift** (difference of mean
deltas) and the **pass-rate gap** (same-family pass rate −
cross-family pass rate).

## Judge result file format

One JSON file per judge group per run:

```json
{
  "judge_group": "same-family",
  "judge_model": "<model name + version, as reported by the operator>",
  "producer_family": "<family that produced the samples>",
  "data_status": "measured",
  "run_date": "YYYY-MM-DD",
  "grades": [
    {"sample_id": "S01", "level": "L2", "scope": "synthetic",
     "reason": "one line"}
  ]
}
```

`scope` is required when level is L2 and the domain is not D7
(rubric rule 3); use `null` otherwise. `data_status` is `"measured"`
for real runs and `"illustrative"` for constructed examples —
`analyze.py` prints a NOT MEASURED banner whenever any input is
illustrative.

## Running a real measurement

1. Generate the judge view:
   `python3 analyze.py --judge-view judge-view.json`
   (contains only `id`, `domain`, `evidence` — safe to send out).
2. Run the **same-family** judge: open a session of a model from the
   producer family, paste `judge-prompt.md` + the judge view, save the
   returned JSON as `results/same-family.json` with `data_status` set
   to `"measured"` and the real model name recorded.
3. Run the **cross-family** judge: hand `judge-prompt.md` + the same
   judge view to an operator of a different model family (for example
   a Manus or Grok session). They must not see `samples.json` or any
   reference material. Save the returned JSON as
   `results/cross-family.json`, same format.
4. Analyse: `python3 analyze.py --same results/same-family.json
   --cross results/cross-family.json --out results/SUMMARY.md`.
5. **Repeat the full run at least 3 times per group** and report the
   mean and spread of the uplift across runs; a single run is a pilot,
   not a result.

## Contamination rules

- Never send `samples.json` itself to a judge — only the judge view.
- Never tell a judge which group it is in, who produced the samples,
  or what any other judge scored.
- If a sample's evidence text is edited, all prior runs are stale:
  bump the benchmark version in `samples.json` and re-run both groups.
- Reference verdicts may be challenged only before a run, in writing,
  in this file's change log — never after seeing judge output.

## Limitations (read before quoting anything)

- **n = 12.** Small sample; treat any single-run uplift as indicative,
  not conclusive. The set should grow before strong claims are made.
- **Judge variance.** LLM judges are stochastic; one run per group can
  swing on sampling alone. Hence the ≥3 repetitions rule.
- **Coarse scale.** Four numeric levels compress real differences;
  hit rate and delta are summaries, not proof of intent.
- **One producer family.** Samples were authored in one working style;
  uplift measured here may not transfer to other producers.
- **Prompt sensitivity.** Results are conditional on
  `judge-prompt.md`; a stricter or looser prompt moves both groups.

## Change log

- v0.1 — apparatus built; illustrative example generated; awaiting
  first measured cross-family run.
