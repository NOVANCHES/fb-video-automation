"""
Motor de Animación Estilo '@iadeguardia' (Neo-Brutalismo + Motion Graphics + Avatar Animado):
Genera escenas animadas con:
  1. Fondos alternados: Papel crema con rayos de sol verde neón (#CCFF00) / Modo oscuro con retícula.
  2. Tarjetas Neo-Brutalistas (borde negro grueso + sombra sólida desplazada) con barras de progreso
     animadas, carpetas/terminales, insignias numeradas y contadores con estrellas.
  3. Avatar Presentador animado (lentes verde neón, sombreado halftone, parpadeo, boca sincronizada
     con la narración y 3 poses de manos: explicando, apuntando arriba y sorprendido).
  4. Subtítulos en burbuja negra con borde neón y palabra activa en verde lima (#CCFF00).
"""

import math
import os
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image, ImageDraw, ImageFont

from config import VIDEO_HEIGHT, VIDEO_WIDTH

# Paleta de color exacta estilo @iadeguardia
CREAM_BG = (246, 245, 238)
DARK_BG = (14, 16, 18)
NEON_LIME = (204, 255, 0)
BLACK = (15, 15, 15)
WHITE = (255, 255, 255)
GRAY_TEXT = (95, 98, 105)
LIGHT_GRAY = (232, 232, 226)


def _get_font(size: int, bold: bool = True, mono: bool = False) -> Any:
    if mono:
        candidates = [r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\courbd.ttf"]
    elif bold:
        candidates = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]
    else:
        candidates = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]

    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _draw_sunburst_cream_bg(angle_offset: float = 0.0) -> Image.Image:
    """Fondo color crema con rayos de sol verde neón estilo cómic/explainer."""
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), CREAM_BG)
    draw = ImageDraw.Draw(img)

    cx, cy = VIDEO_WIDTH // 2, int(VIDEO_HEIGHT * 0.58)
    num_rays = 14
    radius = 2200
    for i in range(num_rays):
        a1 = math.radians(i * (360 / num_rays) + angle_offset)
        a2 = math.radians((i + 0.45) * (360 / num_rays) + angle_offset)
        x1, y1 = cx + radius * math.cos(a1), cy + radius * math.sin(a1)
        x2, y2 = cx + radius * math.cos(a2), cy + radius * math.sin(a2)
        draw.polygon([(cx, cy), (x1, y1), (x2, y2)], fill=(224, 255, 102))

    # Patrón sutil de puntos halftone
    for y in range(40, VIDEO_HEIGHT, 48):
        for x in range(40, VIDEO_WIDTH, 48):
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(215, 214, 205))
    return img


def _draw_dark_grid_bg(pulse: float = 0.0) -> Image.Image:
    """Fondo oscuro con retícula técnica y círculo de puntos halftone verde neón."""
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), DARK_BG)
    draw = ImageDraw.Draw(img)

    step = 44
    for x in range(0, VIDEO_WIDTH, step):
        draw.line([(x, 0), (x, VIDEO_HEIGHT)], fill=(24, 27, 30), width=1)
    for y in range(0, VIDEO_HEIGHT, step):
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(24, 27, 30), width=1)

    # Círculo halftone verde neón arriba a la derecha
    cx, cy = int(VIDEO_WIDTH * 0.85), int(VIDEO_HEIGHT * 0.10)
    max_r = int(280 + 20 * math.sin(pulse * math.pi))
    for y in range(max(0, cy - max_r), min(VIDEO_HEIGHT, cy + max_r), 22):
        for x in range(max(0, cx - max_r), min(VIDEO_WIDTH, cx + max_r), 22):
            dist = math.hypot(x - cx, y - cy)
            if dist < max_r:
                r_dot = max(2, int(6 * (1 - dist / max_r)))
                draw.ellipse([x - r_dot, y - r_dot, x + r_dot, y + r_dot], fill=(95, 125, 20))
    return img


