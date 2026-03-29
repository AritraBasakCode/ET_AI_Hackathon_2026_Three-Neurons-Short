// ═══════════════════════════════════════════════
//  PatternIQ — App Logic
// ═══════════════════════════════════════════════

const $ = id => document.getElementById(id);
let priceChart = null, volChart = null;
let candleSeries, ema20Series, sma50Series, volSeries;

// ── Clock ──────────────────────────────────────
function clock() {
  const now = new Date();
  $('statusTime').textContent = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(clock, 1000); clock();

// ── Seg buttons ───────────────────────────────
function initSeg(id) {
  $(id).querySelectorAll('.chip').forEach(b => {
    b.addEventListener('click', () => {
      $(id).querySelectorAll('.chip').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
    });
  });
}
const active = id => $(id).querySelector('.chip.active')?.dataset.val ?? '';
initSeg('periodGroup');
initSeg('intervalGroup');

const barsSlider = $('barsSlider');
barsSlider.addEventListener('input', () => {
  $('barsVal').textContent = barsSlider.value;
});

// ── Status ────────────────────────────────────
function setStatus(cls, lbl) {
  $('statusDot').className = 'dot ' + cls;
  $('statusLabel').textContent = lbl;
}

// ── Charts ────────────────────────────────────
function initCharts() {
  if (priceChart) { priceChart.remove(); volChart.remove(); }
  const pe = $('priceChart'), ve = $('volChart');

  const base = {
    layout:    { background: { color: 'transparent' }, textColor: '#4a6280' },
    grid:      { vertLines: { color: '#1c2a40' }, horzLines: { color: '#1c2a40' } },
    crosshair: { mode: 1, vertLine: { color: '#F59E0B44' }, horzLine: { color: '#F59E0B44' } },
    rightPriceScale: { borderColor: '#1c2a40' },
    timeScale:       { borderColor: '#1c2a40', timeVisible: true, secondsVisible: false },
  };

  priceChart = LightweightCharts.createChart(pe, { ...base, height: 350, width: pe.clientWidth });
  volChart   = LightweightCharts.createChart(ve, {
    ...base, height: 72, width: ve.clientWidth,
    timeScale: { borderColor: '#1c2a40', visible: false },
    rightPriceScale: { borderColor: '#1c2a40', scaleMargins: { top: 0.1, bottom: 0 } },
  });

  candleSeries = priceChart.addCandlestickSeries({
    upColor: '#10B981', downColor: '#EF4444',
    borderUpColor: '#10B981', borderDownColor: '#EF4444',
    wickUpColor:   '#10B981', wickDownColor:   '#EF4444',
  });
  ema20Series = priceChart.addLineSeries({ color: '#06B6D4', lineWidth: 1.5, title: 'EMA20' });
  sma50Series = priceChart.addLineSeries({ color: '#F59E0B', lineWidth: 1.5, lineStyle: 2, title: 'SMA50' });
  volSeries   = volChart.addHistogramSeries({ color: '#1a2540', priceFormat: { type: 'volume' } });

  priceChart.timeScale().subscribeVisibleLogicalRangeChange(r => { if (r) volChart.timeScale().setVisibleLogicalRange(r); });
  volChart.timeScale().subscribeVisibleLogicalRangeChange(r => { if (r) priceChart.timeScale().setVisibleLogicalRange(r); });

  new ResizeObserver(() => {
    priceChart.applyOptions({ width: pe.clientWidth });
    volChart.applyOptions({ width: ve.clientWidth });
  }).observe(pe);
}

function loadChart(d, symbol) {
  $('chartSym').textContent = symbol;

  const candles = d.dates.map((t,i) => ({ time:t, open:d.open[i], high:d.high[i], low:d.low[i], close:d.close[i] }));
  const ema20   = d.dates.map((t,i) => d.ema20[i] != null ? { time:t, value:d.ema20[i] } : null).filter(Boolean);
  const sma50   = d.dates.map((t,i) => d.sma50[i] != null ? { time:t, value:d.sma50[i] } : null).filter(Boolean);
  const vols    = d.dates.map((t,i) => ({ time:t, value:d.volume[i], color: d.close[i] >= d.open[i] ? 'rgba(16,185,129,.45)' : 'rgba(239,68,68,.45)' }));

  candleSeries.setData(candles);
  ema20Series.setData(ema20);
  sma50Series.setData(sma50);
  volSeries.setData(vols);
  priceChart.timeScale().fitContent();
  volChart.timeScale().fitContent();

  // Last close vs first close
  const pct = d.close.length > 1 ? ((d.close.at(-1) - d.close[0]) / d.close[0] * 100).toFixed(2) : null;
  const dir = pct > 0 ? '▲' : '▼';
  const clr = pct > 0 ? 'var(--bull)' : 'var(--bear)';
  $('chartMeta').innerHTML = pct != null
    ? `<span style="color:${clr}">${dir} ${Math.abs(pct)}% (period)</span><span>${d.dates.length} bars</span>`
    : '';

  $('chartLegend').innerHTML = `
    <div class="leg"><div class="leg-line" style="background:#06B6D4"></div>EMA20</div>
    <div class="leg"><div class="leg-line" style="background:#F59E0B"></div>SMA50</div>
  `;
}

// ── Formatters ────────────────────────────────
const fmt  = (v, d=2) => v == null ? '—' : (+v).toLocaleString('en-IN', { minimumFractionDigits:d, maximumFractionDigits:d });
const fmtV = v => {
  if (v == null) return '—';
  if (v >= 1e7) return (+v/1e7).toFixed(2)+' Cr';
  if (v >= 1e5) return (+v/1e5).toFixed(2)+' L';
  return (+v).toLocaleString('en-IN');
};

// ── Snapshot ──────────────────────────────────
function renderSnapshot(s) {
  const rsi = s.rsi14;
  const rsiCls = rsi == null ? '' : rsi < 30 ? 'bear' : rsi > 70 ? 'bull' : '';
  const priceCls = s.close && s.sma50 ? (s.close > s.sma50 ? 'bull' : 'bear') : '';

  $('statsGrid').innerHTML = [
    { k:'CLOSE',   v:'₹'+fmt(s.close),   c: priceCls },
    { k:'RSI 14',  v: fmt(s.rsi14,1),    c: rsiCls   },
    { k:'EMA 20',  v:'₹'+fmt(s.ema20),   c:''        },
    { k:'SMA 50',  v:'₹'+fmt(s.sma50),   c:''        },
    { k:'VOLUME',  v: fmtV(s.volume),    c:''        },
    { k:'MACD',    v: fmt(s.macd,3),     c: s.macd > 0 ? 'bull' : s.macd < 0 ? 'bear' : '' },
    { k:'ATR 14',  v: fmt(s.atr14),      c:''        },
  ].map(({k,v,c}) => `
    <div class="stat-card ${c}">
      <div class="stat-k">${k}</div>
      <div class="stat-v ${c}">${v}</div>
    </div>`).join('');
  $('statsBlock').style.display = 'block';

  // Gauges
  const rsiPct = rsi != null ? rsi : 50;
  const rsiColor = rsi < 30 ? 'var(--bear)' : rsi > 70 ? 'var(--amber)' : 'var(--cyan)';
  let macdPct = 50;
  if (s.macd != null && s.atr14) { macdPct = Math.min(100, Math.max(0, 50 + (s.macd / s.atr14) * 25)); }

  $('gaugeGrid').innerHTML = `
    <div class="gauge-item">
      <div class="gauge-hdr"><span class="gauge-name">RSI (14)</span><span class="gauge-val">${fmt(rsi,1)}</span></div>
      <div class="gauge-track"><div class="gauge-fill" style="width:${rsiPct}%;background:${rsiColor}"></div></div>
    </div>
    <div class="gauge-item">
      <div class="gauge-hdr"><span class="gauge-name">MACD MOMENTUM</span><span class="gauge-val">${fmt(s.macd,2)}</span></div>
      <div class="gauge-track"><div class="gauge-fill" style="width:${macdPct.toFixed(1)}%;background:${s.macd>0?'var(--bull)':'var(--bear)'}"></div></div>
    </div>
  `;
  $('gaugeBlock').style.display = 'block';
}

// ── AI Insight renderer ───────────────────────
function renderAI(ai) {
  if (!ai) return '';
  if (ai.error) return `<div class="ai-block"><div class="ai-error">${ai.error}</div></div>`;

  const rows = [
    { label: 'WHAT HAPPENED',      key: 'what_happened',    cls: '' },
    { label: 'WHY IT MATTERS',     key: 'why_it_matters',   cls: '' },
    { label: 'RISK CAUTION',       key: 'risk_caution',     cls: 'risk' },
    { label: 'BACKTEST CONTEXT',   key: 'backtest_context', cls: '' },
  ].filter(r => ai[r.key])
   .map(r => `<div class="ai-row">
      <div class="ai-row-label">${r.label}</div>
      <div class="ai-row-text ${r.cls}">${ai[r.key]}</div>
    </div>`).join('');

  const rawRow = ai.raw ? `<div class="ai-row"><div class="ai-row-text">${ai.raw}</div></div>` : '';

  return `
    <div class="ai-block">
      <div class="ai-block-hdr">
        <div class="ai-chip">
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <circle cx="5" cy="5" r="4" stroke="#06B6D4" stroke-width="1"/>
            <path d="M3 5h4M5 3v4" stroke="#06B6D4" stroke-width="1" stroke-linecap="round"/>
          </svg>
          GEMINI AI ANALYSIS
        </div>
      </div>
      ${ai.summary ? `<div class="ai-summary">${ai.summary}</div>` : ''}
      <div class="ai-rows">${rows}${rawRow}</div>
    </div>`;
}

// ── Latest signals ─────────────────────────────
function renderLatest(signals, snap) {
  const el = $('latestSignals');
  const badge = $('latestCount');
  const sigBadge = $('signalBadge');

  if (!signals.length) {
    badge.style.display = 'none';
    sigBadge.style.display = 'none';

    const rsi = snap?.rsi14;
    const close = snap?.close;
    const ema20 = snap?.ema20;
    const sma50 = snap?.sma50;
    const macd  = snap?.macd;

    const trendDir = close && ema20 ? (close > ema20 ? 'bull' : 'bear') : null;
    const trendLbl = trendDir === 'bull' ? 'Above EMA20 — Bullish bias' : trendDir === 'bear' ? 'Below EMA20 — Bearish bias' : null;
    const rsiLbl   = rsi != null ? (rsi < 30 ? 'Oversold (watch for reversal)' : rsi > 70 ? 'Overbought' : 'Neutral zone') : null;
    const macdLbl  = macd != null ? (macd > 0 ? 'MACD Positive' : 'MACD Negative') : null;
    const vs50     = close && sma50 ? (close > sma50 ? 'Above SMA50' : 'Below SMA50') : null;

    const pills = [
      trendLbl ? `<span class="pill ${trendDir}">${trendLbl}</span>` : '',
      rsiLbl   ? `<span class="pill ${rsi<30?'bull':rsi>70?'amber':''}">${rsiLbl}: ${fmt(rsi,1)}</span>` : '',
      macdLbl  ? `<span class="pill ${macd>0?'bull':'bear'}">${macdLbl}</span>` : '',
      vs50     ? `<span class="pill">${vs50}</span>` : '',
    ].filter(Boolean).join('');

    el.innerHTML = `
      <div class="no-sig-card">
        <div class="no-sig-head">
          <div class="no-sig-dot"></div>
          <div class="no-sig-title">NO PATTERN TRIGGERED ON LATEST BAR</div>
        </div>
        <div class="no-sig-body">
          None of the tracked patterns (20D Breakout, RSI Reversal, Support/Resistance Touch) fired on the most recent candle.
          <br><br>
          <b>Current market state:</b>
          <div class="indicator-pills">${pills}</div>
          <br>
          Extend the scan period to <b>2Y / 5Y</b> or increase the recent bars slider to find historical signal occurrences.
        </div>
      </div>`;
    return;
  }

  badge.textContent = signals.length + ' SIGNAL' + (signals.length > 1 ? 'S' : '');
  badge.style.display = 'inline';
  sigBadge.textContent = '⚡ ' + signals.length + ' PATTERN' + (signals.length > 1 ? 'S' : '') + ' DETECTED';
  sigBadge.className = 'chart-badge triggered';
  sigBadge.style.display = 'inline';

  el.innerHTML = signals.map(sig => {
    const metaCells = Object.entries(sig.meta || {}).map(([k,v]) =>
      `<div class="sig-meta-cell">
        <span class="meta-k">${k.replace(/_/g,' ')}</span>
        <span class="meta-v">${typeof v === 'number' ? fmt(v) : (v ?? '—')}</span>
      </div>`
    ).join('');

    const bt = sig.backtest || {};
    const btHtml = bt.total_signals != null ? `
      <div class="bt-block">
        <div class="bt-cell"><span class="bt-k">SIGNALS</span><span class="bt-v">${bt.total_signals}</span></div>
        <div class="bt-cell"><span class="bt-k">WINS</span><span class="bt-v good">${bt.wins}</span></div>
        <div class="bt-cell"><span class="bt-k">SUCCESS</span><span class="bt-v ${bt.success_rate_pct >= 50 ? 'good' : 'bad'}">${bt.success_rate_pct ?? '—'}%</span></div>
        <div class="bt-cell"><span class="bt-k">HOLD</span><span class="bt-v">${bt.params?.hold_days}d</span></div>
      </div>` : '';

    return `
      <div class="sig-card">
        <div class="sig-card-head">
          <span class="sig-pattern-name">${sig.pattern.replace(/_/g,' ')}</span>
          <span class="sig-time-badge">${sig.signal_time ?? ''}</span>
        </div>
        <div class="sig-meta-grid">${metaCells}</div>
        ${btHtml}
        ${renderAI(sig.ai_insight)}
      </div>`;
  }).join('');
}

// ── Recent signals ─────────────────────────────
function renderRecent(signals) {
  const el = $('recentSignals');
  const badge = $('recentCount');
  if (!signals.length) {
    badge.style.display = 'none';
    el.innerHTML = '<div class="await-state"><div>No signals found in recent bars</div></div>';
    return;
  }
  badge.textContent = signals.length + ' FOUND';
  badge.style.display = 'inline';
  el.innerHTML = signals.map(s =>
    `<div class="rec-row">
      <span class="rec-date">${s.date}</span>
      <span class="rec-tag">${s.pattern.replace(/_/g,' ')}</span>
    </div>`
  ).join('');
}

// ── Debug ──────────────────────────────────────
function renderDebug(dbg) {
  $('debugBody').innerHTML = `Resolved: <b>${dbg.resolved_symbol}</b><br>Rows: ${dbg.rows}<br>Columns: ${dbg.columns.join(', ')}`;
  $('debugBlock').style.display = 'block';
}
$('debugToggle').addEventListener('click', () => {
  const b = $('debugBody');
  b.classList.toggle('closed');
  $('dbChev').textContent = b.classList.contains('closed') ? '▶' : '▼';
});

// ── Error toast ────────────────────────────────
let toastTimer;
function showError(msg) {
  const t = $('errorToast');
  t.textContent = '⚠ ' + msg;
  t.style.display = 'block';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.style.display = 'none'; }, 8000);
}

