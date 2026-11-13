"""
visual_engine.py
================
Motor Inteligente de Generación y Validación Estricta de Recursos Visuales.
Aplica las 5 reglas técnicas obligatorias:
1. Sin personajes recurrentes: cada prompt representa exclusivamente el videojuego del guion.
2. Limpieza total de archivos previos antes de ejecutar.
3. 3 llamadas independientes con 3 semillas (seeds) aleatorias distintas. Prohibido usar fallbacks.
4. Validación criptográfica SHA-256: rechaza imágenes con hashes duplicados o ya usadas en el histórico.
5. Nombres con ID de guion y timestamp único ({script_id}_escena{i}_{timestamp}.jpg).
"""

import hashlib
import io
import json
import os
import random
import re
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image
import requests

from config import BASE_DIR, OUTPUT_DIR, VIDEO_HEIGHT, VIDEO_WIDTH

HASH_HISTORY_FILE = OUTPUT_DIR / "image_hashes_history.json"


def calculate_sha256(file_path: Path) -> str:
    """Calcula el hash criptográfico SHA-256 de un archivo en disco."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _download_and_verify_image(
    prompt: str,
    seed: int,
    dest_path: Path,
    max_retries: int = 4,
) -> Path:
    """
    Realiza una llamada independiente al generador de imágenes con una semilla aleatoria única.
    Valida físicamente la integridad del archivo y que sus dimensiones sean correctas (1080x1920).
    PROHIBIDO EL USO DE FALLBACKS: Si falla, lanza una excepción crítica inmediata.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=1080&height=1920&nologo=true"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    last_error = ""
    for attempt in range(1, max_retries + 1):
        print(f"      [Generador] Intento {attempt}/{max_retries} | Semilla {seed} | URL de generación lista...")
        try:
            resp = requests.get(url, headers=headers, timeout=35)
            if resp.status_code == 200 and len(resp.content) > 5000:
                # Validar imagen con Pillow
                im = Image.open(io.BytesIO(resp.content))
                im.verify()  # Verifica integridad estructural

                # Reabrir para procesamiento de tamaño
                im = Image.open(io.BytesIO(resp.content)).convert("RGB")
                if im.size != (VIDEO_WIDTH, VIDEO_HEIGHT):
                    im = im.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)

                im.save(dest_path, "JPEG", quality=95)
                print(f"      [Generador] ✅ Escena generada y verificada: {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
                return dest_path

            elif resp.status_code in (402, 429):
                # Extraer tiempo sugerido de espera si está en el cuerpo
                wait_sec = 46.0
                match = re.search(r"Retry after (\d+)s", resp.text)
                if match:
                    wait_sec = float(match.group(1)) + 2.0
                print(f"      [Generador] Rate limit temporal ({resp.status_code}). Pausando {wait_sec:.1f}s antes del reintento...")
                time.sleep(wait_sec)
                last_error = f"HTTP {resp.status_code}: {resp.text[:120]}"
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:120]}"
                time.sleep(5.0)

        except Exception as exc:
            last_error = str(exc)
            time.sleep(5.0)

    raise RuntimeError(
        f"ERROR CRÍTICO: Falló la generación de imagen para la escena tras {max_retries} intentos. "
        f"Detalle: {last_error}. "
        "REGLA OBLIGATORIA: Está estrictamente prohibido usar imágenes de respaldo (fallback). Abortando ejecución."
    )


