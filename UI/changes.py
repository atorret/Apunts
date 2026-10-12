"""Write exports and import book or chapter changes."""

import io
import os
import re
import sqlite3
import zipfile

from base import (
    CHAPTER_INSERT,
    LibraryError,
    book_of,
    cell_in,
    md_table,
    open_db,
    read_text,
    write_text,
)
from exchange import (
    _is_book,
    _require_status,
)
from readings import (
    _markdown_table,
    _ordered_book_codes,
    _organization_prereqs,
    _preamble_and_sections,
    is_book_organization,
    organization_path,
    organization_relpath,
    parse_dependency_rows,
    parse_explain_entries,
    render_book_organization,
    render_outline,
    render_reading_guide,
    replace_book_sources,
    parse_source_rows,
    DEPENDENCY_COLUMNS,
    SOURCE_COLUMNS,
)
from xref import (
    render_cross_references,
    render_sources_index,
    seed_sources,
)

def save_export(root, doc, book=""):
    """Write an export over the project file of the same name.

    Internal references are written from the stored LaTeX scan.
    Reading order is written to READING_ORDER.md and does not replace ROADMAP.md.
    Returns the project filenames involved.
    """
    if doc == "editorial-organization":
        conn = open_db(root)
        try:
            write_text(os.path.join(root, "EDITORIAL_ORGANIZATION.md"), render_outline(conn))
        finally:
            conn.close()
        return ["EDITORIAL_ORGANIZATION.md"]
    if doc == "internal-references":
        conn = open_db(root)
        try:
            text = render_cross_references(conn)
        finally:
            conn.close()
        write_text(os.path.join(root, "INTERNAL_REFERENCES.md"), text)
        return ["INTERNAL_REFERENCES.md"]
    if doc == "external-sources":
        conn = open_db(root)
        try:
            seed_sources(conn, root)
            text = render_sources_index(root, conn)
        finally:
            conn.close()
        write_text(os.path.join(root, "EXTERNAL_SOURCES.md"), text)
        return ["EXTERNAL_SOURCES.md"]
    if doc == "reading-order":
        conn = open_db(root)
        try:
            write_text(os.path.join(root, "READING_ORDER.md"), render_reading_guide(conn))
        finally:
            conn.close()
        return ["READING_ORDER.md"]
    if doc == "chapter-changes":
        write_text(os.path.join(root, "chapter-changes.md"), render_chapter_changes())
        return ["chapter-changes.md"]
    if doc != "book":
        raise LibraryError("choose a document")
    if not book:
        raise LibraryError("choose a book")
    conn = open_db(root)
    try:
        seed_sources(conn, root)
        known = {row["code"] for row in conn.execute("SELECT code FROM books")}
        codes = _ordered_book_codes(conn) if book == "all" else [book]
        if book != "all" and book not in known:
            raise LibraryError(f"unknown book: {book}")
        names = []
        for code in codes:
            name = organization_relpath(conn, code)
            write_text(organization_path(root, conn, code), render_book_organization(conn, code))
            names.append(name)
    finally:
        conn.close()
    return names


