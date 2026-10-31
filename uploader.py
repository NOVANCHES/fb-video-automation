"""
Módulo 3: Subida Automática a Facebook mediante Selenium (Microsoft Edge) con sesión persistente.
"""

import argparse
import base64
import json
import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import (
    BROWSER_PROFILE_DIR,
    FB_EMAIL,
    FB_PAGE_NAME,
    FB_PASSWORD,
    OUTPUT_DIR,
)


def _create_driver(headless: bool = False) -> webdriver.Remote:
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_bin = next((p for p in edge_paths if os.path.exists(p)), None)

    edge_options = EdgeOptions()
    if edge_bin:
        edge_options.binary_location = edge_bin

    is_cloud = os.getenv("GITHUB_ACTIONS", "").lower() == "true"
    if is_cloud:
        cloud_prof = OUTPUT_DIR / "cloud_edge_profile"
        cloud_prof.mkdir(parents=True, exist_ok=True)
        edge_options.add_argument(f"--user-data-dir={cloud_prof.resolve()}")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--disable-dev-shm-usage")
    else:
        edge_options.add_argument(f"--user-data-dir={BROWSER_PROFILE_DIR.resolve()}")
        edge_options.add_argument("--profile-directory=Default")

    edge_options.add_argument("--disable-notifications")
    edge_options.add_argument("--lang=es-LA")
    edge_options.add_argument("--window-size=1366,900")
    edge_options.add_argument("--disable-blink-features=AutomationControlled")
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    edge_options.add_experimental_option("useAutomationExtension", False)

    if headless or is_cloud:
        edge_options.add_argument("--headless=new")

    driver = webdriver.Edge(options=edge_options)
    driver.set_page_load_timeout(60)
    return driver


def _close_inner_popup_only(driver: webdriver.Remote) -> None:
    """
    Si aparece un segundo diálogo pequeño encima del diálogo principal 'Crear reel',
    cierra únicamente el diálogo interno sin tocar la X de 'Crear reel'.
    """
    try:
        dialogs = driver.find_elements(By.XPATH, "//div[@role='dialog']")
        if len(dialogs) >= 2:
            inner = dialogs[-1]
            close_btns = inner.find_elements(
                By.XPATH, ".//div[@aria-label='Cerrar' or @aria-label='Close'][@role='button']"
            )
            if close_btns:
                driver.execute_script("arguments[0].click();", close_btns[0])
                time.sleep(1.5)
    except Exception:
        pass


def _ensure_logged_in(driver: webdriver.Remote) -> None:
    driver.get("https://www.facebook.com/")
    time.sleep(4)

    has_c_user = any(c.get("name") == "c_user" for c in driver.get_cookies())
    cookies_b64 = os.getenv("FB_COOKIES_B64", "").strip()

    # Si no hay cookie c_user activa y tenemos FB_COOKIES_B64, inyectar cookies de inmediato
    if not has_c_user and cookies_b64:
        try:
            print("[Login] Restaurando sesión activa desde FB_COOKIES_B64 (Modo Nube)...")
            cookies = json.loads(base64.b64decode(cookies_b64).decode("utf-8"))
            for c in cookies:
                cookie_dict = {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c.get("domain", ".facebook.com"),
                    "path": c.get("path", "/"),
                    "secure": c.get("secure", True),
                }
                if "expiry" in c and c["expiry"]:
                    cookie_dict["expiry"] = int(c["expiry"])
                try:
                    driver.add_cookie(cookie_dict)
                except Exception:
                    pass
            driver.get("https://www.facebook.com/me")
            time.sleep(5)
            has_c_user = any(c.get("name") == "c_user" for c in driver.get_cookies())
        except Exception as exc:
            print(f"      Aviso al restaurar FB_COOKIES_B64: {exc}")

    email_inputs = driver.find_elements(By.NAME, "email")
    pass_inputs = driver.find_elements(By.NAME, "pass")

    if not has_c_user and email_inputs and pass_inputs:
        print(f"[Login] Iniciando sesión en Facebook con '{FB_EMAIL}'...")
        email_el = email_inputs[0]
        pass_el = pass_inputs[0]

        email_el.clear()
        email_el.send_keys(FB_EMAIL)
        time.sleep(0.6)

        pass_el.clear()
        pass_el.send_keys(FB_PASSWORD)
        time.sleep(0.6)
        pass_el.send_keys(Keys.RETURN)

        time.sleep(7)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_status.png"))
    else:
        print("[Login] Sesión activa detectada en el perfil persistente.")
        try:
            active_cookies = driver.get_cookies()
            if active_cookies:
                b64_str = base64.b64encode(json.dumps(active_cookies).encode("utf-8")).decode("ascii")
                (OUTPUT_DIR / "fb_cookies.b64").write_text(b64_str, encoding="utf-8")
        except Exception:
            pass


