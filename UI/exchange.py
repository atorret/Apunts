"""Strict markdown import and export, and record updates."""

import re

from base import (
    BOOK_ALT,
    BOOK_CODES,
    BOOK_TABLES,
    BUILTIN_STATUSES,
    CHAPTER_INSERT,
    CHAPTER_RE,
    CHAPTER_TABLES,
    LIBRARY_TABLES,
    LibraryError,
    TABLES,
    md_table,
    parse_md_tables,
    write_text,
)

def _rows(conn, sql, args=()):
    return [dict(row) for row in conn.execute(sql, args)]


def export_rows(conn, scope):
    """Rows for a complete scope. Keys are table names."""
    if scope == "library":
        data = {
            "statuses": _rows(conn, "SELECT name, position FROM statuses ORDER BY position, name"),
            "books": _rows(conn, "SELECT code, title, folder, entry_level, target_level, editorial_status, notes FROM books ORDER BY code"),
            "book_requires": _rows(conn, "SELECT book, requires FROM book_requires ORDER BY book, requires"),
            "parts": _rows(conn, "SELECT id, book, title FROM parts ORDER BY id"),
            "chapters": _rows(conn, "SELECT id, book, title, level, presence, editorial_status, path, notes, explain FROM chapters ORDER BY book, id"),
            "prereqs": _rows(conn, "SELECT chapter, target, kind FROM prereqs ORDER BY chapter, target, kind"),
            "concepts": _rows(conn, "SELECT slug, title FROM concepts ORDER BY slug"),
            "concept_links": _rows(conn, "SELECT concept, role, target FROM concept_links ORDER BY concept, role, target"),
            "roadmaps": _rows(conn, "SELECT id, title, notes FROM roadmaps ORDER BY id"),
            "roadmap_steps": _rows(conn, "SELECT roadmap, position, target FROM roadmap_steps ORDER BY roadmap, position"),
        }
        return data
    if scope in BOOK_CODES or _is_book(conn, scope):
        book = scope
        data = {
            "books": _rows(conn, "SELECT code, title, folder, entry_level, target_level, editorial_status, notes FROM books WHERE code = ?", (book,)),
            "parts": _rows(conn, "SELECT id, book, title FROM parts WHERE book = ? ORDER BY id", (book,)),
            "chapters": _rows(conn, "SELECT id, book, title, level, presence, editorial_status, path, notes, explain FROM chapters WHERE book = ? ORDER BY id", (book,)),
            "prereqs": _rows(
                conn,
                "SELECT p.chapter, p.target, p.kind FROM prereqs p JOIN chapters c ON c.id = p.chapter "
                "WHERE c.book = ? ORDER BY p.chapter, p.target, p.kind",
                (book,),
            ),
            "roadmaps": _rows(conn, "SELECT id, title, notes FROM roadmaps WHERE id = ?", (book,)),
            "roadmap_steps": _rows(conn, "SELECT roadmap, position, target FROM roadmap_steps WHERE roadmap = ? ORDER BY position", (book,)),
        }
        return data
    if CHAPTER_RE.fullmatch(scope):
        data = {
            "chapters": _rows(conn, "SELECT id, book, title, level, presence, editorial_status, path, notes, explain FROM chapters WHERE id = ?", (scope,)),
            "prereqs": _rows(conn, "SELECT chapter, target, kind FROM prereqs WHERE chapter = ? ORDER BY target, kind", (scope,)),
        }
        return data
    raise LibraryError(f"unknown scope: {scope}")


def _is_book(conn, code):
    row = conn.execute("SELECT 1 FROM books WHERE code = ?", (code,)).fetchone()
    return row is not None


def render_strict(scope, data):
    lines = [f"scope: {scope}", ""]
    for name, rows in data.items():
        lines.append(f"## {name}")
        lines.extend(md_table(TABLES[name], rows))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def export_strict(conn, scope, path):
    text = render_strict(scope, export_rows(conn, scope))
    write_text(path, text)
    return path


def export_filter(conn, path, book="", status="", level="", presence=""):
    clauses = []
    args = []
    if book:
        clauses.append("book = ?")
        args.append(book)
    if status:
        clauses.append("editorial_status = ?")
        args.append(status)
    if level:
        clauses.append("level = ?")
        args.append(level)
    if presence:
        clauses.append("presence = ?")
        args.append(presence)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = _rows(
        conn,
        "SELECT id, book, title, level, presence, editorial_status, path, notes, explain FROM chapters"
        + where + " ORDER BY book, id",
        args,
    )
    lines = [
        "import: refused",
        "",
        "Filtered report. Import refuses this file.",
        "",
        "## chapters",
    ]
    lines.extend(md_table(TABLES["chapters"], rows))
    write_text(path, "\n".join(lines) + "\n")
    return path


