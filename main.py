"""
Orquestador Principal Multi-Formato y Multi-Red para Creadores de Facebook y YouTube Shorts:
  - Generación de Contenido Viral Estilo Editorial / Claude / AI KID:
      * Lienzo crema minimalista (#F6F4ED) con tipografía serif y marcador resaltador.
      * Ventana macOS terminal con prompts interactivos.
      * Insignias de producción, pasos numerados y llamado viral a comentar ("COMENTÁ X").
  - Rotación infinita de temas frescos de IA, productividad y tecnología (cero repetición de imágenes).
  - Publicación simultánea independiente en Facebook Reels y YouTube Shorts.
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import OUTPUT_DIR
from editorial_animator import render_editorial_package
from editorial_topics import get_next_editorial_topic
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

    # 80% videos virales editoriales, 20% postales HD con historias
    cycle = ["video", "video", "video", "photo", "video"]
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
    chosen_format = _choose_next_format(post_format.lower().strip())

    print("=" * 65)
    print(f" INICIANDO PIPELINE (FORMATO: {chosen_format.upper()}) | ESTILO: Editorial Claude / AI KID")
    print("=" * 65)

    # Obtener el siguiente tema no repetido del catálogo dinámico
    topic_data = get_next_editorial_topic()
    if topic and topic.strip().lower() != "auto":
        topic_data["topic"] = topic.strip()

    chosen_topic = topic_data["topic"]
    chosen_caption = caption if caption else topic_data["caption"]
    script_text = topic_data["narration_script"]

    print(f"\n[Tema seleccionado]: {chosen_topic}")
    print(f"[Formato elegido]:   {chosen_format}")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO VIDEO: Motor Editorial Minimalista -> Facebook + YouTube Shorts
    # ──────────────────────────────────────────────────────────────────────
    if chosen_format == "video":
        print("\n>>> FASE 1: Renderizando Paquete Editorial (5 Diapositivas HD + Audio Neural)...")
        slide_paths, audio_path, final_video_path = render_editorial_package(topic_data)

        print(f"\n[Video listo]: {final_video_path} (Tamaño: {final_video_path.stat().st_size:,} bytes)")

        if not skip_upload:
            # ─── Publicación en FACEBOOK (error independiente de YouTube) ────
            print("\n>>> FASE 2A: Publicando Reel en FACEBOOK...")
            fb_ok = False
            try:
                upload_video_to_facebook(video_path=final_video_path, caption=chosen_caption, headless=headless)
                fb_ok = True
                print("      [Facebook] ✅ Reel publicado con éxito.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

            # ─── Publicación en YOUTUBE SHORTS (independiente de Facebook) ───
            print("\n>>> FASE 2B: Subiendo a YOUTUBE SHORTS...")
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

            # ─── Resumen de resultados ────────────────────────────────────────
            print("\n" + "─" * 65)
            print(f"  Facebook Reels:   {'✅ PUBLICADO' if fb_ok else '❌ FALLIDO'}")
            print(f"  YouTube Shorts:   {'✅ ' + yt_url if yt_url else '❌ FALLIDO (faltan YT_* secrets)'}")
            print("─" * 65)

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO PHOTO: Hero Card Editorial HD (1080x1920) en Feed de Facebook
    # ──────────────────────────────────────────────────────────────────────
    elif chosen_format == "photo":
        print("\n>>> FASE 1: Generación de Diapositiva Editorial HD...")
        slide_paths, _, _ = render_editorial_package(topic_data)
        hero_image = slide_paths[0]

        if not skip_upload:
            print("\n>>> FASE 2: Publicando en el feed de FACEBOOK")
            try:
                upload_feed_post_to_facebook(story_text=chosen_caption, image_path=hero_image, headless=headless)
                print("      [Facebook] ✅ Publicado con éxito.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO TEXT: Publicación de debate / tutorial paso a paso
    # ──────────────────────────────────────────────────────────────────────
    elif chosen_format == "text":
        print("\n>>> FASE 1: Publicando Tutorial / Debate de Texto en FACEBOOK")
        if not skip_upload:
            try:
                upload_feed_post_to_facebook(story_text=chosen_caption, image_path=None, headless=headless)
                print("      [Facebook] ✅ Publicado con éxito.")
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
        help="Desactiva Google Veo (mantenido por compatibilidad).",
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
