#!/usr/bin/env python3
"""Build data/schedule.json + data/vacation.json from verified windows.

No invented matchups/times: future years use season windows + typical
radio windows only, flagged ESTIMATED. 2026 Stanford/Cal/Westwood/49ers
anchor rows are transcribed from official pages (see sources/verification-log.md).
"""
import json, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"

def d(s): return dt.date.fromisoformat(s)

# ---------- Season windows ----------
# status: VERIFIED | PARTIAL | ESTIMATED | UNVERIFIED
windows = [
 # 2025 NFL season tail (covers Jan–Feb 2026 in this dataset)
 {"league":"NFL","year":2025,"phase":"Regular season (tail)","start":"2025-09-04","end":"2026-01-04","status":"VERIFIED",
  "source_name":"2025 NFL regular season finale Jan 4 2026 (Week 18)","source_url":"https://www.nfl.com/schedule/"},
 {"league":"NFL","year":2025,"phase":"Postseason → Super Bowl LX","start":"2026-01-10","end":"2026-02-08","status":"VERIFIED",
  "source_name":"Super Bowl LX Feb 8 2026, Levi's Stadium, Santa Clara (Seahawks vs Patriots)","source_url":"https://www.nfl.com/schedule/"},
 {"league":"NCAAF — Stanford/Cal","year":2025,"phase":"Bowls / CFP (tail)","start":"2025-12-01","end":"2026-01-20","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2025–26 bowls/CFP window; Stanford/Cal participation TBD (no matchup invented)","source_url":"https://ncaafpass.com/schedule/"},
 # MLB 2026
 {"league":"MLB","year":2026,"phase":"Spring Training (exhibition)","start":"2026-02-20","end":"2026-03-24","status":"VERIFIED",
  "source_name":"MLB Spring Training announcement (Cactus/Grapefruit begin Feb 20)","source_url":"https://www.mlb.com/press-release/press-release-mlb-announces-2026-regular-season-schedule"},
 {"league":"MLB","year":2026,"phase":"Regular season","start":"2026-03-25","end":"2026-09-27","status":"VERIFIED",
  "source_name":"MLB announces 2026 regular season schedule (Opening Night Mar 25, finale Sep 27)","source_url":"https://www.mlb.com/press-release/press-release-mlb-announces-2026-regular-season-schedule"},
 {"league":"MLB","year":2026,"phase":"Postseason (Wild Card → World Series)","start":"2026-09-29","end":"2026-10-31","status":"VERIFIED",
  "source_name":"2026 postseason calendar (Wild Card Sep 29; World Series Oct 23–31)","source_url":"https://www.mlbschedule.net/blog/when-does-mlb-season-end-2026"},
 {"league":"MLB","year":2026,"phase":"All-Star Game","start":"2026-07-14","end":"2026-07-14","status":"VERIFIED",
  "source_name":"2026 All-Star Game, Philadelphia (Citizens Bank Park)","source_url":"https://www.mlbschedule.net/blog/when-does-mlb-season-end-2026"},
 # MLB 2027
 {"league":"MLB","year":2027,"phase":"Spring Training (exhibition)","start":"2027-02-19","end":"2027-03-23","status":"VERIFIED",
  "source_name":"MLB 2027 key dates: spring games begin Feb 19","source_url":"https://usagametime.com/mlb-2027-opening-day-spring-training-key-dates/"},
 {"league":"MLB","year":2027,"phase":"Regular season","start":"2027-03-24","end":"2027-09-26","status":"VERIFIED",
  "source_name":"MLB 2027 schedule released Jul 16 2026 (Opening Night Mar 24 Netflix; Opening Day Mar 25; finale Sep 26)","source_url":"https://www.mlb.com/press-release/press-release-giants-announce-tentative-2027-regular-season-schedule"},
 {"league":"MLB","year":2027,"phase":"Postseason (Wild Card → World Series)","start":"2027-09-28","end":"2027-10-30","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2027 postseason dates not published; modeled on 2026 pattern (WC ~Sep 28, WS ~Oct 22–30)","source_url":"https://www.mlb.com/schedule"},
 {"league":"MLB","year":2027,"phase":"All-Star Game","start":"2027-07-13","end":"2027-07-13","status":"VERIFIED",
  "source_name":"2027 All-Star Game, Wrigley Field, Chicago (Home Run Derby Jul 12)","source_url":"https://usagametime.com/mlb-2027-opening-day-spring-training-key-dates/"},
 # MLB 2028
 {"league":"MLB","year":2028,"phase":"Spring Training (exhibition)","start":"2028-02-18","end":"2028-03-29","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2028 schedule not released; modeled on 2026–2027 pattern","source_url":"https://www.mlb.com/schedule"},
 {"league":"MLB","year":2028,"phase":"Regular season","start":"2028-03-30","end":"2028-09-24","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2028 regular-season schedule not released (Opening Day ~Mar 30 per calendar listings; UNVERIFIED)","source_url":"https://calendarena.com/usa/major-league-baseball-opening-day/"},
 {"league":"MLB","year":2028,"phase":"Postseason (Wild Card → World Series)","start":"2028-09-26","end":"2028-10-28","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2028 postseason dates not published","source_url":"https://www.mlb.com/schedule"},
 {"league":"MLB","year":2028,"phase":"All-Star Game","start":"2028-07-11","end":"2028-07-12","status":"PARTIAL",
  "source_name":"2028 All-Star Game awarded to Oracle Park, San Francisco; date reported as Jul 11 AND Jul 12 — CONFLICT, see Flagged for Review","source_url":"https://www.nbcbayarea.com/news/local/2028-mlb-all-star-game-san-francisco/4128095/"},
 # MLB 2029
 {"league":"MLB","year":2029,"phase":"Spring Training (exhibition)","start":"2029-02-17","end":"2029-03-28","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2029 schedule not released","source_url":"https://www.mlb.com/schedule"},
 {"league":"MLB","year":2029,"phase":"Regular season","start":"2029-03-29","end":"2029-09-23","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2029 regular-season schedule not released (Opening Day ~Mar 29 per calendar listings; UNVERIFIED)","source_url":"https://calendarena.com/usa/major-league-baseball-opening-day/"},
 {"league":"MLB","year":2029,"phase":"Postseason (Wild Card → World Series)","start":"2029-09-25","end":"2029-10-27","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2029 postseason dates not published","source_url":"https://www.mlb.com/schedule"},
 {"league":"MLB","year":2029,"phase":"All-Star Game","start":"","end":"","status":"UNVERIFIED",
  "source_name":"UNVERIFIED — 2029 All-Star host/date not announced; left blank (never inferred)","source_url":"https://www.mlb.com/schedule"},
 # NFL 2026 season
 {"league":"NFL","year":2026,"phase":"Preseason (incl. Hall of Fame Game)","start":"2026-08-06","end":"2026-08-29","status":"VERIFIED",
  "source_name":"2026 NFL preseason: Hall of Fame Game Aug 6; 49ers Aug 13/20/27","source_url":"https://www.49ers.com/schedule/"},
 {"league":"NFL","year":2026,"phase":"Regular season","start":"2026-09-09","end":"2027-01-10","status":"VERIFIED",
  "source_name":"2026 NFL regular season: Kickoff Sep 9; Week 18 Jan 9–10 2027","source_url":"https://www.49ers.com/schedule/"},
 {"league":"NFL","year":2026,"phase":"Postseason → Super Bowl LXI","start":"2027-01-16","end":"2027-02-14","status":"VERIFIED",
  "source_name":"Super Bowl LXI Feb 14 2027, SoFi Stadium, Inglewood","source_url":"https://www.49ers.com/schedule/"},
 # NFL 2027 season
 {"league":"NFL","year":2027,"phase":"Preseason","start":"2027-08-05","end":"2027-08-28","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2027 preseason dates not published (3 games/team expected)","source_url":"https://www.nfl.com/schedule/"},
 {"league":"NFL","year":2027,"phase":"Regular season","start":"2027-09-09","end":"2028-01-09","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2027 schedule release expected May 2027; kickoff modeled as Thu after Labor Day","source_url":"https://datescal.com/nfl-schedule/"},
 {"league":"NFL","year":2027,"phase":"Postseason → Super Bowl LXII","start":"2028-01-15","end":"2028-02-13","status":"PARTIAL",
  "source_name":"Super Bowl LXII Feb 13 2028, Mercedes-Benz Stadium, Atlanta — CONFIRMED; earlier playoff dates ESTIMATED","source_url":"https://awfulannouncing.com/nfl/sets-2028-super-bowl-date.html"},
 # NFL 2028 season
 {"league":"NFL","year":2028,"phase":"Preseason","start":"2028-08-03","end":"2028-08-26","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2028 preseason dates not published","source_url":"https://www.nfl.com/schedule/"},
 {"league":"NFL","year":2028,"phase":"Regular season","start":"2028-09-07","end":"2029-01-07","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2028 schedule not released; kickoff modeled as Thu after Labor Day (Sep 4)","source_url":"https://www.nfl.com/schedule/"},
 {"league":"NFL","year":2028,"phase":"Postseason → Super Bowl LXIII","start":"2029-01-13","end":"2029-02-11","status":"PARTIAL",
  "source_name":"Super Bowl LXIII Feb 11 2029, Allegiant Stadium, Las Vegas — CONFIRMED (NFL Mar 30 2026); earlier playoff dates ESTIMATED","source_url":"https://www.raiders.com/news/super-bowl-returns-to-las-vegas-in-2029"},
 # NFL 2029 season
 {"league":"NFL","year":2029,"phase":"Preseason","start":"2029-08-02","end":"2029-08-25","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2029 preseason dates not published","source_url":"https://www.nfl.com/schedule/"},
 {"league":"NFL","year":2029,"phase":"Regular season","start":"2029-09-06","end":"2030-01-06","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2029 schedule not released; kickoff modeled as Thu after Labor Day (Sep 3)","source_url":"https://www.nfl.com/schedule/"},
 {"league":"NFL","year":2029,"phase":"Postseason → Super Bowl LXIV","start":"2030-01-12","end":"2030-02-10","status":"ESTIMATED",
  "source_name":"ESTIMATED — Super Bowl LXIV reported for Nashville, Feb 2030 (date/city REPORTED, not yet confirmed on NFL.com; treat as estimated)","source_url":"https://www.foxsports.com/stories/nfl/super-bowl-locations-dates"},
 # NCAAF Stanford/Cal 2026
 {"league":"NCAAF — Stanford","year":2026,"phase":"Regular season","start":"2026-08-29","end":"2026-11-28","status":"VERIFIED",
  "source_name":"Stanford 2026 Football Schedule (gostanford.com) — 12 games Aug 29–Nov 28","source_url":"https://gostanford.com/sports/football/schedule"},
 {"league":"NCAAF — California","year":2026,"phase":"Regular season","start":"2026-09-05","end":"2026-11-28","status":"VERIFIED",
  "source_name":"Cal 2026 Football Schedule (calbears.com) — 12 games Sep 5–Nov 28","source_url":"https://calbears.com/sports/football/schedule/text"},
 {"league":"NCAAF — Stanford/Cal","year":2026,"phase":"Bowls / College Football Playoff (TBD participation)","start":"2026-12-01","end":"2027-01-25","status":"ESTIMATED",
  "source_name":"CFP window Dec 18–Jan 25 (NCAAF Pass); Stanford/Cal bowl/CFP participation TBD — window shown, no matchup invented","source_url":"https://ncaafpass.com/schedule/"},
 # NCAAF 2027
 {"league":"NCAAF — Stanford","year":2027,"phase":"Regular season","start":"2027-08-28","end":"2027-11-27","status":"PARTIAL",
  "source_name":"PARTIAL — Full 2027 schedule not released. Reported: hosts Vanderbilt Sep 11 2027; hosts Notre Dame Nov 27 2027; ACC road at BC/Clemson/SMU. Verify on gostanford.com when published.","source_url":"https://gostanford.com/sports/football/schedule"},
 {"league":"NCAAF — California","year":2027,"phase":"Regular season","start":"2027-08-28","end":"2027-11-27","status":"UNVERIFIED",
  "source_name":"UNVERIFIED — No 2027 Cal schedule found on calbears.com as of Nov 2026; window ESTIMATED from 2026 pattern, dates left blank","source_url":"https://calbears.com/sports/football/schedule/text"},
 {"league":"NCAAF — Stanford/Cal","year":2027,"phase":"Bowls / CFP (TBD)","start":"2027-12-01","end":"2028-01-25","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2027 bowls/CFP dates not published (24-team CFP from 2027–28 per reports)","source_url":"https://ncaafpass.com/schedule/"},
 # NCAAF 2028/2029
 {"league":"NCAAF — Stanford/Cal","year":2028,"phase":"Regular season","start":"2028-08-26","end":"2028-11-25","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2028 schedules not released; late-Aug–late-Nov window from 2026 pattern; Big Game traditionally late Nov","source_url":"https://gostanford.com/sports/football/schedule"},
 {"league":"NCAAF — Stanford/Cal","year":2029,"phase":"Regular season","start":"2029-08-25","end":"2029-11-24","status":"ESTIMATED",
  "source_name":"ESTIMATED — 2029 schedules not released","source_url":"https://gostanford.com/sports/football/schedule"},
 # Westwood One
 {"league":"Westwood One Sports (NFL radio)","year":2026,"phase":"National NFL radio: primetime + postseason (verified subset Nov 2026–Jan 2027)","start":"2026-11-25","end":"2027-02-14","status":"PARTIAL",
  "source_name":"Westwood One NFL Schedule page (official) — verified rows Nov 25 2026–Jan 10 2027 transcribed; Sep–Oct 2026 rows on live page, not in snapshot — see westwood-one.html","source_url":"https://www.westwoodonesports.com/nfl-schedule/"},
 {"league":"Westwood One Sports (NFL radio)","year":2027,"phase":"National NFL radio (pattern)","start":"2027-09-09","end":"2028-02-13","status":"ESTIMATED",
  "source_name":"ESTIMATED — No 2027 Westwood One schedule published; pattern = TNF/SNF/MNF + holiday tripleheaders + all postseason (per 2026 pattern)","source_url":"https://www.westwoodonesports.com/nfl-schedule/"},
 {"league":"Westwood One Sports (NFL radio)","year":2028,"phase":"National NFL radio (pattern)","start":"2028-09-07","end":"2029-02-11","status":"ESTIMATED",
  "source_name":"ESTIMATED — No 2028 Westwood One schedule published; same pattern","source_url":"https://www.westwoodonesports.com/nfl-schedule/"},
 {"league":"Westwood One Sports (NFL radio)","year":2029,"phase":"National NFL radio (pattern)","start":"2029-09-06","end":"2030-02-10","status":"ESTIMATED",
  "source_name":"ESTIMATED — No 2029 Westwood One schedule published; same pattern","source_url":"https://www.westwoodonesports.com/nfl-schedule/"},
]

