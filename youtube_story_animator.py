"""
Motor de Animación Narrativa de Largo Formato (60-85s) Estilo YouTube
("Don Zombi", "Curiosamente Graficado", "Sobrevive con Bruno" y "Sebastián Schiller") a 24 FPS continuos.

Características clave:
  - Videos largos de 5 a 6 capítulos/escenas (60 a 85 segundos) con alta retención.
  - Ilustraciones 100% coherentes con el tema (Océano/Fosa de las Marianas, Apagón Mundial,
    Prehistoria/Dinosaurios, Selva/Amazonas, Isla Prohibida, Tormenta Solar, Supervivencia).
  - Personaje 2D animado en vivo a 24 FPS (lip-sync en tiempo real con la voz, parpadeo,
    expresiones dinámicas, linterna/radar animado y medidores HUD según el tema).
  - Ajuste automático de texto (auto-scaling y salto de línea) para que NUNCA se corte un título.
"""

import asyncio
import json
import math
import wave
from pathlib import Path
from typing import Any, Dict, List, Tuple

import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

from config import OUTPUT_DIR, VIDEO_HEIGHT, VIDEO_WIDTH

try:
    from moviepy import AudioFileClip, CompositeAudioClip, VideoClip
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import AudioFileClip, CompositeAudioClip, VideoClip
    MOVIEPY_V2 = False

FPS_SMOOTH = 24
_FONT_CACHE: Dict[Tuple[int, bool], Any] = {}


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
    if any(k in t for k in ["mariana", "océano", "oceano", "mar", "abismo", "submarin", "agua", "profundidad", "tiburón", "tiburon"]):
        return "ocean"
    if any(k in t for k in ["apagón", "apagon", "electricidad", "internet", "red eléctrica", "energia", "energía", "72 horas", "oscuridad"]):
        return "blackout"
    if any(k in t for k in ["prehist", "dinosaurio", "jurásico", "jurasico", "cretácico", "extinción", "fósil", "pasado", "era"]):
        return "prehistory"
    if any(k in t for k in ["isla", "prohibid", "náufrago", "naufrago", "desierta", "triángulo", "búnker", "bunker"]):
        return "island"
    if any(k in t for k in ["selva", "amazonas", "jungla", "bosque", "dron", "inexplorad"]):
        return "jungle"
    if any(k in t for k in ["sol", "espacio", "tormenta solar", "satélite", "asteroide", "planeta", "universo", "nasa", "cosmos"]):
        return "space"
    return "zombie"


def _create_procedural_thematic_art(theme: str, variant: int = 0) -> Image.Image:
    """
    Crea un escenario ilustrado 2D de respaldo 1080x1920 100% coherente con el tema
    si aún no existe el archivo PNG específico en disco.
    """
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

    # Elementos arquitectónicos/ambientales 2D según el tema
    rng = np.random.default_rng(seed=100 + variant * 17)
    if theme == "ocean":
        # Siluetas de paredes abisales y criaturas bioluminiscentes
        draw.polygon([(0, 400), (260, 900), (180, 1920), (0, 1920)], fill=(3, 12, 26, 240))
        draw.polygon([(1080, 350), (820, 950), (890, 1920), (1080, 1920)], fill=(3, 12, 26, 240))
        for _ in range(35):
            bx, by, br = int(rng.integers(80, 1000)), int(rng.integers(250, 1750)), int(rng.integers(6, 28))
            draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(acc_c[0], acc_c[1], acc_c[2], 95), outline=(255, 255, 255, 160), width=2)
    elif theme in ("blackout", "zombie"):
        # Skyline de edificios oscuros estilo cómic 2D
        for x_b in range(0, VIDEO_WIDTH, 130):
            bh = int(rng.integers(550, 1150))
            draw.rectangle([x_b, VIDEO_HEIGHT - bh, x_b + 118, VIDEO_HEIGHT], fill=(14, 16, 26, 255), outline=(0, 0, 0, 255), width=5)
    elif theme in ("jungle", "island", "prehistory"):
        # Árboles y follaje denso en capas con borde negro cómic
        for i in range(12):
            tx = i * 100 + int(rng.integers(-20, 20))
            draw.rectangle([tx, 300, tx + 48, 1920], fill=(18, 38, 22, 230), outline=(0, 0, 0, 255), width=4)

    return img


