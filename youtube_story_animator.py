"""
Motor de Animación Narrativa de Formato Largo (60-85s) Estilo YouTube / Reels Virales
("Don Zombi", "Curiosamente Graficado", "Sobrevive con Bruno" y "Sebastián Schiller") a 24 FPS continuos.

Directrices Técnicas Implementadas:
  1. Coherencia Contextual Estricta (Imagen-Texto):
     - Registro aislado de ilustraciones 2D por temática (CERO zombis en el espacio u océano).
     - Validación semántica previa antes de renderizar cada escena extrayendo entidades del guion.
  2. Optimización de Retención (Estilo Trends de IA / Reels Virales):
     - Cadencia dinámica visual cada 2.5 segundos:
       * Reencuadres y micro-punches de cámara continuos a 24 FPS.
       * Telemetría HUD interactiva sincronizada con la frase exacta narrada en ese segundo.
       * Transiciones fluidas de poses y estados del personaje 2D cada 2.5s.
       * Subtítulos cinéticos tipo karaoke con efecto pop de alta retención.
  3. Variabilidad de Voces Neuronales (Edge-TTS A/B Testing):
     - Integración con voice_manager.py para alternar entre 6 locutores de América Latina
       con micro-variación de tono y velocidad para medir qué voz retiene más audiencia.
"""

import asyncio
from datetime import datetime
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import wave

import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

from config import OUTPUT_DIR, VIDEO_HEIGHT, VIDEO_WIDTH
from voice_manager import select_voice_profile

try:
    from moviepy import AudioFileClip, CompositeAudioClip, VideoClip
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import AudioFileClip, CompositeAudioClip, VideoClip
    MOVIEPY_V2 = False

FPS_SMOOTH = 24
_FONT_CACHE: Dict[Tuple[int, bool], Any] = {}

# ==============================================================================
# 1. CATÁLOGO AISLADO DE ILUSTRACIONES 2D (CERO CONTAMINACIÓN CRUZADA)
# ==============================================================================
THEME_ASSET_REGISTRY: Dict[str, List[str]] = {
    "ocean": ["marianas_1.png", "marianas_2.png"],
    "space": ["espacio_1.png", "espacio_2.png"],
    "blackout": ["apagon_1.png", "apagon_2.png"],
    "prehistory": ["prehistoria_1.png", "prehistoria_2.png"],
    "island": ["isla_1.png", "isla_2.png"],
    "jungle": ["selva_1.png", "selva_2.png"],
    "zombie": ["zombi_1.png", "zombi_2.png", "zombi_3.png"],
}

THEME_KEYWORDS: Dict[str, List[str]] = {
    "space": ["solar", "carrington", "satélite", "satelite", "gps", "espacio", "órbita", "orbita", "aurora", "geomagnética", "geomagnetica", "nasa", "sol", "cme", "transformador"],
    "ocean": ["fosa", "marianas", "océano", "oceano", "mar", "marino", "submarino", "abismo", "profundidad", "metros", "bioluminiscente", "presión", "presion", "peces", "titanio"],
    "blackout": ["apagón", "apagon", "electricidad", "red eléctrica", "red electrica", "transformador", "sin luz", "energía", "energia", "generador", "bomba", "cajeros", "semáforo"],
    "prehistory": ["prehistoria", "dinosaurio", "eras", "jurásico", "jurasico", "devónico", "devonico", "carbonífero", "carbonifero", "cretácico", "cretacico", "asteroide", "fósil", "saurópodo"],
    "island": ["isla", "náufrago", "naufrago", "atrapado", "búnker", "bunker", "prohibida", "costa", "playa"],
    "jungle": ["amazonas", "selva", "bosque", "dron", "drones", "lidar", "árboles", "arboles", "follaje", "vegetación", "vegetacion", "dosel"],
    "zombie": ["zombi", "zombie", "apocalipsis", "infectado", "evacuación", "evacuacion", "supermercado", "refugio", "supervivencia", "escape", "mochila"],
}