def import_book_organization(conn, text, commit=True):
    """Replace one book's organization. Returns the book code."""
    if not is_book_organization(text):
        raise LibraryError("import a book organization file")
    preamble, sections = _preamble_and_sections(text)
    book_match = re.search(r"(?m)^book:\s*(\S+)\s*$", preamble)
    if not book_match:
        raise LibraryError("book organization file needs a book line")
    book = book_match.group(1)
    if not _is_book(conn, book):
        raise LibraryError(f"unknown book: {book}")
    title_match = re.search(rf"(?m)^# {re.escape(book)} (.+)$", preamble)
    if not title_match:
        raise LibraryError(f"the title line must be # {book} followed by the title")
    title = title_match.group(1).strip()
    fields = {}
    for line in preamble.split("\n"):
        line = line.strip()
        if not line.startswith("- "):
            continue
        body = line[2:]
        if ":" not in body:
            raise LibraryError(f"unreadable line: {line}")
        key, value = body.split(":", 1)
        fields[key.strip().lower()] = value.strip()
    missing = [key for key in ("folder", "entry level", "target level", "editorial status", "finish first") if key not in fields]
    if missing:
        raise LibraryError("book organization is missing " + ", ".join(missing))
    status = fields["editorial status"]
    if status in ("—", "-"):
        status = ""
    _require_status(conn, status, set())
    finish = fields["finish first"].strip().rstrip(".")
    if finish.lower() in ("", "nothing", "none", "—"):
        requires = []
    else:
        requires = [item.strip() for item in finish.split(",") if item.strip()]
    if book in requires:
        raise LibraryError("a book cannot require itself")
    known_books = {row["code"] for row in conn.execute("SELECT code FROM books")}
    unknown = [item for item in requires if item not in known_books]
    if unknown:
        raise LibraryError("unknown book in finish first: " + ", ".join(unknown))
    if len(requires) != len(set(requires)):
        raise LibraryError("finish first lists a book twice")
    if "Book dependencies" in sections:
        dep_rows = _markdown_table(sections["Book dependencies"], "Book dependencies")
        if dep_rows and list(dep_rows[0]) != DEPENDENCY_COLUMNS:
            raise LibraryError("book dependency columns must be " + ", ".join(DEPENDENCY_COLUMNS))
        if not dep_rows and _markdown_table_headers(sections["Book dependencies"]) != DEPENDENCY_COLUMNS:
            raise LibraryError("book dependency columns must be " + ", ".join(DEPENDENCY_COLUMNS))
        requires = parse_dependency_rows(book, dep_rows, known_books)
    notes = sections.get("Notes", "").strip()
    if "Chapters" not in sections:
        raise LibraryError("book organization needs a Chapters section")
    chapter_rows = _markdown_table(sections["Chapters"], "Chapters")
    expected = ["chapter", "title", "level", "presence", "editorial status", "path", "prerequisites", "notes"]
    if chapter_rows and list(chapter_rows[0]) != expected:
        raise LibraryError("chapter columns must be " + ", ".join(expected))
    if not chapter_rows and _markdown_table_headers(sections["Chapters"]) != expected:
        raise LibraryError("chapter columns must be " + ", ".join(expected))
    chapters = []
    prereqs = []
    seen_ids = set()
    for row in chapter_rows:
        ident = row["chapter"].strip()
        if not re.fullmatch(rf"{re.escape(book)}/ch\d+", ident):
            raise LibraryError(f"chapter {ident or '(blank)'} is outside {book}")
        if ident in seen_ids:
            raise LibraryError(f"duplicate chapter {ident}")
        seen_ids.add(ident)
        presence = row["presence"].strip()
        if presence not in ("absent", "present", "retired"):
            raise LibraryError(f"bad presence on {ident}")
        editorial = row["editorial status"].strip()
        if editorial in ("—", "-"):
            editorial = ""
        if presence == "retired" and editorial:
            raise LibraryError(f"retired chapter {ident} cannot have a workflow status")
        if presence != "retired" and not editorial:
            raise LibraryError(f"chapter {ident} needs an editorial status")
        _require_status(conn, editorial, set())
        chapters.append({
            "id": ident,
            "title": row["title"].strip(),
            "level": row["level"].strip(),
            "presence": presence,
            "editorial_status": editorial,
            "path": row["path"].strip(),
            "notes": row["notes"],
            "explain": "",
        })
        for target, kind in _organization_prereqs(ident, row["prerequisites"]):
            prereqs.append((ident, target, kind))
    if "What to explain" in sections:
        explain_map = parse_explain_entries(sections["What to explain"])
        known = {chapter["id"] for chapter in chapters}
        extra = set(explain_map) - known
        if extra:
            raise LibraryError("What to explain has extra " + ", ".join(sorted(extra)))
        missing = [chapter["id"] for chapter in chapters if chapter["id"] not in explain_map]
        if missing:
            raise LibraryError("What to explain is missing " + ", ".join(missing))
        for chapter in chapters:
            chapter["explain"] = explain_map[chapter["id"]]
    parts = None
    if "Parts" in sections:
        part_rows = _markdown_table(sections["Parts"], "Parts")
        if part_rows and list(part_rows[0]) != ["part", "title"]:
            raise LibraryError("part columns must be part, title")
        if not part_rows and _markdown_table_headers(sections["Parts"]) != ["part", "title"]:
            raise LibraryError("part columns must be part, title")
        parts = []
        seen_parts = set()
        for row in part_rows:
            ident = row["part"].strip()
            if not ident.startswith(book + "/"):
                raise LibraryError(f"part {ident or '(blank)'} is outside {book}")
            if ident in seen_parts:
                raise LibraryError(f"duplicate part {ident}")
            seen_parts.add(ident)
            parts.append((ident, row["title"].strip()))
    sources = None
    if "Sources" in sections:
        source_rows = _markdown_table(sections["Sources"], "Sources")
        if source_rows and list(source_rows[0]) != SOURCE_COLUMNS:
            raise LibraryError("source columns must be " + ", ".join(SOURCE_COLUMNS))
        if not source_rows and _markdown_table_headers(sections["Sources"]) != SOURCE_COLUMNS:
            raise LibraryError("source columns must be " + ", ".join(SOURCE_COLUMNS))
        parse_source_rows(source_rows)
        sources = source_rows
    try:
        conn.execute(
            "UPDATE books SET title = ?, folder = ?, entry_level = ?, target_level = ?, "
            "editorial_status = ?, notes = ? WHERE code = ?",
            (title, fields["folder"].strip(), fields["entry level"].strip(), fields["target level"].strip(),
             status or None, notes, book),
        )
        conn.execute("DELETE FROM book_requires WHERE book = ?", (book,))
        for item in requires:
            conn.execute("INSERT INTO book_requires (book, requires) VALUES (?, ?)", (book, item))
        if parts is not None:
            conn.execute("DELETE FROM parts WHERE book = ?", (book,))
            for ident, part_title in parts:
                conn.execute("INSERT INTO parts (id, book, title) VALUES (?, ?, ?)", (ident, book, part_title))
        conn.execute("DELETE FROM chapters WHERE book = ?", (book,))
        for chapter in chapters:
            conn.execute(
                CHAPTER_INSERT,
                (chapter["id"], book, chapter["title"], chapter["level"], chapter["presence"],
                 chapter["editorial_status"] or None, chapter["path"], chapter["notes"],
                 chapter["explain"]),
            )
        for ident, target, kind in prereqs:
            conn.execute(
                "INSERT INTO prereqs (chapter, target, kind) VALUES (?, ?, ?)",
                (ident, target, kind),
            )
        if sources is not None:
            replace_book_sources(conn, book, sources)
        if commit:
            conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise LibraryError(f"could not store {book}: {exc}") from exc
    return book