def _switch_to_page_profile_if_needed(driver: webdriver.Remote, page_name: str) -> None:
    if not page_name:
        return

    print(f"[Página] Verificando perfil activo para la página: '{page_name}'...")
    try:
        account_btns = driver.find_elements(
            By.XPATH,
            "//div[@aria-label='Tu perfil' or @aria-label='Cuenta' or @aria-label='Account' or @aria-label='Controles y configuración de la cuenta']//div[@role='button'] | //svg[@aria-label='Tu perfil']/ancestor::div[@role='button']",
        )
        if account_btns:
            driver.execute_script("arguments[0].click();", account_btns[0])
            time.sleep(2.5)
            switch_targets = driver.find_elements(
                By.XPATH,
                f"//span[contains(translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{page_name.upper()}')]/ancestor::div[@role='button' or @role='menuitem'][1]",
            )
            if switch_targets:
                print(f"      Cambiando al perfil de la página '{page_name}'...")
                driver.execute_script("arguments[0].click();", switch_targets[0])
                time.sleep(5)
            else:
                see_all = driver.find_elements(
                    By.XPATH,
                    "//span[contains(text(), 'Ver todos los perfiles') or contains(text(), 'See all profiles')]/ancestor::div[@role='button'][1]",
                )
                if see_all:
                    driver.execute_script("arguments[0].click();", see_all[0])
                    time.sleep(2.5)
                    switch_targets = driver.find_elements(
                        By.XPATH,
                        f"//span[contains(translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{page_name.upper()}')]/ancestor::div[@role='button' or @role='menuitem' or @role='radio'][1]",
                    )
                    if switch_targets:
                        print(f"      Cambiando al perfil de la página '{page_name}'...")
                        driver.execute_script("arguments[0].click();", switch_targets[0])
                        time.sleep(5)
                else:
                    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(1)
    except Exception as exc:
        print(f"      Nota al verificar cambio de perfil: {exc}")


def upload_video_to_facebook(
    video_path: Path = OUTPUT_DIR / "video_final.mp4",
    caption: str = "¡Mira este video hasta el final! #reels #viral",
    headless: bool = False,
) -> None:
    video_abs_path = str(video_path.resolve())
    if not video_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de video a subir: {video_abs_path}")

    print(f"[Subida] Iniciando navegador para publicar: {video_abs_path}")
    driver = _create_driver(headless=headless)

    try:
        _ensure_logged_in(driver)
        _switch_to_page_profile_if_needed(driver, FB_PAGE_NAME)

        print("[Subida] Abriendo interfaz de creación de Facebook Reels...")
        driver.get("https://www.facebook.com/reels/create")
        time.sleep(5)

        print("[Subida] Adjuntando archivo MP4...")
        file_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@type='file' and contains(@accept, 'video')] | //input[@type='file']")
            )
        )
        file_input.send_keys(video_abs_path)
        print("      Archivo cargado. Esperando a que se habilite 'Siguiente' (12s)...")
        time.sleep(12)
        _close_inner_popup_only(driver)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_step1_loaded.png"))

        # Hacer clic en 'Siguiente' (Paso 1 -> Audio/Edición, Paso 2 -> Descripción/Compartir)
        for step in range(2):
            _close_inner_popup_only(driver)
            try:
                next_btn = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[@role='button' and not(@aria-disabled='true')]//span[text()='Siguiente' or text()='Next']/ancestor::div[@role='button'][1]",
                        )
                    )
                )
                driver.execute_script("arguments[0].click();", next_btn)
                print(f"      Avanzando paso {step + 1} ('Siguiente')...")
                time.sleep(5)
                driver.save_screenshot(str(OUTPUT_DIR / f"fb_step2_next{step+1}.png"))
            except TimeoutException:
                print(f"      Nota: Botón 'Siguiente' ya no está presente en paso {step + 1}.")
                break

        _close_inner_popup_only(driver)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox' and (@contenteditable='true')]"))
            )
            boxes = [
                b
                for b in driver.find_elements(By.XPATH, "//div[@role='textbox' and (@contenteditable='true')]")
                if b.is_displayed()
            ]
            if boxes:
                caption_box = boxes[-1]
                driver.execute_script("arguments[0].click(); arguments[0].focus();", caption_box)
                safe_caption = "".join(c for c in caption if ord(c) <= 0xFFFF).strip()
                caption_box.send_keys(safe_caption)
                print(f"      Descripción agregada: '{safe_caption}'")
                time.sleep(2)
                driver.save_screenshot(str(OUTPUT_DIR / "fb_step3_caption.png"))
        except Exception as exc:
            print(f"      Aviso en caja de descripción: {exc}")

        print("[Subida] Haciendo clic en 'Publicar'...")
        publish_btn = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@role='button' and not(@aria-disabled='true')]//span[text()='Publicar' or text()='Compartir' or text()='Publish' or text()='Share']/ancestor::div[@role='button'][1]",
                )
            )
        )
        driver.execute_script("arguments[0].click();", publish_btn)

        print("      Esperando a que finalice el envío del video a Facebook (25s)...")
        time.sleep(25)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_status.png"))
        print("[Subida] ¡Video publicado exitosamente en Facebook!")

    finally:
        driver.quit()