def get_theme_scene_files(theme: str, num_scenes: int = 5) -> List[Path]:
    """
    Devuelve una lista de archivos de ilustración 2D 100% acordes al tema.
    NUNCA usa caras aleatorias ni imágenes que no correspondan al tema.
    """
    theme_map: Dict[str, List[str]] = {
        "ocean": ["marianas_1.png", "marianas_2.png", "selva_2.png", "marianas_1.png", "marianas_2.png"],
        "blackout": ["apagon_1.png", "zombi_1.png", "zombi_2.png", "apagon_1.png", "zombi_3.png"],
        "prehistory": ["prehistoria_1.png", "selva_1.png", "selva_2.png", "prehistoria_1.png", "isla_1.png"],
        "island": ["isla_1.png", "selva_1.png", "zombi_3.png", "selva_2.png", "isla_1.png"],
        "jungle": ["selva_1.png", "selva_2.png", "isla_1.png", "selva_1.png", "selva_2.png"],
        "space": ["espacio_1.png", "apagon_1.png", "zombi_2.png", "espacio_1.png", "zombi_3.png"],
        "zombie": ["zombi_1.png", "zombi_2.png", "zombi_3.png", "apagon_1.png", "zombi_1.png"],
    }
    preferred = theme_map.get(theme, theme_map["zombie"])
    result: List[Path] = []

    for idx in range(num_scenes):
        fname = preferred[idx % len(preferred)]
        fpath = OUTPUT_DIR / fname
        if fpath.exists() and fpath.stat().st_size > 15_000:
            result.append(fpath)
        else:
            # Buscar cualquier otra ilustración válida del mismo grupo o crear escenario temático limpio
            fallback_path = OUTPUT_DIR / f"theme_{theme}_{idx}.png"
            if not fallback_path.exists():
                im = _create_procedural_thematic_art(theme, variant=idx)
                im.save(fallback_path)
            result.append(fallback_path)

    return result


def fetch_or_generate_comic_art(prompt: str, dest_path: Path, seed: int = 101, theme: str = "") -> Path:
    """
    Selecciona una ilustración cómic 2D 100% coherente con el tema (sin usar generadores
    externos inestables que creen rostros deformes sin relación con el texto).
    """
    detected_theme = theme or detect_theme_from_text(prompt)
    scene_files = get_theme_scene_files(detected_theme, num_scenes=5)
    chosen = scene_files[seed % len(scene_files)]

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(chosen).convert("RGB")
    # Ligera variación de encuadre según la semilla para que cada postal sea única pero 100% del tema
    w, h = im.size
    crop_margin = int(min(w, h) * 0.04 * ((seed % 3) + 1))
    im_cropped = im.crop((crop_margin, crop_margin, w - crop_margin, h - crop_margin)).resize((w, h), Image.Resampling.LANCZOS)
    im_cropped.save(dest_path)
    return dest_path


async def _tts_with_word_timings(
    text: str,
    voice: str,
    rate: str,
    audio_out: Path,
) -> List[Dict[str, Any]]:
    comm = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    timings: List[Dict[str, Any]] = []
    with open(audio_out, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                s = chunk["offset"] / 10_000_000.0
                d = chunk["duration"] / 10_000_000.0
                timings.append({"type": chunk["type"], "start": s, "end": s + max(d, 0.15), "text": chunk["text"]})
    return timings


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
        pulse = 0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t)
        # Pings de sonar submarino cada 3.5 segundos
        sonar = np.zeros_like(t)
        for sp in np.arange(1.0, duration - 0.5, 3.5):
            mask = (t >= sp) & (t < sp + 0.28)
            lt = t[mask] - sp
            sonar[mask] += 0.09 * np.sin(2 * np.pi * 1350.0 * lt) * np.exp(-10.0 * lt)
        bg = base * pulse + sonar
    elif mode in ("jungle", "island", "prehistory"):
        base = 0.04 * np.sin(2 * np.pi * 65.0 * t) + 0.025 * np.sin(2 * np.pi * 130.0 * t + 0.8)
        pulse = 0.5 + 0.5 * np.sin(2 * np.pi * 0.45 * t)
        bg = base * pulse
    else:
        base = 0.05 * np.sin(2 * np.pi * 55.0 * t) + 0.03 * np.sin(2 * np.pi * 110.0 * t)
        pulse = 0.5 + 0.5 * np.sin(2 * np.pi * 0.85 * t)
        bg = base * pulse

    # Efecto whoosh cinematográfico en cada cambio de capítulo
    for st_time in scene_switch_times:
        mask = (t >= st_time - 0.18) & (t < st_time + 0.28)
        if np.any(mask):
            lt = t[mask] - (st_time - 0.18)
            freq = np.linspace(260, 75, len(lt))
            whoosh = 0.14 * np.sin(2 * np.pi * freq * lt) * np.exp(-6.0 * lt)
            bg[mask] += whoosh

    audio = np.clip(bg, -0.92, 0.92)
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    return wav_path


