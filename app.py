"""
App Flask: Simulación de Transientes Hidráulicos con TSNet
Integra parámetros editables y visualización de gráficos estático + animado.
"""

import os
import io
import base64
import tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.gettempdir()

# ─────────────────────────────────────────────────────────────
# HTML
# ─────────────────────────────────────────────────────────────
HTML = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Transientes Hidráulicos</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;700;800&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:      #070b14;
      --surface: #0d1220;
      --border:  #1c2740;
      --accent:  #3b82f6;
      --accent2: #06b6d4;
      --danger:  #f43f5e;
      --success: #10b981;
      --text:    #cbd5e1;
      --muted:   #475569;
      --label:   #64748b;
    }

    html, body {
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
    }

    body::after {
      content:''; position:fixed; inset:0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
      pointer-events:none; z-index:9999; opacity:.35;
    }

    .topbar {
      border-bottom: 1px solid var(--border);
      padding: 1.2rem 2.5rem;
      display: flex; align-items: center; gap: 1.5rem;
      background: rgba(13,18,32,0.8);
      backdrop-filter: blur(8px);
      position: sticky; top: 0; z-index: 100;
    }
    .topbar-logo { font-family:'Syne',sans-serif; font-weight:800; font-size:1.3rem; color:#fff; letter-spacing:0.05em; }
    .topbar-logo span { color: var(--accent2); }
    .topbar-sub { font-size:.65rem; color:var(--muted); letter-spacing:.15em; text-transform:uppercase; }

    .main { max-width: 1200px; margin: 0 auto; padding: 2.5rem 2rem 4rem; }

    .upload-zone {
      border: 2px dashed var(--border); border-radius: 8px; padding: 2rem;
      text-align: center; cursor: pointer;
      transition: border-color .2s, background .2s;
      margin-bottom: 2rem; background: var(--surface);
    }
    .upload-zone:hover, .upload-zone.dragover { border-color: var(--accent); background: rgba(59,130,246,0.05); }
    .upload-zone input { display:none; }
    .upload-icon { font-size: 2rem; margin-bottom: .5rem; }
    .upload-label { font-size:.8rem; color:var(--muted); }
    .upload-name { font-size:.75rem; color:var(--accent2); margin-top:.4rem; font-weight:600; }

    .section-title {
      font-family:'Syne',sans-serif; font-size:.7rem; letter-spacing:.2em; text-transform:uppercase;
      color:var(--muted); margin-bottom:1rem; padding-bottom:.4rem; border-bottom:1px solid var(--border);
    }

    .params-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1rem; margin-bottom: 2rem;
    }
    .param-card {
      background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
      padding: 1rem 1.2rem; display: flex; flex-direction: column; gap: .5rem;
      transition: border-color .2s;
    }
    .param-card:focus-within { border-color: var(--accent); }
    .param-label { font-size:.6rem; letter-spacing:.15em; text-transform:uppercase; color:var(--label); }
    .param-name { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; color:#fff; }
    .param-desc { font-size:.62rem; color:var(--muted); line-height:1.4; }
    .param-input {
      background: #060a12; border: 1px solid var(--border); border-radius: 4px;
      color: var(--accent2); font-family:'JetBrains Mono',monospace;
      font-size: 1.1rem; font-weight:600; padding: .4rem .6rem; width: 100%;
      outline: none; margin-top: .3rem; transition: border-color .2s;
    }
    .param-input:focus { border-color: var(--accent); }

    .btn-simulate {
      display: flex; align-items:center; gap:.7rem; background: var(--accent);
      color: #fff; border: none; border-radius: 6px;
      font-family:'Syne',sans-serif; font-size:.9rem; font-weight:700;
      letter-spacing:.05em; padding: .9rem 2.5rem; cursor: pointer;
      transition: background .2s, box-shadow .2s, transform .1s;
      box-shadow: 0 0 30px rgba(59,130,246,0.2);
    }
    .btn-simulate:hover { background:#2563eb; box-shadow:0 0 40px rgba(59,130,246,0.4); }
    .btn-simulate:active { transform:scale(.98); }
    .btn-simulate:disabled { background:var(--muted); cursor:not-allowed; box-shadow:none; }

    .spinner {
      width:18px; height:18px; border:2px solid rgba(255,255,255,.3);
      border-top-color:#fff; border-radius:50%;
      animation: spin .7s linear infinite; display:none;
    }
    @keyframes spin { to { transform:rotate(360deg); } }
    .btn-simulate.loading .spinner { display:block; }
    .btn-simulate.loading .btn-text { opacity:.7; }

    .alert { padding:.8rem 1.2rem; border-radius:6px; font-size:.75rem; margin-top:1rem; display:none; }
    .alert.error { background:rgba(244,63,94,.1); border:1px solid rgba(244,63,94,.3); color:#fda4af; display:block; }
    .alert.info  { background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.3); color:#6ee7b7; display:block; }

    .results { margin-top:3rem; display:none; }
    .results.visible { display:block; }

    .results-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-top:1.5rem; }
    @media (max-width:800px) { .results-grid { grid-template-columns:1fr; } }

    .chart-card { background:var(--surface); border:1px solid var(--border); border-radius:8px; overflow:hidden; }
    .chart-card-header {
      padding:.7rem 1.2rem; border-bottom:1px solid var(--border);
      font-size:.65rem; letter-spacing:.15em; text-transform:uppercase;
      color:var(--label); display:flex; align-items:center; gap:.5rem;
    }
    .chart-card-header .dot { width:6px; height:6px; border-radius:50%; background:var(--accent2); }
    .chart-card img { width:100%; display:block; }

    .anim-wrapper { position:relative; background:#000; }
    .anim-controls {
      position:absolute; bottom:0; left:0; right:0;
      background:rgba(7,11,20,.85); backdrop-filter:blur(4px);
      display:flex; align-items:center; gap:1rem; padding:.5rem 1rem;
      border-top:1px solid var(--border);
    }
    #animCanvas { width:100%; display:block; }
    .anim-btn {
      background:transparent; border:1px solid var(--accent2);
      color:var(--accent2); font-family:'JetBrains Mono',monospace;
      font-size:.65rem; padding:.3rem .7rem; border-radius:3px; cursor:pointer;
      transition:background .15s, color .15s;
    }
    .anim-btn:hover { background:var(--accent2); color:var(--bg); }
    .anim-time { margin-left:auto; font-size:.7rem; color:var(--muted); }
    .speed-label { font-size:.6rem; color:var(--muted); }
    #speedRange {
      -webkit-appearance:none; appearance:none;
      width:70px; height:2px; background:var(--muted); border-radius:2px; outline:none;
    }
    #speedRange::-webkit-slider-thumb {
      -webkit-appearance:none; appearance:none;
      width:12px; height:12px; background:var(--accent2); border-radius:50%; cursor:pointer;
    }
    .action-row { display:flex; align-items:center; gap:1rem; flex-wrap:wrap; }
  </style>
</head>
<body>

<div class="topbar">
  <div>
    <div class="topbar-logo">HYDRO<span>TRANSIENT</span></div>
    <div class="topbar-sub">Simulador MOC &middot; TSNet &middot; Flask</div>
  </div>
</div>

<div class="main">

  <p class="section-title">Archivo de Red (.inp)</p>
  <div class="upload-zone" id="dropZone">
    <input type="file" id="inpFile" accept=".inp"/>
    <div class="upload-icon">&#128194;</div>
    <div class="upload-label">Arrastra tu archivo <strong>.inp</strong> aqu&iacute; o haz clic para seleccionar</div>
    <div class="upload-name" id="uploadName">Sin archivo seleccionado</div>
  </div>

  <p class="section-title">Par&aacute;metros de Simulaci&oacute;n</p>
  <div class="params-grid">
    <div class="param-card">
      <div class="param-label">tiempo total</div>
      <div class="param-name">tf</div>
      <div class="param-desc">Duraci&oacute;n de la simulaci&oacute;n [s]</div>
      <input class="param-input" type="number" id="tf" value="25" step="1" min="1"/>
    </div>
    <div class="param-card">
      <div class="param-label">inicio cierre</div>
      <div class="param-name">ts</div>
      <div class="param-desc">Inicio del cierre de v&aacute;lvula [s]</div>
      <input class="param-input" type="number" id="ts" value="3" step="0.5" min="0"/>
    </div>
    <div class="param-card">
      <div class="param-label">duraci&oacute;n cierre</div>
      <div class="param-name">tc</div>
      <div class="param-desc">Duraci&oacute;n del cierre [s]</div>
      <input class="param-input" type="number" id="tc" value="2" step="0.5" min="0"/>
    </div>
    <div class="param-card">
      <div class="param-label">apertura final</div>
      <div class="param-name">se</div>
      <div class="param-desc">0 = completamente cerrada [0&ndash;1]</div>
      <input class="param-input" type="number" id="se" value="0" step="0.01" min="0" max="1"/>
    </div>
    <div class="param-card">
      <div class="param-label">tipo de cierre</div>
      <div class="param-name">m</div>
      <div class="param-desc">1 = lineal &middot; 2 = cuadr&aacute;tico</div>
      <input class="param-input" type="number" id="m" value="2" step="1" min="1" max="2"/>
    </div>
    <div class="param-card">
      <div class="param-label">wavespeed</div>
      <div class="param-name">a</div>
      <div class="param-desc">Velocidad de onda [m/s]</div>
      <input class="param-input" type="number" id="wavespeed" value="1200" step="50" min="100"/>
    </div>
  </div>

  <div class="action-row">
    <button class="btn-simulate" id="btnSimulate" onclick="runSimulation()">
      <div class="spinner" id="spinner"></div>
      <span class="btn-text">&#9654; Simular Estado Transiente</span>
    </button>
    <div class="alert" id="alertBox"></div>
  </div>

  <div class="results" id="results">
    <p class="section-title">Resultados</p>
    <div class="results-grid">
      <div class="chart-card">
        <div class="chart-card-header"><div class="dot"></div>Head por Nodo (est&aacute;tico)</div>
        <img id="staticChart" src="" alt="Gr&aacute;fico est&aacute;tico"/>
      </div>
      <div class="chart-card">
        <div class="chart-card-header"><div class="dot" style="background:#f59e0b"></div>Perfil de Head &mdash; Animaci&oacute;n</div>
        <div class="anim-wrapper">
          <canvas id="animCanvas"></canvas>
          <div class="anim-controls">
            <button class="anim-btn" id="playBtn" onclick="togglePlay()">&#9646;&#9646; PAUSAR</button>
            <button class="anim-btn" onclick="resetAnim()">&#8635; REINICIAR</button>
            <span class="speed-label">Vel.</span>
            <input type="range" id="speedRange" min="1" max="10" value="3" oninput="updateSpeed(this.value)"/>
            <span class="anim-time" id="animTime">t = 0.00 s</span>
          </div>
        </div>
      </div>
    </div>
  </div>

</div>

<script>
const dropZone   = document.getElementById('dropZone');
const inpFile    = document.getElementById('inpFile');
const uploadName = document.getElementById('uploadName');

dropZone.addEventListener('click', () => inpFile.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('dragover');
  if (e.dataTransfer.files[0]) { inpFile.files = e.dataTransfer.files; uploadName.textContent = e.dataTransfer.files[0].name; }
});
inpFile.addEventListener('change', () => { uploadName.textContent = inpFile.files[0]?.name || 'Sin archivo seleccionado'; });

