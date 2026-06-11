/* ============================================
   MNIST DIGIT CLASSIFIER — Flask-connected JS
   ============================================ */

// ── Particle Background ──────────────────────
const particleCanvas = document.getElementById('particleCanvas');
const pCtx = particleCanvas.getContext('2d');
let particles = [];

function resizeParticleCanvas() {
  particleCanvas.width = window.innerWidth;
  particleCanvas.height = window.innerHeight;
}

class Particle {
  constructor() { this.reset(); }
  reset() {
    this.x = Math.random() * particleCanvas.width;
    this.y = Math.random() * particleCanvas.height;
    this.size = Math.random() * 1.5 + 0.3;
    this.speedX = (Math.random() - 0.5) * 0.4;
    this.speedY = (Math.random() - 0.5) * 0.4;
    this.opacity = Math.random() * 0.5 + 0.1;
    this.color = Math.random() > 0.6
      ? `rgba(99,179,237,${this.opacity})`
      : `rgba(183,148,244,${this.opacity})`;
  }
  update() {
    this.x += this.speedX;
    this.y += this.speedY;
    if (this.x < 0 || this.x > particleCanvas.width ||
        this.y < 0 || this.y > particleCanvas.height) {
      this.reset();
    }
  }
  draw() {
    pCtx.beginPath();
    pCtx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    pCtx.fillStyle = this.color;
    pCtx.fill();
  }
}

function initParticles() {
  particles = [];
  const count = Math.min(120, Math.floor(particleCanvas.width * particleCanvas.height / 12000));
  for (let i = 0; i < count; i++) particles.push(new Particle());
}

function drawConnections() {
  const maxDist = 120;
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < maxDist) {
        const alpha = (1 - dist / maxDist) * 0.12;
        pCtx.beginPath();
        pCtx.strokeStyle = `rgba(99,179,237,${alpha})`;
        pCtx.lineWidth = 0.5;
        pCtx.moveTo(particles[i].x, particles[i].y);
        pCtx.lineTo(particles[j].x, particles[j].y);
        pCtx.stroke();
      }
    }
  }
}

function animateParticles() {
  pCtx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);
  drawConnections();
  particles.forEach(p => { p.update(); p.draw(); });
  requestAnimationFrame(animateParticles);
}

resizeParticleCanvas();
initParticles();
animateParticles();
window.addEventListener('resize', () => { resizeParticleCanvas(); initParticles(); });

// ── Navbar Scroll Effect ─────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 30);
});

// ── Hamburger Menu ────────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinksEl = document.getElementById('navLinks');
hamburger.addEventListener('click', () => {
  navLinksEl.classList.toggle('open');
});
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => navLinksEl.classList.remove('open'));
});

// ── Counter Animation ─────────────────────────
function animateCounter(el, target, duration = 1800) {
  let start = null;
  const isLarge = target > 999;
  function step(ts) {
    if (!start) start = ts;
    const prog = Math.min((ts - start) / duration, 1);
    const eased = 1 - Math.pow(1 - prog, 3);
    const cur = Math.round(eased * target);
    el.textContent = isLarge ? cur.toLocaleString() : cur;
    if (prog < 1) requestAnimationFrame(step);
    else el.textContent = isLarge ? target.toLocaleString() : target;
  }
  requestAnimationFrame(step);
}

const statObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const numEl = e.target.querySelector('.stat-number');
      animateCounter(numEl, parseInt(numEl.dataset.target));
      statObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.stat-card').forEach(c => statObserver.observe(c));

// ── Hero Digit Grid ───────────────────────────
const DIGIT_COLORS = [
  'rgba(99,179,237,0.7)', 'rgba(183,148,244,0.7)', 'rgba(104,211,145,0.7)',
  'rgba(246,211,85,0.7)', 'rgba(252,129,129,0.7)', 'rgba(99,179,237,0.55)',
  'rgba(183,148,244,0.55)', 'rgba(104,211,145,0.55)', 'rgba(246,211,85,0.55)',
  'rgba(252,129,129,0.55)',
];

