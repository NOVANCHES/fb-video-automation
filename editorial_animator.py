"""
Motor de Renderizado Editorial Estilo Claude / AI KID (Minimalista de Alta Retención)
Inspirado en el formato viral de @ai._kid en TikTok e Instagram Reels:
  - Lienzo crema editorial (#F6F4ED) con cuadrícula técnica tenue.
  - Tipografía serif de lujo (Georgia Bold) con marcador resaltador amarillo (#FFF38A).
  - Componentes visuales sin dependencias de fuentes rotas (vectores nativos para flechas, estrellas y tachados).
  - Generación de secuencias de video animadas a 24 FPS con sincronización de audio neural.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import OUTPUT_DIR

WIDTH = 1080
HEIGHT = 1920

# Paleta editorial
COLOR_BG = (246, 244, 237)          # #F6F4ED Crema cálido
COLOR_GRID = (236, 233, 224)        # Cuadrícula sutil
COLOR_TEXT_MAIN = (20, 20, 20)      # Negro carbón
COLOR_TEXT_MUTED = (120, 116, 110)  # Gris editorial
COLOR_HIGHLIGHT = (255, 243, 138)   # Amarillo rotulador (#FFF38A)
COLOR_HIGHLIGHT_RGBA = (255, 243, 138, 245)
COLOR_RED_STRIKE = (220, 65, 65)    # Rojo tachado (#DC4141)
COLOR_RUST_TAG = (200, 90, 60)      # Terracota para footer
COLOR_TERM_BG = (26, 26, 26)        # Terminal macOS (#1A1A1A)


def _get_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Busca fuentes en Windows o Linux con fallbacks elegantes."""
    font_paths = {
        "serif_bold": [
            r"C:\Windows\Fonts\georgiab.ttf",
            r"C:\Windows\Fonts\timesbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        ],
        "serif_reg": [
            r"C:\Windows\Fonts\georgia.ttf",
            r"C:\Windows\Fonts\times.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        ],
        "serif_italic": [
            r"C:\Windows\Fonts\georgiai.ttf",
            r"C:\Windows\Fonts\timesi.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        ],
        "sans_bold": [
            r"C:\Windows\Fonts\arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ],
        "sans_reg": [
            r"C:\Windows\Fonts\arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ],
        "mono_bold": [
            r"C:\Windows\Fonts\consolab.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        ],
        "mono_reg": [
            r"C:\Windows\Fonts\consola.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ],
    }
    candidates = font_paths.get(name, [])
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def create_base_canvas() -> Image.Image:
    """Crea el fondo lienzo crema con cuadrícula técnica sutil."""
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(img)
    step = 48
    for x in range(0, WIDTH, step):
        draw.line([(x, 0), (x, HEIGHT)], fill=COLOR_GRID, width=1)
    for y in range(0, HEIGHT, step):
        draw.line([(0, y), (WIDTH, y)], fill=COLOR_GRID, width=1)
    return img


def draw_header_and_footer(
    img: Image.Image,
    brand: str = "@BrunoSchiller",
    tagline: str = "Automatizá tu contenido con IA",
    kicker: str = "",
) -> None:
    draw = ImageDraw.Draw(img)
    f_link = _get_font("sans_reg", 26)
    link_txt = f"• {brand} •"
    b_link = draw.textbbox((0, 0), link_txt, font=f_link)
    draw.text(((WIDTH - (b_link[2] - b_link[0])) // 2, 110), link_txt, fill=COLOR_TEXT_MUTED, font=f_link)

    if kicker:
        f_kicker = _get_font("sans_bold", 28)
        draw.text((90, 220), kicker.upper(), fill=COLOR_TEXT_MUTED, font=f_kicker)

    f_brand = _get_font("sans_bold", 32)
    f_tag = _get_font("serif_italic", 34)
    y_foot = 1800
    draw.text((90, y_foot), brand, fill=COLOR_TEXT_MAIN, font=f_brand)

    b_tag = draw.textbbox((0, 0), tagline, font=f_tag)
    draw.text((WIDTH - 90 - (b_tag[2] - b_tag[0]), y_foot), tagline, fill=COLOR_RUST_TAG, font=f_tag)


def _draw_star_polygon(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, color=(255, 255, 255)):
    """Dibuja una estrella o destello de 4 puntas de alta gama."""
    points = [
        (cx, cy - r),
        (cx + r * 0.28, cy - r * 0.28),
        (cx + r, cy),
        (cx + r * 0.28, cy + r * 0.28),
        (cx, cy + r),
        (cx - r * 0.28, cy + r * 0.28),
        (cx - r, cy),
        (cx - r * 0.28, cy - r * 0.28),
    ]
    draw.polygon(points, fill=color)


def _draw_arrow_right(draw: ImageDraw.ImageDraw, x: int, y: int, length: int = 40, color=(160, 150, 140)):
    """Dibuja una flecha horizontal limpia."""
    draw.line([(x, y), (x + length, y)], fill=color, width=3)
    draw.polygon([(x + length, y - 6), (x + length + 8, y), (x + length, y + 6)], fill=color)


def draw_headline_with_highlight(
    img: Image.Image,
    full_text: str,
    highlight_words: str,
    y_start: int = 280,
    font_size: int = 74,
) -> int:
    """Ajusta líneas y resalta la palabra clave con rotulador fluorescente."""
    draw = ImageDraw.Draw(img, "RGBA")
    font = _get_font("serif_bold", font_size)
    max_w = WIDTH - 180

    words = full_text.split()
    lines: List[List[str]] = []
    curr: List[str] = []

    for w in words:
        test = " ".join(curr + [w])
        b = draw.textbbox((0, 0), test, font=font)
        if (b[2] - b[0]) <= max_w:
            curr.append(w)
        else:
            if curr:
                lines.append(curr)
            curr = [w]
    if curr:
        lines.append(curr)

    line_h = int(font_size * 1.25)
    curr_y = y_start
    hl_norm = highlight_words.lower().strip()

    for line in lines:
        line_str = " ".join(line)
        if hl_norm and any(h in line_str.lower() for h in hl_norm.split()):
            curr_x = 90
            for w in line:
                b_w = draw.textbbox((0, 0), w, font=font)
                w_w = b_w[2] - b_w[0]
                is_hl = w.lower().strip(",.:;!?") in hl_norm.split()
                if is_hl:
                    pad_x = 12
                    pad_y = 6
                    draw.rounded_rectangle(
                        [curr_x - pad_x, curr_y - pad_y, curr_x + w_w + pad_x, curr_y + line_h - 10],
                        radius=8,
                        fill=COLOR_HIGHLIGHT_RGBA,
                    )
                draw.text((curr_x, curr_y), w, fill=COLOR_TEXT_MAIN, font=font)
                curr_x += w_w + draw.textbbox((0, 0), " ", font=font)[2]
        else:
            draw.text((90, curr_y), line_str, fill=COLOR_TEXT_MAIN, font=font)

        curr_y += line_h

    return curr_y


# ---------------------------------------------------------------------------
# SLIDE 1: HOOK (Tachados + Solución)
# ---------------------------------------------------------------------------
def render_slide_hook(
    title: str,
    highlight_word: str,
    struck_items: List[str],
    winner_item: str,
    subhead: str = "Lo que las empresas no te cuentan.",
    kicker: str = "— LA VERDAD OCULTA",
    brand: str = "@BrunoSchiller",
    tagline: str = "Cómo funciona el mundo real",
) -> Image.Image:
    img = create_base_canvas()
    draw_header_and_footer(img, brand=brand, tagline=tagline, kicker="— LA NUEVA FORMA")
    y_next = draw_headline_with_highlight(img, title, highlight_word, y_start=280, font_size=74)

    draw = ImageDraw.Draw(img, "RGBA")
    f_sub = _get_font("serif_reg", 38)
    draw.text((90, y_next + 15), subhead, fill=COLOR_TEXT_MUTED, font=f_sub)

    card_y = y_next + 110
    f_item = _get_font("serif_reg", 58)
    f_winner = _get_font("serif_bold", 68)

    icon_colors = [(35, 35, 35), (25, 45, 95), (85, 30, 75)]

    for i, item in enumerate(struck_items[:3]):
        iy = card_y + (i * 155)
        draw.rounded_rectangle([90, iy, 190, iy + 100], radius=24, fill=icon_colors[i % len(icon_colors)])

        f_ic = _get_font("sans_bold", 42)
        words = item.split()
        ic_letter = words[1][0].upper() if len(words) > 1 else item[0].upper()
        draw.text((125, iy + 25), ic_letter, fill=(255, 255, 255), font=f_ic)

        draw.line([(80, iy + 110), (200, iy - 10)], fill=COLOR_RED_STRIKE, width=8)
        draw.text((230, iy + 15), item, fill=(50, 50, 50), font=f_item)

        b_txt = draw.textbbox((230, iy + 15), item, font=f_item)
        mid_y = (b_txt[1] + b_txt[3]) // 2
        draw.line([(220, mid_y), (b_txt[2] + 10, mid_y)], fill=COLOR_RED_STRIKE + (220,), width=5)

    wy = card_y + (len(struck_items[:3]) * 165) + 30
    draw.rounded_rectangle([90, wy, 200, wy + 110], radius=26, fill=(225, 95, 55))
    _draw_star_polygon(draw, 145, wy + 55, r=32, color=(255, 255, 255))

    w_words = winner_item.split()
    w_prefix = " ".join(w_words[:-1]) if len(w_words) > 1 else ""
    w_hl = w_words[-1] if w_words else winner_item

    cur_x = 235
    if w_prefix:
        draw.text((cur_x, wy + 20), w_prefix, fill=COLOR_TEXT_MAIN, font=f_winner)
        cur_x += draw.textbbox((0, 0), w_prefix, font=f_winner)[2] + 18

    bw_hl = draw.textbbox((0, 0), w_hl, font=f_winner)
    wh = bw_hl[2] - bw_hl[0]

    draw.rounded_rectangle([cur_x - 12, wy + 10, cur_x + wh + 12, wy + 100], radius=12, fill=COLOR_HIGHLIGHT_RGBA)
    draw.text((cur_x, wy + 20), w_hl, fill=COLOR_TEXT_MAIN, font=f_winner)

    f_swipe = _get_font("serif_italic", 34)
    draw.text((WIDTH - 290, wy + 200), "deslizá", fill=COLOR_RUST_TAG, font=f_swipe)
    _draw_arrow_right(draw, WIDTH - 160, wy + 222, length=38, color=COLOR_RUST_TAG)

    return img


# ---------------------------------------------------------------------------
# SLIDE 2: THE FRAMEWORK (3 Pasos simples)
# ---------------------------------------------------------------------------
def render_slide_steps(
    headline: str,
    highlight_word: str,
    subhead_1: str,
    subhead_2: str,
    steps: List[Tuple[str, str, str]],
    brand: str = "@BrunoSchiller",
    tagline: str = "Automatizá tu contenido con IA",
) -> Image.Image:
    img = create_base_canvas()
    draw_header_and_footer(img, brand=brand, tagline=tagline, kicker="— LO QUE NECESITÁS")
    y_next = draw_headline_with_highlight(img, headline, highlight_word, y_start=280, font_size=74)

    draw = ImageDraw.Draw(img, "RGBA")
    f_sub1 = _get_font("serif_reg", 40)
    f_sub2 = _get_font("sans_bold", 42)
    draw.text((90, y_next + 20), subhead_1, fill=(70, 70, 70), font=f_sub1)
    draw.text((90, y_next + 80), subhead_2, fill=COLOR_TEXT_MAIN, font=f_sub2)

    card_y = y_next + 210
    col_w = 265
    gap = 52
    colors = [(225, 100, 60), (220, 50, 50), (35, 130, 240)]

    for i, (pill, step_title, step_desc) in enumerate(steps[:3]):
        cx = 90 + i * (col_w + gap)

        f_pill = _get_font("sans_bold", 22)
        draw.rounded_rectangle([cx + 60, card_y, cx + col_w - 60, card_y + 36], radius=8, fill=(238, 230, 218))
        draw.text((cx + 78, card_y + 6), pill.upper(), fill=(140, 90, 70), font=f_pill)

        cy = card_y + 55
        draw.rounded_rectangle([cx, cy, cx + col_w, cy + col_w], radius=32, fill=colors[i % len(colors)])

        f_sym = _get_font("sans_bold", 64)
        sym = f"0{i+1}"
        b_sym = draw.textbbox((0, 0), sym, font=f_sym)
        sw = b_sym[2] - b_sym[0]
        draw.text((cx + (col_w - sw) // 2, cy + (col_w // 2) - 38), sym, fill=(255, 255, 255), font=f_sym)

        if i < 2:
            _draw_arrow_right(draw, cx + col_w + 12, cy + (col_w // 2), length=28, color=(180, 170, 160))

        f_st = _get_font("sans_bold", 36)
        b_st = draw.textbbox((0, 0), step_title, font=f_st)
        draw.text((cx + (col_w - (b_st[2] - b_st[0])) // 2, cy + col_w + 25), step_title, fill=COLOR_TEXT_MAIN, font=f_st)

        f_sd = _get_font("serif_reg", 30)
        b_sd = draw.textbbox((0, 0), step_desc, font=f_sd)
        draw.text((cx + (col_w - (b_sd[2] - b_sd[0])) // 2, cy + col_w + 75), step_desc, fill=COLOR_TEXT_MUTED, font=f_sd)

    return img


# ---------------------------------------------------------------------------
# SLIDE 3: TERMINAL DEMO (Consola macOS)
# ---------------------------------------------------------------------------
def render_slide_terminal(
    headline: str,
    highlight_word: str,
    prompt_text: str,
    response_text: str,
    window_title: str = "terminal · diagnostico",
    subtitle: str = "Lo que ocurre detrás de tu pantalla.",
    brand: str = "@BrunoSchiller",
    tagline: str = "Cómo funciona el mundo real",
) -> Image.Image:
    img = create_base_canvas()
    draw_header_and_footer(img, brand=brand, tagline=tagline, kicker="— CÓMO SE USA")
    y_next = draw_headline_with_highlight(img, headline, highlight_word, y_start=280, font_size=74)

    draw = ImageDraw.Draw(img, "RGBA")
    f_sub = _get_font("serif_reg", 38)
    draw.text((90, y_next + 18), subtitle, fill=COLOR_TEXT_MUTED, font=f_sub)

    card_w = 900
    card_h = 800
    card_x = 90
    card_y = y_next + 100

    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([card_x, card_y + 16, card_x + card_w, card_y + card_h + 16], radius=28, fill=(0, 0, 0, 45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=28, fill=COLOR_TERM_BG)

    dot_y = card_y + 38
    draw.ellipse([card_x + 36, dot_y, card_x + 58, dot_y + 22], fill=(255, 95, 86))
    draw.ellipse([card_x + 72, dot_y, card_x + 94, dot_y + 22], fill=(255, 189, 46))
    draw.ellipse([card_x + 108, dot_y, card_x + 130, dot_y + 22], fill=(39, 201, 63))

    f_t = _get_font("mono_reg", 26)
    draw.text((card_x + 155, card_y + 34), window_title, fill=(130, 130, 130), font=f_t)
    draw.line([(card_x, card_y + 78), (card_x + card_w, card_y + 78)], fill=(45, 45, 45), width=2)

    f_body = _get_font("mono_bold", 34)
    f_resp = _get_font("mono_reg", 32)

    draw.text((card_x + 45, card_y + 120), ">", fill=(245, 120, 50), font=f_body)

    words = prompt_text.split()
    lines = []
    cur = []
    for w in words:
        if len(" ".join(cur + [w])) > 36:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))

    py = card_y + 120
    for ln in lines:
        draw.text((card_x + 85, py), ln, fill=(245, 245, 245), font=f_body)
        py += 54

    py += 35
    draw.line([(card_x + 45, py), (card_x + card_w - 45, py)], fill=(45, 45, 45), width=1)
    py += 35

    r_words = response_text.split()
    r_lines = []
    cur = []
    for w in r_words:
        if len(" ".join(cur + [w])) > 40:
            r_lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        r_lines.append(" ".join(cur))

    for ln in r_lines:
        draw.text((card_x + 45, py), ln, fill=(185, 185, 185), font=f_resp)
        py += 50

    return img


# ---------------------------------------------------------------------------
# SLIDE 4: FEATURES (6 Funciones con insignias de producción pro)
# ---------------------------------------------------------------------------
def render_slide_features(
    headline: str,
    highlight_word: str,
    features: List[Tuple[str, str]],
    brand: str = "@BrunoSchiller",
    tagline: str = "Automatizá tu contenido con IA",
) -> Image.Image:
    img = create_base_canvas()
    draw_header_and_footer(img, brand=brand, tagline=tagline, kicker="— LO QUE HACE")
    y_next = draw_headline_with_highlight(img, headline, highlight_word, y_start=280, font_size=74)

    draw = ImageDraw.Draw(img, "RGBA")
    grid_y = y_next + 120
    col_w = 265
    gap_x = 52
    row_h = 320
    gap_y = 40

    badge_tags = ["CUT", "CINE", "SUB", "ANIM", "SFX", "BRAND"]
    badge_colors = [(240, 235, 225), (230, 240, 250), (250, 240, 230), (235, 245, 235), (250, 235, 245), (245, 245, 230)]

    for i, (_, label) in enumerate(features[:6]):
        col = i % 3
        row = i // 3

        cx = 90 + col * (col_w + gap_x)
        cy = grid_y + row * (row_h + gap_y)

        draw.rounded_rectangle([cx, cy, cx + col_w, cy + 180], radius=24, fill=(255, 255, 255), outline=(225, 220, 210), width=2)
        draw.rounded_rectangle([cx + 30, cy + 30, cx + col_w - 30, cy + 150], radius=16, fill=badge_colors[i % len(badge_colors)])

        f_tag = _get_font("sans_bold", 44)
        t_label = badge_tags[i % len(badge_tags)]
        b_t = draw.textbbox((0, 0), t_label, font=f_tag)
        draw.text((cx + (col_w - (b_t[2] - b_t[0])) // 2, cy + 68), t_label, fill=(45, 45, 45), font=f_tag)

        f_lbl = _get_font("serif_reg", 34)
        words = label.split()
        if len(words) > 2:
            l1 = " ".join(words[:2])
            l2 = " ".join(words[2:])
            b1 = draw.textbbox((0, 0), l1, font=f_lbl)
            b2 = draw.textbbox((0, 0), l2, font=f_lbl)
            draw.text((cx + (col_w - (b1[2] - b1[0])) // 2, cy + 205), l1, fill=COLOR_TEXT_MAIN, font=f_lbl)
            draw.text((cx + (col_w - (b2[2] - b2[0])) // 2, cy + 248), l2, fill=COLOR_TEXT_MAIN, font=f_lbl)
        else:
            b1 = draw.textbbox((0, 0), label, font=f_lbl)
            draw.text((cx + (col_w - (b1[2] - b1[0])) // 2, cy + 215), label, fill=COLOR_TEXT_MAIN, font=f_lbl)

    return img


# ---------------------------------------------------------------------------
# SLIDE 5: CTA VIRAL (Comentá PALABRA)
# ---------------------------------------------------------------------------
def render_slide_cta(
    cta_word: str,
    prompt_promise: str,
    brand: str = "@BrunoSchiller",
    tagline: str = "te espero en los comments",
) -> Image.Image:
    img = create_base_canvas()
    draw_header_and_footer(img, brand=brand, tagline=tagline, kicker="— COMENTÁ ABAJO")

    draw = ImageDraw.Draw(img, "RGBA")
    f_cta = _get_font("serif_bold", 120)
    b_cta = draw.textbbox((0, 0), cta_word.upper(), font=f_cta)
    tw = b_cta[2] - b_cta[0]
    th = b_cta[3] - b_cta[1]

    box_w = max(tw + 80, 780)
    box_h = th + 80
    box_x = (WIDTH - box_w) // 2
    box_y = 560

    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=24, fill=COLOR_HIGHLIGHT)
    draw.text((box_x + (box_w - tw) // 2, box_y + 30), cta_word.upper(), fill=COLOR_TEXT_MAIN, font=f_cta)

    f_desc = _get_font("serif_reg", 46)
    words = prompt_promise.split()
    lines = []
    cur = []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textbbox((0, 0), test, font=f_desc)[2] < (WIDTH - 240):
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    y_p = box_y + box_h + 90
    for ln in lines:
        b = draw.textbbox((0, 0), ln, font=f_desc)
        draw.text(((WIDTH - (b[2] - b[0])) // 2, y_p), ln, fill=(40, 40, 40), font=f_desc)
        y_p += 65

    return img


# ---------------------------------------------------------------------------
# PIPELINE COMPLETO DE AUDIO + VIDEO EDITORIAL
# ---------------------------------------------------------------------------
async def _generate_audio_async(script_text: str, audio_path: Path, voice: str = "es-AR-TomasNeural") -> Path:
    import edge_tts
    comm = edge_tts.Communicate(script_text, voice=voice, rate="+5%")
    await comm.save(str(audio_path))
    return audio_path


def render_editorial_package(topic_data: Dict[str, Any]) -> Tuple[List[Path], Path, Path]:
    """
    Renderiza el paquete completo:
      1. 5 diapositivas editoriales en HD
      2. Narración con Edge-TTS
      3. Video vertical 9:16 de alta retención a 24 FPS
    """
    print(f"\n[Editorial Package] Procesando tema: '{topic_data['topic']}'...")

    tagline = topic_data.get("tagline", "Cómo funciona el mundo real")
    subhead_hook = topic_data.get("subhead_hook", "Lo que las empresas no te cuentan.")
    kicker_hook = topic_data.get("kicker_hook", "— LA VERDAD OCULTA")
    window_title = topic_data.get("window_title", "terminal · diagnostico")
    terminal_subtitle = topic_data.get("terminal_subtitle", "Lo que ocurre detrás de tu pantalla.")

    s1 = render_slide_hook(
        title=topic_data["hook_title"],
        highlight_word=topic_data["highlight_word"],
        struck_items=topic_data["struck_items"],
        winner_item=topic_data["winner_item"],
        subhead=subhead_hook,
        kicker=kicker_hook,
        tagline=tagline,
    )
    s2 = render_slide_steps(
        headline=topic_data["step_headline"],
        highlight_word=topic_data["step_highlight"],
        subhead_1=topic_data["subhead_1"],
        subhead_2=topic_data["subhead_2"],
        steps=topic_data["steps"],
        tagline=tagline,
    )
    s3 = render_slide_terminal(
        headline=topic_data["terminal_headline"],
        highlight_word=topic_data["terminal_highlight"],
        prompt_text=topic_data["terminal_prompt"],
        response_text=topic_data["terminal_response"],
        window_title=window_title,
        subtitle=terminal_subtitle,
        tagline=tagline,
    )
    s4 = render_slide_features(
        headline=topic_data["features_headline"],
        highlight_word=topic_data["features_highlight"],
        features=topic_data["features"],
        tagline=tagline,
    )
    s5 = render_slide_cta(
        cta_word=topic_data["cta_word"],
        prompt_promise=topic_data["cta_promise"],
        tagline="te espero en los comments",
    )

    slides = [s1, s2, s3, s4, s5]
    slide_paths: List[Path] = []
    for i, sl in enumerate(slides):
        p = OUTPUT_DIR / f"editorial_slide_{i+1}.png"
        sl.save(p, quality=95)
        slide_paths.append(p)
    print(f"      [Slides HD]: 5 diapositivas generadas en {OUTPUT_DIR}")

    audio_path = OUTPUT_DIR / "editorial_narration.mp3"
    print("      [Audio]: Generando locución neural con Edge-TTS...")
    asyncio.run(_generate_audio_async(topic_data["narration_script"], audio_path, voice="es-AR-TomasNeural"))
    print(f"      [Audio]: Narración lista ({audio_path.name})")

    video_out = OUTPUT_DIR / "video_final.mp4"
    print("      [Video]: Ensamblando video vertical 9:16 a 24 FPS...")
    try:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    except ImportError:
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

    audio = AudioFileClip(str(audio_path))
    total_dur = audio.duration
    slide_dur = total_dur / len(slides)

    clips = []
    for sp in slide_paths:
        c = ImageClip(str(sp)).with_duration(slide_dur)
        clips.append(c)

    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.with_audio(audio)
    final_video.write_videofile(
        str(video_out),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        logger=None,
    )
    audio.close()
    final_video.close()
    for c in clips:
        c.close()

    print(f"      [Video]: ✅ Video final listo: {video_out.name} ({total_dur:.1f}s)")
    return slide_paths, audio_path, video_out
