"""
Orquestador Principal Multi-Formato y Multi-Red para Creadores de Facebook y YouTube Shorts:
  - Descubre automáticamente la tendencia más interesante del día.
  - Alterna entre 3 formatos orgánicos (video, photo, text).
  - NUEVO: Genera clips cinemáticos con Google Veo (con fallback a motor 2D).
  - NUEVO: Publica simultáneamente en Facebook Reels y YouTube Shorts
    (si una red falla, la otra se completa independientemente).
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import OUTPUT_DIR
from generator import (
    discover_trending_topic,
    generate_engaging_video_caption,
    generate_story_post,
    run_generation_pipeline,
    _get_episode_for_topic,
)
from subtitles import add_dynamic_subtitles
from uploader import upload_feed_post_to_facebook, upload_video_to_facebook
from youtube_uploader import upload_to_youtube_shorts


def _choose_next_format(requested_format: str) -> str:
    if requested_format in ("video", "photo", "text"):
        return requested_format

    fmt_history_path = OUTPUT_DIR / "published_formats.json"
    history = []
    if fmt_history_path.exists():
        try:
            history = json.loads(fmt_history_path.read_text(encoding="utf-8"))
        except Exception:
            history = []

    # 80% videos largos animados, 20% postales / texto
    cycle = ["video", "video", "video", "photo", "video"]
    next_fmt = cycle[len(history) % len(cycle)]
    history.append(next_fmt)
    fmt_history_path.write_text(json.dumps(history[-40:], ensure_ascii=False, indent=2), encoding="utf-8")
    return next_fmt


def _try_veo_pipeline(topic: str, theme: str, scene_titles: list, script_text: str) -> Path | None:
    """
    Intenta generar el video con Google Veo y concatenar los clips.
    Retorna la ruta del video final si tuvo éxito, None si se debe usar el fallback 2D.
    """
    try:
        from veo_generator import generate_veo_clips
    except ImportError:
        print("[main] veo_generator no disponible — usando motor 2D.")
        return None

    clips = generate_veo_clips(
        script_text=script_text,
        theme=theme,
        scene_titles=scene_titles,
        output_dir=OUTPUT_DIR,
    )
    if not clips:
        return None

    # Concatenar clips de Veo en un solo video final con MoviePy
    try:
        print(f"[main] Concatenando {len(clips)} clips de Veo...")
        try:
            from moviepy import VideoFileClip, concatenate_videoclips
        except ImportError:
            from moviepy.editor import VideoFileClip, concatenate_videoclips

        loaded = [VideoFileClip(str(c)) for c in clips]
        final = concatenate_videoclips(loaded, method="compose")
        out_path = OUTPUT_DIR / "video_final_veo.mp4"
        final.write_videofile(
            str(out_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None,
        )
        for c in loaded:
            c.close()
        final.close()
        print(f"[main] ✅ Video Veo concatenado: {out_path.name}")
        return out_path
    except Exception as e:
        print(f"[main] Error al concatenar clips Veo: {e} — usando motor 2D.")
        return None


def run_full_pipeline(
    topic: str = "auto",
    caption: str = "",
    post_format: str = "auto",
    skip_upload: bool = False,
    headless: bool = False,
    use_veo: bool = True,
) -> None:
    chosen_format = _choose_next_format(post_format.lower().strip())

    print("=" * 65)
    print(f" INICIANDO PIPELINE (FORMATO: {chosen_format.upper()}) | CANAL: Facebook + YouTube Shorts")
    print("=" * 65)

    if not topic or topic.strip().lower() == "auto":
        topic, auto_caption = discover_trending_topic()
        if not caption:
            caption = auto_caption
    elif not caption:
        caption = f"{topic} | Síguenos para más contenido diario #tendencias #curiosidades #viral"

    print(f"\n[Tema seleccionado]: {topic}")
    print(f"[Formato elegido]:   {chosen_format}")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO VIDEO: Renderizado + publicación dual Facebook + YouTube
    # ──────────────────────────────────────────────────────────────────────
    if chosen_format == "video":
        print("\n>>> FASE 1: Generación de Guion y Escenas Ilustradas")
        _, _ = run_generation_pipeline(topic)

        script_path = OUTPUT_DIR / "guion.txt"
        script_text = script_path.read_text(encoding="utf-8").strip() if script_path.exists() else topic

        caption = generate_engaging_video_caption(topic, script_text)
        print(f"      [Descripción del Reel]: {caption}")

        # Obtener metadatos del episodio (tema, títulos de escenas)
        ep = _get_episode_for_topic(topic)
        theme = ep.get("theme", "zombie")
        scene_titles = [s.get("title", f"Escena {i+1}") for i, s in enumerate(ep.get("scenes", []))]

        # ─── Intentar Google Veo primero; fallback automático al motor 2D ───
        final_video_path: Path | None = None

        if use_veo:
            print("\n>>> FASE 2A: Intentando generación cinemática con Google Veo...")
            final_video_path = _try_veo_pipeline(topic, theme, scene_titles, script_text)

        if final_video_path is None:
            print("\n>>> FASE 2B: Motor de Animación 2D (24 FPS, estilo Don Zombi)...")
            final_video_path = add_dynamic_subtitles()

        print(f"\n[Video listo]: {final_video_path}")

        if not skip_upload:
            # ─── Publicación en FACEBOOK (error independiente de YouTube) ────
            print("\n>>> FASE 3A: Publicando Reel en FACEBOOK...")
            fb_ok = False
            try:
                upload_video_to_facebook(video_path=final_video_path, caption=caption, headless=headless)
                fb_ok = True
                print("      [Facebook] ✅ Reel publicado con éxito.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

            # ─── Publicación en YOUTUBE SHORTS (independiente de Facebook) ───
            print("\n>>> FASE 3B: Subiendo a YOUTUBE SHORTS...")
            yt_url = None
            try:
                yt_url = upload_to_youtube_shorts(
                    video_path=final_video_path,
                    topic=topic,
                    script_text=script_text,
                    theme=theme,
                    privacy="public",
                )
                if yt_url:
                    print(f"      [YouTube] ✅ Short publicado: {yt_url}")
            except Exception as e:
                print(f"      [YouTube] ❌ Error: {e}")

            # ─── Resumen de resultados ────────────────────────────────────────
            print("\n" + "─" * 65)
            print(f"  Facebook Reels:   {'✅ PUBLICADO' if fb_ok else '❌ FALLIDO'}")
            print(f"  YouTube Shorts:   {'✅ ' + yt_url if yt_url else '❌ FALLIDO (faltan YT_* secrets)'}")
            print("─" * 65)

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO PHOTO
    # ──────────────────────────────────────────────────────────────────────
    elif chosen_format == "photo":
        print("\n>>> FASE 1: Generación de Historia Narrativa + Postal Fotográfica HD (1080x1350)")
        story_text, img_path = generate_story_post(topic, with_image=True)

        if not skip_upload:
            print("\n>>> FASE 2: Publicando Foto con Historia en FACEBOOK")
            try:
                upload_feed_post_to_facebook(story_text=story_text, image_path=img_path, headless=headless)
                print("      [Facebook] ✅ Publicado.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO TEXT
    # ──────────────────────────────────────────────────────────────────────
    elif chosen_format == "text":
        print("\n>>> FASE 1: Generación de Historia / Debate Viral en Texto")
        story_text, _ = generate_story_post(topic, with_image=False)

        if not skip_upload:
            print("\n>>> FASE 2: Publicando Historia de Texto en FACEBOOK")
            try:
                upload_feed_post_to_facebook(story_text=story_text, image_path=None, headless=headless)
                print("      [Facebook] ✅ Publicado.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

    print("\n" + "=" * 65)
    print(" ¡PROCESO COMPLETADO!")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline multi-formato y multi-red (Facebook + YouTube Shorts)."
    )
    parser.add_argument("--topic", type=str, default="auto", help="Tema o 'auto'.")
    parser.add_argument("--caption", type=str, default="", help="Descripción opcional.")
    parser.add_argument(
        "--format",
        type=str,
        default="auto",
        choices=["auto", "video", "photo", "text"],
        help="Formato de publicación.",
    )
    parser.add_argument("--skip-upload", action="store_true", help="Solo genera, no sube.")
    parser.add_argument("--headless", action="store_true", help="Ejecuta el navegador oculto.")
    parser.add_argument(
        "--no-veo",
        action="store_true",
        help="Desactiva Google Veo y usa directamente el motor 2D.",
    )
    args = parser.parse_args()

    run_full_pipeline(
        topic=args.topic,
        caption=args.caption,
        post_format=args.format,
        skip_upload=args.skip_upload,
        headless=args.headless,
        use_veo=not args.no_veo,
    )
