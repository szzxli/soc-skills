#!/usr/bin/env python3
"""Evaluator Independence Benchmark - analysis tool.

Reads the sealed sample set (samples.json) and two judge result files
(same-family and cross-family), and reports how far each judge group
drifted from the reference verdicts, plus the same-family uplift.

Pure standard library. See PROTOCOL.md for the design, the judge
result file format, and how to run a real measurement.

Usage:
  python3 analyze.py [--samples samples.json]
                     [--same results/same-family.json]
                     [--cross results/cross-family.json]
                     [--out SUMMARY.md]
  python3 analyze.py --judge-view judge-view.json
  python3 analyze.py --selfcheck
"""

import argparse
import json
import sys
from pathlib import Path

LEVEL_VALUES = {"none": 0.0, "L1": 1.0, "L1+": 1.5, "L2": 2.0}
PASS_THRESHOLD = 2.0
SEALED_KEYS = ("tier", "reference_verdict", "reference_rationale")
HERE = Path(__file__).resolve().parent


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def level_value(raw, where):
    if not isinstance(raw, str):
        fail(f"{where}: level must be a string, got {raw!r}")
    key = raw.strip()
    if key.lower() == "none":
        key = "none"
    if key.upper() == "L3":
        fail(f"{where}: L3 is not a valid judge output (protocol violation)")
    if key not in LEVEL_VALUES:
        fail(f"{where}: unknown level {raw!r}; expected one of "
             f"{sorted(LEVEL_VALUES)}")
    return LEVEL_VALUES[key]


def load_json(path, what):
    p = Path(path)
    if not p.exists():
        fail(f"{what} file not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{what} file is not valid JSON ({p}): {e}")


def load_samples(path):
    data = load_json(path, "samples")
    samples = data.get("samples")
    if not isinstance(samples, list) or not samples:
        fail(f"samples file {path}: missing non-empty 'samples' list")
    refs = {}
    for s in samples:
        sid = s.get("id")
        if not sid:
            fail(f"samples file {path}: a sample has no 'id'")
        if sid in refs:
            fail(f"samples file {path}: duplicate sample id {sid}")
        rv = s.get("reference_verdict") or {}
        refs[sid] = level_value(rv.get("level"),
                                 f"samples {sid} reference_verdict")
    return data, refs


def load_results(path, refs, what):
    data = load_json(path, what)
    grades = data.get("grades")
    if not isinstance(grades, list) or not grades:
        fail(f"{what} file {path}: missing non-empty 'grades' list")
    judged = {}
    for g in grades:
        sid = g.get("sample_id")
        if sid not in refs:
            fail(f"{what} file {path}: unknown sample_id {sid!r}")
        if sid in judged:
            fail(f"{what} file {path}: duplicate grade for {sid}")
        judged[sid] = level_value(g.get("level"), f"{what} {sid}")
    missing = sorted(set(refs) - set(judged))
    if missing:
        fail(f"{what} file {path}: missing grades for samples {missing}")
    return data, judged


def group_stats(refs, judged):
    n = len(refs)
    deltas = [judged[s] - refs[s] for s in refs]
    return {
        "n": n,
        "mean_level": sum(judged.values()) / n,
        "mean_delta": sum(deltas) / n,
        "pass_rate": sum(1 for v in judged.values()
                         if v >= PASS_THRESHOLD) / n,
        "hit_rate": sum(1 for s in refs if judged[s] == refs[s]) / n,
    }


def pct(x):
    return f"{x * 100:.1f}%"


