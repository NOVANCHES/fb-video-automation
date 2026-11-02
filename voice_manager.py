"""
Gestor de Perfiles de Voz Neural (Edge-TTS) y Sistema de Rotación para A/B Testing.
Permite alternar de manera fluida y balanceada entre diferentes modelos neuronales,
tonos y velocidades para evitar monotonía y medir retención de audiencia en Facebook.
"""

from datetime import datetime
import json
from pathlib import Path
import random
from typing import Any, Dict, List, Optional

from config import OUTPUT_DIR

VOICE_PROFILES: List[Dict[str, Any]] = [
    {
        "id": "jorge_mx",
        "name": "Jorge (México)",
        "voice": "es-MX-JorgeNeural",
        "gender": "male",
        "default_rate": "+5%",
        "default_pitch": "+0Hz",
        "style": "documental_enérgico",
        "best_for": ["blackout", "zombie", "prehistory"],
    },
    {
        "id": "dalia_mx",
        "name": "Dalia (México)",
        "voice": "es-MX-DaliaNeural",
        "gender": "female",
        "default_rate": "+4%",
        "default_pitch": "+1Hz",
        "style": "misterio_intrigante",
        "best_for": ["ocean", "space", "island"],
    },
    {
        "id": "gonzalo_co",
        "name": "Gonzalo (Colombia)",
        "voice": "es-CO-GonzaloNeural",
        "gender": "male",
        "default_rate": "+3%",
        "default_pitch": "-2Hz",
        "style": "cine_documental_profundo",
        "best_for": ["ocean", "space", "jungle"],
    },
    {
        "id": "salome_co",
        "name": "Salomé (Colombia)",
        "voice": "es-CO-SalomeNeural",
        "gender": "female",
        "default_rate": "+5%",
        "default_pitch": "+0Hz",
        "style": "storytelling_viral_rapido",
        "best_for": ["blackout", "island", "prehistory"],
    },
    {
        "id": "alonso_us",
        "name": "Alonso (US Latino)",
        "voice": "es-US-AlonsoNeural",
        "gender": "male",
        "default_rate": "+4%",
        "default_pitch": "-1Hz",
        "style": "tension_dramatica_supervivencia",
        "best_for": ["space", "zombie", "blackout"],
    },
    {
        "id": "alex_pe",
        "name": "Alex (Perú)",
        "voice": "es-PE-AlexNeural",
        "gender": "male",
        "default_rate": "+4%",
        "default_pitch": "+0Hz",
        "style": "analitico_exploracion_cientifica",
        "best_for": ["jungle", "ocean", "prehistory"],
    },
]


def select_voice_profile(
    theme: str = "",
    topic: str = "",
    force_voice_id: str = "",
) -> Dict[str, Any]:
    """
    Selecciona el perfil de voz óptimo rotando entre locutores para A/B Testing continuo.
    Guarda el registro en `output/voice_ab_history.json` para monitorear qué voz retiene más audiencia.
    """
    history_file = OUTPUT_DIR / "voice_ab_history.json"
    history: List[Dict[str, Any]] = []
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
        except Exception:
            history = []

    if force_voice_id:
        match = [v for v in VOICE_PROFILES if v["id"] == force_voice_id or v["voice"] == force_voice_id]
        if match:
            chosen = match[0].copy()
        else:
            chosen = VOICE_PROFILES[0].copy()
    else:
        # Rotación balanceada para A/B testing: selecciona la voz que menos se haya usado recientemente
        last_voice_ids = [h.get("voice_id") for h in history[-3:] if h.get("voice_id")]
        candidates = [v for v in VOICE_PROFILES if v["id"] not in last_voice_ids]
        if not candidates:
            candidates = VOICE_PROFILES

        # Priorizar perfiles que se alineen bien con la temática si están disponibles
        if theme:
            theme_matches = [v for v in candidates if theme in v.get("best_for", [])]
            if theme_matches:
                candidates = theme_matches

        chosen_base = candidates[len(history) % len(candidates)]
        chosen = chosen_base.copy()

    # Variación micro-paramétrica para evitar que una misma voz suene idéntica (A/B testing dinámico)
    rate_jitter = random.choice(["+3%", "+4%", "+5%"])
    pitch_jitter = random.choice(["-2Hz", "-1Hz", "+0Hz", "+1Hz"])
    chosen["rate"] = rate_jitter
    chosen["pitch"] = pitch_jitter

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "theme": theme,
        "voice_id": chosen["id"],
        "voice_name": chosen["voice"],
        "gender": chosen["gender"],
        "rate": chosen["rate"],
        "pitch": chosen["pitch"],
        "style": chosen["style"],
    }
    history.append(log_entry)
    history_file.write_text(json.dumps(history[-60:], ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[Voz TTS - A/B Test] Locutor seleccionado: {chosen['name']} ({chosen['voice']})")
    print(f"                     Estilo: {chosen['style']} | Velocidad: {chosen['rate']} | Tono: {chosen['pitch']}")
    return chosen
