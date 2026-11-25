// Freetime1 Planner App (Session arena-1d4ebaad, scope: vacation-hub/**)
// All schedule calculations in PST (UTC-8), with official sources linked on every row.

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[c]));

function badgeForStatus(st) {
  const u = String(st || "").toUpperCase();
  if (u.startsWith("VERIFIED")) return `<span class="badge verified">${esc(st)}</span>`;
  if (u.includes("PARTIAL") || u.includes("TBD") || u.includes("REVIEW")) return `<span class="badge partial">${esc(st)}</span>`;
  if (u.includes("ESTIMATED")) return `<span class="badge estimated">${esc(st)}</span>`;
  return `<span class="badge unverified">${esc(st || "UNVERIFIED")}</span>`;
}

function priorityBadge(p) {
  return String(p || "").includes("HIGH")
    ? `<span class="badge high">${esc(p)}</span>`
    : `<span class="badge">${esc(p || "STANDARD")}</span>`;
}

function catClass(cat) {
  const c = String(cat || "").toLowerCase();
  if (c.includes("westwood")) return "cat-westwood";
  if (c.includes("mlb")) return "cat-mlb";
  if (c.includes("nfl")) return "cat-nfl";
  if (c.includes("ncaaf")) return "cat-ncaaf";
  return "cat-other";
}

function mmTo12h(m) {
  const clamped = Math.max(0, Math.min(1440, m));
  if (clamped === 1440) return "12:00 AM";
  const h = Math.floor(clamped / 60);
  const mm = clamped % 60;
  const ap = h < 12 ? "AM" : "PM";
  const hh = h % 12 || 12;
  return `${hh}:${String(mm).padStart(2, "0")} ${ap}`;
}

function fmtLongDate(iso) {
  const d = new Date(iso + "T12:00:00Z");
  return d.toLocaleDateString("en-US", {
    timeZone: "UTC", weekday: "long", year: "numeric", month: "long", day: "numeric"
  });
}

function addDaysISO(iso, delta) {
  const d = new Date(iso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + delta);
  return d.toISOString().slice(0, 10);
}

async function fetchJSON(relPath) {
  const r = await fetch(relPath);
  if (!r.ok) throw new Error(`Failed loading ${relPath}: ${r.status}`);
  return r.json();
}