def _check_columns(table, rows):
    expected = TABLES[table]
    if table not in TABLES:
        raise LibraryError(f"unknown table: {table}")
    for row in rows:
        unknown = set(row) - set(expected)
        missing = set(expected) - set(row)
        if unknown or missing:
            raise LibraryError(f"{table} columns must be {', '.join(expected)}")


def _require_status(conn, name, creating):
    if name is None or name == "":
        return
    row = conn.execute("SELECT 1 FROM statuses WHERE name = ?", (name,)).fetchone()
    if row:
        return
    if name in creating:
        return
    raise LibraryError(f"unregistered status: {name}")


def import_strict(conn, text):
    scope, tables = parse_md_tables(text)
    for name in tables:
        if name not in TABLES:
            raise LibraryError(f"unknown table: {name}")
        _check_columns(name, tables[name])
    if scope == "library":
        missing = [name for name in LIBRARY_TABLES if name not in tables]
        if missing:
            raise LibraryError("library import must include every table; missing " + ", ".join(missing))
        _import_library(conn, tables)
    elif CHAPTER_RE.fullmatch(scope):
        extra = set(tables) - set(CHAPTER_TABLES)
        missing = [name for name in CHAPTER_TABLES if name not in tables]
        if extra or missing:
            raise LibraryError("a chapter file must contain only chapters and prereqs")
        _import_chapter(conn, scope, tables)
    elif re.fullmatch(BOOK_ALT, scope):
        extra = set(tables) - set(BOOK_TABLES)
        missing = [name for name in BOOK_TABLES if name not in tables]
        if extra or missing:
            raise LibraryError(
                "a book file must contain books, parts, chapters, prereqs, roadmaps, and roadmap_steps"
            )
        _import_book(conn, scope, tables)
    else:
        raise LibraryError(f"unknown scope: {scope}")
    conn.commit()


def _import_library(conn, tables):
    names = [row["name"] for row in tables["statuses"]]
    if len(names) != len(set(names)):
        raise LibraryError("duplicate status name")
    missing_builtin = [name for name in BUILTIN_STATUSES if name not in names]
    if missing_builtin:
        raise LibraryError("the five built-in statuses cannot be removed")
    referenced = set()
    for row in tables["books"]:
        if row["editorial_status"]:
            referenced.add(row["editorial_status"])
    for row in tables["chapters"]:
        if row["editorial_status"]:
            referenced.add(row["editorial_status"])
    unknown = referenced - set(names)
    if unknown:
        raise LibraryError("unregistered status: " + ", ".join(sorted(unknown)))
    _check_library_shape(tables)
    conn.execute("DELETE FROM roadmap_steps")
    conn.execute("DELETE FROM roadmaps")
    conn.execute("DELETE FROM concept_links")
    conn.execute("DELETE FROM concepts")
    conn.execute("DELETE FROM prereqs")
    conn.execute("DELETE FROM chapters")
    conn.execute("DELETE FROM parts")
    conn.execute("DELETE FROM book_requires")
    conn.execute("DELETE FROM books")
    conn.execute("DELETE FROM statuses")
    for index, row in enumerate(tables["statuses"]):
        builtin = 1 if row["name"] in BUILTIN_STATUSES else 0
        position = int(row["position"]) if str(row["position"]).strip() else index + 1
        conn.execute(
            "INSERT INTO statuses (name, position, builtin) VALUES (?, ?, ?)",
            (row["name"], position, builtin),
        )
    _insert_graph(conn, tables)


def _check_library_shape(tables):
    for row in tables["chapters"]:
        if row["presence"] not in ("absent", "present", "retired"):
            raise LibraryError(f"bad presence on {row['id']}")
        if row["presence"] == "retired" and row["editorial_status"]:
            raise LibraryError(f"retired chapter {row['id']} cannot have a workflow status")
        if row["presence"] != "retired" and not row["editorial_status"]:
            raise LibraryError(f"chapter {row['id']} needs an editorial status")
    for row in tables["prereqs"]:
        if row["kind"] not in ("hard", "optional"):
            raise LibraryError(f"bad prerequisite kind on {row['chapter']}")
    for row in tables["concept_links"]:
        if row["role"] not in ("owner", "referenced_by"):
            raise LibraryError(f"bad concept role on {row['concept']}")


