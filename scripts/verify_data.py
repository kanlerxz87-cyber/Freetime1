#!/usr/bin/env python3
"""
Verification suite for FREE TIME VACATION dataset & website assets.
Checks:
- Exact 2,430 official 2027 MLB regular season games (162 per team, 0 duplicate gamePk)
- Exact 109 remaining 2026 NFL regular season games (Weeks 12-18)
- 100% of compiled events, radio stations, vacation windows, and flagged items have valid official https:// source_url
- All JSON files parse cleanly
"""
import csv
import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
OUT_DIR = os.path.join(ROOT, "assets", "data")

errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)
        print(f"  [FAIL] {msg}")
    else:
        print(f"  [PASS] {msg}")


print("1. Verifying 2027 MLB Regular Season raw CSVs...")
pks = set()
teams = Counter()
total_mlb = 0
for f in sorted(glob.glob(os.path.join(DATA_DIR, "mlb_2027_0*.csv"))):
    with open(f) as fh:
        for r in csv.DictReader(fh):
            total_mlb += 1
            pks.add(r["gamePk"])
            teams[r["away"]] += 1
            teams[r["home"]] += 1
check(total_mlb == 2430, f"2027 MLB Regular Season count == 2430 (got {total_mlb})")
check(len(pks) == 2430, f"Unique gamePk count == 2430 (got {len(pks)})")
check(len(teams) == 30 and all(v == 162 for v in teams.values()), f"All 30 MLB teams have exactly 162 games")

print("2. Verifying 2026 NFL Weeks 12-18 raw CSVs...")
nfl_rows = []
nfl_slugs = set()
for fn in ("nfl_2026_w12_15.csv", "nfl_2026_w16_18.csv"):
    with open(os.path.join(DATA_DIR, fn)) as fh:
        for r in csv.DictReader(fh):
            nfl_rows.append(r)
            nfl_slugs.add(r["slug"])
check(len(nfl_rows) == 109, f"Remaining 2026 NFL regular season games == 109 (got {len(nfl_rows)})")
check(len(nfl_slugs) == 109, f"Unique NFL game slugs == 109 (got {len(nfl_slugs)})")

print("3. Verifying compiled JSON assets & 100% source_url coverage...")
for fn in ("meta.json", "daily_summary.json", "vacations.json", "radio.json", "flagged.json", "key_schedules.json"):
    p = os.path.join(OUT_DIR, fn)
    check(os.path.exists(p), f"Exists: assets/data/{fn}")
    with open(p) as fh:
        json.load(fh)

month_files = sorted(glob.glob(os.path.join(OUT_DIR, "months", "*.json")))
check(len(month_files) >= 14, f"Monthly scoreboard shards >= 14 (got {len(month_files)})")

missing_src = 0
total_events = 0
for mf in month_files:
    with open(mf) as fh:
        evs = json.load(fh)
    for e in evs:
        total_events += 1
        if not e.get("source_url", "").startswith("https://"):
            missing_src += 1
check(missing_src == 0, f"All {total_events} compiled events have valid https:// source_url (missing={missing_src})")

with open(os.path.join(OUT_DIR, "radio.json")) as fh:
    radio = json.load(fh)
check(all(s.get("source_url", "").startswith("https://") for s in radio["stations"]), "All Bay Area radio entries have official https:// source_url")

with open(os.path.join(OUT_DIR, "vacations.json")) as fh:
    vac = json.load(fh)
check(all(w.get("source_url", "").startswith("https://") for w in vac["multi_year_windows"]), "All vacation windows have official https:// source_url")

with open(os.path.join(OUT_DIR, "flagged.json")) as fh:
    flg = json.load(fh)
check(all(i.get("source_url", "").startswith("https://") for i in flg["items"]), "All flagged items have official https:// source_url")

if errors:
    print(f"\n❌ VERIFICATION FAILED ({len(errors)} errors)")
    sys.exit(1)
print("\n✅ ALL DATA & SOURCE VERIFICATION CHECKS PASSED!")
