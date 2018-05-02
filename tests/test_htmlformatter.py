from codereport.html import HtmlFormatter
from unittest.mock import Mock, call, patch
# from .templates import line_tpl

def test_wrap():
    tpl_mock = Mock()
    get_line_comment_mock = Mock()
    get_line_comment_mock.side_effect = [None, "LINE 2 COMMENT", None]
    
    html_formatter = HtmlFormatter(get_line_comment=get_line_comment_mock)

    source = [(1, "LINE_A"), (1, "LINE_B"), (1, "LINE_C")]
    outfile = "abc.html"
    
    with patch("codereport.templates.line_tpl", tpl_mock):
        list(html_formatter.wrap(source, outfile))

    assert tpl_mock.render.call_count == len(source)
    tpl_mock.render.assert_has_calls([
        call(lineno=1, cls="", comment=None, code=source[0][1], style=""),
        call(lineno=2, cls="has_comment", comment="LINE 2 COMMENT", code=source[1][1], style=""),
        call(lineno=3, cls="", comment=None, code=source[2][1], style="")
    ])

    assert get_line_comment_mock.call_count == len(source)

