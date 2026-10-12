"""Plan and apply the folder layout."""

import csv
import io
import os
import re
import subprocess

from base import (
    DOCUMENTS,
    LibraryError,
    TABLES,
    chapter_number,
    folder_slug,
    read_text,
    write_text,
)
from exchange import (
    _rows,
)

def snapshot(conn):
    """Stable tuples of every table, for round-trip checks."""
    out = []
    for name, cols in TABLES.items():
        rows = _rows(conn, f"SELECT {', '.join(cols)} FROM {name}")
        packed = [tuple("" if row[c] is None else row[c] for c in cols) for row in rows]
        out.append((name, tuple(sorted(packed))))
    return tuple(out)


# --- layout --------------------------------------------------------------

def _chapter_dirs(root):
    found = []
    for _code, folder, _job in DOCUMENTS:
        chapters = os.path.join(root, folder, "chapters")
        if not os.path.isdir(chapters):
            continue
        for name in os.listdir(chapters):
            if folder_slug(name) and os.path.isdir(os.path.join(chapters, name)):
                found.append((folder, name, os.path.join(folder, "chapters", name).replace("\\", "/")))
    return found


def plan_moves(root, conn):
    dirs = _chapter_dirs(root)
    by_slug = {}
    for folder, name, rel in dirs:
        slug = folder_slug(name)
        by_slug.setdefault(slug, []).append((folder, name, rel))
    moves = []
    problems = []
    rows = _rows(conn, "SELECT id, book, path, presence FROM chapters WHERE presence = 'present'")
    for row in rows:
        if not row["path"]:
            problems.append(f"{row['id']} is present but has no path")
            continue
        target = row["path"].replace("\\", "/").rstrip("/")
        target_dir = os.path.basename(target)
        slug = folder_slug(target_dir)
        if slug is None:
            problems.append(f"{row['id']} path {target} is not a chapter folder")
            continue
        full = os.path.join(root, target.replace("/", os.sep))
        if os.path.isdir(full):
            continue
        matches = by_slug.get(slug, [])
        if len(matches) != 1:
            problems.append(
                f"{row['id']} needs {target}, and slug {slug} matches {len(matches)} folders"
            )
            continue
        src_folder, src_name, src_rel = matches[0]
        if os.path.isdir(full):
            problems.append(f"destination exists and is not the source: {target}")
            continue
        moves.append({
            "id": row["id"],
            "book": row["book"],
            "slug": slug,
            "src": src_rel,
            "dst": target,
            "src_name": src_name,
            "dst_name": target_dir,
        })
    if problems:
        raise LibraryError("layout stopped:\n" + "\n".join(problems))
    # destinations must not collide with each other or with an unmoved folder
    dests = [m["dst"] for m in moves]
    if len(dests) != len(set(dests)):
        raise LibraryError("two chapters would move to the same folder")
    return moves


def _newline(text):
    return "\r\n" if "\r\n" in text else "\n"


def _chapter_block_bounds(text):
    clear = text.find("\\clearpage")
    end = text.find("\\globalbibliography")
    if clear < 0 or end < 0 or end < clear:
        raise LibraryError("main.tex has no chapter block between \\clearpage and \\globalbibliography")
    return clear + len("\\clearpage"), end


def _parse_block_events(block):
    events = []
    for line in block.splitlines():
        stripped = line.strip()
        part = re.match(r"\\input\{chapters/(00-part-[\w-]+)\}", stripped)
        if part:
            events.append(("part", stripped))
            continue
        if stripped.startswith("\\chapterprereqs"):
            events.append(("prereq", stripped))
            continue
        chapter = re.match(r"\\input\{chapters/(ch\d+-[\w-]+)/(.+)\}", stripped)
        if chapter:
            kind = "section" if chapter.group(2).startswith("00-section") else "extra"
            events.append((kind, folder_slug(chapter.group(1)), stripped))
    return events


def _attachments(root, moves):
    """Parts stay in the book they were read in. Prerequisite lines follow the chapter."""
    moved = {m["slug"]: m for m in moves}
    part_before = {}
    prereq_before = {}
    extras = {}
    trailers = {}
    for code, folder, _job in DOCUMENTS:
        path = os.path.join(root, folder, "main.tex")
        if not os.path.isfile(path):
            continue
        text = read_text(path)
        try:
            start, end = _chapter_block_bounds(text)
        except LibraryError:
            continue
        pending_parts = []
        pending_prereqs = []
        for kind, *rest in _parse_block_events(text[start:end]):
            if kind == "part":
                pending_parts.append(rest[0])
            elif kind == "prereq":
                pending_prereqs.append(rest[0])
            elif kind == "section":
                slug = rest[0]
                dest_book = moved[slug]["book"] if slug in moved else code
                prereq_before.setdefault(slug, []).extend(pending_prereqs)
                pending_prereqs = []
                if dest_book == code:
                    part_before.setdefault(slug, []).extend(pending_parts)
                    pending_parts = []
            elif kind == "extra":
                extras.setdefault(rest[0], []).append(rest[1])
        if pending_parts:
            trailers.setdefault(code, []).extend(pending_parts)
    return part_before, prereq_before, extras, trailers


