"""Chapter-level dependency graph from actual \\ref usage (markdown on stdout).

Each row: source chapter -> target chapter (number of references), with the
direction relative to the reading order: back (target read earlier), forward,
or reference (GLOSSARY / unsorted).
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structure_config import ancestors
import texscan


def direction(src, tgt, order):
    if tgt[0] in ("GLOSSARY", "Unsorted") or src[0] in ("GLOSSARY", "Unsorted"):
        return "reference"
    if src[0] == tgt[0]:
        return "back" if order.get(tgt, 1e9) < order.get(src, 1e9) else "forward"
    return "back" if tgt[0] in ancestors(src[0]) else "forward"


def edges():
    s = texscan.scan()
    order, ids = texscan.reading_order()
    c = Counter()
    for f, n, cmd, lab in s.refs:
        if lab not in s.labels:
            continue
        src, tgt = s.chapter[f], s.chapter[s.labels[lab][0][0]]
        if src != tgt:
            c[(src, tgt)] += 1
    return c, order, ids


def name(k, ids):
    return ids.get(k, f"{k[0]}/{k[1]}")


def main():
    c, order, ids = edges()
    print("| from | to | refs | direction |")
    print("|---|---|---|---|")
    for (src, tgt), n in sorted(c.items(), key=lambda kv: (order.get(kv[0][0], 1e9), order.get(kv[0][1], 1e9))):
        print(f"| {name(src, ids)} | {name(tgt, ids)} | {n} | {direction(src, tgt, order)} |")


if __name__ == "__main__":
    main()
