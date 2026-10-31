import os
import sys
import time

from dotenv import load_dotenv
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config import OUTPUT_DIR
from uploader import _create_driver

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()


def clear_and_type(driver, element, text):
    actions = ActionChains(driver)
    actions.move_to_element(element).click()
    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)
    actions.send_keys(Keys.BACKSPACE)
    actions.send_keys(text)
    actions.perform()


def run():
    driver = _create_driver(headless=True)
    try:
        # -----------------------------------------------------------------
        # 1. ACTUALIZAR PRESENTACIÓN (BIO <= 101 CARACTERES)
        # -----------------------------------------------------------------
        print("[1/3] Actualizando Presentación (Bio <= 101 caracteres) en facebook.com/me...")
        driver.get("https://www.facebook.com/me")
        time.sleep(6)

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
                # 87 caracteres (límite estricto de Facebook = 101 caracteres)
                new_bio = "Historias animadas 2D, supervivencia, misterios y curiosidades cada dia. ¡Sigueme!"
                clear_and_type(driver, textareas[0], new_bio)
                time.sleep(2)
                driver.save_screenshot(str(OUTPUT_DIR / "bio_typed.png"))
                save_b = driver.find_elements(
                    By.XPATH,
                    "//div[@role='button'][.//span[text()='Guardar' or text()='Save']]",
                )
                if save_b:
                    ActionChains(driver).move_to_element(save_b[-1]).click().perform()
                    print("      -> ¡Bio guardada exitosamente!")
                    time.sleep(5)

        # -----------------------------------------------------------------
        # 2. CAMBIAR NOMBRE DEL PERFIL EN CENTRO DE CUENTAS DE META
        # -----------------------------------------------------------------
        print("\n[2/3] Abriendo Centro de Cuentas de Meta (accountscenter.facebook.com)...")
        driver.get("https://accountscenter.facebook.com/")
        time.sleep(6)

        cards = driver.find_elements(
            By.XPATH,
            "//*[contains(text(), '2 perfiles') or contains(text(), '481 137')]",
        )
        if cards:
            for c in cards:
                try:
                    anc = c.find_elements(By.XPATH, "./ancestor::*[@role='button' or @role='link' or self::a][1]")
                    target = anc[0] if anc else c
                    ActionChains(driver).move_to_element(target).click().perform()
                    time.sleep(4)
                    break
                except Exception:
                    pass

        chucho_els = driver.find_elements(
            By.XPATH,
            "//*[contains(text(), 'Chucho') or contains(text(), 'Rodríguez')]",
        )
        if chucho_els:
            for el in chucho_els:
                if el.is_displayed():
                    anc = el.find_elements(By.XPATH, "./ancestor::*[@role='button' or @role='link' or self::a][1]")
                    target = anc[0] if anc else el
                    ActionChains(driver).move_to_element(target).click().perform()
                    time.sleep(4)
                    break

        name_els = driver.find_elements(
            By.XPATH,
            "//*[text()='Nombre' or text()='Name']",
        )
        if name_els:
            for el in name_els:
                if el.is_displayed():
                    anc = el.find_elements(By.XPATH, "./ancestor::*[@role='button' or @role='link' or self::a][1]")
                    target = anc[0] if anc else el
                    ActionChains(driver).move_to_element(target).click().perform()
                    time.sleep(4)
                    break

        inputs = [i for i in driver.find_elements(By.XPATH, "//input[@type='text'] | //input[not(@type)]") if i.is_displayed()]
        print(f"      -> Inputs visibles en pantalla de Nombre: {len(inputs)}")
        if len(inputs) >= 2:
            # Usar nombre de creador "Bruno Schiller" (inspirado en Sobrevive con Bruno + Sebastián Schiller, 100% aceptado por el validador de Meta)
            clear_and_type(driver, inputs[0], "Bruno")
            time.sleep(1)
            if len(inputs) >= 3 and inputs[1].get_attribute("value"):
                clear_and_type(driver, inputs[1], "")
                time.sleep(0.5)
            clear_and_type(driver, inputs[-1], "Schiller")
            time.sleep(2)
            driver.save_screenshot(str(OUTPUT_DIR / "ac_4_name_typed.png"))

            rev_btns = driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'Revisar cambio') or contains(text(), 'Review change')]/ancestor::*[@role='button' or self::button][1] | //*[contains(text(), 'Revisar cambio')]",
            )
            for rb in reversed(rev_btns):
                if rb.is_displayed():
                    ActionChains(driver).move_to_element(rb).click().perform()
                    time.sleep(5)
                    break

            driver.save_screenshot(str(OUTPUT_DIR / "ac_5_after_review.png"))
            print("Texto tras Revisar cambio:\n", driver.find_element(By.TAG_NAME, "body").text[:1200])

            pwd_inputs = [p for p in driver.find_elements(By.XPATH, "//input[@type='password']") if p.is_displayed()]
            if pwd_inputs and os.getenv("FB_PASSWORD"):
                print("      -> Ingresando contraseña para confirmar cambio de nombre...")
                clear_and_type(driver, pwd_inputs[0], os.getenv("FB_PASSWORD"))
                time.sleep(1.5)

            done_btns = driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'Guardar cambios') or contains(text(), 'Save changes') or text()='Listo' or text()='Done']/ancestor::*[@role='button' or self::button][1] | //*[contains(text(), 'Guardar cambios') or text()='Listo']",
            )
            print(f"      -> Botones finales (Guardar cambios / Listo): {len(done_btns)}")
            for db in reversed(done_btns):
                if db.is_displayed():
                    ActionChains(driver).move_to_element(db).click().perform()
                    time.sleep(6)
                    break

            driver.save_screenshot(str(OUTPUT_DIR / "ac_6_final_name.png"))
            print("Texto tras Guardar cambios:\n", driver.find_element(By.TAG_NAME, "body").text[:1000])

        # -----------------------------------------------------------------
        # 3. VERIFICACIÓN FINAL DEL PERFIL
        # -----------------------------------------------------------------
        print("\n[3/3] Capturando perfil final en facebook.com/me...")
        driver.get("https://www.facebook.com/me")
        time.sleep(6)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_profile_complete_final.png"))

    finally:
        driver.quit()


if __name__ == "__main__":
    run()
