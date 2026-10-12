"""Parse EDITORIAL_ORGANIZATION.md and seed the database."""

import os
import re
import sqlite3

from base import (
    BOOK_CODES,
    BOOK_ORDER,
    CHAPTER_INSERT,
    LibraryError,
    PART_TITLES,
    book_of,
    chapter_number,
    connect,
    db_path,
    extract_notes,
    id_sequence,
    init_db,
    link_targets,
    parse_folder,
    parse_prereq_cell,
    parse_status_cell,
    read_text,
    short_level,
    slugify,
    split_table_row,
    strip_links,
    tokens_of,
    write_text,
)

def parse_finish_first(book, text, chapters):
    """Return (set of required book codes, list of (chapter, target, kind))."""
    plain = tokens_of(text)
    plain = re.sub(r"\(transitively also[^)]*\)", "", plain)
    plain = re.sub(
        r"(?:«[^»]+»\s*(?:,|and)\s*)*«[^»]+»\s+for the chapters that list them",
        " ",
        plain,
    )
    edges = []
    blank = list(plain)
    for match in re.finditer(r"(?:only\s+)?for\b", plain):
        if plain[match.start():match.start() + 3] == "for" and "only for" not in plain[max(0, match.start() - 5):match.end()]:
            pass
        dst_region = plain[match.end():]
        dsts = []
        cursor = 0
        while True:
            token = re.match(r"\s*(?:,|and)?\s*«([^»]+)»", dst_region[cursor:])
            if not token:
                break
            if dsts and not re.match(r"\s*(?:,|and)", dst_region[cursor:]):
                break
            dsts.append(token.group(1))
            cursor += token.end()
        mod = None
        modifier = re.match(r"\s+(onward|respectively)\b", dst_region[cursor:])
        if modifier:
            mod = modifier.group(1)
            cursor += modifier.end()
        if not dsts:
            continue
        head = plain[:match.start()]
        srcs = []
        while True:
            token = re.search(
                r"((?:,|and)\s*)?«([^»]+)»(\s*\((?:optional|opt\.)\))?\s*$",
                head,
            )
            if not token or "/" not in token.group(2):
                break
            if srcs and not token.group(1):
                break
            srcs.append((token.group(2), bool(token.group(3))))
            head = head[:token.start()]
        srcs.reverse()
        if not srcs:
            continue
        span_start = len(head)
        span_end = match.end() + cursor
        for pos in range(span_start, min(span_end, len(blank))):
            blank[pos] = " "
        targets = dsts
        if mod == "onward" and len(dsts) == 1 and "/" in dsts[0]:
            targets = [
                ch["id"] for ch in chapters
                if ch["book"] == book_of(dsts[0]) and ch["presence"] != "retired"
                and chapter_number(ch["id"]) >= chapter_number(dsts[0])
            ]
        if mod == "respectively":
            pairs = list(zip(srcs, targets))
        else:
            pairs = [(src, dst) for src in srcs for dst in targets]
        for (src, optional), dst in pairs:
            if "/" not in str(dst):
                continue
            edges.append((dst, src, "optional" if optional else "hard"))
    leftover = "".join(blank)
    requires = set()
    for match in re.finditer(r"«([^»]+)»", leftover):
        ident = match.group(1)
        if ident in BOOK_CODES and ident != book:
            requires.add(ident)
    return requires, edges


def parse_syllabus(text):
    history_at = text.find("\n## Revision notes")
    history = text[history_at + 1:] if history_at >= 0 else ""
    body = text[:history_at] if history_at >= 0 else text
    topic_rows = _section_table(body, "## Topic ownership", "## Coverage of the requested topics")
    coverage_rows = _section_table(body, "## Coverage of the requested topics", "<a id=")
    books = []
    for match in re.finditer(r'<a id="[^"]+"></a>\s*\n+## ([A-Z0-9]+) (.+)\n', body):
        code, title = match.group(1), match.group(2).strip()
        start = match.end()
        nxt = re.search(r'\n<a id=', body[start:])
        block = body[start:start + nxt.start()] if nxt else body[start:]
        books.append(_parse_book(code, title, block))
    return {
        "history": history,
        "topics": topic_rows,
        "coverage": coverage_rows,
        "books": books,
    }


