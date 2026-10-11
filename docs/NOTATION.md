# Notation

Conventions used throughout, and the overloaded symbols that remain (each is disambiguated by context).

## Conventions

| Object | Notation | Macro | Notes |
|---|---|---|---|
| Vector space, dimension | `V`, `n` | — | Part I blocks from source B used `E`; normalised to `V`. `m` is kept for manifold dimension in Parts II and IV, where the source does so. |
| Field of scalars | `\R` (sometimes `\K`) | `\R`, `\K` | `\K` where the statement holds over any field. |
| Dual space, covector | `V^*`, `\alpha`, `\beta` | — | |
| Dual basis | `e^i` (algebra), `\dd x^i` (manifolds) | — | Previewed at the start of `sec:contraction`. |
| Reciprocal frame (GA) | `e^i_\sharp` | — | Written with `\sharp` where it must be distinguished from the dual basis; `rem:reciprocal` explains the identification. |
| Tensors of type (l,k) | `\TT{l}{k}(V)` | `\TT` | Synthesis I table writes `T^\ell_k`. |
| Tensor fields | `\TF{l}{k}(M)` | `\TF` | `\Pi` also denotes parallel transport `\Pi^\gamma`. |
| Metric | `g`, `\eta` (Minkowski) | — | Signature conventions: the pitfall in `sec:quadform` is the authority. |
| Musical isomorphisms | `v^\flat`, `\alpha^\sharp` | — | |
| Pull-back | `\phi\pb\omega` | `\pb` | Source B typed `\Phi^*`; normalised (same rendering). |
| Pushforward | `T_p\Phi`, `\dd\phi_p` | — | Both kept. |
| Exterior derivative | `\dd` | `\dd` | |
| Interior product | `\iota_v` | — | Metric-free (`sec:interior`); Chevalley's construction uses a metric `\iota`. |
| Lie derivative, bracket | `\Lie_X`, `[X,Y]` | `\Lie` | |
| Hodge star, codifferential | `\hodge`, `\codiff` | `\hodge`, `\codiff` | |
| Geometric algebra | `\GA(V)`, `\Cl(p,q)` | `\GA`, `\Cl` | |
| Contractions | `A\lc B`, `A\rc B` | `\lc`, `\rc` | |
| Reverse, grade projection | `\rev{A}`, `\gr{A}{k}` | `\rev`, `\gr` | |
| Pseudoscalar, dual | `\pss`, `\dual{A}` | `\pss`, `\dual` | |
| Rotor | `\rotor` | `\rotor` | `R` is reserved for curvature; `sec:rotors` normalised. |
| Vector derivative | `\vd` (bold nabla) | `\vd` | `\nabla` is the covariant derivative. |
| Christoffel symbols | `\Gamma^k{}_{ij}` | — | Some places write `\Gamma^k_{ij}`. |
| Riemann tensor | `R(X,Y)Z`, `R^l{}_{ijk}`, `\mathbb R_{ijkl}` | — | `\mathbb R_{ijkl}=g(R(\partial_i,\partial_j)\partial_k,\partial_l)`. |

## Angles

- `\phi` (and `\Phi`, `\psi`) is reserved for maps, flows and charts.
- Plane polar coordinates are `(r,\varphi)` in Parts I–IV (converted with `tools/replace_phi.py`; files marked `% REWRITTEN`).
- Part V keeps `(r,\theta)` for plane polar coordinates (mechanics conventions); not converted.
- The sphere uses `(\theta,\varphi)` (polar, azimuth) everywhere, including the Schwarzschild metric in the GR bridge.
- In the glossary, `\theta` is also the angle between two mirrors (`id:tworefl`) and `\varphi` a rotation angle (`id:rotor`).
- The closed-not-exact angle form keeps the traditional name `\dd\theta` in Parts III, V and VI.

## Overloaded letters (kept; disambiguated by context)

| Symbol | Meanings |
|---|---|
| `*` | dual space `V^*`, pull-back `\phi\pb`, GA dual `\dual A` |
| `\Pi` | tensor fields `\TF`, parallel transport `\Pi^\gamma` |
| `T` | torsion, stress–energy, `\partial_t\gamma`, kinetic energy, `T^kV^*` |
| `R` | curvature, Green's rectangle, third component in `P\,dx+Q\,dy+R\,dz` |
| `Q` | quadratic form, charge, generalised forces, second component in `P\,dx+Q\,dy` |
| `K` | Gaussian curvature, the field `\K` |
| `S` | symmetric group, symmetric power, action, `\partial_s\gamma` |
| `\iota` | metric interior product (Chevalley) vs metric-free interior product |
