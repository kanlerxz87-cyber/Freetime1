# COORDINATION — Freetime1 shared task board

Session ID for this session: `arena-9f5f3a65`
Branch: `arena/9f5f3a65-freetime1` (branched from `main` @ `a7d1d4a`)
Repo: `kanlerxz87-cyber/Freetime1`
Date started: 2026-11-25

> Per project instructions: claim a task by writing session ID + file scope here,
> commit + push the claim immediately, keep scopes non-overlapping, small frequent
> commits, `git pull --rebase` before every push. This is a single-session run:
> one session claims all tasks below and acts as final integration session.
> No other session is active on this repo at claim time (verified: only `main`
> and this branch exist; working tree clean).

## Task board

| ID | Task | Status | Owner session | Files in scope |
|----|------|--------|---------------|----------------|
| T1 | Research + verification log (MLB/NFL/NCAAF/Westwood One/radio, durations) | in progress | arena-9f5f3a65 | `sources/verification-log.md`, `COORDINATION.md` |
| T2 | Data model: season windows, anchor events, daily free/busy computation (2026–2029) | in progress | arena-9f5f3a65 | `data/schedule.json`, `data/vacation.json`, `tools/build_data.py` |
| T3 | GitHub Pages site: landing + category subpages + scoreboard/calendar UI | in progress | arena-9f5f3a65 | `index.html`, `*.html`, `assets/*`, `.nojekyll` |
| T4 | Vacation-window analysis (1/2/3-week all-off windows, 2027–2029) | in progress | arena-9f5f3a65 | `vacation-windows.html`, `data/vacation.json` |
| T5 | Final integration: re-verify combined data, link check, PR to `main`, merge, Pages deploy | in progress | arena-9f5f3a65 | all (integration only) |
| T6 | Supplemental official-source reconciliation for future schedule claims and status corrections | done | arena/bf7d526d-freetime1 | `sources/arena-bf7d526d-audit.md`, `COORDINATION.md` |
| T7 | Safety correction: prevent partial modeled gaps from appearing certified free; correct flagged official schedule/radio claims from T6 audit | done | arena/bf7d526d-freetime1 | `index.html`, `scoreboard.html`, `vacation-windows.html`, `executive-summary.html`, `methodology.html`, `flagged-for-review.html`, `sources.html`, `assets/app.js`, `assets/style.css`, `scripts/test.mjs`, `COORDINATION.md` |

Status values: `unclaimed`, `in progress`, `done`, `needs review`.
`needs review` = published on Flagged for Review page; does not block merge.

## Claim log

- 2026-11-25 — `arena-9f5f3a65` claims T1 (scope: `sources/verification-log.md`, `COORDINATION.md`). No other claims exist. Pushing claim immediately before starting T2–T5.
- 2026-11-25 — `arena-9f5f3a65` claims T2+T3+T4+T5 (single-session integration; scopes: `data/*`, `tools/*`, `*.html`, `assets/*`, `.nojekyll`). No other sessions active; no overlap possible.
- 2026-11-25 — `arena/bf7d526d-freetime1` claims T6, a separate official-source reconciliation note at `sources/arena-bf7d526d-audit.md` plus this board. The existing site and schedule data remained outside that claim.
- 2026-11-25 — `arena/bf7d526d-freetime1` claims T7 after PR #3 merged the source audit. T7 addresses only prominent false-clearance language and source-status corrections required by that audit; no schedule rows or owner data model are being invented or expanded.
- T7 DONE: homepage, executive summary, scoreboard, vacation analysis and methodology now state that partial-model gaps are not certified free time. Calendar dates use unknown/modeled-activity colors instead of green free-day claims; minute gaps are labeled unmodeled. Flagged page and source table now reflect the official-source findings from T6 (MLB 2027 release, Cal partial slate/conflict, Stanford opponent-vs-date scope, Athletics/Cal station sources, NFL future schedule data status and Super Bowl confirmation limits). Added regression assertions preventing false-free language from returning.
- Verification: `node --check assets/app.js`; `node scripts/test.mjs` (interval/DST/snapshot/link checks plus no-false-free claims); `git diff --check`. External official pages were checked via browser tools; per-address 94122 radio reception remains unknown.
- Follow-up polish after PR #6: removed model-generated date ranges from the vacation page rather than showing unsupported candidate windows, and fixed timeline end-of-day rendering to read “12:00 AM (next day)” instead of “12:00 PM.”

## Handoff / conflict log

- (none)

## Completion records (sources, verification, irregularities)

- (to be filled per task as completed; every verified row links its official source;
  anything not confirmable from an official source is left blank + flagged unverified)

