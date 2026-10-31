"""
Configurador automático de GitHub Actions en la Nube (24/7 Sin PC)
para controlar y ejecutar la creación diaria de videos desde el Xiaomi Redmi Note 10S.
"""

import base64
import json
import subprocess
from pathlib import Path
import requests

from config import FB_EMAIL, FB_PASSWORD, GEMINI_API_KEY, OUTPUT_DIR
from uploader import _create_driver, _ensure_logged_in


def export_active_fb_cookies() -> str:
    cookies_file = OUTPUT_DIR / "fb_cookies.b64"
    if cookies_file.exists() and cookies_file.stat().st_size > 20:
        return cookies_file.read_text(encoding="utf-8").strip()

    print("[1/4] Exportando cookies de sesión activa de Facebook desde el perfil local...")
    driver = _create_driver(headless=True)
    try:
        _ensure_logged_in(driver)
    finally:
        driver.quit()

    if cookies_file.exists():
        return cookies_file.read_text(encoding="utf-8").strip()
    return ""


def get_git_github_token() -> tuple[str, str]:
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        text=True,
        capture_output=True,
        check=True,
    )
    user = ""
    token = ""
    for line in proc.stdout.splitlines():
        if line.startswith("username="):
            user = line.split("=", 1)[1].strip()
        elif line.startswith("password="):
            token = line.split("=", 1)[1].strip()
    return user, token


def encrypt_github_secret(public_key_b64: str, secret_value: str) -> str:
    from nacl import encoding, public

    public_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def setup_cloud_repo() -> None:
    cookies_b64 = export_active_fb_cookies()
    user, token = get_git_github_token()
    if not token:
        raise RuntimeError("No se encontró token de GitHub en git credential helper.")

    repo_name = "fb-video-automation"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    print(f"[2/4] Creando o verificando repositorio en GitHub: {user}/{repo_name}...")
    r_check = requests.get(f"https://api.github.com/repos/{user}/{repo_name}", headers=headers, timeout=15)
    if r_check.status_code == 404:
        r_create = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json={
                "name": repo_name,
                "description": "Automatización 24/7 de Videos Animados para Facebook Reels (Control móvil desde Xiaomi Redmi Note 10S)",
                "private": True,
                "auto_init": False,
            },
            timeout=15,
        )
        if r_create.status_code not in (200, 201):
            # Si el token tiene alcance public_repo únicamente, crear público sin credenciales expuestas (.gitignore protege .env)
            r_create = requests.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json={
                    "name": repo_name,
                    "description": "Automatización 24/7 de Videos Animados para Facebook Reels",
                    "private": False,
                    "auto_init": False,
                },
                timeout=15,
            )
            r_create.raise_for_status()
        print(f"      Repositorio creado: https://github.com/{user}/{repo_name}")
    else:
        print(f"      Repositorio existente detectado: https://github.com/{user}/{repo_name}")

    # Obtener llave pública para cifrar GitHub Actions Secrets
    print("[3/4] Cifrando y subiendo secretos (GEMINI_API_KEY, FB_EMAIL, FB_PASSWORD, FB_COOKIES_B64) a GitHub Actions...")
    r_pk = requests.get(
        f"https://api.github.com/repos/{user}/{repo_name}/actions/secrets/public-key",
        headers=headers,
        timeout=15,
    )
    if r_pk.status_code == 200:
        pk_data = r_pk.json()
        key_id = pk_data["key_id"]
        pub_key = pk_data["key"]

        secrets_map = {
            "GEMINI_API_KEY": GEMINI_API_KEY,
            "FB_EMAIL": FB_EMAIL,
            "FB_PASSWORD": FB_PASSWORD,
            "FB_COOKIES_B64": cookies_b64,
        }
        for s_name, s_val in secrets_map.items():
            if not s_val:
                continue
            enc_val = encrypt_github_secret(pub_key, s_val)
            r_sec = requests.put(
                f"https://api.github.com/repos/{user}/{repo_name}/actions/secrets/{s_name}",
                headers=headers,
                json={"encrypted_value": enc_val, "key_id": key_id},
                timeout=15,
            )
            if r_sec.status_code in (201, 204):
                print(f"      Secreto '{s_name}' guardado en la nube.")
    else:
        print(f"      Nota al consultar public-key de Actions: {r_pk.status_code}")

    print("[4/4] Subiendo código y workflow '.github/workflows/video_diario.yml' a GitHub...")
    gitignore_content = (
        ".venv/\n"
        "__pycache__/\n"
        "browser_profile/\n"
        ".env\n"
        "output/*.mp4\n"
        "output/*.b64\n"
        "output/*.wav\n"
        "output/*.mp3\n"
        "output/sub_frames/\n"
        "output/processed_frames/\n"
        "output/sitcom_audio*/\n"
        "output/sketch_*_audio/\n"
        "output/yt_*/\n"
        "output/.bin/\n"
    )
    Path(".gitignore").write_text(gitignore_content, encoding="utf-8")

    cmds = [
        ["git", "init"],
        ["git", "branch", "-M", "main"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Activar motor 24 FPS estilo Don Zombi / Curiosamente Graficado + GitHub Actions 24/7"],
    ]
    for c in cmds:
        subprocess.run(c, check=False)

    remote_url = f"https://github.com/{user}/{repo_name}.git"
    subprocess.run(["git", "remote", "remove", "origin"], check=False)
    subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check=True)
    print(f"\n¡ÉXITO TOTAL! Tu sistema ya está en la nube en: https://github.com/{user}/{repo_name}/actions")


if __name__ == "__main__":
    setup_cloud_repo()