BOOK_CHANGE_COLUMNS = [
    "code", "title", "folder", "entry level", "target level", "editorial status", "finish first", "notes",
]
CHAPTER_CHANGE_COLUMNS = [
    "chapter", "title", "level", "presence", "editorial status", "path", "prerequisites", "notes",
    "what to explain",
]
CHAPTER_CHANGE_SECTIONS = (
    ("New books", BOOK_CHANGE_COLUMNS, "Books that do not exist yet. Finish first is the complete list of books that must be finished first."),
    ("Edited books", BOOK_CHANGE_COLUMNS, "Books that already exist. The row replaces that book's information, including which books must be finished first."),
    ("Deleted books", ["code"], "Deleting a book also deletes its chapters."),
    ("New chapters", CHAPTER_CHANGE_COLUMNS, "Chapters that do not exist yet. The id is the book code, a slash, and ch with a number. What to explain is the teaching brief."),
    ("Edited chapters", CHAPTER_CHANGE_COLUMNS, "Chapters that already exist. The row replaces that chapter, its prerequisites, and what to explain."),
    ("Deleted chapters", ["chapter"], "Chapters to remove. A chapter whose book is deleted does not need to be listed."),
)


def is_chapter_changes(text):
    head = "\n".join(text.replace("\r\n", "\n").split("\n")[:12])
    return "kind: editorial-organization" in head


