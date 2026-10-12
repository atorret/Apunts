"""Archived layout used by the finished migration in this folder.

Live book folders and build order are in tools/books.py, read from
library.sqlite. Titles of TODO chapters here are syllabus entries only; no
chapter body is ever generated from them.
"""

OLD = "forms-tensors-ga"

# code, folder, title, entry level, target level, jobname
DOCS = [
    ("M1", "M1-math-foundations", "Mathematics I: Foundations", "basics", "undergraduate"),
    ("M2", "M2-math-advanced", "Mathematics II: Advanced", "undergraduate", "graduate (tensors, geometric algebra, differential geometry, groups)"),
    ("M3", "M3-math-differential-equations", "Mathematics III: Differential Equations", "undergraduate", "postdoc/research"),
    ("CM1", "CM1-classical-mechanics-1", "Classical Mechanics I", "basic Newtonian mechanics", "3D mechanics"),
    ("CM2", "CM2-classical-mechanics-2", "Classical Mechanics II", "Lagrangian/Hamiltonian mechanics", "postdoc (modern mathematics, geometric algebra)"),
    ("CM3", "CM3-elasticity", "Elasticity", "zero", "postdoc"),
    ("F1", "F1-fluids-classical", "Fluid Mechanics I: Classical Flows", "Navier-Stokes", "graduate"),
    ("F2", "F2-fluids-complex-extreme", "Fluid Mechanics II: Complex and Extreme Flows", "graduate", "postdoc"),
    ("QM", "QM-quantum-mechanics", "Quantum Mechanics", "zero", "full quantum mechanics"),
    ("QFT", "QFT-quantum-field-theory", "Quantum Field Theory", "quantum mechanics", "postdoc"),
    ("GR", "GR-general-relativity", "General Relativity", "zero", "postdoc"),
]
CONTENT_DOCS = [d[0] for d in DOCS]
GLOSSARY = ("GLOSSARY", "GLOSSARY", "Global Glossary, Identities and Bibliography")
UNSORTED = ("Unsorted", "unsorted", "Unsorted material")

FOLDER = {d[0]: d[1] for d in DOCS}
FOLDER["GLOSSARY"] = "GLOSSARY"
FOLDER["Unsorted"] = "unsorted"
TITLE = {d[0]: d[2] for d in DOCS}
TITLE["GLOSSARY"] = GLOSSARY[2]
TITLE["Unsorted"] = UNSORTED[2]
MAINFILE = {code: "main.tex" for code in FOLDER}
MAINFILE["Unsorted"] = "UNSORTED.tex"
JOB = {code: code for code in FOLDER}
JOB["Unsorted"] = "UNSORTED"

# Reading-order dependencies between documents (A must come before B).
DOC_EDGES = [
    ("M1", "M2"), ("M1", "M3"), ("M1", "CM1"), ("CM1", "CM2"), ("M2", "CM2"), ("CM1", "CM3"), ("M2", "CM3"),
    ("CM1", "F1"), ("F1", "F2"), ("CM3", "F2"), ("M1", "QM"), ("CM2", "QM"), ("QM", "QFT"),
    ("M2", "QFT"), ("M2", "GR"), ("CM2", "GR"), ("GR", "F2"), ("QM", "F2"), ("GR", "QFT"),
]

# Build order: a topological order of DOC_EDGES, then GLOSSARY and the unsorted holder.
BUILD_ORDER = ["M1", "M2", "M3", "CM1", "CM2", "CM3", "F1", "GR", "QM", "F2", "QFT", "GLOSSARY", "Unsorted"]


def ancestors(doc):
    """Documents that must be read before `doc` (transitive)."""
    seen, stack = set(), [doc]
    while stack:
        cur = stack.pop()
        for a, b in DOC_EDGES:
            if b == cur and a not in seen:
                seen.add(a)
                stack.append(a)
    return seen


# ---------------------------------------------------------------------------
# Move rules: (old path relative to OLD, new path relative to repo root).
# A rule whose old path ends with "/" moves a whole folder (recursively).
# Rules are applied in order; the first match wins.
# ---------------------------------------------------------------------------
P = "parts/"
M1, M2, CM1, CM2, F1, GR = (FOLDER[c] for c in ("M1", "M2", "CM1", "CM2", "F1", "GR"))

