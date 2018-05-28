import os
import re

# 3rd party
from slugify import slugify
import pygments
from pygments import highlight
from pygments.lexers.c_cpp import CppLexer
from pygments.lexers import guess_lexer_for_filename

from .html import HtmlFormatter, get_style
from .templates import file_tpl, index_tpl


class TreeNode:
    def __init__(self):
        self.subdirs = []
        self.files = []

    def __repr__(self):
        return "Node("+self.name+": "+repr((self.subdirs, self.files))+")"

class CodeReport:
    def __init__(self, files, get_comment, encoding="utf-8", title="Code Report", commonprefix=os.path.commonprefix):
        self._files = list(map(lambda s: re.sub(r"//+", "/", s), files))
        self._common_prefix = commonprefix(self._files)
        self._get_comment = get_comment
        self._title = title
        self._encoding = encoding

    def _normalize(self, path):
        if path.startswith(self._common_prefix):
            return path[len(self._common_prefix):]
        return path

    def files(self):
        self._file_item_counts = {}

        reportfiles = map(lambda s: (self._normalize(s), s), self._files)

        for dest, src in reportfiles:
            self._file_item_counts[src] = 0
            yield self._make_filename(dest), self._process_file(src)

        yield "index.html", self._make_index()

    def get_file_link(self, file, line=0, col=0):
        file = self._normalize(file)
        if line == 0 and col == 0:
            return self._make_filename(file)
        return "{}#L{}".format(self._make_filename(file), line)

    def _make_filename(self, filename):
        return "{}.html".format(slugify(filename))


    def _make_index(self):
        files = []
        for k, v in self._file_item_counts.items():
            files.append((self._normalize(k), v, self.get_file_link(k)))


        files = reversed(sorted(files, key=lambda f: f[1]))

        return index_tpl.render(files=files,
                               title=self._title)

    def _make_file_tree(self):

        files_sorted = map(self._normalize, sorted(self._files))
        files_sorted = [(s.split(os.sep), s) for s in files_sorted]

        return [self._rec_group(".", files_sorted)]

    def _rec_group(self, name, items):
        node = TreeNode()
        node.name = name

        groups = {}
        # files = []
        for segments, path in items:
            if len(segments) == 1:
                # this group is final
                node.files.append((segments[0], self._make_filename(path)))
                continue
            prim = segments[0]
            rest = segments[1:]

            if not prim in groups:
                groups[prim] = []
            groups[prim].append((rest, path))

        # have all groups
        for k, v in groups.items():
            node.subdirs.append(self._rec_group(k, v))

        return node


    def _process_file(self, f):

        filetree = self._make_file_tree()

        with open(f, "r", encoding=self._encoding) as fh:
            raw_content = fh.read()

        try:
            lexer = guess_lexer_for_filename(f, raw_content)
        except pygments.util.ClassNotFound:
            if f.endswith(".ipp"):
                lexer = CppLexer()

        def get_comment(lineno):
            msgs = self._get_comment(f, lineno, self)
            if msgs is not None:
                self._file_item_counts[f] += len(msgs)
                return "\n".join(msgs)
            return None

        code = highlight(raw_content, lexer, HtmlFormatter(get_comment))


        return file_tpl.render(filetree=filetree,
                              active_file=self._make_filename(self._normalize(f)),
                              filename=f,
                              code=code,
                              title=self._title)
        

    def __iter__(self):
        return self.files()
