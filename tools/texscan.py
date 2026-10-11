"""Scan the document folders: labels, references, citations, inputs, chapters."""
import os
import re
from dataclasses import dataclass, field

from structure_config import FOLDER, BODY, MAINFILE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"build", "sources", "notes", "legacy", "legacy-build", "project-docs"}

RE_LABEL = re.compile(r"\\label\{([^}]+)\}")
RE_REF = re.compile(r"\\(ref|eqref|pageref|nameref)\{([^}]+)\}")
RE_CITE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}")
RE_BIBITEM = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}")
RE_INPUT = re.compile(r"\\input\{([^}]+)\}")
RE_DEP = re.compile(r"Depends on:([^|]*)\|")
RE_DEPLABEL = re.compile(r"\b((?:sec|part):[A-Za-z0-9_-]+)")


def strip_comment(line):
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


def brace_groups(text, start, n):
    """Return n balanced {...} groups starting at text[start:]."""
    groups, i = [], start
    while len(groups) < n and i < len(text):
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
    return groups if len(groups) == n else None


@dataclass
class Scan:
    files: dict = field(default_factory=dict)       # rel path -> (doc, doc-relative path)
    labels: dict = field(default_factory=dict)      # label -> list of (file, line)
    refs: list = field(default_factory=list)        # (file, line, cmd, label)
    cites: list = field(default_factory=list)       # (file, line, key)
    bibitems: set = field(default_factory=set)
    inputs: dict = field(default_factory=dict)      # file -> list of included files (rel to ROOT)
    deps: dict = field(default_factory=dict)        # file -> declared dependency labels
    chapter: dict = field(default_factory=dict)     # file -> (doc, chapter key)
    words: dict = field(default_factory=dict)       # file -> word count


def doc_of_folder():
    return {v: k for k, v in FOLDER.items()}


def scan(include_mains=False):
    s = Scan()
    folders = doc_of_folder()
    for folder, doc in folders.items():
        base = os.path.join(ROOT, folder)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if not fn.endswith(".tex"):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, ROOT).replace("\\", "/")
                drel = os.path.relpath(full, base).replace("\\", "/")
                if drel == MAINFILE[doc] and not include_mains:
                    continue
                s.files[rel] = (doc, drel)
    for rel, (doc, drel) in s.files.items():
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            raw = fh.read()
        s.words[rel] = len(raw.split())
        lines = raw.splitlines()
        if lines:
            m = RE_DEP.search(lines[0])
            s.deps[rel] = RE_DEPLABEL.findall(m.group(1)) if m else []
        s.inputs[rel] = []
        clean_lines = [strip_comment(l) for l in lines]
        for n, line in enumerate(clean_lines, 1):
            for m in RE_LABEL.finditer(line):
                s.labels.setdefault(m.group(1), []).append((rel, n))
            for m in RE_REF.finditer(line):
                s.refs.append((rel, n, m.group(1), m.group(2).strip()))
            for m in RE_CITE.finditer(line):
                for k in m.group(1).split(","):
                    s.cites.append((rel, n, k.strip()))
            for m in RE_BIBITEM.finditer(line):
                s.bibitems.add(m.group(1).strip())
            for m in RE_INPUT.finditer(line):
                target = m.group(1)
                if not target.endswith(".tex"):
                    target += ".tex"
                tgt = os.path.normpath(os.path.join(ROOT, FOLDER[doc], target))
                s.inputs[rel].append(os.path.relpath(tgt, ROOT).replace("\\", "/"))
        joined = "\n".join(clean_lines)
        for m in re.finditer(r"\\glossentry", joined):
            g = brace_groups(joined, m.end(), 3)
            if g and g[2].strip():
                line = joined.count("\n", 0, m.start()) + 1
                s.refs.append((rel, line, "glossentry", g[2].strip()))
    # chapter assignment
    includer = {}
    for f, targets in s.inputs.items():
        for t in targets:
            includer.setdefault(t, f)

    def chap(rel):
        doc, drel = s.files[rel]
        parts = drel.split("/")
        if doc == "GLOSSARY":
            return "glossary"
        if doc == "Unsorted":
            return parts[0] if len(parts) > 1 else drel
        if parts[0] == "chapters":
            return parts[1] if len(parts) > 2 else parts[1][:-4]
        if parts[0] == "exercises":
            return parts[1][:-4]
        if rel in includer and includer[rel] != rel:
            return chap(includer[rel])
        return parts[0]

    for rel in s.files:
        s.chapter[rel] = (s.files[rel][0], chap(rel))
    return s


def reading_order():
    """(doc, chapter key) -> global index in reading order, plus chapter ids."""
    order, ids = {}, {}
    i = 0
    for doc, items in BODY.items():
        for it in items:
            kind = it[0]
            if kind == "part":
                key = (doc, it[1].split("/")[-1])
                ids[key] = f"{doc}/{key[1]}"
            elif kind in ("chapter", "wrapped"):
                key = (doc, it[2])
                ids[key] = f"{doc}/{it[1]}"
            elif kind == "todo":
                key = (doc, "TODO-" + it[1])
                ids[key] = f"{doc}/{it[1]}"
            else:
                continue
            order[key] = i
            i += 1
    return order, ids


def chapter_anchor(s, key):
    """First section/part label of a chapter (its hub), else its first label."""
    doc, ch = key
    cands = []
    for lab, locs in s.labels.items():
        f, n = locs[0]
        if s.chapter.get(f) == key:
            hub = f.endswith("/00-section.tex") or "/00-part-" in f
            cands.append((0 if (hub and re.match(r"(sec|part):", lab)) else 1, f, n, lab))
    if not cands:
        return None
    cands.sort()
    return cands[0][3]
