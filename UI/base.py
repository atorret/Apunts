"""Shared constants, database schema, and markdown helpers."""

import os
import re
import sqlite3
BUILTIN_STATUSES = ("Idea", "To Design", "Building", "To Review", "Finished")
SOURCE_STATUSES = ("unplaced", "proposed", "approved", "merged", "cited, no file")
STATUS_RENAMES = {"To Build": "Building"}
BOOK_ORDER = [
    "M0", "M1", "M2", "M3", "CM1", "CM2", "CM3", "EM", "TH",
    "F1", "F2", "QM", "QFT", "GR", "GLOSSARY",
]
BOOK_CODES = set(BOOK_ORDER)
BOOK_ALT = "CM[1-3]|QFT|QM|EM|TH|F[12]|GR|GLOSSARY|M[0-3]"
CHAPTER_RE = re.compile(rf"(?:{BOOK_ALT})/ch\d+")
ID_RE = re.compile(rf"(?:{CHAPTER_RE.pattern}|(?:{BOOK_ALT}))")

TABLES = {
    "statuses": ["name", "position"],
    "books": ["code", "title", "folder", "entry_level", "target_level", "editorial_status", "notes"],
    "book_requires": ["book", "requires"],
    "parts": ["id", "book", "title"],
    "chapters": ["id", "book", "title", "level", "presence", "editorial_status", "path", "notes", "explain"],
    "prereqs": ["chapter", "target", "kind"],
    "concepts": ["slug", "title"],
    "concept_links": ["concept", "role", "target"],
    "roadmaps": ["id", "title", "notes"],
    "roadmap_steps": ["roadmap", "position", "target"],
    "sources": ["id", "file", "proposed_chapter", "status", "reference", "document", "position"],
    "source_books": ["source", "book"],
}
LIBRARY_TABLES = [
    "statuses", "books", "book_requires", "parts", "chapters", "prereqs",
    "concepts", "concept_links", "roadmaps", "roadmap_steps",
]
BOOK_TABLES = ["books", "parts", "chapters", "prereqs", "roadmaps", "roadmap_steps"]
CHAPTER_TABLES = ["chapters", "prereqs"]

DOCUMENTS = [
    ("M0", "M0-math-basics", "M0"),
    ("M1", "M1-math-foundations", "M1"),
    ("M2", "M2-math-advanced", "M2"),
    ("M3", "M3-math-differential-equations", "M3"),
    ("CM1", "CM1-classical-mechanics-1", "CM1"),
    ("CM2", "CM2-classical-mechanics-2", "CM2"),
    ("CM3", "CM3-elasticity", "CM3"),
    ("EM", "EM-electrodynamics", "EM"),
    ("TH", "TH-thermo-statmech", "TH"),
    ("F1", "F1-fluids-classical", "F1"),
    ("F2", "F2-fluids-complex-extreme", "F2"),
    ("QM", "QM-quantum-mechanics", "QM"),
    ("QFT", "QFT-quantum-field-theory", "QFT"),
    ("GR", "GR-general-relativity", "GR"),
    ("GLOSSARY", "GLOSSARY", "GLOSSARY"),
    ("unsorted", "unsorted", "UNSORTED"),
]
FOLDER_OF = {code: folder for code, folder, _job in DOCUMENTS}
PART_TITLES = {
    "algebra": "Algebra",
    "manifolds": "Manifolds",
    "integration": "Integration",
    "geometry": "Geometry",
}

