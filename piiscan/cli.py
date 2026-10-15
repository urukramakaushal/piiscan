import argparse
import json
import sys
import pandas as pd
from .core import scan, mask, format_report


def main():
    p = argparse.ArgumentParser(prog="piiscan", description="Scan a CSV for personal data and optionally mask it.")
    p.add_argument("path", help="CSV file to scan")
    p.add_argument("--mask", metavar="OUT", help="write a masked copy to this CSV path")
    p.add_argument("--json", action="store_true", help="print the report as JSON")
    a = p.parse_args()

    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            df = pd.read_csv(a.path, dtype=str, encoding=enc)
            break
        except UnicodeDecodeError:
            continue

    report = scan(df)
    print(json.dumps(report, indent=2) if a.json else format_report(report, len(df)))
    if a.mask:
        mask(df).to_csv(a.mask, index=False)
        print(f"\nMasked copy saved to {a.mask}", file=sys.stderr)
    sys.exit(1 if report else 0)  # non-zero exit lets you use it in CI


if __name__ == "__main__":
    main()