def _font(size: int, bold: bool = True) -> Any:
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    candidates = (
        [r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]
        if bold
        else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for c in candidates:
        if Path(c).exists():
            _FONT_CACHE[key] = ImageFont.truetype(c, size)
            return _FONT_CACHE[key]
    _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


def detect_theme_from_text(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["prehist", "dinosaurio", "jurásico", "jurasico", "cretácico", "devónico", "carbonífero"]):
        return "prehistory"
    if any(k in t for k in ["apagón", "apagon", "72 horas", "cajeros automáticos", "semáforos", "electricidad y el internet"]):
        return "blackout"
    if any(k in t for k in ["mariana", "abismo challenger", "submarino", "bioluminiscente", "11 kilómetros bajo", "10,994", "océano", "oceano"]):
        return "ocean"
    if any(k in t for k in ["tormenta solar", "carrington", "eyección de masa coronal", "satélites", "geomagnética", "solar"]):
        return "space"
    if any(k in t for k in ["isla prohibida", "isla desierta", "bambú y hojas de palma", "náufrago"]):
        return "island"
    if any(k in t for k in ["amazonas", "selva", "lidar", "dosel de los árboles"]):
        return "jungle"
    return "zombie"


# ==============================================================================
# 2. MOTOR DE VALIDACIÓN CONTEXTUAL ESTRICTA
# ==============================================================================
def validate_scene_asset(image_path: Path, phrase_text: str = "", theme: str = "") -> bool:
    """
    Valida de forma estricta que la imagen pertenezca exclusivamente al tema narrado.
    Rechaza terminantemente ilustraciones ajenas (ej. zombis en el espacio o en el fondo marino).
    """
    if not image_path.exists() or image_path.stat().st_size < 10_000:
        return False

    fname = image_path.name.lower()
    detected_theme = theme or (detect_theme_from_text(phrase_text) if phrase_text else "")
    if not detected_theme:
        return True

    allowed_files = THEME_ASSET_REGISTRY.get(detected_theme, [])
    for allowed in allowed_files:
        if allowed.lower() in fname:
            return True

    # Si el nombre contiene prefijo de otro tema prohibido, rechazar inmediatamente
    for other_theme, filenames in THEME_ASSET_REGISTRY.items():
        if other_theme != detected_theme:
            for bad_file in filenames:
                bad_stem = bad_file.split("_")[0]
                if fname.startswith(bad_stem):
                    return False

    return False


def _create_procedural_thematic_art(theme: str, variant: int = 0) -> Image.Image:
    """Crea escenario 2D procedimental de respaldo 100% coherente con el tema si faltara archivo."""
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (12, 18, 32))
    draw = ImageDraw.Draw(img, "RGBA")

    palettes = {
        "ocean": [(4, 22, 48), (6, 55, 92), (0, 180, 216)],
        "blackout": [(10, 12, 24), (25, 28, 48), (255, 170, 0)],
        "prehistory": [(28, 18, 14), (72, 36, 22), (255, 95, 35)],
        "island": [(12, 38, 46), (24, 85, 78), (255, 200, 60)],
        "jungle": [(10, 32, 18), (22, 68, 34), (110, 230, 85)],
        "space": [(8, 8, 26), (26, 16, 58), (255, 110, 40)],
        "zombie": [(24, 14, 18), (58, 22, 28), (225, 45, 45)],
    }
    top_c, mid_c, acc_c = palettes.get(theme, palettes["zombie"])

    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        r = int(top_c[0] * (1 - ratio) + mid_c[0] * ratio)
        g = int(top_c[1] * (1 - ratio) + mid_c[1] * ratio)
        b = int(top_c[2] * (1 - ratio) + mid_c[2] * ratio)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b, 255))

    rng = np.random.default_rng(seed=100 + variant * 17)
    if theme == "ocean":
        draw.polygon([(0, 400), (260, 900), (180, 1920), (0, 1920)], fill=(3, 12, 26, 240))
        draw.polygon([(1080, 350), (820, 950), (890, 1920), (1080, 1920)], fill=(3, 12, 26, 240))
        for _ in range(35):
            bx, by, br = int(rng.integers(80, 1000)), int(rng.integers(250, 1750)), int(rng.integers(6, 28))
            draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(acc_c[0], acc_c[1], acc_c[2], 95), outline=(255, 255, 255, 160), width=2)
    elif theme in ("blackout", "zombie"):
        for x_b in range(0, VIDEO_WIDTH, 130):
            bh = int(rng.integers(550, 1150))
            draw.rectangle([x_b, VIDEO_HEIGHT - bh, x_b + 118, VIDEO_HEIGHT], fill=(14, 16, 26, 255), outline=(0, 0, 0, 255), width=5)
    elif theme in ("jungle", "island", "prehistory"):
        for i in range(12):
            tx = i * 100 + int(rng.integers(-20, 20))
            draw.rectangle([tx, 300, tx + 48, 1920], fill=(18, 38, 22, 230), outline=(0, 0, 0, 255), width=4)
    elif theme == "space":
        for _ in range(70):
            sx, sy, sr = int(rng.integers(30, 1050)), int(rng.integers(50, 1850)), int(rng.integers(2, 6))
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, 220))
        # Arco solar
        draw.arc([-200, -200, 1280, 1280], start=0, end=180, fill=(255, 120, 30, 210), width=18)

    return img


def get_theme_scene_files(theme: str, num_scenes: int = 5, script_text: str = "") -> List[Path]:
    """
    Devuelve la lista de ilustraciones 2D estrictamente verificadas para la temática.
    Aplica validación previa para garantizar 100% de coherencia contextual.
    """
    allowed_filenames = THEME_ASSET_REGISTRY.get(theme, THEME_ASSET_REGISTRY["zombie"])
    result: List[Path] = []

    # Filtrar solo archivos existentes y válidos de este tema
    existing_valid: List[Path] = []
    for fn in allowed_filenames:
        p = OUTPUT_DIR / fn
        if p.exists() and p.stat().st_size > 15_000 and validate_scene_asset(p, script_text, theme):
            existing_valid.append(p)

    for idx in range(num_scenes):
        if existing_valid:
            chosen = existing_valid[idx % len(existing_valid)]
            result.append(chosen)
        else:
            fallback = OUTPUT_DIR / f"theme_{theme}_{idx}.png"
            if not fallback.exists():
                im = _create_procedural_thematic_art(theme, variant=idx)
                im.save(fallback)
            result.append(fallback)

    return result


def fetch_or_generate_comic_art(prompt: str, dest_path: Path, seed: int = 101, theme: str = "") -> Path:
    """
    Selecciona y encuadra una ilustración cómic 2D validada previa al 100% con el tema.
    Garantiza que una postal de Tormenta Solar NUNCA use imágenes de zombis.
    """
    detected_theme = theme or detect_theme_from_text(prompt)
    scene_files = get_theme_scene_files(detected_theme, num_scenes=5, script_text=prompt)
    chosen = scene_files[seed % len(scene_files)]

    if not validate_scene_asset(chosen, prompt, detected_theme):
        chosen = scene_files[0]

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(chosen).convert("RGB")
    w, h = im.size
    crop_margin = int(min(w, h) * 0.03 * ((seed % 3) + 1))
    im_cropped = im.crop((crop_margin, crop_margin, w - crop_margin, h - crop_margin)).resize((w, h), Image.Resampling.LANCZOS)
    im_cropped.save(dest_path)
    return dest_path


# ==============================================================================
# 3. LOCUCIÓN NEURAL Y EXTRACCIÓN DE PALABRAS (TTS CON A/B TESTING)
# ==============================================================================
async def _tts_with_word_timings(
    text: str,
    voice: str,
    rate: str,
    audio_out: Path,
    pitch: str = "+0Hz",
) -> List[Dict[str, Any]]:
    """Genera TTS con fallback automatico a otras voces si falla NoAudioReceived."""
    fallback_voices = ["es-MX-JorgeNeural", "es-MX-DaliaNeural", "es-CO-GonzaloNeural"]
    voices_to_try = [voice] + [v for v in fallback_voices if v != voice]

    for attempt_voice in voices_to_try:
        try:
            comm = edge_tts.Communicate(text=text, voice=attempt_voice, rate=rate, pitch=pitch)
            timings: List[Dict[str, Any]] = []
            with open(audio_out, "wb") as f:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                        s = chunk["offset"] / 10_000_000.0
                        d = chunk["duration"] / 10_000_000.0
                        timings.append({"type": chunk["type"], "start": s, "end": s + max(d, 0.15), "text": chunk["text"]})
            if attempt_voice != voice:
                print(f"[TTS] Fallback de voz: {voice} -> {attempt_voice}")
            return timings
        except Exception as e:
            print(f"[TTS] Voz {attempt_voice} fallo: {e} - probando siguiente...")
            continue

    print("[TTS] Todas las voces fallaron. Se usara sincronizacion proporcional.")
    return []