# ---------- Verified 2026 game-day anchors (transcribed, official sources) ----------
# Stanford 2026 (gostanford.com) — date, opponent, kickoff PT
stanford_2026 = [
 ("2026-08-29","vs Hawai'i","4:00 PM PT","ACC Network"),
 ("2026-09-04","vs #7 Miami","6:00 PM PT","ESPN"),
 ("2026-09-19","at Duke","1:00 PM PT","The CW"),
 ("2026-09-26","vs Georgia Tech","7:30 PM PT","ESPN"),
 ("2026-10-03","at Wake Forest","TBA (see gostanford.com)","TBA"),
 ("2026-10-10","at Notre Dame","12:30 PM PT","NBC/Peacock"),
 ("2026-10-17","vs Elon (Homecoming)","4:30 PM PT","ACC Network Extra"),
 ("2026-10-23","vs NC State","7:30 PM PT","ESPN"),
 ("2026-10-31","at Louisville","TBA (see gostanford.com)","TBA"),
 ("2026-11-14","at Virginia Tech","TBA (see gostanford.com)","TBA"),
 ("2026-11-21","at California — 129th Big Game","4:30 PM PT","ACC Network"),
 ("2026-11-28","vs SMU","12:30 PM PT","ACC Network"),
]
# Cal 2026 (calbears.com) — date, opponent, kickoff PT (from schedule/text + Big Game events)
cal_2026 = [
 ("2026-09-05","vs UCLA","7:30 PM PT"),
 ("2026-09-12","at Syracuse","12:30 PM PT"),
 ("2026-09-19","vs Wagner","12:30 PM PT"),
 ("2026-09-25","vs Clemson (Fri)","7:30 PM PT"),
 ("2026-10-03","at UNLV","12:30 PM PT"),
 ("2026-10-10","vs Virginia Tech","12:30 PM PT"),
 ("2026-10-17","vs Wake Forest","7:30 PM PT"),
 ("2026-10-24","at SMU","9:00 AM PT"),
 ("2026-10-31","at NC State","9:00 AM PT"),
 ("2026-11-14","at Virginia","12:30 PM PT"),
 ("2026-11-21","vs Stanford — 129th Big Game","4:30 PM PT"),
 ("2026-11-28","vs Pittsburgh","TBA (see calbears.com)"),
]
# 49ers 2026 preseason + key regular-season anchors (49ers.com)
fortyniners_2026 = [
 ("2026-08-13","Preseason Wk1 vs Tennessee Titans (Levi's)","—"),
 ("2026-08-20","Preseason Wk2 at LA Chargers (SoFi)","—"),
 ("2026-08-27","Preseason Wk3 at Las Vegas Raiders (Allegiant)","—"),
 ("2026-09-10","Week 1: vs Rams — Australia Game, Melbourne (Netflix)","8:35 PM ET / 5:35 PM PT"),
 ("2026-12-17","Week 15 Thu at LA Chargers (SoFi)","5:15 PM PT"),
 ("2027-01-03","Week 17 Sun vs Philadelphia Eagles (Levi's)","5:20 PM PT"),
]
# Westwood One verified subset (westwoodonesports.com/nfl-schedule/ snapshot Nov 2026–Jan 2027)
# date, matchup, kickoff ET, label — transcribed verbatim from official page
westwood_2026 = [
 ("2026-11-25","Green Bay Packers at Los Angeles Rams","7:30 PM ET","Thanksgiving Wednesday"),
 ("2026-11-26","Chicago Bears at Detroit Lions","12:30 PM ET","Thanksgiving Tripleheader"),
 ("2026-11-26","Philadelphia Eagles at Dallas Cowboys","4:15 PM ET","Thanksgiving Tripleheader"),
 ("2026-11-26","Kansas City Chiefs at Buffalo Bills","8:00 PM ET","Thanksgiving Tripleheader"),
 ("2026-11-27","Denver Broncos at Pittsburgh Steelers","2:30 PM ET","Black Friday Game"),
 ("2026-11-29","Las Vegas Raiders at Cleveland Browns","7:30 PM ET","Sunday Night Football"),
 ("2026-11-30","Carolina Panthers at Tampa Bay Buccaneers","7:00 PM ET","Monday Night Football"),
 ("2026-12-03","Kansas City Chiefs at Los Angeles Rams","7:30 PM ET","Thursday Night Football"),
 ("2026-12-06","Houston Texans at Pittsburgh Steelers","7:30 PM ET","Sunday Night Football"),
 ("2026-12-07","Dallas Cowboys at Seattle Seahawks","7:00 PM ET","Monday Night Football"),
 ("2026-12-10","Minnesota Vikings at New England Patriots","7:30 PM ET","Thursday Night Football"),
 ("2026-12-13","Buffalo Bills at Green Bay Packers","7:30 PM ET","Sunday Night Football"),
 ("2026-12-14","Pittsburgh Steelers at Jacksonville Jaguars","7:00 PM ET","Monday Night Football"),
 ("2026-12-17","San Francisco 49ers at Los Angeles Chargers","7:30 PM ET","Thursday Night Football"),
 ("2026-12-19","Seattle Seahawks at Philadelphia Eagles","4:30 PM ET","Week 15 Saturday Doubleheader"),
 ("2026-12-19","Chicago Bears at Buffalo Bills","8:00 PM ET","Week 15 Saturday Doubleheader"),
 ("2026-12-20","Detroit Lions at Minnesota Vikings","7:30 PM ET","Sunday Night Football"),
 ("2026-12-21","New England Patriots at Kansas City Chiefs","7:00 PM ET","Monday Night Football"),
 ("2026-12-24","Houston Texans at Philadelphia Eagles","7:30 PM ET","Thursday Night Football"),
 ("2026-12-25","Green Bay Packers at Chicago Bears","12:30 PM ET","Christmas Tripleheader"),
 ("2026-12-25","Buffalo Bills at Denver Broncos","4:15 PM ET","Christmas Tripleheader"),
 ("2026-12-25","Los Angeles Rams at Seattle Seahawks","8:00 PM ET","Christmas Tripleheader"),
 ("2026-12-26","Week 16 Saturday Doubleheader TBA","4:00 PM ET / 8:00 PM ET","Week 16 Saturday Doubleheader"),
 ("2026-12-27","Jacksonville Jaguars at Dallas Cowboys","7:30 PM ET","Sunday Night Football"),
 ("2026-12-28","New York Giants at Detroit Lions","7:00 PM ET","Monday Night Football"),
 ("2026-12-31","Baltimore Ravens at Cincinnati Bengals","7:30 PM ET","Thursday Night Football"),
 ("2027-01-02","Week 17 Saturday Doubleheader TBA","4:00 PM ET / 8:00 PM ET","Week 17 Saturday Doubleheader"),
 ("2027-01-03","Philadelphia Eagles at San Francisco 49ers","7:30 PM ET","Sunday Night Football"),
 ("2027-01-04","Houston Texans at Green Bay Packers","7:00 PM ET","Monday Night Football"),
 ("2027-01-09","Week 18 Saturday Tripleheader TBA","12:30 PM ET / 4:15 PM ET / 8:00 PM ET","Week 18 Saturday Tripleheader"),
 ("2027-01-10","Week 18 Sunday Night Football — Teams TBA","7:30 PM ET","Sunday Night Football"),
]