async function runSimulation() {
  const file = inpFile.files[0];
  if (!file) { showAlert('Selecciona un archivo .inp primero.', 'error'); return; }
  setLoading(true); hideAlert();

  const fd = new FormData();
  fd.append('inp_file',  file);
  fd.append('tf',        document.getElementById('tf').value);
  fd.append('ts',        document.getElementById('ts').value);
  fd.append('tc',        document.getElementById('tc').value);
  fd.append('se',        document.getElementById('se').value);
  fd.append('m',         document.getElementById('m').value);
  fd.append('wavespeed', document.getElementById('wavespeed').value);

  try {
    const res  = await fetch('/simulate', { method:'POST', body:fd });
    const data = await res.json();
    if (!res.ok || data.error) { showAlert(data.error || 'Error en la simulación.', 'error'); setLoading(false); return; }
    document.getElementById('staticChart').src = 'data:image/png;base64,' + data.static_chart;
    initAnimation(data.anim_data);
    document.getElementById('results').classList.add('visible');
    showAlert('Simulación completada exitosamente.', 'info');
  } catch(err) {
    showAlert('Error de red o servidor: ' + err.message, 'error');
  }
  setLoading(false);
}

function setLoading(v) {
  const btn = document.getElementById('btnSimulate');
  btn.disabled = v; btn.classList.toggle('loading', v);
  document.getElementById('spinner').style.display = v ? 'block' : 'none';
}
function showAlert(msg, type) { const el=document.getElementById('alertBox'); el.textContent=msg; el.className='alert '+type; }
function hideAlert() { document.getElementById('alertBox').className='alert'; }

