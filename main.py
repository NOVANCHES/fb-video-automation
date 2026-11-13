"""
Orquestador Principal Multi-Formato y Multi-Red para Creadores de Videojuegos:
  - Formato Video: Motor Cinético Fluido con 3 escenas independientes,
    semillas aleatorias únicas, validación criptográfica SHA-256 y nombres con timestamp.
  - Reglas técnicas estrictas:
      1. Sin personajes recurrentes: visuales 100% del videojuego actual.
      2. Limpieza física previa de archivos anteriores (.png, .jpg, .webp, .mp4).
      3. Prohibido usar fallbacks; 3 llamadas independientes con semillas distintas.
      4. Validación estricta por hash SHA-256 (entre escenas y contra historial).
      5. Subida exclusiva en Selenium del .mp4 recién creado en los últimos 2 minutos.
"""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import ELEVENLABS_API_KEY, OUTPUT_DIR
from editorial_animator import render_editorial_package
from editorial_topics import get_next_editorial_topic
from fluid_animator import render_fluid_video
from gaming_topics import get_next_gaming_story
from script_bank_manager import get_next_pending_script, mark_script_as_published
from uploader import upload_feed_post_to_facebook, upload_video_to_facebook
from viral_topics import get_viral_story_by_id_or_random
from visual_engine import generate_three_unique_scene_images
from youtube_uploader import upload_to_youtube_shorts


def cleanup_previous_run_artifacts() -> None:
    """
    REGLA 2 OBLIGATORIA:
    Borra físicamente todas las imágenes (.png, .jpg, .jpeg, .webp) y videos (.mp4)
    de ejecuciones anteriores en la carpeta de salida (output/) y temporales
    para que sea imposible reutilizar archivos viejos.
    """
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".mp4"}
    deleted_count = 0
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in extensions:
                # Proteger archivos de registro y control histórico
                if f.name == "image_hashes_history.json":
                    continue
                try:
                    f.unlink()
                    deleted_count += 1
                except Exception as exc:
                    print(f"      [Cleanup] Aviso al borrar {f.name}: {exc}")
    print(f"[Cleanup] Limpieza previa completada: {deleted_count} archivos de ejecuciones anteriores eliminados físicamente.")


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

    cycle = ["video", "video", "photo", "video", "text"]
    next_fmt = cycle[len(history) % len(cycle)]
    history.append(next_fmt)
    fmt_history_path.write_text(json.dumps(history[-40:], ensure_ascii=False, indent=2), encoding="utf-8")
    return next_fmt


