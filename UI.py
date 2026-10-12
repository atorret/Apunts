"""Browse the syllabus database and run seed, export, import, layout, and scans.

    python UI.py seed
    python UI.py serve
    python UI.py scan-xrefs
    python UI.py export --scope library -o library.md
    python UI.py export --scope M1 -o m1.md
    python UI.py export --report filter --status Idea -o ideas.md
    python UI.py import library.md
    python UI.py layout
    python UI.py layout --apply
    python UI.py status M1/ch01 Building
"""

import argparse
import json
import os
import re
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "UI"))
import core

ROOT = core.default_root()
HERE = os.path.dirname(os.path.abspath(__file__))


class LibraryServer(ThreadingHTTPServer):
    allow_reuse_address = False


def _fail(exc):
    print(exc, file=sys.stderr)
    sys.exit(1)


def cmd_seed(_args):
    try:
        path = core.seed(ROOT)
    except core.LibraryError as exc:
        _fail(exc)
    print(f"seeded {path}")


def cmd_export(args):
    try:
        conn = core.open_db(ROOT)
        if args.report == "outline":
            core.rewrite_readings(conn, ROOT)
            print("wrote EDITORIAL_ORGANIZATION.md and READING_ORDER.md")
        elif args.report == "filter":
            if not args.output:
                _fail(core.LibraryError("filter export needs -o"))
            core.export_filter(conn, args.output, args.book or "", args.status or "", args.level or "", args.presence or "")
            print(f"wrote {args.output}")
        else:
            if not args.scope or not args.output:
                _fail(core.LibraryError("strict export needs --scope and -o"))
            core.export_strict(conn, args.scope, args.output)
            print(f"wrote {args.output}")
        conn.close()
    except core.LibraryError as exc:
        _fail(exc)


def cmd_import(args):
    try:
        conn = core.open_db(ROOT)
        text = core.read_text(args.file)
        detail = core.import_user_file(conn, text)
        core.rewrite_readings(conn, ROOT)
        conn.close()
    except core.LibraryError as exc:
        _fail(exc)
    print(f"imported {detail}")


def cmd_layout(args):
    try:
        conn = core.open_db(ROOT)
        print(core.apply_layout(ROOT, conn, args.apply))
        conn.close()
    except (core.LibraryError, subprocess.CalledProcessError) as exc:
        _fail(exc)


def cmd_status(args):
    try:
        conn = core.open_db(ROOT)
        core.set_status(conn, args.id, args.name)
        core.rewrite_readings(conn, ROOT)
        conn.close()
    except core.LibraryError as exc:
        _fail(exc)
    print(f"{args.id} -> {args.name}")


def _page(filters):
    conn = core.open_db(ROOT)
    try:
        data = core.page_data(conn, filters)
    finally:
        conn.close()
    tab = (filters.get("tab") or ["library"])[0]
    if tab not in ("library", "records", "files"):
        tab = "library"
    data["tab"] = tab
    data["notice"] = (filters.get("notice") or [""])[0]
    data["noticeError"] = (filters.get("error") or ["0"])[0] == "1"
    view = os.path.join(HERE, "UI", "view")
    page = core.read_text(os.path.join(view, "page.html"))
    style = core.read_text(os.path.join(view, "style.css"))
    script = core.read_text(os.path.join(view, "library.js"))
    script += core.read_text(os.path.join(view, "panels.js"))
    payload = json.dumps(data).replace("<", "\\u003c")
    page = page.replace("{{STYLE}}", style).replace("{{SCRIPT}}", script)
    return page.replace("{{DATA}}", payload)


