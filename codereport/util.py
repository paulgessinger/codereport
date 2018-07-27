import json
import os
from fs.osfs import OSFS

from .codereport import CodeReport
from .reportitem import ReportItem

def make_report_items(items, path_resolver):
    outitems=[]
    for item in items:
        item["path"] = path_resolver(item["path"])
        outitems.append(ReportItem(**item))
    return outitems

def report_from_json(item_file, dest, title, srcfs = None, 
                     destfs = None, path_resolver = lambda s: s, prefix=None):

    srcfs = srcfs or OSFS("/")
    destfs = destfs or OSFS("/")

    assert os.path.exists(item_file)
    with open(item_file, "r") as f:
        data = json.load(f)

    report_items = make_report_items(data, path_resolver)
    report_items = list(filter(lambda s: os.path.exists(s.path), report_items))

    assert len(report_items) > 0, "No existing files found"

    prefix = prefix or os.path.commonprefix([s.path for s in report_items])

    cp = CodeReport(report_items,
                    rootdir=prefix,
                    title=title,
                    srcfs=srcfs,
                    destfs=destfs)

    cp.render(dest)


