# piiscan 🛡️

Check a CSV for personal data **before** you share it, publish it, or commit it to GitHub.

Detects: emails, phone numbers, credit cards (Luhn-validated), Aadhaar numbers, PAN numbers, and IPv4 addresses.

## Install
```bash
pip install .
```

## Usage
```bash
piiscan customers.csv                       # report only
piiscan customers.csv --json                # machine-readable report
piiscan customers.csv --mask clean.csv      # also write a masked copy
```

Example:
```
PII found in 2 column(s) across 500 rows:

  contact              email: 312, phone: 140
  notes                ipv4: 9
```

Masked values become tags such as `[EMAIL]` or `[PHONE]`.

The exit code is `1` when PII is found and `0` when clean, so it works in CI:
```bash
piiscan data/train.csv || echo "Remove PII before committing!"
```

## Limitations
Regex-based detection can miss unusual formats and can occasionally flag lookalike numbers. It does **not** detect names or addresses. Treat it as a first-pass safety net, not a compliance guarantee.

## Test
```bash
pip install pytest && pytest
```

## Roadmap
- Name and address detection (NER)
- Excel and Parquet input
- Custom regex rules via a config file
- Pre-commit hook

MIT licensed. Contributions welcome.
