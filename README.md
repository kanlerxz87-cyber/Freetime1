# FREE TIME VACATION — SF Bay Area (Outer Sunset 94122) Sports-Free Planner

A verified, zero-hallucination data repository and interactive GitHub Pages dashboard to plan daily free time (in Pacific Time, **PST/PDT**) and multi-year vacations (**2027–2029**) without live AM/FM sports radio conflicts in **Outer Sunset, San Francisco, CA 94122**.

**Live Dashboard:** https://kanlerxz87-cyber.github.io/Freetime1/

---

## Executive Summary (Verified as of November 25, 2026)

### 2027–2029 Multi-Week Vacation Windows
| Mode | 2027 | 2028 | 2029 | Fits 1-Wk / 2-Wk / 3-Wk? |
| --- | --- | --- | --- | --- |
| **Regular Season + Postseason Only** *(Excl. MLB Spring Training & NFL Preseason)* | **Mon Feb 15 – Tue Mar 23 (37 days — VERIFIED)** | **Mon Feb 14 – Wed Mar 29 (~45 days — SB LXII Verified / MLB Est.)** | **Mon Feb 12 – Wed Mar 28 (~45 days — Est.)** | **YES / YES / YES** |
| **Strict Mode — Pre-Super Bowl Gap** *(NFL discontinued the Pro Bowl game starting 2026–27)* | **Mon Feb 1 – Sat Feb 13 (13 days — Verified Dates)** | **Mon Jan 31 – Sat Feb 12 (~13 days — Est.)** | **Mon Jan 29 – Sat Feb 10 (~13 days — Est.)** | **YES / No / No** |
| **Strict Mode — Post-Super Bowl Gap** *(Includes MLB Spring Training & NFL Preseason)* | **Mon Feb 15 – Thu Feb 18 (4 days — VERIFIED)** | **Mon Feb 14 – Fri Feb 18 (~5 days — Est.)** | **Mon Feb 12 – Fri Feb 16 (~5 days — Est.)** | **No / No / No** |

> **Critical 2027 Labor Wildcard:** MLB's 2022–2026 CBA expires **Dec 1, 2026**. If a lockout delays 2027 Spring Training beyond Fri Feb 19, 2027, the Strict Mode Feb–Mar 2027 window would expand. See [`flagged.html`](flagged.html) for all 10 flagged items.

---

## Verified Data Coverage
- **2027 MLB Regular Season:** **2,430 official games** across all 30 MLB clubs (mathematically verified: every club has exactly 162 games, 0 duplicate `gamePk`s) directly from `statsapi.mlb.com`, with **SF Giants** & **Athletics** flagged High Priority.
- **2027 MLB Spring Training, Exhibition & All-Star Game:** **474 official games** (Feb 19 – Mar 23, 2027) + **97th All-Star Game** (Tue Jul 13, 2027 at Wrigley Field) + **Field of Dreams** (Aug 12) + **Little League Classic** (Aug 19).
- **2026 NFL Regular Season (Remaining Weeks 12–18):** **109 official games** (Nov 25, 2026 – Jan 10, 2027) directly from `nfl.com`, with **SF 49ers** & **Westwood One Sports** flagged.
- **2026–27 NFL Postseason & Super Bowls:** Wild Card (Jan 16–18), Divisional (Jan 23–24), Conference Championships (Jan 31), **Super Bowl LXI** (Sun Feb 14, 2027 — Verified), **Super Bowl LXII** (Sun Feb 13, 2028 — Verified), **Super Bowl LXIII** (Las Vegas host confirmed; target Sun Feb 11, 2029).
- **Local High-Priority NCAAF:** **Stanford Cardinal** (KTCT 1050 AM; 6–5 bowl-eligible, Dec 2026 bowl TBD) and **California Golden Bears** (KSFO 810 AM; 3–8, not bowl-eligible).
- **Outer Sunset SF 94122 AM/FM Radio Guide:** KNBR 680 AM/104.5 FM, KSAN 107.7 FM, KTCT 1050 AM, KSFO 810 AM, KNEW 960 AM, KSFN 1510 AM, KGMZ 95.7 FM (Warriors/Valkyries), KZSF 1370 AM, plus verified digital-only confirmations for **San Jose Sharks** (no terrestrial AM/FM since 2021) and **49ers Spanish Radio** (Bay Area streaming-only).
- **100% Official Source Links:** Every single table row (all 3,181 events, 10 radio entries, 10 vacation windows, 10 flagged items) links to an official `https://` source.

---

## Dashboard Pages
- `index.html` — Executive Summary & 14-Day Free-Time Outlook
- `calendar.html` — Interactive Daily Scoreboard & PST/PDT Free-Time Calendar
- `vacations.html` — 2027–2029 Multi-Year Vacation Planner
- `schedules.html` — Searchable Full Schedules & High-Priority Tracker
- `radio.html` — Outer Sunset SF 94122 AM/FM Radio Guide
- `flagged.html` — Flagged for Review & Duration/Halftime Methodology

## Rebuild & Verify Locally
```bash
python3 scripts/build_data.py
python3 scripts/verify_data.py
python3 -m http.server 8000
```