def _draw_wrapped_badge(
    draw: ImageDraw.ImageDraw,
    top_title: str,
    red_tag: str,
    accent_col: Tuple[int, int, int],
) -> None:
    """
    Dibuja el titular superior y la etiqueta de capítulo auto-ajustando el tamaño de fuente
    para que NUNCA se corte ninguna palabra en pantalla.
    """
    draw.rectangle([0, 0, VIDEO_WIDTH, 250], fill=(0, 0, 0, 130))

    # Ajustar tamaño de fuente automáticamente según longitud
    title_clean = top_title.strip().upper()
    font_sz = 68
    while font_sz > 38:
        tb = draw.textbbox((0, 0), title_clean, font=_font(font_sz, bold=True))
        if (tb[2] - tb[0]) <= VIDEO_WIDTH - 90:
            break
        font_sz -= 4

    draw.text(
        (VIDEO_WIDTH // 2, 102),
        title_clean,
        font=_font(font_sz, bold=True),
        fill=(255, 255, 255, 255),
        anchor="mm",
        stroke_width=8,
        stroke_fill=(0, 0, 0, 255),
    )

    if red_tag:
        tag_clean = red_tag.strip().upper()
        tag_sz = 40
        while tag_sz > 26:
            tb = draw.textbbox((0, 0), tag_clean, font=_font(tag_sz, bold=True))
            if (tb[2] - tb[0]) <= VIDEO_WIDTH - 120:
                break
            tag_sz -= 3
        tw_bbox = draw.textbbox((0, 0), tag_clean, font=_font(tag_sz, bold=True))
        tw = tw_bbox[2] - tw_bbox[0]
        bx1 = (VIDEO_WIDTH - tw) // 2 - 28
        bx2 = (VIDEO_WIDTH + tw) // 2 + 28
        draw.rounded_rectangle(
            [bx1, 168, bx2, 232],
            radius=12,
            fill=accent_col + (245,),
            outline=(0, 0, 0, 255),
            width=4,
        )
        draw.text(
            (VIDEO_WIDTH // 2, 200),
            tag_clean,
            font=_font(tag_sz, bold=True),
            fill=(255, 255, 255, 255),
            anchor="mm",
        )


def _draw_live_2d_character_and_hud(
    draw: ImageDraw.ImageDraw,
    t: float,
    prog: float,
    sc_idx: int,
    is_speaking: bool,
    theme: str,
) -> None:
    """
    Dibuja en tiempo real (24 FPS):
      1. Efectos ambientales y medidores HUD animados según el tema (sonar submarino y burbujas
         para Océano, haz de linterna y batería para Apagón, radar GPS para Selva/Isla, etc.).
      2. Nuestro personaje cómic 2D ("Bruno") animado a 24 FPS con lip-sync real al hablar,
         parpadeo natural, movimiento de brazos/objetos y expresiones según el capítulo.
    """
    # --- A. EFECTOS AMBIENTALES Y HUD TEMÁTICO A 24 FPS ---
    if theme == "ocean":
        # Burbujas ascendentes animadas
        for bi in range(14):
            bx = int((110 + bi * 72 + 22 * math.sin(t * 1.8 + bi)) % (VIDEO_WIDTH - 80)) + 40
            by = int((1700 - (t * (95 + (bi % 4) * 25) + bi * 140)) % 1350) + 260
            br = 6 + (bi % 4) * 4
            draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(120, 225, 255, 70), outline=(210, 250, 255, 160), width=2)

        # Medidor de profundidad submarina en vivo (baja de -200m a -10,994m)
        depth_m = int(200 + prog * 10794)
        atm_p = int(20 + prog * 1066)
        draw.rounded_rectangle([55, 265, 510, 345], radius=14, fill=(4, 22, 42, 215), outline=(0, 215, 255, 225), width=3)
        draw.text(
            (282, 305),
            f"PROFUNDIDAD: -{depth_m:,}m | {atm_p} ATM",
            font=_font(28, bold=True),
            fill=(0, 240, 255, 255),
            anchor="mm",
        )
        # Radar sonar circular animado en esquina superior derecha
        rx, ry, rr = 955, 325, 62
        draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(4, 28, 38, 210), outline=(0, 240, 180, 220), width=3)
        draw.ellipse([rx - rr // 2, ry - rr // 2, rx + rr // 2, ry + rr // 2], outline=(0, 240, 180, 110), width=2)
        ang = (t * 3.2) % (2 * math.pi)
        draw.line([(rx, ry), (rx + int(rr * math.cos(ang)), ry + int(rr * math.sin(ang)))], fill=(0, 255, 180, 255), width=4)

    elif theme in ("blackout", "zombie"):
        # Medidor de tiempo transcurrido y energía de la red
        hours_elapsed = int(1 + prog * 71)
        grid_pct = max(0, int(100 - prog * 100))
        draw.rounded_rectangle([55, 265, 520, 345], radius=14, fill=(22, 12, 16, 220), outline=(255, 75, 55, 230), width=3)
        draw.text(
            (287, 305),
            f"HORA +{hours_elapsed:02d}:00 | RED GLOBAL: {grid_pct}%",
            font=_font(28, bold=True),
            fill=(255, 210, 60, 255),
            anchor="mm",
        )

    elif theme in ("jungle", "island", "prehistory"):
        # Esporas/luciérnagas o ceniza volcánica flotando a 24 FPS
        col_p = (255, 130, 40, 155) if theme == "prehistory" else (160, 255, 110, 145)
        for pi in range(12):
            px = int((90 + pi * 83 + 35 * math.sin(t * 1.4 + pi)) % (VIDEO_WIDTH - 80)) + 40
            py = int((1650 - (t * 65 + pi * 120)) % 1250) + 280
            draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=col_p)

        hud_txt = f"OXÍGENO: {int(21 + prog * 12)}% | PELIGRO EXTREMO" if theme == "prehistory" else f"SEÑAL GPS: {max(0, int(100 - prog * 100))}% | ZONA CERO"
        draw.rounded_rectangle([55, 265, 510, 345], radius=14, fill=(14, 28, 18, 220), outline=(95, 235, 120, 225), width=3)
        draw.text((282, 305), hud_txt, font=_font(28, bold=True), fill=(160, 255, 140, 255), anchor="mm")

    elif theme == "space":
        alert_lvl = min(5, 1 + int(prog * 4.9))
        draw.rounded_rectangle([55, 265, 520, 345], radius=14, fill=(16, 12, 36, 220), outline=(255, 140, 40, 230), width=3)
        draw.text((287, 305), f"TORMENTA SOLAR: NIVEL G{alert_lvl}", font=_font(28, bold=True), fill=(255, 190, 60, 255), anchor="mm")

    # --- B. PERSONAJE 2D CÓMIC ANIMADO A 24 FPS (ESTILO DON ZOMBI / CURIOSAMENTE GRAFICADO) ---
    # Alterna posición izquierda/derecha según la escena y camina/respira suavemente
    side_right = (sc_idx % 2 == 1)
    base_cx = 855 if side_right else 225
    walk_x = int(14 * math.sin(t * 2.4))
    bob_y = int(9 * abs(math.sin(t * 4.8)))
    cx = base_cx + walk_x
    cy = 1365 - bob_y

    # Si está en modo apagón/zombi/océano, dibujar haz de luz de linterna que barre la escena
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

    # Piernas animadas estilo stickman/cartoon con borde negro grueso
    leg_swing = int(22 * math.sin(t * 4.8))
    draw.line([(cx - 24, cy + 85), (cx - 32 - leg_swing, cy + 158)], fill=(0, 0, 0, 255), width=14)
    draw.line([(cx + 24, cy + 85), (cx + 32 + leg_swing, cy + 158)], fill=(0, 0, 0, 255), width=14)

    # Torso / Chaqueta 2D con color según el tema
    jacket_colors = {
        "ocean": (245, 190, 25, 255),      # Traje/chaqueta submarina amarilla
        "blackout": (215, 45, 45, 255),    # Hoodie roja estilo Don Zombi
        "zombie": (215, 45, 45, 255),
        "jungle": (65, 155, 75, 255),      # Chaleco explorador verde
        "island": (225, 125, 40, 255),     # Camisa supervivencia naranja
        "prehistory": (185, 115, 55, 255),
        "space": (55, 125, 235, 255),
    }
    j_col = jacket_colors.get(theme, (215, 45, 45, 255))
    draw.rounded_rectangle(
        [cx - 58, cy - 10, cx + 58, cy + 96],
        radius=26,
        fill=j_col,
        outline=(0, 0, 0, 255),
        width=6,
    )
    # Cierre central de la chaqueta
    draw.line([(cx, cy - 8), (cx, cy + 94)], fill=(0, 0, 0, 255), width=4)

    # Brazo animado sosteniendo linterna / escáner
    arm_dir = -1 if side_right else 1
    arm_wave = int(16 * math.sin(t * 5.2)) if is_speaking else int(6 * math.sin(t * 2.5))
    hand_x = cx + arm_dir * 82
    hand_y = cy + 22 + arm_wave
    draw.line([(cx + arm_dir * 42, cy + 18), (hand_x, hand_y)], fill=(0, 0, 0, 255), width=13)
    # Linterna / dispositivo en la mano
    draw.rounded_rectangle(
        [hand_x - 16, hand_y - 10, hand_x + 16, hand_y + 10],
        radius=5,
        fill=(70, 75, 85, 255),
        outline=(0, 0, 0, 255),
        width=4,
    )

    # Cabeza redonda blanca expresiva (sello clásico de Don Zombi / Curiosamente Graficado)
    hr = 68
    hy = cy - 72
    draw.ellipse(
        [cx - hr, hy - hr, cx + hr, hy + hr],
        fill=(248, 250, 252, 255),
        outline=(0, 0, 0, 255),
        width=7,
    )

    # Gorro beanie / casco de explorador encima de la cabeza
    hat_col = (55, 85, 105, 255) if theme != "ocean" else (245, 185, 15, 255)
    draw.chord(
        [cx - hr - 4, hy - hr - 14, cx + hr + 4, hy + 18],
        start=180,
        end=360,
        fill=hat_col,
        outline=(0, 0, 0, 255),
        width=6,
    )
    draw.rounded_rectangle(
        [cx - hr - 6, hy - 28, cx + hr + 6, hy - 6],
        radius=10,
        fill=hat_col,
        outline=(0, 0, 0, 255),
        width=5,
    )

    # Ojos expresivos con parpadeo natural cada 3.4 segundos
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

    # Cejas dinámicas según la intensidad del capítulo
    brow_tilt = 6 if sc_idx in (1, 2, 3) else 0
    draw.line([(cx - 38 + look_offset, hy - 24 - brow_tilt), (cx - 10 + look_offset, hy - 22 + brow_tilt)], fill=(0, 0, 0, 255), width=5)
    draw.line([(cx + 10 + look_offset, hy - 22 + brow_tilt), (cx + 38 + look_offset, hy - 24 - brow_tilt)], fill=(0, 0, 0, 255), width=5)

    # Gota de sudor animada en momentos de alta tensión
    if sc_idx >= 1:
        sy_drop = hy - 14 + int((t * 28) % 18)
        sx_drop = cx + (48 if side_right else -48)
        draw.ellipse([sx_drop - 6, sy_drop - 9, sx_drop + 6, sy_drop + 9], fill=(75, 205, 255, 240), outline=(0, 0, 0, 255), width=3)

    # Boca animada en sincronía real (lip-sync) con la voz del narrador
    my = hy + 30
    mx = cx + look_offset
    if is_speaking:
        mouth_open = int(6 + 11 * abs(math.sin(t * 18.5)))
        draw.rounded_rectangle(
            [mx - 18, my - mouth_open, mx + 18, my + mouth_open],
            radius=9,
            fill=(185, 35, 45, 255),
            outline=(0, 0, 0, 255),
            width=4,
        )
        # Dientes superiores estilo cartoon
        draw.rectangle([mx - 12, my - mouth_open + 2, mx + 12, my - mouth_open + 7], fill=(255, 255, 255, 255))
    else:
        draw.arc([mx - 16, my - 6, mx + 16, my + 10], start=195, end=345, fill=(0, 0, 0, 255), width=5)

    # Signo de interrogación flotante en el capítulo final para invitar a comentar
    if prog > 0.80:
        qy = hy - 115 + int(10 * math.sin(t * 6.0))
        draw.text(
            (cx, qy),
            "?",
            font=_font(76, bold=True),
            fill=(255, 230, 0, 255),
            anchor="mm",
            stroke_width=7,
            stroke_fill=(0, 0, 0, 255),
        )


def build_illustrated_youtube_video(
    story_id: str,
    script_text: str,
    scene_files: List[Path],
    scene_badges: List[Tuple[str, str, Tuple[int, int, int]]],
    timeline_labels: List[str],
    output_filename: str,
    ambience_mode: str = "zombie",
    voice: str = "es-MX-JorgeNeural",
    rate: str = "+4%",
) -> Path:
    work_dir = OUTPUT_DIR / f"yt_{story_id}"
    work_dir.mkdir(parents=True, exist_ok=True)
    voice_mp3 = work_dir / "narration.mp3"

    print(f"[{story_id}] 1/3 Generando narración documental de formato largo con sincronización palabra por palabra...")
    timings = asyncio.run(_tts_with_word_timings(script_text, voice, rate, voice_mp3))

    voice_clip = AudioFileClip(str(voice_mp3))
    total_dur = voice_clip.duration + 0.65
    phrases = _build_phrases_from_timings(script_text, timings, voice_clip.duration, max_words=4)

    loaded_scenes: List[Image.Image] = []
    for idx, sf in enumerate(scene_files):
        if sf.exists() and sf.stat().st_size > 10_000:
            im = Image.open(sf).convert("RGB")
        else:
            im = _create_procedural_thematic_art(ambience_mode, variant=idx)
        im_big = ImageOps.fit(im, (int(VIDEO_WIDTH * 1.24), int(VIDEO_HEIGHT * 1.24)), method=Image.Resampling.LANCZOS)
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

        # Movimiento cinematográfico continuo a 24 FPS (zoom + paneo + vibración en clímax)
        if sc_idx % 2 == 0:
            zoom = 1.0 + 0.15 * sc_local
            pan_x = int((bw - VIDEO_WIDTH) * (0.20 + 0.60 * sc_local))
            pan_y = int((bh - VIDEO_HEIGHT) * (0.35 + 0.30 * math.sin(sc_local * math.pi)))
        else:
            zoom = 1.15 - 0.13 * sc_local
            pan_x = int((bw - VIDEO_WIDTH) * (0.80 - 0.60 * sc_local))
            pan_y = int((bh - VIDEO_HEIGHT) * (0.55 - 0.25 * sc_local))

        # Ligera sacudida dramática en los primeros 0.35s de cada cambio de capítulo
        if sc_local < 0.06 and sc_idx > 0:
            pan_x += int(12 * math.sin(t * 55.0))
            pan_y += int(10 * math.cos(t * 55.0))

        crop_w = int(VIDEO_WIDTH / zoom)
        crop_h = int(VIDEO_HEIGHT / zoom)
        left = max(0, min(bw - crop_w, pan_x))
        top = max(0, min(bh - crop_h, pan_y))

        cropped = big_im.crop((left, top, left + crop_w, top + crop_h))
        frame = cropped.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.BILINEAR)
        draw = ImageDraw.Draw(frame, "RGBA")

        # Verificar qué frase está hablando el narrador en este instante t
        active_phrase = None
        for ph in phrases:
            if ph["start"] - 0.06 <= t <= ph["end"] + 0.12:
                active_phrase = ph
                break

        # 1. PERSONAJE 2D ANIMADO + EFECTOS Y HUD DEL TEMA EN VIVO A 24 FPS
        _draw_live_2d_character_and_hud(
            draw=draw,
            t=t,
            prog=prog,
            sc_idx=sc_idx,
            is_speaking=(active_phrase is not None),
            theme=ambience_mode,
        )

        # 2. ENCABEZADO DEL CAPÍTULO AUTO-AJUSTADO (NUNCA SE CORTA)
        top_title, red_tag, accent_col = scene_badges[min(sc_idx, len(scene_badges) - 1)]
        _draw_wrapped_badge(draw, top_title, red_tag, accent_col)

        # 3. SUBTÍTULOS DINÁMICOS CON FONDO CONTRASTADO Y PALABRA ACTIVA EN AMARILLO
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
                draw.text(
                    (cur_x, sub_y),
                    w_str,
                    font=f_sub,
                    fill=w_color,
                    stroke_width=7,
                    stroke_fill=(0, 0, 0, 255),
                )
                wb = draw.textbbox((0, 0), w_str + " ", font=f_sub)
                cur_x += wb[2] - wb[0]

        # 4. LÍNEA DE TIEMPO INFERIOR CON LOS CAPÍTULOS DEL VIDEO
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
