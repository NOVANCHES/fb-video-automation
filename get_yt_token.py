"""
Script de Una Sola Ejecución para Obtener el YT_REFRESH_TOKEN.
Lee las credenciales desde tu archivo .env local para evitar exponer secretos en git.
"""

import os
from pathlib import Path
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

CLIENT_ID = os.getenv("YT_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8080"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

auth_code_holder = {"code": None, "error": None}


class _OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if "code" in params:
            auth_code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body style='font-family:sans-serif;text-align:center;padding:50px;background:#f5f5f5;'>"
                b"<h1 style='color:#2e7d32;'>&#161;Autorizado con exito!</h1>"
                b"<p style='font-size:18px;'>El script ha capturado tu token. Ya puedes cerrar esta ventana.</p>"
                b"</body></html>"
            )
        elif "error" in params:
            auth_code_holder["error"] = params["error"][0]
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            err_msg = params["error"][0]
            self.wfile.write(f"<h1>Error de autorizacion: {err_msg}</h1>".encode("utf-8"))
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, *args):
        pass


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("[ERROR] Asegúrate de que YT_CLIENT_ID y YT_CLIENT_SECRET están definidos en tu archivo .env")
        return

    auth_link = (
        f"{AUTH_URL}?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPE}"
        f"&access_type=offline"
        f"&prompt=consent"
    )

    print("=" * 65)
    print("  AUTORIZACION DE YOUTUBE PARA BRUNO SCHILLER")
    print("=" * 65)
    print("\n1. Abriendo tu navegador...")
    webbrowser.open(auth_link)
    print(f"\nSi no se abrio automaticamente, abre este enlace:\n{auth_link}\n")

    print("2. Servidor local escuchando en el puerto 8080...")
    server = HTTPServer(("localhost", 8080), _OAuthHandler)

    while auth_code_holder["code"] is None and auth_code_holder["error"] is None:
        server.handle_request()

    if auth_code_holder["error"]:
        print(f"\n[ERROR] Recibido desde Google: {auth_code_holder['error']}")
        return

    code = auth_code_holder["code"]
    print("\n[OK] Codigo de autorizacion recibido. Intercambiando por Refresh Token...")

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
        print(f"[ERROR] Al obtener tokens ({resp.status_code}): {resp.text}")
        return

    tokens = resp.json()
    refresh_token = tokens.get("refresh_token")

    if not refresh_token:
        print("\n[AVISO] No se recibio refresh_token en la respuesta:")
        print(tokens)
        return

    print("\n" + "=" * 65)
    print("[EXITO] REFRESH TOKEN OBTENIDO CON EXITO")
    print("=" * 65)
    print(f"\nYT_CLIENT_ID     = {CLIENT_ID}")
    print(f"YT_CLIENT_SECRET = {CLIENT_SECRET}")
    print(f"YT_REFRESH_TOKEN = {refresh_token}")

    env_path = Path(".env")
    env_content = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    lines = [
        l for l in env_content.splitlines()
        if not l.startswith(("YT_CLIENT_ID=", "YT_CLIENT_SECRET=", "YT_REFRESH_TOKEN="))
    ]
    lines.extend([
        "",
        "# Credenciales de YouTube Data API v3",
        f"YT_CLIENT_ID={CLIENT_ID}",
        f"YT_CLIENT_SECRET={CLIENT_SECRET}",
        f"YT_REFRESH_TOKEN={refresh_token}",
    ])
    env_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print("\n[OK] Credenciales guardadas en .env local.")

    out_json = Path("output/yt_tokens.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        f'{{\n  "YT_CLIENT_ID": "{CLIENT_ID}",\n  "YT_CLIENT_SECRET": "{CLIENT_SECRET}",\n  "YT_REFRESH_TOKEN": "{refresh_token}"\n}}\n',
        encoding="utf-8",
    )
    print("[OK] Copia de seguridad guardada en output/yt_tokens.json.")


if __name__ == "__main__":
    main()
