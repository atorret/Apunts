# External sources

Registry of every source. Generated from `library.sqlite`. Edit a source in the organization file of a book that lists it, then import that file.

Workflow for new sources:

1. Put the file in the owning document's `sources/` folder (for example `QM-quantum-mechanics/sources/`). Sources that concern several documents go to the owner of the topic they mainly treat.
2. Add a row to that book's organization file with status `unplaced`, then import the file.
3. Propose its placement in [ROADMAP.md](ROADMAP.md) (section "Proposed source placements"), naming the [EDITORIAL_ORGANIZATION.md](EDITORIAL_ORGANIZATION.md) row it would fill; status `proposed`.
4. Only after approval: status `approved`; content is merged into chapters only when asked (`merged`).

Status values: `unplaced`, `proposed`, `approved`, `merged`; `cited, no file` for bibliography entries already cited in the text whose file is not in the repository.

## Registry

| ID | file | document | proposed chapter | status | reference |
|---|---|---|---|---|---|
| Spivak | none | cited by M1, M2, GLOSSARY | - | cited, no file | M. Spivak, *Calculus on Manifolds*, Benjamin, 1965. |
| Lee | none | cited by M1, M2, GLOSSARY | - | cited, no file | J. M. Lee, *Introduction to Smooth Manifolds*, 2nd ed., Springer GTM 218, 2013 (Chapters 11, 14, 16); and *Introduction to Riemannian Manifolds*, 2nd ed., Springer, 2018. |
| BottTu | none | cited by M1, M2, GLOSSARY | - | cited, no file | R. Bott and L. W. Tu, *Differential Forms in Algebraic Topology*, Springer GTM 82, 1982. |
| Arnold | none | cited by CM2 | - | cited, no file | V. I. Arnold, *Mathematical Methods of Classical Mechanics*, Springer, 1989 (Chapter 7). |
| Frankel | none | cited by no document | - | cited, no file | T. Frankel, *The Geometry of Physics*, Cambridge University Press. |
| EvansGariepy | none | cited by M2 | - | cited, no file | L. C. Evans and R. F. Gariepy, *Measure Theory and Fine Properties of Functions*, CRC Press (De Giorgi-Federer theorem). |
| Federer | none | cited by M2 | - | cited, no file | H. Federer, *Geometric Measure Theory*, Springer, 1969 (currents). |
| Harrison | none | cited by M2 | - | cited, no file | J. Harrison, ``Stokes' theorem for nonsmooth chains'', *Bull. AMS* 29 (1993), 235-242. |
| AFW | none | cited by M2 | - | cited, no file | D. N. Arnold, R. S. Falk, R. Winther, ``Finite element exterior calculus, homological techniques, and applications'', *Acta Numerica* 15 (2006). |
| MTW | none | cited by M2, GR | - | cited, no file | C. W. Misner, K. S. Thorne, J. A. Wheeler, *Gravitation*, Freeman, 1973 (one-forms as ``stacks of sheets'', Chapters 2-4). |
| Burke | none | cited by GR | - | cited, no file | W. L. Burke, *Applied Differential Geometry*, Cambridge University Press, 1985 (twisted forms, physics). |
| HehlObukhov | none | cited by GR | - | cited, no file | F. W. Hehl and Yu. N. Obukhov, *Foundations of Classical Electrodynamics*, Birkh"auser, 2003. |
| ArnoldKhesin | none | cited by F1 | - | cited, no file | V. I. Arnold and B. A. Khesin, *Topological Methods in Hydrodynamics*, Springer, 1998. |
| Caratheodory | none | cited by Unsorted | - | cited, no file | C. Carath'eodory, ``Untersuchungen "uber die Grundlagen der Thermodynamik'', *Math. Ann.* 67 (1909), 355-386. |
| AharonovBohm | none | cited by GR | - | cited, no file | Y. Aharonov and D. Bohm, ``Significance of electromagnetic potentials in the quantum theory'', *Phys. Rev.* 115 (1959), 485-491. |
| Ahlfors | none | cited by M2 | - | cited, no file | L. V. Ahlfors, *Complex Analysis*, 3rd ed., McGraw-Hill, 1979. |
| Needham | none | cited by M2 | - | cited, no file | T. Needham, *Visual Complex Analysis*, Oxford University Press, 1997. |
| GriffithsHarris | none | cited by M2 | - | cited, no file | P. Griffiths and J. Harris, *Principles of Algebraic Geometry*, Wiley, 1978 (residues, Riemann surfaces, Poincar'e-Lelong). |
| Hormander | none | cited by M2 | - | cited, no file | L. H"ormander, *An Introduction to Complex Analysis in Several Variables*, North-Holland (Cauchy-Pompeiu, $$). |
| Katz | none | cited by M1 | - | cited, no file | V. J. Katz, ``The history of Stokes' theorem'', *Mathematics Magazine* 52 (1979), 146-156. |
| Carroll | none | cited by M2, GR, GLOSSARY | - | cited, no file | S. Carroll, *Spacetime and Geometry: An Introduction to General Relativity*, Addison-Wesley, 2004. |
| HS | none | cited by M2 | - | cited, no file | D. Hestenes and G. Sobczyk, *Clifford Algebra to Geometric Calculus*, Reidel, 1984. |
| DL | none | cited by M2 | - | cited, no file | C. Doran and A. Lasenby, *Geometric Algebra for Physicists*, Cambridge University Press, 2003. |
| DFM | none | cited by no document | - | cited, no file | L. Dorst, D. Fontijne and S. Mann, *Geometric Algebra for Computer Science*, Morgan Kaufmann, 2007. |
| Lo | none | cited by no document | - | cited, no file | P. Lounesto, *Clifford Algebras and Spinors*, 2nd ed., Cambridge University Press, 2001. |
| LM | none | cited by M2 | - | cited, no file | H. B. Lawson and M.-L. Michelsohn, *Spin Geometry*, Princeton University Press, 1989. |
| Gr | none | cited by no document | - | cited, no file | W. Greub, *Multilinear Algebra*, 2nd ed., Springer, 1978. |

## Source files

No source files have been added yet. Each document has an empty `sources/` folder.
