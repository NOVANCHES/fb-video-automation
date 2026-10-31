"""
Motor de Animación Continua a 24 FPS (0 trabas, 100% universal sin datos personales)
para los 3 Sketches Virales de Comedia:
  1. Idea 1: El Choque Generacional Tecnológico (El Boomer, El Millennial, La Gen Z)
  2. Idea 2: Desmintiendo "Hacks" Absurdos (La Promesa, El Intento Olímpico, El Desastre + Silencio Incómodo)
  3. Idea 3: El Reto Callejero Rápido ($100 pesos en 3 segundos: "¡Leche! ¡Kellogg's! ¡Bimbo!" + Frutsi de consolación)
"""

import argparse
import asyncio
import math
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


async def _tts_save(text: str, voice: str, rate: str, out_path: Path) -> Path:
    comm = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await comm.save(str(out_path))
    return out_path


def _draw_top_banner(draw: ImageDraw.ImageDraw, title: str, subtitle: str = "", accent: Tuple[int, int, int] = (255, 225, 0)) -> None:
    draw.rounded_rectangle([50, 80, VIDEO_WIDTH - 50, 240 if subtitle else 190], radius=26, fill=(14, 16, 24), outline=accent, width=5)
    draw.text((VIDEO_WIDTH // 2, 135), title, font=_font(40, bold=True), fill=(255, 255, 255), anchor="mm")
    if subtitle:
        draw.text((VIDEO_WIDTH // 2, 195), subtitle, font=_font(33, bold=True), fill=accent, anchor="mm")


def _draw_bottom_caption(draw: ImageDraw.ImageDraw, line1: str, line2: str = "", accent: Tuple[int, int, int] = (255, 230, 0)) -> None:
    draw.rounded_rectangle([60, 1605, VIDEO_WIDTH - 60, 1795], radius=28, fill=(10, 12, 18), outline=accent, width=5)
    if not line2:
        draw.text((VIDEO_WIDTH // 2, 1700), line1, font=_font(44, bold=True), fill=accent, anchor="mm")
    else:
        draw.text((VIDEO_WIDTH // 2, 1668), line1, font=_font(41, bold=True), fill=(255, 255, 255), anchor="mm")
        draw.text((VIDEO_WIDTH // 2, 1732), line2, font=_font(44, bold=True), fill=accent, anchor="mm")


# =============================================================================
# IDEA 1: EL CHOQUE GENERACIONAL TECNOLÓGICO (30s a 24 FPS)
# =============================================================================
def _sfx_idea1(wav_path: Path, duration: float = 30.0) -> Path:
    sr = 22050
    t = np.linspace(0, duration, int(duration * sr), endpoint=False)
    audio = np.zeros_like(t)

    # Escena 1 (0 - 10s): Clics súper lentos de teclado con eco ("TUC... TUC...") cada 1.8s
    for tap_t in [1.5, 3.3, 5.1, 6.9, 8.6]:
        m = (t >= tap_t) & (t < tap_t + 0.18)
        tl = t[m] - tap_t
        audio[m] += 0.35 * np.sin(2 * np.pi * 620.0 * tl) * np.exp(-22.0 * tl)

    # Escena 2 (10 - 20s): Ráfaga supersónica de tecleo de pulgares (16 clics por segundo) + sorbo de café
    m2 = (t >= 10.5) & (t < 19.5)
    t2 = t[m2] - 10.5
    rapid_env = np.exp(-35.0 * ((t2 * 14.0) % 1.0))
    audio[m2] += 0.16 * np.sin(2 * np.pi * (1100.0 + 200.0 * ((np.floor(t2 * 14.0)) % 3)) * t2) * rapid_env

    # Escena 3 (20 - 30s): Pitido de inicio de nota de voz de WhatsApp + beat electrónico de baile de TikTok
    m_beep = (t >= 20.2) & (t < 20.5)
    tb = t[m_beep] - 20.2
    audio[m_beep] += 0.35 * np.sin(2 * np.pi * 880.0 * tb) * np.exp(-8.0 * tb)

    m3 = (t >= 20.5) & (t < 30.0)
    t3 = t[m3] - 20.5
    kick = np.exp(-14.0 * ((t3 * 2.2) % 1.0)) * np.sin(2 * np.pi * 85.0 * t3)
    synth = 0.08 * np.sin(2 * np.pi * (330.0 + 110.0 * (np.floor(t3 * 4.4) % 4)) * t3)
    audio[m3] += 0.22 * kick + synth

    audio = np.clip(audio, -0.95, 0.95)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    return wav_path


def make_idea1_frame(t: float) -> np.ndarray:
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (26, 28, 38))
    draw = ImageDraw.Draw(img)
    black = (18, 18, 22)

    # -------------------------------------------------------------------------
    # ESCENA 1 (0.0s - 10.0s): EL BOOMER ("Cómo escribe mi papá")
    # -------------------------------------------------------------------------
    if t < 10.0:
        draw.rectangle([0, 0, VIDEO_WIDTH, 1350], fill=(48, 42, 36))
        draw.rectangle([0, 1350, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(68, 52, 40))

        # Personaje de perfil a la izquierda con el brazo súper estirado a medio metro
        cx, cy = 270, 1020
        # Torso
        draw.rounded_rectangle([cx - 110, cy - 40, cx + 110, cy + 260], radius=45, fill=(70, 95, 130), outline=black, width=6)
        # Cabeza inclinada hacia atrás mirando de lejos
        head_x, head_y = cx - 20, cy - 230
        draw.rounded_rectangle([head_x - 95, head_y, head_x + 95, head_y + 195], radius=75, fill=(240, 196, 160), outline=black, width=6)
        # Cabello canoso
        draw.pieslice([head_x - 100, head_y - 15, head_x + 100, head_y + 90], start=180, end=360, fill=(185, 190, 198), outline=black, width=5)
        # Ceño muy fruncido
        draw.line([(head_x + 25, head_y + 62), (head_x + 82, head_y + 78)], fill=black, width=9)
        draw.ellipse([head_x + 42, head_y + 82, head_x + 68, head_y + 108], fill=(255, 255, 255), outline=black, width=4)
        draw.ellipse([head_x + 52, head_y + 90, head_x + 64, head_y + 102], fill=black)
        # Lentes en la pura punta de la nariz
        nose_x, nose_y = head_x + 95, head_y + 118
        draw.polygon([(nose_x, nose_y - 12), (nose_x + 34, nose_y + 8), (nose_x, nose_y + 18)], fill=(235, 185, 150), outline=black, width=5)
        draw.ellipse([nose_x - 10, nose_y - 8, nose_x + 32, nose_y + 30], outline=(210, 175, 50), width=6)
        draw.line([(head_x + 30, head_y + 95), (nose_x - 5, nose_y + 8)], fill=(210, 175, 50), width=5)

        # Brazo izquierdo sosteniendo el teléfono a MEDIO METRO de distancia (x=830)
        phone_x, phone_y = 835, 920
        draw.line([(cx + 80, cy + 40), (phone_x - 25, phone_y + 40)], fill=(70, 95, 130), width=34)
        # Resplandor de brillo al 1000% saliendo del celular
        draw.polygon([(phone_x - 20, phone_y - 90), (head_x + 70, head_y + 40), (head_x + 70, head_y + 180), (phone_x - 20, phone_y + 90)], fill=(255, 255, 210))
        # Teléfono gigante con letra tamaño 80
        draw.rounded_rectangle([phone_x - 35, phone_y - 110, phone_x + 55, phone_y + 110], radius=18, fill=(25, 25, 30), outline=(255, 255, 255), width=5)

        # Brazo derecho con UN SOLO DEDO ÍNDICE bajando lentísimo cada 1.8s
        cycle = (t % 1.8) / 1.8
        finger_offset = int(math.sin(cycle * math.pi) * 140)
        fx, fy = phone_x - 55 - (140 - finger_offset), phone_y - 80 + (140 - finger_offset) // 2
        draw.line([(cx + 60, cy + 95), (fx - 35, fy)], fill=(240, 196, 160), width=28)
        # Dedo índice estirado
        draw.rounded_rectangle([fx - 45, fy - 14, fx + 25, fy + 14], radius=12, fill=(240, 196, 160), outline=black, width=5)

        # Efecto visual "*TUC*" cuando el dedo toca la pantalla
        if cycle > 0.42 and cycle < 0.62:
            draw.ellipse([phone_x - 75, phone_y - 45, phone_x + 15, phone_y + 45], outline=(255, 230, 0), width=6)
            draw.text((phone_x - 95, phone_y - 155), "¡TUC!", font=_font(46, bold=True), fill=(255, 230, 0), anchor="mm")

        # Cota de "0.5 METROS DE DISTANCIA"
        draw.line([(head_x + 110, cy - 190), (phone_x - 30, cy - 190)], fill=(255, 220, 90), width=4)
        draw.text(((head_x + 110 + phone_x - 30) // 2, cy - 225), "← 50 CM DE DISTANCIA →", font=_font(28, bold=True), fill=(255, 220, 90), anchor="mm")

        typed = "H... O... L... A..."[: max(1, int(t * 1.8))]
        _draw_top_banner(draw, "ESCENA 1: Cómo escribe mi papá", "Lentes en la nariz y a medio metro")
        _draw_bottom_caption(draw, f"Con un solo dedo índice: \"{typed}\"", "Velocidad: 1 letra por minuto")

    # -------------------------------------------------------------------------
    # ESCENA 2 (10.0s - 20.0s): EL MILLENNIAL ("Cómo escribo yo")
    # -------------------------------------------------------------------------
    elif t < 20.0:
        draw.rectangle([0, 0, VIDEO_WIDTH, 1350], fill=(32, 46, 58))
        draw.rectangle([0, 1350, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(48, 62, 74))

        cx, cy = 540, 980
        # Torso con hoodie
        draw.rounded_rectangle([cx - 145, cy - 30, cx + 145, cy + 280], radius=52, fill=(45, 115, 105), outline=black, width=6)
        # Cabeza con concentración absoluta
        draw.rounded_rectangle([cx - 105, cy - 245, cx + 105, cy - 35], radius=80, fill=(242, 198, 160), outline=black, width=6)
        draw.pieslice([cx - 112, cy - 265, cx + 112, cy - 140], start=180, end=360, fill=(38, 28, 22), outline=black, width=5)

        # Ojos súper concentrados con reflejo de pantalla + ojeras de café
        for ex in (cx - 42, cx + 42):
            draw.ellipse([ex - 26, cy - 165, ex + 26, cy - 113], fill=(255, 255, 255), outline=black, width=5)
            draw.ellipse([ex - 11, cy - 145, ex + 11, cy - 123], fill=black)
            draw.line([(ex - 28, cy - 178), (ex + 28, cy - 172)], fill=black, width=8)

        # Taza de café humeante al lado con popote/sorbo continuo
        cup_x, cup_y = cx + 225, cy + 25
        draw.rounded_rectangle([cup_x - 55, cup_y - 65, cup_x + 55, cup_y + 75], radius=14, fill=(245, 242, 235), outline=black, width=5)
        draw.rectangle([cup_x - 55, cup_y - 20, cup_x + 55, cup_y + 25], fill=(165, 105, 55), outline=black, width=4)
        draw.text((cup_x, cup_y + 2), "CAFÉ", font=_font(24, bold=True), fill=(255, 255, 255), anchor="mm")
        # Popote directo hacia la boca para tomar café sin soltar el celular
        draw.line([(cup_x - 20, cup_y - 65), (cx + 25, cy - 75)], fill=(40, 180, 95), width=10)

        # Teléfono sostenido horizontalmente con ambas manos + PULGARES SUPERSÓNICOS
        px, py = cx, cy + 125
        draw.rounded_rectangle([px - 155, py - 70, px + 155, py + 70], radius=24, fill=(20, 22, 28), outline=(0, 235, 255), width=5)

        # Pulgares volando a 24 FPS con estelas de velocidad
        for side in (-1, 1):
            for ghost in range(3):
                ang = t * 38.0 + ghost * 0.9 + (0 if side == -1 else 2.1)
                tx = px + side * 85 + int(math.cos(ang) * 42)
                ty = py + int(math.sin(ang * 1.3) * 34)
                color_thumb = (255, 235, 80) if ghost == 0 else (242, 198, 160)
                draw.ellipse([tx - 24, ty - 18, tx + 24, ty + 18], fill=color_thumb, outline=black, width=4)

        # Chispas de velocidad saliendo del teléfono
        for sp_i in range(8):
            ang_s = sp_i * (math.pi / 4) + t * 8.0
            r1 = 165 + int((t * 220 + sp_i * 30) % 75)
            sx1, sy1 = px + int(math.cos(ang_s) * 145), py + int(math.sin(ang_s) * 75)
            sx2, sy2 = px + int(math.cos(ang_s) * r1), py + int(math.sin(ang_s) * (r1 * 0.55))
            draw.line([(sx1, sy1), (sx2, sy2)], fill=(0, 240, 255), width=5)

        _draw_top_banner(draw, "ESCENA 2: Cómo escribo yo (Millennial)", "Pulgares a 300 palabras por minuto + Café")
        _draw_bottom_caption(draw, "Concentración absoluta con dos pulgares", "mientras tomas café sin mirar el teclado", accent=(0, 235, 255))

    # -------------------------------------------------------------------------
    # ESCENA 3 (20.0s - 30.0s): LA GEN Z ("Los de 15 años")
    # -------------------------------------------------------------------------
    else:
        draw.rectangle([0, 0, VIDEO_WIDTH, 1350], fill=(42, 24, 58))
        draw.rectangle([0, 1350, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(58, 34, 78))

        # Baile de TikTok continuo: el cuerpo y los brazos se balancean rítmicamente a 24 FPS
        dance_x = 540 + int(math.sin(t * 7.5) * 95)
        dance_y = 990 + int(abs(math.cos(t * 15.0)) * 32)

        # Torso oversize
        draw.rounded_rectangle([dance_x - 135, dance_y - 30, dance_x + 135, dance_y + 260], radius=48, fill=(235, 65, 155), outline=black, width=6)

        # Brazo izquierdo haciendo pasos de TikTok arriba y abajo
        arm_wave_x = dance_x - 210 + int(math.cos(t * 15.0) * 65)
        arm_wave_y = dance_y - 95 + int(math.sin(t * 15.0) * 85)
        draw.line([(dance_x - 115, dance_y + 20), (arm_wave_x, arm_wave_y)], fill=(235, 65, 155), width=34)
        draw.ellipse([arm_wave_x - 24, arm_wave_y - 24, arm_wave_x + 24, arm_wave_y + 24], fill=(242, 198, 160), outline=black, width=5)

        # Cabeza mirando hacia otro lado distraída (ni siquiera mira la pantalla)
        hx, hy = dance_x, dance_y - 235
        draw.rounded_rectangle([hx - 98, hy, hx + 98, hy + 195], radius=78, fill=(242, 198, 160), outline=black, width=6)
        # Cabello estilo Gen Z (brócoli / rizado arriba)
        for curl_x in range(hx - 75, hx + 85, 38):
            draw.ellipse([curl_x - 32, hy - 35, curl_x + 32, hy + 28], fill=(32, 24, 20), outline=black, width=4)

        # Ojos mirando hacia arriba/lado totalmente distraídos
        for ex in (hx - 36, hx + 36):
            draw.ellipse([ex - 20, hy + 65, ex + 20, hy + 105], fill=(255, 255, 255), outline=black, width=4)
            draw.ellipse([ex - 16, hy + 68, ex + 2, hy + 86], fill=black)

        # TELÉFONO EN POSICIÓN HORIZONTAL PEGADO A LA BOCA COMO PAN TOSTADO
        toast_x, toast_y = hx + 95, hy + 150
        draw.rounded_rectangle([toast_x - 95, toast_y - 26, toast_x + 125, toast_y + 26], radius=14, fill=(30, 34, 42), outline=(0, 255, 145), width=5)
        draw.line([(dance_x + 110, dance_y + 30), (toast_x + 65, toast_y + 10)], fill=(242, 198, 160), width=28)

        # Indicador flotante de Nota de Voz de 3 minutos con ondas de audio animadas
        draw.rounded_rectangle([160, 360, 920, 510], radius=32, fill=(18, 88, 58), outline=(0, 255, 145), width=5)
        draw.ellipse([205, 410, 255, 460], fill=(255, 55, 55))
        for w_idx in range(18):
            wx = 295 + w_idx * 22
            wh = int(14 + abs(math.sin(t * 14.0 + w_idx * 0.7)) * 42)
            draw.line([(wx, 435 - wh), (wx, 435 + wh)], fill=(0, 255, 145), width=6)
        mins = 3
        secs = int((t - 20.0) * 4) % 60
        draw.text((795, 435), f"0{mins}:{secs:02d}", font=_font(42, bold=True), fill=(255, 255, 255), anchor="mm")

        _draw_top_banner(draw, "ESCENA 3: Los de 15 años (Gen Z)", "Teléfono como pan tostado + Baile de TikTok", accent=(0, 255, 145))
        _draw_bottom_caption(draw, "Mandando un audio de 3 minutos", "sin mirar la pantalla mientras bailan", accent=(0, 255, 145))

    return np.asarray(img)


# =============================================================================
# IDEA 2: DESMINTIENDO "HACKS" ABSURDOS (30s a 24 FPS)
# =============================================================================
def _sfx_idea2(wav_path: Path, duration: float = 30.0) -> Path:
    sr = 22050
    t = np.linspace(0, duration, int(duration * sr), endpoint=False)
    audio = np.zeros_like(t)

    # Escena 1 (0 - 8s): Sonido mágico "Brillo estético ✨"
    for ch_idx, freq in enumerate([523.25, 659.25, 783.99, 1046.5]):
        t_st = 1.0 + ch_idx * 0.35
        m = (t >= t_st) & (t < t_st + 0.8)
        tl = t[m] - t_st
        audio[m] += 0.22 * np.sin(2 * np.pi * freq * tl) * np.exp(-3.5 * tl)

    # Escena 2 (8 - 18s): Música épica de entrenamiento deportivo
    m2 = (t >= 8.0) & (t < 18.0)
    t2 = t[m2] - 8.0
    beat = np.exp(-10.0 * ((t2 * 2.5) % 1.0)) * np.sin(2 * np.pi * 110.0 * t2)
    audio[m2] += 0.20 * beat

    # Escena 3A (18.2 - 20.5s): ¡CRASH / EXPLOSIÓN DE PASTEL Y CAMISA VOLANDO!
    m_crash = (t >= 18.4) & (t < 20.2)
    tc = t[m_crash] - 18.4
    rng = np.random.default_rng(42)
    noise = rng.uniform(-1.0, 1.0, size=tc.shape)
    audio[m_crash] += 0.45 * noise * np.exp(-3.5 * tc) + 0.35 * np.sin(2 * np.pi * 95.0 * tc) * np.exp(-4.0 * tc)

    # Escena 3B (21.0 - 25.5s): SILENCIO ABSOLUTO + Grillos "Cri-cri, cri-cri" procesando la humillación
    for c_start in [21.4, 21.65, 22.8, 23.05, 24.2, 24.45]:
        mc = (t >= c_start) & (t < c_start + 0.16)
        tl = t[mc] - c_start
        audio[mc] += 0.22 * np.sin(2 * np.pi * 4200.0 * tl) * (0.5 + 0.5 * np.sin(2 * np.pi * 55.0 * tl))

    # Sonido de tirar al bote de basura (t=26.5s)
    m_bin = (t >= 26.5) & (t < 27.3)
    tb = t[m_bin] - 26.5
    audio[m_bin] += 0.35 * np.sin(2 * np.pi * 140.0 * tb) * np.exp(-7.0 * tb)

    audio = np.clip(audio, -0.95, 0.95)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    return wav_path


def make_idea2_frame(t: float) -> np.ndarray:
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (28, 30, 38))
    draw = ImageDraw.Draw(img)
    black = (18, 18, 22)

    # -------------------------------------------------------------------------
    # ESCENA 1 (0.0s - 8.0s): LA PROMESA (El Hack Viral Perfecto de Internet)
    # -------------------------------------------------------------------------
    if t < 8.0:
        draw.rectangle([0, 0, VIDEO_WIDTH, 1350], fill=(242, 238, 230))
        draw.rectangle([0, 1350, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(215, 205, 192))

        # Mesa estética minimalista
        draw.rounded_rectangle([120, 920, 960, 1020], radius=24, fill=(255, 255, 255), outline=black, width=5)

        if t < 4.0:
            # Camisa abierta y movimiento ninja perfecto en 1 segundo
            fold_prog = min(1.0, max(0.0, (t - 1.5) / 0.8))
            w_shirt = int(240 - 110 * fold_prog)
            draw.rounded_rectangle([540 - w_shirt, 620, 540 + w_shirt, 910], radius=22, fill=(65, 145, 245), outline=black, width=6)
            draw.text((540, 765), "DOBLADO PERFECTO ✨" if fold_prog > 0.8 else "MOVIMIENTO NINJA 🥷", font=_font(36, bold=True), fill=(255, 255, 255), anchor="mm")
        else:
            # Cortando un pastel perfectamente con una copa de cristal sin ensuciar nada
            draw.rounded_rectangle([320, 720, 760, 920], radius=26, fill=(255, 175, 200), outline=black, width=6)
            draw.rectangle([320, 690, 760, 745], fill=(255, 250, 245), outline=black, width=5)
            cup_y = int(460 + math.sin((t - 4.0) * 2.5) * 160)
            draw.polygon([(480, cup_y), (600, cup_y), (575, cup_y + 130), (505, cup_y + 130)], fill=(210, 242, 255), outline=black, width=5)

        _draw_top_banner(draw, "ESCENA 1: El 'Hack' Viral en Internet", "15 Millones de Likes • 'Súper fácil en 1 segundo'", accent=(0, 235, 180))
        _draw_bottom_caption(draw, "En el video viral todo sale perfecto:", "Doblar ropa o partir pastel en 1 segundo", accent=(0, 235, 180))

    # -------------------------------------------------------------------------
    # ESCENA 2 (8.0s - 18.0s): EL INTENTO ("Si esto funciona, mi vida fue una mentira")
    # -------------------------------------------------------------------------
    elif t < 18.0:
        draw.rectangle([0, 0, VIDEO_WIDTH, 1350], fill=(38, 44, 58))
        draw.rectangle([0, 1350, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(55, 62, 78))

        cx, cy = 540, 960
        # Estiramientos deportivos exagerados a 24 FPS (girando hombros y brazos como atleta olímpico)
        stretch_ang = math.sin(t * 7.5) * 0.65
        draw.rounded_rectangle([cx - 125, cy - 30, cx + 125, cy + 250], radius=45, fill=(220, 55, 55), outline=black, width=6)

        # Brazos estirándose de lado a lado
        lx = cx - 120 - int(math.cos(stretch_ang) * 135)
        ly = cy + 20 + int(math.sin(stretch_ang) * 95)
        rx = cx + 120 + int(math.cos(stretch_ang) * 135)
        ry = cy + 20 - int(math.sin(stretch_ang) * 95)
        draw.line([(cx - 110, cy + 20), (lx, ly)], fill=(242, 198, 160), width=32)
        draw.line([(cx + 110, cy + 20), (rx, ry)], fill=(242, 198, 160), width=32)

        # Cabeza con banda deportiva roja en la frente y sonrisa de exceso de confianza
        head_tilt = int(math.sin(t * 6.0) * 18)
        hx = cx + head_tilt
        draw.rounded_rectangle([hx - 95, cy - 235, hx + 95, cy - 40], radius=75, fill=(242, 198, 160), outline=black, width=6)
        draw.rectangle([hx - 98, cy - 205, hx + 98, cy - 170], fill=(235, 40, 40), outline=black, width=5)
        for ex in (hx - 35, hx + 35):
            draw.ellipse([ex - 18, cy - 145, ex + 18, cy - 109], fill=(255, 255, 255), outline=black, width=4)
            draw.ellipse([ex - 8, cy - 135, ex + 8, cy - 119], fill=black)
        draw.arc([hx - 35, cy - 98, hx + 35, cy - 60], start=10, end=170, fill=black, width=6)

        # Mesa lista con el pastel y la camisa enfrente
        draw.rounded_rectangle([140, 1180, 940, 1265], radius=20, fill=(145, 92, 50), outline=black, width=6)
        draw.rounded_rectangle([240, 1080, 500, 1185], radius=18, fill=(255, 175, 200), outline=black, width=5)
        draw.rounded_rectangle([580, 1110, 840, 1185], radius=16, fill=(65, 145, 245), outline=black, width=5)

        _draw_top_banner(draw, "ESCENA 2: El Intento en la Vida Real", "Estiramientos olímpicos y 100% confianza")
        _draw_bottom_caption(draw, "\"Si esto funciona, mi vida entera", "ha sido una mentira... ¡Ahí les voy!\"")

    # -------------------------------------------------------------------------
    # ESCENA 3 (18.0s - 30.0s): EL DESASTRE + SILENCIO DE 3 SEGUNDOS + BASURA
    # -------------------------------------------------------------------------
    else:
        local_t = t - 18.0
        draw.rectangle([0, 0, VIDEO_WIDTH, 1350], fill=(34, 36, 44))
        draw.rectangle([0, 1350, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(48, 50, 58))

        if local_t < 2.8:
            # Caos total: La camisa sale volando por los aires y el pastel explota en puré
            shirt_x = int(540 + math.cos(local_t * 14.0) * 320)
            shirt_y = int(480 - math.sin(local_t * 10.0) * 210)
            draw.rounded_rectangle([shirt_x - 130, shirt_y - 75, shirt_x + 130, shirt_y + 75], radius=24, fill=(65, 145, 245), outline=black, width=6)

            # Pastel hecho puré salpicando por toda la pantalla
            for sp in range(12):
                ang = sp * (math.pi / 6)
                dist = int(local_t * 190)
                px = 540 + int(math.cos(ang) * dist)
                py = 980 + int(math.sin(ang) * dist)
                draw.ellipse([px - 38, py - 28, px + 38, py + 28], fill=(255, 175, 200), outline=black, width=4)

            _draw_top_banner(draw, "ESCENA 3: El Desastre Absoluto", "¡La camisa vuela y el pastel se hace puré!", accent=(255, 85, 85))
            _draw_bottom_caption(draw, "*Movimiento ninja sale terriblemente mal*", "¡Pastel aplastado por toda la mesa!", accent=(255, 85, 85))

        elif local_t < 7.8:
            # PRIMER PLANO EN SILENCIO ABSOLUTO (3+ segundos procesando la humillación con pastel en la cara)
            zoom_p = min(1.0, (local_t - 2.8) / 0.6)
            sc = 1.65 + 0.35 * zoom_p
            cx, cy = 540, 980
            draw.rounded_rectangle([cx - int(110 * sc), cy - int(190 * sc), cx + int(110 * sc), cy + int(40 * sc)], radius=int(80 * sc), fill=(242, 198, 160), outline=black, width=6)
            # Manchas de betún rosa en la mejilla y en la frente
            draw.ellipse([cx + 45, cy - 210, cx + 155, cy - 120], fill=(255, 165, 195), outline=black, width=4)
            draw.ellipse([cx - 145, cy - 95, cx - 55, cy - 25], fill=(255, 165, 195), outline=black, width=4)
            # Mirada vacía al vacío (parpadeo lento en silencio)
            for ex in (cx - int(45 * sc), cx + int(45 * sc)):
                draw.ellipse([ex - 36, cy - 165, ex + 36, cy - 93], fill=(255, 255, 255), outline=black, width=5)
                draw.ellipse([ex - 12, cy - 141, ex + 12, cy - 117], fill=black)
            # Boca totalmente recta en silencio incómodo
            draw.line([(cx - 55, cy - 30), (cx + 55, cy - 30)], fill=black, width=8)

            _draw_top_banner(draw, "*SILENCIO ABSOLUTO DE 3 SEGUNDOS*", "Procesando la humillación... (Cri-cri, cri-cri)")
            _draw_bottom_caption(draw, "...", "(Mirando a la cámara en silencio total)")

        else:
            # Tirando los restos del pastel y la copa al bote de basura
            bin_x, bin_y = 680, 1180
            draw.polygon([(bin_x - 110, bin_y - 160), (bin_x + 110, bin_y - 160), (bin_x + 85, bin_y + 180), (bin_x - 85, bin_y + 180)], fill=(130, 140, 150), outline=black, width=6)
            draw.text((bin_x, bin_y + 10), "BASURA", font=_font(32, bold=True), fill=black, anchor="mm")

            drop_y = int(680 + (local_t - 7.8) * 140)
            draw.ellipse([bin_x - 65, min(bin_y - 120, drop_y), bin_x + 65, min(bin_y - 40, drop_y + 80)], fill=(255, 175, 200), outline=black, width=4)

            _draw_top_banner(draw, "Resultado final del 'Hack': 0/10", "Directo al bote de basura")
            _draw_bottom_caption(draw, "Tiras los restos a la basura en silencio", "y juras no volver a creerle a internet")

    return np.asarray(img)


# =============================================================================
# IDEA 3: EL RETO CALLEJERO RÁPIDO (30s a 24 FPS)
# =============================================================================
def _sfx_idea3(wav_path: Path, duration: float = 30.0) -> Path:
    sr = 22050
    t = np.linspace(0, duration, int(duration * sr), endpoint=False)
    audio = np.zeros_like(t)

    # Escena 1 y 2 (5.0s - 18.0s): Tic-tac acelerado de reloj de concurso ("TIC-TAC-TIC-TAC")
    for tick_t in np.arange(5.5, 18.2, 0.45):
        m = (t >= tick_t) & (t < tick_t + 0.12)
        tl = t[m] - tick_t
        freq = 950.0 if int(tick_t * 2) % 2 == 0 else 720.0
        audio[m] += 0.28 * np.sin(2 * np.pi * freq * tl) * np.exp(-25.0 * tl)

    # Escena 3 (18.5s - 20.0s): ¡CHICHARRA DE ERROR DE PROGRAMA DE CONCURSOS ("¡BUUUUUU ❌!")!
    m_buzz = (t >= 18.5) & (t < 20.1)
    tb = t[m_buzz] - 18.5
    buzz = (
        np.sin(2 * np.pi * 110.0 * tb)
        + 0.7 * np.sin(2 * np.pi * 116.5 * tb)
        + 0.5 * np.sin(2 * np.pi * 220.0 * tb)
    )
    audio[m_buzz] += 0.35 * np.sign(buzz) * np.exp(-1.2 * tb)

    # Pasos corriendo al final (25.5s - 29.5s)
    for step_t in np.arange(25.5, 29.5, 0.18):
        ms = (t >= step_t) & (t < step_t + 0.08)
        ts = t[ms] - step_t
        audio[ms] += 0.22 * np.sin(2 * np.pi * 280.0 * ts) * np.exp(-30.0 * ts)

    audio = np.clip(audio, -0.95, 0.95)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    return wav_path


def make_idea3_frame(t: float) -> np.ndarray:
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (125, 195, 245))
    draw = ImageDraw.Draw(img)
    black = (18, 18, 22)

    # -------------------------------------------------------------------------
    # ESCENA 1 (0.0s - 10.0s): EL ABORDAJE EN EL PARQUE ($100 PESOS EN 3 SEGUNDOS)
    # -------------------------------------------------------------------------
    if t < 10.0:
        # Cielo azul, pasto verde y banca de parque
        draw.rectangle([0, 0, VIDEO_WIDTH, 1180], fill=(115, 195, 248))
        draw.rectangle([0, 1180, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(75, 168, 85))
        draw.rounded_rectangle([140, 980, 940, 1185], radius=18, fill=(148, 88, 45), outline=black, width=6)

        # Persona sentada tranquila en la banca (derecha: x=680)
        vx, vy = 680, 960
        draw.rounded_rectangle([vx - 95, vy - 20, vx + 95, vy + 210], radius=38, fill=(65, 125, 215), outline=black, width=6)
        draw.rounded_rectangle([vx - 85, vy - 205, vx + 85, vy - 20], radius=68, fill=(240, 195, 160), outline=black, width=6)
        for ex in (vx - 30, vx + 30):
            draw.ellipse([ex - 18, vy - 135, ex + 18, vy - 99], fill=(255, 255, 255), outline=black, width=4)
            draw.ellipse([ex - 8, vy - 125, ex + 8, vy - 109], fill=black)

        # Conductor apareciendo de la nada desde la izquierda con micrófono y billete de $100
        slide_in = min(1.0, t / 0.8)
        hx = int(-150 + 470 * slide_in)
        hy = 960
        draw.rounded_rectangle([hx - 95, hy - 20, hx + 95, hy + 210], radius=38, fill=(25, 28, 36), outline=black, width=6)
        draw.rounded_rectangle([hx - 85, hy - 205, hx + 85, hy - 20], radius=68, fill=(242, 198, 160), outline=black, width=6)
        for ex in (hx - 30, hx + 30):
            draw.ellipse([ex - 16, hy - 135, ex + 16, hy - 103], fill=(255, 255, 255), outline=black, width=4)
            draw.ellipse([ex - 7, hy - 125, ex + 7, hy - 111], fill=black)
        open_m = int(8 + abs(math.sin(t * 14.0)) * 16)
        draw.ellipse([hx - 22, hy - 65 - open_m, hx + 22, hy - 65 + open_m], fill=(180, 35, 45), outline=black, width=4)

        # Micrófono puesto directo frente a la cara del entrevistado
        mic_x, mic_y = vx - 125, vy - 75
        draw.line([(hx + 80, hy + 20), (mic_x, mic_y + 35)], fill=black, width=14)
        draw.ellipse([mic_x - 28, mic_y - 28, mic_x + 28, mic_y + 28], fill=(220, 40, 40), outline=black, width=5)

        # Billete de $100 pesos agitándose en la otra mano
        bill_y = hy - 165 + int(math.sin(t * 12.0) * 14)
        draw.rounded_rectangle([hx - 145, bill_y - 42, hx + 25, bill_y + 42], radius=10, fill=(195, 75, 65), outline=black, width=4)
        draw.text((hx - 60, bill_y), "$100 PESOS", font=_font(26, bold=True), fill=(255, 240, 180), anchor="mm")

        # Cronómetro gigante apareciendo en 3, 2, 1
        if t >= 6.0:
            sec_left = max(1, 3 - int(t - 6.0))
            draw.rounded_rectangle([360, 310, 720, 460], radius=28, fill=(220, 30, 30), outline=(255, 255, 255), width=6)
            draw.text((540, 385), f"¡{sec_left}.00 SEG!", font=_font(62, bold=True), fill=(255, 255, 255), anchor="mm")

        _draw_top_banner(draw, "RETO CALLEJERO: $100 Pesos en 3 Segundos", "\"Dime 3 marcas de cereal en 3 segundos\"")
        _draw_bottom_caption(draw, "\"¡Te doy $100 pesos ahora mismo!\"", "\"¡Tres, dos, uno... TIEMPO!\"")

    # -------------------------------------------------------------------------
    # ESCENA 2 (10.0s - 18.5s): EL PÁNICO EN BLANCO Y NEGRO ("¡Leche! ¡Kellogg's! ¡Bimbo!")
    # -------------------------------------------------------------------------
    elif t < 18.5:
        local_t = t - 10.0
        # Filtro dramático en BLANCO Y NEGRO con zoom continuo a la cara de desesperación
        draw.rectangle([0, 0, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(42, 42, 45))
        zoom_sc = 1.45 + min(0.85, local_t * 0.11)
        shake_x = int(math.sin(t * 38.0) * 8)
        cx, cy = 540 + shake_x, 1020

        draw.rounded_rectangle([cx - int(115 * zoom_sc), cy - int(25 * zoom_sc), cx + int(115 * zoom_sc), cy + int(220 * zoom_sc)], radius=40, fill=(95, 95, 100), outline=black, width=6)
        draw.rounded_rectangle([cx - int(98 * zoom_sc), cy - int(215 * zoom_sc), cx + int(98 * zoom_sc), cy - int(25 * zoom_sc)], radius=int(75 * zoom_sc), fill=(210, 210, 215), outline=black, width=6)

        # Ojos en pánico total + gotas de sudor en escala de grises
        for ex in (cx - int(36 * zoom_sc), cx + int(36 * zoom_sc)):
            r_eye = int(24 * zoom_sc)
            draw.ellipse([ex - r_eye, cy - int(135 * zoom_sc) - r_eye, ex + r_eye, cy - int(135 * zoom_sc) + r_eye], fill=(255, 255, 255), outline=black, width=5)
            draw.ellipse([ex - 10, cy - int(135 * zoom_sc) - 10, ex + 10, cy - int(135 * zoom_sc) + 10], fill=black)

        open_m = int((0.4 + 0.6 * abs(math.sin(t * 16.0))) * 28 * zoom_sc)
        draw.ellipse([cx - int(28 * zoom_sc), cy - int(65 * zoom_sc) - open_m, cx + int(28 * zoom_sc), cy - int(65 * zoom_sc) + open_m], fill=(40, 40, 40), outline=black, width=5)

        # Respuestas absurdas apareciendo una por una con tache rojo
        answers = []
        if local_t >= 0.8:
            answers.append(("1. ¡¿LECHE?! ❌ (No es cereal)", (255, 95, 95)))
        if local_t >= 3.0:
            answers.append(("2. ¡KELLOGG'S! ✅", (120, 255, 140)))
        if local_t >= 5.2:
            answers.append(("3. ¡¿BIMBO?! ❌ (Es pan)", (255, 95, 95)))

        for idx_a, (ans_txt, ans_col) in enumerate(answers):
            ay = 340 + idx_a * 110
            draw.rounded_rectangle([95, ay - 42, VIDEO_WIDTH - 95, ay + 42], radius=20, fill=(18, 18, 22), outline=ans_col, width=4)
            draw.text((540, ay), ans_txt, font=_font(40, bold=True), fill=ans_col, anchor="mm")

        _draw_top_banner(draw, "ESCENA 2: El Pánico Frente al Micrófono", "Filtro Blanco y Negro • Cerebro desconectado", accent=(220, 220, 220))
        _draw_bottom_caption(draw, "\"¡Eh... LECHE! ¡KELLOGG'S! ¡BIMBO!\"", "(Cuando te ganan los nervios en la calle)", accent=(255, 110, 110))

    # -------------------------------------------------------------------------
    # ESCENA 3 (18.5s - 30.0s): EL DESENLACE (CHICHARRA + FRUTSI DE CONSOLACIÓN + HUIR CORRIENDO)
    # -------------------------------------------------------------------------
    else:
        local_t = t - 18.5
        draw.rectangle([0, 0, VIDEO_WIDTH, 1180], fill=(115, 195, 248))
        draw.rectangle([0, 1180, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(75, 168, 85))
        draw.rounded_rectangle([140, 980, 940, 1185], radius=18, fill=(148, 88, 45), outline=black, width=6)

        # Víctima sentada sosteniendo su Frutsi / dulce con cara de confusión
        vx, vy = 680, 960
        draw.rounded_rectangle([vx - 95, vy - 20, vx + 95, vy + 210], radius=38, fill=(65, 125, 215), outline=black, width=6)
        draw.rounded_rectangle([vx - 85, vy - 205, vx + 85, vy - 20], radius=68, fill=(240, 195, 160), outline=black, width=6)
        for ex in (vx - 30, vx + 30):
            draw.ellipse([ex - 16, vy - 135, ex + 16, vy - 103], fill=(255, 255, 255), outline=black, width=4)
            draw.ellipse([ex - 7, vy - 125, ex + 7, vy - 111], fill=black)
        draw.line([(vx - 25, vy - 60), (vx + 25, vy - 60)], fill=black, width=6)

        if local_t < 2.2:
            # Letrero gigante de ERROR de programa de concursos
            draw.rounded_rectangle([180, 320, 900, 520], radius=32, fill=(225, 35, 35), outline=(255, 255, 255), width=6)
            draw.text((540, 420), "❌ ¡TIEMPO FUERA! ❌", font=_font(56, bold=True), fill=(255, 255, 255), anchor="mm")

        # Conductor dando palmaditas, entregando el Frutsi y saliendo corriendo a toda velocidad (local_t >= 6.5)
        run_away = max(0, int((local_t - 6.2) * 320)) if local_t >= 6.2 else 0
        hx = 340 - run_away
        hy = 960 - (int(abs(math.sin(t * 22.0)) * 35) if run_away > 0 else 0)
        if hx > -220:
            draw.rounded_rectangle([hx - 95, hy - 20, hx + 95, hy + 210], radius=38, fill=(25, 28, 36), outline=black, width=6)
            draw.rounded_rectangle([hx - 85, hy - 205, hx + 85, hy - 20], radius=68, fill=(242, 198, 160), outline=black, width=6)
            for ex in (hx - 30, hx + 30):
                draw.ellipse([ex - 15, hy - 135, ex + 15, hy - 105], fill=(255, 255, 255), outline=black, width=4)
                draw.ellipse([ex - 6, hy - 125, ex + 6, hy - 113], fill=black)
            draw.arc([hx - 28, hy - 80, hx + 28, hy - 45], start=10, end=170, fill=black, width=5)

            if 2.0 <= local_t < 6.2:
                # Brazo dando palmaditas de consuelo en el hombro
                pat_y = vy - 35 + int(math.sin(t * 16.0) * 18)
                draw.line([(hx + 80, hy + 10), (vx - 65, pat_y)], fill=(242, 198, 160), width=26)

        # El Frutsi rojo brillante + dulce entregado como "Premio de consolación"
        if local_t >= 3.2:
            fx, fy = vx - 135, vy + 25
            draw.rounded_rectangle([fx - 45, fy - 65, fx + 45, fy + 55], radius=28, fill=(235, 35, 55), outline=black, width=5)
            draw.rectangle([fx - 15, fy - 95, fx + 15, fy - 65], fill=(255, 230, 0), outline=black, width=4)
            draw.text((fx, fy - 5), "FRUTSI", font=_font(22, bold=True), fill=(255, 255, 255), anchor="mm")
            draw.rounded_rectangle([240, 360, 840, 470], radius=24, fill=(255, 230, 0), outline=black, width=5)
            draw.text((540, 415), "🏆 PREMIO DE CONSOLACIÓN 🏆", font=_font(36, bold=True), fill=black, anchor="mm")

        _draw_top_banner(draw, "ESCENA 3: Premio de Consolación", "Palmaditas, un Frutsi del bolsillo y a correr")
        _draw_bottom_caption(draw, "\"Ni modo, toma tu Frutsi de consolación\"", "*Sale corriendo de la escena*")

    return np.asarray(img)


def _render_sketch(
    sketch_id: int,
    make_frame_fn: Any,
    sfx_fn: Any,
    dialogue_specs: List[Tuple[float, str, str, str, str]],
    output_filename: str,
) -> Path:
    duration = 30.0
    temp_dir = OUTPUT_DIR / f"sketch_{sketch_id}_audio"
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Sketch {sketch_id} - 1/3] Sintetizando locución y diálogos...")

    async def _gen_all():
        await asyncio.gather(
            *[
                _tts_save(txt, voice, rate, temp_dir / fname)
                for _, voice, rate, txt, fname in dialogue_specs
            ]
        )

    asyncio.run(_gen_all())

    print(f"[Sketch {sketch_id} - 2/3] Generando efectos de sonido y música sincronizada...")
    bg_wav = sfx_fn(temp_dir / "bg_sfx.wav", duration=duration)

    tracks = [AudioFileClip(str(bg_wav))]
    for start_t, _, _, _, fname in dialogue_specs:
        ac = AudioFileClip(str(temp_dir / fname))
        if MOVIEPY_V2:
            ac = ac.with_start(start_t)
        else:
            ac = ac.set_start(start_t)
        tracks.append(ac)

    comp_audio = CompositeAudioClip(tracks)
    if MOVIEPY_V2:
        comp_audio = comp_audio.with_duration(duration)
    else:
        comp_audio = comp_audio.set_duration(duration)

    # Guardar vista previa del sketch
    for idx_s, sample_t in enumerate([4.5, 14.5, 24.5], start=1):
        arr = make_frame_fn(sample_t)
        Image.fromarray(arr).save(OUTPUT_DIR / f"sketch{sketch_id}_scene{idx_s}.jpg", quality=92)

    out_path = OUTPUT_DIR / output_filename
    print(f"[Sketch {sketch_id} - 3/3] Renderizando 720 cuadros continuos a {FPS_SMOOTH} FPS en {out_path.name}...")
    vc = VideoClip(make_frame_fn, duration=duration)
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
    for tr in tracks:
        tr.close()
    print(f"      ¡Sketch {sketch_id} exportado en: {out_path}!")
    return out_path


def render_all_three_sketches(only_id: int | None = None) -> List[Path]:
    specs = {
        1: (
            make_idea1_frame,
            _sfx_idea1,
            [
                (0.4, "es-MX-DaliaNeural", "+8%", "Nivel uno: Cómo escribe mi papá en el celular.", "s1_1.mp3"),
                (4.2, "es-MX-JorgeNeural", "-10%", "A medio metro de distancia, con los lentes en la punta de la nariz y un solo dedo índice.", "s1_2.mp3"),
                (10.3, "es-MX-DaliaNeural", "+10%", "Nivel dos: Cómo escribo yo.", "s1_3.mp3"),
                (13.2, "es-MX-JorgeNeural", "+12%", "Con las dos manos, los pulgares volando a máxima velocidad y sin soltar el café.", "s1_4.mp3"),
                (20.3, "es-MX-DaliaNeural", "+10%", "Nivel tres: Los de quince años.", "s1_5.mp3"),
                (23.2, "es-MX-JorgeNeural", "+8%", "Ni siquiera miran la pantalla: agarran el teléfono como pan tostado mandando un audio de tres minutos mientras bailan.", "s1_6.mp3"),
            ],
            "sketch_1_generaciones.mp4",
        ),
        2: (
            make_idea2_frame,
            _sfx_idea2,
            [
                (0.4, "es-MX-DaliaNeural", "+10%", "Expectativa: El truco viral de internet para doblar una camisa o partir un pastel en un segundo.", "s2_1.mp3"),
                (8.3, "es-MX-JorgeNeural", "+6%", "Si esto funciona, mi vida entera ha sido una mentira. Déjenme calentar primero... ¡ahí les voy!", "s2_2.mp3"),
                (18.1, "es-MX-DaliaNeural", "+12%", "Realidad: Todo sale terriblemente mal.", "s2_3.mp3"),
                (25.2, "es-MX-JorgeNeural", "-5%", "Tres segundos en silencio procesando la humillación... y directo a la basura.", "s2_4.mp3"),
            ],
            "sketch_2_hacks.mp4",
        ),
        3: (
            make_idea3_frame,
            _sfx_idea3,
            [
                (0.3, "es-MX-JorgeNeural", "+18%", "¡Te doy cien pesos ahora mismo si me dices tres marcas de cereal en tres segundos! ¡Tres, dos, uno, tiempo!", "s3_1.mp3"),
                (10.4, "es-MX-DaliaNeural", "+14%", "¡Eh... Leche! ¡Kellogg's! ¡Bimbo!", "s3_2.mp3"),
                (20.2, "es-MX-JorgeNeural", "+8%", "¡Tiempo fuera! Ni modo, la leche y el pan no cuentan, pero toma tu Frutsi de premio de consolación. ¡Adiós!", "s3_3.mp3"),
            ],
            "sketch_3_reto_callejero.mp4",
        ),
    }

    outputs: List[Path] = []
    target_ids = [only_id] if only_id in specs else [1, 2, 3]
    for sid in target_ids:
        fn_frame, fn_sfx, diag, out_name = specs[sid]
        outputs.append(_render_sketch(sid, fn_frame, fn_sfx, diag, out_name))
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, default=None, help="ID del sketch (1, 2 o 3). Omitir para renderizar los 3.")
    args = parser.parse_args()
    render_all_three_sketches(args.id)
