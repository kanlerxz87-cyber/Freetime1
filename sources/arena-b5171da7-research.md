# Supplemental official-source reconciliation — `arena/b5171da7-freetime1`

**Session:** `b5171da7`  
**Checked:** 2026-11-25 (UTC)  
**Purpose:** preserve current official source findings after this branch discovered that `main` had already advanced through PRs #1–#9 and published the integrated planner. This is a supplemental audit, not a replacement for `sources/verification-log.md`, the live site, or other session-owned data.

## Integration and publication decision

A fresh `git fetch origin main` showed `main` at `71b366b`, including the previously merged source audit, safety fixes and alternate planner work. GitHub Pages API reported `status: built`, `source: main:/`, `url: https://kanlerxz87-cyber.github.io/Freetime1/`; the current homepage, scoreboard, vacation page and flagged page were fetched successfully. The published site explicitly says no week can be certified sports-free, and its day gaps are not certified free time.

Because `main` already has an active root site, a `/docs/` planner and a `site/` subdirectory, this session did **not** replace the root site or add a competing Pages deployment workflow. The additive audit file is kept separate so it does not overwrite another session's site/data scope. The existing published site and its legacy root Pages configuration remain authoritative.

## MLB — official 2027 feed and special events

- MLB's official 2027 release says the season begins March 24 with an Opening Night game on Netflix; traditional Opening Day is March 25 with 14 games. It names July 12 for the Home Run Derby and July 13 for the All-Star Game at Wrigley Field, and states Spring Breakout returns without giving its game dates. [Official MLB release](https://www.mlb.com/giants/news/mlb-2027-schedule-released)
- Official StatsAPI date queries reported 17 Spring Training games on Feb. 19, 2027; one game on Mar. 24; 14 on Mar. 25; and 15 on Sept. 26. The counts are returned in API metadata. The larger payloads were chunked by the web fetch tool. [Official StatsAPI sample date](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&startDate=2027-02-19&endDate=2027-02-19)
- The MLB release's initial Opening Night narrative says the matchup is TBD, while a later query of the official StatsAPI returned Boston at Seattle for official date March 24. This is a release-copy/feed-update discrepancy; a live schedule row should follow the current feed, not stale prose.
- The 2027 regular-season schedule is published, but postseason participants, bracket and game-level times are not. Do not estimate a postseason date range as a verified schedule.
- Oracle Park is officially named as the 2028 All-Star host. The exact 2028 date was not stated in MLB's official future-locations page. [MLB future All-Star locations](https://www.mlb.com/all-star/future-locations)
- MLB 2028–2029 future pages reviewed did not supply day-by-day rows. Empty future feed results remain unknown, not free.
- All 30 MLB club pages should remain linked; prioritize Giants (MLB team ID 137) and Athletics (ID 133). The official date API is a schedule, not proof each game airs on a Bay Area AM/FM station.

## NFL, Super Bowls and Westwood One

