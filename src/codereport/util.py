import json
from pathlib import Path

from .codereport import CodeReport
from .reportitem import ReportItem


def make_report_items(items, path_resolver):
    outitems = []
    for item in items:
        new_path = path_resolver(item["path"])
        item["path"] = new_path
        outitems.append(ReportItem(**item))
    return outitems


def report_from_json(
    item_file,
    dest,
    title,
    path_resolver=lambda s: s,
    prefix=None,
):
    item_file = Path(item_file)
    dest = Path(dest)

    assert item_file.exists()

    data = json.loads(item_file.read_text())

    report_items = make_report_items(data, path_resolver)
    report_items = [r for r in report_items if Path(r.path).exists()]

    if len(report_items) == 0:
        return

    if len(report_items) == 1:
        item_path = report_items[0].path
        if item_file.is_file():
            prefix = str(Path(item_path).parent)
        else:
            prefix = item_path
    else:
        from os.path import commonprefix

        prefix = prefix or commonprefix([s.path for s in report_items])

    cp = CodeReport(report_items, rootdir=prefix, title=title)

    cp.render(dest)
