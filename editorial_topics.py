"""
Catálogo Maestro de Temas Virales: "CÓMO FUNCIONA EL MUNDO QUE EL 99% DESCONOCE"
Pilar Central de Bruno Schiller: Misterios, Tecnología, Psicología y Secretos Ocultos.
Cero repetición de temas, cero imágenes recicladas, 100% retención algorítmica.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from config import OUTPUT_DIR

VIRAL_EXPLAINER_TOPICS: List[Dict[str, Any]] = [
    {
        "id": "incognito_mode_reality",
        "topic": "Cómo funciona realmente el Modo Incógnito y por qué no te hace invisible",
        "hook_title": "Borr[a] el mito. No sos invisible.",
        "highlight_word": "invisible.",
        "struck_items": ["Borr[a] 'nadie me ve'.", "Borr[a] 'borra mi rastro'.", "Borr[a] 'navego seguro'."],
        "winner_item": "La verdad del Incógnito.",
        "step_headline": "Lo que sí hace tu navegador.",
        "step_highlight": "tu navegador.",
        "subhead_1": "Solo borra historial en tu pantalla local.",
        "subhead_2": "Tu proveedor y Google ven todo.",
        "steps": [
            ("PASO 1", "Tu Router", "registra cada web"),
            ("PASO 2", "Tu ISP", "guarda tu IP y DNS"),
            ("PASO 3", "Las Webs", "te rastrean por cookies"),
        ],
        "terminal_headline": "Registro de red en vivo.",
        "terminal_highlight": "en vivo.",
        "terminal_prompt": "sudo netstat -an | grep 443 --monitorear paquetes salientes en modo incognito",
        "terminal_response": "Tráfico detectado: IP de origen 192.168.1.5 enviando peticiones abiertas a servidores DNS de tu compañía telefónica.",
        "features_headline": "Quién sí te está viendo.",
        "features_highlight": "te está viendo.",
        "features": [
            ("🌐", "Tu proveedor WiFi"),
            ("🏢", "La red de tu trabajo"),
            ("📱", "Tu operador móvil"),
            ("🎯", "Google y Meta Ads"),
            ("🕵️", "Páginas que visitas"),
            ("🛡️", "Solo una VPN te tapa"),
        ],
        "cta_word": "PRIVACIDAD",
        "cta_promise": "Si querés navegar 100% anónimo sin que nadie vea tu tráfico, comentá PRIVACIDAD y te paso la configuración correcta.",
        "narration_script": (
            "El noventa y cinco por ciento de las personas cree que abrir una pestaña en Modo Incógnito las hace invisibles en internet. "
            "La cruda realidad es que el modo incógnito solo evita que alguien que use tu misma computadora vea tu historial local. "
            "Tu proveedor de internet, la red WiFi de tu trabajo y las páginas que visitas siguen viendo exactamente a qué hora entraste y qué hiciste. "
            "Si querés blindar tu conexión real, comentá PRIVACIDAD y te paso el método que sí funciona."
        ),
        "caption": (
            "¿Creías que el Modo Incógnito te hacía invisible? La verdad que las empresas de tecnología no te dicen. "
            "Comentá PRIVACIDAD y te mando la guía para blindar tu navegación real. "
            "#Curiosidades #Tecnologia #ComoFunciona #Privacidad #Ciberseguridad #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "tiktok_algorithm_mindreader",
        "topic": "Cómo funciona el algoritmo de TikTok para saber qué te gusta antes de que lo busques",
        "hook_title": "Borr[a] la casualidad. Lee tu mente.",
        "highlight_word": "tu mente.",
        "struck_items": ["Borr[a] 'es coincidencia'.", "Borr[a] 'me escucha el micro'.", "Borr[a] 'es magia'."],
        "winner_item": "El algoritmo predictivo.",
        "step_headline": "Mide milisegundos de tu dedo.",
        "step_highlight": "de tu dedo.",
        "subhead_1": "Cada pausa en la pantalla es un dato.",
        "subhead_2": "Crea tu perfil psicológico en 40 minutos.",
        "steps": [
            ("PASO 1", "El Scroll", "mide la velocidad"),
            ("PASO 2", "La Retención", "registra re-visitas"),
            ("PASO 3", "El Grafo", "te agrupa por gustos"),
        ],
        "terminal_headline": "Telemetría de retención.",
        "terminal_highlight": "de retención.",
        "terminal_prompt": "analizar_usuario --metricas [watch_time: 1.25, swipe_speed: -42ms, loop_count: 2]",
        "terminal_response": "Patrón confirmado: Interés del 98% en misterios y tecnología. Inyectando 4 videos similares en su feed.",
        "features_headline": "Las 6 señales que rastrea.",
        "features_highlight": "que rastrea.",
        "features": [
            ("⏱️", "Segundos por video"),
            ("🔁", "Veces que repites"),
            ("💬", "Si abres comentarios"),
            ("🔊", "Si subes el volumen"),
            ("📤", "Si tocas compartir"),
            ("👤", "Si visitas el perfil"),
        ],
        "cta_word": "ALGORITMO",
        "cta_promise": "Comentá ALGORITMO y te paso el truco para reiniciar tu feed y hacer que te recomiende solo contenido de alto valor.",
        "narration_script": (
            "¿Alguna vez sentiste que TikTok te lee los pensamientos? No necesita escuchar tu micrófono. "
            "El algoritmo mide los milisegundos exactos que tu dedo se detiene en cada video, cuántas veces repites una escena y si abres los comentarios. "
            "En menos de cuarenta minutos de uso, sabe tus inseguridades, tus obsesiones y lo que te da risa mejor que tus propios amigos. "
            "Comentá ALGORITMO y te enseño cómo resetearlo."
        ),
        "caption": (
            "El algoritmo no es magia ni te escucha el micrófono: es pura psicología y milisegundos de retención. "
            "Comentá ALGORITMO y te paso el método para resetearlo desde cero. "
            "#TikTokHacks #Psicologia #ComoFunciona #Tecnologia #Secretos #Viral #Shorts"
        ),
    },
    {
        "id": "airplane_single_engine",
        "topic": "Qué pasa realmente en un avión comercial si se le apaga un motor en pleno vuelo",
        "hook_title": "Borr[a] el pánico. Puede volar con uno.",
        "highlight_word": "con uno.",
        "struck_items": ["Borr[a] 'cae en picada'.", "Borr[a] 'se apaga todo'.", "Borr[a] 'es el final'."],
        "winner_item": "Certificación ETOPS.",
        "step_headline": "Diseñados para resistir.",
        "step_highlight": "para resistir.",
        "subhead_1": "Un solo motor puede mantener el vuelo 5 horas.",
        "subhead_2": "Los pilotos entrenan esto cada 6 meses.",
        "steps": [
            ("PASO 1", "El Timón", "compensa el giro"),
            ("PASO 2", "Potencia", "sube al 100% empuje"),
            ("PASO 3", "Desvío", "aterrizaje de manual"),
        ],
        "terminal_headline": "Protocolo de emergencia.",
        "terminal_highlight": "de emergencia.",
        "terminal_prompt": "ENG 1 FAIL -> Autothrottle MCT -> Rudder Trim 8.5 deg Left -> Descend to FL240",
        "terminal_response": "Vuelo estabilizado con motor derecho a 24,000 pies. Rumbo fijado al aeropuerto alterno más cercano (45 minutos).",
        "features_headline": "La ingeniería que te salva.",
        "features_highlight": "que te salva.",
        "features": [
            ("✈️", "Vuelo en crucero"),
            ("⏱️", "Hasta 330 min con uno"),
            ("🛬", "Planeo sin motores"),
            ("👨‍✈️", "Simulador semestral"),
            ("⚙️", "Sistemas triplicados"),
            ("🛡️", "El transporte más seguro"),
        ],
        "cta_word": "AVION",
        "cta_promise": "Comentá AVION y te paso el mapa de qué aerolíneas tienen las rutas más seguras del mundo.",
        "narration_script": (
            "La mayoría de las personas cree que si a un avión comercial se le apaga una turbina en pleno vuelo sobre el océano, el avión cae en picada. "
            "La realidad es que todos los aviones de pasajeros modernos están certificados con la norma E-TOPS. "
            "Un solo motor tiene suficiente potencia para despegar, volar durante más de cuatro horas y aterrizar suavemente en tierra firme. "
            "De hecho, si se apagaran ambos motores, un avión puede planear más de cien kilómetros sin combustible. "
            "Comentá AVION si alguna vez tuviste miedo de volar."
        ),
        "caption": (
            "Lo que las aerolíneas no te explican de cómo funcionan los motores de un avión comercial. "
            "¿Le tienes miedo a volar o eres de los que duerme todo el vuelo? ¡Comentá AVION y te leo en los comentarios! "
            "#Aviacion #Ciencia #ComoFunciona #Misterios #Supervivencia #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "supermarket_psychology_tricks",
        "topic": "Por qué el pan y la leche siempre están al fondo del supermercado",
        "hook_title": "Borr[a] la casualidad. Todo está pensado.",
        "highlight_word": "está pensado.",
        "struck_items": ["Borr[a] 'es por logística'.", "Borr[a] 'es casualidad'.", "Borr[a] 'entro y salgo'."],
        "winner_item": "Neuromarketing visual.",
        "step_headline": "El laberinto diseñado para gastar.",
        "step_highlight": "para gastar.",
        "subhead_1": "Te obligan a recorrer todos los pasillos.",
        "subhead_2": "Gastás 40% más de lo planeado.",
        "steps": [
            ("PASO 1", "La Entrada", "frutas y panadería"),
            ("PASO 2", "El Fondo", "leche, huevos y carne"),
            ("PASO 3", "La Caja", "chicles y antojos"),
        ],
        "terminal_headline": "Psicología de consumo.",
        "terminal_highlight": "de consumo.",
        "terminal_prompt": "calcular_impacto_recorrido --producto_basico: fondo_tienda --tiempo_estancia: +18_minutos",
        "terminal_response": "Resultado: 3.4 productos no planificados agregados al carrito antes de llegar al refrigerador de lácteos.",
        "features_headline": "Los 6 trucos invisibles.",
        "features_highlight": "invisibles.",
        "features": [
            ("🛒", "Carritos cada vez más grandes"),
            ("🎵", "Música lenta para que no apures"),
            ("🍞", "Olor a pan para abrir apetito"),
            ("👁️", "Marcas caras a la altura de ojos"),
            ("🧱", "Pisos lisos para deslizar fácil"),
            ("🍫", "Golosinas en la fila de espera"),
        ],
        "cta_word": "TRUCO",
        "cta_promise": "Comentá TRUCO y te paso los 5 hábitos de compradores inteligentes para ahorrarte 30% en cada visita.",
        "narration_script": (
            "¿Alguna vez fuiste al supermercado solo por un litro de leche y terminaste saliendo con una bolsa llena de cosas que no necesitabas? "
            "No es culpa de tu autocontrol. Los supermercados están diseñados por arquitectos del comportamiento. "
            "Ponen el pan, la leche y los huevos al fondo para obligarte a caminar por pasillos llenos de ofertas tentadoras, mientras usan música de tempo lento para que camines más despacio. "
            "Comentá TRUCO y te paso cómo vencer este sistema en tu próxima compra."
        ),
        "caption": (
            "Los supermercados no tienen ni una sola góndola puesta por casualidad. Así hackean tu mente para que compres de más. "
            "¿Cuántas veces fuiste por leche y saliste con medio carrito lleno? ¡Comentá TRUCO y te paso la guía de ahorro! "
            "#Psicologia #Finanzas #Curiosidades #ComoFunciona #Neuromarketing #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "battery_1_percent_secret",
        "topic": "Qué pasa realmente dentro de tu celular cuando marca 1 por ciento de batería",
        "hook_title": "Borr[a] el número. Es una mentira piadosa.",
        "highlight_word": "mentira piadosa.",
        "struck_items": ["Borr[a] 'le queda 1% exacto'.", "Borr[a] 'se gasta parejo'.", "Borr[a] 'lo cargo al 100%'."],
        "winner_item": "El buffer de seguridad.",
        "step_headline": "Tu batería jamás se vacía a cero.",
        "step_highlight": "a cero.",
        "subhead_1": "Si llegara a 0% real, la química moriría.",
        "subhead_2": "El sistema se apaga para salvar el litio.",
        "steps": [
            ("PASO 1", "Voltaje Cae", "el chip BMS detecta baja"),
            ("PASO 2", "Corte Seguro", "apaga la pantalla"),
            ("PASO 3", "Reserva", "mantiene reloj y arranque"),
        ],
        "terminal_headline": "Lectura BMS de litio.",
        "terminal_highlight": "BMS de litio.",
        "terminal_prompt": "cat /sys/class/power_supply/battery/voltage_now -> umbral_minimo: 3.2V",
        "terminal_response": "Corte preventivo ejecutado a 3.25V. Reserva química del 5% intacta para evitar cristalización de ánodo de litio.",
        "features_headline": "Cómo duplicar su vida útil.",
        "features_highlight": "su vida útil.",
        "features": [
            ("🔋", "Nunca dejes que muera a 0%"),
            ("⚡", "Carga óptima: 20% a 80%"),
            ("🌡️", "El calor degrada el litio"),
            ("🔌", "Carga rápida calienta más"),
            ("🌙", "Desconéctalo al amanecer"),
            ("📱", "Tu batería durará 4 años"),
        ],
        "cta_word": "BATERIA",
        "cta_promise": "Comentá BATERIA y te paso los 3 ajustes ocultos de Android y iPhone que duplican la duración de tu carga diaria.",
        "narration_script": (
            "¿Por qué tu teléfono parece aguantar media hora entera en el uno por ciento de batería, pero cae del cien al noventa en cuestión de minutos? "
            "El porcentaje que ves en pantalla no es una medida exacta de energía, sino una estimación matemática del chip de control. "
            "Tu teléfono en realidad nunca deja que la batería se vacíe al cero por ciento real, porque si los iones de litio caen por debajo de cierto voltaje, la batería se daña químicamente y nunca más volvería a encender. "
            "Comentá BATERIA y te paso cómo cuidar tu celular para que dure años como nuevo."
        ),
        "caption": (
            "El 1% de batería de tu teléfono es en realidad un seguro de vida químico. Descubre cómo funciona por dentro. "
            "Comentá BATERIA y te paso los 3 ajustes ocultos para que tu carga rinda el doble. "
            "#Bateria #Tecnologia #Smartphone #iPhone #Android #ComoFunciona #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "submarine_cables_internet",
        "topic": "Por qué la 'nube' de internet no está en el cielo sino bajo el fondo del océano",
        "hook_title": "Borr[a] el cielo. El internet está bajo el agua.",
        "highlight_word": "bajo el agua.",
        "struck_items": ["Borr[a] 'funciona por satélite'.", "Borr[a] 'está en las nubes'.", "Borr[a] 'es inalámbrico'."],
        "winner_item": "1.4 millones de km de cables.",
        "step_headline": "Cables de fibra en el abismo.",
        "step_highlight": "en el abismo.",
        "subhead_1": "El 99% del tráfico mundial va por el mar.",
        "subhead_2": "Cruzan fosas a 8,000 metros de profundidad.",
        "steps": [
            ("PASO 1", "Fibra Óptica", "hilos de vidrio puro"),
            ("PASO 2", "Repetidores", "amplifican la luz láser"),
            ("PASO 3", "Llegada a Costa", "se conectan a servidores"),
        ],
        "terminal_headline": "Rastreo de ruta transatlántica.",
        "terminal_highlight": "transatlántica.",
        "terminal_prompt": "traceroute 8.8.8.8 --mostrar puntos de salto interoceánicos",
        "terminal_response": "Salto 4: Estación de Amarre Fortaleza (Brasil) -> Cable EllaLink -> Salto 5: Estación Sines (Portugal) en 58 milisegundos a la velocidad de la luz.",
        "features_headline": "Los secretos bajo el mar.",
        "features_highlight": "bajo el mar.",
        "features": [
            ("🌊", "Grosor como manguera de jardín"),
            ("🦈", "Blindados contra tiburones"),
            ("⚡", "Impulsados por rayos láser"),
            ("🚢", "Barcos especiales los reparan"),
            ("🌐", "Cruzan todos los continentes"),
            ("🔒", "El punto más crítico del mundo"),
        ],
        "cta_word": "INTERNET",
        "cta_promise": "Comentá INTERNET y te paso el mapa interactivo en 3D de todos los cables que conectan el planeta ahora mismo.",
        "narration_script": (
            "Cuando la gente habla de guardar fotos en la nube o enviar un mensaje al otro lado del planeta, imagina que sus datos viajan al espacio por satélite. "
            "La realidad es fascinante: más del noventa y nueve por ciento de todo el internet del mundo viaja a través de cables submarinos del grosor de una manguera de jardín, descansando en el lecho marino a miles de metros bajo el océano. "
            "Si esos cables se cortaran, el mundo se quedaría desconectado en segundos. "
            "Comentá INTERNET y te paso el mapa interactivo completo."
        ),
        "caption": (
            "La nube no existe en el cielo: son millones de kilómetros de cables de fibra óptica bajo el fondo del mar. "
            "Comentá INTERNET y te paso el mapa interactivo para que veas por dónde viajan tus datos. "
            "#Internet #Ciencia #Oceano #ComoFunciona #Misterios #Tecnologia #BrunoSchiller #Shorts"
        ),
    },
]


def get_next_editorial_topic() -> Dict[str, Any]:
    """
    Selecciona el siguiente tema viral garantizando rotación estricta
    sin repetir jamás ningún tema reciente (rastreado en editorial_history.json).
    """
    history_file = OUTPUT_DIR / "editorial_history.json"
    used_ids: List[str] = []

    if history_file.exists():
        try:
            used_ids = json.loads(history_file.read_text(encoding="utf-8"))
        except Exception:
            used_ids = []

    # Filtrar temas que no se hayan usado recientemente
    available = [t for t in VIRAL_EXPLAINER_TOPICS if t["id"] not in used_ids[-len(VIRAL_EXPLAINER_TOPICS)+1:]]
    if not available:
        available = VIRAL_EXPLAINER_TOPICS

    chosen = available[0]

    # Guardar en historial
    used_ids.append(chosen["id"])
    history_file.write_text(json.dumps(used_ids[-100:], ensure_ascii=False, indent=2), encoding="utf-8")

    return chosen
