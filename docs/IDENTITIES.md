# Identities (glossary Part C): final list

Status: **orig** = proved in the original (restated in Part C with a step-by-step proof, pointing back);
**added** = proof added by the rewriter (marked `% PROOF ADDED BY REWRITER` in the Part C file);
**flagged** = used but not proved; listed in the "Used but not proved here" paragraph of `part-c-identities/00-intro.tex` with references.

Numbering is automatic (C.1, C.2, ... in the order below); labels are `id:...`.

| Label | Identity | Body label | Status | Part C file |
|---|---|---|---|---|
| `id:fund` | `uv+vu=2\,u\cdot v` | `eq:cliff` | orig | 01-geometric-product |
| `id:abdecomp` | `ab=a\cdot b+a\wedge b` | `eq:polar` | orig | 01-geometric-product |
| `id:lcwedge` | `a\lc(b\wedge c)=(a\cdot b)c-(a\cdot c)b` | `prop:contr` (1), k=2 | added | 01-geometric-product |
| `id:contr3` | `A\lc(B\lc C)=(A\wedge B)\lc C` (general, via basis blades) | `prop:contr` (3) | added | 01-geometric-product |
| `id:cross` | cross product as a dual | `prop:cross` | orig | 01-geometric-product |
| `id:dual` | duality of `\wedge` and `\lc` | `thm:dual` | orig (now via `id:contr3`) | 01-geometric-product |
| `id:hodgehodge` | `\hodge\hodge=(-1)^{k(n-k)}` (Euclidean) | `thm:hodgeGA` | added | 01-geometric-product |
| `id:refl` | `x\mapsto-nxn^{-1}` is a reflection | `thm:refl` | orig | 02-rotors |
| `id:rotor` | `x\mapsto\rotor x\rev\rotor` rotates by `\varphi` | `thm:rotor` | orig | 02-rotors |
| `id:tworefl` | two reflections = rotation by `2\theta` | intuition after `thm:rotor` | added | 02-rotors |
| `id:pbfun` | `\phi\pb(f\alpha)=(f\circ\phi)\phi\pb\alpha`, `\phi\pb\dd f=\dd(f\circ\phi)` | `eq:pullback` | added | 03-pullback |
| `id:pbwedge` | `\phi\pb(\alpha\wedge\beta)=\phi\pb\alpha\wedge\phi\pb\beta` | `sec:pushpull` | orig | 03-pullback |
| `id:pbcomp` | `(\psi\circ\phi)\pb=\phi\pb\psi\pb` | `sec:pushpull` | added | 03-pullback |
| `id:pbd` | `\phi\pb\dd\omega=\dd\phi\pb\omega` | `thm:dprops` (2) | added | 03-pullback |
| `id:natural` | naturality of the line integral | `eq:natural` | orig | 03-pullback |
| `id:assoc` | associativity of `\wedge`; `f\wedge\alpha=f\alpha` | `prop:wedgeprops` (a) | added | 04-forms-derivatives |
| `id:det` | determinant formula | `prop:detformula` | added (detail) | 04-forms-derivatives |
| `id:antider` | `\iota_v` is an antiderivation | `eq:antider` | orig (proof added in Phase 3) | 04-forms-derivatives |
| `id:lcisiota` | left contraction = interior product | `prop:lcisiota` | orig | 04-forms-derivatives |
| `id:iotahodge` | `\iota_v\alpha=(-1)^{(n-k)(k-1)}\hodge(v^\flat\wedge\hodge\alpha)`, `\iota_v\vol=\hodge v^\flat` | `sec:classical` | added | 04-forms-derivatives |
| `id:ddzero` | `\dd\dd=0` | `thm:dprops` (1) | orig | 04-forms-derivatives |
| `id:dinvariant` | invariant formula for `\dd` of a 1-form | `thm:dprops` (3), k=1 | added | 04-forms-derivatives |
| `id:cartan` | `\Lie_X=\dd\iota_X+\iota_X\dd` | `thm:cartan` | orig | 04-forms-derivatives |
| `id:liedx` | `\Lie_X\dd x^i=\dd X^i`; `(\Lie_Xg)_{ab}` | `eq:liemetric` | added | 04-forms-derivatives |
| `id:dGA` | `\dd\leftrightarrow\vd\wedge`; `\vd\wedge\vd\wedge=0=\vd\lc\vd\lc` | `thm:dGA` (1), (3) | orig | 04-forms-derivatives |
| `id:reparam` | reparametrisation | `prop:reparam` | orig | 05-integration-stokes |
| `id:ftc` | `\int_\gamma\dd f=f(\gamma(b))-f(\gamma(a))` | `eq:ftc` | orig | 05-integration-stokes |
| `id:stokes` | generalised Stokes | `thm:stokes` | orig (compact) | 05-integration-stokes |
| `id:fluxbdry` | `j\pb(\iota_X\vol_g)=\langle X,N\rangle\dd A` | `lem:fluxbdry` | orig | 05-integration-stokes |
| `id:divmu` | `\dd\iota_X\mu=\operatorname{div}_\mu X\,\mu` and the coordinate formula | `eq:divmu`, `eq:divcoord` | orig | 05-integration-stokes |
| `id:gauss` | divergence theorem | `thm:gauss` | orig | 05-integration-stokes |
| `id:cauchy` | `\dd(f\dd z)=2i\partial_{\bar z}f\,\dd x\wedge\dd y`; Cauchy | `eq:dfdz`, `thm:cauchy` | orig | 05-integration-stokes |
| `id:residue` | residue theorem | `thm:residue` | orig | 05-integration-stokes |
| `id:CRga` | Cauchy–Riemann as `\vd\mathbf u=0` | `prop:CRga` | orig | 05-integration-stokes |
| `id:gammatrans` | transformation law of `\Gamma` | `eq:christtransf` | added | 06-curvature |
| `id:riemanncomp` | `R^l{}_{ijk}` from `\Gamma` | `eq:riemanncomp` | added | 06-curvature |
| `id:bianchi1` | first Bianchi identity (torsion-free) | general properties of `R` | added | 06-curvature |
| `id:riemannsym` | antisymmetry in the last pair; pair symmetry | metric case (a), (b) | added | 06-curvature |
| `id:threederivs` | `\dd` and `\Lie_Xg` through `\nabla` | `prop:threederivs` | orig | 06-curvature |
| `id:divagree` | `\Gamma^i{}_{ij}=\partial_j\ln\sqrt{|g|}` | `prop:divagree` | orig (Jacobi's formula added) | 06-curvature |
| - | second Bianchi identity | metric case (c) | flagged | 00-intro |
| - | Poincaré lemma | `thm:dprops` (5) | flagged | 00-intro |
| - | existence and uniqueness of `\dd` | `def:d` | flagged | 00-intro |
| - | normal-coordinate expansion | metric case | flagged (sign suspect, AUTHOR_NOTES #1) | 00-intro |
| - | Lorentzian Hodge signs | Part V | flagged | 00-intro |

Dropped from the Phase 1 draft, because the body already gives a complete step-by-step proof and Part C would only repeat it:
`id:operators` (grad/curl/div), `id:pompeiu`, `id:argument`, `id:deviation`. `id:divcoord` was merged into `id:divmu`.
