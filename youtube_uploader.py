"""
Módulo de Subida Automática a YouTube Shorts.
Usa YouTube Data API v3 con autenticación silenciosa por variables de entorno
(sin abrir navegador) para que funcione en GitHub Actions en la nube.

Variables de entorno requeridas:
  YT_CLIENT_ID      → Client ID de OAuth 2.0 (Google Cloud Console)
  YT_CLIENT_SECRET  → Client Secret de OAuth 2.0
  YT_REFRESH_TOKEN  → Refresh Token obtenido una vez con get_yt_token.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from config import OUTPUT_DIR

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
YT_TOKEN_URL = "https://oauth2.googleapis.com/token"
YT_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

# Categorías de YouTube (10 = Music, 22 = People & Blogs, 24 = Entertainment, 28 = Science & Technology)
YT_CATEGORY_ENTERTAINMENT = "24"

HASHTAG_POOL = [
    "#Shorts",
    "#Misterios",
    "#Supervivencia",
    "#Curiosidades",
    "#Ciencia",
    "#DonZombi",
    "#BrunoSchiller",
    "#Viral",
    "#Reels",
]


# ---------------------------------------------------------------------------
# Helpers de OAuth 2.0 silencioso (sin navegador)
# ---------------------------------------------------------------------------
def _build_credentials():
    """
    Construye credenciales OAuth2 usando el refresh_token almacenado en
    variables de entorno. No abre ningún navegador.
    Retorna un objeto google.oauth2.credentials.Credentials listo para usar.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
    except ImportError:
        raise ImportError(
            "Instala google-auth y google-auth-oauthlib:\n"
            "  pip install google-auth google-auth-oauthlib google-api-python-client"
        )

    client_id = os.getenv("YT_CLIENT_ID", "")
    client_secret = os.getenv("YT_CLIENT_SECRET", "")
    refresh_token = os.getenv("YT_REFRESH_TOKEN", "")

    if not all([client_id, client_secret, refresh_token]):
        raise EnvironmentError(
            "Faltan variables de entorno para YouTube:\n"
            "  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN\n"
            "Genera el refresh token una sola vez con: python get_yt_token.py"
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=YT_TOKEN_URL,
        client_id=client_id,
        client_secret=client_secret,
        scopes=[YT_UPLOAD_SCOPE],
    )
    # Refrescar el access token automáticamente
    creds.refresh(Request())
    return creds


def _build_youtube_client():
    """Retorna un cliente autenticado de la YouTube Data API v3."""
    try:
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "Instala google-api-python-client:\n  pip install google-api-python-client"
        )
    creds = _build_credentials()
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


# ---------------------------------------------------------------------------
# Título y descripción optimizados para YouTube Shorts
# ---------------------------------------------------------------------------
def _build_title(topic: str, theme: str = "") -> str:
    """
    Genera un título optimizado para YouTube Shorts.
    Máximo 100 caracteres. Siempre incluye #Shorts al final.
    """
    emoji_map = {
        "ocean": "🌊",
        "space": "🌌",
        "blackout": "⚡",
        "prehistory": "🦕",
        "island": "🏝️",
        "jungle": "🌿",
        "zombie": "⚠️",
    }
    emoji = emoji_map.get(theme, "🔍")
    raw = f"{emoji} {topic.strip()}"
    max_len = 97  # reservar espacio para " #S" si es que hace falta
    if len(raw) > max_len:
        raw = raw[:max_len].rsplit(" ", 1)[0] + "…"
    return raw