CHAPTER_DIRS = [
    # M1
    (P + "01-algebra/01-vectors-covectors/", "M1", "ch06-vectors-covectors"),
    (P + "01-algebra/02-tensors/", "M1", "ch07-tensors"),
    (P + "01-algebra/03-metric/", "M1", "ch08-metric"),
    (P + "01-algebra/04-exterior-algebra/", "M1", "ch09-exterior-algebra"),
    (P + "02-manifolds-and-forms/01-differentiable-manifolds/", "M1", "ch10-differentiable-manifolds"),
    (P + "02-manifolds-and-forms/02-tangent-cotangent/", "M1", "ch11-tangent-cotangent"),
    (P + "02-manifolds-and-forms/03-tensor-fields-forms/", "M1", "ch12-tensor-fields-forms"),
    (P + "03-integration/01-integration-1-forms/", "M1", "ch13-integration-1-forms"),
    (P + "03-integration/02-integration-k-forms/", "M1", "ch14-integration-k-forms"),
    (P + "03-integration/03-stokes/", "M1", "ch15-stokes"),
    (P + "03-integration/04-gauss/", "M1", "ch16-gauss"),
    # M2
    (P + "01-algebra/05-clifford-algebra/", "M2", "ch01-clifford-algebra"),
    (P + "01-algebra/06-multivector-operations/", "M2", "ch02-multivector-operations"),
    (P + "01-algebra/07-rotors/", "M2", "ch03-rotors"),
    (P + "01-algebra/08-duality/", "M2", "ch04-duality"),
    (P + "01-algebra/09-synthesis-1/", "M2", "ch05-synthesis-1"),
    (P + "02-manifolds-and-forms/04-lie-derivative/", "M2", "ch07-lie-derivative"),
    (P + "02-manifolds-and-forms/05-ga-calculus/", "M2", "ch08-ga-calculus"),
    (P + "02-manifolds-and-forms/06-synthesis-2/", "M2", "ch09-synthesis-2"),
    (P + "04-connections-curvature/01-connections/", "M2", "ch10-connections"),
    (P + "04-connections-curvature/02-levi-civita/", "M2", "ch11-levi-civita"),
    (P + "04-connections-curvature/03-riemann-curvature/", "M2", "ch12-riemann-curvature"),
    (P + "04-connections-curvature/04-geodesic-deviation/", "M2", "ch13-geodesic-deviation"),
    (P + "04-connections-curvature/05-synthesis-3/", "M2", "ch14-synthesis-3"),
    (P + "06-complex-analysis/01-residue-theorem/", "M2", "ch17-residue-theorem"),
    (P + "07-perspective/01-current-state/", "M2", "ch20-current-state"),
    (P + "07-perspective/02-master-summary/", "M2", "ch21-master-summary"),
    # GR
    (P + "05-physics/02-bridge-to-gr/", "GR", "ch04-bridge-to-gr"),
]

PHYS = P + "05-physics/01-intrinsic-vs-metric/"
FILE_RULES = [
    # Gauss: classical corollaries need the Hodge star and the Synthesis II dictionary (M2)
    (P + "03-integration/04-gauss/04-classical-corollaries.tex", f"{M2}/chapters/ch09-synthesis-2/04-classical-corollaries.tex"),
    # part hubs
    (P + "01-algebra/00-part.tex", f"{M1}/chapters/00-part-algebra.tex"),
    (P + "02-manifolds-and-forms/00-part.tex", f"{M1}/chapters/00-part-manifolds.tex"),
    (P + "03-integration/00-part.tex", f"{M1}/chapters/00-part-integration.tex"),
    (P + "04-connections-curvature/00-part.tex", f"{M2}/chapters/00-part-geometry.tex"),
    (P + "06-complex-analysis/00-part.tex", f"{M2}/chapters/00-part-complex.tex"),
    (P + "07-perspective/00-part.tex", f"{M2}/chapters/00-part-perspective.tex"),
    (P + "05-physics/00-part.tex", f"{CM1}/chapters/00-part-physics.tex"),
    # physics section, split by owner
    (PHYS + "00-section.tex", f"{CM1}/chapters/ch03-intrinsic-vs-metric/00-section.tex"),
    (PHYS + "01-work-and-energy.tex", f"{CM1}/chapters/ch03-intrinsic-vs-metric/01-work-and-energy.tex"),
    (PHYS + "08-pseudovectors.tex", f"{CM1}/chapters/ch03-intrinsic-vs-metric/08-pseudovectors.tex"),
    (PHYS + "09-sources-of-confusion.tex", f"{CM1}/chapters/ch03-intrinsic-vs-metric/09-sources-of-confusion.tex"),
    (PHYS + "10-dictionary.tex", f"{CM1}/chapters/ch03-intrinsic-vs-metric/10-dictionary.tex"),
    (PHYS + "02-energy-as-contraction.tex", f"{CM2}/chapters/ch02-energy-noether-hamiltonian/02-energy-as-contraction.tex"),
    (PHYS + "03-noether-synthesis.tex", f"{CM2}/chapters/ch02-energy-noether-hamiltonian/03-noether-synthesis.tex"),
    (PHYS + "04-hamiltonian-mechanics.tex", f"{CM2}/chapters/ch02-energy-noether-hamiltonian/04-hamiltonian-mechanics.tex"),
    (PHYS + "07-fluids.tex", f"{F1}/chapters/ch05-circulation/07-fluids.tex"),
    (PHYS + "06-electromagnetism.tex", f"{GR}/chapters/ch03-electromagnetism-forms/06-electromagnetism.tex"),
    (PHYS + "05-thermodynamics.tex", "unsorted/thermodynamics/05-thermodynamics.tex"),
    # figures follow the file that uses them
    ("figures/part1/tikz-sheets.tex", f"{M1}/figures/tikz-sheets.tex"),
    ("figures/part1/tikz-universal-property.tex", f"{M1}/figures/tikz-universal-property.tex"),
    ("figures/part1/tikz-wedge.tex", f"{M1}/figures/tikz-wedge.tex"),
    ("figures/part3/tikz-annulus.tex", f"{M1}/figures/tikz-annulus.tex"),
    ("figures/part1/tikz-two-reflections.tex", f"{M2}/figures/tikz-two-reflections.tex"),
    ("figures/part6/tikz-residue.tex", f"{M2}/figures/tikz-residue.tex"),
    ("figures/part7/tikz-map.tex", f"{M2}/figures/tikz-map.tex"),
    ("figures/part5/tikz-cycle.tex", "unsorted/thermodynamics/figures/tikz-cycle.tex"),
    # global glossary
    ("backmatter/glossary/00-glossary.tex", "GLOSSARY/00-glossary.tex"),
    ("backmatter/glossary/part-a-symbols.tex", "GLOSSARY/symbols/part-a-symbols.tex"),
    ("backmatter/glossary/part-b-terms.tex", "GLOSSARY/terms/part-b-terms.tex"),
    ("backmatter/references.tex", "GLOSSARY/references/references.tex"),
    ("docs/NOTATION.md", "GLOSSARY/notes/NOTATION.md"),
    ("docs/GLOSSARY_DRAFT.md", "GLOSSARY/notes/GLOSSARY_DRAFT.md"),
    ("docs/IDENTITIES.md", "GLOSSARY/notes/IDENTITIES.md"),
    # infrastructure
    (".gitignore", ".gitignore"),
    (".cursor/rules/latex-project.mdc", ".cursor/rules/latex-project.mdc"),
    ("README.md", "unsorted/project-docs/README.md"),
    ("main.tex", "unsorted/legacy/main.tex"),
    ("latexmkrc", "unsorted/legacy/latexmkrc"),
]

