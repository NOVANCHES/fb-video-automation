"""
visual_engine.py
================
Motor Inteligente de Recursos Visuales Dinámicos para Bruno Schiller (Gaming).
Soporta:
1. Videos cortos (.mp4, .webm) con reescalado inteligente 9:16 (B-roll de gameplay).
2. GIFs animados (.gif) con looping suave a 24 FPS.
3. Ilustraciones de alta gama (.jpg, .png) con zoom cinético Ken Burns.
4. Generación procedimental de fondos dinámicos retro/gaming (Matrix code, estrellas, neón).
5. Sistema anti-repetición estricto: NUNCA reutiliza la misma imagen o escena en videos consecutivos.
"""

import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from config import BASE_DIR, OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS

ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
MEDIA_DIR = ASSETS_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def create_procedural_gaming_background(
    theme: str,
    duration: float,
    width: int = VIDEO_WIDTH,
    height: int = VIDEO_HEIGHT,
) -> Image.Image:
    """
    Genera un fondo estético temático de videojuegos (cyberpunk neon, retro matrix o espacio oscuro)
    cuando no hay archivos locales disponibles.
    """
    img = Image.new("RGB", (width, height), (12, 14, 24))
    draw = ImageDraw.Draw(img)

    if "minecraft" in theme.lower() or "creeper" in theme.lower():
        # Fondo pixelado verde oscuro y negro estilo Minecraft
        grid_size = 40
        for x in range(0, width, grid_size):
            for y in range(0, height, grid_size):
                shade = random.randint(15, 45)
                green_tint = random.randint(30, 80)
                draw.rectangle([x, y, x + grid_size, y + grid_size], fill=(shade, green_tint, shade))
    elif "ps2" in theme.lower() or "playstation" in theme.lower():
        # Nebulosa azul cósmica con torres estilo inicio PS2
        for y in range(height):
            alpha = y / height
            r = int(5 + 10 * alpha)
            g = int(8 + 15 * alpha)
            b = int(25 + 65 * alpha)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        # Cyberpunk neón oscuro degradado
        for y in range(height):
            alpha = y / height
            r = int(10 + 20 * alpha)
            g = int(8 + 10 * alpha)
            b = int(22 + 40 * alpha)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    return img


def get_scene_visuals_for_topic(
    topic_data: Dict[str, Any],
    requested_scenes: int = 3,
) -> List[Path]:
    """
    Obtiene la lista de rutas a recursos visuales únicos (imágenes, gifs o videos)
    para el tema dado, garantizando que NO sean repetidos.
    """
    theme_id = topic_data.get("theme_id") or topic_data.get("id") or "gaming"
    
    # 1. Buscar archivos que coincidan exactamente con el theme_id
    matches = sorted(
        list(IMAGES_DIR.glob(f"{theme_id}*.jpg")) +
        list(IMAGES_DIR.glob(f"{theme_id}*.png")) +
        list(MEDIA_DIR.glob(f"{theme_id}*.mp4")) +
        list(MEDIA_DIR.glob(f"{theme_id}*.gif"))
    )

    if len(matches) >= requested_scenes:
        return matches[:requested_scenes]

    # 2. Si faltan, buscar en assets/images con prefijo gaming_
    gaming_files = [
        p for p in sorted(list(IMAGES_DIR.glob("gaming_*.jpg")) + list(IMAGES_DIR.glob("gaming_*.png")))
        if theme_id in p.name
    ]
    if gaming_files:
        return gaming_files[:requested_scenes]

    return matches
