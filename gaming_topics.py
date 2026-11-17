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
    {
        "id": "gaming_sonic_blast_processing",
        "theme_id": "gaming_sonic",
        "game": "Sonic the Hedgehog",
        "topic": "El secreto de velocidad que Sega ocultó en Sonic para engañar al ojo humano",
        "title": "💨 Cómo Sega hacía que Sonic pareciera más rápido de lo que era #Shorts",
        "script": (
            "Sonic the Hedgehog no era tan rápido como parecía en la pantalla, y Sega tenía un truco visual brillante para engañar al ojo humano. "
            "El hardware del Sega Genesis de mil novecientos noventa y uno no podía renderizar fondos complejos a alta velocidad sin que el juego se trabara. "
            "Los programadores de Sega inventaron una técnica llamada deformación de scroll paralelo: en lugar de mover a Sonic, movían el fondo en capas a distintas velocidades. "
            "Las capas de fondo lejanas se desplazaban lento y las cercanas extremadamente rápido, creando una ilusión óptica de velocidad supersónica que duplicaba visualmente la sensación de movimiento. "
            "Sin ese truco de programación, Sonic se habría visto exactamente igual que Mario corriendo. "
            "¿Sabías que toda la velocidad de Sonic era una ilusión programada?"
        ),
        "caption": (
            "Sonic no era tan rápido como parecía — Sega usaba ilusión óptica de scroll paralelo. 💨🎮 "
            "¿Recuerdas la primera vez que jugaste Sonic en Sega Genesis? "
            "#Sonic #Sega #Genesis #RetroGaming #Videojuegos #Gaming #Curiosidades #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 hyper-speed blur motion trail of classic blue Sonic the Hedgehog sprinting through Green Hill Zone, vibrant checkerboard terrain, loop-de-loop in background, Sega Genesis retro pixel art, neon speed lines 4k",
            "Vertical 9:16 technical split-screen showing parallax scrolling layers at different speeds: foreground rocks fast, midground trees medium, distant mountains slow, retro game engine visual with speed indicators 4k",
            "Vertical 9:16 dramatic low-angle shot of Sonic spinning into a golden ring at maximum velocity, golden ring particles exploding outward, motion streaks, vibrant retro game aesthetic 4k",
        ],
    },
    {
        "id": "gaming_diablo_skeleton_king",
        "theme_id": "gaming_diablo",
        "game": "Diablo",
        "topic": "La historia oscura del Rey Esqueleto que aterrorizó a toda una generación",
        "title": "💀 El jefe que hizo llorar a miles de jugadores de Diablo 1 #Shorts",
        "script": (
            "En mil novecientos noventa y seis, Diablo de Blizzard lanzó al mundo al Rey Leoric, el Rey Esqueleto, y marcó el estándar de jefes terrorficos para toda una generación de jugadores. "
            "Lo que pocos saben es que el diseño sonoro de su voz fue grabado por el director de audio lanzando alaridos en un cuarto oscuro del estudio durante tres noches seguidas. "
            "El juego original fue desarrollado por solo veintiún personas en menos de ocho meses bajo una presión brutal de Blizzard para lanzarlo antes de Navidad. "
            "El modo multijugador en línea fue añadido en las últimas cuatro semanas de desarrollo y los propios programadores admitieron que nunca esperaban que funcionara. "
            "¿Recuerdas la primera vez que entraste a las mazmorras de Tristram?"
        ),
        "caption": (
            "Diablo 1 fue desarrollado por solo 21 personas en 8 meses. 💀🏰 "
            "¿Le tuviste miedo al Rey Esqueleto la primera vez? "
            "#Diablo #Blizzard #PCGaming #RPG #Videojuegos #Gaming #Misterios #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 dramatic gothic dungeon atmosphere from Diablo 1, dark stone cathedral corridors lit by flickering orange torches, ancient skeletal warrior king rising from a stone throne, ominous red mist 4k cinematic",
            "Vertical 9:16 isometric dark fantasy dungeon catacombs deep underground, broken stone pillars and skull-covered altar, cursed red candles and demonic runes glowing on floor, Diablo game aesthetic 4k",
            "Vertical 9:16 lone warrior in full plate armor standing at the entrance of a hellish underground labyrinth, distant red infernal glow, atmospheric dungeon fog, epic fantasy game composition 4k",
        ],
    },
    {
        "id": "gaming_halo_warthog_physics",
        "theme_id": "gaming_halo",
        "game": "Halo: Combat Evolved",
        "topic": "Por qué el Warthog de Halo era físicamente imposible pero adictivo",
        "title": "🚙 El vehículo más caótico de los videojuegos y por qué lo amábamos #Shorts",
        "script": (
            "El Warthog de Halo Combat Evolved es considerado por los ingenieros de Bungie como el peor vehículo físicamente diseñado de la historia de los videojuegos, y al mismo tiempo el más divertido. "
            "Su centro de gravedad estaba calculado completamente mal: el motor pesaba demasiado en la parte trasera y las ruedas tenían tracción irreal. "
            "Cada vez que frenabas bruscamente el Warthog salía disparado hacia adelante y volcaba. Si ibas cuesta abajo a máxima velocidad, el vehículo literalmente despegaba como avión. "
            "Los diseñadores de Bungie descubrieron en las pruebas que a los jugadores les causaba más risa conducirlo mal que bien, y en lugar de arreglar la física, decidieron dejarlo exactamente así de caótico. "
            "¿Cuántas veces te mató tu propio Warthog en campaña cooperativa?"
        ),
        "caption": (
            "El Warthog de Halo era físicamente imposible y por eso lo amábamos. 🚙💥 "
            "¿Cuántas veces te voló el Warthog con tu propio equipo adentro? "
            "#Halo #Warthog #Xbox #Bungie #Gaming #Videojuegos #Cooperativo #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 dramatic action shot of a Halo Warthog military jeep launching off a rocky cliff at high speed, spinning sideways in mid-air against an alien purple-sky landscape, sci-fi Halo universe atmosphere 4k",
            "Vertical 9:16 chaotic Halo battlefield scene, Warthog flipped upside down with UNSC marines scrambling out, Covenant plasma shots hitting nearby ground, epic alien planet warfare composition 4k",
            "Vertical 9:16 cinematic Halo ring structure visible in alien sky horizon, desert canyon terrain with Master Chief and a Warthog parked on rocky overlook, epic sci-fi military atmosphere 4k",
        ],
    },
    {
        "id": "gaming_pac_man_kill_screen",
        "theme_id": "gaming_pacman",
        "game": "Pac-Man",
        "topic": "La pantalla imposible de Pac-Man que tomó 26 años en descubrirse",
        "title": "👾 El nivel 256 de Pac-Man: el bug que nadie debía encontrar #Shorts",
        "script": (
            "En el año dos mil nueve, un jugador llamado Billy Mitchell alcanzó el nivel doscientos cincuenta y seis de Pac-Man y descubrió algo que Namco nunca esperaba que nadie viera. "
            "El juego original de arcade de mil novecientos ochenta usaba un byte de memoria para almacenar el número de nivel, y un byte solo puede contar hasta doscientos cincuenta y cinco. "
            "Cuando el contador intentó pasar de doscientos cincuenta y cinco, desbordó la memoria y corrompió la mitad derecha de la pantalla: se llenó de símbolos aleatorios, letras de colores y caracteres imposibles. "
            "Esta pantalla rota se llama Kill Screen y técnicamente hace el juego imbatible porque los puntos necesarios para completarlo están mezclados con datos corruptos. "
            "El nivel doscientos cincuenta y seis se convirtió en el nivel más famoso de la historia de los videojuegos arcade. "
            "¿Sabías que Pac-Man tenía un límite secreto que nadie debía alcanzar?"
        ),
        "caption": (
            "El nivel 256 de Pac-Man es el bug más famoso de la historia del arcade. 👾💾 "
            "¿Sabías que la pantalla se rompe completamente? "
            "#PacMan #Namco #Arcade #RetroGaming #Gaming #Videojuegos #Bugs #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 retro arcade game Pac-Man screen split in half: left side normal yellow Pac-Man maze with ghosts Blinky Pinky Inky and Clyde, right side completely corrupted with random symbols numbers and glitch colors, authentic CRT monitor scanlines 4k",
            "Vertical 9:16 dramatic close-up of a classic upright Pac-Man arcade cabinet glowing in a dark retro arcade room, neon lights reflecting on cabinet art, joystick illuminated, authentic 1980s atmosphere 4k",
            "Vertical 9:16 binary memory overflow visualization: a byte counter rolling from 255 to 000 corrupting a pixel grid maze, digital glitch aesthetic with green terminal font on black background 4k",
        ],
    },
    {
        "id": "gaming_skyrim_arrow_knee",
        "theme_id": "gaming_skyrim",
        "game": "The Elder Scrolls V: Skyrim",
        "topic": "El guardia con la flecha en la rodilla que paralizó internet en 2011",
        "title": "🏹 Cómo una sola frase de Skyrim se convirtió en el meme más viral de 2011 #Shorts",
        "script": (
            "En noviembre del dos mil once, Bethesda lanzó The Elder Scrolls cinco Skyrim y una sola frase pronunciada por un guardia cambió internet para siempre. "
            "La frase era simple: solía ser un aventurero como tú, pero un día recibí una flecha en la rodilla. "
            "El problema es que ese guardia tenía veinticinco frases de diálogo grabadas y esa era la que se escuchaba con más frecuencia por errores de peso de probabilidad en el código. "
            "En menos de dos semanas la frase se extendió por toda internet como un fenómeno viral masivo, con millones de variantes: solía ser programador, pero me dieron una flecha en la rodilla. "
            "Bethesda confesó años después que la frase fue escrita por un escritor de diálogos en veinte minutos y nunca imaginaron que se volvería el meme más reconocido de los videojuegos modernos. "
            "¿Cuántas veces escuchaste esa frase sin poder evitar repetirla?"
        ),
        "caption": (
            "Una sola frase de un guardia de Skyrim paralizó internet en 2011. 🏹⚔️ "
            "¿Recuerdas cuántas veces repetiste 'recibí una flecha en la rodilla'? "
            "#Skyrim #ElderScrolls #Bethesda #Memes #Gaming #Videojuegos #Viral #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 cinematic wide shot of Whiterun city in Skyrim during snowfall, dramatic stone walls and medieval Nordic architecture, Nordic guard in steel armor standing at the main gate, epic fantasy game atmosphere 4k",
            "Vertical 9:16 dramatic slow-motion arrow flying through frozen mountain air toward an armored knee in The Elder Scrolls Skyrim environment, snow particles and winter forest in background 4k",
            "Vertical 9:16 atmospheric Skyrim mountain landscape at dawn, Throat of the World peak visible through dramatic clouds, lone dovahkiin warrior silhouette with dragon flying overhead, epic Nordic fantasy 4k",
        ],
    },
    {
        "id": "gaming_tetris_soviet_origins",
        "theme_id": "gaming_tetris",
        "game": "Tetris",
        "topic": "Cómo un matemático soviético creó el videojuego más jugado de la historia",
        "title": "🧩 La historia secreta del matemático soviético que inventó Tetris #Shorts",
        "script": (
            "En mil novecientos ochenta y cuatro, un científico del Centro de Informática de la Academia de Ciencias de la Unión Soviética llamado Alexei Pajitnov creó Tetris en su computadora de trabajo. "
            "Pajitnov no recibió ni un solo rublo de regalías por su invención durante más de diez años porque el gobierno soviético se apropió inmediatamente de todos los derechos. "
            "Nintendo compró la licencia para Game Boy en mil novecientos ochenta y nueve y Tetris se convirtió en el juego de lanzamiento que convirtió la Game Boy en un fenómeno global. "
            "Pajitnov no vio ni un centavo de los quinientos millones de dólares que generó Tetris hasta mil novecientos noventa y seis cuando recuperó sus derechos al colapsar la Unión Soviética. "
            "Hoy Tetris es el videojuego más vendido y jugado de toda la historia de la humanidad con más de quinientos millones de copias. "
            "¿Sabías que el hombre que creó el juego más famoso del mundo no vio dinero por más de diez años?"
        ),
        "caption": (
            "El creador de Tetris no vio un centavo durante 10 años por culpa del gobierno soviético. 🧩🇷🇺 "
            "¿Sigues jugando Tetris hoy en día? "
            "#Tetris #GameBoy #Nintendo #Retro #Videojuegos #Gaming #Historia #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 classic Tetris falling tetrominoes in vibrant neon colors — L-piece red, S-piece blue, square yellow, T-piece purple — against dark grid background, retro arcade aesthetic with CRT glow 4k",
            "Vertical 9:16 atmospheric Cold War era Soviet research laboratory interior with an old green-screen computer terminal displaying Tetris blocks, dim fluorescent lighting, vintage USSR scientific equipment 4k",
            "Vertical 9:16 iconic original Game Boy handheld console with Tetris cartridge, playing on a classic gray screen with game grid visible, retro nostalgic toy lighting, 1989 aesthetic 4k",
        ],
    },
    {
        "id": "gaming_dark_souls_difficulty",
        "theme_id": "gaming_darksouls",
        "game": "Dark Souls",
        "topic": "Por qué Dark Souls fue diseñado para hacerte sentir estúpido y luego invencible",
        "title": "🔥 La filosofía brutal de Dark Souls que cambió los videojuegos para siempre #Shorts",
        "script": (
            "Hidetaka Miyazaki, el director de Dark Souls, diseñó el juego bajo una filosofía que ningún otro desarrollador se había atrevido a aplicar: la dificultad no es un obstáculo, es el mensaje. "
            "Miyazaki confesó que de joven era pobre y no podía comprar todos los libros de fantasía que quería, así que leía novelas prestadas llenas de páginas faltantes y completaba los huecos con su imaginación. "
            "Esa experiencia de incertidumbre y descubrimiento personal se convirtió en el ADN de Dark Souls: el juego nunca te explica nada, nunca te guía, y nunca se disculpa por matarte. "
            "Pero cuando finalmente derrotas un jefe que te mató cien veces, la recompensa emocional es tan intensa que supera cualquier satisfacción que un videojuego fácil pueda darte. "
            "Dark Souls demostró que los jugadores no quieren que los lleven de la mano. Quieren ganarse cada victoria. "
            "¿Cuál fue el jefe que más te costó superar en Dark Souls?"
        ),
        "caption": (
            "Dark Souls no es difícil por capricho — tiene una filosofía profunda detrás. 🔥⚔️ "
            "¿Cuántas veces moriste en tu primer jefe? "
            "#DarkSouls #FromSoftware #Miyazaki #Gaming #Videojuegos #Dificultad #Gamer #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 atmospheric dark fantasy Lordran landscape, bonfire burning in ancient stone ruins at night surrounded by fog, lone undead warrior knight resting by the flames, souls game aesthetic 4k",
            "Vertical 9:16 dramatic boss fight scene in Dark Souls, enormous armored dragon boss Seathe the Scaleless looming over tiny warrior in cathedral chamber, volumetric blue magical light 4k",
            "Vertical 9:16 iconic YOU DIED red text message over dark fallen warrior on stone floor, dark medieval dungeon environment, souls game death screen aesthetic, moody atmospheric lighting 4k",
        ],
    },
    {
        "id": "gaming_counter_strike_map_design",
        "theme_id": "gaming_csgo",
        "game": "Counter-Strike",
        "topic": "Por qué el mapa Dust 2 es matemáticamente perfecto",
        "title": "🎯 Dust 2 lleva 25 años siendo el mapa perfecto y esto es por qué #Shorts",
        "script": (
            "Dust dos de Counter-Strike es el mapa más jugado en la historia de los videojuegos competitivos y fue diseñado por un estudiante universitario llamado Dave Johnston en solo tres semanas en el año dos mil uno. "
            "Lo extraordinario es que Dust dos logró el equilibrio de diseño que los diseñadores profesionales buscan durante años: cada ángulo tiene un contraángulo, cada posición tiene exactamente dos salidas, y el tiempo que tarda un terrorista en llegar al punto A es matemáticamente igual al que tarda un antiterrorista en defenderlo. "
            "Johnston lo diseñó en su tiempo libre y lo publicó como mapa gratuito para la comunidad. Nunca imaginó que veinticinco años después seguiría siendo el mapa número uno del juego más competitivo del mundo. "
            "Valve intentó reemplazarlo con Dust dos remasterizado en dos mil doce y los jugadores profesionales obligaron a Valve a mantenerlo casi idéntico. "
            "¿Cuántas horas jugaste Dust dos en tu vida?"
        ),
        "caption": (
            "Dust 2 fue diseñado por un estudiante en 3 semanas y lleva 25 años siendo perfecto. 🎯💣 "
            "¿Recuerdas tu primera partida en Dust 2? "
            "#CounterStrike #CSGO #Dust2 #FPS #Gaming #Videojuegos #Competitive #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 dramatic Counter-Strike Dust 2 map iconic catwalk long A site perspective, sandy Middle Eastern architecture, tactical overhead line-of-sight indicators, competitive FPS game screenshot 4k",
            "Vertical 9:16 cinematic close-up of a Counter-Strike player in full tactical gear holding an AK-47, aiming through a narrow doorway in a desert map environment, tense competitive shooter atmosphere 4k",
            "Vertical 9:16 bird's eye view architectural blueprint overlay of Dust 2 map showing symmetrical angles and pathways highlighted in neon lines, game design theory visualization on dark background 4k",
        ],
    },
    {
        "id": "gaming_fortnite_cultural_impact",
        "theme_id": "gaming_fortnite",
        "game": "Fortnite",
        "topic": "Cómo Fortnite cambió la cultura pop y la música en solo 2 años",
        "title": "🕺 Cómo Fortnite destruyó y reconstruyó la cultura pop mundial #Shorts",
        "script": (
            "En dos mil diecisiete, Fortnite era un juego fallido de zombis que nadie jugaba y Epic Games estaba a punto de cancelarlo. "
            "Entonces Epic añadió el modo Battle Royale gratis en solo dos meses, copiando directamente el éxito de PUBG, y en seis meses tenía cien millones de jugadores. "
            "Lo que nadie predijo es el impacto cultural: artistas como Travis Scott, Ariana Grande y Marshmello dieron conciertos virtuales dentro del juego con cien millones de asistentes simultáneos. "
            "El baile de Fortnite llamado El Floss fue popularizado por el Floss Kid en dos mil dieciséis y Epic lo metió al juego como emote, desencadenando la primera batalla legal global sobre si los bailes pueden tener copyright. "
            "NBA, NFL y marcas de ropa de lujo pagaron millones por tener sus logos en el videojuego. Fortnite no es solo un juego — es una plataforma cultural. "
            "¿Recuerdas cuál fue el primer baile que aprendiste de Fortnite?"
        ),
        "caption": (
            "Fortnite era un fracaso en 2017 y casi lo cancelaron. Hoy es una plataforma cultural global. 🕺🌍 "
            "¿Qué emote era tu favorito? "
            "#Fortnite #EpicGames #BattleRoyale #Gaming #Videojuegos #CulturePop #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 vibrant neon Fortnite Battle Royale island landscape with iconic colorful character skins performing victory dances, tropical cartoon-style environment with storm wall approaching in background 4k",
            "Vertical 9:16 massive virtual concert scene inside Fortnite world with giant DJ avatar on stage, millions of player avatars watching below, spectacular light show and fireworks in game environment 4k",
            "Vertical 9:16 dramatic Fortnite storm circle closing over colorful island map, players gliding with umbrellas and parachutes from Battle Bus, vibrant pop art game aesthetic 4k",
        ],
    },
    {
        "id": "gaming_world_of_warcraft_funeral",
        "theme_id": "gaming_wow",
        "game": "World of Warcraft",
        "topic": "El funeral virtual de World of Warcraft que terminó en masacre",
        "title": "⚔️ El funeral de WoW que terminó en la mayor tragedia virtual de la historia #Shorts",
        "script": (
            "En febrero del dos mil seis, una jugadora de World of Warcraft conocida como Fayejin murió de un derrame cerebral en la vida real mientras jugaba. "
            "Su guild organizó un funeral virtual en el juego, en las orillas del lago Tarren Mill, invitando a toda la comunidad a despedirse con sus personajes sin armas equipadas. "
            "Un guild rival llamado Serenity Now se enteró del evento y organizó un ataque armado masivo al funeral, masacrando a cientos de personajes en duelo mientras grababan todo en video y lo subían a internet. "
            "El video se viralizó inmediatamente generando un debate filosófico enorme: ¿Los actos crueles en mundos virtuales tienen peso moral real? "
            "Blizzard nunca tomó acción contra los atacantes porque técnicamente el ataque ocurrió en una zona PvP donde el combate estaba permitido. "
            "¿Crees que atacar un funeral virtual es cruel aunque sea un videojuego?"
        ),
        "caption": (
            "Un guild atacó y masacró un funeral virtual en WoW y el debate moral sigue hoy. ⚔️💀 "
            "¿Crees que hay crueldad real en actos virtuales? "
            "#WorldOfWarcraft #WoW #Blizzard #MMO #Gaming #Videojuegos #Historia #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 atmospheric World of Warcraft lakeside landscape at dusk, dozens of player characters gathered peacefully at water's edge with candles and banners, somber memorial ceremony in fantasy MMORPG world 4k",
            "Vertical 9:16 dramatic World of Warcraft PvP chaos, armored warriors charging across a hillside with swords and spells flying, explosion of arcane magic and battle cries, epic fantasy MMORPG battle 4k",
            "Vertical 9:16 moody WoW Tarren Mill landscape at sunset with Horde and Alliance symbols floating in misty air, dramatic rolling hills and medieval village backdrop, atmospheric MMORPG world 4k",
        ],
    },
    {
        "id": "gaming_kojima_mgs_fourth_wall",
        "theme_id": "gaming_mgs",
        "game": "Metal Gear Solid",
        "topic": "Cómo Psycho Mantis leyó tu memoria de guardado en 1998",
        "title": "🧠 El jefe de Metal Gear Solid que hackeó tu PlayStation en 1998 #Shorts",
        "script": (
            "En mil novecientos noventa y ocho, Hideo Kojima diseñó el combate más innovador y perturbador de la historia de los videojuegos para Metal Gear Solid en PlayStation. "
            "Cuando llegabas a pelear contra Psycho Mantis, el jefe comenzaba a hablar directamente contigo, el jugador, no con Snake el personaje del juego. "
            "Psycho Mantis leía los datos de tu Memory Card y te decía exactamente qué otros juegos de Konami habías jugado ese mes. Si tenías guardadas partidas de Castlevania o Suikoden, Mantis los nombraba. "
            "Después hacía que tu control vibrara sin tocar pantalla alguna, y para ganarlo tenías que desconectar el mando del puerto uno y conectarlo al puerto dos para que Mantis no pudiera leer tus inputs. "
            "Kojima rompió la cuarta pared treinta años antes de que se pusiera de moda. "
            "¿Recuerdas el momento exacto en que Psycho Mantis te nombró tus otros juegos?"
        ),
        "caption": (
            "Psycho Mantis de Metal Gear Solid leía tu Memory Card en tiempo real en 1998. 🧠🎮 "
            "¿Recuerdas cuáles juegos te nombró? "
            "#MetalGearSolid #Kojima #PlayStation #Konami #Gaming #Videojuegos #Historia #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 dramatic Metal Gear Solid boss chamber interior, Psycho Mantis floating in mid-air wearing a black gas mask and black bodysuit with psychic energy aura surrounding him, dark industrial base interior 4k",
            "Vertical 9:16 dramatic PlayStation controller DualShock plugged into controller port 2 on a PS1 console, with on-screen text showing 'HIDEO' codec message, retro gaming setup with TV static glow 4k",
            "Vertical 9:16 cinematic Solid Snake in stealth camouflage sneaking through a Konami military facility corridor, air vents and security cameras overhead, Metal Gear Solid aesthetic 4k",
        ],
    },
    {
        "id": "gaming_among_us_pandemic",
        "theme_id": "gaming_amongus",
        "game": "Among Us",
        "topic": "Cómo un juego de 2018 que nadie jugó se convirtió en el juego del año 2020",
        "title": "🔴 Among Us tenía 30 jugadores activos antes de la pandemia — luego explotó #Shorts",
        "script": (
            "Among Us fue lanzado en junio del dos mil dieciocho por tres desarrolladores del estudio independiente InnerSloth y durante dos años completos el juego tuvo en promedio treinta jugadores activos al día. "
            "InnerSloth estaba a punto de cerrar el servidor definitivamente en marzo del dos mil veinte cuando llegó la pandemia mundial y los confinamientos masivos. "
            "En agosto del dos mil veinte, dos streamers de Twitch llamados Sodapoppin y xQc empezaron a jugarlo en directo y de la noche a la mañana el juego pasó de treinta jugadores a quinientos millones de jugadores activos en un mes. "
            "El equipo completo de InnerSloth era solo cuatro personas y no tenían servidores para soportar ese volumen. El juego caía constantemente y tuvieron que contratar servidores de emergencia en cuarenta y ocho horas. "
            "Among Us ganó el premio al Juego del Año dos mil veinte, dos años después de que nadie lo jugara. "
            "¿Recuerdas la primera vez que alguien te acusó de ser el impostor?"
        ),
        "caption": (
            "Among Us tenía 30 jugadores activos antes de la pandemia — 2 años después ganó el GOTY. 🔴🌍 "
            "¿Recuerdas quién te enseñó a jugar Among Us? "
            "#AmongUs #InnerSloth #Gaming #Pandemia #Videojuegos #Viral #Twitch #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 vibrant cartoon spaceship interior from Among Us, colorful bean-shaped crewmates in different colored spacesuits doing tasks in cafeteria, one impostor lurking in shadows with glowing red eyes 4k",
            "Vertical 9:16 dramatic Among Us emergency meeting scene top-down view, all colored crewmates gathered around the meeting table with chat bubbles flying, accusation chaos, neon cartoon game aesthetic 4k",
            "Vertical 9:16 atmospheric Among Us space station exterior with planet Earth visible through glass window, lone red impostor crewmate standing alone in dark vents corridor, suspense atmosphere 4k",
        ],
    },
    {
        "id": "gaming_no_mans_sky_redemption",
        "theme_id": "gaming_nomanssky",
        "game": "No Man's Sky",
        "topic": "El fracaso más épico de los videojuegos que se convirtió en un milagro",
        "title": "🚀 No Man's Sky: del mayor fracaso gaming al mayor comeback de la historia #Shorts",
        "script": (
            "En agosto del dos mil dieciséis, No Man's Sky fue lanzado como el juego más esperado de la década y en menos de cuarenta y ocho horas se convirtió en el mayor fraude de la historia de los videojuegos. "
            "Las características prometidas en trailers: multijugador, economía galáctica, facciones vivas, planetas con fauna dinámica — nada de eso estaba en el juego. "
            "El director Sean Murray y Hello Games recibieron amenazas de muerte masivas. La empresa tenía dieciséis empleados y se quedaron completamente en silencio durante meses. "
            "Pero en lugar de cerrar, Hello Games pasó los siguientes cuatro años añadiendo silenciosamente todo lo prometido: multijugador, base building, misiones narrativas, nave espacial modificable — todo gratuito. "
            "En dos mil diecinueve, No Man's Sky fue nombrado el mejor juego del año por la comunidad que antes pedía su cancelación. "
            "¿Crees que Hello Games merece el perdón o el olvido?"
        ),
        "caption": (
            "No Man's Sky pasó del mayor fraude gaming al mayor comeback — todo con actualizaciones gratuitas. 🚀🌌 "
            "¿Le diste otra oportunidad después del lanzamiento? "
            "#NoMansSky #HelloGames #Gaming #Redención #Videojuegos #Espacio #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 breathtaking alien planet landscape from No Man's Sky, vibrant purple and orange sky with twin suns setting, exotic bioluminescent alien flora, distant floating rock formations, stunning procedural generation 4k",
            "Vertical 9:16 deep space exploration scene in No Man's Sky, player spaceship traveling through a colorful nebula galaxy with hundreds of stars, beautiful cosmic atmosphere, sci-fi space adventure 4k",
            "Vertical 9:16 alien ocean planet surface in No Man's Sky, turquoise waves under three moons in night sky, exotic sea creatures visible in shallow neon-lit water, atmospheric alien world 4k",
        ],
    },
    {
        "id": "gaming_last_of_us_clicker_science",
        "theme_id": "gaming_lastofus",
        "game": "The Last of Us",
        "topic": "El hongo real que inspiró los infectados de The Last of Us",
        "title": "🍄 El hongo real que convierte hormigas en zombis y que inspiró The Last of Us #Shorts",
        "script": (
            "The Last of Us de Naughty Dog no inventó el hongo que convierte seres vivos en zombis: ese hongo existe en la naturaleza y se llama Ophiocordyceps unilateralis. "
            "Este hongo parasita el cerebro de hormigas carpinteras en la selva tropical. Penetra por el exoesqueleto, invade el sistema nervioso y toma control total del comportamiento del animal. "
            "El hongo obliga a la hormiga a subir exactamente veinte centímetros de altura en la vegetación, que es la temperatura y humedad óptima para la reproducción del hongo. "
            "Cuando la hormiga llega a la posición exacta, el hongo hace que se muerda con la mandíbula a la hoja y la mata. Después el hongo brota del cadáver y libera esporas que infectan otras hormigas. "
            "Neil Druckmann, el director de The Last of Us, vio un documental de la BBC sobre este hongo y en dos horas diseñó el concepto completo del juego. "
            "¿Sabías que los Clickers de The Last of Us están basados en un hongo completamente real?"
        ),
        "caption": (
            "El hongo que convierte a las hormigas en zombis es completamente real y se llama Ophiocordyceps. 🍄😱 "
            "¿Sabías que The Last of Us está basado en ciencia real? "
            "#TheLastOfUs #NaughtyDog #Zombis #Ciencia #Gaming #Videojuegos #Horror #Shorts #Reels"
        ),
        "scene_prompts": [
            "Vertical 9:16 dramatic macro photography of real Ophiocordyceps unilateralis fungus erupting from an ant's head in a tropical rainforest, bioluminescent spores floating in humid jungle air, terrifying natural phenomenon 4k",
            "Vertical 9:16 atmospheric The Last of Us post-apocalyptic overgrown city street, broken skyscrapers covered in vines and moss, Clicker infected zombie with fungal growths on head standing in ruins, horror game aesthetic 4k",
            "Vertical 9:16 cinematic foggy abandoned underground tunnel from The Last of Us, broken fluorescent lights flickering, Joel and Ellie silhouettes navigating through infected zone, survival horror atmosphere 4k",
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
