import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "assets" / "images"
OUTPUT_DIR = BASE_DIR / "output"
BROWSER_PROFILE_DIR = BASE_DIR / "browser_profile"

# Crear directorios automÃ¡ticamente si no existen
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# ConfiguraciÃ³n de Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.8-flash"

# ConfiguraciÃ³n de Voz y SubtÃ­tulos
TTS_VOICE = os.getenv("TTS_VOICE", "es-MX-JorgeNeural")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# ResoluciÃ³n de video (Formato Vertical 9:16 para Facebook Reels / Videos)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 12

# ConfiguraciÃ³n de Facebook
FB_EMAIL = os.getenv("FB_EMAIL", "")
FB_PASSWORD = os.getenv("FB_PASSWORD", "")
FB_PAGE_NAME = os.getenv("FB_PAGE_NAME", "ERPA VARDE")