def render_chapter_changes():
    """Blank import. Every change has to be listed under new, edited, or deleted."""
    lines = [
        "kind: editorial-organization",
        "",
        "Specify every change. An empty table means that list has nothing in it.",
        "This file is an import. The full syllabus in EDITORIAL_ORGANIZATION.md is a reading and is not imported.",
        "A book organization file remains the other import, in its own format.",
        "",
    ]
    for name, columns, note in CHAPTER_CHANGE_SECTIONS:
        lines += [f"## {name}", "", note, ""]
        lines.extend(md_table(columns, []))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _checked_table(sections, name, columns):
    if name not in sections:
        raise LibraryError(f"editorial organization file needs a {name} section")
    rows = _markdown_table(sections[name], name)
    headers = list(rows[0]) if rows else _markdown_table_headers(sections[name])
    if headers != columns:
        raise LibraryError(f"{name} columns must be " + ", ".join(columns))
    return rows


def _blank_status(value):
    value = (value or "").strip()
    if value in ("—", "-"):
        return ""
    return value


def _finish_codes(book, cell):
    cell = (cell or "").strip().rstrip(".")
    if cell.lower() in ("", "nothing", "none", "—"):
        return []
    codes = [item.strip() for item in cell.split(",") if item.strip()]
    if book in codes:
        raise LibraryError(f"{book} cannot require itself")
    if len(codes) != len(set(codes)):
        raise LibraryError(f"{book} lists a finish-first book twice")
    return codes


def _book_code(value, where):
    code = (value or "").strip()
    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,20}", code):
        raise LibraryError(f"{where} needs a book code made of capital letters and digits")
    return code


def _chapter_record(row, books):
    ident = row["chapter"].strip()
    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,20}/ch\d+", ident):
        raise LibraryError(f"chapter {ident or '(blank)'} must look like M0/ch01")
    book = book_of(ident)
    if book not in books:
        raise LibraryError(f"chapter {ident} belongs to {book}, which is not in the library")
    presence = row["presence"].strip()
    if presence not in ("absent", "present", "retired"):
        raise LibraryError(f"bad presence on {ident}")
    editorial = _blank_status(row["editorial status"])
    if presence == "retired" and editorial:
        raise LibraryError(f"retired chapter {ident} cannot have a workflow status")
    if presence != "retired" and not editorial:
        raise LibraryError(f"chapter {ident} needs an editorial status")
    return {
        "id": ident,
        "book": book,
        "title": row["title"].strip(),
        "level": row["level"].strip(),
        "presence": presence,
        "editorial_status": editorial,
        "path": row["path"].strip(),
        "notes": row["notes"],
        "explain": row["what to explain"],
        "prereqs": _organization_prereqs(ident, row["prerequisites"]),
    }


def _book_record(row):
    code = _book_code(row["code"], "a book row")
    return {
        "code": code,
        "title": row["title"].strip(),
        "folder": row["folder"].strip(),
        "entry_level": row["entry level"].strip(),
        "target_level": row["target level"].strip(),
        "editorial_status": _blank_status(row["editorial status"]),
        "requires": _finish_codes(code, row["finish first"]),
        "notes": row["notes"].strip(),
    }


def _unique(rows, key, label):
    seen = []
    for row in rows:
        ident = row[key]
        if ident in seen:
            raise LibraryError(f"duplicate {label} {ident}")
        seen.append(ident)
    return seen