def _multipart(content_type, body):
    """Return ({name: [text]}, {name: (filename, bytes)}) from one upload."""
    match = re.search(r'boundary="?([^";]+)', content_type)
    if not match:
        raise core.LibraryError("missing upload boundary")
    boundary = match.group(1).encode("ascii", "replace")
    fields = {}
    files = {}
    for chunk in body.split(b"--" + boundary)[1:]:
        if chunk.startswith(b"--"):
            break
        if chunk.startswith(b"\r\n"):
            chunk = chunk[2:]
        elif chunk.startswith(b"\n"):
            chunk = chunk[1:]
        sep = b"\r\n\r\n" if b"\r\n\r\n" in chunk else b"\n\n"
        if sep not in chunk:
            continue
        head, payload = chunk.split(sep, 1)
        if payload.endswith(b"\r\n"):
            payload = payload[:-2]
        elif payload.endswith(b"\n"):
            payload = payload[:-1]
        header = head.decode("utf-8", "replace")
        name = re.search(r'name="([^"]*)"', header) or re.search(r"name=([^;\s]+)", header)
        if not name:
            continue
        filename = re.search(r'filename="([^"]*)"', header)
        if filename:
            files[name.group(1)] = (filename.group(1), payload)
        else:
            fields.setdefault(name.group(1), []).append(payload.decode("utf-8"))
    return fields, files