SCHEMA = """
CREATE TABLE statuses (
    name TEXT PRIMARY KEY,
    position INTEGER NOT NULL,
    builtin INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE books (
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    folder TEXT NOT NULL DEFAULT '',
    entry_level TEXT NOT NULL DEFAULT '',
    target_level TEXT NOT NULL DEFAULT '',
    editorial_status TEXT REFERENCES statuses(name),
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE book_requires (
    book TEXT NOT NULL REFERENCES books(code) ON DELETE CASCADE,
    requires TEXT NOT NULL REFERENCES books(code),
    PRIMARY KEY (book, requires)
);
CREATE TABLE parts (
    id TEXT PRIMARY KEY,
    book TEXT NOT NULL REFERENCES books(code) ON DELETE CASCADE,
    title TEXT NOT NULL
);
CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    book TEXT NOT NULL REFERENCES books(code) ON DELETE CASCADE,
    title TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT '',
    presence TEXT NOT NULL CHECK (presence IN ('absent', 'present', 'retired')),
    editorial_status TEXT REFERENCES statuses(name),
    path TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    explain TEXT NOT NULL DEFAULT ''
);
CREATE TABLE prereqs (
    chapter TEXT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    target TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('hard', 'optional')),
    PRIMARY KEY (chapter, target, kind)
);
CREATE TABLE concepts (
    slug TEXT PRIMARY KEY,
    title TEXT NOT NULL
);
CREATE TABLE concept_links (
    concept TEXT NOT NULL REFERENCES concepts(slug) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('owner', 'referenced_by')),
    target TEXT NOT NULL,
    PRIMARY KEY (concept, role, target)
);
CREATE TABLE roadmaps (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE roadmap_steps (
    roadmap TEXT NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    target TEXT NOT NULL,
    PRIMARY KEY (roadmap, position)
);
"""

XREF_SCHEMA = """
CREATE TABLE xref_summary (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    dup_labels INTEGER NOT NULL,
    unresolved INTEGER NOT NULL,
    bad_cites INTEGER NOT NULL,
    prereq_gaps INTEGER NOT NULL
);
CREATE TABLE xref_builds (
    position INTEGER PRIMARY KEY,
    doc TEXT NOT NULL,
    folder TEXT NOT NULL,
    job TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE xref_refs (
    id INTEGER PRIMARY KEY,
    source_file TEXT NOT NULL,
    line INTEGER NOT NULL,
    command TEXT NOT NULL,
    label TEXT NOT NULL,
    source_doc TEXT NOT NULL,
    target_doc TEXT NOT NULL,
    target_id TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('back', 'forward', 'reference'))
);
CREATE TABLE xref_problems (
    position INTEGER PRIMARY KEY,
    message TEXT NOT NULL
);
"""

SOURCE_SCHEMA = """
CREATE TABLE sources (
    id TEXT PRIMARY KEY,
    file TEXT NOT NULL DEFAULT 'none',
    proposed_chapter TEXT NOT NULL DEFAULT '-',
    status TEXT NOT NULL DEFAULT 'unplaced',
    reference TEXT NOT NULL DEFAULT '',
    document TEXT NOT NULL DEFAULT '',
    position INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE source_books (
    source TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    book TEXT NOT NULL REFERENCES books(code) ON DELETE CASCADE,
    PRIMARY KEY (source, book)
);
"""

SCHEMA += XREF_SCHEMA + SOURCE_SCHEMA

CHAPTER_INSERT = (
    "INSERT INTO chapters (id, book, title, level, presence, editorial_status, path, notes, explain) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
)


class LibraryError(Exception):
    pass


def default_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def db_path(root):
    return os.path.join(root, "library.sqlite")


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate_status_renames(conn):
    for old, new in STATUS_RENAMES.items():
        if not conn.execute("SELECT 1 FROM statuses WHERE name = ?", (old,)).fetchone():
            continue
        if conn.execute("SELECT 1 FROM statuses WHERE name = ?", (new,)).fetchone():
            conn.execute(
                "UPDATE books SET editorial_status = ? WHERE editorial_status = ?", (new, old)
            )
            conn.execute(
                "UPDATE chapters SET editorial_status = ? WHERE editorial_status = ?", (new, old)
            )
            conn.execute("DELETE FROM statuses WHERE name = ?", (old,))
        else:
            conn.execute(
                "UPDATE books SET editorial_status = ? WHERE editorial_status = ?", (new, old)
            )
            conn.execute(
                "UPDATE chapters SET editorial_status = ? WHERE editorial_status = ?", (new, old)
            )
            conn.execute("UPDATE statuses SET name = ? WHERE name = ?", (new, old))
    conn.commit()