def _draw_paper_halftone_bg(pulse: float = 0.0) -> Image.Image:
    """Fondo papel crema limpio con esfera halftone amarilla/lima a la derecha."""
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), CREAM_BG)
    draw = ImageDraw.Draw(img)

    for y in range(36, VIDEO_HEIGHT, 44):
        for x in range(36, VIDEO_WIDTH, 44):
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(225, 224, 216))

    cx, cy = int(VIDEO_WIDTH * 0.82), int(VIDEO_HEIGHT * 0.78)
    max_r = int(340 + 20 * math.cos(pulse * math.pi))
    for y in range(max(0, cy - max_r), min(VIDEO_HEIGHT, cy + max_r), 20):
        for x in range(max(0, cx - max_r), min(VIDEO_WIDTH, cx + max_r), 20):
            dist = math.hypot(x - cx, y - cy)
            if dist < max_r:
                r_dot = max(2, int(6 * (1 - dist / max_r)))
                draw.ellipse([x - r_dot, y - r_dot, x + r_dot, y + r_dot], fill=(228, 250, 110))
    return img


def _draw_neobrutalist_box(
    draw: ImageDraw.ImageDraw,
    rect: List[int],
    fill: tuple[int, int, int] = WHITE,
    shadow_color: tuple[int, int, int] = BLACK,
    shadow_offset: int = 12,
    radius: int = 26,
    border_width: int = 6,
) -> None:
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(
        [x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset],
        radius=radius,
        fill=shadow_color,
    )
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=radius,
        fill=fill,
        outline=BLACK,
        width=border_width,
    )


def _draw_star(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    outer_r: int = 44,
    fill: tuple[int, int, int] = NEON_LIME,
) -> None:
    points = []
    inner_r = int(outer_r * 0.44)
    for i in range(10):
        ang = math.radians(i * 36 - 90)
        r = outer_r if i % 2 == 0 else inner_r
        points.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(points, fill=fill, outline=BLACK, width=5)


