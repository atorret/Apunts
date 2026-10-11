# Rewrite plan and status

Conservative edit: same 7 parts, same 29 sections, same order, except for the targeted moves below.
Line numbers refer to `legacy/original.tex`. Status: `[ ]` todo, `[x]` done.

## Forward-dependency fixes

- [ ] **F1** `prop:wedgeprops`: keep (a)–(d); `eq:antider` moves to `sec:interior` with a new proof; (e) (pull-back of a wedge) moves to `sec:pushpull`; `eq:dleibniz` stays as a preview pointing to `def:d`.
- [ ] **F2** Example "raising an index in polar coordinates" (L826–831) moves to `sec:pushpull` after `ex:polarmetric`; Exercise 3 of `sec:metric` gets a `\ref` preview.
- [ ] **F3** `ex:polarwedge` (L1024–1034) moves to `sec:changecoords` after `ex:polarbasis`; forward clause to `ex:paraboloid` dropped.
- [ ] **F4** `thm:dprops(3)`: inline one-line definition of the Lie bracket with `\ref{sec:lie}`.
- [ ] **F5** `eq:iotavol` computation moves from `sec:flux` to `sec:interior`; the step-by-step curl/div verification moves from `sec:classical` into the `R^3` example of `sec:dform`.
- [ ] **F6** `sec:classical` moves to the end of `sec:gauss`.
- [ ] **F7** Sphere examples in `sec:conn` (L3013–3019, L3041–3047) move into `sec:lc` as `ex:spheretransport`, `ex:spheregeod`; refs in `sec:curv`, `sec:curvdd` updated.
- [ ] **F8** `sec:noethersynth` (L3404–3421) moves into Part V after `sec:phys-energy`; bridge synthesis box trimmed to a pointer.
- [ ] **F9** `thm:extuniv` before `thm:extbasis`.

## Previews (one sentence each)

- [ ] `\dd x`, `\partial_x` as dual-basis names, start of `sec:contraction`.
- [ ] Cartan line in the `sec:interior` list.
- [ ] `\vd^2=\pm\Box` in the signature pitfall.
- [ ] Sphere area form in `sec:symcontr` → new label `ex:sphereareaform`.
- [ ] `thm:dprops(4)` → preview of `thm:stokes`.
- [ ] `sec:lc` conserved quantities → preview of `prop:threederivs`.
- [ ] `\vol` and flux 2-form defined in Synthesis II.
- [ ] Hodge star on forms bridge at end of the Hodge subsection of `sec:duality`.
- [ ] Partition of unity, manifold orientation, manifold with boundary at first use (`sec:intk`, `sec:stokes`).
- [ ] `ex:onefunction` cites `thm:dprops`.
- [ ] `rem:kfactorial` above the conventions table.
- [ ] `eq:ftc` reworded as "proved as ... in ...".
- Kept as explicit previews: `rem:twomodels`, `eq:interior`, `tab:dictionary3`, `prop:reparam`, `lem:fluxbdry` (L2646), `eq:newton`, and the ~75 `\ref{sec:...}` signposts in roadmaps.

## Exercises to section end

- [ ] `sec:tensors` (L725–730) → `02-tensors/exercises.tex`.
- [ ] `sec:metric` (L833–840) → `03-metric/exercises.tex`.

## Merges

- [ ] Multilinear map: B formal box (L513) + C definition (L527).
- [ ] Metric: `sec:quadform` box reduced to Q, polarization, (p,q,r), `R^{p,q}`; duplicate sharp/flat (L861) dropped; degenerate g logged.
- [ ] `sec:symcontr` wedge → preview of `eq:wedge11`.
- [ ] `rem:normalisation` + "second description" (L1204) + part of `rem:twomodels`.
- [ ] `ex:polardiv` trimmed, refers back to `sec:conn`.
- [ ] Free particle in polar coordinates: labels `ex:polarstraight`, `ex:polarEL`, `ex:angmom`; `ex:polarfree` keeps mechanics.
- [ ] Pull-back: `eq:pullback` moves to `sec:pushpull`.
- [ ] Signature: pitfall in `sec:quadform` is the authority.
- [ ] Duplicate non-pure example in `sec:tensorproduct`; repeated `T_pM` intros in `sec:dform`, `sec:ga-calculus`.

## Notation

- [ ] E→V, (m→n) in Part I source-B blocks.
- [ ] `\phi` for maps, `\varphi` for angles; plane polar `(r,\varphi)` in Parts I–IV; `\dd\theta` angle form kept.
- [ ] Rotors `R` → `\rotor` in `sec:rotors`, L1612, L4073, figure caption.
- [ ] `\Phi^*` → `\Phi\pb`.

## Other

- [ ] `\cite` at author mentions (no new bibitems).
- [ ] Abstract: "three synthesis sections and a fourth synthesis subsection".
- [ ] Remove "(source A/B/C)" from headings and boxes.
- [ ] AUTHOR-NOTE markers (see `AUTHOR_NOTES.md`).
- [ ] Glossary (Phase 4).