def open_db(root):
    path = db_path(root)
    if not os.path.exists(path):
        raise LibraryError("no library.sqlite; run: python UI.py seed")
    conn = connect(path)
    _migrate_status_renames(conn)
    ensure_chapter_explain(conn)
    ensure_xref_tables(conn)
    ensure_source_tables(conn)
    from xref import seed_sources
    seed_sources(conn, root)
    return conn


def ensure_chapter_explain(conn):
    """Add the teaching-brief column to a database created before it existed."""
    cols = [row[1] for row in conn.execute("PRAGMA table_info(chapters)")]
    if "explain" in cols:
        return
    conn.execute("ALTER TABLE chapters ADD COLUMN explain TEXT NOT NULL DEFAULT ''")
    conn.commit()


def ensure_xref_tables(conn):
    """Add the cross-reference tables to a database created before they existed."""
    present = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'xref_refs'"
    ).fetchone()
    if present:
        return
    conn.executescript(XREF_SCHEMA)
    conn.commit()


def ensure_source_tables(conn):
    """Add the source tables to a database created before they existed."""
    present = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'sources'"
    ).fetchone()
    if present:
        return
    conn.executescript(SOURCE_SCHEMA)
    conn.commit()


def init_db(path):
    conn = connect(path)
    conn.executescript(SCHEMA)
    for i, name in enumerate(BUILTIN_STATUSES, start=1):
        conn.execute(
            "INSERT INTO statuses (name, position, builtin) VALUES (?, ?, 1)",
            (name, i),
        )
    conn.commit()
    return conn


def chapter_number(chapter_id):
    return int(chapter_id.rsplit("/ch", 1)[1])


def book_of(ref):
    return ref.split("/")[0]


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:80] or "item"


def folder_slug(dirname):
    match = re.match(r"ch\d+-(.+)", dirname)
    return match.group(1) if match else None


def cell_out(value):
    text = "" if value is None else str(value)
    text = text.replace("|", "/")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\n", "<br>")


def cell_in(value):
    return value.replace("<br>", "\n").strip()


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell_out(row.get(h, "")) for h in headers) + " |")
    return lines


def parse_md_tables(text):
    """Return (preamble_lines, {heading: [dict]}) from one strict file."""
    if "import: refused" in text.splitlines()[:8]:
        raise LibraryError("import refused: this file is a filtered report")
    lines = text.replace("\r\n", "\n").split("\n")
    scope = None
    tables = {}
    heading = None
    headers = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("scope:"):
            scope = line.split(":", 1)[1].strip()
            continue
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            headers = None
            tables.setdefault(heading, [])
            continue
        if not line.startswith("|"):
            raise LibraryError(f"unexpected line in strict file: {line}")
        cells = [cell_in(c) for c in line.strip().strip("|").split("|")]
        if headers is None:
            if all(set(c) <= set("-: ") and c for c in cells):
                continue
            headers = cells
            continue
        if all(set(c) <= set("-: ") and c for c in cells):
            continue
        if len(cells) != len(headers):
            raise LibraryError(f"row in {heading} has {len(cells)} cells, expected {len(headers)}")
        tables[heading].append(dict(zip(headers, cells)))
    if not scope:
        raise LibraryError("strict file needs a scope line")
    return scope, tables


