const API = 'https://machine-failure-prediction-production-22fe.up.railway.app';

const RISK_ICONS = {
  LOW:      '✓',
  MEDIUM:   '▲',
  HIGH:     '⚠',
  CRITICAL: '✕',
};

// ============================================================
// TABS
// ============================================================
document.querySelectorAll('.tab:not(.tab-disabled)').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
  });
});

// ============================================================
// API STATUS
// ============================================================
async function checkApiStatus() {
  const dot  = document.getElementById('statusDot');
  const text = document.getElementById('statusText');
  try {
    const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(5000) });
    const data = await res.json();
    if (data.status === 'ok') {
      dot.className  = 'status-dot online';
      text.textContent = 'API Online';
    } else {
      throw new Error();
    }
  } catch {
    dot.className  = 'status-dot offline';
    text.textContent = 'API Indisponível';
  }
}

checkApiStatus();

// ============================================================
// INDIVIDUAL PREDICTION
// ============================================================
document.getElementById('formIndividual').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('btnPredict');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Analisando...';

  const fd = new FormData(e.target);

  const payload = {
    'Temperatura Ar [K]':        parseFloat(fd.get('temperatura_ar')),
    'Temperatura Processo [K]':  parseFloat(fd.get('temperatura_processo')),
    'Velocidade Rotacao [rpm]':  parseFloat(fd.get('velocidade_rotacao')),
    'Torque [Nm]':               parseFloat(fd.get('torque')),
    'Desgaste Ferramenta [min]': parseFloat(fd.get('desgaste_ferramenta')),
    'Tipo':                      fd.get('tipo'),
  };

  try {
    const res  = await fetch(`${API}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderResult(data);
  } catch (err) {
    renderError(err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z"/></svg>
      Analisar Máquina`;
  }
});

function renderResult(data) {
  const level = data.risk_level;
  const pct   = (data.probability_failure * 100).toFixed(1);

  document.getElementById('resultEmpty').style.display   = 'none';
  document.getElementById('resultContent').style.display = 'flex';

  const badge = document.getElementById('riskBadge');
  badge.className   = `risk-badge ${level}`;
  badge.textContent = RISK_ICONS[level];

  const label = document.getElementById('riskLabel');
  label.className   = `result-value ${level}`;
  label.textContent = level;

  document.getElementById('probValue').textContent = `${pct}%`;

  const bar = document.getElementById('probBar');
  bar.className = `prob-bar-fill ${level}`;
  setTimeout(() => { bar.style.width = `${Math.min(pct, 100)}%`; }, 50);

  const msg = document.getElementById('resultMessage');
  msg.className   = `result-message ${level}`;
  msg.textContent = data.message;

  document.getElementById('resultStatus').textContent =
    `Predição: ${data.prediction === 1 ? 'Falha detectada' : 'Normal'} · ${new Date().toLocaleTimeString('pt-BR')}`;
}

function renderError(detail) {
  document.getElementById('resultEmpty').style.display   = 'none';
  document.getElementById('resultContent').style.display = 'flex';

  const badge = document.getElementById('riskBadge');
  badge.className   = 'risk-badge CRITICAL';
  badge.textContent = '!';

  const label = document.getElementById('riskLabel');
  label.className   = 'result-value CRITICAL';
  label.textContent = 'ERRO';

  document.getElementById('probValue').textContent = '—';
  document.getElementById('probBar').style.width   = '0%';

  const msg = document.getElementById('resultMessage');
  msg.className   = 'result-message CRITICAL';
  msg.textContent = `Não foi possível conectar à API. Verifique sua conexão. (${detail})`;

  document.getElementById('resultStatus').textContent = new Date().toLocaleTimeString('pt-BR');
}

// ============================================================
// BATCH — UPLOAD & PARSE CSV
// ============================================================
let parsedMachines = [];

const uploadArea = document.getElementById('uploadArea');
const csvInput   = document.getElementById('csvInput');

uploadArea.addEventListener('click', () => csvInput.click());
uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('drag-over'); });
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('drag-over'));
uploadArea.addEventListener('drop', e => {
  e.preventDefault();
  uploadArea.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) processCsvFile(file);
});

csvInput.addEventListener('change', e => {
  if (e.target.files[0]) processCsvFile(e.target.files[0]);
});

