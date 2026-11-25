#!/usr/bin/env python3
"""
Build compiled JSON datasets for the FREE TIME VACATION dashboard from verified raw sources.
All timestamps are normalized to America/Los_Angeles (PST / PDT) using zoneinfo.
"""
import csv
import glob
import json
import os
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")
ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
OUT_DIR = os.path.join(ROOT, "assets", "data")
os.makedirs(OUT_DIR, exist_ok=True)

NFL_TEAMS = {
    "ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
    "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs", "LAC": "Los Angeles Chargers", "LAR": "Los Angeles Rams",
    "LV": "Las Vegas Raiders", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings",
    "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
    "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers",
    "SEA": "Seattle Seahawks", "SF": "San Francisco 49ers", "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans", "WAS": "Washington Commanders"
}

EXTRA_MLB_TEAMS = {
    "343": {"abbr": "NEU", "name": "Northeastern Huskies", "short": "Huskies", "tz": "America/New_York"},
    "105": {"abbr": "SAC", "name": "Sacramento River Cats", "short": "River Cats", "tz": "America/Los_Angeles"},
    "1960": {"abbr": "STP", "name": "St. Paul Saints", "short": "Saints", "tz": "America/Chicago"},
    "5434": {"abbr": "SUG", "name": "Sugar Land Space Cowboys", "short": "Space Cowboys", "tz": "America/Chicago"},
}


def load_mlb_teams():
    with open(os.path.join(DATA_DIR, "mlb_teams.json")) as f:
        teams = json.load(f)["teams"]
    teams.update(EXTRA_MLB_TEAMS)
    return teams


def tz_abbr_for_date(d_str):
    y, m, d = map(int, d_str.split("-"))
    dt = datetime(y, m, d, 12, 0, tzinfo=PT)
    return dt.tzname()  # "PST" or "PDT"


def estimate_mlb_tbd_start_pt(d_str, home_team_info, game_type="R"):
    """Estimate start minute in Pacific Time for an official TBD MLB game using standard home-park slots."""
    y, m, d = map(int, d_str.split("-"))
    dow = date(y, m, d).weekday()  # 0=Mon..6=Sun
    home_tz = ZoneInfo(home_team_info.get("tz", "America/New_York"))
    if game_type in ("S", "E"):
        # Spring training: FL (ET) 1:05 PM local, AZ (MST) 1:05 PM MST
        local_hr, local_mn = 13, 5
        if home_team_info.get("tz") in ("America/Los_Angeles", "America/Phoenix", "America/Denver"):
            home_tz = ZoneInfo("America/Phoenix")
        else:
            home_tz = ZoneInfo("America/New_York")
    elif game_type == "A":
        # All-Star Game: standard 8:00 PM ET / 5:00 PM PDT
        home_tz = ET
        local_hr, local_mn = 20, 0
    else:
        if dow == 6:  # Sunday day game
            local_hr, local_mn = 13, 10
        elif dow == 5:  # Saturday afternoon/early evening
            local_hr, local_mn = 16, 5
        elif dow == 3:  # Thursday getaway/day
            local_hr, local_mn = 13, 10
        else:
            # Standard local night game (Giants 6:45 PM, Cubs/BOS/CLE/TOR/LAD 7:05-7:10 PM)
            if home_team_info.get("abbr") == "SF":
                local_hr, local_mn = 18, 45
            else:
                local_hr, local_mn = 19, 10
    dt_local = datetime(y, m, d, local_hr, local_mn, tzinfo=home_tz)
    dt_pt = dt_local.astimezone(PT)
    return dt_pt.hour * 60 + dt_pt.minute, dt_pt.strftime("%-I:%M %p") + " " + dt_pt.tzname()


def fmt_min(m):
    m = max(0, min(1440, int(round(m))))
    if m == 1440:
        return "11:59 PM"
    h = m // 60
    mn = m % 60
    ap = "AM" if h < 12 else "PM"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12}:{mn:02d} {ap}"


def merge_intervals(intervals):
    if not intervals:
        return []
    iv = sorted((max(0, a), min(1440, b)) for a, b in intervals if b > a)
    merged = [list(iv[0])]
    for a, b in iv[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged]


def compute_free_windows(busy_intervals):
    merged = merge_intervals(busy_intervals)
    free = []
    cur = 0
    for a, b in merged:
        if a > cur:
            free.append((cur, a))
        cur = max(cur, b)
    if cur < 1440:
        free.append((cur, 1440))
    busy_min = sum(b - a for a, b in merged)
    free_min = 1440 - busy_min
    return free, merged, free_min, busy_min


