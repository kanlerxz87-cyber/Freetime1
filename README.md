# Free Time Vacation — Bay Area sports planner

A static, GitHub Pages-ready dashboard for reviewing confirmed sports schedule entries that may interrupt live-radio time in San Francisco (Outer Sunset 94122). It deliberately does **not** mark a day or trip as free just because one schedule source returns no game.

## Pages

- `index.html` — calendar, selected-day scoreboard, and a conservative 1/2/3-week vacation-window result.
- `mlb.html` — 30-club directory and official MLB schedule API method.
- `football.html` — official source links, verified dated Cal fixtures, and unverified schedule fields.
- `radio.html` — Westwood One NFL market affiliate listings and station/source scope limits.
- `sources.html` — source register.
- `review.html` — explicit gaps and irregularities blocking a free-window assertion.

## Data policy

- Calendar MLB data is requested from the official MLB Stats API at `https://statsapi.mlb.com/api/v1/schedule` for the displayed month. Each returned game links to its official MLB game record. The selected-month API URL is shown on the MLB page and beside the load status.
- Cal fixtures are included only when an official Cal Athletics announcement explicitly identifies a game date. Their kickoff times remain blank because they are not verified in the cited releases.
- Future NFL and Stanford rows are not generated from usual league patterns. No per-game radio carriage or exact event end time is inferred.
- NFL / Westwood One market affiliate information and team/league schedule links are provided as review sources. A station finder entry is not a reception or game-specific carriage guarantee for 94122.
- A game-duration average is context only. MLB’s cited 2025 nine-inning average is 2:38; it is not used to fabricate an individual end time. Football elapsed duration and stoppage/halftime details are not treated as a universal exact duration.
- Time labels use `America/Los_Angeles` (PT), changing between PST and PDT. No DST conversion is silently labeled PST year-round.

Because the complete future schedules and radio carriage are not verified for every requested league and date range, the current result is **no certifiable 1-, 2-, or 3-week free window**. This means unknown/incomplete evidence, not “games every day.” See `review.html` for the source-by-source gaps.

## Run locally

Open `index.html` in a modern browser or serve the repository root with a static HTTP server. The overview needs browser network access to `statsapi.mlb.com`; if blocked or offline, it reports an error and keeps the selected day unknown.

## Verification notes

All hand-entered future fixture rows carry a direct official source link on the Football page. MLB game rows are created from the official schedule response and link to their official game records. The source register and flagged-for-review page identify limitations rather than presenting unsourced values as facts. Current data assessment date: 2026-11-25.