- Official NFL 2027 and 2028 team schedule pages returned **“SCHEDULE DATA UNAVAILABLE.”** No regular-season or postseason matchup/time rows should be invented. [NFL 2027](https://www.nfl.com/schedules/2027/by-team) · [NFL 2028](https://www.nfl.com/schedules/2028/by-team)
- Super Bowl LXI is confirmed for Feb. 14, 2027 at SoFi Stadium; kickoff and teams are not entered from that source. [NFL Operations important dates](https://operations.nfl.com/calendar-events/nfl-important-dates)
- Super Bowl LXII's host is Mercedes-Benz Stadium in Atlanta (2028); Super Bowl LXIII's host is Allegiant Stadium in Las Vegas (2029). Those host announcements do not give game dates, kickoff or teams. [LXII](https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028) · [LXIII](https://www.nfl.com/news/las-vegas-to-host-super-bowl-lxiii-in-2029)
- Westwood One's public NFL schedule at capture lists the 2026 season into January 2027, not its 2027–2029 broadcasts. The official station finder lists San Francisco NFL market callsigns KNBR-AM, KNBR-F2, KNBR-FM and KTCT-AM, without mapping each to an exact frequency or guaranteeing individual game clearance. [WWO schedule](https://www.westwoodonesports.com/nfl-schedule/) · [WWO station finder](https://www.westwoodonesports.com/station-finder/)

## Cal and Stanford football

- Cal's official 2027 nonconference announcement lists Sacramento State at Cal Aug. 28, Cal at UCLA Sept. 4, and Old Dominion at Cal Sept. 11; kickoffs and 2027 radio terms were not provided. [Cal 2027 nonconference dates](https://calbears.com/news/2026/6/25/football-cal-announces-odu-sac-state)
- Cal's 2027 ACC opponent grid is official; dates and times remain TBD. [Cal 2027 opponents](https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents)
- Stanford's 2027 ACC opponent grid is official; it says the Big Game will be at Stanford, but the exact date remains TBD. [Stanford 2027 opponents](https://gostanford.com/news/2026/09/16/acc-announces-2027-conference-opponents)
- Stanford–Notre Dame dates are confirmed for Nov. 27, 2027 (at Stanford) and Oct. 14, 2028 (at Notre Dame). [Stanford series announcement](https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry)
- Cal has current official nonconference dates for Cal–UCLA (Sept. 2, 2028), Cal–San José State (Sept. 9, 2028), Cal at Minnesota (Sept. 16, 2028), Wisconsin at Cal (Sept. 1, 2029), Cal at Wyoming (Sept. 8, 2029), and Cal at UCLA (Sept. 15, 2029). The Minnesota date should link to Cal's 2022 rescheduling update; the 2029 Wyoming date appears in the later Cal–UCLA future schedule. [Cal–Minnesota update](https://calbears.com/news/2022/4/15/football-cal-minnesota-move-berkeley-game-up-to-2025) · [Cal 2026–2029 schedule](https://calbears.com/news/2024/7/10/football-cal-ucla-schedule-4-games-from-2026-29)
- **Cal date conflict:** a 2020 release places Cal–Wyoming at home Sept. 2, 2028, but the later official Cal–UCLA schedule places UCLA at Cal on that date. Do not place two home games on the same date; keep Wyoming's 2028 home date flagged/blank pending resolution.
- **Stanford stale nonconference rows:** the 2016 Boston College series release gave Sept. 2, 2028 and Sept. 15, 2029, while a 2023 ACC model lists BC as a 2029 home opponent. Because those future dates have not been recently reconfirmed, the 2028 date and 2029 date are not treated as confirmed calendar dates. Stanford's 2015 Vanderbilt Sept. 11, 2027 entry is also not carried forward absent current confirmation. Stanford formally cancelled its Sept. 4, 2027 TCU game on Apr. 17, 2026. [BC series](https://gostanford.com/news/2016/06/14/boston-college-series) · [ACC 2024–2030 model](https://theacc.com/news/2023/10/30/acc-announces-future-conference-football-schedule-model.aspx) · [TCU cancellation](https://gostanford.com/news/2026/04/17/tcu-series-update)
- Stanford–San José State is scheduled for Nov. 25, 2028 in the current 2025 Stanford update. [Stanford schedule update](https://gostanford.com/news/2025/12/16/updates-to-2026-schedule)

## Bay Area sports radio — current/season-specific evidence

- Giants: English KNBR 680 AM / 104.5 FM; Spanish KSFN 1510 AM and KXZM 93.7 FM. [Giants listen page](https://www.mlb.com/giants/schedule/tv)
- Athletics: the official affiliate page lists KNEW 960 AM for the Bay Area; current carriage on each game and reception at an Outer Sunset address are not proven by the listing. [Athletics affiliate page](https://www.mlb.com/athletics/schedule/watch)
- 49ers: official team materials list KNBR 680 AM / 104.5 FM and KSAN 107.7 FM; some 2026 materials also mention KSFO 810 AM. Future game-by-game radio assignments are not inferred. [49ers radio partners](https://www.49ers.com/fans/tv-radio)
- Warriors: official 2026–27 announcement says 95.7 The Game carries all preseason and regular-season games; NBA dates are not integrated into the partial vacation model. [Warriors 2026–27 radio](https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824)
- Sharks: the official 2026–27 schedule labels its audio as the Sharks Audio Network and does not name an AM/FM station. Older KFOX 98.5 references are not current carriage proof. [Sharks 2026–27 schedule](https://www.nhl.com/sharks/news/san-jose-sharks-announce-broadcast-schedule-for-2026-27-season)
- Earthquakes: official 2026 radio release names KSFO 810 AM English and KZSF 1370 AM Spanish. [Earthquakes 2026 radio](https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season)
- Other college examples verified by official sources: USF men's basketball on KNBR 1050 for 2026–27; Cal men's basketball game listings on KSFO 810 AM with a KALX 90.7 FM game example; SJSU men's basketball on KTRB 860 AM for a cited 2026 game; Stanford baseball on KZSU 90.1 FM for selected 2026 games. SJSU's 2026 football announcement names its digital audio network, not an AM/FM frequency; Stanford's 2026 men's basketball preview lists online audio options rather than terrestrial AM/FM. These are station findings, not complete radio-game feeds. [USF](https://usfdons.com/news/2026/11/12/mens-basketball-usf-increases-coverage-on-knbr-with-live-airings-of-hilltop-hoops-hour-on-youtube) · [Cal schedule](https://calbears.com/sports/mens-basketball/schedule) · [SJSU basketball](https://sjsuspartans.com/news/2026/02/27/spartans-return-home-to-face-colorado-state-on-mountain-west-network) · [Stanford baseball](https://gostanford.com/news/2026/03/12/cardinal-welcomes-pitt-in-acc-play) · [SJSU football broadcast](https://sjsuspartans.com/news/2026/08/26/sjsu-legend-james-jones-and-coaching-legend-greg-kampe-to-join-2026-football-radio-broadcast) · [Stanford basketball](https://gostanford.com/news/2026/10/30/mens-basketball-hosts-eastern-washington-in-season-opener)
- KNBR's official grid is rolling and date-specific. The captured Nov. 16–22, 2026 week lists game-specific Cal–Stanford, Westwood One, NFL, and 49ers pre/postgame blocks; do not treat that week as a permanent template. [KNBR weekly schedule](https://www.thesportsleader.com/shows/)
- No 94122 building-level AM/FM field test, address-specific signal study, or complete inventory of every receiver/affiliate has been performed. Affiliation is not reception.

## Duration assumptions / vacation-window caution

- The dashboard's **2:38** nine-inning MLB duration default is based on MLB's reported historical 2025 regular-season average; it is not an official future end time. [MLB duration reference](https://www.mlb.com/news/mlb-increased-attendance-3rd-straight-season)
- Any 200-minute All-Star/postseason or 240-minute football blocks are rough planning estimates, not station airtimes. Pregame, postgame, extra innings, overtime and delays are not modeled.
- A schedule row does not prove the broadcast is available on standard AM/FM in 94122. No 1-, 2- or 3-week 2027–2029 window is certified free on this source set.

## Status and validation

- This source note records verified facts and unresolved conflicts only; it does not change the merged site or other session-owned schedule files.
- At capture, GitHub Pages reports `built` at `https://kanlerxz87-cyber.github.io/Freetime1/`; run `45630744408` completed successfully. Main already contains merged PRs #1–#9.
- A separate seven-page prototype was locally audited on this branch, but was deliberately not published because `main` already contains the root site, `/docs/` planner, `/site/` files and a live legacy Pages deployment. The prototype would compete for the existing route and has not been merged.
- This audit itself contains no generated schedule rows; all date/time unknowns remain blank or flagged.
