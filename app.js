(() => {
  const $ = (id) => document.getElementById(id);
  const page = document.body.dataset.page;
  const teams = [
    ['Arizona Diamondbacks','dbacks'],['Atlanta Braves','braves'],['Athletics','athletics'],['Baltimore Orioles','orioles'],['Boston Red Sox','redsox'],['Chicago Cubs','cubs'],['Chicago White Sox','whitesox'],['Cincinnati Reds','reds'],['Cleveland Guardians','guardians'],['Colorado Rockies','rockies'],['Detroit Tigers','tigers'],['Houston Astros','astros'],['Kansas City Royals','royals'],['Los Angeles Angels','angels'],['Los Angeles Dodgers','dodgers'],['Miami Marlins','marlins'],['Milwaukee Brewers','brewers'],['Minnesota Twins','twins'],['New York Mets','mets'],['New York Yankees','yankees'],['Philadelphia Phillies','phillies'],['Pittsburgh Pirates','pirates'],['San Diego Padres','padres'],['San Francisco Giants','giants'],['Seattle Mariners','mariners'],['St. Louis Cardinals','cardinals'],['Tampa Bay Rays','rays'],['Texas Rangers','rangers'],['Toronto Blue Jays','bluejays'],['Washington Nationals','nationals']
  ];
  // Each dated Cal entry below comes from the linked official announcement. Unconfirmed kickoff times are intentionally blank.
  const calFixtures = [
    {date:'2027-09-04',fixture:'California vs Florida',kickoff:'',venue:'Berkeley, California',url:'https://calbears.com/news/2020/2/7/football-cal-and-florida-schedule-home-and-home-series-in-2026-and-2027',label:'Cal–Florida series announcement'},
    {date:'2028-09-02',fixture:'California vs Wyoming',kickoff:'',venue:'Berkeley, California',url:'https://calbears.com/news/2020/2/11/football-cal-adds-minnesota-and-wyoming-to-future-schedules',label:'Cal future schedules announcement'},
    {date:'2028-09-09',fixture:'California vs San José State',kickoff:'',venue:'Berkeley, California',url:'https://calbears.com/news/2025/1/30/football-bears-announce-future-games-against-san-jose-state-wagner.aspx',label:'Cal–San José State announcement'},
    {date:'2028-09-16',fixture:'California at Minnesota',kickoff:'',venue:'Minneapolis, Minnesota',url:'https://calbears.com/news/2020/2/11/football-cal-adds-minnesota-and-wyoming-to-future-schedules',label:'Cal future schedules announcement'},
    {date:'2029-09-01',fixture:'California vs Wisconsin',kickoff:'',venue:'Berkeley, California',url:'https://calbears.com/news/2024/3/26/cal-wisconsin-to-meet-in-2029-2030',label:'Cal–Wisconsin announcement'},
    {date:'2029-09-08',fixture:'California at Wyoming',kickoff:'',venue:'Laramie, Wyoming',url:'https://calbears.com/news/2022/4/15/football-cal-minnesota-move-berkeley-game-up-to-2025',label:'Cal schedule update'}
  ];

  const fmtDate = (s, opts={weekday:'long',year:'numeric',month:'long',day:'numeric'}) => new Intl.DateTimeFormat('en-US',{timeZone:'UTC',...opts}).format(new Date(`${s}T12:00:00Z`));
  const fmtTime = (iso) => new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(new Date(iso));
  const dateKey = (y,m,d) => `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;

  if (page === 'mlb') {
    const dir = $('teamDirectory');
    if (dir) dir.innerHTML = teams.map(([name,slug]) => `<a class="team-chip ${slug==='giants'||slug==='athletics'?'team-priority':''}" href="https://www.mlb.com/${slug}" target="_blank" rel="noopener"><span>${name}</span><small>${slug==='giants'||slug==='athletics'?'HIGH PRIORITY':'MLB CLUB'} · OFFICIAL ↗</small></a>`).join('');
  }

  if (page === 'football') {
    const body = $('calFixtures');
    if (body) body.innerHTML = calFixtures.map(g => `<tr><td>${fmtDate(g.date,{year:'numeric',month:'short',day:'numeric'})}</td><td><strong>${g.fixture}</strong><br><small>California · high priority</small></td><td class="blank-value"><span aria-label="Kickoff time unverified">—</span></td><td>${g.venue}</td><td><a href="${g.url}" target="_blank" rel="noopener">${g.label} ↗</a></td></tr>`).join('');
  }

  if (page !== 'overview') return;

  const minDate = new Date(Date.UTC(2026,0,1));
  const maxDate = new Date(Date.UTC(2029,11,1));
  let month = new Date(Date.UTC(2027,0,1));
  let selected = '2027-01-01';
  let gameCache = {};
  let loadState = 'idle';

  const sameMonth = (key) => key.slice(0,7) === `${month.getUTCFullYear()}-${String(month.getUTCMonth()+1).padStart(2,'0')}`;
  const selectedGames = () => gameCache[selected] || [];
  const fixturesFor = (key) => calFixtures.filter(g => g.date === key);

  function renderCalendar() {
    const y = month.getUTCFullYear(), m = month.getUTCMonth();
    $('monthTitle').textContent = new Intl.DateTimeFormat('en-US',{timeZone:'UTC',month:'long',year:'numeric'}).format(month);
    const firstDay = new Date(Date.UTC(y,m,1)).getUTCDay();
    const total = new Date(Date.UTC(y,m+1,0)).getUTCDate();
    const grid = $('calendarGrid');
    grid.innerHTML = '';
    for (let i=0;i<firstDay;i++) grid.append(document.createElement('span')).className='calendar-empty';
    for (let day=1;day<=total;day++) {
      const key=dateKey(y,m,day), btn=document.createElement('button');
      btn.className='day-cell'+(key===selected?' selected':''); btn.type='button'; btn.setAttribute('aria-label',fmtDate(key));
      const games=gameCache[key]||[], cal=fixturesFor(key), count=games.length+cal.length;
      const number=document.createElement('span'); number.className='day-number'; number.textContent=day; btn.append(number);
      if (count) {const marker=document.createElement('span'); marker.className='day-marker'; marker.textContent=`${count} listed`; btn.append(marker); btn.classList.add('has-game');}
      else {const marker=document.createElement('span'); marker.className='day-marker day-marker-empty'; marker.textContent=loadState==='loaded'?'No MLB entry':'Checking'; btn.append(marker);}
      btn.addEventListener('click',()=>{selected=key;renderCalendar();renderDay();}); grid.append(btn);
    }
  }

  function renderDay() {
    $('selectedDate').textContent=fmtDate(selected);
    const mlb=selectedGames(), cal=fixturesFor(selected), all=mlb.length+cal.length;
    const pill=$('dayStatus');
    if (all) {pill.textContent=`${all} listed scheduled ${all===1?'event':'events'}`; pill.className='status-pill status-busy';}
    else if (loadState==='error') {pill.textContent='MLB data unavailable';pill.className='status-pill status-unknown';}
    else {pill.textContent='No listed MLB / Cal date fixture';pill.className='status-pill status-unknown';}
    $('freeAnswer').textContent='Not certifiable';
    $('freeExplanation').textContent=all ? 'At least one official MLB schedule entry or officially dated Cal fixture is listed. Radio airing and exact event end times still need verification.' : 'No game in these displayed sources is not proof of a free day: NFL, Stanford and radio schedules are not fully verified.';
    const list=$('gameList'); list.innerHTML='';
    if (!all) list.innerHTML=`<div class="empty-state"><strong>No game entry in the loaded sources.</strong><p>This is not a “free” designation. Other required schedules and radio carriage are incomplete.</p></div>`;
    mlb.forEach(g=>{
      const item=document.createElement('article'); item.className='game-item';
      const start=g.gameDate?fmtTime(g.gameDate):'Start time not supplied';
      const away=g.teams?.away?.team?.name||'Away team unlisted', home=g.teams?.home?.team?.name||'Home team unlisted';
      const type=g.gameType?` · ${gameTypeName(g.gameType)}`:'';
      const priority=(away.includes('Giants')||home.includes('Giants')||away.includes('Athletics')||home.includes('Athletics'))?' · HIGH PRIORITY':'';
      const eventStatus=g.status?.detailedState?` · ${escapeHtml(g.status.detailedState)}`:'';
      item.innerHTML=`<div class="game-item-top"><span class="sport-label label-mlb">MLB${type}</span>${priority?'<span class="priority-flag">HIGH</span>':''}</div><strong>${escapeHtml(away)} at ${escapeHtml(home)}</strong><p>${escapeHtml(start)}${g.venue?.name?` · ${escapeHtml(g.venue.name)}`:''}${eventStatus}</p><a href="https://www.mlb.com/gameday/${encodeURIComponent(g.gamePk)}" target="_blank" rel="noopener">Official MLB game record ↗</a>`;
      list.append(item);
    });
    cal.forEach(g=>{
      const item=document.createElement('article'); item.className='game-item';
      item.innerHTML=`<div class="game-item-top"><span class="sport-label label-cal">NCAA · CAL</span><span class="priority-flag">HIGH</span></div><strong>${g.fixture}</strong><p>Kickoff not confirmed · ${g.venue}</p><a href="${g.url}" target="_blank" rel="noopener">${g.label} ↗</a>`; list.append(item);
    });
  }

  function gameTypeName(code) {return ({E:'Exhibition',S:'Spring Training',R:'Regular season',F:'Wild Card',D:'Division Series',L:'League Championship',W:'World Series'})[code]||'Scheduled';}

  async function loadMonth() {
    const y=month.getUTCFullYear(),m=month.getUTCMonth();
    const start=dateKey(y,m,1), end=dateKey(y,m,new Date(Date.UTC(y,m+1,0)).getUTCDate());
    const url=`https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=${start}&endDate=${end}&hydrate=team,venue`;
    $('mlbFeedLink')?.setAttribute('href',url);
    loadState='loading'; $('loadNote').textContent='Loading official MLB schedule data for this month…'; renderCalendar(); renderDay();
    try {
      const response=await fetch(url,{headers:{Accept:'application/json'}});
      if(!response.ok) throw new Error(`HTTP ${response.status}`);
      const data=await response.json();
      const byDate={};
      for(const entry of data.dates||[]) for(const g of entry.games||[]) (byDate[g.officialDate] ||= []).push(g);
      gameCache=byDate; loadState='loaded';
      const n=Object.values(byDate).reduce((sum,a)=>sum+a.length,0);
      $('loadNote').innerHTML=`Official MLB feed loaded · ${n} scheduled ${n===1?'game':'games'} returned for this month. <a href="${url}" target="_blank" rel="noopener">Open source response ↗</a>`;
    } catch(error) {
      gameCache={}; loadState='error';
      $('loadNote').innerHTML=`Could not load the official MLB feed (${escapeHtml(error.message)}). Dates remain unknown, not free. <a href="${url}" target="_blank" rel="noopener">Open official feed ↗</a>`;
    }
    renderCalendar(); renderDay();
  }

  function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  $('prevMonth').addEventListener('click',()=>shiftMonth(-1));
  $('nextMonth').addEventListener('click',()=>shiftMonth(1));
  $('todayBtn').addEventListener('click',()=>{const parts=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()).map(p=>[p.type,p.value]));const y=Number(parts.year),m=Number(parts.month)-1,d=Number(parts.day);month=new Date(Date.UTC(y,m,1));selected=dateKey(y,m,d);loadMonth();});
  function shiftMonth(amount){const next=new Date(Date.UTC(month.getUTCFullYear(),month.getUTCMonth()+amount,1));if(next<minDate||next>maxDate)return;month=next;selected=dateKey(next.getUTCFullYear(),next.getUTCMonth(),1);loadMonth();}
  $('windowLength').addEventListener('change',()=>{
    const days=$('windowLength').value;
    $('finderResult').textContent=`No ${days}-night window is certifiable`;
    $('finderNote').textContent='The currently available schedule evidence does not cover all required leagues and local radio broadcasts across a complete search range. This is not a claim that there are no open dates.';
  });
  renderCalendar();renderDay();loadMonth();
})();
