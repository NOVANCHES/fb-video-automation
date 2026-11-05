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
    {
        "id": "general_anesthesia_mystery",
        "topic": "Qué pasa realmente en tu cerebro bajo anestesia general y por qué no es lo mismo que dormir",
        "hook_title": "Borr[a] el sueño. Es un coma inducido.",
        "highlight_word": "coma inducido.",
        "struck_items": ["Borr[a] 'te quedas dormido'.", "Borr[a] 'descansas la mente'.", "Borr[a] 'sueñas cosas'."],
        "winner_item": "Desconexión de redes neurales.",
        "step_headline": "Apagan la sincronía del cerebro.",
        "step_highlight": "del cerebro.",
        "subhead_1": "Tus neuronas siguen vivas pero incomunicadas.",
        "subhead_2": "El tiempo se borra en cero segundos.",
        "steps": [
            ("PASO 1", "El Cóctel", "hipnótico, analgésico y paralizante"),
            ("PASO 2", "El Bloqueo", "apaga el tálamo central"),
            ("PASO 3", "El Despertar", "reinicia la consciencia"),
        ],
        "terminal_headline": "Monitoreo EEG intraoperatorio.",
        "terminal_highlight": "EEG intraoperatorio.",
        "terminal_prompt": "leer_indice_bisespectral --sensor: BIS_frontal --umbral_deseado: 40_a_60",
        "terminal_response": "Valor BIS actual: 44. Consciencia anulada. Corteza cerebral desconectada del tálamo. Dolor: 0%. Recuerdos: 0%.",
        "features_headline": "La ciencia del anestesiólogo.",
        "features_highlight": "del anestesiólogo.",
        "features": [
            ("🧠", "No hay sueños ni descanso"),
            ("⏱️", "Ocho horas se sienten como un parpadeo"),
            ("🛡️", "El médico más vigilante del quirófano"),
            ("💉", "Dosis calculada por microgramo y peso"),
            ("🫀", "Mantiene tus signos vitales estables"),
            ("🔄", "Reversión milimétrica al despertar"),
        ],
        "cta_word": "CEREBRO",
        "cta_promise": "Comentá CEREBRO y te paso cómo los neurocientíficos usan la anestesia para estudiar el misterio de la consciencia humana.",
        "narration_script": (
            "Cuando te ponen anestesia general para una cirugía, no te estás quedando dormido. "
            "Lo que los médicos hacen en realidad es inducirte un coma farmacológico reversible y controlado. "
            "Los fármacos bloquean las señales entre el tálamo y la corteza cerebral, haciendo que tus neuronas sigan activas pero ya no puedan comunicarse entre sí. "
            "Por eso no sueñas nada y ocho horas de cirugía se sienten exactamente como si hubieras parpadeado un milisegundo. "
            "Comentá CEREBRO si alguna vez te operaron y sentiste esa pérdida total del tiempo."
        ),
        "caption": (
            "La anestesia general no es dormir: es apagar la sincronización de tu cerebro. Descubre el misterio médico. "
            "¿Alguna vez te operaron? Comentá CEREBRO y cuéntame qué sentiste al despertar. "
            "#Medicina #Ciencia #Cerebro #ComoFunciona #Misterios #Salud #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "airplane_curved_routes",
        "topic": "Por qué los aviones vuelan en curvas en el mapa y no en línea recta",
        "hook_title": "Borr[a] la recta. La Tierra es una esfera.",
        "highlight_word": "una esfera.",
        "struck_items": ["Borr[a] 'es para esquivar tormentas'.", "Borr[a] 'la ruta más corta es recta'.", "Borr[a] 'el mapa no miente'."],
        "winner_item": "Círculo Máximo (Geodésica).",
        "step_headline": "El mapa plano distorsiona el mundo.",
        "step_highlight": "distorsiona el mundo.",
        "subhead_1": "En una esfera 3D la curva es el camino más corto.",
        "subhead_2": "Ahorra miles de litros de combustible.",
        "steps": [
            ("PASO 1", "Mercator", "deforma los polos norte y sur"),
            ("PASO 2", "La Esfera", "muestra la verdadera distancia"),
            ("PASO 3", "Vientos Jet", "aprovechan corrientes de aire"),
            ("PASO 3", "Vientos Jet", "aprovechan corrientes de aire"),
        ],
        "terminal_headline": "Cálculo de ruta ortodrómica.",
        "terminal_highlight": "ortodrómica.",
        "terminal_prompt": "calcular_geodesica --origen: MAD --destino: LAX --modelo_tierra: WGS84",
        "terminal_response": "Ruta recta en mapa plano: 10,240 km. Ruta curva polar real: 9,380 km. Ahorro neto: 860 km y 52 minutos de vuelo.",
        "features_headline": "Secretos de la navegación aérea.",
        "features_highlight": "navegación aérea.",
        "features": [
            ("🌐", "La Tierra no es un mapa plano"),
            ("✈️", "Rutas polares hacia Asia"),
            ("💨", "Vientos de cola a 300 km/h"),
            ("⛽", "Ahorran millones en turbosina"),
            ("🛰️", "Guiados por GPS satelital"),
            ("🗺️", "La ilusión de la proyección Mercator"),
        ],
        "cta_word": "VUELO",
        "cta_promise": "Comentá VUELO y te paso la aplicación interactiva para ver cómo se deforman los países en los mapas reales.",
        "narration_script": (
            "Si miras la pantalla de entretenimiento de un avión mientras viajas de Europa a América, parece que el piloto se volvió loco y vuela en una curva enorme hacia el polo norte. "
            "No es un desvío. El mapa plano que todos conocemos distorsiona los continentes. "
            "En una esfera tridimensional, una línea curva sobre el mapa es en realidad la distancia más corta y directa entre dos puntos. "
            "Volar por ahí le ahorra a la aerolínea miles de dólares en combustible y casi una hora de viaje. "
            "Comentá VUELO si pensabas que los aviones volaban en línea recta."
        ),
        "caption": (
            "¿Por qué los aviones hacen curvas gigantes en el mapa? La geometría oculta de los vuelos comerciales. "
            "Comentá VUELO y te comparto el simulador 3D de rutas aéreas en tiempo real. "
            "#Aviacion #Ciencia #Geografia #ComoFunciona #Misterios #Vuelos #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "elevator_close_button",
        "topic": "La verdad del botón de 'Cerrar Puertas' en los elevadores modernos",
        "hook_title": "Borr[a] la prisa. Es un botón placebo.",
        "highlight_word": "botón placebo.",
        "struck_items": ["Borr[a] 'cierra más rápido'.", "Borr[a] 'te ahorra tiempo'.", "Borr[a] 'funciona siempre'."],
        "winner_item": "Psicología del control ilusorio.",
        "step_headline": "Desconectado a propósito.",
        "step_highlight": "a propósito.",
        "subhead_1": "Por leyes de accesibilidad el tiempo está fijo.",
        "subhead_2": "Solo bomberos tienen la llave que lo activa.",
        "steps": [
            ("PASO 1", "La Presión", "aprietas el botón con urgencia"),
            ("PASO 2", "El Temporizador", "el circuito ignora la señal"),
            ("PASO 3", "La Ilusión", "la puerta cierra a los 5 segundos"),
        ],
        "terminal_headline": "Circuito de control PLC.",
        "terminal_highlight": "control PLC.",
        "terminal_prompt": "inspeccionar_entradas_plc --modo: NORMAL --boton: CERRAR_PUERTA",
        "terminal_response": "Estado botón: Pulsado (PIN 14). Modo Bombero: INACTIVO. Acción: Ignorado por temporizador de seguridad de 6.0 segundos.",
        "features_headline": "Otros botones placebo del día a día.",
        "features_highlight": "placebo del día a día.",
        "features": [
            ("🛗", "Cerrar puerta en el elevador"),
            ("🚦", "El botón para cruzar la calle"),
            ("🌡️", "Termostatos falsos en oficinas"),
            ("⏱️", "Barras de carga ficticias en apps"),
            ("🧠", "Diseñados para calmar tu ansiedad"),
            ("🔑", "Solo la llave maestra los activa"),
        ],
        "cta_word": "ELEVADOR",
        "cta_promise": "Comentá ELEVADOR y te paso la lista completa de trucos psicológicos que los ingenieros usan en edificios modernos.",
        "narration_script": (
            "Cada vez que te subes a un elevador con prisa y presionas repetidamente el botón de cerrar puertas, estás cayendo en uno de los trucos psicológicos más comunes del mundo. "
            "En la inmensa mayoría de los edificios construidos después de mil novecientos noventa, ese botón está completamente desactivado. "
            "Las regulaciones de seguridad exigen que las puertas permanezcan abiertas un tiempo fijo para personas con movilidad reducida. "
            "El botón solo existe para darte una sensación de control sobre tu tiempo. "
            "Comentá ELEVADOR si siempre lo presionas."
        ),
        "caption": (
            "El botón de cerrar puertas de los elevadores no hace nada: es un botón placebo para calmar tu ansiedad. "
            "¿Eres de los que lo presiona 5 veces seguidas? ¡Comentá ELEVADOR y te leo! "
            "#Psicologia #Ingenieria #Curiosidades #ComoFunciona #Secretos #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "noise_cancelling_physics",
        "topic": "Cómo funcionan los audífonos con cancelación de ruido activa",
        "hook_title": "Borr[a] el silencio. Crean sonido destructor.",
        "highlight_word": "sonido destructor.",
        "struck_items": ["Borr[a] 'bloquean físicamente'.", "Borr[a] 'absorben el sonido'.", "Borr[a] 'es una almohadilla'."],
        "winner_item": "Interferencia destructiva de ondas.",
        "step_headline": "Disparan una onda espejo a tu oído.",
        "step_highlight": "espejo a tu oído.",
        "subhead_1": "Un micro exterior escucha el ruido del motor.",
        "subhead_2": "El altavoz emite la onda exactamente invertida.",
        "steps": [
            ("PASO 1", "Micrófono", "captura la onda ambiental"),
            ("PASO 2", "Procesador DSP", "invierte la fase 180 grados"),
            ("PASO 3", "Cancelación", "pico más valle es igual a cero"),
        ],
        "terminal_headline": "Procesamiento de señal DSP.",
        "terminal_highlight": "de señal DSP.",
        "terminal_prompt": "dsp_anc_process --onda_entrada: [sin(2*pi*f*t)] --fase: +180_deg",
        "terminal_response": "Onda anti-ruido inyectada: [-sin(2*pi*f*t)]. Suma de amplitudes: 0 dB. Ruido ambiente de turbina eliminado en tiempo real.",
        "features_headline": "La magia de la física de ondas.",
        "features_highlight": "física de ondas.",
        "features": [
            ("🎧", "Micrófonos externos e internos"),
            ("⚡", "Cálculo en menos de 5 milisegundos"),
            ("✈️", "Perfecto para ruidos continuos"),
            ("🗣️", "Voces repentinas pasan un poco"),
            ("🔋", "Consume batería por procesar audio"),
            ("🔬", "Física pura en tus oídos"),
        ],
        "cta_word": "SONIDO",
        "cta_promise": "Comentá SONIDO y te paso el test de audio para calibrar la cancelación activa de cualquier auricular.",
        "narration_script": (
            "Cuando te pones unos audífonos con cancelación de ruido y el rugido de un avión desaparece por arte de magia, tus audífonos no están bloqueando el sonido. "
            "Están fabricando más sonido. "
            "Tienen micrófonos en el exterior que capturan el ruido ambiental, y en cuestión de milisegundos, un chip interno genera una onda de sonido exactamente opuesta pero invertida. "
            "Cuando ambas ondas chocan en tu tímpano, la cresta de una cancela el valle de la otra, dejando un silencio matemático absoluto. "
            "Comentá SONIDO y te paso una prueba acústica para tus auriculares."
        ),
        "caption": (
            "La cancelación de ruido no aísla: crea una onda de sonido contraria que destruye el ruido en el aire. "
            "Comentá SONIDO y te comparto el archivo de audio para probar la potencia de tus audífonos. "
            "#Audio #Fisica #Tecnologia #ComoFunciona #Ciencia #Gadgets #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "smartphones_listen_ads",
        "topic": "Cómo saben las aplicaciones de qué hablaste con un amigo sin usar tu micrófono",
        "hook_title": "Borr[a] el micrófono. Es mucho más turbio.",
        "highlight_word": "más turbio.",
        "struck_items": ["Borr[a] 'te graban en secreto'.", "Borr[a] 'analizan tus palabras'.", "Borr[a] 'es espionaje de voz'."],
        "winner_item": "Grafos de proximidad y balizas.",
        "step_headline": "Saben con quién estás sentado.",
        "step_highlight": "estás sentado.",
        "subhead_1": "Si tu amigo busca zapatillas y se sientan juntos...",
        "subhead_2": "La publicidad te las muestra a ti en 2 horas.",
        "steps": [
            ("PASO 1", "Ubicación GPS", "ambos celulares en el mismo café"),
            ("PASO 2", "Balizas Bluetooth", "detectan proximidad física"),
            ("PASO 3", "Cruce de Datos", "te recomiendan lo que él buscó"),
        ],
        "terminal_headline": "Inferencia de grafo relacional.",
        "terminal_highlight": "grafo relacional.",
        "terminal_prompt": "vincular_dispositivos --ip_wifi: 192.168.10.1 --radio_proximidad: 1.8_metros",
        "terminal_response": "Dispositivo A buscó 'viaje a Japón' hace 3 horas. Dispositivo B en contacto físico por 45 minutos. Mostrando anuncio de vuelos a Tokio a Dispositivo B.",
        "features_headline": "Los rastreadores silenciosos.",
        "features_highlight": "rastreadores silenciosos.",
        "features": [
            ("📍", "GPS preciso al milímetro"),
            ("📶", "Misma red WiFi conectada"),
            ("📡", "Pings Bluetooth entre teléfonos"),
            ("👥", "Agenda de contactos cruzada"),
            ("🎯", "Modelos predictivos de Meta y Google"),
            ("🛡️", "No necesitan gastar batería grabando voz"),
        ],
        "cta_word": "DATOS",
        "cta_promise": "Comentá DATOS y te paso la configuración para apagar el escaneo continuo de Bluetooth y WiFi en segundo plano.",
        "narration_script": (
            "¿Hablaste con un amigo de comprarte una cafetera y dos horas después te apareció un anuncio de esa misma marca en Instagram? "
            "Casi todo el mundo cree que las aplicaciones tienen el micrófono encendido escuchando en secreto. "
            "La realidad técnica es mucho más inteligente y perturbadora: no necesitan grabarte la voz. "
            "Saben que estuviste físicamente al lado de tu amigo porque ambos teléfonos se conectaron al mismo router WiFi y cruzaron señales de Bluetooth. "
            "Si tu amigo buscó cafeteras ayer, el algoritmo asume que tú también la quieres. "
            "Comentá DATOS si alguna vez te pasó esto."
        ),
        "caption": (
            "No te escuchan el micrófono: usan grafos de proximidad física y WiFi para predecir tus conversaciones. "
            "¿Te ha pasado hablar de algo y que te aparezca el anuncio al instante? Comentá DATOS y te explico cómo desactivarlo. "
            "#Privacidad #Tecnologia #RedesSociales #ComoFunciona #Ciberseguridad #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "traffic_phantom_jams",
        "topic": "Por qué se forman atascos de tráfico de la nada sin que haya ningún accidente",
        "hook_title": "Borr[a] el choque. Es una onda de choque fantasma.",
        "highlight_word": "fantasma.",
        "struck_items": ["Borr[a] 'hubo un choque'.", "Borr[a] 'hay obras en la vía'.", "Borr[a] 'mala suerte'."],
        "winner_item": "Efecto acordeón matemático.",
        "step_headline": "Un solo frenazo a 5 kilómetros.",
        "step_highlight": "a 5 kilómetros.",
        "subhead_1": "Un conductor distraído frena 1 segundo.",
        "subhead_2": "El décimo auto atrás tiene que frenar a cero.",
        "steps": [
            ("PASO 1", "Frenazo Leve", "conductor reduce 10 km/h"),
            ("PASO 2", "Reacción Tardia", "los siguientes frenan más fuerte"),
            ("PASO 3", "Paro Total", "la onda viaja hacia atrás a 20 km/h"),
        ],
        "terminal_headline": "Simulación fluidodinámica de tráfico.",
        "terminal_highlight": "de tráfico.",
        "terminal_prompt": "simular_flujo_vehicular --densidad: 45_autos_km --perturbacion_freno: -2_segundos",
        "terminal_response": "Onda de parada retrógrada generada. Velocidad de propagación: -19 km/h. Detención completa para 180 vehículos durante 24 minutos.",
        "features_headline": "Cómo romper el atasco fantasma.",
        "features_highlight": "el atasco fantasma.",
        "features": [
            ("🚗", "Deja 3 segundos de distancia"),
            ("🛑", "Evita tocar el freno por reflejo"),
            ("🌊", "La onda viaja en reversa"),
            ("🚚", "Los camiones actúan como amortiguador"),
            ("🤖", "Los autos autónomos lo eliminarán"),
            ("📐", "Es pura física de ondas en fluidos"),
        ],
        "cta_word": "TRAFICO",
        "cta_promise": "Comentá TRAFICO y te paso el simulador interactivo de ondas de choque para que veas cómo se forma desde el aire.",
        "narration_script": (
            "Vas conduciendo por la autopista a cien kilómetros por hora, de repente todo se frena por completo, avanzas a paso de hombre durante media hora... y cuando el tráfico se despeja, no hay obras ni choques ni nada. "
            "Los físicos llaman a esto un atasco fantasma. "
            "Todo comienza cuando un solo conductor frena ligeramente porque iba pegado al de adelante. "
            "El auto que viene detrás frena un poco más fuerte por reflejo, y diez autos más atrás, el frenazo se multiplica hasta obligar a alguien a frenar a cero. "
            "Comentá TRAFICO si odias los embotellamientos."
        ),
        "caption": (
            "Los atascos de tráfico donde nunca hubo un accidente se llaman atascos fantasma y son una onda matemática. "
            "Comentá TRAFICO y te muestro el experimento científico que grabaron desde helicópteros para comprobarlo. "
            "#Trafico #Ciencia #Fisica #ComoFunciona #Curiosidades #Autos #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "money_creation_banks",
        "topic": "De dónde sale realmente el dinero cuando pides un préstamo en el banco",
        "hook_title": "Borr[a] la alcancía. Crean dinero del aire.",
        "highlight_word": "del aire.",
        "struck_items": ["Borr[a] 'prestan dinero ahorrado'.", "Borr[a] 'respaldado en oro'.", "Borr[a] 'el gobierno lo imprime'."],
        "winner_item": "Sistema de Reserva Fraccionaria.",
        "step_headline": "Solo teclean los números en tu cuenta.",
        "step_highlight": "en tu cuenta.",
        "subhead_1": "El 95% del dinero del mundo es digital.",
        "subhead_2": "Nace en el instante exacto que firmas la deuda.",
        "steps": [
            ("PASO 1", "La Solicitud", "pides 50,000 dólares"),
            ("PASO 2", "La Creación", "el banco crea un activo y un pasivo"),
            ("PASO 3", "El Interés", "ese interés no fue creado por nadie"),
        ],
        "terminal_headline": "Libro contable de banco comercial.",
        "terminal_highlight": "banco comercial.",
        "terminal_prompt": "ejecutar_prestamo --cliente: 4092 --monto: +100000 --deposito_bancario_nuevo: TRUE",
        "terminal_response": "Asiento contable completado: Pasivo del banco +$100,000 / Activo del banco (Pagaré del cliente) +$100,000. Masa monetaria M1 incrementada instantáneamente.",
        "features_headline": "Los secretos del dinero fiduciario.",
        "features_highlight": "dinero fiduciario.",
        "features": [
            ("🏦", "Los bancos privados crean el 97% del dinero"),
            ("💵", "El papel moneda es menos del 5%"),
            ("📝", "Tu firma crea la moneda legal"),
            ("📉", "La deuda es el motor de la economía"),
            ("💥", "Si todos pagaran sus deudas, el dinero desaparecería"),
            ("🧠", "El secreto mejor guardado de las finanzas"),
        ],
        "cta_word": "DINERO",
        "cta_promise": "Comentá DINERO y te paso el informe oficial del Banco de Inglaterra donde confirman cómo crean el dinero de la nada.",
        "narration_script": (
            "Casi todo el mundo cree que cuando un banco te da un préstamo para una casa o un auto, te está prestando el dinero que otros clientes dejaron ahorrado en sus cuentas. "
            "La realidad financiera es que los bancos comerciales crean el dinero de la nada. "
            "Cuando el analista aprueba tu préstamo, no transfiere fondos de ninguna caja fuerte: simplemente escribe el saldo en tu cuenta bancaria y crea una nueva deuda en su balance. "
            "Más del noventa y siete por ciento de todo el dinero del planeta nació como una deuda bancaria. "
            "Comentá DINERO y te paso el documento oficial que lo explica."
        ),
        "caption": (
            "Los bancos no prestan el dinero de otros ahorradores: lo crean de la nada en su teclado en cuanto firmas la deuda. "
            "Comentá DINERO y te comparto el documento oficial que explica la reserva fraccionaria. "
            "#Finanzas #Economia #Dinero #ComoFunciona #Secretos #Bancos #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "slot_machines_near_miss",
        "topic": "Cómo programan los casinos las tragamonedas para que sientas que casi ganas",
        "hook_title": "Borr[a] la suerte. Es un casi-acierto diseñado.",
        "highlight_word": "diseñado.",
        "struck_items": ["Borr[a] 'estuve a punto'.", "Borr[a] 'la máquina está cargada'.", "Borr[a] 'la próxima sale'."],
        "winner_item": "Efecto 'Near-Miss' de dopamina.",
        "step_headline": "El cerebro celebra la derrota.",
        "step_highlight": "la derrota.",
        "subhead_1": "Dos símbolos ganadores y el tercero a un milímetro.",
        "subhead_2": "Libera tanta dopamina como si hubieras ganado.",
        "steps": [
            ("PASO 1", "El Giro", "algoritmo RNG decide en 1ms"),
            ("PASO 2", "El Freno", "muestra 2 sietes y el 3ro se pasa"),
            ("PASO 3", "La Trampa", "sonidos alegres aunque perdiste"),
        ],
        "terminal_headline": "Algoritmo RNG de casino.",
        "terminal_highlight": "RNG de casino.",
        "terminal_prompt": "ejecutar_spin_tragamonedas --seed: PRNG_SHA256 --resultado_real: DERROTA",
        "terminal_response": "Resultado: 7 - 7 - CEREZA (+1 posición del 7). Efecto visual: CASI_VICTORIA. Activando luces festivas y fanfarria auditiva.",
        "features_headline": "El neuromarketing de las máquinas.",
        "features_highlight": "las máquinas.",
        "features": [
            ("🎰", "Luces y timbres en pérdidas disfrazadas"),
            ("🧠", "Dopamina idéntica al premio mayor"),
            ("⏰", "Sin relojes ni ventanas en la sala"),
            ("🍸", "Ambiente diseñado para desorientarte"),
            ("🧮", "El algoritmo siempre tiene ventaja matemática"),
            ("🛑", "El botón de parada no altera el resultado"),
        ],
        "cta_word": "CASINO",
        "cta_promise": "Comentá CASINO y te paso el estudio neurocientífico que escaneó cerebros apostando en tragamonedas.",
        "narration_script": (
            "¿Alguna vez jugaste a una máquina tragamonedas y sentiste la adrenalina dispararse porque te salieron dos números siete y el tercero quedó a solo un milímetro? "
            "No estuviste cerca de ganar. "
            "El algoritmo interno de la máquina decide el resultado en un milisegundo antes de que los rodillos empiecen a girar. "
            "Los programadores colocan deliberadamente símbolos ganadores justo por encima o por debajo de la línea de premio. "
            "Esto engaña a tu cerebro para que libere la misma dopamina que una victoria, convenciéndote de meter otra moneda. "
            "Comentá CASINO si alguna vez viste esta trampa."
        ),
        "caption": (
            "El 'casi gano' de los casinos no es suerte: es un algoritmo psicológico diseñado para disparar tu dopamina. "
            "Comentá CASINO y te paso el estudio neurocientífico completo sobre cómo hackean el cerebro en las apuestas. "
            "#Psicologia #Casino #Matematicas #ComoFunciona #Ciencia #Secretos #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "gps_relativity_einstein",
        "topic": "Por qué tu GPS fallaría 11 kilómetros al día si no usara la Teoría de la Relatividad",
        "hook_title": "Borr[a] los satélites solos. Einstein los guía.",
        "highlight_word": "Einstein los guía.",
        "struck_items": ["Borr[a] 'es solo triangulación'.", "Borr[a] 'el tiempo es idéntico'.", "Borr[a] 'la física pura no sirve'."],
        "winner_item": "Dilatación temporal de Einstein.",
        "step_headline": "El tiempo corre más rápido en órbita.",
        "step_highlight": "más rápido en órbita.",
        "subhead_1": "A 20,000 km la gravedad es menor.",
        "subhead_2": "Sus relojes atómicos adelantan 38 microsegundos por día.",
        "steps": [
            ("PASO 1", "Gravedad Menor", "el tiempo en órbita se acelera (+45μs)"),
            ("PASO 2", "Velocidad Alta", "la velocidad lo frena (-7μs)"),
            ("PASO 3", "Diferencia Neta", "+38 microsegundos diarios corregidos"),
        ],
        "terminal_headline": "Corrección relativista de reloj satelital.",
        "terminal_highlight": "reloj satelital.",
        "terminal_prompt": "calcular_dilatacion_satelite --altitud: 20200_km --velocidad: 14000_kmh",
        "terminal_response": "Deriva temporal neta: +38.6 microsegundos/día. Multiplicado por c (velocidad luz) = Error acumulado de 11.4 kilómetros por día sin corrección.",
        "features_headline": "La física cuántica en tu celular.",
        "features_highlight": "en tu celular.",
        "features": [
            ("🛰️", "31 satélites GPS en órbita media"),
            ("⏱️", "Relojes atómicos de cesio y rubidio"),
            ("⚡", "Precisión al nanosegundo"),
            ("🚗", "Sin Einstein terminarías en el río"),
            ("🌌", "Relatividad especial y general combinadas"),
            ("📱", "Tu smartphone usa física de agujeros negros"),
        ],
        "cta_word": "EINSTEIN",
        "cta_promise": "Comentá EINSTEIN y te paso el diagrama interactivo de cómo la gravedad deforma el tiempo alrededor de la Tierra.",
        "narration_script": (
            "Cada vez que abres Google Maps o Waze para llegar a tu destino, tu celular está aplicando la Teoría de la Relatividad General de Albert Einstein. "
            "Los satélites GPS orbitan a veinte mil kilómetros de la Tierra, donde la gravedad es mucho más débil. "
            "Por las leyes de la física, el tiempo corre más rápido allá arriba que aquí en la superficie. "
            "Sus relojes atómicos se adelantan treinta y ocho microsegundos cada día. "
            "Si los ingenieros no hubieran programado las ecuaciones de Einstein para corregir esa diferencia, tu mapa se desviaría once kilómetros cada veinticuatro horas. "
            "Comentá EINSTEIN si sabías esto."
        ),
        "caption": (
            "Si no fuera por Albert Einstein, tu GPS te diría que estás en medio del océano en vez de tu casa. "
            "Comentá EINSTEIN y te paso la infografía visual de la dilatación del tiempo satelital. "
            "#Fisica #Einstein #GPS #Ciencia #ComoFunciona #Tecnologia #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "microwave_oven_water",
        "topic": "Por qué el microondas calienta la comida pero deja el plato de cerámica frío",
        "hook_title": "Borr[a] el fuego. Hace bailar las moléculas.",
        "highlight_word": "las moléculas.",
        "struck_items": ["Borr[a] 'calienta desde adentro hacia afuera'.", "Borr[a] 'es radiación nuclear'.", "Borr[a] 'calienta todo parejo'."],
        "winner_item": "Resonancia dipolar del agua a 2.45 GHz.",
        "step_headline": "Fricción a 2,400 millones de giros por segundo.",
        "step_highlight": "por segundo.",
        "subhead_1": "Las ondas voltean moléculas polares de agua.",
        "subhead_2": "La fricción genera calor instantáneo.",
        "steps": [
            ("PASO 1", "Magnetrón", "dispara ondas electromagnéticas"),
            ("PASO 2", "Agua y Grasa", "rotan a velocidad descomunal"),
            ("PASO 3", "Plato Frío", "la cerámica no tiene moléculas polares"),
        ],
        "terminal_headline": "Espectro electromagnético doméstico.",
        "terminal_highlight": "doméstico.",
        "terminal_prompt": "campo_electromagnetico --frecuencia: 2450_MHz --polaridad: ALTERNANTE",
        "terminal_response": "Molécula H2O (polo positivo/negativo): 2,450,000,000 oscilaciones/segundo. Calor generado por fricción intermolecular: +75°C en 60 segundos.",
        "features_headline": "Secretos de tu cocina moderna.",
        "features_highlight": "cocina moderna.",
        "features": [
            ("🌊", "Solo afecta agua, grasas y azúcares"),
            ("🍽️", "El plato solo se calienta por contacto"),
            ("⚡", "La misma frecuencia que el WiFi 2.4G"),
            ("🛡️", "La rejilla metálica bloquea las ondas"),
            ("🧊", "El hielo seco casi no calienta"),
            ("🍇", "Nunca metas uvas cortadas (hacen plasma)"),
        ],
        "cta_word": "ONDAS",
        "cta_promise": "Comentá ONDAS y te paso el experimento casero para medir la velocidad de la luz usando queso derretido en tu microondas.",
        "narration_script": (
            "¿Por qué cuando sacas un tazón de sopa del microondas la sopa está hirviendo pero el borde del plato está completamente frío? "
            "El microondas no genera calor como un horno tradicional. "
            "Dispara ondas electromagnéticas a dos mil cuatrocientos cincuenta megahercios, la frecuencia exacta que hace rotar violentamente a las moléculas de agua y grasa miles de millones de veces por segundo. "
            "El calor se produce por la fricción de esas moléculas rozándose entre sí. "
            "Como la cerámica y el vidrio no tienen agua libre, las ondas los atraviesan sin tocarlos. "
            "Comentá ONDAS y te paso cómo medir la velocidad de la luz en tu cocina."
        ),
        "caption": (
            "El microondas no tiene fuego ni resistencias: hace vibrar el agua a 2.4 mil millones de veces por segundo. "
            "Comentá ONDAS y te paso el truco para medir la velocidad de la luz con una barra de chocolate. "
            "#Ciencia #Fisica #Cocina #ComoFunciona #Curiosidades #Gadgets #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "submarines_implosion_pressure",
        "topic": "Qué pasa en una implosión submarina a 4,000 metros de profundidad",
        "hook_title": "Borr[a] la explosión. Ocurre hacia adentro en 30ms.",
        "highlight_word": "en 30ms.",
        "struck_items": ["Borr[a] 'te ahogas despacio'.", "Borr[a] 'sientes el agua fría'.", "Borr[a] 'da tiempo de asustarse'."],
        "winner_item": "Compresión adiabática instantánea.",
        "step_headline": "Cuatrocientas atmósferas de presión pura.",
        "step_highlight": "de presión pura.",
        "subhead_1": "El peso de la Torre Eiffel sobre cada metro cuadrado.",
        "subhead_2": "El cerebro tarda 100ms en procesar el dolor.",
        "steps": [
            ("PASO 1", "Microfisura", "el casco cede a 400 bar"),
            ("PASO 2", "Colapso Sónico", "el aire se comprime en 30ms"),
            ("PASO 3", "Flash Térmico", "temperatura alcanza la superficie del sol"),
        ],
        "terminal_headline": "Telemetría de hidrostática abisal.",
        "terminal_highlight": "hidrostática abisal.",
        "terminal_prompt": "calcular_implosion_casco --profundidad: 3800_m --presion_bar: 385",
        "terminal_response": "Colapso volumétrico completo en 0.028 segundos. Tiempo de respuesta sináptica humana: 0.100 segundos. Conclusión: Aniquilación biológica previa a percepción neuronal.",
        "features_headline": "La física extrema del abismo marino.",
        "features_highlight": "del abismo marino.",
        "features": [
            ("🌊", "Presión equivalente a un elefante por uña"),
            ("⚡", "Velocidad de compresión a match 2"),
            ("🔥", "El aire se calienta a miles de grados"),
            ("🧠", "Cero dolor por velocidad física"),
            ("🛡️", "El titanio resiste, el carbono cede por fatiga"),
            ("🌌", "Más hostil que el vacío del espacio exterior"),
        ],
        "cta_word": "ABISMO",
        "cta_promise": "Comentá ABISMO y te paso el mapa de profundidades marinas comparado con los rascacielos más altos del mundo.",
        "narration_script": (
            "A cuatro mil metros bajo la superficie del océano, la presión del agua es de casi cuatrocientas atmósferas. "
            "Eso equivale al peso de la Torre Eiffel descansando sobre tu cuerpo. "
            "Si el casco de un submarino sufre una falla estructural a esa profundidad, la implosión no es como en las películas donde el agua entra por una fuga. "
            "El aire del interior se comprime a la velocidad del sonido en apenas treinta milisegundos. "
            "Como el cerebro humano necesita al menos cien milisegundos para sentir dolor o registrar lo que pasó, la implosión ocurre mucho más rápido que un parpadeo de consciencia. "
            "Comentá ABISMO para conocer los misterios de las profundidades."
        ),
        "caption": (
            "La física de una implosión submarina a 4,000 metros de profundidad: cómo 400 atmósferas colapsan la materia en 30 milisegundos. "
            "Comentá ABISMO y te paso la comparativa de presión con los abismos oceánicos. "
            "#Oceano #Fisica #Ciencia #Misterios #Submarino #ComoFunciona #BrunoSchiller #Shorts"
        ),
    },
    {
        "id": "credit_card_minimum_trap",
        "topic": "La trampa matemática del 'pago mínimo' en las tarjetas de crédito",
        "hook_title": "Borr[a] el alivio. Es una condena de 20 años.",
        "highlight_word": "de 20 años.",
        "struck_items": ["Borr[a] 'estoy al día'.", "Borr[a] 'no me afecta el historial'.", "Borr[a] 'pago poquito y salgo'."],
        "winner_item": "Interés compuesto invertido.",
        "step_headline": "El 90% de tu cuota es solo interés.",
        "step_highlight": "solo interés.",
        "subhead_1": "Compras una tele de 1,000 dólares.",
        "subhead_2": "Terminas pagando 5,400 dólares en 18 años.",
        "steps": [
            ("PASO 1", "El Banco Fija", "cuota mínima del 2% al 5%"),
            ("PASO 2", "Interés Come", "el 85% de tu pago no amortiza deuda"),
            ("PASO 3", "La Bola de Nieve", "cada mes pagas interés sobre interés"),
        ],
        "terminal_headline": "Simulación financiera de deuda revolvente.",
        "terminal_highlight": "deuda revolvente.",
        "terminal_prompt": "simular_amortizacion --deuda_inicial: 2000_USD --tasa_tna: 68% --pago: MINIMO",
        "terminal_response": "Mes 12: Pagado $840. Reducción de capital real: $62. Tiempo estimado de cancelación: 21 años y 4 meses. Total pagado: $7,920.",
        "features_headline": "Cómo romper la trampa del banco.",
        "features_highlight": "del banco.",
        "features": [
            ("💳", "Paga siempre el saldo total de la fecha"),
            ("📉", "Usa la tarjeta como medio de pago, no préstamo"),
            ("🛑", "El interés compuesto es tu peor enemigo"),
            ("💰", "Aplica el método bola de nieve en deudas"),
            ("🗓️", "Aprende tu fecha de corte y de pago"),
            ("🛡️", "Finanzas blindadas con educación real"),
        ],
        "cta_word": "FINANZAS",
        "cta_promise": "Comentá FINANZAS y te paso la calculadora en Excel para ver exactamente cuánto le estás regalando a tu banco.",
        "narration_script": (
            "Cuando llega el resumen de tu tarjeta de crédito y ves la casilla que dice 'Pago Mínimo', parece una oferta generosa del banco para ayudarte a respirar ese mes. "
            "En realidad es el algoritmo financiero más lucrativo jamás inventado. "
            "El pago mínimo está calculado matemáticamente para cubrir casi exclusivamente los intereses del mes y apenas el uno por ciento de la deuda real. "
            "Si compraste un celular de mil dólares y pagas solo el mínimo, tardarás más de quince años en terminar de pagarlo y le habrás entregado cuatro veces su valor al banco. "
            "Comentá FINANZAS y te paso cómo salir de esa trampa."
        ),
        "caption": (
            "El pago mínimo de tu tarjeta de crédito no es una ayuda: es una trampa matemática para cobrarte 4 veces más. "
            "Comentá FINANZAS y te paso la plantilla para calcular tu fecha de libertad financiera. "
            "#Finanzas #Dinero #EducacionFinanciera #TarjetasDeCredito #ComoFunciona #BrunoSchiller #Shorts"
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