let animData=null, frame=0, playing=true, speed=3, tickInterval=null;

function initAnimation(data) {
  animData=data; frame=0; playing=true;
  document.getElementById('playBtn').textContent='⏸ PAUSAR';
  if(tickInterval) clearInterval(tickInterval);
  drawFrame();
  tickInterval = setInterval(()=>{ if(!playing||!animData) return; frame=(frame+speed)%animData.t.length; drawFrame(); }, 50);
}

function drawFrame() {
  if(!animData) return;
  const canvas=document.getElementById('animCanvas');
  const ctx=canvas.getContext('2d');
  const W=canvas.parentElement.clientWidth;
  canvas.width=W; canvas.height=Math.round(W*0.55);
  const H=canvas.height;
  const pad={top:30,right:20,bottom:45,left:55};
  const cw=W-pad.left-pad.right, ch=H-pad.top-pad.bottom;
  const {x1,x2,H1,H2,t}=animData;
  const hMin=Math.min(...H1.flat(),...H2.flat());
  const hMax=Math.max(...H1.flat(),...H2.flat());
  const xMax=x2[x2.length-1];
  const toX=x=>pad.left+(x/xMax)*cw;
  const toY=h=>pad.top+ch-((h-hMin)/(hMax-hMin+1e-9))*ch;

  ctx.fillStyle='#07090f'; ctx.fillRect(0,0,W,H);

  ctx.strokeStyle='rgba(255,255,255,0.04)'; ctx.lineWidth=1;
  for(let i=0;i<=4;i++){
    const y=pad.top+ch*i/4;
    ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(pad.left+cw,y); ctx.stroke();
    const val=hMax-(hMax-hMin)*i/4;
    ctx.fillStyle='rgba(100,116,139,.7)'; ctx.font='10px monospace';
    ctx.textAlign='right'; ctx.fillText(val.toFixed(1),pad.left-6,y+4);
  }
  for(let i=0;i<=4;i++){
    const x=pad.left+cw*i/4;
    ctx.beginPath(); ctx.moveTo(x,pad.top); ctx.lineTo(x,pad.top+ch); ctx.stroke();
    ctx.fillStyle='rgba(100,116,139,.7)'; ctx.font='10px monospace';
    ctx.textAlign='center'; ctx.fillText((xMax*i/4).toFixed(0)+'m',x,pad.top+ch+16);
  }

  ctx.strokeStyle='rgba(255,255,255,0.15)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(pad.left,pad.top); ctx.lineTo(pad.left,pad.top+ch); ctx.lineTo(pad.left+cw,pad.top+ch); ctx.stroke();

  ctx.fillStyle='#64748b'; ctx.font='11px monospace';
  ctx.textAlign='center'; ctx.fillText('Distancia [m]',pad.left+cw/2,H-6);
  ctx.save(); ctx.translate(13,pad.top+ch/2); ctx.rotate(-Math.PI/2);
  ctx.fillText('Head [m]',0,0); ctx.restore();

  const f=Math.min(frame,H1.length-1);

  [[8,0.06,'59,130,246'],[3,0.18,'59,130,246'],[1.5,1,'59,130,246']].forEach(([lw,alpha,c])=>{
    ctx.beginPath(); ctx.lineWidth=lw; ctx.strokeStyle=`rgba(${c},${alpha})`;
    x1.forEach((x,i)=>{ const px=toX(x),py=toY(H1[f][i]); i===0?ctx.moveTo(px,py):ctx.lineTo(px,py); });
    ctx.stroke();
  });
  [[8,0.06,'6,182,212'],[3,0.18,'6,182,212'],[1.5,1,'6,182,212']].forEach(([lw,alpha,c])=>{
    ctx.beginPath(); ctx.lineWidth=lw; ctx.strokeStyle=`rgba(${c},${alpha})`;
    x2.forEach((x,i)=>{ const px=toX(x),py=toY(H2[f][i]); i===0?ctx.moveTo(px,py):ctx.lineTo(px,py); });
    ctx.stroke();
  });

  [['P1','rgba(59,130,246,1)'],['P2','rgba(6,182,212,1)']].forEach(([label,color],i)=>{
    ctx.strokeStyle=color; ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(pad.left+10+i*70,pad.top+8); ctx.lineTo(pad.left+30+i*70,pad.top+8); ctx.stroke();
    ctx.fillStyle=color; ctx.font='10px monospace'; ctx.textAlign='left';
    ctx.fillText(label,pad.left+34+i*70,pad.top+12);
  });

  document.getElementById('animTime').textContent=`t = ${t[f].toFixed(2)} s`;
}

