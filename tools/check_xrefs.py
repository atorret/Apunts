"""Cross-document reference checks; writes /CROSS_REFERENCES.md.

Static: every label defined once, every \\ref/\\eqref/\\pageref/\\nameref and
glossary pointer resolves, every \\cite key is in the bibliography.
Build: no undefined / multiply defined / changed labels / missing external
.aux in any of the 12 logs. Links: every external PDF target and every
relative link in the root .md files exists. Consistency: every reference
across documents is classified (back / forward / reference) and every
chapter's \\chapterprereqs covers the earlier chapters it refers back to.
Exit status 1 if a static, build or link check fails (forward references are
reported, not failures).
"""
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structure_config import CONTENT_DOCS, FOLDER, JOB, MAINFILE, BUILD_ORDER, BODY, ancestors
import texscan
from xref_graph import direction

ROOT = texscan.ROOT
OUT = os.path.join(ROOT, "CROSS_REFERENCES.md")
LOG_PATTERNS = [
    ("undefined reference", re.compile(r"Reference `[^']+' on page \d+ undefined|There were undefined references")),
    ("multiply defined label", re.compile(r"multiply defined")),
    ("labels may have changed", re.compile(r"Label\(s\) may have changed")),
    ("missing external .aux", re.compile(r"^No file .*\.aux", re.M)),
    ("undefined citation", re.compile(r"Citation `[^']+' on page \d+ undefined")),
    ("missing link destination", re.compile(r"has been referenced but does not exist")),
]
ALL = CONTENT_DOCS + ["GLOSSARY", "Unsorted"]


