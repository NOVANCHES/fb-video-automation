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


def _call_gemini_fast(prompt: str, system_instruction: str = "", timeout_sec: float = 10.0) -> str:
    """
    Llama directamente al endpoint REST de Gemini con timeout estricto de 10s
    y CERO bucles de reintento ante errores 429/503 para que nunca se cuelgue en la nube.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "tu_api_key_de_gemini_aqui":
        return ""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        resp = requests.post(url, json=payload, timeout=timeout_sec)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return (parts[0].get("text") or "").strip()
    except Exception:
        pass
    return ""


CURATED_COMIC_TOPICS = [
    "¿Qué pasaría en las primeras 72 horas si se apagara todo el internet y la electricidad del mundo?",
    "3 lugares prohibidos de la Tierra donde nadie tiene permitido entrar jamás",
    "Cómo sobrevivirías si quedaras atrapado en una isla desierta sin herramientas durante 30 días",
    "El misterio de la Fosa de las Marianas: qué vive realmente a 11 kilómetros bajo el océano",
    "¿Cuánto tiempo sobrevivirías en cada era prehistórica si viajaras al pasado?",
    "Los 3 errores que el 95 por ciento de las personas cometería en el día 1 de una evacuación",
    "Por qué existen zonas del Amazonas donde ni los drones ni los satélites pueden ver el suelo",
    "Qué ocurriría con las ciudades del planeta si los humanos desaparecieran por 100 años",
]


def discover_trending_topic() -> tuple[str, str]:
    """
    Consulta en tiempo real Google Trends México y Google News en español,
    filtra temas ya publicados en `output/published_topics.json`, y usa Gemini
    (o el banco de historias estilo Don Zombi / Curiosamente Graficado) para elegir el tema.
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
                        if clean_t and len(clean_t) > 12 and clean_t not in headlines:
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
    trends_block = "\n".join(f"- {h}" for h in headlines[:15]) if headlines else "Supervivencia, misterios sin resolver y ciencia."
    avoid_block = ", ".join(published[-15:]) if published else "ninguno"

    prompt = (
        f"Fecha actual: {today_str}.\n"
        f"Titulares en tendencia hoy:\n{trends_block}\n\n"
        f"Temas ya usados recientemente (NO repetir): {avoid_block}\n\n"
        "Elige o adapta 1 tema sumamente interesante de supervivencia, misterio, ciencia o curiosidad viral estilo 'Curiosamente Graficado' o 'Sobrevive con Bruno'.\n"
        "Devuelve ÚNICAMENTE un JSON con estas 2 claves exactas:\n"
        '- "topic": título del tema para generar el guion\n'
        '- "caption": descripción interesante con una pregunta para debatir en comentarios y 4 hashtags (#reels #viral etc.)\n'
        "Sin bloques markdown, solo JSON puro."
    )
    raw = _call_gemini_fast(prompt, timeout_sec=10.0)
    if raw:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                topic = data.get("topic", "").strip()
                caption = data.get("caption", "").strip()
                if topic:
                    published.append(topic)
                    history_path.write_text(json.dumps(published[-50:], ensure_ascii=False, indent=2), encoding="utf-8")
                    print(f"      [Tendencia elegida]: '{topic}'")
                    return topic, caption or f"{topic} ¿Tú qué opinas? #reels #misterios #curiosidades #viral"
            except Exception:
                pass

    # Elegir un tema fresco que no esté en los últimos publicados
    candidates = [t for t in CURATED_COMIC_TOPICS if t not in published[-8:]] + headlines
    fallback_topic = candidates[len(published) % len(candidates)] if candidates else CURATED_COMIC_TOPICS[0]
    published.append(fallback_topic)
    history_path.write_text(json.dumps(published[-50:], ensure_ascii=False, indent=2), encoding="utf-8")
    fallback_caption = (
        f"¿Te imaginas vivir esto en la vida real? {fallback_topic}. "
        "¿Tú qué harías en esta situación? ¡Te leo en los comentarios! #reels #supervivencia #misterios #curiosidades #viral"
    )
    return fallback_topic, fallback_caption