DIR_RULES = [
    ("backmatter/glossary/part-c-identities/", "GLOSSARY/identities/"),
    ("frontmatter/", "unsorted/frontmatter/"),
    ("docs/", "unsorted/project-docs/"),
    ("legacy/", "unsorted/legacy/"),
    ("build/", "unsorted/legacy-build/build/"),
    ("preamble/", "shared/preamble/"),
    ("tools/", "tools/legacy/"),
]

# Generated outputs of the old root build (untracked except main.pdf).
ROOT_BUILD_OUTPUTS = ["main.aux", "main.fdb_latexmk", "main.fls", "main.log", "main.out",
                      "main.pdf", "main.synctex.gz", "main.toc"]

# Files outside OLD
EXTRA_RULES = [
    ("forms_tensors_geometric_algebra_unified.tex", "unsorted/legacy/forms_tensors_geometric_algebra_unified.tex"),
]

# ---------------------------------------------------------------------------
# Document bodies (reading order). Item kinds:
#   ("todo", id, title, level, prereq-ids)        missing chapter (TODO box)
#   ("todopart", id)                              part heading that does not exist yet
#   ("part", path)                                existing part hub (heading + intro)
#   ("chapter", id, folder, level)                existing chapter; hub = folder/00-section
#   ("wrapped", id, folder, [files], level)       existing subsections without a section heading
#   ("extra", path)                               existing file appended to the previous chapter
# Paths are relative to the document folder.
# ---------------------------------------------------------------------------
U, G, R, B = "undergraduate", "graduate", "postdoc/research", "basic"