def validate_image_hashes(scene_paths: List[Path]) -> None:
    """
    REGLA 4 OBLIGATORIA:
    Valida mediante hash SHA-256 que:
    1. Las 3 imágenes generadas tengan hashes completamente distintos entre sí (cero duplicadas).
    2. Ninguno de los hashes coincida con imágenes utilizadas en ejecuciones previas (historial persistente).
    Si alguna validación falla, detiene la ejecución con un error crítico (raise Exception).
    """
    if len(scene_paths) != 3:
        raise ValueError(f"ERROR CRÍTICO: Se esperaban exactamente 3 imágenes de escena, pero se recibieron {len(scene_paths)}.")

    hashes: List[str] = []
    for p in scene_paths:
        if not p.exists() or p.stat().st_size < 1000:
            raise FileNotFoundError(f"ERROR CRÍTICO: El archivo {p} no existe o está corrupto.")
        h = calculate_sha256(p)
        hashes.append(h)
        print(f"      [Validación SHA-256] {p.name} -> {h[:16]}...")

    # Validación 1: Comparar hashes entre sí
    if len(set(hashes)) < 3:
        raise ValueError(
            f"ERROR CRÍTICO: Dos o más imágenes generadas para este video tienen el mismo hash SHA-256. "
            f"Hashes generados: {hashes}. Abortando para evitar publicar escenas duplicadas."
        )

    # Validación 2: Comparar contra registro histórico
    historical: Set[str] = set()
    if HASH_HISTORY_FILE.exists():
        try:
            historical = set(json.loads(HASH_HISTORY_FILE.read_text(encoding="utf-8")))
        except Exception:
            historical = set()

    for i, h in enumerate(hashes, 1):
        if h in historical:
            raise ValueError(
                f"ERROR CRÍTICO: La imagen de la Escena {i} ({scene_paths[i-1].name}) ya fue utilizada "
                f"en un video anterior (Hash registrado: {h}). Abortando ejecución."
            )

    # Guardar los nuevos hashes en el registro histórico
    historical.update(hashes)
    HASH_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HASH_HISTORY_FILE.write_text(json.dumps(list(historical), indent=2), encoding="utf-8")
    print(f"      [Validación SHA-256] ✅ Hashes validados y registrados en {HASH_HISTORY_FILE.name}")


def generate_three_unique_scene_images(
    story_data: Dict[str, Any],
    timestamp_str: str,
) -> List[Path]:
    """
    REGLAS 1, 3 Y 5 OBLIGATORIAS:
    1. Realiza 3 llamadas independientes para ESCENA_1, ESCENA_2 y ESCENA_3.
    2. Utiliza 3 semillas aleatorias distintas.
    3. Nombra los archivos como {script_id}_escena{i}_{timestamp}.jpg.
    4. Valida hashes antes de entregar las rutas.
    """
    story_id = story_data.get("id") or story_data.get("theme_id") or "VID_001"
    prompts = story_data.get("scene_prompts")
    if not prompts or len(prompts) < 3:
        # Si no tiene prompts de escena definidos, construir 3 prompts exclusivos del juego
        game = story_data.get("game", "Videojuegos")
        topic = story_data.get("topic", "")
        prompts = [
            f"Cinematic vertical 9:16 high resolution video game capture of {game}, showcasing {topic}, dramatic lighting 4k",
            f"Vertical 9:16 gameplay mechanics and detailed in-game perspective of {game}, authentic video game graphics 4k",
            f"Vertical 9:16 climactic action scene from {game}, atmospheric environment and iconic game assets 4k",
        ]

    # Generar 3 semillas aleatorias estrictamente distintas
    seeds: List[int] = []
    while len(seeds) < 3:
        s = random.randint(1000000, 99999999)
        if s not in seeds:
            seeds.append(s)

    scene_paths: List[Path] = []
    print(f"\n[Visual Engine] Iniciando generación de 3 escenas independientes para '{story_id}'...")

    for i in range(1, 4):
        prompt_text = prompts[i - 1]
        seed_val = seeds[i - 1]
        dest_filename = f"{story_id}_escena{i}_{timestamp_str}.jpg"
        dest_file = OUTPUT_DIR / dest_filename

        print(f"\n   >>> Generando ESCENA_{i}_IMAGEN ({dest_filename}) con Semilla {seed_val}...")
        _download_and_verify_image(
            prompt=prompt_text,
            seed=seed_val,
            dest_path=dest_file,
        )
        scene_paths.append(dest_file)

    # Validar criptográficamente por hash SHA-256
    print("\n   >>> Verificando unicidad criptográfica SHA-256...")
    validate_image_hashes(scene_paths)

    return scene_paths
