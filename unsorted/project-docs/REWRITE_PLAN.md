# Rewrite plan and status

Conservative edit: same 7 parts, same 29 sections, same order, except for the targeted moves below.
Line numbers refer to `legacy/original.tex`. Status: `[ ]` todo, `[x]` done.

## Forward-dependency fixes

- [x] **F1** `prop:wedgeprops`: keep (a)–(d); `eq:antider` moves to `sec:interior` with a new proof; (e) (pull-back of a wedge) moves to `sec:pushpull`; `eq:dleibniz` stays as a preview pointing to `def:d`.
- [x] **F2** Example "raising an index in polar coordinates" (L826–831) moves to `sec:pushpull` after `ex:polarmetric`; Exercise 3 of `sec:metric` gets a `\ref` preview.
- [x] **F3** `ex:polarwedge` (L1024–1034) moves to `sec:changecoords` after `ex:polarbasis`; forward clause to `ex:paraboloid` dropped.
- [x] **F4** `thm:dprops(3)`: inline one-line definition of the Lie bracket with `\ref{sec:lie}`.
- [x] **F5** `eq:iotavol` computation moves from `sec:flux` to `sec:interior`; the step-by-step curl/div verification moves from `sec:classical` into the `R^3` example of `sec:dform`.
- [x] **F6** `sec:classical` moves to the end of `sec:gauss`.
- [x] **F7** Sphere examples in `sec:conn` (L3013–3019, L3041–3047) move into `sec:lc` as `ex:spheretransport`, `ex:spheregeod`; refs in `sec:curv`, `sec:curvdd` updated.
- [x] **F8** `sec:noethersynth` (L3404–3421) moves into Part V after `sec:phys-energy`; bridge synthesis box trimmed to a pointer.
- [x] **F9** `thm:extuniv` before `thm:extbasis`.

## Previews (one sentence each)

- [x] `\dd x`, `\partial_x` as dual-basis names, start of `sec:contraction`.
- [x] Cartan line in the `sec:interior` list.
- [x] `\vd^2=\pm\Box` in the signature pitfall.
- [x] Sphere area form in `sec:symcontr` → new label `ex:sphereareaform`.
- [x] `thm:dprops(4)` → preview of `thm:stokes`.
- [x] `sec:lc` conserved quantities → preview of `prop:threederivs`.
- [x] `\vol` and flux 2-form defined in Synthesis II.
- [x] Hodge star on forms bridge at end of the Hodge subsection of `sec:duality`.
- [x] Partition of unity, manifold orientation, manifold with boundary at first use (`sec:intk`, `sec:stokes`).
- [x] `ex:onefunction` cites `thm:dprops`.
- [x] `rem:kfactorial` above the conventions table.
- [x] `eq:ftc` reworded as "proved as ... in ...".
- Kept as explicit previews: `rem:twomodels`, `eq:interior`, `tab:dictionary3`, `prop:reparam`, `lem:fluxbdry` (L2646), `eq:newton`, and the ~75 `\ref{sec:...}` signposts in roadmaps.

## Exercises to section end

- [x] `sec:tensors` (L725–730) → `02-tensors/exercises.tex`.
- [x] `sec:metric` (L833–840) → `03-metric/exercises.tex`.

## Merges

- [x] Multilinear map: B formal box (L513) + C definition (L527).
- [x] Metric: `sec:quadform` box reduced to Q, polarization, (p,q,r), `R^{p,q}`; duplicate sharp/flat (L861) dropped; degenerate g logged.
- [x] `sec:symcontr` wedge → preview of `eq:wedge11`.
- [x] `rem:normalisation` + "second description" (L1204) + part of `rem:twomodels`.
- [x] `ex:polardiv` trimmed, refers back to `sec:conn`.
- [x] Free particle in polar coordinates: labels `ex:polarstraight`, `ex:polarEL`, `ex:angmom`; `ex:polarfree` keeps mechanics.
- [x] Pull-back: `eq:pullback` moves to `sec:pushpull`.
- [x] Signature: pitfall in `sec:quadform` is the authority.
- [x] Duplicate non-pure example in `sec:tensorproduct`; repeated `T_pM` intros in `sec:dform`, `sec:ga-calculus`.

## Notation

- [x] E→V, (m→n) in Part I source-B blocks.
- [x] `\phi` for maps, `\varphi` for angles; plane polar `(r,\varphi)` in Parts I–IV; `\dd\theta` angle form kept.
- [x] Rotors `R` → `\rotor` in `sec:rotors`, L1612, L4073, figure caption.
- [x] `\Phi^*` → `\Phi\pb`.

## Other

- [x] `\cite` at author mentions (no new bibitems).
- [x] Abstract: "three synthesis sections and a fourth synthesis subsection".
- [x] Remove "(source A/B/C)" from headings and boxes.
- [x] AUTHOR-NOTE markers (see `AUTHOR_NOTES.md`).
- [x] Glossary (Phase 4).

## Phase 4

- [x] Glossary Part A (symbols), Part B (terms, alphabetical, synonyms as `see` entries), Part C (40 identities with proofs; `docs/IDENTITIES.md`).
- [x] `\ref{id:...}` pointers in the body (`prop:contr`, `prop:wedgeprops`, `prop:detformula`, `thm:hodgeGA`, `sec:pushpull`, `thm:dprops`, `eq:christtransf`, `eq:riemanncomp`, Bianchi, metric case).
- [x] Abstract and reading guide updated (synthesis count, glossary, provenance only in the reading guide).
- [x] Quality checks: clean rebuild, no `??`, invariants >= baseline, files <= 300 lines, macros only in `preamble/`.