def upload_feed_post_to_facebook(
    story_text: str,
    image_path: Path | None = None,
    headless: bool = False,
) -> None:
    """
    Publica una Historia de Texto o una Foto HD con Historia en el muro del perfil/página
    de Facebook para cumplir los requisitos de variedad de contenido del Panel para Creadores.
    """
    print("[Subida Muro] Iniciando navegador para publicar historia/foto en Facebook...")
    driver = _create_driver(headless=headless)

    try:
        _ensure_logged_in(driver)
        _switch_to_page_profile_if_needed(driver, FB_PAGE_NAME)

        driver.get("https://www.facebook.com/me")
        time.sleep(5)

        # Abrir el compositor haciendo clic en '¿Qué estás pensando?'
        composer_btn = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//span[contains(text(), '¿Qué estás pensando?') or contains(text(), 'What')]/ancestor::div[@role='button'][1]",
                )
            )
        )
        driver.execute_script("arguments[0].click();", composer_btn)
        time.sleep(3.5)

        # Seleccionar específicamente el diálogo 'Crear publicación'
        dialog = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='dialog' and (.//span[text()='Crear publicación'] or .//span[text()='Create post'])]")
            )
        )

        # Escribir la historia en la caja de texto visible dentro de 'Crear publicación'
        box = WebDriverWait(dialog, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//div[@role='textbox' and @contenteditable='true']"))
        )
        webdriver.ActionChains(driver).move_to_element(box).click().perform()
        time.sleep(0.5)
        safe_story = "".join(c for c in story_text if ord(c) <= 0xFFFF).strip()
        for paragraph in safe_story.split("\n"):
            box.send_keys(paragraph)
            box.send_keys(Keys.SHIFT, Keys.ENTER)
        print("      Historia redactada en el compositor.")
        time.sleep(1.5)

        # Si incluye imagen HD, adjuntarla al input[type='file'] dentro de 'Crear publicación'
        if image_path and image_path.exists():
            print(f"[Subida Muro] Adjuntando imagen HD al post: {image_path.resolve()}...")
            photo_btns = dialog.find_elements(
                By.XPATH,
                ".//div[@aria-label='Foto/video' or @aria-label='Photo/video'][@role='button']",
            )
            if photo_btns:
                driver.execute_script("arguments[0].click();", photo_btns[-1])
                time.sleep(2.5)

            dialog_file_inputs = dialog.find_elements(By.XPATH, ".//input[@type='file']")
            if dialog_file_inputs:
                dialog_file_inputs[0].send_keys(str(image_path.resolve()))
                time.sleep(6)

        driver.save_screenshot(str(OUTPUT_DIR / "fb_feed_post_preview.png"))

        # Si el diálogo muestra 'Siguiente' antes de 'Publicar', avanzar primero
        next_btns = dialog.find_elements(
            By.XPATH,
            ".//div[@role='button' and not(@aria-disabled='true')]//span[text()='Siguiente' or text()='Next']/ancestor::div[@role='button'][1]",
        )
        if next_btns:
            driver.execute_script("arguments[0].click();", next_btns[-1])
            print("      Avanzando paso 'Siguiente' en publicación...")
            time.sleep(4)

        # Hacer clic en 'Publicar' dentro del diálogo 'Crear publicación'
        publish_btn = WebDriverWait(dialog, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    ".//div[@role='button' and not(@aria-disabled='true')]//span[text()='Publicar' or text()='Post']/ancestor::div[@role='button'][1]",
                )
            )
        )
        driver.execute_script("arguments[0].click();", publish_btn)
        print("      Esperando confirmación de publicación en el muro (12s)...")
        time.sleep(12)
        driver.save_screenshot(str(OUTPUT_DIR / "fb_status.png"))
        print("[Subida Muro] ¡Publicación de historia/foto completada con éxito!")

    finally:
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 3: Subida automática de MP4 a Facebook con Selenium.")
    parser.add_argument(
        "--video",
        type=Path,
        default=OUTPUT_DIR / "video_final.mp4",
        help="Ruta del archivo MP4 final que se subirá.",
    )
    parser.add_argument(
        "--caption",
        type=str,
        default="3 misterios del universo que la ciencia aún no puede explicar. Síguenos en ERPA VARDE #reels #espacio #curiosidades #viral",
        help="Texto o descripción que acompañará al video en Facebook.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar el navegador en segundo plano.",
    )
    args = parser.parse_args()
    upload_video_to_facebook(video_path=args.video, caption=args.caption, headless=args.headless)