const digitGrid = document.getElementById('digitGrid');
const digits = Array.from({ length: 24 }, () => Math.floor(Math.random() * 10));

function buildDigitGrid() {
  digitGrid.innerHTML = '';
  digits.forEach((d, i) => {
    const cell = document.createElement('div');
    cell.className = 'digit-cell';
    cell.textContent = d;
    cell.style.background = DIGIT_COLORS[d];
    cell.style.animationDelay = `${i * 0.04}s`;
    digitGrid.appendChild(cell);
  });
}
buildDigitGrid();

setInterval(() => {
  const cells = digitGrid.querySelectorAll('.digit-cell');
  const idx = Math.floor(Math.random() * cells.length);
  const newD = Math.floor(Math.random() * 10);
  digits[idx] = newD;
  cells[idx].style.transition = 'background 0.4s ease, transform 0.3s ease';
  cells[idx].style.transform = 'scale(1.15)';
  cells[idx].textContent = newD;
  cells[idx].style.background = DIGIT_COLORS[newD];
  setTimeout(() => { cells[idx].style.transform = 'scale(1)'; }, 300);
}, 800);

// ── Mini Pixel Grid ───────────────────────────
const miniGrid = document.getElementById('miniGrid');
if (miniGrid) {
  [0,0,0,1,0, 0,1,1,1,0, 0,0,1,0,0, 0,0,1,0,0, 0,1,1,1,0].forEach(v => {
    const cell = document.createElement('div');
    cell.className = 'mini-pixel-grid-cell';
    cell.style.background = v ? 'rgba(99,179,237,0.8)' : 'rgba(255,255,255,0.04)';
    miniGrid.appendChild(cell);
  });
}

// ── Drawing Canvas ────────────────────────────
const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');
let isDrawing = false;
let hasDrawn = false;
const canvasHint = document.getElementById('canvasHint');
const brushSlider = document.getElementById('brushSize');
const brushLabel = document.getElementById('brushSizeLabel');

ctx.fillStyle = '#0d0f16';
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.lineJoin = 'round';
ctx.lineCap = 'round';

brushSlider.addEventListener('input', () => {
  brushLabel.textContent = `${brushSlider.value}px`;
});

function getPos(e) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  if (e.touches) {
    return {
      x: (e.touches[0].clientX - rect.left) * scaleX,
      y: (e.touches[0].clientY - rect.top) * scaleY
    };
  }
  return {
    x: (e.clientX - rect.left) * scaleX,
    y: (e.clientY - rect.top) * scaleY
  };
}

function startDraw(e) {
  e.preventDefault();
  isDrawing = true;
  if (!hasDrawn) {
    hasDrawn = true;
    canvasHint.classList.add('hidden');
  }
  const pos = getPos(e);
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, parseInt(brushSlider.value) / 2, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff';
  ctx.fill();
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);
}

function draw(e) {
  if (!isDrawing) return;
  e.preventDefault();
  const pos = getPos(e);
  ctx.lineWidth = parseInt(brushSlider.value);
  ctx.strokeStyle = '#ffffff';
  ctx.shadowBlur = 6;
  ctx.shadowColor = 'rgba(99,179,237,0.5)';
  ctx.lineTo(pos.x, pos.y);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);
}

function stopDraw() {
  isDrawing = false;
  ctx.shadowBlur = 0;
  ctx.beginPath();
}

canvas.addEventListener('mousedown', startDraw);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDraw);
canvas.addEventListener('mouseleave', stopDraw);
canvas.addEventListener('touchstart', startDraw, { passive: false });
canvas.addEventListener('touchmove', draw, { passive: false });
canvas.addEventListener('touchend', stopDraw);

document.getElementById('clearBtn').addEventListener('click', () => {
  ctx.fillStyle = '#0d0f16';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  hasDrawn = false;
  canvasHint.classList.remove('hidden');
  resetPrediction();
});

// ── Confidence Bars ───────────────────────────
const barsContainer = document.getElementById('barsContainer');

