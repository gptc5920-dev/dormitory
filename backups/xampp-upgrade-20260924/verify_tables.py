"""Compare exact table contents across the XAMPP upgrade (no data is printed)."""
import hashlib
import json
import sys
from pathlib import Path

import MySQLdb

root = Path(__file__).resolve().parent
baseline = json.loads((root / "xampp-data-before.json").read_text())
connection = MySQLdb.connect(host="127.0.0.1", port=int(sys.argv[1]), user="root", charset="utf8mb4")
cursor = connection.cursor()
differences = []
for label, expected in baseline.items():
    # phpMyAdmin updates UI preferences while the user browses the server.
    if label == "phpmyadmin.pma__userconfig":
        continue
    schema, table = label.rsplit(".", 1)
    quote = lambda value: "`" + value.replace("`", "``") + "`"
    cursor.execute(f"SELECT * FROM {quote(schema)}.{quote(table)}")
    rows = sorted(repr(row) for row in cursor.fetchall())
    actual = {"rows": len(rows), "sha256": hashlib.sha256("\n".join(rows).encode()).hexdigest()}
    if actual != expected:
        differences.append(label)
print(f"Verified {len(baseline) - 1} existing XAMPP tables (excluding live UI preferences); mismatches: {differences}")
connection.close()
if differences:
    raise SystemExit(1)
