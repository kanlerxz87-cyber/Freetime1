# Coordination

| Task | Status | Owner | Scope |
|---|---|---|---|
| Initial integration | done | cf033448 | docs/, scripts/, README.md, index.html, .nojekyll |
| Coverage gaps | needs review | cf033448 | docs/, index.html |

- Audited 35 visible upcoming listings from the [official Westwood One NFL schedule](https://www.westwoodonesports.com/nfl-schedule/); copied national airtimes in Pacific time, retaining TBD matchup labels. Does not establish local clearances or any broadcasts omitted from the page.
- Read [Stanford](https://gostanford.com/sports/football/schedule), [Cal](https://calbears.com/sports/football/schedule/2026), [NFL](https://www.nfl.com/super-bowl/halftime-show), [MLB spring announcement](https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule), and [Warriors radio announcement](https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824). See Flagged for Review for missing coverage. MLB API was not reachable from the sandbox; runtime retrieval and completeness are not verified.
- Local tests cover interval merging, midnight clipping, daylight-saving boundaries, snapshot shape and internal links; these are not checks of every external URL or schedule.
