import os
import html

class ReportItem:
    def __init__(self, path, line, severity, message, code, col=0):
        self.path = path
        self.line = int(line)
        self.severity = severity
        self.message = message
        self.code = code
        self.col = int(col)
        self.srcfile = None

        self._path_resolver = lambda s: s

    def set_srcfile(self, srcfile):
        self.srcfile = srcfile

    def __repr__(self):
        p = (self.path, self.line, self.code, self.message[:15])
        return 'ReportItem(path="%s", line="%d", code="%s", message="%s")' % p

    def __str__(self):
        msg = html.escape("{sev} [{code}]:\n{msg}".format(sev=self.severity, code=self.code, msg=self.message))
        return "\n".join(['<pre style="display:block;white-space:pre-wrap;">%s</pre>' % l for l in msg.split("\n")])

    def dict(self):
        return {
            "path": self.path,
            "line": self.line,
            "severity": self.severity,
            "message": self.message,
            "code": self.code,
            "col": self.col
        }

    def __hash__(self):
        return hash((self.path, self.line, self.col, self.code))

    def __eq__(self, o):
        return (self.path == o.path
                and self.line == o.line
                and self.col == o.col
                and self.code = o.code)
