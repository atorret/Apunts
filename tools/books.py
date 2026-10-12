"""Document folders and build order.

Folders come from UI/base.py. Which book must be read before which comes from
library.sqlite (table book_requires). The old syllabus and the migration rules
are in tools/legacy/structure_config.py.
"""
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "UI"))
from base import BOOK_ORDER, DOCUMENTS

FOLDER = {code: folder for code, folder, _job in DOCUMENTS}
JOB = {code: job for code, _folder, job in DOCUMENTS}
MAINFILE = {code: "main.tex" for code in FOLDER}
MAINFILE["unsorted"] = "UNSORTED.tex"
CONTENT_DOCS = [code for code, _folder, _job in DOCUMENTS if code not in ("GLOSSARY", "unsorted")]

_EDGES = None


def doc_edges():
    """Pairs (earlier book, later book) from library.sqlite."""
    global _EDGES
    if _EDGES is not None:
        return _EDGES
    path = os.path.join(ROOT, "library.sqlite")
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA query_only = ON")
    try:
        _EDGES = list(conn.execute("SELECT requires, book FROM book_requires"))
    finally:
        conn.close()
    return _EDGES


def ancestors(doc):
    """Books that must be read before `doc`."""
    seen, stack = set(), [doc]
    while stack:
        cur = stack.pop()
        for earlier, later in doc_edges():
            if later == cur and earlier not in seen:
                seen.add(earlier)
                stack.append(earlier)
    return seen


def build_order():
    """Prerequisites first, ties broken by BOOK_ORDER, then GLOSSARY and unsorted."""
    rank = {code: i for i, code in enumerate(BOOK_ORDER)}
    pending = list(CONTENT_DOCS)
    incoming = {code: set() for code in pending}
    for earlier, later in doc_edges():
        if later in incoming and earlier in incoming:
            incoming[later].add(earlier)
    order = []
    while pending:
        ready = [code for code in pending if not incoming[code]]
        if not ready:
            ready = [min(pending, key=lambda code: rank.get(code, 99))]
        ready.sort(key=lambda code: rank.get(code, 99))
        nxt = ready[0]
        order.append(nxt)
        pending.remove(nxt)
        for code in pending:
            incoming[code].discard(nxt)
    return order + ["GLOSSARY", "unsorted"]


BUILD_ORDER = build_order()
