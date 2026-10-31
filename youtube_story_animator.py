"""
Motor de Animación Narrativa Estilo YouTube ("Don Zombi", "Curiosamente Graficado",
"Sobrevive con Bruno" y "Sebastián Schiller") a 24 FPS continuos.

Características clave:
  - CERO acotaciones literales ("ESCENA 1", "*Sale corriendo*", etc.).
  - Ilustraciones estilo cómic 2D de alta calidad (contornos negros limpios, iluminación dramática,
    personaje expresivo de cabeza blanca redondeada en escenarios detallados).
  - Movimiento continuo de cámara a 24 FPS (paneo cinematográfico, zoom suave, partículas/atmósfera
    en tiempo real y línea de tiempo inferior estilo Sebastián Schiller / Don Zombi).
  - Títulos estilo miniatura de YouTube con borde negro grueso ("7 DÍAS ANTES DEL CAOS",
    "DÍA 1 vs DÍA 7", "¿POR QUÉ NO PODEMOS ENTRAR?") y subtítulos limpios palabra por palabra.
"""

import argparse
import asyncio
import base64
from io import BytesIO
import json
import math
import urllib.parse
import wave
from pathlib import Path
from typing import Any, Dict, List, Tuple

import edge_tts
from google import genai
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
import requests

from config import GEMINI_API_KEY, OUTPUT_DIR, VIDEO_HEIGHT, VIDEO_WIDTH

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


def fetch_or_generate_comic_art(prompt: str, dest_path: Path, seed: int = 101) -> Path:
    """
    Si la ilustración cómic 2D ya existe en `dest_path`, la reutiliza.
    Si no existe, intenta generarla con `gemini-nano-banana-2.1` o con el motor
    gratuito Flux (Pollinations) en formato vertical 9:16.
    """
    if dest_path.exists() and dest_path.stat().st_size > 15_000:
        return dest_path

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Intentar con Gemini Nano Banana 2.1 (si la cuenta tiene cuota habilitada)
    if GEMINI_API_KEY and GEMINI_API_KEY != "tu_api_key_de_gemini_aqui":
        try:
            client = genai.Client(api_key=GEMINI_API_KEY, http_options={"timeout": 20000})
            interaction = client.interactions.create(
                model="gemini-nano-banana-2.1",
                input=prompt,
                response_format={"type": "image", "aspect_ratio": "9:16"},
            )
            if getattr(interaction, "output_image", None) and getattr(interaction.output_image, "data", None):
                raw_bytes = base64.b64decode(interaction.output_image.data)
                im = Image.open(BytesIO(raw_bytes)).convert("RGB")
                im.save(dest_path)
                return dest_path
        except Exception:
            pass

    # 2. Respaldo gratuito Flux 2D Cartoon (Pollinations API)
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&seed={seed}&model=flux&nologo=true"
        r = requests.get(url, timeout=25)
        if r.status_code == 200 and len(r.content) > 15_000:
            im = Image.open(BytesIO(r.content)).convert("RGB")
            im.save(dest_path)
            return dest_path
    except Exception:
        pass

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


def _group_timings_into_phrases(timings: List[Dict[str, Any]], max_words: int = 4) -> List[Dict[str, Any]]:
    words = [e for e in timings if e.get("type") == "WordBoundary"]
    if words:
        phrases: List[Dict[str, Any]] = []
        cur: List[Dict[str, Any]] = []
        for w in words:
            cur.append(w)
            if len(cur) >= max_words:
                phrases.append(
                    {
                        "start": cur[0]["start"],
                        "end": cur[-1]["end"],
                        "words": [x["text"] for x in cur],
                        "word_starts": [x["start"] for x in cur],
                    }
                )
                cur = []
        if cur:
            phrases.append(
                {
                    "start": cur[0]["start"],
                    "end": cur[-1]["end"],
                    "words": [x["text"] for x in cur],
                    "word_starts": [x["start"] for x in cur],
                }
            )
        return phrases

    sents = [e for e in timings if e.get("type") == "SentenceBoundary"]
    phrases = []
    for sent in sents:
        w_list = sent.get("text", "").split()
        if not w_list:
            continue
        s0 = sent["start"]
        dur = max(0.5, sent["end"] - s0)
        groups = [w_list[i : i + max_words] for i in range(0, len(w_list), max_words)]
        g_dur = dur / len(groups)
        for idx, g in enumerate(groups):
            gs = s0 + idx * g_dur
            w_dur = g_dur / max(1, len(g))
            phrases.append(
                {
                    "start": gs,
                    "end": gs + g_dur,
                    "words": g,
                    "word_starts": [gs + j * w_dur for j in range(len(g))],
                }
            )
    return phrases


