"""
veo_generator.py — Módulo de Generación de Video Cinemático con Google Veo.
Integra el SDK google-genai para generar clips verticales (9:16) por escena del guion.
Incluye fallback automático al motor 2D si Veo falla por cuota o error.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from config import GEMINI_API_KEY, OUTPUT_DIR


# ==============================================================================
# PROMPTS CINEMÁTICOS EN INGLÉS (COHERENCIA IMAGEN-GUION ESTRICTA POR TEMA)
# ==============================================================================
VEO_SCENE_PROMPTS: Dict[str, List[str]] = {
    "ocean": [
        "Cinematic vertical 9:16 shot, deep-sea submarine descent, abyssal darkness at 11,000 meters, bioluminescent jellyfish floating around titanium porthole, 2D comic style, teal and dark blue tones, dramatic lighting",
        "Vertical 9:16 POV shot inside submarine, giant anglerfish with glowing lure emerges from pitch-black water, deep pressure gauges on dashboard showing 800 ATM, comic book 2D art style, intense motion blur",
        "Vertical 9:16 cinematic shot, hydrothermal vents on ocean floor emitting super-heated mineral plumes at 400°C, translucent abyssal creatures swimming nearby, dark aqua tones, dramatic underwater lighting",
        "Vertical 9:16 shot, sonar radar screen inside submarine cockpit blinking urgently, depth counter ticking to -10994m, extreme tension, comic book style illustration, blue and amber HUD glow",
        "Vertical 9:16 epic shot, submarine pilot looking out porthole at the Challenger Deep abyss, question mark floating above cartoon head, dramatic ocean blue gradient, closing cinematic frame",
    ],
    "space": [
        "Vertical 9:16 cinematic shot, massive solar flare eruption from the sun surface, coronal mass ejection CME wave rushing toward Earth at 2000 km/s, space station alert sirens, dramatic orange and red palette, comic book 2D style",
        "Vertical 9:16 shot, GPS satellite tumbling out of orbit, electrical arcs discharging from solar panels, Earth visible below, dark space background, comic book illustration style, high contrast red alerts",
        "Vertical 9:16 POV from mission control, global power grid map showing cascading blackout zones spreading across continents, operators in panic, amber emergency lights, dramatic newsroom energy",
        "Vertical 9:16 cinematic shot, commercial aircraft cockpit with blank navigation screens after GPS failure, emergency lights on, pilot looking alarmed, cloud layer below, 2D cartoon illustration style",
        "Vertical 9:16 closing shot, cartoon explorer in space suit staring at planet Earth from orbit, question mark bubble above head, 'Are we prepared?' cosmic starfield background, epic scale",
    ],
    "blackout": [
        "Vertical 9:16 cinematic shot, major city skyline plunged into total darkness, only emergency vehicle lights visible, social panic in the streets below, dramatic storm clouds, 2D comic book illustration style",
        "Vertical 9:16 shot, empty ATM machine with error screen, long panicked queue behind it, neon signs flickering out one by one, cinematic night street, comic art style, amber sodium lamp tones",
        "Vertical 9:16 dramatic shot, water pump station completely offline, pressure gauges at zero, desperate family turning on faucet with no water, dark apartment building, 2D illustration",
        "Vertical 9:16 shot, emergency generator sputtering and dying, refrigerator thawing food, family in flashlight glow around radio, last battery light blinking, survival tension, comic book style",
        "Vertical 9:16 epic shot, one prepared family at a table with bottled water and canned food versus dark panicked city outside the window, dramatic contrast lighting, 2D cartoon style",
    ],
    "prehistory": [
        "Vertical 9:16 cinematic shot, Devonian ocean with massive armored Dunkleosteus fish jaw rushing toward camera, prehistoric coral formations, 400 million years ago atmosphere, dark ocean palette, 2D comic style",
        "Vertical 9:16 shot, Carboniferous forest with giant scorpions the size of dogs and meter-wide dragonflies, dense swamp, 31% oxygen atmosphere visible as thick haze, ultra-lush green palette, comic art",
        "Vertical 9:16 epic shot, cartoon explorer running through Jurassic valley as a herd of massive Brachiosaurus dinosaurs stampede past, volcanic mountains in background, earth trembling dust clouds, 2D illustration",
        "Vertical 9:16 cinematic shot, Cretaceous jungle with feathered raptors sprinting toward camera through volcanic ash rain, extreme tension and motion, orange volcanic sky, 2D comic book illustration",
        "Vertical 9:16 dramatic closing shot, asteroid impact fireball visible on horizon with shockwave rolling across prehistoric landscape, cartoon explorer hiding in cave, epic scale, 2D illustration",
    ],
    "island": [
        "Vertical 9:16 cinematic shot, forbidden island coastline with dense tropical jungle, mysterious bunker entrance half-hidden by vines, dramatic storm clouds and mist, 2D comic art style, lush greens",
        "Vertical 9:16 POV shot, cartoon explorer hacking through dense jungle vines with machete, ancient carved stone markers partially visible under moss, dramatic sunlight beams through canopy, adventure comic style",
        "Vertical 9:16 dramatic shot, old military bunker metal door with rusted warning signs, explorer shining flashlight on lock mechanism, tropical insects, 2D cartoon illustration style",
        "Vertical 9:16 overhead shot, small island surrounded by shark-infested waters, distant cargo ship on horizon too far to signal, explorer holding improvised SOS banner, survival tension",
        "Vertical 9:16 closing shot, cartoon explorer sitting on beach at sunset looking at horizon, thought bubble with 30-day calendar, question mark over head, warm tropical palette",
    ],
    "jungle": [
        "Vertical 9:16 cinematic shot looking up through Amazon jungle canopy, 60-meter tall trees forming impenetrable green ceiling blocking 99% of sunlight, drone signal lost indicator, dramatic shafts of light, 2D comic style",
        "Vertical 9:16 shot, drone crashing through dense jungle foliage and losing GPS signal, interference static on remote control screen, cartoon operator in panic, ultra-lush tropical green environment, comic art",
        "Vertical 9:16 dramatic shot, jungle floor in near total darkness, explorer flashlight revealing giant unclassified insect and toxic frog species, eerie bioluminescence, comic book illustration style",
        "Vertical 9:16 LiDAR scan visualization shot, laser beams penetrating jungle canopy revealing hidden ancient pyramid structures below, geometric ruins emerging from digital scan, tech aesthetic meets archaeology",
        "Vertical 9:16 closing epic shot, aerial view of Amazon rainforest stretching to horizon, tiny explorer figure with question mark above, 'What else is hidden here?' text overlay, vast green scale",
    ],
    "zombie": [
        "Vertical 9:16 cinematic shot, panicked crowd rushing supermarket entrance at evacuation hour zero, empty shelves, overturned shopping carts, emergency sirens, dramatic tension, 2D comic book illustration style",
        "Vertical 9:16 shot, highway gridlock at rush hour during emergency evacuation, single car accident blocking all lanes, desperate drivers abandoning vehicles, helicopter spotlight overhead, comic art style",
        "Vertical 9:16 dramatic shot, overloaded phone tower with static interference, hundreds of people staring at NO SIGNAL screens simultaneously, communication blackout panic, 2D illustration",
        "Vertical 9:16 cinematic shot, cartoon character packing emergency backpack with flashlight, water bottles, first aid kit, radio, while city chaos erupts outside window, comic book style",
        "Vertical 9:16 closing shot, prepared family at designated meeting point on map, calm expression amid chaos, '5 survival errors' text overlay, 2D comic art style",
    ],
}


def _build_veo_prompt(scene_text: str, theme: str, scene_index: int) -> str:
    """
    Construye el prompt cinemático en inglés para Veo extrayendo entidades clave
    del fragmento exacto del guion que se narra en esa escena.
    """
    prompts = VEO_SCENE_PROMPTS.get(theme, VEO_SCENE_PROMPTS["zombie"])
    base = prompts[scene_index % len(prompts)]

    # Enriquecer con palabras clave del texto narrado (coherencia imagen-guion)
    keywords = []
    txt = scene_text.lower()
    kw_map = {
        "profundidad": "extreme depth", "satélite": "satellite orbit",
        "apagón": "total blackout", "agua": "water crisis",
        "presión": "crushing pressure", "oscuridad": "total darkness",
        "tormenta solar": "solar storm CME", "selva": "dense rainforest",
        "isla": "forbidden island", "radar": "radar scan active",
        "dinosaurio": "dinosaur stampede", "asteroide": "asteroid impact",
        "bioluminiscente": "bioluminescent deep sea creatures",
        "transformador": "power transformer explosion",
    }
    for es_kw, en_kw in kw_map.items():
        if es_kw in txt:
            keywords.append(en_kw)

    if keywords:
        base += ", featuring " + ", ".join(keywords[:3])

    return base + ", vertical 9:16 aspect ratio, 8-second cinematic clip, broadcast quality"


def generate_veo_clips(
    script_text: str,
    theme: str,
    scene_titles: List[str],
    output_dir: Optional[Path] = None,
) -> Optional[List[Path]]:
    """
    Genera clips cinemáticos verticales (9:16) con Google Veo 3.1 para cada escena.
    Si Veo devuelve error de cuota (429/resource_exhausted), retorna None para
    activar el fallback automático al motor de animación 2D.

    Args:
        script_text:  Guion completo narrado.
        theme:        Temática ('ocean', 'space', 'blackout', etc.)
        scene_titles: Títulos de las 5 escenas (para nombres de archivos).
        output_dir:   Directorio de salida (por defecto: OUTPUT_DIR).

    Returns:
        Lista de Path a los clips .mp4 si el 100% tuvo éxito, o None si falla.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY in ("", "tu_api_key_de_gemini_aqui"):
        print("[Veo] GEMINI_API_KEY no configurada — activando fallback al motor 2D.")
        return None

    out_dir = output_dir or OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError:
        print("[Veo] google-genai no instalado — activando fallback al motor 2D.")
        return None

    # Dividir el guion en bloques por escena
    sentences = [s.strip() for s in script_text.replace(". ", ".|").split("|") if s.strip()]
    n = len(scene_titles)
    block_size = max(1, len(sentences) // n)
    scene_blocks = []
    for i in range(n):
        start = i * block_size
        end = start + block_size if i < n - 1 else len(sentences)
        scene_blocks.append(" ".join(sentences[start:end]))

    print(f"[Veo] Generando {n} clips cinemáticos verticales (9:16) para tema '{theme}'...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    clip_paths: List[Path] = []

    for idx, (block, title) in enumerate(zip(scene_blocks, scene_titles)):
        prompt = _build_veo_prompt(block, theme, idx)
        clip_out = out_dir / f"veo_{theme}_scene_{idx:02d}.mp4"

        # Usar clip en caché si ya existe y tiene tamaño válido
        if clip_out.exists() and clip_out.stat().st_size > 100_000:
            print(f"[Veo]   Escena {idx + 1}/{n} en caché: {clip_out.name}")
            clip_paths.append(clip_out)
            continue

        print(f"[Veo]   Escena {idx + 1}/{n}: {title[:45]}...")
        print(f"[Veo]   Prompt: {prompt[:80]}...")

        try:
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                source=genai_types.GenerateVideosSource(prompt=prompt),
                config=genai_types.GenerateVideosConfig(
                    number_of_videos=1,
                    duration_seconds=8,
                    enhance_prompt=True,
                    aspect_ratio="9:16",
                ),
            )

            # Polling con timeout de 4 minutos por clip
            max_wait = 240
            waited = 0
            while not operation.done and waited < max_wait:
                time.sleep(15)
                waited += 15
                operation = client.operations.get(operation)
                print(f"[Veo]   Renderizando… {waited}s/{max_wait}s", end="\r", flush=True)

            print()  # nueva línea tras el \r

            if not operation.done:
                print(f"[Veo]   ⏱ Timeout en escena {idx + 1} — fallback al motor 2D")
                return None

            if not operation.response or not operation.response.generated_videos:
                print(f"[Veo]   ⚠ Sin respuesta de Veo en escena {idx + 1} — fallback al motor 2D")
                return None

            video_bytes = operation.response.generated_videos[0].video.video_bytes
            if not video_bytes:
                print(f"[Veo]   ⚠ Bytes vacíos en escena {idx + 1} — fallback al motor 2D")
                return None

            clip_out.write_bytes(video_bytes)
            size_kb = clip_out.stat().st_size // 1024
            print(f"[Veo]   ✅ Clip guardado: {clip_out.name} ({size_kb} KB)")
            clip_paths.append(clip_out)

        except Exception as e:
            err_lower = str(e).lower()
            if any(k in err_lower for k in ["quota", "429", "resource_exhausted", "rate_limit", "limit", "404", "not_found", "no longer available"]):
                print(f"\n[Veo]   ⚠ Modelo no disponible o cuota agotada: {e}")
                print("[Veo]   Activando fallback automático al motor de animación 2D...")
                return None
            print(f"\n[Veo]   ❌ Error en escena {idx + 1}: {e} — activando fallback 2D")
            return None

    if len(clip_paths) == n:
        print(f"[Veo] ✅ {n}/{n} clips generados con éxito.")
        return clip_paths
    else:
        print(f"[Veo] ⚠ Solo {len(clip_paths)}/{n} clips completados — fallback al motor 2D.")
        return None
