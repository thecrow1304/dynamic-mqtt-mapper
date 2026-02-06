
const $ = (sel, el=document) => el.querySelector(sel);
const $$ = (sel, el=document) => Array.from(el.querySelectorAll(sel));

const state = {
  devices: {},
  filterText: '',
  filterType: ''
};

async function load() {
  try {
    // Relative Pfad, damit es in HA-Ingress funktioniert
    const res = await fetch('api/devices', { cache: 'no-store' });
    const data = await res.json();
    state.devices = data || {};
    render();
    $('#ts').textContent = new Date().toLocaleString();
  } catch (e) {
    console.error('Laden fehlgeschlagen', e);
  }
}

function render() {
  const devices = state.devices;
  const list = Object.entries(devices).map(([id, dev]) => ({ id, ...dev }));

  // Fülle Filterauswahl für Typen
  const types = [...new Set(list.map(d => d.meta?.type).filter(Boolean))].sort();
  const sel = $('#typeFilter');
  const current = sel.value;
  sel.innerHTML = '<option value="">Alle Gerätetypen</option>' + types.map(t => `<option ${t===current?'selected':''} value="${t}">${t}</option>`).join('');

  // Anwenden von Filtern
  const fText = state.filterText.toLowerCase();
  const fType = state.filterType;
  const filtered = list.filter(d => {
    const hay = [d.id, d.meta?.alias, d.meta?.address, d.meta?.type].join(' ').toLowerCase();
    const matchText = !fText || hay.includes(fText);
    const matchType = !fType || (d.meta?.type === fType);
    return matchText && matchType;
  });

  // Stats
  $('#stats').textContent = `${filtered.length} von ${list.length} Geräten angezeigt`;

  // Render Karten
  const container = $('#devices');
  container.innerHTML = filtered.map(d => renderCard(d)).join('');
}

function renderCard(d) {
  const title = `${d.meta?.alias || d.id}`;
  const subtitle = `${d.id} • ${d.meta?.type || 'Unbekannt'} ${d.meta?.address ? '• '+d.meta.address : ''}`;

  const entities = Object.entries(d.entities || {})
    .sort((a,b) => a[0].localeCompare(b[0]))
    .map(([key, ent]) => {
      const val = ent.last_value;
      const valStr = typeof val === 'boolean' ? (val ? 'ON' : 'OFF') : (val ?? '');
      const unit = ent.unit ? ` ${ent.unit}` : '';
      return `<tr><td>${key}</td><td>${valStr}${unit}</td></tr>`;
    }).join('');

  return `
    <div class="card">
      <h2>${title}</h2>
      <div class="meta">${subtitle}</div>
      <table>
        <thead><tr><th>Entität</th><th>Wert</th></tr></thead>
        <tbody>${entities}</tbody>
      </table>
    </div>
  `;
}

// Event Listeners
$('#search').addEventListener('input', (e) => {
  state.filterText = e.target.value || '';
  render();
});
$('#typeFilter').addEventListener('change', (e) => {
  state.filterType = e.target.value || '';
  render();
});
$('#refreshBtn').addEventListener('click', load);

// Auto-Refresh
load();
setInterval(load, 5000);