function buildBars(probs) {
  barsContainer.innerHTML = '';
  const topIdx = probs.indexOf(Math.max(...probs));
  probs.forEach((p, i) => {
    const row = document.createElement('div');
    row.className = 'conf-bar-row';
    row.innerHTML = `
      <span class="conf-bar-digit">${i}</span>
      <div class="conf-bar-track">
        <div class="conf-bar-fill ${i === topIdx ? 'top-bar' : ''}" id="bar-${i}"></div>
      </div>
      <span class="conf-bar-pct">${(p * 100).toFixed(1)}%</span>
    `;
    barsContainer.appendChild(row);
  });
  requestAnimationFrame(() => {
    probs.forEach((p, i) => {
      const fill = document.getElementById(`bar-${i}`);
      if (fill) fill.style.width = `${p * 100}%`;
    });
  });
}

function resetPrediction() {
  document.getElementById('predictedDigitDisplay').innerHTML = '<div class="digit-placeholder">?</div>';
  document.getElementById('confidenceBadge').textContent = '—';
  barsContainer.innerHTML = '';
  setNote('default', 'Draw a digit and click <strong>Predict</strong> to get a real CNN prediction.');
}

function setNote(type, msg) {
  const note = document.getElementById('predictionNote');
  const text = document.getElementById('noteText');
  if (!note || !text) return;
  note.className = 'prediction-note' + (type === 'error' ? ' error-note' : '');
  text.innerHTML = msg;
}

// Initialize empty bars placeholder
buildBars(Array(10).fill(0));

// ── Real Flask /predict API call ──────────────
const predictBtn = document.getElementById('predictBtn');

async function callPredictAPI() {
  if (!hasDrawn) {
    canvasHint.style.color = 'rgba(252,129,129,0.45)';
    setTimeout(() => { canvasHint.style.color = 'rgba(255,255,255,0.12)'; }, 1200);
    setNote('error', '⚠️ Please draw a digit first!');
    return;
  }

  // Get base64 image from canvas
  const imageDataUrl = canvas.toDataURL('image/png');

  // Show loading state
  predictBtn.classList.add('loading');
  predictBtn.textContent = 'Predicting';
  setNote('default', '⏳ Sending to Flask CNN model...');

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: imageDataUrl }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }

    // ── Display prediction ──────────────────────
    const display = document.getElementById('predictedDigitDisplay');
    display.innerHTML = `<div class="digit-result">${data.prediction}</div>`;

    const pct = (data.confidence * 100).toFixed(1);
    document.getElementById('confidenceBadge').textContent = `${pct}% confident`;

    buildBars(data.all_probs);

    // Flash the panel
    const panel = document.querySelector('.prediction-panel');
    panel.classList.remove('flash');
    void panel.offsetWidth; // reflow
    panel.classList.add('flash');

    setNote('default', `✅ Real CNN prediction: <strong>${data.prediction}</strong> with <strong>${pct}%</strong> confidence.`);

  } catch (err) {
    console.error('Prediction error:', err);
    setNote('error', `❌ ${err.message}. Is the Flask server running and model trained?`);
    document.getElementById('predictedDigitDisplay').innerHTML = '<div class="digit-placeholder">!</div>';
  } finally {
    predictBtn.classList.remove('loading');
    predictBtn.textContent = 'Predict →';
  }
}

if (predictBtn) {
  predictBtn.addEventListener('click', callPredictAPI);
}

