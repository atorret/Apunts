"""Finished eleven-document migration. Kept for the record; do not re-run it.

Chapter folders are changed with `python UI.py layout`.
"""
import csv
import os
import re
import shutil
import subprocess
import sys

if __name__ == "__main__":
    sys.exit("tools/legacy/restructure.py already ran. Change chapter folders with: python UI.py layout")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
from structure_config import (OLD, DOCS, CONTENT_DOCS, FOLDER, TITLE, MAINFILE, JOB, BODY,
                              CHAPTER_DIRS, FILE_RULES, DIR_RULES, ROOT_BUILD_OUTPUTS, EXTRA_RULES,
                              GLOSSARY_TODO, ancestors)
import texscan

ROOT = texscan.ROOT
MAP_CSV = os.path.join(ROOT, "tools", "migration_map.csv")
EDITS_CSV = os.path.join(ROOT, "tools", "migration_edits.csv")
FIELDS = ["old_path", "new_path", "document", "chapter", "kind", "tracked", "words"]


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, check=check, capture_output=True, text=True,
                          encoding="utf-8").stdout


def tracked_files():
    return set(git("ls-files").splitlines())


def target_for(old_rel):
    """old path relative to OLD -> new path relative to ROOT."""
    for old, new in FILE_RULES:
        if old_rel == old:
            return new
    for prefix, doc, ch in CHAPTER_DIRS:
        if old_rel.startswith(prefix):
            rest = old_rel[len(prefix):]
            if rest == "exercises.tex":
                return f"{FOLDER[doc]}/exercises/{ch}.tex"
            return f"{FOLDER[doc]}/chapters/{ch}/{rest}"
    for prefix, newprefix in DIR_RULES:
        if old_rel.startswith(prefix):
            return newprefix + old_rel[len(prefix):]
    if old_rel in ROOT_BUILD_OUTPUTS:
        return "unsorted/legacy-build/" + old_rel
    return None


def classify(new):
    parts = new.split("/")
    folder_doc = {v: k for k, v in FOLDER.items()}
    doc = folder_doc.get(parts[0], "infra")
    chapter, kind = "", "infra"
    if doc in CONTENT_DOCS:
        if parts[1] == "chapters":
            chapter = parts[2] if len(parts) > 3 else parts[2][:-4]
            kind = "part-hub" if chapter.startswith("00-part") else "chapter"
        elif parts[1] == "exercises":
            chapter, kind = parts[2][:-4], "exercises"
        elif parts[1] == "figures":
            kind = "figure"
    elif doc == "GLOSSARY":
        kind = "notes" if parts[1] == "notes" else ("bibliography" if parts[1] == "references" else "glossary")
        chapter = parts[1] if len(parts) > 2 else ""
    elif doc == "Unsorted":
        kind = {"legacy": "legacy", "legacy-build": "legacy-build", "project-docs": "project-docs"}.get(parts[1], "unsorted-content")
        chapter = parts[1]
    return doc, chapter, kind


def words_of(path):
    if not path.endswith(".tex"):
        return ""
    with open(path, encoding="utf-8", errors="replace") as fh:
        return str(len(fh.read().split()))