def _insert_graph(conn, tables):
    for row in tables.get("books", []):
        _require_status(conn, row["editorial_status"], set())
        conn.execute(
            "INSERT INTO books (code, title, folder, entry_level, target_level, editorial_status, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row["code"], row["title"], row["folder"], row["entry_level"], row["target_level"],
             row["editorial_status"] or None, row["notes"]),
        )
    for row in tables.get("book_requires", []):
        conn.execute("INSERT INTO book_requires (book, requires) VALUES (?, ?)", (row["book"], row["requires"]))
    for row in tables.get("parts", []):
        conn.execute("INSERT INTO parts (id, book, title) VALUES (?, ?, ?)", (row["id"], row["book"], row["title"]))
    for row in tables.get("chapters", []):
        status = row["editorial_status"] or None
        _require_status(conn, status, set())
        conn.execute(
            CHAPTER_INSERT,
            (row["id"], row["book"], row["title"], row["level"], row["presence"], status, row["path"],
             row["notes"], row.get("explain") or ""),
        )
    for row in tables.get("prereqs", []):
        conn.execute(
            "INSERT INTO prereqs (chapter, target, kind) VALUES (?, ?, ?)",
            (row["chapter"], row["target"], row["kind"]),
        )
    for row in tables.get("concepts", []):
        conn.execute("INSERT INTO concepts (slug, title) VALUES (?, ?)", (row["slug"], row["title"]))
    for row in tables.get("concept_links", []):
        conn.execute(
            "INSERT INTO concept_links (concept, role, target) VALUES (?, ?, ?)",
            (row["concept"], row["role"], row["target"]),
        )
    for row in tables.get("roadmaps", []):
        conn.execute(
            "INSERT INTO roadmaps (id, title, notes) VALUES (?, ?, ?)",
            (row["id"], row["title"], row["notes"]),
        )
    for row in tables.get("roadmap_steps", []):
        conn.execute(
            "INSERT INTO roadmap_steps (roadmap, position, target) VALUES (?, ?, ?)",
            (row["roadmap"], int(row["position"]), row["target"]),
        )


def _import_book(conn, book, tables):
    codes = [row["code"] for row in tables["books"]]
    if codes != [book]:
        raise LibraryError(f"book file for {book} must contain that book and no other")
    for row in tables["chapters"]:
        if row["book"] != book:
            raise LibraryError(f"chapter {row['id']} is outside {book}")
        if row["presence"] not in ("absent", "present", "retired"):
            raise LibraryError(f"bad presence on {row['id']}")
        _require_status(conn, row["editorial_status"], set())
    ids = {row["id"] for row in tables["chapters"]}
    for row in tables["prereqs"]:
        if row["chapter"] not in ids:
            raise LibraryError(f"prerequisite for {row['chapter']} is outside {book}")
        if row["kind"] not in ("hard", "optional"):
            raise LibraryError("bad prerequisite kind")
    for row in tables["parts"]:
        if row["book"] != book:
            raise LibraryError(f"part {row['id']} is outside {book}")
    roadmap_ids = [row["id"] for row in tables["roadmaps"]]
    if any(rid != book for rid in roadmap_ids):
        raise LibraryError("a book file may only carry that book's own roadmap")
    for row in tables["roadmap_steps"]:
        if row["roadmap"] != book:
            raise LibraryError("roadmap step is outside the book roadmap")
    _require_status(conn, tables["books"][0]["editorial_status"], set())
    conn.execute("DELETE FROM chapters WHERE book = ?", (book,))
    conn.execute("DELETE FROM parts WHERE book = ?", (book,))
    conn.execute("DELETE FROM roadmap_steps WHERE roadmap = ?", (book,))
    conn.execute("DELETE FROM roadmaps WHERE id = ?", (book,))
    book_row = tables["books"][0]
    conn.execute(
        "UPDATE books SET title = ?, folder = ?, entry_level = ?, target_level = ?, "
        "editorial_status = ?, notes = ? WHERE code = ?",
        (book_row["title"], book_row["folder"], book_row["entry_level"], book_row["target_level"],
         book_row["editorial_status"] or None, book_row["notes"], book),
    )
    for row in tables["parts"]:
        conn.execute("INSERT INTO parts (id, book, title) VALUES (?, ?, ?)", (row["id"], row["book"], row["title"]))
    for row in tables["chapters"]:
        conn.execute(
            CHAPTER_INSERT,
            (row["id"], row["book"], row["title"], row["level"], row["presence"],
             row["editorial_status"] or None, row["path"], row["notes"], row.get("explain") or ""),
        )
    for row in tables["prereqs"]:
        conn.execute(
            "INSERT INTO prereqs (chapter, target, kind) VALUES (?, ?, ?)",
            (row["chapter"], row["target"], row["kind"]),
        )
    for row in tables["roadmaps"]:
        conn.execute(
            "INSERT INTO roadmaps (id, title, notes) VALUES (?, ?, ?)",
            (row["id"], row["title"], row["notes"]),
        )
    for row in tables["roadmap_steps"]:
        conn.execute(
            "INSERT INTO roadmap_steps (roadmap, position, target) VALUES (?, ?, ?)",
            (row["roadmap"], int(row["position"]), row["target"]),
        )


