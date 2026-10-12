"""Records and filters for the library browser."""

from base import (
    BOOK_ORDER,
)
from exchange import (
    _rows,
)

def page_data(conn, filters):
    book = (filters.get("book") or [""])[0]
    presence = (filters.get("presence") or [""])[0]
    status = (filters.get("status") or [""])[0]
    level = (filters.get("level") or [""])[0]
    query = (filters.get("q") or [""])[0].strip().lower()
    chapters = _rows(conn, "SELECT * FROM chapters ORDER BY book, id")
    books = _rows(conn, "SELECT * FROM books")
    books.sort(key=lambda b: BOOK_ORDER.index(b["code"]) if b["code"] in BOOK_ORDER else 99)

    def show_chapter(ch):
        if book and ch["book"] != book:
            return False
        if presence and ch["presence"] != presence:
            return False
        if status and (ch["editorial_status"] or "") != status:
            return False
        if level and ch["level"] != level:
            return False
        if query and query not in (
            ch["title"] + " " + ch["id"] + " " + (ch["notes"] or "") + " " + (ch["explain"] or "")
        ).lower():
            return False
        return True

    def show_book(item):
        if book and item["code"] != book:
            return False
        if status and (item["editorial_status"] or "") != status:
            return False
        if presence or level:
            return False
        if query and query not in (item["title"] + " " + item["code"] + " " + (item["notes"] or "")).lower():
            return False
        return True

    parts = _rows(conn, "SELECT id, book, title FROM parts ORDER BY id")
    concepts = _rows(conn, "SELECT * FROM concepts ORDER BY title")
    links = _rows(conn, "SELECT * FROM concept_links ORDER BY concept, role, target")
    roadmaps = _rows(conn, "SELECT * FROM roadmaps ORDER BY id")
    steps = _rows(conn, "SELECT roadmap, position, target FROM roadmap_steps ORDER BY roadmap, position")
    chapter_by_id = {ch["id"]: ch for ch in chapters}

    def show_part(item):
        if book and item["book"] != book:
            return False
        if presence or status or level:
            return False
        blob = item["title"] + " " + item["id"]
        return not query or query in blob.lower()

    def show_concept(item):
        if book or presence or level or status:
            return False
        blob = item["title"] + " " + item["slug"]
        return not query or query in blob.lower()

    def show_roadmap(item):
        targets = [step["target"] for step in steps if step["roadmap"] == item["id"]]
        if book and item["id"] != book and book not in targets and not any(
            target.startswith(book + "/") for target in targets
        ):
            return False
        if presence or status or level:
            matched = False
            for target in targets:
                ch = chapter_by_id.get(target)
                if not ch:
                    continue
                if presence and ch["presence"] != presence:
                    continue
                if status and (ch["editorial_status"] or "") != status:
                    continue
                if level and ch["level"] != level:
                    continue
                matched = True
                break
            if not matched:
                return False
        blob = item["title"] + " " + item["id"] + " " + (item["notes"] or "") + " " + " ".join(targets)
        return not query or query in blob.lower()

    level_options = sorted({
        *(ch["level"] for ch in chapters if ch["level"]),
        *(b["entry_level"] for b in books if b["entry_level"]),
        *(b["target_level"] for b in books if b["target_level"]),
    })

    return {
        "statuses": _rows(conn, "SELECT name, position FROM statuses ORDER BY position, name"),
        "level_options": level_options,
        "books": books,
        "requires": _rows(conn, "SELECT book, requires FROM book_requires ORDER BY book, requires"),
        "chapters": chapters,
        "prereqs": _rows(conn, "SELECT chapter, target, kind FROM prereqs ORDER BY chapter, target"),
        "parts": parts,
        "roadmaps": roadmaps,
        "steps": steps,
        "concepts": concepts,
        "links": links,
        "visible": {
            "books": [b["code"] for b in books if show_book(b)],
            "parts": [p["id"] for p in parts if show_part(p)],
            "chapters": [c["id"] for c in chapters if show_chapter(c)],
            "concepts": [c["slug"] for c in concepts if show_concept(c)],
            "roadmaps": [r["id"] for r in roadmaps if show_roadmap(r)],
        },
        "filters": {"book": book, "presence": presence, "status": status, "level": level, "q": query},
    }

__all__ = [name for name in globals() if not name.startswith('__')]
