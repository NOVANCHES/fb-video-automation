"""
gaming_topics.py
================
Catálogo exclusivo de Historias y Curiosidades Virales de Videojuegos.
Secretos, mitos, errores de programación históricos y misterios de PlayStation, Nintendo, Xbox, PC y GTA.
Cada historia incluye 3 prompts visuales exclusivos e independientes centrados 100% en el videojuego correspondiente.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

GAMING_STORIES: List[Dict[str, Any]] = [
    {
        "id": "gaming_ps2_towers",
        "theme_id": "gaming_ps2",
        "game": "PlayStation 2",
        "topic": "El secreto de las torres de inicio de la PlayStation 2",
        "title": "🎮 El secreto oculto en el inicio de tu PlayStation 2 #Shorts",
        "script": (
            "¿Sabías que las misteriosas torres blancas que aparecían al encender tu PlayStation 2 guardaban un secreto impresionante? "
            "Muchos pensaban que era solo una animación abstracta, pero esas torres representaban físicamente las partidas que tenías guardadas en tu Memory Card. "
            "Cada bloque era un juego diferente y su altura indicaba cuántas horas le habías dedicado. "
            "Si sacabas la Memory Card o la formateabas, el inicio de tu consola se convertía en un cementerio completamente vacío y oscuro. "
            "¿Cuántas torres tenías tú en tu PS2? Déjalo en los comentarios."
        ),
        "caption": (
            "El inicio de la PS2 no era una simple animación: era un mapa en tiempo real de tu Memory Card. 🕹️💾 "
            "¿Llegaste a tener la pantalla llena de torres gigantes? "
            "#PlayStation #PS2 #Gaming #Videojuegos #Curiosidades #Gamer #Nostalgia #Shorts #Reels"
        ),
        "scene_prompts": [
            "Cinematic vertical 9:16 macro shot of a sleek black PlayStation 2 console with glowing blue power LED light, retro gaming television display in background, atmospheric moody blue volumetric lighting, high resolution video game aesthetic",
            "Vertical 9:16 cosmic digital dimension with glowing 3D crystal monolith towers and blocks floating in dense blue mist, iconic PS2 boot screen startup sequence visual, cinematic data particles, octane render 4k",
            "Vertical 9:16 detailed close-up shot of an original black 8MB retro console Memory Card resting on a gaming table, subtle magical data glow and neon reflections, retro gaming memorabilia, 4k video game capture",
        ],
    },
    {
        "id": "gaming_minecraft_creeper",
        "theme_id": "gaming_creeper",
        "game": "Minecraft",
        "topic": "Cómo nació el Creeper por un error de código",
        "title": "🟩 El monstruo más temido de Minecraft nació por un cerdo bugeado #Shorts",
        "script": (
            "El monstruo más temido y legendario de Minecraft no fue planeado por los desarrolladores: nació literalmente por un error de programación de un cerdo. "
            "En dos mil nueve, Notch estaba escribiendo el código para añadir cerdos al juego. "
            "Por accidente, invirtió los valores de altura y longitud en la matriz del modelo 3D. "
            "En lugar de un cerdo horizontal de cuatro patas, apareció una criatura vertical, alargada y perturbadora. "
            "A Notch le fascinó tanto lo tenebrosa que se veía que le pintó una textura verde pixelada, le programó una explosión suicida al acercarse, y así nació el Creeper. "
            "Comenta MINECRAFT si alguna vez te explotó uno en la espalda."
        ),
        "caption": (
            "El Creeper existe gracias a un bug en el modelo del cerdo de Minecraft. 💥🐷 "
            "¿Cuál ha sido tu peor susto con un Creeper? "
            "#Minecraft #Creeper #Gamer #Gaming #Curiosidades #Videojuegos #Notch #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 3D wireframe glitch render of a Minecraft pig model distorted vertically, tall standing slender pink blocky pig creature with 4 stubby legs at bottom, developer debugging software screen, pixelated game art 4k",
            "Vertical 9:16 developer terminal monitor displaying green Java code matrix on dark background, on the right side a 3D Minecraft Creeper texture being applied, iconic pixelated camouflage green texture with hollow black eyes and frowning mouth, 4k",
            "Vertical 9:16 dramatic gameplay perspective inside a dark dense Minecraft oak forest at night under a bright square moon, a menacing green Creeper flashing white with sizzling TNT sparks about to explode, cinematic blocky voxel graphics 4k",
        ],
    },
    {
        "id": "gaming_gta_sa_planes",
        "theme_id": "gaming_gta_sa",
        "game": "GTA San Andreas",
        "topic": "Por qué los aviones se estrellaban solos en GTA San Andreas",
        "title": "✈️ El misterio de por qué los aviones se estrellaban solos en GTA #Shorts",
        "script": (
            "Si jugaste GTA San Andreas en tu infancia, seguro presenciaste decenas de avionetas cayendo del cielo y explotando contra edificios de la nada. "
            "Durante veinte años la comunidad inventó teorías de aviones fantasma y extraterrestres, pero hace poco un programador original de Rockstar reveló la verdad. "
            "El juego tenía una línea de código que hacía aparecer aviones sobrevolando en la dirección hacia donde miraba CJ. "
            "Sin embargo, el radar trazaba la ruta aérea antes de que el motor gráfico cargara las colisiones de rascacielos y árboles altos. "
            "Cuando los edificios aparecían en pantalla, la avioneta ya estaba dentro de su trayectoria a máxima velocidad y el choque era inevitable. "
            "¿Cuál fue el choque más loco que presenciaste en San Andreas?"
        ),
        "caption": (
            "Rockstar finalmente explicó el misterio de los aviones suicidas de GTA San Andreas. 🌆💥 "
            "Comenta cuál fue la avioneta que casi te aplasta mientras jugabas con CJ. "
            "#GTA #GTASanAndreas #RockstarGames #Gaming #Videojuegos #Misterios #Gamer #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 cinematic golden hour shot of Los Santos skyline in GTA San Andreas, retro low-poly video game architecture, vintage cars driving along Vinewood Boulevard, iconic palm trees, dramatic warm sunset lighting 4k",
            "Vertical 9:16 dramatic action shot of a vintage propeller airplane diving uncontrollably between downtown Los Santos skyscrapers, wings clipping concrete buildings with fiery sparks and smoke trails, dynamic motion blur 4k",
            "Vertical 9:16 technical radar HUD overlay with 3D wireframe city mesh collision map showing flight vector path crashing into high-rise building collision box, retro game engine debug visualization, 4k",
        ],
    },
    {
        "id": "gaming_mario_clouds",
        "theme_id": "gaming_mario",
        "game": "Super Mario Bros",
        "topic": "El engaño visual de las nubes y arbustos en Super Mario",
        "title": "🍄 El truco visual que Nintendo nos ocultó por 30 años en Mario #Shorts",
        "script": (
            "Nintendo engañó visualmente a millones de jugadores en el legendario Super Mario Bros de mil novecientos ochenta y cinco y casi nadie lo notó. "
            "El cartucho original de la consola NES tenía apenas cuarenta kilobytes de memoria total, menos que una foto de WhatsApp actual. "
            "Para ahorrar espacio crítico, Shigeru Miyamoto no podía guardar dos dibujos distintos para el cielo y la tierra. "
            "Por eso, las nubes del cielo y los arbustos del suelo son exactamente el mismo dibujo idéntico pixel por pixel. "
            "Lo único que hicieron fue cambiar la paleta de colores: pintaron las nubes de blanco con borde celeste y los arbustos de color verde. "
            "Dime si te habías dado cuenta de este truco de niño."
        ),
        "caption": (
            "Las nubes y los arbustos de Mario Bros son exactamente el mismo sprite con otro color. ☁️🌳 "
            "¿Te habías dado cuenta o acabas de desbloquear este recuerdo? "
            "#SuperMario #Nintendo #RetroGaming #NES #Videojuegos #Gamer #Curiosidades #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 retro 8-bit NES video game level World 1-1, vibrant blue sky, brick blocks and green warp pipes, authentic pixel art aesthetic, nostalgic retro console CRT screen scanlines 4k",
            "Vertical 9:16 split screen comparison graphic: on top a fluffy white cloud sprite in light blue sky, on bottom the identical green bush sprite on grassy terrain, pixel grid alignment overlay demonstrating identical geometry, 4k",
            "Vertical 9:16 macro shot of an authentic grey NES game cartridge circuit board showing the ROM microchip with 40KB capacity, golden circuit traces glowing with retro nostalgic amber lighting, 4k",
        ],
    },
    {
        "id": "gaming_pokemon_lavender",
        "theme_id": "gaming_pokemon",
        "game": "Pokémon Rojo y Azul",
        "topic": "La ciencia real detrás de la música de Pueblo Lavanda",
        "title": "👻 La verdad científica detrás de la música de Pueblo Lavanda #Shorts",
        "script": (
            "La música de Pueblo Lavanda en los primeros cartuchos de Pokémon provocó una de las leyendas urbanas más famosas de la historia de los videojuegos. "
            "El mito afirmaba que las frecuencias sonoras provocaban mareos y ansiedad extrema en los niños japoneses en mil novecientos noventa y seis. "
            "Aunque la historia de histeria colectiva fue una creepypasta de internet, la ciencia detrás de la composición es real. "
            "El compositor Junichi Masuda utilizó un intervalo disonante en semitonos tocado en ondas cuadradas agudas. "
            "El sistema auditivo humano interpreta instintivamente esa disonancia acústica como una alarma biológica de peligro inminente y depredadores cercanos. "
            "¿Te daba escalofríos escuchar esta melodía en tu Game Boy?"
        ),
        "caption": (
            "La ciencia detrás de la misteriosa música de Pueblo Lavanda en Pokémon. 🎵💀 "
            "¿Recuerdas el miedo que daba entrar a la Torre Pokémon de noche? "
            "#Pokemon #PuebloLavanda #Nintendo #GameBoy #Videojuegos #Gaming #Misterios #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 moody atmospheric render of Lavender Town from Pokémon, purple foggy streets with the towering silhouette of the Pokémon Tower graveyard, ghostly purple lanterns and eerie mist, pixel aesthetic 4k",
            "Vertical 9:16 sound frequency oscilloscope display showing harsh dissonant high-pitch square soundwaves vibrating against dark purple grid, audio engineering frequency spectrum analysis visual 4k",
            "Vertical 9:16 close-up of a classic grey Game Boy handheld console running the game with purple screen glow reflecting on buttons, moody dark room ambiance, retro gaming nostalgia 4k",
        ],
    },
    {
        "id": "gaming_rdr2_horse_detail",
        "theme_id": "gaming_rdr2",
        "game": "Red Dead Redemption 2",
        "topic": "La obsesión de detalles extremos en Red Dead Redemption 2",
        "title": "🤠 Los detalles enfermizos de realismo en Red Dead Redemption 2 #Shorts",
        "script": (
            "Red Dead Redemption dos es considerado el videojuego con el nivel de detalle más enfermizo de la historia de la industria. "
            "Rockstar dedicó más de ocho años y miles de desarrolladores para programar físicas que el noventa por ciento de los jugadores jamás notaría a simple vista. "
            "Por ejemplo, la anatomía de los caballos reacciona a la temperatura ambiental: en las montañas nevadas sus cuerpos tiemblan y sus partes se contraen por el frío, mientras que en el calor del desierto sudan espuma blanca realista. "
            "Si dejas a un enemigo abatido en el bosque, su cuerpo pasa por cuatro etapas de descomposición biológica a lo largo de varias semanas dentro del juego. "
            "¿Cuál es el detalle más impresionante que has descubierto en Red Dead?"
        ),
        "caption": (
            "El nivel de detalle y realismo de Red Dead Redemption 2 sigue insuperable. 🐎❄️ "
            "Comenta tu momento favorito en el mundo de Arthur Morgan. "
            "#RDR2 #RedDeadRedemption #RockstarGames #Gaming #Videojuegos #Gamer #Detalles #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 cinematic ultra-realistic western landscape in snowy Rocky Mountains, Arthur Morgan riding a majestic thoroughbred horse through deep snowdrifts, breath vapor visible in freezing air, 4k video game capture",
            "Vertical 9:16 extreme macro shot of horse coat and musculature reacting to extreme blizzard conditions, realistic frost on fur and detailed procedural weather physics, cinematic lighting 4k",
            "Vertical 9:16 atmospheric wild west valley at sunset, lush pine forests and dramatic mountain backdrop with god rays breaking through storm clouds, Red Dead Redemption open world scale 4k",
        ],
    },
    {
        "id": "gaming_zelda_oot_water_temple",
        "theme_id": "gaming_zelda",
        "game": "The Legend of Zelda",
        "topic": "Por qué el Templo del Agua casi arruina Zelda Ocarina of Time",
        "title": "🗝️ El nivel que le quitó el sueño a toda una generación de gamers #Shorts",
        "script": (
            "El Templo del Agua en Zelda Ocarina of Time es considerado por millones de jugadores como el nivel más desesperante y frustrante en la historia de Nintendo. "
            "Pero lo que pocos saben es que el propio director del juego, Eiji Aonuma, pidió disculpas públicas a la comunidad años después. "
            "El problema no era la dificultad de los acertijos: era que en la versión de Nintendo sesenta y cuatro tenías que pausar el juego cada quince segundos solo para ponerte y quitarte las botas de hierro en el menú. "
            "Aonuma confesó que el laberinto de compuertas inundadas fue diseñado de forma tan compleja que incluso a los propios desarrolladores les costaba terminarlo en las pruebas. "
            "¿Pudiste pasártelo sin usar ninguna guía?"
        ),
        "caption": (
            "El Templo del Agua: el laberinto que traumatizó a todos los jugadores de Nintendo 64. 🌊⚔️ "
            "Comenta cuántas horas te quedaste atascado buscando la última llave. "
            "#Zelda #OcarinaOfTime #Nintendo #N64 #RetroGaming #Gaming #Videojuegos #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 epic subterranean Water Temple interior from Legend of Zelda Ocarina of Time, massive multi-level submerged central pillar with water sluice gates and glowing runes under dark turquoise water, 4k",
            "Vertical 9:16 first-person perspective sinking to temple floor wearing heavy metallic Iron Boots with chains, air bubbles rising rapidly toward water surface, aquatic caustic reflections on ancient stone bricks 4k",
            "Vertical 9:16 iconic glowing golden small key resting inside a submerged stone corridor alcove, illuminated by underwater torches and magical blue water refractions, 4k cinematic render",
        ],
    },
]

GAMING_HISTORY_FILE = Path(__file__).parent / "output" / "gaming_history.json"


def get_next_gaming_story(story_id: str = "") -> Dict[str, Any]:
    """Obtiene una historia específica o rota ordenadamente sin repetir historias recientes."""
    if story_id and story_id.strip().lower() != "auto":
        for s in GAMING_STORIES:
            if s["id"] == story_id.strip() or s["theme_id"] == story_id.strip():
                return s

    history: List[str] = []
    if GAMING_HISTORY_FILE.exists():
        try:
            history = json.loads(GAMING_HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            history = []

    # Filtrar historias no usadas recientemente
    recent_set = set(history[-len(GAMING_STORIES) + 1:] if len(history) >= len(GAMING_STORIES) else history)
    available = [s for s in GAMING_STORIES if s["id"] not in recent_set]

    chosen = available[0] if available else GAMING_STORIES[len(history) % len(GAMING_STORIES)]

    history.append(chosen["id"])
    GAMING_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    GAMING_HISTORY_FILE.write_text(json.dumps(history[-50:], ensure_ascii=False, indent=2), encoding="utf-8")

    return chosen