def _draw_presenter_avatar(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    scale: float = 1.0,
    mouth_state: int = 0,
    pose: str = "neutral",
    in_box: bool = False,
) -> None:
    """
    Dibuja el personaje presentador estilo grabado halftone con lentes verde neón,
    boca animada (0=cerrada, 1=semiabierta, 2=abierta) y mano expresiva.
    """
    if in_box:
        box_w, box_h = int(380 * scale), int(410 * scale)
        bx1, by1 = cx - box_w // 2, cy - box_h // 2 + int(30 * scale)
        bx2, by2 = bx1 + box_w, by1 + box_h
        # Etiqueta "// AL AIRE" por encima de la cabeza del avatar
        label_y = cy - int(225 * scale) - 46
        draw.ellipse([bx1 + 6, label_y + 6, bx1 + 24, label_y + 24], fill=(235, 45, 45))
        draw.text((bx1 + 38, label_y - 2), "// AL AIRE", font=_get_font(28, mono=True), fill=WHITE)
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=30, fill=(248, 248, 245), outline=BLACK, width=5)
    else:
        # Círculo verde neón detrás del personaje (como en frame 1)
        bg_r = int(230 * scale)
        draw.ellipse(
            [cx - bg_r, cy - int(60 * scale) - bg_r, cx + bg_r, cy - int(60 * scale) + bg_r],
            fill=NEON_LIME,
            outline=BLACK,
            width=7,
        )

    # Torso / Camiseta con textura punteada
    torso_w, torso_h = int(330 * scale), int(230 * scale)
    tx1, ty1 = cx - torso_w // 2, cy + int(55 * scale)
    tx2, ty2 = cx + torso_w // 2, ty1 + torso_h
    draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=int(95 * scale), fill=(55, 58, 62), outline=BLACK, width=6)

    # Textura halftone en el torso
    for dy in range(ty1 + 20, ty2 - 15, int(14 * scale)):
        for dx in range(tx1 + 25, tx2 - 25, int(14 * scale)):
            draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(215, 215, 215))

    # Cuello
    nw, nh = int(86 * scale), int(55 * scale)
    draw.rectangle([cx - nw // 2, cy + int(15 * scale), cx + nw // 2, cy + int(15 * scale) + nh], fill=(40, 40, 40), outline=BLACK, width=5)

    # Cabeza
    hw, hh = int(225 * scale), int(265 * scale)
    hx1, hy1 = cx - hw // 2, cy - int(225 * scale)
    hx2, hy2 = cx + hw // 2, hy1 + hh
    draw.rounded_rectangle([hx1, hy1, hx2, hy2], radius=int(110 * scale), fill=WHITE, outline=BLACK, width=6)

    # Sombreado punteado de cabello y barba estilo grabado
    for dy in range(hy1 + 12, hy1 + int(70 * scale), max(6, int(9 * scale))):
        for dx in range(hx1 + 22, hx2 - 22, max(6, int(9 * scale))):
            if math.hypot(dx - cx, dy - (hy1 + hh // 2)) < hw * 0.48:
                draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=BLACK)

    # Barba (parte inferior de la cara)
    by_top = hy2 - int(88 * scale)
    draw.pieslice([hx1 + 6, hy1 + 10, hx2 - 6, hy2 - 4], start=15, end=165, fill=(45, 45, 45), outline=BLACK, width=5)
    for dy in range(by_top, hy2 - 14, max(6, int(8 * scale))):
        for dx in range(hx1 + 28, hx2 - 28, max(6, int(8 * scale))):
            if math.hypot(dx - cx, dy - (hy2 - int(70 * scale))) < hw * 0.42:
                draw.ellipse([dx - 1, dy - 1, dx + 1, dy + 1], fill=(220, 220, 220))

    # Cejas expresivas
    ey_y = hy1 + int(82 * scale)
    draw.line([(cx - int(72 * scale), ey_y), (cx - int(26 * scale), ey_y + int(4 * scale))], fill=BLACK, width=int(11 * scale))
    draw.line([(cx + int(24 * scale), ey_y - int(2 * scale)), (cx + int(74 * scale), ey_y - int(12 * scale))], fill=BLACK, width=int(11 * scale))

    # Ojos grandes con pupila brillante
    eye_y = hy1 + int(132 * scale)
    for ex in (cx - int(50 * scale), cx + int(50 * scale)):
        er_w, er_h = int(24 * scale), int(30 * scale)
        draw.ellipse([ex - er_w, eye_y - er_h, ex + er_w, eye_y + er_h], fill=BLACK)
        # Brillo blanco en pupila
        draw.ellipse([ex - int(12 * scale), eye_y - int(16 * scale), ex - int(2 * scale), eye_y - int(4 * scale)], fill=WHITE)

    # Lentes icónicos VERDE NEÓN (#CCFF00)
    g_r = int(48 * scale)
    for gx in (cx - int(52 * scale), cx + int(52 * scale)):
        draw.ellipse([gx - g_r, eye_y - g_r, gx + g_r, eye_y + g_r], outline=NEON_LIME, width=int(13 * scale))
    # Puente de los lentes
    draw.line([(cx - int(6 * scale), eye_y), (cx + int(6 * scale), eye_y)], fill=NEON_LIME, width=int(12 * scale))

    # Boca sincronizada con la voz
    my = hy2 - int(45 * scale)
    if mouth_state == 0:
        draw.arc([cx - int(24 * scale), my - int(12 * scale), cx + int(24 * scale), my + int(12 * scale)], start=15, end=165, fill=WHITE, width=int(6 * scale))
    elif mouth_state == 1:
        draw.rounded_rectangle([cx - int(22 * scale), my - int(8 * scale), cx + int(22 * scale), my + int(10 * scale)], radius=8, fill=BLACK, outline=WHITE, width=3)
    else:
        draw.ellipse([cx - int(24 * scale), my - int(14 * scale), cx + int(24 * scale), my + int(16 * scale)], fill=(190, 40, 50), outline=BLACK, width=4)

    # Poses de manos (apuntando arriba 'point' o sorprendido 'hand')
    if pose == "point":
        hx, hy = cx + int(115 * scale), cy + int(45 * scale)
        # Dedo índice apuntando hacia arriba al ejemplo
        draw.rounded_rectangle([hx - int(18 * scale), hy - int(95 * scale), hx + int(18 * scale), hy + int(20 * scale)], radius=14, fill=WHITE, outline=BLACK, width=6)
        # Otros dedos doblados + palma
        draw.rounded_rectangle([hx - int(22 * scale), hy - int(20 * scale), hx + int(68 * scale), hy + int(65 * scale)], radius=24, fill=WHITE, outline=BLACK, width=6)
        for f_idx in range(1, 3):
            fx = hx + int(f_idx * 22 * scale)
            draw.rounded_rectangle([fx - int(11 * scale), hy - int(32 * scale), fx + int(11 * scale), hy + int(15 * scale)], radius=10, fill=WHITE, outline=BLACK, width=5)
    elif pose == "surprised":
        hx, hy = cx + int(62 * scale), cy - int(20 * scale)
        # Mano abierta cerca del rostro (como en frame 3)
        draw.rounded_rectangle([hx - int(45 * scale), hy - int(20 * scale), hx + int(55 * scale), hy + int(75 * scale)], radius=28, fill=WHITE, outline=BLACK, width=6)
        for f_idx in range(-1, 3):
            fx = hx + int(f_idx * 22 * scale)
            draw.rounded_rectangle([fx - int(10 * scale), hy - int(65 * scale), fx + int(10 * scale), hy + int(10 * scale)], radius=10, fill=WHITE, outline=BLACK, width=5)


def _draw_speech_subtitles(
    draw: ImageDraw.ImageDraw,
    subtitle_text: str,
    highlight_word_idx: int,
    layout: str = "side",
) -> None:
    """
    Dibuja la burbuja de subtítulos con sombra verde neón y palabra activa en verde lima (#CCFF00).
    """
    words = subtitle_text.upper().split()
    if not words:
        return

    font_sub = _get_font(44 if layout == "side" else 56, bold=True)
    if len(words) >= 3:
        mid = (len(words) + 1) // 2
        lines = [words[:mid], words[mid:]]
    else:
        lines = [words]

    display_text = "\n".join(" ".join(line) for line in lines)
    bbox = draw.multiline_textbbox((0, 0), display_text, font=font_sub, align="left" if layout == "side" else "center", spacing=10)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if layout == "side":
        x = 465
        y = 1450 - text_h // 2
        max_x = min(VIDEO_WIDTH - 45, x + text_w + 56)
        box_rect = [x - 28, y - 24, max_x, y + text_h + 26]
    else:
        x = (VIDEO_WIDTH - text_w) // 2
        y = 1135 - text_h // 2
        box_rect = [x - 36, y - 24, x + text_w + 36, y + text_h + 26]

    # Sombra sólida verde neón desplazada + caja negra
    sx1, sy1, sx2, sy2 = box_rect
    draw.rounded_rectangle([sx1 + 8, sy1 + 8, sx2 + 8, sy2 + 8], radius=24, fill=NEON_LIME)
    draw.rounded_rectangle(box_rect, radius=24, fill=BLACK, outline=NEON_LIME, width=3)

    cur_y = y
    word_counter = 0
    for line_words in lines:
        line_str = " ".join(line_words)
        lb = draw.textbbox((0, 0), line_str, font=font_sub)
        line_w = lb[2] - lb[0]
        cur_x = x if layout == "side" else (VIDEO_WIDTH - line_w) // 2
        for w in line_words:
            is_active = word_counter == highlight_word_idx
            color = NEON_LIME if is_active else WHITE
            draw.text((cur_x, cur_y), w, font=font_sub, fill=color)
            wb = draw.textbbox((0, 0), w + " ", font=font_sub)
            cur_x += wb[2] - wb[0]
            word_counter += 1
        cur_y += (bbox[3] - bbox[1]) // max(1, len(lines)) + 8


def render_iadeguardia_frame(
    scene_idx: int,
    total_scenes: int,
    scene_progress: float,
    video_progress: float,
    card_title: str,
    card_subtitle: str,
    subtitle_text: str,
    highlight_word_idx: int,
    step_counter: int,
) -> Image.Image:
    """
    Renderiza un fotograma completo 1080x1920 con el estilo animado de @iadeguardia:
      - Escena 0: Portada/Hook en papel crema con rayos neón + tarjeta comparativa animada + Avatar grande.
      - Escena 1: Modo oscuro técnico con tarjeta de carpeta/terminal neón + Avatar en ventana '// AL AIRE' apuntando arriba.
      - Escena 2 y 3: Tarjetas de Ranking numeradas [1], [2], [3] con sombra sólida, estrella y Avatar expresivo.
    """
    mouth_state = step_counter % 3

    if scene_idx == 0:
        # ESCENA 1: HOOK CON RAYOS DE SOL NEÓN + TARJETA DE BARRAS ANIMADAS
        img = _draw_sunburst_cream_bg(angle_offset=scene_progress * 18.0)
        draw = ImageDraw.Draw(img)

        # Insignia superior negra en cápsula
        draw.rounded_rectangle([65, 135, 760, 202], radius=32, fill=BLACK)
        draw.text((412, 168), ">> TENDENCIA DEL DIA - DATOS REALES", font=_get_font(27, mono=True), fill=WHITE, anchor="mm")
        _draw_star(draw, 920, 195, outer_r=58, fill=NEON_LIME)

        # Título gigante en dos líneas
        words_t = card_title.upper().split()
        mid_t = max(1, (len(words_t) + 1) // 2)
        t_line1 = " ".join(words_t[:mid_t])[:20]
        t_line2 = " ".join(words_t[mid_t:])[:20] or "LO MAS VIRAL"
        draw.text((68, 235), t_line1, font=_get_font(76, bold=True), fill=BLACK)
        draw.text((68, 325), t_line2, font=_get_font(76, bold=True), fill=BLACK)

        # Tarjeta Neo-Brutalista con barras de impacto animadas
        _draw_neobrutalist_box(draw, [65, 445, 1015, 795], fill=WHITE, shadow_color=BLACK, shadow_offset=14, radius=28)
        fill_prog = min(1.0, 0.35 + 0.65 * scene_progress)

        # Barra 1 (Negra)
        draw.rounded_rectangle([100, 480, 160, 535], radius=12, fill=BLACK)
        draw.text((130, 507), "01", font=_get_font(28, bold=True), fill=NEON_LIME, anchor="mm")
        draw.text((180, 492), card_subtitle[:42] or "Impacto global confirmado", font=_get_font(31, bold=True), fill=BLACK)
        draw.text((975, 490), "98.4% [+]", font=_get_font(34, bold=True), fill=BLACK, anchor="ra")
        draw.rounded_rectangle([100, 550, 975, 605], radius=12, fill=LIGHT_GRAY, outline=BLACK, width=4)
        bar1_w = int(875 * fill_prog)
        draw.rounded_rectangle([100, 550, 100 + max(40, bar1_w), 605], radius=12, fill=BLACK)

        # Barra 2 (Verde Neón)
        draw.rounded_rectangle([100, 635, 160, 690], radius=12, fill=NEON_LIME, outline=BLACK, width=3)
        draw.text((130, 662), "02", font=_get_font(28, bold=True), fill=BLACK, anchor="mm")
        draw.text((180, 645), "Nivel de interes hoy", font=_get_font(34, bold=True), fill=BLACK)
        draw.text((975, 645), "VIRAL [!]", font=_get_font(34, bold=True), fill=BLACK, anchor="ra")
        draw.rounded_rectangle([100, 705, 975, 760], radius=12, fill=LIGHT_GRAY, outline=BLACK, width=4)
        bar2_w = int(760 * fill_prog)
        draw.rounded_rectangle([100, 705, 100 + max(40, bar2_w), 760], radius=12, fill=NEON_LIME, outline=BLACK, width=4)

        # Avatar grande centrado abajo + Subtítulos encima
        _draw_presenter_avatar(draw, cx=VIDEO_WIDTH // 2, cy=1520, scale=1.42, mouth_state=mouth_state, pose="neutral", in_box=False)
        _draw_speech_subtitles(draw, subtitle_text, highlight_word_idx, layout="center")
        return img

    elif scene_idx == 1:
        # ESCENA 2: MODO OSCURO CON CARPETA/TARJETA VERDE NEÓN + AVATAR '// AL AIRE' APUNTANDO ARRIBA
        img = _draw_dark_grid_bg(pulse=scene_progress)
        draw = ImageDraw.Draw(img)

        clean_t = card_title.upper().replace("EJEMPLO 1:", "").replace("1.", "").strip()
        words_t = clean_t.split()
        mid_t = max(1, (len(words_t) + 1) // 2)
        part_a = " ".join(words_t[:mid_t])[:18] or "CONCEPTO"
        part_b = " ".join(words_t[mid_t:])[:22] or "CLAVE #1"
        draw.text((68, 175), f"{part_a} =", font=_get_font(60, bold=True), fill=WHITE)
        draw.text((68, 255), part_b, font=_get_font(60, bold=True), fill=NEON_LIME)

        # Ilustración de Carpeta / Tarjeta Neo-Brutalista Verde Neón (como en frame 2)
        fx1, fy1, fx2, fy2 = 68, 365, 980, 825
        # Pestaña superior de carpeta
        draw.polygon([(fx1, fy1 + 45), (fx1, fy1), (fx1 + 260, fy1), (fx1 + 310, fy1 + 45)], fill=NEON_LIME, outline=WHITE, width=4)
        draw.rounded_rectangle([fx1, fy1 + 40, fx2, fy2], radius=28, fill=NEON_LIME, outline=WHITE, width=5)
        draw.text((fx1 + 35, fy1 + 8), "dato_01/", font=_get_font(34, mono=True), fill=BLACK)

        # Contenido explicativo dentro de la carpeta neón
        draw.rounded_rectangle([fx1 + 40, fy1 + 95, fx2 - 40, fy2 - 45], radius=20, fill=BLACK)
        # Dividir subtítulo explicativo en 2 líneas claras
        sub_words = card_subtitle.split()
        s_mid = max(1, (len(sub_words) + 1) // 2)
        s_l1 = " ".join(sub_words[:s_mid])
        s_l2 = " ".join(sub_words[s_mid:])
        draw.text((fx1 + 75, fy1 + 145), f"> {s_l1}", font=_get_font(40, mono=True), fill=NEON_LIME)
        if s_l2:
            draw.text((fx1 + 75, fy1 + 215), f"  {s_l2}", font=_get_font(38, mono=True), fill=WHITE)

        # Barra de avance animada dentro de la tarjeta
        prog_w = int((fx2 - fx1 - 160) * min(1.0, 0.25 + 0.75 * scene_progress))
        draw.rounded_rectangle([fx1 + 75, fy2 - 115, fx1 + 75 + max(40, prog_w), fy2 - 80], radius=10, fill=NEON_LIME)

        # Avatar en recuadro "// AL AIRE" abajo a la izquierda apuntando hacia arriba
        _draw_presenter_avatar(draw, cx=240, cy=1420, scale=0.95, mouth_state=mouth_state, pose="point", in_box=True)
        _draw_speech_subtitles(draw, subtitle_text, highlight_word_idx, layout="side")
        return img

    else:
        # ESCENA 3 Y 4: TARJETA DE RANKING NUMERADA + SOMBRA SÓLIDA + ESTRELLA + AVATAR EXPRESIVO
        img = _draw_paper_halftone_bg(pulse=scene_progress)
        draw = ImageDraw.Draw(img)

        num_badge = scene_idx
        # Insignia cuadrada negra con número grande en verde neón (como el '5' de frame 3)
        _draw_neobrutalist_box(draw, [65, 145, 275, 365], fill=BLACK, shadow_color=NEON_LIME, shadow_offset=12, radius=32)
        draw.text((170, 255), str(num_badge), font=_get_font(135, bold=True), fill=NEON_LIME, anchor="mm")

        # Título al lado de la insignia
        clean_title = card_title.replace(f"EJEMPLO {num_badge}:", "").replace(f"{num_badge}.", "").strip()
        t_words = clean_title.split()
        t_mid = max(1, (len(t_words) + 1) // 2)
        draw.text((310, 185), " ".join(t_words[:t_mid])[:18], font=_get_font(62, bold=True), fill=BLACK)
        if t_words[t_mid:]:
            draw.text((310, 265), " ".join(t_words[t_mid:])[:18], font=_get_font(62, bold=True), fill=BLACK)

        # Tarjeta Neo-Brutalista blanca con sombra negra gruesa (como en frame 3)
        _draw_neobrutalist_box(draw, [65, 415, 1015, 675], fill=WHITE, shadow_color=BLACK, shadow_offset=14, radius=28)
        sub_words = card_subtitle.split()
        s_mid = max(1, (len(sub_words) + 1) // 2)
        draw.text((105, 465), " ".join(sub_words[:s_mid])[:34], font=_get_font(44, bold=False), fill=GRAY_TEXT)
        draw.text((105, 545), " ".join(sub_words[s_mid:])[:34] or clean_title[:28], font=_get_font(48, bold=True), fill=BLACK)

        # Ícono ilustrado a la derecha dentro de la tarjeta
        draw.rounded_rectangle([825, 445, 980, 635], radius=22, fill=BLACK)
        _draw_star(draw, 902, 540, outer_r=48, fill=NEON_LIME)

        # Estrella + Contador destacado debajo de la tarjeta
        _draw_star(draw, 115, 765, outer_r=45, fill=NEON_LIME)
        draw.text((185, 730), f"DATO CLAVE #{num_badge}", font=_get_font(58, bold=True), fill=BLACK)

        pose = "surprised" if scene_idx % 2 == 0 else "point"
        _draw_presenter_avatar(draw, cx=235, cy=1460, scale=1.05, mouth_state=mouth_state, pose=pose, in_box=False)
        _draw_speech_subtitles(draw, subtitle_text, highlight_word_idx, layout="side")
        return img