def build_all_games():
    mlb_teams = load_mlb_teams()
    games = []

    # 1. NFL 2026 Weeks 12-18 (Verified from nfl.com)
    for fname in ("nfl_2026_w12_15.csv", "nfl_2026_w16_18.csv"):
        with open(os.path.join(DATA_DIR, fname)) as f:
            for row in csv.DictReader(f):
                d_str = row["date"]
                y, m, d = map(int, d_str.split("-"))
                hh, mm = map(int, row["time_et"].split(":"))
                dt_et = datetime(y, m, d, hh, mm, tzinfo=ET)
                dt_pt = dt_et.astimezone(PT)
                start_min = dt_pt.hour * 60 + dt_pt.minute
                dur = 192  # 3h 12m NFL regular season avg
                is_tbd = row["tbd"] == "1"
                away_code, home_code = row["away"], row["home"]
                away_name = NFL_TEAMS[away_code]
                home_name = NFL_TEAMS[home_code]
                hp = (away_code == "SF" or home_code == "SF")
                radio_parts = []
                if hp:
                    radio_parts.append("KNBR 680/104.5 & KSAN 107.7 FM (49ers)")
                if row["wwo"] == "1":
                    radio_parts.append("Westwood One Sports (KNBR/KSFO)")
                if not radio_parts:
                    radio_parts.append("NFL National/Team Radio (All-NFL Conflict)")
                t_label = dt_pt.strftime("%-I:%M %p") + " " + dt_pt.tzname()
                if is_tbd:
                    t_label = f"TBD (Est. {t_label})"
                games.append({
                    "id": f"nfl-2026-w{row['week']}-{away_code.lower()}-{home_code.lower()}",
                    "date": dt_pt.strftime("%Y-%m-%d"),
                    "league": "NFL",
                    "phase": f"Regular Season (Wk {row['week']})",
                    "away": away_code,
                    "home": home_code,
                    "matchup": f"{away_name} at {home_name}",
                    "short_matchup": f"{away_code} @ {home_code}",
                    "start_min": start_min,
                    "end_min": min(1440, start_min + dur),
                    "duration_min": dur,
                    "halftime_min": 13,
                    "time_display": t_label,
                    "tbd": is_tbd,
                    "status": "Verified (Flex TBD)" if is_tbd else "Verified",
                    "high_priority": hp,
                    "priority_tag": "49ers" if hp else ("Westwood One" if row["wwo"] == "1" else ""),
                    "radio": "; ".join(radio_parts),
                    "network": row["network"],
                    "note": row["note"],
                    "source_url": f"https://www.nfl.com/games/{row['slug']}"
                })

    # 2. MLB 2027 Spring Training + Exhibition + All-Star Game (Verified from statsapi.mlb.com)
    with open(os.path.join(DATA_DIR, "mlb_2027_spring.csv")) as f:
        for row in csv.DictReader(f):
            d_str = row["date"]
            gtype = row["gameType"]
            away_id, home_id = row["away"], row["home"]
            away_t = mlb_teams[away_id]
            home_t = mlb_teams[home_id]
            is_tbd = row["tbd"] == "1"
            if gtype == "A":
                phase = "All-Star Game"
                dur = 185
            elif gtype == "E":
                phase = "Exhibition"
                dur = 160
            else:
                phase = "Spring Training"
                dur = 160
            if is_tbd:
                start_min, est_lbl = estimate_mlb_tbd_start_pt(d_str, home_t, gtype)
                t_label = f"TBD (Est. {est_lbl})"
                game_date_pt = d_str
            else:
                dt_utc = datetime.fromisoformat(row["gameDate"].replace("Z", "+00:00"))
                dt_pt = dt_utc.astimezone(PT)
                start_min = dt_pt.hour * 60 + dt_pt.minute
                t_label = dt_pt.strftime("%-I:%M %p") + " " + dt_pt.tzname()
                game_date_pt = dt_pt.strftime("%Y-%m-%d")
            hp = (away_id in ("137", "133") or home_id in ("137", "133"))
            ptag = []
            if "137" in (away_id, home_id):
                ptag.append("Giants")
            if "133" in (away_id, home_id):
                ptag.append("Athletics")
            radio_parts = []
            if "137" in (away_id, home_id):
                radio_parts.append("KNBR 680/104.5 & KSFN 1510 AM (Giants)")
            if "133" in (away_id, home_id):
                radio_parts.append("KNEW 960 AM / KSTE 650 AM (Athletics)")
            if gtype == "A":
                radio_parts.append("ESPN Radio (KTCT 1050 AM)")
            if not radio_parts:
                radio_parts.append("MLB Team Radio (All-MLB Conflict)")
            games.append({
                "id": f"mlb-2027-{row['gamePk']}",
                "date": game_date_pt,
                "league": "MLB",
                "phase": phase,
                "away": away_t["abbr"],
                "home": home_t["abbr"],
                "matchup": f"{away_t['name']} at {home_t['name']}",
                "short_matchup": f"{away_t['abbr']} @ {home_t['abbr']}",
                "start_min": start_min,
                "end_min": min(1440, start_min + dur),
                "duration_min": dur,
                "halftime_min": 0,
                "time_display": t_label,
                "tbd": is_tbd,
                "status": "Verified (Time TBD)" if is_tbd else "Verified",
                "high_priority": hp or (gtype == "A"),
                "priority_tag": " & ".join(ptag) if ptag else ("All-Star" if gtype == "A" else ""),
                "radio": "; ".join(radio_parts),
                "network": "MLB",
                "note": row.get("note", ""),
                "source_url": f"https://www.mlb.com/gameday/{row['gamePk']}"
            })

    # 3. MLB 2027 Regular Season (ALL 2,430 verified games from statsapi.mlb.com)
    for fpath in sorted(glob.glob(os.path.join(DATA_DIR, "mlb_2027_0*.csv"))):
        with open(fpath) as f:
            for row in csv.DictReader(f):
                d_str = row["date"]
                away_id, home_id = row["away"], row["home"]
                away_t = mlb_teams[away_id]
                home_t = mlb_teams[home_id]
                is_tbd = row["tbd"] == "1"
                dur = 165  # 2h 45m avg (2h 42m 9-inn avg)
                if is_tbd:
                    start_min, est_lbl = estimate_mlb_tbd_start_pt(d_str, home_t, "R")
                    t_label = f"TBD (Est. {est_lbl})"
                    game_date_pt = d_str
                else:
                    dt_utc = datetime.fromisoformat(row["gameDate"].replace("Z", "+00:00"))
                    dt_pt = dt_utc.astimezone(PT)
                    start_min = dt_pt.hour * 60 + dt_pt.minute
                    t_label = dt_pt.strftime("%-I:%M %p") + " " + dt_pt.tzname()
                    game_date_pt = dt_pt.strftime("%Y-%m-%d")
                hp = (away_id in ("137", "133") or home_id in ("137", "133"))
                ptag = []
                if "137" in (away_id, home_id):
                    ptag.append("Giants")
                if "133" in (away_id, home_id):
                    ptag.append("Athletics")
                note = row.get("note", "") or ""
                is_special = any(k in note for k in ("Field of Dreams", "Little League", "Opening Night"))
                phase = "Special Game" if ("Field of Dreams" in note or "Little League" in note) else "Regular Season"
                radio_parts = []
                if "137" in (away_id, home_id):
                    radio_parts.append("KNBR 680/104.5 & KSFN 1510 AM (Giants)")
                if "133" in (away_id, home_id):
                    radio_parts.append("KNEW 960 AM / KSTE 650 AM (Athletics)")
                if not radio_parts:
                    radio_parts.append("MLB Team Radio (All-MLB Conflict)")
                games.append({
                    "id": f"mlb-2027-{row['gamePk']}",
                    "date": game_date_pt,
                    "league": "MLB",
                    "phase": phase,
                    "away": away_t["abbr"],
                    "home": home_t["abbr"],
                    "matchup": f"{away_t['name']} at {home_t['name']}",
                    "short_matchup": f"{away_t['abbr']} @ {home_t['abbr']}",
                    "start_min": start_min,
                    "end_min": min(1440, start_min + dur),
                    "duration_min": dur,
                    "halftime_min": 0,
                    "time_display": t_label,
                    "tbd": is_tbd,
                    "status": "Verified (Time TBD)" if is_tbd else "Verified",
                    "high_priority": hp or is_special,
                    "priority_tag": " & ".join(ptag) if ptag else ("Special" if is_special else ""),
                    "radio": "; ".join(radio_parts),
                    "network": "MLB",
                    "note": note,
                    "source_url": f"https://www.mlb.com/gameday/{row['gamePk']}"
                })

    # 4. Other Verified & Estimated Events (NCAAF Stanford/Cal, WWO NCAAF, NFL 2026-27 Playoffs, Super Bowls, HR Derby)
    with open(os.path.join(DATA_DIR, "other_verified_events.json")) as f:
        other = json.load(f)
    for ev in other["events"]:
        hh, mm = map(int, ev["time_pt"].split(":"))
        start_min = hh * 60 + mm
        tz_lbl = tz_abbr_for_date(ev["date"])
        dt_disp = fmt_min(start_min) + " " + tz_lbl
        if ev["tbd"]:
            dt_disp = f"TBD (Est. {dt_disp})"
        ptag = ""
        if "Stanford" in ev["matchup"]:
            ptag = "Stanford"
        elif "California" in ev["matchup"]:
            ptag = "Cal"
        elif "Super Bowl" in ev["matchup"]:
            ptag = "Super Bowl"
        games.append({
            "id": ev["id"],
            "date": ev["date"],
            "league": ev["league"],
            "phase": ev["phase"],
            "away": "",
            "home": "",
            "matchup": ev["matchup"],
            "short_matchup": ev["matchup"],
            "start_min": start_min,
            "end_min": min(1440, start_min + ev["duration_min"]),
            "duration_min": ev["duration_min"],
            "halftime_min": ev["halftime_min"],
            "time_display": dt_disp,
            "tbd": ev["tbd"],
            "status": ev["status"],
            "high_priority": ev["high_priority"],
            "priority_tag": ptag,
            "radio": ev["radio"],
            "network": ev["league"],
            "note": ev["note"],
            "source_url": ev["source_url"]
        })

    # 5. Add clearly-labeled Estimated Calendar Blocks for Oct–Dec 2027 (unreleased MLB Postseason + 2027 NFL Regular Season + Stanford/Cal 2027 NCAAF)
    # So clicking days in Oct–Dec 2027 in the scoreboard shows honest "Estimated (Official Schedule Unreleased)" alerts instead of falsely showing "Free"!
    cur = date(2027, 9, 28)
    end_2027 = date(2027, 12, 31)
    while cur <= end_2027:
        d_str = cur.isoformat()
        dow = cur.weekday()  # 0=Mon..6=Sun
        tz_lbl = tz_abbr_for_date(d_str)
        # MLB 2027 Postseason (Est. Sep 28 – Oct 30, 2027)
        if date(2027, 9, 28) <= cur <= date(2027, 10, 30):
            start_m = 14 * 60 if cur <= date(2027, 10, 9) else 17 * 60
            games.append({
                "id": f"est-mlb-post-{d_str}",
                "date": d_str,
                "league": "MLB",
                "phase": "Postseason (Estimated)",
                "away": "", "home": "",
                "matchup": "2027 MLB Postseason Window (Schedule Unreleased — Est.)",
                "short_matchup": "MLB Postseason (Est.)",
                "start_min": start_m,
                "end_min": start_m + 185,
                "duration_min": 185,
                "halftime_min": 0,
                "time_display": f"Est. {fmt_min(start_m)} {tz_lbl}",
                "tbd": True,
                "status": "Estimated (Schedule Unreleased)",
                "high_priority": False,
                "priority_tag": "Estimated",
                "radio": "ESPN Radio (KTCT 1050 AM) / Giants or A's if qualified",
                "network": "MLB Postseason",
                "note": "Official 2027 MLB Postseason dates & matchups release late summer 2027.",
                "source_url": "https://www.mlb.com/schedule/2027-09-26"
            })
        # NFL 2027 Regular Season (Est. Thu Sep 9, 2027 – Sun Jan 9, 2028) — Thu/Sun/Mon + Thanksgiving/Christmas/Late-Dec Sat
        if cur >= date(2027, 9, 9):
            is_thanksgiving = (cur == date(2027, 11, 25))
            is_xmas = (cur == date(2027, 12, 25))
            if dow == 3:  # Thursday
                slots = [(9 * 60 + 30, "Thanksgiving Early (Est.)"), (13 * 60 + 30, "Thanksgiving Late (Est.)"), (17 * 60 + 20, "Thanksgiving Night (Est.)")] if is_thanksgiving else [(17 * 60 + 15, "Thursday Night Football (Est.)")]
            elif dow == 6:  # Sunday
                slots = [(10 * 60, "NFL Sunday Early Window (Est.)"), (13 * 60 + 25, "NFL Sunday Late Window (Est.)"), (17 * 60 + 20, "Sunday Night Football (Est.)")]
            elif dow == 0:  # Monday
                slots = [(17 * 60 + 15, "Monday Night Football (Est.)")]
            elif dow == 5 and (cur >= date(2027, 12, 18) or is_xmas):  # Late-Dec Sat / Christmas
                slots = [(13 * 60 + 30, "NFL Saturday/Holiday Early (Est.)"), (17 * 60, "NFL Saturday/Holiday Late (Est.)")]
            else:
                slots = []
            for idx, (sm, lbl) in enumerate(slots):
                games.append({
                    "id": f"est-nfl-2027-{d_str}-{idx}",
                    "date": d_str,
                    "league": "NFL",
                    "phase": "Regular Season (Estimated)",
                    "away": "", "home": "",
                    "matchup": f"2027 NFL {lbl} — Official Schedule Releases May 2027",
                    "short_matchup": f"NFL {lbl}",
                    "start_min": sm,
                    "end_min": min(1440, sm + 192),
                    "duration_min": 192,
                    "halftime_min": 13,
                    "time_display": f"Est. {fmt_min(sm)} {tz_lbl}",
                    "tbd": True,
                    "status": "Estimated (Schedule Unreleased)",
                    "high_priority": (dow == 6),
                    "priority_tag": "Estimated (Incl. 49ers/WWO)",
                    "radio": "KNBR 680/104.5, KSAN 107.7 FM & Westwood One Sports",
                    "network": "NFL",
                    "note": "Official 2027 NFL schedule releases May 2027; times estimated from standard NFL windows.",
                    "source_url": "https://www.nfl.com/schedules/"
                })
        # Stanford & Cal 2027 NCAAF Saturdays (Est. Sep 4 – Nov 27, 2027)
        if date(2027, 9, 4) <= cur <= date(2027, 11, 27) and dow == 5:
            games.append({
                "id": f"est-ncaaf-2027-{d_str}",
                "date": d_str,
                "league": "NCAAF",
                "phase": "Regular Season (Estimated)",
                "away": "", "home": "",
                "matchup": "2027 Stanford & Cal ACC Football Saturday Window (Dates Release Jan 2027)",
                "short_matchup": "Stanford & Cal NCAAF (Est.)",
                "start_min": 12 * 60 + 30,
                "end_min": 19 * 60 + 30,
                "duration_min": 205,
                "halftime_min": 20,
                "time_display": f"Est. 12:30 PM – 7:30 PM {tz_lbl}",
                "tbd": True,
                "status": "Estimated (ACC Schedule Unreleased)",
                "high_priority": True,
                "priority_tag": "Stanford & Cal (Est.)",
                "radio": "KTCT 1050 AM (Stanford) & KSFO 810 AM (Cal)",
                "network": "ACC",
                "note": "Exact 2027 ACC football dates release Jan 2027; kickoff times announced 6–12 days prior.",
                "source_url": "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state.aspx"
            })
        cur += timedelta(days=1)

    # Also add Aug 5 - Sep 27 2027 estimated NFL Preseason & NFL Weeks 1-3 + NCAAF Sep 4-25 Saturdays!
    cur = date(2027, 8, 5)
    while cur <= date(2027, 9, 27):
        d_str = cur.isoformat()
        dow = cur.weekday()
        tz_lbl = tz_abbr_for_date(d_str)
        if date(2027, 8, 5) <= cur <= date(2027, 8, 29) and dow in (3, 4, 5, 6):
            # NFL Preseason Thu-Sun
            if cur == date(2027, 8, 5) or cur >= date(2027, 8, 12):
                sm = 17 * 60 if dow in (3, 4) else 13 * 60
                lbl = "Hall of Fame Game (Est.)" if cur == date(2027, 8, 5) else "NFL Preseason Slate (Est.)"
                games.append({
                    "id": f"est-nfl-pre2027-{d_str}",
                    "date": d_str,
                    "league": "NFL",
                    "phase": "Preseason (Estimated)",
                    "away": "", "home": "",
                    "matchup": f"2027 NFL {lbl} — Official Schedule Releases May 2027",
                    "short_matchup": f"NFL {lbl}",
                    "start_min": sm,
                    "end_min": min(1440, sm + 190),
                    "duration_min": 190,
                    "halftime_min": 13,
                    "time_display": f"Est. {fmt_min(sm)} {tz_lbl}",
                    "tbd": True,
                    "status": "Estimated (Schedule Unreleased)",
                    "high_priority": False,
                    "priority_tag": "Estimated Preseason",
                    "radio": "KNBR/KSAN (49ers preseason) & NFL Radio",
                    "network": "NFL",
                    "note": "Official 2027 NFL Preseason dates release May 2027.",
                    "source_url": "https://www.nfl.com/schedules/"
                })
        if cur >= date(2027, 9, 9):
            slots = []
            if dow == 3:
                slots = [(17 * 60 + 15, "Thursday Night Football (Est.)")]
            elif dow == 6:
                slots = [(10 * 60, "NFL Sunday Early Window (Est.)"), (13 * 60 + 25, "NFL Sunday Late Window (Est.)"), (17 * 60 + 20, "Sunday Night Football (Est.)")]
            elif dow == 0:
                slots = [(17 * 60 + 15, "Monday Night Football (Est.)")]
            for idx, (sm, lbl) in enumerate(slots):
                games.append({
                    "id": f"est-nfl-2027-early-{d_str}-{idx}",
                    "date": d_str,
                    "league": "NFL",
                    "phase": "Regular Season (Estimated)",
                    "away": "", "home": "",
                    "matchup": f"2027 NFL {lbl} — Official Schedule Releases May 2027",
                    "short_matchup": f"NFL {lbl}",
                    "start_min": sm,
                    "end_min": min(1440, sm + 192),
                    "duration_min": 192,
                    "halftime_min": 13,
                    "time_display": f"Est. {fmt_min(sm)} {tz_lbl}",
                    "tbd": True,
                    "status": "Estimated (Schedule Unreleased)",
                    "high_priority": (dow == 6),
                    "priority_tag": "Estimated (Incl. 49ers/WWO)",
                    "radio": "KNBR 680/104.5, KSAN 107.7 FM & Westwood One Sports",
                    "network": "NFL",
                    "note": "Official 2027 NFL schedule releases May 2027.",
                    "source_url": "https://www.nfl.com/schedules/"
                })
        if date(2027, 9, 4) <= cur <= date(2027, 9, 27) and dow == 5:
            games.append({
                "id": f"est-ncaaf-2027-early-{d_str}",
                "date": d_str,
                "league": "NCAAF",
                "phase": "Regular Season (Estimated)",
                "away": "", "home": "",
                "matchup": "2027 Stanford & Cal Football Saturday Window (Dates Release Jan 2027)",
                "short_matchup": "Stanford & Cal NCAAF (Est.)",
                "start_min": 12 * 60 + 30,
                "end_min": 19 * 60 + 30,
                "duration_min": 205,
                "halftime_min": 20,
                "time_display": f"Est. 12:30 PM – 7:30 PM {tz_lbl}",
                "tbd": True,
                "status": "Estimated (Schedule Unreleased)",
                "high_priority": True,
                "priority_tag": "Stanford & Cal (Est.)",
                "radio": "KTCT 1050 AM (Stanford) & KSFO 810 AM (Cal)",
                "network": "ACC",
                "note": "Exact 2027 ACC football dates release Jan 2027.",
                "source_url": "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state.aspx"
            })
        cur += timedelta(days=1)

    games.sort(key=lambda g: (g["date"], g["start_min"], g["league"], g["matchup"]))
    return games, other


