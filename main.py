"""
Orquestador Principal Multi-Formato y Multi-Red para Creadores de Facebook y YouTube Shorts:
  - Formato Video (80%): Motor Cinético Fluido (Estilo @finanz_ia, @nagumonetiza, @mixidev_esp):
      * Movimiento continuo Ken Burns (zoom 1.0 -> 1.12 sin saltos).
      * Subtítulos cinéticos "Pop-Spring" centrados en amarillo viral #FFE600 con rebote elástico.
      * Ilustraciones HD dinámicas del personaje con poses y objetos en sincronía con el guion.
      * Locución ElevenLabs / Neural con timestamps exactos por palabra.
      * Música de fondo ambiental (BGM piano/chill) a 12% con audio ducking.
  - Formato Foto (20%): Carrusel Editorial HD (Estilo Claude / AI KID):
      * 5 postales HD con tipografía editorial, terminal y llamadas a comentar.
  - Publicación simultánea independiente en Facebook Reels y YouTube Shorts.
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import ELEVENLABS_API_KEY, OUTPUT_DIR
from editorial_animator import render_editorial_package
from editorial_topics import get_next_editorial_topic
from fluid_animator import render_fluid_video
from script_bank_manager import get_next_pending_script, mark_script_as_published
from uploader import upload_feed_post_to_facebook, upload_video_to_facebook
from viral_topics import get_viral_story_by_id_or_random
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

    # Alterna automáticamente entre Video (Reels), Foto (Postal Editorial HD) y Texto (Debate)
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
    chosen_format = _choose_next_format(post_format.lower().strip())

    print("=" * 65)
    print(f" INICIANDO PIPELINE (FORMATO: {chosen_format.upper()}) | ESTILO: Fluido Viral @finanz_ia")
    print("=" * 65)

    if chosen_format == "video":
        # Priorizar el Banco Masivo de 50 Guiones del usuario
        bank_script = get_next_pending_script()
        if bank_script and (not topic or topic.strip().lower() == "auto"):
            topic_data = bank_script
            print(f"[Banco Guiones] Seleccionado guion pendiente: {topic_data['id']} - {topic_data['title']}")
        else:
            # Usar catálogo de respaldo si no hay banco o se solicitó un tema específico
            topic_data = get_viral_story_by_id_or_random(topic if topic != "auto" else "")
    else:
        # Usar catálogo editorial para carrusel de diapositivas
        topic_data = get_next_editorial_topic()

    if topic and topic.strip().lower() != "auto":
        topic_data["topic"] = topic.strip()

    chosen_topic = topic_data.get("topic", "Misterios y Curiosidades")
    chosen_caption = caption if caption else topic_data.get("caption", "")
    script_text = topic_data.get("script") or topic_data.get("narration_script", "")

    print(f"\n[Tema seleccionado]: {chosen_topic}")
    print(f"[Formato elegido]:   {chosen_format}")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO VIDEO: Motor Cinético Fluido -> Facebook Reels + YouTube Shorts
    # ──────────────────────────────────────────────────────────────────────
    if chosen_format == "video":
        print("\n>>> FASE 1: Renderizando Video Cinético Fluido (24 FPS + BGM + Subtítulos Pop)...")
        final_video_path = OUTPUT_DIR / "video_final.mp4"
        render_fluid_video(
            topic_data=topic_data,
            output_mp4=final_video_path,
            preferred_tts="elevenlabs" if ELEVENLABS_API_KEY else "edge_tts",
        )

        print(f"\n[Video listo]: {final_video_path} (Tamaño: {final_video_path.stat().st_size:,} bytes)")

        if not skip_upload:
            # ─── Publicación en FACEBOOK ────
            print("\n>>> FASE 2A: Publicando Reel en FACEBOOK...")
            fb_ok = False
            try:
                upload_video_to_facebook(video_path=final_video_path, caption=chosen_caption, headless=headless)
                fb_ok = True
                print("      [Facebook] ✅ Reel publicado con éxito.")
            except Exception as e:
                print(f"      [Facebook] ❌ Error: {e}")

            # ─── Publicación en YOUTUBE SHORTS ───
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

            print("\n" + "─" * 65)
            print(f"  Facebook Reels:   {'✅ PUBLICADO' if fb_ok else '❌ FALLIDO'}")
            print(f"  YouTube Shorts:   {'✅ ' + yt_url if yt_url else '❌ FALLIDO'}")
            print("─" * 65)

            # Si el guion proviene del banco masivo, marcar como PUBLICADO para no repetirlo
            if topic_data.get("id", "").startswith("VID-") and (fb_ok or yt_url):
                mark_script_as_published(topic_data["id"], video_url=yt_url or "facebook_published")
                print(f"[Banco Guiones] Guion {topic_data['id']} marcado como PUBLICADO con éxito.")

    # ──────────────────────────────────────────────────────────────────────
    # FORMATO FOTO: Carrusel Editorial HD -> Facebook Post
    # ──────────────────────────────────────────────────────────────────────
    elif chosen_format == "photo":
        print("\n>>> FASE 1: Renderizando Carrusel Editorial HD (5 Diapositivas)...")
        slide_paths, _, _ = render_editorial_package(topic_data)

        # Publicar la postal principal de impacto
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
    parser = argparse.ArgumentParser(description="Orquestador Bruno Schiller - Contenido Fluido Viral")
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
