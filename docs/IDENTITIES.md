# Identities (glossary Part C)

Status: **orig** = proved in the original (cleaned up in Part C, pointing back);
**added** = proof added by the rewriter (`% PROOF ADDED BY REWRITER`);
**flagged** = stated without proof, with a pointer to a reference.

| Label | Identity | Source label | Status | Part C file |
|---|---|---|---|---|
| `id:fund` | `uv+vu=2\,u\cdot v` | `prop:fund` | orig | 01-geometric-product |
| `id:abdecomp` | `ab=a\cdot b+a\wedge b` | `prop:abdecomp` | orig | 01-geometric-product |
| `id:lcwedge` | `a\lc(b\wedge c)=(a\cdot b)c-(a\cdot c)b` | `prop:contr` (1) | added | 01-geometric-product |
| `id:contr3` | `(A\wedge B)\lc C=A\lc(B\lc C)` for vectors `A,B` | `prop:contr` (3) | added (vector case) | 01-geometric-product |
| `id:cross` | `a\times b=-\pss(a\wedge b)` | `prop:cross` | orig | 01-geometric-product |
| `id:dual` | `\dual{(A\wedge B)}=A\lc\dual B` | `thm:dual` | orig | 01-geometric-product |
| `id:hodgehodge` | `\hodge\hodge=(-1)^{k(n-k)}` (Euclidean) | `sec:duality` | added | 01-geometric-product |
| `id:refl` | reflection `v\mapsto -nvn^{-1}` | `thm:refl` | orig | 02-rotors |
| `id:tworefl` | two reflections = rotation by `2\theta` | `thm:rotor` | added | 02-rotors |
| `id:rotor` | `v\mapsto \rotor v\rev\rotor` | `thm:rotor` | orig | 02-rotors |
| `id:pbfun` | `\phi\pb f=f\circ\phi` | `eq:pullback` | added | 03-pullback |
| `id:pbwedge` | `\phi\pb(\alpha\wedge\beta)=\phi\pb\alpha\wedge\phi\pb\beta` | `prop:wedgeprops` (e) | added | 03-pullback |
| `id:pbcomp` | `(\psi\circ\phi)\pb=\phi\pb\psi\pb` | — | added | 03-pullback |
| `id:pbd` | `\phi\pb\dd\omega=\dd\phi\pb\omega` | `thm:dprops` | added | 03-pullback |
| `id:natural` | naturality of the line integral | `eq:natural` | orig | 03-pullback |
| `id:det` | `\alpha^1\wedge\dots\wedge\alpha^k(v_1,\dots,v_k)=\det(\alpha^i(v_j))` | `sec:extalg` | added | 04-forms-derivatives |
| `id:assoc` | associativity of `\wedge` | `prop:wedgeprops` | added | 04-forms-derivatives |
| `id:antider` | `\iota_v(\alpha\wedge\beta)=\iota_v\alpha\wedge\beta+(-1)^k\alpha\wedge\iota_v\beta` | `eq:antider` | added | 04-forms-derivatives |
| `id:lcisiota` | left contraction = interior product | `prop:lcisiota` | orig | 04-forms-derivatives |
| `id:iotahodge` | `\iota_v\alpha=(-1)^{n(k-1)}\hodge(v^\flat\wedge\hodge\alpha)` (Euclidean) | — | added | 04-forms-derivatives |
| `id:ddzero` | `\dd^2=0` | `thm:dprops` (1) | orig | 04-forms-derivatives |
| `id:dinvariant` | `\dd\alpha(X,Y)=X\alpha(Y)-Y\alpha(X)-\alpha([X,Y])` | `thm:dprops` (3) | added | 04-forms-derivatives |
| `id:cartan` | `\Lie_X=\dd\iota_X+\iota_X\dd` | `thm:cartan` | orig | 04-forms-derivatives |
| `id:liedx` | `\Lie_X\dd x^i=\dd X^i`, `eq:liemetric` | `eq:liemetric` | added | 04-forms-derivatives |
| `id:operators` | grad/curl/div as `\dd` | `prop:operators` | orig | 04-forms-derivatives |
| `id:dGA` | `\vd=\dd-\codiff` decomposition | `thm:dGA` | orig (1,3,4,5); (2) flagged | 04-forms-derivatives |
| `id:reparam` | reparametrisation invariance | `prop:reparam` | orig | 05-integration-stokes |
| `id:ftc` | `\int_\gamma\dd f=f(b)-f(a)` | `eq:ftc` | orig | 05-integration-stokes |
| `id:stokes` | `\int_M\dd\omega=\int_{\partial M}\omega` | `thm:stokes` | orig | 05-integration-stokes |
| `id:fluxbdry` | flux-boundary lemma | `lem:fluxbdry` | orig | 05-integration-stokes |
| `id:gauss` | divergence theorem | `thm:gauss` | orig | 05-integration-stokes |
| `id:divcoord` | `\operatorname{div}X=\frac1{\sqrt{|g|}}\partial_i(\sqrt{|g|}X^i)` | `eq:divcoord` | orig | 05-integration-stokes |
| `id:cauchy` | Cauchy theorem | `thm:cauchy` | orig | 05-integration-stokes |
| `id:residue` | residue theorem (as Stokes) | `thm:residue` | orig | 05-integration-stokes |
| `id:pompeiu` | Cauchy–Pompeiu | `eq:pompeiu` | orig | 05-integration-stokes |
| `id:argument` | argument principle | `eq:argument` | orig | 05-integration-stokes |
| `id:CRga` | Cauchy–Riemann as `\vd f=0` | `prop:CRga` | orig | 05-integration-stokes |
| `id:gammatrans` | transformation law of `\Gamma` | `sec:conn` | added | 06-curvature |
| `id:riemanncomp` | Riemann components from `\Gamma` | `eq:riemanncomp` | added | 06-curvature |
| `id:bianchi1` | first Bianchi identity (torsion-free) | `sec:curvprops` | added | 06-curvature |
| `id:riemannsym` | antisymmetries and pair symmetry of `\mathbb R` | `sec:curvprops` | added | 06-curvature |
| `id:threederivs` | three derivatives agree on functions | `prop:threederivs` | orig | 06-curvature |
| `id:divagree` | divergences agree | `prop:divagree` | orig | 06-curvature |
| `id:deviation` | geodesic deviation | `sec:deviation` | orig (given lemma); lemma added in coordinates | 06-curvature |
| — | second / contracted Bianchi | — | flagged | 06-curvature |
| — | Poincaré lemma | — | flagged | 04-forms-derivatives |
| — | existence/uniqueness of `\dd` | — | flagged | 04-forms-derivatives |
| — | normal-coordinate expansion | — | flagged (sign suspect, AUTHOR_NOTES #1) | 06-curvature |
| — | Lorentzian Hodge signs | — | flagged | 01-geometric-product |

Exact source labels are confirmed while writing Part C; the final list is the one in `backmatter/glossary/part-c-identities/`.
