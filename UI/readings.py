"""Editorial organization, reading order, and book organization files."""

import io
import os
import re
import zipfile

from base import (
    BOOK_CODES,
    BOOK_ORDER,
    FOLDER_OF,
    LibraryError,
    SOURCE_STATUSES,
    cell_in,
    chapter_number,
    md_table,
)
from exchange import (
    _rows,
)

def _note_inline(notes):
    text = (notes or "").replace("\n", " ").strip()
    return f" *({text})*" if text else ""


def render_outline(conn):
    lines = [
        "# Editorial organization",
        "",
        "The reading order that takes each document from its entry level to its target level. "
        "This file is generated from `library.sqlite`. Edit a book by importing its organization file, "
        "or import an editorial organization change file that names the new, edited, and deleted books and chapters. "
        "Either import rewrites this file. Editorial status can also be set in the browser. "
        "Sources are listed under each book. Edit them in that book's organization file. "
        "Book dependencies are listed under each book. Edit which books must be finished first "
        "in that book's organization file, or in an editorial organization change file. "
        "The hand-edited revision log is in [EDITORIAL_ORGANIZATION_HISTORY.md](EDITORIAL_ORGANIZATION_HISTORY.md).",
        "",
        "- **Present** chapters are existing material. The path is the chapter folder.",
        "- **Absent** chapters are named steps with no content yet (`TODO(DOC/chNN)`).",
        "- **Retired** rows keep a chapter number whose text now lives somewhere else.",
        "- Levels: basic, undergraduate, graduate, postdoc/research.",
        "- An optional prerequisite is marked *(opt.)*. Unmarked prerequisites are hard.",
        "- Editorial status is separate from presence: Idea, To Design, Building, To Review, Finished, "
        "or a registered custom name.",
        "",
        "Documents: " + ", ".join(f"[{code}](#{code.lower()})" for code in BOOK_ORDER) + ".",
        "",
        "## Level scale",
        "",
        "- **basic**: first-year material with no previous course assumed.",
        "- **undergraduate**: standard degree-course material.",
        "- **graduate**: first-year graduate courses.",
        "- **postdoc/research**: topics at the research frontier.",
        "",
        "## Topic ownership",
        "",
        "A topic lists every chapter or book that owns it, and every chapter or book that only references it.",
        "",
    ]
    concepts = _rows(conn, "SELECT slug, title FROM concepts ORDER BY title")
    header = ["topic", "owner", "referenced by"]
    topic_rows = []
    for concept in concepts:
        owners = _rows(
            conn,
            "SELECT target FROM concept_links WHERE concept = ? AND role = 'owner' ORDER BY target",
            (concept["slug"],),
        )
        refs = _rows(
            conn,
            "SELECT target FROM concept_links WHERE concept = ? AND role = 'referenced_by' ORDER BY target",
            (concept["slug"],),
        )
        topic_rows.append({
            "topic": concept["title"],
            "owner": ", ".join(_md_ref(r["target"]) for r in owners),
            "referenced by": ", ".join(_md_ref(r["target"]) for r in refs),
        })
    lines.extend(md_table(header, topic_rows))
    lines += ["", "## Coverage of the requested topics", ""]
    coverage = _rows(conn, "SELECT id, title, notes FROM roadmaps WHERE id LIKE 'coverage-%' ORDER BY title")
    cov_rows = []
    for road in coverage:
        steps = _rows(
            conn,
            "SELECT target FROM roadmap_steps WHERE roadmap = ? ORDER BY position",
            (road["id"],),
        )
        where = road["notes"] or ", ".join(_md_ref(s["target"]) for s in steps)
        cov_rows.append({"requested": road["title"], "where": where})
    lines.extend(md_table(["requested", "where"], cov_rows))
    lines.append("")
    books = _rows(conn, "SELECT * FROM books")
    books.sort(key=lambda b: BOOK_ORDER.index(b["code"]) if b["code"] in BOOK_ORDER else 99)
    for book in books:
        lines += [f'<a id="{book["code"].lower()}"></a>', "", f"## {book['code']} {book['title']}", ""]
        if book["folder"]:
            lines.append(f"- Folder: [{book['folder']}/]({book['folder']}/)")
        if book["entry_level"] or book["target_level"]:
            lines.append(f"- Entry level: {book['entry_level']}. Target level: {book['target_level']}.")
        reqs = _rows(conn, "SELECT requires FROM book_requires WHERE book = ? ORDER BY requires", (book["code"],))
        if reqs:
            lines.append("- Finish first: " + ", ".join(_md_ref(r["requires"]) for r in reqs))
        lines.append(f"- Editorial status: {book['editorial_status'] or '—'}")
        if book["notes"]:
            for note_line in book["notes"].splitlines():
                if note_line.strip():
                    lines.append(f"- {note_line.strip()}")
        chapters = _rows(conn, "SELECT * FROM chapters WHERE book = ? ORDER BY id", (book["code"],))
        present = sum(1 for ch in chapters if ch["presence"] == "present")
        absent = sum(1 for ch in chapters if ch["presence"] == "absent")
        retired = sum(1 for ch in chapters if ch["presence"] == "retired")
        lines.append(
            f"- Chapters: {len(chapters)} planned, {present} present, {absent} absent, {retired} retired."
        )
        lines.append("")
        rows = []
        for ch in chapters:
            pres = _rows(
                conn,
                "SELECT target, kind FROM prereqs WHERE chapter = ? ORDER BY target",
                (ch["id"],),
            )
            if not pres:
                pre_text = "none" if ch["presence"] != "retired" else "—"
            else:
                bits = []
                for pre in pres:
                    label = _md_ref(pre["target"]) if not pre["target"].endswith(tuple()) else pre["target"]
                    if "/part:" in pre["target"]:
                        book_code, _, label_name = pre["target"].partition("/part:")
                        label = f"{book_code} Part intro `part:{label_name}`"
                    else:
                        label = _md_ref(pre["target"])
                    if pre["kind"] == "optional":
                        label += " (opt.)"
                    bits.append(label)
                pre_text = "; ".join(bits)
            if ch["presence"] == "present" and ch["path"]:
                status = f"present: [{ch['path']}/]({ch['path']}/)"
            elif ch["presence"] == "absent":
                status = f"TODO({ch['id']})"
            else:
                status = "moved"
            status += f"; {ch['editorial_status'] or '—'}"
            rows.append({
                "chapter": ch["id"],
                "title": ch["title"] + _note_inline(ch["notes"]),
                "level reached": ch["level"] or "—",
                "prerequisites": pre_text,
                "editorial status": ch["editorial_status"] or "—",
                "status": status,
            })
        lines.extend(md_table(
            ["chapter", "title", "level reached", "prerequisites", "editorial status", "status"],
            rows,
        ))
        lines.extend(render_outline_dependencies(conn, book["code"], reqs))
        sources = book_source_rows(conn, book["code"])
        if sources:
            rel = organization_relpath(conn, book["code"])
            lines += [
                "",
                "### Sources",
                "",
                f"Edited in [{rel}]({rel}).",
                "",
            ]
            lines.extend(md_table(
                ["ID", "file", "proposed chapter", "status", "reference"],
                [
                    {
                        "ID": item["id"],
                        "file": item["file"],
                        "proposed chapter": item["proposed_chapter"],
                        "status": item["status"],
                        "reference": item["reference"],
                    }
                    for item in sources
                ],
            ))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _md_ref(ident):
    if ident in BOOK_CODES:
        return f"[{ident}](#{ident.lower()})"
    if "/" in ident and ident.split("/")[0] in BOOK_CODES:
        return f"[{ident}](#{ident.split('/')[0].lower()})"
    return ident


