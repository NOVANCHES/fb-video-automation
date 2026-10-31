"""
Módulo 1: Generación de Guion (Gemini API + FreeLLM g4f),
Búsqueda de Fotografías HD Reales (Wikimedia Commons / NASA API) con Tarjetas de Ejemplos,
Voz (edge-tts) y Ensamblaje Rápido.
"""

import argparse
import asyncio
import json
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List

import edge_tts
import requests
from google import genai
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    IMAGES_DIR,
    OUTPUT_DIR,
    TTS_VOICE,
    VIDEO_FPS,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)

try:
    from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
    MOVIEPY_V2 = False


def discover_trending_topic() -> tuple[str, str]:
    """
    Consulta en tiempo real Google Trends México y Google News en español,
    filtra temas ya publicados en `output/published_topics.json`, y usa Gemini
    para elegir el tema en tendencia más atractivo del día junto con su descripción.
    """
    print("[Tendencias] Buscando qué está en tendencia hoy en tiempo real...")
    headlines: List[str] = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    rss_urls = [
        "https://trends.google.com/trending/rss?geo=MX",
        "https://news.google.com/rss?hl=es-419&gl=MX&ceid=MX:es-419",
    ]
    for url in rss_urls:
        try:
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                for item in root.findall(".//item/title")[:15]:
                    if item.text:
                        clean_t = item.text.split(" - ")[0].strip()
                        if clean_t and clean_t not in headlines:
                            headlines.append(clean_t)
        except Exception:
            pass

    history_path = OUTPUT_DIR / "published_topics.json"
    published: List[str] = []
    if history_path.exists():
        try:
            published = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception:
            published = []

    today_str = datetime.now().strftime("%Y-%m-%d")
    trends_block = "\n".join(f"- {h}" for h in headlines[:20]) if headlines else "Ciencia, tecnología, descubrimientos espaciales y fenómenos virales del momento."
    avoid_block = ", ".join(published[-15:]) if published else "ninguno"

    if GEMINI_API_KEY and GEMINI_API_KEY != "tu_api_key_de_gemini_aqui":
        try:
            client = genai.Client(api_key=GEMINI_API_KEY, http_options={"timeout": 12000})
            prompt = (
                f"Fecha actual: {today_str}.\n"
                f"Titulares y búsquedas en tendencia hoy:\n{trends_block}\n\n"
                f"Temas ya usados recientemente (NO repetir): {avoid_block}\n\n"
                "Elige o adapta 1 tema sumamente interesante, curioso o viral del momento que haga que todos se detengan a ver el Reel (puede estar conectado a una tendencia actual de tecnología, ciencia, historia, naturaleza, espacio o cultura general con 3 datos/ejemplos asombrosos).\n"
                "Devuelve ÚNICAMENTE un JSON con estas 2 claves exactas:\n"
                '- "topic": título del tema para generar el guion con 3 ejemplos\n'
                '- "caption": texto llamativo para la publicación de Facebook en ERPA VARDE incluyendo 4 hashtags en tendencia (#reels #viral etc.)\n'
                "Sin bloques markdown, solo JSON puro."
            )
            interaction = client.interactions.create(model=GEMINI_MODEL, input=prompt)
            raw = (interaction.output_text or "").strip()
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                topic = data.get("topic", "").strip()
                caption = data.get("caption", "").strip()
                if topic:
                    published.append(topic)
                    history_path.write_text(json.dumps(published[-50:], ensure_ascii=False, indent=2), encoding="utf-8")
                    print(f"      [Tendencia elegida]: '{topic}'")
                    return topic, caption or f"{topic} | Síguenos en ERPA VARDE #reels #tendencia #curiosidades #viral"
        except Exception as exc:
            print(f"      Aviso al analizar tendencias con Gemini: {exc}")

    fallback_topic = headlines[0] if headlines else "3 descubrimientos recientes que están sorprendiendo al mundo hoy"
    fallback_caption = f"¡Todos están hablando de esto hoy! {fallback_topic} | Síguenos en ERPA VARDE #reels #tendencias #viral"
    return fallback_topic, fallback_caption


