#!/usr/bin/env python3
"""
grade.py — soc-skills grader harness (evidence-pack collector)

Given a project directory, automatically collects:
  - full README
  - file inventory (classified by kind: code / test / doc / data / config)
  - first N lines of key files (excerpts)

Outputs a standardized "evidence pack" JSON, ready to feed into rubric-prompt.md.

Does not grade (grading is done by the user running rubric-prompt through an LLM);
the harness only standardizes and reproduces the input.

Usage:
    python grade.py <project_dir> [--head-lines 60] [--output evidence.json]
    python grade.py ~/workspace/soc-home-lab/02-python-ioc-analyzer --output /tmp/p2.json

Exit codes: 0 success; 1 directory missing; 2 no README.
"""

import argparse
import json
import os
import sys

# Directories/files excluded from the evidence pack (deps, caches, VCS)
SKIP_DIRS = {".venv", "venv", "__pycache__", ".pytest_cache", "node_modules",
             ".git", ".hg", "dist", "build", ".tox", ".mypy_cache"}
SKIP_FILES = {".DS_Store"}

# Classify by extension + path keywords
def classify(path: str) -> str:
    p = path.lower()
    base = os.path.basename(p)
    if "test" in base or p.startswith("tests/") or "/tests/" in p:
        return "test"
    if base.endswith((".py", ".tf", ".sh", ".js", ".ts", ".go", ".rs")):
        return "code"
    if base.endswith((".json", ".yaml", ".yml", ".csv")) and "sample" in p:
        return "data"
    if base.endswith((".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".tfvars")):
        return "config"
    if base.endswith((".md", ".txt", ".rst")):
        return "doc"
    if base.endswith((".json", ".yaml", ".yml")):
        return "data"
    return "other"


def collect(project_dir: str, head_lines: int) -> dict:
    project_dir = os.path.abspath(project_dir)
    if not os.path.isdir(project_dir):
        print(f"error: not a directory: {project_dir}", file=sys.stderr)
        sys.exit(1)

    readme_path = os.path.join(project_dir, "README.md")
    if not os.path.isfile(readme_path):
        print(f"error: no README.md in {project_dir}", file=sys.stderr)
        sys.exit(2)
    with open(readme_path, encoding="utf-8", errors="replace") as f:
        readme = f.read()

    files, excerpts = [], []
    # Priority files go into excerpts first: main code, tests, runbooks, walkthroughs, reports
    priority_keywords = ("main.", "triage", "ioc_analyzer.py", "test_",
                         "runbook", "walkthrough", "report", "incident",
                         "skill.md", "cheatsheet", "architecture")
    for root, dirs, filenames in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn in SKIP_FILES:
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, project_dir)
            kind = classify(rel)
            if kind == "other":
                continue
            try:
                size = os.path.getsize(full)
                with open(full, encoding="utf-8", errors="replace") as f:
                    nlines = sum(1 for _ in f)
            except OSError:
                continue
            files.append({"path": rel, "kind": kind, "lines": nlines,
                          "bytes": size})
            if any(k in rel.lower() for k in priority_keywords):
                try:
                    with open(full, encoding="utf-8", errors="replace") as f:
                        head = "".join(f.readlines()[:head_lines])
                except OSError:
                    head = ""
                excerpts.append({"path": rel, "head": head})

    # Sort excerpts by priority-keyword match order + path for stable output
    excerpts.sort(key=lambda e: e["path"])

    n_code = sum(1 for f in files if f["kind"] == "code")
    n_test = sum(1 for f in files if f["kind"] == "test")
    notes = (f"{n_code} code files, {n_test} test files; "
             f"venv/cache/vcs excluded; excerpts={len(excerpts)}")

    return {
        "project": os.path.basename(project_dir.rstrip("/")),
        "readme": readme,
        "files": sorted(files, key=lambda f: f["path"]),
        "excerpts": excerpts,
        "notes": notes,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect a project evidence-pack JSON")
    ap.add_argument("project_dir", help="project directory")
    ap.add_argument("--head-lines", type=int, default=60,
                    help="excerpt line count (default 60)")
    ap.add_argument("--output", "-o", default="-",
                    help="output path, - means stdout (default)")
    args = ap.parse_args()

    pack = collect(args.project_dir, args.head_lines)
    out = json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=False)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"evidence pack written: {args.output} "
              f"({len(pack['files'])} files, {len(pack['excerpts'])} excerpts)",
              file=sys.stderr)


if __name__ == "__main__":
    main()
