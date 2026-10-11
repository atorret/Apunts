"""Rewrite the first-line header of every content file (re-runnable).

Header format:
  % Section N[.M]: title | Part: P | Depends on: sec:a, sec:b | Status: todo|done | Original lines: a-b
  %!TEX root = <relative>/main.tex

Section numbers follow folder order; the title is read from the first \\section/\\subsection
in the file. "Status" and "Original lines" are kept from the existing header.

Usage:  python tools/headers.py [--done PATH_PREFIX ...]
        --done marks every file under the given prefixes as Status: done.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEPENDS = {
    "01-algebra/01-vectors-covectors": "none",
    "01-algebra/02-tensors": "sec:vectors",
    "01-algebra/03-metric": "sec:vectors, sec:tensors",
    "01-algebra/04-exterior-algebra": "sec:tensors, sec:metric",
    "01-algebra/05-clifford-algebra": "sec:metric, sec:ext",
    "01-algebra/06-multivector-operations": "sec:clifford",
    "01-algebra/07-rotors": "sec:ops",
    "01-algebra/08-duality": "sec:ext, sec:ops",
    "01-algebra/09-synthesis-1": "sec:vectors to sec:duality",
    "02-manifolds-and-forms/01-differentiable-manifolds": "part:algebra",
    "02-manifolds-and-forms/02-tangent-cotangent": "sec:manifolds, sec:vectors, sec:ext",
    "02-manifolds-and-forms/03-tensor-fields-forms": "sec:tangent, sec:ext",
    "02-manifolds-and-forms/04-lie-derivative": "sec:fields, sec:interior",
    "02-manifolds-and-forms/05-ga-calculus": "sec:fields, sec:duality",
    "02-manifolds-and-forms/06-synthesis-2": "sec:fields, sec:lie, sec:ga-calculus",
    "03-integration/01-integration-1-forms": "sec:fields, sec:tangent",
    "03-integration/02-integration-k-forms": "sec:int1, sec:ext",
    "03-integration/03-stokes": "sec:intk, sec:fields",
    "03-integration/04-gauss": "sec:stokes, sec:interior, sec:metric",
    "04-connections-curvature/01-connections": "sec:fields, sec:tangent",
    "04-connections-curvature/02-levi-civita": "sec:conn, sec:metric",
    "04-connections-curvature/03-riemann-curvature": "sec:conn, sec:lc",
    "04-connections-curvature/04-geodesic-deviation": "sec:lc, sec:curv",
    "04-connections-curvature/05-synthesis-3": "sec:lie, sec:lc, sec:curv, sec:gauss",
    "05-physics/01-intrinsic-vs-metric": "part:manifolds, part:integration, sec:lc",
    "05-physics/02-bridge-to-gr": "sec:phys, part:geometry",
    "06-complex-analysis/01-residue-theorem": "sec:stokes, sec:ga-calculus",
    "07-perspective/01-current-state": "all previous parts",
    "07-perspective/02-master-summary": "all previous parts",
}


def braced(s: str, start: int) -> str:
    depth, out = 0, []
    for ch in s[start:]:
        if ch == "{":
            depth += 1
            if depth == 1:
                continue
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        out.append(ch)
    return "".join(out)


def title_of(text: str, cmd: str):
    m = re.search(r"\\%s\*?\{" % cmd, text)
    return braced(text, m.end() - 1) if m else None


def old_field(line: str, name: str, default: str) -> str:
    m = re.search(name + r":\s*([^|]+)", line)
    return m.group(1).strip() if m else default


def main():
    done = []
    if "--done" in sys.argv:
        done = sys.argv[sys.argv.index("--done") + 1:]
    part_dirs = sorted(p for p in (ROOT / "parts").iterdir() if p.is_dir())
    sec_no = 0
    for pi, pdir in enumerate(part_dirs, 1):
        files = [pdir / "00-part.tex"]
        sec_dirs = sorted(d for d in pdir.iterdir() if d.is_dir())
        for f in files:
            fix(f, f"Part {pi}: {title_of(f.read_text(encoding='utf-8'), 'part')}", pi,
                "previous parts" if pi > 1 else "none", "../../main.tex", done)
        for sdir in sec_dirs:
            sec_no += 1
            rel = f"{pdir.name}/{sdir.name}"
            dep = DEPENDS.get(rel, "see docs/REWRITE_PLAN.md")
            for f in sorted(sdir.glob("*.tex")):
                text = f.read_text(encoding="utf-8")
                if f.name == "00-section.tex":
                    label = f"Section {sec_no}: {title_of(text, 'section')}"
                elif f.name in ("exercises.tex", "keypoints.tex"):
                    label = f"Section {sec_no} ({f.stem}): {title_of(text, 'section') or f.stem.capitalize()}"
                else:
                    num = int(f.name.split("-", 1)[0])
                    label = f"Section {sec_no}.{num}: {title_of(text, 'subsection') or f.stem}"
                fix(f, label, pi, dep, "../../../main.tex", done)


def fix(f: Path, label: str, part: int, dep: str, root: str, done):
    lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
    first = lines[0] if lines and lines[0].startswith("%") else ""
    status = old_field(first, "Status", "todo")
    rel = f.relative_to(ROOT).as_posix()
    if any(rel.startswith(d) for d in done):
        status = "done"
    orig = old_field(first, "Original lines", "")
    new = f"% {label} | Part: {part} | Depends on: {dep} | Status: {status}"
    if orig:
        new += f" | Original lines: {orig}"
    body = lines[1:] if first else lines
    if body and body[0].startswith("%!TEX root"):
        body = body[1:]
    f.write_text(new + "\n" + f"%!TEX root = {root}\n" + "".join(body), encoding="utf-8")


if __name__ == "__main__":
    main()