def _xml(text):
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _num(value):
    text = f"{float(value):.1f}"
    return text[:-2] if text.endswith(".0") else text


def _short(text, limit):
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _title_lines(text, limit=26):
    words = " ".join((text or "").split()).split()
    if not words:
        return [""]
    lines, cur = [], ""
    for word in words:
        piece = word if len(word) <= limit else _short(word, limit)
        trial = piece if not cur else cur + " " + piece
        if len(trial) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = piece
    if cur:
        lines.append(cur)
    if len(lines) > 2:
        lines = [lines[0], _short(lines[1], limit)]
    return lines


def _order_layers(layers, edges, order):
    """Put each book's neighbours nearer to it, so arrows cross less often."""
    preds, succs = {}, {}
    for src, dst in edges:
        succs.setdefault(src, []).append(dst)
        preds.setdefault(dst, []).append(src)
    ranks = sorted(layers)
    index = {}

    def reindex():
        index.clear()
        for rank in ranks:
            for i, code in enumerate(layers[rank]):
                index[code] = i

    def bary(code, neighbors, positions):
        vals = [positions[item] for item in neighbors if item in positions]
        if not vals:
            return positions.get(code, 0)
        return sum(vals) / len(vals)

    reindex()
    for _ in range(4):
        for rank in ranks:
            layers[rank].sort(key=lambda code: (bary(code, preds.get(code, []), index), order.get(code, 99), code))
            reindex()
        for rank in reversed(ranks):
            layers[rank].sort(key=lambda code: (bary(code, succs.get(code, []), index), order.get(code, 99), code))
            reindex()
    # A last pass uses only the previous column. Ties keep the order already chosen,
    # so a book is not pulled upward by a link that skips a column.
    rank_of = {code: rank for rank in ranks for code in layers[rank]}
    place = {rank: i for i, rank in enumerate(ranks)}
    snapshot = dict(index)
    for rank in ranks:
        prev = ranks[place[rank] - 1] if place[rank] else None
        layers[rank].sort(
            key=lambda code, prev=prev: (
                bary(
                    code,
                    [item for item in preds.get(code, []) if prev is not None and rank_of.get(item) == prev],
                    snapshot,
                ),
                snapshot.get(code, 0),
                code,
            )
        )
    reindex()


