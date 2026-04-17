# -----------------------------------------------------------#
## Template HTML del formulario de login
# -----------------------------------------------------------#
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>La Agencia — Login</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', sans-serif;
      background: #0d0d0d;
      color: #e0e0e0;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }}
    .card {{
      background: #1a1a1a;
      border: 1px solid #333;
      border-radius: 8px;
      padding: 2.5rem 2rem;
      width: 360px;
      box-shadow: 0 0 30px rgba(0,255,150,0.05);
    }}
    h1 {{ font-size: 1.4rem; margin-bottom: 0.3rem; color: #00ff99; }}
    p.sub {{ font-size: 0.8rem; color: #666; margin-bottom: 1.8rem; }}
    label {{ display: block; font-size: 0.8rem; color: #888; margin-bottom: 0.3rem; }}
    input {{
      width: 100%; padding: 0.65rem 0.9rem;
      background: #111; border: 1px solid #333;
      border-radius: 4px; color: #e0e0e0;
      font-size: 0.95rem; margin-bottom: 1.1rem;
    }}
    input:focus {{ outline: none; border-color: #00ff99; }}
    button {{
      width: 100%; padding: 0.7rem;
      background: #00ff99; color: #000;
      border: none; border-radius: 4px;
      font-size: 1rem; font-weight: 600;
      cursor: pointer; transition: opacity .2s;
    }}
    button:hover {{ opacity: 0.85; }}
    .msg {{
      margin-top: 1.2rem; padding: 0.7rem 1rem;
      border-radius: 4px; font-size: 0.9rem;
    }}
    .ok  {{ background:#003320; border:1px solid #00ff99; color:#00ff99; }}
    .err {{ background:#330000; border:1px solid #ff4444; color:#ff4444; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>🕶️ La Agencia</h1>
    <p class="sub">Ingresa tus credenciales de operador</p>
    <form method="post" action="/login">
      <label for="user">Usuario</label>
      <input id="user" name="user" type="text" placeholder="admin" required autofocus>
      <label for="password">Contraseña</label>
      <input id="password" name="password" type="password" placeholder="••••••••" required>
      <button type="submit">Acceder</button>
    </form>
    {mensaje}
  </div>
</body>
</html>
"""
