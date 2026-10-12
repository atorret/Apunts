"""Scan LaTeX files and render the cross-reference report."""

import os
import re

from base import (
    BOOK_ORDER,
    DOCUMENTS,
    FOLDER_OF,
    LibraryError,
    ensure_source_tables,
    ensure_xref_tables,
    read_text,
)
from exchange import (
    _rows,
)

_XREF_SKIP_DIRS = {"build", "sources", "notes", "legacy", "legacy-build", "project-docs"}
_XREF_LABEL = re.compile(r"\\label\{([^}]+)\}")
_XREF_REF = re.compile(r"\\(ref|eqref|pageref|nameref)\{([^}]+)\}")
_XREF_CITE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}")
_XREF_BIBITEM = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}")
_XREF_INPUT = re.compile(r"\\input\{([^}]+)\}")
_XREF_LOG_PATTERNS = [
    ("undefined reference", re.compile(r"Reference `[^']+' on page \d+ undefined|There were undefined references")),
    ("multiply defined label", re.compile(r"multiply defined")),
    ("labels may have changed", re.compile(r"Label\(s\) may have changed")),
    ("missing external .aux", re.compile(r"^No file .*\.aux", re.M)),
    ("undefined citation", re.compile(r"Citation `[^']+' on page \d+ undefined")),
    ("missing link destination", re.compile(r"has been referenced but does not exist")),
]


def _tex_strip_comment(line):
    out = []
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if line[i] == "%":
            break
        out.append(line[i])
        i += 1
    return "".join(out)


def _tex_brace_groups(text, start, count):
    groups = []
    i = start
    while len(groups) < count and i < len(text):
        while i < len(text) and text[i] in " \t\r\n":
            i += 1
        if i >= len(text) or text[i] != "{":
            return None
        depth, j = 0, i
        while j < len(text):
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        groups.append(text[i + 1:j])
        i = j + 1
    return groups if len(groups) == count else None


def _xref_doc_label(code):
    return "Unsorted" if code == "unsorted" else code


def _xref_documents(conn, root):
    """Books that have a folder on disk, in reading order, then unsorted."""
    by_code = {}
    for row in _rows(conn, "SELECT code, folder FROM books"):
        folder = (row["folder"] or FOLDER_OF.get(row["code"], "")).strip().strip("/\\")
        if folder:
            by_code[row["code"]] = folder
    if "unsorted" not in by_code and os.path.isdir(os.path.join(root, "unsorted")):
        by_code["unsorted"] = "unsorted"
    codes = [code for code in BOOK_ORDER if code in by_code]
    codes.extend(sorted(code for code in by_code if code not in codes and code != "unsorted"))
    if "unsorted" in by_code:
        codes.append("unsorted")
    jobs = {code: job for code, _folder, job in DOCUMENTS}
    docs = []
    for code in codes:
        folder = by_code[code]
        if not os.path.isdir(os.path.join(root, folder)):
            continue
        docs.append({
            "code": code,
            "folder": folder,
            "job": jobs.get(code, "UNSORTED" if code == "unsorted" else code),
            "main": "UNSORTED.tex" if code == "unsorted" else "main.tex",
        })
    return docs


def _xref_chapter_key(doc, relative):
    parts = relative.replace("\\", "/").split("/")
    if doc == "GLOSSARY":
        return "glossary"
    if doc == "unsorted":
        if len(parts) > 1:
            return parts[0]
        name = parts[0]
        return name[:-4] if name.endswith(".tex") else name
    if parts[0] == "chapters" and len(parts) >= 2:
        name = parts[1]
        return name[:-4] if name.endswith(".tex") else name
    if parts[0] == "exercises" and len(parts) >= 2:
        name = parts[1]
        return name[:-4] if name.endswith(".tex") else name
    return None


def _xref_chapter_ids(conn):
    """Map (book, chapter folder name) to the chapter id stored in the library."""
    found = {}
    for row in _rows(conn, "SELECT id, book, path FROM chapters"):
        path = (row["path"] or "").replace("\\", "/").strip("/")
        if not path:
            continue
        found[(row["book"], os.path.basename(path))] = row["id"]
    return found


