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
      position: absolute;
      width: 52px;
      text-align: center;
      cursor: default;
      transition: transform 0.15s;
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
      </div>

      <div class="sep"></div>
      <h2>Consultas</h2>
      <button onclick="openModal('ver-misiones')">🔍 Misiones de agente</button>
      <button onclick="openModal('ver-mensajes')">📨 Mensajes de agente</button>
    </div>

    <!-- ── Office ── -->
    <div class="office" id="office">
      <div class="zone zone-trabajando">
        <span class="zone-label">💼 Trabajando</span>
        <div id="zone-trabajando-agents" style="position:relative;flex:1;"></div>
      </div>
      <div class="zone zone-holgazaneando">
        <span class="zone-label">😴 Holgazaneando</span>
        <div id="zone-holgazaneando-agents" style="position:relative;flex:1;"></div>
      </div>
      <div class="zone zone-recreandose">
        <span class="zone-label">🎮 Recreándose</span>
        <div id="zone-recreandose-agents" style="position:relative;flex:1;"></div>
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
        <option value="espía">Espía</option>
        <option value="analista">Analista</option>
        <option value="guardián">Guardián</option>
        <option value="admin">Admin</option>
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

  <!-- Toast -->
  <div class="toast" id="toast"></div>

<script>
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
  }}
  function closeModal(name) {{
    document.getElementById('modal-' + name).classList.remove('active');
  }}

  // ─── API helpers ───
  async function api(method, path, body) {{
    const opts = {{ method, headers: {{ 'Content-Type': 'application/json' }} }};
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch('/api' + path, opts);
    return {{ status: res.status, data: await res.json() }};
  }}

  // ─── Office rendering ───
  const ICONS = {{ 'espía': '🕵️', 'analista': '📊', 'guardián': '🛡️', 'admin': '👔' }};

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
          left: ${{10 + (i % 5) * 18}}%;
          top: ${{10 + Math.floor(i / 5) * 40}}%;
          --wander-duration: ${{dur}}s;
          animation-delay: ${{delay}}s;
        `;
        el.onclick = () => showDetail(ag);
        el.innerHTML = `
          <div class="agent-icon">${{ICONS[ag.rol] || '🤖'}}</div>
          <div class="agent-name">${{ag.nombre}}</div>
          <div class="agent-bar"><div class="agent-bar-fill" style="width:${{ag.energia}}%;background:${{energyColor(ag.energia)}}"></div></div>
        `;
        container.appendChild(el);
      }});
    }});
  }}

  function showDetail(ag) {{
    const panel = document.getElementById('detail-panel');
    document.getElementById('detail-name').textContent = (ICONS[ag.rol] || '🤖') + ' ' + ag.nombre;
    let html = `<b>Rol:</b> ${{ag.rol}} &nbsp; <b>Energía:</b> ${{ag.energia}}/100`;
    if (ag.misiones && ag.misiones.length > 0) {{
      html += '<br><b>Misiones:</b><ul style="margin:0.3rem 0 0 1.2rem">';
      ag.misiones.forEach(m => {{
        const color = m.estado === 'completada' ? '#00ff99' : '#ffaa00';
        html += `<li style="color:${{color}}">${{m.titulo}} [${{m.prioridad}}] — ${{m.estado}}</li>`;
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
    const prioridad = document.getElementById('cm-prioridad').value;
    if (!titulo || !agente_asignado) return toast('Título y agente requeridos', false);
    const r = await api('POST', '/misiones', {{ titulo, descripcion, agente_asignado, energia_requerida, prioridad }});
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
    const r = await api('PUT', '/misiones/' + id + '/completar');
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
        [${{m.prioridad}}] | Energía: ${{m.energia_requerida}}
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
</script>

</body>
</html>
"""
