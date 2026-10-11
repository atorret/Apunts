# From Vectors to Stokes to Spacetime — modular LaTeX source

Notes on forms, tensors and geometric algebra, split from the single file
`legacy/original.tex` into a modular project.

## Build

```
latexmk            # uses latexmkrc: pdflatex, nonstopmode, output in build/main.pdf
latexmk -C         # clean build/
python tools/check.py main.tex build/main.log   # invariant counts, duplicate/undefined labels, warnings
```

Requires a TeX distribution with `latexmk` and `pdflatex` (tested with MiKTeX) and Python 3 for the checker.

## Folder map

| Path | Contents |
|---|---|
| `main.tex` | Thin root: preamble inputs, front matter, the seven parts, glossary, references |
| `preamble/` | `packages`, `colors`, `layout`, `environments` (boxes, counters, `\Step`, `\numcheck`), `macros-general`, `macros-geometry`, `macros-algebra` |
| `frontmatter/` | `title`, `abstract`, `reading-guide` |
| `parts/NN-slug/` | One folder per part; `00-part.tex` holds the part heading and intro |
| `parts/NN-slug/NN-section/` | One folder per section; `00-section.tex` holds the heading, intro and the `\input` list; `NN-*.tex` are subsections; `exercises.tex` and `keypoints.tex` close the section |
| `figures/partN/` | One file per figure (`tikz-*.tex`), complete with caption and label |
| `backmatter/glossary/` | Glossary: Part A symbols, Part B terms, Part C identities (with proofs) |
| `backmatter/references.tex` | The `thebibliography` block |
| `docs/` | Tracking files (see below) |
| `legacy/` | `original.tex` (read-only) and `original.pdf` |
| `tools/` | `split.py` (one-off splitter used in Phase 2), `check.py` (invariant checker) |

## Label convention

Existing label names are never changed. Prefixes: `part:`, `sec:`, `def:`, `thm:`, `prop:`, `lem:`,
`cor:`, `ex:`, `rem:`, `eq:`, `fig:`, `tab:`, and `id:` for the glossary identities (numbered C.1, C.2, …).
Always refer with `\ref`/`\eqref`; never hard-code a number.

## How to add a section

1. Create a folder `parts/NN-part/MM-new-section/` with `00-section.tex` containing the `\section{...}\label{sec:...}`
   heading, a short intro, and `\input{...}` lines for its subsection files.
2. Start every file with the header
   `% Section N: title | Part: P | Depends on: sec:a, sec:b | Status: todo` and
   `%!TEX root = ../../../main.tex`.
3. Add `\input{parts/NN-part/MM-new-section/00-section}` to the part's `00-part.tex`, in reading order.
4. Put any new macro in `preamble/`, never in a content file.
5. Run `latexmk` and `python tools/check.py main.tex build/main.log`.

## Finding rewriter-marked blocks

Every block changed during the restructure carries a marker comment:

```
rg "% REORDERED"               # moved block (comment says from where)
rg "% REWRITTEN"               # reworded / merged / trimmed block
rg "% PROOF ADDED BY REWRITER" # new proof
rg "% AUTHOR-NOTE:"            # doubtful mathematics, needs the author's decision
rg "Status: todo"              # files not yet reviewed
```

The doubtful points are also listed in `docs/AUTHOR_NOTES.md`.

## Tracking files (`docs/`)

| File | Purpose |
|---|---|
| `BASELINE.md` | Page count, warnings and invariant counts of the original |
| `REWRITE_PLAN.md` | Every move, merge and preview, with status |
| `NOTATION.md` | Notation conventions and the clashes that remain |
| `GLOSSARY_DRAFT.md` | Term list behind glossary Part B |
| `IDENTITIES.md` | Identity list behind glossary Part C, with proof status |
| `AUTHOR_NOTES.md` | Suspected errors and open questions for the author |
| `PROVENANCE.md` | Source (A/B/C) extract markers removed from the text, with line ranges |
