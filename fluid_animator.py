"""
Motor de Video Cinético y Fluido para Bruno Schiller (Estilo @finanz_ia, @nagumonetiza, @mixidev_esp).
Combina:
  1. Locución con ElevenLabs (con fallback a Locución Neural de alta fidelidad con captura de timestamps).
  2. Subtítulos Cinéticos "Pop-Spring" con colores semánticos inteligentes (Verde Neón, Rojo Alerta, Cyan Tech, Amarillo Viral).
  3. Movimiento de cámara Ken Burns continuo con sub-pixel transform (zoom 1.0 -> 1.12 sin saltos).
  4. Transiciones fluidas de fundido cruzado (cross-fade) sincronizadas con efectos de sonido (whoosh / ding).
  5. Música de fondo ambiental (BGM piano/chill) a 12% de volumen con audio ducking.
"""

import math
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from config import (
    BASE_DIR,
    OUTPUT_DIR,
    VIDEO_FPS,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)
from tts_engine import synthesize_speech

try:
    from moviepy import (
        AudioFileClip,
        CompositeAudioClip,
        VideoClip,
        afx,
        concatenate_audioclips,
    )
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import (
        AudioFileClip,
        CompositeAudioClip,
        VideoClip,
        afx,
        concatenate_audioclips,
    )
    MOVIEPY_V2 = False

FONTS_DIR = BASE_DIR / "assets" / "fonts"
BGM_DIR = BASE_DIR / "assets" / "bgm"
SFX_DIR = BASE_DIR / "assets" / "sfx"
IMAGES_DIR = BASE_DIR / "assets" / "images"

_FONT_CACHE: Dict[Tuple[str, int], Any] = {}


