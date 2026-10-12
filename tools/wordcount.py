"""Per-document word counts (chapters + exercises; figures and scaffolding excluded).

  python tools/wordcount.py          table on stdout
  python tools/wordcount.py --json   machine-readable
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from books import CONTENT_DOCS
import texscan


def counts():
    s = texscan.scan()
    per = {d: 0 for d in CONTENT_DOCS + ["GLOSSARY", "unsorted"]}
    for f, (doc, drel) in s.files.items():
        top = drel.split("/")[0]
        if doc in CONTENT_DOCS and top not in ("chapters", "exercises"):
            continue
        per[doc] += s.words[f]
    return per


def main():
    per = counts()
    content = {d: per[d] for d in CONTENT_DOCS}
    mean = sum(content.values()) / len(content)
    lo, hi = 0.85 * mean, 1.15 * mean
    if "--json" in sys.argv:
        print(json.dumps({"per": per, "mean": mean, "lo": lo, "hi": hi}))
        return
    print(f"{'doc':10} {'words':>7} {'vs mean':>8}  band")
    for d in CONTENT_DOCS:
        w = content[d]
        print(f"{d:10} {w:7d} {100 * (w - mean) / mean:+7.0f}%  {'ok' if lo <= w <= hi else 'OUT'}")
    print(f"{'mean':10} {mean:7.0f}   band {lo:.0f}-{hi:.0f}")
    print(f"{'GLOSSARY':10} {per['GLOSSARY']:7d}  (reference document, outside the balance rule)")
    print(f"{'unsorted':10} {per['unsorted']:7d}")


if __name__ == "__main__":
    main()