def generate_script(topic: str) -> str:
    """
    Genera el guion usando Gemini API o FreeLLM (g4f) como respaldo gratuito.
    """
    system_instruction = (
        "Eres un guionista experto en videos virales cortos para Facebook Reels. "
        "Escribe únicamente el texto hablado del narrador en español con ejemplos claros. "
        "Reglas estrictas:\n"
        "- Duración de lectura: 25 a 35 segundos (entre 65 y 85 palabras).\n"
        "- Comienza con un gancho muy potente en la primera oración y da 3 ejemplos claros.\n"
        "- NO incluyas etiquetas como '[Música]', 'Narrador:', asteriscos, emojis ni títulos.\n"
        "- Devuelve solo el párrafo limpio que leerá la voz artificial."
    )

    print(f"[1/4] Generando guion sobre: '{topic}'...")

    if GEMINI_API_KEY and GEMINI_API_KEY != "tu_api_key_de_gemini_aqui":
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            interaction = client.interactions.create(
                model=GEMINI_MODEL,
                system_instruction=system_instruction,
                input=f"Crea un guion corto con 3 ejemplos impactantes para Facebook sobre: {topic}",
            )
            script_text = (interaction.output_text or "").strip()
            if script_text:
                script_path = OUTPUT_DIR / "guion.txt"
                script_path.write_text(script_text, encoding="utf-8")
                print(f"      Guion generado con Gemini ({GEMINI_MODEL}) en: {script_path}")
                return script_text
        except Exception as exc:
            print(f"      Aviso Gemini ({exc}), cambiando a FreeLLM (g4f)...")

    try:
        from g4f.client import Client as G4FClient  # type: ignore

        g4f_client = G4FClient()
        response = g4f_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Crea un guion corto con 3 ejemplos sobre: {topic}"},
            ],
        )
        script_text = response.choices[0].message.content.strip()
        if script_text:
            script_path = OUTPUT_DIR / "guion.txt"
            script_path.write_text(script_text, encoding="utf-8")
            print(f"      Guion generado con FreeLLM (g4f) en: {script_path}")
            return script_text
    except Exception as exc:
        print(f"      Aviso FreeLLM: {exc}")

    script_path = OUTPUT_DIR / "guion.txt"
    if script_path.exists():
        return script_path.read_text(encoding="utf-8").strip()

    raise RuntimeError("No se pudo generar el guion.")


def _plan_visual_scenes(script_text: str, num_scenes: int = 4) -> List[Dict[str, str]]:
    """
    Usa Gemini para extraer 4 escenas con términos de búsqueda reales en inglés
    y etiquetas explicativas en español (Ejemplos visuales) para mostrar en pantalla.
    """
    default_scenes = [
        {
            "query": "Deep space galaxy cluster Hubble",
            "title": "MISTERIOS DEL COSMOS",
            "subtitle": "Lo que la ciencia aún no logra explicar",
        },
        {
            "query": "Norma Cluster Great Attractor galaxy",
            "title": "EJEMPLO 1: EL GRAN ATRACTOR",
            "subtitle": "Anomalía gravitacional que arrastra galaxias",
        },
        {
            "query": "Dark matter cosmic web simulation",
            "title": "EJEMPLO 2: MATERIA OSCURA (95%)",
            "subtitle": "Estructura invisible que domina el universo",
        },
        {
            "query": "Radio telescope deep space signal nebula",
            "title": "EJEMPLO 3: SEÑALES DE RADIO FRB",
            "subtitle": "Destellos repetitivos a millones de años luz",
        },
    ]

    if not GEMINI_API_KEY or GEMINI_API_KEY == "tu_api_key_de_gemini_aqui":
        return default_scenes[:num_scenes]

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"A partir de este guion:\n\"{script_text}\"\n\n"
            f"Devuelve ÚNICAMENTE un JSON array válido con {num_scenes} objetos. "
            "Cada objeto debe tener exactamente estas 3 claves:\n"
            '- "query": término de búsqueda fotográfico en inglés (2 a 4 palabras simples, ej. "Hubble galaxy nebula", "black hole accretion disk", "radio telescope stars")\n'
            '- "title": título corto en mayúsculas en español (ej. "EJEMPLO 1: EL GRAN ATRACTOR")\n'
            '- "subtitle": dato clave o explicación corta en español (máximo 7 palabras)\n'
            "No incluyas bloques markdown ```json, solo el JSON puro."
        )
        interaction = client.interactions.create(model=GEMINI_MODEL, input=prompt)
        raw = (interaction.output_text or "").strip()
        match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list) and len(parsed) >= num_scenes:
                return parsed[:num_scenes]
    except Exception:
        pass

    return default_scenes[:num_scenes]


