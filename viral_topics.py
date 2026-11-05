"""
Catálogo de Guiones Virales de Alta Retención (Estilo @finanz_ia, @nagumonetiza, @mixidev_esp).
Directos, intrigantes, con datos reales y ganchos de conversión masiva.
"""

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
]


def get_viral_story_by_id_or_random(story_id: str = "") -> Dict[str, Any]:
    if story_id:
        for s in VIRAL_STORIES:
            if s["id"] == story_id:
                return s
    return VIRAL_STORIES[0]