def _reading_paths(positions, heights, edges, ranks, box_w, content_bottom):
    """Arrow paths. Neighbouring columns meet in the gap. A longer arrow uses the nearest open row.

    An open row is a horizontal line that misses every book in the columns it crosses,
    including the space between two books. positions maps a code to (x, y).
    ranks maps a code to its column number.
    Returns (path data, extra height under the books).
    """
    present = [item for item in edges if item[0] in positions and item[1] in positions]
    rank_list = sorted(set(ranks.values()))
    rank_at = {rank: i for i, rank in enumerate(rank_list)}
    short, long = [], []
    for src, dst in present:
        span = rank_at.get(ranks.get(dst), 0) - rank_at.get(ranks.get(src), 0)
        if span < 1:
            continue
        (short if span == 1 else long).append((src, dst))

    def port_y(group, side):
        buckets = {}
        for src, dst in group:
            buckets.setdefault(src if side == "out" else dst, []).append((src, dst))
        found = {}
        for key, items in buckets.items():
            other = 1 if side == "out" else 0
            items.sort(key=lambda item: positions[item[other]][1])
            top, height = positions[key][1], heights[key]
            count = len(items)
            for i, item in enumerate(items):
                if count == 1:
                    found[item] = top + height / 2
                else:
                    margin = min(12, height / 4)
                    found[item] = top + margin + (height - 2 * margin) * i / (count - 1)
        return found

    both = short + long
    leave_y = port_y(both, "out")
    enter_y = port_y(both, "in")
    paths = []
    for src, dst in short:
        x1 = positions[src][0] + box_w
        y1 = leave_y[(src, dst)]
        x2 = positions[dst][0]
        y2 = enter_y[(src, dst)]
        mid = (x1 + x2) / 2
        paths.append(
            f"M {_num(x1)} {_num(y1)} C {_num(mid)} {_num(y1)}, {_num(mid)} {_num(y2)}, {_num(x2)} {_num(y2)}"
        )

    clearance = 6
    lane_gap = 11
    low_bound = 8
    high_bound = content_bottom + 12 + max(len(long), 1) * lane_gap + 8

    def free_rows(blockers):
        spans = []
        for top, bottom in blockers:
            start = top - clearance
            end = bottom + clearance
            if end > low_bound and start < high_bound:
                spans.append((max(start, low_bound), min(end, high_bound)))
        spans.sort()
        merged = []
        for start, end in spans:
            if end <= start:
                continue
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)
        free = []
        cursor = low_bound
        for start, end in merged:
            if start - cursor >= 3:
                free.append((cursor, start))
            cursor = max(cursor, end)
        if high_bound - cursor >= 3:
            free.append((cursor, high_bound))
        return free

    def nearest_row(free, y1, y2):
        lo, hi = (y1, y2) if y1 <= y2 else (y2, y1)
        mid = (y1 + y2) / 2
        if not free:
            return max(mid, content_bottom + 12)
        best_y, best_key = mid, None
        for start, end in free:
            if end < lo:
                y, cost = end, lo - end
            elif start > hi:
                y, cost = start, start - hi
            else:
                left = max(start, lo)
                right = min(end, hi)
                y, cost = min(max(mid, left), right), 0
            key = (cost, abs(y - mid))
            if best_key is None or key < best_key:
                best_y, best_key = y, key
        return best_y

    def place_row(ideal, free, taken):
        def legal(y):
            if not any(start <= y <= end for start, end in free):
                return False
            return all(abs(y - other) >= lane_gap - 0.01 for other in taken)

        if legal(ideal):
            return ideal
        for step in range(1, 500):
            for y in (ideal - step, ideal + step):
                if legal(y):
                    return y
        if not free:
            return ideal
        start, end = min(
            free,
            key=lambda span: span[0] - ideal if ideal < span[0] else ideal - span[1] if ideal > span[1] else 0,
        )
        return min(max(ideal, start), end)

    by_rank = {}
    for code, rank in ranks.items():
        if code in positions:
            by_rank.setdefault(rank, []).append(code)
    channels = {}
    taken = []
    ideals = {}
    for src, dst in long:
        src_at = rank_at.get(ranks.get(src), 0)
        dst_at = rank_at.get(ranks.get(dst), 0)
        blockers = []
        for rank in rank_list:
            at = rank_at[rank]
            if src_at < at < dst_at:
                for code in by_rank.get(rank, []):
                    blockers.append((positions[code][1], positions[code][1] + heights[code]))
        free = free_rows(blockers)
        ideals[(src, dst)] = (nearest_row(free, leave_y[(src, dst)], enter_y[(src, dst)]), free)
    for src, dst in sorted(long, key=lambda item: ideals[item][0]):
        ideal, free = ideals[(src, dst)]
        channels[(src, dst)] = place_row(ideal, free, taken)
        taken.append(channels[(src, dst)])

    def side_slot(items, index):
        groups = {}
        for item in items:
            groups.setdefault(item[index], []).append(item)
        found = {}
        for group in groups.values():
            group.sort(key=lambda item: channels[item])
            for i, item in enumerate(group):
                found[item] = i
        return found

    leave_slot = side_slot(long, 0)
    enter_slot = side_slot(long, 1)
    low = content_bottom
    for src, dst in long:
        x1 = positions[src][0] + box_w
        y1 = leave_y[(src, dst)]
        x2 = positions[dst][0]
        y2 = enter_y[(src, dst)]
        channel = channels[(src, dst)]
        leave = x1 + 12 + min(leave_slot[(src, dst)], 6) * 5
        enter = x2 - 12 - min(enter_slot[(src, dst)], 6) * 5
        if enter < leave:
            leave, enter = (x1 + x2) / 2 - 2, (x1 + x2) / 2 + 2
        low = max(low, y1, y2, channel)
        paths.append(
            f"M {_num(x1)} {_num(y1)} L {_num(leave)} {_num(y1)} L {_num(leave)} {_num(channel)} "
            f"L {_num(enter)} {_num(channel)} L {_num(enter)} {_num(y2)} L {_num(x2)} {_num(y2)}"
        )
    extra = 0 if low <= content_bottom else low - content_bottom + 10
    return paths, extra