# All 30 MLB clubs (official league membership)
mlb_clubs = ["Arizona Diamondbacks","Atlanta Braves","Baltimore Orioles","Boston Red Sox","Chicago Cubs","Chicago White Sox","Cincinnati Reds","Cleveland Guardians","Colorado Rockies","Detroit Tigers","Houston Astros","Kansas City Royals","Los Angeles Angels","Los Angeles Dodgers","Miami Marlins","Milwaukee Brewers","Minnesota Twins","New York Mets","New York Yankees","Oakland Athletics (Athletics)","Philadelphia Phillies","Pittsburgh Pirates","San Diego Padres","San Francisco Giants","Seattle Mariners","St. Louis Cardinals","Tampa Bay Rays","Texas Rangers","Toronto Blue Jays","Washington Nationals"]

# ---------- Daily free/busy computation ----------
# Busy-day rules (documented in methodology.html):
#  MLB spring/regular/postseason: every day busy EXCEPT All-Star break non-game days.
#  NFL preseason: Thu–Sun busy. Regular: Sun/Thu/Mon busy (+Sat Dec–Jan). Postseason: Sat/Sun/Mon busy.
#  NCAAF: 2026 = actual Stanford/Cal dates; other years = every Saturday in window (conservative).
#  Westwood: same days as NFL primetime (subset; no extra blocking).
allstar_breaks = {  # year: (allstar_date, [free_break_dates])
 2026: ("2026-07-14", ["2026-07-13","2026-07-15","2026-07-16"]),
 2027: ("2027-07-13", ["2027-07-12","2027-07-14","2027-07-15"]),
 2028: ("2028-07-11", ["2028-07-10","2028-07-12","2028-07-13"]),  # ESTIMATED (date conflict)
 2029: ("", []),
}
def in_window(day, league_substr, phase_substr=None):
    for w in windows:
        if league_substr not in w["league"]: continue
        if phase_substr and phase_substr not in w["phase"]: continue
        if not w["start"] or not w["end"]: continue
        if d(w["start"]) <= day <= d(w["end"]): return w
    return None

