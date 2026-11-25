/* Free Time Vacation - shared site code.
 * All clock math is done in America/Los_Angeles (Pacific Time).
 * MLB games are read live from the official MLB Stats API (statsapi.mlb.com).
 * NFL / 49ers / Stanford / Cal / estimate windows come from the JSON files in data/.
 */
(function () {
  var PT = 'America/Los_Angeles';
  var RANGE_START = '2026-11-25';
  var RANGE_END = '2029-12-31';
  var MLB_URL = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=' + RANGE_START +
    '&endDate=' + RANGE_END +
    '&fields=dates,date,games,gamePk,gameType,gameDate,officialDate,status,detailedState,startTimeTBD,dayNight,teams,away,home,team,id,name,venue,description';
  var TEAMS_URL = 'https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2027&fields=teams,id,name,abbreviation,teamName,venue,name,division,name,league,name,clubName';
  var GIANTS = 137, ATHLETICS = 133;
  var GAME_TYPE = { S: 'Spring Training', R: 'Regular season', F: 'Postseason (Wild Card)', D: 'Postseason (Division Series)', L: 'Postseason (LCS)', W: 'World Series', A: 'All-Star', E: 'Exhibition', P: 'Postseason' };
  var DAY_MS = 86400000;

  // ---------- Pacific time helpers ----------
  var dtf = new Intl.DateTimeFormat('en-US', { timeZone: PT, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' });
  function ptParts(ms) {
    var o = {};
    dtf.formatToParts(new Date(ms)).forEach(function (p) { o[p.type] = p.value; });
    return { y: +o.year, m: +o.month, d: +o.day, h: +o.hour, mi: +o.minute, s: +o.second };
  }
  function ptOffsetMin(ms) {
    var p = ptParts(ms);
    var asUtc = Date.UTC(p.y, p.m - 1, p.d, p.h, p.mi, p.s);
    return Math.round((asUtc - ms) / 60000);
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function keyOf(ms) { var p = ptParts(ms); return p.y + '-' + pad(p.m) + '-' + pad(p.d); }
  function addDays(key, n) {
    var a = key.split('-').map(Number);
    var t = new Date(Date.UTC(a[0], a[1] - 1, a[2] + n));
    return t.toISOString().slice(0, 10);
  }
  function ptDayStart(key) {
    var a = key.split('-').map(Number);
    var off = ptOffsetMin(Date.UTC(a[0], a[1] - 1, a[2], 12));
    return Date.UTC(a[0], a[1] - 1, a[2]) - off * 60000;
  }
  function fmtT(ms) {
    var p = ptParts(ms);
    var h = p.h % 12; if (h === 0) h = 12;
    return h + ':' + pad(p.mi) + ' ' + (p.h < 12 ? 'AM' : 'PM');
  }
  function fmtDay(key) {
    var a = key.split('-').map(Number);
    var d = new Date(Date.UTC(a[0], a[1] - 1, a[2], 12));
    return d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
  }
  function fmtShort(key) {
    var a = key.split('-').map(Number);
    var d = new Date(Date.UTC(a[0], a[1] - 1, a[2], 12));
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function minsTxt(m) { var h = Math.floor(m / 60), r = m % 60; return (h ? h + ' h ' : '') + r + ' min'; }

  function getJSON(u) {
    return fetch(u, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error(u + ' returned ' + r.status);
      return r.json();
    });
  }

  // ---------- data loading ----------
  var CTX = null;
  function loadCtx() {
    if (CTX) return CTX;
    CTX = Promise.all([
      getJSON('data/durations.json'), getJSON('data/estimates.json'), getJSON('data/nfl-radio.json'),
      getJSON('data/49ers-2026.json'), getJSON('data/ncaaf.json')
    ]).then(function (arr) {
      var dur = arr[0], est = arr[1], nfl = arr[2], sf = arr[3], cfb = arr[4];
      var DUR = {};
      dur.items.forEach(function (i) { DUR[i.league] = i.minutes; });
      var events = [], windows = est.windows.slice(), mlb = { ok: false, error: '', games: 0 };
      var ctx = { events: events, windows: windows, mlb: mlb, dur: DUR, durations: dur, est: est, nfl: nfl, sf: sf, cfb: cfb, teams: null };

      function nflEvent(g, league, title, src, priority, radio, tier, endMinutes) {
        var start = Date.parse(g.date);
        var dm = endMinutes || DUR[league];
        return { league: league, title: title, venue: g.venue || '', startMs: start, endMs: start + dm * 60000, est: !!g.estimated_time,
          status: 'Scheduled', priority: priority, tier: tier, radio: radio, source: src, label: g.label || '', gameType: '' };
      }

      // NFL national radio (Westwood One), skipping rows that are duplicated by the 49ers schedule
      nfl.games.forEach(function (g) {
        if (g.dupOf) return;
        events.push(nflEvent(g, 'NFL', g.matchup, 'https://www.westwoodonesports.com/events/' + g.id, 'high',
          'Westwood One Sports national NFL radio (local SF station not verified)', 'NFL'));
      });
      // 49ers (official schedule); games with a date only
      sf.games.forEach(function (g) {
        if (!g.date) return;
        events.push({ league: 'NFL', title: 'San Francisco 49ers ' + g.opponent + ' (' + g.week + ')', venue: g.venue,
          startMs: Date.parse(g.date), endMs: Date.parse(g.date) + DUR.NFL * 60000, est: false, status: 'Scheduled', priority: 'high', tier: 'Core: 49ers',
          radio: sf.radio, source: g.source, label: g.tv, gameType: 'Regular season' });
      });
      // Stanford / Cal
      cfb.games.forEach(function (g) {
        if (g.conditional || !g.date) return;
        events.push({ league: 'CFB', title: g.team + ' ' + g.opponent, venue: '', startMs: Date.parse(g.date),
          endMs: Date.parse(g.date) + DUR.CFB * 60000, est: !!g.estimated_time, status: g.status, priority: 'high',
          tier: 'Core: ' + g.team, radio: g.radio || 'Not verified', source: g.source, label: g.tv || '', gameType: '' });
      });
      cfb.cal_2027_known.forEach(function (g) {
        if (!g.date) return;
        events.push({ league: 'CFB', title: 'California ' + g.opponent, venue: '', startMs: Date.parse(g.date + 'T12:30:00-07:00'),
          endMs: Date.parse(g.date + 'T12:30:00-07:00') + DUR.CFB * 60000, est: true, status: 'Date only (time TBA, 12:30 PM PT estimate)', priority: 'high',
          tier: 'Core: California', radio: 'Not verified', source: g.source, label: '', gameType: 'Regular season' });
      });
      // Extra events from estimates.json (Super Bowl date; secondary-source date, flagged)
      est.events_extra.forEach(function (e) {
        var lg = e.duration_league || e.league;
        var st = Date.parse(e.date);
        events.push({ league: e.league, title: e.title, venue: '', startMs: st, endMs: st + DUR[lg] * 60000,
          est: !!e.estimated_time, status: 'Date from secondary source; time estimated', priority: 'high', tier: e.league_label || e.league,
          radio: 'Not verified', source: e.source, label: e.time_note || '', gameType: '' });
      });

      function radioForMLB(homeId, awayId) {
        if (homeId === GIANTS || awayId === GIANTS) return 'KNBR 680 AM / 104.5 FM (Giants flagship; per-game listing not verified)';
        if (homeId === ATHLETICS || awayId === ATHLETICS) return 'KNEW 960 AM (Bay Area; Wikipedia 2025 snapshot, 2027 not verified)';
        return 'Not verified';
      }
      function loadMLB() {
        return getJSON(MLB_URL).then(function (j) {
          (j.dates || []).forEach(function (d) {
            (d.games || []).forEach(function (g) {
              var home = g.teams.home.team, away = g.teams.away.team;
              var est = false, start = Date.parse(g.gameDate);
              if (g.status && g.status.startTimeTBD) {
                est = true;
                start = ptDayStart(g.officialDate) + (g.dayNight === 'night' ? 19 : 13) * 3600000;
              }
              var pri = (home.id === GIANTS || away.id === GIANTS || home.id === ATHLETICS || away.id === ATHLETICS) ? 'Core' : 'high';
              events.push({ league: 'MLB', title: away.name + ' at ' + home.name, venue: (g.venue && g.venue.name) || '',
                startMs: start, endMs: start + DUR.MLB * 60000, est: est,
                status: (g.status && g.status.detailedState) || 'Scheduled' + (est ? ' (time TBD, estimated)' : ''),
                priority: pri, tier: (pri === 'Core' ? 'Core: ' + (home.id === GIANTS || away.id === GIANTS ? 'Giants' : 'Athletics') : 'MLB'),
                radio: radioForMLB(home.id, away.id), source: 'https://www.mlb.com/gameday/' + g.gamePk,
                label: GAME_TYPE[g.gameType] || g.gameType, gameType: g.gameType, ids: [home.id, away.id], desc: g.description || '', dateKey: g.officialDate,
                dayNight: g.dayNight });
              mlb.games++;
            });
          });
          mlb.ok = true;
        }).catch(function (err) {
          mlb.ok = false; mlb.error = String(err && err.message || err);
          windows.push({ league: 'MLB', label: 'MLB live feed unavailable in this browser: MLB games unverified and treated as busy', start: RANGE_START, end: RANGE_END, est: true, source: MLB_URL });
        });
      }
      function loadTeams() {
        return getJSON(TEAMS_URL).then(function (j) { ctx.teams = j.teams || []; }).catch(function () { ctx.teams = []; });
      }
      return Promise.all([loadMLB(), loadTeams()]).then(function () {
        events.sort(function (a, b) { return a.startMs - b.startMs; });
        return ctx;
      });
    });
    return CTX;
  }

  // ---------- day analysis ----------
  function analyzeDay(key, ctx) {
    var s = ptDayStart(key), e = ptDayStart(addDays(key, 1));
    var evs = ctx.events.filter(function (x) { return x.startMs < e && x.endMs > s; });
    var wins = ctx.windows.filter(function (w) { return w.start <= key && key <= w.end; });
    var status;
    if (evs.length === 0 && wins.length === 0) status = 'FREE';
    else if (evs.length === 0) status = 'ESTIMATED';
    else status = 'BUSY';
    var free = [];
    if (status === 'FREE') {
      free = [{ from: s, to: e }];
    } else if (wins.length === 0) {
      // compute gaps between verified/estimated game windows
      var iv = evs.map(function (x) { return { a: Math.max(x.startMs, s), b: Math.min(x.endMs, e) }; }).sort(function (p, q) { return p.a - q.a; });
      var cur = s;
      iv.forEach(function (x) {
        if (x.a > cur) free.push({ from: cur, to: x.a });
        if (x.b > cur) cur = x.b;
      });
      if (cur < e) free.push({ from: cur, to: e });
      free = free.filter(function (f) { return f.to - f.from >= 60000; });
    }
    var confidence = 'estimated';
    if (status === 'FREE' && key.indexOf('2027') === 0 && ctx.mlb.ok) confidence = 'verified';
    if (status === 'BUSY' && evs.every(function (x) { return !x.est; }) && wins.length === 0) confidence = 'verified';
    return { key: key, status: status, events: evs, windows: wins, free: free, confidence: confidence, startMs: s, endMs: e };
  }
  function keysBetween(a, b) {
    var out = [], k = a;
    while (k <= b) { out.push(k); k = addDays(k, 1); }
    return out;
  }
  function freeRuns(ctx) {
    var runs = [], cur = null;
    keysBetween(RANGE_START, RANGE_END).forEach(function (k) {
      var d = analyzeDay(k, ctx);
      if (d.status === 'FREE') {
        if (!cur) cur = { start: k, end: k, days: 0, confs: {} };
        cur.end = k; cur.days++; cur.confs[d.confidence] = true;
      } else if (cur) { runs.push(cur); cur = null; }
    });
    if (cur) runs.push(cur);
    runs.forEach(function (r) { r.conf = r.confs.estimated ? 'estimated' : 'verified'; });
    return runs;
  }

  function statusBadge(st, conf) {
    if (st === 'FREE') return '<span class="badge free">FREE' + (conf === 'estimated' ? ' (estimated)' : ' (verified)') + '</span>';
    if (st === 'ESTIMATED') return '<span class="badge est">ESTIMATED BUSY</span>';
    return '<span class="badge busy">BUSY</span>';
  }
  function priBadge(p, tier) {
    return '<span class="badge ' + (p === 'Core' ? 'core' : 'hi') + '">' + esc(tier || (p === 'Core' ? 'Core' : 'High priority')) + '</span>';
  }

  // Scoreboard-style view of one day
  function renderDay(el, key, ctx) {
    var d = analyzeDay(key, ctx);
    var h = '<div class="daybar"><h2>' + esc(fmtDay(key)) + '</h2> ' + statusBadge(d.status, d.confidence) + '</div>';
    if (d.status === 'FREE') {
      h += '<p class="lead">No tracked game is scheduled on this Pacific calendar day. Free time: <strong>all day (12:00 AM - 12:00 AM)</strong>.</p>';
    } else if (d.status === 'ESTIMATED') {
      h += '<p class="lead">No verified game is loaded for this day, but it falls inside an <strong>estimated season window</strong>. Games are expected; exact times are not yet published.</p>';
    }
    if (d.windows.length) {
      h += '<div class="note"><strong>Estimated windows covering this day:</strong><ul>' + d.windows.map(function (w) {
        return '<li>' + esc(w.label) + ' - <a href="' + esc(w.source) + '" target="_blank" rel="noopener">source</a></li>';
      }).join('') + '</ul></div>';
    }
    h += '<h3>Games on air (' + d.events.length + ')</h3>';
    if (!d.events.length) h += '<p class="muted">None loaded for this day.</p>';
    else {
      h += '<div class="games">' + d.events.map(function (x) {
        return '<div class="game"><div class="gtime">' + fmtT(x.startMs) + (x.est ? ' <span class="est-t">est.</span>' : '') + '<small>' + minsTxt(Math.round((x.endMs - x.startMs) / 60000)) + ' avg</small></div>' +
          '<div class="gbody"><div class="gtop">' + priBadge(x.priority, x.tier) + ' <span class="lg">' + esc(x.league) + (x.label ? ' - ' + esc(x.label) : '') + '</span></div>' +
          '<div class="gtitle">' + esc(x.title) + '</div>' +
          '<div class="gmeta">' + esc(x.venue) + ' | ' + esc(x.status) + '</div>' +
          '<div class="gmeta">Radio: ' + esc(x.radio) + '</div>' +
          '<div class="gmeta"><a href="' + esc(x.source) + '" target="_blank" rel="noopener">official source</a></div></div></div>';
      }).join('') + '</div>';
    }
    h += '<h3>Free time (Pacific)</h3>';
    if (d.status === 'FREE') h += '<p>Entire day.</p>';
    else if (d.windows.length) h += '<p class="muted">Free-time blocks are not calculated on this day because at least one league is estimated (its games are not yet verified).</p>';
    else if (!d.free.length) h += '<p>No free block: games cover the whole day.</p>';
    else {
      h += '<table class="tbl"><thead><tr><th>From</th><th>To</th><th>Length</th></tr></thead><tbody>' + d.free.map(function (f) {
        var to = fmtT(f.to); if (f.to === d.endMs) to = '12:00 AM (next day)';
        var from = fmtT(f.from); if (f.from === d.startMs) from = '12:00 AM';
        return '<tr><td>' + from + '</td><td>' + to + '</td><td>' + minsTxt(Math.round((f.to - f.from) / 60000)) + '</td></tr>';
      }).join('') + '</tbody></table>';
    }
    el.innerHTML = h;
    return d;
  }

  function renderMonth(el, y, m, ctx, selected) {
    var first = y + '-' + pad(m) + '-01';
    var dow = new Date(Date.UTC(y, m - 1, 1, 12)).getUTCDay();
    var days = new Date(Date.UTC(y, m, 0, 12)).getUTCDate();
    var h = '<div class="cal"><div class="calhead">' + ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(function (x) { return '<div>' + x + '</div>'; }).join('') + '</div><div class="calgrid">';
    for (var i = 0; i < dow; i++) h += '<div class="cell blank"></div>';
    for (var dd = 1; dd <= days; dd++) {
      var k = y + '-' + pad(m) + '-' + pad(dd);
      var inRange = k >= RANGE_START && k <= RANGE_END;
      if (!inRange) { h += '<div class="cell blank"><span>' + dd + '</span></div>'; continue; }
      var st = analyzeDay(k, ctx);
      var cls = st.status === 'FREE' ? 'free' : (st.status === 'ESTIMATED' ? 'est' : 'busy');
      h += '<a class="cell ' + cls + (k === selected ? ' sel' : '') + '" href="scoreboard.html?date=' + k + '" title="' + esc(fmtShort(k)) + ': ' + st.status + '"><span>' + dd + '</span><em>' + (st.status === 'FREE' ? 'Free' : (st.status === 'ESTIMATED' ? 'Est.' : st.events.length + ' gm')) + '</em></a>';
    }
    h += '</div></div>';
    el.innerHTML = h;
  }

  // ---------- nav ----------
  var PAGES = [
    ['index.html', 'Home'], ['scoreboard.html', 'Scoreboard'], ['vacation.html', 'Vacation windows'],
    ['mlb.html', 'MLB'], ['nfl.html', 'NFL & 49ers'], ['ncaaf.html', 'Stanford & Cal'],
    ['radio.html', 'Radio'], ['flagged.html', 'Flagged for Review'], ['sources.html', 'Sources & method']
  ];
  function nav() {
    var cur = (location.pathname.split('/').pop() || 'index.html');
    if (cur === '') cur = 'index.html';
    var el = document.getElementById('nav');
    if (!el) return;
    el.innerHTML = '<header class="top"><a class="brand" href="index.html">Free Time Vacation</a><nav>' +
      PAGES.map(function (p) { return '<a href="' + p[0] + '"' + (p[0] === cur ? ' class="on"' : '') + '>' + p[1] + '</a>'; }).join('') +
      '</nav></header>';
  }
  function status(el) {
    loadCtx().then(function (ctx) {
      el.innerHTML = ctx.mlb.ok
        ? '<span class="dot ok"></span>Live MLB feed: <strong>' + ctx.mlb.games + ' MLB games loaded</strong> from statsapi.mlb.com (official MLB Stats API). Time zone: Pacific.'
        : '<span class="dot bad"></span>Live MLB feed unavailable in this browser (' + esc(ctx.mlb.error) + '). MLB days are shown as estimated busy.';
    });
  }

  window.FT = {
    loadCtx: loadCtx, analyzeDay: analyzeDay, renderDay: renderDay, renderMonth: renderMonth, freeRuns: freeRuns,
    nav: nav, status: status, keysBetween: keysBetween, addDays: addDays, fmtDay: fmtDay, fmtShort: fmtShort,
    fmtT: fmtT, esc: esc, minsTxt: minsTxt, keyOf: keyOf, RANGE_START: RANGE_START, RANGE_END: RANGE_END,
    GAME_TYPE: GAME_TYPE, statusBadge: statusBadge
  };
  document.addEventListener('DOMContentLoaded', nav);
})();