def _book_columns(conn):
    books = _rows(conn, "SELECT code, title, editorial_status FROM books")
    books.sort(key=lambda b: BOOK_ORDER.index(b["code"]) if b["code"] in BOOK_ORDER else 99)
    incoming = {b["code"]: [] for b in books}
    edges = []
    for row in _rows(conn, "SELECT book, requires FROM book_requires ORDER BY requires, book"):
        if row["book"] in incoming and row["requires"] in incoming:
            incoming[row["book"]].append(row["requires"])
            edges.append((row["requires"], row["book"]))
    rank = {}

    def depth(code, seen):
        if code in rank:
            return rank[code]
        if code in seen:
            return 0
        seen.add(code)
        scores = [depth(item, seen) for item in incoming.get(code, [])]
        rank[code] = max(scores) + 1 if scores else 0
        return rank[code]

    for book in books:
        depth(book["code"], set())
    layers = {}
    for book in books:
        layers.setdefault(rank[book["code"]], []).append(book["code"])
    _order_layers(layers, edges, {code: i for i, code in enumerate(BOOK_ORDER)})
    by_code = {book["code"]: book for book in books}
    columns = {key: [by_code[code] for code in layers[key]] for key in layers}
    return columns, edges, rank


def render_reading_order_svg(conn):
    """Picture of the book order: left to right, arrow toward the book that waits."""
    columns, edges, rank = _book_columns(conn)
    box_w = 210
    col_gap, row_gap, pad = 72, 18, 16
    titles = {}
    heights = {}
    for books in columns.values():
        for book in books:
            lines = _title_lines(book["title"], 30)
            titles[book["code"]] = lines
            heights[book["code"]] = 36 + 14 * len(lines)
    positions = {}
    keys = sorted(columns)
    x = pad
    bottom = pad
    for key in keys:
        y = pad
        for book in columns[key]:
            positions[book["code"]] = (x, y)
            y += heights[book["code"]] + row_gap
        bottom = max(bottom, y)
        x += box_w + col_gap
    width = max(x - col_gap + pad, pad + box_w)
    content_bottom = max(bottom - row_gap, pad)
    paths, extra = _reading_paths(positions, heights, edges, rank, box_w, content_bottom)
    height = max(content_bottom + extra + pad, pad + 50)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_num(width)}" height="{_num(height)}" '
        f'viewBox="0 0 {_num(width)} {_num(height)}" role="img">',
        "<title>Book reading order</title>",
        f'<rect width="{_num(width)}" height="{_num(height)}" fill="#f3efe6"/>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">'
        '<path d="M0,0 L8,3 L0,6 Z" fill="#6b645b"/></marker></defs>',
    ]
    for path in paths:
        parts.append(
            f'<path d="{path}" fill="none" stroke="#6b645b" stroke-width="1.4" '
            'stroke-linejoin="round" stroke-linecap="round" marker-end="url(#arrow)"/>'
        )
    for code, (bx, by) in positions.items():
        box_h = heights[code]
        parts.append(
            f'<rect x="{_num(bx)}" y="{_num(by)}" width="{box_w}" height="{_num(box_h)}" rx="6" '
            'fill="#fffdf8" stroke="#1c1915" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{_num(bx + 10)}" y="{_num(by + 20)}" font-family="Georgia, serif" font-size="15" '
            f'fill="#1c1915">{_xml(code)}</text>'
        )
        for i, line in enumerate(titles[code]):
            parts.append(
                f'<text x="{_num(bx + 10)}" y="{_num(by + 36 + i * 14)}" font-family="Georgia, serif" font-size="11" '
                f'fill="#6b645b">{_xml(line)}</text>'
            )
    parts.append("</svg>")
    return "\n".join(parts)