def _fetch_real_hd_image(query: str, idx: int) -> Image.Image:
    """
    Descarga fotografías reales en alta definición desde Wikimedia Commons o NASA Image API
    en menos de 2 segundos, sin requerir clave de API.
    """
    headers = {"User-Agent": "FBVideoCreatorBot/2.0 (Educational Space Reels)"}

    # 1. Buscar en Wikimedia Commons (archivos fotográficos reales de todo tipo de temas)
    try:
        wiki_url = (
            "https://commons.wikimedia.org/w/api.php?action=query&generator=search"
            f"&gsrnamespace=6&gsrsearch={requests.utils.quote(query + ' jpg')}"
            "&gsrlimit=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
        )
        r = requests.get(wiki_url, headers=headers, timeout=5)
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            thumb = info.get("thumburl") or info.get("url")
            if thumb and any(ext in thumb.lower() for ext in (".jpg", ".jpeg", ".png")):
                img_resp = requests.get(thumb, headers=headers, timeout=6)
                if img_resp.status_code == 200 and len(img_resp.content) > 15_000:
                    return Image.open(BytesIO(img_resp.content)).convert("RGB")
    except Exception:
        pass

    # 2. Buscar en NASA Image Library API (excelente para ciencia, planetas, universo, tierra, tecnología)
    try:
        nasa_url = f"https://images-api.nasa.gov/search?q={requests.utils.quote(query)}&media_type=image"
        r = requests.get(nasa_url, headers=headers, timeout=5)
        items = r.json().get("collection", {}).get("items", [])
        if items:
            item = items[(idx - 1) % min(len(items), 8)]
            href = item.get("links", [{}])[0].get("href")
            if href:
                img_resp = requests.get(href, headers=headers, timeout=6)
                if img_resp.status_code == 200 and len(img_resp.content) > 10_000:
                    return Image.open(BytesIO(img_resp.content)).convert("RGB")
    except Exception:
        pass

    # 3. Respaldo garantizado de NASA/Hubble en caso de consulta muy específica
    fallback_queries = ["galaxy nebula hubble", "black hole space", "supernova stars", "deep field cosmos"]
    try:
        fq = fallback_queries[(idx - 1) % len(fallback_queries)]
        nasa_url = f"https://images-api.nasa.gov/search?q={requests.utils.quote(fq)}&media_type=image"
        r = requests.get(nasa_url, headers=headers, timeout=5)
        items = r.json().get("collection", {}).get("items", [])
        if items:
            href = items[idx % len(items)].get("links", [{}])[0].get("href")
            img_resp = requests.get(href, headers=headers, timeout=6)
            return Image.open(BytesIO(img_resp.content)).convert("RGB")
    except Exception:
        pass

    return Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (15, 25, 45))


def _download_and_prepare_scene(args: tuple[int, Dict[str, str]]) -> Dict[str, Any]:
    idx, scene_info = args
    raw_img = _fetch_real_hd_image(scene_info["query"], idx)
    # Adaptar a alta resolución 1200x2133 para permitir zoom/paneo animado sin perder nitidez
    zoom_w, zoom_h = int(VIDEO_WIDTH * 1.18), int(VIDEO_HEIGHT * 1.18)
    fitted = ImageOps.fit(raw_img, (zoom_w, zoom_h), method=Image.Resampling.LANCZOS)
    # Mejorar contraste y saturación para un look documental vibrante
    fitted = ImageEnhance.Color(fitted).enhance(1.22)
    fitted = ImageEnhance.Contrast(fitted).enhance(1.12)

    dest = IMAGES_DIR / f"ai_scene_{idx:02d}.jpg"
    fitted.save(dest, quality=94)
    return {
        "index": idx,
        "path": str(dest),
        "title": scene_info.get("title", f"EJEMPLO {idx}"),
        "subtitle": scene_info.get("subtitle", ""),
    }


