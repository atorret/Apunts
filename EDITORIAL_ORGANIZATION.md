# Editorial organization

The reading order that takes each document from its entry level to its target level. This file is generated from `library.sqlite`. Edit a book by importing its organization file, or import an editorial organization change file that names the new, edited, and deleted books and chapters. Either import rewrites this file. Editorial status can also be set in the browser. Sources are listed under each book. Edit them in that book's organization file. Book dependencies are listed under each book. Edit which books must be finished first in that book's organization file, or in an editorial organization change file. The hand-edited revision log is in [EDITORIAL_ORGANIZATION_HISTORY.md](EDITORIAL_ORGANIZATION_HISTORY.md).

- **Present** chapters are existing material. The path is the chapter folder.
- **Absent** chapters are named steps with no content yet (`TODO(DOC/chNN)`).
- **Retired** rows keep a chapter number whose text now lives somewhere else.
- Levels: basic, undergraduate, graduate, postdoc/research.
- An optional prerequisite is marked *(opt.)*. Unmarked prerequisites are hard.
- Editorial status is separate from presence: Idea, To Design, Building, To Review, Finished, or a registered custom name.

Documents: [M0](#m0), [M1](#m1), [M2](#m2), [M3](#m3), [CM1](#cm1), [CM2](#cm2), [CM3](#cm3), [EM](#em), [TH](#th), [F1](#f1), [F2](#f2), [QM](#qm), [QFT](#qft), [GR](#gr), [GLOSSARY](#glossary).

## Level scale

- **basic**: first-year material with no previous course assumed.
- **undergraduate**: standard degree-course material.
- **graduate**: first-year graduate courses.
- **postdoc/research**: topics at the research frontier.

## Topic ownership

A topic lists every chapter or book that owns it, and every chapter or book that only references it.

| topic | owner | referenced by |
| --- | --- | --- |
| Calculus of variations (mathematics) | [M0/ch09](#m0) | [CM2/ch01](#cm2), [CM3/ch08](#cm3), [EM/ch05](#em), [M3/ch07](#m3) |
| Classical electrodynamics: Maxwell's equations, waves, radiation, covariant formulation | [EM](#em) | [F2/ch05](#f2), [GR/ch03](#gr), [QFT](#qft) |
| Complex analysis | [M0/ch12](#m0), [M2/ch17](#m2) | [F1/ch06](#f1), [M3/ch03](#m3) |
| Continuum kinematics, strain, Cauchy stress, balance laws | [CM3/ch02](#cm3), [CM3/ch03](#cm3) | [F1](#f1) |
| Electromagnetism as differential forms | [GR/ch03](#gr) | [F2/ch05](#f2) |
| Geometric algebra, connections, curvature, Lie groups | [M2](#m2) | [CM2](#cm2), [GR](#gr), [QFT](#qft), [QM](#qm) |
| Green's, Stokes' and divergence theorems | [M0/ch04](#m0), [M1/ch11](#m1), [M1/ch12](#m1) | [CM3/ch03](#cm3), [F1/ch02](#f1), [M0/ch12](#m0), [M3/ch05](#m3) |
| Hawking radiation and the Unruh effect | [QFT/ch12](#qft) | [GR/ch13](#gr) |
| Hilbert spaces | [M2/ch18](#m2), [QM/ch04](#qm) | [M2/ch19](#m2), [M3/ch07](#m3), [QM](#qm) |
| Hodge star | [M1/ch04](#m1), [M2/ch04](#m2) | [F1/ch05](#f1), [GR/ch03](#gr), [M1/ch07](#m1), [M1/ch12](#m1) |
| Lie derivative, Lie bracket and Cartan's formula | [M1/ch08](#m1) | [CM2/ch03](#cm2), [F1/ch05](#f1), [GR/ch04](#gr), [M1/ch12](#m1), [M2/ch11](#m2), [M2/ch12](#m2), [M2/ch13](#m2), [M2/ch14](#m2), [M2/ch15](#m2) |
| Numbers, one-variable calculus, matrices and determinants | [M0](#m0) | [CM1](#cm1), [CM2](#cm2), [CM3](#cm3), [EM](#em), [F1](#f1), [F2](#f2), [GLOSSARY](#glossary), [GR](#gr), [M0](#m0), [M1](#m1), [M2](#m2), [M3](#m3), [QFT](#qft), [QM](#qm), [TH](#th) |
| Numerical methods | [CM3/ch12](#cm3), [F2/ch08](#f2), [M0/ch11](#m0), [M3/ch09](#m3) |  |
| Ordinary differential equations: existence and uniqueness, linear systems, Sturm-Liouville, dynamical systems, asymptotic methods | [M0/ch05](#m0), [M3/ch01](#m3), [M3/ch02](#m3), [M3/ch03](#m3) | [CM1/ch05](#cm1), [CM2/ch05](#cm2), [F1/ch08](#f1), [F1/ch09](#f1), [QM/ch09](#qm) |
| Partial differential equations: classification, elliptic, parabolic, hyperbolic, weak solutions, nonlinear PDEs, Green's functions | [M0/ch08](#m0), [M3/ch04](#m3), [M3/ch05](#m3), [M3/ch06](#m3), [M3/ch07](#m3), [M3/ch08](#m3), [M3/ch09](#m3), [M3/ch10](#m3) | [CM3/ch07](#cm3), [CM3/ch12](#cm3), [F1/ch11](#f1), [F1/ch12](#f1), [F2/ch07](#f2), [F2/ch08](#f2), [GR/ch10](#gr) |
| Probability and stochastic processes | [M0/ch10](#m0), [M2/ch19](#m2) | [F2/ch01](#f2), [QM/ch13](#qm), [TH](#th) |
| Small oscillations and normal modes | [CM1/ch05](#cm1) | [CM2/ch01](#cm2) |
| Special functions | [M0/ch07](#m0) | [M0/ch08](#m0), [QM/ch07](#qm) |
| Special relativity and Minkowski geometry | [EM/ch02](#em), [EM/ch03](#em) | [CM2/ch07](#cm2), [F2](#f2), [GR](#gr), [QFT](#qft), [QM/ch15](#qm) |
| Spinors | [M2/ch16](#m2) | [CM2/ch06](#cm2), [CM2/ch07](#cm2), [GR/ch11](#gr), [QFT/ch01](#qft), [QM/ch15](#qm) |
| Symbols, terms, identities, bibliography | [GLOSSARY](#glossary) | [CM1](#cm1), [CM2](#cm2), [CM3](#cm3), [EM](#em), [F1](#f1), [F2](#f2), [GLOSSARY](#glossary), [GR](#gr), [M0](#m0), [M1](#m1), [M2](#m2), [M3](#m3), [QFT](#qft), [QM](#qm), [TH](#th) |
| Tensors, differential forms, integration on manifolds | [M1/ch01](#m1), [M1/ch02](#m1), [M1/ch03](#m1), [M1/ch04](#m1), [M1/ch05](#m1), [M1/ch06](#m1), [M1/ch07](#m1), [M1/ch08](#m1), [M1/ch09](#m1), [M1/ch10](#m1), [M1/ch11](#m1), [M1/ch12](#m1) | [CM1](#cm1), [CM2](#cm2), [CM3](#cm3), [EM](#em), [F1](#f1), [F2](#f2), [GLOSSARY](#glossary), [GR](#gr), [M0](#m0), [M1](#m1), [M2](#m2), [M3](#m3), [QFT](#qft), [QM](#qm), [TH](#th) |
| Thermodynamics, equilibrium statistical mechanics, kinetic theory, non-equilibrium | [TH](#th) | [CM3/ch11](#cm3), [F1/ch02](#f1), [F2/ch03](#f2), [F2/ch05](#f2), [F2/ch07](#f2), [F2/ch10](#f2), [GR/ch13](#gr), [GR/ch14](#gr), [QFT/ch17](#qft) |
| Topology: homotopy, homology, de Rham cohomology | [M2/ch22](#m2) | [CM3/ch13](#cm3), [GR/ch12](#gr), [QFT/ch11](#qft) |

## Coverage of the requested topics

| requested | where |
| --- | --- |
| Classical electrodynamics and special relativity | EM |
| Classical mechanics, 3D to Lagrangian to postdoc with modern mathematics | CM2; geometric algebra in CM2/ch06 and CM2/ch07, prepared by M2 |
| Classical mechanics, basic Newton to 3D | CM1 (basic to undergraduate) |
| Elastic materials, zero to postdoc | CM3 (basic to postdoc/research) |
| Fluids from Navier-Stokes to postdoc | F1 (classical flows), F2 (extensions below) |
| General relativity from nothing to postdoc | EM/ch02 to EM/ch03 (special relativity), then GR (undergraduate to postdoc/research) |
| Interfaces, capillarity and wetting | F2/ch09 |
| Kinetic theory and the hydrodynamic limit | TH/ch05, F2/ch10 |
| Mathematics needed for all of this | M0, M1, M2, M3 |
| Multifluid flows, mixing and unmixing | F2/ch04 |
| Non-Newtonian flows | F2/ch02 |
| Ordinary and partial differential equations (theory, stability, asymptotics, numerics) | M0/ch05, M0/ch08 (basics); M3 (graduate to postdoc/research) |
| Plasma flows | F2/ch05 |
| QFT from quantum mechanics to postdoc | QFT (graduate to postdoc/research) |
| Quantum flows | F2/ch07 |
| Quantum mechanics from nothing to full QM | QM (basic to graduate) |
| Rotating and stratified flows | F1/ch13 |
| Special-relativistic flows | F2/ch06 |
| Temperature-dependent flows | F2/ch03 |
| Thermodynamics and statistical mechanics | TH |
| Turbulence | F1/ch10 (introduction), F2/ch01 (advanced) |

<a id="m0"></a>

## M0 Mathematics 0: Basics and Undergraduate Methods

- Folder: [M0-math-basics/](M0-math-basics/)
- Entry level: zero. Target level: undergraduate.
- Editorial status: Idea
- Entry level: zero. Target level: undergraduate (the first-year toolkit of M0/ch01 to M0/ch03, then the undergraduate methods that M1 and the physics documents assume).
- Finish first: nothing (entry point of the series)
- Reading note: M0/ch02 and M0/ch03 are independent of each other; both need only M0/ch01. M0/ch04 and M0/ch05 need both and are independent of each other. M0/ch06 to M0/ch12 follow the prerequisites in the table; M0/ch09, M0/ch10 and M0/ch12 branch off early and do not need the Fourier, special-function or PDE chapters.
- Green's theorem (planar), Stokes' theorem and the divergence theorem are first met in classical vector-calculus form in M0/ch04; M0/ch12 uses the planar Green theorem to prove Cauchy's theorem.
- Target level completed by: **M0/ch09 Calculus of variations**, **M0/ch10 Probability, statistics and random processes**, **M0/ch11 Numerical methods** and **M0/ch12 Complex analysis** (all TODO), which are parallel branches.
- Chapters: 12 planned, 0 present, 12 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| M0/ch01 | Numbers, complex numbers, sets and functions | basic | none | Idea | TODO(M0/ch01); Idea |
| M0/ch02 | Calculus of one variable | basic | [M0/ch01](#m0) | Idea | TODO(M0/ch02); Idea |
| M0/ch03 | Linear algebra: matrices, determinants, eigenvalues | basic | [M0/ch01](#m0) | Idea | TODO(M0/ch03); Idea |
| M0/ch04 | Multivariable and vector calculus in three dimensions: gradient, divergence, curl, line and surface integrals, and the classical theorems of Green, Stokes and Gauss | undergraduate | [M0/ch02](#m0); [M0/ch03](#m0) | Idea | TODO(M0/ch04); Idea |
| M0/ch05 | Ordinary differential equations | undergraduate | [M0/ch02](#m0); [M0/ch03](#m0) | Idea | TODO(M0/ch05); Idea |
| M0/ch06 | Fourier series, Fourier and Laplace transforms | undergraduate | [M0/ch04](#m0); [M0/ch05](#m0) | Idea | TODO(M0/ch06); Idea |
| M0/ch07 | Special functions: Legendre, Bessel, spherical harmonics and the hypergeometric family | undergraduate | [M0/ch05](#m0); [M0/ch06](#m0) | Idea | TODO(M0/ch07); Idea |
| M0/ch08 | Partial differential equations of physics: separation of variables and Green's functions | undergraduate | [M0/ch04](#m0); [M0/ch05](#m0); [M0/ch06](#m0); [M0/ch07](#m0) | Idea | TODO(M0/ch08); Idea |
| M0/ch09 | Calculus of variations | undergraduate | [M0/ch04](#m0); [M0/ch05](#m0) | Idea | TODO(M0/ch09); Idea |
| M0/ch10 | Probability, statistics and random processes | undergraduate | [M0/ch02](#m0); [M0/ch04](#m0) | Idea | TODO(M0/ch10); Idea |
| M0/ch11 | Numerical methods: quadrature, ODE solvers, linear systems and finite differences | undergraduate | [M0/ch03](#m0); [M0/ch05](#m0); [M0/ch08](#m0) | Idea | TODO(M0/ch11); Idea |
| M0/ch12 | Complex analysis: analytic functions, Cauchy's theorem, Laurent series, residues and conformal maps | undergraduate | [M0/ch01](#m0); [M0/ch04](#m0) | Idea | TODO(M0/ch12); Idea |

### Book dependencies

Edited in [M0-math-basics/M0-organization.md](M0-math-basics/M0-organization.md). An editorial organization change file can replace the same list.

Finish first: nothing.
Required by: [CM1](#cm1), [M1](#m1), [M3](#m3), [QM](#qm), [TH](#th).


<a id="m1"></a>

## M1 Mathematics I: Foundations

- Folder: [M1-math-foundations/](M1-math-foundations/)
- Entry level: undergraduate. Target level: graduate.
- Finish first: [M0](#m0)
- Editorial status: To Review
- Entry level: undergraduate (after M0). Target level: graduate (differential geometry and integration on manifolds: M1/ch05 to M1/ch12); the tensor-algebra chapters M1/ch01 to M1/ch04 are undergraduate.
- Finish first: [M0](#m0)
- Green's theorem (planar), Stokes' theorem and the divergence theorem are first met in classical vector-calculus form in M0/ch04; M1/ch09 to M1/ch12 then present them as special cases of the general Stokes theorem on manifolds. M0/ch12 uses the planar Green theorem to prove Cauchy's theorem.
- M1/ch08 (the Lie derivative, moved here from M2/ch07) comes straight after the forms chapter M1/ch07 and before the integration chapters, because the Gauss theorem in M1/ch12 is derived from it.
- Why M1/ch08 and the Hodge star are in M1: in main.pdf the divergence is defined by L_X mu = (div X) mu and Gauss is Stokes for the form i_X mu with d i_X mu = L_X mu (Cartan's formula), so M1/ch12 needs M1/ch08. The curl in M1/ch07 and the classical dictionary grad, curl, div via the musical isomorphisms and the Hodge star in M1/ch12 need the star, which is therefore defined in M1/ch04. M1 stays independent of M2.
- The Lie bracket appears in Theorem 12.5(3) of M1/ch07 (the invariant formula for d); the text defines it inline, so M1/ch08 is not a prerequisite of M1/ch07. The Synthesis boxes at the end of M1/ch10 and M1/ch12 compare with geometric algebra and point forward to M2/ch04 and M2/ch09: they are comparisons, not prerequisites.
- M1 chapters are numbered consecutively, M1/ch01 to M1/ch12, in reading order.
- Target level completed by: **M1/ch12 The Gauss (divergence) theorem** (present), which needs **M1/ch08 The Lie derivative and Cartan's formula** (present).
- Chapters: 12 planned, 12 present, 0 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| M1/ch01 | Vectors, covectors and contraction | undergraduate | none | To Review | present: [M1-math-foundations/chapters/ch01-vectors-covectors/](M1-math-foundations/chapters/ch01-vectors-covectors/); To Review |
| M1/ch02 | Multilinear maps, tensors and the tensor algebra | undergraduate | [M1/ch01](#m1); M1 Part intro `part:algebra` | To Review | present: [M1-math-foundations/chapters/ch02-tensors/](M1-math-foundations/chapters/ch02-tensors/); To Review |
| M1/ch03 | The metric tensor and the musical isomorphisms | undergraduate | [M1/ch01](#m1); [M1/ch02](#m1) | To Review | present: [M1-math-foundations/chapters/ch03-metric/](M1-math-foundations/chapters/ch03-metric/); To Review |
| M1/ch04 | The exterior algebra, the wedge product and the Hodge star *(the Hodge star (Definition 8.9, the sign rule and the star on forms) moves here from main.pdf §8.4; its comparison with the geometric-algebra dual stays in M2/ch04)* | undergraduate | [M1/ch01](#m1); [M1/ch02](#m1); [M1/ch03](#m1) | To Review | present: [M1-math-foundations/chapters/ch04-exterior-algebra/](M1-math-foundations/chapters/ch04-exterior-algebra/); To Review |
| M1/ch05 | Differentiable manifolds | graduate | M1 Part intro `part:algebra` | To Review | present: [M1-math-foundations/chapters/ch05-differentiable-manifolds/](M1-math-foundations/chapters/ch05-differentiable-manifolds/); To Review |
| M1/ch06 | Tangent and cotangent spaces | graduate | [M1/ch01](#m1); [M1/ch02](#m1); [M1/ch03](#m1); [M1/ch04](#m1); [M1/ch05](#m1) | To Review | present: [M1-math-foundations/chapters/ch06-tangent-cotangent/](M1-math-foundations/chapters/ch06-tangent-cotangent/); To Review |
| M1/ch07 | Tensor fields and differential forms | graduate | [M1/ch01](#m1); [M1/ch02](#m1); [M1/ch03](#m1); [M1/ch04](#m1); [M1/ch06](#m1) | To Review | present: [M1-math-foundations/chapters/ch07-tensor-fields-forms/](M1-math-foundations/chapters/ch07-tensor-fields-forms/); To Review |
| M1/ch08 | The Lie derivative and Cartan's formula *(graduate; moved from M2/ch07; includes the operator relations [∂_i, x^j] = {ι_i, dx^j ∧} = δ and the Heisenberg/fermion remark)* | graduate | [M1/ch04](#m1); [M1/ch06](#m1); [M1/ch07](#m1) | To Review | present: [M1-math-foundations/chapters/ch08-lie-derivative/](M1-math-foundations/chapters/ch08-lie-derivative/); To Review |
| M1/ch09 | Integration of 1-forms | graduate | [M1/ch01](#m1); [M1/ch06](#m1); [M1/ch07](#m1) | To Review | present: [M1-math-foundations/chapters/ch09-integration-1-forms/](M1-math-foundations/chapters/ch09-integration-1-forms/); To Review |
| M1/ch10 | From 1-forms to k-forms: integration is full contraction | graduate | [M1/ch04](#m1); [M1/ch06](#m1); [M1/ch09](#m1) | To Review | present: [M1-math-foundations/chapters/ch10-integration-k-forms/](M1-math-foundations/chapters/ch10-integration-k-forms/); To Review |
| M1/ch11 | Stokes' theorem as it is understood today | graduate | [M1/ch05](#m1); [M1/ch07](#m1); [M1/ch09](#m1); [M1/ch10](#m1) | To Review | present: [M1-math-foundations/chapters/ch11-stokes/](M1-math-foundations/chapters/ch11-stokes/); To Review |
| M1/ch12 | The Gauss (divergence) theorem | graduate | [M1/ch03](#m1); [M1/ch04](#m1); [M1/ch07](#m1); [M1/ch08](#m1); [M1/ch10](#m1); [M1/ch11](#m1) | To Review | present: [M1-math-foundations/chapters/ch12-gauss/](M1-math-foundations/chapters/ch12-gauss/); To Review |

### Book dependencies

Edited in [M1-math-foundations/M1-organization.md](M1-math-foundations/M1-organization.md). An editorial organization change file can replace the same list.

Finish first: [M0](#m0).
Required by: [CM1](#cm1), [M2](#m2).


### Sources

Edited in [M1-math-foundations/M1-organization.md](M1-math-foundations/M1-organization.md).

| ID | file | proposed chapter | status | reference |
| --- | --- | --- | --- | --- |
| Spivak | none | - | cited, no file | M. Spivak, *Calculus on Manifolds*, Benjamin, 1965. |
| Lee | none | - | cited, no file | J. M. Lee, *Introduction to Smooth Manifolds*, 2nd ed., Springer GTM 218, 2013 (Chapters 11, 14, 16); and *Introduction to Riemannian Manifolds*, 2nd ed., Springer, 2018. |
| BottTu | none | - | cited, no file | R. Bott and L. W. Tu, *Differential Forms in Algebraic Topology*, Springer GTM 82, 1982. |
| Katz | none | - | cited, no file | V. J. Katz, ``The history of Stokes' theorem'', *Mathematics Magazine* 52 (1979), 146-156. |

<a id="m2"></a>

## M2 Mathematics II: Advanced

- Folder: [M2-math-advanced/](M2-math-advanced/)
- Entry level: undergraduate. Target level: graduate.
- Finish first: [M1](#m1)
- Editorial status: To Review
- Entry level: undergraduate. Target level: graduate (tensors, geometric algebra, differential geometry, groups); the last Lie-group, bundle and survey chapters reach postdoc/research.
- Finish first: [M1](#m1); chapter-specific: [M0/ch12](#m0) for M2/ch17, [M0/ch06](#m0) for M2/ch18, [M0/ch10](#m0) for M2/ch19 (transitively also M0)
- Reading note: M2/ch22 is appended after the master summary so that existing chapter numbers do not change; it can be read any time after M1/ch11 and M2/ch06.
- M2/ch07 is a retired number: the Lie derivative and Cartan's formula moved to M1/ch08, because M1/ch12 (Gauss) is derived from Cartan's formula and Part IV (torsion, curvature) uses the Lie bracket. M2/ch04 takes the Hodge star definition from M1/ch04.
- Target level completed by: **M2/ch21 Master summary** (present).
- Chapters: 22 planned, 15 present, 6 absent, 1 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| M2/ch01 | The geometric (Clifford) algebra | graduate | [M1/ch02](#m1); [M1/ch03](#m1); [M1/ch04](#m1) | To Review | present: [M2-math-advanced/chapters/ch01-clifford-algebra/](M2-math-advanced/chapters/ch01-clifford-algebra/); To Review |
| M2/ch02 | Operations on multivectors | graduate | [M1/ch04](#m1); [M2/ch01](#m2) | To Review | present: [M2-math-advanced/chapters/ch02-multivector-operations/](M2-math-advanced/chapters/ch02-multivector-operations/); To Review |
| M2/ch03 | Reflections, rotations and rotors | graduate | [M2/ch01](#m2); [M2/ch02](#m2) | To Review | present: [M2-math-advanced/chapters/ch03-rotors/](M2-math-advanced/chapters/ch03-rotors/); To Review |
| M2/ch04 | Duality: the pseudoscalar, the dual, the cross product and the Hodge star *(the Hodge star is defined in M1/ch04; here only its relation to the geometric-algebra dual and the remarks on the two meanings of dual)* | graduate | [M1/ch03](#m1); [M1/ch04](#m1); [M2/ch02](#m2); [M2/ch03](#m2) | To Review | present: [M2-math-advanced/chapters/ch04-duality/](M2-math-advanced/chapters/ch04-duality/); To Review |
| M2/ch05 | Synthesis I: contraction, duality and the role of the metric | graduate | [M1/ch01](#m1); [M1/ch03](#m1); [M1/ch04](#m1); [M1/ch12](#m1); [M2/ch02](#m2); [M2/ch04](#m2) | To Review | present: [M2-math-advanced/chapters/ch05-synthesis-1/](M2-math-advanced/chapters/ch05-synthesis-1/); To Review |
| M2/ch06 | Groups: symmetry, finite groups and representations | graduate | [M1/ch03](#m1); [M2/ch03](#m2) | Idea | TODO(M2/ch06); Idea |
| M2/ch07 | *(moved to M1/ch08: the Lie derivative and Cartan's formula)* | — | — | — | moved; — |
| M2/ch08 | The exterior derivative in geometric algebra | graduate | [M1/ch07](#m1); [M2/ch02](#m2); [M2/ch04](#m2); [M2/ch05](#m2) | To Review | present: [M2-math-advanced/chapters/ch08-ga-calculus/](M2-math-advanced/chapters/ch08-ga-calculus/); To Review |
| M2/ch09 | Synthesis II: one calculus, three languages | graduate | [M1/ch03](#m1); [M1/ch04](#m1); [M1/ch07](#m1); [M1/ch08](#m1); [M1/ch10](#m1); [M1/ch11](#m1); [M1/ch12](#m1); M1 Part intro `part:algebra`; [M2/ch04](#m2); [M2/ch05](#m2); [M2/ch08](#m2) | To Review | present: [M2-math-advanced/chapters/ch09-synthesis-2/](M2-math-advanced/chapters/ch09-synthesis-2/); To Review |
| M2/ch10 | Connections and the covariant derivative | graduate | [M1/ch02](#m1); [M1/ch06](#m1); [M1/ch07](#m1) | To Review | present: [M2-math-advanced/chapters/ch10-connections/](M2-math-advanced/chapters/ch10-connections/); To Review |
| M2/ch11 | Torsion, the Levi-Civita connection and geodesics | graduate | [M1/ch03](#m1); [M1/ch08](#m1); [M2/ch10](#m2) | To Review | present: [M2-math-advanced/chapters/ch11-levi-civita/](M2-math-advanced/chapters/ch11-levi-civita/); To Review |
| M2/ch12 | The Riemann curvature tensor | graduate | [M2/ch10](#m2); [M2/ch11](#m2) | To Review | present: [M2-math-advanced/chapters/ch12-riemann-curvature/](M2-math-advanced/chapters/ch12-riemann-curvature/); To Review |
| M2/ch13 | Geodesic deviation: tidal forces | graduate | [M2/ch11](#m2); [M2/ch12](#m2) | To Review | present: [M2-math-advanced/chapters/ch13-geodesic-deviation/](M2-math-advanced/chapters/ch13-geodesic-deviation/); To Review |
| M2/ch14 | Synthesis III: three derivatives, three invariants | graduate | [M1/ch07](#m1); [M1/ch08](#m1); [M1/ch09](#m1); [M1/ch12](#m1); [M2/ch10](#m2); [M2/ch11](#m2); [M2/ch12](#m2) | To Review | present: [M2-math-advanced/chapters/ch14-synthesis-3/](M2-math-advanced/chapters/ch14-synthesis-3/); To Review |
| M2/ch15 | Lie groups and Lie algebras | graduate | [M1/ch08](#m1); [M2/ch06](#m2) | Idea | TODO(M2/ch15); Idea |
| M2/ch16 | Fibre bundles, gauge connections and spinors | postdoc/research | [M2/ch10](#m2); [M2/ch15](#m2) | Idea | TODO(M2/ch16); Idea |
| M2/ch17 | The residue theorem as Stokes' theorem *(graduate; its last subsections (currents, Clifford analysis) reach research level)* | graduate | [M0/ch12](#m0); [M1/ch04](#m1); [M1/ch09](#m1); [M1/ch10](#m1); [M1/ch11](#m1); [M1/ch12](#m1); [M2/ch01](#m2); [M2/ch04](#m2); [M2/ch08](#m2); [M2/ch09](#m2) | To Review | present: [M2-math-advanced/chapters/ch17-residue-theorem/](M2-math-advanced/chapters/ch17-residue-theorem/); To Review |
| M2/ch18 | Hilbert spaces, distributions and spectral theory | graduate | [M0/ch06](#m0); [M2/ch17](#m2) | Idea | TODO(M2/ch18); Idea |
| M2/ch19 | Stochastic processes and statistical methods | graduate | [M0/ch10](#m0); [M2/ch18](#m2) | Idea | TODO(M2/ch19); Idea |
| M2/ch20 | The current state of the subject *(postdoc/research survey (geometric measure theory, discrete exterior calculus))* | postdoc/research | [M1/ch11](#m1); [M1/ch12](#m1); [M2/ch01](#m2); [M2/ch09](#m2); [M2/ch17](#m2) | To Review | present: [M2-math-advanced/chapters/ch20-current-state/](M2-math-advanced/chapters/ch20-current-state/); To Review |
| M2/ch21 | Master summary | graduate | [M1/ch06](#m1); [M1/ch08](#m1); [M1/ch12](#m1); M1 Part intro `part:algebra`; M1 Part intro `part:manifolds`; [M2/ch05](#m2); [M2/ch08](#m2); [M2/ch09](#m2); [M2/ch12](#m2); [M2/ch14](#m2); [M2/ch17](#m2); M2 Part intro `part:geometry` | To Review | present: [M2-math-advanced/chapters/ch21-master-summary/](M2-math-advanced/chapters/ch21-master-summary/); To Review |
| M2/ch22 | Topology: homotopy, homology and de Rham cohomology | graduate | [M1/ch07](#m1); [M1/ch11](#m1); [M2/ch06](#m2) | Idea | TODO(M2/ch22); Idea |

### Book dependencies

Edited in [M2-math-advanced/M2-organization.md](M2-math-advanced/M2-organization.md). An editorial organization change file can replace the same list.

Finish first: [M1](#m1).
Required by: [CM2](#cm2), [CM3](#cm3), [GR](#gr), [QFT](#qft).


### Sources

Edited in [M2-math-advanced/M2-organization.md](M2-math-advanced/M2-organization.md).

| ID | file | proposed chapter | status | reference |
| --- | --- | --- | --- | --- |
| Spivak | none | - | cited, no file | M. Spivak, *Calculus on Manifolds*, Benjamin, 1965. |
| Lee | none | - | cited, no file | J. M. Lee, *Introduction to Smooth Manifolds*, 2nd ed., Springer GTM 218, 2013 (Chapters 11, 14, 16); and *Introduction to Riemannian Manifolds*, 2nd ed., Springer, 2018. |
| BottTu | none | - | cited, no file | R. Bott and L. W. Tu, *Differential Forms in Algebraic Topology*, Springer GTM 82, 1982. |
| EvansGariepy | none | - | cited, no file | L. C. Evans and R. F. Gariepy, *Measure Theory and Fine Properties of Functions*, CRC Press (De Giorgi-Federer theorem). |
| Federer | none | - | cited, no file | H. Federer, *Geometric Measure Theory*, Springer, 1969 (currents). |
| Harrison | none | - | cited, no file | J. Harrison, ``Stokes' theorem for nonsmooth chains'', *Bull. AMS* 29 (1993), 235-242. |
| AFW | none | - | cited, no file | D. N. Arnold, R. S. Falk, R. Winther, ``Finite element exterior calculus, homological techniques, and applications'', *Acta Numerica* 15 (2006). |
| MTW | none | - | cited, no file | C. W. Misner, K. S. Thorne, J. A. Wheeler, *Gravitation*, Freeman, 1973 (one-forms as ``stacks of sheets'', Chapters 2-4). |
| Ahlfors | none | - | cited, no file | L. V. Ahlfors, *Complex Analysis*, 3rd ed., McGraw-Hill, 1979. |
| Needham | none | - | cited, no file | T. Needham, *Visual Complex Analysis*, Oxford University Press, 1997. |
| GriffithsHarris | none | - | cited, no file | P. Griffiths and J. Harris, *Principles of Algebraic Geometry*, Wiley, 1978 (residues, Riemann surfaces, Poincar'e-Lelong). |
| Hormander | none | - | cited, no file | L. H"ormander, *An Introduction to Complex Analysis in Several Variables*, North-Holland (Cauchy-Pompeiu, $$). |
| Carroll | none | - | cited, no file | S. Carroll, *Spacetime and Geometry: An Introduction to General Relativity*, Addison-Wesley, 2004. |
| HS | none | - | cited, no file | D. Hestenes and G. Sobczyk, *Clifford Algebra to Geometric Calculus*, Reidel, 1984. |
| DL | none | - | cited, no file | C. Doran and A. Lasenby, *Geometric Algebra for Physicists*, Cambridge University Press, 2003. |
| LM | none | - | cited, no file | H. B. Lawson and M.-L. Michelsohn, *Spin Geometry*, Princeton University Press, 1989. |

<a id="m3"></a>

## M3 Mathematics III: Differential Equations

- Folder: [M3-math-differential-equations/](M3-math-differential-equations/)
- Entry level: undergraduate. Target level: postdoc/research.
- Finish first: [M0](#m0)
- Editorial status: Idea
- Entry level: undergraduate (M0/ch05 and M0/ch08 are the elementary ODE and PDE chapters). Target level: postdoc/research (mathematical theory of the Euler and Navier-Stokes equations, M3/ch10); the other chapters are graduate.
- Finish first: [M0](#m0), and [M2/ch18](#m2) only for M3/ch07 onward (transitively also M1)
- Ownership: this document owns the general theory of ordinary differential equations, dynamical systems, asymptotic methods and partial differential equations; the physics documents reference it and do not repeat it. M3/ch10 states the Euler and Navier-Stokes equations in the form it needs; their physical derivation stays in [F1/ch02](#f1) and [F1/ch03](#f1).
- Reading note: M3/ch01 to M3/ch03 (ordinary equations) and M3/ch04 to M3/ch09 (partial equations) are two blocks; the PDE block needs only M3/ch01 from the ODE block. Green's identities in M3/ch05 follow from the classical divergence theorem of M0/ch04.
- Reading note: M3/ch10 is appended after M3/ch09 so that existing chapter numbers do not change; it was split out of M3/ch08 so that the graduate fluids chapters (F1/ch12, F2/ch07) need only the dispersive-wave half.
- Target level completed by: **M3/ch10 Mathematical theory of the Euler and Navier-Stokes equations** (TODO). M3/ch08 (dispersive waves and solitons) is graduate. M3/ch09 is a graduate methods chapter used by [CM3/ch12](#cm3) and [F2/ch08](#f2).
- Chapters: 10 planned, 0 present, 10 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| M3/ch01 | Ordinary differential equations: existence and uniqueness, linear systems, Floquet theory and Sturm-Liouville problems | graduate | [M0/ch03](#m0); [M0/ch05](#m0) | Idea | TODO(M3/ch01); Idea |
| M3/ch02 | Dynamical systems: phase portraits, stability, bifurcations and chaos | graduate | [M3/ch01](#m3) | Idea | TODO(M3/ch02); Idea |
| M3/ch03 | Asymptotic and perturbation methods: regular and singular perturbations, matched asymptotics, multiple scales, WKB | graduate | [M0/ch12](#m0); [M3/ch01](#m3) | Idea | TODO(M3/ch03); Idea |
| M3/ch04 | Partial differential equations: classification, characteristics, first-order equations and well-posedness | graduate | [M0/ch04](#m0); [M0/ch08](#m0); [M3/ch01](#m3) | Idea | TODO(M3/ch04); Idea |
| M3/ch05 | Elliptic and parabolic equations: Green's identities, maximum principles, Green's functions and the heat kernel | graduate | [M0/ch04](#m0); [M0/ch06](#m0); [M3/ch04](#m3) | Idea | TODO(M3/ch05); Idea |
| M3/ch06 | Hyperbolic equations and conservation laws: wave equation, shocks, the Riemann problem and the Cauchy problem | graduate | [M3/ch04](#m3) | Idea | TODO(M3/ch06); Idea |
| M3/ch07 | Weak solutions, Sobolev spaces and variational formulations | graduate | [M0/ch09](#m0); [M2/ch18](#m2); [M3/ch05](#m3) | Idea | TODO(M3/ch07); Idea |
| M3/ch08 | Nonlinear dispersive waves and solitons | graduate | [M3/ch06](#m3); [M3/ch07](#m3) | Idea | TODO(M3/ch08); Idea |
| M3/ch09 | Numerical methods for PDEs: finite differences, finite volumes, finite elements, spectral methods, stability and convergence | graduate | [M0/ch11](#m0); [M3/ch05](#m3); [M3/ch06](#m3); [M3/ch07](#m3) | Idea | TODO(M3/ch09); Idea |
| M3/ch10 | Mathematical theory of the Euler and Navier-Stokes equations: weak solutions, regularity and blow-up | postdoc/research | [M3/ch07](#m3); [M3/ch08](#m3) | Idea | TODO(M3/ch10); Idea |

### Book dependencies

Edited in [M3-math-differential-equations/M3-organization.md](M3-math-differential-equations/M3-organization.md). An editorial organization change file can replace the same list.

Finish first: [M0](#m0).


<a id="cm1"></a>

## CM1 Classical Mechanics I

- Folder: [CM1-classical-mechanics-1/](CM1-classical-mechanics-1/)
- Entry level: basic Newtonian mechanics. Target level: 3D mechanics.
- Finish first: [M0](#m0), [M1](#m1)
- Editorial status: To Review
- Entry level: basic Newtonian mechanics. Target level: 3D mechanics.
- Finish first: [M0](#m0) and [M1](#m1) (the optional CM1/ch03 also uses [M2/ch10](#m2) and [M2/ch11](#m2))
- Target level completed by: **CM1/ch08 Rigid-body motion in 3D: inertia tensor and Euler equations** (TODO).
- Chapters: 8 planned, 1 present, 7 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| CM1/ch01 | Kinematics in one and three dimensions | basic | [M0/ch04](#m0) | Idea | TODO(CM1/ch01); Idea |
| CM1/ch02 | Newton's laws, forces and free-body problems | basic | [CM1/ch01](#cm1) | Idea | TODO(CM1/ch02); Idea |
| CM1/ch03 | Intrinsic quantities and metric-dependent quantities in physics *(spans undergraduate to graduate: written in the language of differential forms (prerequisites in M1) and uses the Levi-Civita connection (M2/ch11) no other CM1 chapter requires it)* | graduate | [M1/ch09](#m1); [M1/ch12](#m1); M1 Part intro `part:integration`; M1 Part intro `part:manifolds`; [M2/ch11](#m2) | To Review | present: [CM1-classical-mechanics-1/chapters/ch03-intrinsic-vs-metric/](CM1-classical-mechanics-1/chapters/ch03-intrinsic-vs-metric/); To Review |
| CM1/ch04 | Work, energy, momentum and conservation laws; collisions and systems of particles | basic | [CM1/ch02](#cm1) | Idea | TODO(CM1/ch04); Idea |
| CM1/ch05 | Oscillations: free, damped, driven and coupled (normal modes) | undergraduate | [CM1/ch02](#cm1); [M0/ch05](#m0) | Idea | TODO(CM1/ch05); Idea |
| CM1/ch06 | Central forces, Kepler orbits, gravitation and scattering | undergraduate | [CM1/ch03](#cm1) (opt.); [CM1/ch04](#cm1); [M0/ch04](#m0) | Idea | TODO(CM1/ch06); Idea |
| CM1/ch07 | Non-inertial reference frames | undergraduate | [CM1/ch02](#cm1) | Idea | TODO(CM1/ch07); Idea |
| CM1/ch08 | Rigid-body motion in 3D: inertia tensor and Euler equations | undergraduate | [CM1/ch04](#cm1); [M1/ch02](#m1) | Idea | TODO(CM1/ch08); Idea |

### Book dependencies

Edited in [CM1-classical-mechanics-1/CM1-organization.md](CM1-classical-mechanics-1/CM1-organization.md). An editorial organization change file can replace the same list.

Finish first: [M0](#m0), [M1](#m1).
Required by: [CM2](#cm2), [CM3](#cm3), [F1](#f1).


<a id="cm2"></a>

## CM2 Classical Mechanics II

- Folder: [CM2-classical-mechanics-2/](CM2-classical-mechanics-2/)
- Entry level: Lagrangian/Hamiltonian mechanics. Target level: postdoc.
- Finish first: [CM1](#cm1), [M2](#m2)
- Editorial status: To Review
- Entry level: Lagrangian/Hamiltonian mechanics. Target level: postdoc (modern mathematics, geometric algebra).
- Finish first: [CM1](#cm1), [M2](#m2), [M3/ch02](#m3) only for CM2/ch05, and [EM/ch02](#em) only for CM2/ch07 (transitively also M1)
- Target level completed by: **CM2/ch10 Multisymplectic and covariant formulations** and **CM2/ch12 Celestial mechanics and the N-body problem** (both TODO); the postdoc chapters are parallel branches.
- Chapters: 12 planned, 1 present, 11 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| CM2/ch01 | Constraints, variational principles and Lagrangian mechanics | undergraduate | [CM1/ch05](#cm1); [CM1/ch08](#cm1); [M0/ch09](#m0); [M1/ch06](#m1) (opt.) | Idea | TODO(CM2/ch01); Idea |
| CM2/ch02 | (no section heading: TODO(CM2/ch02)) Energy as a contraction: Legendre transform, Noether, relativity; Geodesics, Killing fields, Noether and the inertia metric; Action and Hamiltonian mechanics *(graduate; also previews relativity (energy as a contraction) and Bohr-Sommerfeld quantisation)* | graduate | M1 Part intro `part:integration`; M1 Part intro `part:manifolds`; [M2/ch10](#m2); [M2/ch11](#m2) | To Review | present: [CM2-classical-mechanics-2/chapters/ch02-energy-noether-hamiltonian/](CM2-classical-mechanics-2/chapters/ch02-energy-noether-hamiltonian/); To Review |
| CM2/ch03 | Symplectic geometry, Poisson brackets and Hamiltonian flows | graduate | [CM2/ch02](#cm2); [M1/ch08](#m1) | Idea | TODO(CM2/ch03); Idea |
| CM2/ch04 | Canonical transformations and Hamilton-Jacobi theory | graduate | [CM2/ch03](#cm2) | Idea | TODO(CM2/ch04); Idea |
| CM2/ch05 | Integrable systems, action-angle variables, perturbation theory, KAM and chaos | graduate | [CM2/ch04](#cm2); [M3/ch02](#m3) | Idea | TODO(CM2/ch05); Idea |
| CM2/ch06 | Rigid bodies and rotors in geometric algebra | graduate | [CM1/ch08](#cm1); [M2/ch03](#m2) | Idea | TODO(CM2/ch06); Idea |
| CM2/ch07 | Spacetime algebra and relativistic mechanics | graduate | [CM2/ch06](#cm2); [EM/ch02](#em); [M2/ch03](#m2); [M2/ch04](#m2) | Idea | TODO(CM2/ch07); Idea |
| CM2/ch08 | Geometric mechanics: Lie groups, momentum maps and reduction | postdoc/research | [CM2/ch03](#cm2); [M2/ch15](#m2) | Idea | TODO(CM2/ch08); Idea |
| CM2/ch09 | Classical field theory: Lagrangian densities and Noether currents | graduate | [CM2/ch02](#cm2); [M2/ch09](#m2) | Idea | TODO(CM2/ch09); Idea |
| CM2/ch10 | Multisymplectic and covariant formulations | postdoc/research | [CM2/ch08](#cm2); [CM2/ch09](#cm2) | Idea | TODO(CM2/ch10); Idea |
| CM2/ch11 | Nonholonomic and constrained Hamiltonian systems (Dirac brackets) | graduate | [CM2/ch01](#cm2); [CM2/ch03](#cm2) | Idea | TODO(CM2/ch11); Idea |
| CM2/ch12 | Celestial mechanics and the N-body problem | postdoc/research | [CM1/ch06](#cm1); [CM2/ch05](#cm2) | Idea | TODO(CM2/ch12); Idea |

### Book dependencies

Edited in [CM2-classical-mechanics-2/CM2-organization.md](CM2-classical-mechanics-2/CM2-organization.md). An editorial organization change file can replace the same list.

Finish first: [CM1](#cm1), [M2](#m2).


### Sources

Edited in [CM2-classical-mechanics-2/CM2-organization.md](CM2-classical-mechanics-2/CM2-organization.md).

| ID | file | proposed chapter | status | reference |
| --- | --- | --- | --- | --- |
| Arnold | none | - | cited, no file | V. I. Arnold, *Mathematical Methods of Classical Mechanics*, Springer, 1989 (Chapter 7). |

<a id="cm3"></a>

## CM3 Elasticity

- Folder: [CM3-elasticity/](CM3-elasticity/)
- Entry level: zero. Target level: postdoc.
- Finish first: [CM1](#cm1), [M2](#m2)
- Editorial status: Idea
- Entry level: zero. Target level: postdoc.
- Finish first: [CM1](#cm1), [M2](#m2), and [CM2/ch01](#cm2) only for CM3/ch08 onward, [M3/ch06](#m3) only for CM3/ch07, [M3/ch07](#m3) and [M3/ch09](#m3) only for CM3/ch12, [M2/ch22](#m2) only for CM3/ch13, [TH/ch01](#th) only for CM3/ch11 (transitively also M1)
- Ownership: this document owns continuum kinematics, strain, the Cauchy stress tensor and the balance laws (CM3/ch02, CM3/ch03); fluid mechanics (F1) references them.
- Target level completed by: **CM3/ch13 Geometric elasticity: defects, incompatibility and Riemann-Cartan geometry** (TODO). CM3/ch14 is a parallel graduate branch.
- Chapters: 14 planned, 0 present, 14 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| CM3/ch01 | Stress, strain and Hooke's law in one dimension | basic | [CM1/ch02](#cm1) | Idea | TODO(CM3/ch01); Idea |
| CM3/ch02 | Kinematics of deformation: displacement and the strain tensor | undergraduate | [CM1/ch02](#cm1); [CM3/ch01](#cm3) (opt.); [M1/ch02](#m1) | Idea | TODO(CM3/ch02); Idea |
| CM3/ch03 | The Cauchy stress tensor and equilibrium | undergraduate | [CM3/ch02](#cm3); [M0/ch04](#m0) | Idea | TODO(CM3/ch03); Idea |
| CM3/ch04 | Linear isotropic elasticity: Navier-Cauchy equations | undergraduate | [CM3/ch01](#cm3); [CM3/ch03](#cm3) | Idea | TODO(CM3/ch04); Idea |
| CM3/ch05 | Classical problems: torsion, bending, plane elasticity | undergraduate | [CM3/ch04](#cm3) | Idea | TODO(CM3/ch05); Idea |
| CM3/ch06 | Beams, plates, shells and buckling | graduate | [CM3/ch05](#cm3); [M0/ch05](#m0) | Idea | TODO(CM3/ch06); Idea |
| CM3/ch07 | Elastic waves | graduate | [CM3/ch04](#cm3); [M0/ch08](#m0); [M3/ch06](#m3) | Idea | TODO(CM3/ch07); Idea |
| CM3/ch08 | Energy methods and variational principles | graduate | [CM2/ch01](#cm2); [CM3/ch04](#cm3); [M0/ch09](#m0) | Idea | TODO(CM3/ch08); Idea |
| CM3/ch09 | Anisotropic elasticity and composites | graduate | [CM3/ch04](#cm3) | Idea | TODO(CM3/ch09); Idea |
| CM3/ch10 | Finite (nonlinear) elasticity | graduate | [CM3/ch08](#cm3); [M2/ch10](#m2) | Idea | TODO(CM3/ch10); Idea |
| CM3/ch11 | Plasticity, viscoelasticity and thermoelasticity | graduate | [CM3/ch10](#cm3); [TH/ch01](#th) | Idea | TODO(CM3/ch11); Idea |
| CM3/ch12 | Finite element methods for solids | graduate | [CM3/ch08](#cm3); [M0/ch11](#m0); [M3/ch07](#m3); [M3/ch09](#m3) | Idea | TODO(CM3/ch12); Idea |
| CM3/ch13 | Geometric elasticity: defects, incompatibility and Riemann-Cartan geometry | postdoc/research | [CM3/ch10](#cm3); [M2/ch12](#m2); [M2/ch22](#m2) | Idea | TODO(CM3/ch13); Idea |
| CM3/ch14 | Fracture and contact mechanics | graduate | [CM3/ch08](#cm3); [CM3/ch11](#cm3) | Idea | TODO(CM3/ch14); Idea |

### Book dependencies

Edited in [CM3-elasticity/CM3-organization.md](CM3-elasticity/CM3-organization.md). An editorial organization change file can replace the same list.

Finish first: [CM1](#cm1), [M2](#m2).


<a id="em"></a>

## EM Electrodynamics and Special Relativity

- Folder: [EM-electrodynamics/](EM-electrodynamics/)
- Entry level: undergraduate. Target level: graduate.
- Editorial status: Idea
- Entry level: undergraduate. Target level: graduate.
- Finish first: [CM1/ch02](#cm1), and [M0/ch04](#m0), [M0/ch06](#m0), [M0/ch08](#m0), [M0/ch09](#m0), [M1/ch02](#m1), [M1/ch03](#m1) for the chapters that list them
- Ownership: this document owns special relativity and Minkowski geometry (EM/ch02, EM/ch03), moved here from GR/ch01 and GR/ch02, and classical electrodynamics. GR, QM, QFT, CM2/ch07 and F2 reference them. The differential-forms treatment of Maxwell's equations stays in [GR/ch03](#gr).
- Target level completed by: **EM/ch07 Radiation from moving charges and radiation reaction** (TODO).
- Chapters: 7 planned, 0 present, 7 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| EM/ch01 | Electrostatics, magnetostatics and Maxwell's equations | undergraduate | [CM1/ch02](#cm1); [M0/ch04](#m0) | Idea | TODO(EM/ch01); Idea |
| EM/ch02 | Special relativity | undergraduate | [CM1/ch02](#cm1); [M1/ch03](#m1) | Idea | TODO(EM/ch02); Idea |
| EM/ch03 | Minkowski spacetime and tensors on spacetime | undergraduate | [EM/ch02](#em); [M1/ch02](#m1) | Idea | TODO(EM/ch03); Idea |
| EM/ch04 | Electromagnetic waves and radiation | undergraduate | [EM/ch01](#em); [M0/ch06](#m0); [M0/ch08](#m0) | Idea | TODO(EM/ch04); Idea |
| EM/ch05 | Covariant electrodynamics and the field Lagrangian | graduate | [EM/ch03](#em); [EM/ch04](#em); [M0/ch09](#m0) | Idea | TODO(EM/ch05); Idea |
| EM/ch06 | Electromagnetism in matter: dielectrics, conductors and dispersion | graduate | [EM/ch04](#em) | Idea | TODO(EM/ch06); Idea |
| EM/ch07 | Radiation from moving charges and radiation reaction | graduate | [EM/ch05](#em) | Idea | TODO(EM/ch07); Idea |

### Book dependencies

Edited in [EM-electrodynamics/EM-organization.md](EM-electrodynamics/EM-organization.md). An editorial organization change file can replace the same list.

Finish first: nothing.


<a id="th"></a>

## TH Thermodynamics and Statistical Mechanics

- Folder: [TH-thermo-statmech/](TH-thermo-statmech/)
- Entry level: undergraduate. Target level: graduate.
- Finish first: [M0](#m0)
- Editorial status: Idea
- Entry level: undergraduate. Target level: graduate.
- Finish first: [M0](#m0) and [CM1/ch04](#cm1); chapter-specific: [M0/ch10](#m0) for TH/ch02, [QM/ch08](#qm) only for TH/ch03, [CM2/ch02](#cm2) only for TH/ch05, [M2/ch19](#m2) only for TH/ch06
- Ownership: this document owns thermodynamics, equilibrium statistical mechanics, kinetic theory and non-equilibrium statistical mechanics; F1, F2, CM3, GR and QFT reference them. The hydrodynamic limit of kinetic theory (Chapman-Enskog) is in [F2/ch10](#f2), so that TH does not depend on the fluids documents.
- Target level completed by: **TH/ch04** and **TH/ch06** (both TODO), which are parallel branches.
- Chapters: 6 planned, 0 present, 6 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| TH/ch01 | Thermodynamics: laws, potentials and phase equilibria | undergraduate | [CM1/ch04](#cm1); [M0/ch04](#m0) | Idea | TODO(TH/ch01); Idea |
| TH/ch02 | Statistical ensembles and the partition function | undergraduate | [M0/ch10](#m0); [TH/ch01](#th) | Idea | TODO(TH/ch02); Idea |
| TH/ch03 | Quantum statistics: Fermi and Bose gases and Bose-Einstein condensation | graduate | [QM/ch08](#qm); [TH/ch02](#th) | Idea | TODO(TH/ch03); Idea |
| TH/ch04 | Phase transitions and critical phenomena: mean field theory and the renormalisation group | graduate | [TH/ch02](#th) | Idea | TODO(TH/ch04); Idea |
| TH/ch05 | Kinetic theory: Liouville, BBGKY, the Boltzmann equation and the H-theorem | graduate | [CM2/ch02](#cm2); [TH/ch02](#th) | Idea | TODO(TH/ch05); Idea |
| TH/ch06 | Non-equilibrium statistical mechanics: Langevin, Fokker-Planck, linear response and fluctuation-dissipation | graduate | [M2/ch19](#m2); [TH/ch05](#th) | Idea | TODO(TH/ch06); Idea |

### Book dependencies

Edited in [TH-thermo-statmech/TH-organization.md](TH-thermo-statmech/TH-organization.md). An editorial organization change file can replace the same list.

Finish first: [M0](#m0).


<a id="f1"></a>

## F1 Fluid Mechanics I: Classical Flows

- Folder: [F1-fluids-classical/](F1-fluids-classical/)
- Entry level: undergraduate continuum mechanics. Target level: graduate.
- Finish first: [CM1](#cm1)
- Editorial status: To Review
- Entry level: undergraduate continuum mechanics (the Navier-Stokes equations are derived in F1/ch03). Target level: graduate.
- Finish first: [CM1](#cm1), and [CM3/ch02](#cm3) to [CM3/ch03](#cm3) (continuum kinematics and stress), [TH/ch01](#th) only for F1/ch02, and [M3/ch02](#m3), [M3/ch03](#m3), [M3/ch06](#m3), [M3/ch08](#m3) for F1/ch09, F1/ch08, F1/ch11, F1/ch12 respectively (transitively also M1, M2)
- Target level completed by: **F1/ch12 Waves in fluids** and **F1/ch13 Rotating and stratified flows** (both TODO).
- Chapters: 13 planned, 1 present, 12 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| F1/ch01 | Continuum hypothesis and kinematics of flow | undergraduate | [CM1/ch02](#cm1); [CM3/ch02](#cm3); [M0/ch04](#m0) | Idea | TODO(F1/ch01); Idea |
| F1/ch02 | Conservation laws: mass, momentum, energy | undergraduate | [CM3/ch03](#cm3); [F1/ch01](#f1); [M0/ch04](#m0); [TH/ch01](#th) | Idea | TODO(F1/ch02); Idea |
| F1/ch03 | The Navier-Stokes equations and constitutive relations | undergraduate | [F1/ch02](#f1) | Idea | TODO(F1/ch03); Idea |
| F1/ch04 | Ideal flow: Euler equations and Bernoulli | undergraduate | [F1/ch03](#f1) | Idea | TODO(F1/ch04); Idea |
| F1/ch05 | (no section heading: TODO(F1/ch05)) Fluids: circulation needs a metric *(graduate: Kelvin's circulation theorem stated with differential forms and the Lie derivative)* | graduate | [M1/ch09](#m1); M1 Part intro `part:integration`; M1 Part intro `part:manifolds`; [M2/ch11](#m2) | To Review | present: [F1-fluids-classical/chapters/ch05-circulation/](F1-fluids-classical/chapters/ch05-circulation/); To Review |
| F1/ch06 | Potential flow and complex potentials | undergraduate | [F1/ch04](#f1); [M0/ch12](#m0); [M2/ch17](#m2) (opt.) | Idea | TODO(F1/ch06); Idea |
| F1/ch07 | Viscous flows: exact solutions, Stokes flow, lubrication | graduate | [F1/ch03](#f1) | Idea | TODO(F1/ch07); Idea |
| F1/ch08 | Boundary layers | graduate | [F1/ch07](#f1); [M3/ch03](#m3) | Idea | TODO(F1/ch08); Idea |
| F1/ch09 | Hydrodynamic stability | graduate | [F1/ch08](#f1); [M3/ch02](#m3) | Idea | TODO(F1/ch09); Idea |
| F1/ch10 | Introduction to turbulence | graduate | [F1/ch09](#f1) | Idea | TODO(F1/ch10); Idea |
| F1/ch11 | Compressible flow and gas dynamics | graduate | [F1/ch04](#f1); [M3/ch06](#m3) | Idea | TODO(F1/ch11); Idea |
| F1/ch12 | Waves in fluids | graduate | [F1/ch06](#f1); [M3/ch08](#m3) | Idea | TODO(F1/ch12); Idea |
| F1/ch13 | Rotating and stratified flows | graduate | [F1/ch04](#f1); [F1/ch12](#f1) | Idea | TODO(F1/ch13); Idea |

### Book dependencies

Edited in [F1-fluids-classical/F1-organization.md](F1-fluids-classical/F1-organization.md). An editorial organization change file can replace the same list.

Finish first: [CM1](#cm1).
Required by: [F2](#f2).


### Sources

Edited in [F1-fluids-classical/F1-organization.md](F1-fluids-classical/F1-organization.md).

| ID | file | proposed chapter | status | reference |
| --- | --- | --- | --- | --- |
| ArnoldKhesin | none | - | cited, no file | V. I. Arnold and B. A. Khesin, *Topological Methods in Hydrodynamics*, Springer, 1998. |

<a id="f2"></a>

## F2 Fluid Mechanics II: Complex and Extreme Flows

- Folder: [F2-fluids-complex-extreme/](F2-fluids-complex-extreme/)
- Entry level: graduate. Target level: postdoc.
- Finish first: [F1](#f1)
- Editorial status: Idea
- Entry level: graduate. Target level: postdoc.
- Finish first: [F1](#f1); chapter-specific: [CM3/ch11](#cm3) (optional) for F2/ch02, [TH/ch01](#th) for F2/ch03, [EM/ch05](#em) and [TH/ch05](#th) for F2/ch05, [EM/ch03](#em) and [GR/ch05](#gr) for F2/ch06, [QM/ch08](#qm), [TH/ch03](#th) and [M3/ch08](#m3) for F2/ch07, [M3/ch09](#m3) for F2/ch08, [TH/ch05](#th) for F2/ch10 (transitively also CM1, CM2, M1, M2)
- F2 has no single completing chapter: F2/ch01 to F2/ch10 are parallel branches, each reaching its level once its listed prerequisites are met.
- Chapters: 10 planned, 0 present, 10 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| F2/ch01 | Turbulence: advanced theory and extensions | postdoc/research | [F1/ch10](#f1); [M0/ch10](#m0); [M2/ch19](#m2) | Idea | TODO(F2/ch01); Idea |
| F2/ch02 | Non-Newtonian and complex fluids | graduate | [CM3/ch11](#cm3) (opt.); [F1/ch07](#f1) | Idea | TODO(F2/ch02); Idea |
| F2/ch03 | Temperature-dependent flows: convection and variable properties | graduate | [F1/ch09](#f1); [TH/ch01](#th) | Idea | TODO(F2/ch03); Idea |
| F2/ch04 | Multifluid flows: mixing and unmixing | postdoc/research | [F2/ch03](#f2) | Idea | TODO(F2/ch04); Idea |
| F2/ch05 | Plasma: magnetohydrodynamics and kinetic theory | postdoc/research | [EM/ch05](#em); [F1/ch11](#f1); [GR/ch03](#gr) (opt.); [TH/ch05](#th) | Idea | TODO(F2/ch05); Idea |
| F2/ch06 | Relativistic fluids: special-relativistic flows and fluids in curved spacetime | postdoc/research | [EM/ch03](#em); [F1/ch11](#f1); [GR/ch05](#gr) | Idea | TODO(F2/ch06); Idea |
| F2/ch07 | Quantum fluids: superfluids and Bose-Einstein condensates | postdoc/research | [F1/ch04](#f1); [M3/ch08](#m3); [QM/ch08](#qm); [TH/ch03](#th) | Idea | TODO(F2/ch07); Idea |
| F2/ch08 | Numerical methods for fluids | postdoc/research | [F1/ch03](#f1); [M0/ch11](#m0); [M3/ch09](#m3) | Idea | TODO(F2/ch08); Idea |
| F2/ch09 | Interfaces, capillarity and wetting | graduate | [F1/ch07](#f1); [F1/ch09](#f1) | Idea | TODO(F2/ch09); Idea |
| F2/ch10 | Kinetic theory and the hydrodynamic limit: Chapman-Enskog and transport coefficients | postdoc/research | [F1/ch03](#f1); [TH/ch05](#th) | Idea | TODO(F2/ch10); Idea |

### Book dependencies

Edited in [F2-fluids-complex-extreme/F2-organization.md](F2-fluids-complex-extreme/F2-organization.md). An editorial organization change file can replace the same list.

Finish first: [F1](#f1).


<a id="qm"></a>

## QM Quantum Mechanics

- Folder: [QM-quantum-mechanics/](QM-quantum-mechanics/)
- Entry level: zero physics. Target level: full quantum mechanics.
- Finish first: [M0](#m0)
- Editorial status: Idea
- Entry level: zero physics (mathematics from M0 assumed). Target level: full quantum mechanics.
- Finish first: [M0](#m0) and [CM1/ch02](#cm1); chapter-specific: [M3/ch03](#m3) for QM/ch09, [M2/ch15](#m2) for QM/ch12, [M0/ch10](#m0) for QM/ch13, [CM2/ch01](#cm2) for QM/ch14, [EM/ch02](#em) for QM/ch15 (transitively also M2)
- Late link: QM/ch15 uses special relativity from [EM/ch02](#em).
- Target level completed by: **QM/ch15 Relativistic quantum mechanics: Klein-Gordon and Dirac** (TODO).
- Chapters: 15 planned, 0 present, 15 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| QM/ch01 | Experimental origins of quantum theory | basic | [CM1/ch02](#cm1) | Idea | TODO(QM/ch01); Idea |
| QM/ch02 | Wave mechanics and the Schrodinger equation | undergraduate | [M0/ch08](#m0); [QM/ch01](#qm) | Idea | TODO(QM/ch02); Idea |
| QM/ch03 | One-dimensional problems | undergraduate | [QM/ch02](#qm) | Idea | TODO(QM/ch03); Idea |
| QM/ch04 | Hilbert spaces, Dirac notation and the postulates | undergraduate | [M0/ch03](#m0); [M0/ch06](#m0); [M2/ch18](#m2) (opt.); [QM/ch03](#qm) | Idea | TODO(QM/ch04); Idea |
| QM/ch05 | The harmonic oscillator | undergraduate | [QM/ch04](#qm) | Idea | TODO(QM/ch05); Idea |
| QM/ch06 | Angular momentum and spin | undergraduate | [M0/ch03](#m0); [QM/ch04](#qm) | Idea | TODO(QM/ch06); Idea |
| QM/ch07 | The hydrogen atom | undergraduate | [M0/ch07](#m0); [QM/ch06](#qm) | Idea | TODO(QM/ch07); Idea |
| QM/ch08 | Identical particles, atoms and molecules | graduate | [QM/ch06](#qm) | Idea | TODO(QM/ch08); Idea |
| QM/ch09 | Approximation methods: perturbation theory, variational, WKB | graduate | [M3/ch03](#m3); [QM/ch05](#qm) | Idea | TODO(QM/ch09); Idea |
| QM/ch10 | Time-dependent perturbation theory and transitions | graduate | [QM/ch09](#qm) | Idea | TODO(QM/ch10); Idea |
| QM/ch11 | Scattering theory | graduate | [QM/ch09](#qm) | Idea | TODO(QM/ch11); Idea |
| QM/ch12 | Symmetries in quantum mechanics | graduate | [M2/ch15](#m2); [QM/ch06](#qm) | Idea | TODO(QM/ch12); Idea |
| QM/ch13 | Density matrices, entanglement, measurement and open quantum systems | graduate | [M0/ch10](#m0); [QM/ch04](#qm) | Idea | TODO(QM/ch13); Idea |
| QM/ch14 | Path integrals | graduate | [CM2/ch01](#cm2); [QM/ch05](#qm) | Idea | TODO(QM/ch14); Idea |
| QM/ch15 | Relativistic quantum mechanics: Klein-Gordon and Dirac | graduate | [EM/ch02](#em); [QM/ch12](#qm) | Idea | TODO(QM/ch15); Idea |

### Book dependencies

Edited in [QM-quantum-mechanics/QM-organization.md](QM-quantum-mechanics/QM-organization.md). An editorial organization change file can replace the same list.

Finish first: [M0](#m0).
Required by: [QFT](#qft).


<a id="qft"></a>

## QFT Quantum Field Theory

- Folder: [QFT-quantum-field-theory/](QFT-quantum-field-theory/)
- Entry level: quantum mechanics. Target level: postdoc.
- Finish first: [M2](#m2), [QM](#qm)
- Editorial status: Idea
- Entry level: quantum mechanics. Target level: postdoc.
- Finish first: [QM](#qm), [M2](#m2), [EM/ch03](#em) for QFT/ch01; chapter-specific: [GR/ch07](#gr) and [GR/ch13](#gr) for QFT/ch12, [GR/ch07](#gr) for QFT/ch18, [TH/ch02](#th) for QFT/ch17 (transitively also CM1, CM2, M1)
- Ownership: this document owns the derivation of Hawking radiation and the Unruh effect (QFT/ch12); GR/ch13 covers classical black-hole mechanics and does not depend on QFT.
- The graduate target is reached at **QFT/ch10 The Standard Model**; QFT/ch11 to QFT/ch18 are parallel postdoc/research branches (all TODO).
- Chapters: 18 planned, 0 present, 18 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| QFT/ch01 | Lorentz group and its representations | graduate | [EM/ch03](#em); [M2/ch15](#m2) | Idea | TODO(QFT/ch01); Idea |
| QFT/ch02 | Classical field theory | graduate | [CM2/ch09](#cm2) | Idea | TODO(QFT/ch02); Idea |
| QFT/ch03 | Canonical quantisation of free fields | graduate | [QFT/ch02](#qft); [QM/ch08](#qm); [QM/ch15](#qm) | Idea | TODO(QFT/ch03); Idea |
| QFT/ch04 | Interacting fields, the S-matrix and Feynman diagrams | graduate | [QFT/ch03](#qft); [QM/ch10](#qm); [QM/ch11](#qm) | Idea | TODO(QFT/ch04); Idea |
| QFT/ch05 | Quantum electrodynamics | graduate | [QFT/ch04](#qft) | Idea | TODO(QFT/ch05); Idea |
| QFT/ch06 | Path-integral quantisation | graduate | [QFT/ch04](#qft); [QM/ch14](#qm) | Idea | TODO(QFT/ch06); Idea |
| QFT/ch07 | Renormalisation, the renormalisation group and effective field theory | graduate | [QFT/ch05](#qft); [QFT/ch06](#qft) | Idea | TODO(QFT/ch07); Idea |
| QFT/ch08 | Non-abelian gauge theories | graduate | [M2/ch15](#m2); [M2/ch16](#m2) (opt.); [QFT/ch07](#qft) | Idea | TODO(QFT/ch08); Idea |
| QFT/ch09 | Spontaneous symmetry breaking and the Higgs mechanism | graduate | [QFT/ch08](#qft) | Idea | TODO(QFT/ch09); Idea |
| QFT/ch10 | The Standard Model | graduate | [QFT/ch09](#qft) | Idea | TODO(QFT/ch10); Idea |
| QFT/ch11 | Anomalies, instantons and topology | postdoc/research | [M2/ch22](#m2); [QFT/ch08](#qft) | Idea | TODO(QFT/ch11); Idea |
| QFT/ch12 | Quantum field theory in curved spacetime: the Unruh effect and Hawking radiation | postdoc/research | [GR/ch07](#gr); [GR/ch13](#gr); [QFT/ch06](#qft) | Idea | TODO(QFT/ch12); Idea |
| QFT/ch13 | Conformal field theory and the bootstrap | postdoc/research | [QFT/ch07](#qft) | Idea | TODO(QFT/ch13); Idea |
| QFT/ch14 | Lattice gauge theory and non-perturbative methods | postdoc/research | [QFT/ch06](#qft); [QFT/ch08](#qft) | Idea | TODO(QFT/ch14); Idea |
| QFT/ch15 | Supersymmetry | postdoc/research | [M2/ch16](#m2); [QFT/ch10](#qft) | Idea | TODO(QFT/ch15); Idea |
| QFT/ch16 | Scattering amplitudes and on-shell methods | postdoc/research | [QFT/ch05](#qft); [QFT/ch08](#qft) | Idea | TODO(QFT/ch16); Idea |
| QFT/ch17 | Finite-temperature and non-equilibrium quantum field theory | postdoc/research | [QFT/ch06](#qft); [TH/ch02](#th) | Idea | TODO(QFT/ch17); Idea |
| QFT/ch18 | Large N, holography and AdS/CFT | postdoc/research | [GR/ch07](#gr); [QFT/ch13](#qft) | Idea | TODO(QFT/ch18); Idea |

### Book dependencies

Edited in [QFT-quantum-field-theory/QFT-organization.md](QFT-quantum-field-theory/QFT-organization.md). An editorial organization change file can replace the same list.

Finish first: [M2](#m2), [QM](#qm).


<a id="gr"></a>

## GR General Relativity

- Folder: [GR-general-relativity/](GR-general-relativity/)
- Entry level: undergraduate, after special relativity. Target level: postdoc.
- Finish first: [M2](#m2)
- Editorial status: To Review
- Entry level: undergraduate, after special relativity ([EM/ch02](#em), [EM/ch03](#em)). Target level: postdoc.
- Finish first: [EM/ch03](#em), [M2](#m2), [CM2/ch02](#cm2) for GR/ch04, [CM2/ch03](#cm2) and [M3/ch06](#m3) for GR/ch10, [TH/ch01](#th) for GR/ch13 and GR/ch14 (transitively also CM1, M1)
- GR does not depend on QFT: the derivation of Hawking radiation is owned by [QFT/ch12](#qft), which depends on GR/ch07 and GR/ch13.
- Ownership: special relativity and Minkowski geometry moved to [EM/ch02](#em) and [EM/ch03](#em); GR/ch01 and GR/ch02 are retired numbers.
- The graduate target is reached at **GR/ch09 Cosmology**; GR/ch10 to GR/ch13 and GR/ch15 to GR/ch17 are parallel postdoc/research branches (all TODO or present as listed).
- Chapters: 17 planned, 2 present, 13 absent, 2 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |
| GR/ch01 | *(moved to EM/ch02: special relativity)* | — | — | — | moved; — |
| GR/ch02 | *(moved to EM/ch03: Minkowski spacetime and tensors on spacetime)* | — | — | — | moved; — |
| GR/ch03 | (no section heading: TODO(GR/ch03)) Electromagnetism: which fields are 1-forms, 2-forms, 3-forms? *(graduate: Maxwell's equations as forms; includes the Aharonov-Bohm effect (quantum))* | graduate | M1 Part intro `part:integration`; M1 Part intro `part:manifolds`; [M2/ch09](#m2); [M2/ch11](#m2) | To Review | present: [GR-general-relativity/chapters/ch03-electromagnetism-forms/](GR-general-relativity/chapters/ch03-electromagnetism-forms/); To Review |
| GR/ch04 | Bridge to general relativity | graduate | [CM1/ch03](#cm1); [CM2/ch02](#cm2); [M1/ch03](#m1); [M1/ch05](#m1); [M1/ch07](#m1); [M1/ch08](#m1); M1 Part intro `part:algebra`; [M2/ch10](#m2); [M2/ch11](#m2); [M2/ch12](#m2); [M2/ch13](#m2); M2 Part intro `part:geometry` | To Review | present: [GR-general-relativity/chapters/ch04-bridge-to-gr/](GR-general-relativity/chapters/ch04-bridge-to-gr/); To Review |
| GR/ch05 | The Einstein field equations | graduate | [EM/ch03](#em); [GR/ch04](#gr); [M2/ch12](#m2) | Idea | TODO(GR/ch05); Idea |
| GR/ch06 | The Schwarzschild solution and classical tests | graduate | [GR/ch05](#gr) | Idea | TODO(GR/ch06); Idea |
| GR/ch07 | Black holes: horizons, charged and rotating solutions | graduate | [GR/ch06](#gr) | Idea | TODO(GR/ch07); Idea |
| GR/ch08 | Gravitational waves | graduate | [GR/ch05](#gr) | Idea | TODO(GR/ch08); Idea |
| GR/ch09 | Cosmology | graduate | [GR/ch05](#gr) | Idea | TODO(GR/ch09); Idea |
| GR/ch10 | Hamiltonian (ADM) formulation and numerical relativity | postdoc/research | [CM2/ch03](#cm2); [GR/ch05](#gr); [M3/ch06](#m3) | Idea | TODO(GR/ch10); Idea |
| GR/ch11 | Tetrads, spinors and gauge-theory gravity in geometric algebra | postdoc/research | [GR/ch05](#gr); [M2/ch16](#m2) | Idea | TODO(GR/ch11); Idea |
| GR/ch12 | Causal structure and singularity theorems | postdoc/research | [GR/ch07](#gr); [M2/ch22](#m2) | Idea | TODO(GR/ch12); Idea |
| GR/ch13 | Black hole mechanics and thermodynamics (classical) | postdoc/research | [GR/ch07](#gr); [TH/ch01](#th) | Idea | TODO(GR/ch13); Idea |
| GR/ch14 | Relativistic stars and accretion | graduate | [GR/ch06](#gr); [TH/ch01](#th) | Idea | TODO(GR/ch14); Idea |
| GR/ch15 | Black hole perturbations and quasinormal modes | postdoc/research | [GR/ch07](#gr); [GR/ch08](#gr); [M3/ch03](#m3) | Idea | TODO(GR/ch15); Idea |
| GR/ch16 | Post-Newtonian theory and gravitational-wave source modelling | postdoc/research | [GR/ch08](#gr) | Idea | TODO(GR/ch16); Idea |
| GR/ch17 | Cosmological perturbation theory and inflation | postdoc/research | [GR/ch09](#gr) | Idea | TODO(GR/ch17); Idea |

### Book dependencies

Edited in [GR-general-relativity/GR-organization.md](GR-general-relativity/GR-organization.md). An editorial organization change file can replace the same list.

Finish first: [M2](#m2).


### Sources

Edited in [GR-general-relativity/GR-organization.md](GR-general-relativity/GR-organization.md).

| ID | file | proposed chapter | status | reference |
| --- | --- | --- | --- | --- |
| MTW | none | - | cited, no file | C. W. Misner, K. S. Thorne, J. A. Wheeler, *Gravitation*, Freeman, 1973 (one-forms as ``stacks of sheets'', Chapters 2-4). |
| Burke | none | - | cited, no file | W. L. Burke, *Applied Differential Geometry*, Cambridge University Press, 1985 (twisted forms, physics). |
| HehlObukhov | none | - | cited, no file | F. W. Hehl and Yu. N. Obukhov, *Foundations of Classical Electrodynamics*, Birkh"auser, 2003. |
| AharonovBohm | none | - | cited, no file | Y. Aharonov and D. Bohm, ``Significance of electromagnetic potentials in the quantum theory'', *Phys. Rev.* 115 (1959), 485-491. |
| Carroll | none | - | cited, no file | S. Carroll, *Spacetime and Geometry: An Introduction to General Relativity*, Addison-Wesley, 2004. |

<a id="glossary"></a>

## GLOSSARY Global glossary, identities and bibliography

- Entry level: reference. Target level: reference.
- Editorial status: To Review
- Not a levelled course: it is consulted alongside every path above, not read as one. It owns all symbols (Part A), terms (Part B), identities with proofs (Part C) and the single bibliography. Folder: [GLOSSARY/](GLOSSARY/).
- Entries currently cover M1 and M2 topics only. Missing blocks: `TODO(GLOSSARY/M0)`, `TODO(GLOSSARY/M3)`, `TODO(GLOSSARY/CM1)`, `TODO(GLOSSARY/CM2)`, `TODO(GLOSSARY/CM3)`, `TODO(GLOSSARY/EM)`, `TODO(GLOSSARY/TH)`, `TODO(GLOSSARY/F1)`, `TODO(GLOSSARY/F2)`, `TODO(GLOSSARY/QM)`, `TODO(GLOSSARY/QFT)`, `TODO(GLOSSARY/GR)`.
- Chapters: 0 planned, 0 present, 0 absent, 0 retired.

| chapter | title | level reached | prerequisites | editorial status | status |
| --- | --- | --- | --- | --- | --- |

### Book dependencies

Edited in [GLOSSARY/GLOSSARY-organization.md](GLOSSARY/GLOSSARY-organization.md). An editorial organization change file can replace the same list.

Finish first: nothing.


### Sources

Edited in [GLOSSARY/GLOSSARY-organization.md](GLOSSARY/GLOSSARY-organization.md).

| ID | file | proposed chapter | status | reference |
| --- | --- | --- | --- | --- |
| Spivak | none | - | cited, no file | M. Spivak, *Calculus on Manifolds*, Benjamin, 1965. |
| Lee | none | - | cited, no file | J. M. Lee, *Introduction to Smooth Manifolds*, 2nd ed., Springer GTM 218, 2013 (Chapters 11, 14, 16); and *Introduction to Riemannian Manifolds*, 2nd ed., Springer, 2018. |
| BottTu | none | - | cited, no file | R. Bott and L. W. Tu, *Differential Forms in Algebraic Topology*, Springer GTM 82, 1982. |
| Frankel | none | - | cited, no file | T. Frankel, *The Geometry of Physics*, Cambridge University Press. |
| Caratheodory | none | - | cited, no file | C. Carath'eodory, ``Untersuchungen "uber die Grundlagen der Thermodynamik'', *Math. Ann.* 67 (1909), 355-386. |
| Carroll | none | - | cited, no file | S. Carroll, *Spacetime and Geometry: An Introduction to General Relativity*, Addison-Wesley, 2004. |
| DFM | none | - | cited, no file | L. Dorst, D. Fontijne and S. Mann, *Geometric Algebra for Computer Science*, Morgan Kaufmann, 2007. |
| Lo | none | - | cited, no file | P. Lounesto, *Clifford Algebras and Spinors*, 2nd ed., Cambridge University Press, 2001. |
| Gr | none | - | cited, no file | W. Greub, *Multilinear Algebra*, 2nd ed., Springer, 1978. |