def _xref_ancestors(conn):
    requires = {}
    for row in _rows(conn, "SELECT book, requires FROM book_requires"):
        requires.setdefault(row["book"], set()).add(row["requires"])
    cache = {}

    def ancestors(doc):
        if doc in cache:
            return cache[doc]
        seen = set()
        stack = list(requires.get(doc, ()))
        while stack:
            current = stack.pop()
            if current in seen or current == doc:
                continue
            seen.add(current)
            stack.extend(requires.get(current, ()))
        cache[doc] = seen
        return seen

    return ancestors


def _xref_direction(src_doc, src_key, tgt_doc, tgt_key, order, ancestors):
    if src_doc in ("GLOSSARY", "unsorted") or tgt_doc in ("GLOSSARY", "unsorted"):
        return "reference"
    if src_doc == tgt_doc:
        src_at = order.get((src_doc, src_key), 10**9)
        tgt_at = order.get((tgt_doc, tgt_key), 10**9)
        return "back" if tgt_at < src_at else "forward"
    if tgt_doc in ancestors(src_doc):
        return "back"
    return "forward"


def _xref_display_id(doc, key, chapter_ids):
    stored = chapter_ids.get((doc, key))
    if stored:
        return stored
    return f"{_xref_doc_label(doc)}/{key}"