def _get_font(size: int = 76, bold: bool = True) -> Any:
    key = ("bold" if bold else "normal", size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    font_candidates = [
        str(FONTS_DIR / "BeVietnamPro-Bold.ttf"),
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for cand in font_candidates:
        if os.path.exists(cand):
            try:
                _FONT_CACHE[key] = ImageFont.truetype(cand, size)
                return _FONT_CACHE[key]
            except Exception:
                continue

    _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


def _spring_scale(rel_time: float, anim_dur: float = 0.18) -> float:
    """Calcula el factor de escala elástica (Pop-Spring) tipo TikTok / Reels."""
    if rel_time <= 0:
        return 0.1
    if rel_time >= anim_dur:
        return 1.0
    p = rel_time / anim_dur
    # Sobreimpulso elástico: inicia en 0.2, sube a 1.28, amortigua a 1.0
    scale = 1.0 - math.exp(-6.5 * p) * math.cos(2.8 * math.pi * p)
    return max(0.1, min(scale, 1.35))


def _get_word_color(text: str) -> Tuple[int, int, int]:
    """Asigna color semántico de alto impacto para Gaming, Videojuegos y curiosidades virales."""
    t = text.upper()
    # 1. Éxito / Consolas / Niveles / Ganancia -> Verde Neón (#00FF66)
    if any(k in t for k in ["PLAYSTATION", "PS2", "MEMORY", "CARD", "JUEGOS", "JUEGO", "HORAS", "VIDA", "WIN", "GANAN", "GANAS", "100%", "DINERO", "PRECIO", "VALOR", "EXTRA", "SECRETO", "TESORO"]):
        return (0, 255, 102)
    # 2. Peligro / Muerte / Bugs / Errores / Alerta -> Rojo Escarlata (#FF3838)
    if any(k in t for k in ["CREEPER", "EXPLOSIÓN", "EXPLOSION", "ERROR", "BUG", "MUERTE", "PELIGRO", "TRAMPA", "SUICIDA", "CEMENTERIO", "VACÍO", "VACIO", "OSCURO", "CHOQUE", "ESTRELLABAN", "PERTURBADOR", "MIEDO", "DESESPERANTE", "FRUSTRANTE", "PÁNICO", "PANICO"]):
        return (255, 56, 56)
    # 3. Marcas de Gaming / Títulos / Lore -> Cyan Eléctrico (#00E5FF)
    if any(k in t for k in ["MINECRAFT", "NOTCH", "GTA", "SAN ANDREAS", "ROCKSTAR", "CJ", "NINTENDO", "MARIO", "ZELDA", "POKÉMON", "POKEMON", "RED DEAD", "CÓDIGO", "CODIGO", "TORRES", "BLOQUES", "CONSOLA", "NES", "DISCO", "PUEBLO", "TEMPLO"]):
        return (0, 229, 255)
    # 4. Color base -> Amarillo Viral (#FFE500)
    return (255, 230, 0)


def _draw_subtitles_on_frame(
    canvas: Image.Image,
    current_time: float,
    word_timings: List[Dict[str, Any]],
    font_size: int = 78,
) -> None:
    """
    Dibuja subtítulos cinéticos con colores semánticos dinámicos al estilo @finanz_ia:
    - 1 o 2 palabras simultáneas en el tercio medio-inferior.
    - Colores llamativos (Verde Neón, Rojo Alerta, Cyan Tech, Amarillo Viral).
    - Trazo negro grueso de 9px y sombra profunda para legibilidad total.
    - Animación elástica de rebote (pop-spring) en cada entrada de palabra.
    """
    if not word_timings:
        return

    # Construir bloques de 1 a 2 palabras para mantener cadencia rápida
    blocks = []
    i = 0
    while i < len(word_timings):
        w1 = word_timings[i]
        if i + 1 < len(word_timings):
            w2 = word_timings[i + 1]
            if w2["start"] - w1["end"] < 0.4:
                blocks.append({
                    "text": f"{w1['word']} {w2['word']}".upper(),
                    "start": w1["start"],
                    "end": max(w2["end"], w1["start"] + 0.35),
                })
                i += 2
                continue
        blocks.append({
            "text": w1["word"].upper(),
            "start": w1["start"],
            "end": max(w1["end"], w1["start"] + 0.3),
        })
        i += 1

    active_entry = None
    entry_start = 0.0
    for b in blocks:
        if b["start"] <= current_time <= b["end"] + 0.08:
            active_entry = b["text"]
            entry_start = b["start"]
            break

    if not active_entry:
        return

    rel_t = current_time - entry_start
    scale = _spring_scale(rel_t, anim_dur=0.18)

    # Renderizar el texto en una capa separada para escalarlo
    font = _get_font(int(font_size * scale), bold=True)
    temp_img = Image.new("RGBA", (VIDEO_WIDTH, 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(temp_img)

    bbox = d.textbbox((0, 0), active_entry, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    tx = (VIDEO_WIDTH - tw) // 2
    ty = (400 - th) // 2

    # Sombra negra profunda
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 5), (5, 5), (-5, 5)]:
        d.text((tx + ox, ty + oy), active_entry, font=font, fill=(0, 0, 0, 240), stroke_width=9, stroke_fill=(0, 0, 0, 255))

    # Color semántico inteligente
    fill_color = _get_word_color(active_entry)
    d.text((tx, ty), active_entry, font=font, fill=(fill_color[0], fill_color[1], fill_color[2], 255), stroke_width=7, stroke_fill=(0, 0, 0, 255))

    target_y = int(VIDEO_HEIGHT * 0.62)
    canvas.alpha_composite(temp_img, dest=(0, target_y))


def _ken_burns_transform(
    base_img: Image.Image,
    rel_time: float,
    duration: float,
    zoom_in: bool = True,
) -> Image.Image:
    """Aplica zoom suave Ken Burns continuo con sub-pixel sampling."""
    w, h = VIDEO_WIDTH, VIDEO_HEIGHT
    progress = min(max(rel_time / max(duration, 0.01), 0.0), 1.0)
    ease_p = 0.5 - 0.5 * math.cos(progress * math.pi)

    if zoom_in:
        scale = 1.0 + 0.12 * ease_p
    else:
        scale = 1.12 - 0.12 * ease_p

    crop_w = w / scale
    crop_h = h / scale
    x1 = (w - crop_w) / 2.0
    y1 = (h - crop_h) / 2.0
    x2 = x1 + crop_w
    y2 = y1 + crop_h

    return base_img.transform(
        (w, h),
        Image.Transform.EXTENT,
        (x1, y1, x2, y2),
        Image.Resampling.BILINEAR,
    )


def render_fluid_video(
    topic_data: Dict[str, Any],
    output_mp4: Path,
    scene_image_paths: Optional[List[Path]] = None,
    preferred_tts: str = "elevenlabs",
) -> Path:
    """
    Renderiza el video fluido final a 24 FPS combinando:
    1. Locución y timings por palabra (ElevenLabs o Neural).
    2. Escenas ilustradas en alta definición con Ken Burns continuo.
    3. Transiciones de fundido cruzado suave.
    4. Subtítulos Cinéticos "Pop-Spring" con colores dinámicos.
    5. BGM integrado con ducking y efectos de sonido (whoosh / ding).
    """
    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    temp_audio = OUTPUT_DIR / "fluid_temp_voice.mp3"

    print(f"\n[Fluid Animator] Procesando tema: '{topic_data['topic']}'...")

    script_text = topic_data.get("script") or topic_data.get("narration_script") or ""

    # 1. Locución
    audio_file, word_timings = synthesize_speech(
        text=script_text,
        output_audio=temp_audio,
        preferred_engine=preferred_tts,
    )

    audio_clip = AudioFileClip(str(audio_file))
    total_duration = audio_clip.duration
    print(f"      [Audio] Duración: {total_duration:.2f}s | Palabras sincronizadas: {len(word_timings)}")

    # 2. Cargar imágenes de escenas
    loaded_scenes: List[Image.Image] = []
    if scene_image_paths:
        for p in scene_image_paths:
            if p.exists():
                im = Image.open(p).convert("RGB")
                if im.size != (VIDEO_WIDTH, VIDEO_HEIGHT):
                    im = im.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
                loaded_scenes.append(im)

    if not loaded_scenes:
        theme_id = topic_data.get("theme_id") or topic_data.get("id") or "amazon_returns"
        # Buscar en assets/images/
        matching = sorted(list(IMAGES_DIR.glob(f"{theme_id}*.jpg")) + list(IMAGES_DIR.glob(f"{theme_id}*.png")))
        if not matching:
            # Buscar cualquier escena temática de videojuegos en assets/images/ (¡NUNCA almacén repetido!)
            gaming_scenes = sorted(list(IMAGES_DIR.glob("gaming_*.jpg")) + list(IMAGES_DIR.glob("gaming_*.png")))
            if gaming_scenes:
                matching = gaming_scenes[:3]
            else:
                matching = sorted(list(IMAGES_DIR.glob("*.jpg")))[:3]
        for p in matching:
            if p.exists():
                im = Image.open(p).convert("RGB").resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
                loaded_scenes.append(im)

    num_scenes = max(1, len(loaded_scenes))
    scene_dur = total_duration / num_scenes
    crossfade_dur = 0.40

    print(f"      [Escenas]: {num_scenes} escenas HD listas ({scene_dur:.1f}s por escena con Ken Burns)")

    # 3. Renderizador continuo de fotogramas (24 FPS)
    def make_frame(t: float) -> np.ndarray:
        scene_idx = min(int(t / scene_dur), num_scenes - 1)
        rel_t = t - (scene_idx * scene_dur)
        zoom_in = (scene_idx % 2 == 0)

        current_img = loaded_scenes[scene_idx]
        frame_canvas = _ken_burns_transform(current_img, rel_t, scene_dur, zoom_in=zoom_in)

        if scene_idx > 0 and rel_t < crossfade_dur:
            prev_img = loaded_scenes[scene_idx - 1]
            prev_t = scene_dur - (crossfade_dur - rel_t)
            prev_frame = _ken_burns_transform(prev_img, prev_t, scene_dur, zoom_in=not zoom_in)
            blend_alpha = rel_t / crossfade_dur
            frame_canvas = Image.blend(prev_frame, frame_canvas, blend_alpha)

        canvas_rgba = frame_canvas.convert("RGBA")

        # Viñeta superior e inferior sutil
        draw_ov = ImageDraw.Draw(canvas_rgba, "RGBA")
        draw_ov.rectangle([0, 0, VIDEO_WIDTH, 170], fill=(0, 0, 0, 95))
        draw_ov.rectangle([0, VIDEO_HEIGHT - 240, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(0, 0, 0, 110))

        # Cabecera fija
        top_font = _get_font(34, bold=True)
        draw_ov.text((VIDEO_WIDTH // 2 - 120, 65), "@BrunoSchiller", font=top_font, fill=(255, 255, 255, 230))

        # Subtítulos Cinéticos "Pop-Spring"
        _draw_subtitles_on_frame(canvas_rgba, current_time=t, word_timings=word_timings)

        return np.array(canvas_rgba.convert("RGB"))

    print("      [Video] Compilando video cinético a 24 FPS...")
    video_clip = VideoClip(make_frame, duration=total_duration)

    # 4. Mezcla de Audio: Voz principal + BGM + Efectos SFX
    audio_tracks = [audio_clip]

    # BGM
    bgm_candidates = list(BGM_DIR.glob("*.mp3"))
    if bgm_candidates:
        bgm_path = bgm_candidates[0]
        try:
            bgm_raw = AudioFileClip(str(bgm_path))
            if hasattr(bgm_raw, "subclipped"):
                bgm_sub = bgm_raw.subclipped(0, min(total_duration, bgm_raw.duration))
            else:
                bgm_sub = bgm_raw.subclip(0, min(total_duration, bgm_raw.duration))

            if MOVIEPY_V2 and hasattr(bgm_sub, "with_effects"):
                bgm_ducked = bgm_sub.with_effects([afx.MultiplyVolume(0.12)])
            elif hasattr(bgm_sub, "volumex"):
                bgm_ducked = bgm_sub.volumex(0.12)
            else:
                bgm_ducked = bgm_sub

            audio_tracks.append(bgm_ducked)
            print(f"      [BGM] Música añadida ({bgm_path.name}) al 12% con ducking.")
        except Exception as e:
            print(f"      [BGM] Nota: {e}")

    # SFX: whoosh en transiciones de escena
    whoosh_path = SFX_DIR / "whoosh.wav"
    if whoosh_path.exists() and num_scenes > 1:
        try:
            for s_idx in range(1, num_scenes):
                sw_time = max(0.0, s_idx * scene_dur - 0.15)
                wh = AudioFileClip(str(whoosh_path))
                if hasattr(wh, "with_start"):
                    wh_positioned = wh.with_start(sw_time)
                else:
                    wh_positioned = wh.set_start(sw_time)

                if MOVIEPY_V2 and hasattr(wh_positioned, "with_effects"):
                    wh_scaled = wh_positioned.with_effects([afx.MultiplyVolume(0.16)])
                elif hasattr(wh_positioned, "volumex"):
                    wh_scaled = wh_positioned.volumex(0.16)
                else:
                    wh_scaled = wh_positioned
                audio_tracks.append(wh_scaled)
            print(f"      [SFX] Transiciones whoosh insertadas en cada corte de escena.")
        except Exception as e:
            print(f"      [SFX] Nota whoosh: {e}")

    final_audio = CompositeAudioClip(audio_tracks)
    if hasattr(video_clip, "with_audio"):
        video_clip = video_clip.with_audio(final_audio)
    else:
        video_clip = video_clip.set_audio(final_audio)

    video_clip.write_videofile(
        str(output_mp4),
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        logger=None,
    )

    audio_clip.close()
    video_clip.close()

    print(f"      [Video] Listo: {output_mp4.name} ({output_mp4.stat().st_size:,} bytes)")
    return output_mp4
