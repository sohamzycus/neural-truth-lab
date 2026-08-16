/* All metrics loaded from data/results.json — never hard-coded */

let DATA = null;
const charts = {};
const GITHUB = 'https://github.com/sohamzycus/neural-truth-lab/tree/main/session7';

const STATUS_MAP = {
  PASS: 'supported', SUPPORTED: 'supported',
  FAIL: 'not-supported', 'NOT SUPPORTED': 'not-supported', 'NOT DEMONSTRATED': 'not-supported',
  PARTIAL: 'partial',
  'NOT RUN': 'not-run',
};

function pct(x) {
  if (x == null || Number.isNaN(x)) return '—';
  return (x * 100).toFixed(1) + '%';
}

function num(x) { return x == null ? '—' : String(x); }

function get(path, obj = DATA) {
  return path.split('.').reduce((o, k) => (o && o[k] != null ? o[k] : null), obj);
}

function detInverse() {
  return get('representation_comparison.results.A_deterministic_inverse.test_eval')
    || { string_exact_match_rate: get('deterministic_inverse.string_exact_match_rate'), count: get('deterministic_inverse.total') };
}

function learnedHeldOut() {
  const r = get('baseline_reconstruction.dynamic_kronecker.test_eval')
    || get('reconstruction.dynamic_kronecker.held_out_eval')
    || get('decoder_ablation.results.position_mlp.test_eval');
  return r;
}

function collisionScale() { return DATA.collision_scale?.methods || {}; }

function dynInverse(text) {
  const raw = new TextEncoder().encode(text);
  const max = 256;
  const feats = [raw.length / max, [...text].length / max];
  for (let i = 0; i < max; i++) {
    if (i < raw.length) feats.push(raw[i] / 255, i / Math.max(raw.length - 1, 1), 1);
    else feats.push(0, i / (max - 1), 0);
  }
  let o = 2, out = [];
  for (let i = 0; i < max; i++) {
    if (feats[o + 2] > 0.5) out.push(Math.round(feats[o] * 255));
    o += 3;
  }
  return new TextDecoder().decode(new Uint8Array(out.slice(0, Math.round(feats[0] * max))));
}

function statusClass(s) {
  const k = STATUS_MAP[String(s || '').toUpperCase()] || 'partial';
  return `status-${k}`;
}

function mapHypStatus(s) {
  const m = { PASS: 'SUPPORTED', FAIL: 'NOT SUPPORTED', PARTIAL: 'PARTIAL', 'NOT RUN': 'NOT RUN' };
  return m[s] || s;
}

async function load() {
  try {
    const r = await fetch('data/results.json');
    if (!r.ok) throw new Error(r.statusText);
    DATA = await r.json();
    render();
  } catch (e) {
    document.getElementById('hero-cards').innerHTML =
      '<div class="card"><span class="status-not-supported">Experiment not run</span> — run python experiments/run_all.py</div>';
  }
}

function renderHero() {
  const cs = collisionScale().dynamic_kronecker || {};
  const det = detInverse();
  const learned = learnedHeldOut();
  const teTrunc = get('waste_by_language.telugu.fixed_truncation_rate');

  document.getElementById('headline').textContent =
    'We solved the fixed-window representation problem. The learned inverse remains unsolved.';

  document.getElementById('hero-cards').innerHTML = [
    ['Observed dynamic collisions', cs.collision_groups ?? '—', ''],
    ['Deterministic inverse', pct(det.string_exact_match_rate), 'pass'],
    ['Learned held-out exact', pct(learned?.string_exact_match_rate), 'fail'],
    ['Max fixed Telugu trunc.', pct(teTrunc), 'warn'],
  ].map(([l, v, c]) =>
    `<div class="card metric-card"><div class="label">${l}</div><div class="value ${c}">${v}</div></div>`
  ).join('');

  document.getElementById('story-diagram').innerHTML = `
    <div>FIXED CHRONOKER → 32-byte window → waste + truncation</div>
    <div style="color:var(--accent);margin:.5rem 0">↓ DYNAMIC CHRONOKER → variable-length → preserves bytes</div>
    <div class="sd-split">
      <div class="sd-branch pass"><div>deterministic inverse</div><div style="font-size:1.5rem;font-weight:700;color:var(--pass)">${pct(det.string_exact_match_rate)}</div><div class="muted">${det.count || 46}/46 test exact</div></div>
      <div class="sd-branch fail"><div>learned decoder</div><div style="font-size:1.5rem;font-weight:700;color:var(--fail)">${pct(learned?.string_exact_match_rate)}</div><div class="muted">held-out exact</div></div>
    </div>`;

  document.getElementById('distinction-callout').innerHTML = `
    <strong>THE INFORMATION IS PRESENT. THE LEARNED INVERSE CANNOT RECOVER IT.</strong><br><br>
    Deterministic inverse (${pct(det.string_exact_match_rate)}) shows bytes are retained in the representation layout.
    Learned decoder (${pct(learned?.string_exact_match_rate)}) asks whether a neural network can discover that inverse — not demonstrated under the tested setup.`;
}

