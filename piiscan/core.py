"""Detect and mask personal data (PII) in tabular data."""
import re
import pandas as pd

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "aadhaar": re.compile(r"(?<!\d)[2-9]\d{3}\s?\d{4}\s?\d{4}(?!\s?\d)"),
    "pan": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    "ipv4": re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    "phone": re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,11}\d(?!\d)"),
}
# Order matters: more specific patterns first so they are not mislabelled as phone numbers.
ORDER = ["email", "pan", "ipv4", "credit_card", "aadhaar", "phone"]


def luhn_ok(s: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", s)]
    if not 13 <= len(digits) <= 16:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def find_pii(value) -> list:
    """Return the PII types found in one cell, most specific first."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value)
    found, remaining = [], text
    for kind in ORDER:
        for m in PATTERNS[kind].finditer(remaining):
            if kind == "credit_card" and not luhn_ok(m.group()):
                continue
            found.append(kind)
            remaining = remaining.replace(m.group(), " ")
            break
    return found


def scan(df: pd.DataFrame) -> dict:
    """Count PII hits per column and type."""
    report = {}
    for col in df.columns:
        counts = {}
        for v in df[col]:
            for kind in find_pii(v):
                counts[kind] = counts.get(kind, 0) + 1
        if counts:
            report[col] = counts
    return report


def _mask_text(text: str) -> str:
    for kind in ORDER:
        def repl(m, kind=kind):
            if kind == "credit_card" and not luhn_ok(m.group()):
                return m.group()
            return f"[{kind.upper()}]"
        text = PATTERNS[kind].sub(repl, text)
    return text


def mask(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with every detected PII value replaced by a [TYPE] tag."""
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].map(lambda v: _mask_text(v) if isinstance(v, str) else v)
    return out


def format_report(report: dict, rows: int) -> str:
    if not report:
        return f"No PII detected in {rows} rows."
    lines = [f"PII found in {len(report)} column(s) across {rows} rows:", ""]
    for col, counts in report.items():
        detail = ", ".join(f"{k}: {n}" for k, n in sorted(counts.items()))
        lines.append(f"  {col:<20} {detail}")
    return "\n".join(lines)
