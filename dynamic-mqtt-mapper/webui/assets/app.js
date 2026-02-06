
const $ = (sel, el=document) => el.querySelector(sel);
const state = { devices: {}, filterText: '', filterType: '' };

async function load(){
  try{ const res = await fetch('api/devices', {cache:'no-store'}); state.devices = await res.json(); render(); $('#ts').textContent = new Date().toLocaleString(); }
  catch(e){ console.error('Laden fehlgeschlagen', e); }
}

function render(){
  const list = Object.entries(state.devices).map(([id,dev])=>({id,...dev}));
  const types = [...new Set(list.map(d=>d.meta?.type).filter(Boolean))].sort();
  const sel = $('#typeFilter'); const current = sel.value;
  sel.innerHTML = '<option value="">Alle Gerätetypen</option>' + types.map(t=>`<option ${t===current?'selected':''} value="${t}">${t}</option>`).join('');
  const fText = state.filterText.toLowerCase(); const fType = state.filterType;
  const filtered = list.filter(d=>{ const hay=[d.id,d.meta?.alias,d.meta?.address,d.meta?.type].join(' ').toLowerCase(); return (!fText||hay.includes(fText)) && (!fType||d.meta?.type===fType); });
  document.getElementById('stats').textContent = `${filtered.length} von ${list.length} Geräten angezeigt`;
  const container = document.getElementById('devices'); container.innerHTML = filtered.map(renderCard).join('');
}

function renderCard(d){
  const title = `${d.meta?.alias || d.id}`; const subtitle = `${d.id} • ${d.meta?.type || 'Unbekannt'} ${d.meta?.address ? '• '+d.meta.address : ''}`;
  const entities = Object.entries(d.entities||{}).sort((a,b)=>a[0].localeCompare(b[0])).map(([key, ent])=>{
    const val = ent.last_value; const valStr = typeof val==='boolean' ? (val?'ON':'OFF') : (val ?? ''); const unit = ent.unit ? ` ${ent.unit}` : '';
    return `<tr><td>${key}</td><td>${valStr}${unit}</td></tr>`; }).join('');
  return `<div class="card"><h2>${title}</h2><div class="meta">${subtitle}</div><table><thead><tr><th>Entität</th><th>Wert</th></tr></thead><tbody>${entities}</tbody></table></div>`;
}

document.getElementById('search').addEventListener('input', e=>{ state.filterText = e.target.value || ''; render(); });
document.getElementById('typeFilter').addEventListener('change', e=>{ state.filterType = e.target.value || ''; render(); });
document.getElementById('refreshBtn').addEventListener('click', load);
load(); setInterval(load, 5000);
