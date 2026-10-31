import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "assets" / "images"
OUTPUT_DIR = BASE_DIR / "output"
BROWSER_PROFILE_DIR = BASE_DIR / "browser_profile"

# Crear directorios automáticamente si no existen
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# Configuración de Voz y Subtítulos
TTS_VOICE = os.getenv("TTS_VOICE", "es-MX-JorgeNeural")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Resolución de video (Formato Vertical 9:16 para Facebook Reels / Videos)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 24

# Configuración de Facebook (vacío = publicar directamente en el perfil de creador principal Bruno Schiller)
FB_EMAIL = os.getenv("FB_EMAIL", "")
FB_PASSWORD = os.getenv("FB_PASSWORD", "")
FB_PAGE_NAME = os.getenv("FB_PAGE_NAME", "")