BODY = {
    "M1": [
        ("todo", "ch01", "Numbers, complex numbers, sets and functions", B, []),
        ("todo", "ch02", "Calculus of one variable", B, ["M1/ch01"]),
        ("todo", "ch03", "Linear algebra: matrices, determinants, eigenvalues", B, ["M1/ch01"]),
        ("todo", "ch04", "Multivariable and vector calculus in three dimensions: gradient, divergence, curl, line and surface integrals, and the classical theorems of Green, Stokes and Gauss", U, ["M1/ch02", "M1/ch03"]),
        ("todo", "ch05", "Ordinary differential equations", U, ["M1/ch02", "M1/ch03"]),
        ("part", "chapters/00-part-algebra"),
        ("chapter", "ch06", "ch06-vectors-covectors", U),
        ("chapter", "ch07", "ch07-tensors", U),
        ("chapter", "ch08", "ch08-metric", U),
        ("chapter", "ch09", "ch09-exterior-algebra", U),
        ("part", "chapters/00-part-manifolds"),
        ("chapter", "ch10", "ch10-differentiable-manifolds", G),
        ("chapter", "ch11", "ch11-tangent-cotangent", G),
        ("chapter", "ch12", "ch12-tensor-fields-forms", G),
        ("part", "chapters/00-part-integration"),
        ("chapter", "ch13", "ch13-integration-1-forms", G),
        ("chapter", "ch14", "ch14-integration-k-forms", G),
        ("chapter", "ch15", "ch15-stokes", G),
        ("chapter", "ch16", "ch16-gauss", G),
        ("todo", "ch17", "Fourier series, Fourier and Laplace transforms", U, ["M1/ch04", "M1/ch05"]),
        ("todo", "ch18", "Partial differential equations of physics: separation of variables, special functions and Green's functions", U, ["M1/ch04", "M1/ch05", "M1/ch17"]),
        ("todo", "ch19", "Calculus of variations", U, ["M1/ch04", "M1/ch05"]),
        ("todo", "ch20", "Probability, statistics and random processes", U, ["M1/ch02", "M1/ch04"]),
        ("todo", "ch21", "Numerical methods: quadrature, ODE solvers, linear systems and finite differences", U, ["M1/ch03", "M1/ch05", "M1/ch18"]),
        ("todo", "ch22", "Complex analysis: analytic functions, Cauchy's theorem, Laurent series, residues and conformal maps", U, ["M1/ch01", "M1/ch04"]),
    ],
    "M2": [
        ("todopart", "M2/part-I"),
        ("chapter", "ch01", "ch01-clifford-algebra", G),
        ("chapter", "ch02", "ch02-multivector-operations", G),
        ("chapter", "ch03", "ch03-rotors", G),
        ("chapter", "ch04", "ch04-duality", G),
        ("chapter", "ch05", "ch05-synthesis-1", G),
        ("todo", "ch06", "Groups: symmetry, finite groups and representations", G, ["M1/ch08", "M2/ch03"]),
        ("todopart", "M2/part-II"),
        ("chapter", "ch07", "ch07-lie-derivative", G),
        ("chapter", "ch08", "ch08-ga-calculus", G),
        ("chapter", "ch09", "ch09-synthesis-2", G),
        ("extra", "chapters/ch09-synthesis-2/04-classical-corollaries"),
        ("part", "chapters/00-part-geometry"),
        ("chapter", "ch10", "ch10-connections", G),
        ("chapter", "ch11", "ch11-levi-civita", G),
        ("chapter", "ch12", "ch12-riemann-curvature", G),
        ("chapter", "ch13", "ch13-geodesic-deviation", G),
        ("chapter", "ch14", "ch14-synthesis-3", G),
        ("todo", "ch15", "Lie groups and Lie algebras", G, ["M2/ch06", "M2/ch07"]),
        ("todo", "ch16", "Fibre bundles, gauge connections and spinors", R, ["M2/ch10", "M2/ch15"]),
        ("part", "chapters/00-part-complex"),
        ("chapter", "ch17", "ch17-residue-theorem", G),
        ("todo", "ch18", "Hilbert spaces, distributions and spectral theory", G, ["M1/ch17", "M2/ch17"]),
        ("todo", "ch19", "Stochastic processes and statistical methods", G, ["M1/ch20", "M2/ch18"]),
        ("part", "chapters/00-part-perspective"),
        ("chapter", "ch20", "ch20-current-state", R),
        ("chapter", "ch21", "ch21-master-summary", G),
        ("todo", "ch22", "Topology: homotopy, homology and de Rham cohomology", G, ["M1/ch12", "M1/ch15", "M2/ch06"]),
    ],
    "M3": [
        ("todo", "ch01", "Ordinary differential equations: existence and uniqueness, linear systems, Floquet theory and Sturm-Liouville problems", G, ["M1/ch03", "M1/ch05"]),
        ("todo", "ch02", "Dynamical systems: phase portraits, stability, bifurcations and chaos", G, ["M3/ch01"]),
        ("todo", "ch03", "Asymptotic and perturbation methods: regular and singular perturbations, matched asymptotics, multiple scales, WKB", G, ["M1/ch22", "M3/ch01"]),
        ("todo", "ch04", "Partial differential equations: classification, characteristics, first-order equations and well-posedness", G, ["M1/ch04", "M1/ch18", "M3/ch01"]),
        ("todo", "ch05", "Elliptic and parabolic equations: Green's identities, maximum principles, Green's functions and the heat kernel", G, ["M1/ch04", "M1/ch17", "M3/ch04"]),
        ("todo", "ch06", "Hyperbolic equations and conservation laws: wave equation, shocks, the Riemann problem and the Cauchy problem", G, ["M3/ch04"]),
        ("todo", "ch07", "Weak solutions, Sobolev spaces and variational formulations", G, ["M1/ch19", "M2/ch18", "M3/ch05"]),
        ("todo", "ch08", "Nonlinear PDEs: dispersive waves, solitons, and the mathematical theory of the Euler and Navier-Stokes equations", R, ["M3/ch06", "M3/ch07"]),
        ("todo", "ch09", "Numerical methods for PDEs: finite differences, finite volumes, finite elements, spectral methods, stability and convergence", G, ["M1/ch21", "M3/ch05", "M3/ch06", "M3/ch07"]),
    ],
    "CM1": [
        ("todo", "ch01", "Kinematics in one and three dimensions", B, ["M1/ch04"]),
        ("todo", "ch02", "Newton's laws, forces and free-body problems", B, ["CM1/ch01"]),
        ("part", "chapters/00-part-physics"),
        ("chapter", "ch03", "ch03-intrinsic-vs-metric", U),
        ("todo", "ch04", "Work, energy, momentum and conservation laws; collisions and systems of particles", B, ["CM1/ch02"]),
        ("todo", "ch05", "Oscillations: free, damped, driven and coupled (normal modes)", U, ["CM1/ch02", "M1/ch05"]),
        ("todo", "ch06", "Central forces, Kepler orbits, gravitation and scattering", U, ["CM1/ch03", "CM1/ch04"]),
        ("todo", "ch07", "Non-inertial reference frames", U, ["CM1/ch02"]),
        ("todo", "ch08", "Rigid-body motion in 3D: inertia tensor and Euler equations", U, ["CM1/ch04", "M1/ch07"]),
    ],
    "CM2": [
        ("todo", "ch01", "Constraints, variational principles and Lagrangian mechanics (including small oscillations)", U, ["CM1/ch08", "M1/ch11", "M1/ch19"]),
        ("wrapped", "ch02", "ch02-energy-noether-hamiltonian",
         ["02-energy-as-contraction", "03-noether-synthesis", "04-hamiltonian-mechanics"], G),
        ("todo", "ch03", "Symplectic geometry, Poisson brackets and Hamiltonian flows", G, ["CM2/ch02", "M2/ch07"]),
        ("todo", "ch04", "Canonical transformations and Hamilton-Jacobi theory", G, ["CM2/ch03"]),
        ("todo", "ch05", "Integrable systems, action-angle variables, perturbation theory, KAM and chaos", G, ["CM2/ch04", "M3/ch02"]),
        ("todo", "ch06", "Rigid bodies and rotors in geometric algebra", G, ["CM1/ch08", "M2/ch03"]),
        ("todo", "ch07", "Spacetime algebra and relativistic mechanics", G, ["CM2/ch06", "M2/ch03", "M2/ch04"]),
        ("todo", "ch08", "Geometric mechanics: Lie groups, momentum maps and reduction", R, ["CM2/ch03", "M2/ch15"]),
        ("todo", "ch09", "Classical field theory: Lagrangian densities and Noether currents", G, ["CM2/ch02", "M2/ch09"]),
        ("todo", "ch10", "Multisymplectic and covariant formulations", R, ["CM2/ch08", "CM2/ch09"]),
    ],
    "CM3": [
        ("todo", "ch01", "Stress, strain and Hooke's law in one dimension", B, ["CM1/ch02"]),
        ("todo", "ch02", "Kinematics of deformation: displacement and the strain tensor", U, ["CM3/ch01", "M1/ch07"]),
        ("todo", "ch03", "The Cauchy stress tensor and equilibrium", U, ["CM3/ch02", "M1/ch16"]),
        ("todo", "ch04", "Linear isotropic elasticity: Navier-Cauchy equations", U, ["CM3/ch03"]),
        ("todo", "ch05", "Classical problems: torsion, bending, plane elasticity", U, ["CM3/ch04"]),
        ("todo", "ch06", "Beams, plates, shells and buckling", G, ["CM3/ch05", "M1/ch05"]),
        ("todo", "ch07", "Elastic waves", G, ["CM3/ch04", "M1/ch18", "M3/ch06"]),
        ("todo", "ch08", "Energy methods and variational principles", G, ["CM3/ch04", "CM2/ch01", "M1/ch19"]),
        ("todo", "ch09", "Anisotropic elasticity and composites", G, ["CM3/ch04"]),
        ("todo", "ch10", "Finite (nonlinear) elasticity", G, ["CM3/ch08", "M2/ch10"]),
        ("todo", "ch11", "Plasticity, viscoelasticity, thermoelasticity and fracture", G, ["CM3/ch10"]),
        ("todo", "ch12", "Finite element methods for solids", G, ["CM3/ch08", "M1/ch21", "M3/ch07", "M3/ch09"]),
        ("todo", "ch13", "Geometric elasticity: defects, incompatibility and Riemann-Cartan geometry", R, ["CM3/ch10", "M2/ch12", "M2/ch22"]),
    ],
    "F1": [
        ("todo", "ch01", "Continuum hypothesis and kinematics of flow", U, ["CM1/ch02", "CM3/ch02", "M1/ch04"]),
        ("todo", "ch02", "Conservation laws: mass, momentum, energy", U, ["F1/ch01", "CM3/ch03", "M1/ch16"]),
        ("todo", "ch03", "The Navier-Stokes equations and constitutive relations", U, ["F1/ch02"]),
        ("todo", "ch04", "Ideal flow: Euler equations and Bernoulli", U, ["F1/ch03"]),
        ("wrapped", "ch05", "ch05-circulation", ["07-fluids"], G),
        ("todo", "ch06", "Potential flow and complex potentials", U, ["F1/ch04", "M2/ch17"]),
        ("todo", "ch07", "Viscous flows: exact solutions, Stokes flow, lubrication", G, ["F1/ch03"]),
        ("todo", "ch08", "Boundary layers", G, ["F1/ch07", "M3/ch03"]),
        ("todo", "ch09", "Hydrodynamic stability", G, ["F1/ch08", "M3/ch02"]),
        ("todo", "ch10", "Introduction to turbulence", G, ["F1/ch09"]),
        ("todo", "ch11", "Compressible flow and gas dynamics", G, ["F1/ch04", "M3/ch06"]),
        ("todo", "ch12", "Waves in fluids", G, ["F1/ch06", "M3/ch08"]),
    ],
    "F2": [
        ("todo", "ch01", "Turbulence: advanced theory and extensions", R, ["F1/ch10", "M1/ch20", "M2/ch19"]),
        ("todo", "ch02", "Non-Newtonian and complex fluids", G, ["F1/ch07", "CM3/ch11"]),
        ("todo", "ch03", "Temperature-dependent flows: convection and variable properties", G, ["F1/ch09"]),
        ("todo", "ch04", "Multifluid flows: mixing and unmixing", R, ["F2/ch03"]),
        ("todo", "ch05", "Plasma: magnetohydrodynamics and kinetic theory", R, ["F1/ch11", "GR/ch03"]),
        ("todo", "ch06", "Relativistic fluids: special-relativistic flows and fluids in curved spacetime", R, ["GR/ch02", "GR/ch05", "F1/ch11"]),
        ("todo", "ch07", "Quantum fluids: superfluids and Bose-Einstein condensates", R, ["QM/ch08", "F1/ch04", "M3/ch08"]),
        ("todo", "ch08", "Numerical methods for fluids", R, ["F1/ch03", "M1/ch21", "M3/ch09"]),
    ],
    "QM": [
        ("todo", "ch01", "Experimental origins of quantum theory", B, ["CM1/ch02"]),
        ("todo", "ch02", "Wave mechanics and the Schrodinger equation", U, ["QM/ch01", "M1/ch18"]),
        ("todo", "ch03", "One-dimensional problems", U, ["QM/ch02"]),
        ("todo", "ch04", "Hilbert spaces, Dirac notation and the postulates", U, ["QM/ch03", "M2/ch18"]),
        ("todo", "ch05", "The harmonic oscillator", U, ["QM/ch04"]),
        ("todo", "ch06", "Angular momentum and spin", U, ["QM/ch04", "M2/ch06"]),
        ("todo", "ch07", "The hydrogen atom", U, ["QM/ch06"]),
        ("todo", "ch08", "Identical particles, atoms and molecules", G, ["QM/ch06"]),
        ("todo", "ch09", "Approximation methods: perturbation theory, variational, WKB", G, ["QM/ch05", "M3/ch03"]),
        ("todo", "ch10", "Time-dependent perturbation theory and transitions", G, ["QM/ch09"]),
        ("todo", "ch11", "Scattering theory", G, ["QM/ch09"]),
        ("todo", "ch12", "Symmetries in quantum mechanics", G, ["QM/ch06", "M2/ch15"]),
        ("todo", "ch13", "Density matrices, entanglement, measurement and open quantum systems", G, ["QM/ch04", "M1/ch20"]),
        ("todo", "ch14", "Path integrals", G, ["QM/ch05", "CM2/ch01"]),
        ("todo", "ch15", "Relativistic quantum mechanics: Klein-Gordon and Dirac", G, ["QM/ch12", "GR/ch01"]),
    ],
    "QFT": [
        ("todo", "ch01", "Lorentz group and its representations", G, ["GR/ch01", "M2/ch15"]),
        ("todo", "ch02", "Classical field theory", G, ["CM2/ch09"]),
        ("todo", "ch03", "Canonical quantisation of free fields", G, ["QFT/ch02", "QM/ch15"]),
        ("todo", "ch04", "Interacting fields, the S-matrix and Feynman diagrams", G, ["QFT/ch03"]),
        ("todo", "ch05", "Quantum electrodynamics", G, ["QFT/ch04"]),
        ("todo", "ch06", "Path-integral quantisation", G, ["QFT/ch04", "QM/ch14"]),
        ("todo", "ch07", "Renormalisation, the renormalisation group and effective field theory", R, ["QFT/ch05", "QFT/ch06"]),
        ("todo", "ch08", "Non-abelian gauge theories", R, ["QFT/ch07", "M2/ch16"]),
        ("todo", "ch09", "Spontaneous symmetry breaking and the Higgs mechanism", R, ["QFT/ch08"]),
        ("todo", "ch10", "The Standard Model", R, ["QFT/ch09"]),
        ("todo", "ch11", "Anomalies, instantons and topology", R, ["QFT/ch08", "M2/ch22"]),
        ("todo", "ch12", "Quantum field theory in curved spacetime", R, ["QFT/ch06", "GR/ch07"]),
        ("todo", "ch13", "Conformal field theory and research frontiers", R, ["QFT/ch07"]),
    ],
    "GR": [
        ("todo", "ch01", "Special relativity", U, ["CM1/ch02", "M1/ch08"]),
        ("todo", "ch02", "Minkowski spacetime and tensors on spacetime", U, ["GR/ch01", "M1/ch12"]),
        ("wrapped", "ch03", "ch03-electromagnetism-forms", ["06-electromagnetism"], G),
        ("chapter", "ch04", "ch04-bridge-to-gr", G),
        ("todo", "ch05", "The Einstein field equations", G, ["GR/ch04", "M2/ch12"]),
        ("todo", "ch06", "The Schwarzschild solution and classical tests", G, ["GR/ch05"]),
        ("todo", "ch07", "Black holes: horizons, charged and rotating solutions", G, ["GR/ch06"]),
        ("todo", "ch08", "Gravitational waves", G, ["GR/ch05"]),
        ("todo", "ch09", "Cosmology", G, ["GR/ch05"]),
        ("todo", "ch10", "Hamiltonian (ADM) formulation and numerical relativity", R, ["GR/ch05", "CM2/ch03", "M3/ch06"]),
        ("todo", "ch11", "Tetrads, spinors and gauge-theory gravity in geometric algebra", R, ["GR/ch05", "M2/ch16"]),
        ("todo", "ch12", "Causal structure and singularity theorems", R, ["GR/ch07", "M2/ch22"]),
        ("todo", "ch13", "Black hole thermodynamics and Hawking radiation", R, ["GR/ch07", "QFT/ch12"]),
    ],
}

