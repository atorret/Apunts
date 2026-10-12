kind: book-organization
book: M1

# M1 Mathematics I: Foundations

- Folder: M1-math-foundations
- Entry level: undergraduate
- Target level: graduate
- Editorial status: To Review
- Finish first: M0

## Notes

Entry level: undergraduate (after M0). Target level: graduate (differential geometry and integration on manifolds: M1/ch05 to M1/ch12); the tensor-algebra chapters M1/ch01 to M1/ch04 are undergraduate.
Finish first: [M0](#m0)
Green's theorem (planar), Stokes' theorem and the divergence theorem are first met in classical vector-calculus form in M0/ch04; M1/ch09 to M1/ch12 then present them as special cases of the general Stokes theorem on manifolds. M0/ch12 uses the planar Green theorem to prove Cauchy's theorem.
M1/ch08 (the Lie derivative, moved here from M2/ch07) comes straight after the forms chapter M1/ch07 and before the integration chapters, because the Gauss theorem in M1/ch12 is derived from it.
Why M1/ch08 and the Hodge star are in M1: in main.pdf the divergence is defined by L_X mu = (div X) mu and Gauss is Stokes for the form i_X mu with d i_X mu = L_X mu (Cartan's formula), so M1/ch12 needs M1/ch08. The curl in M1/ch07 and the classical dictionary grad, curl, div via the musical isomorphisms and the Hodge star in M1/ch12 need the star, which is therefore defined in M1/ch04. M1 stays independent of M2.
The Lie bracket appears in Theorem 12.5(3) of M1/ch07 (the invariant formula for d); the text defines it inline, so M1/ch08 is not a prerequisite of M1/ch07. The Synthesis boxes at the end of M1/ch10 and M1/ch12 compare with geometric algebra and point forward to M2/ch04 and M2/ch09: they are comparisons, not prerequisites.
M1 chapters are numbered consecutively, M1/ch01 to M1/ch12, in reading order.
Target level completed by: **M1/ch12 The Gauss (divergence) theorem** (present), which needs **M1/ch08 The Lie derivative and Cartan's formula** (present).

## Parts

This table is the complete list of parts in the book. A chapter may name a part as a prerequisite.


| part                | title       |
| ------------------- | ----------- |
| M1/part:algebra     | Algebra     |
| M1/part:integration | Integration |
| M1/part:manifolds   | Manifolds   |




## Chapters

This table is the complete chapter list, in reading order. Finish each prerequisite before the chapter. Mark an optional prerequisite with (opt.). What each chapter must teach is in What to explain.


| chapter | title                                                      | level         | presence | editorial status | path                                                       | prerequisites                                        | notes                                                                                                                                                               |
| ------- | ---------------------------------------------------------- | ------------- | -------- | ---------------- | ---------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M1/ch01 | Vectors, covectors and contraction                         | undergraduate | present  | To Review        | M1-math-foundations/chapters/ch01-vectors-covectors        | none                                                 |                                                                                                                                                                     |
| M1/ch02 | Multilinear maps, tensors and the tensor algebra           | undergraduate | present  | To Review        | M1-math-foundations/chapters/ch02-tensors                  | M1/ch01; M1/part:algebra                             |                                                                                                                                                                     |
| M1/ch03 | The metric tensor and the musical isomorphisms             | undergraduate | present  | To Review        | M1-math-foundations/chapters/ch03-metric                   | M1/ch01; M1/ch02                                     |                                                                                                                                                                     |
| M1/ch04 | The exterior algebra, the wedge product and the Hodge star | undergraduate | present  | To Review        | M1-math-foundations/chapters/ch04-exterior-algebra         | M1/ch01; M1/ch02; M1/ch03                            | the Hodge star (Definition 8.9, the sign rule and the star on forms) moves here from main.pdf §8.4; its comparison with the geometric-algebra dual stays in M2/ch04 |
| M1/ch05 | Differentiable manifolds                                   | graduate      | present  | To Review        | M1-math-foundations/chapters/ch05-differentiable-manifolds | M1/part:algebra                                      |                                                                                                                                                                     |
| M1/ch06 | Tangent and cotangent spaces                               | graduate      | present  | To Review        | M1-math-foundations/chapters/ch06-tangent-cotangent        | M1/ch01; M1/ch02; M1/ch03; M1/ch04; M1/ch05          |                                                                                                                                                                     |
| M1/ch07 | Tensor fields and differential forms                       | graduate      | present  | To Review        | M1-math-foundations/chapters/ch07-tensor-fields-forms      | M1/ch01; M1/ch02; M1/ch03; M1/ch04; M1/ch06          |                                                                                                                                                                     |
| M1/ch08 | The Lie derivative and Cartan's formula                    | graduate      | present  | To Review        | M1-math-foundations/chapters/ch08-lie-derivative           | M1/ch04; M1/ch06; M1/ch07                            | graduate; moved from M2/ch07; includes the operator relations [∂_i, x^j] = {ι_i, dx^j ∧} = δ and the Heisenberg/fermion remark                                      |
| M1/ch09 | Integration of 1-forms                                     | graduate      | present  | To Review        | M1-math-foundations/chapters/ch09-integration-1-forms      | M1/ch01; M1/ch06; M1/ch07                            |                                                                                                                                                                     |
| M1/ch10 | From 1-forms to k-forms: integration is full contraction   | graduate      | present  | To Review        | M1-math-foundations/chapters/ch10-integration-k-forms      | M1/ch04; M1/ch06; M1/ch09                            |                                                                                                                                                                     |
| M1/ch11 | Stokes' theorem as it is understood today                  | graduate      | present  | To Review        | M1-math-foundations/chapters/ch11-stokes                   | M1/ch05; M1/ch07; M1/ch09; M1/ch10                   |                                                                                                                                                                     |
| M1/ch12 | The Gauss (divergence) theorem                             | graduate      | present  | To Review        | M1-math-foundations/chapters/ch12-gauss                    | M1/ch03; M1/ch04; M1/ch07; M1/ch08; M1/ch10; M1/ch11 |                                                                                                                                                                     |




## What to explain

These sections are the complete chapter list. Write what each chapter must teach under its heading. An empty section means it is not decided yet.

### M1/ch01 Vectors, covectors and contraction



### M1/ch02 Multilinear maps, tensors and the tensor algebra



### M1/ch03 The metric tensor and the musical isomorphisms



### M1/ch04 The exterior algebra, the wedge product and the Hodge star



### M1/ch05 Differentiable manifolds



### M1/ch06 Tangent and cotangent spaces



### M1/ch07 Tensor fields and differential forms



### M1/ch08 The Lie derivative and Cartan's formula



### M1/ch09 Integration of 1-forms



### M1/ch10 From 1-forms to k-forms: integration is full contraction



### M1/ch11 Stokes' theorem as it is understood today



### M1/ch12 The Gauss (divergence) theorem



## Book dependencies

This table is the complete list of books that must be finished first. Importing the file updates them. The Finish first line above is the same list.


| requires |
| -------- |
| M0       |




## Sources

This table is the complete list of sources for this book. Importing the file updates them. A source listed in several books has one registry row: its file, proposed chapter, status, and reference change everywhere.


| ID     | file | proposed chapter | status         | reference                                                                                                                                                                  |
| ------ | ---- | ---------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spivak | none | -                | cited, no file | M. Spivak, *Calculus on Manifolds*, Benjamin, 1965.                                                                                                                        |
| Lee    | none | -                | cited, no file | J. M. Lee, *Introduction to Smooth Manifolds*, 2nd ed., Springer GTM 218, 2013 (Chapters 11, 14, 16); and *Introduction to Riemannian Manifolds*, 2nd ed., Springer, 2018. |
| BottTu | none | -                | cited, no file | R. Bott and L. W. Tu, *Differential Forms in Algebraic Topology*, Springer GTM 82, 1982.                                                                                   |
| Katz   | none | -                | cited, no file | V. J. Katz, ``The history of Stokes' theorem'', *Mathematics Magazine* 52 (1979), 146-156.                                                                                 |