def compute_daily_calendar(games, start_d, end_d):
    by_date = defaultdict(list)
    for g in games:
        by_date[g["date"]].append(g)

    days = {}
    cur = start_d
    while cur <= end_d:
        d_str = cur.isoformat()
        tz_lbl = tz_abbr_for_date(d_str)
        day_games = by_date.get(d_str, [])

        # Strict mode (all games incl. Spring Training / Preseason)
        all_busy = [(g["start_min"], g["end_min"]) for g in day_games]
        free_all, busy_all, free_min_all, busy_min_all = compute_free_windows(all_busy)

        # Regular + Postseason only (excludes Spring Training, Exhibition, Preseason)
        reg_games = [g for g in day_games if not any(k in g["phase"] for k in ("Spring Training", "Exhibition", "Preseason"))]
        reg_busy = [(g["start_min"], g["end_min"]) for g in reg_games]
        free_reg, busy_reg, free_min_reg, busy_min_reg = compute_free_windows(reg_busy)

        # High-priority local teams only (Giants, Athletics, 49ers, Stanford, Cal, Super Bowl)
        hp_games = [g for g in day_games if g["high_priority"]]
        hp_busy = [(g["start_min"], g["end_min"]) for g in hp_games]
        free_hp, busy_hp, free_min_hp, busy_min_hp = compute_free_windows(hp_busy)

        days[d_str] = {
            "date": d_str,
            "dow": cur.strftime("%a"),
            "tz": tz_lbl,
            "total_games": len(day_games),
            "reg_games": len(reg_games),
            "hp_games": len(hp_games),
            "tbd_games": sum(1 for g in day_games if g["tbd"]),
            "is_free_strict": len(day_games) == 0,
            "is_free_reg": len(reg_games) == 0,
            "is_free_hp": len(hp_games) == 0,
            "free_min_strict": free_min_all,
            "busy_min_strict": busy_min_all,
            "free_windows_strict": [[fmt_min(a), fmt_min(b), b - a] for a, b in free_all],
            "busy_windows_strict": [[fmt_min(a), fmt_min(b), b - a] for a, b in busy_all],
            "free_min_reg": free_min_reg,
            "free_windows_reg": [[fmt_min(a), fmt_min(b), b - a] for a, b in free_reg],
            "free_min_hp": free_min_hp,
            "free_windows_hp": [[fmt_min(a), fmt_min(b), b - a] for a, b in free_hp],
            "leagues": sorted(set(g["league"] for g in day_games)),
            "has_estimated": any("Estimated" in g["status"] for g in day_games),
        }
        cur += timedelta(days=1)
    return days, by_date