def _build_phrases_from_timings(
    script_text: str,
    timings: List[Dict[str, Any]],
    total_dur: float,
    max_words: int = 4,
) -> List[Dict[str, Any]]:
    word_evs = [e for e in timings if e["type"] == "WordBoundary"]
    if word_evs:
        phrases: List[Dict[str, Any]] = []
        cur_w: List[str] = []
        w_starts: List[float] = []
        p_start = 0.0
        last_e = 0.0
        for ev in word_evs:
            if not cur_w:
                p_start = ev["start"]
            cur_w.append(ev["text"])
            w_starts.append(ev["start"])
            last_e = ev["end"]
            if len(cur_w) >= max_words:
                phrases.append({"start": p_start, "end": last_e, "words": cur_w, "word_starts": w_starts})
                cur_w = []
                w_starts = []
        if cur_w:
            phrases.append({"start": p_start, "end": last_e, "words": cur_w, "word_starts": w_starts})
        return phrases

    raw_words = script_text.split()
    groups = [raw_words[i : i + max_words] for i in range(0, len(raw_words), max_words)] or [["HISTORIA"]]
    dur_per_g = total_dur / len(groups)
    phrases = []
    for idx, g in enumerate(groups):
        st = idx * dur_per_g
        en = st + dur_per_g
        w_dur = dur_per_g / max(1, len(g))
        w_starts = [st + i * w_dur for i in range(len(g))]
        phrases.append({"start": st, "end": en, "words": g, "word_starts": w_starts})
    return phrases