def render_reading_guide(conn):
    """Reading order export: the order picture and which books must be finished first."""
    lines = [
        "# Reading order",
        "",
        "Generated from `library.sqlite`. This file is a reading, not an import.",
        "Edit which books must be finished first in that book's organization file, "
        "or in an editorial organization change file, then import it.",
        "",
        render_reading_order_svg(conn),
        "",
        "Read the books from left to right. An arrow runs from a book you finish first "
        "to the book that waits for it. Books in the same column do not depend on each other, "
        "so they can be read in either order. A book with no arrow pointing to it is a place to start.",
        "",
        "Inside a book, follow that book's organization file. Chapters are listed in reading order, "
        "and each row names what must come first. An optional prerequisite is marked (opt.). "
        "What to explain has one section for each chapter, saying what that chapter must teach. "
        "The same order for every book is collected in "
        "[EDITORIAL_ORGANIZATION.md](EDITORIAL_ORGANIZATION.md).",
        "",
        "Chapter-specific requirements live on the chapter rows there.",
        "",
    ]
    books = _rows(conn, "SELECT code, title FROM books")
    books.sort(key=lambda b: BOOK_ORDER.index(b["code"]) if b["code"] in BOOK_ORDER else 99)
    for book in books:
        reqs = _rows(conn, "SELECT requires FROM book_requires WHERE book = ? ORDER BY requires", (book["code"],))
        needed_by = _rows(conn, "SELECT book FROM book_requires WHERE requires = ? ORDER BY book", (book["code"],))
        lines.append(f"## {book['code']} {book['title']}")
        lines.append("")
        if reqs:
            lines.append("Finish first: " + ", ".join(r["requires"] for r in reqs) + ".")
        else:
            lines.append("Finish first: nothing.")
        if needed_by:
            lines.append("Required by: " + ", ".join(r["book"] for r in needed_by) + ".")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _preamble_and_sections(text):
    text = text.replace("\r\n", "\n")
    chunks = re.split(r"(?m)^## (?!#)", text)
    sections = {}
    for chunk in chunks[1:]:
        name, _, body = chunk.partition("\n")
        sections[name.strip()] = body
    return chunks[0], sections