def write_text(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def read_text(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


# --- syllabus seed -------------------------------------------------------

def strip_links(text):
    return re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)


def short_level(text):
    text = strip_links(text).strip().rstrip(".")
    text = re.sub(r"\s*\(.*$", "", text).strip()
    return text


def split_table_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def extract_notes(title):
    notes = []

    def grab(match):
        notes.append(match.group(1).strip())
        return ""

    title = re.sub(r"\*\((?:note|optional enrichment):\s*(.*?)\)\*", grab, title)
    title = re.sub(r"\s+", " ", title).strip()
    return title, " ".join(notes)


def parse_prereq_cell(cell):
    cell = cell.strip()
    if cell in ("", "none", "—", "-", "–"):
        return []
    found = []
    for part in cell.split(";"):
        optional = bool(re.search(r"\(opt\.\)|\(optional\)", part))
        for match in re.finditer(r"([A-Z0-9]+) Part intro `part:([^`]+)`", part):
            found.append((f"{match.group(1)}/part:{match.group(2)}", "optional" if optional else "hard"))
        for match in re.finditer(r"\[([^\]]+)\]", part):
            target = re.sub(r"\s*\(.*\)\s*$", "", match.group(1)).strip()
            if target and target not in ("none",):
                found.append((target, "optional" if optional else "hard"))
    return found


def parse_status_cell(cell):
    cell = cell.strip()
    if cell.startswith("TODO"):
        return "absent", "Idea", ""
    if cell.startswith("present:"):
        match = re.search(r"\(([^)]+)\)", cell)
        path = match.group(1).strip().rstrip("/") if match else ""
        return "present", "To Review", path
    if cell.startswith("moved:"):
        return "retired", None, ""
    raise LibraryError(f"unrecognised status cell: {cell}")


def parse_folder(line):
    match = re.search(r"Folder:\s*(?:\[([^\]]+)\]\([^)]*\)|([A-Za-z0-9_./-]+))", line)
    if not match:
        return ""
    raw = match.group(1) or match.group(2)
    return raw.strip().rstrip("/")


def expand_range(start, end, chapters):
    if book_of(start) != book_of(end):
        return [start, end]
    lo, hi = chapter_number(start), chapter_number(end)
    if lo > hi:
        lo, hi = hi, lo
    chosen = [
        ch["id"] for ch in chapters
        if ch["book"] == book_of(start)
        and ch["presence"] != "retired"
        and lo <= chapter_number(ch["id"]) <= hi
    ]
    return chosen or [start, end]


def tokens_of(text):
    """Replace markdown links with «id» and return the plain string."""
    def repl(match):
        ident = re.sub(r"\s*\(.*\)\s*$", "", match.group(1)).strip()
        return f"«{ident}»"
    return re.sub(r"\[([^\]]+)\]\([^)]*\)", repl, text)


def id_sequence(text, chapters):
    """Chapter and book ids in order. A same-book 'A to B' expands."""
    plain = tokens_of(text)
    matches = list(re.finditer(r"«([^»]+)»", plain))
    # also bare chapter ids that were not linked
    bare = list(re.finditer(CHAPTER_RE, plain))
    marks = [(m.start(), m.end(), m.group(1)) for m in matches]
    occupied = [(m.start(), m.end()) for m in matches]
    for match in bare:
        if any(a <= match.start() < b for a, b in occupied):
            continue
        marks.append((match.start(), match.end(), match.group(0)))
    marks.sort()
    steps = []
    index = 0
    while index < len(marks):
        ident = marks[index][2]
        if index + 1 < len(marks):
            between = plain[marks[index][1]:marks[index + 1][0]]
            nxt = marks[index + 1][2]
            if (re.search(r"\bto\b", between) and "/" in ident and "/" in nxt
                    and book_of(ident) == book_of(nxt)):
                for step in expand_range(ident, nxt, chapters):
                    if step not in steps:
                        steps.append(step)
                index += 2
                continue
        if ident == "all documents":
            for code in BOOK_ORDER:
                if code not in steps:
                    steps.append(code)
        elif ident not in steps:
            steps.append(ident)
        index += 1
    return steps


def link_targets(cell, chapters, role_expand=True):
    if not cell.strip():
        return []
    if re.search(r"all documents", cell, re.I):
        return list(BOOK_ORDER)
    return id_sequence(cell, chapters) if role_expand else []

__all__ = [name for name in globals() if not name.startswith('__')]