def run_full_pipeline(
    topic: str = "auto",
    caption: str = "",
    post_format: str = "auto",
    skip_upload: bool = False,
    headless: bool = False,
    use_veo: bool = False,
) -> None:
    # REGLA 2 OBLIGATORIA: Limpieza física previa antes de iniciar cualquier generación
    cleanup_previous_run_artifacts()

    chosen_format = _choose_next_format(post_format.lower().strip())

    print("=" * 65)
    print(f" INICIANDO PIPELINE (FORMATO: {chosen_format.upper()}) | TEMÁTICA: Videojuegos")
    print("=" * 65)

    if chosen_format == "video":
        if not topic or topic.strip().lower() == "auto" or "game" in topic.lower() or "videojuego" in topic.lower():
            topic_data = get_next_gaming_story(topic if topic != "auto" else "")
            print(f"[Gaming] Seleccionado guion de Videojuegos: {topic_data['id']} - {topic_data['title']}")
        else:
            bank_script = get_next_pending_script()
            if bank_script:
                topic_data = bank_script
            else:
                topic_data = get_viral_story_by_id_or_random(topic)
    else:
        topic_data = get_next_editorial_topic()

    if topic and topic.strip().lower() != "auto":
        topic_data["topic"] = topic.strip()

    chosen_topic = topic_data.get("topic", "Curiosidades de Videojuegos")
    chosen_caption = caption if caption else topic_data.get("caption", "")
    script_text = topic_data.get("script") or topic_data.get("narration_script", "")
    script_id = topic_data.get("id") or topic_data.get("theme_id") or "VID_001"
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n[Tema seleccionado]: {chosen_topic}")
    print(f"[Formato elegido]:   {chosen_format}")
    print(f"[ID del Guion]:      {script_id}")
    print(f"[Marca de Tiempo]:   {timestamp_str}")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO VIDEO: Motor Cinético Fluido -> Facebook Reels + YouTube Shorts
    # ──────────────────────────────────────────────────────────────────────
    if chosen_format == "video":
        # REGLAS 1, 3, 4 Y 5: Generar 3 imágenes independientes con semillas aleatorias únicas
        print("\n>>> FASE 1: Generando 3 Escenas Independientes con Semillas Únicas y Validación SHA-256...")
        scene_image_paths = generate_three_unique_scene_images(
            story_data=topic_data,
            timestamp_str=timestamp_str,
        )

        # REGLA 5: Nombre único con ID y timestamp para el archivo MP4
        final_video_filename = f"{script_id}_{timestamp_str}.mp4"
        final_video_path = OUTPUT_DIR / final_video_filename

        print(f"\n>>> FASE 2: Renderizando Video Cinético Fluido ({final_video_filename})...")
        render_fluid_video(
            topic_data=topic_data,
            output_mp4=final_video_path,
            scene_image_paths=scene_image_paths,
            preferred_tts="elevenlabs" if ELEVENLABS_API_KEY else "edge_tts",
        )

        print(f"\n[Video listo y verificado]: {final_video_path} (Tamaño: {final_video_path.stat().st_size:,} bytes)")

        if not skip_upload:
            # ─── Publicación en FACEBOOK ────
            print("\n>>> FASE 3A: Publicando Reel en FACEBOOK...")
            fb_ok = False
            try:
                # REGLA 5: uploader valida antigüedad menor a 120 segundos
                upload_video_to_facebook(
                    video_path=final_video_path,
                    caption=chosen_caption,
                    headless=headless,
                )
                fb_ok = True
                print("      [Facebook] ✅ Reel publicado con éxito.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

            # ─── Publicación en YOUTUBE SHORTS ───
            print("\n>>> FASE 3B: Subiendo a YOUTUBE SHORTS...")
            yt_url = None
            try:
                yt_url = upload_to_youtube_shorts(
                    video_path=final_video_path,
                    topic=chosen_topic,
                    script_text=script_text,
                    theme="tech",
                    privacy="public",
                )
                if yt_url:
                    print(f"      [YouTube] ✅ Short publicado: {yt_url}")
            except Exception as e:
                print(f"      [YouTube] ❌ Error: {e}")

            print("\n" + "─" * 65)
            print(f"  Facebook Reels:   {'✅ PUBLICADO' if fb_ok else '❌ FALLIDO'}")
            print(f"  YouTube Shorts:   {'✅ ' + yt_url if yt_url else '❌ FALLIDO'}")
            print("─" * 65)

            if topic_data.get("id", "").startswith("VID-") and (fb_ok or yt_url):
                mark_script_as_published(topic_data["id"], video_url=yt_url or "facebook_published")
                print(f"[Banco Guiones] Guion {topic_data['id']} marcado como PUBLICADO con éxito.")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO FOTO: Carrusel Editorial HD -> Facebook Post
    # ──────────────────────────────────────────────────────────────────────
    elif chosen_format == "photo":
        print("\n>>> FASE 1: Renderizando Carrusel Editorial HD (5 Diapositivas)...")
        slide_paths, _, _ = render_editorial_package(topic_data)
        main_slide = slide_paths[0]
        print(f"\n[Postal lista]: {main_slide}")

        if not skip_upload:
            print("\n>>> FASE 2: Publicando Postal Editorial en FACEBOOK...")
            fb_ok = False
            try:
                upload_feed_post_to_facebook(story_text=chosen_caption, image_path=main_slide, headless=headless)
                fb_ok = True
                print("      [Facebook] ✅ Postal publicada con éxito.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO TEXT: Historia / Pregunta de Debate en Texto -> Facebook Post
    # ──────────────────────────────────────────────────────────────────────
    elif chosen_format == "text":
        print("\n>>> FASE 1: Preparando Historia de Debate en Texto...")
        story_content = chosen_caption or script_text
        print(f"\n[Texto listo]:\n{story_content[:150]}...")

        if not skip_upload:
            print("\n>>> FASE 2: Publicando Historia de Debate en FACEBOOK...")
            fb_ok = False
            try:
                upload_feed_post_to_facebook(story_text=story_content, image_path=None, headless=headless)
                fb_ok = True
                print("      [Facebook] ✅ Historia de debate publicada con éxito.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

    print("\n" + "=" * 65)
    print(" ¡PROCESO COMPLETADO!")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestador de Videojuegos - Contenido Fluido Viral")
    parser.add_argument("--topic", type=str, default="auto", help="Tema específico o 'auto'")
    parser.add_argument("--caption", type=str, default="", help="Texto de la publicación")
    parser.add_argument("--format", type=str, default="auto", choices=["auto", "video", "photo", "text"], help="Formato")
    parser.add_argument("--skip-upload", action="store_true", help="Solo generar archivos sin subir")
    parser.add_argument("--headless", action="store_true", help="Ejecutar navegador en modo invisible")
    parser.add_argument("--use-veo", action="store_true", help="Usar Google Veo si está disponible")

    args = parser.parse_args()

    run_full_pipeline(
        topic=args.topic,
        caption=args.caption,
        post_format=args.format,
        skip_upload=args.skip_upload,
        headless=args.headless,
        use_veo=args.use_veo,
    )
