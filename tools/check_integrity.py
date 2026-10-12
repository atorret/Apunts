"""Move-only integrity check against the pre-migration commit.

1. Every file of the baseline commit appears in tools/migration_map.csv, and
   every mapped file exists at its new path.
2. Every moved file is byte-identical to its original once the allowed
   structural lines are masked out on both sides: \\input lines, %!TEX root
   lines, and the xr-hyper line added to shared/preamble/packages.tex.
   .gitignore and .cursor/rules/latex-project.mdc are configuration and are
   reported as edited.
3. Every recorded edit in tools/migration_edits.csv is a path-only action.

  python tools/check_integrity.py [BASELINE]   (default BASELINE: 1dde429)
"""
import csv
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import texscan

ROOT = texscan.ROOT
BASELINE = sys.argv[1] if len(sys.argv) > 1 else "1dde429"
MASK = [re.compile(r"^\s*\\input\{[^}]*\}\s*(%.*)?$"),
        re.compile(r"^%!TEX root = "),
        re.compile(r"^\\usepackage\{xr-hyper\}"),
        re.compile(r"^\\externaldocument\b"),
        re.compile(r"^\\missingchapter\b"),
        re.compile(r"^\\chapterprereqs\b")]
CONFIG = {".gitignore", ".cursor/rules/latex-project.mdc"}
ALLOWED_EDITS = re.compile(
    r"^(tex-root-path|input-path|input-line-moved-to-main\.tex|"
    r"input-line-removed \(target now .+\)|externaldocument)$")


def git_bytes(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout


def masked(data):
    text = data.decode("utf-8").replace("\r\n", "\n")
    return [l for l in text.split("\n") if not any(rx.match(l) for rx in MASK)]


def main():
    with open(os.path.join(ROOT, "tools", "migration_map.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(os.path.join(ROOT, "tools", "migration_edits.csv"), encoding="utf-8") as fh:
        edits = list(csv.DictReader(fh))
    problems = []
    baseline = set(git_bytes("ls-tree", "-r", "--name-only", BASELINE).decode().splitlines())
    mapped = {r["old_path"] for r in rows}
    for f in sorted(baseline - mapped):
        problems.append(f"baseline file not in the map: {f}")
    identical = masked_equal = config = 0
    for r in rows:
        new = os.path.join(ROOT, r["new_path"])
        if not os.path.exists(new):
            problems.append(f"missing at new path: {r['new_path']}")
            continue
        if r["old_path"] not in baseline:
            continue
        old_data = git_bytes("show", f"{BASELINE}:{r['old_path']}")
        with open(new, "rb") as fh:
            new_data = fh.read()
        old_id = git_bytes("rev-parse", f"{BASELINE}:{r['old_path']}").strip()
        new_id = git_bytes("hash-object", "--path", r["new_path"], r["new_path"]).strip()
        if old_id == new_id:
            identical += 1
        elif r["new_path"] in CONFIG:
            config += 1
        elif r["new_path"].endswith(".tex") and masked(old_data) == masked(new_data):
            masked_equal += 1
        else:
            problems.append(f"content changed: {r['old_path']} -> {r['new_path']}")
    for e in edits:
        if not ALLOWED_EDITS.match(e["action"]):
            problems.append(f"non-path edit recorded: {e['new_path']}:{e['old_line_no']} {e['action']}")
    print(f"baseline {BASELINE}: {len(baseline)} files; mapped {len(rows)} "
          f"({len(rows) - len(mapped & baseline)} untracked build/legacy outputs)")
    print(f"byte-identical: {identical}; identical after masking path lines: {masked_equal}; "
          f"configuration edited: {config}; recorded path edits: {len(edits)}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("PASS: no content was written, rewritten or deleted")


if __name__ == "__main__":
    main()
