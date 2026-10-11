"""Generate the root markdown files from the structure config and the tree.

  python tools/gen_docs.py   writes MIGRATION_LEDGER.md, CHAPTER_ORGANIZATION.md,
                             ROADMAP.md (status tables) and sources_index.md
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structure_config import (DOCS, CONTENT_DOCS, FOLDER, TITLE, MAINFILE, JOB, BODY, DOC_EDGES,
                              GLOSSARY_TODO, ancestors)
import texscan
import wordcount
from xref_graph import direction

ROOT = texscan.ROOT
LEVEL_RANK = {"basic": 0, "undergraduate": 1, "graduate": 2, "postdoc/research": 3}

# Existing chapters whose content spans more than one level (rows say so; nothing is split).
SPANS = {
    "CM1/ch03": "spans undergraduate to graduate: written in the language of differential forms "
                "(prerequisites in M1) and uses the Levi-Civita connection (M2/ch11)",
    "CM2/ch02": "graduate; also previews relativity (energy as a contraction) and Bohr-Sommerfeld quantisation",
    "F1/ch05": "graduate: Kelvin's circulation theorem stated with differential forms and the Lie derivative",
    "GR/ch03": "graduate: Maxwell's equations as forms; includes the Aharonov-Bohm effect (quantum)",
    "M2/ch17": "graduate; its last subsections (currents, Clifford analysis) reach research level",
    "M2/ch19": "postdoc/research survey (geometric measure theory, discrete exterior calculus)",
}


def section_title(s, rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"\\(sub)?section\*?\{", text)
    if not m:
        return ""
    g = texscan.brace_groups(text, m.end() - 1, 1)
    return g[0] if g else ""


def md_inline(t):
    t = t.replace("\\`", "").replace("\\'", "")
    t = re.sub(r"\$([^$]*)\$", r"\1", t)
    t = t.replace("\\to", "->").replace("\\", "").replace("{", "").replace("}", "")
    return t.replace("|", "/")


def prereqs_from_main(code):
    with open(os.path.join(ROOT, FOLDER[code], MAINFILE[code]), encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    out, pending = {}, None
    for line in lines:
        m = re.match(r"\\chapterprereqs\{([^}]*)\}", line)
        if m:
            pending = [x for x in m.group(1).split(",") if x]
            continue
        m = re.match(r"\\input\{chapters/([^/}]+)/", line)
        if m and pending is not None:
            out[m.group(1)] = pending
            pending = None
    return out


def label_to_id(s, ids, lab):
    if lab not in s.labels:
        return lab
    key = s.chapter[s.labels[lab][0][0]]
    if key[1].startswith("00-part-"):
        return f"{key[0]} Part intro `{lab}`"
    return ids.get(key, f"{key[0]}/{key[1]}")


def link_id(cid):
    doc = cid.split("/")[0]
    return f"[{cid}](#{doc.lower()})" if doc in CONTENT_DOCS else cid


def chapter_rows(s, ids):
    rows = {}
    for code in CONTENT_DOCS:
        stated = prereqs_from_main(code)
        rows[code] = []
        for it in BODY[code]:
            kind = it[0]
            if kind == "todo":
                _, cid, title, level, pre = it
                rows[code].append(dict(id=f"{code}/{cid}", title=title, level=level,
                                       prereqs=pre, status=f"TODO({code}/{cid})", present=False, words=0))
            elif kind in ("chapter", "wrapped"):
                cid, folder, level = it[1], it[2], it[-1]
                path = f"{FOLDER[code]}/chapters/{folder}/"
                files = [f for f in s.files if s.chapter[f] == (code, folder)]
                words = sum(s.words[f] for f in files)
                if kind == "chapter":
                    title = md_inline(section_title(s, path + "00-section.tex"))
                else:
                    subs = [md_inline(section_title(s, path + f + ".tex")) for f in it[3]]
                    title = f"(no section heading: TODO({code}/{cid})) " + "; ".join(subs)
                pre = [label_to_id(s, ids, l) for l in stated.get(folder, [])]
                rows[code].append(dict(id=f"{code}/{cid}", title=title, level=level, prereqs=pre,
                                       status=f"present: [{path}]({path})", present=True, words=words,
                                       span=SPANS.get(f"{code}/{cid}", "")))
    return rows


def gen_chapter_org(s, ids, rows):
    out = ["# Chapter organization", "",
           "The reading order that takes each document from its entry level to its target level. This is the only "
           "syllabus in the repository; [ROADMAP.md](ROADMAP.md) links here and does not repeat it.", "",
           "- **Present** chapters are existing material, moved unchanged; the path is the chapter folder. "
           "Their prerequisites are the ones printed in the PDF (author-declared dependencies plus every earlier "
           "chapter the text refers back to).",
           "- **TODO** chapters are named steps with no content yet (`TODO(DOC/chNN)`). Naming them is organization; "
           "no chapter body has been written. Their prerequisites are planned.",
           "- Levels: basic, undergraduate, graduate, postdoc/research. A row gives the level that chapter reaches "
           "on the way to the target.",
           "- Generated by `tools/gen_docs.py` from `tools/structure_config.py`; edit the config, not this file.", "",
           "Documents: " + ", ".join(f"[{c}](#{c.lower()})" for c in CONTENT_DOCS) + ", [GLOSSARY](#glossary).", ""]
    parents = defaultdict(list)
    for a, b in DOC_EDGES:
        parents[b].append(a)
    for code, folder, title, entry, target in DOCS:
        r = rows[code]
        present = [x for x in r if x["present"]]
        out += [f'<a id="{code.lower()}"></a>', "", f"## {code} {title}", "",
                f"- Folder: [{folder}/]({folder}/) (root file `{MAINFILE[code]}`, PDF `build/{JOB[code]}.pdf`)",
                f"- Entry level: {entry}. Target level: {target}.",
                "- Finish first: " + (", ".join(f"[{p}](#{p.lower()})" for p in parents[code]) or "nothing (entry point of the series)")
                + (f" (transitively also {', '.join(sorted(ancestors(code) - set(parents[code])))})"
                   if ancestors(code) - set(parents[code]) else ""),
                f"- Chapters: {len(r)} planned, {len(present)} present, {len(r) - len(present)} TODO.", "",
                "| chapter | title | level reached | prerequisites | status |", "|---|---|---|---|---|"]
        for x in r:
            pre = "; ".join(link_id(p) if "/" in p and "`" not in p else p for p in x["prereqs"]) or "none"
            title = x["title"] + (f" *(note: {x['span']})*" if x.get("span") else "")
            out.append(f"| {x['id']} | {title} | {x['level']} | {pre} | {x['status']} |")
        last = r[-1]
        out += ["", f"Target level completed by: **{last['id']} {last['title']}** "
                    f"({'present' if last['present'] else 'TODO'}).", ""]
    out += ['<a id="glossary"></a>', "", "## GLOSSARY Global glossary, identities and bibliography", "",
            "Not a levelled course: it is consulted alongside every path above, not read as one. It owns all "
            "symbols (Part A), terms (Part B), identities with proofs (Part C) and the single bibliography. "
            "Folder: [GLOSSARY/](GLOSSARY/).", "",
            "Entries currently cover M1 and M2 topics only. Missing blocks: "
            + ", ".join(f"`TODO(GLOSSARY/{c})`" for c in GLOSSARY_TODO) + ".", ""]
    write("CHAPTER_ORGANIZATION.md", out)


def gen_ledger():
    with open(os.path.join(ROOT, "tools", "migration_map.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(os.path.join(ROOT, "tools", "migration_edits.csv"), encoding="utf-8") as fh:
        edits = list(csv.DictReader(fh))
    per = defaultdict(Counter)
    for e in edits:
        a = e["action"]
        per[e["new_path"]]["removed" if a.startswith("input-line") else "path"] += 1
    kinds = Counter(r["kind"] for r in rows)
    out = ["# Migration ledger", "",
           "Every file of the old single book `forms-tensors-ga/` (plus the root "
           "`forms_tensors_geometric_algebra_unified.tex`), with its new path. Generated by `tools/gen_docs.py` from "
           "`tools/migration_map.csv` (the map that `tools/restructure.py migrate` executed with `git mv`) and "
           "`tools/migration_edits.csv` (every line edit). Baseline commit: `1dde429`.", "",
           "Allowed edits in moved files are structural only, and `tools/check_integrity.py` verifies that each "
           "moved file equals its original once they are masked:", "",
           "- `%!TEX root` lines rewritten to the new root file;",
           "- `\\input{...}` paths rewritten relative to the document folder;",
           "- `\\input` lines of part hubs moved to the document's `main.tex` (chapter order lives there);",
           "- `\\input` lines removed where the target now belongs to another document (listed below);",
           "- one line `\\usepackage{xr-hyper}` added to `shared/preamble/packages.tex`;",
           "- `.gitignore` and `.cursor/rules/latex-project.mdc` updated for the new paths (configuration).", "",
           f"Totals: {len(rows)} files ({sum(r['tracked'] == 'yes' for r in rows)} tracked by git, "
           f"{sum(r['tracked'] == 'no' for r in rows)} untracked build outputs), {len(edits)} line edits.", "",
           "| kind | files |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in sorted(kinds.items())]
    out += ["", "## Input lines removed because the target moved to another document", "",
            "| file | removed line | target now |", "|---|---|---|"]
    for e in edits:
        if e["action"].startswith("input-line-removed"):
            tgt = e["action"][len("input-line-removed (target now "):-1]
            out.append(f"| `{e['new_path']}` | `{e['before'].strip()}` | `{tgt}` |")
    out += ["", "## All moved files", "",
            "| old path | new path | document | chapter | kind | git | words | path edits | input lines moved/removed |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        c = per.get(r["new_path"], Counter())
        out.append(f"| `{r['old_path']}` | `{r['new_path']}` | {r['document']} | {r['chapter']} | {r['kind']} | "
                   f"{'tracked' if r['tracked'] == 'yes' else 'untracked'} | {r['words']} | {c['path'] or ''} | {c['removed'] or ''} |")
    write("MIGRATION_LEDGER.md", out)


def gen_sources(s):
    path = os.path.join(ROOT, "GLOSSARY", "references", "references.tex")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    items = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})", text, re.S)
    citers = defaultdict(set)
    for f, n, k in s.cites:
        citers[k].add(s.files[f][0])
    out = ["# Sources index", "",
           "Registry of every source. Workflow for new sources:", "",
           "1. Put the file in the owning document's `sources/` folder (for example `QM-quantum-mechanics/sources/`). "
           "Sources that concern several documents go to the owner of the topic they mainly treat.",
           "2. Add a row below with status `unplaced`.",
           "3. Propose its placement in [ROADMAP.md](ROADMAP.md) (section \"Proposed source placements\"), naming the "
           "[CHAPTER_ORGANIZATION.md](CHAPTER_ORGANIZATION.md) row it would fill; status `proposed`.",
           "4. Only after approval: status `approved`; content is merged into chapters only when asked (`merged`).", "",
           "Status values: `unplaced`, `proposed`, `approved`, `merged`; `cited, no file` for bibliography entries "
           "already cited in the text whose file is not in the repository.", "",
           "## Registry", "",
           "| ID | file | document | proposed chapter | status | reference |", "|---|---|---|---|---|---|"]
    for key, body in items:
        ref = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", " ".join(body.split()))
        ref = ref.replace("~", " ").replace("--", "-").replace("\\&", "&").replace("{", "").replace("}", "")
        ref = re.sub(r"\\[a-zA-Z]+ ?", "", ref).replace("\\", "").replace("|", "/")
        docs = ", ".join(sorted(citers.get(key, []), key=lambda d: (CONTENT_DOCS + ["GLOSSARY", "Unsorted"]).index(d)))
        out.append(f"| {key} | none | cited by {docs or 'no document'} | - | cited, no file | {ref} |")
    out += ["", "## Source files", "", "No source files have been added yet. Each document has an empty `sources/` folder.", ""]
    write("sources_index.md", out)


def status_block(s, ids, rows):
    per = wordcount.counts()
    content = {d: per[d] for d in CONTENT_DOCS}
    mean = sum(content.values()) / len(content)
    out = ["| document | folder | words | vs mean | +/-15% band | chapters present / planned | highest level present | target |",
           "|---|---|---|---|---|---|---|---|"]
    for code, folder, title, entry, target in DOCS:
        r = rows[code]
        pres = [x for x in r if x["present"]]
        hi = max((x["level"] for x in pres), key=lambda l: LEVEL_RANK[l], default="none")
        w = content[code]
        band = "inside" if 0.85 * mean <= w <= 1.15 * mean else "outside"
        out.append(f"| {code} {title} | [{folder}/]({folder}/) | {w:,} | {100 * (w - mean) / mean:+.0f}% | {band} | "
                   f"{len(pres)} / {len(r)} | {hi} | {target} |")
    out += ["", f"Mean over the ten documents: {mean:,.0f} words; band {0.85 * mean:,.0f} to {1.15 * mean:,.0f}. "
                f"GLOSSARY: {per['GLOSSARY']:,} words (reference document, outside the balance rule). "
                f"Unsorted: {per['Unsorted']:,} words.", ""]
    m1, m2 = content["M1"], content["M2"]
    pair = (m1 + m2) / 2
    out += [f"M1 and M2 against their shared mean ({pair:,.0f}): M1 {100 * (m1 - pair) / pair:+.1f}%, "
            f"M2 {100 * (m2 - pair) / pair:+.1f}%.", ""]
    return out, content, mean


def forward_block(s, ids, order):
    c = Counter()
    for f, n, cmd, lab in s.refs:
        if lab not in s.labels or s.files[f][1] == MAINFILE[s.files[f][0]]:
            continue
        src, tgt = s.chapter[f], s.chapter[s.labels[lab][0][0]]
        if src[0] != tgt[0] and direction(src, tgt, order) == "forward":
            c[(ids.get(src, src[1]), ids.get(tgt, tgt[1]))] += 1
    out = ["| from chapter | refers forward to | refs |", "|---|---|---|"]
    out += [f"| {a} | {b} | {n} |" for (a, b), n in sorted(c.items())]
    return out


def gen_roadmap(s, ids, order, rows):
    status, content, mean = status_block(s, ids, rows)
    with open(os.path.join(ROOT, "tools", "ROADMAP.template.md"), encoding="utf-8") as fh:
        tpl = fh.read()
    mer = ["```mermaid", "flowchart LR"] + [f"  {a} --> {b}" for a, b in DOC_EDGES] + \
          ['  GLOSSARY -.-|"referenced by all"| M1', "```"]
    todo_counts = "\n".join(
        f"- **{code}**: " + ", ".join(f"`{x['status']}` {x['title']}" for x in rows[code] if not x["present"])
        for code in CONTENT_DOCS)
    text = (tpl.replace("{{STATUS}}", "\n".join(status))
               .replace("{{GRAPH}}", "\n".join(mer))
               .replace("{{FORWARD}}", "\n".join(forward_block(s, ids, order)))
               .replace("{{TODO}}", todo_counts))
    with open(os.path.join(ROOT, "ROADMAP.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write(name, lines):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def main():
    s = texscan.scan()
    order, ids = texscan.reading_order()
    rows = chapter_rows(s, ids)
    gen_ledger()
    gen_chapter_org(s, ids, rows)
    gen_sources(s)
    gen_roadmap(s, ids, order, rows)
    print("wrote MIGRATION_LEDGER.md, CHAPTER_ORGANIZATION.md, sources_index.md, ROADMAP.md")


if __name__ == "__main__":
    main()