def _synthesize_cinematic_ambience(wav_path: Path, duration: float, mode: str = "zombie") -> Path:
    """
    Crea una atmósfera sonora cinematográfica continua (pulso de suspenso oscuro + sub-bajo)
    que acompaña la narración sin tapar la voz.
    """
    sr = 22050
    t = np.linspace(0, duration, int(duration * sr), endpoint=False)
    if mode == "zombie":
        # Pulso de suspenso estilo Don Zombi / Sobrevive con Bruno
        drone = 0.08 * np.sin(2 * np.pi * 55.0 * t) + 0.05 * np.sin(2 * np.pi * 110.0 * t)
        pulse = 0.11 * np.exp(-8.0 * ((t * 1.5) % 1.0)) * np.sin(2 * np.pi * 65.41 * t)
        tension = 0.03 * np.sin(2 * np.pi * (220.0 + 8.0 * np.sin(2 * np.pi * 0.25 * t)) * t)
        audio = drone + pulse + tension
    else:
        # Atmósfera de misterio profundo / exploración estilo Curiosamente Graficado / Sebastián Schiller
        drone = 0.07 * np.sin(2 * np.pi * 73.42 * t) + 0.05 * np.sin(2 * np.pi * 146.83 * t)
        pulse = 0.09 * np.exp(-6.0 * ((t * 1.2) % 1.0)) * np.sin(2 * np.pi * 98.0 * t)
        shimmer = 0.03 * np.sin(2 * np.pi * 440.0 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t))
        audio = drone + pulse + shimmer

    audio = np.clip(audio, -0.9, 0.9)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    return wav_path