def find_free_streaks(days_dict, start_d, end_d, key="is_free_strict", min_len=3):
    streaks = []
    run_start = None
    run_len = 0
    cur = start_d
    while cur <= end_d:
        d_str = cur.isoformat()
        if days_dict[d_str][key]:
            if run_start is None:
                run_start = cur
            run_len += 1
        else:
            if run_len >= min_len:
                streaks.append({
                    "start": run_start.isoformat(),
                    "end": (cur - timedelta(days=1)).isoformat(),
                    "days": run_len
                })
            run_start = None
            run_len = 0
        cur += timedelta(days=1)
    if run_len >= min_len:
        streaks.append({
            "start": run_start.isoformat(),
            "end": end_d.isoformat(),
            "days": run_len
        })
    return streaks


def build_vacation_windows(days):
    """Build verified 2027 + projected 2028–2029 vacation window analysis."""
    # Exact streaks from verified 2026-11-25..2027-12-31 daily dataset
    streaks_2026_strict = find_free_streaks(days, date(2026, 11, 25), date(2026, 12, 31), "is_free_strict", min_len=2)
    streaks_2027_strict = find_free_streaks(days, date(2027, 1, 1), date(2027, 12, 31), "is_free_strict", min_len=3)
    streaks_2027_reg = find_free_streaks(days, date(2027, 1, 1), date(2027, 12, 31), "is_free_reg", min_len=3)

    return {
        "verified_date": "2026-11-25",
        "headline_finding": {
            "strict_mode_summary": "With MLB Spring Training & NFL Preseason included, there is NO 2-week (14+ day) or 3-week (21+ day) zero-sports window in 2027, 2028, or 2029 — HOWEVER, because the NFL officially discontinued the Pro Bowl game beginning 2026–27, there IS a 13-day (1-week+) zero-game stretch every early February (Feb 1–13, 2027; est. Jan 31–Feb 12, 2028; est. Jan 29–Feb 10, 2029), plus a 4-day post-Super Bowl gap (Feb 15–18, 2027) before Spring Training opens Feb 19!",
            "regular_season_mode_summary": "Excluding Spring Training & Preseason exhibitions, a massive 5-to-6+ week completely zero-sports window opens EVERY year immediately after the Super Bowl: 37 consecutive days in 2027 (Mon Feb 15 – Tue Mar 23, VERIFIED), ~45 consecutive days in 2028 (Mon Feb 14 – Wed Mar 29, SB LXII verified / MLB est.), and ~45 consecutive days in 2029 (Mon Feb 12 – Wed Mar 28, est.) — ideal for 1-week, 2-week, or 3-week vacations!",
            "lockout_wildcard": "MLB's CBA expires Dec 1, 2026. If a lockout delays 2027 Spring Training beyond Feb 19, 2027, the strict-mode Feb–Mar 2027 window could expand into a multi-week zero-sports stretch."
        },
        "streaks_late_2026_strict": streaks_2026_strict,
        "streaks_2027_strict": streaks_2027_strict,
        "streaks_2027_regular_postseason": streaks_2027_reg,
        "multi_year_windows": [
            {
                "year": 2027,
                "window_name": "2027 Pre-Super Bowl Gap (Pro Bowl Discontinued)",
                "start_date": "2027-02-01",
                "end_date": "2027-02-13",
                "days": 13,
                "mode": "Both Strict & Regular/Postseason",
                "fits_1wk": True,
                "fits_2wk": False,
                "fits_3wk": False,
                "status": "Verified Dates (Flagged: Check LA Flag Showcase)",
                "bookends": "After Conf Championships (Sun Jan 31) → Before Super Bowl LXI (Sun Feb 14)",
                "notes": "NFL officially eliminated the AFC-NFC Pro Bowl game starting 2026–27 (Aug 27, 2026 release). Zero MLB or NCAAF games.",
                "source_url": "https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested"
            },
            {
                "year": 2027,
                "window_name": "2027 Post-Super Bowl Strict Gap (Before Spring Training)",
                "start_date": "2027-02-15",
                "end_date": "2027-02-18",
                "days": 4,
                "mode": "Strict (Includes Spring Training)",
                "fits_1wk": False,
                "fits_2wk": False,
                "fits_3wk": False,
                "status": "Verified",
                "bookends": "After Super Bowl LXI (Sun Feb 14) → Before MLB Spring Training Opener (Fri Feb 19)",
                "notes": "Longest post-Super Bowl strict gap in 2027 unless MLB CBA lockout delays Feb 19 Spring Training.",
                "source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&gameType=S&startDate=2027-02-19&endDate=2027-02-19"
            },
            {
                "year": 2027,
                "window_name": "2027 Prime Multi-Week Window (Regular + Postseason Only)",
                "start_date": "2027-02-15",
                "end_date": "2027-03-23",
                "days": 37,
                "mode": "Regular Season + Postseason (Excl. Spring Training)",
                "fits_1wk": True,
                "fits_2wk": True,
                "fits_3wk": True,
                "status": "Verified",
                "bookends": "After Super Bowl LXI (Sun Feb 14) → Before MLB Opening Night BOS@SEA (Wed Mar 24)",
                "notes": "BEST 2027 VACATION WINDOW! 5 weeks + 2 days with ZERO regular-season or postseason NFL, MLB, or NCAAF games. (Spring Training exhibitions occur Feb 19 – Mar 23.)",
                "source_url": "https://www.mlb.com/gameday/852583"
            },
            {
                "year": 2027,
                "window_name": "2027 MLB All-Star Break Gap (Mid-Summer Mini-Break)",
                "start_date": "2027-07-14",
                "end_date": "2027-07-14",
                "days": 1,
                "mode": "Both Strict & Regular/Postseason",
                "fits_1wk": False,
                "fits_2wk": False,
                "fits_3wk": False,
                "status": "Verified",
                "bookends": "After 97th All-Star Game Wrigley Field (Tue Jul 13) → Before ATL@BOS (Thu Jul 15)",
                "notes": "Only 1 completely game-free day in all of summer 2027 (Wed Jul 14; Mon Jul 12 has HR Derby; Thu Jul 15 has 1 MLB game ATL@BOS).",
                "source_url": "https://www.mlb.com/gameday/853074"
            },
            {
                "year": 2028,
                "window_name": "2028 Pre-Super Bowl LXII Gap (No Pro Bowl Game)",
                "start_date": "2028-01-31",
                "end_date": "2028-02-12",
                "days": 13,
                "mode": "Both Strict & Regular/Postseason",
                "fits_1wk": True,
                "fits_2wk": False,
                "fits_3wk": False,
                "status": "Estimated (SB LXII Date Verified)",
                "bookends": "After est. Conf Championships (Sun Jan 30) → Before CONFIRMED Super Bowl LXII Atlanta (Sun Feb 13, 2028)",
                "notes": "13-day stretch assuming discontinued Pro Bowl game format continues.",
                "source_url": "https://www.nfl.com/super-bowl/event-info/"
            },
            {
                "year": 2028,
                "window_name": "2028 Post-Super Bowl LXII Strict Gap (Before Spring Training)",
                "start_date": "2028-02-14",
                "end_date": "2028-02-18",
                "days": 5,
                "mode": "Strict (Includes Spring Training)",
                "fits_1wk": False,
                "fits_2wk": False,
                "fits_3wk": False,
                "status": "Estimated (SB LXII Date Verified; MLB 2028 Unreleased)",
                "bookends": "After CONFIRMED Super Bowl LXII (Sun Feb 13, 2028) → Before est. 2028 Spring Training (~Sat Feb 19, 2028)",
                "notes": "2028 MLB schedule releases ~July 2027; exact Spring Training start TBD.",
                "source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028"
            },
            {
                "year": 2028,
                "window_name": "2028 Prime Multi-Week Window (Regular + Postseason Only)",
                "start_date": "2028-02-14",
                "end_date": "2028-03-29",
                "days": 45,
                "mode": "Regular Season + Postseason (Excl. Spring Training)",
                "fits_1wk": True,
                "fits_2wk": True,
                "fits_3wk": True,
                "status": "Estimated (SB LXII Verified; MLB 2028 Unreleased)",
                "bookends": "After CONFIRMED Super Bowl LXII (Sun Feb 13, 2028) → Before est. 2028 MLB Opening Day (~Thu Mar 30, 2028)",
                "notes": "BEST 2028 VACATION WINDOW! ~6+ weeks free of all regular-season & postseason MLB/NFL/NCAAF games (2028 is a leap year with Feb 29!).",
                "source_url": "https://www.nfl.com/super-bowl/event-info/"
            },
            {
                "year": 2029,
                "window_name": "2029 Pre-Super Bowl LXIII Gap (No Pro Bowl Game)",
                "start_date": "2029-01-29",
                "end_date": "2029-02-10",
                "days": 13,
                "mode": "Both Strict & Regular/Postseason",
                "fits_1wk": True,
                "fits_2wk": False,
                "fits_3wk": False,
                "status": "Estimated (Host Confirmed; Subject to 18-Game Review)",
                "bookends": "After est. Conf Championships (Sun Jan 28) → Before proj. Super Bowl LXIII Las Vegas (Sun Feb 11, 2029)",
                "notes": "Shifts one week later if NFL expands to an 18-game season prior to 2028.",
                "source_url": "https://www.nfl.com/super-bowl/event-info/"
            },
            {
                "year": 2029,
                "window_name": "2029 Post-Super Bowl LXIII Strict Gap (Before Spring Training)",
                "start_date": "2029-02-12",
                "end_date": "2029-02-16",
                "days": 5,
                "mode": "Strict (Includes Spring Training)",
                "fits_1wk": False,
                "fits_2wk": False,
                "fits_3wk": False,
                "status": "Estimated",
                "bookends": "After proj. Super Bowl LXIII (Sun Feb 11, 2029) → Before est. 2029 Spring Training (~Sat Feb 17, 2029)",
                "notes": "Estimated from standard NFL 17-game calendar and MLB mid-Feb Spring Training start.",
                "source_url": "https://www.nfl.com/super-bowl/event-info/"
            },
            {
                "year": 2029,
                "window_name": "2029 Prime Multi-Week Window (Regular + Postseason Only)",
                "start_date": "2029-02-12",
                "end_date": "2029-03-28",
                "days": 45,
                "mode": "Regular Season + Postseason (Excl. Spring Training)",
                "fits_1wk": True,
                "fits_2wk": True,
                "fits_3wk": True,
                "status": "Estimated",
                "bookends": "After proj. Super Bowl LXIII (Sun Feb 11, 2029) → Before est. 2029 MLB Opening Day (~Thu Mar 29, 2029)",
                "notes": "BEST 2029 VACATION WINDOW! ~6+ weeks free of all regular-season & postseason MLB/NFL/NCAAF games.",
                "source_url": "https://www.nfl.com/super-bowl/event-info/"
            }
        ]
    }