// ---------------------------------------------------------------------------
// 1. EXECUTIVE SUMMARY / VACATION WINDOWS (index.html)
// ---------------------------------------------------------------------------
async function initExecutiveSummary() {
  const vacEl = document.getElementById("vacation-tier-table");
  const bridgeEl = document.getElementById("bridge-windows-table");
  if (!vacEl && !bridgeEl) return;

  const vac = await fetchJSON("data/vacation_analysis.json");
  let activeTier = "core_strict";
  let activeYear = "all";

  function renderRuns() {
    if (!vacEl) return;
    const tierObj = vac.tiers[activeTier];
    let rows = activeYear === "all"
      ? tierObj.top_runs
      : (tierObj.by_year[activeYear] || []);

    const trs = rows.map((r) => `
      <tr>
        <td><strong>${esc(r.year)}</strong></td>
        <td><strong><a href="scoreboard.html#${esc(r.start)}">${esc(r.start)}</a> → <a href="scoreboard.html#${esc(r.end)}">${esc(r.end)}</a></strong></td>
        <td><strong>${r.days} days</strong> (${r.weeks} wks)</td>
        <td>${r.fits_1wk ? "✅ Yes" : "❌ No"}</td>
        <td>${r.fits_2wk ? "✅ Yes" : "❌ No"}</td>
        <td>${r.fits_3wk ? "✅ Yes" : "❌ No"}</td>
        <td class="small">After: ${esc(r.bounded_after)}<br>Before: ${esc(r.bounded_before)}</td>
        <td>${badgeForStatus(r.verification_status)}</td>
        <td><a href="https://www.nfl.com/news/2026-27-national-football-league-important-dates" target="_blank" rel="noopener">nfl.com</a> · <a href="https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule" target="_blank" rel="noopener">mlb.com</a></td>
      </tr>
    `).join("") || `<tr><td colspan="9">No multi-day zero-game runs for this filter.</td></tr>`;

    vacEl.innerHTML = `
      <p class="small" style="margin:4px 0 10px"><strong>${esc(tierObj.name)}:</strong> ${esc(tierObj.description)}</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th>Zero-Game Window</th>
              <th>Length</th>
              <th>1 Wk (7d)</th>
              <th>2 Wks (14d)</th>
              <th>3 Wks (21d)</th>
              <th>Bounding Broadcasts</th>
              <th>Status</th>
              <th>Official Sources</th>
            </tr>
          </thead>
          <tbody>${trs}</tbody>
        </table>
      </div>
    `;
  }

  document.querySelectorAll("[data-tier-btn]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-tier-btn]").forEach((b) => b.classList.remove("active-tab"));
      btn.classList.add("active-tab");
      activeTier = btn.dataset.tierBtn;
      renderRuns();
    });
  });

  document.querySelectorAll("[data-year-btn]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-year-btn]").forEach((b) => b.classList.remove("active-tab"));
      btn.classList.add("active-tab");
      activeYear = btn.dataset.yearBtn;
      renderRuns();
    });
  });

  renderRuns();

  if (bridgeEl) {
    bridgeEl.innerHTML = `
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th>Combined February Span</th>
              <th>Free Days</th>
              <th>Only Broadcast in Entire Span</th>
              <th>Why This Solves 2-Week Strict Planning</th>
              <th>Status</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
            ${vac.one_game_bridge_windows.map((b) => `
              <tr>
                <td><strong>${b.year}</strong></td>
                <td><strong>${esc(b.window)}</strong> (${b.total_days}d)</td>
                <td><strong>${b.free_days} / ${b.total_days} days</strong></td>
                <td>${esc(b.single_conflict)}</td>
                <td>${esc(b.why_it_matters)}</td>
                <td>${badgeForStatus(b.status)}</td>
                <td><a href="${esc(b.source_url)}" target="_blank" rel="noopener">Official NFL Announcement</a></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }
}