def _prereq_macro(conn, chapter_id):
    rows = _rows(conn, "SELECT target, kind FROM prereqs WHERE chapter = ? ORDER BY target", (chapter_id,))
    if not rows:
        return "none"
    bits = []
    for row in rows:
        label = f"TODO({row['target']})" if "/part:" not in row["target"] else row["target"]
        if row["kind"] == "optional":
            label += " (opt.)"
        bits.append(label)
    return "; ".join(bits)


def _render_book_body(conn, code, part_before, prereq_before, extras, trailers, nl):
    chapters = _rows(
        conn,
        "SELECT * FROM chapters WHERE book = ? AND presence != 'retired' ORDER BY id",
        (code,),
    )
    chapters.sort(key=lambda ch: chapter_number(ch["id"]))
    lines = []
    for ch in chapters:
        if ch["presence"] == "present" and ch["path"]:
            slug = folder_slug(os.path.basename(ch["path"].rstrip("/")))
            dirname = os.path.basename(ch["path"].rstrip("/"))
            for line in part_before.get(slug, []):
                lines.append(line)
            for line in prereq_before.get(slug, []):
                lines.append(line)
            lines.append(f"\\input{{chapters/{dirname}/00-section}}")
            for line in extras.get(slug, []):
                rewritten = re.sub(r"chapters/ch\d+-" + re.escape(slug), f"chapters/{dirname}", line)
                if rewritten not in lines:
                    lines.append(rewritten)
        else:
            title = ch["title"].replace("{", "\\{").replace("}", "\\}")
            lines.append(f"\\missingchapter{{{ch['id']}}}{{{title}}}{{{_prereq_macro(conn, ch['id'])}}}")
    for line in trailers.get(code, []):
        lines.append(line)
    return nl.join(lines)


def _external_line(folder, job):
    return (
        f"\\externaldocument[][nocite]{{../{folder}/build/{job}}}"
        f"[../../{folder}/build/{job}.pdf]"
    )


def _ensure_externals(text, code):
    additions = []
    for other, folder, job in DOCUMENTS:
        if other == code:
            continue
        line = _external_line(folder, job)
        if line not in text and f"../{folder}/build/{job}" not in text:
            additions.append(line)
    if not additions:
        return text, []
    marker = "\\begin{document}"
    at = text.find(marker)
    if at < 0:
        return text, []
    nl = _newline(text)
    block = nl.join(additions) + nl
    return text[:at] + block + text[at:], additions


def _new_main(code, title, entry, target, body, nl):
    externals = [_external_line(folder, job) for other, folder, job in DOCUMENTS if other != code]
    lines = [
        f"% {code} {title} | root file | build: latexmk (see latexmkrc), output build/{code}.pdf",
        "% Generated from library.sqlite by python UI.py layout.",
        f"\\def\\thisdoc{{{code}}}",
        "",
        "\\documentclass[11pt,a4paper]{article}",
        "",
        "\\input{../shared/preamble/packages}",
        "\\input{../shared/preamble/colors}",
        "\\input{../shared/preamble/layout}",
        "\\input{../shared/preamble/environments}",
        "\\input{../shared/preamble/macros-general}",
        "\\input{../shared/preamble/macros-geometry}",
        "\\input{../shared/preamble/macros-algebra}",
        "\\input{../shared/preamble/macros-structure}",
        "",
        f"\\renewcommand{{\\runningtitle}}{{{code} {title}}}",
        f"\\hypersetup{{pdftitle={{{code} {title}}}}}",
        "",
        *externals,
        "",
        "\\begin{document}",
        "",
        f"\\doctitle{{{code}}}{{{title}}}{{{entry}}}{{{target}}}",
        "",
        "\\vspace{0.8em}",
        "\\tableofcontents",
        "\\clearpage",
        body,
        "",
        "\\globalbibliography",
        "",
        "\\end{document}",
        "",
    ]
    return nl.join(lines)


def _latexmkrc(code):
    return (
        f"# latexmk configuration for {code}: pdflatex, output in build/{code}.pdf\n"
        "$pdf_mode = 1;\n"
        "$out_dir = 'build';\n"
        f"$jobname = '{code}';\n"
        "$pdflatex = 'pdflatex -interaction=nonstopmode -file-line-error -synctex=1 %O %S';\n"
        "$max_repeat = 6;\n"
        "@default_files = ('main.tex');\n"
    )


def layout_actions(root, conn):
    moves = plan_moves(root, conn)
    actions = []
    for code, folder, _job in DOCUMENTS:
        if code in ("GLOSSARY", "unsorted"):
            continue
        base = os.path.join(root, folder)
        if not os.path.isdir(base):
            actions.append(("mkdir", folder))
    for move in moves:
        actions.append(("git-mv", move["src"], move["dst"]))
    actions.append(("rewrite-mains", str(len(moves))))
    actions.append(("externals", "M0, EM, TH"))
    actions.append(("migration-map", str(len(moves))))
    return moves, actions


