# Baseline (Phase 0)

Source: `legacy/original.tex` (a byte-for-byte copy of
`../forms_tensors_geometric_algebra_unified.tex`, 4143 lines), compiled three times with
MiKTeX `pdflatex -interaction=nonstopmode`. Output: `legacy/original.pdf`.

Reproduce with `python tools/check.py legacy/original.tex legacy/original.log`.

## Build

| Item | Value |
|---|---|
| Pages | 96 |
| LaTeX/package warnings | 83 (all `Package hyperref Warning: Token not allowed in a PDF string (Unicode)`, caused by math in section titles) |
| Overfull boxes | 4 |
| Underfull boxes | 27 |
| Undefined references/citations | 0 |

## Invariants (the restructured project must match or exceed each count)

| Counter | Baseline |
|---|---|
| `\label` | 243 |
| `\ref` + `\eqref` | 352 (152 distinct targets) |
| `\cite` | 0 |
| `\bibitem` | 27 |
| `\part` | 7 |
| `\section` (numbered) | 29 (+2 starred: Reading guide, References) |
| `\subsection` (numbered) | 92 (+2 starred) |
| `\Step` | 32 |
| `\numcheck` | 12 (11 in the body + the `\newcommand` in the preamble; since Phase 3 `tools/check.py` counts the body only, so the body baseline is **11**) |
| example | 59 |
| formal | 32 |
| intuition | 44 |
| synthesis | 14 |
| definition | 19 |
| theorem | 17 |
| proposition | 19 |
| lemma | 1 |
| corollary | 3 |
| proof | 34 |
| exercises | 7 |
| keypoints | 7 |
| keyidea | 8 |
| pitfall | 6 |
| remark | 13 |
| specialcase | 5 |
| figure | 7 |
| table | 1 |
| tikzpicture | 8 |

## Corrections to the brief

- 29 numbered sections (31 including the two starred ones).
- 352 `\ref`/`\eqref` occurrences (152 distinct labels), not 272.
- 27 `\bibitem`s, not 25.
- 34 extract blocks.
- 11 numbered forward refs and 94 forward `sec:`/`part:` refs (93 + `part:integration`).
- All 15 in-body `\renewcommand`s are `\arraystretch`; no macro had to move.

The section count may change only if sections are merged; the plan keeps all 29.
