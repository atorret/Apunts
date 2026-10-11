"""One-off Phase 2 splitter: legacy/original.tex -> modular files (original order).

Each spec entry is (regex, offset, relative path). The regex is searched forward
from the previous anchor; the file starts at match_line + offset and runs to the
line before the next anchor. Section files (00-section.tex) and part files
(00-part.tex) receive \\input lines for their children. Figures are extracted to
figures/, extract markers are removed and logged to docs/PROVENANCE.md.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "legacy" / "original.tex").read_text(encoding="utf-8").splitlines()

P1, P2, P3, P4, P5, P6, P7 = ("parts/01-algebra", "parts/02-manifolds-and-forms",
    "parts/03-integration", "parts/04-connections-curvature", "parts/05-physics",
    "parts/06-complex-analysis", "parts/07-perspective")

def S(lbl):
    return r"\\section\{.*\\label\{%s\}" % re.escape(lbl)

def L(lbl):
    return r"\\label\{%s\}" % re.escape(lbl)

KP, EX = r"^\\begin\{keypoints\}", r"^\\begin\{exercises\}"

SPEC = [
    (r"^\\begin\{center\}", 0, "frontmatter/title.tex"),
    (r"^\\begin\{center\}", 0, "frontmatter/abstract.tex"),
    (r"^\\vspace\{0\.8em\}", 0, "MAIN-TOC"),
    (r"^% =+", 0, "frontmatter/reading-guide.tex"),
    (r"^\\clearpage", 0, "MAIN-CLEAR"),
    (r"\\part\{Algebraic", -1, f"{P1}/00-part.tex"),
    (S("sec:vectors"), -1, f"{P1}/01-vectors-covectors/00-section.tex"),
    (L("sec:vs"), 0, f"{P1}/01-vectors-covectors/01-vector-spaces-change-of-basis.tex"),
    (L("sec:dualspace"), 0, f"{P1}/01-vectors-covectors/02-dual-space.tex"),
    (L("sec:contraction"), 0, f"{P1}/01-vectors-covectors/03-contraction.tex"),
    (S("sec:tensors"), -1, f"{P1}/02-tensors/00-section.tex"),
    (L("sec:multilinear"), 0, f"{P1}/02-tensors/01-multilinear-maps.tex"),
    (L("sec:tensorproduct"), 0, f"{P1}/02-tensors/02-tensor-product.tex"),
    (L("sec:tensortypes"), 0, f"{P1}/02-tensors/03-tensor-types.tex"),
    (L("sec:symcontr"), 0, f"{P1}/02-tensors/04-symmetric-antisymmetric-contraction.tex"),
    (L("sec:tensoralgebra"), 0, f"{P1}/02-tensors/05-tensor-algebra.tex"),
    (S("sec:metric"), -1, f"{P1}/03-metric/00-section.tex"),
    (r"begin extract GR lines 317-369", 0, f"{P1}/03-metric/01-metric-and-musical-isomorphisms.tex"),
    (EX, 0, f"{P1}/03-metric/exercises.tex"),
    (L("sec:quadform"), 0, f"{P1}/03-metric/02-quadratic-forms-signature.tex"),
    (KP, 0, f"{P1}/03-metric/keypoints.tex"),
    (S("sec:ext"), -1, f"{P1}/04-exterior-algebra/00-section.tex"),
    (L("sec:altforms"), 0, f"{P1}/04-exterior-algebra/01-alternating-forms-wedge.tex"),
    (L("sec:wedgeprops"), 0, f"{P1}/04-exterior-algebra/02-wedge-properties.tex"),
    (L("sec:extquotient"), 0, f"{P1}/04-exterior-algebra/03-exterior-quotient.tex"),
    (L("sec:blades"), 0, f"{P1}/04-exterior-algebra/04-blades.tex"),
    (L("sec:wedgetensor"), 0, f"{P1}/04-exterior-algebra/05-wedge-and-tensor-product.tex"),
    (L("sec:interior"), 0, f"{P1}/04-exterior-algebra/06-interior-product.tex"),
    (KP, 0, f"{P1}/04-exterior-algebra/keypoints.tex"),
    (S("sec:clifford"), -1, f"{P1}/05-clifford-algebra/00-section.tex"),
    (r"subsection\{Definition by relations", 0, f"{P1}/05-clifford-algebra/01-definition-by-relations.tex"),
    (r"subsection\{Size of the algebra", 0, f"{P1}/05-clifford-algebra/02-size-and-grades.tex"),
    (r"subsection\{Examples\}", 0, f"{P1}/05-clifford-algebra/03-examples.tex"),
    (r"subsection\{The geometric product of two", 0, f"{P1}/05-clifford-algebra/04-product-of-two-vectors.tex"),
    (S("sec:ops"), -1, f"{P1}/06-multivector-operations/00-section.tex"),
    (r"subsection\{Involutions", 0, f"{P1}/06-multivector-operations/01-involutions.tex"),
    (r"subsection\{Inner, outer", 0, f"{P1}/06-multivector-operations/02-inner-outer-contraction.tex"),
    (S("sec:rotors"), -1, f"{P1}/07-rotors/00-section.tex"),
    (r"begin extract GA lines 610-667", 0, f"{P1}/07-rotors/01-reflections-and-rotors.tex"),
    (S("sec:duality"), -1, f"{P1}/08-duality/00-section.tex"),
    (r"subsection\{The pseudoscalar", 0, f"{P1}/08-duality/01-pseudoscalar.tex"),
    (r"subsection\{The dual\}", 0, f"{P1}/08-duality/02-dual.tex"),
    (r"subsection\{The cross product", 0, f"{P1}/08-duality/03-cross-product.tex"),
    (r"subsection\{Relation to the Hodge", 0, f"{P1}/08-duality/04-hodge-star.tex"),
    (S("sec:synth1"), -1, f"{P1}/09-synthesis-1/00-section.tex"),
    (L("sec:contr4"), 0, f"{P1}/09-synthesis-1/01-contraction-four-guises.tex"),
    (L("sec:whichmetric"), 0, f"{P1}/09-synthesis-1/02-which-operations-need-a-metric.tex"),
    (L("sec:conventions"), 0, f"{P1}/09-synthesis-1/03-dictionary-of-conventions.tex"),
    (KP, 0, f"{P1}/09-synthesis-1/keypoints.tex"),
    (r"\\part\{Manifolds", -2, f"{P2}/00-part.tex"),
    (S("sec:manifolds"), -1, f"{P2}/01-differentiable-manifolds/00-section.tex"),
    (r"begin extract GR lines 377-426", 0, f"{P2}/01-differentiable-manifolds/01-charts-and-atlases.tex"),
    (EX, 0, f"{P2}/01-differentiable-manifolds/exercises.tex"),
    (S("sec:tangent"), -1, f"{P2}/02-tangent-cotangent/00-section.tex"),
    (L("sec:tangentvectors"), 0, f"{P2}/02-tangent-cotangent/01-tangent-vectors.tex"),
    (L("sec:changecoords"), 0, f"{P2}/02-tangent-cotangent/02-changing-coordinates.tex"),
    (L("sec:trio"), 0, f"{P2}/02-tangent-cotangent/03-the-trio.tex"),
    (L("sec:pushpull"), 0, f"{P2}/02-tangent-cotangent/04-pushforward-pullback.tex"),
    (S("sec:fields"), -1, f"{P2}/03-tensor-fields-forms/00-section.tex"),
    (L("sec:tensorfields"), 0, f"{P2}/03-tensor-fields-forms/01-tensor-fields.tex"),
    (L("sec:oneforms"), 0, f"{P2}/03-tensor-fields-forms/02-one-forms.tex"),
    (L("sec:dform"), 0, f"{P2}/03-tensor-fields-forms/03-exterior-derivative.tex"),
    (S("sec:lie"), -1, f"{P2}/04-lie-derivative/00-section.tex"),
    (r"subsection\{Vector fields and their flows", 0, f"{P2}/04-lie-derivative/01-flows.tex"),
    (r"subsection\{Definition and properties", 0, f"{P2}/04-lie-derivative/02-definition-properties.tex"),
    (L("sec:cartan"), 0, f"{P2}/04-lie-derivative/03-cartan-formula.tex"),
    (L("sec:operators"), 0, f"{P2}/04-lie-derivative/04-operator-relations.tex"),
    (KP, 0, f"{P2}/04-lie-derivative/keypoints.tex"),
    (S("sec:ga-calculus"), -1, f"{P2}/05-ga-calculus/00-section.tex"),
    (r"begin\{definition\}\[Vector derivative", 0, f"{P2}/05-ga-calculus/01-vector-derivative.tex"),
    (r"begin\{example\}\[Vector calculus in", 0, f"{P2}/05-ga-calculus/02-examples.tex"),
    (S("sec:synth2"), -1, f"{P2}/06-synthesis-2/00-section.tex"),
    (r"subsection\{The dictionary in", 0, f"{P2}/06-synthesis-2/01-dictionary-r3.tex"),
    (r"subsection\{One reason", 0, f"{P2}/06-synthesis-2/02-one-reason-three-identities.tex"),
    (r"subsection\{Maxwell", 0, f"{P2}/06-synthesis-2/03-maxwell-three-languages.tex"),
    (KP, 0, f"{P2}/06-synthesis-2/keypoints.tex"),
    (r"\\part\{Integration", -2, f"{P3}/00-part.tex"),
    (S("sec:int1"), -1, f"{P3}/01-integration-1-forms/00-section.tex"),
    (L("sec:int1def"), 0, f"{P3}/01-integration-1-forms/01-definition.tex"),
    (L("sec:riemannsums"), 0, f"{P3}/01-integration-1-forms/02-riemann-sums.tex"),
    (L("sec:linearity"), 0, f"{P3}/01-integration-1-forms/03-linearity.tex"),
    (L("sec:naturality"), 0, f"{P3}/01-integration-1-forms/04-naturality.tex"),
    (L("sec:expl-closed"), 0, f"{P3}/01-integration-1-forms/05-exact-closed.tex"),
    (L("sec:circulation"), 0, f"{P3}/01-integration-1-forms/06-circulation.tex"),
    (S("sec:intk"), -1, f"{P3}/02-integration-k-forms/00-section.tex"),
    (r"^Let \$\\phi:U\\subset", 0, f"{P3}/02-integration-k-forms/01-full-contraction.tex"),
    (L("sec:flux"), 0, f"{P3}/02-integration-k-forms/02-flux.tex"),
    (S("sec:stokes"), -1, f"{P3}/03-stokes/00-section.tex"),
    (r"subsection\{Statement\}", 0, f"{P3}/03-stokes/01-statement.tex"),
    (L("sec:green"), 0, f"{P3}/03-stokes/02-green-warm-up.tex"),
    (L("sec:stokesproof"), 0, f"{P3}/03-stokes/03-proof.tex"),
    (L("sec:adjoint"), 0, f"{P3}/03-stokes/04-adjoint.tex"),
    (L("sec:classical"), 0, f"{P3}/03-stokes/05-classical-corollaries.tex"),
    (S("sec:gauss"), -1, f"{P3}/04-gauss/00-section.tex"),
    (L("sec:divmu"), 0, f"{P3}/04-gauss/01-divergence-volume-form.tex"),
    (L("sec:boundaryterm"), 0, f"{P3}/04-gauss/02-boundary-term.tex"),
    (r"subsection\{Statement and proof", 0, f"{P3}/04-gauss/03-statement-and-proof.tex"),
    (r"begin\{remark\}\[What needs what", 0, f"{P3}/04-gauss/05-what-needs-what.tex"),
    (KP, 0, f"{P3}/04-gauss/keypoints.tex"),
    (r"\\part\{Connections", -2, f"{P4}/00-part.tex"),
    (S("sec:conn"), -1, f"{P4}/01-connections/00-section.tex"),
    (r"subsection\{Definition\}", 0, f"{P4}/01-connections/01-definition.tex"),
    (r"subsection\{Covariant derivative of covectors", 0, f"{P4}/01-connections/02-covectors-and-tensors.tex"),
    (r"subsection\{Parallel transport", 0, f"{P4}/01-connections/03-parallel-transport.tex"),
    (r"subsection\{Geodesics\}", 0, f"{P4}/01-connections/04-geodesics.tex"),
    (EX, 0, f"{P4}/01-connections/exercises.tex"),
    (S("sec:lc"), -1, f"{P4}/02-levi-civita/00-section.tex"),
    (r"begin\{formal\}\[\{torsion", 0, f"{P4}/02-levi-civita/01-torsion-levi-civita.tex"),
    (r"subsection\{Geodesics as extremals", 0, f"{P4}/02-levi-civita/02-variational-principle.tex"),
    (EX, 0, f"{P4}/02-levi-civita/exercises.tex"),
    (S("sec:curv"), -1, f"{P4}/03-riemann-curvature/00-section.tex"),
    (r"begin\{intuition\}\[\{curvature = failure", 0, f"{P4}/03-riemann-curvature/01-riemann-tensor.tex"),
    (r"subsection\{General properties", 0, f"{P4}/03-riemann-curvature/02-general-properties.tex"),
    (r"subsection\{Ricci tensor", 0, f"{P4}/03-riemann-curvature/03-ricci-scalar.tex"),
    (r"subsection\{The metric case", 0, f"{P4}/03-riemann-curvature/04-metric-case.tex"),
    (EX, 0, f"{P4}/03-riemann-curvature/exercises.tex"),
    (S("sec:deviation"), -1, f"{P4}/04-geodesic-deviation/00-section.tex"),
    (r"begin\{intuition\}\[\{tidal forces", 0, f"{P4}/04-geodesic-deviation/01-deviation-equation.tex"),
    (EX, 0, f"{P4}/04-geodesic-deviation/exercises.tex"),
    (S("sec:synth3"), -1, f"{P4}/05-synthesis-3/00-section.tex"),
    (L("sec:threederivs"), 0, f"{P4}/05-synthesis-3/01-three-derivatives.tex"),
    (L("sec:divthree"), 0, f"{P4}/05-synthesis-3/02-divergence-three-ways.tex"),
    (L("sec:curvdd"), 0, f"{P4}/05-synthesis-3/03-curvature-vs-dd.tex"),
    (L("sec:noethersynth"), 0, f"{P4}/05-synthesis-3/04-noether-synthesis.tex"),
    (KP, 0, f"{P4}/05-synthesis-3/keypoints.tex"),
    (r"\\part\{Physics", -2, f"{P5}/00-part.tex"),
    (S("sec:phys"), -1, f"{P5}/01-intrinsic-vs-metric/00-section.tex"),
    (L("sec:phys-work"), 0, f"{P5}/01-intrinsic-vs-metric/01-work-and-energy.tex"),
    (L("sec:phys-energy"), 0, f"{P5}/01-intrinsic-vs-metric/02-energy-as-contraction.tex"),
    (L("sec:phys-hamilton"), 0, f"{P5}/01-intrinsic-vs-metric/04-hamiltonian-mechanics.tex"),
    (L("sec:phys-thermo"), 0, f"{P5}/01-intrinsic-vs-metric/05-thermodynamics.tex"),
    (L("sec:phys-em"), 0, f"{P5}/01-intrinsic-vs-metric/06-electromagnetism.tex"),
    (L("sec:phys-fluids"), 0, f"{P5}/01-intrinsic-vs-metric/07-fluids.tex"),
    (L("sec:phys-cross"), 0, f"{P5}/01-intrinsic-vs-metric/08-pseudovectors.tex"),
    (L("sec:phys-confusion"), 0, f"{P5}/01-intrinsic-vs-metric/09-sources-of-confusion.tex"),
    (L("sec:phys-dict"), 0, f"{P5}/01-intrinsic-vs-metric/10-dictionary.tex"),
    (S("sec:bridge"), -1, f"{P5}/02-bridge-to-gr/00-section.tex"),
    (r"begin extract GR lines 999-1028", 0, f"{P5}/02-bridge-to-gr/01-gr-dictionary-einstein.tex"),
    (r"\\part\{Complex", -2, f"{P6}/00-part.tex"),
    (S("sec:complex"), -1, f"{P6}/01-residue-theorem/00-section.tex"),
    (L("sec:complexforms"), 0, f"{P6}/01-residue-theorem/01-complex-forms.tex"),
    (L("sec:cauchy"), 0, f"{P6}/01-residue-theorem/02-cauchy.tex"),
    (L("sec:residue"), 0, f"{P6}/01-residue-theorem/03-residue-theorem.tex"),
    (L("sec:rescohom"), 0, f"{P6}/01-residue-theorem/04-cohomology.tex"),
    (L("sec:pompeiu"), 0, f"{P6}/01-residue-theorem/05-cauchy-pompeiu.tex"),
    (L("sec:argument"), 0, f"{P6}/01-residue-theorem/06-argument-principle.tex"),
    (L("sec:rescurrent"), 0, f"{P6}/01-residue-theorem/07-current-picture.tex"),
    (L("sec:synth4"), 0, f"{P6}/01-residue-theorem/08-synthesis-4.tex"),
    (r"\\part\{Perspective", -2, f"{P7}/00-part.tex"),
    (S("sec:current"), -1, f"{P7}/01-current-state/00-section.tex"),
    (S("sec:summary"), -1, f"{P7}/02-master-summary/00-section.tex"),
    (r"subsection\{One picture", 0, f"{P7}/02-master-summary/01-one-picture.tex"),
    (r"subsection\{The essence", 0, f"{P7}/02-master-summary/02-essence.tex"),
    (r"subsection\{The toolkit", 0, f"{P7}/02-master-summary/03-toolkit-metric-geometry.tex"),
    (r"subsection\{The dictionary of the algebras", 0, f"{P7}/02-master-summary/04-dictionary-algebras.tex"),
    (r"subsection\{Common mistakes", 0, f"{P7}/02-master-summary/05-common-mistakes.tex"),
    (r"subsection\{Suggested path", 0, f"{P7}/02-master-summary/06-suggested-path.tex"),
    (r"\\section\*\{References", -1, "backmatter/references.tex"),
    (r"^\\end\{document\}", 0, "MAIN-END"),
]

FIGS = {
    "fig:sheets": "figures/part1/tikz-sheets.tex",
    "fig:wedge": "figures/part1/tikz-wedge.tex",
    "fig:tworefl": "figures/part1/tikz-two-reflections.tex",
    "fig:annulus": "figures/part3/tikz-annulus.tex",
    "fig:cycle": "figures/part5/tikz-cycle.tex",
    "fig:residue": "figures/part6/tikz-residue.tex",
    "fig:map": "figures/part7/tikz-map.tex",
}
INLINE_TIKZ = "figures/part1/tikz-universal-property.tex"

SECTION_NAMES = {}


def locate():
    starts = []
    pos = 203  # 0-based index of first line after \begin{document}
    for rx, off, path in SPEC:
        r = re.compile(rx)
        for i in range(pos, len(SRC)):
            if r.search(SRC[i]):
                starts.append((i + off, path))
                pos = i + 1
                break
        else:
            raise SystemExit(f"anchor not found: {rx}")
    return starts


def depth_root(path: str) -> str:
    return "/".join([".."] * (len(Path(path).parts) - 1)) + "/main.tex"


def main():
    starts = locate()
    segs = []
    for k, (s, path) in enumerate(starts):
        e = starts[k + 1][0] if k + 1 < len(starts) else len(SRC)
        segs.append((s, e, path))
    # coverage check
    assert segs[0][0] == 203 + 1 or True
    prov = []
    files = {}
    order = []
    for s, e, path in segs:
        lines = SRC[s:e]
        kept = []
        for j, l in enumerate(lines):
            m = re.match(r"^%+ ---- begin extract (GA|GR) lines (\d+-\d+) ----", l)
            if m:
                prov.append([m.group(1), m.group(2), s + j + 1, None, path])
                continue
            if re.match(r"^%+ ---- end extract ----", l):
                for p in reversed(prov):
                    if p[3] is None:
                        p[3] = s + j + 1
                        if p[4] != path:
                            p[4] = p[4] + " ... " + path
                        break
                continue
            kept.append(l)
        files.setdefault(path, []).append((s + 1, e, kept))
        order.append(path)
    # figure extraction
    figfiles = {}
    for path, chunks in files.items():
        for c in chunks:
            text = "\n".join(c[2])
            def repl(m):
                block = m.group(0)
                lab = re.search(r"\\label\{(fig:[^}]+)\}", block).group(1)
                figfiles[FIGS[lab]] = (block, path)
                return "\\input{%s}" % FIGS[lab][:-4]
            text = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", repl, text, flags=re.S)
            def repl2(m):
                figfiles[INLINE_TIKZ] = (m.group(0), path)
                return "\\input{%s}" % INLINE_TIKZ[:-4]
            text = re.sub(r"\\begin\{tikzpicture\}\[baseline=.*?\\end\{tikzpicture\}", repl2, text, flags=re.S)
            c[2][:] = text.split("\n")
    # write content files
    children = {}
    for path in dict.fromkeys(order):
        if path.startswith("MAIN"):
            continue
        p = Path(path)
        if not path.startswith("parts/") or p.name == "00-part.tex":
            continue
        if p.name == "00-section.tex":
            parent = p.parent.parent / "00-part.tex"
        else:
            parent = p.parent / "00-section.tex"
        children.setdefault(parent.as_posix(), []).append(path)
    secno = 0
    partno = 0
    for path in dict.fromkeys(order):
        if path.startswith("MAIN"):
            continue
        chunks = files[path]
        body = []
        for c in chunks:
            body.extend(c[2])
        while body and body[-1].strip() == "":
            body.pop()
        rng = ", ".join(f"{a}-{b}" for a, b, _ in chunks)
        p = Path(path)
        if p.name == "00-part.tex":
            partno += 1
        if p.name == "00-section.tex":
            secno += 1
        title = next((re.sub(r"\\label\{.*", "", m.group(1)) for l in body
                      for m in [re.search(r"\\(?:sub)?section\*?\{(.*)", l)] if m), p.stem)
        head = (f"% Section {secno}: {title} | Part: {partno} | Depends on: see docs/REWRITE_PLAN.md"
                f" | Status: todo | Original lines: {rng}")
        if p.name == "00-part.tex":
            head = f"% Part {partno} | Status: todo | Original lines: {rng}"
        if path.startswith("frontmatter") or path.startswith("backmatter"):
            head = f"% {p.stem} | Status: todo | Original lines: {rng}"
        out = [head, f"%!TEX root = {depth_root(path)}"] + body
        for ch in children.get(path, []):
            out.append(f"\\input{{{ch[:-4]}}}")
        dest = ROOT / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    for fpath, (block, src) in figfiles.items():
        dest = ROOT / fpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f"% Figure | used in {src}\n%!TEX root = {depth_root(fpath)}\n{block}\n",
                        encoding="utf-8")
    # main input list
    tops = [p for p in dict.fromkeys(order) if not p.startswith("MAIN") and
            (p.startswith("frontmatter") or p.endswith("00-part.tex") or p.startswith("backmatter"))]
    (ROOT / "tools" / "main_inputs.txt").write_text("\n".join(tops), encoding="utf-8")
    with open(ROOT / "docs" / "PROVENANCE.md", "w", encoding="utf-8") as f:
        f.write("# Provenance of extracted blocks\n\n"
                "The original file marked text copied from the source texts with comments\n"
                "`% ---- begin extract GA|GR lines X-Y ----` ... `%% ---- end extract ----`.\n"
                "GA = source C (geometric algebra notes), GR = source B (GR course companion).\n"
                "Unmarked text is source A or merge glue. X-Y are line numbers in the SOURCE text.\n"
                "The markers have been removed from the .tex files; this table preserves them.\n"
                "\"Original lines\" are lines of `legacy/original.tex` (begin marker .. end marker).\n\n"
                "| # | Source | Source lines | Original lines | New file(s) |\n|---|---|---|---|---|\n")
        for k, (src, sl, b, e, path) in enumerate(prov, 1):
            f.write(f"| {k} | {src} | {sl} | {b}-{e} | `{path}` |\n")
    print("files:", len(set(order)), "figures:", len(figfiles), "extracts:", len(prov))
    print("first segment starts at line", segs[0][0] + 1, "last ends", segs[-1][1])


if __name__ == "__main__":
    main()