// ── Trigger Training via /train endpoint ─────
async function triggerTraining() {
  const trainBtn = document.getElementById('trainBtn');
  if (trainBtn) {
    trainBtn.disabled = true;
    trainBtn.textContent = 'Training…';
  }

  // Show overlay
  const overlay = document.createElement('div');
  overlay.className = 'training-overlay';
  overlay.innerHTML = `
    <div class="training-spinner"></div>
    <div class="training-message">Training CNN Model…</div>
    <div class="training-sub">This takes ~2–5 minutes on CPU. Please wait.</div>
  `;
  document.body.appendChild(overlay);

  try {
    const resp = await fetch('/train', { method: 'POST' });
    const data = await resp.json();
    if (resp.ok) {
      overlay.innerHTML = `
        <div style="font-size:3rem">✅</div>
        <div class="training-message">Training complete!</div>
        <div class="training-sub">Reloading page…</div>
      `;
      setTimeout(() => location.reload(), 1500);
    } else {
      throw new Error(data.output || 'Training failed');
    }
  } catch (err) {
    overlay.innerHTML = `
      <div style="font-size:3rem">❌</div>
      <div class="training-message">Training failed</div>
      <div class="training-sub" style="max-width:400px;text-align:center">${err.message}</div>
      <button onclick="document.querySelector('.training-overlay').remove()" style="margin-top:16px;padding:8px 20px;border-radius:8px;border:none;background:rgba(255,255,255,0.1);color:white;cursor:pointer">Close</button>
    `;
    if (trainBtn) {
      trainBtn.disabled = false;
      trainBtn.textContent = 'Train Now';
    }
  }
}

// Make triggerTraining global (called from inline onclick)
window.triggerTraining = triggerTraining;

// ── Accuracy Chart ───────────────────────────
const chartCanvas = document.getElementById('accuracyChart');
const chartCtx = chartCanvas.getContext('2d');

const epochs = [1,2,3,4,5,6,7,8,9,10];
const trainAcc = [0.891,0.942,0.959,0.967,0.972,0.975,0.978,0.980,0.981,0.982];
const valAcc   = [0.952,0.962,0.968,0.972,0.975,0.977,0.979,0.980,0.981,0.982];

function drawChart() {
  const W = chartCanvas.offsetWidth || 500;
  chartCanvas.width = W;
  const H = chartCanvas.height;
  const padL = 52, padR = 20, padT = 20, padB = 40;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;

  chartCtx.clearRect(0, 0, W, H);

  // Grid
  chartCtx.strokeStyle = 'rgba(255,255,255,0.04)';
  chartCtx.lineWidth = 1;
  for (let i = 0; i <= 5; i++) {
    const y = padT + (chartH / 5) * i;
    chartCtx.beginPath();
    chartCtx.moveTo(padL, y);
    chartCtx.lineTo(padL + chartW, y);
    chartCtx.stroke();
    chartCtx.fillStyle = 'rgba(160,174,192,0.6)';
    chartCtx.font = '10px Inter';
    chartCtx.textAlign = 'right';
    chartCtx.fillText((100 - i * 4) + '%', padL - 8, y + 4);
  }

  // X axis labels
  chartCtx.fillStyle = 'rgba(160,174,192,0.6)';
  chartCtx.font = '10px Inter';
  chartCtx.textAlign = 'center';
  epochs.forEach((e, i) => {
    const x = padL + (chartW / (epochs.length - 1)) * i;
    chartCtx.fillText(e, x, H - padB + 16);
  });
  chartCtx.fillText('Epoch', padL + chartW / 2, H - 4);

  function plotLine(data, color) {
    const points = data.map((v, i) => ({
      x: padL + (chartW / (epochs.length - 1)) * i,
      y: padT + chartH - ((v - 0.88) / (1 - 0.88)) * chartH
    }));

    // Fill
    const grad = chartCtx.createLinearGradient(0, padT, 0, padT + chartH);
    grad.addColorStop(0, color.replace('1)', '0.15)'));
    grad.addColorStop(1, color.replace('1)', '0.01)'));
    chartCtx.beginPath();
    chartCtx.moveTo(points[0].x, padT + chartH);
    points.forEach(p => chartCtx.lineTo(p.x, p.y));
    chartCtx.lineTo(points[points.length - 1].x, padT + chartH);
    chartCtx.closePath();
    chartCtx.fillStyle = grad;
    chartCtx.fill();

    // Line
    chartCtx.beginPath();
    chartCtx.shadowColor = color.replace('1)', '0.6)');
    chartCtx.shadowBlur = 8;
    chartCtx.strokeStyle = color;
    chartCtx.lineWidth = 2.5;
    chartCtx.lineJoin = 'round';
    chartCtx.moveTo(points[0].x, points[0].y);
    points.forEach(p => chartCtx.lineTo(p.x, p.y));
    chartCtx.stroke();
    chartCtx.shadowBlur = 0;

    // Dots
    points.forEach(p => {
      chartCtx.beginPath();
      chartCtx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
      chartCtx.fillStyle = color;
      chartCtx.fill();
    });
  }

  plotLine(trainAcc, 'rgba(99,179,237,1)');
  plotLine(valAcc, 'rgba(183,148,244,1)');

  // Legend
  const legendY = padT + 10;
  chartCtx.fillStyle = 'rgba(99,179,237,1)';
  chartCtx.fillRect(padL, legendY, 20, 3);
  chartCtx.fillStyle = 'rgba(160,174,192,0.8)';
  chartCtx.font = '11px Inter';
  chartCtx.textAlign = 'left';
  chartCtx.fillText('Train Acc', padL + 26, legendY + 6);
  chartCtx.fillStyle = 'rgba(183,148,244,1)';
  chartCtx.fillRect(padL + 100, legendY, 20, 3);
  chartCtx.fillStyle = 'rgba(160,174,192,0.8)';
  chartCtx.fillText('Val Acc', padL + 126, legendY + 6);
}

const chartObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { drawChart(); chartObserver.unobserve(e.target); }
  });
}, { threshold: 0.3 });
chartObserver.observe(chartCanvas);
window.addEventListener('resize', drawChart);

// ── Tab Switching ─────────────────────────────
function switchTab(tabId, btn) {
  document.querySelectorAll('.code-tab-content').forEach(t => t.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`tab-${tabId}`).classList.remove('hidden');
  btn.classList.add('active');
}
window.switchTab = switchTab;

// ── Copy Code ─────────────────────────────────
function copyCode(id, btn) {
  const text = document.getElementById(id).innerText || document.getElementById(id).textContent;
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
  });
}
window.copyCode = copyCode;

// ── Intersection Observer — fade in ──────────
const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
      fadeObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll(
  '.overview-card, .tech-card, .arch-layer, .metric-card, .pipeline-step, .api-step'
).forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  fadeObserver.observe(el);
});

// ── Active nav on scroll ──────────────────────
const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-link');

new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const id = e.target.id;
      navItems.forEach(a => { a.style.color = ''; a.style.background = ''; });
      const active = document.querySelector(`.nav-link[href="#${id}"]`);
      if (active) {
        active.style.color = 'var(--primary)';
        active.style.background = 'rgba(99,179,237,0.08)';
      }
    }
  });
}, { threshold: 0.4 }).observe && sections.forEach(s =>
  new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        navItems.forEach(a => { a.style.color = ''; a.style.background = ''; });
        const active = document.querySelector(`.nav-link[href="#${e.target.id}"]`);
        if (active) { active.style.color = 'var(--primary)'; active.style.background = 'rgba(99,179,237,0.08)'; }
      }
    });
  }, { threshold: 0.4 }).observe(s)
);

// ── Image Upload ──────────────────────────────
const imageUpload = document.getElementById('imageUpload');
if (imageUpload) {
  imageUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        // Clear canvas
        ctx.fillStyle = '#0d0f16';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        hasDrawn = true;
        
        const canvasHint = document.getElementById('canvasHint');
        if (canvasHint) canvasHint.classList.add('hidden');

        // Scale down if image is larger than canvas, otherwise fit
        const padding = 20;
        const availWidth = canvas.width - padding * 2;
        const availHeight = canvas.height - padding * 2;
        
        const scale = Math.min(availWidth / img.width, availHeight / img.height);
        const w = img.width * scale;
        const h = img.height * scale;
        
        const x = (canvas.width - w) / 2;
        const y = (canvas.height - h) / 2;
        
        ctx.drawImage(img, x, y, w, h);
        
        // Auto predict if ready
        const predictBtn = document.getElementById('predictBtn');
        if (predictBtn && !predictBtn.disabled) {
          callPredictAPI();
        }
        
        // Reset input
        imageUpload.value = '';
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  });
}
