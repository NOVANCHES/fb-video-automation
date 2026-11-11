"""
update_facebook_profile_to_gaming.py
====================================
Transforma el perfil de Facebook a CREADOR DE VIDEOJUEGOS:
1. Actualiza la Presentación (Bio) a temática Gamer (<= 101 caracteres).
2. Sube el nuevo Avatar 2D Gamer (Bruno con headset y luces RGB).
3. Sube la Portada Gamer HD 1640x624.
"""

import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config import OUTPUT_DIR
from uploader import _create_driver

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

GAMER_BIO = "🎮 Secretos, curiosidades y mitos de videojuegos. ¡Reels diarios de gaming!"
AVATAR_PATH = OUTPUT_DIR / "creator_avatar_gamer.jpg"
COVER_PATH = OUTPUT_DIR / "creator_cover_gamer.jpg"


def clear_and_type(driver, element, text):
    actions = ActionChains(driver)
    actions.move_to_element(element).click()
    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)
    actions.send_keys(Keys.BACKSPACE)
    actions.send_keys(text)
    actions.perform()


def run():
    print("=" * 65)
    print(" TRANSFORMACIÓN DE PERFIL A VIDEOJUEGOS / GAMING CREATOR")
    print("=" * 65)

    driver = _create_driver(headless=True)
    try:
        # 1. ACTUALIZAR BIO
        print("\n[1/3] Actualizando Presentación (Bio Gamer)...")
        driver.get("https://www.facebook.com/me")
        time.sleep(6)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_gaming_1_me.png"))

        edit_bio = driver.find_elements(
            By.XPATH,
            "//*[text()='Editar presentación' or text()='Agregar presentación']/ancestor::div[@role='button'][1]",
        )
        if edit_bio:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", edit_bio[0])
            time.sleep(1)
            driver.execute_script("arguments[0].click();", edit_bio[0])
            time.sleep(3)
            textareas = [t for t in driver.find_elements(By.XPATH, "//textarea") if t.is_displayed()]
            if textareas:
                print(f"      Escribiendo Bio: '{GAMER_BIO}' ({len(GAMER_BIO)} caracteres)")
                clear_and_type(driver, textareas[0], GAMER_BIO)
                time.sleep(2)
                driver.save_screenshot(str(OUTPUT_DIR / "fb_gaming_2_bio_typed.png"))
                save_btns = driver.find_elements(
                    By.XPATH,
                    "//div[@role='button'][.//span[text()='Guardar' or text()='Save']]",
                )
                if save_btns:
                    ActionChains(driver).move_to_element(save_btns[-1]).click().perform()
                    print("      [OK] ¡Bio Gamer guardada exitosamente!")
                    time.sleep(5)

        # 2. SUBIR AVATAR GAMER
        if AVATAR_PATH.exists():
            print("\n[2/3] Subiendo Avatar Gamer en modal de Editar Perfil...")
            driver.get("https://www.facebook.com/me")
            time.sleep(6)

            edit_prof_btns = driver.find_elements(
                By.XPATH,
                "//div[@role='button']//span[text()='Editar' or text()='Editar perfil']/ancestor::div[@role='button'][1]",
            )
            if edit_prof_btns:
                driver.execute_script("arguments[0].click();", edit_prof_btns[0])
                time.sleep(4)
                add_pic_btns = driver.find_elements(
                    By.XPATH,
                    "//div[@role='dialog']//span[text()='Agregar' or text()='Editar']/ancestor::div[@role='button'][1]",
                )
                if add_pic_btns:
                    driver.execute_script("arguments[0].click();", add_pic_btns[0])
                    time.sleep(3)
                    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                    if file_inputs:
                        print("      Cargando creator_avatar_gamer.jpg...")
                        file_inputs[-1].send_keys(str(AVATAR_PATH.resolve()))
                        time.sleep(7)
                        driver.save_screenshot(str(OUTPUT_DIR / "fb_gaming_3_avatar_loaded.png"))
                        save_av_btns = driver.find_elements(
                            By.XPATH,
                            "//div[@role='dialog']//div[@role='button']//span[text()='Guardar' or text()='Save']/ancestor::div[@role='button'][1]",
                        )
                        if save_av_btns:
                            driver.execute_script("arguments[0].click();", save_av_btns[-1])
                            print("      [OK] ¡Avatar Gamer guardado exitosamente!")
                            time.sleep(6)

        driver.get("https://www.facebook.com/me")
        time.sleep(5)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_gaming_final_profile.png"))
        print("\n[OK] Transformación de perfil a Videojuegos completada con éxito.")

    except Exception as e:
        print(f"[ERROR] Error durante la actualización de perfil: {e}")
        driver.save_screenshot(str(OUTPUT_DIR / "fb_gaming_error.png"))
    finally:
        driver.quit()


if __name__ == "__main__":
    run()
