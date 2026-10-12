"""Round-trip checks for the syllabus database. Run: python UI/test_library.py"""

import io
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import core

FIXTURE = """# Editorial organization

## Topic ownership

| topic | owner | referenced by |
| --- | --- | --- |
| Demo topic | [M0/ch01](#m0) | [M1](#m1) |

## Coverage of the requested topics

| requested | where |
| --- | --- |
| Demo path | [M0/ch01](#m0) to [M0/ch02](#m0), then [M1](#m1) |

<a id="m0"></a>

## M0 Demo

- Folder: M0-demo/
- Entry level: zero. Target level: undergraduate.
- Finish first: nothing (entry point of the series)
- Chapters: 2 planned, 0 present, 2 TODO.

| chapter | title | level reached | prerequisites | status |
| --- | --- | --- | --- | --- |
| M0/ch01 | One | basic | none | TODO(M0/ch01) |
| M0/ch02 | Two *(note: a note)* | basic | [M0/ch01](#m0) | TODO(M0/ch02) |

<a id="m1"></a>

## M1 Other

- Folder: M1-demo/
- Entry level: undergraduate. Target level: graduate.
- Finish first: [M0](#m0); chapter-specific: [M0/ch02](#m0) for M1/ch01
- Chapters: 1 planned, 1 present, 0 TODO.

| chapter | title | level reached | prerequisites | status |
| --- | --- | --- | --- | --- |
| M1/ch01 | Vec | undergraduate | [M0/ch01](#m0) | present: [M1-demo/chapters/ch01-vec/](M1-demo/chapters/ch01-vec/) |

## Revision notes

kept for history
"""


def _path_points(d):
    tokens = d.replace(",", " ").split()
    pts = []
    i = 0
    cx = cy = 0.0
    while i < len(tokens):
        cmd = tokens[i]
        i += 1
        if cmd in ("M", "L"):
            cx, cy = float(tokens[i]), float(tokens[i + 1])
            pts.append((cx, cy))
            i += 2
        elif cmd == "C":
            c1 = (float(tokens[i]), float(tokens[i + 1]))
            c2 = (float(tokens[i + 2]), float(tokens[i + 3]))
            end = (float(tokens[i + 4]), float(tokens[i + 5]))
            p0 = (cx, cy)
            for step in range(1, 9):
                t = step / 8
                u = 1 - t
                x = u ** 3 * p0[0] + 3 * u ** 2 * t * c1[0] + 3 * u * t ** 2 * c2[0] + t ** 3 * end[0]
                y = u ** 3 * p0[1] + 3 * u ** 2 * t * c1[1] + 3 * u * t ** 2 * c2[1] + t ** 3 * end[1]
                pts.append((x, y))
            cx, cy = end
            i += 6
        else:
            raise AssertionError("unexpected path command " + cmd)
    return pts