def _section_table(body, start_heading, end_marker):
    start = body.find(start_heading)
    if start < 0:
        return []
    rest = body[start:]
    end = rest.find(end_marker, len(start_heading))
    chunk = rest[:end] if end >= 0 else rest
    rows = []
    headers = None
    for line in chunk.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_table_row(line)
        if headers is None:
            headers = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") and c for c in cells):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def _parse_book(code, title, block):
    folder = ""
    entry = ""
    target = ""
    finish = ""
    notes = []
    chapters = []
    headers = None
    in_table = False
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Folder:"):
            folder = parse_folder(stripped)
            continue
        if stripped.startswith("- Entry level:"):
            both = stripped[2:].strip()
            match = re.search(r"Entry level:\s*(.*?)\s*Target level:\s*(.*)", both)
            if match:
                entry = short_level(match.group(1))
                target = short_level(match.group(2))
            notes.append(stripped[2:].strip())
            continue
        if stripped.startswith("- Finish first:"):
            finish = stripped.split(":", 1)[1].strip()
            notes.append(stripped[2:].strip())
            continue
        if stripped.startswith("- Chapters:"):
            continue
        if stripped.startswith("#"):
            headers = None
            in_table = False
            continue
        if stripped.startswith("|"):
            cells = split_table_row(stripped)
            if headers is None:
                headers = [c.lower() for c in cells]
                in_table = True
                continue
            if all(set(c) <= set("-: ") and c for c in cells):
                continue
            row = dict(zip(headers, cells))
            if "chapter" not in row:
                continue
            chapter_title, chapter_notes = extract_notes(row.get("title", ""))
            presence, status, path = parse_status_cell(row.get("status", ""))
            level = row.get("level reached", "").strip()
            if level in ("—", "-", "–"):
                level = ""
            chapters.append({
                "id": row["chapter"].strip(),
                "book": code,
                "title": chapter_title,
                "level": level,
                "presence": presence,
                "editorial_status": status,
                "path": path,
                "notes": chapter_notes,
                "prereqs": parse_prereq_cell(row.get("prerequisites", "")),
            })
            continue
        if in_table and stripped:
            notes.append(stripped)
        elif stripped.startswith("- "):
            notes.append(stripped[2:].strip())
        elif stripped and not stripped.startswith("#"):
            notes.append(stripped)
    if code == "GLOSSARY" and not entry:
        entry = target = "reference"
    return {
        "code": code,
        "title": title,
        "folder": folder,
        "entry_level": entry,
        "target_level": target,
        "finish": finish,
        "notes": "\n".join(notes),
        "chapters": chapters,
    }


def _part_record(part_id):
    book, _, label = part_id.partition("/part:")
    return {"id": part_id, "book": book, "title": PART_TITLES.get(label, label.replace("-", " ").title())}


def build_model(parsed):
    chapters = [ch for book in parsed["books"] for ch in book["chapters"]]
    by_id = {ch["id"]: ch for ch in chapters}
    parts = {}
    for pid, book in (
        ("M1/part:algebra", "M1"),
        ("M1/part:manifolds", "M1"),
        ("M1/part:integration", "M1"),
        ("M2/part:geometry", "M2"),
    ):
        if any(item["code"] == book for item in parsed["books"]):
            parts[pid] = _part_record(pid)
    prereqs = []
    for ch in chapters:
        seen = set()
        for target, kind in ch["prereqs"]:
            if target.startswith(tuple(f"{c}/part:" for c in BOOK_CODES)) or "/part:" in target:
                parts.setdefault(target, _part_record(target))
            key = (ch["id"], target)
            if key in seen:
                continue
            seen.add(key)
            prereqs.append({"chapter": ch["id"], "target": target, "kind": kind})
    book_requires = []
    seen_edges = {(row["chapter"], row["target"]) for row in prereqs}
    for book in parsed["books"]:
        if not book["finish"]:
            continue
        requires, edges = parse_finish_first(book["code"], book["finish"], chapters)
        for req in sorted(requires, key=lambda c: BOOK_ORDER.index(c) if c in BOOK_ORDER else 99):
            book_requires.append({"book": book["code"], "requires": req})
        for chapter, target, kind in edges:
            if "/part:" in target:
                parts.setdefault(target, _part_record(target))
            if (chapter, target) in seen_edges:
                continue
            if chapter not in by_id:
                continue
            seen_edges.add((chapter, target))
            prereqs.append({"chapter": chapter, "target": target, "kind": kind})
    concepts = []
    links = []
    used_slugs = set()
    for row in parsed["topics"]:
        title = row.get("topic", "").strip()
        if not title:
            continue
        slug = slugify(title)
        base = slug
        n = 2
        while slug in used_slugs:
            slug = f"{base}-{n}"
            n += 1
        used_slugs.add(slug)
        concepts.append({"slug": slug, "title": title})
        for target in link_targets(row.get("owner", ""), chapters):
            links.append({"concept": slug, "role": "owner", "target": target})
        for target in link_targets(row.get("referenced by", ""), chapters):
            links.append({"concept": slug, "role": "referenced_by", "target": target})
    roadmaps = []
    steps = []
    for book in parsed["books"]:
        roadmaps.append({
            "id": book["code"],
            "title": f"{book['code']} reading order",
            "notes": "",
        })
        position = 1
        for ch in book["chapters"]:
            if ch["presence"] == "retired":
                continue
            steps.append({"roadmap": book["code"], "position": position, "target": ch["id"]})
            position += 1
    for row in parsed["coverage"]:
        title = row.get("requested", "").strip()
        where = row.get("where", "").strip()
        if not title:
            continue
        slug = "coverage-" + slugify(title)
        base = slug
        n = 2
        while any(r["id"] == slug for r in roadmaps):
            slug = f"{base}-{n}"
            n += 1
        roadmaps.append({"id": slug, "title": title, "notes": strip_links(where)})
        position = 1
        for target in id_sequence(where, chapters):
            steps.append({"roadmap": slug, "position": position, "target": target})
            position += 1
    for book in parsed["books"]:
        present = any(ch["presence"] == "present" for ch in book["chapters"])
        if book["code"] == "GLOSSARY":
            book["editorial_status"] = "To Review"
        elif present:
            book["editorial_status"] = "To Review"
        else:
            book["editorial_status"] = "Idea"
    return {
        "books": parsed["books"],
        "parts": list(parts.values()),
        "chapters": chapters,
        "prereqs": prereqs,
        "book_requires": book_requires,
        "concepts": concepts,
        "concept_links": links,
        "roadmaps": roadmaps,
        "roadmap_steps": steps,
        "history": parsed["history"],
    }