// ---------------------------------------------------------------------------
// 2. INTERACTIVE DAILY PST SCOREBOARD & CALENDAR (scoreboard.html)
// ---------------------------------------------------------------------------
async function initScoreboardPage() {
  const rootEl = document.getElementById("scoreboard-day-panel");
  if (!rootEl) return;

  const calData = await fetchJSON("data/daily_calendar.json");
  const dayMap = new Map(calData.days.map((d) => [d.d, d]));

  let currentISO = "2026-11-25";
  const hashDate = (location.hash || "").replace("#", "");
  if (/^\d{4}-\d{2}-\d{2}$/.test(hashDate) && dayMap.has(hashDate)) {
    currentISO = hashDate;
  }
  let currentTier = "core_strict";
  let includePrePost = false;

  const dateInput = document.getElementById("sb-date");
  const monthSelect = document.getElementById("sb-month");
  const tierSelect = document.getElementById("sb-tier");
  const bufferCheck = document.getElementById("sb-buffer");

  if (monthSelect) {
    let opts = "";
    for (let y = 2026; y <= 2029; y++) {
      for (let m = 1; m <= 12; m++) {
        const ym = `${y}-${String(m).padStart(2, "0")}`;
        const lbl = new Date(Date.UTC(y, m - 1, 1)).toLocaleDateString("en-US", {
          timeZone: "UTC", month: "long", year: "numeric"
        });
        opts += `<option value="${ym}">${lbl}</option>`;
      }
    }
    monthSelect.innerHTML = opts;
    monthSelect.addEventListener("change", () => {
      const target = `${monthSelect.value}-01`;
      if (dayMap.has(target)) selectDate(target);
    });
  }

  function computeIntervals(events) {
    const pre = includePrePost ? 30 : 0;
    const post = includePrePost ? 15 : 0;
    const adj = events.map((e) => ({
      ...e,
      effStart: Math.max(0, e.start_pst - pre),
      effEnd: Math.min(1440, e.end_pst + post),
    })).sort((a, b) => a.effStart - b.effStart);

    const merged = [];
    for (const ev of adj) {
      if (!merged.length || ev.effStart > merged[merged.length - 1].end) {
        merged.push({ start: ev.effStart, end: ev.effEnd });
      } else {
        merged[merged.length - 1].end = Math.max(merged[merged.length - 1].end, ev.effEnd);
      }
    }
    const free = [];
    let cur = 0;
    for (const b of merged) {
      if (b.start > cur) free.push({ start: cur, end: b.start });
      cur = Math.max(cur, b.end);
    }
    if (cur < 1440) free.push({ start: cur, end: 1440 });
    const busyMins = merged.reduce((s, x) => s + (x.end - x.start), 0);
    return { adj, merged, free, freeMins: 1440 - busyMins, busyMins };
  }

  function renderCalendarMonth(ym) {
    const grid = document.getElementById("sb-cal-grid");
    const summaryEl = document.getElementById("sb-month-summary");
    if (!grid) return;
    const [y, m] = ym.split("-").map(Number);
    const firstDow = new Date(Date.UTC(y, m - 1, 1)).getUTCDay();
    const daysInMonth = new Date(Date.UTC(y, m, 0)).getUTCDate();

    let freeCount = 0;
    let html = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
      .map((d) => `<div class="cal-dow">${d}</div>`).join("");
    for (let i = 0; i < firstDow; i++) html += `<div></div>`;
    for (let d = 1; d <= daysInMonth; d++) {
      const iso = `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
      const rec = dayMap.get(iso);
      const isFree = rec ? rec.free[currentTier] : true;
      if (isFree) freeCount++;
      const cls = `cal-day ${isFree ? "is-free" : "is-busy"}${iso === currentISO ? " is-selected" : ""}`;
      html += `<button type="button" class="${cls}" data-cal-iso="${iso}" title="${iso}: ${isFree ? "100% FREE" : "BUSY"}">${d}</button>`;
    }
    grid.innerHTML = html;
    if (summaryEl) {
      summaryEl.innerHTML = `<strong>${freeCount}</strong> completely game-free days / <strong>${daysInMonth - freeCount}</strong> busy game days in this month under selected rule.`;
    }
    grid.querySelectorAll("[data-cal-iso]").forEach((btn) => {
      btn.addEventListener("click", () => selectDate(btn.dataset.calIso));
    });
  }

  function renderSelectedDay() {
    const rec = dayMap.get(currentISO);
    if (!rec) {
      rootEl.innerHTML = `<div class="callout warn">Date ${esc(currentISO)} is outside the 2026–2029 dataset.</div>`;
      return;
    }
    const tierEvents = rec.events.filter((e) => e.tiers.includes(currentTier));
    const { adj, free, freeMins, busyMins } = computeIntervals(tierEvents);
    const isAllDayFree = tierEvents.length === 0;

    const tlBlocks = adj.map((ev) => {
      const left = ((ev.effStart / 1440) * 100).toFixed(2);
      const width = (Math.max(1.2, ((ev.effEnd - ev.effStart) / 1440) * 100)).toFixed(2);
      return `<div class="tl-busy ${catClass(ev.category)}" style="left:${left}%;width:${width}%" title="${esc(ev.title)} (${mmTo12h(ev.effStart)}–${mmTo12h(ev.effEnd)} PST)">${esc(ev.category.split("—")[0].trim())}</div>`;
    }).join("");

    const scoreCards = adj.length
      ? `<div class="score-cards">${adj.map((ev) => `
          <div class="score-card ${catClass(ev.category)}">
            <div style="display:flex;justify-content:space-between;gap:6px;align-items:center">
              <span class="sc-time">${mmTo12h(ev.effStart)} – ${mmTo12h(ev.effEnd)} PST</span>
              ${priorityBadge(ev.priority)}
            </div>
            <div class="sc-title">${esc(ev.title)}</div>
            <div class="sc-meta">
              📻 ${esc(ev.radio)}<br>
              ⏱️ Halftime: ${esc(ev.halftime_pst)} · ${badgeForStatus(ev.status)} ·
              <a href="${esc(ev.source_url)}" target="_blank" rel="noopener">Official Source ↗</a>
            </div>
          </div>
        `).join("")}</div>`
      : `<div class="callout good"><strong>100% GAME-FREE DAY!</strong> Zero broadcasts are scheduled in this listener mode across all 1,440 minutes (12:00 AM – 12:00 AM PST). Ideal vacation day!</div>`;

    const freeRows = free.map((f) => {
      const mins = f.end - f.start;
      return `<tr>
        <td><strong>${mmTo12h(f.start)} – ${mmTo12h(f.end)} PST</strong></td>
        <td><span class="badge free-pill">FREE TIME</span></td>
        <td><strong>${mins} min</strong> (${(mins / 60).toFixed(2)} hrs)</td>
      </tr>`;
    }).join("");

    const evRows = adj.map((ev) => `
      <tr>
        <td><strong>${mmTo12h(ev.effStart)} – ${mmTo12h(ev.effEnd)} PST</strong></td>
        <td>${ev.official_time ? `<strong>${esc(ev.official_time)}</strong>` : `<span class="blank-cell">— (Blank / Unconfirmed)</span>`}</td>
        <td>${esc(ev.title)}</td>
        <td>${esc(ev.halftime_pst)}</td>
        <td>${esc(ev.radio)}</td>
        <td>${priorityBadge(ev.priority)}</td>
        <td>${badgeForStatus(ev.status)}</td>
        <td><a href="${esc(ev.source_url)}" target="_blank" rel="noopener">Verify ↗</a></td>
      </tr>
    `).join("") || `<tr><td colspan="8">Zero scheduled games on air today.</td></tr>`;

    rootEl.innerHTML = `
      <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px">
        <h2 style="margin:0">${esc(fmtLongDate(currentISO))}</h2>
        ${isAllDayFree
          ? `<span class="badge free-pill" style="font-size:0.9rem;padding:5px 12px">✅ FULL FREE DAY (24.0 hrs Free)</span>`
          : `<span class="badge busy-pill" style="font-size:0.9rem;padding:5px 12px">📻 BUSY GAME DAY (${(busyMins / 60).toFixed(1)} hrs Busy · ${(freeMins / 60).toFixed(1)} hrs Free)</span>`
        }
      </div>
      <p class="small" style="margin:6px 0 12px">
        Free minutes today: <strong>${freeMins} min (${(freeMins / 60).toFixed(2)} hours)</strong> · Busy radio minutes: <strong>${busyMins} min (${(busyMins / 60).toFixed(2)} hours)</strong> · All times shown in <strong>PST (UTC-8)</strong>.
      </p>

      <h3>24-Hour PST Radio Availability Bar (Green = Free Time · Colored = Game On Air)</h3>
      <div class="timeline-bar">${tlBlocks}</div>
      <div class="tl-ticks">
        <span>12:00 AM PST</span><span>4:00 AM</span><span>8:00 AM</span><span>12:00 PM</span><span>4:00 PM</span><span>8:00 PM</span><span>12:00 AM PST</span>
      </div>

      <h3>Live Radio Scoreboard (${adj.length} Broadcast${adj.length === 1 ? "" : "s"} in Selected Mode)</h3>
      ${scoreCards}

      <h3>Exact PST Free-Time Windows Today</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Free Window (PST)</th><th>Availability</th><th>Exact Free Duration</th></tr></thead>
          <tbody>${freeRows}</tbody>
        </table>
      </div>

      <h3>Line-by-Line Broadcast Breakdown & Official Sources</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Planning Window (PST)</th>
              <th>Official Confirmed Start</th>
              <th>Game / Broadcast</th>
              <th>Halftime (PST)</th>
              <th>SF 94122 Station</th>
              <th>Priority</th>
              <th>Verification</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>${evRows}</tbody>
        </table>
      </div>
    `;
  }

  function selectDate(iso) {
    if (!dayMap.has(iso)) return;
    currentISO = iso;
    if (dateInput) dateInput.value = iso;
    if (monthSelect) monthSelect.value = iso.slice(0, 7);
    history.replaceState(null, "", `#${iso}`);
    renderCalendarMonth(iso.slice(0, 7));
    renderSelectedDay();
  }

  document.getElementById("sb-prev")?.addEventListener("click", () => selectDate(addDaysISO(currentISO, -1)));
  document.getElementById("sb-next")?.addEventListener("click", () => selectDate(addDaysISO(currentISO, 1)));
  document.getElementById("sb-prev-wk")?.addEventListener("click", () => selectDate(addDaysISO(currentISO, -7)));
  document.getElementById("sb-next-wk")?.addEventListener("click", () => selectDate(addDaysISO(currentISO, 7)));
  document.getElementById("sb-today")?.addEventListener("click", () => selectDate("2026-11-25"));
  document.querySelectorAll("[data-jump-iso]").forEach((b) => {
    b.addEventListener("click", () => selectDate(b.dataset.jumpIso));
  });
  dateInput?.addEventListener("change", (e) => selectDate(e.target.value));
  tierSelect?.addEventListener("change", (e) => {
    currentTier = e.target.value;
    renderCalendarMonth(currentISO.slice(0, 7));
    renderSelectedDay();
  });
  bufferCheck?.addEventListener("change", (e) => {
    includePrePost = e.target.checked;
    renderSelectedDay();
  });

  selectDate(currentISO);
}

// ---------------------------------------------------------------------------
// 3. CORE GAMES PAGE (core-games.html) & MASTER SCHEDULES (verified-schedules.html)
// ---------------------------------------------------------------------------
async function initCoreAndMasterPages() {
  const needsMaster = document.querySelector("[data-master-section]");
  if (!needsMaster) return;

  const master = await fetchJSON("data/schedules_master.json");

  // 30 MLB Clubs
  const clubsEl = document.getElementById("mlb-30-table");
  if (clubsEl) {
    clubsEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>#</th><th>MLB Club (Official Name)</th><th>Abbr</th><th>Priority</th><th>SF 94122 Radio Notes</th><th>2027 Schedule</th><th>2028–2029</th><th>Official Source</th></tr></thead>
      <tbody>${master.mlb_30_clubs.map((c, i) => `
        <tr>
          <td>${i + 1}</td>
          <td><strong>${esc(c.name)}</strong></td>
          <td><code>${esc(c.abbreviation)}</code></td>
          <td>${priorityBadge(c.priority)}</td>
          <td class="small">${esc(c.bay_area_radio)}</td>
          <td>${badgeForStatus("VERIFIED")}</td>
          <td>${badgeForStatus("ESTIMATED")}</td>
          <td><a href="${esc(c.official_url)}" target="_blank" rel="noopener">mlb.com/${esc(c.official_url.split("/")[3])} ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  // 2027 Giants & Athletics Interactive Browser
  const mlbGamesEl = document.getElementById("mlb-2027-games-table");
  if (mlbGamesEl) {
    const teamFilter = document.getElementById("mlb-team-filter");
    const phaseFilter = document.getElementById("mlb-phase-filter");
    const monthFilter = document.getElementById("mlb-month-filter");
    const searchInput = document.getElementById("mlb-search");

    function renderMLBGames() {
      const tf = teamFilter?.value || "all";
      const pf = phaseFilter?.value || "all";
      const mf = monthFilter?.value || "all";
      const q = (searchInput?.value || "").trim().toLowerCase();

      let combined = [];
      if (tf === "all" || tf === "SF Giants") combined = combined.concat(master.giants_2027);
      if (tf === "all" || tf === "Athletics") combined = combined.concat(master.athletics_2027);
      combined.sort((a, b) => a.date.localeCompare(b.date) || a.team.localeCompare(b.team));

      const filtered = combined.filter((g) => {
        if (pf !== "all" && g.phase !== pf) return false;
        if (mf !== "all" && !g.date.startsWith(mf)) return false;
        if (q && !`${g.date} ${g.team} ${g.matchup} ${g.phase}`.toLowerCase().includes(q)) return false;
        return true;
      });

      const countEl = document.getElementById("mlb-games-count");
      if (countEl) countEl.textContent = `Showing ${filtered.length} official 2027 MLB StatsAPI game rows (click any date to open on PST Scoreboard).`;

      mlbGamesEl.innerHTML = `<div class="table-wrap"><table>
        <thead>
          <tr>
            <th>Date</th>
            <th>High-Priority Club</th>
            <th>Phase</th>
            <th>Matchup</th>
            <th>Official Confirmed First Pitch</th>
            <th>Estimated Planning Window (If TBD)</th>
            <th>Status</th>
            <th>Official MLB Gameday Source</th>
          </tr>
        </thead>
        <tbody>
          ${filtered.slice(0, 400).map((g) => `
            <tr>
              <td><a href="scoreboard.html#${esc(g.date)}"><strong>${esc(g.date)}</strong></a></td>
              <td><strong>${esc(g.team)}</strong> ${g.is_bay_bridge ? '<span class="badge high">Bay Bridge</span>' : ""}</td>
              <td>${esc(g.phase)}</td>
              <td>${esc(g.matchup)}</td>
              <td>${g.official_time_pst ? `<strong>${esc(g.official_time_pst)}</strong> <span class="small">(${esc(g.official_time_pt)})</span>` : `<span class="blank-cell">— (Blank: startTimeTBD=true)</span>`}</td>
              <td class="small">${g.estimated_window_pst ? esc(g.estimated_window_pst) : "— (Confirmed above)"}</td>
              <td>${badgeForStatus(g.status)}</td>
              <td><a href="${esc(g.source_url)}" target="_blank" rel="noopener">gameday/${g.gamePk} ↗</a></td>
            </tr>
          `).join("")}
        </tbody>
      </table></div>`;
    }

    [teamFilter, phaseFilter, monthFilter].forEach((el) => el?.addEventListener("change", renderMLBGames));
    searchInput?.addEventListener("input", renderMLBGames);
    renderMLBGames();
  }

  // 49ers 2026-27 Full Table
  const ninersEl = document.getElementById("niners-full-table");
  if (ninersEl) {
    ninersEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Week</th><th>Matchup</th><th>Venue</th><th>Official Kickoff</th><th>Status / Result</th><th>SF 94122 Radio</th><th>Official Source</th></tr></thead>
      <tbody>${master.fortyniners_2026_27.map((r) => `
        <tr>
          <td><a href="scoreboard.html#${esc(r.date)}"><strong>${esc(r.date)}</strong></a></td>
          <td>${esc(r.week)}</td>
          <td><strong>${esc(r.matchup)}</strong></td>
          <td>${esc(r.venue)}</td>
          <td>${r.official_time ? `<strong>${esc(r.official_time)}</strong>` : `<span class="blank-cell">— (Blank / TBD)</span>`}</td>
          <td>${esc(r.result_or_note)}</td>
          <td class="small">${esc(r.radio)}</td>
          <td><a href="${esc(r.source_url)}" target="_blank" rel="noopener">49ers.com ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  // NFL 32 Teams
  const nfl32El = document.getElementById("nfl-32-table");
  if (nfl32El) {
    nfl32El.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>#</th><th>NFL Club</th><th>Priority</th><th>Official Team Schedule</th></tr></thead>
      <tbody>${master.nfl_32_teams.map((t, i) => `
        <tr>
          <td>${i + 1}</td>
          <td><strong>${esc(t.name)}</strong></td>
          <td>${priorityBadge(t.priority)}</td>
          <td><a href="${esc(t.official_url)}" target="_blank" rel="noopener">${esc(t.official_url.replace("https://www.", ""))} ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  // Westwood One 35 Verified NFL Broadcasts
  const wwEl = document.getElementById("westwood-35-table");
  if (wwEl) {
    wwEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Official Airtime (ET)</th><th>Converted PST</th><th>Matchup</th><th>Broadcast Package</th><th>Venue</th><th>Status</th><th>Official Source</th></tr></thead>
      <tbody>${master.westwood_one_nfl_2026_27.map((w) => `
        <tr>
          <td><a href="scoreboard.html#${esc(w.date)}"><strong>${esc(w.date)}</strong></a></td>
          <td>${esc(w.official_et)}</td>
          <td><strong>${esc(w.official_pst)}</strong></td>
          <td><strong>${esc(w.matchup)}</strong></td>
          <td>${esc(w.package)}</td>
          <td class="small">${esc(w.venue)}</td>
          <td>${badgeForStatus(w.status)}</td>
          <td><a href="${esc(w.source_url)}" target="_blank" rel="noopener">events/${esc(w.event_id)} ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  // Stanford & Cal 2026 + 2027-2029
  const stanEl = document.getElementById("stanford-2026-table");
  if (stanEl) {
    stanEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Matchup</th><th>Official Kickoff</th><th>Result / Note</th><th>SF Radio</th><th>Official Source</th></tr></thead>
      <tbody>${master.stanford_2026.map((r) => `
        <tr>
          <td><a href="scoreboard.html#${esc(r.date)}"><strong>${esc(r.date)}</strong></a></td>
          <td><strong>${esc(r.matchup)}</strong></td>
          <td>${r.official_time ? `<strong>${esc(r.official_time)}</strong>` : `<span class="blank-cell">— (Historical Boxscore)</span>`}</td>
          <td>${esc(r.result)}</td>
          <td>${esc(r.radio)}</td>
          <td><a href="${esc(r.source_url)}" target="_blank" rel="noopener">gostanford.com ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  const calEl = document.getElementById("cal-2026-table");
  if (calEl) {
    calEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Matchup</th><th>Official Kickoff</th><th>Result / Note</th><th>SF Radio</th><th>Official Source</th></tr></thead>
      <tbody>${master.cal_2026.map((r) => `
        <tr>
          <td><a href="scoreboard.html#${esc(r.date)}"><strong>${esc(r.date)}</strong></a></td>
          <td><strong>${esc(r.matchup)}</strong></td>
          <td><strong>${esc(r.official_time)}</strong></td>
          <td>${esc(r.result)}</td>
          <td><strong>${esc(r.radio)}</strong></td>
          <td><a href="${esc(r.source_url)}" target="_blank" rel="noopener">calbears.com ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  const ncaafFutEl = document.getElementById("ncaaf-future-table");
  if (ncaafFutEl) {
    ncaafFutEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Official Confirmed Date</th><th>Program</th><th>Announced Matchup / Conference Slate</th><th>Official Kickoff</th><th>Status</th><th>Official Source</th></tr></thead>
      <tbody>${master.ncaaf_future_official.map((r) => `
        <tr>
          <td>${r.date ? `<a href="scoreboard.html#${esc(r.date)}"><strong>${esc(r.date)}</strong></a>` : `<span class="blank-cell">— (Blank: Unannounced)</span>`}</td>
          <td><strong>${esc(r.team)}</strong></td>
          <td>${esc(r.matchup)}</td>
          <td><span class="blank-cell">— (Blank: TBD)</span></td>
          <td>${badgeForStatus(r.status)}</td>
          <td><a href="${esc(r.source_url)}" target="_blank" rel="noopener">Official Release ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }
}

// ---------------------------------------------------------------------------
// 4. RADIO 94122, DURATIONS, REPO AUDIT, FLAGGED FOR REVIEW
// ---------------------------------------------------------------------------
async function initSecondaryPages() {
  const radioEl = document.getElementById("radio-94122-table");
  if (radioEl) {
    const stations = await fetchJSON("data/radio_94122.json");
    radioEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Station / Frequency</th><th>Power & Signal in Outer Sunset 94122</th><th>Live Broadcast Sports</th><th>Priority</th><th>Status</th><th>Official Sources</th></tr></thead>
      <tbody>${stations.map((s) => `
        <tr>
          <td><strong>${esc(s.station)}</strong><br><span class="small">${esc(s.nickname)}</span></td>
          <td class="small"><strong>${esc(s.band_power)}</strong><br>${esc(s.reception_94122)}</td>
          <td><ul style="margin:0;padding-left:18px">${s.live_sports.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></td>
          <td>${priorityBadge(s.priority)}</td>
          <td>${badgeForStatus(s.status)}</td>
          <td>${s.official_sources.map((u) => `<a href="${esc(u.url)}" target="_blank" rel="noopener">${esc(u.label)} ↗</a>`).join("<br>")}</td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  const durEl = document.getElementById("durations-table");
  if (durEl) {
    const durs = await fetchJSON("data/durations.json");
    durEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Sport / Package</th><th>Official Clock Rule</th><th>Official Halftime / Break</th><th>Official Published Mean</th><th>Planning Duration</th><th>Radio Pre/Post Buffer</th><th>Status</th><th>Official Source</th></tr></thead>
      <tbody>${durs.map((d) => `
        <tr>
          <td><strong>${esc(d.sport)}</strong></td>
          <td class="small">${esc(d.official_rule_clock)}</td>
          <td><strong>${esc(d.official_halftime_or_break)}</strong></td>
          <td>${d.official_confirmed_average.startsWith("—") ? `<span class="blank-cell">${esc(d.official_confirmed_average)}</span>` : `<strong>${esc(d.official_confirmed_average)}</strong>`}</td>
          <td><strong>${d.planning_duration_min} min</strong> (${(d.planning_duration_min / 60).toFixed(2)}h)</td>
          <td class="small">${esc(d.radio_pre_post_buffer)}</td>
          <td>${badgeForStatus(d.status)}</td>
          <td><a href="${esc(d.official_source_url)}" target="_blank" rel="noopener">${esc(d.official_source_label)} ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  const auditEl = document.getElementById("repo-audit-table");
  if (auditEl) {
    const audits = await fetchJSON("data/repo_audit.json");
    auditEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>ID</th><th>Severity</th><th>Repo File & Line</th><th>What Existing Repo Claimed / Did</th><th>Official Verified Finding</th><th>Official Sources</th></tr></thead>
      <tbody>${audits.map((a) => `
        <tr>
          <td><strong>${esc(a.id)}</strong></td>
          <td><span class="badge ${a.severity.includes("Critical") ? "high" : "partial"}">${esc(a.severity)}</span></td>
          <td><code>${esc(a.file)}</code></td>
          <td class="small">${esc(a.claim_in_repo)}</td>
          <td>${esc(a.official_finding)}</td>
          <td>${a.official_sources.map((u) => `<a href="${esc(u.url)}" target="_blank" rel="noopener">${esc(u.label)} ↗</a>`).join("<br>")}</td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }

  const flagEl = document.getElementById("flagged-items-table");
  if (flagEl) {
    const flags = await fetchJSON("data/flagged_items.json");
    flagEl.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Flag ID</th><th>Category</th><th>Item</th><th>Official Confirmed Facts</th><th>Blank / Unverified Field</th><th>Status</th><th>Official Source</th></tr></thead>
      <tbody>${flags.map((f) => `
        <tr>
          <td><strong>${esc(f.id)}</strong></td>
          <td>${esc(f.category)}</td>
          <td><strong>${esc(f.item)}</strong></td>
          <td class="small">${esc(f.official_confirmed_value)}</td>
          <td class="blank-cell">${esc(f.unverified_blank_field)}</td>
          <td>${badgeForStatus(f.status)}</td>
          <td><a href="${esc(f.source_url)}" target="_blank" rel="noopener">${esc(f.source_label)} ↗</a></td>
        </tr>
      `).join("")}</tbody></table></div>`;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await Promise.all([
      initExecutiveSummary(),
      initScoreboardPage(),
      initCoreAndMasterPages(),
      initSecondaryPages(),
    ]);
  } catch (err) {
    console.error("Planner init error:", err);
  }
});
