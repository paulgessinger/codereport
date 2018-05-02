from pygments.formatters import HtmlFormatter as VanillaHtmlFormatter


_css_styles = VanillaHtmlFormatter().get_style_defs(".highlight")
def get_style():
    return _css_styles

class HtmlFormatter(VanillaHtmlFormatter):
    def __init__(self,  get_line_comment, *args, **kwargs):
        self._get_line_comment = get_line_comment
        super().__init__(*args, **kwargs)

    def wrap(self, source, outfile):
        return self._wrap_div(self._wrap_lines(source))

    def _wrap_lines(self, source):
        from .templates import line_tpl

        style = []
        if self.prestyles:
            style.append(self.prestyles)
        if self.noclasses:
            style.append('line-height: 125%')
        style = '; '.join(style)

        i = self.linenostart
        for t, line in source:
            if t == 1:
                comment = self._get_line_comment(i)

                cssclass = "has_comment" if comment else ""
                line = line_tpl.render(lineno=i,
                                             cls=cssclass,
                                             comment=comment,
                                             code=line,
                                             style=style)
                i += 1
            yield t, line