def _import_chapter(conn, chapter, tables):
    rows = tables["chapters"]
    if len(rows) > 1 or (rows and rows[0]["id"] != chapter):
        raise LibraryError(f"chapter file for {chapter} must contain that chapter only")
    for row in tables["prereqs"]:
        if row["chapter"] != chapter:
            raise LibraryError(f"prerequisite row {row['chapter']} is outside {chapter}")
        if row["kind"] not in ("hard", "optional"):
            raise LibraryError("bad prerequisite kind")
    if not rows:
        conn.execute("DELETE FROM chapters WHERE id = ?", (chapter,))
        return
    row = rows[0]
    _require_status(conn, row["editorial_status"], set())
    if row["presence"] not in ("absent", "present", "retired"):
        raise LibraryError(f"bad presence on {chapter}")
    exists = conn.execute("SELECT 1 FROM chapters WHERE id = ?", (chapter,)).fetchone()
    if exists:
        conn.execute(
            "UPDATE chapters SET book = ?, title = ?, level = ?, presence = ?, editorial_status = ?, "
            "path = ?, notes = ?, explain = ? WHERE id = ?",
            (row["book"], row["title"], row["level"], row["presence"], row["editorial_status"] or None,
             row["path"], row["notes"], row.get("explain") or "", chapter),
        )
    else:
        conn.execute(
            CHAPTER_INSERT,
            (row["id"], row["book"], row["title"], row["level"], row["presence"],
             row["editorial_status"] or None, row["path"], row["notes"], row.get("explain") or ""),
        )
    conn.execute("DELETE FROM prereqs WHERE chapter = ?", (chapter,))
    for pre in tables["prereqs"]:
        conn.execute(
            "INSERT INTO prereqs (chapter, target, kind) VALUES (?, ?, ?)",
            (pre["chapter"], pre["target"], pre["kind"]),
        )


def set_status(conn, ident, status):
    update_record(conn, ident, presence=None, editorial_status=status, level=None)


def _apply_chapter_fields(conn, chapter_id, presence, editorial_status, level):
    row = conn.execute("SELECT id FROM chapters WHERE id = ?", (chapter_id,)).fetchone()
    if not row:
        raise LibraryError(f"no chapter {chapter_id}")
    if presence not in ("absent", "present", "retired"):
        raise LibraryError(f"bad presence on {chapter_id}")
    if presence == "retired":
        editorial_status = None
    elif not editorial_status:
        raise LibraryError(f"chapter {chapter_id} needs an editorial status")
    else:
        _require_status(conn, editorial_status, set())
    conn.execute(
        "UPDATE chapters SET presence = ?, editorial_status = ?, level = ? WHERE id = ?",
        (presence, editorial_status, level if level is not None else "", chapter_id),
    )


def update_record(conn, ident, presence=None, editorial_status=None, level=None):
    """Update workflow fields. Omitted arguments are left unchanged."""
    if CHAPTER_RE.fullmatch(ident):
        row = conn.execute(
            "SELECT presence, editorial_status, level FROM chapters WHERE id = ?", (ident,)
        ).fetchone()
        if not row:
            raise LibraryError(f"no chapter {ident}")
        new_presence = presence if presence is not None else row["presence"]
        new_status = editorial_status if editorial_status is not None else row["editorial_status"]
        new_level = level if level is not None else row["level"]
        if new_presence == "retired" and editorial_status is not None:
            raise LibraryError(f"{ident} is retired and has no workflow status")
        _apply_chapter_fields(conn, ident, new_presence, new_status, new_level)
        conn.commit()
        return
    found = conn.execute(
        "SELECT code, editorial_status, target_level FROM books WHERE code = ?", (ident,)
    ).fetchone()
    if not found:
        raise LibraryError(f"no book or chapter {ident}")
    book_status = editorial_status if editorial_status is not None else found["editorial_status"]
    book_level = level if level is not None else found["target_level"]
    if not book_status:
        raise LibraryError(f"book {ident} needs an editorial status")
    _require_status(conn, book_status, set())
    conn.execute(
        "UPDATE books SET editorial_status = ?, target_level = ? WHERE code = ?",
        (book_status, book_level or "", ident),
    )
    chapters = _rows(conn, "SELECT id, presence, editorial_status, level FROM chapters WHERE book = ?", (ident,))
    if not chapters:
        conn.commit()
        return
    for ch in chapters:
        new_presence = presence if presence is not None else ch["presence"]
        if editorial_status is not None:
            new_status = None if new_presence == "retired" else editorial_status
        elif new_presence == "retired":
            new_status = None
        else:
            new_status = ch["editorial_status"]
        new_level = level if level is not None else ch["level"]
        _apply_chapter_fields(conn, ch["id"], new_presence, new_status, new_level)
    conn.commit()


__all__ = [name for name in globals() if not name.startswith('__')]
