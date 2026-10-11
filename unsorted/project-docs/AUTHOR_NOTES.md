# Author notes

Points where the mathematics or a reference looks doubtful. Nothing here was "fixed" silently:
each open item is marked in the source with `% AUTHOR-NOTE:` (search `rg "AUTHOR-NOTE"`).
Line numbers refer to `legacy/original.tex`.

## Open

| # | Where (original line) | New file | Issue | Suggested resolution |
|---|---|---|---|---|
| 1 | L3261, normal-coordinate expansion | `parts/04-connections-curvature/03-riemann-curvature/04-metric-case.tex` | With this document's convention `\mathbb R_{ijkl}=g(R(\partial_i,\partial_j)\partial_k,\partial_l)`, the unit-sphere check gives the opposite sign. | Probably `g_{ij}=\delta_{ij}-\tfrac13\mathbb R_{iklj}x^kx^l+\dots` (equivalently `+\tfrac13\mathbb R_{ikjl}`). |
| 2 | L3398 | `parts/04-connections-curvature/05-synthesis-3/03-curvature-vs-dd.tex` | `[\nabla_i,\nabla_j]V^k=R^k{}_{lij}V^l` uses Carroll's index order. | In this document's order, `R^k{}_{ijl}V^l`. |
| 3 | L1764, conventions table | `parts/01-algebra/09-synthesis-1/03-dictionary-of-conventions.tex` | Signature row says "GR notes: (negative, positive)", but the formal box at L794 uses (positive, negative). | Check which one the GR notes use. |
| 4 | L690 | `parts/01-algebra/02-tensors/03-tensor-types.tex` | "(In the notes this appears with B=A.)" refers to a `B` never defined here. | Define `B` or delete the sentence. |
| 5 | `thm:dGA` (2) | `parts/02-manifolds-and-forms/05-ga-calculus/01-vector-derivative.tex` | Sign of the codifferential and the "standard formula" are convention dependent; `\hodge\hodge` in Lorentzian signature is never addressed but used for Maxwell in `R^{1,3}`. | State the convention. The Euclidean `\hodge\hodge` is proved in glossary identity `id:hodgehodge`. |
| 7 | `thm:dprops` (3) for k>1, (5) | `parts/02-manifolds-and-forms/03-tensor-fields-forms/03-exterior-derivative.tex` | Stated without proof. | Partly resolved: (2) is proved in `id:pbd` and (3) for 1-forms in `id:dinvariant`; (3) for k>1 and (5) (Poincaré lemma) are left to `\cite{Lee,BottTu}`. |
| 9 | L1196 | `parts/01-algebra/04-exterior-algebra/05-wedge-and-tensor-product.tex` | Kobayashi–Nomizu named, not in the bibliography. | Add a bibitem if wanted (BibTeX conversion not done; needs approval). |
| 10 | "Lee Prop. 7.5" | `parts/04-connections-curvature/03-riemann-curvature/02-general-properties.tex` | The Lee bibitem lists two books; it is unclear which one (and which edition) is meant. | Check and make the citation precise. ("Narciso's notes" was generalised to "some lecture notes" with `\cite{Carroll}`.) |
| 11 | Euler–Lagrange equations, Laurent series | Parts IV–VI | Used beyond the stated reader profile. | Glossary entries added; consider a one-line recap. |
| 12 | "lecture notes I4" / "the notes" | `02-tangent-cotangent/04-pushforward-pullback.tex`, `03-tensor-fields-forms/01-tensor-fields.tex`, `02-tensors/03-tensor-types.tex` | External references to lecture notes that are not in the bibliography. Others were generalised in Part IV; these remain, and the reading guide explains them. | Decide whether to add a bibitem or drop them. |
| 13 | Lorentzian Hodge signs | Part V (Maxwell) | Signs of `\hodge` on `R^{1,3}` depend on conventions not fixed in the text. | Flagged only. |

## Resolved

| # | Item | Resolution |
|---|---|---|
| 6 | `prop:contr` (3): only a proof idea, and `thm:dual` depends on it | Full proof on basis blades in glossary identity `id:contr3`; pointer added to the proof idea. |
| 8 | `eq:antider` never proved (two places pointed at each other) | Proof added by the rewriter in `sec:interior`; summarised in `id:antider`. |
| 14 | `\ref` to example, remark and special-case boxes printed the subsection number | The counter is stepped with `\refstepcounter` before the box (`preamble/environments.tex`), so the reference matches the number in the title. |