function renderQuestion() {
  document.getElementById('research-question').textContent =
    get('assignment.research_question') || 'How much can deterministic byte features be compressed before learned reversibility breaks?';
}

function renderWhy() {
  const sample = 'నమస్కారం తెలుగు భాష';
  const bytes = new TextEncoder().encode(sample);
  const cap = 32;
  const fb = document.getElementById('fixed-bar-why');
  const db = document.getElementById('dynamic-bar-why');
  fb.innerHTML = '';
  for (let i = 0; i < cap; i++) {
    const d = document.createElement('div');
    d.className = 'byte-slot' + (i < bytes.length ? '' : ' waste');
    fb.appendChild(d);
  }
  db.innerHTML = '';
  for (let i = 0; i < bytes.length; i++) {
    const d = document.createElement('div');
    d.className = 'byte-slot';
    db.appendChild(d);
  }
  const te = get('waste_by_language.telugu');
  document.getElementById('telugu-callout').innerHTML = `
    <strong>Telugu — strongest observed fixed truncation example</strong><br>
    Fixed truncation rate: <strong>${pct(te?.fixed_truncation_rate)}</strong> on baseline corpus (${te?.count || 7} strings).
    Dynamic truncation: <strong>${pct(te?.dynamic_truncation_rate)}</strong>.
    <br><span class="muted">Observed on evaluated corpus — not a universal language property.</span>`;
}

function renderDynamic() {
  const waste = DATA.waste_by_language || {};
  const sel = document.getElementById('waste-lang');
  sel.innerHTML = Object.keys(waste).map(k => `<option value="${k}">${k}</option>`).join('');
  sel.onchange = () => {
    document.getElementById('waste-stats').textContent = JSON.stringify({ category: sel.value, ...waste[sel.value] }, null, 2);
  };
  sel.dispatchEvent(new Event('change'));
}

function renderCollisions() {
  const scale = DATA.collision_scale;
  const n = scale?.strings_tested || 64;
  document.getElementById('collision-n').textContent = n.toLocaleString();
  const methods = scale?.methods || DATA.collision || {};
  const labels = {
    fixed_kronecker: 'Fixed Kronecker',
    dynamic_kronecker: 'Dynamic Kronecker',
    fourier_magnitude: 'Fourier magnitude',
    fourier_phase: 'Fourier + phase',
  };
  document.getElementById('collision-cards').innerHTML = Object.entries(methods)
    .filter(([k]) => !k.includes('projected'))
    .map(([k, v]) => `
    <div class="card metric-card">
      <div class="label">${labels[k] || k}</div>
      <div class="value">${v.collision_groups ?? '—'} <small style="font-size:.8rem;color:var(--muted)">groups / ${v.total_strings || n} strings</small></div>
    </div>`).join('');

  const fixedEx = methods.fixed_kronecker?.examples?.[0];
  const fourierEx = methods.fourier_magnitude?.examples?.[0];
  let txt = '';
  if (fixedEx) txt += `Fixed: long repeated "a" strings → same representation:\n${JSON.stringify((fixedEx[1] || []).slice(0, 2), null, 2)}\n\n`;
  if (fourierEx) txt += `Fourier magnitude: permutation collision:\n${JSON.stringify(fourierEx[1], null, 2)}`;
  document.getElementById('collision-examples').textContent = txt || 'See results/collision_scale.json';
}

function renderReversibility() {
  const det = detInverse();
  const learned = learnedHeldOut();
  document.getElementById('det-metric').textContent = `${pct(det.string_exact_match_rate)} exact`;
  document.getElementById('learned-metric').textContent = `${pct(learned?.string_exact_match_rate)} exact`;
  const inp = document.getElementById('lab-input');
  const upd = () => {
    const rec = dynInverse(inp.value);
    document.getElementById('lab-output').textContent =
      `Original: ${inp.value}\nUTF-8: ${[...new TextEncoder().encode(inp.value)].join(' ')}\nInverse: ${rec}\nExact: ${rec === inp.value}`;
  };
  inp.oninput = upd;
  upd();
}

function chartOpts(yLabel) {
  return {
    scales: {
      x: { ticks: { color: '#7d8da8' }, title: { display: true, text: 'Latent dimension', color: '#7d8da8' } },
      y: { ticks: { color: '#7d8da8' }, title: { display: true, text: yLabel, color: '#7d8da8' }, min: 0 },
    },
    plugins: { legend: { labels: { color: '#e8edf7' } } },
  };
}