def import_chapter_changes(conn, text):
    """Apply an editorial organization change file. Returns a short summary."""
    if not is_chapter_changes(text):
        raise LibraryError("import an editorial organization change file")
    _preamble, sections = _preamble_and_sections(text)
    tables = {
        name: _checked_table(sections, name, columns)
        for name, columns, _note in CHAPTER_CHANGE_SECTIONS
    }
    existing = {row["code"] for row in conn.execute("SELECT code FROM books")}
    new_books = [_book_record(row) for row in tables["New books"]]
    edited_books = [_book_record(row) for row in tables["Edited books"]]
    deleted_books = [_book_code(row["code"], "a deleted book") for row in tables["Deleted books"]]
    new_codes = _unique(new_books, "code", "book")
    edited_codes = _unique(edited_books, "code", "book")
    if len(deleted_books) != len(set(deleted_books)):
        raise LibraryError("a deleted book is listed twice")
    overlap = (set(new_codes) & set(edited_codes)) | (set(new_codes) & set(deleted_books)) | (set(edited_codes) & set(deleted_books))
    if overlap:
        raise LibraryError("a book is listed in more than one of new, edited, and deleted: " + ", ".join(sorted(overlap)))
    missing_new = [code for code in new_codes if code in existing]
    if missing_new:
        raise LibraryError("new book already exists: " + ", ".join(missing_new))
    missing_edit = [code for code in edited_codes + deleted_books if code not in existing]
    if missing_edit:
        raise LibraryError("unknown book: " + ", ".join(missing_edit))
    for record in new_books + edited_books:
        if not record["title"]:
            raise LibraryError(f"{record['code']} needs a title")
        _require_status(conn, record["editorial_status"], set())
    library = (existing - set(deleted_books)) | set(new_codes)
    for record in new_books + edited_books:
        unknown = [code for code in record["requires"] if code not in library]
        if unknown:
            raise LibraryError(f"{record['code']} finish first names an unknown book: " + ", ".join(unknown))
    chapter_ids = {row["id"] for row in conn.execute("SELECT id FROM chapters")}
    new_chapters = [_chapter_record(row, library) for row in tables["New chapters"]]
    edited_chapters = [_chapter_record(row, library) for row in tables["Edited chapters"]]
    deleted_chapters = []
    for row in tables["Deleted chapters"]:
        ident = row["chapter"].strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9]{0,20}/ch\d+", ident):
            raise LibraryError(f"chapter {ident or '(blank)'} must look like M0/ch01")
        deleted_chapters.append(ident)
    new_ids = _unique(new_chapters, "id", "chapter")
    edited_ids = _unique(edited_chapters, "id", "chapter")
    if len(deleted_chapters) != len(set(deleted_chapters)):
        raise LibraryError("a deleted chapter is listed twice")
    overlap = (set(new_ids) & set(edited_ids)) | (set(new_ids) & set(deleted_chapters)) | (set(edited_ids) & set(deleted_chapters))
    if overlap:
        raise LibraryError("a chapter is listed in more than one of new, edited, and deleted: " + ", ".join(sorted(overlap)))
    already = [ident for ident in new_ids if ident in chapter_ids]
    if already:
        raise LibraryError("new chapter already exists: " + ", ".join(already))
    absent = [ident for ident in edited_ids + deleted_chapters if ident not in chapter_ids]
    if absent:
        raise LibraryError("unknown chapter: " + ", ".join(absent))
    deleted_book_set = set(deleted_books)
    for record in new_chapters + edited_chapters:
        if record["book"] in deleted_book_set:
            raise LibraryError(f"{record['id']} belongs to {record['book']}, which this file deletes")
        _require_status(conn, record["editorial_status"], set())
    if not (new_books or edited_books or deleted_books or new_chapters or edited_chapters or deleted_chapters):
        raise LibraryError("specify at least one new, edited, or deleted book or chapter")
    try:
        for record in new_books:
            conn.execute(
                "INSERT INTO books (code, title, folder, entry_level, target_level, editorial_status, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (record["code"], record["title"], record["folder"], record["entry_level"], record["target_level"],
                 record["editorial_status"] or None, record["notes"]),
            )
        for record in edited_books:
            conn.execute(
                "UPDATE books SET title = ?, folder = ?, entry_level = ?, target_level = ?, "
                "editorial_status = ?, notes = ? WHERE code = ?",
                (record["title"], record["folder"], record["entry_level"], record["target_level"],
                 record["editorial_status"] or None, record["notes"], record["code"]),
            )
        for record in new_books + edited_books:
            conn.execute("DELETE FROM book_requires WHERE book = ?", (record["code"],))
            for item in record["requires"]:
                conn.execute(
                    "INSERT INTO book_requires (book, requires) VALUES (?, ?)",
                    (record["code"], item),
                )
        for record in new_chapters:
            conn.execute(
                CHAPTER_INSERT,
                (record["id"], record["book"], record["title"], record["level"], record["presence"],
                 record["editorial_status"] or None, record["path"], record["notes"],
                 record["explain"]),
            )
        for record in edited_chapters:
            conn.execute(
                "UPDATE chapters SET title = ?, level = ?, presence = ?, editorial_status = ?, "
                "path = ?, notes = ?, explain = ? WHERE id = ?",
                (record["title"], record["level"], record["presence"], record["editorial_status"] or None,
                 record["path"], record["notes"], record["explain"], record["id"]),
            )
            conn.execute("DELETE FROM prereqs WHERE chapter = ?", (record["id"],))
        for record in new_chapters + edited_chapters:
            for target, kind in record["prereqs"]:
                conn.execute(
                    "INSERT INTO prereqs (chapter, target, kind) VALUES (?, ?, ?)",
                    (record["id"], target, kind),
                )
        for ident in deleted_chapters:
            conn.execute("DELETE FROM roadmap_steps WHERE target = ?", (ident,))
            conn.execute("DELETE FROM concept_links WHERE target = ?", (ident,))
            conn.execute("DELETE FROM chapters WHERE id = ?", (ident,))
        for code in deleted_books:
            conn.execute("DELETE FROM roadmap_steps WHERE target = ? OR target LIKE ?", (code, code + "/%"))
            conn.execute("DELETE FROM concept_links WHERE target = ? OR target LIKE ?", (code, code + "/%"))
            conn.execute("DELETE FROM roadmaps WHERE id = ?", (code,))
            conn.execute("DELETE FROM book_requires WHERE book = ? OR requires = ?", (code, code))
            conn.execute("DELETE FROM books WHERE code = ?", (code,))
        conn.execute(
            "DELETE FROM sources WHERE NOT EXISTS "
            "(SELECT 1 FROM source_books sb WHERE sb.source = sources.id)"
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise LibraryError(f"could not apply the editorial organization changes: {exc}") from exc
    bits = []
    for count, word in (
        (len(new_books), "new book"),
        (len(edited_books), "edited book"),
        (len(deleted_books), "deleted book"),
        (len(new_chapters), "new chapter"),
        (len(edited_chapters), "edited chapter"),
        (len(deleted_chapters), "deleted chapter"),
    ):
        if count:
            bits.append(f"{count} {word}" + ("s" if count != 1 else ""))
    return "Applied " + ", ".join(bits) + "."


def import_user_file(conn, text):
    """Import a book organization file or an editorial organization change file."""
    if is_book_organization(text):
        book = import_book_organization(conn, text)
        return f"{book} was updated."
    if is_chapter_changes(text):
        return import_chapter_changes(conn, text)
    raise LibraryError(
        "import a book organization file or an editorial organization change file. "
        "The full syllabus, internal references, and the reading order are not imported"
    )


def _decode_markdown(filename, raw):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".md", ".markdown"):
        raise LibraryError("choose a .md file")
    if not raw:
        raise LibraryError("the file is empty")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise LibraryError("file must be UTF-8") from exc


