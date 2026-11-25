function parseDate(s){ const [y,m,d]=s.split('-').map(Number); return new Date(Date.UTC(y,m-1,d)); }
function fmtDate(d){ return d.toISOString().slice(0,10); }
function addDays(d,n){ const x=new Date(d); x.setUTCDate(x.getUTCDate()+n); return x; }
function inRange(day,start,end){ return day>=start && day<=end; }
function monthName(y,m){ return new Date(Date.UTC(y,m,1)).toLocaleString('en-US',{month:'long',year:'numeric',timeZone:'UTC'}); }

function getVerifiedEventsForDay(dayStr){
  const ev=[];
  (VERIFIED_49ERS_2026||[]).forEach(g=>{ if(g.date===dayStr) ev.push({time:g.time||g.etTime||'', title:`49ers ${g.opponent}`, priority:'high', status:g.status, sourceUrl:g.sourceUrl, type:'NFL - 49ers'}); });
  (VERIFIED_WESTWOOD_ONE_NFL_2026||[]).forEach(g=>{ if(g.date===dayStr) ev.push({time:g.etTime||'', title:`Westwood One: ${g.matchup}`, priority:'high', status:g.status, sourceUrl:g.sourceUrl, type:'Westwood One NFL Radio'}); });
  (VERIFIED_STANFORD_2026||[]).forEach(g=>{ if(g.date===dayStr) ev.push({time:g.time||'', title:`Stanford vs ${g.opponent}`, priority:'high', status:g.status, sourceUrl:g.sourceUrl, type:'NCAAF - Stanford'}); });
  (VERIFIED_CAL_2026||[]).forEach(g=>{ if(g.date===dayStr) ev.push({time:g.time||'', title:`Cal vs ${g.opponent}`, priority:'high', status:g.status, sourceUrl:g.sourceUrl, type:'NCAAF - Cal'}); });
  return ev;
}

function getSeasonWindowsForDay(dayStr){
  return (SEASON_WINDOWS||[]).filter(w=>dayStr>=w.start && dayStr<=w.end);
}

function dayStatus(dayStr){
  const events=getVerifiedEventsForDay(dayStr);
  const windows=getSeasonWindowsForDay(dayStr);
  const highWindows=windows.filter(w=>w.priority==='high');
  let status='free';
  let label='Free (no known conflicts)';
  if(events.length>0 || highWindows.length>0){
    // If we have specific verified times only, we could be partial; but season windows mean potentially all-day busy.
    const hasSeasonWindow=highWindows.length>0;
    const hasTimedEvents=events.some(e=>e.time && e.time!=='TBD');
    if(hasSeasonWindow){ status='busy'; label='Busy / conflict window'; }
    else if(hasTimedEvents){ status='partial'; label='Partial free time (specific events)'; }
    else { status='busy'; label='Busy / conflict'; }
  }
  return {status,label,events,windows};
}

function renderCalendar(containerId, year, month, selectedStr, onSelect){
  const cont=document.getElementById(containerId);
  const first=new Date(Date.UTC(year,month,1));
  const startDay=first.getUTCDay();
  const daysInMonth=new Date(Date.UTC(year,month+1,0)).getUTCDate();
  const prevDays=new Date(Date.UTC(year,month,0)).getUTCDate();
  let html='<div class="calendar">';
  ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].forEach(d=>html+=`<div class="cal-head">${d}</div>`);
  for(let i=0;i<42;i++){
    const dayNum=i-startDay+1;
    let d, inMonth=true;
    if(dayNum<1){ d=new Date(Date.UTC(year,month-1,prevDays+dayNum)); inMonth=false; }
    else if(dayNum>daysInMonth){ d=new Date(Date.UTC(year,month+1,dayNum-daysInMonth)); inMonth=false; }
    else { d=new Date(Date.UTC(year,month,dayNum)); }
    const ds=fmtDate(d);
    const st=dayStatus(ds);
    const sel=ds===selectedStr?' selected':'';
    const other=inMonth?'':' other';
    const evs=st.events.slice(0,2);
    html+=`<div class="day${other}${sel}" data-date="${ds}" role="button" tabindex="0" aria-label="${ds} ${st.label}">`;
    html+=`<div class="dnum">${d.getUTCDate()}</div>`;
    html+=`<div class="status ${st.status}">${st.status==='free'?'Free':st.status==='partial'?'Partial':'Busy'}</div>`;
    evs.forEach(e=>{ html+=`<div class="ev ${e.priority==='high'?'high':''} ${e.status==='estimated'?'est':''}" title="${e.title.replace(/"/g,'&quot;')}">${e.title}</div>`; });
    const extra=st.events.length+st.windows.length - evs.length;
    if(extra>0) html+=`<div class="more">+${extra} more</div>`;
    if(st.events.length===0 && st.windows.length>0) html+=`<div class="ev est" title="${st.windows[0].label}">${st.windows[0].scope}</div>`;
    html+=`</div>`;
  }
  html+='</div>';
  cont.innerHTML=html;
  cont.querySelectorAll('.day').forEach(el=>{
    el.addEventListener('click',()=>onSelect(el.dataset.date));
    el.addEventListener('keydown',(e)=>{ if(e.key==='Enter'||e.key===' ') { e.preventDefault(); onSelect(el.dataset.date); } });
  });
}