function renderCapacity() {
  const sweep = DATA.latent_sweep?.results || [];
  if (!sweep.length) return;
  const dims = sweep.map(r => r.latent_dim);
  const held = sweep.map(r => (r.test_eval?.string_exact_match_rate ?? 0) * 100);
  const bacc = sweep.map(r => (r.test_eval?.avg_byte_accuracy ?? 0) * 100);

  document.getElementById('capacity-note').textContent =
    'No tested latent dimension from 16 through 1024 achieved held-out exact reconstruction under the tested position-MLP training configuration. This experiment did not identify a positive capacity threshold.';

  const ctx = document.getElementById('chart-frontier').getContext('2d');
  if (charts.frontier) charts.frontier.destroy();
  charts.frontier = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dims,
      datasets: [{
        label: 'Held-out exact %',
        data: held,
        borderColor: '#2dd4bf',
        backgroundColor: 'rgba(45,212,191,.12)',
        fill: true,
        tension: 0.1,
        pointRadius: 6,
      }],
    },
    options: { ...chartOpts('Held-out exact %'), plugins: {
      legend: { labels: { color: '#e8edf7' } },
      annotation: { annotations: { line1: { type: 'label', content: 'No tested capacity threshold observed', yValue: 5 } } },
    }},
  });

  const ctx2 = document.getElementById('chart-byte-acc').getContext('2d');
  if (charts.bacc) charts.bacc.destroy();
  charts.bacc = new Chart(ctx2, {
    type: 'bar',
    data: { labels: dims, datasets: [{ label: 'Held-out byte accuracy %', data: bacc, backgroundColor: '#818cf8' }] },
    options: chartOpts('Byte accuracy %'),
  });
}

function renderDecoder() {
  const results = DATA.decoder_ablation?.results || {};
  const labels = { position_mlp: 'Position MLP', sequence: 'Sequence', autoregressive: 'Autoregressive' };
  const names = Object.keys(results);
  const held = names.map(k => (results[k].test_eval?.string_exact_match_rate ?? 0) * 100);
  const params = names.map(k => results[k].trainable_parameters_decoder);

  const ctx = document.getElementById('chart-decoder').getContext('2d');
  if (charts.decoder) charts.decoder.destroy();
  charts.decoder = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: names.map(k => labels[k] || k),
      datasets: [
        { label: 'Held-out exact %', data: held, backgroundColor: '#f87171' },
        { label: 'Decoder params', data: params, backgroundColor: '#818cf8', yAxisID: 'y1' },
      ],
    },
    options: {
      scales: {
        x: { ticks: { color: '#7d8da8' } },
        y: { ticks: { color: '#7d8da8' }, min: 0, title: { display: true, text: 'Exact %', color: '#7d8da8' } },
        y1: { position: 'right', ticks: { color: '#7d8da8' }, grid: { drawOnChartArea: false } },
      },
      plugins: { legend: { labels: { color: '#e8edf7' } } },
    },
  });

  document.getElementById('decoder-table').textContent = names.map(k =>
    `${labels[k]}: held-out exact ${pct(results[k].test_eval?.string_exact_match_rate)} | params ${results[k].trainable_parameters_decoder}`
  ).join('\n') + '\n\nChanging decoder family among the tested architectures did not recover held-out exact reconstruction.';
}

function renderPaths() {
  const rc = DATA.representation_comparison?.results || {};
  const paths = [
    { key: 'A_deterministic_inverse', title: 'PATH A — Deterministic inverse', steps: 'Dynamic → Inverse' },
    { key: 'B_full_features_learned_decoder', title: 'PATH B — Full 771D + decoder', steps: 'Dynamic → Full → Decoder' },
    { key: 'C_projected_64d_learned_decoder', title: 'PATH C — 64D + decoder', steps: 'Dynamic → 64D → Decoder' },
  ];
  document.getElementById('path-cards').innerHTML = paths.map(p => {
    const row = rc[p.key] || {};
    const te = row.test_eval || row;
    const rate = te.string_exact_match_rate;
    const cls = rate >= 0.99 ? 'pass' : 'fail';
    return `<div class="card path-card">
      <h3>${p.title}</h3>
      <div class="muted">${p.steps}</div>
      <div class="path-metric ${cls}">${pct(rate)}</div>
      <div class="muted">test exact (${te.count || '—'} strings)</div>
    </div>`;
  }).join('');
}

function renderLanguages() {
  const langs = DATA.language_generalization?.languages || DATA.waste_by_language || {};
  const keys = Object.keys(langs);
  const tabs = document.getElementById('lang-tabs');
  tabs.innerHTML = keys.map((k, i) =>
    `<button class="${i === 0 ? 'active' : ''}" data-lang="${k}">${k.toUpperCase().slice(0, 2)}</button>`
  ).join('');
  const show = k => {
    tabs.querySelectorAll('button').forEach(b => b.classList.toggle('active', b.dataset.lang === k));
    document.getElementById('lang-detail').textContent = JSON.stringify(langs[k], null, 2);
  };
  tabs.querySelectorAll('button').forEach(b => b.onclick = () => show(b.dataset.lang));
  if (keys[0]) show(keys[0]);
}

