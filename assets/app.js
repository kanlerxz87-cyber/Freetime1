// Freetime1 scoreboard + tables. Data: data/schedule.json, data/vacation.json
// All times Pacific (America/Los_Angeles). Busy blocks use planning durations:
// MLB 150m, NFL 192m, NCAAF 204m, +30m radio pregame. Verified 2026 anchors override typical windows.
const DUR = { MLB:150, NFL:192, NCAAF:204, PRE:30 };
let SCHEDULE = null, VACATION = null;
const $ = (s, el=document) => el.querySelector(s);
const $$ = (s, el=document) => [...el.querySelectorAll(s)];
function fmtDate(iso){ const d=new Date(iso+"T12:00:00"); return d.toLocaleDateString("en-US",{weekday:"long",year:"numeric",month:"long",day:"numeric"}); }
function esc(s){ return String(s??"").replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function statusBadge(st){
  const m={VERIFIED:"verified",ESTIMATED:"estimated",PARTIAL:"partial",UNVERIFIED:"unverified"};
  return `<span class="badge ${m[st]||""}">${esc(st)}</span>`;
}
async function loadData(){
  const [a,b] = await Promise.all([fetch("data/schedule.json").then(r=>r.json()), fetch("data/vacation.json").then(r=>r.json())]);
  SCHEDULE=a; VACATION=b;
}
function dayByDate(iso){ return SCHEDULE.days.find(d=>d.date===iso); }
function addDays(iso,n){ const d=new Date(iso+"T12:00:00"); d.setDate(d.getDate()+n); return d.toISOString().slice(0,10); }
function todayPT(){ return new Date().toLocaleDateString("en-CA",{timeZone:"America/Los_Angeles"}); }

// Build timeline blocks for a date. Returns [{startMin,endMin,label,cls,note}]
function blocksFor(iso){
  const day = dayByDate(iso); if(!day) return [];
  const wd = new Date(iso+"T12:00:00").getDay(); // 0 Sun..6 Sat
  const blocks=[];
  const reasons = day.busy_reasons||[];
  const has = s => reasons.some(r=>r.includes(s));
  // Verified 2026 NCAAF anchors (actual kickoffs PT)
  const stan = (SCHEDULE.stanford_2026||[]).find(x=>x.date===iso);
  const cal = (SCHEDULE.cal_2026||[]).find(x=>x.date===iso);
  function parsePT(t){
    // "4:00 PM PT" -> minutes; TBA -> null
    const m = String(t||"").match(/(\d+):(\d+)\s*(AM|PM)/i); if(!m) return null;
    let h=+m[1]%12; if(/PM/i.test(m[3])) h+=12; return h*60+(+m[2]);
  }
  if(stan){ const s=parsePT(stan.kickoff_pt); if(s!=null) blocks.push({startMin:s,endMin:s+DUR.NCAAF,label:`Stanford ${stan.matchup} (VERIFIED)`,cls:"ncaaf",note:`Kickoff ${stan.kickoff_pt} + ${DUR.NCAAF}m`}); }
  if(cal){ const s=parsePT(cal.kickoff_pt); if(s!=null) blocks.push({startMin:s,endMin:s+DUR.NCAAF,label:`Cal ${cal.matchup} (VERIFIED)`,cls:"ncaaf",note:`Kickoff ${cal.kickoff_pt} + ${DUR.NCAAF}m`}); }
  // Verified Westwood 2026 (ET -> PT approx: ET-3h; label shows both)
  const ww = (SCHEDULE.westwood_2026_verified||[]).find(x=>x.date===iso);
  if(ww){
    const m=String(ww.kickoff_et).match(/(\d+):(\d+)\s*(AM|PM)/i);
    if(m){ let h=+m[1]%12; if(/PM/i.test(m[3])) h+=12; const et=h*60+(+m[2]); const pt=et-180;
      blocks.push({startMin:pt,endMin:pt+DUR.NFL,label:`Westwood One: ${ww.matchup} (VERIFIED)`,cls:"westwood",note:`${ww.kickoff_et} → ~${Math.floor(pt/60)}:${String(pt%60).padStart(2,"0")} PT + ${DUR.NFL}m · ${ww.label}`});
    }
  }
  // Typical windows (ESTIMATED) when no verified block covers that league that day
  const hasVerifiedNCAAF = !!(stan||cal);
  if(has("MLB") && !blocks.some(b=>b.cls==="mlb"||b.cls==="spring")){
    const isSpring = has("Spring");
    // Weekday evening 6:45pm PT; weekend afternoon 1:05pm PT (typical first-pitch pattern)
    const start = (wd===0||wd===6) ? 13*60+5 : 18*60+45;
    blocks.push({startMin:start,endMin:start+DUR.MLB,label:isSpring?"MLB Spring Training — typical window (ESTIMATED)":"MLB (all 30 clubs) — typical window (ESTIMATED)",cls:isSpring?"spring":"mlb",note:`Typical first pitch ${start/60|0}:${String(start%60).padStart(2,"0")} PT + ${DUR.MLB}m + ${DUR.PRE}m pregame. Exact time TBA — see mlb.html.`});
  }
  if(has("NFL") && !ww){
    let start=null, label="NFL — typical window (ESTIMATED)";
    if(wd===0) start=13*60+25; else if(wd===3||wd===0+1) start=17*60+20; // Thu/Mon primetime ~5:20pm PT
    if(wd===3) start=17*60+20; if(wd===1) start=17*60+20;
    if(wd===5||wd===6) start=13*60+25; // Sat postseason/doubleheader approx
    if(start!=null) blocks.push({startMin:start,endMin:start+DUR.NFL,label,cls:"nfl",note:`Typical kickoff + ${DUR.NFL}m + ${DUR.PRE}m pregame. Exact time TBA — see nfl.html.`});
  }
  if(has("NCAAF") && !hasVerifiedNCAAF && day.date>="2027-01-01"){
    const start=12*60; // Saturday noon PT typical
    blocks.push({startMin:start,endMin:start+DUR.NCAAF,label:"NCAAF Stanford/Cal — typical Saturday window (ESTIMATED)",cls:"ncaaf",note:`Typical kickoff 12:00 PM PT + ${DUR.NCAAF}m. Exact date/time TBA — see ncaaf.html.`});
  }
  // Sort + clamp to day
  return blocks.map(b=>({...b,startMin:Math.max(0,b.startMin),endMin:Math.min(1440,b.endMin)})).sort((a,b)=>a.startMin-b.startMin);
}
function freeGaps(blocks){
  const gaps=[]; let cur=0;
  for(const b of blocks){ if(b.startMin>cur) gaps.push({start:cur,end:b.startMin}); cur=Math.max(cur,b.endMin); }
  if(cur<1440) gaps.push({start:cur,end:1440});
  return gaps.filter(g=>g.end>g.start);
}
function mmToTime(m){ const h=Math.floor(m/60), mm=m%60; const ap=h>=12?"PM":"AM"; const hh=h%12||12; return `${hh}:${String(mm).padStart(2,"0")} ${ap}`; }

function renderDay(iso){
  const day=dayByDate(iso);
  const el=$("#day-view"); if(!el) return;
  if(!day){ el.innerHTML=`<div class="callout warn">No data for ${esc(iso)} (dataset covers 2026-01-01 – 2029-12-31).</div>`; return; }
  const blocks=blocksFor(iso), gaps=freeGaps(blocks);
  const freeMins=gaps.reduce((a,g)=>a+(g.end-g.start),0);
  const status = `<span class="badge unverified">NOT CERTIFIED — schedule coverage is incomplete</span>`;
  const reasons = (day.busy_reasons||[]).map(r=>`<li>${esc(r)}</li>`).join("") || "<li>No event window is modeled for this date; schedule coverage is incomplete, so this is not evidence of a free day.</li>";
  const tlBlocks = blocks.map(b=>{
    const left=(b.startMin/1440*100).toFixed(2), width=((b.endMin-b.startMin)/1440*100).toFixed(2);
    return `<div class="block ${b.cls}" style="left:${left}%;width:${width}%" title="${esc(b.label)} — ${esc(b.note)}">${esc(b.label)}</div>`;
  }).join("");
  const gapRows = gaps.map(g=>`<tr><td>${mmToTime(g.start)} – ${mmToTime(g.end)} PT</td><td>${g.end-g.start} min (${((g.end-g.start)/60).toFixed(1)} h)</td></tr>`).join("");
  const blockRows = blocks.map(b=>`<tr><td>${mmToTime(b.startMin)} – ${mmToTime(b.endMin)} PT</td><td>${esc(b.label)}</td><td>${esc(b.note)}</td></tr>`).join("") || `<tr><td colspan="3">No busy blocks.</td></tr>`;
  el.innerHTML = `
    <h2 style="margin-top:0">${esc(fmtDate(iso))}</h2>
    <p>${status} <span class="small">· All times Pacific (PT). Free minutes = minutes with no tracked game on air.</span></p>
    <p><strong>Unblocked in this partial model: ${freeMins} min (${(freeMins/60).toFixed(1)} h)</strong> of 1,440 min. This is not verified free time.</p>
    <h3>Why?</h3><ul>${reasons}</ul>
    <h3>Timeline (12:00 AM – 11:59 PM PT)</h3>
    <div class="timeline"><div class="ticks"><span>12 AM</span><span>6 AM</span><span>12 PM</span><span>6 PM</span><span>12 AM</span></div>${tlBlocks}</div>
    <p class="small">Colored blocks show modeled or transcribed windows only; blank space is not certified free time. Verified kickoff anchors still do not establish complete coverage of every required league, special event, or broadcast.</p>
    <h3>Busy blocks (on air)</h3>
    <table><thead><tr><th>Window (PT)</th><th>Game / window</th><th>Note</th></tr></thead><tbody>${blockRows}</tbody></table>
    <h3>Unmodeled gaps (not confirmed game-free)</h3>
    <table><thead><tr><th>Free window (PT)</th><th>Length</th></tr></thead><tbody>${gapRows}</tbody></table>
  `;
  renderMonth(iso.slice(0,7), iso);
}
function renderMonth(ym, selected){
  const el=$("#month-grid"); if(!el) return;
  const [y,m]=ym.split("-").map(Number);
  const first=new Date(y,m-1,1), daysIn=new Date(y,m,0).getDate();
  const startDow=first.getDay();
  let html=`<div class="dow">Sun</div><div class="dow">Mon</div><div class="dow">Tue</div><div class="dow">Wed</div><div class="dow">Thu</div><div class="dow">Fri</div><div class="dow">Sat</div>`;
  for(let i=0;i<startDow;i++) html+=`<div></div>`;
  for(let d=1;d<=daysIn;d++){
    const iso=`${y}-${String(m).padStart(2,"0")}-${String(d).padStart(2,"0")}`;
    const day=dayByDate(iso);
    const cls=day?(day.free?"unknown":"modeled-busy"):"unknown";
    const sel=iso===selected?" sel":"";
    html+=`<button class="${cls}${sel}" data-date="${iso}" title="${iso}: ${day&&!day.free?"modeled activity; not a verified complete schedule":"coverage unknown; not certified free"}">${d}</button>`;
  }
  el.innerHTML=html;
  $$("#month-grid button").forEach(b=>b.addEventListener("click",()=>{ setDate(b.dataset.date); }));
}
function setDate(iso){
  const inp=$("#date-input"); if(inp) inp.value=iso;
  const sel=$("#month-select"); if(sel) sel.value=iso.slice(0,7);
  renderDay(iso);
}
function initScoreboard(){
  const today=todayPT();
  const initial = (today>="2026-01-01"&&today<="2029-12-31")?today:"2026-11-25";
  // month select options
  const sel=$("#month-select");
  if(sel){
    let opts="";
    for(let y=2026;y<=2029;y++) for(let m=1;m<=12;m++){
      const v=`${y}-${String(m).padStart(2,"0")}`;
      opts+=`<option value="${v}">${new Date(y,m-1,1).toLocaleDateString("en-US",{month:"long",year:"numeric"})}</option>`;
    }
    sel.innerHTML=opts; sel.value=initial.slice(0,7);
    sel.addEventListener("change",()=>renderMonth(sel.value, $("#date-input").value));
  }
  $("#btn-yesterday")?.addEventListener("click",()=>setDate(addDays($("#date-input").value,-1)));
  $("#btn-today")?.addEventListener("click",()=>setDate(initial));
  $("#btn-tomorrow")?.addEventListener("click",()=>setDate(addDays($("#date-input").value,1)));
  $("#date-input")?.addEventListener("change",e=>setDate(e.target.value));
  setDate(initial);
}
function renderWindowsTable(elId, rows){
  const el=document.getElementById(elId); if(!el) return;
  el.innerHTML=`<table><thead><tr><th>Window</th><th>Phase</th><th>Status</th><th>Source (official)</th></tr></thead><tbody>${
    rows.map(w=>`<tr><td>${esc(w.start||"—")} → ${esc(w.end||"—")}</td><td>${esc(w.league)} — ${esc(w.phase)}</td><td>${statusBadge(w.status)}</td><td><a href="${esc(w.source_url)}" target="_blank" rel="noopener">${esc(w.source_name)}</a></td></tr>`).join("")
  }</tbody></table>`;
}
function renderVacation(){
  const sEl=$("#vacation-strict"), rEl=$("#vacation-regular");
  if(sEl) sEl.innerHTML=`<table><thead><tr><th>Candidate start</th><th>Candidate end</th><th>Days in partial model</th><th>Coverage status</th></tr></thead><tbody>${
    VACATION.strict_top_runs.map(r=>`<tr><td>${esc(r.start)}</td><td>${esc(r.end)}</td><td><strong>${r.days}</strong></td><td><span class="badge unverified">NOT CERTIFIED</span></td></tr>`).join("")
  }</tbody></table>`;
  if(rEl) rEl.innerHTML=`<table><thead><tr><th>Candidate start</th><th>Candidate end</th><th>Days in partial model</th><th>Coverage status</th></tr></thead><tbody>${
    VACATION.regular_only_top_runs.map(r=>`<tr><td>${esc(r.start)}</td><td>${esc(r.end)}</td><td><strong>${r.days}</strong> (${(r.days/7).toFixed(1)} weeks)</td><td><span class="badge unverified">NOT CERTIFIED</span></td></tr>`).join("")
  }</tbody></table>`;
}
function renderGameTables(){
  const st=$("#stanford-table"), ca=$("#cal-table"), ww=$("#westwood-table"), n49=$("#niners-table");
  if(st) st.innerHTML=`<table><thead><tr><th>Date</th><th>Matchup</th><th>Kickoff (PT)</th><th>TV</th><th>Source</th></tr></thead><tbody>${
    SCHEDULE.stanford_2026.map(r=>`<tr><td>${esc(r.date)}</td><td>${esc(r.matchup)}</td><td>${esc(r.kickoff_pt)}</td><td>${esc(r.tv)}</td><td><a href="https://gostanford.com/sports/football/schedule" target="_blank" rel="noopener">gostanford.com</a></td></tr>`).join("")
  }</tbody></table>`;
  if(ca) ca.innerHTML=`<table><thead><tr><th>Date</th><th>Matchup</th><th>Kickoff (PT)</th><th>Source</th></tr></thead><tbody>${
    SCHEDULE.cal_2026.map(r=>`<tr><td>${esc(r.date)}</td><td>${esc(r.matchup)}</td><td>${esc(r.kickoff_pt)}</td><td><a href="https://calbears.com/sports/football/schedule/text" target="_blank" rel="noopener">calbears.com</a></td></tr>`).join("")
  }</tbody></table>`;
  if(ww) ww.innerHTML=`<table><thead><tr><th>Date</th><th>Matchup</th><th>Kickoff (ET)</th><th>Label</th><th>Source</th></tr></thead><tbody>${
    SCHEDULE.westwood_2026_verified.map(r=>`<tr><td>${esc(r.date)}</td><td>${esc(r.matchup)}</td><td>${esc(r.kickoff_et)}</td><td>${esc(r.label)}</td><td><a href="https://www.westwoodonesports.com/nfl-schedule/" target="_blank" rel="noopener">westwoodonesports.com</a></td></tr>`).join("")
  }</tbody></table>`;
  if(n49) n49.innerHTML=`<table><thead><tr><th>Date</th><th>Event</th><th>Time</th><th>Source</th></tr></thead><tbody>${
    SCHEDULE.fortyniners_2026_anchors.map(r=>`<tr><td>${esc(r.date)}</td><td>${esc(r.event)}</td><td>${esc(r.time)}</td><td><a href="https://www.49ers.com/schedule/" target="_blank" rel="noopener">49ers.com</a></td></tr>`).join("")
  }</tbody></table>`;
  const clubs=$("#mlb-clubs");
  if(clubs) clubs.innerHTML=`<table><thead><tr><th>#</th><th>Club (all 30 shown)</th><th>Priority</th><th>Official schedule</th></tr></thead><tbody>${
    SCHEDULE.mlb_clubs_30.map((c,i)=>{
      const high = c.includes("Giants")||c.includes("Athletics");
      return `<tr><td>${i+1}</td><td>${esc(c)}</td><td>${high?'<span class="badge high">HIGH PRIORITY</span>':'<span class="badge">Standard</span>'}</td><td><a href="https://www.mlb.com/schedule" target="_blank" rel="noopener">mlb.com/schedule</a></td></tr>`;
    }).join("")
  }</tbody></table>`;
}
document.addEventListener("DOMContentLoaded", async ()=>{
  try{ await loadData(); }catch(e){ console.error(e); }
  if(!SCHEDULE) return;
  if(document.getElementById("day-view")) initScoreboard();
  renderWindowsTable("windows-table", SCHEDULE.windows);
  renderVacation(); renderGameTables();
  const meta=$("#data-meta"); if(meta) meta.textContent=`Data generated ${SCHEDULE.generated} · ${SCHEDULE.days.length} days (2026-01-01 – 2029-12-31) · Timezone America/Los_Angeles.`;
});
