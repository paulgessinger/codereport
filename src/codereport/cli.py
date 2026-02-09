import argparse
from pathlib import Path

from codereport.util import report_from_json


def main():
    p = argparse.ArgumentParser(description="Generate a code report")
    p.add_argument("item_file", help="JSON file to take items from")
    p.add_argument("dest", help="Destination folder for the report")
    p.add_argument(
        "--map-dir", action="append", default=[], type=lambda s: s.split(":")
    )
    p.add_argument(
        "--title", help="Sets the title for the report", default="Code report"
    )
    p.add_argument("--prefix", help="Remove prefix from files", default=None)
    args = p.parse_args()

    def path_resolver(p):
        for src, dest in args.map_dir:
            if p.startswith(src):
                return dest + p[len(src) :]
        return p

    report_from_json(
        Path(args.item_file).resolve(),
        Path(args.dest).resolve(),
        args.title,
        prefix=args.prefix,
        path_resolver=path_resolver,
    )