function togglePlay(){ playing=!playing; document.getElementById('playBtn').textContent=playing?'⏸ PAUSAR':'▶ CONTINUAR'; }
function resetAnim(){ frame=0; playing=true; document.getElementById('playBtn').textContent='⏸ PAUSAR'; drawFrame(); }
function updateSpeed(v){ speed=parseInt(v); }
window.addEventListener('resize',()=>{ if(animData) drawFrame(); });
</script>
</body>
</html>'''


# ─────────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        import tsnet
    except ImportError:
        return jsonify({'error': 'tsnet no está instalado. Ejecuta: pip install tsnet'}), 500

    try:
        f = request.files.get('inp_file')
        if not f:
            return jsonify({'error': 'No se recibió archivo .inp'}), 400

        inp_path = os.path.join(UPLOAD_FOLDER, 'sistema.inp')
        f.save(inp_path)

        tf        = float(request.form.get('tf',        25))
        ts        = float(request.form.get('ts',         3))
        tc        = float(request.form.get('tc',         2))
        se        = float(request.form.get('se',         0))
        m         = int(  request.form.get('m',          2))
        wavespeed = float(request.form.get('wavespeed', 1200))

        tm = tsnet.network.TransientModel(inp_path)
        tm.set_wavespeed(wavespeed)
        tm.set_time(tf)
        tm.valve_closure('V1', [tc, ts, se, m])

        tm = tsnet.simulation.Initializer(tm, 0.0)
        tm = tsnet.simulation.MOCSimulator(tm)

        # ── Gráfico estático: head por nodo ──
        nodes   = ['J2', 'J3']
        t_vec   = tm.simulation_timestamps
        fig_s, ax_s = plt.subplots(figsize=(7, 4), facecolor='#0d1220')
        ax_s.set_facecolor('#07090f')
        colors_n = ['#3b82f6', '#06b6d4', '#f59e0b', '#10b981']

        for idx, node in enumerate(nodes):
            try:
                H_node = np.array(tm.nodes[node].head)
                ax_s.plot(t_vec, H_node, color=colors_n[idx % len(colors_n)],
                          linewidth=1.5, label=node)
            except Exception:
                pass

        ax_s.set_xlabel('Tiempo [s]', color='#64748b', fontsize=9)
        ax_s.set_ylabel('Head [m]',   color='#64748b', fontsize=9)
        ax_s.set_title('Head vs Tiempo por Nodo', color='#cbd5e1', fontsize=10)
        ax_s.tick_params(colors='#64748b')
        for spine in ax_s.spines.values(): spine.set_edgecolor('#1c2740')
        ax_s.legend(facecolor='#0d1220', edgecolor='#1c2740', labelcolor='#cbd5e1', fontsize=8)
        ax_s.grid(color='#1c2740', linestyle='--', linewidth=0.5)
        plt.tight_layout()

        buf = io.BytesIO()
        fig_s.savefig(buf, format='png', dpi=120, facecolor='#0d1220')
        buf.seek(0)
        static_b64 = base64.b64encode(buf.read()).decode()
        plt.close(fig_s)

        # ── Datos animación ──
        pipe1 = tm.links['P1']
        pipe2 = tm.links['P2']
        H1 = np.array(pipe1.H_profile)
        H2 = np.array(pipe2.H_profile)

        x1 = np.linspace(0, pipe1.length, H1.shape[1]).tolist()
        x2 = np.linspace(pipe1.length, pipe1.length + pipe2.length, H2.shape[1]).tolist()

        # Submuestrear a máximo 500 frames para no saturar el JSON
        total = len(H1)
        step  = max(1, total // 500)
        idx_r = list(range(0, total, step))

        anim_data = {
            'x1': x1,
            'x2': x2,
            'H1': H1[idx_r].tolist(),
            'H2': H2[idx_r].tolist(),
            't':  [float(t_vec[i]) for i in idx_r],
        }

        return jsonify({'static_chart': static_b64, 'anim_data': anim_data})

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'detail': traceback.format_exc()}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
