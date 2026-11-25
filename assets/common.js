/* Shared helpers & navigation renderer for FREE TIME VACATION dashboard */
const FT = {
  TODAY: "2026-11-25",
  MIN_DATE: "2026-11-25",
  MAX_DATE: "2027-12-31",
  monthCache: {},

  async loadJSON(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
    return res.json();
  },

  async loadMonth(ym) {
    if (this.monthCache[ym]) return this.monthCache[ym];
    try {
      const data = await this.loadJSON(`assets/data/months/${ym}.json`);
      this.monthCache[ym] = data;
      return data;
    } catch {
      this.monthCache[ym] = [];
      return [];
    }
  },

  fmtDuration(mins) {
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    if (h === 0) return `${m}m`;
    if (m === 0) return `${h}h`;
    return `${h}h ${String(m).padStart(2, "0")}m`;
  },

  fmtMinClock(m) {
    m = Math.max(0, Math.min(1440, Math.round(m)));
    if (m === 1440) return "11:59 PM";
    const h = Math.floor(m / 60);
    const mn = m % 60;
    const ap = h < 12 ? "AM" : "PM";
    const h12 = h % 12 === 0 ? 12 : h % 12;
    return `${h12}:${String(mn).padStart(2, "0")} ${ap}`;
  },

  fmtDateLong(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d, 12, 0, 0));
    return dt.toLocaleDateString("en-US", {
      weekday: "long", year: "numeric", month: "long", day: "numeric", timeZone: "UTC"
    });
  },

  fmtDateShort(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d, 12, 0, 0));
    return dt.toLocaleDateString("en-US", {
      weekday: "short", month: "short", day: "numeric", year: "numeric", timeZone: "UTC"
    });
  },

  shiftDate(iso, deltaDays) {
    const [y, m, d] = iso.split("-").map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d + deltaDays, 12, 0, 0));
    return dt.toISOString().slice(0, 10);
  },

  esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },

  leagueBadge(league) {
    const map = {
      "MLB": "badge-blue",
      "NFL": "badge-red",
      "NCAAF": "badge-purple",
      "WWO-NCAAF": "badge-purple",
      "WWO": "badge-amber"
    };
    return `<span class="badge ${map[league] || "badge-slate"}">${this.esc(league)}</span>`;
  },

  statusBadge(status) {
    if (status === "Verified") return `<span class="badge badge-green">Verified</span>`;
    if (status.includes("Verified")) return `<span class="badge badge-amber">${this.esc(status)}</span>`;
    return `<span class="badge badge-slate">${this.esc(status)}</span>`;
  },

  renderNav(activeKey) {
    const links = [
      { key: "home", href: "index.html", label: "Executive Summary" },
      { key: "calendar", href: "calendar.html", label: "Daily Scoreboard & PST Calendar" },
      { key: "vacations", href: "vacations.html", label: "2027–2029 Vacations" },
      { key: "schedules", href: "schedules.html", label: "Full Schedules" },
      { key: "radio", href: "radio.html", label: "SF 94122 Radio Guide" },
      { key: "flagged", href: "flagged.html", label: "Flagged for Review" }
    ];
    const header = document.getElementById("site-header");
    if (!header) return;
    header.innerHTML = `
      <div class="topbar">
        <div class="topbar-inner">
          <a class="brand" href="index.html">
            <span class="brand-dot"></span>
            <span>FREE TIME VACATION <span style="font-weight:500;color:#94a3b8;font-size:.82rem;">SF 94122</span></span>
          </a>
          <nav class="nav">
            ${links.map(l => `<a href="${l.href}" class="${l.key === activeKey ? "active" : ""}">${l.label}</a>`).join("")}
          </nav>
        </div>
      </div>`;
  },

  renderFooter() {
    const el = document.getElementById("site-footer");
    if (!el) return;
    el.innerHTML = `
      <div class="container" style="padding-top:0;padding-bottom:24px;">
        <div class="footer">
          <div>
            <strong>FREE TIME VACATION</strong> · Outer Sunset, San Francisco 94122 · All times in Pacific Time (PST/PDT) · Verified as of Nov 25, 2026
          </div>
          <div>
            <a href="flagged.html">Flagged for Review</a> ·
            <a href="https://github.com/kanlerxz87-cyber/Freetime1" target="_blank" rel="noopener">GitHub Repo</a>
          </div>
        </div>
      </div>`;
  }
};
