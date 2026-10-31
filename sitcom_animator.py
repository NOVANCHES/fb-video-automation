"""
Motor de Animación Continua a 24 FPS (0 trabas) + Audio Multipista (Voces + Efectos + Música)
para "Idea 1: Comedia de Restaurante (POV y Humor Laboral)".

Cada fotograma se calcula matemáticamente en tiempo continuo `t` (24 cuadros por segundo reales),
garantizando movimiento 100% fluido de brazos, piernas, expresiones faciales, paneos de cámara,
zoom estilo 'The Office', cortes de pánico en la cocina con Sergio y Yashua, y cámara lenta final.
"""

import asyncio
import math
import struct
import wave
from pathlib import Path
from typing import Any, List, Tuple

import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import OUTPUT_DIR, VIDEO_HEIGHT, VIDEO_WIDTH

try:
    from moviepy import AudioFileClip, CompositeAudioClip, VideoClip
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import AudioFileClip, CompositeAudioClip, VideoClip
    MOVIEPY_V2 = False

FPS_SMOOTH = 24

# Cache de fuentes para renderizado ultrarrápido a 24 FPS
_FONT_CACHE = {}


def _font(size: int, bold: bool = True) -> Any:
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    candidates = (
        [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]
        if bold
        else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for c in candidates:
        if Path(c).exists():
            _FONT_CACHE[key] = ImageFont.truetype(c, size)
            return _FONT_CACHE[key]
    _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


def _generate_sfx_and_music_wav(wav_path: Path, total_duration: float = 32.0) -> Path:
    """
    Sintetiza una pista de audio de fondo continua con efectos de sonido sincronizados:
      - 0.0 - 4.0s: Ambiente tranquilo de restaurante cerrando
      - 4.0 - 4.7s: Campanilla de puerta "¡DING-DONG!" clara y brillante
      - 6.2 - 6.6s: Golpe cómico estilo 'The Office'
      - 10.5 - 21.0s: Pulso de tensión dramática en la cocina (latido + trémolo de suspenso)
      - 21.0 - 24.8s: Ritmo acelerado de comedia (corriendo con platos)
      - 25.0 - 27.8s: Redoble de expectativa al abrir la cuenta + sonido de moneditas (clink)
      - 28.0 - 32.0s: Melodía triste de violín/piano en cámara lenta cuando cae de rodillas
    """
    sample_rate = 22050
    num_samples = int(total_duration * sample_rate)
    t = np.linspace(0, total_duration, num_samples, endpoint=False)
    audio = np.zeros_like(t)

    # 1. Campanilla de puerta (Ding-Dong en t=4.0s y t=4.35s)
    m_ding = (t >= 4.0) & (t < 4.8)
    td = t[m_ding] - 4.0
    audio[m_ding] += 0.38 * np.sin(2 * np.pi * 987.77 * td) * np.exp(-5.0 * td)
    m_dong = (t >= 4.35) & (t < 5.3)
    td2 = t[m_dong] - 4.35
    audio[m_dong] += 0.38 * np.sin(2 * np.pi * 783.99 * td2) * np.exp(-4.0 * td2)

    # 2. Escena 2 (10.5s - 21.0s): Música de tensión dramática (bajo pulsante + cuerda tensa)
    m_s2 = (t >= 10.5) & (t < 21.0)
    ts2 = t[m_s2] - 10.5
    heartbeat = np.exp(-12.0 * ((ts2 * 2.2) % 1.0)) * np.sin(2 * np.pi * 65.4 * ts2)
    tremolo = (0.5 + 0.5 * np.sin(2 * np.pi * 10.0 * ts2)) * (
        np.sin(2 * np.pi * 220.0 * ts2) + 0.6 * np.sin(2 * np.pi * 233.08 * ts2)
    )
    audio[m_s2] += 0.16 * heartbeat + 0.06 * tremolo

    # 3. Escena 3A (21.0s - 24.8s): Cámara rápida corriendo (notas rápidas staccato)
    m_run = (t >= 21.0) & (t < 24.8)
    tr = t[m_run] - 21.0
    run_freqs = 330.0 + 110.0 * (np.floor(tr * 8.0) % 4)
    env_run = np.exp(-10.0 * ((tr * 8.0) % 1.0))
    audio[m_run] += 0.12 * np.sin(2 * np.pi * run_freqs * tr) * env_run

    # 4. Sonido de moneditas al abrir la cuenta (t=25.8s y 26.05s)
    for coin_t, freq in [(25.8, 2400.0), (26.05, 2750.0), (26.25, 2200.0)]:
        mc = (t >= coin_t) & (t < coin_t + 0.35)
        tc = t[mc] - coin_t
        audio[mc] += 0.25 * np.sin(2 * np.pi * freq * tc) * np.exp(-14.0 * tc)

    # 5. Escena 3B (27.8s - 32.0s): Canción triste de violín/piano en cámara lenta (Am -> F -> Dm -> E)
    sad_notes = [
        (27.8, 28.9, 440.0),   # A4
        (28.9, 30.0, 392.0),   # G4
        (30.0, 31.0, 349.23),  # F4
        (31.0, 32.0, 329.63),  # E4
    ]
    for n_start, n_end, f_note in sad_notes:
        mn = (t >= n_start) & (t < n_end)
        tn = t[mn] - n_start
        vibrato = 1.0 + 0.008 * np.sin(2 * np.pi * 5.5 * tn)
        env = np.minimum(1.0, tn / 0.15) * np.exp(-0.6 * tn)
        violin = (
            np.sin(2 * np.pi * f_note * vibrato * tn)
            + 0.4 * np.sin(2 * np.pi * 2 * f_note * vibrato * tn)
            + 0.2 * np.sin(2 * np.pi * 0.5 * f_note * tn)
        )
        audio[mn] += 0.16 * violin * env

    audio = np.clip(audio, -0.95, 0.95)
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return wav_path


async def _generate_segment_tts(text: str, voice: str, rate: str, out_path: Path) -> Path:
    comm = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await comm.save(str(out_path))
    return out_path


def _prepare_dialogue_clips(temp_dir: Path) -> List[Tuple[float, Path]]:
    """
    Genera las líneas de voz con sincronización exacta para cada momento de las 3 escenas.
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    segments = [
        # (start_sec, voice, rate, text, filename)
        (
            0.3,
            "es-MX-DaliaNeural",
            "+8%",
            "Cuando faltan cinco minutos para cerrar el turno, y por fin terminas de limpiar la última mesa.",
            "seg1_narrator.mp3",
        ),
        (
            6.3,
            "es-MX-JorgeNeural",
            "+5%",
            "¡Claro, pasen, bienvenidos! ¡Aquí tenemos mesa para todos!",
            "seg2_chucho_smile.mp3",
        ),
        (
            10.8,
            "es-MX-DaliaNeural",
            "+12%",
            "Corte rápido a la cocina con Sergio y Yashua.",
            "seg3_kitchen_intro.mp3",
        ),
        (
            13.8,
            "es-MX-JorgeNeural",
            "+10%",
            "Hermano... pidieron cinco cortes bien cocidos, ¡y la parrilla ya estaba apagada!",
            "seg4_chucho_panic.mp3",
        ),
        (
            21.2,
            "es-MX-DaliaNeural",
            "+10%",
            "Después de correr por todo el restaurante, abres la cuenta esperando una buena propina...",
            "seg5_tip_intro.mp3",
        ),
        (
            26.8,
            "es-MX-JorgeNeural",
            "-8%",
            "Tres pesos... y una servilleta que dice: excelente servicio, gracias.",
            "seg6_sad_ending.mp3",
        ),
    ]

    async def _run_all():
        tasks = [
            _generate_segment_tts(text, voice, rate, temp_dir / fname)
            for _, voice, rate, text, fname in segments
        ]
        await asyncio.gather(*tasks)

    asyncio.run(_run_all())
    return [(start_t, temp_dir / fname) for start_t, _, _, _, fname in segments]


def _draw_character(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    scale: float,
    name: str,
    role: str,
    expression: str,
    talk_phase: float,
    sweat: bool = False,
    wiping_phase: float | None = None,
    holding_shield_tray: bool = False,
    holding_spatula: bool = False,
    kneeling: bool = False,
) -> None:
    """
    Dibuja un personaje animado estilo serie animada moderna (Chucho, Sergio o Yashua)
    con movimientos fluidos continuos en cada fotograma `t`.
    """
    black = (18, 18, 22)
    skin = (242, 198, 160) if name != "Yashua" else (218, 168, 128)
    shirt_color = (35, 42, 55) if role == "waiter" else (245, 245, 248)
    apron_color = (20, 22, 28) if role == "waiter" else (180, 35, 35)

    # Sombra en el suelo
    draw.ellipse(
        [cx - int(110 * scale), cy + int(230 * scale), cx + int(110 * scale), cy + int(265 * scale)],
        fill=(0, 0, 0, 75),
    )

    # Piernas (animadas al correr o arrodilladas)
    leg_top = cy + int(110 * scale)
    if kneeling:
        # De rodillas en el suelo
        draw.rounded_rectangle(
            [cx - int(85 * scale), leg_top, cx - int(15 * scale), leg_top + int(95 * scale)],
            radius=16,
            fill=(28, 30, 38),
            outline=black,
            width=5,
        )
        draw.rounded_rectangle(
            [cx + int(15 * scale), leg_top, cx + int(85 * scale), leg_top + int(95 * scale)],
            radius=16,
            fill=(28, 30, 38),
            outline=black,
            width=5,
        )
    else:
        draw.rounded_rectangle(
            [cx - int(65 * scale), leg_top, cx - int(15 * scale), leg_top + int(140 * scale)],
            radius=16,
            fill=(28, 30, 38),
            outline=black,
            width=5,
        )
        draw.rounded_rectangle(
            [cx + int(15 * scale), leg_top, cx + int(65 * scale), leg_top + int(140 * scale)],
            radius=16,
            fill=(28, 30, 38),
            outline=black,
            width=5,
        )

    # Torso y mandil
    tx1, ty1 = cx - int(95 * scale), cy - int(45 * scale)
    tx2, ty2 = cx + int(95 * scale), cy + int(135 * scale)
    draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=int(42 * scale), fill=shirt_color, outline=black, width=6)
    draw.rounded_rectangle(
        [tx1 + int(18 * scale), ty1 + int(25 * scale), tx2 - int(18 * scale), ty2],
        radius=int(20 * scale),
        fill=apron_color,
        outline=black,
        width=5,
    )

    # Etiqueta con nombre en el pecho
    draw.rounded_rectangle(
        [cx - int(58 * scale), ty1 + int(38 * scale), cx + int(58 * scale), ty1 + int(72 * scale)],
        radius=8,
        fill=(255, 230, 0),
        outline=black,
        width=3,
    )
    draw.text((cx, ty1 + int(55 * scale)), name.upper(), font=_font(int(22 * scale)), fill=black, anchor="mm")

    # Cabeza con rebote suave de respiración
    bob = int(math.sin(talk_phase * 2.0) * 4 * scale)
    hx1, hy1 = cx - int(88 * scale), cy - int(225 * scale) + bob
    hx2, hy2 = cx + int(88 * scale), cy - int(35 * scale) + bob
    draw.rounded_rectangle([hx1, hy1, hx2, hy2], radius=int(75 * scale), fill=skin, outline=black, width=6)

    # Cabello o gorro de chef
    if role == "chef":
        # Gorro de cocinero blanco para Sergio
        draw.rounded_rectangle(
            [cx - int(80 * scale), hy1 - int(70 * scale), cx + int(80 * scale), hy1 + int(18 * scale)],
            radius=28,
            fill=(252, 252, 255),
            outline=black,
            width=5,
        )
    else:
        draw.pieslice(
            [hx1 - int(6 * scale), hy1 - int(18 * scale), hx2 + int(6 * scale), hy1 + int(95 * scale)],
            start=180,
            end=360,
            fill=(30, 24, 20),
            outline=black,
            width=5,
        )

    # Ojos y cejas según la expresión
    eye_y = hy1 + int(82 * scale)
    for idx_e, ex in enumerate((cx - int(34 * scale), cx + int(34 * scale))):
        if expression == "relief":
            # Ojos cerrados de alivio (arcos suaves)
            draw.arc(
                [ex - int(22 * scale), eye_y - int(10 * scale), ex + int(22 * scale), eye_y + int(18 * scale)],
                start=15,
                end=165,
                fill=black,
                width=int(6 * scale),
            )
        else:
            er = int(22 * scale) if expression in ("panic", "fake_smile", "shock") else int(18 * scale)
            draw.ellipse([ex - er, eye_y - er, ex + er, eye_y + er], fill=(255, 255, 255), outline=black, width=4)
            pr = int(8 * scale) if expression in ("panic", "fake_smile") else int(10 * scale)
            jitter_x = int(math.sin(talk_phase * 9.0) * 3 * scale) if expression == "panic" else 0
            draw.ellipse([ex - pr + jitter_x, eye_y - pr, ex + pr + jitter_x, eye_y + pr], fill=black)

        # Cejas
        ey_top = eye_y - int(32 * scale)
        if expression == "fake_smile":
            # Cejas arqueadas tensas estilo The Office
            slant = -10 if idx_e == 0 else 10
            draw.line(
                [(ex - int(24 * scale), ey_top + slant), (ex + int(24 * scale), ey_top - slant)],
                fill=black,
                width=int(7 * scale),
            )
        elif expression in ("panic", "sad"):
            slant = -12 if idx_e == 0 else 12
            draw.line(
                [(ex - int(24 * scale), ey_top - slant), (ex + int(24 * scale), ey_top + slant)],
                fill=black,
                width=int(7 * scale),
            )
        else:
            draw.line(
                [(ex - int(22 * scale), ey_top), (ex + int(22 * scale), ey_top)],
                fill=black,
                width=int(6 * scale),
            )

    # Boca expresiva y sincronizada
    my = hy2 - int(44 * scale)
    if expression == "fake_smile":
        # Sonrisa gigante y exagerada mostrando dientes apretados + tic nervioso
        mw, mh = int(58 * scale), int(28 * scale)
        draw.rounded_rectangle([cx - mw, my - mh // 2, cx + mw, my + mh], radius=16, fill=(255, 255, 255), outline=black, width=5)
        draw.line([(cx - mw + 6, my + 4), (cx + mw - 6, my + 4)], fill=black, width=3)
        for tx in range(cx - mw + int(18 * scale), cx + mw - int(10 * scale), max(8, int(18 * scale))):
            draw.line([(tx, my - mh // 2 + 4), (tx, my + mh - 4)], fill=black, width=3)
    elif expression == "relief":
        draw.arc([cx - int(26 * scale), my - int(12 * scale), cx + int(26 * scale), my + int(16 * scale)], start=10, end=170, fill=black, width=5)
    elif expression == "sad":
        draw.arc([cx - int(30 * scale), my - int(6 * scale), cx + int(30 * scale), my + int(28 * scale)], start=195, end=345, fill=black, width=6)
    else:
        open_amt = int((0.4 + 0.6 * abs(math.sin(talk_phase * 6.5))) * 22 * scale)
        draw.ellipse([cx - int(24 * scale), my - open_amt, cx + int(24 * scale), my + open_amt], fill=(170, 35, 45), outline=black, width=4)

    # Gotas de sudor frío animadas (caen continuamente con `talk_phase`)
    if sweat:
        drop_y = hy1 + int(35 * scale) + int(((talk_phase * 45) % 55) * scale)
        drop_x = hx2 - int(18 * scale)
        draw.ellipse([drop_x - int(8 * scale), drop_y, drop_x + int(8 * scale), drop_y + int(22 * scale)], fill=(70, 195, 255), outline=black, width=3)

    # Brazos y accesorios animados
    if wiping_phase is not None:
        # Brazo limpiando la mesa de izquierda a derecha continuamente
        wipe_x = cx + int(math.sin(wiping_phase * 5.0) * 115 * scale)
        wipe_y = cy + int(95 * scale)
        draw.line([(cx + int(65 * scale), cy + int(5 * scale)), (wipe_x, wipe_y)], fill=shirt_color, width=int(26 * scale))
        # Trapo amarillo limpiando con destellos de limpieza
        draw.rounded_rectangle([wipe_x - 36, wipe_y - 16, wipe_x + 36, wipe_y + 18], radius=10, fill=(255, 230, 40), outline=black, width=4)
    elif holding_shield_tray:
        # Yashua sosteniendo la charola vacía como si fuera un escudo
        sh_x = cx - int(55 * scale) + int(math.sin(talk_phase * 14.0) * 5 * scale)
        sh_y = cy + int(20 * scale)
        r_tray = int(92 * scale)
        draw.ellipse([sh_x - r_tray, sh_y - r_tray, sh_x + r_tray, sh_y + r_tray], fill=(195, 205, 215), outline=black, width=6)
        draw.ellipse([sh_x - int(68 * scale), sh_y - int(68 * scale), sh_x + int(68 * scale), sh_y + int(68 * scale)], fill=(225, 232, 240), outline=black, width=4)
    elif holding_spatula:
        # Sergio con espátula temblando
        sp_x = cx + int(105 * scale)
        sp_y = cy - int(20 * scale) + int(math.sin(talk_phase * 12.0) * 8 * scale)
        draw.line([(cx + int(75 * scale), cy + int(20 * scale)), (sp_x, sp_y - int(70 * scale))], fill=black, width=8)
        draw.rectangle([sp_x - 22, sp_y - int(115 * scale), sp_x + 22, sp_y - int(65 * scale)], fill=(200, 210, 220), outline=black, width=4)
    elif kneeling:
        # Brazos levantados al cielo en cámara lenta dramática
        draw.line([(cx - int(75 * scale), cy), (cx - int(130 * scale), cy - int(135 * scale))], fill=shirt_color, width=int(26 * scale))
        draw.line([(cx + int(75 * scale), cy), (cx + int(130 * scale), cy - int(135 * scale))], fill=shirt_color, width=int(26 * scale))


def _draw_top_pov_banner(draw: ImageDraw.ImageDraw, text: str, subtext: str = "") -> None:
    """Banner superior limpio estilo POV de Reels/TikTok."""
    draw.rounded_rectangle([55, 85, VIDEO_WIDTH - 55, 245 if subtext else 195], radius=26, fill=(12, 14, 20), outline=(255, 220, 0), width=4)
    draw.text((VIDEO_WIDTH // 2, 140), text, font=_font(38, bold=True), fill=(255, 255, 255), anchor="mm")
    if subtext:
        draw.text((VIDEO_WIDTH // 2, 198), subtext, font=_font(32, bold=True), fill=(255, 225, 0), anchor="mm")


def _draw_subtitle_pill(draw: ImageDraw.ImageDraw, text: str, highlight_color: Tuple[int, int, int] = (255, 230, 0)) -> None:
    if not text:
        return
    draw.rounded_rectangle([65, 1610, VIDEO_WIDTH - 65, 1795], radius=28, fill=(10, 12, 18), outline=highlight_color, width=5)
    lines = text.split("\n")
    if len(lines) == 1:
        draw.text((VIDEO_WIDTH // 2, 1702), lines[0], font=_font(44, bold=True), fill=highlight_color, anchor="mm")
    else:
        draw.text((VIDEO_WIDTH // 2, 1672), lines[0], font=_font(42, bold=True), fill=(255, 255, 255), anchor="mm")
        draw.text((VIDEO_WIDTH // 2, 1735), lines[1], font=_font(44, bold=True), fill=highlight_color, anchor="mm")


def make_sitcom_frame(t: float) -> np.ndarray:
    """
    Genera el fotograma exacto en el instante `t` (a 24 FPS continuos sin pausas):
      - Escena 1 (0.0s - 10.5s): La entrada triunfal (limpiando mesa -> campanilla + clientes -> zoom The Office).
      - Escena 2 (10.5s - 21.0s): El cónclave en la cocina (Sergio, Yashua con charola-escudo y Chucho en pánico).
      - Escena 3 (21.0s - 32.0s): El desenlace de la propina (cámara rápida -> monedas + servilleta -> rodillas slow-mo).
    """
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (28, 24, 34))
    draw = ImageDraw.Draw(img)

    # =========================================================================
    # ESCENA 1: LA ENTRADA TRIUNFAL (0.0s a 10.5s)
    # =========================================================================
    if t < 10.5:
        # Paredes cálidas de restaurante nocturno + piso de madera
        draw.rectangle([0, 0, VIDEO_WIDTH, 1280], fill=(48, 34, 32))
        draw.rectangle([0, 1280, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(72, 48, 34))
        for px in range(0, VIDEO_WIDTH, 135):
            draw.line([(px, 1280), (px - 60, VIDEO_HEIGHT)], fill=(52, 34, 24), width=4)

        # Reloj de pared marcando 10:55 PM (faltan 5 min para las 11:00 PM)
        draw.ellipse([110, 310, 260, 460], fill=(248, 245, 235), outline=(20, 20, 20), width=6)
        draw.line([(185, 385), (150, 355)], fill=(20, 20, 20), width=6)
        draw.line([(185, 385), (175, 325)], fill=(220, 40, 40), width=5)
        draw.text((185, 492), "10:55 PM", font=_font(28, bold=True), fill=(255, 225, 130), anchor="mm")

        # Puerta de entrada al fondo con campanilla
        door_open = min(1.0, max(0.0, (t - 4.0) / 0.8)) if t >= 4.0 else 0.0
        draw.rectangle([680, 320, 995, 980], fill=(22, 30, 48), outline=(120, 85, 50), width=10)
        # Campanilla dorada vibrando cuando t >= 4.0
        bell_shake = int(math.sin(t * 45.0) * 10) if 4.0 <= t < 5.5 else 0
        draw.ellipse([815 + bell_shake, 265, 865 + bell_shake, 315], fill=(255, 215, 0), outline=(20, 20, 20), width=4)
        if 4.0 <= t < 5.8:
            draw.rounded_rectangle([620, 250, 1045, 330], radius=18, fill=(255, 230, 0), outline=(0, 0, 0), width=4)
            draw.text((832, 290), "¡DING - DONG! (5 CLIENTES)", font=_font(30, bold=True), fill=(0, 0, 0), anchor="mm")

        # Grupo grande de 5 clientes entrando cuando t >= 4.2
        if t >= 4.2:
            walk_prog = min(1.0, (t - 4.2) / 2.2)
            for c_idx in range(5):
                cx_cust = int(930 - walk_prog * 220 + (c_idx - 2) * 58)
                cy_cust = int(680 + (c_idx % 2) * 55 + abs(math.sin(t * 10.0 + c_idx)) * 14)
                draw.ellipse([cx_cust - 34, cy_cust - 85, cx_cust + 34, cy_cust - 17], fill=(235, 190, 155), outline=(0, 0, 0), width=4)
                draw.rounded_rectangle([cx_cust - 42, cy_cust - 17, cx_cust + 42, cy_cust + 95], radius=18, fill=(60 + c_idx * 30, 90, 160), outline=(0, 0, 0), width=4)

        # Mesa en primer plano
        draw.rounded_rectangle([140, 1120, 940, 1210], radius=22, fill=(140, 82, 45), outline=(20, 20, 20), width=6)

        if t < 4.0:
            # Limpiando la mesa con cara de alivio absoluto
            _draw_character(
                draw,
                cx=460,
                cy=980,
                scale=1.25,
                name="Chucho",
                role="waiter",
                expression="relief",
                talk_phase=t,
                wiping_phase=t,
            )
            _draw_top_pov_banner(draw, "POV: Cuando faltan 5 minutos", "para cerrar el turno...")
            _draw_subtitle_pill(draw, "Por fin limpiando la última mesa...\n¡En 5 minutos nos vamos!")
        elif t < 6.2:
            # Pausa dramática al escuchar la campanilla
            _draw_character(
                draw,
                cx=460,
                cy=980,
                scale=1.25,
                name="Chucho",
                role="waiter",
                expression="shock",
                talk_phase=t,
                sweat=True,
            )
            _draw_top_pov_banner(draw, "Cuando faltan 5 minutos para cerrar", "*Suena la campanilla de la puerta*")
            _draw_subtitle_pill(draw, "*¡DING-DONG!* Entra un grupo\nde 5 personas a las 10:55 PM")
        else:
            # ZOOM ESTILO THE OFFICE a la cara de Chucho con la sonrisa más grande y falsa del mundo
            zoom_prog = min(1.0, (t - 6.2) / 0.45)
            char_scale = 1.25 + 0.85 * zoom_prog
            char_cy = int(980 + 240 * zoom_prog)
            _draw_character(
                draw,
                cx=540,
                cy=char_cy,
                scale=char_scale,
                name="Chucho",
                role="waiter",
                expression="fake_smile",
                talk_phase=t,
                sweat=True,
            )
            _draw_top_pov_banner(draw, "Mirada a la cámara estilo The Office", "Sonrisa 100% falsa activada")
            _draw_subtitle_pill(draw, "\"¡CLARO, PASEN!\n¡AQUÍ TENEMOS MESA!\"")

    # =========================================================================
    # ESCENA 2: EL CÓNCLAVE EN LA COCINA (10.5s a 21.0s)
    # =========================================================================
    elif t < 21.0:
        # Fondo de cocina metálica + puerta abatible con ventanilla circular
        draw.rectangle([0, 0, VIDEO_WIDTH, 1300], fill=(38, 46, 54))
        for gy in range(260, 1280, 110):
            draw.line([(0, gy), (VIDEO_WIDTH, gy)], fill=(52, 62, 72), width=3)
        draw.rectangle([0, 1300, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(45, 48, 52))

        # Parrilla al fondo con letrero "PARRILLA APAGADA / FRÍA"
        draw.rounded_rectangle([580, 360, 1020, 620], radius=16, fill=(25, 28, 32), outline=(0, 0, 0), width=5)
        draw.rounded_rectangle([610, 390, 990, 470], radius=10, fill=(200, 35, 35), outline=(255, 255, 255), width=3)
        draw.text((800, 430), "PARRILLA: APAGADA", font=_font(30, bold=True), fill=(255, 255, 255), anchor="mm")

        # Puerta abatible de cocina a la izquierda
        draw.rectangle([30, 310, 360, 1290], fill=(160, 170, 180), outline=(20, 20, 20), width=6)
        draw.ellipse([125, 460, 265, 600], fill=(22, 28, 38), outline=(20, 20, 20), width=6)

        # Cortes rápidos estilo pánico entre los 3 compañeros y plano grupal
        local_t = t - 10.5
        shake_x = int(math.sin(t * 32.0) * 6)
        if local_t < 3.2:
            # Plano de los 3 escondidos detrás de la puerta (Sergio, Yashua con charola-escudo y Chucho)
            _draw_character(draw, cx=230 + shake_x, cy=1050, scale=0.92, name="Sergio", role="chef", expression="panic", talk_phase=t, sweat=True, holding_spatula=True)
            _draw_character(draw, cx=830 - shake_x, cy=1050, scale=0.95, name="Yashua", role="waiter", expression="panic", talk_phase=t, sweat=True, holding_shield_tray=True)
            _draw_character(draw, cx=530 + shake_x, cy=1110, scale=1.08, name="Chucho", role="waiter", expression="panic", talk_phase=t, sweat=True)
            _draw_top_pov_banner(draw, "ESCENA 2: El cónclave en la cocina", "Escondidos con Sergio y Yashua")
            _draw_subtitle_pill(draw, "Yashua usando la charola como escudo\nmientras entramos en pánico")
        elif local_t < 6.8:
            # Corte rápido a primer plano de Chucho sudando frío + Yashua atrás con el escudo
            _draw_character(draw, cx=820, cy=1020, scale=1.0, name="Yashua", role="waiter", expression="panic", talk_phase=t, sweat=True, holding_shield_tray=True)
            _draw_character(draw, cx=420 + shake_x, cy=1080, scale=1.35, name="Chucho", role="waiter", expression="panic", talk_phase=t, sweat=True)
            _draw_top_pov_banner(draw, "Pánico total en la cocina", "*Música de tensión dramática*")
            _draw_subtitle_pill(draw, "\"Pidieron 5 cortes BIEN COCIDOS...\"\n(Sudando frío)", highlight_color=(255, 95, 95))
        else:
            # Corte rápido de impacto: ¡La parrilla ya estaba apagada!
            _draw_character(draw, cx=260 - shake_x, cy=1040, scale=1.05, name="Sergio", role="chef", expression="panic", talk_phase=t, sweat=True, holding_spatula=True)
            _draw_character(draw, cx=780 + shake_x, cy=1040, scale=1.05, name="Yashua", role="waiter", expression="panic", talk_phase=t, sweat=True, holding_shield_tray=True)
            _draw_character(draw, cx=520 + shake_x, cy=1140, scale=1.22, name="Chucho", role="waiter", expression="panic", talk_phase=t, sweat=True)
            _draw_top_pov_banner(draw, "ALERTA ROJA EN LA PARRILLA", "5 Cortes Bien Cocidos a las 11 PM")
            _draw_subtitle_pill(draw, "\"¡...Y LA PARRILLA YA\nESTABA APAGADA!\"", highlight_color=(255, 220, 0))

    # =========================================================================
    # ESCENA 3: EL DESENLACE DE LA PROPINA (21.0s a 32.0s)
    # =========================================================================
    else:
        local_t = t - 21.0
        if local_t < 3.8:
            # SUB-ESCENA 3A: Cámara rápida de Chucho corriendo de un lado a otro con platos y jarras
            draw.rectangle([0, 0, VIDEO_WIDTH, 1280], fill=(48, 34, 32))
            draw.rectangle([0, 1280, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(72, 48, 34))
            # Líneas de velocidad horizontales animadas
            for ly in range(360, 1450, 90):
                lx1 = int(((t * 1400 + ly * 7) % (VIDEO_WIDTH + 300)) - 300)
                draw.line([(lx1, ly), (lx1 + 220, ly)], fill=(255, 235, 120), width=5)

            run_x = int(540 + math.sin(t * 9.5) * 310)
            run_y = int(1020 + abs(math.cos(t * 19.0)) * 38)
            _draw_character(draw, cx=run_x, cy=run_y, scale=1.18, name="Chucho", role="waiter", expression="panic", talk_phase=t * 2.0, sweat=True)
            # Platos volando en las manos
            draw.ellipse([run_x - 190, run_y - 35, run_x - 70, run_y + 15], fill=(245, 245, 245), outline=(0, 0, 0), width=4)
            draw.ellipse([run_x + 70, run_y - 35, run_x + 190, run_y + 15], fill=(245, 245, 245), outline=(0, 0, 0), width=4)
            _draw_top_pov_banner(draw, "MODO TURBO ACTIVADO (x4)", "Sirviendo los 5 cortes y rellenando vasos")
            _draw_subtitle_pill(draw, "Corriendo por todo el salón\npara dar el mejor servicio...")

        elif local_t < 7.2:
            # SUB-ESCENA 3B: Zoom extremo al abrir la cuenta -> monedas + servilleta "Excelente servicio, gracias"
            draw.rectangle([0, 0, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(32, 24, 28))
            zoom_p = min(1.0, (local_t - 3.8) / 1.2)
            # Carpeta negra de la cuenta abierta en primer plano
            pad = int(45 * (1.0 - 0.25 * zoom_p))
            draw.rounded_rectangle([65 + pad, 340, VIDEO_WIDTH - 65 - pad, 1480], radius=32, fill=(22, 24, 30), outline=(255, 215, 0), width=6)
            draw.line([(VIDEO_WIDTH // 2, 360), (VIDEO_WIDTH // 2, 1460)], fill=(55, 58, 68), width=5)

            # Servilleta blanca con texto escrito a mano
            draw.rounded_rectangle([135, 470, 945, 980], radius=18, fill=(250, 248, 242), outline=(180, 180, 175), width=4)
            draw.text((540, 620), "\"Excelente servicio,", font=_font(56, bold=True), fill=(25, 45, 130), anchor="mm")
            draw.text((540, 710), "muchas gracias :)\"", font=_font(56, bold=True), fill=(25, 45, 130), anchor="mm")
            draw.text((540, 845), "— Mesa 4 (Cuenta de $2,850)", font=_font(34, bold=False), fill=(110, 110, 110), anchor="mm")

            # Solo 3 moneditas de $1 peso brillando abajo
            for m_idx, mx in enumerate([330, 540, 750]):
                my_coin = 1210 + int(math.sin(t * 6.0 + m_idx) * 6)
                draw.ellipse([mx - 72, my_coin - 72, mx + 72, my_coin + 72], fill=(215, 175, 55), outline=(0, 0, 0), width=5)
                draw.ellipse([mx - 54, my_coin - 54, mx + 54, my_coin + 54], fill=(245, 208, 85), outline=(120, 90, 20), width=3)
                draw.text((mx, my_coin), "$1", font=_font(48, bold=True), fill=(0, 0, 0), anchor="mm")

            _draw_top_pov_banner(draw, "El momento de la verdad...", "Abres la carpeta esperando la propina")
            _draw_subtitle_pill(draw, "Solo 3 moneditas y una servilleta:\n\"Excelente servicio, gracias\"", highlight_color=(255, 215, 0))

        else:
            # SUB-ESCENA 3C: Cámara lenta dramática en blanco y negro/azul triste, cayendo de rodillas bajo la lluvia
            draw.rectangle([0, 0, VIDEO_WIDTH, 1320], fill=(22, 28, 42))
            draw.rectangle([0, 1320, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(32, 38, 52))
            # Reflector solitario sobre Chucho
            draw.polygon([(540, 180), (160, 1520), (920, 1520)], fill=(46, 58, 82))

            drop_offset = min(140, int((local_t - 7.2) * 85))
            _draw_character(
                draw,
                cx=540,
                cy=1060 + drop_offset,
                scale=1.32,
                name="Chucho",
                role="waiter",
                expression="sad",
                talk_phase=t * 0.4,
                kneeling=True,
            )

            # Lluvia dramática cayendo continuamente en cámara lenta
            for r_idx in range(36):
                rx = (r_idx * 97) % VIDEO_WIDTH
                ry = int((t * 360 + r_idx * 173) % 1550)
                draw.line([(rx, ry), (rx - 8, ry + 55)], fill=(150, 195, 255), width=3)

            _draw_top_pov_banner(draw, "*Suena canción triste en cámara lenta*", "Soldado caído en cierre de turno")
            _draw_subtitle_pill(draw, "Te dejas caer de rodillas...\n\"Gracias por los 3 pesos\"", highlight_color=(135, 205, 255))

    return np.asarray(img)


def render_restaurant_comedy_video(output_path: Path = OUTPUT_DIR / "comedia_restaurante_pov.mp4") -> Path:
    """
    Ensambla el video completo de 32 segundos a 24 FPS continuos (768 fotogramas únicos sin trabas)
    con voces sincronizadas, efectos de sonido (campanilla, monedas) y música dramática.
    """
    total_duration = 32.0
    temp_audio_dir = OUTPUT_DIR / "sitcom_audio"
    temp_audio_dir.mkdir(parents=True, exist_ok=True)

    print("[1/3] Sintetizando voces de personajes y narración (Chucho + Narradora)...")
    dialogue_items = _prepare_dialogue_clips(temp_audio_dir)

    print("[2/3] Generando banda sonora y efectos (campanilla, tensión en cocina, monedas y violín triste)...")
    bg_wav = _generate_sfx_and_music_wav(temp_audio_dir / "bg_sfx.wav", total_duration=total_duration)

    audio_tracks = [AudioFileClip(str(bg_wav))]
    for start_sec, mp3_path in dialogue_items:
        clip_a = AudioFileClip(str(mp3_path))
        if MOVIEPY_V2:
            clip_a = clip_a.with_start(start_sec)
        else:
            clip_a = clip_a.set_start(start_sec)
        audio_tracks.append(clip_a)

    comp_audio = CompositeAudioClip(audio_tracks)
    if MOVIEPY_V2:
        comp_audio = comp_audio.with_duration(total_duration)
    else:
        comp_audio = comp_audio.set_duration(total_duration)

    print(f"[3/3] Renderizando animación continua a {FPS_SMOOTH} FPS reales (768 cuadros fluidos sin trabas)...")
    for idx_p, sample_t in enumerate([2.0, 7.5, 15.0, 26.0, 29.5], start=1):
        arr = make_sitcom_frame(sample_t)
        Image.fromarray(arr).save(OUTPUT_DIR / f"sitcom_preview_{idx_p}.jpg", quality=93)

    video_clip = VideoClip(make_sitcom_frame, duration=total_duration)
    if MOVIEPY_V2:
        video_clip = video_clip.with_audio(comp_audio)
    else:
        video_clip = video_clip.set_audio(comp_audio)

    video_clip.write_videofile(
        str(output_path),
        fps=FPS_SMOOTH,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger=None,
    )

    video_clip.close()
    comp_audio.close()
    for tr in audio_tracks:
        tr.close()

    print(f"      ¡Video de comedia animado exportado exitosamente en: {output_path}!")
    return output_path


def _prepare_ep2_dialogue_clips(temp_dir: Path) -> List[Tuple[float, Path]]:
    temp_dir.mkdir(parents=True, exist_ok=True)
    segments = [
        (
            0.3,
            "es-MX-DaliaNeural",
            "+8%",
            "Cuando atiendes una mesa de diez personas que se cambiaron de silla toda la noche, y preguntas cómo va a ser la cuenta.",
            "ep2_seg1.mp3",
        ),
        (
            6.5,
            "es-MX-JorgeNeural",
            "+6%",
            "¿Quieren todo junto en una sola cuenta? ... ¿O diez cuentas separadas?",
            "ep2_seg2.mp3",
        ),
        (
            11.0,
            "es-MX-DaliaNeural",
            "+10%",
            "En la caja, Sergio y Yashua intentan descifrar las matemáticas imposibles.",
            "ep2_seg3.mp3",
        ),
        (
            14.8,
            "es-MX-JorgeNeural",
            "+10%",
            "¡Yashua! ¡Piden dividir los nachos entre tres, pero el de azul dice que él solo tomó agua!",
            "ep2_seg4.mp3",
        ),
        (
            21.2,
            "es-MX-DaliaNeural",
            "+10%",
            "Después de cobrar nueve tarjetas diferentes, falta un corte de seiscientos pesos que nadie reconoce...",
            "ep2_seg5.mp3",
        ),
        (
            27.2,
            "es-MX-JorgeNeural",
            "-6%",
            "¿Quién se comió el Ribeye fantasma? ... Nadie fue.",
            "ep2_seg6.mp3",
        ),
    ]

    async def _run_all():
        tasks = [
            _generate_segment_tts(text, voice, rate, temp_dir / fname)
            for _, voice, rate, text, fname in segments
        ]
        await asyncio.gather(*tasks)

    asyncio.run(_run_all())
    return [(start_t, temp_dir / fname) for start_t, _, _, _, fname in segments]


def make_ep2_frame(t: float) -> np.ndarray:
    """
    Episodio 2 a 24 FPS continuos: "Cuentas Separadas y el Ribeye Fantasma"
      - Escena 1 (0.0s - 10.5s): Mesa gigante que se cambia de silla + "¡10 cuentas separadas!" + Zoom The Office con ecuaciones.
      - Escena 2 (10.5s - 21.0s): Cónclave en caja con Sergio y Yashua con tickets de 2 metros y calculadora echando humo.
      - Escena 3 (21.0s - 32.0s): Cobrando 10 tarjetas en cámara rápida + "El Ribeye Fantasma de $650" + caída dramática slow-mo.
    """
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (28, 24, 34))
    draw = ImageDraw.Draw(img)

    if t < 10.5:
        draw.rectangle([0, 0, VIDEO_WIDTH, 1280], fill=(44, 32, 38))
        draw.rectangle([0, 1280, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(68, 46, 34))

        # Clientes al fondo intercambiando lugares continuamente (movimiento sinusoidal cruzado)
        for c_idx in range(6):
            swap_x = int(540 + math.sin(t * 3.5 + c_idx * 1.1) * 360)
            swap_y = int(560 + (c_idx % 2) * 75 + abs(math.cos(t * 7.0 + c_idx)) * 12)
            draw.ellipse([swap_x - 32, swap_y - 80, swap_x + 32, swap_y - 16], fill=(235, 192, 155), outline=(0, 0, 0), width=4)
            draw.rounded_rectangle([swap_x - 40, swap_y - 16, swap_x + 40, swap_y + 90], radius=16, fill=(50 + c_idx * 32, 110, 175), outline=(0, 0, 0), width=4)

        draw.rounded_rectangle([90, 650, 990, 740], radius=20, fill=(140, 82, 45), outline=(20, 20, 20), width=6)

        if t < 6.0:
            _draw_character(draw, cx=540, cy=1050, scale=1.22, name="Chucho", role="waiter", expression="relief", talk_phase=t)
            _draw_top_pov_banner(draw, "POV: Mesa de 10 personas", "Se cambiaron de silla 4 veces")
            _draw_subtitle_pill(draw, "Llegas con la cuenta y haces\nla pregunta más peligrosa...")
        else:
            zoom_p = min(1.0, (t - 6.0) / 0.5)
            _draw_character(draw, cx=540, cy=int(1050 + 200 * zoom_p), scale=1.22 + 0.78 * zoom_p, name="Chucho", role="waiter", expression="fake_smile", talk_phase=t, sweat=True)
            # Ecuaciones matemáticas flotando alrededor de Chucho estilo meme
            formulas = ["$3,890 / 9.5?", "Nachos ÷ 3 - Queso", "Agua = $0?", "Ribeye = ¿?"]
            for f_i, form_txt in enumerate(formulas):
                fx = int(190 + (f_i % 2) * 690 + math.sin(t * 4.0 + f_i) * 24)
                fy = int(420 + (f_i // 2) * 280 + math.cos(t * 3.5 + f_i) * 18)
                draw.text((fx, fy), form_txt, font=_font(34, bold=True), fill=(255, 235, 80), anchor="mm")
            _draw_top_pov_banner(draw, "\"¡10 CUENTAS SEPARADAS!\"", "Zoom estilo The Office al mesero")
            _draw_subtitle_pill(draw, "\"Y los nachos del centro\nlos divides entre 3 sin el queso\"")

    elif t < 21.0:
        draw.rectangle([0, 0, VIDEO_WIDTH, 1300], fill=(36, 44, 54))
        draw.rectangle([0, 1300, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(45, 48, 52))
        shake_x = int(math.sin(t * 30.0) * 6)

        _draw_character(draw, cx=240 + shake_x, cy=1050, scale=0.96, name="Sergio", role="chef", expression="panic", talk_phase=t, sweat=True, holding_spatula=True)
        _draw_character(draw, cx=830 - shake_x, cy=1050, scale=0.96, name="Yashua", role="waiter", expression="panic", talk_phase=t, sweat=True, holding_shield_tray=True)
        _draw_character(draw, cx=535 + shake_x, cy=1110, scale=1.18, name="Chucho", role="waiter", expression="panic", talk_phase=t, sweat=True)

        # Ticket gigante de 2 metros ondeando en pantalla
        ticket_wave = int(math.sin(t * 8.0) * 18)
        draw.rounded_rectangle([370 + ticket_wave, 290, 710 + ticket_wave, 770], radius=12, fill=(250, 248, 240), outline=(0, 0, 0), width=5)
        draw.text((540 + ticket_wave, 355), "MESA 8 - DIVIDIR:", font=_font(28, bold=True), fill=(0, 0, 0), anchor="mm")
        draw.text((540 + ticket_wave, 430), "1/3 Nachos: $63.33", font=_font(26, bold=False), fill=(40, 40, 40), anchor="mm")
        draw.text((540 + ticket_wave, 495), "2/7 Jarra: $41.14", font=_font(26, bold=False), fill=(40, 40, 40), anchor="mm")
        draw.text((540 + ticket_wave, 575), "1 RIBEYE: ¿DE QUIÉN?", font=_font(28, bold=True), fill=(210, 30, 30), anchor="mm")

        _draw_top_pov_banner(draw, "Caos matemático con Sergio y Yashua", "Dividiendo fracciones de nachos")
        _draw_subtitle_pill(draw, "\"¡El de azul dice que solo tomó agua\ny se comió medio corte!\"", highlight_color=(255, 110, 110))

    else:
        local_t = t - 21.0
        if local_t < 5.5:
            draw.rectangle([0, 0, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(32, 26, 36))
            # Terminal bancaria pasando 10 tarjetas a toda velocidad
            card_x = int(540 + math.sin(t * 14.0) * 240)
            draw.rounded_rectangle([340, 520, 740, 1080], radius=36, fill=(40, 45, 55), outline=(0, 0, 0), width=6)
            draw.rounded_rectangle([380, 575, 700, 760], radius=16, fill=(140, 245, 160), outline=(0, 0, 0), width=4)
            draw.text((540, 640), f"TARJETA #{min(9, int(local_t * 2) + 1)}/10", font=_font(36, bold=True), fill=(0, 0, 0), anchor="mm")
            draw.text((540, 705), "FALTA: $650.00", font=_font(34, bold=True), fill=(190, 20, 20), anchor="mm")
            # Tarjeta deslizándose continuamente
            draw.rounded_rectangle([card_x - 150, 1150, card_x + 150, 1330], radius=22, fill=(35, 115, 235), outline=(255, 255, 255), width=5)
            _draw_top_pov_banner(draw, "Pasando 9 tarjetas diferentes...", "¡Y sobra un corte que nadie reconoce!")
            _draw_subtitle_pill(draw, "Cuando ya cobraste a todos\ny falta el Ribeye de $650...")
        else:
            draw.rectangle([0, 0, VIDEO_WIDTH, 1320], fill=(22, 28, 42))
            draw.rectangle([0, 1320, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(32, 38, 52))
            draw.polygon([(540, 180), (160, 1520), (920, 1520)], fill=(46, 58, 82))
            drop_offset = min(140, int((local_t - 5.5) * 65))
            _draw_character(draw, cx=540, cy=1060 + drop_offset, scale=1.32, name="Chucho", role="waiter", expression="sad", talk_phase=t * 0.4, kneeling=True)
            for r_idx in range(36):
                rx = (r_idx * 97) % VIDEO_WIDTH
                ry = int((t * 360 + r_idx * 173) % 1550)
                draw.line([(rx, ry), (rx - 8, ry + 55)], fill=(150, 195, 255), width=3)
            _draw_top_pov_banner(draw, "El misterio del Ribeye Fantasma", "*Canción triste en cámara lenta*")
            _draw_subtitle_pill(draw, "\"¿Quién pidió el corte?...\"\nAbsolutamente nadie fue.", highlight_color=(135, 205, 255))

    return np.asarray(img)


def render_restaurant_comedy_ep2(output_path: Path = OUTPUT_DIR / "comedia_restaurante_ep2.mp4") -> Path:
    total_duration = 32.0
    temp_audio_dir = OUTPUT_DIR / "sitcom_audio_ep2"
    temp_audio_dir.mkdir(parents=True, exist_ok=True)

    print("[EP2 1/3] Sintetizando voces de personajes (Episodio 2: Cuentas Separadas)...")
    dialogue_items = _prepare_ep2_dialogue_clips(temp_audio_dir)

    print("[EP2 2/3] Generando banda sonora y efectos sincronizados...")
    bg_wav = _generate_sfx_and_music_wav(temp_audio_dir / "bg_sfx_ep2.wav", total_duration=total_duration)

    audio_tracks = [AudioFileClip(str(bg_wav))]
    for start_sec, mp3_path in dialogue_items:
        clip_a = AudioFileClip(str(mp3_path))
        if MOVIEPY_V2:
            clip_a = clip_a.with_start(start_sec)
        else:
            clip_a = clip_a.set_start(start_sec)
        audio_tracks.append(clip_a)

    comp_audio = CompositeAudioClip(audio_tracks)
    if MOVIEPY_V2:
        comp_audio = comp_audio.with_duration(total_duration)
    else:
        comp_audio = comp_audio.set_duration(total_duration)

    print(f"[EP2 3/3] Renderizando Episodio 2 a {FPS_SMOOTH} FPS continuos...")
    video_clip = VideoClip(make_ep2_frame, duration=total_duration)
    if MOVIEPY_V2:
        video_clip = video_clip.with_audio(comp_audio)
    else:
        video_clip = video_clip.set_audio(comp_audio)

    video_clip.write_videofile(
        str(output_path),
        fps=FPS_SMOOTH,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger=None,
    )

    video_clip.close()
    comp_audio.close()
    for tr in audio_tracks:
        tr.close()

    print(f"      ¡Episodio 2 exportado exitosamente en: {output_path}!")
    return output_path


if __name__ == "__main__":
    import sys

    if "--ep2" in sys.argv:
        render_restaurant_comedy_ep2()
    else:
        render_restaurant_comedy_video()
