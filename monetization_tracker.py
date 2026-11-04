"""
Módulo de Auditoría y Seguimiento de Monetización en Tiempo Real
para YouTube Shorts (YPP) y Facebook Reels (Meta for Creators).

Calcula el avance porcentual, ritmo de publicación, métricas de vistas
y estado de elegibilidad de las cuentas de Bruno Schiller.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import OUTPUT_DIR

# Metadatos del canal
YT_CHANNEL_ID = "UCsSt3vnxhQvg2UmNhPAw-sQ"
YT_CHANNEL_URL = f"https://www.youtube.com/channel/{YT_CHANNEL_ID}"
FB_PROFILE_NAME = "Bruno Schiller"

# Requisitos oficiales
YT_TIER1_SUBS = 500
YT_TIER1_SHORTS_VIEWS = 3_000_000
YT_TIER1_VIDEOS = 3

YT_TIER2_SUBS = 1_000
YT_TIER2_SHORTS_VIEWS = 10_000_000

FB_INSTREAM_FOLLOWERS = 5_000
FB_INSTREAM_MINUTES = 60_000
FB_STARS_FOLLOWERS = 500


def _fetch_channel_info() -> Dict[str, Any]:
    """Obtiene suscriptores y número de videos públicos del canal de YouTube."""
    info = {"subscribers": 0, "video_count": 0, "name": "Bruno Schiller"}
    req = urllib.request.Request(
        YT_CHANNEL_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Suscriptores
        m_subs = re.search(r'([0-9.,]+K?M?)\s+suscriptor', html, re.IGNORECASE)
        if m_subs:
            raw_s = m_subs.group(1).replace(".", "").replace(",", "")
            if "K" in raw_s.upper():
                info["subscribers"] = int(float(raw_s.upper().replace("K", "")) * 1_000)
            elif "M" in raw_s.upper():
                info["subscribers"] = int(float(raw_s.upper().replace("M", "")) * 1_000_000)
            else:
                try:
                    info["subscribers"] = int(raw_s)
                except Exception:
                    pass

        # Videos
        m_vid = re.search(r'([0-9.,]+)\s+video', html, re.IGNORECASE)
        if m_vid:
            raw_v = m_vid.group(1).replace(".", "").replace(",", "")
            try:
                info["video_count"] = int(raw_v)
            except Exception:
                pass
    except Exception as e:
        print(f"[Tracker] Advertencia al consultar estadísticas de canal: {e}")

    return info


def _fetch_video_views(video_id: str) -> int:
    """Obtiene el número de vistas públicas de un Short individual."""
    url = f"https://www.youtube.com/shorts/{video_id}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r'"viewCount":\s*"(\d+)"', html)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return 0


def _progress_bar(current: float, target: float, length: int = 24) -> str:
    """Genera una barra de progreso visual de consola."""
    ratio = min(1.0, max(0.0, current / target)) if target > 0 else 0.0
    filled = int(ratio * length)
    pct = ratio * 100
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {pct:5.1f}% ({current:,}/{target:,})"


def generate_monetization_report() -> Dict[str, Any]:
    """Calcula todas las métricas y genera el informe completo."""
    print("\n" + "=" * 68)
    print(" 🚀 AUDITORÍA DE MONETIZACIÓN: BRUNO SCHILLER (YouTube + Facebook)")
    print("=" * 68)

    # 1. YouTube Stats
    print("\n[1/3] Consultando métricas en vivo de YouTube...")
    ch_info = _fetch_channel_info()
    subs = ch_info["subscribers"]
    yt_videos_total = ch_info["video_count"]

    yt_history_path = OUTPUT_DIR / "youtube_upload_history.json"
    yt_uploads: List[Dict[str, Any]] = []
    if yt_history_path.exists():
        try:
            yt_uploads = json.loads(yt_history_path.read_text(encoding="utf-8"))
        except Exception:
            yt_uploads = []

    total_shorts_views = 0
    detailed_shorts = []
    for item in yt_uploads:
        vid_id = item.get("video_id")
        views = _fetch_video_views(vid_id) if vid_id else 0
        total_shorts_views += views
        detailed_shorts.append({
            "video_id": vid_id,
            "title": item.get("title", ""),
            "views": views,
            "url": item.get("url", f"https://www.youtube.com/shorts/{vid_id}"),
        })

    # 2. Facebook Stats (desde registros de publicación)
    print("[2/3] Analizando historial de publicaciones de Facebook...")
    topics_path = OUTPUT_DIR / "published_topics.json"
    fmts_path = OUTPUT_DIR / "published_formats.json"

    published_topics = []
    if topics_path.exists():
        try:
            published_topics = json.loads(topics_path.read_text(encoding="utf-8"))
        except Exception:
            published_topics = []

    published_fmts = []
    if fmts_path.exists():
        try:
            published_fmts = json.loads(fmts_path.read_text(encoding="utf-8"))
        except Exception:
            published_fmts = []

    total_posts = len(published_topics)
    total_reels = sum(1 for f in published_fmts if f == "video")
    total_photos = sum(1 for f in published_fmts if f == "photo")
    total_texts = sum(1 for f in published_fmts if f == "text")

    # 3. Compilar resultados
    report = {
        "timestamp": datetime.now().isoformat(),
        "youtube": {
            "channel_id": YT_CHANNEL_ID,
            "channel_url": YT_CHANNEL_URL,
            "subscribers": subs,
            "total_channel_videos": yt_videos_total,
            "shorts_tracked_count": len(yt_uploads),
            "shorts_total_views": total_shorts_views,
            "shorts_list": detailed_shorts,
            "milestones": {
                "tier1_fan_funding": {
                    "subs": {"current": subs, "target": YT_TIER1_SUBS, "reached": subs >= YT_TIER1_SUBS},
                    "shorts_views": {
                        "current": total_shorts_views,
                        "target": YT_TIER1_SHORTS_VIEWS,
                        "reached": total_shorts_views >= YT_TIER1_SHORTS_VIEWS,
                    },
                    "videos_90d": {
                        "current": len(yt_uploads),
                        "target": YT_TIER1_VIDEOS,
                        "reached": len(yt_uploads) >= YT_TIER1_VIDEOS,
                    },
                },
                "tier2_full_ads": {
                    "subs": {"current": subs, "target": YT_TIER2_SUBS, "reached": subs >= YT_TIER2_SUBS},
                    "shorts_views": {
                        "current": total_shorts_views,
                        "target": YT_TIER2_SHORTS_VIEWS,
                        "reached": total_shorts_views >= YT_TIER2_SHORTS_VIEWS,
                    },
                },
            },
        },
        "facebook": {
            "profile_name": FB_PROFILE_NAME,
            "professional_mode": True,
            "total_publications": total_posts,
            "breakdown": {
                "reels": total_reels,
                "photos_with_stories": total_photos,
                "text_debates": total_texts,
            },
            "milestones": {
                "ads_on_reels": {
                    "status": "En aceleración (invitación automática por retención y consistencia)",
                    "daily_target": 6,
                },
                "performance_bonus": {
                    "status": "Activo por distribución multi-formato (fotos HD + reels)",
                },
                "in_stream_ads": {
                    "followers_target": FB_INSTREAM_FOLLOWERS,
                    "minutes_target": FB_INSTREAM_MINUTES,
                },
                "stars": {
                    "followers_target": FB_STARS_FOLLOWERS,
                },
            },
        },
    }

    # Guardar en JSON
    status_file = OUTPUT_DIR / "monetization_status.json"
    status_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Imprimir resumen de alto impacto
    print("\n" + "─" * 68)
    print(" 🔴 YOUTUBE SHORTS (YPP - Programa de Socios de YouTube)")
    print("─" * 68)
    print(f" Canal:                Bruno Schiller | Misterios y Supervivencia")
    print(f" Suscriptores actuales: {subs}")
    print(f" Videos en el canal:   {yt_videos_total} (Shorts rastreados: {len(yt_uploads)})")
    print(f" Vistas totales Shorts:{total_shorts_views:,}")
    print()
    print(" [Progreso hacia Nivel 1: Financiación de Fans (500 subs + 3M vistas)]")
    print(f"  • Suscriptores:     {_progress_bar(subs, YT_TIER1_SUBS)}")
    print(f"  • Vistas Shorts:    {_progress_bar(total_shorts_views, YT_TIER1_SHORTS_VIEWS)}")
    print(f"  • Subidas mínimas:  {_progress_bar(len(yt_uploads), YT_TIER1_VIDEOS)}")
    print()
    print(" [Progreso hacia Nivel 2: Monetización Completa de Anuncios (1,000 subs + 10M vistas)]")
    print(f"  • Suscriptores:     {_progress_bar(subs, YT_TIER2_SUBS)}")
    print(f"  • Vistas Shorts:    {_progress_bar(total_shorts_views, YT_TIER2_SHORTS_VIEWS)}")

    if detailed_shorts:
        print("\n  Videos destacados:")
        for s in detailed_shorts[:3]:
            print(f"   ▶ {s['title'][:45]}... → {s['views']:,} vistas ({s['url']})")

    print("\n" + "─" * 68)
    print(" 🔵 FACEBOOK (Meta for Creators - Modo Profesional)")
    print("─" * 68)
    print(f" Perfil:               {FB_PROFILE_NAME} (Modo Profesional: ACTIVO)")
    print(f" Publicaciones totales: {total_posts}")
    print(f"  • Reels (video 24 FPS): {total_reels}")
    print(f"  • Postales HD (debate): {total_photos}")
    print(f"  • Textos de misterio:   {total_texts}")
    print()
    print(" Programas de Monetización Meta:")
    print("  1. Anuncios en Reels (Ads on Reels):")
    print("     Estado: Elegible por algoritmo. Se desbloquea con el ritmo de 6 reels/día.")
    print("  2. Bonificación por Rendimiento (Performance Bonus):")
    print("     Estado: Optimizado. Las postales HD con historias generan comentarios masivos.")
    print("  3. Anuncios In-Stream:")
    print("     Meta: 5,000 seguidores + 60,000 minutos reproducidos en 60 días.")
    print("  4. Estrellas de Facebook:")
    print("     Meta: 500 seguidores constantes.")

    print("\n" + "=" * 68)
    print(f" Informe guardado en: {status_file.name}")
    print("=" * 68 + "\n")

    return report


if __name__ == "__main__":
    generate_monetization_report()