def _book_line(text):
    match = re.search(r"(?m)^book:\s*(\S+)\s*$", text)
    return match.group(1) if match else ""


def import_book_archive(conn, blob):
    """Replace every book whose organization file is in the zip."""
    try:
        archive = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile as exc:
        raise LibraryError("all books expects the book-organizations zip") from exc
    names = [name for name in archive.namelist() if not name.endswith("/")]
    if not names:
        raise LibraryError("the zip is empty")
    texts = []
    seen = []
    for name in names:
        if not name.lower().endswith((".md", ".markdown")):
            raise LibraryError(f"{name} is not a book organization file")
        try:
            text = archive.read(name).decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise LibraryError(f"{name} must be UTF-8") from exc
        if not is_book_organization(text):
            raise LibraryError(f"{name} is not a book organization file")
        code = _book_line(text)
        if not code:
            raise LibraryError(f"{name} needs a book line")
        if code in seen:
            raise LibraryError(f"{code} is in the zip more than once")
        seen.append(code)
        texts.append(text)
    return _import_book_texts(conn, texts)


def _import_book_texts(conn, texts):
    updated = []
    try:
        for text in texts:
            updated.append(import_book_organization(conn, text, commit=False))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return "Updated " + ", ".join(updated) + "."


def import_project_book(conn, root, code):
    """Replace one book from its organization file in the project."""
    if not code or code == "all":
        raise LibraryError("choose a book")
    name = organization_relpath(conn, code)
    path = organization_path(root, conn, code)
    if not os.path.isfile(path):
        raise LibraryError(f"{name} is not in the project")
    text = read_text(path)
    if not is_book_organization(text):
        raise LibraryError(f"{name} is not a book organization file")
    found = _book_line(text)
    if found != code:
        raise LibraryError(f"{name} is for {found or 'another book'}, not {code}")
    import_book_organization(conn, text)
    return f"{code} was updated."


