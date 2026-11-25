export const zone = 'America/Los_Angeles';
const dayFormat = new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'});
const clock = new Intl.DateTimeFormat('en-US',{timeZone:zone,hour:'2-digit',minute:'2-digit',hourCycle:'h23',timeZoneName:'short'});
export function dayOf(ms){const p=Object.fromEntries(dayFormat.formatToParts(ms).map(({type,value})=>[type,value]));return `${p.year}-${p.month}-${p.day}`;}
export const shift = (day,n) => new Date(Date.parse(day)+n*86400000).toISOString().slice(0,10);
export function local(day,time){const utc=Date.parse(`${day}T${time}:00Z`);const p=clock.formatToParts(utc+8*3600000);return utc+(p.find(x=>x.type==='timeZoneName').value==='PDT'?7:8)*3600000;}
export const fmt = ms => clock.format(ms);
export function intervals(rows,lo,hi){const spans=rows.filter(r=>Number.isFinite(r.start)).map(r=>[Math.max(lo,r.start),Math.min(hi,r.start+r.duration*60000)]).filter(([a,b])=>a<b).sort((a,b)=>a[0]-b[0]);const busy=[],gaps=[];let cursor=lo;for(const [a,b] of spans){const tail=busy.at(-1);if(tail&&a<=tail[1])tail[1]=Math.max(tail[1],b);else busy.push([a,b]);}for(const [a,b] of busy){if(cursor<a)gaps.push([cursor,a]);cursor=b;}if(cursor<hi)gaps.push([cursor,hi]);return {busy,gaps};}
