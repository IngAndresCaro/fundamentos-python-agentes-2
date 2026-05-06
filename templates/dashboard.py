"""
dashboard.py — Templates HTML para el dashboard principal.

La oficina es un canvas HTML5 con tres zonas:
  - Trabajando (verde)   - agentes con misiones pendientes
  - Holgazaneando (rojo) - agentes sin misiones y energía > 50
  - Recreándose (azul)   - agentes sin misiones y energía <= 50

Los agentes se mueven con animación CSS dentro de su zona asignada.
Los botones visibles dependen del rol (admin vs invitado).
"""

# {rol} — "admin" o "invitado", controla qué botones se muestran
# {agentes_json} — JSON con la lista de agentes para el canvas
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>La Agencia — Oficina</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', sans-serif;
      background: #0d0d0d;
      color: #e0e0e0;
      min-height: 100vh;
    }}
    /* ── Top Bar ── */
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.8rem 1.5rem;
      background: #111;
      border-bottom: 1px solid #222;
    }}
    .topbar h1 {{ font-size: 1.1rem; color: #00ff99; }}
    .topbar .meta {{ font-size: 0.78rem; color: #666; }}
    .topbar a {{
      color: #ff4444; text-decoration: none; font-size: 0.85rem;
      border: 1px solid #ff4444; padding: 0.3rem 0.8rem; border-radius: 4px;
    }}
    .topbar a:hover {{ background: #ff4444; color: #000; }}

    /* ── Layout ── */
    .main {{ display: flex; height: calc(100vh - 52px); }}
    .sidebar {{
      width: 260px;
      background: #111;
      border-right: 1px solid #222;
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      overflow-y: auto;
    }}
    .sidebar h2 {{ font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.3rem; }}
    .sidebar button {{
      width: 100%; padding: 0.6rem 0.8rem;
      background: #1a1a1a; color: #e0e0e0;
      border: 1px solid #333; border-radius: 4px;
      font-size: 0.85rem; cursor: pointer;
      text-align: left; transition: all 0.2s;
    }}
    .sidebar button:hover {{ border-color: #00ff99; color: #00ff99; }}
    .sidebar .sep {{ border-top: 1px solid #222; margin: 0.5rem 0; }}

    /* ── Office Canvas ── */
    .office {{
      flex: 1;
      position: relative;
      overflow: hidden;
      background:
        radial-gradient(circle at 20% 80%, rgba(0,255,150,0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(100,100,255,0.03) 0%, transparent 50%),
        #0d0d0d;
    }}
    .zone {{
      position: absolute;
      border-radius: 12px;
      border: 1px dashed;
      display: flex;
      flex-direction: column;
      padding: 0.6rem;
      overflow: hidden;
    }}
    .zone-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 0.4rem;
      opacity: 0.7;
    }}
    .zone-trabajando {{
      top: 3%; left: 2%; width: 46%; height: 45%;
      border-color: rgba(0,255,150,0.3);
      background: rgba(0,255,150,0.04);
    }}
    .zone-trabajando .zone-label {{ color: #00ff99; }}
    .zone-holgazaneando {{
      top: 3%; right: 2%; width: 46%; height: 45%;
      border-color: rgba(255,68,68,0.3);
      background: rgba(255,68,68,0.04);
    }}
    .zone-holgazaneando .zone-label {{ color: #ff4444; }}
    .zone-recreandose {{
      bottom: 3%; left: 2%; width: 96%; height: 42%;
      border-color: rgba(100,150,255,0.3);
      background: rgba(100,150,255,0.04);
    }}
    .zone-recreandose .zone-label {{ color: #6496ff; }}

    /* ── Agents ── */
    .agent {{
      width: 52px;
      text-align: center;
      cursor: default;
      transition: transform 0.15s;
      flex-shrink: 0;
    }}
    .agent:hover {{ transform: scale(1.15); }}
    .agent-icon {{
      font-size: 1.8rem;
      animation: float 3s ease-in-out infinite;
    }}
    .agent-name {{
      font-size: 0.6rem;
      color: #ccc;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 64px;
    }}
    .agent-bar {{
      height: 3px;
      border-radius: 2px;
      margin-top: 2px;
      background: #333;
      overflow: hidden;
    }}
    .agent-bar-fill {{
      height: 100%;
      border-radius: 2px;
      transition: width 0.5s;
    }}

    @keyframes float {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-6px); }}
    }}
    @keyframes wander {{
      0%   {{ transform: translate(0, 0); }}
      25%  {{ transform: translate(15px, -10px); }}
      50%  {{ transform: translate(-10px, 8px); }}
      75%  {{ transform: translate(12px, 12px); }}
      100% {{ transform: translate(0, 0); }}
    }}
    .agent {{ animation: wander var(--wander-duration, 8s) ease-in-out infinite; }}
    .agent .agent-icon {{ animation: float 3s ease-in-out infinite; }}

    /* ── Modal ── */
    .modal-bg {{
      display: none;
      position: fixed; top: 0; left: 0;
      width: 100%; height: 100%;
      background: rgba(0,0,0,0.7);
      z-index: 100;
      justify-content: center;
      align-items: center;
    }}
    .modal-bg.active {{ display: flex; }}
    .modal {{
      background: #1a1a1a;
      border: 1px solid #333;
      border-radius: 8px;
      padding: 1.8rem;
      width: 400px;
      max-height: 80vh;
      overflow-y: auto;
    }}
    .modal h2 {{ font-size: 1.1rem; color: #00ff99; margin-bottom: 1rem; }}
    .modal label {{ display: block; font-size: 0.78rem; color: #888; margin-bottom: 0.2rem; margin-top: 0.7rem; }}
    .modal input, .modal select, .modal textarea {{
      width: 100%; padding: 0.55rem 0.8rem;
      background: #111; border: 1px solid #333;
      border-radius: 4px; color: #e0e0e0;
      font-size: 0.9rem;
    }}
    .modal input:focus, .modal select:focus, .modal textarea:focus {{ outline: none; border-color: #00ff99; }}
    .modal textarea {{ resize: vertical; min-height: 60px; }}
    .modal .btn-row {{ display: flex; gap: 0.6rem; margin-top: 1.2rem; }}
    .modal .btn {{
      flex: 1; padding: 0.6rem;
      border: none; border-radius: 4px;
      font-size: 0.9rem; font-weight: 600;
      cursor: pointer;
    }}
    .modal .btn-ok {{ background: #00ff99; color: #000; }}
    .modal .btn-ok:hover {{ opacity: 0.85; }}
    .modal .btn-cancel {{ background: #333; color: #e0e0e0; }}
    .modal .btn-cancel:hover {{ background: #444; }}

    /* ── Toast ── */
    .toast {{
      position: fixed; bottom: 1.5rem; right: 1.5rem;
      padding: 0.7rem 1.2rem;
      border-radius: 6px;
      font-size: 0.85rem;
      z-index: 200;
      opacity: 0;
      transition: opacity 0.3s;
    }}
    .toast.show {{ opacity: 1; }}
    .toast.ok  {{ background: #003320; border: 1px solid #00ff99; color: #00ff99; }}
    .toast.err {{ background: #330000; border: 1px solid #ff4444; color: #ff4444; }}

    /* ── Agent detail panel ── */
    .detail-panel {{
      display: none;
      position: absolute;
      bottom: 0; left: 0; right: 0;
      background: #151515;
      border-top: 1px solid #333;
      padding: 1rem 1.5rem;
      z-index: 50;
      max-height: 200px;
      overflow-y: auto;
    }}
    .detail-panel.active {{ display: block; }}
    .detail-panel h3 {{ color: #00ff99; font-size: 0.95rem; margin-bottom: 0.4rem; }}
    .detail-panel .info {{ font-size: 0.8rem; color: #aaa; }}
    .detail-panel .close-detail {{
      position: absolute; top: 0.5rem; right: 1rem;
      background: none; border: none; color: #666;
      font-size: 1.2rem; cursor: pointer;
    }}
  </style>
</head>
<body>

  <!-- ── Top Bar ── -->
  <div class="topbar">
    <h1>🏢 La Agencia</h1>
    <span class="meta">Rol: <strong>{rol}</strong></span>
    <a href="/logout">Cerrar sesión</a>
  </div>

  <div class="main">
    <!-- ── Sidebar ── -->
    <div class="sidebar">
      <h2>Operaciones</h2>
      <button onclick="refreshOffice()">🔄 Actualizar oficina</button>

      <div id="admin-actions" style="display:{admin_display}">
        <div class="sep"></div>
        <h2>Admin</h2>
        <button onclick="openModal('crear-agente')">➕ Crear agente</button>
        <button onclick="openModal('crear-mision')">📋 Nueva misión</button>
        <button onclick="openModal('enviar-mensaje')">💬 Enviar mensaje</button>
        <button onclick="openModal('completar-mision')">✅ Completar misión</button>
        <button onclick="openModal('recargar-agente')">🔋 Recargar agente</button>
        <button onclick="openModal('eliminar-agente')">🗑️ Eliminar agente</button>
      </div>

      <div class="sep"></div>
      <h2>Consultas</h2>
      <input type="file" id="videoInput" accept="video/*" style="display:none;">
      <button id="loadVideoBtn" style="width:100%;margin-bottom:0.5rem">Cargar video</button>
      <button onclick="openModal('ver-misiones')">🔍 Misiones de agente</button>
      <button onclick="openModal('ver-mensajes')">📨 Mensajes de agente</button>
      <button onclick="openModal('ver-briefing')">🗂️ Briefing de agente</button>
    </div>

    <!-- ── Office ── -->
    <div class="office" id="office">
      <div class="zone zone-trabajando">
        <span class="zone-label">💼 Trabajando</span>
        <div id="zone-trabajando-agents" style="display:flex;flex-wrap:wrap;gap:8px;flex:1;align-content:flex-start;overflow-y:auto;"></div>
      </div>
      <div class="zone zone-holgazaneando">
        <span class="zone-label">😴 Holgazaneando</span>
        <div id="zone-holgazaneando-agents" style="display:flex;flex-wrap:wrap;gap:8px;flex:1;align-content:flex-start;overflow-y:auto;"></div>
      </div>
      <div class="zone zone-recreandose">
        <span class="zone-label">🎮 Recreándose</span>
        <div id="zone-recreandose-agents" style="display:flex;flex-wrap:wrap;gap:8px;flex:1;align-content:flex-start;overflow-y:auto;"></div>
      </div>

      <!-- Detail panel -->
      <div class="detail-panel" id="detail-panel">
        <button class="close-detail" onclick="closeDetail()">✕</button>
        <h3 id="detail-name"></h3>
        <div class="info" id="detail-info"></div>
      </div>
    </div>
  </div>

  <!-- ═══ MODALS ═══ -->

  <!-- Crear agente -->
  <div class="modal-bg" id="modal-crear-agente">
    <div class="modal">
      <h2>➕ Crear agente</h2>
      <label>Nombre</label>
      <input id="ca-nombre" placeholder="Ej: Agente Smith">
      <label>Rol</label>
      <select id="ca-rol">
        <optgroup label="Scrum">
          <option value="scrum_master">Scrum Master</option>
          <option value="product_owner">Product Owner</option>
        </optgroup>
        <optgroup label="Gestión">
          <option value="orquestador">Orquestador</option>
          <option value="admin">Admin</option>
        </optgroup>
        <optgroup label="Análisis">
          <option value="spec">Spec</option>
        </optgroup>
        <optgroup label="Desarrollo">
          <option value="backend">Backend</option>
          <option value="frontend">Frontend</option>
          <option value="arquitecto">Arquitecto</option>
        </optgroup>
        <optgroup label="Operaciones">
          <option value="devops">DevOps</option>
          <option value="dba">DBA</option>
          <option value="seguridad">Seguridad</option>
        </optgroup>
        <optgroup label="Calidad">
          <option value="qa">QA</option>
        </optgroup>
      </select>
      <label>Energía inicial</label>
      <input id="ca-energia" type="number" value="100" min="1" max="200">
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('crear-agente')">Cancelar</button>
        <button class="btn btn-ok" onclick="submitCrearAgente()">Crear</button>
      </div>
    </div>
  </div>

  <!-- Crear misión -->
  <div class="modal-bg" id="modal-crear-mision">
    <div class="modal">
      <h2>📋 Nueva misión</h2>
      <label>Título</label>
      <input id="cm-titulo" placeholder="Ej: Infiltrar base enemiga">
      <label>Descripción</label>
      <textarea id="cm-desc" placeholder="Detalles de la misión..."></textarea>
      <label>Agente asignado</label>
      <input id="cm-agente" placeholder="Nombre del agente">
      <label>Energía requerida</label>
      <input id="cm-energia" type="number" value="20" min="1">
      <label>Recompensa (XP)</label>
      <input id="cm-recompensa" type="number" value="10" min="0">
      <label>Prioridad</label>
      <select id="cm-prioridad">
        <option value="baja">Baja</option>
        <option value="media" selected>Media</option>
        <option value="alta">Alta</option>
        <option value="critica">Crítica</option>
      </select>
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('crear-mision')">Cancelar</button>
        <button class="btn btn-ok" onclick="submitCrearMision()">Crear</button>
      </div>
    </div>
  </div>

  <!-- Enviar mensaje -->
  <div class="modal-bg" id="modal-enviar-mensaje">
    <div class="modal">
      <h2>💬 Enviar mensaje</h2>
      <label>Remitente</label>
      <input id="em-remitente" placeholder="Tu nombre o alias">
      <label>Destinatario (agente)</label>
      <input id="em-destinatario" placeholder="Nombre del agente">
      <label>Contenido</label>
      <textarea id="em-contenido" placeholder="Escribe el mensaje..."></textarea>
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('enviar-mensaje')">Cancelar</button>
        <button class="btn btn-ok" onclick="submitEnviarMensaje()">Enviar</button>
      </div>
    </div>
  </div>

  <!-- Completar misión -->
  <div class="modal-bg" id="modal-completar-mision">
    <div class="modal">
      <h2>✅ Completar misión</h2>
      <label>ID de la misión</label>
      <input id="comp-id" type="number" min="1" placeholder="Ej: 1">
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('completar-mision')">Cancelar</button>
        <button class="btn btn-ok" onclick="submitCompletarMision()">Completar</button>
      </div>
    </div>
  </div>

  <!-- Ver misiones de agente -->
  <div class="modal-bg" id="modal-ver-misiones">
    <div class="modal">
      <h2>🔍 Misiones de agente</h2>
      <label>Nombre del agente</label>
      <input id="vm-agente" placeholder="Nombre del agente">
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('ver-misiones')">Cancelar</button>
        <button class="btn btn-ok" onclick="submitVerMisiones()">Buscar</button>
      </div>
      <div id="vm-resultado" style="margin-top:1rem;font-size:0.82rem;color:#aaa;"></div>
    </div>
  </div>

  <!-- Ver mensajes de agente -->
  <div class="modal-bg" id="modal-ver-mensajes">
    <div class="modal">
      <h2>📨 Mensajes de agente</h2>
      <label>Nombre del agente</label>
      <input id="vmsg-agente" placeholder="Nombre del agente">
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('ver-mensajes')">Cancelar</button>
        <button class="btn btn-ok" onclick="submitVerMensajes()">Buscar</button>
      </div>
      <div id="vmsg-resultado" style="margin-top:1rem;font-size:0.82rem;color:#aaa;"></div>
    </div>
  </div>

  <!-- Briefing de agente -->
  <div class="modal-bg" id="modal-ver-briefing">
    <div class="modal" style="max-width:600px;max-height:85vh;overflow-y:auto">
      <h2>🗂️ Briefing de agente</h2>
      <label>Nombre del agente</label>
      <input id="vb-agente" placeholder="Nombre del agente">
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('ver-briefing')">Cancelar</button>
        <button class="btn btn-ok" onclick="submitVerBriefing()">Generar briefing</button>
      </div>
      <div id="vb-resultado" style="margin-top:1rem;font-size:0.82rem;color:#aaa;"></div>
    </div>
  </div>

  <!-- Eliminar agente -->
  <div class="modal-bg" id="modal-eliminar-agente">
    <div class="modal">
      <h2>🗑️ Eliminar agente</h2>
      <p style="color:#aaa;font-size:0.82rem;margin-bottom:0.8rem">Agentes con misiones activas (pendiente/en_curso) no se pueden eliminar.</p>
      <div id="ea-lista" style="margin-bottom:1rem;max-height:300px;overflow-y:auto;font-size:0.85rem;">
        <i style="color:#666">Cargando agentes...</i>
      </div>
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('eliminar-agente')">Cerrar</button>
      </div>
    </div>
  </div>

  <!-- Recargar agente -->
  <div class="modal-bg" id="modal-recargar-agente">
    <div class="modal">
      <h2>🔋 Recargar agente</h2>
      <label>Agente</label>
      <select id="ra-agente" style="width:100%;padding:0.5rem;margin-bottom:0.6rem;background:#111;border:1px solid #333;color:#eee;border-radius:4px">
        <option value="">Cargando...</option>
      </select>
      <div id="ra-info" style="font-size:0.78rem;color:#888;margin-bottom:0.6rem"></div>
      <label>Nuevo rol (opcional)</label>
      <select id="ra-rol">
        <option value="">(sin cambio)</option>
        <optgroup label="Scrum">
          <option value="scrum_master">Scrum Master</option>
          <option value="product_owner">Product Owner</option>
        </optgroup>
        <optgroup label="Gestión">
          <option value="orquestador">Orquestador</option>
          <option value="admin">Admin</option>
        </optgroup>
        <optgroup label="Análisis">
          <option value="spec">Spec</option>
        </optgroup>
        <optgroup label="Desarrollo">
          <option value="backend">Backend</option>
          <option value="frontend">Frontend</option>
          <option value="arquitecto">Arquitecto</option>
        </optgroup>
        <optgroup label="Operaciones">
          <option value="devops">DevOps</option>
          <option value="dba">DBA</option>
          <option value="seguridad">Seguridad</option>
        </optgroup>
        <optgroup label="Calidad">
          <option value="qa">QA</option>
        </optgroup>
      </select>
      <label>Nueva energía (opcional)</label>
      <input id="ra-energia" type="number" min="1" max="200" placeholder="Ej: 100">
      <div class="btn-row">
        <button class="btn btn-cancel" onclick="closeModal('recargar-agente')">Cancelar</button>
        <button class="btn btn-ok" onclick="submitRecargarAgente()">Guardar</button>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div class="toast" id="toast"></div>


  // ─── Estado ───
  const ROL = "{rol}";
  let agentes = [];

  // ─── Helpers ───
  function toast(msg, ok) {{
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast show ' + (ok ? 'ok' : 'err');
    setTimeout(() => t.className = 'toast', 3000);
  }}

  function openModal(name) {{
    document.getElementById('modal-' + name).classList.add('active');
    if (name === 'eliminar-agente') cargarListaEliminacion();
    if (name === 'recargar-agente') cargarListaRecarga();
  }}
  function closeModal(name) {{
    document.getElementById('modal-' + name).classList.remove('active');
  }}

  // ─── API helpers ───
  async function api(method, path, body) {{
    const opts = {{ method, headers: {{ 'Content-Type': 'application/json', 'X-API-KEY': '{api_key}' }} }};
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch('/api' + path, opts);
    return {{ status: res.status, data: await res.json() }};
  }}

  // ─── Office rendering ───
  const ICONS = {{ 'scrum_master': '🏅', 'product_owner': '📌', 'orquestador': '🎯', 'admin': '👔', 'spec': '📋', 'backend': '⚙️', 'frontend': '🎨', 'arquitecto': '🏗️', 'devops': '🚀', 'dba': '🗄️', 'seguridad': '🔐', 'qa': '🧪' }};

  function energyColor(e) {{
    if (e > 70) return '#00ff99';
    if (e > 30) return '#ffaa00';
    return '#ff4444';
  }}

  function classifyAgent(ag, misiones) {{
    const pending = misiones.filter(m => m.estado === 'pendiente');
    if (pending.length > 0) return 'trabajando';
    if (ag.energia > 50) return 'holgazaneando';
    return 'recreandose';
  }}

  function placeAgents(classified) {{
    ['trabajando', 'holgazaneando', 'recreandose'].forEach(zone => {{
      const container = document.getElementById('zone-' + zone + '-agents');
      container.innerHTML = '';
      const list = classified[zone] || [];
      list.forEach((ag, i) => {{
        const el = document.createElement('div');
        el.className = 'agent';
        const dur = 6 + Math.random() * 8;
        const delay = Math.random() * -10;
        el.style.cssText = `
          --wander-duration: ${{dur}}s;
          animation-delay: ${{delay}}s;
        `;
        el.onclick = () => showDetail(ag);
        el.innerHTML = `
          <div class="agent-icon">${{ICONS[ag.rol] || '🤖'}}</div>
          <div class="agent-name">${{ag.nombre}}</div>
          <div class="agent-bar"><div class="agent-bar-fill" style="width:${{ag.energia}}%;background:${{energyColor(ag.energia)}}"></div></div>
          <div style="font-size:0.6rem;color:#4dc9f6;text-align:center">⭐ ${{ag.experiencia || 0}} XP</div>
        `;
        container.appendChild(el);
      }});
    }});
  }}

  function showDetail(ag) {{
    const panel = document.getElementById('detail-panel');
    document.getElementById('detail-name').textContent = (ICONS[ag.rol] || '🤖') + ' ' + ag.nombre;
    let html = `<b>Rol:</b> ${{ag.rol}} &nbsp; <b>Energía:</b> ${{ag.energia}}/100 &nbsp; <b style="color:#4dc9f6">⭐ ${{ag.experiencia || 0}} XP</b>`;
    if (ag.misiones && ag.misiones.length > 0) {{
      html += '<br><b>Misiones:</b><ul style="margin:0.3rem 0 0 1.2rem">';
      ag.misiones.forEach(m => {{
        const color = m.estado === 'completada' ? '#00ff99' : '#ffaa00';
        html += `<li style="color:${{color}}">${{m.titulo}} [${{m.prioridad}}] — ${{m.estado}} | 🎁 ${{m.recompensa || 10}} XP</li>`;
      }});
      html += '</ul>';
    }} else {{
      html += '<br><i style="color:#666">Sin misiones asignadas</i>';
    }}
    document.getElementById('detail-info').innerHTML = html;
    panel.classList.add('active');
  }}

  function closeDetail() {{
    document.getElementById('detail-panel').classList.remove('active');
  }}

  async function refreshOffice() {{
    try {{
      const res = await api('GET', '/agentes');
      agentes = res.data;

      // Fetch misiones for each agent in parallel
      const withMisiones = await Promise.all(agentes.map(async ag => {{
        const mr = await api('GET', '/misiones/' + encodeURIComponent(ag.nombre));
        ag.misiones = mr.data;
        return ag;
      }}));

      const classified = {{ trabajando: [], holgazaneando: [], recreandose: [] }};
      withMisiones.forEach(ag => {{
        classified[classifyAgent(ag, ag.misiones || [])].push(ag);
      }});

      placeAgents(classified);
    }} catch (e) {{
      toast('Error al cargar oficina', false);
    }}
  }}

  // ─── Form submissions ───
  async function submitCrearAgente() {{
    const nombre = document.getElementById('ca-nombre').value.trim();
    const rol = document.getElementById('ca-rol').value;
    const energia = parseInt(document.getElementById('ca-energia').value);
    if (!nombre) return toast('Nombre requerido', false);
    const r = await api('POST', '/agentes', {{ nombre, rol, energia }});
    if (r.status < 300) {{ toast('Agente creado', true); closeModal('crear-agente'); refreshOffice(); }}
    else toast(r.data.detail || 'Error', false);
  }}

  async function submitCrearMision() {{
    const titulo = document.getElementById('cm-titulo').value.trim();
    const descripcion = document.getElementById('cm-desc').value.trim();
    const agente_asignado = document.getElementById('cm-agente').value.trim();
    const energia_requerida = parseInt(document.getElementById('cm-energia').value);
    const recompensa = parseInt(document.getElementById('cm-recompensa').value);
    const prioridad = document.getElementById('cm-prioridad').value;
    if (!titulo || !agente_asignado) return toast('Título y agente requeridos', false);
    const r = await api('POST', '/misiones', {{ titulo, descripcion, agente_asignado, energia_requerida, recompensa, prioridad }});
    if (r.status < 300) {{ toast('Misión creada (#' + r.data.id + ')', true); closeModal('crear-mision'); refreshOffice(); }}
    else toast(r.data.detail || 'Error', false);
  }}

  async function submitEnviarMensaje() {{
    const remitente = document.getElementById('em-remitente').value.trim();
    const destinatario = document.getElementById('em-destinatario').value.trim();
    const contenido = document.getElementById('em-contenido').value.trim();
    if (!remitente || !destinatario || !contenido) return toast('Todos los campos son requeridos', false);
    const r = await api('POST', '/mensajes', {{ remitente, destinatario, contenido }});
    if (r.status < 300) {{ toast('Mensaje enviado', true); closeModal('enviar-mensaje'); }}
    else toast(r.data.detail || 'Error', false);
  }}

  async function submitCompletarMision() {{
    const id = parseInt(document.getElementById('comp-id').value);
    if (!id) return toast('ID requerido', false);
    const r = await api('POST', '/misiones/' + id + '/completar');
    if (r.status < 300) {{ toast('Misión completada', true); closeModal('completar-mision'); refreshOffice(); }}
    else toast(r.data.detail || 'Error', false);
  }}

  async function submitVerMisiones() {{
    const nombre = document.getElementById('vm-agente').value.trim();
    if (!nombre) return toast('Nombre requerido', false);
    const r = await api('GET', '/misiones/' + encodeURIComponent(nombre));
    const container = document.getElementById('vm-resultado');
    if (r.data.length === 0) {{ container.innerHTML = '<i>Sin misiones</i>'; return; }}
    container.innerHTML = r.data.map(m =>
      `<div style="padding:0.4rem 0;border-bottom:1px solid #222">
        <b>#${{m.id}}</b> ${{m.titulo}} — <span style="color:${{m.estado==='completada'?'#00ff99':'#ffaa00'}}">${{m.estado}}</span>
        [${{m.prioridad}}] | Energía: ${{m.energia_requerida}} | 🎁 ${{m.recompensa || 10}} XP
      </div>`
    ).join('');
  }}

  async function submitVerMensajes() {{
    const nombre = document.getElementById('vmsg-agente').value.trim();
    if (!nombre) return toast('Nombre requerido', false);
    const r = await api('GET', '/mensajes/' + encodeURIComponent(nombre));
    const container = document.getElementById('vmsg-resultado');
    if (r.data.length === 0) {{ container.innerHTML = '<i>Sin mensajes</i>'; return; }}
    container.innerHTML = r.data.map(m =>
      `<div style="padding:0.4rem 0;border-bottom:1px solid #222">
        <b>${{m.remitente}}</b>: ${{m.contenido}}
        <span style="color:#555;font-size:0.7rem"> ${{m.timestamp}}</span>
      </div>`
    ).join('');
  }}

  // ─── Init ───
  refreshOffice();

  async function submitVerBriefing() {{
    const nombre = document.getElementById('vb-agente').value.trim();
    if (!nombre) return toast('Nombre requerido', false);
    const container = document.getElementById('vb-resultado');
    container.innerHTML = '<i>Generando briefing...</i>';
    try {{
      const r = await api('GET', '/briefing/' + encodeURIComponent(nombre));
      if (r.status >= 400) {{ container.innerHTML = `<span style="color:#ff4444">${{r.data.detail || 'Error'}}</span>`; return; }}
      const b = r.data;
      let html = `
        <div style="border-bottom:1px solid #222;padding-bottom:0.5rem;margin-bottom:0.5rem">
          <b style="color:#00ff99">${{b.agente.nombre}}</b> — ${{b.agente.rol}} | Energía: ${{b.agente.energia}}
        </div>
        <div style="margin-bottom:0.5rem">
          📋 Misiones: <b>${{b.resumen_misiones.total}}</b> total |
          <span style="color:#ffaa00">${{b.resumen_misiones.pendientes}} pendientes</span> |
          <span style="color:#4dc9f6">${{b.resumen_misiones.en_curso || 0}} en curso</span> |
          <span style="color:#00ff99">${{b.resumen_misiones.completadas}} completadas</span>
        </div>
        <div style="background:#111;border:1px solid #333;border-radius:4px;padding:0.6rem;margin-bottom:0.4rem">
          🌐 <b>Inteligencia externa:</b>
          ${{b.tono ? `<span style="display:inline-block;background:#1a1a2e;border:1px solid #555;border-radius:3px;padding:0.1rem 0.4rem;font-size:0.7rem;margin-left:0.4rem;color:${{b.tono==='empático'?'#ffaa00':b.tono==='profesional'?'#4dc9f6':'#00ff99'}}">${{b.tono}}</span>` : ''}}<br>
          <i>${{b.inteligencia_externa}}</i>
        </div>
        <div style="font-size:0.7rem;color:#555;margin-bottom:0.6rem">Fuente: ${{b.fuente_externa}}</div>
      `;

      // ── Bloque de inteligencia de seguridad (Agente Smit) ──
      if (b.inteligencia_seguridad) {{
        const seg = b.inteligencia_seguridad;
        // SBOM escaneado
        const sbomHtml = seg.sbom.map(c =>
          `<span style="display:inline-block;background:#1a1a2e;border:1px solid ${{c.cves_encontrados > 0 ? '#ff4444' : '#333'}};border-radius:3px;padding:0.15rem 0.5rem;margin:0.15rem;font-size:0.75rem">`
          + `${{c.componente}} <span style="color:#888">v${{c.version}}</span>`
          + (c.cves_encontrados > 0 ? ` <span style="color:#ff4444;font-weight:bold">${{c.cves_encontrados}} CVE</span>` : ` <span style="color:#00ff99">✔</span>`)
          + `</span>`
        ).join('');

        // Alertas críticas
        let alertasHtml = '';
        if (seg.alertas_criticas && seg.alertas_criticas.length > 0) {{
          alertasHtml = `<div style="background:#2a1010;border:1px solid #ff4444;border-radius:4px;padding:0.5rem;margin-bottom:0.4rem">
            <b style="color:#ff4444">🚨 ${{seg.alertas_criticas.length}} alerta(s) CVSS ≥ 7.0</b>
            ${{seg.alertas_criticas.map(a => `<div style="font-size:0.78rem;padding:0.2rem 0;border-bottom:1px solid #331111">
              <b style="color:#ffaa00">${{a.id}}</b> (${{a.componente}}) — ${{a.severidad}} <span style="color:#ff4444">${{a.score}}</span>
              <div style="color:#aaa;font-size:0.72rem">${{a.descripcion.substring(0, 150)}}…</div>
            </div>`).join('')}}
          </div>`;
        }}

        // Vulnerabilidades recientes
        let vulnsHtml = '';
        if (seg.vulnerabilidades_recientes && seg.vulnerabilidades_recientes.length > 0) {{
          vulnsHtml = seg.vulnerabilidades_recientes.map(v =>
            `<div style="font-size:0.78rem;padding:0.3rem 0;border-bottom:1px solid #222">
              <b style="color:${{v.score >= 7 ? '#ff4444' : v.score >= 4 ? '#ffaa00' : '#00ff99'}}">${{v.id}}</b>
              <span style="color:#888">(${{v.componente}} — ${{v.fuente}})</span>
              <span style="float:right;color:${{v.score >= 7 ? '#ff4444' : '#ffaa00'}}">${{v.severidad}} ${{v.score}}</span>
              <div style="color:#aaa;font-size:0.72rem">${{v.descripcion.substring(0, 180)}}…</div>
            </div>`
          ).join('');
        }}

        // Recomendaciones
        const recsHtml = seg.recomendaciones.map(r =>
          `<div style="font-size:0.78rem;padding:0.15rem 0;color:#ccc">${{r}}</div>`
        ).join('');

        // Misiones analizadas + auto-completadas
        const misionesHtml = seg.misiones_analizadas
          ? seg.misiones_analizadas.map(m => `<span style="background:#1a2a1a;border:1px solid #00ff99;border-radius:3px;padding:0.1rem 0.4rem;margin:0.1rem;font-size:0.72rem;display:inline-block">🔍 ${{m}}</span>`).join('')
          : '';

        let autoCompHtml = '';
        if (seg.misiones_auto_completadas && seg.misiones_auto_completadas.length > 0) {{
          autoCompHtml = `<div style="background:#102a10;border:1px solid #00ff99;border-radius:4px;padding:0.5rem;margin-top:0.4rem">
            <b style="color:#00ff99;font-size:0.82rem">✅ Misiones completadas automáticamente (${{seg.misiones_auto_completadas.length}}):</b>
            ${{seg.misiones_auto_completadas.map(m => `<div style="font-size:0.78rem;color:#ccc;padding:0.1rem 0">  ✔ ${{m}}</div>`).join('')}}
          </div>`;
        }}
        if (seg.misiones_sin_energia && seg.misiones_sin_energia.length > 0) {{
          autoCompHtml += `<div style="background:#2a2a10;border:1px solid #ffaa00;border-radius:4px;padding:0.5rem;margin-top:0.4rem">
            <b style="color:#ffaa00;font-size:0.82rem">⚠️ Sin energía suficiente (${{seg.misiones_sin_energia.length}}):</b>
            ${{seg.misiones_sin_energia.map(m => `<div style="font-size:0.78rem;color:#ccc;padding:0.1rem 0">  ⚡ ${{m}}</div>`).join('')}}
          </div>`;
        }}

        html += `
          <div style="background:#0d1117;border:2px solid #ff4444;border-radius:6px;padding:0.7rem;margin-top:0.5rem">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
              <b style="color:#ff4444;font-size:1rem">🛡️ Inteligencia de Seguridad</b>
              <span style="font-size:0.72rem;color:${{seg.estado === 'activo' ? '#00ff99' : '#ffaa00'}}">${{seg.estado === 'activo' ? '● NVD activo' : '● Modo fallback'}}</span>
            </div>
            <div style="margin-bottom:0.5rem">
              <b style="color:#888;font-size:0.78rem">SBOM escaneado:</b><br>${{sbomHtml}}
            </div>
            ${{alertasHtml}}
            ${{vulnsHtml ? `<details style="margin-bottom:0.4rem"><summary style="color:#4dc9f6;cursor:pointer;font-size:0.82rem">📄 ${{seg.total_vulnerabilidades}} vulnerabilidad(es) encontrada(s)</summary><div style="max-height:200px;overflow-y:auto;margin-top:0.3rem">${{vulnsHtml}}</div></details>` : '<div style="color:#00ff99;font-size:0.82rem;margin-bottom:0.4rem">✅ Sin vulnerabilidades detectadas</div>'}}
            <details style="margin-bottom:0.4rem"><summary style="color:#ffaa00;cursor:pointer;font-size:0.82rem">💡 Recomendaciones (${{seg.recomendaciones.length}})</summary><div style="margin-top:0.3rem">${{recsHtml}}</div></details>
            ${{misionesHtml ? `<div style="margin-top:0.3rem"><b style="color:#888;font-size:0.72rem">Misiones analizadas:</b><br>${{misionesHtml}}</div>` : ''}}
            ${{autoCompHtml}}
            <div style="font-size:0.65rem;color:#444;margin-top:0.4rem">Fuentes: ${{seg.fuentes.join(' | ')}}</div>
          </div>
        `;
      }}

      // ── Bloque auto-completar misiones para agentes admin ──
      if (b.auto_completadas) {{
        const ac = b.auto_completadas;
        let adminAutoHtml = '';
        if (ac.misiones_completadas && ac.misiones_completadas.length > 0) {{
          adminAutoHtml += `<div style="margin-bottom:0.3rem">${{ac.misiones_completadas.map(t => `<span style="display:inline-block;background:#0a2a0a;border:1px solid #00ff99;border-radius:3px;padding:0.1rem 0.4rem;margin:0.1rem;font-size:0.75rem">✅ ${{t}}</span>`).join('')}}</div>`;
        }}
        if (ac.misiones_sin_energia && ac.misiones_sin_energia.length > 0) {{
          adminAutoHtml += `<div>${{ac.misiones_sin_energia.map(t => `<span style="display:inline-block;background:#2a1a0a;border:1px solid #ffaa00;border-radius:3px;padding:0.1rem 0.4rem;margin:0.1rem;font-size:0.75rem">⚠️ ${{t}}</span>`).join('')}}</div>`;
        }}
        html += `
          <div style="background:#0a1a0a;border:1px solid #00ff99;border-radius:4px;padding:0.6rem;margin-bottom:0.4rem">
            <b style="color:#00ff99">⚡ Auto-completar (${{ac.tipo_agente || 'AgenteAdmin'}})</b><br>
            <span style="font-size:0.75rem;color:#888">El agente admin ejecutó sus misiones pendientes al recibir el briefing.</span>
            <div style="margin-top:0.3rem">${{adminAutoHtml}}</div>
          </div>
        `;
      }}

      container.innerHTML = html;
      // Refrescar oficina si se completaron misiones (Smit o Admin)
      const smitAutoCompleted = b.inteligencia_seguridad && b.inteligencia_seguridad.misiones_auto_completadas && b.inteligencia_seguridad.misiones_auto_completadas.length > 0;
      const adminAutoCompleted = b.auto_completadas && b.auto_completadas.misiones_completadas && b.auto_completadas.misiones_completadas.length > 0;
      if (smitAutoCompleted || adminAutoCompleted) {{
        refreshOffice();
      }}
    }} catch (e) {{
      container.innerHTML = '<span style="color:#ff4444">Error de conexión</span>';
    }}
  }}

  async function cargarListaRecarga() {{
    const select = document.getElementById('ra-agente');
    const info = document.getElementById('ra-info');
    select.innerHTML = '<option value="">Cargando...</option>';
    info.innerHTML = '';
    try {{
      const r = await api('GET', '/agentes');
      if (!r.data || r.data.length === 0) {{ select.innerHTML = '<option value="">No hay agentes</option>'; return; }}
      select.innerHTML = '<option value="">(selecciona)</option>' + r.data.map(ag =>
        `<option value="${{ag.nombre}}">${{ag.nombre}} — ${{ag.rol}} | ⚡${{ag.energia}} | ⭐${{ag.experiencia || 0}} XP</option>`
      ).join('');
      select.onchange = () => {{
        const ag = r.data.find(a => a.nombre === select.value);
        if (ag) info.innerHTML = `Rol actual: <b>${{ag.rol}}</b> | Energía: <b>${{ag.energia}}</b> | XP: <b>${{ag.experiencia || 0}}</b>`;
        else info.innerHTML = '';
      }};
    }} catch (e) {{
      select.innerHTML = '<option value="">Error cargando</option>';
    }}
  }}

  async function submitRecargarAgente() {{
    const nombre = document.getElementById('ra-agente').value;
    if (!nombre) return toast('Selecciona un agente', false);
    const rol = document.getElementById('ra-rol').value || null;
    const energiaVal = document.getElementById('ra-energia').value;
    const energia = energiaVal ? parseInt(energiaVal) : null;
    if (!rol && !energia) return toast('Indica rol o energía a cambiar', false);
    const body = {{}};
    if (rol) body.rol = rol;
    if (energia) body.energia = energia;
    const r = await api('PUT', '/agentes/' + encodeURIComponent(nombre), body);
    if (r.status < 300) {{
      toast('Agente ' + nombre + ' recargado', true);
      closeModal('recargar-agente');
      refreshOffice();
    }} else {{
      toast(r.data.detail || 'Error', false);
    }}
  }}

  async function cargarListaEliminacion() {{
    const container = document.getElementById('ea-lista');
    container.innerHTML = '<i style="color:#666">Cargando agentes...</i>';
    try {{
      const r = await api('GET', '/agentes');
      if (!r.data || r.data.length === 0) {{ container.innerHTML = '<i>No hay agentes</i>'; return; }}
      const checks = await Promise.all(r.data.map(async ag => {{
        const estado = await api('GET', '/agentes/' + encodeURIComponent(ag.nombre) + '/estado-eliminacion');
        return {{ ...ag, ...estado.data }};
      }}));
      container.innerHTML = checks.map(ag => {{
        const icon = ICONS[ag.rol] || '🤖';
        if (!ag.puede_eliminar) {{
          const lista = ag.misiones_activas.map(m => m.titulo).join(', ');
          return `<div style="padding:0.5rem;margin-bottom:0.4rem;background:#1a1a2e;border:1px solid #333;border-radius:4px;display:flex;justify-content:space-between;align-items:center">
            <span>${{icon}} <b>${{ag.nombre}}</b> <span style="color:#888">${{ag.rol}}</span></span>
            <span style="color:#ff4444;font-size:0.75rem" title="${{lista}}">🔒 Con misiones activas</span>
          </div>`;
        }}
        return `<div style="padding:0.5rem;margin-bottom:0.4rem;background:#1a1a2e;border:1px solid #333;border-radius:4px;display:flex;justify-content:space-between;align-items:center">
          <span>${{icon}} <b>${{ag.nombre}}</b> <span style="color:#888">${{ag.rol}} | ⚡${{ag.energia}}</span></span>
          <button class="btn btn-cancel" style="padding:0.2rem 0.6rem;font-size:0.75rem" onclick="confirmarEliminar('${{ag.nombre}}')">🗑️ Eliminar</button>
        </div>`;
      }}).join('');
    }} catch (e) {{
      container.innerHTML = '<span style="color:#ff4444">Error cargando agentes</span>';
    }}
  }}

  async function confirmarEliminar(nombre) {{
    if (!confirm('¿Eliminar a ' + nombre + '? Se borrarán también sus mensajes y misiones completadas.')) return;
    const r = await api('DELETE', '/agentes/' + encodeURIComponent(nombre));
    if (r.status < 300) {{
      toast('Agente ' + nombre + ' eliminado', true);
      cargarListaEliminacion();
      refreshOffice();
    }} else {{
      toast(r.data.detail || 'Error al eliminar', false);
    }}
  }}
</script>

</body>
</html>
"""
