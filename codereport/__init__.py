import os
import re
from datetime import datetime

from jinja2 import Environment, PackageLoader, select_autoescape
from slugify import slugify

import pygments
from pygments import highlight
from pygments.lexers.c_cpp import CppLexer
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter

env = Environment(
    loader=PackageLoader('codereport', 'templates'),
        
)
env.globals["pygments_style"] = HtmlFormatter().get_style_defs('.highlight')
env.globals["report_created"] = datetime.now().strftime("%H:%M:%S %d.%m.%Y")

filetpl = env.get_template("file.html")
indextpl = env.get_template("index.html")



class HtmlLineFormatter(HtmlFormatter):

    def __init__(self, get_line_comment, *args, **kwargs):
        self._get_line_comment = get_line_comment
        super().__init__(*args, **kwargs)

    def wrap(self, source, outfile):
        return self._wrap_div(self._wrap_lines(source))

    def _wrap_lines(self, source):
        style = []
        if self.prestyles:
            style.append(self.prestyles)
        if self.noclasses:
            style.append('line-height: 125%')
        style = '; '.join(style)

        # the empty span here is to keep leading empty lines from being
        # ignored by HTML parsers
        i = self.linenostart
        for t, line in source:
            if t == 1:
                # line = '<span id="LC%d">%s</span>' % (i, line)
                # line = '{} {}'.format(i, self._wrap_pre(str(line)))
                # line = self._wrap_pre(ine)
                comment = self._get_line_comment(i)

                cssclass = " has_comment" if comment else ""

                line = '<pre' + (style and ' style="%s"' % style) + '>' + line + '</pre>'
                line = '<span id="L{lineno}" class="line{cls}"><span class="lineno"><pre>{lineno: >4d}</pre></span><span class="code">'.format(lineno=i, cls=cssclass) + line
                line += '</span><span class="comment">{}</span></span>'.format(comment if comment else "")
                i += 1
            yield t, line

class TreeNode:
    def __init__(self):
        self.subdirs = []
        self.files = []

    def __repr__(self):
        return "Node("+self.name+": "+repr((self.subdirs, self.files))+")"


class CodeReport:
    def __init__(self, files, get_display_name, get_comment, title="Code Report"):
        self._files = files
        self._get_display_name = get_display_name
        self._get_comment = get_comment
        self._title = title

    def get_file_link(self, file, line=0, col=0):
        if line == 0 and col == 0:
            return self._make_filename(file)
        return "{}#L{}".format(self._make_filename(file), line)

    def _make_filename(self, filename):
        return "{}.html".format(slugify(self._get_display_name(filename)))

    def files(self):

        self._file_item_counts = {}


        for f in self._files:
            self._file_item_counts[f] = 0
            yield self._make_filename(f), self._process_file(f)

        yield "index.html", self._make_index()

    def _make_index(self):

        files = []
        for k, v in self._file_item_counts.items():
            files.append((k, v, self.get_file_link(k)))


        files = reversed(sorted(files, key=lambda f: f[1]))

        return indextpl.render(files=files,
                               title=self._title)

    def _make_file_tree(self):
        common_prefix = os.path.commonprefix(self._files)

        files_sorted = map(lambda s: re.sub(r"//+", "/", s.replace(common_prefix, "")), sorted(self._files))
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

        def files():
            for _f in self._files:
                yield _f, self._make_filename(_f), f == _f

        with open(f, "r") as fh:
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

        code = highlight(raw_content, lexer, HtmlLineFormatter(get_comment))


        return filetpl.render(filetree=filetree,
                              active_file=self._make_filename(f),
                              filename=f,
                              code=code,
                              title=self._title)
        

    def __iter__(self):
        return self.files()