def _build_description(topic: str, script_text: str, theme: str = "") -> str:
    """
    Genera una descripción optimizada para YouTube Shorts:
    gancho, primeras 3 líneas del guion resumidas, pregunta de debate y hashtags.
    """
    theme_tags = {
        "ocean": ["#FosaDeMariana", "#OceanoMisterioso", "#SinFondo"],
        "space": ["#TormentaSolar", "#Carrington", "#SatelitesCaidos"],
        "blackout": ["#ApagonGlobal", "#SinElectricidad", "#Supervivencia72h"],
        "prehistory": ["#Prehistoria", "#Dinosaurios", "#ViajeroDelTiempo"],
        "island": ["#IslaProhibida", "#Naufrago", "#Bunker"],
        "jungle": ["#Amazonas", "#SelvaInexplorada", "#LiDAR"],
        "zombie": ["#Evacuacion", "#ApocalipsisZombi", "#Plan72h"],
    }
    tags = " ".join(HASHTAG_POOL[:5] + theme_tags.get(theme, [])[:3])

    # Tomar las primeras ~180 palabras del guion como resumen
    words = script_text.split()
    snippet = " ".join(words[:50]) + ("…" if len(words) > 50 else "")

    desc = (
        f"{topic.strip()}\n\n"
        f"{snippet}\n\n"
        "▶ Mira todos los capítulos hasta el final — el último dato lo cambia todo.\n"
        f"👇 ¿Tú qué harías? Déjalo en los comentarios.\n\n"
        f"Bruno Schiller | Misterios y Supervivencia\n\n"
        f"{tags}"
    )
    return desc


# ---------------------------------------------------------------------------
# Subida principal
# ---------------------------------------------------------------------------
def upload_to_youtube_shorts(
    video_path: Path,
    topic: str,
    script_text: str = "",
    theme: str = "",
    privacy: str = "public",
) -> Optional[str]:
    """
    Sube un video como YouTube Short (formato vertical 9:16, hasta 3 min).

    Args:
        video_path:   Ruta local al archivo .mp4 renderizado.
        topic:        Tema del video (para el título).
        script_text:  Guion narrado (para la descripción).
        theme:        Temática ('ocean', 'space', 'blackout', etc.).
        privacy:      'public' | 'private' | 'unlisted'.

    Returns:
        URL del video de YouTube si tuvo éxito, None si falló.
    """
    print(f"\n[YouTube Shorts] Subiendo video: {video_path.name}")
    print(f"                  Tema: {topic}")
    print(f"                  Privacidad: {privacy}")

    if not video_path.exists():
        print(f"[YouTube Shorts] ERROR: El archivo de video no existe en {video_path}")
        return None

    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print(
            "[YouTube Shorts] ERROR: google-api-python-client no instalado.\n"
            "  Ejecuta: pip install google-api-python-client google-auth google-auth-oauthlib"
        )
        return None

    title = _build_title(topic, theme)
    description = _build_description(topic, script_text, theme)
    tags = [t.lstrip("#") for t in (HASHTAG_POOL + ["BrunoSchiller", "MisteriosYSupervivencia"])]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags[:30],  # YT acepta hasta 500 caracteres en tags, máximo ~30 tags
            "categoryId": YT_CATEGORY_ENTERTAINMENT,
            "defaultLanguage": "es",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    try:
        youtube = _build_youtube_client()

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=5 * 1024 * 1024,  # chunks de 5 MB
        )

        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"[YouTube Shorts] Subiendo… {pct}%", end="\r", flush=True)

        video_id = response.get("id", "")
        url = f"https://www.youtube.com/shorts/{video_id}"
        print(f"\n[YouTube Shorts] ✅ ¡Publicado con éxito!")
        print(f"                  URL: {url}")
        print(f"                  Título: {title}")

        # Guardar historial de subidas
        history_path = OUTPUT_DIR / "youtube_upload_history.json"
        history = []
        if history_path.exists():
            try:
                history = json.loads(history_path.read_text(encoding="utf-8"))
            except Exception:
                history = []
        history.append({
            "video_id": video_id,
            "url": url,
            "title": title,
            "topic": topic,
            "theme": theme,
            "privacy": privacy,
        })
        history_path.write_text(json.dumps(history[-30:], ensure_ascii=False, indent=2), encoding="utf-8")

        return url

    except EnvironmentError as e:
        print(f"[YouTube Shorts] ⚠️  Configuración incompleta: {e}")
        return None
    except Exception as e:
        print(f"[YouTube Shorts] ❌ Error al subir: {e}")
        return None