def build_summary(samples_meta, refs, same_meta, same, cross_meta, cross):
    ref_pass = sum(1 for v in refs.values()
                   if v >= PASS_THRESHOLD) / len(refs)
    uplift = same["mean_delta"] - cross["mean_delta"]
    pass_gap = same["pass_rate"] - cross["pass_rate"]
    illustrative = any(
        (m or {}).get("data_status") == "illustrative"
        for m in (same_meta, cross_meta))
    lines = []
    if illustrative:
        lines += [
            "> **ILLUSTRATIVE - NOT MEASURED DATA.**",
            "> These judge outputs were hand-constructed to demonstrate",
            "> the analysis pipeline. They are not scores produced by",
            "> real judges and must not be quoted as results.",
            "",
        ]
    lines += [
        "# Evaluator Independence Benchmark - Summary",
        "",
        f"Samples: {len(refs)} (benchmark v{samples_meta.get('version', '?')}); "
        f"reference pass rate {pct(ref_pass)}.",
        "",
        "| Judge group | Judge model | Mean level | Mean delta vs reference "
        "| Pass rate | Reference hit rate |",
        "|---|---|---|---|---|---|",
    ]
    for label, meta, st in (("same-family", same_meta, same),
                            ("cross-family", cross_meta, cross)):
        lines.append(
            f"| {label} | {(meta or {}).get('judge_model', '?')} "
            f"| {st['mean_level']:.3f} | {st['mean_delta']:+.3f} "
            f"| {pct(st['pass_rate'])} | {pct(st['hit_rate'])} |")
    lines += [
        "",
        f"- **Same-family uplift** (same-family mean delta minus "
        f"cross-family mean delta): **{uplift:+.3f} levels**",
        f"- **Pass-rate gap** (same-family minus cross-family): "
        f"**{pass_gap * 100:+.1f} percentage points**",
        "",
        "Positive uplift = the same-family judge graded more leniently "
        "than the cross-family judge against identical sealed references. "
        "See PROTOCOL.md for method, controls, and limitations.",
    ]
    return "\n".join(lines) + "\n", illustrative


def make_judge_view(samples_data):
    view = {"benchmark": samples_data.get("benchmark"),
            "version": samples_data.get("version"),
            "samples": [{"id": s["id"], "domain": s["domain"],
                         "evidence": s["evidence"]}
                        for s in samples_data["samples"]]}
    text = json.dumps(view, ensure_ascii=False)
    for key in SEALED_KEYS:
        if f'"{key}"' in text:
            fail(f"internal error: sealed key {key} leaked into judge view")
    return view


def selfcheck(samples_path):
    data, refs = load_samples(samples_path)
    tiers = {}
    for s in data["samples"]:
        tier = s.get("tier")
        if tier not in ("meets-bar", "inflated", "insufficient"):
            fail(f"selfcheck: sample {s.get('id')} has bad tier {tier!r}")
        tiers[tier] = tiers.get(tier, 0) + 1
        rv = s["reference_verdict"]
        expect_pass = refs[s["id"]] >= PASS_THRESHOLD
        if bool(rv.get("pass")) != expect_pass:
            fail(f"selfcheck: sample {s['id']} pass flag inconsistent "
                 f"with reference level {rv.get('level')}")
    if len(refs) < 12:
        fail(f"selfcheck: need at least 12 samples, found {len(refs)}")
    view = make_judge_view(data)
    for s in view["samples"]:
        if set(s) != {"id", "domain", "evidence"}:
            fail(f"selfcheck: judge view sample keys wrong: {sorted(s)}")
    print(f"selfcheck OK: {len(refs)} samples; tiers {tiers}; "
          f"reference mean level "
          f"{sum(refs.values()) / len(refs):.3f}; "
          f"reference pass rate "
          f"{pct(sum(1 for v in refs.values() if v >= PASS_THRESHOLD) / len(refs))}; "
          f"judge view strips all sealed fields")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Evaluator Independence Benchmark analysis")
    ap.add_argument("--samples", default=str(HERE / "samples.json"))
    ap.add_argument("--same", help="same-family judge results JSON")
    ap.add_argument("--cross", help="cross-family judge results JSON")
    ap.add_argument("--out", help="also write the Markdown summary here")
    ap.add_argument("--judge-view", metavar="PATH",
                    help="write the blinded judge view JSON and exit")
    ap.add_argument("--selfcheck", action="store_true",
                    help="validate samples + judge-view stripping and exit")
    args = ap.parse_args(argv)

    if args.selfcheck:
        return selfcheck(args.samples)

    samples_data, refs = load_samples(args.samples)

    if args.judge_view:
        view = make_judge_view(samples_data)
        Path(args.judge_view).write_text(
            json.dumps(view, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print(f"judge view written: {args.judge_view} "
              f"({len(view['samples'])} samples, sealed fields stripped)")
        return 0

    if not args.same or not args.cross:
        fail("both --same and --cross result files are required "
             "(or use --selfcheck / --judge-view)")

    same_meta, same_judged = load_results(args.same, refs, "same-family")
    cross_meta, cross_judged = load_results(args.cross, refs, "cross-family")
    same_stats = group_stats(refs, same_judged)
    cross_stats = group_stats(refs, cross_judged)
    summary, _ = build_summary(samples_data, refs, same_meta, same_stats,
                               cross_meta, cross_stats)
    print(summary, end="")
    if args.out:
        Path(args.out).write_text(summary, encoding="utf-8")
        print(f"summary written: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