def generate_script(topic: str) -> str:
    """
    Genera el guion usando Gemini REST rápido (10s max), FreeLLM (g4f) o guion narrativo dinámico.
    """
    system_instruction = (
        "Eres un guionista experto en videos animados de supervivencia y misterios estilo Don Zombi y Curiosamente Graficado. "
        "Escribe únicamente el texto hablado del narrador en español. "
        "Reglas estrictas:\n"
        "- Duración de lectura: 25 a 35 segundos (entre 65 y 85 palabras).\n"
        "- Comienza con una pregunta o gancho muy potente y desarrolla 3 fases o datos sorprendentes.\n"
        "- NO incluyas etiquetas como '[Música]', 'Narrador:', asteriscos, emojis ni acotaciones de escena.\n"
        "- Devuelve solo el párrafo limpio que leerá la voz artificial."
    )

    print(f"[1/4] Generando guion sobre: '{topic}'...")

    script_text = _call_gemini_fast(
        f"Crea un guion narrativo atrapante en español sobre: {topic}",
        system_instruction=system_instruction,
        timeout_sec=10.0,
    )
    if script_text:
        script_path = OUTPUT_DIR / "guion.txt"
        script_path.write_text(script_text, encoding="utf-8")
        print(f"      Guion generado con Gemini en: {script_path}")
        return script_text

    try:
        from g4f.client import Client as G4FClient  # type: ignore

        def _g4f_call() -> str:
            g4f_client = G4FClient()
            response = g4f_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Crea un guion narrativo corto en español sobre: {topic}"},
                ],
            )
            return (response.choices[0].message.content or "").strip()

        with ThreadPoolExecutor(max_workers=1) as ex:
            script_text = ex.submit(_g4f_call).result(timeout=12)
        if script_text and len(script_text.split()) >= 25:
            script_path = OUTPUT_DIR / "guion.txt"
            script_path.write_text(script_text, encoding="utf-8")
            print(f"      Guion generado con FreeLLM (g4f) en: {script_path}")
            return script_text
    except Exception as exc:
        print(f"      Aviso FreeLLM: {exc}")

    # Respaldo narrativo dinámico garantizado (sin repeticiones ni bloqueos)
    fallback_scripts = [
        (
            f"¿Alguna vez te has preguntado qué pasaría realmente con {topic}? "
            "En las primeras veinticuatro horas, el noventa por ciento de las personas subestima por completo la situación y agota los recursos básicos en cuestión de minutos. "
            "Para el tercer día, cuando las comunicaciones fallan y nadie puede pedir ayuda externa, solo quienes conocen las reglas básicas de supervivencia logran mantenerse a salvo. "
            "Al final, el mayor peligro nunca es el fenómeno en sí, sino el pánico colectivo."
        ),
        (
            f"Existe un detalle oculto detrás de {topic} que muy pocas personas conocen hasta que es demasiado tarde. "
            "Aunque la ciencia moderna ha intentado explicarlo con satélites y sensores avanzados, las condiciones extremas destruyen cualquier equipo en pocas horas. "
            "Quienes han investigado este misterio coinciden en tres señales de alerta que jamás debes ignorar si quieres salir con vida. "
            "Y tú, ¿te atreverías a comprobarlo por tu cuenta?"
        ),
    ]
    chosen_script = fallback_scripts[abs(hash(topic)) % len(fallback_scripts)]
    script_path = OUTPUT_DIR / "guion.txt"
    script_path.write_text(chosen_script, encoding="utf-8")
    return chosen_script


