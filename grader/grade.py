#!/usr/bin/env python3
"""
grade.py — soc-skills 评分器 harness（证据包收集器）

给定一个项目目录，自动收集：
  - README 全文
  - 文件清单（按 kind 分类：code / test / doc / data / config）
  - 关键文件的前 N 行（excerpts）

输出标准化的"证据包"JSON，可直接喂给 rubric-prompt.md。

不做评分本身（评分由使用者用 rubric-prompt 跑 LLM 完成），
harness 只负责把输入标准化、可复现。

用法：
    python grade.py <project_dir> [--head-lines 60] [--output evidence.json]
    python grade.py ~/workspace/soc-home-lab/02-python-ioc-analyzer --output /tmp/p2.json

退出码：0 成功；1 目录不存在；2 无 README。
"""

import argparse
import json
import os
import sys

# 不进证据包的目录/文件（依赖、缓存、版本控制）
SKIP_DIRS = {".venv", "venv", "__pycache__", ".pytest_cache", "node_modules",
             ".git", ".hg", "dist", "build", ".tox", ".mypy_cache"}
SKIP_FILES = {".DS_Store"}

# 按扩展名 + 路径关键词分类
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
    # 关键文件优先进 excerpts：主代码、测试、runbook、walkthrough、report
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

    # excerpts 按优先级关键词出现顺序 + 路径排序，保证稳定输出
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
    ap = argparse.ArgumentParser(description="收集项目证据包 JSON")
    ap.add_argument("project_dir", help="项目目录")
    ap.add_argument("--head-lines", type=int, default=60,
                    help="excerpts 截取行数（默认 60）")
    ap.add_argument("--output", "-o", default="-",
                    help="输出路径，- 表示 stdout（默认）")
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
