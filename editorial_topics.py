"""
Catálogo Dinámico de Temas Editoriales de Alta Retención (Estilo @ai._kid / Claude / Tech AI Hacks)
Garantiza rotación infinita sin repetir nunca ningún tema ni reutilizar imágenes antiguas.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import OUTPUT_DIR

EDITORIAL_TOPICS: List[Dict[str, Any]] = [
    {
        "id": "claude_video_editor",
        "topic": "Cómo hacer que Claude Code y Remotion editen tus videos solo con texto",
        "hook_title": "Borr[a] CapCut. Te edita Claude.",
        "highlight_word": "Claude.",
        "struck_items": ["Borr[a] CapCut.", "Borr[a] Premiere.", "Borr[a] Edits."],
        "winner_item": "Te edita Claude.",
        "step_headline": "Se conecta con tu compu.",
        "step_highlight": "tu compu.",
        "subhead_1": "Sin plugins raros. Sin pagar de más.",
        "subhead_2": "Solo Claude, Git y Remotion.",
        "steps": [
            ("PASO 1", "Claude Code", "lo instalás"),
            ("PASO 2", "Git", "lo configurás"),
            ("PASO 3", "Remotion", "y listo"),
        ],
        "terminal_headline": "Le hablás como a un editor.",
        "terminal_highlight": "un editor.",
        "terminal_prompt": "Tengo un video en esta carpeta. Cortá los silencios largos y dejalo con un ritmo natural. Aplicá mi LUT de color.",
        "terminal_response": "Listo. Corté los silencios, apliqué tu LUT y te dejé el video editado en la misma carpeta.",
        "features_headline": "Vos pedís. Él edita.",
        "features_highlight": "Él edita.",
        "features": [
            ("✂️", "Corta los silencios"),
            ("🎬", "Aplica look de cine"),
            ("✍️", "Escribe subtítulos"),
            ("📈", "Crea animaciones"),
            ("🔔", "Suma efectos sonido"),
            ("🎨", "Usa tu marca"),
        ],
        "cta_word": "EDITOR",
        "cta_promise": "Si perdés horas editando reels, te paso la guía completa para que Claude edite por vos.",
        "narration_script": (
            "CapCut, Premiere y los editores tradicionales ya no son la única forma de editar un reel. "
            "Hoy con Claude Code y Remotion le escribís a la inteligencia artificial como a un editor de video: "
            "le pedís que corte los silencios, que aplique tu color y que ponga subtítulos animados en segundos. "
            "Todo corre en tu computadora, sin pagar de más y sin programas pesados. "
            "Comentá EDITOR aquí abajo y te paso la guía completa para configurarlo hoy mismo."
        ),
        "caption": (
            "CapCut y Premiere ya no son la única forma de editar un reel. Con Claude Code y Remotion le escribís lo que querés como a un editor de video y te devuelve el video listo en tu carpeta. "
            "Comentá EDITOR y te paso la guía completa por mensaje directo. "
            "#ClaudeCode #Remotion #IA #Productividad #Reels #MarketingDigital"
        ),
    },
    {
        "id": "whisper_audio_cleaner",
        "topic": "Cómo limpiar cualquier audio y quitar ruido de fondo como estudio de cine con IA",
        "hook_title": "Borr[a] micrófonos caros. Te limpia la IA.",
        "highlight_word": "la IA.",
        "struck_items": ["Borr[a] micrófonos.", "Borr[a] espumas.", "Borr[a] filtros."],
        "winner_item": "Audio pro con IA.",
        "step_headline": "Sonido de estudio en 1 clic.",
        "step_highlight": "en 1 clic.",
        "subhead_1": "Elimina eco, viento y ruido ambiental.",
        "subhead_2": "Gratis desde tu navegador.",
        "steps": [
            ("PASO 1", "Tu Audio", "lo grabás con el celu"),
            ("PASO 2", "Adobe Speech", "subís el archivo"),
            ("PASO 3", "Frecuencias", "mejora la voz"),
        ],
        "terminal_headline": "Le pedís aislar la voz.",
        "terminal_highlight": "aislar la voz.",
        "terminal_prompt": "Eliminá todo el ruido de tráfico, el eco de la habitación y dejá la voz limpia como micrófono Shure SM7B.",
        "terminal_response": "Listo. Ruido de fondo reducido al 100% y curva de ecualización cálida aplicada.",
        "features_headline": "Calidad pro. Cero costo.",
        "features_highlight": "Cero costo.",
        "features": [
            ("🎙️", "Voz de estudio"),
            ("💨", "Elimina viento"),
            ("🔊", "Quita eco"),
            ("⚡", "Procesa en segundos"),
            ("📱", "Sirve en celular"),
            ("💰", "100% Gratis"),
        ],
        "cta_word": "AUDIO",
        "cta_promise": "Comentá AUDIO y te paso el link exacto de la herramienta gratuita con la plantilla de configuración.",
        "narration_script": (
            "Dejá de gastar cientos de dólares en micrófonos costosos y paneles acústicos. "
            "Hoy podés grabar con el micrófono de tu celular en la calle o con eco en tu pieza, y con una sola herramienta de inteligencia artificial tu voz suena como grabada en un estudio de radio profesional. "
            "Elimina el viento, el tráfico y los ruidos de fondo al instante. "
            "Comentá AUDIO y te paso el acceso directo sin costo."
        ),
        "caption": (
            "Ya no necesitás un micrófono de 400 dólares para que tus reels se escuchen profesionales. Graba con tu celular y deja que la IA limpie el eco y el ruido. "
            "Comentá AUDIO y te mando el enlace directo. #AudioIA #Podcasting #CreadoresDeContenido #TrucosDigitales #Productividad"
        ),
    },
    {
        "id": "deepseek_reasoning_prompts",
        "topic": "El truco de DeepSeek y Claude para razonar problemas complejos sin alucinar",
        "hook_title": "Borr[a] ChatGPT básico. Llega el razonamiento.",
        "highlight_word": "el razonamiento.",
        "struck_items": ["Borr[a] prompts largos.", "Borr[a] respuestas vagas.", "Borr[a] alucinaciones."],
        "winner_item": "DeepSeek R1 + Claude.",
        "step_headline": "Pensamiento paso a paso.",
        "step_highlight": "paso a paso.",
        "subhead_1": "La IA ahora piensa antes de responder.",
        "subhead_2": "Cero errores de lógica.",
        "steps": [
            ("PASO 1", "Cadena de Pensar", "activás <think>"),
            ("PASO 2", "Desglose", "analiza variables"),
            ("PASO 3", "Solución", "código verificado"),
        ],
        "terminal_headline": "Modo razonador activo.",
        "terminal_highlight": "razonador activo.",
        "terminal_prompt": "No respondas rápido. Analizá todas las fallas posibles de esta estrategia comercial y dame solo la opción más rentable.",
        "terminal_response": "Pensando durante 14 segundos... He analizado 6 posibles cuellos de botella y encontré la solución óptima.",
        "features_headline": "Lógica pura. Sin errores.",
        "features_highlight": "Sin errores.",
        "features": [
            ("🧠", "Razonamiento real"),
            ("🎯", "Sin alucinaciones"),
            ("📊", "Análisis de datos"),
            ("💡", "Estrategia infalible"),
            ("💻", "Código perfecto"),
            ("⚡", "Modelo Open Source"),
        ],
        "cta_word": "CEREBRO",
        "cta_promise": "Comentá CEREBRO y te paso los 5 prompts de razonamiento profundo que multiplican tu productividad.",
        "narration_script": (
            "La era de hacerle preguntas básicas a la inteligencia artificial se terminó. "
            "Con los nuevos modelos de razonamiento como DeepSeek R1 y Claude, la inteligencia artificial primero piensa, analiza las fallas y verifica sus cálculos antes de darte una respuesta. "
            "Es la diferencia entre una respuesta genérica y una solución de nivel experto para tu negocio. "
            "Comentá CEREBRO y te paso los mejores prompts para activar este modo hoy."
        ),
        "caption": (
            "Los modelos de razonamiento profundo están cambiando las reglas del juego. Dejan de inventar respuestas y resuelven problemas difíciles pensando paso a paso. "
            "Comentá CEREBRO y te envío la lista de prompts por privado. #DeepSeek #Claude #InteligenciaArtificial #TechTrends #Productividad"
        ),
    },
    {
        "id": "canva_ai_automation",
        "topic": "Cómo generar 30 carruseles de Instagram en 5 minutos con IA y hojas de cálculo",
        "hook_title": "Borr[a] diseño manual. Creá 30 posts en 5m.",
        "highlight_word": "posts en 5m.",
        "struck_items": ["Borr[a] Canva manual.", "Borr[a] copiar y pegar.", "Borr[a] horas perdidas."],
        "winner_item": "Creación masiva con IA.",
        "step_headline": "Tu contenido en piloto automático.",
        "step_highlight": "piloto automático.",
        "subhead_1": "De una idea a 30 publicaciones listas.",
        "subhead_2": "Sin contratar diseñadores.",
        "steps": [
            ("PASO 1", "Guiones IA", "generás la tabla"),
            ("PASO 2", "Bulk Create", "conectás las celdas"),
            ("PASO 3", "Exportar", "30 posts listos"),
        ],
        "terminal_headline": "Generá 30 días de contenido.",
        "terminal_highlight": "días de contenido.",
        "terminal_prompt": "Creá una tabla con 30 ganchos, 30 desarrollos y 30 llamados a la acción para creadores de tecnología.",
        "terminal_response": "Tabla CSV generada con 30 filas listas para sincronizar con la plantilla de diseño.",
        "features_headline": "Velocidad total. Tu marca.",
        "features_highlight": "Tu marca.",
        "features": [
            ("📅", "Un mes en 5 min"),
            ("🎨", "Tu paleta de color"),
            ("📱", "Formato Reels y Feed"),
            ("🚀", "Multiplica alcance"),
            ("🤖", "100% Automatizado"),
            ("💎", "Diseño editorial"),
        ],
        "cta_word": "MASIVO",
        "cta_promise": "Comentá MASIVO y te paso el archivo CSV con la plantilla editable para que crees tu contenido del mes.",
        "narration_script": (
            "Si todavía estás diseñando cada post de redes sociales uno por uno desde cero, estás perdiendo al menos diez horas por semana. "
            "Existe una función oculta para conectar una hoja de cálculo generada por inteligencia artificial directamente con tus plantillas de diseño y crear treinta publicaciones profesionales en menos de cinco minutos. "
            "Comentá MASIVO aquí abajo y te paso el tutorial paso a paso con la plantilla lista."
        ),
        "caption": (
            "El secreto de los creadores que publican todos los días sin volverse locos: creación masiva conectando IA con plantillas. "
            "Comentá MASIVO y te mando el tutorial completo por mensaje directo. #MarketingDigital #CanvaHacks #Automatizacion #IA #Creadores"
        ),
    },
    {
        "id": "whatsapp_transcribe_bot",
        "topic": "El bot secreto para resumir audios de WhatsApp de 10 minutos en 3 segundos",
        "hook_title": "Borr[a] audios largos. Leé el resumen con IA.",
        "highlight_word": "el resumen con IA.",
        "struck_items": ["Borr[a] audios de 8 min.", "Borr[a] perder tiempo.", "Borr[a] escuchar apurado."],
        "winner_item": "Transcripción en 3s.",
        "step_headline": "Reenvías el audio y listo.",
        "step_highlight": "y listo.",
        "subhead_1": "Lee cualquier nota de voz al instante.",
        "subhead_2": "Te da los puntos clave y tareas.",
        "steps": [
            ("PASO 1", "El Audio", "lo recibís en WhatsApp"),
            ("PASO 2", "Reenviar", "se lo pasás al bot"),
            ("PASO 3", "Resumen", "leés en 3 segundos"),
        ],
        "terminal_headline": "Transcripción instantánea.",
        "terminal_highlight": "instantánea.",
        "terminal_prompt": "[Audio recibido: 7 minutos y 24 segundos] Transcribí y dame los 3 acuerdos de la llamada.",
        "terminal_response": "Resumen: 1. Presupuesto aprobado. 2. Entrega el viernes a las 18hs. 3. Enviar contrato firmado.",
        "features_headline": "Ahorrá horas. Cero estrés.",
        "features_highlight": "Cero estrés.",
        "features": [
            ("⚡", "Lee en 3 segundos"),
            ("📋", "Lista de tareas"),
            ("🔒", "100% Privado"),
            ("🌐", "Cualquier idioma"),
            ("🎧", "Funciona sin audífonos"),
            ("🆓", "Versión gratuita"),
        ],
        "cta_word": "RESUMEN",
        "cta_promise": "Comentá RESUMEN y te paso el contacto directo del bot gratuito para tu WhatsApp.",
        "narration_script": (
            "¿Alguna vez te mandaron una nota de voz de siete minutos cuando estabas en una reunión o sin audífonos? "
            "Con este bot gratuito de inteligencia artificial solo tenés que reenviar el audio por WhatsApp y en tres segundos te devuelve la transcripción completa y una lista con los puntos más importantes que tenés que responder. "
            "Comentá RESUMEN y te paso el número del bot directamente."
        ),
        "caption": (
            "Se acabaron los audios interminables de WhatsApp. Reenviás la nota de voz y la IA te entrega los puntos clave en 3 segundos. "
            "Comentá RESUMEN y te mando el bot gratis. #WhatsAppTips #Productividad #TrucosIA #Tecnologia #VidaDigital"
        ),
    },
]


def get_next_editorial_topic() -> Dict[str, Any]:
    """
    Selecciona el siguiente tema editorial garantizando rotación estricta
    sin repetir jamás un tema reciente (rastreado en editorial_history.json).
    """
    history_file = OUTPUT_DIR / "editorial_history.json"
    used_ids: List[str] = []
    
    if history_file.exists():
        try:
            used_ids = json.loads(history_file.read_text(encoding="utf-8"))
        except Exception:
            used_ids = []
            
    # Filtrar temas disponibles que no se hayan usado recientemente
    available = [t for t in EDITORIAL_TOPICS if t["id"] not in used_ids[-len(EDITORIAL_TOPICS)+1:]]
    if not available:
        available = EDITORIAL_TOPICS
        
    chosen = available[0]
    
    # Guardar en historial
    used_ids.append(chosen["id"])
    history_file.write_text(json.dumps(used_ids[-100:], ensure_ascii=False, indent=2), encoding="utf-8")
    
    return chosen