def _plan_visual_scenes(script_text: str, num_scenes: int = 4) -> List[Dict[str, str]]:
    """
    Usa Gemini REST rápido para extraer escenas con etiquetas explicativas en español.
    """
    default_scenes = [
        {
            "query": "survival bunker emergency supplies cartoon",
            "title": "FASE 1: LAS PRIMERAS 24H",
            "subtitle": "El error que comete el 90% de la gente",
        },
        {
            "query": "dark city blackout survival comic",
            "title": "FASE 2: DÍA 3 SIN SEÑAL",
            "subtitle": "Cuando fallan todas las comunicaciones",
        },
        {
            "query": "remote island lighthouse rescue comic",
            "title": "FASE 3: SUPERVIVENCIA EXTREMA",
            "subtitle": "La regla clave para resistir hasta el final",
        },
        {
            "query": "deep jungle mystery expedition cartoon",
            "title": "FASE 4: EL DATO OCULTO",
            "subtitle": "Lo que nadie te cuenta sobre este misterio",
        },
    ]

    prompt = (
        f"A partir de este guion:\n\"{script_text}\"\n\n"
        f"Devuelve ÚNICAMENTE un JSON array válido con {num_scenes} objetos. "
        "Cada objeto debe tener exactamente estas 3 claves:\n"
        '- "query": descripción corta en inglés de la escena (2 a 4 palabras)\n'
        '- "title": título corto impactante en mayúsculas en español (máximo 3 palabras)\n'
        '- "subtitle": subtítulo corto en mayúsculas en español (máximo 4 palabras)\n'
        "No incluyas bloques markdown ```json, solo el JSON puro."
    )
    raw = _call_gemini_fast(prompt, timeout_sec=10.0)
    if raw:
        match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
        if match:
            try:
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
    lista para el muro de Facebook, acompañada opcionalmente de una postal cómic 2D 4:5 (1080x1350).
    """
    print(f"[Historia] Redactando historia viral para Facebook sobre: '{topic}'...")
    story_text = ""
    img_query = "mystery jungle survival comic"
    headline = topic[:30].upper()
    subheadline = "EL DATO QUE POCOS CONOCEN"

    prompt = (
        f"Escribe una publicación fascinante para Facebook en español contando una historia o caso de supervivencia/misterio sobre: '{topic}'.\n"
        "Estructura de la historia:\n"
        "- Primera línea: Un título o pregunta gancho muy potente.\n"
        "- Desarrollo: 2 a 3 párrafos cortos contando la historia, datos reales o reglas de supervivencia de forma clara y atrapante.\n"
        "- Cierre: Una pregunta abierta para que los seguidores debatan en los comentarios + 4 hashtags.\n"
        "- NO uses caracteres especiales raros, escribe en texto limpio.\n\n"
        "Devuelve ÚNICAMENTE un JSON válido con estas 4 claves:\n"
        '- "story": el texto completo de la publicación (con saltos de línea \\n)\n'
        '- "query": descripción de la escena en inglés (2 a 4 palabras)\n'
        '- "headline": titular corto impactante en español (máximo 4 palabras en mayúsculas)\n'
        '- "subheadline": subtítulo explicativo en español (máximo 6 palabras)\n'
        "Sin bloques markdown, solo JSON puro."
    )
    raw = _call_gemini_fast(prompt, timeout_sec=10.0)
    if raw:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                story_text = data.get("story", "").strip()
                img_query = data.get("query", img_query).strip()
                headline = data.get("headline", headline).strip()
                subheadline = data.get("subheadline", subheadline).strip()
            except Exception:
                pass

    if not story_text:
        story_text = (
            f"¿Qué harías tú si tuvieras que enfrentarte a esto? {topic}\n\n"
            "La mayoría de las personas cree que sabría exactamente cómo reaccionar en una situación límite, "
            "pero los expertos en supervivencia revelan que las decisiones de los primeros 15 minutos lo definen todo.\n\n"
            "¿Cuál sería tu primer movimiento o qué objeto llevarías contigo? ¡Déjalo en los comentarios y veamos quién sobreviviría más tiempo!\n\n"
            "#supervivencia #misterios #curiosidades #historias #tendencias"
        )

    story_path = OUTPUT_DIR / "story_post.txt"
    story_path.write_text(story_text, encoding="utf-8")

    if not with_image:
        return story_text, None

    seed_val = abs(hash(topic)) % 900 + 100
    print(f"[Imagen] Creando postal ilustrada estilo cómic 2D (1080x1350) para '{img_query}'...")
    from youtube_story_animator import fetch_or_generate_comic_art

    art_prompt = (
        "2D cartoon comic illustration in the style of Curiosamente Graficado and Don Zombi, "
        "clean bold black outlines, vibrant comic shading, expressive white round-headed cartoon character "
        f"exploring: {img_query}, vertical 4:5, no text"
    )
    art_path = fetch_or_generate_comic_art(art_prompt, OUTPUT_DIR / f"post_comic_{seed_val}.png", seed=seed_val)
    if art_path.exists():
        raw_img = Image.open(art_path).convert("RGB")
    else:
        raw_img = _fetch_real_hd_image(img_query, 1)

    card = ImageOps.fit(raw_img, (1080, 1350), method=Image.Resampling.LANCZOS)
    card = ImageEnhance.Color(card).enhance(1.15)
    draw = ImageDraw.Draw(card, "RGBA")

    bold_path = r"C:\Windows\Fonts\impact.ttf" if Path(r"C:\Windows\Fonts\impact.ttf").exists() else r"C:\Windows\Fonts\arialbd.ttf"
    reg_path = r"C:\Windows\Fonts\arialbd.ttf"
    font_h = ImageFont.truetype(bold_path, 62) if Path(bold_path).exists() else ImageFont.load_default()
    font_s = ImageFont.truetype(reg_path if Path(reg_path).exists() else bold_path, 36)

    draw.rectangle([0, 980, 1080, 1350], fill=(0, 0, 0, 165))
    draw.text(
        (540, 1095),
        headline[:32].upper(),
        font=font_h,
        fill=(255, 255, 255, 255),
        anchor="mm",
        stroke_width=6,
        stroke_fill=(0, 0, 0, 255),
    )
    draw.rounded_rectangle([140, 1155, 940, 1235], radius=14, fill=(215, 35, 35, 245), outline=(0, 0, 0, 255), width=4)
    draw.text(
        (540, 1195),
        subheadline[:44].upper(),
        font=font_s,
        fill=(255, 255, 255, 255),
        anchor="mm",
    )

    img_out = OUTPUT_DIR / "post_image.jpg"
    card.save(img_out, quality=95)
    print(f"      Imagen para publicación guardada en: {img_out}")
    return story_text, img_out


def generate_engaging_video_caption(topic: str, script_text: str) -> str:
    """
    Genera una descripción interesante para el video acompañada de una pregunta
    de debate directamente relacionada con el contenido del video para impulsar comentarios.
    """
    prompt = (
        f"Tema del video: '{topic}'\n"
        f"Guion del video: \"{script_text}\"\n\n"
        "Escribe una descripción sumamente atractiva en español para publicar este Reel en Facebook.\n"
        "Estructura obligatoria:\n"
        "1. Un gancho o dato intrigante de 1 a 2 líneas sobre lo que revela el video.\n"
        "2. Una pregunta abierta muy interesante acerca del video para que la gente debata y deje su opinión en los comentarios (ej. '¿Tú qué harías en esta situación?' o '¿Cuánto tiempo crees que sobrevivirías?').\n"
        "3. 5 hashtags relevantes en tendencia (#reels #curiosidades #misterios #supervivencia #viral).\n"
        "Devuelve únicamente el texto limpio listo para copiar y pegar, sin caracteres raros ni bloques markdown."
    )
    text = _call_gemini_fast(prompt, timeout_sec=10.0)
    if text:
        return text

    return (
        f"¿Te imaginas estar en medio de esto? {topic}. "
        "Mira el video hasta el final porque el último dato cambia todo. "
        "¿Tú qué harías en esta situación o cuál sería tu plan para sobrevivir? ¡Te leo en los comentarios! "
        "#reels #curiosidades #supervivencia #misterios #viral"
    )


def run_generation_pipeline(topic: str) -> tuple[Path, Path]:
    script_text = generate_script(topic)
    scenes_meta = _plan_visual_scenes(script_text, num_scenes=3)
    meta_path = OUTPUT_DIR / "scenes_meta.json"
    meta_path.write_text(json.dumps(scenes_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    audio_path = OUTPUT_DIR / "narration.mp3"
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
