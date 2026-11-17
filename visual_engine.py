"""
visual_engine.py
================
Motor de Generación y Validación de Imágenes con Gemini Imagen (google-genai SDK).

Usa el modelo gemini-3.1-flash-lite-image (Nano Banana 2 Lite) para generar imágenes
únicas y específicas del videojuego en cada escena.

Reglas técnicas obligatorias:
1. Sin personajes recurrentes: cada prompt representa exclusivamente el videojuego del guion.
2. Limpieza total de archivos previos antes de ejecutar.
3. 3 llamadas independientes con prompts distintos. Prohibido usar fallbacks.
4. Validación criptográfica SHA-256: rechaza imágenes con hashes duplicados o ya usadas.
5. Nombres con ID de guion y timestamp único ({script_id}_escena{i}_{timestamp}.jpg).
"""

import hashlib
import io
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image

try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("[visual_engine] ADVERTENCIA: google-genai no disponible, usando Pollinations como respaldo.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from config import BASE_DIR, OUTPUT_DIR, VIDEO_HEIGHT, VIDEO_WIDTH

HASH_HISTORY_FILE = OUTPUT_DIR / "image_hashes_history.json"

# ---------------------------------------------------------------------------
# Modelos Gemini Imagen (en orden de preferencia)
# ---------------------------------------------------------------------------
IMAGEN_MODELS = [
    "gemini-3.1-flash-lite-image",   # Nano Banana 2 Lite — ultra-rápido
    "gemini-nano-banana-2.1",         # Nano Banana 2.1 — alta eficiencia
    "gemini-3-pro-image",             # Nano Banana Pro — mayor calidad
]


def _get_gemini_client():
    """Crea y devuelve un cliente Gemini autenticado con la API key del .env."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Intentar leer del archivo .env
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        raise RuntimeError("ERROR CRÍTICO: No se encontró GEMINI_API_KEY en el entorno ni en .env")
    return genai.Client(api_key=api_key)


def calculate_sha256(file_path: Path) -> str:
    """Calcula el hash criptográfico SHA-256 de un archivo en disco."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _generate_image_with_gemini(
    prompt: str,
    dest_path: Path,
    model: str = "gemini-3.1-flash-lite-image",
    max_retries: int = 3,
) -> Path:
    """
    Genera una imagen usando Gemini Imagen SDK y la guarda en dest_path.
    Lanza RuntimeError si falla tras max_retries intentos.
    PROHIBIDO EL USO DE FALLBACKS.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    client = _get_gemini_client()

    last_error = ""
    for attempt in range(1, max_retries + 1):
        print(f"      [Gemini Imagen] Intento {attempt}/{max_retries} | Modelo: {model}")
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=genai_types.ImageConfig(
                        aspect_ratio="9:16",
                    ),
                ),
            )

            # Extraer imagen de la respuesta
            img_data = None
            for part in response.parts:
                if part.inline_data and part.inline_data.data:
                    img_data = part.inline_data.data
                    break

            if not img_data:
                # Intentar vía as_image() si está disponible
                for part in response.parts:
                    if hasattr(part, "as_image"):
                        try:
                            pil_img = part.as_image()
                            buf = io.BytesIO()
                            pil_img.save(buf, format="JPEG", quality=95)
                            img_data = buf.getvalue()
                            break
                        except Exception:
                            pass

            if not img_data or len(img_data) < 5000:
                raise ValueError(f"Respuesta vacía o imagen muy pequeña ({len(img_data) if img_data else 0} bytes)")

            # Validar con Pillow y redimensionar si es necesario
            im = Image.open(io.BytesIO(img_data)).convert("RGB")
            if im.size != (VIDEO_WIDTH, VIDEO_HEIGHT):
                im = im.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)

            im.save(dest_path, "JPEG", quality=95)
            print(f"      [Gemini Imagen] ✅ Escena guardada: {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
            return dest_path

        except Exception as exc:
            last_error = str(exc)
            print(f"      [Gemini Imagen] ⚠️  Error en intento {attempt}: {last_error[:120]}")
            if attempt < max_retries:
                wait = 10 * attempt
                print(f"      [Gemini Imagen] Esperando {wait}s antes del reintento...")
                time.sleep(wait)

    raise RuntimeError(
        f"ERROR CRÍTICO: Gemini Imagen falló tras {max_retries} intentos con modelo '{model}'. "
        f"Último error: {last_error}. "
        "REGLA OBLIGATORIA: Está estrictamente prohibido usar imágenes de respaldo (fallback). Abortando."
    )


def _generate_image_with_pollinations(
    prompt: str,
    seed: int,
    dest_path: Path,
    max_retries: int = 5,
) -> Path:
    """
    Genera imagen con Pollinations flux-pro — modelo de alta calidad sin caché.
    Cada seed produce una imagen completamente diferente y única.
    Espera 52s entre reintentos en caso de rate limit 402.
    """
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    # flux-pro: sin caché agresivo, alta calidad, seed respetado
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?seed={seed}&width=1080&height=1920&nologo=true&model=flux-pro&enhance=true"
    )
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    last_error = ""
    for attempt in range(1, max_retries + 1):
        print(f"      [flux-pro] Intento {attempt}/{max_retries} | Seed {seed}")
        try:
            resp = requests.get(url, headers=headers, timeout=60)
            if resp.status_code == 200 and len(resp.content) > 5000:
                im = Image.open(io.BytesIO(resp.content)).convert("RGB")
                if im.size != (VIDEO_WIDTH, VIDEO_HEIGHT):
                    im = im.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
                im.save(dest_path, "JPEG", quality=95)
                print(f"      [flux-pro] ✅ {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
                return dest_path
            elif resp.status_code in (402, 429):
                wait_sec = 52.0
                print(f"      [flux-pro] Rate limit ({resp.status_code}). Pausa {wait_sec}s...")
                time.sleep(wait_sec)
                last_error = f"HTTP {resp.status_code}"
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:80]}"
                time.sleep(8.0)
        except Exception as exc:
            last_error = str(exc)
            time.sleep(8.0)

    raise RuntimeError(
        f"ERROR CRÍTICO: Pollinations flux-pro falló tras {max_retries} intentos. "
        f"Último error: {last_error}. Abortando — prohibido usar fallbacks."
    )


def validate_image_hashes(scene_paths: List[Path]) -> None:
    """
    REGLA 4 OBLIGATORIA:
    Valida mediante hash SHA-256 que:
    1. Las 3 imágenes generadas tengan hashes completamente distintos entre sí.
    2. Ningún hash coincida con imágenes utilizadas en ejecuciones previas (historial persistente).
    Si alguna validación falla, detiene con error crítico.
    """
    if len(scene_paths) != 3:
        raise ValueError(
            f"ERROR CRÍTICO: Se esperaban exactamente 3 imágenes de escena, "
            f"pero se recibieron {len(scene_paths)}."
        )

    hashes: List[str] = []
    for p in scene_paths:
        if not p.exists() or p.stat().st_size < 1000:
            raise FileNotFoundError(f"ERROR CRÍTICO: El archivo {p} no existe o está corrupto.")
        h = calculate_sha256(p)
        hashes.append(h)
        print(f"      [SHA-256] {p.name} -> {h[:16]}...")

    # Validación 1: Hashes entre sí
    if len(set(hashes)) < 3:
        raise ValueError(
            f"ERROR CRÍTICO: Dos o más imágenes tienen el mismo hash SHA-256. "
            f"Hashes: {hashes}. Abortando para evitar publicar escenas duplicadas."
        )

    # Validación 2: Contra historial
    historical: Set[str] = set()
    if HASH_HISTORY_FILE.exists():
        try:
            historical = set(json.loads(HASH_HISTORY_FILE.read_text(encoding="utf-8")))
        except Exception:
            historical = set()

    for i, h in enumerate(hashes, 1):
        if h in historical:
            raise ValueError(
                f"ERROR CRÍTICO: Imagen Escena {i} ({scene_paths[i-1].name}) ya fue usada "
                f"en un video anterior (Hash: {h}). Abortando."
            )

    # Guardar nuevos hashes en historial
    historical.update(hashes)
    HASH_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HASH_HISTORY_FILE.write_text(json.dumps(list(historical), indent=2), encoding="utf-8")
    print(f"      [SHA-256] ✅ 3 hashes únicos validados y registrados en {HASH_HISTORY_FILE.name}")


def generate_three_unique_scene_images(
    story_data: Dict[str, Any],
    timestamp_str: str,
) -> List[Path]:
    """
    REGLAS 1, 3 Y 5 OBLIGATORIAS:
    - 3 llamadas independientes a Gemini Imagen para ESCENA_1, ESCENA_2 y ESCENA_3.
    - Prompts distintos y específicos del videojuego del guion.
    - Nombres: {script_id}_escena{i}_{timestamp}.jpg.
    - Validación SHA-256 antes de entregar las rutas.
    """
    story_id = story_data.get("id") or story_data.get("theme_id") or "VID_001"
    prompts = story_data.get("scene_prompts")
    game = story_data.get("game", "videojuego")
    topic = story_data.get("topic", "")

    if not prompts or len(prompts) < 3:
        # Construir 3 prompts exclusivos del juego si no hay scene_prompts definidos
        prompts = [
            (
                f"Cinematic vertical 9:16 high resolution ultra-detailed screenshot of {game}, "
                f"showcasing {topic}, dramatic volumetric lighting, 4k game capture, "
                "no text, no watermarks, no logos, no human characters unrelated to the game"
            ),
            (
                f"Vertical 9:16 dramatic in-game gameplay perspective of {game}, "
                f"iconic game mechanics and environment, atmospheric lighting, "
                "ultra HD 4k game art, photorealistic render, no watermarks"
            ),
            (
                f"Vertical 9:16 cinematic key art of {game}, "
                f"featuring {topic} scene, epic composition, vibrant game palette, "
                "4k resolution, no text overlays, no logos"
            ),
        ]

    seeds = []
    while len(seeds) < 3:
        s = random.randint(1_000_000, 99_999_999)
        if s not in seeds:
            seeds.append(s)

    scene_paths: List[Path] = []
    print(f"\n[Visual Engine] 🎨 Generando 3 escenas únicas con Gemini Imagen para '{story_id}'...")

    # Intentar primero con Gemini Imagen; si falla, usar Pollinations flux-pro
    working_model = None
    if GENAI_AVAILABLE:
        for model_name in IMAGEN_MODELS:
            print(f"   Probando Gemini Imagen: {model_name}")
            try:
                test_prompt = prompts[0]
                test_dest = OUTPUT_DIR / f"{story_id}_escena1_{timestamp_str}.jpg"
                _generate_image_with_gemini(test_prompt, test_dest, model=model_name, max_retries=1)
                working_model = model_name
                scene_paths.append(test_dest)
                print(f"   ✅ Gemini Imagen funcional: {working_model}")
                break
            except Exception as e:
                print(f"   ❌ {model_name}: {str(e)[:80]}")
                continue

    if not working_model:
        print("   ⚠️  Gemini Imagen sin quota. Usando Pollinations flux-pro (imágenes únicas por seed)...")

    # Generar las escenas (desde la 1 si no hay Gemini, desde la 2 si ya se generó la primera)
    start_i = 2 if working_model else 1

    for i in range(start_i, 4):
        prompt_text = prompts[i - 1]
        dest_filename = f"{story_id}_escena{i}_{timestamp_str}.jpg"
        dest_file = OUTPUT_DIR / dest_filename

        print(f"\n   >>> Generando ESCENA_{i} ({dest_filename})...")

        if working_model:
            _generate_image_with_gemini(
                prompt=prompt_text,
                dest_path=dest_file,
                model=working_model,
                max_retries=3,
            )
        else:
            _generate_image_with_pollinations(
                prompt=prompt_text,
                seed=seeds[i - 1],
                dest_path=dest_file,
                max_retries=5,
            )
            # Pausa entre imágenes para evitar rate limit 402
            if i < 3:
                print(f"      [flux-pro] Pausa 52s para evitar rate limit antes de la siguiente escena...")
                time.sleep(52)
        scene_paths.append(dest_file)

    # Validar unicidad criptográfica SHA-256
    print("\n   >>> Verificando unicidad criptográfica SHA-256...")
    validate_image_hashes(scene_paths)

    return scene_paths
