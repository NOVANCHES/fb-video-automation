"""
Módulo 2: Subtítulos Dinámicos + Animación Ken Burns (Zoom/Paneo) + Tarjetas Visuales de Ejemplos.
"""

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image, ImageDraw, ImageFont

from animator import render_iadeguardia_frame
from config import IMAGES_DIR, OUTPUT_DIR, VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH, WHISPER_MODEL

try:
    from moviepy import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips
    MOVIEPY_V2 = False


def _ensure_ffmpeg_in_path() -> str:
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        return ffmpeg_bin

    import imageio_ffmpeg

    ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    local_bin_dir = OUTPUT_DIR / ".bin"
    local_bin_dir.mkdir(parents=True, exist_ok=True)
    standard_ffmpeg = local_bin_dir / "ffmpeg.exe"
    if not standard_ffmpeg.exists():
        shutil.copy2(ffmpeg_exe, standard_ffmpeg)
    os.environ["PATH"] = f"{local_bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    return str(standard_ffmpeg)


def _format_srt_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours = millis // 3_600_000
    millis %= 3_600_000
    minutes = millis // 60_000
    millis %= 60_000
    secs = millis // 1_000
    millis %= 1_000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _chunks_from_timings_json(timings_path: Path, max_words: int = 4) -> List[Dict[str, Any]]:
    events = json.loads(timings_path.read_text(encoding="utf-8"))
    word_events = [e for e in events if e.get("type") == "WordBoundary"]

    if word_events:
        chunks: List[Dict[str, Any]] = []
        cur_words: List[str] = []
        chunk_start = None
        last_end = 0.0
        for ev in word_events:
            if chunk_start is None:
                chunk_start = ev["start"]
            cur_words.append(ev["text"])
            last_end = ev["end"]
            if len(cur_words) >= max_words:
                chunks.append({"start": chunk_start, "end": last_end, "text": " ".join(cur_words)})
                cur_words = []
                chunk_start = None
        if cur_words and chunk_start is not None:
            chunks.append({"start": chunk_start, "end": last_end, "text": " ".join(cur_words)})
        return chunks

    sentence_events = [e for e in events if e.get("type") == "SentenceBoundary"]
    chunks = []
    for sent in sentence_events:
        words = sent.get("text", "").split()
        if not words:
            continue
        start = sent["start"]
        total_dur = max(sent["end"] - start, 0.5)
        groups = [words[i : i + max_words] for i in range(0, len(words), max_words)]
        dur_per_group = total_dur / len(groups)
        for idx, grp in enumerate(groups):
            g_start = start + idx * dur_per_group
            g_end = g_start + dur_per_group
            chunks.append({"start": g_start, "end": g_end, "text": " ".join(grp)})
    return chunks


def generate_subtitles_srt(
    media_path: Path,
    srt_output_path: Path = OUTPUT_DIR / "subtitles.srt",
) -> tuple[Path, List[Dict[str, Any]]]:
    _ensure_ffmpeg_in_path()
    chunks: List[Dict[str, Any]] = []

    timings_path = OUTPUT_DIR / "timings.json"
    if timings_path.exists():
        print("[1/2] Generando subtítulos dinámicos sincronizados (3-4 palabras por bloque)...")
        chunks = _chunks_from_timings_json(timings_path, max_words=4)

    if not chunks:
        script_path = OUTPUT_DIR / "guion.txt"
        text = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
        words = re.findall(r"\S+", text)
        clip = VideoFileClip(str(media_path))
        total_dur = clip.duration
        clip.close()
        groups = [words[i : i + 4] for i in range(0, len(words), 4)] or [["VIDEO"]]
        dur_per_grp = total_dur / len(groups)
        for idx, grp in enumerate(groups):
            g_start = idx * dur_per_grp
            chunks.append({"start": g_start, "end": g_start + dur_per_grp, "text": " ".join(grp)})

    srt_lines: List[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        start_ts = _format_srt_timestamp(chunk["start"])
        end_ts = _format_srt_timestamp(max(chunk["end"], chunk["start"] + 0.25))
        text = chunk["text"].upper()
        srt_lines.append(f"{idx}\n{start_ts} --> {end_ts}\n{text}\n")

    srt_output_path.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"      Subtítulos SRT generados en: {srt_output_path} ({len(chunks)} bloques dinámicos)")
    return srt_output_path, chunks