document.getElementById('btnClearCsv').addEventListener('click', () => {
  parsedMachines = [];
  csvInput.value = '';
  document.getElementById('batchPreview').style.display  = 'none';
  document.getElementById('batchResults').style.display  = 'none';
  uploadArea.style.display = '';
});

function processCsvFile(file) {
  const reader = new FileReader();
  reader.onload = e => {
    const lines = e.target.result.trim().split('\n');
    if (lines.length < 2) { alert('CSV vazio ou sem dados.'); return; }

    const headers = lines[0].split(',').map(h => h.trim());
    const required = [
      'Temperatura Ar [K]', 'Temperatura Processo [K]',
      'Velocidade Rotacao [rpm]', 'Torque [Nm]',
      'Desgaste Ferramenta [min]', 'Tipo'
    ];

    const missing = required.filter(r => !headers.includes(r));
    if (missing.length) {
      alert(`Colunas ausentes no CSV:\n${missing.join('\n')}`);
      return;
    }

    parsedMachines = lines.slice(1).filter(l => l.trim()).map(line => {
      const vals = line.split(',').map(v => v.trim());
      const row  = {};
      headers.forEach((h, i) => { row[h] = vals[i]; });
      return {
        'Temperatura Ar [K]':        parseFloat(row['Temperatura Ar [K]']),
        'Temperatura Processo [K]':  parseFloat(row['Temperatura Processo [K]']),
        'Velocidade Rotacao [rpm]':  parseFloat(row['Velocidade Rotacao [rpm]']),
        'Torque [Nm]':               parseFloat(row['Torque [Nm]']),
        'Desgaste Ferramenta [min]': parseFloat(row['Desgaste Ferramenta [min]']),
        'Tipo':                      row['Tipo'],
      };
    });

    uploadArea.style.display = 'none';
    document.getElementById('batchResults').style.display = 'none';
    document.getElementById('previewCount').textContent   = `${parsedMachines.length} máquinas carregadas`;
    document.getElementById('batchPreview').style.display = '';
  };
  reader.readAsText(file);
}

// ============================================================
// BATCH — PREDICT
// ============================================================
document.getElementById('btnBatchPredict').addEventListener('click', async () => {
  if (!parsedMachines.length) return;

  const btn = document.getElementById('btnBatchPredict');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Analisando...';

  try {
    const res = await fetch(`${API}/predict/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ machines: parsedMachines }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderBatchResults(data);
  } catch (err) {
    alert(`Erro ao analisar lote: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z"/></svg>
      Analisar Lote`;
  }
});

function renderBatchResults(data) {
  const predictions = data.predictions;

  // Combina com input original e ordena por risco (maior primeiro)
  const ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
  const rows  = predictions.map((p, i) => ({ ...p, input: parsedMachines[i], idx: i + 1 }));
  rows.sort((a, b) => ORDER[a.risk_level] - ORDER[b.risk_level]);

  // Contagem por nível
  const counts = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
  predictions.forEach(p => counts[p.risk_level]++);

  // Summary chips
  const summary = document.getElementById('batchSummary');
  summary.innerHTML = Object.entries(counts).map(([level, n]) => `
    <div class="summary-chip chip-${level.toLowerCase()}">
      <div>
        <div class="chip-count">${n}</div>
        <div class="chip-label">${level}</div>
      </div>
    </div>
  `).join('') + `
    <div class="summary-chip" style="margin-left:auto">
      <div>
        <div class="chip-count">${data.total}</div>
        <div class="chip-label">Total</div>
      </div>
    </div>`;

  // Table rows
  const tbody = document.getElementById('resultsBody');
  tbody.innerHTML = rows.map(r => `
    <tr>
      <td>${r.idx}</td>
      <td>${r.input['Tipo']}</td>
      <td>${r.input['Temperatura Ar [K]'].toFixed(1)}</td>
      <td>${r.input['Velocidade Rotacao [rpm]'].toFixed(0)}</td>
      <td>${r.input['Torque [Nm]'].toFixed(1)}</td>
      <td>${r.input['Desgaste Ferramenta [min]'].toFixed(0)} min</td>
      <td>${(r.probability_failure * 100).toFixed(1)}%</td>
      <td><span class="table-badge ${r.risk_level}">${r.risk_level}</span></td>
    </tr>
  `).join('');

  document.getElementById('batchResults').style.display = '';
}
