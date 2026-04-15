from flask import Flask, render_template_string

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>sen(x) · a</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Bebas+Neue&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0a0a0f;
      --panel: #12121a;
      --accent: #00ffb3;
      --accent2: #ff3d6e;
      --wave: #00ffb3;
      --grid: rgba(255,255,255,0.04);
      --text: #e0e0e0;
      --muted: #444;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Space Mono', monospace;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2rem;
      overflow: hidden;
    }

    /* grain overlay */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.07'/%3E%3C/svg%3E");
      pointer-events: none;
      z-index: 999;
      opacity: 0.4;
    }

    header {
      display: flex;
      align-items: baseline;
      gap: 1rem;
    }

    h1 {
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(2rem, 5vw, 4rem);
      letter-spacing: 0.1em;
      color: var(--accent);
      text-shadow: 0 0 30px rgba(0,255,179,0.4);
    }

    .formula {
      font-size: clamp(0.8rem, 1.5vw, 1rem);
      color: var(--muted);
      font-style: italic;
    }

    .canvas-wrapper {
      position: relative;
      width: min(90vw, 860px);
      height: clamp(240px, 40vh, 400px);
      border: 1px solid rgba(0,255,179,0.15);
      border-radius: 4px;
      background: var(--panel);
      box-shadow: 0 0 60px rgba(0,255,179,0.06), inset 0 0 40px rgba(0,0,0,0.4);
      overflow: hidden;
    }

    canvas {
      display: block;
      width: 100%;
      height: 100%;
    }

    /* axis labels */
    .axis-x { position: absolute; right: 10px; bottom: 6px; font-size: 0.65rem; color: var(--muted); }
    .axis-y { position: absolute; left: 8px; top: 6px; font-size: 0.65rem; color: var(--muted); }

    .controls {
      display: flex;
      align-items: center;
      gap: 2.5rem;
      flex-wrap: wrap;
      justify-content: center;
    }

    .knob-group {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.6rem;
    }

    .knob-label {
      font-size: 0.65rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--muted);
    }

    .value-display {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 2.2rem;
      color: var(--accent);
      text-shadow: 0 0 20px rgba(0,255,179,0.5);
      min-width: 5ch;
      text-align: center;
    }

    input[type=range] {
      -webkit-appearance: none;
      appearance: none;
      width: 220px;
      height: 3px;
      background: var(--muted);
      border-radius: 2px;
      outline: none;
      cursor: pointer;
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 18px;
      height: 18px;
      background: var(--accent);
      border-radius: 50%;
      box-shadow: 0 0 12px rgba(0,255,179,0.8);
      transition: transform 0.1s;
    }
    input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.3); }

    .btn {
      font-family: 'Space Mono', monospace;
      font-size: 0.7rem;
      letter-spacing: 0.15em;
      padding: 0.5rem 1.2rem;
      border: 1px solid var(--accent2);
      background: transparent;
      color: var(--accent2);
      border-radius: 2px;
      cursor: pointer;
      text-transform: uppercase;
      transition: background 0.2s, color 0.2s, box-shadow 0.2s;
    }
    .btn:hover {
      background: var(--accent2);
      color: var(--bg);
      box-shadow: 0 0 20px rgba(255,61,110,0.5);
    }
    .btn.active {
      background: var(--accent2);
      color: var(--bg);
    }

    footer {
      font-size: 0.6rem;
      color: #333;
      letter-spacing: 0.15em;
    }
  </style>
</head>
<body>

<header>
  <h1>WAVE LAB</h1>
  <span class="formula">f(x) = sin(x + φ) · a</span>
</header>

<div class="canvas-wrapper">
  <canvas id="c"></canvas>
  <span class="axis-x">x →</span>
  <span class="axis-y">↑ y</span>
</div>

<div class="controls">
  <div class="knob-group">
    <span class="knob-label">Amplitud (a)</span>
    <div class="value-display" id="aVal">1.00</div>
    <input type="range" id="aSlider" min="-3" max="3" step="0.01" value="1">
  </div>

  <div class="knob-group">
    <span class="knob-label">Frecuencia (f)</span>
    <div class="value-display" id="fVal">1.00</div>
    <input type="range" id="fSlider" min="0.1" max="5" step="0.05" value="1">
  </div>

  <div class="knob-group">
    <span class="knob-label">Animación</span>
    <button class="btn active" id="animBtn">PAUSAR</button>
  </div>
