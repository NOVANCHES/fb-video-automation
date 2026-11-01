"""
Módulo 1: Generación de Guiones de Formato Largo (65-80s, 5 Capítulos),
Historias Ilustradas 100% Coherentes con el Tema y Descripciones Virales para Facebook.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
import requests

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OUTPUT_DIR,
)


def _call_gemini_fast(prompt: str, system_instruction: str = "", timeout_sec: float = 10.0) -> str:
    """
    Llama directamente al endpoint REST de Gemini con timeout estricto de 10s
    y CERO bucles de reintento ante errores 429/503 para nunca bloquear la ejecución.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "tu_api_key_de_gemini_aqui":
        return ""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        resp = requests.post(url, json=payload, timeout=timeout_sec)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return (parts[0].get("text") or "").strip()
    except Exception:
        pass
    return ""


# ==============================================================================
# BANCO DE EPISODIOS DE FORMATO LARGO (65-80 SEGUNDOS, 5 CAPÍTULOS)
# Cada episodio tiene su propio tema visual, guion largo de ~185 palabras,
# 5 capítulos sincronizados, postal ilustrada coherente y pregunta de debate.
# ==============================================================================
THEMATIC_EPISODES: List[Dict[str, Any]] = [
    {
        "topic": "El misterio de la Fosa de las Marianas: qué vive realmente a 11 kilómetros bajo el océano",
        "theme": "ocean",
        "headline": "A 11,000 METROS BAJO EL MAR",
        "subheadline": "LO QUE VIVE EN LA FOSA DE LAS MARIANAS",
        "script": (
            "¿Qué pasaría si descendieras hoy mismo en un submarino hasta el punto más profundo y oscuro de todo el planeta, a casi once mil metros bajo el océano? "
            "En el capítulo uno, al cruzar los primeros doscientos metros de profundidad, la luz del sol desaparece para siempre y entras en la zona crepuscular, donde la temperatura cae casi al punto de congelación. "
            "En el capítulo dos, a los cuatro mil metros de profundidad, la oscuridad es total y la única luz proviene de medusas bioluminiscentes y peces abisales con dientes gigantescos que usan señuelos brillantes para cazar en el vacío. "
            "En el capítulo tres, al llegar a los ocho mil metros, la presión del agua supera las ochocientas atmósferas: es como tener el peso de cincuenta aviones comerciales aplastando cada centímetro del casco de titanio. "
            "En el capítulo cuatro, al tocar el fondo del Abismo Challenger a casi once mil metros, los reflectores revelan chimeneas hidrotermales hirviendo a cuatrocientos grados y criaturas translúcidas que sobreviven sin oxígeno ni luz solar. "
            "Y en el capítulo cinco, lo más inquietante: hemos explorado menos del cinco por ciento del fondo oceánico. ¿Te atreverías a bajar ahí por un millón de dólares? Déjalo en los comentarios."
        ),
        "scenes": [
            {"title": "200 METROS", "subtitle": "DESAPARECE LA LUZ SOLAR"},
            {"title": "4,000 METROS", "subtitle": "CRIATURAS BIOLUMINISCENTES"},
            {"title": "8,000 METROS", "subtitle": "PRESIÓN EXTREMA: 800 ATM"},
            {"title": "10,994 METROS", "subtitle": "EL FONDO DEL ABISMO"},
            {"title": "EL GRAN MISTERIO", "subtitle": "¿BAJARÍAS POR $1,000,000?"},
        ],
        "story": (
            "¿Te atreverías a descender a 10,994 metros bajo el océano en la Fosa de las Marianas?\n\n"
            "A esa profundidad, la oscuridad es absoluta y la presión es de más de 1,086 atmósferas (equivalente a que un elefante se pare sobre tu pulgar). "
            "Sin embargo, cuando las pocas expediciones humanas han encendido sus reflectores en el fondo, han encontrado chimeneas volcánicas submarinas, anfípodos gigantes y peces translúcidos cuyos órganos internos se ven a través de su piel.\n\n"
            "Lo más asombroso es que conocemos mejor la superficie de Marte que el fondo de nuestros propios océanos.\n\n"
            "¿Aceptarías bajar en un submarino hasta el fondo del Abismo Challenger si te pagaran un millón de dólares, o ni loco entrarías? ¡Te leo en los comentarios!\n\n"
            "#misterios #oceano #curiosidades #ciencia #supervivencia"
        ),
        "caption": (
            "A casi 11 kilómetros bajo el mar, la presión aplastaría cualquier submarino común en milisegundos, pero ahí abajo hay vida que parece de otro planeta. "
            "Mira hasta el capítulo 5: ¿tú aceptarías bajar al fondo de la Fosa de las Marianas por un millón de dólares o ni loco te subirías al submarino? ¡Te leo en los comentarios! "
            "#reels #oceano #misterios #curiosidades #supervivencia #viral"
        ),
    },
    {
        "topic": "¿Qué pasaría en las primeras 72 horas si se apagara todo el internet y la electricidad del mundo?",
        "theme": "blackout",
        "headline": "72 HORAS DE APAGÓN MUNDIAL",
        "subheadline": "¿CUÁNTO TIEMPO SOBREVIVIRÍAS SIN RED?",
        "script": (
            "¿Qué ocurriría exactamente minuto a minuto si hoy mismo a medianoche se apagara por completo toda la electricidad y el internet del planeta? "
            "En la primera hora, el caos comienza en las ciudades: todos los semáforos se apagan al mismo tiempo, miles de personas quedan atrapadas en elevadores y el tráfico colapsa por completo mientras los teléfonos pierden toda señal. "
            "Para la hora doce, cuando la gente descubre que los cajeros automáticos y las tarjetas bancarias no funcionan sin red, solo el dinero en efectivo tiene valor y las filas en gasolineras y supermercados se vuelven interminables. "
            "A las veinticuatro horas llega el problema que casi nadie prevé: las bombas eléctricas de agua potable dejan de funcionar y los edificios se quedan sin una sola gota de agua en las tuberías. "
            "Para la hora cuarenta y ocho, los generadores de emergencia de reserva agotan su combustible, toda la comida refrigerada se echa a perder y la única forma de enterarse de lo que pasa es con una radio de baterías. "
            "Al cumplir las setenta y dos horas, solo sobreviven sin pánico quienes tenían agua almacenada, comida no perecedera y linternas. ¿Cuántos días durarías tú con lo que tienes hoy en tu casa? Comenta aquí abajo."
        ),
        "scenes": [
            {"title": "HORA 1: EL APAGÓN", "subtitle": "CAEN SEMÁFOROS Y SEÑAL"},
            {"title": "HORA 12: SIN BANCOS", "subtitle": "CAJEROS Y TARJETAS MUERTOS"},
            {"title": "HORA 24: SIN AGUA", "subtitle": "FALLAN LAS BOMBAS ELÉCTRICAS"},
            {"title": "HORA 48: OSCURIDAD", "subtitle": "SE AGOTAN LOS GENERADORES"},
            {"title": "HORA 72: ¿LISTO?", "subtitle": "¿CUÁNTOS DÍAS DURARÍAS TÚ?"},
        ],
        "story": (
            "¿Qué pasaría en tu ciudad si hoy mismo se apagara toda la electricidad y el internet durante 72 horas?\n\n"
            "1. En los primeros 60 minutos: dejan de funcionar semáforos, cajeros automáticos, pagos con tarjeta y redes celulares.\n"
            "2. A las 24 horas: las plantas de bombeo eléctrico se detienen y deja de salir agua de los grifos.\n"
            "3. A las 72 horas: los supermercados quedan vacíos y solo quienes tienen radio de pilas, agua embotellada y comida enlatada mantienen el control.\n\n"
            "Si el apagón ocurriera justo en este instante, ¿para cuántos días te alcanzaría la comida y el agua que tienes ahora mismo en tu cocina? ¡Déjalo en los comentarios!\n\n"
            "#supervivencia #apagon #curiosidades #misterios #tendencias"
        ),
        "caption": (
            "El 90% de las personas cree que un apagón global solo sería quedarse sin Wi-Fi, pero a las 24 horas ocurre algo mucho más grave con el agua potable. "
            "Si hoy se apagara todo el planeta, ¿para cuántos días te alcanzaría lo que tienes ahora mismo en tu casa? ¡Comenta tu respuesta! "
            "#reels #supervivencia #curiosidades #misterios #viral"
        ),
    },
    {
        "topic": "¿Cuánto tiempo sobrevivirías en cada era prehistórica si viajaras al pasado?",
        "theme": "prehistory",
        "headline": "VIAJAR A LA PREHISTORIA",
        "subheadline": "¿CUÁNTO TIEMPO SOBREVIVIRÍAS?",
        "script": (
            "¿Cuánto tiempo lograrías mantenerte con vida si una máquina del tiempo te enviara por accidente a las eras más peligrosas de la prehistoria? "
            "En la primera parada, hace cuatrocientos millones de años en el periodo Devónico, ni siquiera podrías pisar tierra firme: los continentes eran desiertos de roca ardiente y los océanos estaban dominados por peces acorazados de nueve metros con mandíbulas como guillotinas. "
            "En la segunda parada, durante el periodo Carbonífero, el nivel de oxígeno en el aire era tan alto que te marearías en minutos, mientras escorpiones del tamaño de un perro y libélulas gigantes cazaban entre pantanos infinitos. "
            "En la tercera parada, hace ciento cincuenta millones de años en pleno Jurásico, el suelo temblaría bajo manadas de saurópodos colosales, y tu única oportunidad sería esconderte en cuevas estrechas donde los grandes depredadores no pudieran entrar. "
            "En la cuarta parada, al final del Cretácico hace sesenta y seis millones de años, tendrías que escapar de dinosaurios emplumados ultrarrápidos con el oído más agudo de la historia bajo lluvias de ceniza volcánica. "
            "Y en la quinta parada, el impacto del asteroide cambiaría el planeta para siempre. ¿En cuál de estas eras crees que sobrevivirías más tiempo? Te leo en los comentarios."
        ),
        "scenes": [
            {"title": "ERA 1: DEVÓNICO", "subtitle": "MONSTRUOS ACORAZADOS"},
            {"title": "ERA 2: CARBONÍFERO", "subtitle": "INSECTOS GIGANTES Y 31% O2"},
            {"title": "ERA 3: JURÁSICO", "subtitle": "TIERRA DE COLOSOS"},
            {"title": "ERA 4: CRETÁCICO", "subtitle": "CAZADORES IMPLACABLES"},
            {"title": "EL IMPACTO FINAL", "subtitle": "¿EN CUÁL SOBREVIVIRÍAS?"},
        ],
        "story": (
            "Si viajaras al pasado sin armas modernas, ¿en qué era prehistórica sobrevivirías más tiempo?\n\n"
            "Muchos piensan primero en el Cretácico con el Tiranosaurio Rex, pero en el periodo Carbonífero el oxígeno superaba el 30% y los bosques estaban llenos de artrópodos gigantes, mientras que en el Pérmico las temperaturas superaban los 50 grados centígrados en gran parte del planeta.\n\n"
            "Si tuvieras que sobrevivir 24 horas en una de estas eras solo con una mochila de campamento, ¿cuál elegirías y cuál sería tu estrategia? ¡Comenta aquí abajo!\n\n"
            "#prehistoria #dinosaurios #supervivencia #ciencia #curiosidades"
        ),
        "caption": (
            "Viajar a la época de los dinosaurios suena increíble hasta que descubres lo que había en el aire y en los bosques prehistóricos. "
            "Si tuvieras que sobrevivir 24 horas en una de estas 5 eras, ¿cuál elegirías para salir con vida? ¡Déjalo en los comentarios! "
            "#reels #prehistoria #dinosaurios #supervivencia #curiosidades #viral"
        ),
    },
    {
        "topic": "Cómo sobrevivirías si quedaras atrapado en una isla prohibida durante 30 días",
        "theme": "island",
        "headline": "30 DÍAS EN UNA ISLA PROHIBIDA",
        "subheadline": "LAS 5 REGLAS PARA SALIR CON VIDA",
        "script": (
            "¿Qué harías si despertaras completamente solo en la playa de una isla prohibida y tuvieras que sobrevivir treinta días hasta que llegue un rescate? "
            "En el día uno, la regla de oro que separa a los sobrevivientes de las víctimas es la regla del tres: puedes resistir tres semanas sin comida, pero solo tres días sin agua potable, así que buscar un manantial o recolectar agua de lluvia es tu prioridad absoluta. "
            "Para el día cinco, antes de que caiga la primera tormenta tropical, necesitas levantar un refugio elevado con bambú y hojas de palma lejos de la marea alta y de los insectos venenosos del suelo. "
            "En el día doce, cuando el hambre aprieta, encender una fogata por fricción no solo te permite cocinar peces y hervir el agua, sino mantener una columna de humo visible a kilómetros en el mar. "
            "Para el día veinte, al explorar el interior de la jungla, descubres por qué la isla estaba restringida en los mapas: antiguas estructuras abandonadas cubiertas por la vegetación donde ningún barco comercial se acerca. "
            "Al llegar al día treinta, una señal gigante de piedras en la arena es tu única esperanza cuando pasa un helicóptero. ¿Qué único objeto elegirías llevar a la isla? Comenta abajo."
        ),
        "scenes": [
            {"title": "DÍA 1: EL AGUA", "subtitle": "LA REGLA MORTAL DE LOS 3 DÍAS"},
            {"title": "DÍA 5: EL REFUGIO", "subtitle": "PROTECCIÓN CONTRA TORMENTAS"},
            {"title": "DÍA 12: EL FUEGO", "subtitle": "HUMO Y AGUA PURIFICADA"},
            {"title": "DÍA 20: EL MISTERIO", "subtitle": "¿POR QUÉ ESTÁ PROHIBIDA?"},
            {"title": "DÍA 30: EL RESCATE", "subtitle": "¿QUÉ OBJETO LLEVARÍAS TÚ?"},
        ],
        "story": (
            "Imagina despertar en una isla tropical restringida con solo un objeto en tu mochila para sobrevivir 30 días.\n\n"
            "El 80% de las personas elegiría llevar comida, pero los instructores de supervivencia explican que el agua potable y una herramienta para cortar y hacer fuego en las primeras 48 horas son lo único que garantiza llegar a la segunda semana.\n\n"
            "Si solo pudieras elegir UN objeto entre un cuchillo de supervivencia, un encendedor infinito o un filtro de agua, ¿cuál elegirías y por qué? ¡Te leo en los comentarios!\n\n"
            "#supervivencia #isla #misterios #retos #curiosidades"
        ),
        "caption": (
            "Sobrevivir 30 días en una isla desierta depende por completo de lo que hagas antes de que caiga la primera noche. "
            "Si solo pudieras llevar UN objeto contigo (cuchillo, fuego o filtro de agua), ¿cuál elegirías para sobrevivir los 30 días? ¡Te leo en los comentarios! "
            "#reels #supervivencia #isla #misterios #curiosidades #viral"
        ),
    },
    {
        "topic": "¿Qué pasaría si una megatormenta solar golpeara la Tierra mañana mismo?",
        "theme": "space",
        "headline": "IMPACTO DE TORMENTA SOLAR",
        "subheadline": "EL EVENTO QUE APAGARÍA LOS SATÉLITES",
        "script": (
            "¿Sabías que en mil ochocientos cincuenta y nueve una tormenta solar tan potente golpeó la Tierra que los cables de telégrafo echaron chispas en llamas, y qué pasaría si ocurriera hoy mismo? "
            "En la fase uno, los observatorios espaciales detectarían una eyección de masa coronal gigante saliendo del Sol a millones de kilómetros por hora, dándonos apenas dieciocho horas de advertencia antes del impacto. "
            "En la fase dos, al chocar contra el campo magnético de la Tierra, el cielo nocturno se iluminaría con auroras boreales visibles hasta en el ecuador, pero en el espacio cientos de satélites de GPS y comunicaciones quedarían fritos al instante. "
            "En la fase tres, las corrientes geomagnéticas inducidas sobrecargarían los transformadores de alta tensión en tierra, provocando apagones en cadena en continentes enteros. "
            "En la fase cuatro, todos los vuelos comerciales tendrían que aterrizar de emergencia por la pérdida de radares y navegación satelital, mientras el internet submarino sufriría interrupciones masivas. "
            "Y en la fase cinco, reemplazar los transformadores gigantes tomaría meses de trabajo. ¿Crees que nuestra civilización moderna está preparada para una tormenta solar nivel cinco? Déjalo en los comentarios."
        ),
        "scenes": [
            {"title": "FASE 1: ALERTA SOLAR", "subtitle": "SOLO 18 HORAS DE AVISO"},
            {"title": "FASE 2: EL IMPACTO", "subtitle": "CAEN LOS SATÉLITES GPS"},
            {"title": "FASE 3: ALTA TENSIÓN", "subtitle": "COLAPSO DE TRANSFORMADORES"},
            {"title": "FASE 4: SIN RADARES", "subtitle": "VUELOS E INTERNET DETENIDOS"},
            {"title": "FASE 5: EL DEBATE", "subtitle": "¿ESTAMOS PREPARADOS HOY?"},
        ],
        "story": (
            "En 1859 ocurrió el Evento Carrington: la tormenta solar más potente registrada en la historia.\n\n"
            "En aquella época apenas existían los telégrafos, pero los científicos de la NASA advierten que si una tormenta solar de la misma magnitud impactara la Tierra hoy, desactivaría satélites GPS, telecomunicaciones y transformadores eléctricos en cuestión de minutos.\n\n"
            "¿Qué tan dependiente eres hoy de la tecnología si mañana dejaran de funcionar el GPS y los satélites durante un mes entero? ¡Comenta tu opinión!\n\n"
            "#espacio #ciencia #tormentasolar #misterios #curiosidades"
        ),
        "caption": (
            "Ya ocurrió una vez en 1859 y los astrónomos saben que volverá a ocurrir tarde o temprano. "
            "Si una tormenta solar apagara los satélites y el GPS durante un mes entero, ¿qué sería lo primero que colapsaría en tu ciudad? ¡Te leo en los comentarios! "
            "#reels #espacio #ciencia #supervivencia #curiosidades #viral"
        ),
    },
    {
        "topic": "Por qué existen zonas del Amazonas donde ni los drones ni los satélites pueden ver el suelo",
        "theme": "jungle",
        "headline": "EL MISTERIO DEL AMAZONAS",
        "subheadline": "LA ZONA DONDE NO ENTRA LA LUZ",
        "script": (
            "¿Por qué en pleno siglo veintiuno, teniendo satélites militares y drones de última generación, todavía existen zonas profundas del Amazonas donde nadie ha podido ver qué hay en el suelo? "
            "En el capítulo uno, al adentrarte apenas cincuenta kilómetros fuera de las rutas fluviales, el dosel de los árboles gigantes forma un techo vegetal de sesenta metros de altura tan compacto que bloquea el noventa y nueve por ciento de la luz solar. "
            "En el capítulo dos, cuando los exploradores intentan volar drones bajo las copas de los árboles, la humedad del cien por ciento y el follaje espeso cortan por completo la señal de radio y el GPS en pocos metros. "
            "En el capítulo tres, en el suelo perpetuamente oscuro de la selva profunda, habitan miles de especies de insectos, anfibios venenosos y depredadores que ni siquiera han sido clasificados por la biología. "
            "En el capítulo cuatro, recientes escaneos láser desde aviones han revelado trazos geométricos y calzadas antiguas ocultas bajo la vegetación, demostrando que ahí existieron ciudades enteras hace siglos. "
            "Y en el capítulo cinco, la pregunta sigue abierta: ¿qué más crees que permanece oculto bajo la selva más grande del mundo? Comenta tu teoría."
        ),
        "scenes": [
            {"title": "CAPÍTULO 1: EL TECHO", "subtitle": "99% DE LA LUZ BLOQUEADA"},
            {"title": "CAPÍTULO 2: SIN SEÑAL", "subtitle": "LOS DRONES PIERDEN EL GPS"},
            {"title": "CAPÍTULO 3: LA SOMBRA", "subtitle": "ESPECIES AÚN DESCONOCIDAS"},
            {"title": "CAPÍTULO 4: LÁSER LIDAR", "subtitle": "CIUDADES OCULTAS BAJO TIERRA"},
            {"title": "CAPÍTULO 5: TU TEORÍA", "subtitle": "¿QUÉ CREES QUE OCULTA?"},
        ],
        "story": (
            "¿Por qué aún no hemos podido explorar el 100% de las profundidades del Amazonas?\n\n"
            "En las zonas más densas de la selva, el techo de hojas a 60 metros de altura es tan cerrado que ni la luz del sol ni las cámaras ópticas de los satélites logran atravesarlo. "
            "Cuando los arqueólogos usaron tecnología láser LiDAR desde el aire, descubrieron pirámides de tierra, canales y calzadas de civilizaciones antiguas que llevaban siglos escondidas a simple vista.\n\n"
            "¿Qué crees que sea lo más asombroso que aún falta por descubrir en las zonas inexploradas de la selva? ¡Déjalo en los comentarios!\n\n"
            "#amazonas #misterios #selva #curiosidades #historia"
        ),
        "caption": (
            "Ni los satélites ópticos ni los drones comunes logran penetrar las zonas más densas del Amazonas, pero el láser LiDAR acaba de revelar algo increíble bajo los árboles. "
            "¿Qué crees que siga oculto hoy en las zonas inexploradas de la selva? ¡Comenta tu teoría! "
            "#reels #amazonas #misterios #curiosidades #supervivencia #viral"
        ),
    },
    {
        "topic": "Los 5 errores que el 95 por ciento de las personas cometería en una evacuación de emergencia",
        "theme": "zombie",
        "headline": "5 ERRORES EN UNA EVACUACIÓN",
        "subheadline": "LO QUE EL 95% HACE MAL EL DÍA 1",
        "script": (
            "Si hoy sonaran las alarmas de evacuación en tu ciudad por una emergencia mayor, ¿cometerías alguno de los cinco errores que dejan atrapado al noventa y cinco por ciento de la gente? "
            "El error número uno ocurre en los primeros treinta minutos: correr al supermercado al mismo tiempo que toda la ciudad, quedando atrapado en aglomeraciones cuando los estantes de agua y comida ya están vacíos. "
            "El error número dos es intentar salir por la autopista principal en hora pico sin revisar el combustible: un solo accidente bloquea todos los carriles y convierte los autos en una trampa inmóvil. "
            "El error número tres es depender exclusivamente del teléfono celular para ubicarse; cuando las antenas se saturan por millones de llamadas simultáneas, sin un mapa físico ni radio quedas totalmente incomunicado. "
            "El error número cuatro es empacar maletas pesadas llenas de cosas innecesarias en lugar de una mochila ligera de setenta y dos horas con agua, botiquín, linterna y baterías. "
            "Y el error número cinco es no tener un punto de reunión familiar acordado de antemano. ¿Cuántos de estos cinco puntos tienes listos hoy en tu casa? Déjalo en los comentarios."
        ),
        "scenes": [
            {"title": "ERROR 1: EL SÚPER", "subtitle": "CAOS EN LOS PRIMEROS 30 MIN"},
            {"title": "ERROR 2: AUTOPISTAS", "subtitle": "CARRILES BLOQUEADOS SIN SALIDA"},
            {"title": "ERROR 3: EL CELULAR", "subtitle": "ANTENAS SATURADAS SIN RED"},
            {"title": "ERROR 4: EL EQUIPAJE", "subtitle": "MOCHILA LIGERA DE 72 HORAS"},
            {"title": "ERROR 5: EL PLAN", "subtitle": "¿ESTÁS PREPARADO HOY?"},
        ],
        "story": (
            "El 95% de las personas comete exactamente los mismos 5 errores durante la primera hora de una emergencia o evacuación:\n\n"
            "1. Ir al supermercado cuando ya colapsaron las filas.\n"
            "2. Tomar la avenida principal sin combustible suficiente.\n"
            "3. Confiar solo en el celular sin tener radio ni mapa físico.\n"
            "4. Cargar peso innecesario en vez de agua, botiquín y linterna.\n"
            "5. No haber acordado un punto de encuentro familiar si se cae la red.\n\n"
            "Sé sincero: si tuvieras que salir en 5 minutos de tu casa, ¿ya tienes lista una mochila de emergencia o tendrías que improvisar? ¡Te leo en los comentarios!\n\n"
            "#supervivencia #emergencia #curiosidades #prevencion #tendencias"
        ),
        "caption": (
            "En una emergencia real, las decisiones que tomas en los primeros 30 minutos hacen toda la diferencia. "
            "Sé sincero: ¿cuántos de estos 5 puntos tienes listos hoy en casa o cuál te faltaría preparar? ¡Te leo en los comentarios! "
            "#reels #supervivencia #curiosidades #misterios #viral"
        ),
    },
]


