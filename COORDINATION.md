# Coordination board

| Task | Status | Owner/session | File scope |
|---|---|---|---|
| Build evidence-led vacation-planning dashboard and source/limitations pages; populate available verified records | done | `arena/6c361796-freetime1` | `index.html`, `styles.css`, `app.js`, `football.html`, `mlb.html`, `radio.html`, `review.html`, `sources.html`, `README.md`, `.github/workflows/pages.yml`, `.nojekyll`, `COORDINATION.md` |

## Log

### Claim
- Claim recorded 2026-11-25. Repository initially contained only `README.md`; no coordination board or task claims existed. Work stayed on the active Arena branch `arena/6c361796-freetime1`; the initial claim was committed and pushed after rebasing on `origin/main`.

### Completion and verification — 2026-11-25
- Built the static multi-page GitHub Pages dashboard: Overview/calendar, MLB club directory, Football, Radio, Source Register, and Flagged for Review. The calendar uses date navigation and selected-day detail; blanks/source failures remain unknown and the 1/2/3-week finder refuses to certify a window while schedules or broadcasts are incomplete.
- Source verification performed against official primary sources:
  - MLB Stats API schedule endpoint (`https://statsapi.mlb.com/api/v1/schedule`): directly queried the official endpoint, verified the 2027 regular-season response reported 2,430 scheduled games, and inspected returned official game records with dates, status, team names and venue. Overview queries the official API by displayed month; result links point to MLB game records.
  - Cal Athletics official announcements: confirmed 2027 Cal–Florida on Sep. 4; 2028 Wyoming (Sep. 2), San José State (Sep. 9), Minnesota (Sep. 16); 2029 Wisconsin (Sep. 1) and Wyoming (Sep. 8). Kickoff times remain blank. Sources are individually linked on each Football table row: `https://calbears.com/news/2020/2/7/football-cal-and-florida-schedule-home-and-home-series-in-2026-and-2027`, `https://calbears.com/news/2020/2/11/football-cal-adds-minnesota-and-wyoming-to-future-schedules`, `https://calbears.com/news/2025/1/30/football-bears-announce-future-games-against-san-jose-state-wagner`, `https://calbears.com/news/2024/3/26/cal-wisconsin-to-meet-in-2029-2030`, and `https://calbears.com/news/2022/4/15/football-cal-minnesota-move-berkeley-game-up-to-2025`.
  - NFL official 2026–27 key dates and schedule portal; official 49ers schedule destination; official Stanford athletics schedule destination. No unsupported future game rows were generated.
  - Westwood One NFL Station Finder Source lists KNBR-AM, KNBR-F2, KNBR-FM and KTCT-AM for San Francisco, CA. The page is explicitly scoped to market listing, not event-level carriage/reception.
  - MLB official news source supports the 2025 nine-inning average duration of 2:38; it is contextual only, never used as an event end time.
- Checks: `node --check app.js`; `git diff --check`; all six HTML pages parsed; local HTML/CSS/JS references checked (none missing); local HTTP preview returned HTTP 200 for index, all subpages, CSS and JS.
- Irregularities and incomplete coverage are recorded on `review.html`: full future NFL/49ers and Stanford schedules; unfilled future MLB schedules outside currently available official data; complete per-game Westwood One / local affiliate clearance; other local sports scan; exact game end times/free minutes; and reception testing in Outer Sunset 94122. No free vacation period is asserted because these gaps materially affect the user’s definition of free.
- Publishing status: static Pages workflow added. The site is not claimed live until the workflow and repository Pages configuration succeed after merge.
