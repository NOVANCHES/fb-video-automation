"""
script_bank_manager.py
======================
Gestor del Banco Masivo de Guiones (banco_masivo_de_guiones_para_automatizaci_n.txt).
Maneja lectura, selección del primer guion PENDIENTE, construcción de metadatos
y actualización atómica a PUBLICADO para evitar repeticiones.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PRIMARY_PATH = Path(r"c:\Users\olou1\Downloads\banco_masivo_de_guiones_para_automatizaci_n.txt")
BACKUP_PATH = Path(__file__).parent / "banco_guiones.txt"
LOG_HISTORY = Path(__file__).parent / "output" / "published_scripts.json"


def _get_active_file() -> Path:
    if PRIMARY_PATH.exists():
        return PRIMARY_PATH
    return BACKUP_PATH


def parse_all_scripts(filepath: Optional[Path] = None) -> List[Dict[str, Any]]:
    path = filepath or _get_active_file()
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    blocks = [
        b.strip()
        for b in text.split("================================================================================")
        if b.strip() and "ID:" in b
    ]

    scripts = []
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        data: Dict[str, Any] = {}
        header = lines[0]

        # ID, Categoría, Estado
        id_match = re.search(r"ID:\s*([A-Za-z0-9_\-]+)", header)
        cat_match = re.search(r"CATEGOR[IÍ]A:\s*([^|]+)", header)
        status_match = re.search(r"\[ESTADO:\s*([^\]]+)\]", header)

        data["id"] = id_match.group(1).strip() if id_match else "UNKNOWN"
        data["category"] = cat_match.group(1).strip() if cat_match else "General"
        data["status"] = status_match.group(1).strip().upper() if status_match else "PENDIENTE"

        for line in lines[1:]:
            if line.startswith("TÍTULO:") or line.startswith("TITULO:"):
                data["title"] = line.split(":", 1)[1].strip()
            elif line.startswith("VISUALES:"):
                data["visuals"] = line.split(":", 1)[1].strip()
            elif line.startswith("GANCHO:"):
                data["hook"] = line.split(":", 1)[1].strip()
            elif line.startswith("CUERPO:"):
                data["body"] = line.split(":", 1)[1].strip()
            elif line.startswith("CIERRE:"):
                data["close"] = line.split(":", 1)[1].strip()

        # Construir script completo para TTS
        hook = data.get("hook", "")
        body = data.get("body", "")
        close = data.get("close", "")
        title = data.get("title", "")

        narration = f"{hook} {body} {close}".strip()
        data["narration_script"] = narration
        data["script"] = narration
        data["topic"] = title
        data["theme_id"] = data["id"].lower().replace("-", "_")

        # Hashtags dinámicos según categoría
        cat_lower = data["category"].lower()
        cat_tags = "#Curiosidades #Ciencia"
        if "tecnolog" in cat_lower or "ia" in cat_lower or "seguridad" in cat_lower:
            cat_tags = "#Tecnologia #Trucos #Seguridad #IA"
        elif "psicolog" in cat_lower or "vida" in cat_lower:
            cat_tags = "#Psicologia #Mente #DatosCuriosos"
        elif "finanz" in cat_lower or "negocio" in cat_lower:
            cat_tags = "#Finanzas #Dinero #Negocios #Ahorro"
        elif "espacio" in cat_lower or "misterio" in cat_lower:
            cat_tags = "#Misterios #Espacio #Universo #Ciencia"
        elif "salud" in cat_lower or "cuerpo" in cat_lower:
            cat_tags = "#Salud #CuerpoHumano #Ciencia"
        elif "animal" in cat_lower or "naturaleza" in cat_lower:
            cat_tags = "#Naturaleza #Animales #Planeta"

        data["caption"] = (
            f"🔍 {title}\n\n"
            f"{hook}\n\n"
            f"{body}\n\n"
            f"👇 {close}\n\n"
            f"{cat_tags} #BrunoSchiller #Shorts #Reels #Viral"
        )
        data["yt_title"] = f"🔍 {title} #Shorts"

        scripts.append(data)

    return scripts


def get_next_pending_script() -> Optional[Dict[str, Any]]:
    scripts = parse_all_scripts()
    for s in scripts:
        if s.get("status") == "PENDIENTE":
            return s
    return None


def mark_script_as_published(script_id: str, video_url: str = "") -> bool:
    """Actualiza el archivo del banco cambiando [ESTADO: PENDIENTE] a [ESTADO: PUBLICADO]."""
    updated_any = False
    for path in [PRIMARY_PATH, BACKUP_PATH]:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        # Patrón para cambiar el estado exacto de ese ID
        pattern = rf"(ID:\s*{re.escape(script_id)}\s*\|[^\[\n]+)\[ESTADO:\s*PENDIENTE\]"
        if re.search(pattern, content):
            new_content = re.sub(pattern, r"\1[ESTADO: PUBLICADO]", content)
            path.write_text(new_content, encoding="utf-8")
            updated_any = True
            print(f"[Banco Guiones] {path.name} actualizado: {script_id} -> PUBLICADO")

    # Registrar en log histórico local
    LOG_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    history = []
    if LOG_HISTORY.exists():
        try:
            history = json.loads(LOG_HISTORY.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append({
        "id": script_id,
        "timestamp": datetime.now().isoformat(),
        "video_url": video_url
    })
    LOG_HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    return updated_any


if __name__ == "__main__":
    next_s = get_next_pending_script()
    if next_s:
        print(f"Siguiente guion pendiente: {next_s['id']} - {next_s['title']}")
        print(f"Voz en off ({len(next_s['narration_script'].split())} palabras):\n{next_s['narration_script']}")
    else:
        print("No hay guiones pendientes en el banco.")