def _markdown_table(body, heading):
    headers = None
    rows = []
    for raw in body.split("\n"):
        line = raw.strip()
        if not line.startswith("|"):
            continue
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
        rows.append(dict(zip(headers, cells)))
    if headers is None:
        raise LibraryError(f"{heading} needs a table")
    return rows


def is_book_organization(text):
    head = "\n".join(text.replace("\r\n", "\n").split("\n")[:12])
    return "kind: book-organization" in head


EXPLAIN_COLUMNS = ["chapter", "title", "what to explain"]


def parse_explain_entries(body):
    """Map chapter id to teaching brief. One heading per chapter, or the older table."""
    body = (body or "").replace("\r\n", "\n")
    if re.search(r"(?m)^### ", body):
        entries = {}
        for chunk in re.split(r"(?m)^### ", body)[1:]:
            first, _, rest = chunk.partition("\n")
            ident = first.strip().split()[0] if first.strip() else ""
            if not ident:
                raise LibraryError("a What to explain heading needs a chapter id")
            if ident in entries:
                raise LibraryError(f"duplicate What to explain heading {ident}")
            entries[ident] = rest.strip()
        return entries
    if re.search(r"(?m)^\s*\|", body):
        rows = _markdown_table(body, "What to explain")
        headers = list(rows[0]) if rows else None
        if headers is None:
            for raw in body.split("\n"):
                line = raw.strip()
                if not line.startswith("|"):
                    continue
                cells = [cell_in(c) for c in line.strip().strip("|").split("|")]
                if all(set(c) <= set("-: ") and c for c in cells):
                    continue
                headers = cells
                break
        allowed = (EXPLAIN_COLUMNS, ["chapter", "what to explain"])
        if headers not in allowed:
            raise LibraryError("What to explain columns must be " + ", ".join(EXPLAIN_COLUMNS))
        entries = {}
        for row in rows:
            ident = row["chapter"].strip()
            if not ident:
                raise LibraryError("a What to explain row needs a chapter id")
            if ident in entries:
                raise LibraryError(f"duplicate What to explain row {ident}")
            entries[ident] = row["what to explain"]
        return entries
    return {}


def render_explain_section(chapters):
    """What to explain as one section per chapter."""
    lines = [
        "",
        "## What to explain",
        "",
        "These sections are the complete chapter list. Write what each chapter must teach under its heading. "
        "An empty section means it is not decided yet.",
        "",
    ]
    last = len(chapters) - 1
    for index, chapter in enumerate(chapters):
        lines.append(f"### {chapter['id']} {chapter['title']}")
        brief = (chapter.get("explain") or "").strip()
        if brief:
            lines.append("")
            lines.append(brief)
        if index != last:
            lines.append("")
    return lines


def _organization_prereqs(chapter, cell):
    cell = (cell or "").strip()
    if cell.lower() in ("", "none", "—", "-"):
        return []
    rows = []
    for bit in cell.split(";"):
        bit = bit.strip()
        if not bit or bit.lower() == "none":
            continue
        kind = "hard"
        if bit.endswith("(opt.)"):
            kind = "optional"
            bit = bit[: -len("(opt.)")].strip()
        if not bit:
            raise LibraryError(f"empty prerequisite on {chapter}")
        rows.append((bit, kind))
    return rows