def cmd_map():
    tracked = tracked_files()
    rows, unmapped = [], []
    base = os.path.join(ROOT, OLD)
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            old_rel = os.path.relpath(full, base).replace("\\", "/")
            new = target_for(old_rel)
            if new is None:
                unmapped.append(old_rel)
                continue
            old = f"{OLD}/{old_rel}"
            doc, ch, kind = classify(new)
            rows.append([old, new, doc, ch, kind, "yes" if old in tracked else "no", words_of(full)])
    for old, new in EXTRA_RULES:
        doc, ch, kind = classify(new)
        rows.append([old, new, doc, ch, kind, "yes" if old in tracked else "no", words_of(os.path.join(ROOT, old))])
    if unmapped:
        sys.exit("unmapped files:\n  " + "\n  ".join(unmapped))
    news = [r[1] for r in rows]
    dup = {n for n in news if news.count(n) > 1}
    if dup:
        sys.exit(f"duplicate targets: {dup}")
    rows.sort(key=lambda r: r[0])
    with open(MAP_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(FIELDS)
        w.writerows(rows)
    print(f"{len(rows)} files mapped ({sum(r[5] == 'yes' for r in rows)} tracked) -> {MAP_CSV}")


def read_map():
    with open(MAP_CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def doc_root_of(new):
    """(doc code, doc folder, main file) for files whose paths get rewritten, else None."""
    parts = new.split("/")
    if not new.endswith(".tex"):
        return None
    if parts[0] == "shared":
        return ("M1", FOLDER["M1"], MAINFILE["M1"])
    folder_doc = {v: k for k, v in FOLDER.items()}
    doc = folder_doc.get(parts[0])
    if doc is None:
        return None
    if doc == "Unsorted" and parts[1] not in ("frontmatter", "thermodynamics"):
        return None
    return (doc, FOLDER[doc], MAINFILE[doc])


RE_INPUT_LINE = re.compile(r"^(\s*)\\input\{([^}]+)\}(\s*(%.*)?)$")
RE_ROOT_LINE = re.compile(r"^%!TEX root = (.+)$")


def cmd_migrate():
    rows = read_map()
    tracked = tracked_files()
    old2new = {r["old_path"]: r["new_path"] for r in rows}
    for r in rows:
        src, dst = os.path.join(ROOT, r["old_path"]), os.path.join(ROOT, r["new_path"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if r["old_path"] in tracked:
            git("mv", r["old_path"], r["new_path"])
        else:
            shutil.move(src, dst)
    edits = []
    for r in rows:
        info = doc_root_of(r["new_path"])
        if info is None:
            continue
        doc, folder, main = info
        path = os.path.join(ROOT, r["new_path"])
        with open(path, encoding="utf-8", newline="") as fh:
            text = fh.read()
        nl = "\r\n" if "\r\n" in text else "\n"
        lines = text.split(nl)
        out = []
        is_part_hub = "/chapters/00-part-" in r["new_path"]
        for n, line in enumerate(lines, 1):
            m = RE_ROOT_LINE.match(line)
            if m:
                rootpath = os.path.relpath(os.path.join(ROOT, folder, main),
                                           os.path.dirname(path)).replace("\\", "/")
                new_line = f"%!TEX root = {rootpath}"
                if new_line != line:
                    edits.append([r["new_path"], n, "tex-root-path", line, new_line])
                out.append(new_line)
                continue
            m = RE_INPUT_LINE.match(line)
            if m:
                tgt_old = f"{OLD}/{m.group(2)}" + ("" if m.group(2).endswith(".tex") else ".tex")
                tgt_new = old2new.get(tgt_old)
                if tgt_new is None:
                    sys.exit(f"{r['new_path']}:{n}: input target not in map: {tgt_old}")
                tgt_doc = doc_root_of(tgt_new)
                if is_part_hub:
                    edits.append([r["new_path"], n, "input-line-moved-to-main.tex", line, ""])
                    continue
                if tgt_doc is None or tgt_doc[0] != doc:
                    edits.append([r["new_path"], n, f"input-line-removed (target now {tgt_new})", line, ""])
                    continue
                rel = os.path.relpath(os.path.join(ROOT, tgt_new), os.path.join(ROOT, folder))
                rel = rel.replace("\\", "/")[:-4]
                new_line = f"{m.group(1)}\\input{{{rel}}}{m.group(3)}"
                if new_line != line:
                    edits.append([r["new_path"], n, "input-path", line, new_line])
                out.append(new_line)
                continue
            out.append(line)
        new_text = nl.join(out)
        if new_text != text:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_text)
    with open(EDITS_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["new_path", "old_line_no", "action", "before", "after"])
        w.writerows(edits)
    old_dir = os.path.join(ROOT, OLD)
    for dirpath, dirnames, filenames in os.walk(old_dir, topdown=False):
        if not os.listdir(dirpath):
            os.rmdir(dirpath)
    if os.path.isdir(old_dir):
        left = [os.path.join(dp, f) for dp, _, fs in os.walk(old_dir) for f in fs]
        sys.exit(f"files left behind in {OLD}: {left}")
    print(f"moved {len(rows)} files, {len(edits)} path edits -> {EDITS_CSV}")


# ---------------------------------------------------------------------------
# scaffolding
# ---------------------------------------------------------------------------
LATEXMKRC = """# latexmk configuration for {code}: pdflatex, output in build/{job}.pdf
$pdf_mode = 1;
$out_dir = 'build';
$jobname = '{job}';
$pdflatex = 'pdflatex -interaction=nonstopmode -file-line-error -synctex=1 %O %S';
$max_repeat = 6;
@default_files = ('{main}');
"""

PREAMBLE = r"""\documentclass[11pt,a4paper]{{article}}

\input{{../shared/preamble/packages}}
\input{{../shared/preamble/colors}}
\input{{../shared/preamble/layout}}
\input{{../shared/preamble/environments}}
\input{{../shared/preamble/macros-general}}
\input{{../shared/preamble/macros-geometry}}
\input{{../shared/preamble/macros-algebra}}
\input{{../shared/preamble/macros-structure}}

\renewcommand{{\runningtitle}}{{{code} {title}}}
\hypersetup{{pdftitle={{{code} {title}}}}}
"""


def externals(code):
    lines = []
    for other in [d[0] for d in DOCS] + ["GLOSSARY", "Unsorted"]:
        if other == code:
            continue
        f, j = FOLDER[other], JOB[other]
        lines.append(f"\\externaldocument[][nocite]{{../{f}/build/{j}}}[../../{f}/build/{j}.pdf]")
    return "\n".join(lines)


def header(code):
    return (f"% {code} {TITLE[code]} | root file | build: latexmk (see latexmkrc), output build/{JOB[code]}.pdf\n"
            f"% Generated by tools/restructure.py scaffold from tools/structure_config.py.\n"
            f"\\def\\thisdoc{{{code}}}\n")


def tex_escape(s):
    return s.replace("&", r"\&").replace("_", r"\_").replace("#", r"\#")


def present_anchors(s, order, ids):
    """chapter id (e.g. 'M1/ch06') -> anchor label, for chapters that exist."""
    out = {}
    for key, cid in ids.items():
        if key[1].startswith("TODO-"):
            continue
        a = texscan.chapter_anchor(s, key)
        if a:
            out[cid] = a
    return out


def chapter_prereqs(s, key, order):
    doc = key[0]
    files = [f for f in s.files if s.chapter[f] == key]
    found = set()
    for f in files:
        for lab in s.deps.get(f, []):
            if lab in s.labels:
                found.add(s.chapter[s.labels[lab][0][0]])
    anc = ancestors(doc)
    for f, n, cmd, lab in s.refs:
        if f not in files or lab not in s.labels:
            continue
        k = s.chapter[s.labels[lab][0][0]]
        if k == key or k[0] in ("GLOSSARY", "Unsorted"):
            continue
        if (k[0] == doc and order.get(k, 10 ** 9) < order[key]) or k[0] in anc:
            found.add(k)
    found.discard(key)
    found = {k for k in found if k[0] not in ("GLOSSARY", "Unsorted")}
    return sorted(found, key=lambda k: order.get(k, 10 ** 9))


def render_ids(idlist, anchors):
    parts = []
    for cid in idlist:
        if cid in anchors:
            parts.append(f"\\ref{{{anchors[cid]}}}~(\\nameref{{{anchors[cid]}}})")
        else:
            parts.append(f"TODO({cid})")
    return "; ".join(parts) if parts else "none"


def body_lines(code, s, order, ids, anchors):
    out = []
    for it in BODY[code]:
        kind = it[0]
        if kind == "todo":
            _, cid, title, level, pre = it
            out.append(f"\\missingchapter{{{code}/{cid}}}{{{tex_escape(title)}}}{{{render_ids(pre, anchors)}}}")
        elif kind == "todopart":
            out.append(f"\\todopart{{{it[1]}}}")
        elif kind == "part":
            out.append(f"\\input{{{it[1]}}}")
        elif kind == "chapter":
            _, cid, folder, level = it
            pre = [texscan.chapter_anchor(s, k) for k in chapter_prereqs(s, (code, folder), order)]
            out.append(f"\\chapterprereqs{{{','.join(p for p in pre if p)}}}")
            out.append(f"\\input{{chapters/{folder}/00-section}}")
        elif kind == "wrapped":
            _, cid, folder, files, level = it
            pre = [texscan.chapter_anchor(s, k) for k in chapter_prereqs(s, (code, folder), order)]
            out.append(f"\\chapterprereqs{{{','.join(p for p in pre if p)}}}")
            out.append(f"\\todoheading{{{code}/{cid}}}")
            for f in files:
                out.append(f"\\input{{chapters/{folder}/{f}}}")
        elif kind == "extra":
            out.append(f"\\input{{{it[1]}}}")
    return out


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def gitkeep(d):
    os.makedirs(d, exist_ok=True)
    if not [f for f in os.listdir(d) if f != ".gitkeep"]:
        write(os.path.join(d, ".gitkeep"), "")


def cmd_scaffold():
    sys.exit("scaffold no longer writes main.tex; chapter order comes from library.sqlite (python UI.py layout)")
    s = texscan.scan()
    order, ids = texscan.reading_order()
    anchors = present_anchors(s, order, ids)
    for code, folder, title, entry, target in DOCS:
        base = os.path.join(ROOT, folder)
        for sub in ("chapters", "exercises", "figures", "sources", "backmatter"):
            gitkeep(os.path.join(base, sub))
        write(os.path.join(base, "latexmkrc"), LATEXMKRC.format(code=code, job=JOB[code], main=MAINFILE[code]))
        doc = [header(code), PREAMBLE.format(code=code, title=title), externals(code), "",
               r"\begin{document}", "",
               f"\\doctitle{{{code}}}{{{title}}}{{{entry}}}{{{target}}}", "",
               r"\vspace{0.8em}", r"\tableofcontents", r"\clearpage", ""]
        doc += body_lines(code, s, order, ids, anchors)
        doc += ["", r"\globalbibliography", "", r"\end{document}", ""]
        write(os.path.join(base, MAINFILE[code]), "\n".join(doc))
    # GLOSSARY
    g = os.path.join(ROOT, "GLOSSARY")
    gitkeep(os.path.join(g, "sources"))
    write(os.path.join(g, "latexmkrc"), LATEXMKRC.format(code="GLOSSARY", job="GLOSSARY", main="main.tex"))
    todo = [f"\\missingglossary{{GLOSSARY/{c}}}{{Entries for {c} {TITLE[c]}}}" for c in GLOSSARY_TODO]
    gdoc = [header("GLOSSARY"), PREAMBLE.format(code="GLOSSARY", title=TITLE["GLOSSARY"]), externals("GLOSSARY"), "",
            r"\begin{document}", "",
            r"\doctitle{GLOSSARY}{" + TITLE["GLOSSARY"] + r"}{all documents}{all documents}", "",
            r"\vspace{0.8em}", r"\tableofcontents", r"\clearpage", "",
            r"\input{00-glossary}", ""] + todo + ["", r"\input{references/references}", "", r"\end{document}", ""]
    write(os.path.join(g, "main.tex"), "\n".join(gdoc))
    # unsorted holder
    u = os.path.join(ROOT, "unsorted")
    write(os.path.join(u, "latexmkrc"), LATEXMKRC.format(code="Unsorted", job="UNSORTED", main="UNSORTED.tex"))
    udoc = [header("Unsorted"), PREAMBLE.format(code="Unsorted", title=TITLE["Unsorted"]), externals("Unsorted"), "",
            r"\begin{document}", "",
            r"\doctitle{Unsorted}{Material that fits no document}{--}{--}", "",
            r"\vspace{0.8em}", r"\tableofcontents", r"\clearpage", "",
            r"\input{frontmatter/title}", r"\input{frontmatter/abstract}", r"\input{frontmatter/reading-guide}",
            r"\clearpage", "",
            r"\todoheading{Unsorted/thermodynamics}", r"\input{thermodynamics/05-thermodynamics}", "",
            r"\globalbibliography", "", r"\end{document}", ""]
    write(os.path.join(u, "UNSORTED.tex"), "\n".join(udoc))
    print("scaffold written")