GLOSSARY_TODO = ["M3", "CM1", "CM2", "CM3", "F1", "F2", "QM", "QFT", "GR"]

# Planned prerequisite printed in EDITORIAL_ORGANIZATION.md but not in the PDF box:
# the residue theorem has no label to cite for the missing classical chapter.
EXTRA_PREREQS = {"M2/ch17": ["M1/ch22"]}

# Longer level sentences for the syllabus. The PDF title page keeps DOCS.
ORG_LEVEL = {
    "M1": ("basics",
           "undergraduate, with one graduate-level block: differential geometry and "
           "integration on manifolds (M1/ch10 to M1/ch16)"),
    "M2": ("undergraduate",
           "graduate (tensors, geometric algebra, differential geometry, groups); the last "
           "Lie-group, bundle and survey chapters reach postdoc/research"),
    "M3": ("undergraduate (M1/ch05 and M1/ch18 are the elementary ODE and PDE chapters)",
           "postdoc/research (nonlinear PDEs, M3/ch08); the other chapters are graduate"),
}

# Full "Finish first" sentence body where chapter-only dependencies change it.
FINISH_FIRST = {
    "M3": "[M1](#m1), and [M2/ch18](#m2) only for M3/ch07 onward",
    "CM2": "[CM1](#cm1), [M2](#m2), and [M3/ch02](#m3) only for CM2/ch05 (transitively also M1)",
    "CM3": ("[CM1](#cm1), [M2](#m2), and [CM2/ch01](#cm2) only for CM3/ch08 onward, "
            "[M3/ch06](#m3) only for CM3/ch07, [M3/ch07](#m3) and [M3/ch09](#m3) only for CM3/ch12, "
            "[M2/ch22](#m2) only for CM3/ch13 (transitively also M1)"),
    "F1": ("[CM1](#cm1), and [CM3/ch02](#cm3) to [CM3/ch03](#cm3) (continuum kinematics and stress), "
           "and [M3/ch02](#m3), [M3/ch03](#m3), [M3/ch06](#m3), [M3/ch08](#m3) for F1/ch09, F1/ch08, "
           "F1/ch11, F1/ch12 respectively (transitively also M1, M2)"),
    "F2": ("[F1](#f1), [CM3](#cm3), [GR](#gr), [QM](#qm), and [M3/ch08](#m3), [M3/ch09](#m3) "
           "for F2/ch07, F2/ch08 respectively (transitively also CM1, CM2, M1, M2)"),
    "QM": "[M1](#m1), [CM2](#cm2), and [M3/ch03](#m3) only for QM/ch09 (transitively also CM1, M2)",
    "GR": "[M2](#m2), [CM2](#cm2), and [M3/ch06](#m3) only for GR/ch10 (transitively also CM1, M1)",
}