def _load_fonts() -> tuple[Any, Any, Any]:
    bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    reg_path = r"C:\Windows\Fonts\segoeui.ttf"
    if os.path.exists(bold_path):
        font_sub = ImageFont.truetype(bold_path, 70)
        font_title = ImageFont.truetype(bold_path, 42)
        font_desc = ImageFont.truetype(reg_path if os.path.exists(reg_path) else bold_path, 32)
    else:
        default = ImageFont.load_default()
        font_sub, font_title, font_desc = default, default, default
    return font_sub, font_title, font_desc


def _render_animated_scene_frame(
    large_scene_img: Image.Image,
    scene_progress: float,
    video_progress: float,
    scene_idx: int,
    total_scenes: int,
    card_title: str,
    card_subtitle: str,
    subtitle_text: str,
    highlight_word_idx: int,
) -> Image.Image:
    """
    Aplica animación de cámara Ken Burns (zoom + paneo suave) sobre la fotografía HD,
    dibuja la tarjeta infográfica del ejemplo en la parte superior con barra de progreso
    animada, y resalta la palabra activa en los subtítulos inferiores.
    """
    lw, lh = large_scene_img.size
    # Zoom progresivo entre 1.0x y 1.15x del tamaño final
    extra_w = max(0, lw - VIDEO_WIDTH)
    extra_h = max(0, lh - VIDEO_HEIGHT)

    # Alternar dirección de movimiento entre escenas (zoom in vs pan suave)
    if scene_idx % 2 == 0:
        crop_scale = 1.0 - (0.12 * scene_progress)
    else:
        crop_scale = 0.88 + (0.12 * scene_progress)

    crop_w = int(VIDEO_WIDTH + extra_w * crop_scale)
    crop_h = int(VIDEO_HEIGHT + extra_h * crop_scale)
    left = max(0, (lw - crop_w) // 2)
    top = max(0, (lh - crop_h) // 2)

    cropped = large_scene_img.crop((left, top, left + crop_w, top + crop_h))
    img = cropped.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.BILINEAR)
    draw = ImageDraw.Draw(img, "RGBA")

    font_sub, font_title, font_desc = _load_fonts()

    # 1. Barra de progreso superior animada (amarillo / cian)
    bar_width = int(VIDEO_WIDTH * min(1.0, max(0.02, video_progress)))
    draw.rectangle([0, 0, VIDEO_WIDTH, 14], fill=(0, 0, 0, 160))
    draw.rectangle([0, 0, bar_width, 14], fill=(0, 230, 255, 255))

    # 2. Tarjeta visual del Ejemplo en la parte superior
    card_margin_x = 55
    card_top = 85
    card_bottom = 265
    draw.rounded_rectangle(
        [card_margin_x, card_top, VIDEO_WIDTH - card_margin_x, card_bottom],
        radius=26,
        fill=(10, 15, 28, 215),
        outline=(0, 220, 255, 220),
        width=3,
    )

    # Indicador numérico de escena (ej. "1/4")
    badge_text = f"ESCENA {scene_idx + 1}/{total_scenes}"
    draw.rounded_rectangle(
        [card_margin_x + 28, card_top - 22, card_margin_x + 245, card_top + 22],
        radius=14,
        fill=(0, 210, 255, 255),
    )
    draw.text(
        (card_margin_x + 136, card_top),
        badge_text,
        font=font_desc,
        fill=(10, 15, 28, 255),
        anchor="mm",
    )

    # Título del Ejemplo y explicación corta
    draw.text(
        (VIDEO_WIDTH // 2, card_top + 68),
        card_title[:36].upper(),
        font=font_title,
        fill=(255, 235, 0, 255),
        anchor="mm",
        stroke_width=3,
        stroke_fill=(0, 0, 0, 255),
    )
    if card_subtitle:
        draw.text(
            (VIDEO_WIDTH // 2, card_top + 128),
            card_subtitle[:52],
            font=font_desc,
            fill=(235, 245, 255, 255),
            anchor="mm",
        )

    # 3. Subtítulos dinámicos inferiores con resaltado de palabra activa (Karaoke/Reels)
    words = subtitle_text.upper().split()
    if not words:
        return img

    if len(words) >= 3:
        mid = (len(words) + 1) // 2
        lines = [words[:mid], words[mid:]]
    else:
        lines = [words]

    display_text = "\n".join(" ".join(line) for line in lines)
    bbox = draw.multiline_textbbox((0, 0), display_text, font=font_sub, align="center", spacing=14)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (VIDEO_WIDTH - text_w) // 2
    y = int(VIDEO_HEIGHT * 0.74) - (text_h // 2)

    pad_x, pad_y = 38, 24
    draw.rounded_rectangle(
        [x - pad_x, y - pad_y, x + text_w + pad_x, y + text_h + pad_y],
        radius=26,
        fill=(0, 0, 0, 195),
        outline=(255, 235, 0, 140),
        width=2,
    )

    # Dibujar palabra por palabra resaltando en amarillo neón la palabra activa y blanco el resto
    cur_y = y
    word_counter = 0
    for line_words in lines:
        line_str = " ".join(line_words)
        lb = draw.textbbox((0, 0), line_str, font=font_sub)
        line_w = lb[2] - lb[0]
        cur_x = (VIDEO_WIDTH - line_w) // 2
        for w in line_words:
            is_active = word_counter == highlight_word_idx
            fill_color = (255, 235, 0, 255) if is_active else (255, 255, 255, 255)
            draw.text(
                (cur_x, cur_y),
                w,
                font=font_sub,
                fill=fill_color,
                stroke_width=6,
                stroke_fill=(0, 0, 0, 255),
            )
            wb = draw.textbbox((0, 0), w + " ", font=font_sub)
            cur_x += wb[2] - wb[0]
            word_counter += 1
        cur_y += (bbox[3] - bbox[1]) // max(1, len(lines)) + 10

    return img


def burn_subtitles(
    video_path: Path,
    srt_path: Path,
    chunks: List[Dict[str, Any]],
    output_video_path: Path = OUTPUT_DIR / "video_final.mp4",
) -> Path:
    print("[2/2] Renderizando escenas animadas 2D (@iadeguardia), avatar parlante y subtítulos neón...")
    meta_path = OUTPUT_DIR / "scenes_meta.json"
    scenes_meta: List[Dict[str, Any]] = []
    if meta_path.exists():
        scenes_meta = json.loads(meta_path.read_text(encoding="utf-8"))

    num_scenes = max(4, len(scenes_meta))

    audio_path = OUTPUT_DIR / "narration.mp3"
    audio_clip = AudioFileClip(str(audio_path)) if audio_path.exists() else VideoFileClip(str(video_path)).audio
    total_dur = audio_clip.duration

    sub_frames_dir = OUTPUT_DIR / "sub_frames"
    sub_frames_dir.mkdir(parents=True, exist_ok=True)
    for old_f in sub_frames_dir.glob("sub_*.jpg"):
        old_f.unlink(missing_ok=True)

    clips = []
    cur_t = 0.0
    frame_counter = 0

    for idx, chunk in enumerate(chunks):
        c_end = min(total_dur, float(chunk["end"]))
        if idx == len(chunks) - 1:
            c_end = total_dur
        chunk_dur = max(0.20, c_end - cur_t)

        words = chunk["text"].split()
        # Subdividir cada bloque en pasos por palabra para animar el zoom + karaoke palabra por palabra
        num_steps = max(1, min(len(words), 3))
        step_dur = chunk_dur / num_steps

        for s in range(num_steps):
            step_t = cur_t + s * step_dur
            video_prog = step_t / max(total_dur, 0.1)
            scene_float = video_prog * num_scenes
            scene_idx = min(num_scenes - 1, int(scene_float))
            scene_prog = min(1.0, max(0.0, scene_float - scene_idx))

            meta = scenes_meta[scene_idx] if scene_idx < len(scenes_meta) else {}
            card_title = meta.get("title", f"EJEMPLO {scene_idx + 1}")
            card_sub = meta.get("subtitle", "")

            active_word = min(len(words) - 1, int((s / num_steps) * len(words)))
            rendered = render_iadeguardia_frame(
                scene_idx=scene_idx,
                total_scenes=num_scenes,
                scene_progress=scene_prog,
                video_progress=video_prog,
                card_title=card_title,
                card_subtitle=card_sub,
                subtitle_text=chunk["text"],
                highlight_word_idx=active_word,
                step_counter=frame_counter,
            )

            frame_path = sub_frames_dir / f"sub_{frame_counter:03d}.jpg"
            rendered.save(frame_path, quality=92)
            frame_counter += 1

            if MOVIEPY_V2:
                clip = ImageClip(str(frame_path)).with_duration(step_dur)
            else:
                clip = ImageClip(str(frame_path)).set_duration(step_dur)
            clips.append(clip)

        cur_t += chunk_dur
        if cur_t >= total_dur:
            break

    final_video = concatenate_videoclips(clips, method="chain")
    if MOVIEPY_V2:
        final_video = final_video.with_audio(audio_clip)
    else:
        final_video = final_video.set_audio(audio_clip)

    final_video.write_videofile(
        str(output_video_path),
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger=None,
    )
    audio_clip.close()
    final_video.close()
    print(f"      Video final animado exportado en: {output_video_path}")
    return output_video_path


def add_dynamic_subtitles(
    video_path: Path = OUTPUT_DIR / "video_base.mp4",
    output_video_path: Path = OUTPUT_DIR / "video_final.mp4",
) -> Path:
    from youtube_story_animator import (
        build_illustrated_youtube_video,
        detect_theme_from_text,
        get_theme_scene_files,
    )

    script_path = OUTPUT_DIR / "guion.txt"
    script_text = (
        script_path.read_text(encoding="utf-8").strip()
        if script_path.exists()
        else "¿Qué pasaría si tuvieras que sobrevivir siete días en el lugar más extremo del planeta?"
    )

    meta_path = OUTPUT_DIR / "scenes_meta.json"
    scenes_meta: List[Dict[str, Any]] = []
    if meta_path.exists():
        try:
            scenes_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            scenes_meta = []

    theme = detect_theme_from_text(script_text)
    num_chapters = max(5, len(scenes_meta))
    scene_files = get_theme_scene_files(theme, num_scenes=num_chapters)

    accent_map = {
        "ocean": (0, 155, 215),
        "blackout": (215, 35, 35),
        "prehistory": (215, 85, 25),
        "island": (25, 145, 85),
        "jungle": (25, 145, 75),
        "space": (135, 45, 215),
        "zombie": (215, 35, 35),
    }
    accent_col = accent_map.get(theme, (215, 35, 35))

    scene_badges: List[tuple[str, str, tuple[int, int, int]]] = []
    timeline_labels: List[str] = []

    for idx in range(num_chapters):
        sm = scenes_meta[idx] if idx < len(scenes_meta) else {}
        title_raw = sm.get("title", f"CAPÍTULO {idx + 1}").upper()
        sub_raw = sm.get("subtitle", "DATO CLAVE").upper()
        scene_badges.append((title_raw, sub_raw, accent_col))
        timeline_labels.append(title_raw[:13])

    return build_illustrated_youtube_video(
        story_id=f"long_{theme}",
        script_text=script_text,
        scene_files=scene_files,
        scene_badges=scene_badges,
        timeline_labels=timeline_labels,
        output_filename=output_video_path.name,
        ambience_mode=theme,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 2: Subtítulos dinámicos y animación visual.")
    parser.add_argument(
        "--video",
        type=Path,
        default=OUTPUT_DIR / "video_base.mp4",
        help="Ruta del video base.",
    )
    args = parser.parse_args()
    add_dynamic_subtitles(args.video)
