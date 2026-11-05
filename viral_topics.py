"""
Catálogo de Guiones Virales de Alta Retención (Estilo @finanz_ia, @nagumonetiza, @mixidev_esp).
Directos, intrigantes, con datos reales y ganchos de conversión masiva.
Incluye rotación inteligente sin repeticiones para Bruno Schiller.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

VIRAL_STORIES: List[Dict[str, Any]] = [
    {
        "id": "amazon_returns",
        "theme_id": "amazon_returns",
        "topic": "El negocio oculto de las devoluciones de Amazon",
        "title": "📦 El negocio sucio de las devoluciones de Amazon que casi nadie conoce #Shorts",
        "script": (
            "¿Sabías que Amazon prefiere tirar millones de productos nuevos a la basura antes que volver a guardarlos en sus almacenes? "
            "Por pura logística, revisar y reempaquetar una devolución les cuesta más caro que el producto mismo. "
            "Por eso, subastan palets enteros llenos de computadoras, audífonos y ropa de marca por una fracción ridícula de su precio real. "
            "Cientos de revendedores compran estos lotes cerrados y ganan miles de dólares vendiendo todo por separado. "
            "Comentá AMAZON y te paso la página oficial donde se consiguen."
        ),
        "caption": (
            "Amazon prefiere liquidar palets de devoluciones por una fracción de su valor antes que reabastecerlos. "
            "¿Comprarías un lote a ciegas para revenderlo? Comentá AMAZON y te paso la plataforma oficial. "
            "#Finanzas #Negocios #Amazon #Trucos #ComoFunciona #Dinero #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "taipei_damper",
        "theme_id": "taipei_damper",
        "topic": "La bola de 660 toneladas suspendida en el cielo",
        "title": "🏗️ La bola de 660 toneladas suspendida en el cielo que desafía terremotos #Shorts",
        "script": (
            "En el piso ochenta y siete del rascacielos Taipei 101 cuelga una masa dorada de seiscientas sesenta toneladas suspendida de gruesos cables de acero. "
            "No es una escultura moderna: es un amortiguador de masa sincronizada que salva a miles de personas. "
            "Cuando un tifón azota el rascacielos con vientos huracanados o la tierra tiembla por un terremoto, el edificio se balancea, pero la esfera oscila en dirección contraria absorbiendo el cuarenta por ciento de la energía cinética. "
            "Comentá EDIFICIO y te muestro el video en vivo de cómo se movió durante el último gran sismo."
        ),
        "caption": (
            "La esfera dorada de 660 toneladas que cuelga dentro del rascacielos Taipei 101 para evitar que colapse en terremotos. "
            "Comentá EDIFICIO y te paso las grabaciones reales de cómo salva el rascacielos. "
            "#Ingenieria #Arquitectura #Ciencia #ComoFunciona #Misterios #Terremoto #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "flight_cookies",
        "theme_id": "flight_cookies",
        "topic": "La trampa secreta de las aerolíneas con tus cookies",
        "title": "✈️ Por qué te suben el precio del vuelo si lo buscas dos veces #Shorts",
        "script": (
            "Si buscas un vuelo para tus vacaciones y vuelves a entrar tres horas después, casi siempre verás que el pasaje subió de precio de golpe. "
            "No es que se hayan agotado los asientos. Las aerolíneas rastrean tus cookies y tu dirección de internet. "
            "Saben que estás desesperado por viajar y su algoritmo incrementa la tarifa automáticamente para meterte pánico y obligarte a comprar ya. "
            "Comentá VUELO y te paso los tres pasos exactos para congelar la tarifa más baja usando navegación blindada."
        ),
        "caption": (
            "Las aerolíneas rastrean tus búsquedas para subirte la tarifa cuando detectan tu urgencia. "
            "Comentá VUELO y te comparto el método para comprar siempre con la tarifa base real. "
            "#Viajes #Vuelos #Consejos #Trucos #ComoFunciona #Finanzas #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "supermarket_psychology",
        "theme_id": "supermarket_psychology",
        "topic": "La trampa visual de por qué la leche y el pan están al fondo del supermercado",
        "title": "🛒 Por qué el pan y la leche siempre están al fondo del súper #Shorts",
        "script": (
            "¿Alguna vez te diste cuenta de que en cualquier supermercado del planeta la leche, los huevos y el pan siempre están en la esquina más lejana de la entrada? "
            "No es casualidad ni mala suerte de diseño: es un laberinto psicológico estudiado al milímetro. "
            "El noventa por ciento de los clientes entra buscando solo uno de esos productos básicos. "
            "Para llegar hasta ellos, te obligan a recorrer pasillos enteros rodeados de promociones con luces cálidas, música lenta y ofertas señuelo. "
            "Para cuando llegas a la caja, llevas cinco cosas que jamás planeabas comprar. Comentá SUPER y te cuento cómo esquivar sus trampas de compra."
        ),
        "caption": (
            "El diseño de los supermercados no es aleatorio: es una trampa psicológica para que gastes el triple. "
            "Comentá SUPER y te comparto las 4 reglas para comprar solo lo que necesitas. "
            "#Psicologia #Finanzas #Supermercado #Trucos #Ahorro #ComoFunciona #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "hotel_safe_master",
        "theme_id": "hotel_safe_master",
        "topic": "El código maestro de fábrica de las cajas fuertes de hotel",
        "title": "🔐 El código secreto que abre casi cualquier caja fuerte de hotel #Shorts",
        "script": (
            "Cuando te hospedas en un hotel y guardas tu pasaporte o dinero en la caja fuerte de tu habitación, te sientes totalmente protegido al poner tu propia clave de cuatro dígitos. "
            "Pero lo que la mayoría ignora es que muchas cajas fuertes jamás fueron reprogramadas por el personal de mantenimiento. "
            "Siguen teniendo activo el código maestro de fábrica del fabricante: normalmente seis ceros o del uno al seis. "
            "Cualquiera con dos minutos a solas puede introducirlo y anular tu contraseña privada al instante. "
            "Comentá HOTEL y te muestro cómo verificar si la caja de tu habitación está realmente segura en diez segundos."
        ),
        "caption": (
            "Muchas cajas fuertes de hoteles mantienen el código maestro de fábrica por negligencia. "
            "Comentá HOTEL y te paso el método para probar tu caja antes de dejar objetos de valor. "
            "#Seguridad #Hoteles #Viajes #Misterios #Trucos #ComoFunciona #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "battery_1_percent",
        "theme_id": "battery_1_percent",
        "topic": "Por qué tu celular se apaga al 1 por ciento aunque le quede energía",
        "title": "🔋 Por qué tu celular se apaga al 1% cuando aún tiene batería #Shorts",
        "script": (
            "Cuando la pantalla de tu celular se apaga mostrando el uno por ciento de batería, en realidad tu teléfono no está completamente vacío. "
            "Todavía le queda entre un diez y un quince por ciento de energía química real dentro de sus celdas de litio. "
            "El sistema operativo fuerza el apagado de emergencia como un seguro de vida. "
            "Si una batería de litio se descarga a cero absoluto de voltaje, sus compuestos internos se cristalizan para siempre y el teléfono jamás volvería a encender, o peor: podría entrar en corto circuito e incendiarse. "
            "Comentá BATERIA y te paso el secreto para que tu batería dure tres años sin degradarse."
        ),
        "caption": (
            "El apagado al 1% es una protección química vital de las baterías de litio. "
            "Comentá BATERIA y te paso los hábitos comprobados para duplicar la vida útil de tu teléfono. "
            "#Tecnologia #Baterias #Celulares #Ciencia #ComoFunciona #Consejos #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "airplane_bleed_hole",
        "theme_id": "airplane_bleed_hole",
        "topic": "El diminuto agujero en la ventana del avión que te mantiene con vida",
        "title": "✈️ El agujero secreto en la ventana del avión que te salva la vida #Shorts",
        "script": (
            "Si alguna vez miraste de cerca la ventana de un avión comercial a diez mil metros de altura, habrás notado un pequeño agujero diminuto en la parte inferior del vidrio. "
            "No es una falla ni una grieta peligrosa: se llama agujero de purga y es lo que evita que el avión sufra una descompresión explosiva. "
            "Las ventanas de los aviones tienen tres capas acrílicas. "
            "Ese orificio equilibra la presión monstruosa del exterior helado con la cabina presurizada caliente, haciendo que solo el panel externo soporte la fuerza y evitando además que el cristal se empañe de hielo. "
            "Comentá AVION y te cuento los secretos que los pilotos nunca dicen por el megáfono."
        ),
        "caption": (
            "El pequeño orificio en la ventana del avión equilibra presiones extremas para que la cabina no colapse. "
            "Comentá AVION y conoce los misterios aeronáuticos más fascinantes. "
            "#Aviacion #Aviones #Ciencia #Ingenieria #ComoFunciona #Misterios #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "elevator_placebo",
        "theme_id": "elevator_placebo",
        "topic": "El botón de cerrar puertas del ascensor que no sirve para nada",
        "title": "🏢 La mentira del botón de cerrar puertas en los ascensores #Shorts",
        "script": (
            "¿Eres de los que presiona desesperadamente el botón de cerrar puertas en el ascensor pensando que va a acelerar tu viaje? "
            "Lamento desilusionarte, pero en el ochenta por ciento de los ascensores modernos ese botón es un engaño total. "
            "Se llama botón placebo: los ingenieros lo conectan a una luz pero no al mecanismo del motor para darle a los pasajeros una falsa sensación de control y calmar su ansiedad. "
            "Solo los bomberos con una llave física maestra pueden activar su funcionamiento instantáneo. "
            "Comentá ELEVADOR y te paso la combinación oculta de botones que usan los técnicos para viajes directos."
        ),
        "caption": (
            "El botón de cerrar puertas es en la mayoría de casos un placebo psicológico diseñado para reducir la ansiedad. "
            "Comentá ELEVADOR y descubre los códigos ocultos de los sistemas de transporte vertical. "
            "#Psicologia #Ingenieria #Curiosidades #ComoFunciona #Misterios #Elevadores #BrunoSchiller #Shorts"
        ),
    },
]

HISTORY_FILE = Path(__file__).parent / "output" / "viral_history.json"


def get_viral_story_by_id_or_random(story_id: str = "") -> Dict[str, Any]:
    """Selecciona una historia específica o rota de forma inteligente entre historias no publicadas recientemente."""
    if story_id and story_id.strip().lower() != "auto":
        for s in VIRAL_STORIES:
            if s["id"] == story_id.strip():
                return s

    history: List[str] = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            history = []

    # Filtrar historias no usadas recientemente
    recent_set = set(history[-len(VIRAL_STORIES) + 1:] if len(history) >= len(VIRAL_STORIES) else history)
    available = [s for s in VIRAL_STORIES if s["id"] not in recent_set]

    chosen = available[0] if available else VIRAL_STORIES[len(history) % len(VIRAL_STORIES)]

    history.append(chosen["id"])
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history[-50:], ensure_ascii=False, indent=2), encoding="utf-8")

    return chosen