def build_illustrated_youtube_video(
    story_id: str,
    script_text: str,
    scene_files: List[Path],
    scene_badges: List[Tuple[str, str, Tuple[int, int, int]]],
    timeline_labels: List[str],
    output_filename: str,
    ambience_mode: str = "zombie",
) -> Path:
    """
    Renderiza un video vertical 1080x1920 a 24 FPS continuos al estilo de:
      - Don Zombi ("7 DÍAS ANTES DEL CAOS")
      - Sobrevive con Bruno ("DÍA 1" -> "DÍA 3" -> "DÍA 7")
      - Curiosamente Graficado ("¿POR QUÉ NO PODEMOS ENTRAR?")
      - Sebastián Schiller (barra de línea de tiempo inferior animada)
    """
    temp_dir = OUTPUT_DIR / f"yt_{story_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    audio_path = temp_dir / "narration.mp3"

    print(f"[{story_id}] 1/3 Generando narración documental con sincronización palabra por palabra...")
    raw_timings = asyncio.run(_tts_with_word_timings(script_text, "es-MX-JorgeNeural", "+6%", audio_path))
    phrases = _group_timings_into_phrases(raw_timings, max_words=4)

    voice_clip = AudioFileClip(str(audio_path))
    total_dur = voice_clip.duration + 0.4

    bg_wav = _synthesize_cinematic_ambience(temp_dir / "ambience.wav", total_dur, mode=ambience_mode)
    bg_clip = AudioFileClip(str(bg_wav))
    comp_audio = CompositeAudioClip([bg_clip, voice_clip])
    if MOVIEPY_V2:
        comp_audio = comp_audio.with_duration(total_dur)
    else:
        comp_audio = comp_audio.set_duration(total_dur)

    # Pre-cargar y escalar las ilustraciones 2D a tamaño extra (1260x2240) para paneo y zoom suave a 24 FPS
    overscan_w, overscan_h = int(VIDEO_WIDTH * 1.16), int(VIDEO_HEIGHT * 1.16)
    loaded_scenes: List[Image.Image] = []
    for sf in scene_files:
        im = Image.open(sf).convert("RGB")
        im = ImageOps.fit(im, (overscan_w, overscan_h), method=Image.Resampling.LANCZOS)
        im = ImageEnhance.Contrast(im).enhance(1.06)
        loaded_scenes.append(im)

    num_scenes = len(loaded_scenes)

    def make_frame(t: float) -> np.ndarray:
        prog = min(1.0, max(0.0, t / max(0.1, total_dur)))
        s_float = prog * num_scenes
        s_idx = min(num_scenes - 1, int(s_float))
        s_prog = min(1.0, max(0.0, s_float - s_idx))

        base_im = loaded_scenes[s_idx]
        # Movimiento de cámara continuo a 24 FPS (zoom + paneo lateral suave + ligera vibración de acción)
        if s_idx % 2 == 0:
            zoom_factor = 1.0 - 0.12 * s_prog
            pan_x = int(math.sin(s_prog * math.pi) * 35)
        else:
            zoom_factor = 0.88 + 0.12 * s_prog
            pan_x = int(math.cos(s_prog * math.pi) * 35)

        cw = int(VIDEO_WIDTH + (overscan_w - VIDEO_WIDTH) * zoom_factor)
        ch = int(VIDEO_HEIGHT + (overscan_h - VIDEO_HEIGHT) * zoom_factor)
        left = max(0, min(overscan_w - cw, (overscan_w - cw) // 2 + pan_x))
        top = max(0, min(overscan_h - ch, (overscan_h - ch) // 2))

        frame = base_im.crop((left, top, left + cw, top + ch)).resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.BILINEAR)
        draw = ImageDraw.Draw(frame, "RGBA")

        # Viñeta oscura superior e inferior para que los títulos y subtítulos resalten con nitidez
        draw.rectangle([0, 0, VIDEO_WIDTH, 285], fill=(0, 0, 0, 115))
        draw.rectangle([0, 1460, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(0, 0, 0, 155))

        # Partículas atmosféricas continuas a 24 FPS (cenizas en apocalipsis zombi / luciérnagas en selva)
        for p_i in range(18):
            px = int((p_i * 137 + t * (45 + (p_i % 3) * 18)) % VIDEO_WIDTH)
            py = int((p_i * 193 - t * (55 + (p_i % 4) * 15)) % VIDEO_HEIGHT)
            p_col = (255, 120, 50, 175) if ambience_mode == "zombie" else (160, 255, 120, 175)
            r_p = 3 + (p_i % 4)
            draw.ellipse([px - r_p, py - r_p, px + r_p, py + r_p], fill=p_col)

        # 1. TÍTULO ESTILO MINIATURA DE YOUTUBE ARRIBA (como "7 DÍAS / ANTES DEL CAOS" o "¿POR QUÉ NO PODEMOS ENTRAR?")
        top_title, red_tag, accent_col = scene_badges[min(s_idx, len(scene_badges) - 1)]
        draw.text(
            (VIDEO_WIDTH // 2, 118),
            top_title,
            font=_font(72, bold=True),
            fill=(255, 255, 255, 255),
            anchor="mm",
            stroke_width=8,
            stroke_fill=(0, 0, 0, 255),
        )
        if red_tag:
            tw_bbox = draw.textbbox((0, 0), red_tag, font=_font(44, bold=True))
            tw = tw_bbox[2] - tw_bbox[0]
            bx1 = (VIDEO_WIDTH - tw) // 2 - 28
            bx2 = (VIDEO_WIDTH + tw) // 2 + 28
            draw.rounded_rectangle([bx1, 172, bx2, 238], radius=12, fill=accent_col + (245,), outline=(0, 0, 0, 255), width=4)
            draw.text((VIDEO_WIDTH // 2, 205), red_tag, font=_font(42, bold=True), fill=(255, 255, 255, 255), anchor="mm")

        # 2. SUBTÍTULOS DINÁMICOS LIMPIOS (solo lo que dice el narrador, resaltando la palabra activa)
        active_phrase = None
        for ph in phrases:
            if ph["start"] - 0.08 <= t <= ph["end"] + 0.15:
                active_phrase = ph
                break

        if active_phrase:
            words = [w.upper() for w in active_phrase["words"]]
            starts = active_phrase["word_starts"]
            active_w_idx = 0
            for wi, ws in enumerate(starts):
                if t >= ws - 0.04:
                    active_w_idx = wi

            f_sub = _font(58, bold=True)
            full_line = " ".join(words)
            lb = draw.textbbox((0, 0), full_line, font=f_sub)
            lw = lb[2] - lb[0]
            cur_x = (VIDEO_WIDTH - lw) // 2
            sub_y = 1565

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

        # 3. LÍNEA DE TIEMPO INFERIOR ESTILO SEBASTIÁN SCHILLER / SOBREVIVE CON BRUNO
        tl_y = 1815
        draw.line([(85, tl_y), (VIDEO_WIDTH - 85, tl_y)], fill=(255, 255, 255, 140), width=4)
        prog_x = int(85 + (VIDEO_WIDTH - 170) * prog)
        draw.line([(85, tl_y), (prog_x, tl_y)], fill=(255, 215, 0, 255), width=6)
        draw.ellipse([prog_x - 10, tl_y - 10, prog_x + 10, tl_y + 10], fill=(255, 215, 0, 255), outline=(0, 0, 0, 255), width=3)

        for idx_l, lbl in enumerate(timeline_labels):
            lx = int(115 + idx_l * ((VIDEO_WIDTH - 230) / max(1, len(timeline_labels) - 1)))
            draw.line([(lx, tl_y - 12), (lx, tl_y + 12)], fill=(255, 255, 255, 200), width=3)
            draw.text((lx, tl_y + 34), lbl, font=_font(26, bold=True), fill=(235, 235, 235, 230), anchor="mm")

        return np.asarray(frame.convert("RGB"))

    # Guardar fotograma de vista previa
    preview_arr = make_frame(min(3.5, total_dur * 0.2))
    preview_path = OUTPUT_DIR / f"preview_{story_id}.jpg"
    Image.fromarray(preview_arr).save(preview_path, quality=94)

    out_path = OUTPUT_DIR / output_filename
    print(f"[{story_id}] 2/3 Renderizando video a {FPS_SMOOTH} FPS continuos en {out_path.name}...")
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
    print(f"[{story_id}] 3/3 ¡Exportado con éxito en: {out_path}!")
    return out_path


def run_youtube_style_demos() -> List[Path]:
    outputs: List[Path] = []

    # VIDEO 1: Estilo "Don Zombi" / "Sobrevive con Bruno"
    zombi_script = (
        "¿Qué harías si hoy mismo comenzara un apocalipsis zombi y solo tuvieras siete días antes del colapso total? "
        "En el día uno, el error mortal que comete el noventa por ciento de la gente es correr al supermercado cuando ya es demasiado tarde: "
        "en menos de dos horas el agua potable, las latas y las baterías desaparecen por completo. "
        "Para el día tres, cuando cae la electricidad y las calles dejan de ser seguras, tu única opción es bloquear puertas y ventanas en silencio absoluto, "
        "porque el más mínimo ruido atrae a toda la horda. "
        "Y si logras resistir hasta el día noventa, los únicos sobrevivientes son los que alcanzan zonas altas aisladas en la costa esperando un rescate."
    )
    zombi_scenes = [
        OUTPUT_DIR / "zombi_1.png",
        OUTPUT_DIR / "zombi_2.png",
        OUTPUT_DIR / "zombi_3.png",
    ]
    zombi_badges = [
        ("7 DÍAS", "ANTES DEL CAOS", (215, 35, 35)),
        ("DÍA 3", "NO HAGAS RUIDO", (215, 35, 35)),
        ("DÍA 90", "EL RESCATE FINAL", (225, 45, 35)),
    ]
    outputs.append(
        build_illustrated_youtube_video(
            story_id="don_zombi",
            script_text=zombi_script,
            scene_files=zombi_scenes,
            scene_badges=zombi_badges,
            timeline_labels=["DÍA 1: EL CAOS", "DÍA 3: EL APAGÓN", "DÍA 90: RESCATE"],
            output_filename="yt_apocalipsis_zombi.mp4",
            ambience_mode="zombie",
        )
    )

    # VIDEO 2: Estilo "Curiosamente Graficado" / "Sebastián Schiller"
    selva_script = (
        "¿Por qué realmente no podemos explorar las profundidades de las selvas más densas del planeta ni siquiera con tecnología moderna? "
        "Aunque hoy tenemos satélites y drones avanzados, el techo de árboles en las zonas inexploradas del Amazonas es tan espeso que bloquea el noventa y nueve por ciento de la señal y de la luz del sol. "
        "Abajo, en la oscuridad perpetua del suelo selvático, la humedad destruye los equipos electrónicos en cuestión de horas, "
        "y habitan especies venenosas y ruinas ocultas donde ningún ser humano ha podido sobrevivir por mucho tiempo."
    )
    selva_scenes = [
        OUTPUT_DIR / "selva_1.png",
        OUTPUT_DIR / "selva_2.png",
    ]
    selva_badges = [
        ("¿POR QUÉ NO", "PODEMOS ENTRAR?", (200, 35, 35)),
        ("EL 99% SIN LUZ", "ZONA INEXPLORADA", (25, 145, 75)),
    ]
    outputs.append(
        build_illustrated_youtube_video(
            story_id="curiosamente_selva",
            script_text=selva_script,
            scene_files=selva_scenes,
            scene_badges=selva_badges,
            timeline_labels=["0 KM: ENTRADA", "50 KM: SIN SEÑAL", "ZONA CERO"],
            output_filename="yt_misterio_selva.mp4",
            ambience_mode="jungle",
        )
    )

    return outputs


if __name__ == "__main__":
    run_youtube_style_demos()