def _path_hits_box(d, box):
    x, y, w, h = box
    left, right, top, bottom = x + 1, x + w - 1, y + 1, y + h - 1
    pts = _path_points(d)
    for start, end in zip(pts, pts[1:]):
        for step in range(1, 17):
            t = step / 17
            px = start[0] + (end[0] - start[0]) * t
            py = start[1] + (end[1] - start[1]) * t
            if left < px < right and top < py < bottom:
                return True
    return False


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.syllabus = os.path.join(self.root, "EDITORIAL_ORGANIZATION.md")
        with open(self.syllabus, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        core.seed(self.root, self.syllabus)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_seed_once(self):
        with self.assertRaises(core.LibraryError):
            core.seed(self.root, self.syllabus)
        history = os.path.join(self.root, "EDITORIAL_ORGANIZATION_HISTORY.md")
        with open(history, encoding="utf-8") as fh:
            self.assertIn("kept for history", fh.read())

    def test_round_trip(self):
        conn = core.connect(core.db_path(self.root))
        before = core.snapshot(conn)
        path = os.path.join(self.root, "library.md")
        core.export_strict(conn, "library", path)
        core.import_strict(conn, core.read_text(path))
        after = core.snapshot(conn)
        conn.close()
        self.assertEqual(before, after)

    def test_book_scope_keeps_other_books(self):
        conn = core.connect(core.db_path(self.root))
        path = os.path.join(self.root, "m0.md")
        core.export_strict(conn, "M0", path)
        text = core.read_text(path).replace("| Two |", "| Two renamed |")
        core.import_strict(conn, text)
        m1 = conn.execute("SELECT title FROM books WHERE code = 'M1'").fetchone()["title"]
        m0ch = conn.execute("SELECT title FROM chapters WHERE id = 'M0/ch02'").fetchone()["title"]
        concepts = conn.execute("SELECT COUNT(*) AS c FROM concepts").fetchone()["c"]
        conn.close()
        self.assertEqual(m1, "Other")
        self.assertEqual(m0ch, "Two renamed")
        self.assertEqual(concepts, 1)

    def test_chapter_scope_replaces_only_its_prereqs(self):
        conn = core.connect(core.db_path(self.root))
        path = os.path.join(self.root, "ch.md")
        core.export_strict(conn, "M1/ch01", path)
        text = core.read_text(path)
        text = text.replace(
            "| M1/ch01 | M0/ch01 | hard |",
            "| M1/ch01 | M0/ch02 | hard |",
        )
        # finish-first also added M0/ch02; the file is the complete set for this chapter
        core.import_strict(conn, text)
        rows = conn.execute(
            "SELECT target FROM prereqs WHERE chapter = 'M1/ch01' ORDER BY target"
        ).fetchall()
        other = conn.execute(
            "SELECT target FROM prereqs WHERE chapter = 'M0/ch02'"
        ).fetchone()["target"]
        conn.close()
        self.assertEqual([r["target"] for r in rows], ["M0/ch02"])
        self.assertEqual(other, "M0/ch01")

    def test_filter_and_unknown_status_rejected(self):
        conn = core.connect(core.db_path(self.root))
        path = os.path.join(self.root, "ideas.md")
        core.export_filter(conn, path, status="Idea")
        with self.assertRaises(core.LibraryError):
            core.import_strict(conn, core.read_text(path))
        bad = "scope: M0/ch02\n\n## chapters\n"
        bad += "| id | book | title | level | presence | editorial_status | path | notes |\n"
        bad += "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        bad += "| M0/ch02 | M0 | Two | basic | absent | Not A Status |  |  |\n\n"
        bad += "## prereqs\n| chapter | target | kind |\n| --- | --- | --- |\n"
        with self.assertRaises(core.LibraryError):
            core.import_strict(conn, bad)
        conn.close()

    def test_book_organization_round_trip_and_outline(self):
        conn = core.connect(core.db_path(self.root))
        before = core.snapshot(conn)
        original = core.render_book_organization(conn, "M0")
        self.assertIn("kind: book-organization", original)
        self.assertIn("M0/ch02", original)
        changed = original.replace("| Two |", "| Two renamed |", 1)
        changed = changed.replace("| M0/ch01 | a note |", "| M0/ch01 (opt.) | a note |", 1)
        core.import_book_organization(conn, changed)
        title = conn.execute("SELECT title FROM chapters WHERE id = 'M0/ch02'").fetchone()["title"]
        kind = conn.execute(
            "SELECT kind FROM prereqs WHERE chapter = 'M0/ch02'"
        ).fetchone()["kind"]
        other = conn.execute("SELECT title FROM books WHERE code = 'M1'").fetchone()["title"]
        outline = core.render_outline(conn)
        conn.close()
        self.assertEqual(title, "Two renamed")
        self.assertEqual(kind, "optional")
        self.assertEqual(other, "Other")
        self.assertIn("Two renamed", outline)
        self.assertIn("(opt.)", outline)
        conn = core.connect(core.db_path(self.root))
        core.import_book_organization(conn, original)
        core.rewrite_readings(conn, self.root)
        after = core.snapshot(conn)
        with self.assertRaises(core.LibraryError):
            core.import_book_organization(conn, "# Editorial organization\n\nnot a book file\n")
        conn.close()
        self.assertEqual(before, after)

    def test_all_book_organizations_download_together(self):
        conn = core.connect(core.db_path(self.root))
        blob = core.book_organizations_zip(conn)
        conn.close()
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            self.assertEqual(archive.namelist(), ["M0-demo/M0-organization.md", "M1-demo/M1-organization.md"])
            text = archive.read("M0-demo/M0-organization.md").decode("utf-8")
        self.assertIn("kind: book-organization", text)
        self.assertIn("book: M0", text)

    def test_book_organization_what_to_explain(self):
        conn = core.connect(core.db_path(self.root))
        original = core.render_book_organization(conn, "M0")
        self.assertIn("## What to explain", original)
        self.assertIn("### M0/ch01 One\n", original)
        self.assertNotIn("| what to explain |", original)
        start = original.find("## What to explain")
        changed = original[:start] + original[start:].replace(
            "### M0/ch01 One\n",
            "### M0/ch01 One\n\nThe pairing of vectors and covectors.\n\nIt is the teaching brief.\n",
            1,
        )
        core.import_book_organization(conn, changed)
        brief = conn.execute("SELECT explain FROM chapters WHERE id = 'M0/ch01'").fetchone()["explain"]
        other = conn.execute("SELECT explain FROM chapters WHERE id = 'M0/ch02'").fetchone()["explain"]
        again = core.render_book_organization(conn, "M0")
        self.assertEqual(brief, "The pairing of vectors and covectors.\n\nIt is the teaching brief.")
        self.assertEqual(other, "")
        self.assertIn("The pairing of vectors and covectors.\n\nIt is the teaching brief.", again)
        broken = changed.replace("### M0/ch02 Two\n", "", 1)
        with self.assertRaises(core.LibraryError):
            core.import_book_organization(conn, broken)
        conn.close()

    def test_reading_guide_is_picture_and_explanation(self):
        conn = core.connect(core.db_path(self.root))
        text = core.render_reading_guide(conn)
        conn.close()
        self.assertTrue(text.startswith("# Reading order\n"))
        self.assertIn("<svg", text)
        self.assertIn(">M0<", text)
        self.assertIn(">M1<", text)
        self.assertIn("Read the books from left to right.", text)
        self.assertIn("Inside a book", text)
        self.assertIn("Finish first: M0.", text)
        self.assertIn("Required by: M1.", text)
        self.assertIn("## M0 Demo", text)
        self.assertNotIn("Decisions taken", text)
        self.assertNotIn("## Plan", text)

    def test_skip_arrow_runs_below_the_books(self):
        positions = {"A": (16, 16), "B": (282, 16), "C": (548, 16)}
        heights = {"A": 50, "B": 50, "C": 50}
        ranks = {"A": 0, "B": 1, "C": 2}
        paths, extra = core._reading_paths(
            positions, heights, [("A", "B"), ("B", "C"), ("A", "C")], ranks, 210, 66,
        )
        skip = [path for path in paths if " L " in path]
        self.assertEqual(len(skip), 1)
        self.assertFalse(_path_hits_box(skip[0], (282, 16, 210, 50)))
        ys = [point[1] for point in _path_points(skip[0])]
        self.assertGreater(max(ys), 66)
        self.assertLess(max(ys), 110)
        self.assertGreater(extra, 0)
        for path in paths:
            if " C " in path:
                self.assertFalse(_path_hits_box(path, (282, 16, 210, 50)))

    def test_skip_arrow_uses_the_gap_between_books(self):
        positions = {"A": (16, 40), "B1": (282, 16), "B2": (282, 120), "C": (548, 40)}
        heights = {"A": 50, "B1": 50, "B2": 50, "C": 50}
        ranks = {"A": 0, "B1": 1, "B2": 1, "C": 2}
        paths, extra = core._reading_paths(
            positions, heights, [("A", "C")], ranks, 210, 170,
        )
        self.assertEqual(extra, 0)
        self.assertFalse(_path_hits_box(paths[0], (282, 16, 210, 50)))
        self.assertFalse(_path_hits_box(paths[0], (282, 120, 210, 50)))
        self.assertTrue(all(point[1] < 120 for point in _path_points(paths[0])))

    def test_export_overwrites_the_project_file(self):
        conn = core.connect(core.db_path(self.root))
        outline = core.render_outline(conn)
        conn.close()
        names = core.save_export(self.root, "editorial-organization")
        self.assertEqual(names, ["EDITORIAL_ORGANIZATION.md"])
        with open(os.path.join(self.root, "EDITORIAL_ORGANIZATION.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), outline if outline.endswith("\n") else outline + "\n")
        self.assertEqual(core.save_export(self.root, "book", "M0"), ["M0-demo/M0-organization.md"])
        self.assertTrue(os.path.isfile(os.path.join(self.root, "M0-demo", "M0-organization.md")))
        self.assertFalse(os.path.isfile(os.path.join(self.root, "M0-organization.md")))
        self.assertEqual(
            core.save_export(self.root, "book", "all"),
            ["M0-demo/M0-organization.md", "M1-demo/M1-organization.md"],
        )
        self.assertEqual(core.save_export(self.root, "reading-order"), ["READING_ORDER.md"])
        self.assertFalse(os.path.isfile(os.path.join(self.root, "ROADMAP.md")))
        with self.assertRaises(core.LibraryError):
            core.save_export(self.root, "internal-references")
        conn = core.connect(core.db_path(self.root))
        summary = core.import_project_books(conn, self.root)
        path = os.path.join(self.root, "M0-demo", "M0-organization.md")
        with open(path, encoding="utf-8") as fh:
            stored = fh.read()
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(stored.replace("# M0 Demo", "# M0 From project", 1))
        self.assertIn("M0 was updated.", core.import_project_book(conn, self.root, "M0"))
        self.assertEqual(conn.execute("SELECT title FROM books WHERE code = 'M0'").fetchone()["title"], "From project")
        self.assertEqual(conn.execute("SELECT title FROM books WHERE code = 'M1'").fetchone()["title"], "Other")
        with self.assertRaises(core.LibraryError):
            core.import_project_book(conn, self.root, "ZZ")
        conn.close()
        self.assertIn("M0", summary)
        self.assertIn("M1", summary)

    def test_empty_folder_uses_the_document_folder(self):
        conn = core.connect(core.db_path(self.root))
        conn.execute("UPDATE books SET folder = '' WHERE code = 'M0'")
        conn.commit()
        conn.close()
        self.assertEqual(core.save_export(self.root, "book", "M0"), ["M0-math-basics/M0-organization.md"])
        path = os.path.join(self.root, "M0-math-basics", "M0-organization.md")
        self.assertTrue(os.path.isfile(path))
        self.assertFalse(os.path.isfile(os.path.join(self.root, "M0-organization.md")))
        conn = core.connect(core.db_path(self.root))
        self.assertIn("M0 was updated.", core.import_project_book(conn, self.root, "M0"))
        conn.close()

    def test_import_follows_the_chosen_target(self):
        conn = core.connect(core.db_path(self.root))
        m0 = core.render_book_organization(conn, "M0")
        m1 = core.render_book_organization(conn, "M1")
        with self.assertRaises(core.LibraryError):
            core.import_chosen(conn, "book", "M0", "M1-organization.md", m1.encode("utf-8"))
        with self.assertRaises(core.LibraryError):
            core.import_chosen(conn, "chapter", "", "M0-organization.md", m0.encode("utf-8"))
        renamed = m0.replace("# M0 Demo", "# M0 Renamed", 1)
        self.assertIn(
            "M0 was updated.",
            core.import_chosen(conn, "book", "M0", "M0-organization.md", renamed.encode("utf-8")),
        )
        self.assertEqual(conn.execute("SELECT title FROM books WHERE code = 'M0'").fetchone()["title"], "Renamed")
        summary = core.import_chosen(conn, "book", "all", "book-organizations.zip", core.book_organizations_zip(conn))
        self.assertIn("M0", summary)
        self.assertIn("M1", summary)
        self.assertEqual(conn.execute("SELECT title FROM books WHERE code = 'M0'").fetchone()["title"], "Renamed")
        self.assertEqual(conn.execute("SELECT title FROM books WHERE code = 'M1'").fetchone()["title"], "Other")
        conn.close()

    def test_only_book_and_chapter_changes_import(self):
        conn = core.connect(core.db_path(self.root))
        book = core.render_book_organization(conn, "M1")
        self.assertIn("M1 was updated.", core.import_user_file(conn, book))
        with self.assertRaises(core.LibraryError):
            core.import_user_file(conn, core.render_outline(conn))
        with self.assertRaises(core.LibraryError):
            core.import_user_file(conn, core.render_chapter_changes())
        with self.assertRaises(core.LibraryError):
            core.import_user_file(conn, core.render_reading_guide(conn))
        conn.close()

    def test_chapter_changes_edit_add_and_delete(self):
        conn = core.connect(core.db_path(self.root))

        def add_row(text, heading, row):
            start = text.find(f"## {heading}\n")
            sep = text.find("\n| ---", start)
            end = text.find("\n", sep + 1)
            return text[:end] + "\n" + row + text[end:]

        edited = add_row(
            core.render_chapter_changes(),
            "Edited chapters",
            "| M0/ch02 | Two renamed | basic | absent | Idea |  | none |  |  |",
        )
        summary = core.import_chapter_changes(conn, edited)
        title = conn.execute("SELECT title FROM chapters WHERE id = 'M0/ch02'").fetchone()["title"]
        prereqs = conn.execute("SELECT COUNT(*) AS c FROM prereqs WHERE chapter = 'M0/ch02'").fetchone()["c"]
        kept = conn.execute("SELECT title FROM chapters WHERE id = 'M0/ch01'").fetchone()["title"]
        self.assertEqual(summary, "Applied 1 edited chapter.")
        self.assertEqual(title, "Two renamed")
        self.assertEqual(prereqs, 0)
        self.assertEqual(kept, "One")

        added = add_row(
            core.render_chapter_changes(),
            "New chapters",
            "| M0/ch03 | Three | basic | absent | Idea |  | M0/ch01 |  |  |",
        )
        core.import_chapter_changes(conn, added)
        self.assertEqual(
            conn.execute("SELECT title FROM chapters WHERE id = 'M0/ch03'").fetchone()["title"],
            "Three",
        )

        removed = add_row(core.render_chapter_changes(), "Deleted chapters", "| M0/ch02 |")
        core.import_chapter_changes(conn, removed)
        self.assertIsNone(conn.execute("SELECT id FROM chapters WHERE id = 'M0/ch02'").fetchone())
        self.assertIsNotNone(conn.execute("SELECT id FROM chapters WHERE id = 'M0/ch01'").fetchone())

        new_book = add_row(
            core.render_chapter_changes(),
            "New books",
            "| ZZ | Extra | ZZ-extra | basic | undergraduate | Idea | M0 |  |",
        )
        new_book = add_row(
            new_book,
            "New chapters",
            "| ZZ/ch01 | Start | basic | absent | Idea |  | none |  |  |",
        )
        summary = core.import_chapter_changes(conn, new_book)
        self.assertIn("1 new book", summary)
        self.assertIn("1 new chapter", summary)
        outline = core.render_outline(conn)
        self.assertIn("ZZ Extra", outline)
        self.assertIn("Start", outline)

        core.import_chapter_changes(
            conn,
            add_row(core.render_chapter_changes(), "Deleted books", "| M0 |"),
        )
        self.assertIsNone(conn.execute("SELECT code FROM books WHERE code = 'M0'").fetchone())
        self.assertIsNone(conn.execute("SELECT id FROM chapters WHERE id = 'M0/ch01'").fetchone())
        self.assertEqual(conn.execute("SELECT title FROM books WHERE code = 'M1'").fetchone()["title"], "Other")
        both = add_row(core.render_chapter_changes(), "Edited chapters", "| M1/ch01 | Vec | undergraduate | present | Idea |  | none |  |  |")
        both = add_row(both, "Deleted chapters", "| M1/ch01 |")
        with self.assertRaises(core.LibraryError):
            core.import_chapter_changes(conn, both)
        conn.close()

    def test_page_lists_parts_with_books_and_chapters(self):
        conn = core.connect(core.db_path(self.root))
        conn.execute("INSERT INTO parts (id, book, title) VALUES ('M0/part:algebra', 'M0', 'Algebra')")
        conn.commit()
        page = core.page_data(conn, {})
        self.assertEqual(page["visible"]["books"], ["M0", "M1"])
        self.assertEqual(page["visible"]["parts"], [
            "M0/part:algebra", "M1/part:algebra", "M1/part:integration", "M1/part:manifolds",
        ])
        self.assertEqual(page["visible"]["chapters"], ["M0/ch01", "M0/ch02", "M1/ch01"])
        filtered = core.page_data(conn, {"status": ["Idea"], "book": ["M0"]})
        self.assertEqual(filtered["visible"]["parts"], [])
        self.assertIn("M0/ch01", filtered["visible"]["chapters"])
        conn.close()

    def test_update_record_chapter_and_book_cascade(self):
        conn = core.connect(core.db_path(self.root))
        core.update_record(conn, "M0/ch01", presence="present", editorial_status="Building", level="undergraduate")
        row = conn.execute(
            "SELECT presence, editorial_status, level FROM chapters WHERE id = 'M0/ch01'"
        ).fetchone()
        self.assertEqual(row["presence"], "present")
        self.assertEqual(row["editorial_status"], "Building")
        self.assertEqual(row["level"], "undergraduate")
        core.update_record(conn, "M0", editorial_status="Idea", level="basic", presence="absent")
        book = conn.execute(
            "SELECT editorial_status, target_level FROM books WHERE code = 'M0'"
        ).fetchone()
        self.assertEqual(book["editorial_status"], "Idea")
        self.assertEqual(book["target_level"], "basic")
        rows = conn.execute(
            "SELECT presence, editorial_status, level FROM chapters WHERE book = 'M0' ORDER BY id"
        ).fetchall()
        for ch in rows:
            self.assertEqual(ch["presence"], "absent")
            self.assertEqual(ch["editorial_status"], "Idea")
            self.assertEqual(ch["level"], "basic")
        core.update_record(conn, "M0/ch01", presence="retired")
        with self.assertRaises(core.LibraryError):
            core.update_record(conn, "M0/ch01", editorial_status="Finished")
        conn.close()

    def test_scan_rewrites_cross_references_and_export(self):
        def write(rel, text):
            path = os.path.join(self.root, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)

        write("M0-demo/main.tex", "\\input{chapters/ch01-one/00-section}\n")
        write(
            "M0-demo/chapters/ch01-one/00-section.tex",
            "\\label{sec:one}\nSee \\ref{sec:one}.\n",
        )
        write(
            "M0-demo/chapters/ch02-two/00-section.tex",
            "\\label{sec:later}\n\\ref{sec:vec}\n",
        )
        write("M0-demo/main.tex", "\\input{chapters/ch01-one/00-section}\n\\input{chapters/ch02-two/00-section}\n")
        write(
            "M1-demo/main.tex",
            "\\chapterprereqs{}\n\\input{chapters/ch01-vec/00-section}\n",
        )
        write(
            "M1-demo/chapters/ch01-vec/00-section.tex",
            "\\label{sec:vec}\n\\ref{sec:one}\n\\ref{sec:missing}\n",
        )
        conn = core.connect(core.db_path(self.root))
        conn.execute(
            "UPDATE chapters SET path = ? WHERE id = ?",
            ("M0-demo/chapters/ch01-one", "M0/ch01"),
        )
        conn.commit()
        summary = core.scan_cross_references(self.root, conn)
        self.assertIn("Stored 2 internal references", summary)
        directions = {
            row["label"]: row["direction"]
            for row in conn.execute("SELECT label, direction, target_id FROM xref_refs")
        }
        self.assertEqual(directions["sec:one"], "back")
        self.assertEqual(directions["sec:vec"], "forward")
        target = conn.execute(
            "SELECT target_id FROM xref_refs WHERE label = 'sec:one'"
        ).fetchone()["target_id"]
        self.assertEqual(target, "M0/ch01")
        same = conn.execute(
            "SELECT COUNT(*) AS c FROM xref_refs WHERE label = 'sec:one' AND source_doc = 'M0'"
        ).fetchone()["c"]
        self.assertEqual(same, 0)
        self.assertEqual(conn.execute("SELECT unresolved FROM xref_summary").fetchone()["unresolved"], 1)
        self.assertEqual(conn.execute("SELECT prereq_gaps FROM xref_summary").fetchone()["prereq_gaps"], 1)
        write("M1-demo/chapters/ch01-vec/00-section.tex", "\\label{sec:vec}\n")
        again = core.scan_cross_references(self.root, conn)
        self.assertIn("Stored 1 internal references", again)
        self.assertEqual(conn.execute("SELECT COUNT(*) AS c FROM xref_refs").fetchone()["c"], 1)
        text = core.render_cross_references(conn)
        self.assertIn("Generated from `library.sqlite`", text)
        self.assertIn("sec:vec", text)
        self.assertIn("forward", text)
        names = core.save_export(self.root, "internal-references")
        self.assertEqual(names, ["INTERNAL_REFERENCES.md"])
        self.assertTrue(text.startswith("# Internal references\n"))
        with open(os.path.join(self.root, "INTERNAL_REFERENCES.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), text)
        conn.close()

    def test_export_writes_sources_index(self):
        def write(rel, text):
            path = os.path.join(self.root, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)

        write(
            "GLOSSARY/references/references.tex",
            "\\begin{thebibliography}{9}\n"
            "\\bibitem{Demo} A.~Author, \\emph{Title}, Press, 2000.\n"
            "\\bibitem{Other} B.~Other, \\emph{Book}.\n"
            "\\end{thebibliography}\n",
        )
        write("M0-demo/chapters/ch01-one/00-section.tex", "See \\cite{Demo,Other}. % \\cite{Hidden}\n")
        write("M1-demo/chapters/ch01-vec/00-section.tex", "\\cite{Demo}\n")
        write("M0-demo/sources/.gitkeep", "")
        write("M0-demo/sources/notes.pdf", "source")
        conn = core.connect(core.db_path(self.root))
        text = core.render_sources_index(self.root, conn)
        conn.close()
        self.assertIn(
            "| Demo | none | cited by M0, M1 | - | cited, no file | A. Author, *Title*, Press, 2000. |",
            text,
        )
        self.assertIn("| Other | none | cited by M0 | - | cited, no file | B. Other, *Book*. |", text)
        self.assertNotIn("Hidden", text)
        self.assertIn("`M0-demo/sources/notes.pdf` | M0 |", text)
        self.assertNotIn(".gitkeep", text)
        names = core.save_export(self.root, "external-sources")
        self.assertEqual(names, ["EXTERNAL_SOURCES.md"])
        self.assertTrue(text.startswith("# External sources\n"))
        with open(os.path.join(self.root, "EXTERNAL_SOURCES.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), text if text.endswith("\n") else text + "\n")

    def test_book_organization_updates_sources(self):
        def write(rel, text):
            path = os.path.join(self.root, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)

        write(
            "GLOSSARY/references/references.tex",
            "\\begin{thebibliography}{9}\n"
            "\\bibitem{Demo} A.~Author, \\emph{Title}, Press, 2000.\n"
            "\\bibitem{Other} B.~Other, \\emph{Book}.\n"
            "\\end{thebibliography}\n",
        )
        write("M0-demo/chapters/ch01-one/00-section.tex", "See \\cite{Demo,Other}.\n")
        write("M1-demo/chapters/ch01-vec/00-section.tex", "\\cite{Demo}\n")
        conn = core.connect(core.db_path(self.root))
        core.seed_sources(conn, self.root)
        original = core.render_book_organization(conn, "M0")
        self.assertIn("## Sources", original)
        self.assertIn("| Demo | none | - | cited, no file | A. Author, *Title*, Press, 2000. |", original)
        self.assertIn("| Other | none | - | cited, no file | B. Other, *Book*. |", original)
        changed = original.replace(
            "| Demo | none | - | cited, no file | A. Author, *Title*, Press, 2000. |",
            "| Demo | M0-demo/sources/demo.pdf | M0/ch01 | proposed | A. Author, *Title*, 2nd ed. |",
            1,
        )
        changed = changed.replace(
            "| Other | none | - | cited, no file | B. Other, *Book*. |",
            "| Fresh | none | - | unplaced | A new source. |",
            1,
        )
        core.import_book_organization(conn, changed)
        demo = conn.execute(
            "SELECT file, proposed_chapter, status, reference, document FROM sources WHERE id = 'Demo'"
        ).fetchone()
        self.assertEqual(demo["file"], "M0-demo/sources/demo.pdf")
        self.assertEqual(demo["proposed_chapter"], "M0/ch01")
        self.assertEqual(demo["status"], "proposed")
        self.assertEqual(demo["reference"], "A. Author, *Title*, 2nd ed.")
        self.assertEqual(demo["document"], "cited by M0, M1")
        listed = core.render_book_organization(conn, "M1")
        self.assertIn("| Demo | M0-demo/sources/demo.pdf | M0/ch01 | proposed | A. Author, *Title*, 2nd ed. |", listed)
        self.assertIn("| Fresh | none | - | unplaced | A new source. |", core.render_book_organization(conn, "M0"))
        self.assertIsNone(conn.execute("SELECT 1 FROM sources WHERE id = 'Other'").fetchone())
        index = core.render_sources_index(self.root, conn)
        self.assertIn("| Demo | M0-demo/sources/demo.pdf | cited by M0, M1 | M0/ch01 | proposed |", index)
        self.assertIn("| Fresh | none | M0 | - | unplaced | A new source. |", index)
        conn.close()

    def test_organization_updates_book_dependencies(self):
        conn = core.connect(core.db_path(self.root))
        original = core.render_book_organization(conn, "M1")
        self.assertIn("## Book dependencies", original)
        self.assertIn("| requires |\n| --- |\n| M0 |", original)
        cleared = original.replace("| requires |\n| --- |\n| M0 |", "| requires |\n| --- |")
        core.import_book_organization(conn, cleared)
        self.assertEqual(
            conn.execute("SELECT requires FROM book_requires WHERE book = 'M1'").fetchall(),
            [],
        )
        legacy = original
        start = legacy.find("\n## Book dependencies\n")
        end = legacy.find("\n## Sources\n", start)
        legacy = legacy[:start] + legacy[end:]
        legacy = legacy.replace("- Finish first: M0", "- Finish first: nothing", 1)
        core.import_book_organization(conn, legacy)
        self.assertEqual(
            conn.execute("SELECT COUNT(*) AS c FROM book_requires WHERE book = 'M1'").fetchone()["c"],
            0,
        )
        with self.assertRaises(core.LibraryError):
            core.import_book_organization(
                conn,
                original.replace("| requires |\n| --- |\n| M0 |", "| requires |\n| --- |\n| M1 |"),
            )
        restored = original.replace("- Finish first: M0", "- Finish first: nothing", 1)
        core.import_book_organization(conn, restored)
        self.assertEqual(
            [row["requires"] for row in conn.execute(
                "SELECT requires FROM book_requires WHERE book = 'M1' ORDER BY requires"
            )],
            ["M0"],
        )
        outline = core.render_outline(conn)
        self.assertIn("### Book dependencies", outline)
        self.assertIn("Edited in [M1-demo/M1-organization.md](M1-demo/M1-organization.md).", outline)
        self.assertIn("Finish first: [M0](#m0).", outline)
        self.assertIn("Required by: [M1](#m1).", outline)

        def add_row(text, heading, row):
            start = text.find(f"## {heading}\n")
            sep = text.find("\n| ---", start)
            end = text.find("\n", sep + 1)
            return text[:end] + "\n" + row + text[end:]

        edited = add_row(
            core.render_chapter_changes(),
            "Edited books",
            "| M1 | Other | M1-demo | undergraduate | graduate | Idea |  |  |",
        )
        core.import_chapter_changes(conn, edited)
        self.assertEqual(
            conn.execute("SELECT COUNT(*) AS c FROM book_requires WHERE book = 'M1'").fetchone()["c"],
            0,
        )
        self.assertNotIn("Required by: [M1](#m1).", core.render_outline(conn))
        conn.close()

    def test_outline_shows_sources_edited_in_the_book_file(self):
        conn = core.connect(core.db_path(self.root))
        conn.execute(
            "INSERT INTO sources (id, file, proposed_chapter, status, reference, document, position) "
            "VALUES ('Demo', 'none', 'M0/ch01', 'proposed', 'A book.', 'M0', 0)"
        )
        conn.execute("INSERT INTO source_books (source, book) VALUES ('Demo', 'M0')")
        conn.commit()
        outline = core.render_outline(conn)
        self.assertIn("Edit them in that book's organization file.", outline)
        self.assertIn("### Sources", outline)
        self.assertIn("[M0-demo/M0-organization.md](M0-demo/M0-organization.md)", outline)
        self.assertIn("| Demo | none | M0/ch01 | proposed | A book. |", outline)
        self.assertEqual(outline.count("### Sources"), 1)
        parsed = core.parse_syllabus(outline)
        m0 = next(book for book in parsed["books"] if book["code"] == "M0")
        self.assertEqual([ch["id"] for ch in m0["chapters"]], ["M0/ch01", "M0/ch02"])
        conn.close()


if __name__ == "__main__":
    unittest.main()