def render_book_organization(conn, code):
    """One book's chapters and the order they are read in."""
    row = conn.execute("SELECT * FROM books WHERE code = ?", (code,)).fetchone()
    if not row:
        raise LibraryError(f"unknown book: {code}")
    book = dict(row)
    reqs = _rows(conn, "SELECT requires FROM book_requires WHERE book = ? ORDER BY requires", (code,))
    finish = ", ".join(item["requires"] for item in reqs) if reqs else "nothing"
    lines = [
        "kind: book-organization",
        f"book: {code}",
        "",
        f"# {code} {book['title']}",
        "",
        f"- Folder: {book['folder']}",
        f"- Entry level: {book['entry_level']}",
        f"- Target level: {book['target_level']}",
        f"- Editorial status: {book['editorial_status'] or ''}",
        f"- Finish first: {finish}",
        "",
        "## Notes",
        "",
    ]
    if (book["notes"] or "").strip():
        lines.append(book["notes"].strip())
        lines.append("")
    lines += [
        "## Parts",
        "",
        "This table is the complete list of parts in the book. A chapter may name a part as a prerequisite.",
        "",
    ]
    parts = _rows(conn, "SELECT id, title FROM parts WHERE book = ? ORDER BY id", (code,))
    lines.extend(md_table(["part", "title"], [{"part": part["id"], "title": part["title"]} for part in parts]))
    lines += [
        "",
        "## Chapters",
        "",
        "This table is the complete chapter list, in reading order. Finish each prerequisite before the chapter. "
        "Mark an optional prerequisite with (opt.). What each chapter must teach is in What to explain.",
        "",
    ]
    chapters = _rows(conn, "SELECT * FROM chapters WHERE book = ? ORDER BY id", (code,))
    chapters.sort(key=lambda ch: (chapter_number(ch["id"]), ch["id"]))
    rows = []
    for chapter in chapters:
        pres = _rows(
            conn,
            "SELECT target, kind FROM prereqs WHERE chapter = ? ORDER BY target, kind",
            (chapter["id"],),
        )
        if pres:
            bits = []
            for pre in pres:
                label = pre["target"]
                if pre["kind"] == "optional":
                    label += " (opt.)"
                bits.append(label)
            pre_text = "; ".join(bits)
        else:
            pre_text = "none"
        rows.append({
            "chapter": chapter["id"],
            "title": chapter["title"],
            "level": chapter["level"],
            "presence": chapter["presence"],
            "editorial status": chapter["editorial_status"] or "",
            "path": chapter["path"],
            "prerequisites": pre_text,
            "notes": chapter["notes"],
        })
    lines.extend(md_table(
        ["chapter", "title", "level", "presence", "editorial status", "path", "prerequisites", "notes"],
        rows,
    ))
    lines.extend(render_explain_section(chapters))
    lines.extend(render_dependencies_section(conn, code))
    lines.extend(render_sources_section(conn, code))
    return "\n".join(lines).rstrip() + "\n"


SOURCE_COLUMNS = ["ID", "file", "proposed chapter", "status", "reference"]
DEPENDENCY_COLUMNS = ["requires"]


def render_outline_dependencies(conn, code, reqs):
    """Book-dependency summary under one book in the editorial organization."""
    needed = _rows(
        conn,
        "SELECT book FROM book_requires WHERE requires = ? ORDER BY book",
        (code,),
    )
    rel = organization_relpath(conn, code)
    lines = [
        "",
        "### Book dependencies",
        "",
        f"Edited in [{rel}]({rel}). An editorial organization change file can replace the same list.",
        "",
    ]
    if reqs:
        lines.append("Finish first: " + ", ".join(_md_ref(item["requires"]) for item in reqs) + ".")
    else:
        lines.append("Finish first: nothing.")
    if needed:
        lines.append("Required by: " + ", ".join(_md_ref(item["book"]) for item in needed) + ".")
    lines.append("")
    return lines


def render_dependencies_section(conn, code):
    """Book-dependency table of one book organization file."""
    reqs = _rows(conn, "SELECT requires FROM book_requires WHERE book = ? ORDER BY requires", (code,))
    lines = [
        "",
        "## Book dependencies",
        "",
        "This table is the complete list of books that must be finished first. "
        "Importing the file updates them. The Finish first line above is the same list.",
        "",
    ]
    lines.extend(md_table(
        DEPENDENCY_COLUMNS,
        [{"requires": item["requires"]} for item in reqs],
    ))
    lines.append("")
    return lines


def parse_dependency_rows(book, rows, known):
    """Check a book organization Book dependencies table. Returns the required book codes."""
    codes = []
    for row in rows:
        code = row["requires"].strip()
        if not code or code.lower() in ("nothing", "none", "—", "-"):
            continue
        if code == book:
            raise LibraryError("a book cannot require itself")
        if code not in known:
            raise LibraryError(f"unknown book in book dependencies: {code}")
        if code in codes:
            raise LibraryError(f"book dependencies list {code} twice")
        codes.append(code)
    return codes


def book_source_rows(conn, code):
    return _rows(
        conn,
        "SELECT s.id, s.file, s.proposed_chapter, s.status, s.reference "
        "FROM sources s JOIN source_books b ON b.source = s.id "
        "WHERE b.book = ? ORDER BY s.position, s.id",
        (code,),
    )


