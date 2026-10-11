"""Invariant and warning checker.

Usage:
  python tools/check.py legacy/original.tex legacy/original.log
  python tools/check.py main.tex build/main.log

For main.tex, every \\input is expanded recursively so the counts refer to the
whole document.
"""
import re
import sys
from pathlib import Path

ENVS = ["example", "formal", "intuition", "synthesis", "definition", "theorem",
        "proposition", "lemma", "corollary", "proof", "exercises", "keypoints",
        "keyidea", "pitfall", "remark", "specialcase", "figure", "table",
        "tikzpicture", "identity"]


def expand(path: Path, root: Path) -> str:
    text = path.read_text(encoding="utf-8")
    out = []
    for line in text.splitlines(keepends=True):
        stripped = line.split("%", 1)[0] if not line.lstrip().startswith("%") else ""
        m = re.search(r"\\input\{([^}]+)\}", stripped)
        if m:
            target = root / m.group(1)
            if target.suffix != ".tex":
                target = target.with_suffix(".tex")
            out.append(expand(target, root))
        else:
            out.append(line)
    return "".join(out)


def strip_comments(t: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in t.splitlines())


def main():
    tex = Path(sys.argv[1])
    t = strip_comments(expand(tex, tex.parent))
    t = t[max(t.find("\\begin{document}"), 0):]
    counts = {
        "label": len(re.findall(r"\\label\{", t)),
        "ref+eqref": len(re.findall(r"\\(?:ref|eqref)\{", t)),
        "cite": len(re.findall(r"\\cite\{", t)),
        "bibitem": len(re.findall(r"\\bibitem", t)),
        "part": len(re.findall(r"\\part\{", t)),
        "section": len(re.findall(r"\\section\{", t)),
        "subsection": len(re.findall(r"\\subsection\{", t)),
        "Step": len(re.findall(r"\\Step\{", t)),
        "numcheck": len(re.findall(r"\\numcheck", t)),
    }
    for e in ENVS:
        counts[e] = len(re.findall(r"\\begin\{%s\}" % e, t))
    labels = re.findall(r"\\label\{([^}]+)\}", t)
    dup = sorted({l for l in labels if labels.count(l) > 1})
    refs = {r for r in re.findall(r"\\(?:ref|eqref|pageref|hyperref\[)\{?([^}\]]+)", t) if "#" not in r}
    undefined = sorted(r for r in refs if r not in set(labels))
    for k, v in counts.items():
        print(f"{k:12s} {v}")
    print("duplicate labels:", dup)
    print("undefined refs (source):", undefined)
    if len(sys.argv) > 2 and Path(sys.argv[2]).exists():
        log = Path(sys.argv[2]).read_text(encoding="latin-1")
        warns = re.findall(r"^(?:LaTeX|Package \w+) Warning.*$", log, re.M)
        over = len(re.findall(r"^Overfull", log, re.M))
        under = len(re.findall(r"^Underfull", log, re.M))
        pages = re.search(r"Output written on .*?\((\d+)\s+pages", log, re.S)
        print("pages:", pages.group(1) if pages else "?")
        print("LaTeX/package warnings:", len(warns))
        for w in sorted(set(warns)):
            print("   ", w[:150])
        print("overfull:", over, "underfull:", under)
        print("undefined in log:", len(re.findall(r"undefined", log)))


if __name__ == "__main__":
    main()
