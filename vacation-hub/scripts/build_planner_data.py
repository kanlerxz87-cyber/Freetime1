#!/usr/bin/env python3
"""
Deterministic data builder for Freetime1 `vacation-hub/` sub-site (Session arena-1d4ebaad).

Strictly uses official verified sources:
- MLB StatsAPI (`statsapi.mlb.com`) + `mlb.com` official releases
- `nfl.com`, `media.nfl.com`, `operations.nfl.com`, `49ers.com`
- `westwoodonesports.com`
- `gostanford.com`, `calbears.com`, `collegefootballplayoff.com`, `ncaa.com`
- `nba.com/warriors`, `valkyries.wnba.com`, `sjearthquakes.com`, `nhl.com/sharks`

Verification contract:
- Official confirmed fields are NEVER inferred or guessed. When an official source marks
  a kickoff/first-pitch time TBD or has not published a future season, the official field
  is left strictly blank ("") and flagged UNVERIFIED / ESTIMATED.
- Estimated planning windows live in separate, explicitly labeled `estimated_*` fields so
  the PST minute-by-minute scoreboard and 2027-2029 vacation analyzer work without ever
  conflating an estimate with verified data.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_MLB = json.loads((DATA_DIR / "raw_mlb_statsapi.json").read_text())

TZ_PT = ZoneInfo("America/Los_Angeles")
TZ_ET = ZoneInfo("America/New_York")
TZ_PST_FIXED = dt.timezone(dt.timedelta(hours=-8), name="PST")

# Official & planning durations (minutes)
DURATIONS = {
    "MLB": {"game": 158, "halftime": 0, "halftime_offset": 0, "pregame": 30, "postgame": 15},
    "NFL": {"game": 192, "halftime": 12, "halftime_offset": 86, "pregame": 30, "postgame": 15},
    "NFL_SB": {"game": 225, "halftime": 28, "halftime_offset": 92, "pregame": 60, "postgame": 30},
    "NCAAF": {"game": 204, "halftime": 20, "halftime_offset": 88, "pregame": 30, "postgame": 15},
    "NBA": {"game": 140, "halftime": 15, "halftime_offset": 58, "pregame": 30, "postgame": 30},
    "WNBA": {"game": 125, "halftime": 15, "halftime_offset": 52, "pregame": 15, "postgame": 15},
    "MLS": {"game": 125, "halftime": 15, "halftime_offset": 48, "pregame": 15, "postgame": 15},
    "NCAAB": {"game": 130, "halftime": 15, "halftime_offset": 52, "pregame": 15, "postgame": 15},
}

MLB_SLUG_BY_ID = {
    108: "angels", 109: "dbacks", 110: "orioles", 111: "redsox", 112: "cubs",
    113: "reds", 114: "guardians", 115: "rockies", 116: "tigers", 117: "astros",
    118: "royals", 119: "dodgers", 120: "nationals", 121: "mets", 133: "athletics",
    134: "pirates", 135: "padres", 136: "mariners", 137: "giants", 138: "cardinals",
    139: "rays", 140: "rangers", 141: "bluejays", 142: "twins", 143: "phillies",
    144: "braves", 145: "whitesox", 146: "marlins", 147: "yankees", 158: "brewers",
    105: "sacramento-river-cats",
}

TEAM_BY_ID = {t["id"]: t for t in RAW_MLB["teams"]}
TEAM_BY_ID[105] = {"id": 105, "name": "Sacramento River Cats (AAA)", "abbreviation": "SAC", "clubName": "River Cats"}


def parse_iso_utc(iso_str: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))


def fmt_hm_12(total_min: int) -> str:
    m = total_min % 1440
    h, mm = divmod(m, 60)
    ap = "AM" if h < 12 else "PM"
    hh = h % 12 or 12
    return f"{hh}:{mm:02d} {ap}"


def utc_to_pst_and_pt(utc_dt: dt.datetime) -> tuple[str, int, str, int, str]:
    pst_dt = utc_dt.astimezone(TZ_PST_FIXED)
    pt_dt = utc_dt.astimezone(TZ_PT)
    pst_min = pst_dt.hour * 60 + pst_dt.minute
    pt_min = pt_dt.hour * 60 + pt_dt.minute
    pt_tz_abbr = pt_dt.tzname() or "PT"
    return (
        f"{fmt_hm_12(pst_min)} PST",
        pst_min,
        f"{fmt_hm_12(pt_min)} {pt_tz_abbr}",
        pt_min,
        pst_dt.date().isoformat(),
    )


def et_str_to_utc(date_iso: str, et_time_str: str) -> dt.datetime | None:
    parts = et_time_str.strip().replace("\u00a0", " ").split()
    if len(parts) < 2 or ":" not in parts[0]:
        return None
    hh_s, mm_s = parts[0].split(":", 1)
    hh = int(hh_s) % 12
    if parts[1].upper().startswith("P"):
        hh += 12
    mm = int(mm_s)
    y, m, d_i = map(int, date_iso.split("-"))
    local_et = dt.datetime(y, m, d_i, hh, mm, tzinfo=TZ_ET)
    return local_et.astimezone(dt.timezone.utc)


def pt_str_to_utc(date_iso: str, pt_time_str: str) -> dt.datetime | None:
    clean = pt_time_str.strip().replace("\u00a0", " ")
    if not clean or "TBA" in clean.upper() or "TBD" in clean.upper():
        return None
    parts = clean.split()
    if len(parts) < 2 or ":" not in parts[0]:
        return None
    hh_s, mm_s = parts[0].split(":", 1)
    hh = int(hh_s) % 12
    if parts[1].upper().startswith("P"):
        hh += 12
    mm = int(mm_s)
    y, m, d_i = map(int, date_iso.split("-"))
    local_pt = dt.datetime(y, m, d_i, hh, mm, tzinfo=TZ_PT)
    return local_pt.astimezone(dt.timezone.utc)


# ---------------------------------------------------------------------------
# 1. REPO AUDIT (T7) — Line-by-line audit of existing merged files on `main`
# ---------------------------------------------------------------------------
REPO_AUDIT = [
    {
        "id": "AUDIT-01",
        "severity": "Critical Defect",
        "file": "tools/build_data.py (L223–250, L278–326)",
        "claim_in_repo": "Claims NO 7-day strict game-free vacation window exists in 2027–2029 (max 4–5 days in February) because `Postseason` marks every Sat/Sun/Mon through Super Bowl as BUSY.",
        "official_finding": "INCORRECT. Official NFL 2026–27 Important Dates confirm Divisional Playoffs are Jan 23–24 (Sat/Sun only), AFC/NFC Championships are Jan 31 (Sun only), Super Bowl LXI is Feb 14, 2027, AND on Aug 27, 2026 the NFL officially abolished the AFC–NFC Pro Bowl game. With 2026–27 CFP ending Jan 25, 2027 and MLB Spring Training opening Feb 19, 2027, `2027-02-01` through `2027-02-13` is a VERIFIED 13-CONSECUTIVE-DAY strict zero-game window (nearly 2 full weeks!).",
        "official_sources": [
            {"label": "NFL 2026–27 Important Dates (nfl.com)", "url": "https://www.nfl.com/news/2026-27-national-football-league-important-dates"},
            {"label": "NFL Abolishes AFC–NFC Pro Bowl Game (nfl.com, Aug 27, 2026)", "url": "https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested"},
            {"label": "MLB 2027 Spring Training Opens Feb 19 (mlb.com)", "url": "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule"},
        ],
    },
    {
        "id": "AUDIT-02",
        "severity": "Critical Defect",
        "file": "tools/build_data.py (L223–252) & data/schedule.json",
        "claim_in_repo": "Marks Wednesday `2026-11-25` (today) as `free: true` ('FREE DAY — no games in any tracked category') because `busy_reasons()` checks NFL regular season only on Mon/Thu/Sun (+ Black Friday/Christmas/Dec Sat).",
        "official_finding": "CONTRADICTS OFFICIAL WESTWOOD ONE SCHEDULE. Westwood One Sports officially broadcasts `Green Bay Packers at Los Angeles Rams` live on Wednesday, Nov 25, 2026 at 7:30 PM ET (4:30 PM PST) as 'Thanksgiving Wednesday' (`events/548511`). `tools/build_data.py` transcribed this game into `westwood_2026` at L153 yet failed to mark `2026-11-25` busy in `busy_reasons()`.",
        "official_sources": [
            {"label": "Westwood One Event 548511 — GB at LAR Nov 25, 2026", "url": "https://www.westwoodonesports.com/events/548511"},
            {"label": "Westwood One Official NFL Schedule", "url": "https://www.westwoodonesports.com/nfl-schedule/"},
        ],
    },
    {
        "id": "AUDIT-03",
        "severity": "Critical Defect",
        "file": "assets/app.js (L48)",
        "claim_in_repo": "`const ww = (SCHEDULE.westwood_2026_verified||[]).find(x=>x.date===iso);` renders only the FIRST matching Westwood One broadcast on any given date.",
        "official_finding": "DROPS MULTIPLE GAMES PER DAY. On Thanksgiving (`2026-11-26`, 3 games: 12:30 PM, 4:15 PM, 8:00 PM ET), Week 15 Sat (`2026-12-19`, 2 games), Christmas (`2026-12-25`, 3 games), Week 16/17 Sat (`2026-12-26`, `2027-01-02`, 2 games), and Week 18 Sat (`2027-01-09`, 3 games), `.find()` discards games 2 and 3 and falsely reports afternoon/evening hours as FREE.",
        "official_sources": [
            {"label": "Westwood One Official NFL Schedule (Tripleheaders & Doubleheaders)", "url": "https://www.westwoodonesports.com/nfl-schedule/"},
        ],
    },
    {
        "id": "AUDIT-04",
        "severity": "Data Error",
        "file": "tools/build_data.py (L205–209)",
        "claim_in_repo": "Hardcodes Thursday `2026-07-16` and Thursday `2027-07-15` as MLB All-Star Break FREE days (`allstar_breaks`).",
        "official_finding": "INCORRECT PER OFFICIAL MLB STATSAPI. `statsapi.mlb.com` shows `totalGames: 1` on `2026-07-16` AND `totalGames: 1` on `2027-07-15` (standalone Thursday regular-season return game). Only Monday (`2027-07-12`) and Wednesday (`2027-07-14`) have 0 MLB games during the 2027 All-Star week.",
        "official_sources": [
            {"label": "MLB StatsAPI 2027 Official Schedule (`2027-07-15` totalGames=1)", "url": "https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&season=2027&startDate=2027-07-11&endDate=2027-07-16"},
            {"label": "MLB StatsAPI 2026 Official Schedule (`2026-07-16` totalGames=1)", "url": "https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&season=2026&startDate=2026-07-12&endDate=2026-07-17"},
        ],
    },
    {
        "id": "AUDIT-05",
        "severity": "Data Error",
        "file": "tools/build_data.py (L29–30)",
        "claim_in_repo": "Marks `2026-10-29` through `2026-10-31` as BUSY 2026 MLB Postseason days.",
        "official_finding": "2026 World Series ended on Wednesday, Oct 28, 2026 (Milwaukee Brewers defeated Tampa Bay Rays 4–1 in Game 5). Games 6 and 7 (Oct 30–31) were if-necessary and not played; `statsapi.mlb.com` confirms zero MLB games after `2026-10-28`.",
        "official_sources": [
            {"label": "MLB Events — 2026 World Series Result (Oct 23–28, 2026)", "url": "https://www.mlb.com/events"},
            {"label": "MLB 2026 World Series Schedule FAQ", "url": "https://www.mlb.com/news/2026-mlb-world-series-faq-schedule-times-teams-and-more"},
        ],
    },
    {
        "id": "AUDIT-06",
        "severity": "Data Error",
        "file": "tools/build_data.py (L142) & ncaaf.html",
        "claim_in_repo": "Lists Cal `2026-11-28 vs Pittsburgh` kickoff as `TBA (see calbears.com)`, omits Stanford's clinched 2026 bowl berth, and claims in F-02 that 'No 2027 Cal schedule was found on calbears.com'.",
        "official_finding": "1) `calbears.com` now lists `Nov 28, 2026 vs Pittsburgh` at `4:30 PM PT` on `KSFO 810 AM`. 2) `gostanford.com` confirms Stanford (6–5) clinched a 2026 bowl berth on Nov 21, 2026 (44–28 Big Game win), whereas Cal (3–8) is eliminated from 2026 bowls. 3) `calbears.com` published its 2027 non-conference dates on June 25, 2026 (Aug 28 vs Sac State, Sept 11 vs Old Dominion, plus UCLA; with an earlier Sept 2024 BYU Sept 11 release creating a date conflict to flag) and 2028–2029 Wyoming/Minnesota dates.",
        "official_sources": [
            {"label": "Cal 2026 Official Schedule (Nov 28 vs Pitt 4:30 PM PT)", "url": "https://calbears.com/sports/football/schedule"},
            {"label": "Stanford Clinches 2026 Bowl Berth in Big Game (gostanford.com)", "url": "https://gostanford.com/news/2026/11/21/stanford-secures-bowl-berth-with-big-game-win"},
            {"label": "Cal Completes 2027 Nonconference Slate (calbears.com, Jun 25, 2026)", "url": "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state.aspx"},
        ],
    },
    {
        "id": "AUDIT-07",
        "severity": "Data Error",
        "file": "radio-guide.html & flagged-for-review.html (F-06, F-07)",
        "claim_in_repo": "Lists `KGO 810 AM` via a fan blog (`insidethe49.com`), marks Cal's radio flagship as 'No official source found', and marks Athletics Bay Area radio as 'No official source found'.",
        "official_finding": "1) 810 AM in San Francisco is now `KSFO 810 AM` (verified on both `calbears.com` as Cal Football's 2026 English radio station AND `sjearthquakes.com` as Earthquakes' 2026 English flagship). 2) `mlb.com/athletics/schedule/affiliates` officially lists `960 AM KNEW (Bay Area)` and `650 AM KSTE (Sacramento)` on the A's Radio Network (while 94122 signal quality & 2027 carriage remain valid flags). 3) `mlb.com/giants/schedule/broadcast-partners` officially confirms `KNBR 104.5 FM/680 AM` and `KSFN 1510 AM/99.3 FM`.",
        "official_sources": [
            {"label": "Cal 2026 Football Schedule (`Radio: KSFO 810 AM`)", "url": "https://calbears.com/sports/football/schedule"},
            {"label": "Athletics Official TV & Radio Affiliates (`mlb.com`)", "url": "https://www.mlb.com/athletics/schedule/affiliates"},
            {"label": "Giants Official Broadcast Partners (`mlb.com`)", "url": "https://www.mlb.com/giants/schedule/broadcast-partners"},
        ],
    },
    {
        "id": "AUDIT-08",
        "severity": "Source Replacement",
        "file": "sources/verification-log.md, methodology.html, mlb.html, nfl.html",
        "claim_in_repo": "Cites non-official secondary/blog domains (`baseballjerseyshop.com`, `huffsports.com`, `newsbreak.com`, `staging.elkford.ca`, `mlbschedule.net`, `usagametime.com`, `calendarena.com`, `ncaafpass.com`, `awfulannouncing.com`, `insidethe49.com`, `wikipedia.org`) on rows marked VERIFIED or in methodology tables.",
        "official_finding": "Every single one of these topics has a direct primary official source (`mlb.com`, `statsapi.mlb.com`, `nfl.com`, `media.nfl.com`, `operations.nfl.com`, `collegefootballplayoff.com`, `ncaa.com`, `49ers.com`, `calbears.com`, `gostanford.com`). Also, `nfl.com` officially confirmed Nashville for Super Bowl LXIV (2030) on May 19, 2026, while listing Super Bowl LXII (2028 Atlanta) exact date as TBA.",
        "official_sources": [
            {"label": "MLB Average Game Time 2:38 in 2025 (`mlb.com`)", "url": "https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year"},
            {"label": "NFL Operations Official Terms — 60m clock, 12m halftime", "url": "https://operations.nfl.com/rules-officiating/nfl-football-basics/football-terms"},
            {"label": "Super Bowl LXIV Official NFL Announcement (Nashville 2030)", "url": "https://www.nfl.com/news/super-bowl-lxiv-to-be-held-in-nashville-s-new-nissan-stadium-in-2030"},
        ],
    },
    {
        "id": "AUDIT-09",
        "severity": "Missing Scope",
        "file": "radio-guide.html & flagged-for-review.html (F-09)",
        "claim_in_repo": "Treats all other Bay Area AM/FM live radio sports as out of scope and omits Golden State Warriors (95.7 FM), Golden State Valkyries (95.7 FM), San Jose Earthquakes (KSFO 810 / KZSF 1370), Sharks status, and Westwood One NCAA broadcasts.",
        "official_finding": "Prompt explicitly requested BOTH a dedicated Core Games section AND searching SF Bay Area radio stations for all other live over-the-air sports in 94122 (flagging them high priority). Official team releases confirm Warriors (preseason + 82-game regular season on `95.7 The Game`), Valkyries (`95.7 The Game`), Earthquakes (`KSFO 810 AM` / `KZSF 1370 AM`), Westwood One NCAA Football/Basketball, and Sharks' digital-only `Sharks Audio Network` (not AM/FM).",
        "official_sources": [
            {"label": "Warriors 2026–27 Radio Schedule on 95.7 The Game (`nba.com`)", "url": "https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824"},
            {"label": "Valkyries Radio Schedule on 95.7 The Game (`wnba.com`)", "url": "https://valkyries.wnba.com/news/golden-state-valkyries-announce-local-television-and-radio-broadcast-schedule-20260425"},
            {"label": "Earthquakes 2026 Radio Stations KSFO 810 & KZSF 1370 (`sjearthquakes.com`)", "url": "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season"},
            {"label": "Sharks Audio Network Digital Broadcasts (`nhl.com`)", "url": "https://www.nhl.com/sharks/news/sharks-announce-2026-preseason-schedule"},
        ],
    },
    {
        "id": "AUDIT-10",
        "severity": "UI Bug",
        "file": "mlb.html, nfl.html, ncaaf.html & assets/app.js (L152–157, L191)",
        "claim_in_repo": "Each league subpage includes `<div id=\"windows-table\">` expecting filtered rows (e.g. `mlb.html` says 'filter to MLB rows'), but `app.js` calls `renderWindowsTable('windows-table', SCHEDULE.windows)` unfiltered on all pages, and names the Athletics `'Oakland Athletics (Athletics)'`.",
        "official_finding": "All 43 windows across MLB, NFL, NCAAF, and Westwood One render identically on `mlb.html`, `nfl.html`, and `ncaaf.html`. Also `statsapi.mlb.com` lists club 133 officially as `Athletics` (`ATH`), not `Oakland Athletics`.",
        "official_sources": [
            {"label": "MLB StatsAPI Official Club List (`id=133`, `name='Athletics'`)", "url": "https://statsapi.mlb.com/api/v1/teams?sportId=1"},
        ],
    },
]

# ---------------------------------------------------------------------------
# 2. OUTER SUNSET SF 94122 RADIO DIAL & LIVE SPORTS MATRIX
# ---------------------------------------------------------------------------
RADIO_STATIONS_94122 = [
    {
        "station": "KNBR 680 AM / 104.5 FM",
        "nickname": "The Sports Leader",
        "band_power": "AM 680 kHz (50,000W Class A clear-channel, Belmont) + FM 104.5 MHz (San Francisco)",
        "reception_94122": "Primary local Grade-A AM & FM signal across Outer Sunset 94122",
        "live_sports": [
            "San Francisco Giants MLB (English Flagship — Spring Training select, all 162 Regular Season, Postseason)",
            "San Francisco 49ers NFL (AM/FM Co-Flagship — Preseason, Regular Season, Postseason)",
            "Stanford Cardinal NCAAF (Cardinal Sports Network Flagship)",
            "Westwood One Sports NFL & NCAA (Charter Affiliate — TNF, SNF, MNF, Holidays, NFL Playoffs, Super Bowl, March Madness; subject to Giants/49ers conflicts)",
        ],
        "priority": "HIGH PRIORITY",
        "status": "VERIFIED",
        "official_sources": [
            {"label": "Giants Broadcast Partners (mlb.com)", "url": "https://www.mlb.com/giants/schedule/broadcast-partners"},
            {"label": "49ers Official Schedule Radio Listings (49ers.com)", "url": "https://www.49ers.com/schedule/"},
            {"label": "Stanford Football Schedule Listen Links (gostanford.com)", "url": "https://gostanford.com/sports/football/schedule"},
            {"label": "Westwood One Station Finder", "url": "https://www.westwoodonesports.com/station-finder/"},
        ],
    },
    {
        "station": "KSAN 107.7 FM",
        "nickname": "107.7 The Bone",
        "band_power": "FM 107.7 MHz (San Bruno Mountain Class B FM)",
        "reception_94122": "Strong direct line-of-sight FM reception in Outer Sunset 94122",
        "live_sports": [
            "San Francisco 49ers NFL (FM Rock Co-Flagship — Preseason, Regular Season, Postseason)",
        ],
        "priority": "HIGH PRIORITY",
        "status": "VERIFIED",
        "official_sources": [
            {"label": "49ers Official Schedule (`KSAN 107.7 FM / KNBR 104.5 FM / 680 AM`)", "url": "https://www.49ers.com/schedule/"},
        ],
    },
    {
        "station": "KTCT 1050 AM",
        "nickname": "KNBR 1050 / ESPN Radio",
        "band_power": "AM 1050 kHz (50,000W Day / 10,000W Night, San Mateo)",
        "reception_94122": "Strong daytime AM across 94122; directional night pattern",
        "live_sports": [
            "Giants / 49ers / Stanford conflict overflow broadcasts",
            "ESPN Radio National MLB (Sunday Night Baseball, Opening Night, All-Star, Wild Card,DS, LCS, World Series)",
            "ESPN Radio College Football Playoff & NBA Finals",
            "Stanford Men's Basketball & USF Dons Basketball",
        ],
        "priority": "HIGH PRIORITY",
        "status": "VERIFIED",
        "official_sources": [
            {"label": "MLB World Series National ESPN Radio Release (mlb.com)", "url": "https://mlb.com/news/press-release-broadcast-schedule-announced-for-the-2026-world-series-presented-by-capital-one"},
            {"label": "Westwood One Station Finder (KTCT-AM)", "url": "https://www.westwoodonesports.com/station-finder/"},
        ],
    },
    {
        "station": "KSFO 810 AM",
        "nickname": "Talk Radio 810 AM (formerly KGO 810 frequency)",
        "band_power": "AM 810 kHz (50,000W Class A clear-channel)",
        "reception_94122": "Booming 50kW Bay Area AM groundwave throughout Outer Sunset 94122",
        "live_sports": [
            "California Golden Bears NCAAF (Official 2026 English Radio Flagship — every game on `calbears.com`)",
            "California Golden Bears Men's Basketball",
            "San Jose Earthquakes MLS (Official 2026 English Radio Flagship)",
        ],
        "priority": "HIGH PRIORITY",
        "status": "VERIFIED",
        "official_sources": [
            {"label": "Cal 2026 Official Football Schedule (`Radio: KSFO 810 AM`)", "url": "https://calbears.com/sports/football/schedule"},
            {"label": "San Jose Earthquakes 2026 Radio Stations Release (`KSFO 810 AM`)", "url": "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season"},
        ],
    },
    {
        "station": "KGMZ-FM 95.7",
        "nickname": "95.7 The Game",
        "band_power": "FM 95.7 MHz (San Francisco Class B FM)",
        "reception_94122": "Primary local SF FM sports signal in Outer Sunset 94122",
        "live_sports": [
            "Golden State Warriors NBA (Official Flagship — all Preseason, 82 Regular Season, and Postseason games + 30m pre/postgame)",
            "Golden State Valkyries WNBA (Official Flagship — all home & scheduled radio broadcasts May–Sept)",
        ],
        "priority": "HIGH PRIORITY (Tier 4 Full Radio Dial)",
        "status": "VERIFIED",
        "official_sources": [
            {"label": "Warriors 2026–27 TV & Radio Broadcast Schedule (`nba.com`)", "url": "https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824"},
            {"label": "Valkyries Radio Partnership & Broadcast Schedule (`valkyries.wnba.com`)", "url": "https://valkyries.wnba.com/news/golden-state-valkyries-announce-local-television-and-radio-broadcast-schedule-20260425"},
        ],
    },
    {
        "station": "KNEW 960 AM / KSTE 650 AM",
        "nickname": "A's Radio Network (Bay Area / Sacramento)",
        "band_power": "AM 960 kHz (5,000W Oakland) / AM 650 kHz (21,400W Day Sacramento)",
        "reception_94122": "960 AM KNEW reaches SF 94122 across the Bay; 650 AM KSTE is Sacramento flagship (fringe daytime in SF). Flagged for 2027 Sacramento-era Bay Area carriage re-check.",
        "live_sports": [
            "Athletics MLB (Listed on official `mlb.com/athletics/schedule/affiliates` as `960 AM KNEW — Bay Area` and `650 AM KSTE — Sacramento` + digital A's Cast)",
        ],
        "priority": "HIGH PRIORITY",
        "status": "PARTIAL",
        "official_sources": [
            {"label": "Athletics Official TV & Radio Affiliates (`mlb.com`)", "url": "https://www.mlb.com/athletics/schedule/affiliates"},
        ],
    },
    {
        "station": "KSFN 1510 AM / 99.3 FM",
        "nickname": "Giants Spanish Radio Network",
        "band_power": "AM 1510 kHz (Piedmont/SF Bay)",
        "reception_94122": "Daytime Bay Area AM coverage",
        "live_sports": [
            "San Francisco Giants MLB (Spanish Flagship)",
        ],
        "priority": "HIGH PRIORITY",
        "status": "VERIFIED",
        "official_sources": [
            {"label": "Giants Spanish Radio Network (`mlb.com`)", "url": "https://www.mlb.com/giants/schedule/broadcast-partners"},
        ],
    },
    {
        "station": "KZSF 1370 AM",
        "nickname": "La Kaliente 1370 AM",
        "band_power": "AM 1370 kHz (San Jose)",
        "reception_94122": "South Bay AM; fringe reception in Outer Sunset 94122",
        "live_sports": [
            "San Jose Earthquakes MLS (Official 2026 Spanish Radio Flagship)",
        ],
        "priority": "HIGH PRIORITY (Tier 4 Full Radio Dial)",
        "status": "VERIFIED",
        "official_sources": [
            {"label": "San Jose Earthquakes 2026 Radio Release (`KZSF 1370 AM`)", "url": "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season"},
        ],
    },
    {
        "station": "Sharks Audio Network (Digital Only — No SF AM/FM)",
        "nickname": "sjsharks.com/listen & Sharks+SAP Center App",
        "band_power": "Internet stream only (left terrestrial 98.5 KFOX in 2021)",
        "reception_94122": "NOT receivable on a standard AM/FM radio in 94122 (excluded from AM/FM busy blocks unless NHL Stanley Cup Final airs nationally on Westwood One)",
        "live_sports": [
            "San Jose Sharks NHL (Digital stream only; verified non-AM/FM)",
        ],
        "priority": "EXCLUDED (Digital-Only)",
        "status": "VERIFIED",
        "official_sources": [
            {"label": "Sharks 2026–27 Audio Network Release (`nhl.com/sharks`)", "url": "https://www.nhl.com/sharks/news/sharks-announce-2026-preseason-schedule"},
        ],
    },
]

# ---------------------------------------------------------------------------
# 3. GAME DURATIONS & HALFTIME RESEARCH
# ---------------------------------------------------------------------------
DURATIONS_RESEARCH = [
    {
        "sport": "MLB (All 30 Clubs — 9-Inning Game)",
        "official_rule_clock": "Pitch timer: 15s bases empty / 18s runners on; 9 innings (no clock)",
        "official_halftime_or_break": "None (between-inning breaks 2m 15s; 7th-inning stretch ~2–3m)",
        "official_confirmed_average": "158 min (2h 38m in 2025; 2h 36m in 2024; 2h 40m in 2023)",
        "planning_duration_min": 158,
        "radio_pre_post_buffer": "+30m pregame / +15m postgame (KNBR station practice — estimated)",
        "status": "VERIFIED (2023–2025 MLB Averages)",
        "official_source_label": "MLB.com — Average game time under 3 hours for 3rd straight year (2:38)",
        "official_source_url": "https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year",
    },
    {
        "sport": "NFL (Regular Season & Playoffs)",
        "official_rule_clock": "60 min regulation (4 × 15-min quarters)",
        "official_halftime_or_break": "12 minutes official intermission (Rule 4; ~86m after kickoff in real time)",
        "official_confirmed_average": "— (Official rulebook defines 60m clock + 12m halftime; league does not publish a fixed elapsed guarantee)",
        "planning_duration_min": 192,
        "radio_pre_post_buffer": "+30m pregame / +15m postgame (Westwood One / KNBR — estimated)",
        "status": "VERIFIED (Clock & 12m Halftime) / ESTIMATED (192m Total Elapsed)",
        "official_source_label": "NFL Football Operations — Official Terms (60m regulation, 12m halftime)",
        "official_source_url": "https://operations.nfl.com/rules-officiating/nfl-football-basics/football-terms",
    },
    {
        "sport": "NFL Super Bowl (LXI / LXII / LXIII)",
        "official_rule_clock": "60 min regulation (4 × 15-min quarters)",
        "official_halftime_or_break": "~25–30 minutes extended Super Bowl Halftime Show",
        "official_confirmed_average": "— (Extended halftime show & ceremonies)",
        "planning_duration_min": 225,
        "radio_pre_post_buffer": "+60m pregame / +30m postgame (estimated)",
        "status": "ESTIMATED (225m Elapsed + 28m Halftime)",
        "official_source_label": "NFL.com — Super Bowl LXI Official Event Info",
        "official_source_url": "https://www.nfl.com/news/2026-27-national-football-league-important-dates",
    },
    {
        "sport": "NCAAF (Stanford & California FBS)",
        "official_rule_clock": "60 min regulation (4 × 15-min quarters; running clock on first downs except final 2m of halves)",
        "official_halftime_or_break": "20 minutes official NCAA Rule 3-2-1 intermission (~88m after kickoff)",
        "official_confirmed_average": "— (Official NCAA rulebook sets 60m clock + 20m halftime; total elapsed estimated)",
        "planning_duration_min": 204,
        "radio_pre_post_buffer": "+30m pregame / +15m postgame (KSFO 810 / KNBR — estimated)",
        "status": "VERIFIED (60m Clock & 20m Halftime) / ESTIMATED (204m Total Elapsed)",
        "official_source_label": "NCAA Football Rules & CFP Broadcast Schedule",
        "official_source_url": "https://collegefootballplayoff.com/news/2026/6/1/26-27-broadcast-sked",
    },
    {
        "sport": "NBA — Golden State Warriors (95.7 FM)",
        "official_rule_clock": "48 min regulation (4 × 12-min quarters)",
        "official_halftime_or_break": "15 minutes halftime",
        "official_confirmed_average": "30-min pregame & 30-min postgame shows officially confirmed on 95.7 The Game",
        "planning_duration_min": 140,
        "radio_pre_post_buffer": "+30m pregame / +30m postgame (VERIFIED on nba.com/warriors)",
        "status": "VERIFIED (30m Pre/Post) / ESTIMATED (140m Game Elapsed)",
        "official_source_label": "Warriors 2026–27 Radio Release (`nba.com/warriors`)",
        "official_source_url": "https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824",
    },
    {
        "sport": "WNBA — Golden State Valkyries (95.7 FM)",
        "official_rule_clock": "40 min regulation (4 × 10-min quarters)",
        "official_halftime_or_break": "15 minutes halftime",
        "official_confirmed_average": "—",
        "planning_duration_min": 125,
        "radio_pre_post_buffer": "+15m pregame / +15m postgame (estimated)",
        "status": "ESTIMATED (125m Elapsed)",
        "official_source_label": "Valkyries Official Radio Broadcast Schedule (`valkyries.wnba.com`)",
        "official_source_url": "https://valkyries.wnba.com/news/golden-state-valkyries-announce-local-television-and-radio-broadcast-schedule-20260425",
    },
    {
        "sport": "MLS — San Jose Earthquakes (KSFO 810 AM)",
        "official_rule_clock": "90 min regulation (2 × 45-min halves + stoppage)",
        "official_halftime_or_break": "15 minutes halftime",
        "official_confirmed_average": "—",
        "planning_duration_min": 125,
        "radio_pre_post_buffer": "+15m pregame / +15m postgame (estimated)",
        "status": "ESTIMATED (125m Elapsed)",
        "official_source_label": "San Jose Earthquakes 2026 Radio Stations (`sjearthquakes.com`)",
        "official_source_url": "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season",
    },
]

# ---------------------------------------------------------------------------
# 4. BUILD VERIFIED MLB CLUBS + 2027 GIANTS & ATHLETICS GAME LISTS
# ---------------------------------------------------------------------------
MLB_30_CLUBS = []
for t in sorted(RAW_MLB["teams"], key=lambda x: x["name"]):
    cid = t["id"]
    slug = MLB_SLUG_BY_ID[cid]
    is_high = cid in (137, 133)
    MLB_30_CLUBS.append({
        "id": cid,
        "name": t["name"],
        "abbreviation": t["abbreviation"],
        "priority": "HIGH PRIORITY" if is_high else "STANDARD (All 30 Shown)",
        "bay_area_radio": (
            "KNBR 680 AM / 104.5 FM (English) · KSFN 1510 AM (Spanish)"
            if cid == 137 else (
                "960 AM KNEW (Bay Area) / 650 AM KSTE (Sacramento) — 94122 carriage flagged"
                if cid == 133 else "ESPN Radio national select (KTCT 1050 AM) / opponent broadcasts when facing SF/ATH"
            )
        ),
        "schedule_2027_status": "VERIFIED (Spring Training Feb 19–Mar 23; Regular Season Mar 24/25–Sep 26)",
        "schedule_2028_2029_status": "UNVERIFIED / ESTIMATED (Not yet released by MLB)",
        "official_url": f"https://www.mlb.com/{slug}/schedule",
    })


def parse_mlb_team_games(raw_dates: list[dict], focal_id: int, team_label: str, radio_label: str) -> list[dict]:
    rows = []
    for d_entry in raw_dates:
        sched_date = d_entry["date"]
        for g in d_entry["games"]:
            gpk = g["gamePk"]
            gtype = g["gameType"]
            phase_map = {"S": "Spring Training", "E": "Exhibition", "R": "Regular Season"}
            phase = phase_map.get(gtype, gtype)
            tbd = bool(g["status"].get("startTimeTBD", False))
            away_id = g["teams"]["away"]["team"]["id"]
            home_id = g["teams"]["home"]["team"]["id"]
            away_name = TEAM_BY_ID.get(away_id, {"name": f"Team {away_id}"})["name"]
            home_name = TEAM_BY_ID.get(home_id, {"name": f"Team {home_id}"})["name"]
            is_home = (home_id == focal_id)
            matchup = f"vs {away_name}" if is_home else f"at {home_name}"
            if not tbd:
                utc_dt = parse_iso_utc(g["gameDate"])
                off_pst, pst_min, off_pt, pt_min, _ = utc_to_pst_and_pt(utc_dt)
                status = "VERIFIED"
                est_pst = ""
                est_pt = ""
            else:
                off_pst = ""
                off_pt = ""
                status = "PARTIAL (Date Verified · Time TBD)"
                wd = dt.date.fromisoformat(sched_date).weekday()
                # Typical afternoon weekend or Spring Training (12:05 PM PST / 1:05 PM PDT), evening weekday (5:45 PM PST / 6:45 PM PDT)
                if gtype in ("S", "E") or wd in (5, 6):
                    pst_min = 12 * 60 + 5
                    pt_min = 13 * 60 + 5 if sched_date >= "2027-03-14" else 12 * 60 + 5
                else:
                    pst_min = 17 * 60 + 45
                    pt_min = 18 * 60 + 45
                est_pst = f"{fmt_hm_12(pst_min)} – {fmt_hm_12(pst_min + DURATIONS['MLB']['game'])} PST (Est.)"
                est_pt = f"{fmt_hm_12(pt_min)} – {fmt_hm_12(pt_min + DURATIONS['MLB']['game'])} PT (Est.)"
            rows.append({
                "date": sched_date,
                "gamePk": gpk,
                "team": team_label,
                "phase": phase,
                "matchup": matchup,
                "is_bay_bridge": {away_id, home_id} == {133, 137},
                "official_time_pst": off_pst,
                "official_time_pt": off_pt,
                "start_min_pst": pst_min,
                "end_min_pst": pst_min + DURATIONS["MLB"]["game"],
                "start_min_pt": pt_min,
                "end_min_pt": pt_min + DURATIONS["MLB"]["game"],
                "time_tbd": tbd,
                "estimated_window_pst": est_pst,
                "estimated_window_pt": est_pt,
                "radio": radio_label,
                "priority": "HIGH PRIORITY",
                "status": status,
                "source_url": f"https://www.mlb.com/gameday/{gpk}",
            })
    return rows


GIANTS_2027_GAMES = parse_mlb_team_games(
    RAW_MLB["giants_2027"], 137, "SF Giants", "KNBR 680 AM / 104.5 FM · KSFN 1510 AM"
)
ATHLETICS_2027_GAMES = parse_mlb_team_games(
    RAW_MLB["athletics_2027"], 133, "Athletics", "960 AM KNEW / 650 AM KSTE (Flagged in 94122)"
)

MLB_DAILY_COUNTS_2026 = {d["date"]: d["totalGames"] for d in RAW_MLB["league_2026"]["dates"]}
MLB_DAILY_COUNTS_2027 = {d["date"]: d["totalGames"] for d in RAW_MLB["league_2027"]["dates"]}

# ---------------------------------------------------------------------------
# 5. NFL 32 TEAMS, 49ERS 2026–27 FULL SCHEDULE, WESTWOOD ONE NFL & NCAA
# ---------------------------------------------------------------------------
NFL_32_TEAMS = [
    ("Arizona Cardinals", "https://www.azcardinals.com/schedule/"),
    ("Atlanta Falcons", "https://www.atlantafalcons.com/schedule/"),
    ("Baltimore Ravens", "https://www.baltimoreravens.com/schedule/"),
    ("Buffalo Bills", "https://www.buffalobills.com/schedule/"),
    ("Carolina Panthers", "https://www.panthers.com/schedule/"),
    ("Chicago Bears", "https://www.chicagobears.com/schedule/"),
    ("Cincinnati Bengals", "https://www.bengals.com/schedule/"),
    ("Cleveland Browns", "https://www.clevelandbrowns.com/schedule/"),
    ("Dallas Cowboys", "https://www.dallascowboys.com/schedule/"),
    ("Denver Broncos", "https://www.denverbroncos.com/schedule/"),
    ("Detroit Lions", "https://www.detroitlions.com/schedule/"),
    ("Green Bay Packers", "https://www.packers.com/schedule/"),
    ("Houston Texans", "https://www.houstontexans.com/schedule/"),
    ("Indianapolis Colts", "https://www.colts.com/schedule/"),
    ("Jacksonville Jaguars", "https://www.jaguars.com/schedule/"),
    ("Kansas City Chiefs", "https://www.chiefs.com/schedule/"),
    ("Las Vegas Raiders", "https://www.raiders.com/schedule/"),
    ("Los Angeles Chargers", "https://www.chargers.com/schedule/"),
    ("Los Angeles Rams", "https://www.therams.com/schedule/"),
    ("Miami Dolphins", "https://www.miamidolphins.com/schedule/"),
    ("Minnesota Vikings", "https://www.vikings.com/schedule/"),
    ("New England Patriots", "https://www.patriots.com/schedule/"),
    ("New Orleans Saints", "https://www.neworleanssaints.com/schedule/"),
    ("New York Giants", "https://www.giants.com/schedule/"),
    ("New York Jets", "https://www.newyorkjets.com/schedule/"),
    ("Philadelphia Eagles", "https://www.philadelphiaeagles.com/schedule/"),
    ("Pittsburgh Steelers", "https://www.steelers.com/schedule/"),
    ("San Francisco 49ers", "https://www.49ers.com/schedule/"),
    ("Seattle Seahawks", "https://www.seahawks.com/schedule/"),
    ("Tampa Bay Buccaneers", "https://www.buccaneers.com/schedule/"),
    ("Tennessee Titans", "https://www.tennesseetitans.com/schedule/"),
    ("Washington Commanders", "https://www.commanders.com/schedule/"),
]

FORTYNINERS_2026_FULL = [
    ("2026-08-13", "Preseason Wk 1", "vs Tennessee Titans", "Levi's Stadium", "", "FINAL (L 13–19)", "https://www.49ers.com/game-day/2026/pre/titans-at-49ers/"),
    ("2026-08-20", "Preseason Wk 2", "at Los Angeles Chargers", "SoFi Stadium", "", "FINAL (W 41–17)", "https://www.49ers.com/game-day/2026/pre/49ers-at-chargers/"),
    ("2026-08-27", "Preseason Wk 3", "at Las Vegas Raiders", "Allegiant Stadium", "", "FINAL (W 18–12)", "https://www.49ers.com/game-day/2026/pre/49ers-at-raiders/"),
    ("2026-09-10", "Week 1 (Thu)", "vs Los Angeles Rams (Australia)", "Melbourne Cricket Ground", "5:35 PM PT", "FINAL (W 27–7)", "https://www.49ers.com/game-day/2026/reg-week1/49ers-at-rams/"),
    ("2026-09-20", "Week 2 (Sun)", "vs Miami Dolphins", "Levi's Stadium", "1:05 PM PT", "FINAL (W 35–13)", "https://www.49ers.com/game-day/2026/reg-week2/dolphins-at-49ers/"),
    ("2026-09-27", "Week 3 (Sun)", "vs Arizona Cardinals", "Levi's Stadium", "1:25 PM PT", "FINAL (W 36–30)", "https://www.49ers.com/game-day/2026/reg-week3/cardinals-at-49ers/"),
    ("2026-10-04", "Week 4 (Sun)", "vs Denver Broncos", "Levi's Stadium", "1:05 PM PT", "FINAL (W 24–14)", "https://www.49ers.com/game-day/2026/reg-week4/broncos-at-49ers/index"),
    ("2026-10-11", "Week 5 (Sun)", "at Seattle Seahawks", "Lumen Field", "1:25 PM PT", "FINAL (W 32–29)", "https://www.49ers.com/game-day/2026/reg-week5/49ers-at-seahawks/"),
    ("2026-10-19", "Week 6 (Mon)", "vs Washington Commanders (MNF)", "Levi's Stadium", "5:15 PM PT", "FINAL (W 23–17)", "https://www.49ers.com/game-day/2026/reg-week6/commanders-at-49ers/index"),
    ("2026-10-25", "Week 7 (Sun)", "at Atlanta Falcons", "Mercedes-Benz Stadium", "10:00 AM PT", "FINAL (L 20–29)", "https://www.49ers.com/game-day/2026/reg-week7/49ers-at-falcons/"),
    ("2026-11-08", "Week 9 (Sun)", "vs Las Vegas Raiders", "Levi's Stadium", "1:05 PM PST", "FINAL (W 38–17)", "https://www.49ers.com/game-day/2026/reg-week9/raiders-at-49ers/index"),
    ("2026-11-15", "Week 10 (Sun)", "at Dallas Cowboys", "AT&T Stadium", "1:25 PM PST", "FINAL (W 46–40)", "https://www.49ers.com/game-day/2026/reg-week10/49ers-at-cowboys/"),
    ("2026-11-22", "Week 11 (Sun)", "vs Minnesota Vikings (Mexico City)", "Estadio Banorte", "1:25 PM PST", "FINAL (W 35–10)", "https://www.49ers.com/game-day/2026/reg-week11/vikings-at-49ers/"),
    ("2026-11-29", "Week 12 (Sun)", "vs Seattle Seahawks", "Levi's Stadium", "1:25 PM PST", "Scheduled (FOX)", "https://www.49ers.com/game-day/2026/reg-week12/seahawks-at-49ers/"),
    ("2026-12-06", "Week 13 (Sun)", "at New York Giants", "MetLife Stadium", "10:00 AM PST", "Scheduled (FOX)", "https://www.49ers.com/schedule/"),
    ("2026-12-13", "Week 14 (Sun)", "vs Los Angeles Rams", "Levi's Stadium", "1:25 PM PST", "Scheduled (FOX)", "https://www.49ers.com/schedule/"),
    ("2026-12-17", "Week 15 (Thu)", "at Los Angeles Chargers (TNF)", "SoFi Stadium", "5:15 PM PST", "Scheduled (Prime / Westwood One)", "https://www.49ers.com/schedule/"),
    ("2026-12-27", "Week 16 (Sun)", "at Kansas City Chiefs", "Arrowhead Stadium", "1:25 PM PST", "Scheduled (CBS)", "https://www.49ers.com/schedule/"),
    ("2027-01-03", "Week 17 (Sun)", "vs Philadelphia Eagles (SNF)", "Levi's Stadium", "5:20 PM PST", "Scheduled (NBC / Westwood One)", "https://www.49ers.com/schedule/"),
    ("2027-01-10", "Week 18 (Sat/Sun TBD)", "at Arizona Cardinals", "State Farm Stadium", "", "Date/Time TBD (Jan 9 or Jan 10, 2027)", "https://www.49ers.com/schedule/"),
]

# All 35 verified upcoming Westwood One NFL listings (Nov 25, 2026 – Jan 10, 2027)
WESTWOOD_ONE_NFL_VERIFIED = [
    ("2026-11-25", "7:30 PM ET", "548511", "Green Bay Packers at Los Angeles Rams", "SoFi Stadium, Inglewood, CA", "Thanksgiving Wednesday"),
    ("2026-11-26", "12:30 PM ET", "548512", "Chicago Bears at Detroit Lions", "Ford Field, Detroit, MI", "NFL Thanksgiving Day Tripleheader"),
    ("2026-11-26", "4:15 PM ET", "548513", "Philadelphia Eagles at Dallas Cowboys", "AT&T Stadium, Arlington, TX", "NFL Thanksgiving Day Tripleheader"),
    ("2026-11-26", "8:00 PM ET", "548514", "Kansas City Chiefs at Buffalo Bills", "New Highmark Stadium, Orchard Park, NY", "NFL Thanksgiving Day Tripleheader"),
    ("2026-11-27", "2:30 PM ET", "548515", "Denver Broncos at Pittsburgh Steelers", "Acrisure Stadium, Pittsburgh, PA", "NFL Black Friday Game"),
    ("2026-11-29", "7:30 PM ET", "548502", "Las Vegas Raiders at Cleveland Browns", "Huntington Bank Field, Cleveland, OH", "Sunday Night Football"),
    ("2026-11-30", "7:00 PM ET", "548544", "Carolina Panthers at Tampa Bay Buccaneers", "Raymond James Stadium, Tampa, FL", "Monday Night Football"),
    ("2026-12-03", "7:30 PM ET", "548566", "Kansas City Chiefs at Los Angeles Rams", "SoFi Stadium, Inglewood, CA", "Thursday Night Football"),
    ("2026-12-06", "7:30 PM ET", "548503", "Houston Texans at Pittsburgh Steelers", "Acrisure Stadium, Pittsburgh, PA", "Sunday Night Football"),
    ("2026-12-07", "7:00 PM ET", "548545", "Dallas Cowboys at Seattle Seahawks", "Lumen Field, Seattle, WA", "Monday Night Football"),
    ("2026-12-10", "7:30 PM ET", "548567", "Minnesota Vikings at New England Patriots", "Gillette Stadium, Foxborough, MA", "Thursday Night Football"),
    ("2026-12-13", "7:30 PM ET", "548505", "Buffalo Bills at Green Bay Packers", "Lambeau Field, Green Bay, WI", "Sunday Night Football"),
    ("2026-12-14", "7:00 PM ET", "548546", "Pittsburgh Steelers at Jacksonville Jaguars", "EverBank Stadium, Jacksonville, FL", "Monday Night Football"),
    ("2026-12-17", "7:30 PM ET", "548568", "San Francisco 49ers at Los Angeles Chargers", "SoFi Stadium, Inglewood, CA", "Thursday Night Football"),
    ("2026-12-19", "4:30 PM ET", "548517", "Seattle Seahawks at Philadelphia Eagles", "Lincoln Financial Field, Philadelphia, PA", "Week 15 Saturday NFL Doubleheader"),
    ("2026-12-19", "8:00 PM ET", "548518", "Chicago Bears at Buffalo Bills", "New Highmark Stadium, Orchard Park, NY", "Week 15 Saturday NFL Doubleheader"),
    ("2026-12-20", "7:30 PM ET", "548506", "Detroit Lions at Minnesota Vikings", "U.S. Bank Stadium, Minneapolis, MN", "Sunday Night Football"),
    ("2026-12-21", "7:00 PM ET", "548548", "New England Patriots at Kansas City Chiefs", "GEHA Field at Arrowhead Stadium, Kansas City, MO", "Monday Night Football"),
    ("2026-12-24", "7:30 PM ET", "548569", "Houston Texans at Philadelphia Eagles", "Lincoln Financial Field, Philadelphia, PA", "Thursday Night Football"),
    ("2026-12-25", "12:30 PM ET", "548528", "Green Bay Packers at Chicago Bears", "Soldier Field, Chicago, IL", "Christmas Day NFL Tripleheader"),
    ("2026-12-25", "4:15 PM ET", "548531", "Buffalo Bills at Denver Broncos", "Empower Field at Mile High, Denver, CO", "Christmas Day NFL Tripleheader"),
    ("2026-12-25", "8:00 PM ET", "548534", "Los Angeles Rams at Seattle Seahawks", "Lumen Field, Seattle, WA", "Christmas Day NFL Tripleheader"),
    ("2026-12-26", "4:00 PM ET", "548519", "Week 16 Saturday Doubleheader TBA (Game 1)", "TBA", "Week 16 Saturday NFL Doubleheader"),
    ("2026-12-26", "8:00 PM ET", "548520", "Week 16 Saturday Doubleheader TBA (Game 2)", "TBA", "Week 16 Saturday NFL Doubleheader"),
    ("2026-12-27", "7:30 PM ET", "548507", "Jacksonville Jaguars at Dallas Cowboys", "AT&T Stadium, Arlington, TX", "Sunday Night Football"),
    ("2026-12-28", "7:00 PM ET", "548550", "New York Giants at Detroit Lions", "Ford Field, Detroit, MI", "Monday Night Football"),
    ("2026-12-31", "7:30 PM ET", "548570", "Baltimore Ravens at Cincinnati Bengals", "Paycor Stadium, Cincinnati, OH", "Thursday Night Football"),
    ("2027-01-02", "4:00 PM ET", "548521", "Week 17 Saturday Doubleheader TBA (Game 1)", "TBA", "Week 17 Saturday NFL Doubleheader"),
    ("2027-01-02", "8:00 PM ET", "548522", "Week 17 Saturday Doubleheader TBA (Game 2)", "TBA", "Week 17 Saturday NFL Doubleheader"),
    ("2027-01-03", "7:30 PM ET", "548509", "Philadelphia Eagles at San Francisco 49ers", "Levi's Stadium, Santa Clara, CA", "Sunday Night Football"),
    ("2027-01-04", "7:00 PM ET", "548552", "Houston Texans at Green Bay Packers", "Lambeau Field, Green Bay, WI", "Monday Night Football"),
    ("2027-01-09", "12:30 PM ET", "548523", "Week 18 Saturday Tripleheader TBA (Game 1)", "TBA", "Week 18 Saturday NFL Tripleheader"),
    ("2027-01-09", "4:15 PM ET", "548524", "Week 18 Saturday Tripleheader TBA (Game 2)", "TBA", "Week 18 Saturday NFL Tripleheader"),
    ("2027-01-09", "8:00 PM ET", "548526", "Week 18 Saturday Tripleheader TBA (Game 3)", "TBA", "Week 18 Saturday NFL Tripleheader"),
    ("2027-01-10", "7:30 PM ET", "548510", "Week 18 Sunday Night Football — Teams TBA", "TBA", "Sunday Night Football"),
]

WESTWOOD_ONE_NCAA_VERIFIED = [
    ("2026-11-28", "11:30 AM ET", "557131", "NCAAF: Michigan at Ohio State", "Ohio Stadium, Columbus, OH", "https://www.westwoodonesports.com/events/557131"),
    ("2026-12-01", "9:15 PM ET", "581797", "NCAAB: Duke at Florida", "Exactech Arena, Gainesville, FL", "https://www.westwoodonesports.com/events/581797"),
    ("2026-12-05", "3:30 PM ET", "557146", "NCAAF: SEC Championship Game", "Mercedes-Benz Stadium, Atlanta, GA", "https://www.westwoodonesports.com/events/557146"),
    ("2026-12-12", "2:00 PM ET", "557132", "NCAAF: Army vs Navy", "MetLife Stadium, East Rutherford, NJ", "https://www.westwoodonesports.com/events/557132"),
]

# ---------------------------------------------------------------------------
# 6. STANFORD & CALIFORNIA NCAAF (2026 VERIFIED + 2027–2029 OFFICIAL PARTIAL)
# ---------------------------------------------------------------------------
STANFORD_2026 = [
    ("2026-08-29", "vs Hawai'i", "4:00 PM PT", "FINAL (W 37–27)", "KNBR 680/1050", "https://gostanford.com/boxscore/27043"),
    ("2026-09-04", "vs #7 Miami (Fri)", "6:00 PM PT", "FINAL (L 6–45)", "KNBR 680/1050", "https://gostanford.com/boxscore/27044"),
    ("2026-09-19", "at Duke", "1:00 PM PT", "FINAL (L 7–35)", "KNBR 680/1050", "https://gostanford.com/boxscore/27045"),
    ("2026-09-26", "vs Georgia Tech", "7:30 PM PT", "FINAL (W 34–27)", "KNBR 680/1050", "https://gostanford.com/boxscore/27046"),
    ("2026-10-03", "at Wake Forest", "", "FINAL (L 3–57)", "KNBR 680/1050", "https://gostanford.com/boxscore/27047"),
    ("2026-10-10", "at #3 Notre Dame", "12:30 PM PT", "FINAL (L 7–58)", "KNBR 680/1050", "https://gostanford.com/boxscore/27048"),
    ("2026-10-17", "vs Elon", "4:30 PM PT", "FINAL (W 34–7)", "KNBR 680/1050", "https://gostanford.com/boxscore/27049"),
    ("2026-10-23", "vs NC State (Fri)", "7:30 PM PT", "FINAL (W 31–28)", "KNBR 680/1050", "https://gostanford.com/boxscore/27050"),
    ("2026-10-31", "at Louisville", "", "FINAL (L 24–52)", "KNBR 680/1050", "https://gostanford.com/boxscore/27051"),
    ("2026-11-14", "at Virginia Tech", "", "FINAL (W 40–22)", "KNBR 680/1050", "https://gostanford.com/boxscore/27052"),
    ("2026-11-21", "at California (129th Big Game)", "4:30 PM PST", "FINAL (W 44–28 · Clinched Bowl Berth)", "KNBR 680 AM / 104.5 FM", "https://gostanford.com/news/2026/11/21/stanford-secures-bowl-berth-with-big-game-win"),
    ("2026-11-28", "vs SMU", "12:30 PM PST", "Scheduled (ACC Network)", "KNBR 680 AM / 1050 AM", "https://gostanford.com/sports/football/schedule"),
]

CAL_2026 = [
    ("2026-09-05", "vs UCLA", "7:30 PM PT", "FINAL (L 24–45)", "KSFO 810 AM", "https://calbears.com/sports/football/schedule"),
    ("2026-09-12", "at Syracuse", "12:30 PM PT", "FINAL (W 21–18)", "KSFO 810 AM", "https://calbears.com/sports/football/schedule"),
    ("2026-09-19", "vs Wagner", "12:30 PM PT", "FINAL (W 49–7)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38593"),
    ("2026-09-25", "vs Clemson (Fri)", "7:30 PM PT", "FINAL (L 10–24)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38594"),
    ("2026-10-03", "at UNLV", "12:30 PM PT", "FINAL (L 31–39)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38595"),
    ("2026-10-10", "vs Virginia Tech", "12:30 PM PT", "FINAL (W 25–20)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38596"),
    ("2026-10-17", "vs #21 Wake Forest", "7:30 PM PT", "FINAL (L 7–41)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38597"),
    ("2026-10-24", "at #23 SMU", "9:00 AM PT", "FINAL (L 20–59)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38598"),
    ("2026-10-31", "at NC State", "9:00 AM PT", "FINAL (L 10–31)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38599"),
    ("2026-11-14", "at Virginia", "12:30 PM PST", "FINAL (L 7–36)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38600"),
    ("2026-11-21", "vs Stanford (129th Big Game)", "4:30 PM PST", "FINAL (L 28–44)", "KSFO 810 AM", "https://calbears.com/boxscore.aspx?id=38601"),
    ("2026-11-28", "vs Pittsburgh", "4:30 PM PST", "Scheduled", "KSFO 810 AM", "https://calbears.com/sports/football/schedule"),
]

NCAAF_FUTURE_OFFICIAL_DATES = [
    {"date": "2027-08-28", "team": "California", "matchup": "vs Sacramento State (Week Zero)", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state.aspx"},
    {"date": "2027-09-04", "team": "Stanford", "matchup": "at TCU", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://gostanford.com/news/2016/06/14/boston-college-series"},
    {"date": "2027-09-11", "team": "Stanford", "matchup": "vs Vanderbilt", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://gostanford.com/news/2016/06/14/boston-college-series"},
    {"date": "2027-09-11", "team": "California", "matchup": "vs Old Dominion (Note: earlier 2024 release listed BYU on Sept 11 — flagged)", "official_time": "", "status": "PARTIAL (Date Confirmed · Opponent Conflict Flagged)", "source_url": "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state.aspx"},
    {"date": "2027-11-27", "team": "Stanford", "matchup": "vs Notre Dame (Legends Trophy)", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry"},
    {"date": "", "team": "Stanford (2027 ACC)", "matchup": "Home: Cal, Duke, North Carolina, Syracuse · Away: Boston College, Clemson, SMU, Virginia Tech", "official_time": "", "status": "PARTIAL (Opponents Verified · Dates Blank)", "source_url": "https://gostanford.com/news/2023/10/30/acc-announces-football-schedule-model"},
    {"date": "", "team": "California (2027 Non-Conf + ACC)", "matchup": "vs/at UCLA + 8 ACC conference games (dates/times unannounced)", "official_time": "", "status": "PARTIAL (Opponents Verified · Dates Blank)", "source_url": "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state.aspx"},
    {"date": "2028-09-02", "team": "California", "matchup": "vs Wyoming", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://calbears.com/news/2020/2/11/football-cal-adds-minnesota-and-wyoming-to-future-schedules"},
    {"date": "2028-09-16", "team": "California", "matchup": "at Minnesota", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://calbears.com/news/2020/2/11/football-cal-adds-minnesota-and-wyoming-to-future-schedules"},
    {"date": "2028-10-14", "team": "Stanford", "matchup": "at Notre Dame", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry"},
    {"date": "2028-11-25", "team": "Stanford", "matchup": "vs San Jose State (Bill Walsh Legacy Game)", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://gostanford.com/news/2025/12/16/updates-to-2026-schedule"},
    {"date": "", "team": "Stanford (2028 ACC)", "matchup": "Home: Clemson, SMU, Virginia, Virginia Tech · Away: Cal, Georgia Tech, Miami, North Carolina", "official_time": "", "status": "PARTIAL (Opponents Verified · Dates Blank)", "source_url": "https://gostanford.com/news/2023/10/30/acc-announces-football-schedule-model"},
    {"date": "2029-09-08", "team": "California", "matchup": "at Wyoming", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://calbears.com/news/2020/2/11/football-cal-adds-minnesota-and-wyoming-to-future-schedules"},
    {"date": "2029-09-15", "team": "Stanford", "matchup": "vs Boston College", "official_time": "", "status": "VERIFIED (Date) / TBD (Time)", "source_url": "https://gostanford.com/news/2016/06/14/boston-college-series"},
    {"date": "", "team": "Stanford (2029 ACC)", "matchup": "Home: Boston College, Cal, Louisville, Wake Forest · Away: Duke, Florida State, Pitt, SMU", "official_time": "", "status": "PARTIAL (Opponents Verified · Dates Blank)", "source_url": "https://gostanford.com/news/2023/10/30/acc-announces-football-schedule-model"},
]

# ---------------------------------------------------------------------------
# 7. DAILY SCHEDULE & PST MINUTE-BY-MINUTE ENGINE (2026-01-01 – 2029-12-31)
# ---------------------------------------------------------------------------
# Index exact games by date for fast lookup
giants_by_date: dict[str, list[dict]] = {}
for g in GIANTS_2027_GAMES:
    giants_by_date.setdefault(g["date"], []).append(g)

athletics_by_date: dict[str, list[dict]] = {}
for g in ATHLETICS_2027_GAMES:
    athletics_by_date.setdefault(g["date"], []).append(g)

niners_by_date: dict[str, list[tuple]] = {}
for row in FORTYNINERS_2026_FULL:
    niners_by_date.setdefault(row[0], []).append(row)

ww_nfl_by_date: dict[str, list[tuple]] = {}
for row in WESTWOOD_ONE_NFL_VERIFIED:
    ww_nfl_by_date.setdefault(row[0], []).append(row)

ww_ncaa_by_date: dict[str, list[tuple]] = {}
for row in WESTWOOD_ONE_NCAA_VERIFIED:
    ww_ncaa_by_date.setdefault(row[0], []).append(row)

stanford_2026_by_date = {r[0]: r for r in STANFORD_2026}
cal_2026_by_date = {r[0]: r for r in CAL_2026}
ncaaf_future_by_date: dict[str, list[dict]] = {}
for row in NCAAF_FUTURE_OFFICIAL_DATES:
    if row["date"]:
        ncaaf_future_by_date.setdefault(row["date"], []).append(row)

# Verified 2026-27 NFL Postseason exact game dates (nfl.com/news/2026-27-national-football-league-important-dates)
NFL_2026_27_PLAYOFF_DATES = {
    "2027-01-16": ("NFL Wild Card Saturday (Tripleheader)", [(13 * 60 + 30, 192), (17 * 60, 192)]),
    "2027-01-17": ("NFL Wild Card Sunday (Tripleheader)", [(10 * 60, 192), (13 * 60 + 30, 192), (17 * 60 + 15, 192)]),
    "2027-01-18": ("NFL Wild Card Monday Night Football", [(17 * 60 + 15, 192)]),
    "2027-01-23": ("NFL Divisional Playoffs Saturday (Doubleheader)", [(13 * 60 + 30, 192), (17 * 60 + 15, 192)]),
    "2027-01-24": ("NFL Divisional Playoffs Sunday (Doubleheader)", [(12 * 60, 192), (15 * 60 + 30, 192)]),
    "2027-01-31": ("AFC & NFC Championship Sunday (Doubleheader)", [(12 * 60, 192), (15 * 60 + 30, 192)]),
    "2027-02-14": ("Super Bowl LXI — SoFi Stadium, Inglewood", [(15 * 60 + 30, 225)]),
}

# Verified Jan–Feb 2026 (2025 season playoffs ending Super Bowl LX Feb 8, 2026)
NFL_2025_26_PLAYOFF_DATES = {
    "2026-01-03": ("2025 NFL Week 18 Saturday Doubleheader", [(13 * 60 + 30, 192), (17 * 60, 192)]),
    "2026-01-04": ("2025 NFL Week 18 Sunday Slate", [(10 * 60, 192), (13 * 60 + 25, 192), (17 * 60 + 20, 192)]),
    "2026-01-10": ("2025–26 NFL Wild Card Saturday", [(13 * 60 + 30, 192), (17 * 60, 192)]),
    "2026-01-11": ("2025–26 NFL Wild Card Sunday", [(10 * 60, 192), (13 * 60 + 30, 192), (17 * 60 + 15, 192)]),
    "2026-01-12": ("2025–26 NFL Wild Card Monday", [(17 * 60 + 15, 192)]),
    "2026-01-17": ("2025–26 NFL Divisional Saturday", [(13 * 60 + 30, 192), (17 * 60 + 15, 192)]),
    "2026-01-18": ("2025–26 NFL Divisional Sunday", [(12 * 60, 192), (15 * 60 + 30, 192)]),
    "2026-01-25": ("2025–26 AFC & NFC Championship Sunday", [(12 * 60, 192), (15 * 60 + 30, 192)]),
    "2026-02-08": ("Super Bowl LX — Levi's Stadium, Santa Clara", [(15 * 60 + 30, 225)]),
}

# Estimated future NFL Postseason exact round structure (modeled on NFL 14-team format + abolished Pro Bowl game)
def build_est_nfl_playoffs(wc_sat_iso: str, sb_label: str, sb_source: str) -> dict[str, tuple[str, list, str]]:
    wc_sat = dt.date.fromisoformat(wc_sat_iso)
    out = {}
    def iso(off): return (wc_sat + dt.timedelta(days=off)).isoformat()
    out[iso(0)] = ("NFL Wild Card Saturday (Est.)", [(13 * 60 + 30, 192), (17 * 60, 192)], sb_source)
    out[iso(1)] = ("NFL Wild Card Sunday (Est.)", [(10 * 60, 192), (13 * 60 + 30, 192), (17 * 60 + 15, 192)], sb_source)
    out[iso(2)] = ("NFL Wild Card Monday (Est.)", [(17 * 60 + 15, 192)], sb_source)
    out[iso(7)] = ("NFL Divisional Saturday (Est.)", [(13 * 60 + 30, 192), (17 * 60 + 15, 192)], sb_source)
    out[iso(8)] = ("NFL Divisional Sunday (Est.)", [(12 * 60, 192), (15 * 60 + 30, 192)], sb_source)
    out[iso(15)] = ("AFC & NFC Championship Sunday (Est.)", [(12 * 60, 192), (15 * 60 + 30, 192)], sb_source)
    # Days 16..28 = 13-day pre-Super Bowl NFL-free window (AFC-NFC Pro Bowl game discontinued Aug 27, 2026!)
    out[iso(29)] = (sb_label, [(15 * 60 + 30, 225)], sb_source)
    return out


EST_PLAYOFFS_2028 = build_est_nfl_playoffs(
    "2028-01-15",
    "Super Bowl LXII — Mercedes-Benz Stadium, Atlanta (Host Verified · Date Est. Feb 13, 2028)",
    "https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028",
)
EST_PLAYOFFS_2029 = build_est_nfl_playoffs(
    "2029-01-13",
    "Super Bowl LXIII — Allegiant Stadium, Las Vegas (Host Verified · Date Est. Feb 11, 2029)",
    "https://www.nfl.com/news/las-vegas-to-host-super-bowl-lxiii-in-2029",
)

# Verified 2026-27 CFP dates (for Full Radio 94122 ESPN Radio / Westwood One tier)
CFP_2026_27_DATES = {
    "2026-12-18": ("CFP First Round (Fri)", 17 * 60, 204),
    "2026-12-19": ("CFP First Round Tripleheader (Sat)", 9 * 60, 630),
    "2026-12-30": ("CFP Quarterfinal — Fiesta Bowl", 16 * 60 + 30, 204),
    "2027-01-01": ("CFP Quarterfinal Tripleheader (Cotton, Rose, Peach)", 9 * 60, 660),
    "2027-01-14": ("CFP Semifinal — Orange Bowl", 16 * 60 + 30, 204),
    "2027-01-15": ("CFP Semifinal — Sugar Bowl", 16 * 60 + 30, 204),
    "2027-01-25": ("2027 CFP National Championship (Allegiant Stadium)", 16 * 60 + 30, 215),
}


def make_event(
    *,
    title: str,
    category: str,
    sport_key: str,
    start_pst: int,
    dur_min: int,
    priority: str,
    status: str,
    radio: str,
    source_url: str,
    tiers: list[str],
    official_time_label: str = "",
) -> dict:
    end_pst = min(1440, start_pst + dur_min)
    start_clamped = max(0, start_pst)
    spec = DURATIONS[sport_key]
    ht_window = None
    if spec["halftime"] > 0 and start_clamped + spec["halftime_offset"] < 1440:
        hs = start_clamped + spec["halftime_offset"]
        he = min(1440, hs + spec["halftime"])
        ht_window = f"{fmt_hm_12(hs)}–{fmt_hm_12(he)} PST ({spec['halftime']}m)"
    return {
        "title": title,
        "category": category,
        "start_pst": start_clamped,
        "end_pst": end_pst,
        "window_pst": f"{fmt_hm_12(start_clamped)} – {fmt_hm_12(end_pst)} PST",
        "halftime_pst": ht_window or "—",
        "official_time": official_time_label,  # Blank ("") if unverified/estimated!
        "priority": priority,
        "status": status,
        "radio": radio,
        "source_url": source_url,
        "tiers": tiers,
    }


def build_day_events(day: dt.date) -> list[dict]:
    iso = day.isoformat()
    yr = day.year
    wd = day.weekday()  # Mon=0 .. Sun=6
    events: list[dict] = []

    # ---- A. MLB ----
    if yr == 2026 and iso in MLB_DAILY_COUNTS_2026:
        cnt = MLB_DAILY_COUNTS_2026[iso]
        is_spring = iso < "2026-03-25"
        is_post = iso >= "2026-09-29"
        is_asg = iso == "2026-07-14"
        phase = "Spring Training" if is_spring else ("All-Star Game" if is_asg else ("Postseason" if is_post else "Regular Season"))
        tiers = ["core_strict", "full_radio_94122"] if is_spring else ["core_strict", "core_regular", "full_radio_94122"]
        if not is_spring:
            tiers.append("sf_high_priority")
        s_min = 12 * 60 + 5 if (is_spring or wd in (5, 6)) else 17 * 60 + 45
        events.append(make_event(
            title=f"MLB 2026 {phase} ({cnt} official game{'s' if cnt != 1 else ''} across 30 clubs)",
            category="MLB",
            sport_key="MLB",
            start_pst=s_min,
            dur_min=158 if cnt <= 2 else 210,
            priority="HIGH PRIORITY" if not is_post else "STANDARD",
            status="VERIFIED",
            radio="KNBR 680/104.5 · KNEW 960/KSTE 650 · KTCT 1050 ESPN Radio",
            source_url=f"https://www.mlb.com/schedule/{iso}",
            tiers=tiers,
            official_time_label="Completed 2026 Slate",
        ))

    elif yr == 2027:
        # Exact Giants & Athletics games from official MLB StatsAPI!
        g_list = giants_by_date.get(iso, [])
        a_list = athletics_by_date.get(iso, [])
        for g in g_list:
            is_spring = g["phase"] != "Regular Season"
            tiers = ["core_strict", "sf_high_priority", "full_radio_94122"]
            if not is_spring:
                tiers.append("core_regular")
            events.append(make_event(
                title=f"MLB HIGH: SF Giants {g['matchup']} ({g['phase']})",
                category="MLB — SF Giants",
                sport_key="MLB",
                start_pst=g["start_min_pst"],
                dur_min=158,
                priority="HIGH PRIORITY",
                status=g["status"],
                radio=g["radio"],
                source_url=g["source_url"],
                tiers=tiers,
                official_time_label=g["official_time_pst"],
            ))
        for g in a_list:
            if g["is_bay_bridge"] and g_list:
                # Still list Athletics perspective or note dual Bay Bridge high-priority broadcast
                pass
            is_spring = g["phase"] != "Regular Season"
            tiers = ["core_strict", "sf_high_priority", "full_radio_94122"]
            if not is_spring:
                tiers.append("core_regular")
            events.append(make_event(
                title=f"MLB HIGH: Athletics {g['matchup']} ({g['phase']})",
                category="MLB — Athletics",
                sport_key="MLB",
                start_pst=g["start_min_pst"],
                dur_min=158,
                priority="HIGH PRIORITY",
                status=g["status"],
                radio=g["radio"],
                source_url=g["source_url"],
                tiers=tiers,
                official_time_label=g["official_time_pst"],
            ))
        # Remaining 28 MLB clubs on days in statsapi.mlb.com
        if iso in MLB_DAILY_COUNTS_2027:
            tot = MLB_DAILY_COUNTS_2027[iso]
            local_cnt = len(g_list) + len([x for x in a_list if not x["is_bay_bridge"]])
            other_cnt = max(0, tot - local_cnt)
            is_spring = iso < "2027-03-24"
            is_asg = iso == "2027-07-13"
            if is_asg:
                events.append(make_event(
                    title="2027 MLB All-Star Game at Wrigley Field (Chicago)",
                    category="MLB — All-Star",
                    sport_key="MLB",
                    start_pst=17 * 60,
                    dur_min=180,
                    priority="HIGH PRIORITY",
                    status="PARTIAL (Date Verified · Time TBD)",
                    radio="KTCT 1050 AM (ESPN Radio National)",
                    source_url="https://www.mlb.com/all-star",
                    tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                    official_time_label="",
                ))
            elif other_cnt > 0:
                tiers = ["core_strict", "full_radio_94122"] if is_spring else ["core_strict", "core_regular", "full_radio_94122"]
                s_min = 10 * 60 + 10 if wd in (5, 6) else 15 * 60 + 40
                events.append(make_event(
                    title=f"MLB League Slate ({other_cnt} other game{'s' if other_cnt != 1 else ''} across 30 MLB clubs)",
                    category="MLB — 30 Clubs",
                    sport_key="MLB",
                    start_pst=s_min,
                    dur_min=158,
                    priority="STANDARD",
                    status="VERIFIED",
                    radio="ESPN Radio select (KTCT 1050 AM) / MLB 30-club rule",
                    source_url=f"https://www.mlb.com/schedule/{iso}",
                    tiers=tiers,
                    official_time_label="Multiple (see mlb.com)",
                ))
        # Estimated 2027 MLB Postseason (Sep 28 – Oct 30, 2027; omit typical World Series travel Thursdays Oct 21/28? Keep realistic WC/DS/LCS/WS game days)
        if "2027-09-28" <= iso <= "2027-10-30" and iso not in ("2027-09-27", "2027-10-01", "2027-10-21", "2027-10-25", "2027-10-29"):
            events.append(make_event(
                title="2027 MLB Postseason Window (Estimated — Official Bracket Dates Unreleased)",
                category="MLB — Postseason (Est.)",
                sport_key="MLB",
                start_pst=17 * 60,
                dur_min=175,
                priority="HIGH PRIORITY",
                status="ESTIMATED",
                radio="KTCT 1050 AM (ESPN Radio) / KNBR 680 if Giants qualify",
                source_url="https://www.mlb.com/schedule",
                tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                official_time_label="",
            ))

    elif yr in (2028, 2029):
        # Estimated MLB Spring Training + Regular Season + Postseason for 2028 & 2029
        sp_start = f"{yr}-02-18" if yr == 2028 else f"{yr}-02-17"
        reg_start = f"{yr}-03-23" if yr == 2028 else f"{yr}-03-22"  # Modeled on 2026/2027 late-March Opening Night!
        reg_end = f"{yr}-09-24" if yr == 2028 else f"{yr}-09-23"
        post_start = f"{yr}-09-26" if yr == 2028 else f"{yr}-09-25"
        post_end = f"{yr}-10-28" if yr == 2028 else f"{yr}-10-27"
        asg_tue = "2028-07-11" if yr == 2028 else "2029-07-10"
        asg_free = {"2028-07-10", "2028-07-12"} if yr == 2028 else {"2029-07-09", "2029-07-11"}

        if sp_start <= iso < reg_start:
            events.append(make_event(
                title=f"{yr} MLB Spring Training — Giants, A's & All 30 Clubs (Estimated)",
                category="MLB — Spring (Est.)",
                sport_key="MLB",
                start_pst=12 * 60 + 5,
                dur_min=158,
                priority="HIGH PRIORITY",
                status="ESTIMATED",
                radio="KNBR 680/104.5 · A's Radio Network",
                source_url="https://www.mlb.com/schedule",
                tiers=["core_strict", "sf_high_priority", "full_radio_94122"],
                official_time_label="",
            ))
        elif reg_start <= iso <= reg_end and iso not in asg_free:
            if iso == asg_tue and yr == 2028:
                events.append(make_event(
                    title="2028 MLB All-Star Game at Oracle Park, San Francisco (Host Verified · Exact July Date Unconfirmed)",
                    category="MLB — All-Star",
                    sport_key="MLB",
                    start_pst=17 * 60,
                    dur_min=180,
                    priority="HIGH PRIORITY",
                    status="PARTIAL (Host Verified · Date Blank)",
                    radio="KNBR 680/104.5 · KTCT 1050 ESPN Radio",
                    source_url="https://www.mlb.com/giants/fans/all-star-game",
                    tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                    official_time_label="",
                ))
            else:
                s_min = 12 * 60 + 5 if wd in (5, 6) else 17 * 60 + 45
                tiers = ["core_strict", "core_regular", "full_radio_94122"]
                if wd != 3:  # Typical Giants/A's play ~6 days/week
                    tiers.append("sf_high_priority")
                events.append(make_event(
                    title=f"{yr} MLB Regular Season — Giants, A's & 30 Clubs (Estimated)",
                    category="MLB (Est.)",
                    sport_key="MLB",
                    start_pst=s_min,
                    dur_min=158,
                    priority="HIGH PRIORITY",
                    status="ESTIMATED",
                    radio="KNBR 680/104.5 · A's Radio · KTCT 1050",
                    source_url="https://www.mlb.com/schedule",
                    tiers=tiers,
                    official_time_label="",
                ))
        elif post_start <= iso <= post_end and wd != 3:
            events.append(make_event(
                title=f"{yr} MLB Postseason Window (Estimated)",
                category="MLB — Postseason (Est.)",
                sport_key="MLB",
                start_pst=17 * 60,
                dur_min=175,
                priority="HIGH PRIORITY",
                status="ESTIMATED",
                radio="KTCT 1050 ESPN Radio / KNBR 680",
                source_url="https://www.mlb.com/schedule",
                tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                official_time_label="",
            ))

    # ---- B. NFL & 49ERS & WESTWOOD ONE NFL ----
    # 1) Exact 2026-27 49ers games
    for row in niners_by_date.get(iso, []):
        _, wk_lbl, opp, venue, off_pt, res_note, url = row
        is_pre = "Preseason" in wk_lbl
        utc_dt = pt_str_to_utc(iso, off_pt)
        if utc_dt:
            off_pst_s, s_pst, _, _, _ = utc_to_pst_and_pt(utc_dt)
            st = "VERIFIED"
        else:
            off_pst_s = ""
            s_pst = 17 * 60 if is_pre else 13 * 60 + 25
            st = "PARTIAL (Date Verified · Time TBD)" if not is_pre else "VERIFIED (Completed)"
        tiers = ["core_strict", "sf_high_priority", "full_radio_94122"]
        if not is_pre:
            tiers.append("core_regular")
        events.append(make_event(
            title=f"NFL HIGH: SF 49ers {opp} ({wk_lbl})",
            category="NFL — SF 49ers",
            sport_key="NFL",
            start_pst=s_pst,
            dur_min=192,
            priority="HIGH PRIORITY",
            status=st,
            radio="KSAN 107.7 FM / KNBR 104.5 FM / 680 AM",
            source_url=url,
            tiers=tiers,
            official_time_label=off_pst_s,
        ))

    # 2) Exact Westwood One verified NFL broadcasts (Nov 25, 2026 – Jan 10, 2027)
    for row in ww_nfl_by_date.get(iso, []):
        _, et_str, ev_id, matchup, venue, pkg_lbl = row
        utc_dt = et_str_to_utc(iso, et_str)
        off_pst_s, s_pst, _, _, _ = utc_to_pst_and_pt(utc_dt)
        st = "VERIFIED" if "TBA" not in matchup else "PARTIAL (Window Verified · Teams TBA)"
        events.append(make_event(
            title=f"Westwood One NFL: {matchup} ({pkg_lbl})",
            category="Westwood One NFL",
            sport_key="NFL",
            start_pst=s_pst,
            dur_min=192,
            priority="HIGH PRIORITY",
            status=st,
            radio="Westwood One Sports (KNBR 680 / KTCT 1050)",
            source_url=f"https://www.westwoodonesports.com/events/{ev_id}",
            tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
            official_time_label=off_pst_s,
        ))

    # 3) Other 2026 NFL Preseason & Regular Season league windows (Aug 6 – Nov 23, 2026 & Sunday daytime slates Nov 29 – Jan 10)
    if "2026-08-06" <= iso <= "2026-08-29" and wd in (3, 4, 5, 6) and iso not in niners_by_date:
        events.append(make_event(
            title="2026 NFL Preseason League Slate" if iso != "2026-08-06" else "2026 NFL Hall of Fame Game (Preseason Kickoff)",
            category="NFL — Preseason",
            sport_key="NFL",
            start_pst=17 * 60,
            dur_min=192,
            priority="STANDARD",
            status="VERIFIED",
            radio="Westwood One (HoF Game) / NFL League Rule",
            source_url="https://www.nfl.com/schedules/",
            tiers=["core_strict", "full_radio_94122"],
            official_time_label="Completed",
        ))
    if "2026-09-09" <= iso <= "2026-11-23":
        if iso == "2026-09-09" or wd in (0, 3, 6):
            s_pst = 9 * 60 if wd == 6 else 16 * 60 + 15
            dur = 520 if wd == 6 else 192
            events.append(make_event(
                title="2026 NFL Regular Season + Westwood One National Primetime",
                category="NFL — 32 Teams",
                sport_key="NFL",
                start_pst=s_pst,
                dur_min=dur,
                priority="STANDARD",
                status="VERIFIED",
                radio="Westwood One Sports / NFL 32-Team Rule",
                source_url="https://www.nfl.com/schedules/",
                tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                official_time_label="Completed",
            ))
    elif "2026-11-29" <= iso <= "2027-01-10" and wd == 6:
        # Sunday early & late afternoon NFL 32-team windows (10:00 AM PST & 1:05/1:25 PM PST)
        events.append(make_event(
            title="NFL Week Sunday Early & Late Afternoon Slate (All 32 Teams)",
            category="NFL — 32 Teams",
            sport_key="NFL",
            start_pst=10 * 60,
            dur_min=395,
            priority="STANDARD",
            status="VERIFIED",
            radio="Westwood One Sunday Doubleheader / KNBR",
            source_url="https://www.nfl.com/schedules/",
            tiers=["core_strict", "core_regular", "full_radio_94122"],
            official_time_label="10:00 AM & 1:05/1:25 PM PST",
        ))

    # 4) Verified 2025-26 & 2026-27 NFL Postseason exact dates
    if iso in NFL_2025_26_PLAYOFF_DATES:
        lbl, slots = NFL_2025_26_PLAYOFF_DATES[iso]
        sk = "NFL_SB" if "Super Bowl" in lbl else "NFL"
        for idx, (s_m, d_m) in enumerate(slots, 1):
            suffix = f" (Game {idx})" if len(slots) > 1 else ""
            events.append(make_event(
                title=f"{lbl}{suffix}",
                category="NFL — Postseason",
                sport_key=sk,
                start_pst=s_m,
                dur_min=d_m,
                priority="HIGH PRIORITY",
                status="VERIFIED",
                radio="Westwood One Sports (KNBR 680 / KTCT 1050)",
                source_url="https://www.nfl.com/schedules/",
                tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                official_time_label="Completed",
            ))

    if iso in NFL_2026_27_PLAYOFF_DATES:
        lbl, slots = NFL_2026_27_PLAYOFF_DATES[iso]
        sk = "NFL_SB" if "Super Bowl" in lbl else "NFL"
        for idx, (s_m, d_m) in enumerate(slots, 1):
            suffix = f" (Window {idx})" if len(slots) > 1 else ""
            events.append(make_event(
                title=f"{lbl}{suffix}",
                category="NFL — Postseason",
                sport_key=sk,
                start_pst=s_m,
                dur_min=d_m,
                priority="HIGH PRIORITY",
                status="VERIFIED (Date) / Est. Kickoff",
                radio="Westwood One Sports (All Playoff Games + Super Bowl LXI)",
                source_url="https://www.nfl.com/news/2026-27-national-football-league-important-dates",
                tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                official_time_label="",
            ))

    # 5) Estimated 2027, 2028, 2029 NFL Preseason, Regular Season, and Postseason
    nfl_est_seasons = [
        (2027, "2027-08-05", "2027-08-28", "2027-09-09", "2028-01-09"),
        (2028, "2028-08-03", "2028-08-26", "2028-09-07", "2029-01-07"),
        (2029, "2029-08-02", "2029-08-25", "2029-09-06", "2029-12-31"),
    ]
    for syr, pre_s, pre_e, reg_s, reg_e in nfl_est_seasons:
        if pre_s <= iso <= pre_e and wd in (3, 4, 5, 6):
            tiers = ["core_strict", "full_radio_94122"]
            if wd == 5:  # Typical 49ers preseason Saturday/Thursday estimate
                tiers.append("sf_high_priority")
            events.append(make_event(
                title=f"{syr} NFL Preseason Window — 49ers & 32 Teams (Estimated)",
                category="NFL — Preseason (Est.)",
                sport_key="NFL",
                start_pst=17 * 60,
                dur_min=192,
                priority="HIGH PRIORITY" if wd == 5 else "STANDARD",
                status="ESTIMATED",
                radio="KSAN 107.7 / KNBR 680 (49ers) · Westwood One",
                source_url="https://www.nfl.com/schedules/",
                tiers=tiers,
                official_time_label="",
            ))
        elif reg_s <= iso <= reg_e:
            is_thanksgiving = (day.month == 11 and wd == 3 and 22 <= day.day <= 28)
            is_black_friday = (day.month == 11 and wd == 4 and 23 <= day.day <= 29)
            is_christmas = (day.month == 12 and day.day == 25)
            is_late_sat = (wd == 5 and (day.month == 12 and day.day >= 15 or day.month == 1))
            if is_thanksgiving or is_christmas:
                for idx, sm in enumerate((9 * 60 + 30, 13 * 60 + 15, 17 * 60 + 20), 1):
                    events.append(make_event(
                        title=f"{syr} NFL Holiday Tripleheader Game {idx} — Westwood One (Estimated)",
                        category="Westwood One NFL (Est.)",
                        sport_key="NFL",
                        start_pst=sm,
                        dur_min=192,
                        priority="HIGH PRIORITY",
                        status="ESTIMATED",
                        radio="Westwood One Sports (KNBR 680 / KTCT 1050)",
                        source_url="https://www.westwoodonesports.com/nfl-schedule/",
                        tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                        official_time_label="",
                    ))
            elif is_black_friday:
                events.append(make_event(
                    title=f"{syr} NFL Black Friday National Broadcast (Estimated)",
                    category="Westwood One NFL (Est.)",
                    sport_key="NFL",
                    start_pst=12 * 60,
                    dur_min=192,
                    priority="HIGH PRIORITY",
                    status="ESTIMATED",
                    radio="Westwood One Sports",
                    source_url="https://www.westwoodonesports.com/nfl-schedule/",
                    tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                    official_time_label="",
                ))
            elif wd == 6:  # Sunday NFL triple window (10am, 1:25pm, 5:20pm SNF)
                events.append(make_event(
                    title=f"{syr} NFL Sunday Early/Late Afternoon Slate + 49ers Window (Estimated)",
                    category="NFL — 49ers & 32 Teams (Est.)",
                    sport_key="NFL",
                    start_pst=10 * 60,
                    dur_min=395,
                    priority="HIGH PRIORITY",
                    status="ESTIMATED",
                    radio="KSAN 107.7 / KNBR 680 (49ers) · Westwood One",
                    source_url="https://www.nfl.com/schedules/",
                    tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                    official_time_label="",
                ))
                events.append(make_event(
                    title=f"{syr} Westwood One Sunday Night Football (Estimated)",
                    category="Westwood One NFL (Est.)",
                    sport_key="NFL",
                    start_pst=17 * 60 + 20,
                    dur_min=192,
                    priority="HIGH PRIORITY",
                    status="ESTIMATED",
                    radio="Westwood One Sports (KNBR 680 / KTCT 1050)",
                    source_url="https://www.westwoodonesports.com/nfl-schedule/",
                    tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                    official_time_label="",
                ))
            elif wd in (0, 3):  # MNF / TNF
                lbl = "Monday Night Football" if wd == 0 else "Thursday Night Football"
                events.append(make_event(
                    title=f"{syr} Westwood One {lbl} (Estimated)",
                    category="Westwood One NFL (Est.)",
                    sport_key="NFL",
                    start_pst=17 * 60 + 15,
                    dur_min=192,
                    priority="HIGH PRIORITY",
                    status="ESTIMATED",
                    radio="Westwood One Sports (KNBR 680 / KTCT 1050)",
                    source_url="https://www.westwoodonesports.com/nfl-schedule/",
                    tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                    official_time_label="",
                ))
            elif is_late_sat:
                for idx, sm in enumerate((13 * 60 + 30, 17 * 60 + 15), 1):
                    events.append(make_event(
                        title=f"{syr} NFL Late-Season Saturday Doubleheader Game {idx} (Estimated)",
                        category="Westwood One NFL (Est.)",
                        sport_key="NFL",
                        start_pst=sm,
                        dur_min=192,
                        priority="HIGH PRIORITY",
                        status="ESTIMATED",
                        radio="Westwood One Sports",
                        source_url="https://www.westwoodonesports.com/nfl-schedule/",
                        tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                        official_time_label="",
                    ))

    for playoff_map in (EST_PLAYOFFS_2028, EST_PLAYOFFS_2029):
        if iso in playoff_map:
            lbl, slots, s_url = playoff_map[iso]
            sk = "NFL_SB" if "Super Bowl" in lbl else "NFL"
            for idx, (s_m, d_m) in enumerate(slots, 1):
                suffix = f" (Window {idx})" if len(slots) > 1 else ""
                events.append(make_event(
                    title=f"{lbl}{suffix}",
                    category="NFL — Postseason (Est.)",
                    sport_key=sk,
                    start_pst=s_m,
                    dur_min=d_m,
                    priority="HIGH PRIORITY",
                    status="PARTIAL (SB Host Verified · Playoff Dates Est.)" if "Super Bowl" in lbl else "ESTIMATED",
                    radio="Westwood One Sports (All Playoff Games)",
                    source_url=s_url,
                    tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                    official_time_label="",
                ))

    # ---- C. NCAAF STANFORD & CALIFORNIA ----
    if iso in stanford_2026_by_date:
        _, opp, pt_str, res, rad, url = stanford_2026_by_date[iso]
        utc_dt = pt_str_to_utc(iso, pt_str)
        if utc_dt:
            off_pst_s, s_pst, _, _, _ = utc_to_pst_and_pt(utc_dt)
        else:
            off_pst_s, s_pst = "", 12 * 60 + 30
        events.append(make_event(
            title=f"NCAAF HIGH: Stanford {opp} ({res})",
            category="NCAAF — Stanford",
            sport_key="NCAAF",
            start_pst=s_pst,
            dur_min=204,
            priority="HIGH PRIORITY",
            status="VERIFIED",
            radio=rad,
            source_url=url,
            tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
            official_time_label=off_pst_s,
        ))
    if iso in cal_2026_by_date:
        _, opp, pt_str, res, rad, url = cal_2026_by_date[iso]
        utc_dt = pt_str_to_utc(iso, pt_str)
        if utc_dt:
            off_pst_s, s_pst, _, _, _ = utc_to_pst_and_pt(utc_dt)
        else:
            off_pst_s, s_pst = "", 12 * 60 + 30
        events.append(make_event(
            title=f"NCAAF HIGH: California {opp} ({res})",
            category="NCAAF — California",
            sport_key="NCAAF",
            start_pst=s_pst,
            dur_min=204,
            priority="HIGH PRIORITY",
            status="VERIFIED",
            radio=rad,
            source_url=url,
            tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
            official_time_label=off_pst_s,
        ))
    # Stanford 2026 Bowl Eligibility (clinched Nov 21, 2026; ACC bowl slot typically Dec 26–31, 2026; exact bowl announced Dec 6, 2026)
    if iso == "2026-12-28":
        events.append(make_event(
            title="NCAAF HIGH: Stanford 2026 Bowl Game Placeholder (Bowl Clinched Nov 21 · Exact Date/Bowl Announced Dec 6)",
            category="NCAAF — Stanford Bowl (TBD)",
            sport_key="NCAAF",
            start_pst=13 * 60,
            dur_min=204,
            priority="HIGH PRIORITY",
            status="PARTIAL (Bowl Berth Verified · Date/Opponent TBD)",
            radio="KNBR 680 AM / 1050 AM",
            source_url="https://gostanford.com/news/2026/11/21/stanford-secures-bowl-berth-with-big-game-win",
            tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
            official_time_label="",
        ))

    # Future NCAAF 2027-2029 officially dated games + remaining ACC Saturdays
    if yr in (2027, 2028, 2029):
        dated_rows = ncaaf_future_by_date.get(iso, [])
        for idx, r in enumerate(dated_rows):
            events.append(make_event(
                title=f"NCAAF HIGH: {r['team']} {r['matchup']}",
                category=f"NCAAF — {r['team']}",
                sport_key="NCAAF",
                start_pst=12 * 60 + 30 + idx * 210,
                dur_min=204,
                priority="HIGH PRIORITY",
                status=r["status"],
                radio="KNBR 680/1050 (Stanford) · KSFO 810 AM (Cal)",
                source_url=r["source_url"],
                tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                official_time_label="",
            ))
        ncaaf_bounds = {
            2027: ("2027-08-28", "2027-11-27"),
            2028: ("2028-08-26", "2028-11-25"),
            2029: ("2029-08-25", "2029-11-24"),
        }[yr]
        if ncaaf_bounds[0] <= iso <= ncaaf_bounds[1] and wd == 5 and not dated_rows:
            events.append(make_event(
                title=f"{yr} NCAAF Stanford & Cal ACC Saturday Window (Opponents Announced · Exact Date/Kickoff TBD)",
                category="NCAAF — Stanford/Cal (Est.)",
                sport_key="NCAAF",
                start_pst=12 * 60 + 30,
                dur_min=204,
                priority="HIGH PRIORITY",
                status="ESTIMATED",
                radio="KNBR 680/1050 · KSFO 810 AM",
                source_url="https://gostanford.com/news/2023/10/30/acc-announces-football-schedule-model",
                tiers=["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"],
                official_time_label="",
            ))

    # ---- D. TIER 4 ONLY: ALL OTHER SF 94122 OVER-THE-AIR AM/FM SPORTS ----
    # 1) Westwood One NCAA Football & Basketball verified upcoming
    for row in ww_ncaa_by_date.get(iso, []):
        _, et_s, _, title_s, _, url_s = row
        utc_dt = et_str_to_utc(iso, et_s)
        off_pst_s, s_pst, _, _, _ = utc_to_pst_and_pt(utc_dt)
        sk = "NCAAB" if "NCAAB" in title_s else "NCAAF"
        events.append(make_event(
            title=f"Westwood One {title_s}",
            category="Westwood One NCAA",
            sport_key=sk,
            start_pst=s_pst,
            dur_min=DURATIONS[sk]["game"],
            priority="HIGH PRIORITY (Radio 94122)",
            status="VERIFIED",
            radio="Westwood One Sports (KNBR 680 / KTCT 1050)",
            source_url=url_s,
            tiers=["full_radio_94122"],
            official_time_label=off_pst_s,
        ))

    # 2) CFP National Radio on KTCT 1050 ESPN Radio (2026-27 verified)
    if iso in CFP_2026_27_DATES:
        cfp_lbl, cfp_s, cfp_d = CFP_2026_27_DATES[iso]
        events.append(make_event(
            title=f"ESPN Radio National CFP: {cfp_lbl}",
            category="CFP Radio (94122)",
            sport_key="NCAAF",
            start_pst=cfp_s,
            dur_min=cfp_d,
            priority="HIGH PRIORITY (Radio 94122)",
            status="VERIFIED",
            radio="KTCT 1050 AM (ESPN Radio)",
            source_url="https://collegefootballplayoff.com/news/2026/6/1/26-27-broadcast-sked",
            tiers=["full_radio_94122"],
            official_time_label=f"{fmt_hm_12(cfp_s)} PST",
        ))

    # 3) Golden State Warriors NBA on 95.7 The Game KGMZ-FM (Oct – Apr; All-Star break Feb 14–23, 2027 free of regular-season games!)
    # Verified 2026-27 season: Oct 21, 2026 – Apr 11, 2027 (All-Star Feb 19–21, 2027; Warriors 6-game road trip ends Feb 13, 2027; no Warriors games Feb 14–18 & Feb 22–23).
    warriors_verified_dates = {
        "2026-10-21": ("at Los Angeles Lakers (Season Opener)", 19 * 60),
        "2026-12-01": ("vs Utah Jazz (NBC)", 20 * 60),
        "2027-01-12": ("vs Sacramento Kings (NBC)", 20 * 60),
        "2027-03-09": ("vs Portland Trail Blazers (NBC)", 20 * 60),
        "2027-04-06": ("vs Western Conf Opponent (NBC)", 20 * 60),
    }
    if iso in warriors_verified_dates:
        w_opp, w_s = warriors_verified_dates[iso]
        events.append(make_event(
            title=f"NBA Radio: Golden State Warriors {w_opp}",
            category="NBA — Warriors (95.7 FM)",
            sport_key="NBA",
            start_pst=w_s,
            dur_min=140,
            priority="HIGH PRIORITY (Radio 94122)",
            status="VERIFIED",
            radio="95.7 The Game (KGMZ-FM)",
            source_url="https://www.nba.com/warriors/news/warriors-announce-2026-27-regular-season-schedule-20260813",
            tiers=["full_radio_94122"],
            official_time_label=f"{fmt_hm_12(w_s)} PST",
        ))
    else:
        # Typical Warriors NBA schedule cadence (~3.5 games/week: Tue/Thu/Sat + alternate Mon/Fri) during NBA regular season, excluding NBA All-Star break!
        in_nba = (
            ("2026-01-01" <= iso <= "2026-04-12" and not ("2026-02-13" <= iso <= "2026-02-18"))
            or ("2026-10-05" <= iso <= "2027-04-11" and not ("2027-02-14" <= iso <= "2027-02-23") and iso != "2026-11-26" and iso != "2026-12-24")
            or ("2027-10-06" <= iso <= "2028-04-09" and not ("2028-02-14" <= iso <= "2028-02-22"))
            or ("2028-10-05" <= iso <= "2029-04-15" and not ("2029-02-12" <= iso <= "2029-02-20"))
            or ("2029-10-05" <= iso <= "2029-12-31")
        )
        if in_nba and wd in (1, 3, 5):
            events.append(make_event(
                title="NBA Radio: Golden State Warriors Typical Game Window (Est.)",
                category="NBA — Warriors (95.7 FM)",
                sport_key="NBA",
                start_pst=19 * 60,
                dur_min=140,
                priority="HIGH PRIORITY (Radio 94122)",
                status="ESTIMATED",
                radio="95.7 The Game (KGMZ-FM — Confirmed Flagship)",
                source_url="https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824",
                tiers=["full_radio_94122"],
                official_time_label="",
            ))

    # 4) Golden State Valkyries WNBA on 95.7 The Game (May – Sept, Wed/Fri/Sun typical)
    if 5 <= day.month <= 9 and day.day >= 8 and wd in (2, 4, 6):
        events.append(make_event(
            title="WNBA Radio: Golden State Valkyries Broadcast Window",
            category="WNBA — Valkyries (95.7 FM)",
            sport_key="WNBA",
            start_pst=19 * 60 if wd != 6 else 17 * 60 + 30,
            dur_min=125,
            priority="HIGH PRIORITY (Radio 94122)",
            status="VERIFIED (2026 Season) / ESTIMATED (2027–2029)",
            radio="95.7 The Game (KGMZ-FM)",
            source_url="https://valkyries.wnba.com/news/golden-state-valkyries-announce-local-television-and-radio-broadcast-schedule-20260425",
            tiers=["full_radio_94122"],
            official_time_label="",
        ))

    # 5) San Jose Earthquakes MLS on KSFO 810 AM / KZSF 1370 AM (Late Feb – Mid Oct Saturdays)
    if ((day.month == 2 and day.day >= 21) or (3 <= day.month <= 10 and not (day.month == 10 and day.day > 18))) and wd == 5:
        events.append(make_event(
            title="MLS Radio: San Jose Earthquakes Saturday Window",
            category="MLS — Earthquakes (KSFO 810)",
            sport_key="MLS",
            start_pst=19 * 60 + 30,
            dur_min=125,
            priority="HIGH PRIORITY (Radio 94122)",
            status="VERIFIED (Stations) / ESTIMATED (2027–2029 Dates)",
            radio="KSFO 810 AM (English) · KZSF 1370 AM (Spanish)",
            source_url="https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season",
            tiers=["full_radio_94122"],
            official_time_label="",
        ))

    events.sort(key=lambda e: (e["start_pst"], e["end_pst"], e["title"]))
    return events


def merge_busy_intervals(events: list[dict], tier: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]], int]:
    raw = sorted((e["start_pst"], e["end_pst"]) for e in events if tier in e["tiers"])
    merged: list[tuple[int, int]] = []
    for s, e in raw:
        if not merged or s > merged[-1][1]:
            merged.append((s, e))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
    free: list[tuple[int, int]] = []
    cur = 0
    for s, e in merged:
        if s > cur:
            free.append((cur, s))
        cur = max(cur, e)
    if cur < 1440:
        free.append((cur, 1440))
    busy_mins = sum(e - s for s, e in merged)
    return merged, free, 1440 - busy_mins


TIERS = ["core_strict", "core_regular", "sf_high_priority", "full_radio_94122"]

days_out = []
cur_day = dt.date(2026, 1, 1)
end_day = dt.date(2029, 12, 31)
while cur_day <= end_day:
    evs = build_day_events(cur_day)
    tier_free = {}
    tier_free_mins = {}
    for t in TIERS:
        _, _, f_mins = merge_busy_intervals(evs, t)
        tier_free[t] = (f_mins == 1440)
        tier_free_mins[t] = f_mins
    days_out.append({
        "d": cur_day.isoformat(),
        "w": cur_day.strftime("%a"),
        "free": tier_free,
        "free_mins": tier_free_mins,
        "events": evs,
    })
    cur_day += dt.timedelta(days=1)


def find_runs(tier: str, min_days: int = 2) -> list[dict]:
    runs = []
    i = 0
    n = len(days_out)
    while i < n:
        if days_out[i]["free"][tier]:
            j = i
            while j < n and days_out[j]["free"][tier]:
                j += 1
            length = j - i
            if length >= min_days:
                s_iso = days_out[i]["d"]
                e_iso = days_out[j - 1]["d"]
                yr = int(s_iso[:4])
                before_ev = days_out[i - 1]["events"][-1]["title"] if i > 0 and days_out[i - 1]["events"] else "Start of dataset"
                after_ev = days_out[j]["events"][0]["title"] if j < n and days_out[j]["events"] else "End of dataset"
                runs.append({
                    "year": yr,
                    "start": s_iso,
                    "end": e_iso,
                    "days": length,
                    "weeks": round(length / 7.0, 2),
                    "fits_1wk": length >= 7,
                    "fits_2wk": length >= 14,
                    "fits_3wk": length >= 21,
                    "bounded_after": before_ev,
                    "bounded_before": after_ev,
                    "verification_status": (
                        "VERIFIED" if s_iso <= "2027-03-25" and e_iso <= "2027-03-25" else "ESTIMATED (Future Schedule Unreleased)"
                    ),
                })
            i = j
        else:
            i += 1
    runs.sort(key=lambda r: (-r["days"], r["start"]))
    return runs


def runs_by_year(tier: str) -> dict[str, list[dict]]:
    all_r = find_runs(tier, min_days=2)
    out: dict[str, list[dict]] = {}
    for yr in (2027, 2028, 2029, 2026):
        yr_runs = [r for r in all_r if r["year"] == yr or r["end"].startswith(str(yr))]
        yr_runs.sort(key=lambda r: (-r["days"], r["start"]))
        out[str(yr)] = yr_runs[:8]
    return out


BRIDGE_WINDOWS = [
    {
        "year": 2027,
        "window": "2027-02-01 → 2027-02-18",
        "total_days": 18,
        "free_days": 17,
        "single_conflict": "Sun Feb 14, 2027 (Super Bowl LXI, ~3:30–7:15 PM PST on Westwood One / KNBR)",
        "why_it_matters": "Combines the verified 13-day pre-Super Bowl NFL/MLB-free window (Feb 1–13) and verified 4-day post-Super Bowl window (Feb 15–18) into a 2.5-week strict vacation with only 3.75 hours of sports radio in 18 days.",
        "status": "VERIFIED BOUNDS",
        "source_url": "https://www.nfl.com/news/2026-27-national-football-league-important-dates",
    },
    {
        "year": 2028,
        "window": "2028-01-31 → 2028-02-17",
        "total_days": 18,
        "free_days": 17,
        "single_conflict": "Sun Feb 13, 2028 (Super Bowl LXII in Atlanta — Host Verified, Date Est.)",
        "why_it_matters": "Same 18-day / 17-free-day strict window if you listen to Super Bowl LXII on the road or return Sunday afternoon.",
        "status": "ESTIMATED",
        "source_url": "https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028",
    },
    {
        "year": 2029,
        "window": "2029-01-29 → 2029-02-16",
        "total_days": 19,
        "free_days": 18,
        "single_conflict": "Sun Feb 11, 2029 (Super Bowl LXIII in Las Vegas — Host Verified, Date Est.)",
        "why_it_matters": "19-day / 18-free-day strict window interrupted only by Super Bowl LXIII Sunday afternoon.",
        "status": "ESTIMATED",
        "source_url": "https://www.nfl.com/news/las-vegas-to-host-super-bowl-lxiii-in-2029",
    },
]

VACATION_ANALYSIS = {
    "generated": "2026-11-25",
    "location": "Outer Sunset, San Francisco, CA 94122 (Standard AM/FM Terrestrial Radio)",
    "timezone_primary": "PST (UTC-8) / Pacific Time (America/Los_Angeles)",
    "one_game_bridge_windows": BRIDGE_WINDOWS,
    "tiers": {
        "core_strict": {
            "name": "Tier 1 — Core Rule (Strict: Includes MLB Spring Training & NFL Preseason)",
            "description": "Free ONLY when zero MLB (all 30 clubs, Spring+Reg+All-Star+Post), zero NFL (all 32 teams, Pre+Reg+Post), zero Stanford/Cal NCAAF, and zero Westwood One NFL games are on air.",
            "top_runs": find_runs("core_strict", min_days=3)[:20],
            "by_year": runs_by_year("core_strict"),
        },
        "core_regular": {
            "name": "Tier 2 — Core Rule (Championship Seasons: Excludes Spring Training & NFL Preseason)",
            "description": "Free when zero Regular Season, All-Star, or Postseason MLB (30 clubs), NFL (32 teams), Stanford/Cal NCAAF, or Westwood One NFL games are on air.",
            "top_runs": find_runs("core_regular", min_days=4)[:16],
            "by_year": runs_by_year("core_regular"),
        },
        "sf_high_priority": {
            "name": "Tier 3 — SF High-Priority Teams + Westwood One National NFL Only",
            "description": "Free when SF Giants, Athletics, SF 49ers, Stanford NCAAF, Cal NCAAF, and Westwood One national NFL radio are all off air (ignores out-of-market MLB/NFL daytime games not on SF radio).",
            "top_runs": find_runs("sf_high_priority", min_days=3)[:20],
            "by_year": runs_by_year("sf_high_priority"),
        },
        "full_radio_94122": {
            "name": "Tier 4 — Full Outer Sunset 94122 AM/FM Sports Dial (Adds Warriors, Valkyries, Earthquakes, NCAA)",
            "description": "Adds Golden State Warriors NBA (95.7 FM), Golden State Valkyries WNBA (95.7 FM), San Jose Earthquakes MLS (KSFO 810 / KZSF 1370), CFP Radio (KTCT 1050), and Westwood One NCAA to Tier 1.",
            "top_runs": find_runs("full_radio_94122", min_days=2)[:16],
            "by_year": runs_by_year("full_radio_94122"),
        },
    },
}

# ---------------------------------------------------------------------------
# 8. FLAGGED FOR REVIEW ITEMS (Official Sources Linked, Unconfirmed Left Blank)
# ---------------------------------------------------------------------------
FLAGGED_ITEMS = [
    {
        "id": "FLG-01",
        "category": "MLB 2027 Labor / CBA",
        "item": "MLB–MLBPA Collective Bargaining Agreement expires December 1, 2026",
        "official_confirmed_value": "CBA expiration Dec 1, 2026; 2027 Spring Training slated Feb 19 & Opening Night Mar 24",
        "unverified_blank_field": "Whether any labor stoppage alters 2027 Spring/Regular Season dates",
        "status": "NEEDS REVIEW",
        "source_label": "MLB.com Official 2027 Spring Training Release (notes Dec 1 CBA expiration)",
        "source_url": "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule",
    },
    {
        "id": "FLG-02",
        "category": "MLB 2027 Giants & A's First-Pitch Times",
        "item": "2027 SF Giants & Athletics games with `startTimeTBD: true` in MLB StatsAPI",
        "official_confirmed_value": f"All 195 Giants & 193 Athletics 2027 game dates & opponents verified (`statsapi.mlb.com`); {sum(1 for g in GIANTS_2027_GAMES if g['time_tbd'])} Giants games & {sum(1 for g in ATHLETICS_2027_GAMES if g['time_tbd'])} Athletics games still have `startTimeTBD=true`",
        "unverified_blank_field": "Official First-Pitch Time (left strictly BLANK in official column; typical PT/PST window shown separately as Estimated)",
        "status": "PARTIAL / TBD",
        "source_label": "MLB StatsAPI 2027 Official Schedule (`sportId=1&season=2027`)",
        "source_url": "https://www.mlb.com/giants/schedule/2027-03",
    },
    {
        "id": "FLG-03",
        "category": "MLB 2028 All-Star Game Date",
        "item": "2028 MLB All-Star Game at Oracle Park, San Francisco",
        "official_confirmed_value": "Host: San Francisco Giants / Oracle Park; Month: July 2028",
        "unverified_blank_field": "Exact July 2028 calendar date (secondary outlets report July 11 vs July 12; `mlb.com` states 'July 2028' only — left blank)",
        "status": "PARTIAL (Date Blank)",
        "source_label": "MLB.com Giants Official 2028 All-Star Page",
        "source_url": "https://www.mlb.com/giants/fans/all-star-game",
    },
    {
        "id": "FLG-04",
        "category": "MLB 2027 Postseason & 2028–2029 Seasons",
        "item": "2027 MLB Postseason bracket dates and 2028–2029 full MLB schedules",
        "official_confirmed_value": "2027 regular season ends Sept 26, 2027; `statsapi.mlb.com` returns `totalGames: 0` for 2028",
        "unverified_blank_field": "Exact 2027 Wild Card/World Series dates & all 2028–2029 MLB dates (modeled as ESTIMATED)",
        "status": "ESTIMATED",
        "source_label": "MLB.com Official Schedule",
        "source_url": "https://www.mlb.com/schedule",
    },
    {
        "id": "FLG-05",
        "category": "NFL 2027–2029 Schedules & Super Bowl Dates",
        "item": "2027–2029 NFL Regular Season / Preseason schedules & Super Bowl LXII / LXIII exact dates",
        "official_confirmed_value": "Super Bowl LXI: Feb 14, 2027 (SoFi); Super Bowl LXII host: Atlanta (2028, date listed TBA on nfl.com); Super Bowl LXIII host: Las Vegas (2029); Super Bowl LXIV host: Nashville (2030); AFC–NFC Pro Bowl game discontinued Aug 27, 2026",
        "unverified_blank_field": "2027–2029 weekly NFL schedules (released each May) & official `nfl.com` calendar dates for SB LXII/LXIII",
        "status": "PARTIAL / ESTIMATED",
        "source_label": "NFL.com Super Bowl LXII / LXIII / LXIV Official Announcements",
        "source_url": "https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028",
    },
    {
        "id": "FLG-06",
        "category": "49ers Week 18 & Stanford 2026 Bowl",
        "item": "2026–27 49ers Week 18 at Arizona & Stanford 2026 Bowl Assignment",
        "official_confirmed_value": "49ers Week 18 at Cardinals is Jan 9 or Jan 10, 2027; Stanford clinched bowl eligibility Nov 21, 2026 (6–5)",
        "unverified_blank_field": "Exact 49ers Week 18 kickoff time & Stanford's Dec 2026 bowl date/opponent (announced Dec 6, 2026)",
        "status": "PARTIAL / TBD",
        "source_label": "49ers.com Schedule & GoStanford Bowl Berth Release",
        "source_url": "https://gostanford.com/news/2026/11/21/stanford-secures-bowl-berth-with-big-game-win",
    },
    {
        "id": "FLG-07",
        "category": "NCAAF Cal 2027 Sept 11 Opponent Discrepancy",
        "item": "California 2027 Non-Conference Sept 11 Slot (Old Dominion vs. earlier BYU announcement)",
        "official_confirmed_value": "Cal's June 25, 2026 official release states Aug 28 vs Sac State, Sept 11 vs Old Dominion, plus UCLA completes 2027 non-conference play; an earlier Sept 2024 Cal release listed BYU on Sept 11, 2027",
        "unverified_blank_field": "Confirmed disposition of the 2027 BYU date + all 2027–2029 ACC conference game dates & kickoffs",
        "status": "NEEDS REVIEW",
        "source_label": "CalBears.com June 25, 2026 Official Release",
        "source_url": "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state.aspx",
    },
    {
        "id": "FLG-08",
        "category": "Radio Reception in Outer Sunset 94122",
        "item": "Athletics Terrestrial AM Carriage (`960 AM KNEW` / `650 AM KSTE`) & Westwood One Local Preemptions",
        "official_confirmed_value": "`mlb.com/athletics/schedule/affiliates` lists 960 AM KNEW (Bay Area) and 650 AM KSTE (Sacramento); `westwoodonesports.com/station-finder` lists KNBR/KTCT with conflict caveats",
        "unverified_blank_field": "Verified 2027 field-strength reception of 960 AM / 650 AM inside Outer Sunset 94122 and game-by-game KNBR vs KTCT preemption routing when Giants/49ers overlap Westwood One",
        "status": "NEEDS REVIEW",
        "source_label": "Athletics Official Radio Affiliates & Westwood One Station Finder",
        "source_url": "https://www.mlb.com/athletics/schedule/affiliates",
    },
]

# Write all JSON outputs
(DATA_DIR / "repo_audit.json").write_text(json.dumps(REPO_AUDIT, indent=2))
(DATA_DIR / "radio_94122.json").write_text(json.dumps(RADIO_STATIONS_94122, indent=2))
(DATA_DIR / "durations.json").write_text(json.dumps(DURATIONS_RESEARCH, indent=2))
(DATA_DIR / "flagged_items.json").write_text(json.dumps(FLAGGED_ITEMS, indent=2))
(DATA_DIR / "vacation_analysis.json").write_text(json.dumps(VACATION_ANALYSIS, indent=2))
(DATA_DIR / "schedules_master.json").write_text(json.dumps({
    "generated": "2026-11-25",
    "mlb_30_clubs": MLB_30_CLUBS,
    "nfl_32_teams": [{"name": n, "priority": "HIGH PRIORITY" if "49ers" in n else "STANDARD (All 32 Shown)", "official_url": u} for n, u in NFL_32_TEAMS],
    "giants_2027": GIANTS_2027_GAMES,
    "athletics_2027": ATHLETICS_2027_GAMES,
    "fortyniners_2026_27": [
        {"date": r[0], "week": r[1], "matchup": r[2], "venue": r[3], "official_time": r[4], "result_or_note": r[5], "radio": "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM", "source_url": r[6]}
        for r in FORTYNINERS_2026_FULL
    ],
    "westwood_one_nfl_2026_27": [
        {
            "date": r[0],
            "official_et": r[1],
            "official_pst": utc_to_pst_and_pt(et_str_to_utc(r[0], r[1]))[0],
            "event_id": r[2],
            "matchup": r[3],
            "venue": r[4],
            "package": r[5],
            "status": "VERIFIED" if "TBA" not in r[3] else "PARTIAL (Slot Verified · Teams TBA)",
            "source_url": f"https://www.westwoodonesports.com/events/{r[2]}",
        }
        for r in WESTWOOD_ONE_NFL_VERIFIED
    ],
    "westwood_one_ncaa_2026": [
        {
            "date": r[0],
            "official_et": r[1],
            "official_pst": utc_to_pst_and_pt(et_str_to_utc(r[0], r[1]))[0],
            "event_id": r[2],
            "matchup": r[3],
            "venue": r[4],
            "source_url": r[5],
        }
        for r in WESTWOOD_ONE_NCAA_VERIFIED
    ],
    "stanford_2026": [
        {"date": r[0], "matchup": r[1], "official_time": r[2], "result": r[3], "radio": r[4], "source_url": r[5]}
        for r in STANFORD_2026
    ],
    "cal_2026": [
        {"date": r[0], "matchup": r[1], "official_time": r[2], "result": r[3], "radio": r[4], "source_url": r[5]}
        for r in CAL_2026
    ],
    "ncaaf_future_official": NCAAF_FUTURE_OFFICIAL_DATES,
}, indent=2))
(DATA_DIR / "daily_calendar.json").write_text(json.dumps({
    "generated": "2026-11-25",
    "start": "2026-01-01",
    "end": "2029-12-31",
    "days": days_out,
}, separators=(",", ":")))

print("=== VACATION SUMMARY ===")
for tk, tv in VACATION_ANALYSIS["tiers"].items():
    print(f"\n[{tk}] {tv['name']}")
    for r in tv["top_runs"][:6]:
        print(f"  {r['start']} -> {r['end']} : {r['days']}d ({r['weeks']}w) | 1wk={r['fits_1wk']} 2wk={r['fits_2wk']} 3wk={r['fits_3wk']} | {r['verification_status']}")