## Completion records (final integration, 2026-11-25)

- T1 Research + verification: DONE. Sources in `sources/verification-log.md` + `sources.html`.
  Verified: MLB 2026/2027 windows (mlb.com press releases), NFL/49ers 2026 (49ers.com),
  Stanford/Cal 2026 12+12 game days (gostanford.com/calbears.com), Westwood One 31 rows
  (westwoodonesports.com/nfl-schedule fetched), SB LXII/LXIII (NFL announcements),
  KNBR/KSAN/KTCT/KGO/KSFN (49ers.com + KNBR). Irregularities F-01..F-09 on Flagged page.
- T2 Data model: DONE. `tools/build_data.py` → `data/schedule.json` (43 windows, 1,461 days)
  + `data/vacation.json`. No invented matchups; future years ESTIMATED. Holiday fix
  (Black Friday/Christmas) applied and re-verified (Dec 25/Nov 27 2026 now BUSY).
- T3 Site: DONE. 12 pages + `assets/style.css` + `assets/app.js` + `.nojekyll`.
  Scoreboard has Yesterday/Today/Tomorrow, date picker, month calendar, PT timeline,
  free-gap minutes. All internal links checked (0 missing); `node --check` OK; JSON valid.
  External link check via bash curl is blocked by sandbox egress (github/npm/pypi only);
  verification was done via web_search/fetch_page tools instead.
- T4 Vacation analysis: DONE. Strict max 2027–2029 = 4–5 days (Feb); no 7/14/21-day window.
  Regular-only: 2027 37d, 2028/2029 45d EST. Tables on vacation-windows.html + exec summary.
- T5 Integration: DONE (this session). Re-verified combined data line-by-line against
  verification log; site serves 200 on all pages locally (python http.server :8000).
  Note: later source audit found several claims requiring correction; see T6/T7 and PR records.

## PR / deploy record