def _get_episode_for_topic(topic: str) -> Dict[str, Any]:
    from youtube_story_animator import detect_theme_from_text

    t_low = topic.lower().strip()
    for ep in THEMATIC_EPISODES:
        if ep["topic"].lower() == t_low or t_low in ep["topic"].lower() or ep["topic"].lower() in t_low:
            return ep

    theme = detect_theme_from_text(topic)
    for ep in THEMATIC_EPISODES:
        if ep["theme"] == theme:
            return ep
    return THEMATIC_EPISODES[0]


def discover_trending_topic() -> tuple[str, str]:
    """
    Selecciona el siguiente episodio de formato largo asegurando rotación real
    sin repetir nunca el mismo tema consecutivo (incluso si se ejecuta en la nube).
    """
    print("[Tendencias] Seleccionando siguiente episodio animado de alta retención...")
    history_path = OUTPUT_DIR / "published_topics.json"
    published: List[str] = []
    if history_path.exists():
        try:
            published = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception:
            published = []

    # Filtrar episodios que NO sean el último publicado y usar semilla horaria para rotación en la nube
    recent_set = set(published[-4:])
    available = [ep for ep in THEMATIC_EPISODES if ep["topic"] not in recent_set]
    if not available:
        available = THEMATIC_EPISODES

    hour_slot = int(datetime.now().timestamp() // 3600)
    idx = (len(published) + hour_slot) % len(available)
    chosen_ep = available[idx]

    topic = chosen_ep["topic"]
    caption = chosen_ep["caption"]

    published.append(topic)
    history_path.write_text(json.dumps(published[-50:], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"      [Episodio elegido]: '{topic}' (Tema visual: {chosen_ep['theme']})")
    return topic, caption


def generate_script(topic: str) -> str:
    """
    Genera un guion documental largo (170 a 210 palabras, ~65-80 segundos) estructurado
    en 5 capítulos con gancho inicial y pregunta final de debate.
    """
    print(f"[1/4] Preparando guion de formato largo (5 capítulos, 65-80s) sobre: '{topic}'...")
    ep = _get_episode_for_topic(topic)

    system_instruction = (
        "Eres el guionista principal de canales de animación 2D como Don Zombi, Curiosamente Graficado y Sobrevive con Bruno. "
        "Escribe únicamente el texto hablado del narrador en español para un video de formato largo (entre 170 y 210 palabras, unos 70 segundos de duración). "
        "Reglas estrictas:\n"
        "- Divide la narrativa fluidamente en 5 capítulos o fases progresivas.\n"
        "- Comienza con una pregunta gancho muy potente y cierra con una pregunta abierta para que la audiencia debata en los comentarios.\n"
        "- NO incluyas etiquetas como '[Música]', 'Narrador:', asteriscos ni emojis.\n"
        "- Devuelve únicamente los párrafos limpios que leerá la voz."
    )

    # Si el tema coincide con uno de nuestros episodios maestros de 5 capítulos, usar su guion largo verificado
    if ep["topic"].lower() == topic.lower().strip():
        script_text = ep["script"]
        script_path = OUTPUT_DIR / "guion.txt"
        script_path.write_text(script_text, encoding="utf-8")
        print(f"      Guion largo de 5 capítulos ({len(script_text.split())} palabras) listo en: {script_path}")
        return script_text

    # Si es un tema personalizado nuevo, pedir guion largo de 185 palabras a Gemini REST
    custom_script = _call_gemini_fast(
        f"Escribe un guion documental narrativo de 185 palabras en 5 capítulos sobre: {topic}",
        system_instruction=system_instruction,
        timeout_sec=12.0,
    )
    if custom_script and len(custom_script.split()) >= 120:
        script_path = OUTPUT_DIR / "guion.txt"
        script_path.write_text(custom_script, encoding="utf-8")
        return custom_script

    script_text = ep["script"]
    script_path = OUTPUT_DIR / "guion.txt"
    script_path.write_text(script_text, encoding="utf-8")
    return script_text


def _plan_visual_scenes(script_text: str, num_scenes: int = 5, topic: str = "") -> List[Dict[str, str]]:
    """
    Devuelve los 5 capítulos visuales sincronizados exactamente con el guion y el tema.
    """
    ep = _get_episode_for_topic(topic or script_text)
    if len(ep.get("scenes", [])) >= num_scenes:
        return ep["scenes"][:num_scenes]
    return ep["scenes"]


def _draw_multiline_headline(
    draw: ImageDraw.ImageDraw,
    headline: str,
    subheadline: str,
    accent_color: tuple[int, int, int] = (215, 35, 35),
) -> None:
    """
    Dibuja el titular y subtítulo en la parte inferior de la postal 1080x1350
    ajustando automáticamente el tamaño de fuente y dividiendo en 2 líneas si es largo
    para que JAMÁS se corte una sola letra.
    """
    draw.rectangle([0, 945, 1080, 1350], fill=(0, 0, 0, 195))
    draw.line([(0, 945), (1080, 945)], fill=accent_color + (255,), width=6)

    bold_path = r"C:\Windows\Fonts\impact.ttf" if Path(r"C:\Windows\Fonts\impact.ttf").exists() else r"C:\Windows\Fonts\arialbd.ttf"
    reg_path = r"C:\Windows\Fonts\arialbd.ttf"

    words = headline.strip().upper().split()
    if len(words) >= 4 and len(headline) > 20:
        mid = (len(words) + 1) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [headline.strip().upper()]

    # Encontrar el tamaño de fuente ideal para que quepa con margen amplio
    font_sz = 64
    while font_sz > 36:
        f_test = ImageFont.truetype(bold_path, font_sz) if Path(bold_path).exists() else ImageFont.load_default()
        max_w = max((draw.textbbox((0, 0), ln, font=f_test)[2] - draw.textbbox((0, 0), ln, font=f_test)[0]) for ln in lines)
        if max_w <= 980:
            break
        font_sz -= 4

    font_h = ImageFont.truetype(bold_path, font_sz) if Path(bold_path).exists() else ImageFont.load_default()

    if len(lines) == 1:
        draw.text(
            (540, 1065),
            lines[0],
            font=font_h,
            fill=(255, 255, 255, 255),
            anchor="mm",
            stroke_width=6,
            stroke_fill=(0, 0, 0, 255),
        )
    else:
        draw.text(
            (540, 1022),
            lines[0],
            font=font_h,
            fill=(255, 255, 255, 255),
            anchor="mm",
            stroke_width=6,
            stroke_fill=(0, 0, 0, 255),
        )
        draw.text(
            (540, 1098),
            lines[1],
            font=font_h,
            fill=(255, 235, 0, 255),
            anchor="mm",
            stroke_width=6,
            stroke_fill=(0, 0, 0, 255),
        )

    sub_clean = subheadline.strip().upper()
    sub_sz = 36
    while sub_sz > 24:
        f_sub_test = ImageFont.truetype(reg_path if Path(reg_path).exists() else bold_path, sub_sz)
        sb = draw.textbbox((0, 0), sub_clean, font=f_sub_test)
        if (sb[2] - sb[0]) <= 880:
            break
        sub_sz -= 2

    font_s = ImageFont.truetype(reg_path if Path(reg_path).exists() else bold_path, sub_sz)
    sb = draw.textbbox((0, 0), sub_clean, font=font_s)
    sw = sb[2] - sb[0]
    bx1 = max(70, 540 - sw // 2 - 34)
    bx2 = min(1010, 540 + sw // 2 + 34)

    draw.rounded_rectangle(
        [bx1, 1175, bx2, 1255],
        radius=16,
        fill=accent_color + (245,),
        outline=(255, 255, 255, 220),
        width=3,
    )
    draw.text(
        (540, 1215),
        sub_clean,
        font=font_s,
        fill=(255, 255, 255, 255),
        anchor="mm",
    )


def generate_story_post(topic: str, with_image: bool = True) -> tuple[str, Path | None]:
    """
    Genera una publicación narrativa en el muro de Facebook cuya ilustración cómic 2D
    coincide al 100% con el tema descrito (CERO imágenes sin sentido o rostros deformes).
    """
    print(f"[Historia] Redactando historia viral coherente para Facebook sobre: '{topic}'...")
    ep = _get_episode_for_topic(topic)
    story_text = ep["story"]
    headline = ep["headline"]
    subheadline = ep["subheadline"]
    theme = ep["theme"]

    story_path = OUTPUT_DIR / "story_post.txt"
    story_path.write_text(story_text, encoding="utf-8")

    if not with_image:
        return story_text, None

    seed_val = abs(hash(topic)) % 900 + 100
    print(f"[Imagen] Creando postal ilustrada 2D cómic 100% del tema '{theme}' (1080x1350)...")
    from youtube_story_animator import fetch_or_generate_comic_art

    art_path = fetch_or_generate_comic_art(
        prompt=topic,
        dest_path=OUTPUT_DIR / f"post_comic_{theme}_{seed_val}.png",
        seed=seed_val,
        theme=theme,
    )
    raw_img = Image.open(art_path).convert("RGB")

    card = ImageOps.fit(raw_img, (1080, 1350), method=Image.Resampling.LANCZOS)
    card = ImageEnhance.Color(card).enhance(1.12)
    draw = ImageDraw.Draw(card, "RGBA")

    accent_map = {
        "ocean": (0, 145, 210),
        "blackout": (215, 35, 35),
        "prehistory": (215, 85, 25),
        "island": (25, 145, 85),
        "jungle": (25, 145, 75),
        "space": (135, 45, 215),
        "zombie": (215, 35, 35),
    }
    _draw_multiline_headline(draw, headline, subheadline, accent_color=accent_map.get(theme, (215, 35, 35)))

    img_out = OUTPUT_DIR / "post_image.jpg"
    card.save(img_out, quality=95)
    print(f"      Imagen temática verificada guardada en: {img_out}")
    return story_text, img_out


def generate_engaging_video_caption(topic: str, script_text: str) -> str:
    """
    Devuelve una descripción sumamente atractiva con pregunta abierta de debate
    100% conectada con el tema del video para multiplicar comentarios.
    """
    ep = _get_episode_for_topic(topic)
    if ep.get("caption"):
        return ep["caption"]

    return (
        f"¿Te imaginas estar en medio de esto? {topic}. "
        "Mira los 5 capítulos del video hasta el final porque el último dato cambia todo. "
        "¿Tú qué harías en esta situación o cuál sería tu plan para sobrevivir? ¡Te leo en los comentarios! "
        "#reels #curiosidades #supervivencia #misterios #viral"
    )


def run_generation_pipeline(topic: str) -> tuple[Path, Path]:
    script_text = generate_script(topic)
    scenes_meta = _plan_visual_scenes(script_text, num_scenes=5, topic=topic)
    meta_path = OUTPUT_DIR / "scenes_meta.json"
    meta_path.write_text(json.dumps(scenes_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    audio_path = OUTPUT_DIR / "narration.mp3"
    video_base_path = OUTPUT_DIR / "video_base.mp4"
    return video_base_path, audio_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 1: Generación de guion largo y escenas 2D.")
    parser.add_argument(
        "--topic",
        type=str,
        default="El misterio de la Fosa de las Marianas: qué vive realmente a 11 kilómetros bajo el océano",
        help="Tema sobre el cual se escribirá el guion.",
    )
    args = parser.parse_args()
    run_generation_pipeline(args.topic)