def _synthesize_documentary_ambience(
    wav_path: Path,
    duration: float,
    scene_switch_times: List[float],
    mode: str = "zombie",
) -> Path:
    sr = 44100
    n = int(sr * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    if mode == "ocean":
        base = 0.05 * np.sin(2 * np.pi * 48.0 * t) + 0.03 * np.sin(2 * np.pi * 96.0 * t)
        sonar = np.zeros_like(t)
        for sp in np.arange(1.0, duration - 0.5, 3.5):
            mask = (t >= sp) & (t < sp + 0.28)
            lt = t[mask] - sp
            sonar[mask] += 0.09 * np.sin(2 * np.pi * 1350.0 * lt) * np.exp(-10.0 * lt)
        signal = base + sonar
    elif mode == "space":
        # Ondas electromagnéticas y pulso solar
        base = 0.04 * np.sin(2 * np.pi * 65.0 * t) + 0.02 * np.sin(2 * np.pi * 130.0 * t * (1.0 + 0.1 * np.sin(t * 0.8)))
        pulse = 0.03 * np.sin(2 * np.pi * 4.0 * t)
        signal = base + pulse
    elif mode in ("blackout", "zombie"):
        sub_drone = 0.06 * np.sin(2 * np.pi * 42.0 * t) + 0.03 * np.sin(2 * np.pi * 84.0 * t)
        noise = 0.012 * np.random.normal(0, 1, n)
        signal = sub_drone + noise
    else:
        hum = 0.05 * np.sin(2 * np.pi * 55.0 * t)
        signal = hum

    for sw in scene_switch_times:
        mask = (t >= sw - 0.08) & (t < sw + 0.45)
        lt = t[mask] - (sw - 0.08)
        signal[mask] += 0.16 * np.sin(2 * np.pi * 45.0 * lt) * np.exp(-6.5 * lt)

    signal = np.clip(signal, -0.92, 0.92)
    signal_int16 = (signal * 32767).astype(np.int16)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(signal_int16.tobytes())
    return wav_path


# ==============================================================================
# 4. TELEMETRÍA Y HUD CONTEXTUAL EN CADENCIA DE 2.5 SEGUNDOS
# ==============================================================================
def _extract_contextual_hud_text(theme: str, phrase_text: str, t: float, prog: float) -> str:
    """
    Extrae la telemetría del HUD directamente de las palabras clave y entidades
    de la frase exacta que se narra en este segundo, rotando cada 2.5 segundos.
    """
    txt = phrase_text.lower()
    beat = int(t / 2.5)

    if theme == "ocean":
        if any(w in txt for w in ["luz", "crepuscular", "solar", "sol"]):
            return "ZONA CREPUSCULAR | LUX: 0.00 | TEMP: 2.1°C"
        if any(w in txt for w in ["bioluminiscente", "medusa", "dientes", "señuelo"]):
            return "RADAR BIOLUMINISCENTE | 4,000m | FAUNA ACTIVA"
        if any(w in txt for w in ["presión", "presion", "aviones", "ochocientas", "titanio"]):
            return "PRESIÓN CASCO: 890 ATM [ALERTA ESTRUCTURAL]"
        if any(w in txt for w in ["chimeneas", "hidrotermal", "400", "cuatrocientos", "fondo"]):
            return "FONDO ABISMO: -10,994m | TEMP CHIMENEA: 400°C"
        depth = int(200 + prog * 10794)
        atm = int(20 + prog * 1066)
        cycling = [
            f"PROFUNDIDAD: -{depth:,}m | {atm} ATM",
            "SONAR ABISAL: RADAR ACTIVO (1,500m)",
            "CASCO DE TITANIO: PRESIÓN NOMINAL",
            "SENSORES TÉRMICOS: 1.8°C AGUA MARINA",
        ]
        return cycling[beat % len(cycling)]

    elif theme == "space":
        if any(w in txt for w in ["satélite", "satelite", "gps", "órbita", "orbita"]):
            return "TELEMETRÍA SATÉLITES: SEÑAL 0% | CAÍDA EN ÓRBITA"
        if any(w in txt for w in ["transformador", "alta tensión", "tensión", "eléctrico"]):
            return "TRANSFORMADORES: SOBRETENSIÓN 1,800 kV [PELIGRO]"
        if any(w in txt for w in ["radar", "vuelos", "aviación", "internet"]):
            return "RADARES AÉREOS: ENLACE PERDIDO | GPS APAGADO"
        if any(w in txt for w in ["aviso", "18 horas", "alerta"]):
            return "ALERTA TEMPRANA: IMPACTO SOLAR EN 18 HORAS"
        alert_lvl = min(5, 1 + int(prog * 4.9))
        cme_spd = int(1800 + (t * 73) % 650)
        cycling = [
            f"TORMENTA SOLAR: NIVEL G{alert_lvl} (EXTREMA)",
            f"VELOCIDAD CME: {cme_spd:,} KM/S",
            "RADAR HELIOSFÉRICO: FRENTE DE ONDA",
            "MAGNETÓMETRO: ANOMALÍA GEOMAGNÉTICA",
        ]
        return cycling[beat % len(cycling)]

    elif theme == "blackout":
        if any(w in txt for w in ["semáforo", "semaforo", "tráfico", "elevador", "primera hora"]):
            return "HORA +01:00 | SEMÁFOROS Y TRÁFICO COLAPSADOS"
        if any(w in txt for w in ["cajero", "tarjeta", "banco", "efectivo"]):
            return "HORA +12:00 | CAJEROS FUERA DE SERVICIO"
        if any(w in txt for w in ["agua", "bomba", "tubería", "grifo"]):
            return "HORA +24:00 | BOMBAS DE AGUA DETENIDAS"
        if any(w in txt for w in ["generador", "batería", "radio", "comida"]):
            return "HORA +48:00 | GENERADORES SIN COMBUSTIBLE"
        hours = int(1 + prog * 71)
        grid = max(0, int(100 - prog * 100))
        cycling = [
            f"HORA +{hours:02d}:00 | RED ELÉCTRICA: {grid}%",
            "SUBESTACIONES: ALTA TENSIÓN EN CERO",
            "RED CELULAR: TORRES SIN RESPALDO",
            "RADIO DE EMERGENCIA: CANAL AM 740 kHz",
        ]
        return cycling[beat % len(cycling)]

    elif theme == "prehistory":
        if any(w in txt for w in ["devónico", "devonico", "pez", "acorazado"]):
            return "ERA DEVÓNICA (-400M AÑOS) | 0% TIERRA FIRME"
        if any(w in txt for w in ["carbonífero", "carbonifero", "oxígeno", "libélula", "escorpión"]):
            return "CARBONÍFERO | OXÍGENO: 31% [INTOXICACIÓN]"
        if any(w in txt for w in ["jurásico", "jurasico", "saurópodo", "coloso"]):
            return "JURÁSICO | SÍSMICA: MANADA SAURÓPODOS"
        if any(w in txt for w in ["cretácico", "cretacico", "asteroide", "ceniza"]):
            return "CRETÁCICO SUPERIOR | ALERTA DE IMPACTO"
        cycling = [
            f"CRONÓMETRO: -{int(400 - prog * 334)}M AÑOS",
            "ATMÓSFERA PREHISTÓRICA: COMPOSICIÓN HOSTIL",
            "RADAR DEPREDADORES: FAUNA COLOSAL DETECTADA",
            "RETORNO TEMPORAL: SIN ENLACE CUÁNTICO",
        ]
        return cycling[beat % len(cycling)]

    elif theme == "jungle":
        if any(w in txt for w in ["techo", "dosel", "60 metros", "99%"]):
            return "DOSEL VEGETAL: 60m | LUZ SOLAR: 1%"
        if any(w in txt for w in ["dron", "drones", "gps", "radio"]):
            return "TELEMETRÍA DRON: PÉRDIDA DE SEÑAL GPS"
        if any(w in txt for w in ["especies", "insectos", "veneno"]):
            return "BIODIVERSIDAD NO CLASIFICADA: ALTA"
        if any(w in txt for w in ["lidar", "ciudades", "calzadas", "pirámide"]):
            return "ESCÁNER LÁSER LiDAR: ESTRUCTURA DETECTADA"
        cycling = [
            "SEÑAL GPS: BLOQUEADA POR EL FOLLAJE",
            "RADAR DE PENETRACIÓN: VEGETACIÓN COMPACTA",
            "HUMEDAD RELATIVA: 99.8% | ZONA CERO",
            "ESCÁNER LiDAR 3D: MAPEO ACTIVO",
        ]
        return cycling[beat % len(cycling)]

    elif theme == "island":
        if any(w in txt for w in ["búnker", "bunker", "puerta"]):
            return "BÚNKER SUBTERRÁNEO: ACCESO SELLADO"
        if any(w in txt for w in ["agua", "deshidratación"]):
            return "RECURSOS: FUENTE DE AGUA NO DETECTADA"
        cycling = [
            f"DÍA DE SUPERVIVENCIA: {int(1 + prog * 29)} / 30",
            "SEÑAL DE RESCATE: 0% COBERTURA",
            "PERÍMETRO COSTEÑO: NIEBLA DENSA",
            "EXPLORACIÓN ACTIVA: ZONA DESCONOCIDA",
        ]
        return cycling[beat % len(cycling)]

    else:  # zombie
        if any(w in txt for w in ["súper", "super", "comida", "estantes"]):
            return "MINUTO 30 | SUPERMERCADOS COLAPSADOS"
        if any(w in txt for w in ["autopista", "carriles", "auto"]):
            return "AUTOPISTAS: TRÁFICO BLOQUEADO AL 100%"
        if any(w in txt for w in ["celular", "antena", "llamada"]):
            return "RED TELEFÓNICA: SATURACIÓN TOTAL"
        if any(w in txt for w in ["mochila", "72 horas", "botiquín"]):
            return "EQUIPO ESENCIAL: MOCHILA DE 72 HORAS"
        cycling = [
            "EVACUACIÓN DÍA 1 | TIEMPO CRÍTICO",
            "REFUGIO SEGURO: PERÍMETRO EN OBSERVACIÓN",
            "COMUNICACIONES: RADIO DE PILAS ACTIVA",
            "ALERTAS MUNICIPALES: FRECUENCIA 162.4 MHz",
        ]
        return cycling[beat % len(cycling)]


# ==============================================================================
# 5. RENDERIZADO DEL PERSONAJE 2D CON TRANSICIONES DINÁMICAS (RETENCIÓN)
# ==============================================================================
def _draw_live_2d_character_and_hud(
    draw: ImageDraw.ImageDraw,
    t: float,
    prog: float,
    sc_idx: int,
    is_speaking: bool,
    theme: str,
    phrase_text: str = "",
) -> None:
    beat_idx = int(t / 2.5)
    beat_local = (t % 2.5) / 2.5

    # --- A. TELEMETRÍA Y HUD INTERACTIVO SINCRONIZADO CADA 2.5s ---
    hud_text = _extract_contextual_hud_text(theme, phrase_text, t, prog)

    # Colores del HUD según el tema
    hud_styles = {
        "ocean": ((4, 22, 42, 225), (0, 215, 255, 235), (0, 240, 255, 255)),
        "space": ((18, 12, 38, 225), (255, 130, 45, 235), (255, 195, 60, 255)),
        "blackout": ((22, 12, 16, 225), (255, 75, 55, 235), (255, 210, 60, 255)),
        "prehistory": ((28, 18, 14, 225), (255, 115, 45, 235), (255, 185, 75, 255)),
        "island": ((14, 32, 28, 225), (45, 215, 145, 235), (140, 255, 195, 255)),
        "jungle": ((12, 28, 16, 225), (85, 230, 110, 235), (160, 255, 140, 255)),
        "zombie": ((24, 14, 18, 225), (255, 65, 55, 235), (255, 215, 75, 255)),
    }
    bg_hud, border_hud, text_hud = hud_styles.get(theme, hud_styles["zombie"])

    # Tarjeta de telemetría HUD superior
    draw.rounded_rectangle([50, 260, 530, 345], radius=14, fill=bg_hud, outline=border_hud, width=3)

    # Indicador luminoso intermitente a 2.5 Hz en la esquina izquierda del HUD
    dot_glow = (255, 40, 40, 255) if (int(t * 5) % 2 == 0) else (40, 220, 80, 255)
    draw.ellipse([68, 296, 84, 312], fill=dot_glow, outline=(0, 0, 0, 255), width=2)

    # Texto autoajustable del HUD
    f_hud = _font(25, bold=True)
    draw.text((305, 303), hud_text, font=f_hud, fill=text_hud, anchor="mm")

    # Efecto radar / escáner circular en esquina superior derecha
    rx, ry, rr = 960, 315, 56
    draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(10, 16, 28, 215), outline=border_hud, width=3)
    draw.ellipse([rx - rr // 2, ry - rr // 2, rx + rr // 2, ry + rr // 2], outline=(border_hud[0], border_hud[1], border_hud[2], 100), width=2)
    ang = (t * 3.4) % (2 * math.pi)
    draw.line([(rx, ry), (rx + int(rr * math.cos(ang)), ry + int(rr * math.sin(ang)))], fill=text_hud, width=4)

    # Partículas temáticas a 24 FPS
    if theme == "ocean":
        for bi in range(12):
            bx = int((110 + bi * 78 + 24 * math.sin(t * 1.8 + bi)) % (VIDEO_WIDTH - 80)) + 40
            by = int((1700 - (t * (90 + (bi % 4) * 22) + bi * 130)) % 1350) + 260
            br = 5 + (bi % 3) * 3
            draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(120, 225, 255, 65), outline=(210, 250, 255, 140), width=2)
    elif theme in ("space", "blackout"):
        for sp in range(8):
            spx = int((80 + sp * 125 + 35 * math.sin(t * 3.2 + sp)) % (VIDEO_WIDTH - 70))
            spy = int((1600 - (t * 110 + sp * 140)) % 1200) + 280
            draw.line([(spx, spy), (spx + 6, spy - 14)], fill=(255, 215, 60, 180), width=2)

    # --- B. PERSONAJE 2D CÓMIC (ESTILO DON ZOMBI) CON ROTACIÓN DE POSES CADA 2.5s ---
    side_right = (sc_idx % 2 == 1)
    base_cx = 855 if side_right else 225
    walk_x = int(14 * math.sin(t * 2.4))
    bob_y = int(9 * abs(math.sin(t * 4.8)))
    cx = base_cx + walk_x
    cy = 1365 - bob_y

    # Haz de luz de linterna / escáner en ambientes oscuros
    if theme in ("blackout", "zombie", "ocean", "jungle"):
        beam_dir = -1 if side_right else 1
        beam_angle = 0.22 * math.sin(t * 2.6)
        bx_end = cx + beam_dir * 520
        by_top = cy - 180 + int(190 * beam_angle)
        by_bot = cy + 95 + int(190 * beam_angle)
        draw.polygon(
            [(cx + beam_dir * 45, cy + 25), (bx_end, by_top), (bx_end, by_bot)],
            fill=(255, 245, 150, 52),
        )

    # Sombra bajo el personaje
    draw.ellipse([cx - 85, cy + 145, cx + 85, cy + 178], fill=(0, 0, 0, 135))

    # Piernas animadas con borde negro
    leg_swing = int(22 * math.sin(t * 4.8))
    draw.line([(cx - 24, cy + 85), (cx - 32 - leg_swing, cy + 158)], fill=(0, 0, 0, 255), width=14)
    draw.line([(cx + 24, cy + 85), (cx + 32 + leg_swing, cy + 158)], fill=(0, 0, 0, 255), width=14)

    # Torso / Chaqueta con color temático
    jacket_colors = {
        "ocean": (245, 190, 25, 255),
        "blackout": (215, 45, 45, 255),
        "zombie": (215, 45, 45, 255),
        "jungle": (65, 155, 75, 255),
        "island": (225, 125, 40, 255),
        "prehistory": (185, 115, 55, 255),
        "space": (55, 125, 235, 255),
    }
    j_col = jacket_colors.get(theme, (215, 45, 45, 255))
    draw.rounded_rectangle([cx - 58, cy - 10, cx + 58, cy + 96], radius=26, fill=j_col, outline=(0, 0, 0, 255), width=6)
    draw.line([(cx, cy - 8), (cx, cy + 94)], fill=(0, 0, 0, 255), width=4)

    # Variación de Poses cada 2.5s para alta retención (alerta, escaneo, asombro, señalando)
    pose_mode = beat_idx % 4
    arm_dir = -1 if side_right else 1

    if pose_mode == 0:  # Estado Alerta
        arm_wave = int(14 * math.sin(t * 5.0)) if is_speaking else int(6 * math.sin(t * 2.5))
        hand_x = cx + arm_dir * 84
        hand_y = cy + 22 + arm_wave
        draw.line([(cx + arm_dir * 42, cy + 18), (hand_x, hand_y)], fill=(0, 0, 0, 255), width=13)
        draw.rounded_rectangle([hand_x - 16, hand_y - 10, hand_x + 16, hand_y + 10], radius=5, fill=(70, 75, 85, 255), outline=(0, 0, 0, 255), width=4)

    elif pose_mode == 1:  # Estado Escaneo / Radar de muñeca
        hand_x = cx + arm_dir * 55
        hand_y = cy - 25 + int(8 * math.sin(t * 3.5))
        draw.line([(cx + arm_dir * 42, cy + 18), (hand_x, hand_y)], fill=(0, 0, 0, 255), width=13)
        # Dispositivo de radar con pantalla parpadeante
        draw.rounded_rectangle([hand_x - 18, hand_y - 14, hand_x + 18, hand_y + 14], radius=6, fill=(40, 45, 55, 255), outline=(0, 0, 0, 255), width=4)
        draw.rectangle([hand_x - 10, hand_y - 8, hand_x + 10, hand_y + 8], fill=(0, 255, 170, 255))

    elif pose_mode == 2:  # Estado Asombro / Tensión
        hand_x = cx + arm_dir * 38
        hand_y = cy - 8 + int(5 * math.sin(t * 6.0))
        draw.line([(cx + arm_dir * 42, cy + 18), (hand_x, hand_y)], fill=(0, 0, 0, 255), width=13)
        draw.ellipse([hand_x - 14, hand_y - 14, hand_x + 14, hand_y + 14], fill=(70, 75, 85, 255), outline=(0, 0, 0, 255), width=4)

    else:  # Estado Explicando / Señalando hacia el escenario
        hand_x = cx + arm_dir * 105
        hand_y = cy - 18 + int(8 * math.sin(t * 4.0))
        draw.line([(cx + arm_dir * 42, cy + 18), (hand_x, hand_y)], fill=(0, 0, 0, 255), width=13)
        draw.line([(hand_x, hand_y), (hand_x + arm_dir * 22, hand_y - 12)], fill=(0, 0, 0, 255), width=8)

    # Cabeza redonda blanca expresiva estilo Don Zombi
    hr = 68
    hy = cy - 72
    draw.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=(248, 250, 252, 255), outline=(0, 0, 0, 255), width=7)

    # Gorro beanie / casco
    hat_col = (55, 85, 105, 255) if theme != "ocean" else (245, 185, 15, 255)
    draw.chord([cx - hr - 4, hy - hr - 14, cx + hr + 4, hy + 18], start=180, end=360, fill=hat_col, outline=(0, 0, 0, 255), width=6)
    draw.rounded_rectangle([cx - hr - 6, hy - 28, cx + hr + 6, hy - 6], radius=10, fill=hat_col, outline=(0, 0, 0, 255), width=5)

    # Ojos y parpadeo natural
    is_blinking = (t % 3.4) > 3.22
    look_offset = -6 if side_right else 6
    for ex in (cx - 24 + look_offset, cx + 24 + look_offset):
        if is_blinking:
            draw.line([(ex - 13, hy - 2), (ex + 13, hy - 2)], fill=(0, 0, 0, 255), width=5)
        else:
            draw.ellipse([ex - 13, hy - 16, ex + 13, hy + 12], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=4)
            px = ex + (-3 if side_right else 3)
            draw.ellipse([px - 5, hy - 6, px + 5, hy + 4], fill=(0, 0, 0, 255))
            draw.ellipse([px - 2, hy - 5, px + 1, hy - 2], fill=(255, 255, 255, 255))

    # Cejas dinámicas que cambian con la intensidad
    brow_tilt = 8 if pose_mode == 2 else (4 if sc_idx >= 1 else 0)
    draw.line([(cx - 38 + look_offset, hy - 24 - brow_tilt), (cx - 10 + look_offset, hy - 22 + brow_tilt)], fill=(0, 0, 0, 255), width=5)
    draw.line([(cx + 10 + look_offset, hy - 22 + brow_tilt), (cx + 38 + look_offset, hy - 24 - brow_tilt)], fill=(0, 0, 0, 255), width=5)

    # Gota de sudor animada en tensión
    if sc_idx >= 1 or pose_mode == 2:
        sy_drop = hy - 14 + int((t * 28) % 18)
        sx_drop = cx + (48 if side_right else -48)
        draw.ellipse([sx_drop - 6, sy_drop - 9, sx_drop + 6, sy_drop + 9], fill=(75, 205, 255, 240), outline=(0, 0, 0, 255), width=3)

    # Lip-sync real con la locución hablada
    my = hy + 30
    mx = cx + look_offset
    if is_speaking:
        mouth_open = int(6 + 11 * abs(math.sin(t * 18.5)))
        draw.rounded_rectangle([mx - 18, my - mouth_open, mx + 18, my + mouth_open], radius=9, fill=(185, 35, 45, 255), outline=(0, 0, 0, 255), width=4)
        draw.rectangle([mx - 12, my - mouth_open + 2, mx + 12, my - mouth_open + 7], fill=(255, 255, 255, 255))
    else:
        draw.arc([mx - 16, my - 6, mx + 16, my + 10], start=195, end=345, fill=(0, 0, 0, 255), width=5)

    # Signo de interrogación en el cierre para invitar al debate
    if prog > 0.80:
        qy = hy - 115 + int(10 * math.sin(t * 6.0))
        draw.text((cx, qy), "?", font=_font(76, bold=True), fill=(255, 230, 0, 255), anchor="mm", stroke_width=7, stroke_fill=(0, 0, 0, 255))