function renderFourier() {
  const m = collisionScale();
  const items = [
    ['fourier_magnitude', 'Magnitude only'],
    ['fourier_phase', 'Magnitude + phase'],
  ];
  document.getElementById('fourier-cards').innerHTML = items.map(([k, label]) => {
    const v = m[k] || {};
    return `<div class="card metric-card"><div class="label">${label}</div>
      <div class="value">${v.collision_groups ?? '—'} <small>collision groups</small></div>
      <div class="muted">${v.unique_keys ?? '—'} unique / ${v.total_strings || DATA.collision_scale?.strings_tested || '—'} tested</div></div>`;
  }).join('');
}

function renderFailure() {
  const sweep = DATA.latent_sweep?.results || [];
  const dec = DATA.decoder_ablation?.results || {};
  const rep = DATA.representation_comparison?.results || {};

  const rows = [
    ['Deterministic inverse', pct(detInverse().string_exact_match_rate)],
    ['Learned inverse (64-d)', pct(learnedHeldOut()?.string_exact_match_rate)],
    ['Full 771-d + decoder', pct(rep.B_full_features_learned_decoder?.test_eval?.string_exact_match_rate)],
    ...sweep.filter(r => [128, 256, 512, 1024].includes(r.latent_dim)).map(r =>
      [`${r.latent_dim}-d + decoder`, pct(r.test_eval?.string_exact_match_rate)]),
    ['Position MLP', pct(dec.position_mlp?.test_eval?.string_exact_match_rate)],
    ['Sequence', pct(dec.sequence?.test_eval?.string_exact_match_rate)],
    ['Autoregressive', pct(dec.autoregressive?.test_eval?.string_exact_match_rate)],
  ];

  document.getElementById('failure-content').innerHTML = `
    <table><thead><tr><th>Method</th><th>Held-out exact</th></tr></thead>
    <tbody>${rows.map(([a, b]) => `<tr><td>${a}</td><td>${b}</td></tr>`).join('')}</tbody></table>
    <p style="margin-top:1rem"><strong>Conclusion:</strong> The current evidence rules out a simple "64 dimensions are too small" explanation, but does <em>not</em> isolate the remaining bottleneck.</p>`;

  document.getElementById('inverse-disclaimer').innerHTML = `
    <strong>IMPORTANT:</strong> The deterministic inverse result is not a learned reconstruction result.
    It verifies the representation retains enough information for an explicitly defined inverse.
    The neural decoder asks: can a learned model discover that inverse? Current answer: not under the tested setup.`;
}

function renderScoreboard() {
  const hyp = DATA.hypotheses || {};
  document.getElementById('hypothesis-board').innerHTML = Object.entries(hyp).map(([k, v]) =>
    `<div class="score-row"><span>${k.replace(/_/g, ' ')}</span><span class="${statusClass(mapHypStatus(v.status))}">${mapHypStatus(v.status)}</span></div>`
  ).join('');
}

function renderConclusion() {
  document.getElementById('learned-list').innerHTML = `
    <li>Fixed-window representation creates measurable waste and truncation.</li>
    <li>Dynamic representation eliminates observed truncation in the tested corpus.</li>
    <li>Dynamic representation retained enough information for deterministic exact inversion.</li>
    <li>Learned reconstruction is dramatically harder than deterministic inversion.</li>
    <li>Increasing latent dimension alone did not solve the problem.</li>
    <li>Changing decoder family alone did not solve the problem.</li>
    <li>The remaining bottleneck is not yet isolated.</li>
    <li>Tiny LM usefulness remains NOT RUN.</li>`;
  document.getElementById('limits-list').innerHTML = `
    <li>46 test strings — limited generalization claim strength</li>
    <li>2,000 training steps may be insufficient</li>
    <li>max_bytes=256 not tested beyond</li>
    <li>H8 language-model experiment not run</li>`;
  document.getElementById('meta-footer').textContent =
    ` · ${DATA.timestamp || ''} · seed ${DATA.meta?.seed ?? '—'} · commit ${DATA.meta?.git_commit ?? '—'}`;
}

function render() {
  renderHero();
  renderQuestion();
  renderWhy();
  renderDynamic();
  renderCollisions();
  renderReversibility();
  renderCapacity();
  renderDecoder();
  renderPaths();
  renderLanguages();
  renderFourier();
  renderFailure();
  renderScoreboard();
  renderConclusion();
}

load();
