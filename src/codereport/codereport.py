import os
import re
from pathlib import Path

# 3rd party
from slugify import slugify
import pygments
from pygments import highlight
from pygments.lexers.c_cpp import CppLexer
from pygments.lexers import guess_lexer_for_filename
import itertools
from collections import OrderedDict

from .html import HtmlFormatter, get_style
from .templates import *
from .filetree import make_file_tree, SourceFile


def _get_lexer(srcfile, raw_content):
    try:
        lexer = guess_lexer_for_filename(srcfile.raw_path, raw_content)
    except pygments.util.ClassNotFound:
        if srcfile.path.endswith(".ipp"):
            lexer = CppLexer()
        else:
            raise

    return lexer


class CodeReport:
    def __init__(
        self,
        items,
        encoding="utf-8",
        title="Code Report",
        srcdir=None,
        rootdir="/",
    ):
        self._items = items
        self._title = title
        self._encoding = encoding
        self._srcdir = Path(srcdir) if srcdir is not None else None
        self._rootdir = rootdir

        self._srcfiles = []

    def _resolve_src(self, relpath):
        """Resolve a source file path, optionally relative to srcdir."""
        if self._srcdir is not None:
            return self._srcdir / relpath
        return Path(relpath)

    def render(self, destdir):
        destdir = Path(destdir)

        kf = lambda i: os.path.normpath(i.path)
        for file, items in itertools.groupby(sorted(self._items, key=kf), kf):
            items = list(items)

            def normpath(s):
                out = s
                if s.startswith(self._rootdir):
                    out = s[len(self._rootdir) :]
                return os.path.normpath(out)

            srcfile = SourceFile(items[0].path, normpath=normpath)
            srcfile.add_items(items)
            self._srcfiles.append(srcfile)

        self._filetree = make_file_tree(self._srcfiles)

        destdir.mkdir(parents=True, exist_ok=True)

        for sf in self._srcfiles:
            (destdir / sf.report_file_name).write_text(
                self._render_code_file(sf), encoding=self._encoding
            )

        (destdir / "index.html").write_text(
            self._render_index(), encoding=self._encoding
        )

        (destdir / "index_summary.html").write_text(
            self._render_summary(self._items, standalone=True),
            encoding=self._encoding,
        )

        kf = lambda i: i.code
        for code, items in itertools.groupby(sorted(self._items, key=kf), kf):
            (destdir / f"{code}.html").write_text(
                self._render_code_summary(code, items), encoding=self._encoding
            )

    def _render_code_file(self, srcfile):
        raw_content = self._resolve_src(srcfile.raw_path).read_text(
            encoding=self._encoding
        )

        lexer = _get_lexer(srcfile, raw_content)

        def get_comment(lineno):
            items = filter(lambda i: i.line == lineno, srcfile.items)
            return "\n\n".join(map(str, items))

        code = highlight(raw_content, lexer, HtmlFormatter(get_comment))

        return file_tpl.render(
            srcfile=srcfile,
            code=code,
            summary=self._render_summary(srcfile.items, srcfile=srcfile),
            title=self._title,
        )

    def _render_index(self):
        return index_tpl.render(
            nodelist=[self._filetree],
            summary=self._render_summary(self._items),
            title=self._title,
        )

    def _render_summary(self, items, standalone=False, srcfile=None):
        kf = lambda i: i.code
        by_code = {}
        for item in items:
            if not item.code in by_code:
                by_code[item.code] = []
            by_code[item.code].append(item)

        by_code = OrderedDict(
            reversed(sorted(by_code.items(), key=lambda i: len(i[1])))
        )

        files = set([i.path for i in items])

        return summary_tpl.render(
            by_code=by_code,
            standalone=standalone,
            single_file=len(files) > 1,
            srcfile=srcfile,
        )

    def _render_code_summary(self, code, items):
        fk = lambda i: i.srcfile

        file_html = []

        for srcfile, file_items in itertools.groupby(sorted(items, key=fk), fk):

            file_items = list(sorted(file_items, key=lambda i: i.line))

            def get_comment(lineno):
                items = filter(
                    lambda i: i.line == lineno and i.code == code, srcfile.items
                )
                return "\n\n".join(map(str, items))

            raw_content = self._resolve_src(srcfile.raw_path).read_text(
                encoding=self._encoding
            )
            lexer = _get_lexer(srcfile, raw_content)
            lines = raw_content.split("\n")

            context = 5

            merged_items = []

            for item in file_items:
                if item.code != code:
                    continue
                #  print(item.srcfile.path, item.line - context, item.line + context)
                start = item.line - context
                end = item.line + context
                if len(merged_items) == 0:
                    merged_items.append((start, end))
                    continue

                (lstart, lend) = merged_items[-1]

                if start >= lstart and start <= lend:
                    #  print("MERGE!")
                    start = min(start, lstart)
                    end = max(end, lend)
                    merged_items[-1] = start, end
                else:
                    merged_items.append((start, end))

            html = []

            for start, end in merged_items:
                chunk = "\n".join(lines[start:end]).encode()

                _code = highlight(
                    chunk,
                    lexer,
                    HtmlFormatter(get_comment, linenostart=start + 1),
                )

                html.append(_code)

            file_html.append((srcfile, html))

        return code_tpl.render(code=code, title=self._title, data=file_html)