def import_project_books(conn, root):
    """Replace every book from its organization file in the project."""
    missing = []
    texts = []
    for code in _ordered_book_codes(conn):
        name = organization_relpath(conn, code)
        path = organization_path(root, conn, code)
        if not os.path.isfile(path):
            missing.append(name)
            continue
        texts.append(read_text(path))
    if missing:
        raise LibraryError("missing organization file: " + ", ".join(missing))
    return _import_book_texts(conn, texts)


def import_chosen(conn, mode, book, filename, raw):
    """Import the file the user chose for one book, every book, or the chapter template."""
    if mode == "chapter":
        text = _decode_markdown(filename, raw)
        if not is_chapter_changes(text):
            raise LibraryError(
                "editorial organization import needs a chapter-changes file. "
                "Download the template, then list the new, edited, and deleted books and chapters"
            )
        return import_chapter_changes(conn, text)
    if mode != "book":
        raise LibraryError("choose book organization or editorial organization")
    if book == "all":
        if not filename.lower().endswith(".zip"):
            raise LibraryError("all books expects the book-organizations zip")
        if not raw:
            raise LibraryError("the file is empty")
        return import_book_archive(conn, raw)
    if not book:
        raise LibraryError("choose a book")
    text = _decode_markdown(filename, raw)
    if not is_book_organization(text):
        raise LibraryError(f"choose a book organization file for {book}")
    found = _book_line(text)
    if found != book:
        raise LibraryError(f"this file is for {found or 'another book'}, not {book}")
    import_book_organization(conn, text)
    return f"{book} was updated."


def _markdown_table_headers(body):
    for raw in body.split("\n"):
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell_in(c) for c in line.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):
            continue
        return cells
    return None


def _replace_section(text, heading, next_heading, replacement):
    start = text.find(heading)
    if start < 0:
        return text
    end = text.find("\n" + next_heading, start + len(heading))
    if end < 0:
        return text
    block = text[start:end]
    if "generated from `library.sqlite`" in block:
        return text
    return text[:start] + replacement.rstrip() + "\n\n" + text[end + 1:]


def retarget_roadmap(root):
    path = os.path.join(root, "ROADMAP.md")
    if not os.path.exists(path):
        return
    text = read_text(path).replace("\r\n", "\n")
    old = "The tables in this file are generated by `tools/gen_docs.py` (template: `tools/ROADMAP.template.md`)."
    new = (
        "Book dependencies are in [READING_ORDER.md](READING_ORDER.md), generated from `library.sqlite`. "
        "The narrative below is kept and is not regenerated."
    )
    text = text.replace(old, new)
    text = _replace_section(
        text,
        "## Document dependencies",
        "## Status",
        "## Document dependencies\n\n"
        "Book-to-book requirements are in [READING_ORDER.md](READING_ORDER.md), "
        "generated from `library.sqlite`.\n",
    )
    text = _replace_section(
        text,
        "## Status",
        "## Balance",
        "## Status\n\n"
        "Present, absent, and retired counts, and editorial status, are in "
        "[EDITORIAL_ORGANIZATION.md](EDITORIAL_ORGANIZATION.md), generated from `library.sqlite`.\n",
    )
    text = text.replace(
        "`python tools/restructure.py scaffold` | regenerates every `main.tex` from `tools/structure_config.py`",
        "`python UI.py layout` | creates missing book folders and renames chapter folders from `library.sqlite`",
    )
    text = text.replace(
        "`python tools/gen_docs.py` | regenerates this file's tables, EDITORIAL_ORGANIZATION.md, MIGRATION_LEDGER.md, sources_index.md",
        "`python UI.py` | reads `library.sqlite`; `gen_docs.py` no longer writes the syllabus or these dependency tables",
    )
    write_text(path, text)


def rewrite_readings(conn, root):
    write_text(os.path.join(root, "EDITORIAL_ORGANIZATION.md"), render_outline(conn))
    write_text(os.path.join(root, "READING_ORDER.md"), render_reading_guide(conn))
    retarget_roadmap(root)

__all__ = [name for name in globals() if not name.startswith('__')]