def _validate_targets(model):
    chapter_ids = {ch["id"] for ch in model["chapters"]}
    part_ids = {p["id"] for p in model["parts"]}
    book_ids = {b["code"] for b in model["books"]}
    for row in model["prereqs"]:
        if row["target"] not in chapter_ids and row["target"] not in part_ids:
            raise LibraryError(f"prerequisite target {row['target']} of {row['chapter']} is unknown")
    for row in model["concept_links"]:
        if row["target"] not in chapter_ids and row["target"] not in book_ids:
            raise LibraryError(f"concept link target {row['target']} is unknown")
    for row in model["roadmap_steps"]:
        if row["target"] not in chapter_ids and row["target"] not in book_ids:
            raise LibraryError(f"roadmap step {row['target']} is unknown")
    for row in model["book_requires"]:
        if row["requires"] not in book_ids:
            raise LibraryError(f"{row['book']} requires unknown book {row['requires']}")


def insert_model(conn, model):
    _validate_targets(model)
    for book in model["books"]:
        conn.execute(
            "INSERT INTO books (code, title, folder, entry_level, target_level, editorial_status, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (book["code"], book["title"], book["folder"], book["entry_level"], book["target_level"],
             book["editorial_status"], book["notes"]),
        )
    for row in model["book_requires"]:
        conn.execute(
            "INSERT INTO book_requires (book, requires) VALUES (?, ?)",
            (row["book"], row["requires"]),
        )
    for row in model["parts"]:
        conn.execute(
            "INSERT INTO parts (id, book, title) VALUES (?, ?, ?)",
            (row["id"], row["book"], row["title"]),
        )
    for ch in model["chapters"]:
        conn.execute(
            CHAPTER_INSERT,
            (ch["id"], ch["book"], ch["title"], ch["level"], ch["presence"],
             ch["editorial_status"], ch["path"], ch["notes"], ch.get("explain") or ""),
        )
    for row in model["prereqs"]:
        conn.execute(
            "INSERT OR IGNORE INTO prereqs (chapter, target, kind) VALUES (?, ?, ?)",
            (row["chapter"], row["target"], row["kind"]),
        )
    for row in model["concepts"]:
        conn.execute("INSERT INTO concepts (slug, title) VALUES (?, ?)", (row["slug"], row["title"]))
    for row in model["concept_links"]:
        conn.execute(
            "INSERT OR IGNORE INTO concept_links (concept, role, target) VALUES (?, ?, ?)",
            (row["concept"], row["role"], row["target"]),
        )
    for row in model["roadmaps"]:
        conn.execute(
            "INSERT INTO roadmaps (id, title, notes) VALUES (?, ?, ?)",
            (row["id"], row["title"], row["notes"]),
        )
    for row in model["roadmap_steps"]:
        conn.execute(
            "INSERT INTO roadmap_steps (roadmap, position, target) VALUES (?, ?, ?)",
            (row["roadmap"], row["position"], row["target"]),
        )


def seed(root, syllabus=None):
    path = db_path(root)
    if os.path.exists(path):
        conn = connect(path)
        try:
            count = conn.execute("SELECT COUNT(*) AS c FROM books").fetchone()["c"]
        except sqlite3.OperationalError:
            count = 0
        conn.close()
        if count:
            raise LibraryError("database already has books; seed runs once")
        os.remove(path)
    syllabus = syllabus or os.path.join(root, "EDITORIAL_ORGANIZATION.md")
    text = read_text(syllabus)
    model = build_model(parse_syllabus(text))
    conn = init_db(path)
    try:
        insert_model(conn, model)
        conn.commit()
    except Exception:
        conn.close()
        if os.path.exists(path):
            os.remove(path)
        raise
    history_path = os.path.join(root, "EDITORIAL_ORGANIZATION_HISTORY.md")
    if model["history"].strip() and not os.path.exists(history_path):
        banner = (
            "# Editorial organization history\n\n"
            "Copied once from the hand-edited syllabus at seed time. "
            "This file is not regenerated.\n\n"
        )
        write_text(history_path, banner + model["history"].lstrip())
    from changes import rewrite_readings
    rewrite_readings(conn, root)
    conn.close()
    return path


__all__ = [name for name in globals() if not name.startswith('__')]