stanford_days = {d(x[0]) for x in stanford_2026}
cal_days = {d(x[0]) for x in cal_2026}
# 2026 NCAAF: also count ACC Championship Dec 5 as potential busy (if either qualifies) — mark as TBD, treat as busy for vacation (conservative)
ncaaf_2026_extra = {d("2026-12-05")}

def busy_reasons(day):
    reasons = []
    # MLB
    mlb = in_window(day, "MLB", "Spring") or in_window(day, "MLB", "Regular") or in_window(day, "MLB", "Postseason")
    if mlb:
        # All-Star break free days override
        yr = day.year
        if yr in allstar_breaks and day.isoformat() in allstar_breaks[yr][1]:
            pass
        else:
            # All-Star day itself is busy (the game)
            reasons.append(f"MLB {mlb['phase']} ({mlb['status']})")
    # NFL
    nfl = in_window(day, "NFL", "Preseason") or in_window(day, "NFL", "Regular") or in_window(day, "NFL", "Postseason")
    if nfl:
        wd = day.weekday()  # Mon=0..Sun=6
        phase = nfl["phase"]
        busy = False
        if "Preseason" in phase and wd in (3,4,5,6): busy=True
        elif "Regular" in phase and wd in (0,3,6): busy=True
        elif "Regular" in phase and wd==5 and day.month in (12,1): busy=True  # Sat doubleheaders
        elif "Regular" in phase and day.month==12 and day.day==25: busy=True  # Christmas Day tripleheader (Fri in 2026)
        elif "Regular" in phase and day.month==11 and wd==4 and 22 <= day.day <= 28: busy=True  # Black Friday game (Fri after Thanksgiving)
        elif "Postseason" in phase and wd in (0,5,6): busy=True
        if busy: reasons.append(f"NFL {phase} ({nfl['status']})")
    # NCAAF
    if day.year == 2026:
        if day in stanford_days: reasons.append("NCAAF Stanford game day (VERIFIED)")
        if day in cal_days: reasons.append("NCAAF Cal game day (VERIFIED)")
        if day in ncaaf_2026_extra: reasons.append("NCAAF ACC Championship — TBD participation (treat as busy)")
    else:
        w = in_window(day, "NCAAF")
        if w and day.weekday()==5:  # Saturday
            reasons.append(f"NCAAF Stanford/Cal Saturday window ({w['status']})")
    # Westwood (subset of NFL primetime days — list for display when NFL busy on Thu/Mon/Sun)
    if any("NFL" in r for r in reasons) and day.weekday() in (0,3,6):
        reasons.append("Westwood One national NFL radio (primetime/postseason pattern)")
    return reasons

