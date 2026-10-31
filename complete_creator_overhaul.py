"""
Auditoría completa de Monetización + Configuración Integral del Perfil de Creador:
  1. Inspecciona los criterios exactos de Estrellas (2/3), Suscripciones (2/3), Monetización de Contenido y Estado del Perfil (92%).
  2. Crea y sube la Foto de Perfil (Avatar 2D Cómic) y la Foto de Portada HD estilo Don Zombi / Curiosamente Graficado.
  3. Actualiza la Presentación (Bio) y cambia el Nombre del Perfil en el Centro de Cuentas de Meta.
"""

import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import OUTPUT_DIR
from uploader import _create_driver

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def generate_comic_channel_branding() -> tuple[Path, Path]:
    """
    Crea el Avatar circular/cuadrado 1080x1080 y el Banner de Portada 1640x624
    con el estilo ilustrado 2D de Don Zombi / Curiosamente Graficado.
    """
    avatar_out = OUTPUT_DIR / "creator_avatar_comic.jpg"
    cover_out = OUTPUT_DIR / "creator_cover_comic.jpg"

    z1 = OUTPUT_DIR / "zombi_1.png"
    s1 = OUTPUT_DIR / "selva_1.png"
    z3 = OUTPUT_DIR / "zombi_3.png"

    # 1. Avatar 1080x1080 centrado en el personaje estilo cómic 2D
    if z1.exists():
        im_a = Image.open(z1).convert("RGB")
        w, h = im_a.size
        # Recortar la parte superior-central donde está el rostro del personaje con gorro y sudadera roja
        crop_box = (int(w * 0.12), int(h * 0.22), int(w * 0.72), int(h * 0.56))
        face_crop = im_a.crop(crop_box)
        avatar = ImageOps.fit(face_crop, (1080, 1080), method=Image.Resampling.LANCZOS)
    else:
        avatar = Image.new("RGB", (1080, 1080), (22, 28, 38))

    draw_a = ImageDraw.Draw(avatar, "RGBA")
    draw_a.ellipse([24, 24, 1056, 1056], outline=(255, 220, 0, 255), width=22)
    avatar.save(avatar_out, quality=95)

    # 2. Portada 1640x624 combinando las ilustraciones 2D (Supervivencia Zombi + Selva Inexplorada + Faro)
    cover = Image.new("RGB", (1640, 624), (16, 18, 24))
    panels = [p for p in (z1, s1, z3) if p.exists()]
    if panels:
        pw = 1640 // len(panels)
        for idx, p_path in enumerate(panels):
            pim = Image.open(p_path).convert("RGB")
            p_fit = ImageOps.fit(pim, (pw + 4, 624), method=Image.Resampling.LANCZOS)
            p_fit = ImageEnhance.Brightness(p_fit).enhance(0.72)
            cover.paste(p_fit, (idx * pw, 0))

    draw_c = ImageDraw.Draw(cover, "RGBA")
    for idx in range(1, len(panels)):
        lx = idx * (1640 // len(panels))
        draw_c.line([(lx, 0), (lx, 624)], fill=(0, 0, 0, 255), width=10)

    bold_font_path = r"C:\Windows\Fonts\impact.ttf" if Path(r"C:\Windows\Fonts\impact.ttf").exists() else r"C:\Windows\Fonts\arialbd.ttf"
    sub_font_path = r"C:\Windows\Fonts\arialbd.ttf"
    f_big = ImageFont.truetype(bold_font_path, 66)
    f_sub = ImageFont.truetype(sub_font_path, 34)

    draw_c.rounded_rectangle([360, 155, 1575, 470], radius=28, fill=(10, 12, 18, 225), outline=(255, 220, 0, 255), width=6)
    draw_c.text(
        (968, 255),
        "SUPERVIVENCIA • MISTERIOS • HISTORIAS",
        font=f_big,
        fill=(255, 255, 255, 255),
        anchor="mm",
        stroke_width=5,
        stroke_fill=(0, 0, 0, 255),
    )
    draw_c.rounded_rectangle([540, 330, 1395, 420], radius=16, fill=(215, 35, 35, 255), outline=(0, 0, 0, 255), width=4)
    draw_c.text(
        (968, 375),
        "NUEVOS VIDEOS ILUSTRADOS DÍA, TARDE Y NOCHE",
        font=f_sub,
        fill=(255, 255, 255, 255),
        anchor="mm",
    )
    cover.save(cover_out, quality=95)
    return avatar_out, cover_out


def run_overhaul() -> None:
    avatar_path, cover_path = generate_comic_channel_branding()
    driver = _create_driver(headless=True)

    try:
        # =====================================================================
        # PARTE 1: INSPECCIONAR CRITERIOS EXACTOS DE MONETIZACIÓN Y PROGRESO (92%)
        # =====================================================================
        print("[1/4] Inspeccionando requisitos detallados de Monetización (Estrellas, Suscripciones, Estado del perfil)...")
        driver.get("https://www.facebook.com/professional_dashboard/monetization")
        time.sleep(6)

        for item_label, slug in [("Estrellas", "stars"), ("Suscripciones", "subs"), ("Monetización de contenido", "content_mon")]:
            try:
                els = driver.find_elements(By.XPATH, f"//span[contains(text(), '{item_label}')]/ancestor::div[@role='button' or @role='link' or tabindex='0'][1] | //span[text()='{item_label}']")
                if els:
                    driver.execute_script("arguments[0].click();", els[-1])
                    time.sleep(4)
                    driver.save_screenshot(str(OUTPUT_DIR / f"mon_{slug}.png"))
                    txt = driver.find_element(By.TAG_NAME, "body").text
                    (OUTPUT_DIR / f"mon_{slug}.txt").write_text(txt, encoding="utf-8")
                    print(f"--- Detalle de {item_label} ---")
                    for line in txt.splitlines():
                        if any(k in line.lower() for k in ("criterio", "seguidor", "requisito", "cumpl", "día", "publica", "1,000", "500", "elegib", "invitación")):
                            print("  *", line)
                    driver.get("https://www.facebook.com/professional_dashboard/monetization")
                    time.sleep(4)
            except Exception as e:
                print(f"Nota en {item_label}: {e}")

        # Inspeccionar el 8% faltante en "Estado del perfil (Progreso semanal 92%)"
        driver.get("https://www.facebook.com/professional_dashboard")
        time.sleep(5)
        try:
            prog_els = driver.find_elements(By.XPATH, "//span[contains(text(), 'Progreso semanal') or contains(text(), 'Estado del perfil')]/ancestor::div[@role='button' or @role='link'][1] | //span[contains(text(), 'Progreso semanal')]")
            if prog_els:
                driver.execute_script("arguments[0].click();", prog_els[0])
                time.sleep(4)
                driver.save_screenshot(str(OUTPUT_DIR / "dashboard_profile_progress.png"))
                ptxt = driver.find_element(By.TAG_NAME, "body").text
                (OUTPUT_DIR / "dashboard_profile_progress.txt").write_text(ptxt, encoding="utf-8")
                print("--- Estado del Perfil (Progreso 92%) ---")
                print(ptxt[:1200])
        except Exception as e:
            print(f"Nota en progreso semanal: {e}")

        # =====================================================================
        # PARTE 2: SUBIR FOTO DE PERFIL (AVATAR 2D), PORTADA Y BIO EN /me
        # =====================================================================
        print("\n[2/4] Subiendo Foto de Perfil 2D Cómic, Portada HD y Presentación en facebook.com/me...")
        driver.get("https://www.facebook.com/me")
        time.sleep(6)

        # Abrir el modal "Editar" del perfil donde están Foto del perfil, Foto de portada y Presentación
        edit_prof_btns = driver.find_elements(
            By.XPATH,
            "//div[@role='button']//span[text()='Editar' or text()='Editar perfil']/ancestor::div[@role='button'][1]",
        )
        if edit_prof_btns:
            driver.execute_script("arguments[0].click();", edit_prof_btns[0])
            time.sleep(4)
            driver.save_screenshot(str(OUTPUT_DIR / "edit_profile_modal.png"))

            # En el modal 'Editar perfil', buscar los inputs de archivo o botones Agregar/Editar de Foto del perfil
            add_pic_btns = driver.find_elements(
                By.XPATH,
                "//div[@role='dialog']//span[text()='Agregar' or text()='Editar']/ancestor::div[@role='button'][1]",
            )
            if add_pic_btns:
                # El primer botón Agregar/Editar en el modal corresponde a "Foto del perfil"
                driver.execute_script("arguments[0].click();", add_pic_btns[0])
                time.sleep(3)
                driver.save_screenshot(str(OUTPUT_DIR / "edit_avatar_submodal.png"))

                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                if file_inputs:
                    print("      Enviando archivo de Foto de Perfil (creator_avatar_comic.jpg)...")
                    file_inputs[-1].send_keys(str(avatar_path.resolve()))
                    time.sleep(7)
                    driver.save_screenshot(str(OUTPUT_DIR / "avatar_preview_loaded.png"))

                    save_av_btns = driver.find_elements(
                        By.XPATH,
                        "//div[@role='dialog']//div[@role='button']//span[text()='Guardar' or text()='Save']/ancestor::div[@role='button'][1]",
                    )
                    if save_av_btns:
                        driver.execute_script("arguments[0].click();", save_av_btns[-1])
                        print("      ¡Foto de Perfil guardada exitosamente!")
                        time.sleep(8)

        # Actualizar también la Foto de Portada con el nuevo arte 2D Cómic
        driver.get("https://www.facebook.com/me")
        time.sleep(5)
        cover_btns = driver.find_elements(
            By.XPATH,
            "//span[text()='Editar foto de portada' or text()='Agregar foto de portada']/ancestor::div[@role='button'][1]",
        )
        if cover_btns:
            driver.execute_script("arguments[0].click();", cover_btns[0])
            time.sleep(2.5)
            # Hacer clic en 'Subir foto' si aparece menú desplegable
            upload_menu = driver.find_elements(
                By.XPATH,
                "//span[text()='Subir foto' or text()='Upload photo']/ancestor::div[@role='menuitem' or @role='button'][1]",
            )
            if upload_menu:
                driver.execute_script("arguments[0].click();", upload_menu[0])
                time.sleep(2)
            file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs:
                file_inputs[0].send_keys(str(cover_path.resolve()))
                time.sleep(7)
                save_cov = driver.find_elements(
                    By.XPATH,
                    "//div[@role='button']//span[text()='Guardar cambios' or text()='Save changes']/ancestor::div[@role='button'][1]",
                )
                if save_cov:
                    driver.execute_script("arguments[0].click();", save_cov[-1])
                    print("      ¡Nueva Foto de Portada 2D Cómic guardada exitosamente!")
                    time.sleep(6)

        # Actualizar Presentación (Bio) alineada al canal de historias animadas
        driver.get("https://www.facebook.com/me")
        time.sleep(5)
        edit_bio = driver.find_elements(
            By.XPATH,
            "//span[text()='Editar presentación' or text()='Agregar presentación']/ancestor::div[@role='button'][1]",
        )
        if edit_bio:
            driver.execute_script("arguments[0].click();", edit_bio[0])
            time.sleep(2.5)
            textareas = driver.find_elements(By.XPATH, "//textarea")
            if textareas:
                bio_box = textareas[0]
                new_bio = "Historias animadas de supervivencia, misterios sin resolver y curiosidades todos los dias (Dia, Tarde y Noche). Sigueme!"
                actions = ActionChains(driver)
                actions.move_to_element(bio_box).click()
                actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
                actions.send_keys(new_bio).perform()
                time.sleep(1.5)
                save_b = driver.find_elements(
                    By.XPATH,
                    "//div[@role='button']//span[text()='Guardar' or text()='Save']/ancestor::div[@role='button'][1]",
                )
                if save_b:
                    driver.execute_script("arguments[0].click();", save_b[-1])
                    print("      ¡Presentación (Bio) actualizada!")
                    time.sleep(4)

        # =====================================================================
        # PARTE 3: CAMBIAR NOMBRE DEL PERFIL EN ACCOUNTS CENTER DE META
        # =====================================================================
        print("\n[3/4] Abriendo Centro de Cuentas de Meta para cambiar el nombre del perfil...")
        driver.get("https://accountscenter.facebook.com/profiles")
        time.sleep(6)
        driver.save_screenshot(str(OUTPUT_DIR / "ac_step1_profiles.png"))
        ac_text = driver.find_element(By.TAG_NAME, "body").text
        print("Perfiles en Centro de Cuentas:\n", ac_text[:600])

        # Hacer clic en el perfil 'Chucho Rodríguez'
        prof_cards = driver.find_elements(
            By.XPATH,
            "//span[contains(text(), 'Chucho') or contains(text(), 'Rodríguez')]/ancestor::a[1] | //span[contains(text(), 'Chucho') or contains(text(), 'Rodríguez')]/ancestor::div[@role='button' or @role='link'][1]",
        )
        if prof_cards:
            driver.execute_script("arguments[0].click();", prof_cards[0])
            time.sleep(4)
            driver.save_screenshot(str(OUTPUT_DIR / "ac_step2_profile_detail.png"))

            # Hacer clic en 'Nombre'
            name_links = driver.find_elements(
                By.XPATH,
                "//span[text()='Nombre' or text()='Name']/ancestor::a[1] | //span[text()='Nombre' or text()='Name']/ancestor::div[@role='button' or @role='link'][1]",
            )
            if name_links:
                driver.execute_script("arguments[0].click();", name_links[0])
                time.sleep(4)
                driver.save_screenshot(str(OUTPUT_DIR / "ac_step3_name_form.png"))
                form_txt = driver.find_element(By.TAG_NAME, "body").text
                print("Formulario de Nombre en Meta:\n", form_txt[:800])

                inputs = [i for i in driver.find_elements(By.XPATH, "//input[@type='text']") if i.is_displayed()]
                print(f"      Inputs de nombre encontrados: {len(inputs)}")
                if len(inputs) >= 2:
                    # Cambiar de 'Chucho Rodríguez' a 'Don Curioso' (nombre de creador sin datos personales)
                    first_in = inputs[0]
                    last_in = inputs[-1]

                    for inp, val in [(first_in, "Don"), (last_in, "Curioso")]:
                        actions = ActionChains(driver)
                        actions.move_to_element(inp).click()
                        actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
                        actions.send_keys(val).perform()
                        time.sleep(1)

                    # Si hay un input intermedio (segundo nombre), limpiarlo
                    if len(inputs) == 3:
                        mid_in = inputs[1]
                        actions = ActionChains(driver)
                        actions.move_to_element(mid_in).click()
                        actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).perform()
                        time.sleep(0.5)

                    driver.save_screenshot(str(OUTPUT_DIR / "ac_step4_name_typed.png"))
                    review_btns = driver.find_elements(
                        By.XPATH,
                        "//span[contains(text(), 'Revisar cambio') or contains(text(), 'Review change') or text()='Guardar']/ancestor::div[@role='button'][1] | //button[contains(., 'Revisar')]",
                    )
                    if review_btns:
                        driver.execute_script("arguments[0].click();", review_btns[-1])
                        time.sleep(5)
                        driver.save_screenshot(str(OUTPUT_DIR / "ac_step5_after_review.png"))
                        rev_txt = driver.find_element(By.TAG_NAME, "body").text
                        print("Resultado tras Revisar cambio:\n", rev_txt[:800])

                        done_btns = driver.find_elements(
                            By.XPATH,
                            "//span[contains(text(), 'Guardar cambios') or contains(text(), 'Save changes') or text()='Listo' or text()='Done']/ancestor::div[@role='button'][1]",
                        )
                        if done_btns:
                            driver.execute_script("arguments[0].click();", done_btns[-1])
                            time.sleep(5)
                            driver.save_screenshot(str(OUTPUT_DIR / "ac_step6_name_saved.png"))
                            print("      ¡Cambio de nombre aplicado!")

        # Captura final del perfil actualizado
        print("\n[4/4] Verificando vista final del perfil en facebook.com/me...")
        driver.get("https://www.facebook.com/me")
        time.sleep(6)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_profile_final_verified.png"))

    finally:
        driver.quit()


if __name__ == "__main__":
    run_overhaul()