def generate_scene_images(script_text: str, num_scenes: int = 4) -> List[Path]:
    """
    Planifica las 4 escenas animadas (Hook, Carpeta Neón y Tarjetas Numeradas) y guarda
    sus metadatos explicativos en `output/scenes_meta.json` para el motor de animación (`animator.py`).
    """
    print(f"[2/4] Planificando {num_scenes} escenas animadas estilo @iadeguardia...")
    scenes_plan = _plan_visual_scenes(script_text, num_scenes=num_scenes)
    scenes_meta = [
        {
            "index": idx,
            "title": scene_info.get("title", f"EJEMPLO {idx}"),
            "subtitle": scene_info.get("subtitle", ""),
        }
        for idx, scene_info in enumerate(scenes_plan, start=1)
    ]

    meta_path = OUTPUT_DIR / "scenes_meta.json"
    meta_path.write_text(json.dumps(scenes_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"      {len(scenes_meta)} escenas animadas estructuradas en: {meta_path}")
    return []


async def _synthesize_voice_and_timings_async(
    text: str,
    output_audio_path: Path,
    timings_path: Path,
    voice: str,
) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate="+5%")
    word_timings: List[Dict[str, Any]] = []

    with open(output_audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                start_sec = chunk["offset"] / 10_000_000.0
                dur_sec = chunk["duration"] / 10_000_000.0
                word_timings.append(
                    {
                        "type": chunk["type"],
                        "start": start_sec,
                        "end": start_sec + max(dur_sec, 0.15),
                        "text": chunk["text"],
                    }
                )

    timings_path.write_text(json.dumps(word_timings, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_voice(
    text: str,
    output_audio_path: Path = OUTPUT_DIR / "narration.mp3",
    timings_path: Path = OUTPUT_DIR / "timings.json",
) -> Path:
    print(f"[3/4] Generando locución con edge-tts (voz: {TTS_VOICE})...")
    asyncio.run(_synthesize_voice_and_timings_async(text, output_audio_path, timings_path, TTS_VOICE))
    print(f"      Audio generado en: {output_audio_path}")
    return output_audio_path


def assemble_video(
    audio_path: Path,
    image_paths: List[Path],
    output_video_path: Path = OUTPUT_DIR / "video_base.mp4",
) -> Path:
    print("[4/4] Preparando base de audio y escenas...")
    processed_dir = OUTPUT_DIR / "processed_frames"
    processed_images = sorted(processed_dir.glob("frame_*.jpg"))

    audio_clip = AudioFileClip(str(audio_path))
    total_duration = audio_clip.duration
    duration_per_image = total_duration / len(processed_images)

    clips = []
    for img_path in processed_images:
        if MOVIEPY_V2:
            clip = ImageClip(str(img_path)).with_duration(duration_per_image)
        else:
            clip = ImageClip(str(img_path)).set_duration(duration_per_image)
        clips.append(clip)

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
    print(f"      Video base exportado en: {output_video_path}")
    return output_video_path


def generate_story_post(topic: str, with_image: bool = True) -> tuple[str, Path | None]:
    """
    Genera una publicación narrativa (historia en tendencia / curiosidad profunda)
    lista para el muro de Facebook, acompañada opcionalmente de una infografía/fotografía HD 4:5 (1080x1350).
    """
    print(f"[Historia] Redactando historia viral para Facebook sobre: '{topic}'...")
    story_text = ""
    img_query = "Hubble galaxy cosmos"
    headline = topic[:36].upper()
    subheadline = "Una historia real que todos están comentando hoy"

    if GEMINI_API_KEY and GEMINI_API_KEY != "tu_api_key_de_gemini_aqui":
        try:
            client = genai.Client(api_key=GEMINI_API_KEY, http_options={"timeout": 12000})
            prompt = (
                f"Escribe una publicación fascinante para Facebook en español contando una historia real o explicando de forma atrapante el tema: '{topic}'.\n"
                "Estructura de la historia:\n"
                "- Primera línea: Un título o pregunta gancho muy potente.\n"
                "- Desarrollo: 2 a 3 párrafos cortos contando la historia, datos reales o ejemplos sorprendentes de forma clara y amena.\n"
                "- Cierre: Una pregunta abierta para que los seguidores opinen en los comentarios + 4 hashtags.\n"
                "- NO uses caracteres especiales raros, escribe en texto limpio.\n\n"
                "Devuelve ÚNICAMENTE un JSON válido con estas 4 claves:\n"
                '- "story": el texto completo de la publicación (con saltos de línea \\n)\n'
                '- "query": término de búsqueda fotográfico en inglés (2 a 4 palabras simples)\n'
                '- "headline": titular corto impactante en español (máximo 5 palabras en mayúsculas)\n'
                '- "subheadline": subtítulo explicativo en español (máximo 8 palabras)\n'
                "Sin bloques markdown, solo JSON puro."
            )
            interaction = client.interactions.create(model=GEMINI_MODEL, input=prompt)
            raw = (interaction.output_text or "").strip()
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                story_text = data.get("story", "").strip()
                img_query = data.get("query", img_query).strip()
                headline = data.get("headline", headline).strip()
                subheadline = data.get("subheadline", subheadline).strip()
        except Exception as exc:
            print(f"      Aviso al generar historia con Gemini: {exc}")

    if not story_text:
        story_text = (
            f"¿Alguna vez te has puesto a pensar en esto sobre {topic}?\n\n"
            "Cada día la ciencia y la tecnología nos revelan detalles que parecen sacados de una película, "
            "pero están ocurriendo ahora mismo frente a nuestros ojos.\n\n"
            "¿Qué opinas tú sobre este fenómeno? Te leo en los comentarios.\n\n"
            "#curiosidades #historia #tendencias #ciencia"
        )

    story_path = OUTPUT_DIR / "story_post.txt"
    story_path.write_text(story_text, encoding="utf-8")

    if not with_image:
        return story_text, None

    print(f"[Imagen] Creando postal fotográfica HD (1080x1350) para '{img_query}'...")
    raw_img = _fetch_real_hd_image(img_query, 1)
    card = ImageOps.fit(raw_img, (1080, 1350), method=Image.Resampling.LANCZOS)
    card = ImageEnhance.Color(card).enhance(1.2)
    draw = ImageDraw.Draw(card, "RGBA")

    bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    reg_path = r"C:\Windows\Fonts\segoeui.ttf"
    font_h = ImageFont.truetype(bold_path, 52) if Path(bold_path).exists() else ImageFont.load_default()
    font_s = ImageFont.truetype(reg_path if Path(reg_path).exists() else bold_path, 34)

    draw.rounded_rectangle(
        [45, 1020, 1035, 1295],
        radius=28,
        fill=(8, 14, 28, 225),
        outline=(0, 225, 255, 240),
        width=4,
    )
    draw.text(
        (540, 1110),
        headline[:34].upper(),
        font=font_h,
        fill=(255, 235, 0, 255),
        anchor="mm",
        stroke_width=3,
        stroke_fill=(0, 0, 0, 255),
    )
    draw.text(
        (540, 1205),
        subheadline[:52],
        font=font_s,
        fill=(235, 245, 255, 255),
        anchor="mm",
    )

    img_out = OUTPUT_DIR / "post_image.jpg"
    card.save(img_out, quality=95)
    print(f"      Imagen para publicación guardada en: {img_out}")
    return story_text, img_out


def run_generation_pipeline(topic: str) -> tuple[Path, Path]:
    script_text = generate_script(topic)
    generate_scene_images(script_text, num_scenes=4)
    audio_path = generate_voice(script_text)
    video_base_path = OUTPUT_DIR / "video_base.mp4"
    return video_base_path, audio_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 1: Generación de guion, fotografías HD, voz y video.")
    parser.add_argument(
        "--topic",
        type=str,
        default="3 misterios del espacio que los cientificos aun no pueden explicar",
        help="Tema sobre el cual se escribirá el guion.",
    )
    args = parser.parse_args()
    run_generation_pipeline(args.topic)
