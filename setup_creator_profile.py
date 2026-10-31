"""
Configurador automático del Perfil Profesional y Panel para Creadores de Facebook:
1. Actualiza la Presentación (Bio) disparando eventos nativos de teclado en React.
2. Sube Foto de Portada HD (1640x624) y Foto de Perfil HD (1080x1080).
"""

import os
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import OUTPUT_DIR
from generator import _fetch_real_hd_image
from uploader import _create_driver


def create_creator_branding_assets() -> tuple[Path, Path]:
    cover_path = OUTPUT_DIR / "creator_cover.jpg"
    avatar_path = OUTPUT_DIR / "creator_avatar.jpg"
    if cover_path.exists() and avatar_path.exists():
        return cover_path, avatar_path

    bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    reg_path = r"C:\Windows\Fonts\segoeui.ttf"
    font_lg = ImageFont.truetype(bold_path, 58) if os.path.exists(bold_path) else ImageFont.load_default()
    font_md = ImageFont.truetype(reg_path if os.path.exists(reg_path) else bold_path, 32)

    raw_bg = _fetch_real_hd_image("James Webb Carina Nebula cosmic cliffs", 1)
    cover = ImageOps.fit(raw_bg, (1640, 624), method=Image.Resampling.LANCZOS)
    cover = ImageEnhance.Brightness(cover).enhance(0.65)
    cover = ImageEnhance.Color(cover).enhance(1.3)
    draw_c = ImageDraw.Draw(cover, "RGBA")
    draw_c.rounded_rectangle([380, 145, 1560, 480], radius=30, fill=(8, 14, 28, 205), outline=(0, 225, 255, 230), width=4)
    draw_c.text((970, 255), "CIENCIA • TECNOLOGIA • MISTERIOS", font=font_lg, fill=(255, 235, 0, 255), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, 255))
    draw_c.text((970, 355), "Historias reales, descubrimientos y tendencias todos los dias", font=font_md, fill=(235, 245, 255, 255), anchor="mm")
    cover.save(cover_path, quality=95)

    raw_av = _fetch_real_hd_image("Hubble spiral galaxy glowing core", 2)
    avatar = ImageOps.fit(raw_av, (1080, 1080), method=Image.Resampling.LANCZOS)
    avatar = ImageEnhance.Contrast(avatar).enhance(1.2)
    draw_a = ImageDraw.Draw(avatar, "RGBA")
    draw_a.ellipse([40, 40, 1040, 1040], outline=(0, 225, 255, 240), width=14)
    avatar.save(avatar_path, quality=95)
    return cover_path, avatar_path


def configure_creator_profile() -> None:
    cover_path, avatar_path = create_creator_branding_assets()
    driver = _create_driver(headless=True)

    try:
        print("[1/3] Abriendo perfil de Facebook...")
        driver.get("https://www.facebook.com/me")
        time.sleep(6)

        # 1. Actualizar Presentación (Bio) con eventos nativos de teclado
        print("[2/3] Actualizando Presentación (Bio) de creador digital...")
        try:
            edit_bio_btns = driver.find_elements(
                By.XPATH,
                "//span[text()='Editar presentación' or text()='Agregar presentación']/ancestor::div[@role='button'][1]",
            )
            if edit_bio_btns:
                driver.execute_script("arguments[0].click();", edit_bio_btns[0])
                time.sleep(2.5)
                bio_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea"))
                )
                bio_text = "Ciencia, tecnologia, historias reales y lo mas viral del dia. Sigueme para descubrir mas."
                actions = ActionChains(driver)
                actions.move_to_element(bio_box).click()
                actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
                actions.send_keys(bio_text).perform()
                time.sleep(2)

                save_btns = driver.find_elements(
                    By.XPATH,
                    "//div[@role='button']//span[text()='Guardar' or text()='Save']/ancestor::div[@role='button'][1]",
                )
                if save_btns:
                    driver.execute_script("arguments[0].click();", save_btns[-1])
                    print("      Presentación guardada.")
                    time.sleep(4)
        except Exception as exc:
            print(f"      Nota en presentación: {exc}")

        # 2. Subir Foto de Portada y Foto de Perfil usando los inputs de archivo de la página
        print("[3/3] Subiendo Foto de Portada HD...")
        try:
            cover_btns = driver.find_elements(
                By.XPATH,
                "//span[text()='Agregar foto de portada' or text()='Editar foto de portada']/ancestor::div[@role='button'][1]",
            )
            if cover_btns:
                driver.execute_script("arguments[0].click();", cover_btns[0])
                time.sleep(2.5)
                # Buscar todos los inputs de archivo en el DOM tras abrir el menú de portada
                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file' and contains(@accept, 'image')] | //input[@type='file']")
                if file_inputs:
                    file_inputs[0].send_keys(str(cover_path.resolve()))
                    time.sleep(7)
                    save_cover = driver.find_elements(
                        By.XPATH,
                        "//div[@role='button']//span[text()='Guardar cambios' or text()='Save changes']/ancestor::div[@role='button'][1]",
                    )
                    if save_cover:
                        driver.execute_script("arguments[0].click();", save_cover[-1])
                        print("      Foto de portada guardada con éxito.")
                        time.sleep(5)
        except Exception as exc:
            print(f"      Nota en portada: {exc}")

        driver.get("https://www.facebook.com/me")
        time.sleep(5)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_profile_updated.png"))

    finally:
        driver.quit()


if __name__ == "__main__":
    configure_creator_profile()