def main():
    s = texscan.scan(include_mains=True)
    order, ids = texscan.reading_order()
    failures = []

    # --- static
    dups = {l: v for l, v in s.labels.items() if len(v) > 1}
    for l, v in dups.items():
        failures.append(f"label `{l}` defined {len(v)} times: {v}")
    unresolved = [(f, n, c, l) for f, n, c, l in s.refs if l not in s.labels]
    for f, n, c, l in unresolved:
        failures.append(f"{f}:{n}: \\{c}{{{l}}} has no target")
    badcites = [(f, n, k) for f, n, k in s.cites if k not in s.bibitems]
    for f, n, k in badcites:
        failures.append(f"{f}:{n}: \\cite{{{k}}} not in the bibliography")

    # --- build logs
    build = {}
    for code in BUILD_ORDER:
        log = os.path.join(ROOT, FOLDER[code], "build", JOB[code] + ".log")
        pdf = os.path.join(ROOT, FOLDER[code], "build", JOB[code] + ".pdf")
        if not os.path.exists(log) or not os.path.exists(pdf):
            build[code] = ["not built"]
            failures.append(f"{code}: not built")
            continue
        with open(log, encoding="latin-1") as fh:
            text = fh.read()
        probs = [name for name, rx in LOG_PATTERNS if rx.search(text)]
        build[code] = probs
        failures += [f"{code}: {p} (see {FOLDER[code]}/build/{JOB[code]}.log)" for p in probs]

    # --- links
    for code in BUILD_ORDER:
        main = os.path.join(ROOT, FOLDER[code], MAINFILE[code])
        with open(main, encoding="utf-8") as fh:
            for m in re.finditer(r"\\externaldocument(?:\[[^\]]*\])*\{([^}]+)\}\[([^\]]+)\]", fh.read()):
                aux = os.path.normpath(os.path.join(ROOT, FOLDER[code], m.group(1) + ".aux"))
                pdf = os.path.normpath(os.path.join(ROOT, FOLDER[code], "build", m.group(2)))
                for p in (aux, pdf):
                    if not os.path.exists(p):
                        failures.append(f"{code}: external target missing: {os.path.relpath(p, ROOT)}")
    for md in sorted(f for f in os.listdir(ROOT) if f.endswith(".md")):
        with open(os.path.join(ROOT, md), encoding="utf-8") as fh:
            for m in re.finditer(r"\]\(([^)\s]+)\)", fh.read()):
                link = m.group(1).split("#")[0]
                if not link or re.match(r"[a-z]+:", link):
                    continue
                if not os.path.exists(os.path.join(ROOT, link)):
                    failures.append(f"{md}: broken link {link}")

    # --- consistency
    def cid(key):
        return ids.get(key, f"{key[0]}/{key[1]}")

    cross = []
    for f, n, c, l in s.refs:
        if l not in s.labels or s.files[f][1] == MAINFILE[s.files[f][0]]:
            continue
        src, tgt = s.chapter[f], s.chapter[s.labels[l][0][0]]
        if src[0] != tgt[0]:
            cross.append((f, n, c, l, src, tgt, direction(src, tgt, order)))
    grid = Counter((src[0], tgt[0]) for *_, src, tgt, _ in cross)

    stated = {}
    for code in CONTENT_DOCS:
        with open(os.path.join(ROOT, FOLDER[code], MAINFILE[code]), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        pending = None
        for line in lines:
            m = re.match(r"\\chapterprereqs\{([^}]*)\}", line)
            if m:
                pending = [x for x in m.group(1).split(",") if x]
                continue
            m = re.match(r"\\input\{chapters/([^/}]+)/", line)
            if m and pending is not None:
                stated[(code, m.group(1))] = pending
                pending = None
    gaps = []
    for key, labels in stated.items():
        have = {s.chapter[s.labels[l][0][0]] for l in labels if l in s.labels}
        files = [f for f in s.files if s.chapter[f] == key]
        for f, n, c, l in s.refs:
            if f not in files or l not in s.labels:
                continue
            k = s.chapter[s.labels[l][0][0]]
            if k == key or k[0] in ("GLOSSARY", "Unsorted") or k in have:
                continue
            if direction(key, k, order) == "back":
                gaps.append((key, f, n, l, k))
    for key, f, n, l, k in gaps:
        failures.append(f"{cid(key)}: refers back to {cid(k)} ({f}:{n}, {l}) but its prerequisites omit it")

    # --- report
    out = ["# Cross-document references", "",
           "Generated by `tools/check_xrefs.py` (run by `tools/build_all.ps1`). Do not edit by hand.", "",
           "A reference is **back** when its target is read earlier: an earlier chapter of the same document, or a "
           "document upstream in the dependency graph of [ROADMAP.md](ROADMAP.md). It is **forward** otherwise, and "
           "**reference** when GLOSSARY or the unsorted holder is involved. Forward references are kept unchanged "
           "(no text is edited); they are the soft prerequisites listed in ROADMAP.md.", "",
           "## Checks", "",
           f"- Labels defined more than once: {len(dups)}",
           f"- References without a target: {len(unresolved)}",
           f"- Citations missing from the bibliography: {len(badcites)}",
           f"- Chapters whose prerequisites omit a chapter they refer back to: {len(gaps)}",
           f"- Overall: {'PASS' if not failures else 'FAIL (' + str(len(failures)) + ' problems, listed at the end)'}", "",
           "| build | status |", "|---|---|"]
    for code in BUILD_ORDER:
        out.append(f"| {code} (`{FOLDER[code]}/build/{JOB[code]}.pdf`) | {', '.join(build[code]) or 'clean'} |")
    out += ["", "## References between documents (rows: from, columns: to)", "",
            "| from \\ to | " + " | ".join(ALL) + " |", "|---" * (len(ALL) + 1) + "|"]
    for a in ALL:
        out.append(f"| **{a}** | " + " | ".join(str(grid.get((a, b), "")) for b in ALL) + " |")
    counts = Counter(d for *_, d in cross)
    out += ["", f"Totals: {len(cross)} references across documents; back {counts['back']}, "
                f"forward {counts['forward']}, reference {counts['reference']}.", ""]

    def table(rows, title):
        out.extend([f"## {title}", ""])
        if not rows:
            out.extend(["None.", ""])
            return
        out.extend(["| source | command | label | target chapter | direction |", "|---|---|---|---|---|"])
        for f, n, c, l, src, tgt, d in sorted(rows, key=lambda r: (ALL.index(r[4][0]), r[0], r[1])):
            out.append(f"| `{f}:{n}` | `\\{c}` | `{l}` | {cid(tgt)} | {d} |")
        out.append("")

    table([r for r in cross if r[6] == "forward"], "Forward references (soft prerequisites)")
    table([r for r in cross if r[5][0] == "Unsorted"], "References into unsorted material")
    table([r for r in cross if r[6] == "back"], "Back references across documents")
    table([r for r in cross if r[6] == "reference" and r[5][0] != "Unsorted"], "References to and from GLOSSARY")
    if failures:
        out += ["## Problems", ""] + [f"- {p}" for p in failures] + [""]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    print(f"cross-document references: {len(cross)} (back {counts['back']}, forward {counts['forward']}, "
          f"reference {counts['reference']}); problems: {len(failures)} -> {OUT}")
    for p in failures[:40]:
        print("  " + p)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