def _redirect_files(handler, notice, error=False):
    query = "tab=files&notice=" + quote(notice[:400])
    if error:
        query += "&error=1"
    handler.send_response(303)
    handler.send_header("Location", "/?" + query)
    handler.send_header("Content-Length", "0")
    handler.end_headers()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[ui]", fmt % args)

    def _send(self, code, body, content_type="text/html; charset=utf-8", extra=None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self):
        raw_length = self.headers.get("Content-Length", "")
        if not str(raw_length).isdigit():
            raise core.LibraryError("missing upload length")
        length = int(raw_length)
        if length > 5_000_000:
            raise core.LibraryError("file is larger than 5 MB")
        return self.rfile.read(length)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/export":
            self._export(parse_qs(parsed.query))
            return
        if parsed.path != "/":
            self._send(404, "not found", "text/plain; charset=utf-8")
            return
        try:
            body = _page(parse_qs(parsed.query))
        except core.LibraryError as exc:
            self._send(500, str(exc), "text/plain; charset=utf-8")
            return
        self._send(200, body)

    def _export(self, query):
        doc = (query.get("doc") or [""])[0].strip()
        book = (query.get("book") or [""])[0].strip()
        try:
            names = core.save_export(ROOT, doc, book)
        except core.LibraryError as exc:
            _redirect_files(self, "Export failed: " + str(exc), error=True)
            return
        if doc == "internal-references":
            notice = f"Overwrote {names[0]} from the stored scan."
        elif len(names) == 1:
            notice = f"Overwrote {names[0]}."
        else:
            notice = "Overwrote " + ", ".join(names) + "."
        _redirect_files(self, notice)

    def _uploaded_markdown(self):
        ctype = self.headers.get("Content-Type", "")
        body = self._read_body()
        if ctype.startswith("multipart/form-data"):
            _fields, files = _multipart(ctype, body)
            if "file" not in files:
                raise core.LibraryError("choose a .md file")
            filename, raw = files["file"]
        else:
            form = parse_qs(body.decode("utf-8"))
            pasted = (form.get("text") or [""])[0]
            if not pasted.strip():
                raise core.LibraryError("choose a .md file")
            return "pasted.md", pasted
        filename = os.path.basename(filename.replace("\\", "/"))
        ext = os.path.splitext(filename)[1].lower()
        if ext not in (".md", ".markdown"):
            raise core.LibraryError("choose a .md file")
        if not raw:
            raise core.LibraryError("the file is empty")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise core.LibraryError("file must be UTF-8") from exc
        return filename, text

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/import":
            self._import()
            return
        if parsed.path == "/scan-xrefs":
            self._scan_xrefs()
            return
        if parsed.path not in ("/status", "/record"):
            self._send(404, "not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, "missing upload length", "text/plain; charset=utf-8")
            return
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        ident = (form.get("id") or [""])[0]
        nxt = (form.get("next") or ["/"])[0]
        try:
            conn = core.open_db(ROOT)
            if parsed.path == "/status":
                name = (form.get("status") or [""])[0]
                core.set_status(conn, ident, name)
            else:
                presence = (form.get("presence") or [""])[0]
                status = (form.get("status") or [""])[0]
                kwargs = {}
                if "level" in form:
                    kwargs["level"] = (form.get("level") or [""])[0]
                if presence:
                    kwargs["presence"] = presence
                if status:
                    kwargs["editorial_status"] = status
                core.update_record(conn, ident, **kwargs)
            core.rewrite_readings(conn, ROOT)
            conn.close()
        except core.LibraryError as exc:
            self._send(400, str(exc), "text/plain; charset=utf-8")
            return
        self.send_response(303)
        self.send_header("Location", nxt if nxt.startswith("/") else "/")
        self.end_headers()

    def _import(self):
        try:
            ctype = self.headers.get("Content-Type", "")
            body = self._read_body()
            if not ctype.startswith("multipart/form-data"):
                raise core.LibraryError("choose a file")
            fields, files = _multipart(ctype, body)
            mode = (fields.get("mode") or [""])[0].strip()
            book = (fields.get("book") or [""])[0].strip()
            conn = core.open_db(ROOT)
            try:
                if mode == "book" and book == "all":
                    filename = "the project organization files"
                    summary = core.import_project_books(conn, ROOT)
                elif mode == "book":
                    filename = core.organization_relpath(conn, book) if book else "the book organization file"
                    summary = core.import_project_book(conn, ROOT, book)
                else:
                    if "file" not in files:
                        raise core.LibraryError("choose a file")
                    filename, raw = files["file"]
                    filename = os.path.basename(filename.replace("\\", "/"))
                    summary = core.import_chosen(conn, mode, book, filename, raw)
                core.rewrite_readings(conn, ROOT)
            finally:
                conn.close()
        except core.LibraryError as exc:
            _redirect_files(self, "Import failed: " + str(exc), error=True)
            return
        _redirect_files(self, f"Imported {filename}. {summary} EDITORIAL_ORGANIZATION.md was rewritten.")

    def _scan_xrefs(self):
        try:
            conn = core.open_db(ROOT)
            try:
                summary = core.scan_cross_references(ROOT, conn)
            finally:
                conn.close()
        except core.LibraryError as exc:
            _redirect_files(self, "Scan failed: " + str(exc), error=True)
            return
        _redirect_files(self, summary)


def cmd_scan(_args):
    try:
        conn = core.open_db(ROOT)
        try:
            print(core.scan_cross_references(ROOT, conn))
        finally:
            conn.close()
    except core.LibraryError as exc:
        _fail(exc)


def cmd_serve(args):
    try:
        server = LibraryServer(("127.0.0.1", args.port), Handler)
    except OSError as exc:
        _fail(f"port {args.port} is already in use: {exc}")
    url = f"http://127.0.0.1:{args.port}/"
    print(f"library UI at {url}")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Syllabus database")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("seed", help="parse EDITORIAL_ORGANIZATION.md once").set_defaults(func=cmd_seed)

    exp = sub.add_parser("export", help="write a strict file or a reading")
    exp.add_argument("--scope", help="library, a book code, or a chapter id")
    exp.add_argument("--report", choices=("outline", "filter"))
    exp.add_argument("-o", "--output")
    exp.add_argument("--book")
    exp.add_argument("--status")
    exp.add_argument("--level")
    exp.add_argument("--presence")
    exp.set_defaults(func=cmd_export)

    imp = sub.add_parser("import", help="apply a strict markdown file")
    imp.add_argument("file")
    imp.set_defaults(func=cmd_import)

    lay = sub.add_parser("layout", help="show or apply folder changes")
    lay.add_argument("--apply", action="store_true")
    lay.set_defaults(func=cmd_layout)

    st = sub.add_parser("status", help="set editorial status")
    st.add_argument("id")
    st.add_argument("name")
    st.set_defaults(func=cmd_status)

    scan = sub.add_parser("scan-xrefs", help="reread .tex files into the internal-reference tables")
    scan.set_defaults(func=cmd_scan)

    srv = sub.add_parser("serve", help="browse on localhost")
    srv.add_argument("--port", type=int, default=8765)
    srv.add_argument("--no-browser", action="store_true")
    srv.set_defaults(func=cmd_serve)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
