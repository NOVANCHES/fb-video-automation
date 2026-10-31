import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config import OUTPUT_DIR
from uploader import _create_driver

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
AVATAR_IMG = OUTPUT_DIR / "creator_avatar_comic.jpg"


def run():
    driver = _create_driver(headless=True)
    try:
        # -----------------------------------------------------------------
        # 1. SUBIR FOTO DE PERFIL USANDO EL INPUT DENTRO DEL DIALOG
        # -----------------------------------------------------------------
        print("[1/4] Subiendo Foto de Perfil 2D Cómic y actualizando Presentación...")
        driver.get("https://www.facebook.com/me")
        time.sleep(6)

        # Actualizar Presentación primero directamente en la columna izquierda
        try:
            edit_bio = driver.find_elements(
                By.XPATH,
                "//span[text()='Editar presentación' or text()='Agregar presentación']/ancestor::div[@role='button'][1]",
            )
            if edit_bio:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", edit_bio[0])
                time.sleep(1)
                driver.execute_script("arguments[0].click();", edit_bio[0])
                time.sleep(3)
                textareas = driver.find_elements(By.XPATH, "//textarea")
                if textareas:
                    bio_box = textareas[0]
                    new_bio = "🎬 Historias animadas 2D, supervivencia, misterios reales y curiosidades todos los días. ¡Sígueme y comenta tu teoría! 🔥"
                    driver.execute_script(
                        """
                        const ta = arguments[0];
                        const val = arguments[1];
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                        nativeSetter.call(ta, val);
                        ta.dispatchEvent(new Event('input', { bubbles: true }));
                        ta.dispatchEvent(new Event('change', { bubbles: true }));
                        """,
                        bio_box,
                        new_bio,
                    )
                    time.sleep(2)
                    save_b = driver.find_elements(
                        By.XPATH,
                        "//div[@role='button']//span[text()='Guardar' or text()='Save']/ancestor::div[@role='button'][1]",
                    )
                    if save_b:
                        driver.execute_script("arguments[0].click();", save_b[-1])
                        print("      -> ¡Presentación (Bio) actualizada!")
                        time.sleep(4)
        except Exception as e:
            print("      -> Aviso en Bio:", e)

        # Ahora abrir modal Editar -> Elegir foto del perfil -> input[@type='file'] dentro del dialog
        driver.get("https://www.facebook.com/me")
        time.sleep(5)
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

                # Buscar inputs de tipo file DENTRO de div[@role='dialog'] o que acepten image/*
                dialog_inputs = driver.find_elements(By.XPATH, "//div[@role='dialog']//input[@type='file']")
                all_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                print(f"      -> Inputs en dialog: {len(dialog_inputs)} | Inputs totales: {len(all_inputs)}")
                for idx, inp in enumerate(all_inputs):
                    print(f"         input[{idx}] accept={inp.get_attribute('accept')}")

                target_input = None
                if dialog_inputs:
                    target_input = dialog_inputs[0]
                else:
                    for inp in all_inputs:
                        acc = (inp.get_attribute("accept") or "").lower()
                        if "image" in acc and "video" not in acc:
                            target_input = inp
                            break
                    if not target_input and all_inputs:
                        target_input = all_inputs[0]

                if target_input:
                    print("      -> Enviando creator_avatar_comic.jpg al input de imagen...")
                    target_input.send_keys(str(AVATAR_IMG.resolve()))
                    time.sleep(7)
                    driver.save_screenshot(str(OUTPUT_DIR / "avatar_crop_dialog.png"))

                    save_av_btns = driver.find_elements(
                        By.XPATH,
                        "//div[@role='dialog']//div[@role='button']//span[text()='Guardar' or text()='Save']/ancestor::div[@role='button'][1] | //div[@aria-label='Guardar' and @role='button']",
                    )
                    print(f"      -> Botones Guardar en modal de Avatar: {len(save_av_btns)}")
                    if save_av_btns:
                        driver.execute_script("arguments[0].click();", save_av_btns[-1])
                        print("      -> ¡Clic en Guardar Foto de Perfil ejecutado! Esperando 10s...")
                        time.sleep(10)
                        driver.save_screenshot(str(OUTPUT_DIR / "avatar_after_save.png"))

        # -----------------------------------------------------------------
        # 2. ACTIVAR "NOTIFICARME" EN MONETIZACIÓN E INSPECCIONAR NIVEL 3
        # -----------------------------------------------------------------
        print("\n[2/4] Activando 'Notificarme' en Monetización e inspeccionando Nivel 3...")
        for prog_name, slug in [("Estrellas", "Estrellas"), ("Suscripciones", "Suscripciones"), ("Monetización de contenido", "Monetización de contenido")]:
            try:
                driver.get("https://www.facebook.com/professional_dashboard/monetization")
                time.sleep(5)
                items = driver.find_elements(
                    By.XPATH,
                    f"//span[contains(text(), '{slug}')]/ancestor::div[@role='button' or @role='link'][1] | //span[contains(text(), '{slug}')]",
                )
                if items:
                    driver.execute_script("arguments[0].click();", items[0])
                    time.sleep(4)
                    # Hacer scroll para ver tarjetas inferiores de criterios
                    driver.execute_script("window.scrollBy(0, 450);")
                    time.sleep(2)
                    driver.save_screenshot(str(OUTPUT_DIR / f"mon_criteria_{slug[:5]}.png"))

                    notif_btns = driver.find_elements(
                        By.XPATH,
                        "//div[@role='button']//span[text()='Notificarme' or text()='Notify me']/ancestor::div[@role='button'][1]",
                    )
                    if notif_btns:
                        driver.execute_script("arguments[0].click();", notif_btns[0])
                        time.sleep(3)
                        print(f"      -> ¡'Notificarme' activado en {prog_name}!")
                    else:
                        print(f"      -> {prog_name}: Notificación ya activa o no requiere clic.")
            except Exception as e:
                print(f"      -> Aviso en {prog_name}:", e)

        # Ver requisitos de Nivel 3 en Progreso Semanal
        try:
            driver.get("https://www.facebook.com/professional_dashboard")
            time.sleep(5)
            prog_links = driver.find_elements(
                By.XPATH,
                "//span[contains(text(), 'Progreso semanal') or contains(text(), '92%')]/ancestor::a[1] | //span[contains(text(), 'Progreso semanal')]",
            )
            if prog_links:
                driver.execute_script("arguments[0].click();", prog_links[0])
                time.sleep(4)
                niv3 = driver.find_elements(By.XPATH, "//span[contains(text(), 'Nivel 3')]")
                if niv3:
                    driver.execute_script("arguments[0].click();", niv3[0])
                    time.sleep(3)
                    driver.save_screenshot(str(OUTPUT_DIR / "dashboard_nivel3.png"))
                    print("--- Texto Nivel 3 ---")
                    for l in [x.strip() for x in driver.find_element(By.TAG_NAME, "body").text.splitlines() if x.strip()]:
                        print("  *", l)
        except Exception as e:
            print("      -> Aviso Nivel 3:", e)

        # -----------------------------------------------------------------
        # 3. CAMBIAR NOMBRE DEL PERFIL EN CENTRO DE CUENTAS DE META
        # -----------------------------------------------------------------
        print("\n[3/4] Cambiando el nombre del perfil en Centro de Cuentas de Meta...")
        driver.get("https://accountscenter.facebook.com/")
        time.sleep(6)

        # Clic en la tarjeta "+52 481 137 9548 / 2 perfiles"
        prof_cards = driver.find_elements(
            By.XPATH,
            "//span[contains(text(), 'perfiles') or contains(text(), '481')]/ancestor::div[@role='button' or @role='link'][1] | //a[contains(@href, 'profiles')] | //span[contains(text(), '2 perfiles')]",
        )
        print(f"      -> Tarjetas de perfiles encontradas: {len(prof_cards)}")
        if prof_cards:
            driver.execute_script("arguments[0].click();", prof_cards[0])
            time.sleep(4)
        else:
            # Clic por elemento en la zona central
            el = driver.execute_script("return document.elementFromPoint(600, 320);")
            if el:
                driver.execute_script("arguments[0].click();", el)
                time.sleep(4)

        driver.save_screenshot(str(OUTPUT_DIR / "ac_profiles_list.png"))
        print("Texto en lista de perfiles:\n", driver.find_element(By.TAG_NAME, "body").text[:800])

        # Clic en Chucho Rodríguez
        chucho_els = driver.find_elements(
            By.XPATH,
            "//span[contains(text(), 'Chucho') or contains(text(), 'Rodríguez')]/ancestor::div[@role='button' or @role='link'][1] | //span[contains(text(), 'Chucho')]",
        )
        print(f"      -> Elementos 'Chucho' encontrados: {len(chucho_els)}")
        if chucho_els:
            driver.execute_script("arguments[0].click();", chucho_els[0])
            time.sleep(4)
            driver.save_screenshot(str(OUTPUT_DIR / "ac_chucho_detail.png"))
            print("Texto en detalle del perfil:\n", driver.find_element(By.TAG_NAME, "body").text[:800])

            # Clic en Nombre
            name_els = driver.find_elements(
                By.XPATH,
                "//span[text()='Nombre' or text()='Name']/ancestor::div[@role='button' or @role='link'][1] | //a[contains(@href, 'name')] | //span[text()='Nombre']",
            )
            print(f"      -> Elementos 'Nombre' encontrados: {len(name_els)}")
            if name_els:
                driver.execute_script("arguments[0].click();", name_els[0])
                time.sleep(4)
                driver.save_screenshot(str(OUTPUT_DIR / "ac_name_form.png"))
                print("Texto en formulario de Nombre:\n", driver.find_element(By.TAG_NAME, "body").text[:1000])

                inputs = [i for i in driver.find_elements(By.XPATH, "//input[@type='text']") if i.is_displayed()]
                print(f"      -> Inputs de texto visibles: {len(inputs)}")
                for idx, inp in enumerate(inputs):
                    print(f"         input[{idx}] value='{inp.get_attribute('value')}'")

                if len(inputs) >= 2:
                    # Usar setter nativo de React para que Meta detecte el cambio en el estado del botón "Revisar cambio"
                    def set_react_input(el, val):
                        driver.execute_script(
                            """
                            const input = arguments[0];
                            const value = arguments[1];
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(input, value);
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('blur', { bubbles: true }));
                            """,
                            el,
                            val,
                        )

                    set_react_input(inputs[0], "Don")
                    time.sleep(0.5)
                    if len(inputs) >= 3:
                        set_react_input(inputs[1], "")
                        time.sleep(0.5)
                    set_react_input(inputs[-1], "Curioso")
                    time.sleep(1.5)
                    driver.save_screenshot(str(OUTPUT_DIR / "ac_name_filled.png"))

                    rev_btns = driver.find_elements(
                        By.XPATH,
                        "//span[contains(text(), 'Revisar cambio') or contains(text(), 'Review change')]/ancestor::div[@role='button'][1] | //button[contains(., 'Revisar')] | //span[contains(text(), 'Revisar cambio')]",
                    )
                    print(f"      -> Botones 'Revisar cambio': {len(rev_btns)}")
                    if rev_btns:
                        driver.execute_script("arguments[0].click();", rev_btns[-1])
                        time.sleep(5)
                        driver.save_screenshot(str(OUTPUT_DIR / "ac_name_review.png"))
                        print("Texto tras Revisar cambio:\n", driver.find_element(By.TAG_NAME, "body").text[:1000])

                        pwd_inputs = driver.find_elements(By.XPATH, "//input[@type='password']")
                        if pwd_inputs and os.getenv("FB_PASSWORD"):
                            print("      -> Ingresando contraseña de confirmación en Meta Accounts Center...")
                            driver.execute_script(
                                """
                                const input = arguments[0];
                                const value = arguments[1];
                                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                nativeInputValueSetter.call(input, value);
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                """,
                                pwd_inputs[0],
                                os.getenv("FB_PASSWORD"),
                            )
                            time.sleep(1)

                        done_btns = driver.find_elements(
                            By.XPATH,
                            "//span[contains(text(), 'Guardar cambios') or contains(text(), 'Save changes') or text()='Listo' or text()='Done']/ancestor::div[@role='button'][1] | //span[contains(text(), 'Guardar cambios') or text()='Listo']",
                        )
                        if done_btns:
                            driver.execute_script("arguments[0].click();", done_btns[-1])
                            time.sleep(6)
                            driver.save_screenshot(str(OUTPUT_DIR / "ac_name_saved.png"))
                            print("      -> ¡Cambio de nombre completado!")

        # -----------------------------------------------------------------
        # 4. VERIFICACIÓN FINAL EN FACEBOOK.COM/ME
        # -----------------------------------------------------------------
        print("\n[4/4] Verificando vista final en facebook.com/me...")
        driver.get("https://www.facebook.com/me")
        time.sleep(6)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_profile_after_all.png"))

    finally:
        driver.quit()


if __name__ == "__main__":
    run()