start, end = d("2026-01-01"), d("2029-12-31")
days = []
cur = start
while cur <= end:
    r = busy_reasons(cur)
    days.append({"date": cur.isoformat(), "weekday": cur.strftime("%A"),
                 "free": len(r)==0, "busy_reasons": r})
    cur += dt.timedelta(days=1)

# Longest consecutive free runs
runs = []
i = 0
while i < len(days):
    if days[i]["free"]:
        j = i
        while j < len(days) and days[j]["free"]: j += 1
        runs.append({"start": days[i]["date"], "end": days[j-1]["date"], "days": j-i})
        i = j
    else: i += 1
runs.sort(key=lambda x: -x["days"])

# Regular-season-only alternative (exclude spring training + NFL preseason from blocking)
def busy_regular_only(day):
    r = []
    mlb = in_window(day, "MLB", "Regular") or in_window(day, "MLB", "Postseason")
    if mlb:
        yr = day.year
        if not (yr in allstar_breaks and day.isoformat() in allstar_breaks[yr][1]):
            r.append("MLB")
    nfl = in_window(day, "NFL", "Regular") or in_window(day, "NFL", "Postseason")
    if nfl:
        wd = day.weekday()
        if "Regular" in nfl["phase"] and wd in (0,3,6): r.append("NFL")
        elif "Regular" in nfl["phase"] and wd==5 and day.month in (12,1): r.append("NFL")
        elif "Regular" in nfl["phase"] and day.month==12 and day.day==25: r.append("NFL")
        elif "Regular" in nfl["phase"] and day.month==11 and wd==4 and 22 <= day.day <= 28: r.append("NFL")
        elif "Postseason" in nfl["phase"] and wd in (0,5,6): r.append("NFL")
    if day.year == 2026:
        if day in stanford_days or day in cal_days or day in ncaaf_2026_extra: r.append("NCAAF")
    else:
        w = in_window(day, "NCAAF")
        if w and day.weekday()==5: r.append("NCAAF")
    return r