def _draw_wrapped_badge(draw: ImageDraw.ImageDraw, top_title: str, red_tag: str, accent_col: Tuple[int, int, int]) -> None:
    draw.rectangle([0, 0, VIDEO_WIDTH, 260], fill=(0, 0, 0, 200))
    draw.line([(0, 260), (VIDEO_WIDTH, 260)], fill=accent_col + (255,), width=6)

    title_words = top_title.strip().upper().split()
    if len(title_words) >= 4 and len(top_title) > 22:
        mid = (len(title_words) + 1) // 2
        lines = [" ".join(title_words[:mid]), " ".join(title_words[mid:])]
    else:
        lines = [top_title.strip().upper()]

    font_sz = 52
    while font_sz > 32:
        f_cand = _font(font_sz, bold=True)
        max_w = max((draw.textbbox((0, 0), ln, font=f_cand)[2] - draw.textbbox((0, 0), ln, font=f_cand)[0]) for ln in lines)
        if max_w <= VIDEO_WIDTH - 80:
            break
        font_sz -= 4

    font_t = _font(font_sz, bold=True)
    if len(lines) == 1:
        draw.text((VIDEO_WIDTH // 2, 75), lines[0], font=font_t, fill=(255, 255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 255))
    else:
        draw.text((VIDEO_WIDTH // 2, 52), lines[0], font=font_t, fill=(255, 255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 255))
        draw.text((VIDEO_WIDTH // 2, 114), lines[1], font=font_t, fill=(255, 235, 0, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 255))

    tag_clean = red_tag.strip().upper()
    if tag_clean:
        tag_sz = 30
        while tag_sz > 20:
            f_tag = _font(tag_sz, bold=True)
            tb = draw.textbbox((0, 0), tag_clean, font=f_tag)
            if (tb[2] - tb[0]) <= VIDEO_WIDTH - 160:
                break
            tag_sz -= 2

        f_tag = _font(tag_sz, bold=True)
        tw_bbox = draw.textbbox((0, 0), tag_clean, font=f_tag)
        tw = tw_bbox[2] - tw_bbox[0]
        bx1 = (VIDEO_WIDTH - tw) // 2 - 28
        bx2 = (VIDEO_WIDTH + tw) // 2 + 28
        draw.rounded_rectangle([bx1, 168, bx2, 232], radius=12, fill=accent_col + (245,), outline=(0, 0, 0, 255), width=4)
        draw.text((VIDEO_WIDTH // 2, 200), tag_clean, font=_font(tag_sz, bold=True), fill=(255, 255, 255, 255), anchor="mm")


# ==============================================================================
# 6. PIPELINE PRINCIPAL DE ANIMACIÓN Y RENDERIZADO
# ==============================================================================
def build_illustrated_youtube_video(
    story_id: str,
    script_text: str,
    scene_files: List[Path],
    scene_badges: List[Tuple[str, str, Tuple[int, int, int]]],
    timeline_labels: List[str],
    output_filename: str,
    ambience_mode: str = "zombie",
    voice_profile: Optional[Dict[str, Any]] = None,
) -> Path:
    work_dir = OUTPUT_DIR / f"yt_{story_id}"
    work_dir.mkdir(parents=True, exist_ok=True)
    voice_mp3 = work_dir / "narration.mp3"

    # Selección de Perfil de Voz Neural para A/B Testing
    if not voice_profile:
        voice_profile = select_voice_profile(theme=ambience_mode, topic=script_text[:60])

    voice = voice_profile["voice"]
    rate = voice_profile.get("rate", "+4%")
    pitch = voice_profile.get("pitch", "+0Hz")

    print(f"[{story_id}] 1/3 Generando narración TTS ({voice_profile['name']}) con sincronización y A/B test...")
    timings = asyncio.run(_tts_with_word_timings(script_text, voice, rate, voice_mp3, pitch=pitch))

    voice_clip = AudioFileClip(str(voice_mp3))
    total_dur = voice_clip.duration + 0.65
    phrases = _build_phrases_from_timings(script_text, timings, voice_clip.duration, max_words=4)

    # Carga y validación contextual previa de ilustraciones 2D
    loaded_scenes: List[Image.Image] = []
    for idx, sf in enumerate(scene_files):
        if sf.exists() and sf.stat().st_size > 10_000 and validate_scene_asset(sf, script_text, ambience_mode):
            im = Image.open(sf).convert("RGB")
        else:
            # Reemplazar con el recurso verificado correspondiente a la temática
            verified_list = THEME_ASSET_REGISTRY.get(ambience_mode, [])
            valid_found = False
            for vfn in verified_list:
                vp = OUTPUT_DIR / vfn
                if vp.exists() and vp.stat().st_size > 10_000:
                    im = Image.open(vp).convert("RGB")
                    valid_found = True
                    break
            if not valid_found:
                im = _create_procedural_thematic_art(ambience_mode, variant=idx)

        im_big = ImageOps.fit(im, (int(VIDEO_WIDTH * 1.25), int(VIDEO_HEIGHT * 1.25)), method=Image.Resampling.LANCZOS)
        im_big = ImageEnhance.Color(im_big).enhance(1.12)
        im_big = ImageEnhance.Contrast(im_big).enhance(1.06)
        loaded_scenes.append(im_big)

    num_scenes = len(loaded_scenes)
    scene_dur = total_dur / num_scenes
    switch_times = [i * scene_dur for i in range(1, num_scenes)]

    amb_wav = work_dir / "ambience.wav"
    _synthesize_documentary_ambience(amb_wav, total_dur, switch_times, mode=ambience_mode)
    bg_clip = AudioFileClip(str(amb_wav))
    comp_audio = CompositeAudioClip([bg_clip, voice_clip])

    def make_frame(t: float) -> np.ndarray:
        prog = min(1.0, max(0.0, t / max(total_dur, 0.1)))
        sc_idx = min(num_scenes - 1, int(t / scene_dur))
        sc_local = (t - sc_idx * scene_dur) / max(scene_dur, 0.1)
        sc_local = min(1.0, max(0.0, sc_local))

        big_im = loaded_scenes[sc_idx]
        bw, bh = big_im.size

        # Cadencia dinámica de 2.5s estilo Reels virales (micro-reencuadres y punches)
        beat_idx = int(t / 2.5)
        beat_local = (t % 2.5) / 2.5
        snap_impulse = 0.025 * math.exp(-beat_local * 16.0)

        beat_mode = beat_idx % 4
        if beat_mode == 0:
            zoom = 1.02 + 0.08 * beat_local + snap_impulse
            pan_x = int((bw - VIDEO_WIDTH) * (0.25 + 0.45 * beat_local))
            pan_y = int((bh - VIDEO_HEIGHT) * 0.40)
        elif beat_mode == 1:
            zoom = 1.08 + snap_impulse
            pan_x = int((bw - VIDEO_WIDTH) * (0.70 - 0.50 * beat_local))
            pan_y = int((bh - VIDEO_HEIGHT) * (0.35 + 0.20 * math.sin(beat_local * math.pi)))
        elif beat_mode == 2:
            zoom = 1.14 + 0.04 * beat_local + snap_impulse
            pan_x = int((bw - VIDEO_WIDTH) * 0.50)
            pan_y = int((bh - VIDEO_HEIGHT) * 0.45)
        else:
            zoom = 1.10 - 0.06 * beat_local + snap_impulse
            pan_x = int((bw - VIDEO_WIDTH) * (0.30 + 0.35 * beat_local))
            pan_y = int((bh - VIDEO_HEIGHT) * (0.50 - 0.15 * beat_local))

        # Sacudida cinematográfica en cambio de capítulo
        if sc_local < 0.05 and sc_idx > 0:
            pan_x += int(10 * math.sin(t * 50.0))
            pan_y += int(8 * math.cos(t * 50.0))

        crop_w = int(VIDEO_WIDTH / zoom)
        crop_h = int(VIDEO_HEIGHT / zoom)
        left = max(0, min(bw - crop_w, pan_x))
        top = max(0, min(bh - crop_h, pan_y))

        cropped = big_im.crop((left, top, left + crop_w, top + crop_h))
        frame = cropped.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.BILINEAR)
        draw = ImageDraw.Draw(frame, "RGBA")

        # Determinar la frase activa exacta en este segundo t
        active_phrase = None
        phrase_text = ""
        for ph in phrases:
            if ph["start"] - 0.06 <= t <= ph["end"] + 0.12:
                active_phrase = ph
                phrase_text = " ".join(ph["words"])
                break

        # 1. PERSONAJE 2D + HUD CONTEXTUAL EN TIEMPO REAL
        _draw_live_2d_character_and_hud(
            draw=draw,
            t=t,
            prog=prog,
            sc_idx=sc_idx,
            is_speaking=(active_phrase is not None),
            theme=ambience_mode,
            phrase_text=phrase_text,
        )

        # 2. ENCABEZADO AUTO-AJUSTADO DEL CAPÍTULO
        top_title, red_tag, accent_col = scene_badges[min(sc_idx, len(scene_badges) - 1)]
        _draw_wrapped_badge(draw, top_title, red_tag, accent_col)

        # 3. SUBTÍTULOS CINÉTICOS CON FONDO OSCURO Y RESALTE POP
        draw.rectangle([0, VIDEO_HEIGHT - 410, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(0, 0, 0, 175))
        if active_phrase:
            words = [w.upper() for w in active_phrase["words"]]
            starts = active_phrase["word_starts"]
            active_w_idx = 0
            for wi, ws in enumerate(starts):
                if t >= ws - 0.04:
                    active_w_idx = wi

            f_sub = _font(54, bold=True)
            full_line = " ".join(words)
            while True:
                lb = draw.textbbox((0, 0), full_line, font=f_sub)
                if (lb[2] - lb[0]) <= VIDEO_WIDTH - 90 or f_sub.size <= 36:
                    break
                f_sub = _font(f_sub.size - 4, bold=True)

            lw = lb[2] - lb[0]
            cur_x = (VIDEO_WIDTH - lw) // 2
            sub_y = 1585

            for wi, w_str in enumerate(words):
                is_curr = wi == active_w_idx
                w_color = (255, 230, 0, 255) if is_curr else (255, 255, 255, 255)
                # Resalte pop en la palabra hablada actual
                f_word = _font(f_sub.size + 4, bold=True) if is_curr else f_sub
                y_offset = -4 if is_curr else 0

                draw.text(
                    (cur_x, sub_y + y_offset),
                    w_str,
                    font=f_word,
                    fill=w_color,
                    stroke_width=7,
                    stroke_fill=(0, 0, 0, 255),
                )
                wb = draw.textbbox((0, 0), w_str + " ", font=f_sub)
                cur_x += wb[2] - wb[0]

        # 4. LÍNEA DE TIEMPO INFERIOR CON LOS CAPÍTULOS
        tl_y = 1815
        draw.line([(85, tl_y), (VIDEO_WIDTH - 85, tl_y)], fill=(255, 255, 255, 140), width=4)
        prog_x = int(85 + (VIDEO_WIDTH - 170) * prog)
        draw.line([(85, tl_y), (prog_x, tl_y)], fill=(255, 215, 0, 255), width=6)
        draw.ellipse([prog_x - 10, tl_y - 10, prog_x + 10, tl_y + 10], fill=(255, 215, 0, 255), outline=(0, 0, 0, 255), width=3)

        for idx_l, lbl in enumerate(timeline_labels):
            lx = int(105 + idx_l * ((VIDEO_WIDTH - 210) / max(1, len(timeline_labels) - 1)))
            draw.line([(lx, tl_y - 12), (lx, tl_y + 12)], fill=(255, 255, 255, 200), width=3)
            draw.text((lx, tl_y + 34), lbl[:14], font=_font(24, bold=True), fill=(235, 235, 235, 230), anchor="mm")

        return np.asarray(frame.convert("RGB"))

    preview_arr = make_frame(min(4.0, total_dur * 0.2))
    preview_path = OUTPUT_DIR / f"preview_{story_id}.jpg"
    Image.fromarray(preview_arr).save(preview_path, quality=94)

    out_path = OUTPUT_DIR / output_filename
    print(f"[{story_id}] 2/3 Renderizando video largo ({total_dur:.1f}s) a {FPS_SMOOTH} FPS continuos en {out_path.name}...")
    vc = VideoClip(make_frame, duration=total_dur)
    if MOVIEPY_V2:
        vc = vc.with_audio(comp_audio)
    else:
        vc = vc.set_audio(comp_audio)

    vc.write_videofile(
        str(out_path),
        fps=FPS_SMOOTH,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger=None,
    )
    vc.close()
    comp_audio.close()
    voice_clip.close()
    bg_clip.close()
    print(f"[{story_id}] 3/3 ¡Exportado con éxito ({total_dur:.1f}s) en: {out_path}!")
    return out_path

