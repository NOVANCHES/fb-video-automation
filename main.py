"""
Orquestador Principal Multi-Formato para Creadores de Facebook:
  - Descubre automáticamente la tendencia más interesante del día (Google Trends / News + Gemini)
  - Alterna inteligentemente entre 3 formatos orgánicos:
      1. 'video': Reel animado con fotografías HD, tarjetas de ejemplos y subtítulos karaoke
      2. 'photo': Fotografía/Infografía HD 4:5 acompañada de una historia larga en el muro
      3. 'text' : Historia narrativa o pregunta de debate sobre la tendencia del día en el muro
"""

import argparse
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import OUTPUT_DIR
from generator import (
    discover_trending_topic,
    generate_engaging_video_caption,
    generate_story_post,
    run_generation_pipeline,
)
from subtitles import add_dynamic_subtitles
from uploader import upload_feed_post_to_facebook, upload_video_to_facebook


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

    # Prioridad principal a VIDEOS LARGOS ANIMADOS (80% videos, 20% postales ilustradas del tema)
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
) -> None:
    chosen_format = _choose_next_format(post_format.lower().strip())

    print("=" * 65)
    print(f" INICIANDO PIPELINE DE CREADOR EN TENDENCIA (FORMATO: {chosen_format.upper()})")
    print("=" * 65)

    if not topic or topic.strip().lower() == "auto":
        topic, auto_caption = discover_trending_topic()
        if not caption:
            caption = auto_caption
    elif not caption:
        caption = f"{topic} | Síguenos para más contenido diario #tendencias #curiosidades #viral"

    print(f"\n[Tema seleccionado]: {topic}")
    print(f"[Formato elegido]:   {chosen_format}")

    if chosen_format == "video":
        print("\n>>> FASE 1: Generación de Guion, Escenas Ilustradas y Locución")
        base_video_path, _ = run_generation_pipeline(topic)

        script_path = OUTPUT_DIR / "guion.txt"
        script_text = script_path.read_text(encoding="utf-8").strip() if script_path.exists() else topic
        print("\n>>> Redactando descripción interesante + pregunta de debate sobre el video...")
        caption = generate_engaging_video_caption(topic, script_text)
        print(f"      [Descripción del Reel]: {caption}")

        print("\n>>> FASE 2: Renderizado Animado a 24 FPS (Estilo Don Zombi / Curiosamente Graficado)")
        final_video_path = add_dynamic_subtitles(video_path=base_video_path)

        if not skip_upload:
            print("\n>>> FASE 3: Subida Automática de Reel a Facebook")
            upload_video_to_facebook(video_path=final_video_path, caption=caption, headless=headless)

    elif chosen_format == "photo":
        print("\n>>> FASE 1: Generación de Historia Narrativa + Postal Fotográfica HD (1080x1350)")
        story_text, img_path = generate_story_post(topic, with_image=True)

        if not skip_upload:
            print("\n>>> FASE 2: Publicando Foto con Historia en el Muro de Facebook")
            upload_feed_post_to_facebook(story_text=story_text, image_path=img_path, headless=headless)

    elif chosen_format == "text":
        print("\n>>> FASE 1: Generación de Historia / Debate Viral en Texto")
        story_text, _ = generate_story_post(topic, with_image=False)

        if not skip_upload:
            print("\n>>> FASE 2: Publicando Historia de Texto en el Muro de Facebook")
            upload_feed_post_to_facebook(story_text=story_text, image_path=None, headless=headless)

    print("\n" + "=" * 65)
    print(" ¡PROCESO COMPLETADO CON ÉXITO!")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline multi-formato de contenido en tendencia para Facebook.")
    parser.add_argument(
        "--topic",
        type=str,
        default="auto",
        help="Tema o 'auto' para detectar automáticamente la tendencia del día.",
    )
    parser.add_argument(
        "--caption",
        type=str,
        default="",
        help="Descripción opcional.",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="auto",
        choices=["auto", "video", "photo", "text"],
        help="Formato de publicación: 'auto' (alterna entre video, foto con historia y texto), 'video', 'photo' o 'text'.",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Genera el contenido sin subirlo a Facebook.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecuta el navegador oculto.",
    )
    args = parser.parse_args()

    run_full_pipeline(
        topic=args.topic,
        caption=args.caption,
        post_format=args.format,
        skip_upload=args.skip_upload,
        headless=args.headless,
    )