days_ro = []
cur = start
while cur <= end:
    days_ro.append({"date": cur.isoformat(), "free": len(busy_regular_only(cur))==0})
    cur += dt.timedelta(days=1)
runs_ro = []
i = 0
while i < len(days_ro):
    if days_ro[i]["free"]:
        j = i
        while j < len(days_ro) and days_ro[j]["free"]: j += 1
        runs_ro.append({"start": days_ro[i]["date"], "end": days_ro[j-1]["date"], "days": j-i})
        i = j
    else: i += 1
runs_ro.sort(key=lambda x: -x["days"])

schedule = {
 "generated": "2026-11-25",
 "timezone": "America/Los_Angeles (Pacific; PST/PDT as applicable — site labels all times PT)",
 "durations_minutes": {"MLB":150,"NFL":192,"NCAAF":204,"radio_pregame":30,"radio_postgame":15,
   "halftime_NFL":12,"halftime_NCAAF":20},
 "windows": windows,
 "mlb_clubs_30": mlb_clubs,
 "stanford_2026": [{"date":a,"matchup":b,"kickoff_pt":c,"tv":e} for a,b,c,e in stanford_2026],
 "cal_2026": [{"date":a,"matchup":b,"kickoff_pt":c} for a,b,c in cal_2026],
 "fortyniners_2026_anchors": [{"date":a,"event":b,"time":c} for a,b,c in fortyniners_2026],
 "westwood_2026_verified": [{"date":a,"matchup":b,"kickoff_et":c,"label":e} for a,b,c,e in westwood_2026],
 "days": days,
 "vacation_strict_top_runs": runs[:12],
 "vacation_regular_only_top_runs": runs_ro[:8],
}
vacation = {
 "generated": "2026-11-25",
 "strict_definition": "FREE DAY = no MLB (spring/regular/postseason), no NFL (preseason/regular/postseason game day), no Stanford/Cal NCAAF game day, no Westwood One primetime day. See methodology.html.",
 "regular_only_definition": "Same but EXCLUDES MLB Spring Training and NFL preseason (regular season + postseason only).",
 "strict_top_runs": runs[:12],
 "regular_only_top_runs": runs_ro[:8],
 "notes": [
  "No 7-day (1-week) all-off window exists in 2027–2029 under the STRICT definition; longest is 4–5 days in February (post-Super Bowl, pre-Spring Training).",
  "No 14-day or 21-day all-off window exists under EITHER definition in 2027–2029 except the February regular-season-only window (see regular_only_top_runs).",
  "July All-Star breaks give 3 free days per year (All-Star Game day itself is busy).",
  "All future-year windows are ESTIMATED until MLB/NFL/NCAAF publish official schedules; re-run tools/build_data.py when released.",
 ],
}
OUT.mkdir(exist_ok=True)
(OUT/"schedule.json").write_text(json.dumps(schedule, indent=1))
(OUT/"vacation.json").write_text(json.dumps(vacation, indent=1))
print(f"days={len(days)} strict_runs_top={runs[:5]}")
print(f"regular_only_top={runs_ro[:5]}")
print("wrote", OUT/"schedule.json", OUT/"vacation.json")
