# Author notes

Points where the mathematics or a reference looks doubtful. Nothing here was "fixed" silently:
each item is marked in the source with `% AUTHOR-NOTE:` (search `rg "AUTHOR-NOTE"`).
Line numbers refer to `legacy/original.tex`.

| # | Where (original line) | New file | Issue | Suggested resolution |
|---|---|---|---|---|
| 1 | L3261, normal-coordinate expansion | `parts/04-connections-curvature/03-riemann-curvature/` | With this document's convention `\mathbb R_{ijkl}=g(R(\partial_i,\partial_j)\partial_k,\partial_l)`, the unit-sphere check gives the opposite sign. | Probably `g_{ij}=\delta_{ij}-\tfrac13\mathbb R_{iklj}x^kx^l+\dots` (equivalently `+\tfrac13\mathbb R_{ikjl}`). |
| 2 | L3398 | `parts/04-connections-curvature/05-synthesis-3/03-curvature-vs-dd.tex` | `[\nabla_i,\nabla_j]V^k=R^k{}_{lij}V^l` uses Carroll's index order. | In this document's order, `R^k{}_{ijl}V^l`. |
| 3 | L1764, conventions table | `parts/01-algebra/09-synthesis-1/` | Signature row says "GR notes: (negative, positive)", but the formal box at L794 uses (positive, negative). | Check which one the GR notes use. |
| 4 | L690 | `parts/01-algebra/02-tensors/03-tensor-types.tex` | "(In the notes this appears with B=A.)" refers to a `B` never defined here. | Define `B` or delete the sentence. |
| 5 | `thm:dGA` (2) | `parts/02-manifolds-and-forms/05-ga-calculus/` | Sign of the codifferential and the "standard formula" are convention dependent and unproved; `\hodge\hodge` in Lorentzian signature is never addressed but used for Maxwell in `R^{1,3}`. | State the convention; see glossary identity on `\hodge\hodge` (Euclidean case proved). |
| 6 | `prop:contr` (3) | `parts/01-algebra/06-multivector-operations/` | Only a proof idea; `thm:dual` depends on it. | Glossary Part C proves the vector case; general case still open. |
| 7 | `thm:dprops` (2), (3), (5) | `parts/02-manifolds-and-forms/03-tensor-fields-forms/03-exterior-derivative.tex` | Stated without proof. | (3) proved for 1-forms in glossary Part C; (2), (5) left to references. |
| 8 | `eq:antider` | moved to `sec:interior` | Never proved (two places pointed at each other). | Proof added by rewriter. |
| 9 | L1196 | `parts/01-algebra/04-exterior-algebra/05-wedge-and-tensor-product.tex` | Kobayashi–Nomizu cited by name, not in the bibliography. | Add a bibitem if wanted. |
| 10 | "Narciso's notes", "Lee Prop. 7.5" | Part IV | External citations without a bibliography entry (Lee has one). | Narciso: add a bibitem or drop the name. |
| 11 | Euler–Lagrange equations, Laurent series | Parts IV–VI | Used beyond the stated reader profile. | Glossary entries added; consider a one-line recap. |
| 12 | "lecture notes I4" / "the notes" at L297, 690, 711, 1833, 1843, 1991, 2029, 3175, 3297, 3701 | various | External references to lecture notes that are not in the bibliography. | Kept verbatim; decide whether to add a bibitem. |
| 13 | Lorentzian Hodge signs | Part V (Maxwell) | Signs of `\hodge` on `R^{1,3}` depend on conventions not fixed in the text. | Flagged only. |