// ── Run ────────────────────────────────────────
async function run() {
  $('errorToast').style.display = 'none';
  $('signalBadge').style.display = 'none';
  $('latestSignals').innerHTML = `<div class="await-state"><div class="await-icon">◈</div><div>SCANNING PATTERNS…</div></div>`;
  $('recentSignals').innerHTML  = `<div class="await-state"><div class="await-icon">◈</div><div>BUILDING SIGNAL LOG…</div></div>`;
  setStatus('loading', 'SCANNING');
  $('runBtn').disabled = true;
  $('runLabel').textContent = 'SCANNING…';

  const payload = {
    symbol:      $('symbolInput').value.trim().toUpperCase() || 'TCS.NS',
    period:      active('periodGroup'),
    interval:    active('intervalGroup'),
    recent_bars: parseInt(barsSlider.value),
  };

  try {
    initCharts();
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const e = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(e.detail || res.statusText);
    }
    const data = await res.json();

    loadChart(data.chart_data, data.symbol);
    renderSnapshot(data.snapshot);
    renderLatest(data.latest_signals, data.snapshot);
    renderRecent(data.recent_signals);
    renderDebug(data.debug);
    setStatus('active', 'LIVE');
  } catch(e) {
    showError(e.message);
    $('latestSignals').innerHTML = `<div class="await-state"><div style="color:var(--bear)">Analysis failed</div></div>`;
    $('recentSignals').innerHTML  = `<div class="await-state"><div style="color:var(--bear)">Analysis failed</div></div>`;
    setStatus('error', 'ERROR');
  } finally {
    $('runBtn').disabled = false;
    $('runLabel').textContent = 'SCAN PATTERNS';
  }
}

$('runBtn').addEventListener('click', run);
$('symbolInput').addEventListener('keydown', e => { if (e.key === 'Enter') run(); });
window.addEventListener('load', initCharts);