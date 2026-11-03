"""
Script de Una Sola Ejecución para Obtener el YT_REFRESH_TOKEN.

Ejecútalo UNA SOLA VEZ en tu computadora local:
  python get_yt_token.py

Abrirá tu navegador para que inicies sesión en tu cuenta de YouTube (Bruno Schiller).
Al autorizar, imprimirá el REFRESH_TOKEN en consola.

Luego ve a GitHub → Settings → Secrets → Actions y crea los secretos:
  YT_CLIENT_ID      = <tu Client ID>
  YT_CLIENT_SECRET  = <tu Client Secret>
  YT_REFRESH_TOKEN  = <el token que imprimió este script>

REQUISITOS PREVIOS EN GOOGLE CLOUD:
  1. Ir a console.cloud.google.com
  2. Crear proyecto nuevo → Activar "YouTube Data API v3"
  3. Pantalla de consentimiento OAuth → Externo → Agregar tu correo como Usuario de prueba
  4. Credenciales → Crear ID de cliente OAuth 2.0 → Tipo: "Aplicación de escritorio"
  5. Descargar el JSON del cliente y copiar Client ID y Client Secret aquí abajo,
     o definir como variables de entorno YT_CLIENT_ID / YT_CLIENT_SECRET.
"""

import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import requests

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
# Puedes poner tus valores aquí o definirlos como variables de entorno antes de correr
CLIENT_ID = os.getenv("YT_CLIENT_ID", "PEGA_AQUI_TU_CLIENT_ID")
CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "PEGA_AQUI_TU_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
# ──────────────────────────────────────────────────────────────────────────────

auth_code_holder = {"code": None}


class _OAuthHandler(BaseHTTPRequestHandler):
    """Servidor HTTP temporal de un solo uso para capturar el código de OAuth."""

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if "code" in params:
            auth_code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Autorizado. Puedes cerrar esta ventana.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>Error: no se recibio el codigo.</h1>")

    def log_message(self, *args):  # silenciar logs del servidor HTTP
        pass


def main():
    if CLIENT_ID.startswith("PEGA_AQUI"):
        print("❌ Edita get_yt_token.py y pon tu Client ID y Client Secret antes de correrlo.")
        return

    # Construir URL de autorización
    params = (
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPE}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    auth_full_url = AUTH_URL + params

    print("=" * 65)
    print("  OBTENCIÓN DE REFRESH TOKEN DE YOUTUBE (Una sola vez)")
    print("=" * 65)
    print(f"\n1. Abriendo tu navegador para autorizar...")
    webbrowser.open(auth_full_url)
    print(f"   Si no se abre, ve a:\n   {auth_full_url}\n")

    # Iniciar servidor HTTP temporal en puerto 8080
    print("2. Esperando que apruebes el acceso en el navegador...")
    server = HTTPServer(("localhost", 8080), _OAuthHandler)
    server.handle_request()  # atiende exactamente UNA petición y cierra

    code = auth_code_holder.get("code")
    if not code:
        print("❌ No se capturó el código de autorización.")
        return

    # Intercambiar código por tokens
    print("\n3. Intercambiando código por tokens...")
    resp = requests.post(
        TOKEN_URL,
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )

    if resp.status_code != 200:
        print(f"❌ Error al obtener tokens: {resp.status_code} — {resp.text}")
        return

    tokens = resp.json()
    refresh_token = tokens.get("refresh_token", "")

    if not refresh_token:
        print("❌ No se recibió refresh_token. Asegúrate de que la pantalla de consentimiento")
        print("   está configurada como 'Externo' y tu correo está en 'Usuarios de prueba'.")
        return

    print("\n" + "=" * 65)
    print("✅ ¡Refresh Token obtenido con éxito!")
    print("=" * 65)
    print(f"\nYT_CLIENT_ID     = {CLIENT_ID}")
    print(f"YT_CLIENT_SECRET = {CLIENT_SECRET}")
    print(f"YT_REFRESH_TOKEN = {refresh_token}")
    print("\n📋 PASOS SIGUIENTES:")
    print("  1. Ve a tu repo en GitHub → Settings → Secrets and variables → Actions")
    print("  2. Crea los siguientes 'Repository secrets':")
    print(f"       YT_CLIENT_ID     → {CLIENT_ID}")
    print(f"       YT_CLIENT_SECRET → {CLIENT_SECRET}")
    print(f"       YT_REFRESH_TOKEN → {refresh_token}")
    print("  3. ¡Listo! El workflow video_diario.yml subirá videos automáticamente.")
    print("=" * 65)


if __name__ == "__main__":
    main()