def main():
    games, other = build_all_games()
    start_d = date(2026, 11, 25)
    end_d = date(2027, 12, 31)
    days, by_date = compute_daily_calendar(games, start_d, end_d)
    vacations = build_vacation_windows(days)

    with open(os.path.join(DATA_DIR, "bay_area_radio.json")) as f:
        radio = json.load(f)
    with open(os.path.join(DATA_DIR, "flagged_review.json")) as f:
        flagged = json.load(f)

    # Split games by month (YYYY-MM) so the browser scoreboard loads ONLY the needed month instantaneously!
    months_dir = os.path.join(OUT_DIR, "months")
    os.makedirs(months_dir, exist_ok=True)
    by_month = defaultdict(list)
    for g in games:
        by_month[g["date"][:7]].append(g)
    for ym, glist in sorted(by_month.items()):
        with open(os.path.join(months_dir, f"{ym}.json"), "w") as f:
            json.dump(glist, f, separators=(",", ":"))

    # Write compact daily summary index (Nov 25, 2026 – Dec 31, 2027 = 402 days)
    with open(os.path.join(OUT_DIR, "daily_summary.json"), "w") as f:
        json.dump(days, f, separators=(",", ":"))

    # Write high-priority & key schedules bundle (all NFL 2026 remaining + all 2027 Giants/A's + NCAAF + Special Games)
    key_games = [
        g for g in games
        if g["league"] in ("NFL", "NCAAF", "WWO-NCAAF")
        or g["high_priority"]
        or g["phase"] in ("All-Star Game", "Special Game", "All-Star Week")
    ]
    with open(os.path.join(OUT_DIR, "key_schedules.json"), "w") as f:
        json.dump(key_games, f, separators=(",", ":"))

    # Write metadata + summary stats
    mlb_reg_2027 = [g for g in games if g["league"] == "MLB" and g["phase"] in ("Regular Season", "Special Game")]
    mlb_spr_2027 = [g for g in games if g["league"] == "MLB" and g["phase"] in ("Spring Training", "Exhibition")]
    nfl_rem_2026 = [g for g in games if g["league"] == "NFL" and g["phase"].startswith("Regular Season (Wk")]
    meta = {
        "generated_at": "2026-11-25",
        "timezone": "America/Los_Angeles (PST/PDT)",
        "location": "Outer Sunset, San Francisco, CA 94122",
        "counts": {
            "total_indexed_events": len(games),
            "mlb_2027_regular": len(mlb_reg_2027),
            "mlb_2027_spring_exhibition": len(mlb_spr_2027),
            "nfl_2026_remaining_reg": len(nfl_rem_2026),
            "total_calendar_days": len(days),
            "strict_free_days_2027": sum(1 for k, v in days.items() if k.startswith("2027-") and v["is_free_strict"]),
            "reg_free_days_2027": sum(1 for k, v in days.items() if k.startswith("2027-") and v["is_free_reg"]),
            "flagged_items": len(flagged["items"]),
            "radio_stations": len(radio["stations"])
        },
        "durations_and_halftimes": other["durations_and_halftimes"],
        "estimated_season_blocks": other["estimated_season_blocks"]
    }
    with open(os.path.join(OUT_DIR, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    with open(os.path.join(OUT_DIR, "vacations.json"), "w") as f:
        json.dump(vacations, f, indent=2)
    with open(os.path.join(OUT_DIR, "radio.json"), "w") as f:
        json.dump(radio, f, indent=2)
    with open(os.path.join(OUT_DIR, "flagged.json"), "w") as f:
        json.dump(flagged, f, indent=2)

    print("BUILD COMPLETE!")
    print(json.dumps(meta["counts"], indent=2))
    print("\n2027 Strict Free Streaks (>=3 days):", vacations["streaks_2027_strict"])
    print("2027 Reg+Postseason Free Streaks (>=3 days):", vacations["streaks_2027_regular_postseason"])


if __name__ == "__main__":
    main()
