import argparse
import json
import os

from codereport import CodeReport, ReportItem

def make_report_items(items, path_resolver):
    outitems=[]
    for item in items:
        item["path"] = path_resolver(item["path"])
        outitems.append(ReportItem(**item))
    return outitems

def main():
    p = argparse.ArgumentParser(description="Generate a code report")
    p.add_argument("item_file", help="JSON file to take items from")
    p.add_argument("dest", help="Destionation folder for the report")
    p.add_argument("--map-dir", action="append", default=[], type=lambda s: s.split(":"))
    p.add_argument("--title", help="Sets the title for the report", default="Code report")

    args = p.parse_args()

    def path_resolver(p):
        for src, dest in args.map_dir:
            if p.startswith(src):
                return dest+p[len(src):]
        return p

    assert os.path.exists(args.item_file)

    with open(args.item_file, "r") as f:
        data = json.load(f)

    report_items = make_report_items(data, path_resolver)
    report_items = list(filter(lambda s: os.path.exists(s.path), report_items))

    prefix = os.path.commonprefix([s.path for s in report_items])

    cp = CodeReport(report_items, rootdir=prefix)
    cp.render(args.dest)



