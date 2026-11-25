#!/usr/bin/env python3
"""Automated line-by-line link, schema, and official-source verifier for `vacation-hub/`."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

PLANNER_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = PLANNER_DIR.parent

OFFICIAL_HOST_SUFFIXES = (
    "mlb.com",
    "nfl.com",
    "westwoodonesports.com",
    "gostanford.com",
    "calbears.com",
    "collegefootballplayoff.com",
    "ncaa.com",
    "nba.com",
    "wnba.com",
    "sjearthquakes.com",
    "nhl.com",
    # 32 official NFL club domains
    "49ers.com", "azcardinals.com", "atlantafalcons.com", "baltimoreravens.com",
    "buffalobills.com", "panthers.com", "chicagobears.com", "bengals.com",
    "clevelandbrowns.com", "dallascowboys.com", "denverbroncos.com", "detroitlions.com",
    "packers.com", "houstontexans.com", "colts.com", "jaguars.com", "chiefs.com",
    "raiders.com", "chargers.com", "therams.com", "miamidolphins.com", "vikings.com",
    "patriots.com", "neworleanssaints.com", "giants.com", "newyorkjets.com",
    "philadelphiaeagles.com", "steelers.com", "seahawks.com", "buccaneers.com",
    "tennesseetitans.com", "commanders.com",
)


def is_official_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return False
    host = parsed.hostname.lower()
    return any(host == sfx or host.endswith("." + sfx) for sfx in OFFICIAL_HOST_SUFFIXES)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.links.append(v)


errors: list[str] = []

# 1. Check all HTML pages & links inside vacation-hub/ and README.md
html_files = sorted(PLANNER_DIR.glob("*.html"))
assert len(html_files) == 8, f"Expected 8 HTML pages in vacation-hub/, found {len(html_files)}"

external_urls: set[str] = set()
for hf in html_files:
    parser = LinkCollector()
    parser.feed(hf.read_text())
    for raw in parser.links:
        if raw.startswith(("http://", "https://")):
            external_urls.add(raw)
            if not is_official_url(raw):
                errors.append(f"{hf.name}: non-official external URL {raw}")
        elif raw.startswith("#") or raw.startswith("mailto:"):
            continue
        else:
            clean = raw.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            target = (hf.parent / clean).resolve()
            if not target.exists():
                errors.append(f"{hf.name}: broken relative link {raw} -> {target}")

# 2. Check all JSON files and verify every `source_url` / `official_url` is an official domain
for jf in sorted((PLANNER_DIR / "data").glob("*.json")):
    data = json.loads(jf.read_text())
    text = json.dumps(data)
    for m in re.finditer(r'https?://[^"\\\s]+', text):
        u = m.group(0)
        external_urls.add(u)
        if not is_official_url(u):
            errors.append(f"{jf.name}: non-official URL {u}")

# 3. Verify strict blank rule on TBD MLB games
master = json.loads((PLANNER_DIR / "data" / "schedules_master.json").read_text())
for club_key in ("giants_2027", "athletics_2027"):
    rows = master[club_key]
    for g in rows:
        if g["time_tbd"] and (g["official_time_pst"] != "" or g["official_time_pt"] != ""):
            errors.append(f"{club_key} gamePk {g['gamePk']}: time_tbd=True but official_time not blank!")
        if not g["time_tbd"] and not g["official_time_pst"]:
            errors.append(f"{club_key} gamePk {g['gamePk']}: time_tbd=False but official_time_pst blank!")

# 4. Verify key calendar & vacation invariants
cal = json.loads((PLANNER_DIR / "data" / "daily_calendar.json").read_text())
by_d = {d["d"]: d for d in cal["days"]}
assert len(by_d) == 1461, f"Expected 1461 days, got {len(by_d)}"
assert by_d["2026-11-25"]["free"]["core_strict"] is False, "2026-11-25 must be BUSY (Westwood One GB@LAR)"
assert len([e for e in by_d["2026-11-26"]["events"] if "Westwood One NFL" in e["category"]]) == 3, "Thanksgiving must have 3 Westwood One games"
assert all(by_d[f"2027-02-{d:02d}"]["free"]["core_strict"] for d in range(1, 14)), "Feb 1-13, 2027 must be 13-day strict free window"
assert by_d["2027-02-14"]["free"]["core_strict"] is False, "Super Bowl LXI Feb 14, 2027 must be BUSY"
assert all(by_d[f"2027-02-{d:02d}"]["free"]["full_radio_94122"] for d in range(15, 19)), "Feb 15-18, 2027 must be 4-day full 94122 free window"
assert by_d["2027-07-15"]["free"]["core_strict"] is False, "July 15, 2027 has 1 MLB game in StatsAPI and must be BUSY"

if errors:
    for e in errors:
        print("ERROR:", e, file=sys.stderr)
    sys.exit(1)

print(
    f"VERIFICATION PASSED: {len(html_files)} HTML pages, 0 broken internal links, "
    f"{len(external_urls)} unique official https URLs verified, 1,461 days checked."
)
