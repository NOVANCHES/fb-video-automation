"""
generate_gaming_branding.py
===========================
Genera los activos oficiales de marca para el perfil de Facebook transformado a VIDEOJUEGOS:
1. Avatar Gamer 1080x1080 circular con borde de neón.
2. Portada Gamer 1640x624 con estética arcade/cyberpunk y llamadas a la acción.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance

OUTPUT_DIR = Path(r"C:\Users\olou1\.gemini\antigravity\scratch\fb-video-automation\output")
BRAIN_DIR = Path(r"C:\Users\olou1\.gemini\antigravity\brain\0e89bc87-742f-464d-8583-8c0dd78d7d7e")


def create_gaming_branding():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    avatar_out = OUTPUT_DIR / "creator_avatar_gamer.jpg"
    cover_out = OUTPUT_DIR / "creator_cover_gamer.jpg"

    # 1. AVATAR GAMER
    # Buscar el gamer_avatar generado por el subagente
    avatar_candidates = sorted(list(BRAIN_DIR.glob("gamer_avatar*.jpg")), key=lambda p: p.stat().st_mtime, reverse=True)
    if avatar_candidates:
        base_av = Image.open(avatar_candidates[0]).convert("RGB")
        avatar = ImageOps.fit(base_av, (1080, 1080), method=Image.Resampling.LANCZOS)
    else:
        avatar = Image.new("RGB", (1080, 1080), (12, 14, 24))

    draw_av = ImageDraw.Draw(avatar, "RGBA")
    # Doble anillo de neón (Cyan #00E5FF y Amarillo #FFE500)
    draw_av.ellipse([20, 20, 1060, 1060], outline=(0, 229, 255, 255), width=18)
    draw_av.ellipse([34, 34, 1046, 1046], outline=(255, 230, 0, 180), width=8)
    avatar.save(avatar_out, quality=95)
    print(f"[Branding] Avatar Gamer guardado: {avatar_out}")

    # 2. PORTADA GAMER 1640x624
    cover = Image.new("RGB", (1640, 624), (10, 12, 20))
    draw_c = ImageDraw.Draw(cover, "RGBA")

    # Gradiente de fondo con iluminación cyberpunk (azul profundo a violeta oscuro)
    for y in range(624):
        r = int(12 + (y / 624) * 16)
        g = int(14 + (y / 624) * 8)
        b = int(28 + (y / 624) * 35)
        draw_c.line([(0, y), (1640, y)], fill=(r, g, b))

    # Rejilla cyberpunk retro en perspectiva inferior
    grid_color = (0, 229, 255, 35)
    for x in range(0, 1640, 60):
        draw_c.line([(x, 380), (x, 624)], fill=grid_color, width=2)
    for y in range(380, 624, 35):
        draw_c.line([(0, y), (1640, y)], fill=grid_color, width=2)

    # Si hay imágenes de escenas gamer, colocar un collage a los lados con máscara de opacidad
    scene_candidates = sorted(list(BRAIN_DIR.glob("gaming_ps2_scene*.jpg")), key=lambda p: p.stat().st_mtime, reverse=True)
    if scene_candidates:
        sc1 = Image.open(scene_candidates[0]).convert("RGB")
        sc1_fit = ImageOps.fit(sc1, (480, 624), method=Image.Resampling.LANCZOS)
        sc1_fit = ImageEnhance.Brightness(sc1_fit).enhance(0.45)
        cover.paste(sc1_fit, (1160, 0))

    if avatar_candidates:
        av_small = Image.open(avatar_candidates[0]).convert("RGB")
        av_small_fit = ImageOps.fit(av_small, (420, 624), method=Image.Resampling.LANCZOS)
        av_small_fit = ImageEnhance.Brightness(av_small_fit).enhance(0.40)
        cover.paste(av_small_fit, (0, 0))

    # Cuadro central con desenfoque e iluminación
    draw_c.rounded_rectangle([280, 95, 1360, 520], radius=28, fill=(8, 10, 16, 235), outline=(0, 229, 255, 255), width=6)
    draw_c.rounded_rectangle([292, 107, 1348, 508], radius=22, outline=(255, 230, 0, 120), width=2)

    bold_font_path = r"C:\Windows\Fonts\impact.ttf" if Path(r"C:\Windows\Fonts\impact.ttf").exists() else r"C:\Windows\Fonts\arialbd.ttf"
    sub_font_path = r"C:\Windows\Fonts\arialbd.ttf"
    f_title = ImageFont.truetype(bold_font_path, 64)
    f_badge = ImageFont.truetype(bold_font_path, 34)
    f_sub = ImageFont.truetype(sub_font_path, 28)

    # Título principal
    draw_c.text(
        (820, 185),
        "BRUNO SCHILLER",
        font=f_title,
        fill=(255, 255, 255, 255),
        anchor="mm",
        stroke_width=6,
        stroke_fill=(0, 0, 0, 255),
    )

    # Badge neón
    draw_c.rounded_rectangle([420, 240, 1220, 310], radius=14, fill=(225, 0, 80, 240), outline=(0, 0, 0, 255), width=3)
    draw_c.text(
        (820, 275),
        "🎮 SECRETOS • CURIOSIDADES • MITOS GAMER 🕹️",
        font=f_badge,
        fill=(255, 255, 255, 255),
        anchor="mm",
        stroke_width=3,
        stroke_fill=(0, 0, 0, 255),
    )

    # Subtexto
    draw_c.text(
        (820, 365),
        "GTA • MINECRAFT • PLAYSTATION • NINTENDO • LEYENDAS",
        font=f_sub,
        fill=(0, 229, 255, 255),
        anchor="mm",
        stroke_width=4,
        stroke_fill=(0, 0, 0, 255),
    )

    draw_c.text(
        (820, 425),
        "NUEVOS REELS Y VIDEOS TODOS LOS DÍAS",
        font=f_sub,
        fill=(255, 230, 0, 255),
        anchor="mm",
        stroke_width=3,
        stroke_fill=(0, 0, 0, 255),
    )

    cover.save(cover_out, quality=95)
    print(f"[Branding] Portada Gamer guardada: {cover_out}")
    return avatar_out, cover_out


if __name__ == "__main__":
    create_gaming_branding()