- PR #3 — [Supplemental source audit](https://github.com/kanlerxz87-cyber/Freetime1/pull/3), merged 2026-11-25 (source audit, no root site replacement).
- PR #6 — [Prevent incomplete schedules from claiming free windows](https://github.com/kanlerxz87-cyber/Freetime1/pull/6), merged 2026-11-25, merge commit `70229fbc`.
- PR #7 — [Remove unverified vacation candidates](https://github.com/kanlerxz87-cyber/Freetime1/pull/7), merged 2026-11-25, merge commit `ffe54b8a`.
- GitHub Pages deployment for `ffe54b8a` completed successfully in run [45629717700](https://github.com/kanlerxz87-cyber/Freetime1/actions/runs/45629717700). Public site: https://kanlerxz87-cyber.github.io/Freetime1/ . Pages API reports status `built`.
- Public pages were fetched after deployment with a cache-busting query to verify the updated landing, scoreboard, vacation assessment, and flagged-review content.

## Supplemental verification dashboard — cf033448

- Preserved the concurrently merged site from PR #1. An add/add conflict in the task board was resolved by retaining that board and appending this handoff. The supplemental page was moved out of the existing landing page scope.
- [PR #2](https://github.com/kanlerxz87-cyber/Freetime1/pull/2) publishes `daily-source-check.html` separately. GitHub records merge and deployment status.
| Coverage gaps | needs review | cf033448 | docs/, index.html |

- Audited 35 visible upcoming listings from the [official Westwood One NFL schedule](https://www.westwoodonesports.com/nfl-schedule/); copied national airtimes in Pacific time, retaining TBD matchup labels. Does not establish local clearances or any broadcasts omitted from the page.
- Read [Stanford](https://gostanford.com/sports/football/schedule), [Cal](https://calbears.com/sports/football/schedule/2026), [NFL](https://www.nfl.com/super-bowl/halftime-show), [MLB spring announcement](https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule), and [Warriors radio announcement](https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824). See Flagged for Review for missing coverage. MLB API was not reachable from the sandbox; runtime retrieval and completeness are not verified.
- Local tests cover interval merging, midnight clipping, daylight-saving boundaries, snapshot shape and internal links; these are not checks of every external URL or schedule.

## Concurrent branch reconciliation — arena/bf7d526d-freetime1

- 2026-11-25 — This Arena branch was created from the original `a7d1d4a` base when no `COORDINATION.md` existed in its checkout. During `git pull --rebase origin main`, `origin/main` advanced to include merged PR #1 and PR #2, including the shared site, task board, and source-review work.
- A duplicate standalone planner had been created locally on this branch. To avoid overwriting the already-merged integration site or task-board records, that duplicate site commit is being omitted from the rebase. The PR #1/#2 files and records are preserved unchanged.
- No other session's file scope is being edited. Any independently verified issue discovered against the merged data will be logged as a request/handoff here, not silently changed in their owned pages or data.

## T6 completion and integration-owner request — arena/bf7d526d-freetime1

- T6 DONE: `sources/arena-bf7d526d-audit.md` records official-source checks and correction recommendations; each finding links to the corresponding league, team, or broadcaster source.
- The official-source corrections were applied in the follow-up safety PRs #6 and #7; the merged dashboard and navigation remain intact.
- In particular: MLB's official 2028 All-Star host/month is used without treating non-MLB dates as confirmed; Cal's partial 2027 dates and BYU/ODU conflict are shown; Stanford opponent allocation is separated from exact dates; Athletics/Cal radio source claims are updated; Westwood One's 2025 affiliate-list scope is stated; future Super Bowl claims are limited to directly verified data; game duration estimates are clearly separated from official statistics.

## Session arena/5bf1f962-freetime1 - separate planner in `docs/`

Branch: `arena/5bf1f962-freetime1` (from `main`). Scope: `docs/` only, plus this section and the README section. Root pages (`index.html`, `*.html`, `data/`, `tools/`, `sources/`) are NOT changed by this session.

| Task | Status | Owner session | File scope | Notes |
|---|---|---|---|---|
| D1 Source data (MLB live, Westwood One 35 games, 49ers 2026, Stanford/Cal 2026-27) | done | arena/5bf1f962 | `docs/data/*.json` | NFL radio rebuilt from the Westwood One page; unsourced items removed |
| D2 Free-time engine + scoreboard/calendar/windows | done | arena/5bf1f962 | `docs/assets/app.js`, `docs/scoreboard.html`, `docs/vacation.html` | Tested with JSDOM |
| D3 Subpages + Flagged for Review + Sources | done | arena/5bf1f962 | `docs/*.html`, `docs/assets/style.css` | |
| D4 Integration PR + merge + Pages check | in progress | arena/5bf1f962 | this section | Results below |

Reconciliation note: the root planner and `docs/` planner were built independently. Known differences to check: Feb-window lengths and the July All-Star week (`docs/` estimates Jul 12 as busy, since the Home Run Derby is not in the MLB feed). Neither planner overrides the other; flagged for review.

Results:
- PR: https://github.com/kanlerxz87-cyber/Freetime1/pull/4 (arena/5bf1f962-freetime1 -> main)
- Merge: merged 2026-11-25 13:56 UTC, merge commit f664bd1 (merge commit, not squash). Flagged items did not block.
- Pages: build for f664bd1 status "built" (no errors). Live: https://kanlerxz87-cyber.github.io/Freetime1/docs/scoreboard.html renders the new planner with live MLB data.
- Root site (PR #1/#2) unchanged.


## Session arena/f7d614e2 (2026-11-25)
- **Session ID:** `f7d614e2`
- **Branch:** `arena/f7d614e2-freetime1`
- **Scope:** Attempted full planner build; discovered main already had integrated site from prior sessions (PRs #4-#8 merged).
- **Actions:** Built an alternative static dashboard (index/calendar/schedule/sources/flagged-review + site/data/data.js) with verified 49ers 2026 (NFL.com), Westwood One 2026 NFL broadcasts, Stanford/Cal 2026, and 2027 MLB season landmarks. All values sourced/flagged; no inferred values.
- **Conflict resolution:** On rebase against updated main, resolved COORDINATION/README/index/sources conflicts by preserving main's integrated site (no other-session work discarded). Added non-conflicting artifacts under `site/`, `calendar.html`, `schedule.html`, `flagged-review.html`.
- **Verification performed:** Cross-checked extracted 49ers/Westwood One/Stanford/Cal rows against official pages fetched 2026-11-25. Flagged 2028-2029 MLB, 2027-2029 NFL, 2027-2029 NCAAF as estimated/TBD.
- **Irregularities:** Full per-game ingestion for all MLB 2027-2028 and all NFL 2027-2029 not complete; SF 94122 AM/FM per-game carriage unverified; A's 2027-2029 radio affiliate unverified. See `flagged-review.html` and `site/data/data.js` notes.
- **PR:** https://github.com/kanlerxz87-cyber/Freetime1/pull/9
- **Merge result:** Merged to `main` (merge commit on main, 2026-11-25). GitHub Pages build triggered (legacy, source main:/).

## Supplemental reconciliation — `arena/b5171da7-freetime1` (2026-11-25)

- The original coordination claim was committed and pushed as `7d3da8b` before research began. After fetching upstream, this branch found that PRs #1–#9 had already integrated the root dashboard and a live Pages deployment. To avoid replacing another session's site/data or Pages source, the separate prototype was withheld; branch history was merged with `main` preserving all upstream files.
- [PR #10 — Supplemental official-source reconciliation](https://github.com/kanlerxz87-cyber/Freetime1/pull/10) added only `sources/arena-b5171da7-research.md`; it did not modify the dashboard or schedule data. Merged 2026-11-25 at 14:14 UTC, merge commit `e74fd4c`.
- GitHub Pages deployment for `e74fd4c` completed successfully in run [45631857954](https://github.com/kanlerxz87-cyber/Freetime1/actions/runs/45631857954). Pages API reports `built`; live site remains https://kanlerxz87-cyber.github.io/Freetime1/.
- No 94122 reception test or comprehensive future schedule import was performed; all schedule uncertainty remains flagged in the published planner.

## Session `arena/e4a8480c-freetime1` — Full Verified 2,430-Game MLB 2027 + 109-Game NFL 2026 Planner (`planner/`, 2026-11-25)

- **Branch:** `arena/e4a8480c-freetime1` (merged with `origin/main` @ `018e4c8`, preserving 100% of root site, `docs/`, `site/`, and prior audit/coordination records unchanged).
- **File Scope:** `planner/` (6-page dashboard + `planner/assets/`), `data/mlb_2027_*.csv`, `data/mlb_teams.json`, `data/nfl_2026_*.csv`, `data/other_verified_events.json`, `data/bay_area_radio.json`, `data/flagged_review.json`, `scripts/build_data.py`, `scripts/verify_data.py`, plus appended sections in `README.md` & `COORDINATION.md`.
- **Key Verified Additions (Addressing Prior Sessions' Incomplete Full-Schedule Ingestion):**
  - Fetched and checksum-verified **all 2,430 official 2027 MLB Regular Season games** from `statsapi.mlb.com` (all 30 teams = exactly 162 games each, 0 duplicates, 594 `startTimeTBD=true` explicitly flagged rather than misrepresented as verified).
  - Fetched **all 474 official 2027 MLB Spring Training & Exhibition games** (Feb 19 – Mar 23, 2027) + 97th All-Star Game (Jul 13, 2027) + Field of Dreams (Aug 12) + Little League Classic (Aug 19).
  - Fetched **all 109 remaining official 2026 NFL Regular Season games** (Weeks 12–18, Nov 25, 2026 – Jan 10, 2027) with exact `nfl.com/games/...` URLs and flex pools.
  - Verified NFL Aug 27, 2026 Pro Bowl game discontinuation (`https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested`), identifying a **13-day zero-game window (Feb 1–13, 2027)** in Strict Mode alongside the **37-day verified Regular+Postseason window (Feb 15–Mar 23, 2027)**.
  - Verified NFL Rulebook Rule 4-1-3 (**13-minute** official halftime), NCAA Rule 3-2-2 (**20-minute** official halftime), Cal 2026 record (3–8, not bowl-eligible), Stanford 2026 (6–5, bowl-eligible -> Dec bowl TBD flagged), San Jose Sharks streaming-only audio (no terrestrial AM/FM since 2021), SF 49ers Spanish streaming-only in Bay Area (`49ers.com/esp`), and SF Giants Spanish flagship KSFN 1510 AM.
- **Verification (`scripts/verify_data.py` + local HTTP 200 + `node --check`):**
  - 2,430 / 2,430 unique MLB 2027 regular games (all 30 teams × 162); 109 / 109 NFL Weeks 12–18 games; 3,181 / 3,181 compiled events with official `https://` source links; all 6 `planner/*.html` pages pass ref/JS/HTTP-200 checks.
- **PR:** https://github.com/kanlerxz87-cyber/Freetime1/pull/12 (`arena/e4a8480c-freetime1` -> `main`).
- **Live URL (after merge):** https://kanlerxz87-cyber.github.io/Freetime1/planner/

---

## Session `arena-1d4ebaad` (`arena/1d4ebaad-freetime1`) — Non-Overlapping Multi-Tier PST Vacation Hub & Line-by-Line Repo Audit (`vacation-hub/**`)

### Conflict Resolution & Scope Isolation Log
- **2026-11-25 (`arena-1d4ebaad`)**: Synced cleanly onto `origin/main` across PRs #1–#12. When PR #12 (`arena/e4a8480c-freetime1`) merged its dashboard under `planner/`, we relocated our self-contained 8-page suite from `planner/` to **`vacation-hub/`** so zero files from PRs #1–#12 (root, `docs/`, `site/`, `planner/`, `data/`, `tools/`, `scripts/`, `sources/`) were overwritten or discarded.

### Completed Tasks (`arena-1d4ebaad`)

| ID | Task | Status | Owner session | Files in scope |
|----|------|--------|---------------|----------------|
| T7 | Line-by-line official-source code & data audit of existing repository files, URLs, schedules, and scoreboard/computation defects | `done` | `arena-1d4ebaad` | `vacation-hub/repo-audit.html`, `vacation-hub/data/repo_audit.json`, `COORDINATION.md` |
| T8 | Official source verification: MLB (30 clubs, all 195 Giants & 193 Athletics 2027 games + 2026/2027 daily league counts from `statsapi.mlb.com`), NFL/49ers/Pro Bowl abolition/Super Bowls, Stanford & Cal NCAAF (2026–2029), Westwood One 35 NFL + NCAA broadcasts, Outer Sunset SF 94122 AM/FM dial & all live radio sports (Warriors, Valkyries, Earthquakes, NCAA, Sharks digital exclusion), and official game/halftime durations | `done` | `arena-1d4ebaad` | `vacation-hub/data/*.json`, `vacation-hub/scripts/build_planner_data.py`, `vacation-hub/scripts/save_raw_mlb.py` |
| T9 | Interactive PST daily scoreboard & calendar (2026–2029, multi-game per day, halftime windows, minute-by-minute free intervals) + 1/2/3-week vacation analyzer across 4 listener tiers | `done` | `arena-1d4ebaad` | `vacation-hub/index.html`, `vacation-hub/core-games.html`, `vacation-hub/scoreboard.html`, `vacation-hub/radio-94122.html`, `vacation-hub/assets/*` |
| T10 | Master verified tables (official links per row, blank unconfirmed values), durations methodology, Flagged for Review page, link/build checks, PR to `main`, merge & GitHub Pages deploy check | `done` | `arena-1d4ebaad` | `vacation-hub/verified-schedules.html`, `vacation-hub/durations.html`, `vacation-hub/flagged-for-review.html`, `vacation-hub/scripts/verify_planner.py`, `README.md`, `COORDINATION.md` |
| T10-flags | Unconfirmed future dates/times (`FLG-01`–`FLG-08`) & repo audit flags (`AUDIT-01`–`AUDIT-10`) published on `vacation-hub/flagged-for-review.html` | `needs review` | `arena-1d4ebaad` | `vacation-hub/flagged-for-review.html`, `vacation-hub/repo-audit.html` |

### Sources, Verification & Logged Requests (`arena-1d4ebaad`)
- **Primary Official Sources Linked**: `statsapi.mlb.com` (`sportId=1`, 1,020 unique official `https://` URLs verified), `mlb.com`, `nfl.com` (2026–27 Important Dates, Aug 27 2026 Pro Bowl game discontinuation, Super Bowls LXII/LXIII/LXIV), `media.nfl.com`, `operations.nfl.com`, `49ers.com`, `westwoodonesports.com` (35 NFL + 4 NCAA upcoming event pages), `gostanford.com`, `calbears.com` (`KSFO 810 AM` + June 25 2026 non-conf release), `collegefootballplayoff.com`, `nba.com/warriors` (`95.7 The Game`), `valkyries.wnba.com` (`95.7 The Game`), `sjearthquakes.com` (`KSFO 810 AM` / `KZSF 1370 AM`), `nhl.com/sharks` (digital-only `Sharks Audio Network`).
- **Automated Verification**: `python3 vacation-hub/scripts/verify_planner.py` (8 HTML pages, 0 broken internal links, 1,020 unique official `https://` URLs, 0 non-official hosts, strict blank `""` on `startTimeTBD=true`, 1,461 daily records), plus `python3 scripts/verify_data.py` and `node scripts/test.mjs` all passing.
- **Logged Change Requests for Root Files Owned by `arena-9f5f3a65` (Not Edited Directly)**:
  1. `tools/build_data.py`: Replace blanket `Postseason wd in (0,5,6)` busy rule with official NFL playoff round dates + Aug 27, 2026 Pro Bowl abolition (`Feb 1–13, 2027` is 13 days free); mark `2026-11-25` busy (`events/548511`); remove `2026-07-16` & `2027-07-15` from `allstar_breaks` (`totalGames=1` in StatsAPI); end 2026 World Series on `2026-10-28`.
  2. `assets/app.js`: Change `westwood_2026_verified.find(...)` at L48 to `.filter(...)` so multi-game holiday slates render all broadcasts; filter `renderWindowsTable` per league subpage.