DOC_BULLETS = {
    "M1": [
        "Reading note: the undergraduate methods chapters M1/ch17 to M1/ch22 do not depend on the "
        "graduate block (M1/ch10 to M1/ch16) and can be read before it.",
        "Green's theorem (planar), Stokes' theorem and the divergence theorem are first met in "
        "classical vector-calculus form in M1/ch04; M1/ch13 to M1/ch16 then present them as special "
        "cases of the general Stokes theorem on manifolds. M1/ch22 uses the planar Green theorem to "
        "prove Cauchy's theorem.",
        "M1/ch22 is appended after M1/ch21 so that existing chapter numbers do not change.",
    ],
    "M2": [
        "Reading note: M2/ch22 is appended after the master summary so that existing chapter numbers "
        "do not change; it can be read any time after M1/ch15 and M2/ch06.",
    ],
    "M3": [
        "Ownership: this document owns the general theory of ordinary differential equations, dynamical "
        "systems, asymptotic methods and partial differential equations; the physics documents reference "
        "it and do not repeat it. M3/ch08 states the Euler and Navier-Stokes equations in the form it "
        "needs; their physical derivation stays in [F1/ch02](#f1) and [F1/ch03](#f1).",
        "Reading note: M3/ch01 to M3/ch03 (ordinary equations) and M3/ch04 to M3/ch09 (partial equations) "
        "are two blocks; the PDE block needs only M3/ch01 from the ODE block. Green's identities in "
        "M3/ch05 follow from the classical divergence theorem of M1/ch04.",
    ],
    "CM3": [
        "Ownership: this document owns continuum kinematics, strain, the Cauchy stress tensor and the "
        "balance laws (CM3/ch02, CM3/ch03); fluid mechanics (F1) references them.",
    ],
    "QM": [
        "Late link: QM/ch15 uses special relativity from [GR/ch01](#gr).",
    ],
    "GR": [
        "Late link: GR/ch13 uses [QFT/ch12](#qft). This is the only dependency of GR on QFT.",
        "Ownership: this document owns special relativity and Minkowski geometry (GR/ch01, GR/ch02); "
        "F2, QFT and CM2/ch07 reference them.",
    ],
}