def scan_cross_references(root, conn):
    """Replace the stored internal references with a fresh scan of the .tex files.

    Returns a one-line summary.
    """
    ensure_xref_tables(conn)
    docs = _xref_documents(conn, root)
    folder_of = {item["code"]: item["folder"] for item in docs}
    main_of = {item["code"]: item["main"] for item in docs}
    files = {}
    labels = {}
    refs = []
    cites = []
    bibitems = set()
    inputs = {}
    order = {}
    stated = {}
    problems = []

    for doc in docs:
        base = os.path.join(root, doc["folder"])
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [name for name in dirnames if name not in _XREF_SKIP_DIRS]
            for filename in filenames:
                if not filename.endswith(".tex"):
                    continue
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, root).replace("\\", "/")
                drel = os.path.relpath(full, base).replace("\\", "/")
                files[rel] = {"doc": doc["code"], "drel": drel, "key": None}
        main_path = os.path.join(base, doc["main"])
        if not os.path.isfile(main_path):
            continue
        main_text = read_text(main_path)
        position = 0
        pending = None
        for raw in main_text.splitlines():
            line = _tex_strip_comment(raw).strip()
            prereq = re.match(r"\\chapterprereqs\{([^}]*)\}", line)
            if prereq:
                pending = [item.strip() for item in prereq.group(1).split(",") if item.strip()]
                continue
            included = _XREF_INPUT.search(line)
            if not included:
                continue
            target = included.group(1).strip()
            if not target.endswith(".tex"):
                target += ".tex"
            key = _xref_chapter_key(doc["code"], target)
            if key and (doc["code"], key) not in order:
                order[(doc["code"], key)] = position
                position += 1
            if key and pending is not None:
                stated[(doc["code"], key)] = pending
                pending = None

    for rel, info in files.items():
        try:
            raw = read_text(os.path.join(root, rel))
        except (OSError, UnicodeDecodeError) as exc:
            problems.append(f"{rel}: {exc}")
            continue
        lines = [_tex_strip_comment(line) for line in raw.splitlines()]
        inputs[rel] = []
        folder = folder_of[info["doc"]]
        for number, line in enumerate(lines, start=1):
            for match in _XREF_LABEL.finditer(line):
                labels.setdefault(match.group(1).strip(), []).append((rel, number))
            for match in _XREF_REF.finditer(line):
                refs.append((rel, number, match.group(1), match.group(2).strip()))
            for match in _XREF_CITE.finditer(line):
                for key in match.group(1).split(","):
                    key = key.strip()
                    if key:
                        cites.append((rel, number, key))
            for match in _XREF_BIBITEM.finditer(line):
                bibitems.add(match.group(1).strip())
            for match in _XREF_INPUT.finditer(line):
                target = match.group(1).strip()
                if not target.endswith(".tex"):
                    target += ".tex"
                target_path = os.path.normpath(os.path.join(root, folder, target))
                inputs[rel].append(os.path.relpath(target_path, root).replace("\\", "/"))
        joined = "\n".join(lines)
        for match in re.finditer(r"\\glossentry", joined):
            groups = _tex_brace_groups(joined, match.end(), 3)
            if groups and groups[2].strip():
                line_no = joined.count("\n", 0, match.start()) + 1
                refs.append((rel, line_no, "glossentry", groups[2].strip()))

    includer = {}
    for source, targets in inputs.items():
        for target in targets:
            includer.setdefault(target, source)

    def chapter_key(rel, seen=None):
        info = files.get(rel)
        if not info:
            return None
        if info["key"]:
            return info["key"]
        key = _xref_chapter_key(info["doc"], info["drel"])
        if key:
            info["key"] = key
            return key
        seen = seen or set()
        parent = includer.get(rel)
        if parent and parent not in seen and parent in files:
            seen.add(rel)
            key = chapter_key(parent, seen)
            if key:
                info["key"] = key
                return key
        info["key"] = info["drel"]
        return info["key"]

    for rel in files:
        chapter_key(rel)

    for label, places in labels.items():
        if len(places) > 1:
            problems.append(f"label `{label}` defined {len(places)} times: {places}")
    unresolved = [(rel, number, command, label) for rel, number, command, label in refs if label not in labels]
    for rel, number, command, label in unresolved:
        problems.append(f"{rel}:{number}: \\{command}{{{label}}} has no target")
    bad_cites = [(rel, number, key) for rel, number, key in cites if key not in bibitems]
    for rel, number, key in bad_cites:
        problems.append(f"{rel}:{number}: \\cite{{{key}}} not in the bibliography")

    chapter_ids = _xref_chapter_ids(conn)
    ancestors = _xref_ancestors(conn)
    cross = []
    for rel, number, command, label in refs:
        info = files.get(rel)
        if not info or info["drel"] == main_of[info["doc"]]:
            continue
        if label not in labels:
            continue
        target_rel = labels[label][0][0]
        target = files.get(target_rel)
        if not target:
            continue
        src = (info["doc"], info["key"])
        tgt = (target["doc"], target["key"])
        if src[0] == tgt[0]:
            continue
        direction = _xref_direction(src[0], src[1], tgt[0], tgt[1], order, ancestors)
        cross.append({
            "source_file": rel,
            "line": number,
            "command": command,
            "label": label,
            "source_doc": src[0],
            "target_doc": tgt[0],
            "target_id": _xref_display_id(tgt[0], tgt[1], chapter_ids),
            "direction": direction,
            "src_key": src,
            "tgt_key": tgt,
        })

    gaps = []
    for key, names in stated.items():
        have = set()
        for label in names:
            if label not in labels:
                continue
            target_rel = labels[label][0][0]
            target = files.get(target_rel)
            if target:
                have.add((target["doc"], target["key"]))
        owned = [rel for rel, info in files.items() if (info["doc"], info["key"]) == key]
        for rel, number, _command, label in refs:
            if rel not in owned or label not in labels:
                continue
            target_rel = labels[label][0][0]
            target = files.get(target_rel)
            if not target:
                continue
            tgt = (target["doc"], target["key"])
            if tgt == key or tgt[0] in ("GLOSSARY", "unsorted") or tgt in have:
                continue
            if _xref_direction(key[0], key[1], tgt[0], tgt[1], order, ancestors) != "back":
                continue
            message = (
                f"{_xref_display_id(key[0], key[1], chapter_ids)}: refers back to "
                f"{_xref_display_id(tgt[0], tgt[1], chapter_ids)} ({rel}:{number}, {label}) "
                "but its prerequisites omit it"
            )
            gaps.append(message)
    problems.extend(gaps)

    builds = []
    for index, doc in enumerate(docs):
        log = os.path.join(root, doc["folder"], "build", doc["job"] + ".log")
        pdf = os.path.join(root, doc["folder"], "build", doc["job"] + ".pdf")
        if not os.path.exists(log) or not os.path.exists(pdf):
            status = "not built"
        else:
            with open(log, encoding="latin-1") as fh:
                text = fh.read()
            found = [name for name, pattern in _XREF_LOG_PATTERNS if pattern.search(text)]
            status = ", ".join(found) if found else "clean"
            for name in found:
                problems.append(f"{doc['code']}: {name} (see {doc['folder']}/build/{doc['job']}.log)")
        builds.append({
            "position": index,
            "doc": doc["code"],
            "folder": doc["folder"],
            "job": doc["job"],
            "status": status,
        })

    conn.execute("DELETE FROM xref_refs")
    conn.execute("DELETE FROM xref_problems")
    conn.execute("DELETE FROM xref_builds")
    conn.execute("DELETE FROM xref_summary")
    conn.execute(
        "INSERT INTO xref_summary (id, dup_labels, unresolved, bad_cites, prereq_gaps) VALUES (1, ?, ?, ?, ?)",
        (
            sum(1 for places in labels.values() if len(places) > 1),
            len(unresolved),
            len(bad_cites),
            len(gaps),
        ),
    )
    for build in builds:
        conn.execute(
            "INSERT INTO xref_builds (position, doc, folder, job, status) VALUES (?, ?, ?, ?, ?)",
            (build["position"], build["doc"], build["folder"], build["job"], build["status"]),
        )
    for ref in cross:
        conn.execute(
            """INSERT INTO xref_refs
               (source_file, line, command, label, source_doc, target_doc, target_id, direction)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ref["source_file"], ref["line"], ref["command"], ref["label"],
                ref["source_doc"], ref["target_doc"], ref["target_id"], ref["direction"],
            ),
        )
    for index, message in enumerate(problems):
        conn.execute(
            "INSERT INTO xref_problems (position, message) VALUES (?, ?)",
            (index, message),
        )
    conn.commit()
    counts = {"back": 0, "forward": 0, "reference": 0}
    for ref in cross:
        counts[ref["direction"]] += 1
    return (
        f"Scanned LaTeX. Stored {len(cross)} internal references "
        f"(back {counts['back']}, forward {counts['forward']}, reference {counts['reference']}). "
        f"Problems: {len(problems)}."
    )


def render_cross_references(conn):
    """INTERNAL_REFERENCES.md from the stored scan."""
    ensure_xref_tables(conn)
    summary = conn.execute("SELECT * FROM xref_summary WHERE id = 1").fetchone()
    if summary is None:
        raise LibraryError("scan the LaTeX files first")
    refs = _rows(
        conn,
        "SELECT * FROM xref_refs ORDER BY source_doc, source_file, line, label",
    )
    builds = _rows(conn, "SELECT * FROM xref_builds ORDER BY position")
    problems = _rows(conn, "SELECT message FROM xref_problems ORDER BY position")
    docs = []
    for build in builds:
        if build["doc"] not in docs:
            docs.append(build["doc"])
    for ref in refs:
        for code in (ref["source_doc"], ref["target_doc"]):
            if code not in docs:
                docs.append(code)

    def doc_key(code):
        if code == "unsorted":
            return (2, 0)
        if code in BOOK_ORDER:
            return (0, BOOK_ORDER.index(code))
        return (1, code)

    docs.sort(key=doc_key)
    refs.sort(key=lambda ref: (doc_key(ref["source_doc"]), ref["source_file"], ref["line"], ref["label"]))
    labels = [_xref_doc_label(code) for code in docs]
    grid = {}
    counts = {"back": 0, "forward": 0, "reference": 0}
    for ref in refs:
        grid[(ref["source_doc"], ref["target_doc"])] = grid.get((ref["source_doc"], ref["target_doc"]), 0) + 1
        counts[ref["direction"]] += 1

    lines = [
        "# Internal references",
        "",
        "Generated from `library.sqlite`. This file is a reading, not an import. "
        "Scan the LaTeX files in the library, then export this document to refresh it.",
        "",
        "A reference is **back** when its target is a document this one lists as finish-first. "
        "It is **forward** otherwise, and **reference** when GLOSSARY or unsorted is involved.",
        "",
        "## Checks",
        "",
        f"- Labels defined more than once: {summary['dup_labels']}",
        f"- References without a target: {summary['unresolved']}",
        f"- Citations missing from the bibliography: {summary['bad_cites']}",
        f"- Chapters whose prerequisites omit a chapter they refer back to: {summary['prereq_gaps']}",
        "- Overall: "
        + (
            "PASS"
            if not problems
            else "FAIL ("
            + str(len(problems))
            + (" problem" if len(problems) == 1 else " problems")
            + ", listed at the end)"
        ),
        "",
        "| build | status |",
        "| --- | --- |",
    ]
    for build in builds:
        lines.append(
            f"| {_xref_doc_label(build['doc'])} (`{build['folder']}/build/{build['job']}.pdf`) | {build['status']} |"
        )
    lines.extend([
        "",
        "## References between documents (rows: from, columns: to)",
        "",
        "| from \\ to | " + " | ".join(labels) + " |",
        "| " + " | ".join(["---"] * (len(labels) + 1)) + " |",
    ])
    for code in docs:
        cells = [str(grid.get((code, other), "") or "") for other in docs]
        lines.append(f"| **{_xref_doc_label(code)}** | " + " | ".join(cells) + " |")
    lines.extend([
        "",
        f"Totals: {len(refs)} references across documents; back {counts['back']}, "
        f"forward {counts['forward']}, reference {counts['reference']}.",
        "",
    ])

    def table(title, predicate):
        chosen = [ref for ref in refs if predicate(ref)]
        lines.extend([f"## {title}", ""])
        if not chosen:
            lines.extend(["None.", ""])
            return
        lines.extend([
            "| source | command | label | target chapter | direction |",
            "| --- | --- | --- | --- | --- |",
        ])
        for ref in chosen:
            lines.append(
                f"| `{ref['source_file']}:{ref['line']}` | `\\{ref['command']}` | `{ref['label']}` | "
                f"{ref['target_id']} | {ref['direction']} |"
            )
        lines.append("")

    table("Forward references (soft prerequisites)", lambda ref: ref["direction"] == "forward")
    table("References into unsorted material", lambda ref: ref["target_doc"] == "unsorted")
    table("Back references across documents", lambda ref: ref["direction"] == "back")
    table(
        "References to and from GLOSSARY",
        lambda ref: ref["direction"] == "reference" and ref["target_doc"] != "unsorted",
    )
    if problems:
        lines.extend(["## Problems", ""])
        lines.extend(f"- {row['message']}" for row in problems)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


_SOURCE_BIBITEM = re.compile(
    r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})",
    re.S,
)


def _source_doc_key(code):
    if code == "unsorted":
        return (2, 0)
    if code in BOOK_ORDER:
        return (0, BOOK_ORDER.index(code))
    return (1, code)


def _source_reference(body):
    ref = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", " ".join(body.split()))
    ref = ref.replace("~", " ").replace("--", "-").replace("\\&", "&").replace("{", "").replace("}", "")
    ref = re.sub(r"\\[a-zA-Z]+ ?", "", ref).replace("\\", "").replace("|", "/")
    return ref.strip()


def _bibliography_path(root, conn):
    row = conn.execute("SELECT folder FROM books WHERE code = 'GLOSSARY'").fetchone()
    folder = "GLOSSARY"
    if row and (row["folder"] or "").strip():
        folder = row["folder"].strip().strip("/\\")
    return os.path.join(root, folder, "references", "references.tex")


def _citing_documents(root, conn):
    citers = {}
    for doc in _xref_documents(conn, root):
        base = os.path.join(root, doc["folder"])
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [name for name in dirnames if name not in _XREF_SKIP_DIRS]
            for filename in filenames:
                if not filename.endswith(".tex"):
                    continue
                full = os.path.join(dirpath, filename)
                try:
                    raw = read_text(full)
                except (OSError, UnicodeDecodeError):
                    continue
                for line in raw.splitlines():
                    line = _tex_strip_comment(line)
                    for match in _XREF_CITE.finditer(line):
                        for key in match.group(1).split(","):
                            key = key.strip()
                            if key:
                                citers.setdefault(key, set()).add(doc["code"])
    return citers


def _source_files(root, conn):
    found = []
    for doc in _xref_documents(conn, root):
        base = os.path.join(root, doc["folder"], "sources")
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            for filename in filenames:
                if filename == ".gitkeep":
                    continue
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, root).replace("\\", "/")
                found.append((doc["code"], rel))
    found.sort(key=lambda item: (_source_doc_key(item[0]), item[1]))
    return found


def _source_id_from_path(rel):
    name = os.path.splitext(os.path.basename(rel))[0]
    ident = re.sub(r"[^A-Za-z0-9]+", "", name)
    if not ident or not ident[0].isalpha():
        ident = "s" + ident
    return ident[:40]


def _seed_cited_sources(conn, root):
    if conn.execute("SELECT COUNT(*) AS c FROM sources").fetchone()["c"]:
        return
    path = _bibliography_path(root, conn)
    if not os.path.isfile(path):
        return
    items = _SOURCE_BIBITEM.findall(read_text(path))
    citers = _citing_documents(root, conn)
    known = {row["code"] for row in conn.execute("SELECT code FROM books")}
    for position, (key, body) in enumerate(items):
        key = key.strip()
        codes = sorted(citers.get(key, ()), key=_source_doc_key)
        labels = [_xref_doc_label(code) for code in codes]
        document = "cited by " + (", ".join(labels) if labels else "no document")
        conn.execute(
            "INSERT INTO sources (id, file, proposed_chapter, status, reference, document, position) "
            "VALUES (?, 'none', '-', 'cited, no file', ?, ?, ?)",
            (key, _source_reference(body), document, position),
        )
        books = [code for code in codes if code in known]
        if not books and "GLOSSARY" in known:
            books = ["GLOSSARY"]
        for book in books:
            conn.execute("INSERT INTO source_books (source, book) VALUES (?, ?)", (key, book))


def _seed_source_files(conn, root):
    """Add a registry row for a file in a sources folder that is not registered yet."""
    next_pos = conn.execute("SELECT COALESCE(MAX(position), -1) + 1 AS n FROM sources").fetchone()["n"]
    used = {row["id"] for row in conn.execute("SELECT id FROM sources")}
    for code, rel in _source_files(root, conn):
        existing = conn.execute("SELECT id FROM sources WHERE file = ?", (rel,)).fetchone()
        if existing:
            conn.execute(
                "INSERT OR IGNORE INTO source_books (source, book) VALUES (?, ?)",
                (existing["id"], code),
            )
            continue
        ident = _source_id_from_path(rel)
        base = ident
        n = 2
        while ident in used:
            ident = f"{base}{n}"
            n += 1
        used.add(ident)
        conn.execute(
            "INSERT INTO sources (id, file, proposed_chapter, status, reference, document, position) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ident, rel, "-", "unplaced", "", code, next_pos),
        )
        conn.execute("INSERT INTO source_books (source, book) VALUES (?, ?)", (ident, code))
        next_pos += 1


def seed_sources(conn, root):
    """Fill the source registry from the bibliography, then from files in sources folders."""
    ensure_source_tables(conn)
    _seed_cited_sources(conn, root)
    _seed_source_files(conn, root)
    conn.commit()


def render_sources_index(root, conn):
    """EXTERNAL_SOURCES.md from the sources stored for each book."""
    seed_sources(conn, root)
    path = _bibliography_path(root, conn)
    rows = _rows(conn, "SELECT * FROM sources ORDER BY position, id")
    if not rows and not os.path.isfile(path):
        raise LibraryError("GLOSSARY/references/references.tex is missing")
    lines = [
        "# External sources",
        "",
        "Registry of every source. Generated from `library.sqlite`. "
        "Edit a source in the organization file of a book that lists it, then import that file.",
        "",
        "Workflow for new sources:",
        "",
        "1. Put the file in the owning document's `sources/` folder (for example `QM-quantum-mechanics/sources/`). "
        "Sources that concern several documents go to the owner of the topic they mainly treat.",
        "2. Add a row to that book's organization file with status `unplaced`, then import the file.",
        "3. Propose its placement in [ROADMAP.md](ROADMAP.md) (section \"Proposed source placements\"), naming the "
        "[EDITORIAL_ORGANIZATION.md](EDITORIAL_ORGANIZATION.md) row it would fill; status `proposed`.",
        "4. Only after approval: status `approved`; content is merged into chapters only when asked (`merged`).",
        "",
        "Status values: `unplaced`, `proposed`, `approved`, `merged`; `cited, no file` for bibliography entries "
        "already cited in the text whose file is not in the repository.",
        "",
        "## Registry",
        "",
        "| ID | file | document | proposed chapter | status | reference |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['file']} | {row['document']} | {row['proposed_chapter']} | "
            f"{row['status']} | {row['reference']} |"
        )
    files = _source_files(root, conn)
    lines.extend(["", "## Source files", ""])
    if files:
        lines.extend(["| file | document |", "| --- | --- |"])
        for code, rel in files:
            lines.append(f"| `{rel}` | {_xref_doc_label(code)} |")
    else:
        lines.append("No source files have been added yet. Each document has an empty `sources/` folder.")
    lines.append("")
    return "\n".join(lines)

__all__ = [name for name in globals() if not name.startswith('__')]