</div>

<footer>WAVE LAB · FLASK + CANVAS · SEN(X)·A</footer>

<script>
  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');

  let a = 1, freq = 1, phase = 0;
  let animating = true;
  let raf;

  const aSlider = document.getElementById('aSlider');
  const fSlider = document.getElementById('fSlider');
  const aVal    = document.getElementById('aVal');
  const fVal    = document.getElementById('fVal');
  const animBtn = document.getElementById('animBtn');

  aSlider.addEventListener('input', () => {
    a = parseFloat(aSlider.value);
    aVal.textContent = a.toFixed(2);
  });
  fSlider.addEventListener('input', () => {
    freq = parseFloat(fSlider.value);
    fVal.textContent = freq.toFixed(2);
  });
  animBtn.addEventListener('click', () => {
    animating = !animating;
    animBtn.textContent = animating ? 'PAUSAR' : 'ANIMAR';
    animBtn.classList.toggle('active', animating);
    if (animating) loop();
    else cancelAnimationFrame(raf);
  });

  function resize() {
    const w = canvas.parentElement.clientWidth;
    const h = canvas.parentElement.clientHeight;
    canvas.width  = w * devicePixelRatio;
    canvas.height = h * devicePixelRatio;
    ctx.scale(devicePixelRatio, devicePixelRatio);
  }

  function draw(W, H) {
    ctx.clearRect(0, 0, W, H);

    const cx = W / 2, cy = H / 2;
    const ampMax = H * 0.42;
    const xScale = W / (4 * Math.PI);   // show 2 full cycles

    // ── grid ──────────────────────────────────────────────────
    ctx.strokeStyle = 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 1;
    for (let i = 1; i < 4; i++) {
      const y = H * i / 4;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
    for (let i = 1; i < 8; i++) {
      const x = W * i / 8;
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }

    // ── axes ──────────────────────────────────────────────────
    ctx.strokeStyle = 'rgba(255,255,255,0.15)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(0, cy); ctx.lineTo(W, cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx, 0); ctx.lineTo(cx, H); ctx.stroke();

    // ── amplitude guides ──────────────────────────────────────
    if (a !== 0) {
      const ay = cy - a * ampMax;
      ctx.setLineDash([4, 6]);
      ctx.strokeStyle = 'rgba(0,255,179,0.18)';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(0, ay); ctx.lineTo(W, ay); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, 2*cy - ay); ctx.lineTo(W, 2*cy - ay); ctx.stroke();
      ctx.setLineDash([]);
    }

    // ── wave (glow layers) ────────────────────────────────────
    const draws = [
      { lw: 8,  alpha: 0.06, color: '0,255,179' },
      { lw: 4,  alpha: 0.15, color: '0,255,179' },
      { lw: 1.5,alpha: 1,    color: '0,255,179' },
    ];

    draws.forEach(({ lw, alpha, color }) => {
      ctx.beginPath();
      ctx.lineWidth = lw;
      ctx.strokeStyle = `rgba(${color},${alpha})`;
      for (let px = 0; px <= W; px++) {
        const xRad = (px - cx) / xScale + phase;
        const y = cy - Math.sin(freq * xRad) * a * ampMax;
        px === 0 ? ctx.moveTo(px, y) : ctx.lineTo(px, y);
      }
      ctx.stroke();
    });

    // ── moving dot ────────────────────────────────────────────
    const dotX = cx;
    const dotY = cy - Math.sin(freq * phase) * a * ampMax;
    ctx.beginPath();
    ctx.arc(dotX, dotY, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#ff3d6e';
    ctx.shadowColor = '#ff3d6e';
    ctx.shadowBlur = 20;
    ctx.fill();
    ctx.shadowBlur = 0;

    // ── label ─────────────────────────────────────────────────
    ctx.font = "bold 13px 'Space Mono', monospace";
    ctx.fillStyle = 'rgba(0,255,179,0.6)';
    ctx.fillText(`sin(${freq.toFixed(2)}x + φ) · ${a.toFixed(2)}`, 14, 22);
  }

  function loop() {
    const W = canvas.parentElement.clientWidth;
    const H = canvas.parentElement.clientHeight;
    draw(W, H);
    phase += 0.025;
    raf = requestAnimationFrame(loop);
  }

  window.addEventListener('resize', () => { resize(); });
  resize();
  loop();
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)