# Replaces the generated "target level completed by" paragraph.
TARGET_NOTE = {
    "M1": "Target level completed by: **M1/ch21 Numerical methods** and **M1/ch22 Complex analysis** "
          "(both TODO) for the undergraduate path; the graduate differential-geometry block ends at "
          "**M1/ch16 The Gauss (divergence) theorem** (present).",
    "M2": "Target level completed by: **M2/ch21 Master summary** (present).",
    "M3": "Target level completed by: **M3/ch08 Nonlinear PDEs** (TODO). M3/ch09 is a graduate methods "
          "chapter used by [CM3/ch12](#cm3) and [F2/ch08](#f2).",
}

LEVEL_SCALE = [
    "## Level scale",
    "",
    "- **basic**: first-year material with no previous course assumed.",
    "- **undergraduate**: standard degree-course material.",
    "- **graduate**: first-year graduate courses.",
    "- **postdoc/research**: topics at the research frontier.",
]

TOPIC_OWNERSHIP = [
    "## Topic ownership",
    "",
    "Each topic has one owner; other documents reference it and do not repeat it.",
    "",
    "| topic | owner | referenced by |",
    "|---|---|---|",
    "| Continuum kinematics, strain, Cauchy stress, balance laws | [CM3/ch02](#cm3), [CM3/ch03](#cm3) | [F1](#f1) |",
    "| Special relativity and Minkowski geometry | [GR/ch01](#gr), [GR/ch02](#gr) | [F2](#f2), [QFT](#qft), [CM2/ch07](#cm2) |",
    "| Electromagnetism as differential forms | [GR/ch03](#gr) | [F2/ch05](#f2) |",
    "| Tensors, differential forms, integration on manifolds | [M1/ch06](#m1) to [M1/ch16](#m1) | all documents |",
    "| Geometric algebra, connections, curvature, Lie groups, Hilbert spaces | [M2](#m2) | [CM2](#cm2), [GR](#gr), [QM](#qm), [QFT](#qft) |",
    "| Calculus of variations (mathematics) | [M1/ch19](#m1) | [CM2/ch01](#cm2), [CM3/ch08](#cm3), [M3/ch07](#m3) |",
    "| Probability and stochastic processes | [M1/ch20](#m1), [M2/ch19](#m2) | [F2/ch01](#f2), [QM/ch13](#qm) |",
    "| Numerical methods | [M1/ch21](#m1) (basics), [M3/ch09](#m3) (general theory for PDEs), [CM3/ch12](#cm3) (finite elements for solids), [F2/ch08](#f2) (fluids) | |",
    "| Green's, Stokes' and divergence theorems | [M1/ch04](#m1) (classical statements, including the planar Green theorem); [M1/ch15](#m1), [M1/ch16](#m1) (general form) | [M1/ch22](#m1) (Cauchy's theorem), [M3/ch05](#m3) (Green's identities), [CM3/ch03](#cm3), [F1/ch02](#f1) |",
    "| Ordinary differential equations: existence and uniqueness, linear systems, Sturm-Liouville, dynamical systems, asymptotic methods | [M1/ch05](#m1) (elementary), [M3/ch01](#m3) to [M3/ch03](#m3) | [CM1/ch05](#cm1), [CM2/ch05](#cm2), [QM/ch09](#qm), [F1/ch08](#f1), [F1/ch09](#f1) |",
    "| Partial differential equations: classification, elliptic, parabolic, hyperbolic, weak solutions, nonlinear PDEs, Green's functions | [M1/ch18](#m1) (elementary), [M3/ch04](#m3) to [M3/ch09](#m3) | [CM3/ch07](#cm3), [CM3/ch12](#cm3), [F1/ch11](#f1), [F1/ch12](#f1), [F2/ch07](#f2), [F2/ch08](#f2), [GR/ch10](#gr) |",
    "| Complex analysis | [M1/ch22](#m1) (classical), [M2/ch17](#m2) (as Stokes' theorem) | [F1/ch06](#f1), [M3/ch03](#m3) |",
    "| Topology: homotopy, homology, de Rham cohomology | [M2/ch22](#m2) | [QFT/ch11](#qft), [GR/ch12](#gr), [CM3/ch13](#cm3) |",
    "| Symbols, terms, identities, bibliography | [GLOSSARY](#glossary) | all documents |",
]