function renderDayDetail(dayStr){
  const el=document.getElementById('day-detail');
  if(!el) return;
  const st=dayStatus(dayStr);
  let html=`<h3>${dayStr} <span class="badge ${st.status==='free'?'free':'busy'}">${st.label}</span></h3>`;
  html+=`<p class="small">Timezone reference: Pacific Time (PT/PST/PDT as applicable). Minute-level free time can only be computed from verified event times; season-window busy days are marked as estimated busy for planning.</p>`;
  if(st.events.length===0 && st.windows.length===0){
    html+=`<div class="callout good"><strong>No known conflicts found in current dataset.</strong> This does not guarantee no games; verify against official schedules linked on the Sources page before booking travel.</div>`;
  }
  if(st.events.length>0){
    html+=`<h4>Verified/TBD Events</h4><div class="table-wrap"><table><thead><tr><th>Time</th><th>Event</th><th>Type</th><th>Priority</th><th>Status</th><th>Source</th></tr></thead><tbody>`;
    st.events.forEach(e=>{
      html+=`<tr class="${e.priority==='high'?'high-row':''}"><td>${e.time||'<span class="badge tbd">TBD</span>'}</td><td>${e.title}</td><td>${e.type}</td><td><span class="badge high">High</span></td><td><span class="badge ${e.status}">${e.status}</span></td><td><a href="${e.sourceUrl}" target="_blank" rel="noopener">Source</a></td></tr>`;
    });
    html+=`</tbody></table></div>`;
  }
  if(st.windows.length>0){
    html+=`<h4>Season Windows Covering This Day</h4><div class="table-wrap"><table><thead><tr><th>Window</th><th>Scope</th><th>Priority</th><th>Status</th><th>Dates</th><th>Source</th><th>Note</th></tr></thead><tbody>`;
    st.windows.forEach(w=>{
      html+=`<tr class="${w.status==='estimated'?'est-row':''}"><td>${w.label}</td><td>${w.scope}</td><td><span class="badge ${w.priority==='high'?'high':'med'}">${w.priority}</span></td><td><span class="badge ${w.status}">${w.status}</span></td><td>${w.start} to ${w.end}</td><td><a href="${w.sourceUrl}" target="_blank" rel="noopener">Source</a></td><td class="small">${w.note||''}</td></tr>`;
    });
    html+=`</tbody></table></div>`;
  }
  // Simple day timeline
  html+=`<h4>Day Timeline (planning estimate)</h4><div class="timeline">`;
  for(let h=0;h<24;h++){
    const label=h===0?'12:00 AM':h<12?`${h}:00 AM`:h===12?'12:00 PM':`${h-12}:00 PM`;
    let slotClass='free', slotText='Free (no verified event in dataset)';
    if(st.windows.length>0){ slotClass='partial'; slotText='Estimated busy season window - check official daily schedule'; }
    if(st.events.length>0){ slotClass='partial'; slotText='Event(s) on this day - see verified times above'; }
    if(st.windows.length===0 && st.events.length===0){ slotClass='free'; slotText='No known conflict in dataset'; }
    html+=`<div class="trow"><div class="ttime">${label}</div><div class="tslot ${slotClass}">${slotText}</div></div>`;
  }
  html+=`</div>`;
  html+=`<div class="callout warn small"><strong>Accuracy note:</strong> This timeline is a planning aid. "Estimated busy season window" means a sport in scope is in season; it does not mean every minute is occupied. For minute-level accuracy, consult the official day schedule linked in Sources. Unverified/TBD times are left blank or marked TBD.</div>`;
  el.innerHTML=html;
}