def render_sources_section(conn, code):
    """Sources section of one book organization file."""
    lines = [
        "",
        "## Sources",
        "",
        "This table is the complete list of sources for this book. Importing the file updates them. "
        "A source listed in several books has one registry row: its file, proposed chapter, status, and reference "
        "change everywhere.",
        "",
    ]
    rows = [
        {
            "ID": item["id"],
            "file": item["file"],
            "proposed chapter": item["proposed_chapter"],
            "status": item["status"],
            "reference": item["reference"],
        }
        for item in book_source_rows(conn, code)
    ]
    lines.extend(md_table(SOURCE_COLUMNS, rows))
    lines.append("")
    return lines


def parse_source_rows(rows):
    """Check a book organization Sources table. Returns the stored fields."""
    parsed = []
    seen = set()
    for row in rows:
        ident = row["ID"].strip()
        if not ident:
            raise LibraryError("a source id is blank")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", ident):
            raise LibraryError(f"source id {ident} must be letters and digits")
        if ident in seen:
            raise LibraryError(f"duplicate source {ident}")
        seen.add(ident)
        status = row["status"].strip()
        if status not in SOURCE_STATUSES:
            raise LibraryError(
                f"bad status on {ident}; use " + ", ".join(SOURCE_STATUSES)
            )
        parsed.append({
            "id": ident,
            "file": row["file"].strip() or "none",
            "proposed_chapter": row["proposed chapter"].strip() or "-",
            "status": status,
            "reference": row["reference"].strip(),
        })
    return parsed


def replace_book_sources(conn, book, rows):
    """Replace the sources listed for one book. A shared source keeps its document line."""
    parsed = parse_source_rows(rows)
    next_pos = conn.execute("SELECT COALESCE(MAX(position), -1) + 1 AS n FROM sources").fetchone()["n"]
    for item in parsed:
        existing = conn.execute("SELECT 1 FROM sources WHERE id = ?", (item["id"],)).fetchone()
        if existing:
            conn.execute(
                "UPDATE sources SET file = ?, proposed_chapter = ?, status = ?, reference = ? WHERE id = ?",
                (item["file"], item["proposed_chapter"], item["status"], item["reference"], item["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO sources (id, file, proposed_chapter, status, reference, document, position) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (item["id"], item["file"], item["proposed_chapter"], item["status"], item["reference"], book, next_pos),
            )
            next_pos += 1
        conn.execute(
            "INSERT OR IGNORE INTO source_books (source, book) VALUES (?, ?)",
            (item["id"], book),
        )
    if parsed:
        marks = ",".join("?" for _ in parsed)
        conn.execute(
            f"DELETE FROM source_books WHERE book = ? AND source NOT IN ({marks})",
            [book] + [item["id"] for item in parsed],
        )
    else:
        conn.execute("DELETE FROM source_books WHERE book = ?", (book,))
    conn.execute(
        "DELETE FROM sources WHERE NOT EXISTS (SELECT 1 FROM source_books sb WHERE sb.source = sources.id)"
    )


def book_organizations_zip(conn):
    """Every book organization file, in reading order."""
    books = _rows(conn, "SELECT code FROM books")
    books.sort(key=lambda b: BOOK_ORDER.index(b["code"]) if b["code"] in BOOK_ORDER else 99)
    if not books:
        raise LibraryError("there are no books")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for book in books:
            code = book["code"]
            archive.writestr(organization_relpath(conn, code), render_book_organization(conn, code))
    return buf.getvalue()


def organization_filename(code):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", code + "-organization").strip("-") + ".md"


def book_folder(conn, code):
    """Folder name for a book, with no leading or trailing slash."""
    row = conn.execute("SELECT folder FROM books WHERE code = ?", (code,)).fetchone()
    if row is None:
        raise LibraryError(f"unknown book: {code}")
    folder = (row["folder"] or FOLDER_OF.get(code, "")).replace("\\", "/").strip().strip("/")
    if not folder or folder == "." or ".." in folder.split("/"):
        raise LibraryError(f"{code} has no book folder")
    return folder


def organization_relpath(conn, code):
    """Project-relative path of a book's organization file."""
    return book_folder(conn, code) + "/" + organization_filename(code)


def organization_path(root, conn, code):
    return os.path.join(root, book_folder(conn, code), organization_filename(code))


def _ordered_book_codes(conn):
    books = _rows(conn, "SELECT code FROM books")
    books.sort(key=lambda b: BOOK_ORDER.index(b["code"]) if b["code"] in BOOK_ORDER else 99)
    return [book["code"] for book in books]

__all__ = [name for name in globals() if not name.startswith('__')]