def _rewrite_inputs(root, moves):
    """Point \\input lines at the new chapter folder names. Returns edit records."""
    edits = []
    if not moves:
        return edits
    replacements = [(m["src_name"], m["dst_name"]) for m in moves]
    skip = {".git", "build", "UI", "legacy", "legacy-build"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in skip]
        for filename in filenames:
            if not filename.endswith(".tex"):
                continue
            path = os.path.join(dirpath, filename)
            text = read_text(path)
            pieces = []
            changed = False
            for line in text.splitlines(keepends=True):
                updated = line
                if "\\input" in line:
                    for old, new in replacements:
                        updated = updated.replace(f"chapters/{old}/", f"chapters/{new}/")
                if updated != line:
                    changed = True
                pieces.append(updated)
            if not changed:
                continue
            new_text = "".join(pieces)
            rel = os.path.relpath(path, root).replace("\\", "/")
            for number, (before, after) in enumerate(zip(text.splitlines(), new_text.splitlines()), start=1):
                if before != after and "\\input" in before:
                    edits.append((rel, number, "input-path", before.strip(), after.strip()))
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_text)
    return edits


def _update_migration_map(root, moves):
    path = os.path.join(root, "tools", "migration_map.csv")
    if not os.path.isfile(path) or not moves:
        return
    text = read_text(path)
    for move in moves:
        old_folder = move["src"].split("/")[0]
        src_code = next((code for code, folder, _job in DOCUMENTS if folder == old_folder), None)
        text = text.replace(move["src"] + "/", move["dst"] + "/")
        text = text.replace(f",{move['src_name']},", f",{move['dst_name']},")
        if src_code and src_code != move["book"]:
            text = text.replace(f",{src_code},{move['dst_name']},", f",{move['book']},{move['dst_name']},")
    if not text.endswith("\n"):
        text += "\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _append_edits(root, edits):
    if not edits:
        return
    path = os.path.join(root, "tools", "migration_edits.csv")
    existing = read_text(path) if os.path.isfile(path) else "new_path,old_line_no,action,before,after\n"
    if not existing.endswith("\n"):
        existing += "\n"
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    for rel, number, action, before, after in edits:
        writer.writerow([rel, number, action, before, after])
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(existing + buf.getvalue())


def apply_layout(root, conn, apply):
    moves, actions = layout_actions(root, conn)
    report = ["layout plan:"]
    for action in actions:
        report.append("  " + " ".join(action))
    for move in moves:
        report.append(f"  move {move['id']}: {move['src']} -> {move['dst']}")
    if not apply:
        report.append("dry-run only; pass --apply to change files")
        return "\n".join(report)
    for code, folder, _job in DOCUMENTS:
        if code in ("GLOSSARY", "unsorted"):
            continue
        base = os.path.join(root, folder)
        if os.path.isdir(base):
            continue
        for sub in ("chapters", "exercises", "figures", "sources", "backmatter"):
            os.makedirs(os.path.join(base, sub), exist_ok=True)
            write_text(os.path.join(base, sub, ".gitkeep"), "")
        write_text(os.path.join(base, "latexmkrc"), _latexmkrc(code))
    for move in moves:
        src = os.path.join(root, move["src"].replace("/", os.sep))
        dst = os.path.join(root, move["dst"].replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        subprocess.run(["git", "mv", src, dst], cwd=root, check=True)
    input_edits = _rewrite_inputs(root, moves)
    part_before, prereq_before, extras, trailers = _attachments(root, moves)
    external_edits = []
    for code, folder, _job in DOCUMENTS:
        if code == "unsorted":
            main_name = "UNSORTED.tex"
            main_path = os.path.join(root, folder, main_name)
        else:
            main_name = "main.tex"
            main_path = os.path.join(root, folder, main_name)
        book = conn.execute("SELECT * FROM books WHERE code = ?", (code,)).fetchone()
        if code not in ("GLOSSARY", "unsorted"):
            nl = "\n"
            body = _render_book_body(conn, code, part_before, prereq_before, extras, trailers, nl)
            if os.path.isfile(main_path):
                text = read_text(main_path)
                nl = _newline(text)
                body = _render_book_body(conn, code, part_before, prereq_before, extras, trailers, nl)
                start, end = _chapter_block_bounds(text)
                text = text[:start] + nl + body + nl + text[end:]
            else:
                title = book["title"] if book else code
                entry = book["entry_level"] if book else ""
                target = book["target_level"] if book else ""
                text = _new_main(code, title, entry, target, body, nl)
            text, added = _ensure_externals(text, code)
            for line in added:
                external_edits.append((f"{folder}/{main_name}", 0, "externaldocument", "", line))
            if not text.endswith("\n") and not text.endswith("\r\n"):
                text += nl
            with open(main_path, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
        elif os.path.isfile(main_path):
            text = read_text(main_path)
            text, added = _ensure_externals(text, code)
            for line in added:
                external_edits.append((f"{folder}/{main_name}", 0, "externaldocument", "", line))
            with open(main_path, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
    _update_migration_map(root, moves)
    _append_edits(root, input_edits + external_edits)
    report.append("applied")
    return "\n".join(report)


__all__ = [name for name in globals() if not name.startswith('__')]