COVERAGE = [
    "## Coverage of the requested topics",
    "",
    "| requested | where |",
    "|---|---|",
    "| General relativity from nothing to postdoc | [GR](#gr) (undergraduate to postdoc/research) |",
    "| Quantum mechanics from nothing to full QM | [QM](#qm) (basic to graduate) |",
    "| QFT from quantum mechanics to postdoc | [QFT](#qft) (graduate to postdoc/research) |",
    "| Classical mechanics, basic Newton to 3D | [CM1](#cm1) (basic to undergraduate) |",
    "| Classical mechanics, 3D to Lagrangian to postdoc with modern mathematics | [CM2](#cm2); geometric algebra in CM2/ch06 and CM2/ch07, prepared by [M2](#m2) |",
    "| Elastic materials, zero to postdoc | [CM3](#cm3) (basic to postdoc/research) |",
    "| Fluids from Navier-Stokes to postdoc | [F1](#f1) (classical flows), [F2](#f2) (extensions below) |",
    "| Turbulence | [F1/ch10](#f1) (introduction), [F2/ch01](#f2) (advanced) |",
    "| Non-Newtonian flows | [F2/ch02](#f2) |",
    "| Temperature-dependent flows | [F2/ch03](#f2) |",
    "| Multifluid flows, mixing and unmixing | [F2/ch04](#f2) |",
    "| Plasma flows | [F2/ch05](#f2) |",
    "| Special-relativistic flows | [F2/ch06](#f2) |",
    "| Quantum flows | [F2/ch07](#f2) |",
    "| Ordinary and partial differential equations (theory, stability, asymptotics, numerics) | [M1/ch05](#m1), [M1/ch18](#m1) (basics); [M3](#m3) (graduate to postdoc/research) |",
    "| Mathematics needed for all of this | [M1](#m1), [M2](#m2), [M3](#m3) |",
]
