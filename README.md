# Automatización de Videos para Facebook (Gemini + Edge-TTS + MoviePy + Whisper + FFmpeg + Selenium)

Este proyecto implementa de forma modular el flujo completo para crear videos verticales (9:16) con inteligencia artificial y publicarlos automáticamente en tu página de Facebook (**ERPA VARDE**).

## Estructura del Proyecto

- `config.py`: Configuración central de rutas, resolución (1080x1920) y variables de entorno.
- `generator.py` (**Módulo 1**): Consume la API de Gemini (`gemini-3.8-flash`) para redactar el guion, lo convierte en voz natural con `edge-tts` y ensambla el video `.mp4` con las imágenes de `assets/images/` usando `MoviePy`.
- `subtitles.py` (**Módulo 2**): Transcribe el audio con `OpenAI Whisper` (con marcas de tiempo por palabra para crear bloques cortos tipo Reels) y quema los subtítulos dinámicamente con `FFmpeg`.
- `uploader.py` (**Módulo 3**): Automatiza Chrome con `Selenium` usando un perfil persistente (`browser_profile/`) para iniciar sesión en tu cuenta (`Voircréerpartager` / `ERPA VARDE`) y subir el `.mp4` final a Facebook Reels.
- `main.py` (**Orquestador**): Ejecuta los 3 módulos en secuencia con un solo comando.

---

## 1. Instalación

Abre una terminal en esta carpeta y crea/instala las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Nota sobre FFmpeg:** El módulo `subtitles.py` detecta automáticamente el binario de FFmpeg incluido en `imageio-ffmpeg` (instalado con `MoviePy`) si no tienes `ffmpeg` en el `PATH` de Windows. Si deseas usar filtros de subtítulos avanzados (`libass`), se recomienda instalar la versión completa de FFmpeg en Windows ejecutando:
> ```powershell
> winget install Gyan.FFmpeg
> ```

---

## 2. Configuración (`.env`)

Edita el archivo `.env` y coloca tu clave gratuita de Gemini API (puedes obtenerla en [Google AI Studio](https://aistudio.google.com/apikey)):

```env
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
TTS_VOICE=es-MX-JorgeNeural
WHISPER_MODEL=base
FB_EMAIL=Voircréerpartager
FB_PASSWORD=lol1321
FB_PAGE_NAME=ERPA VARDE
```

Coloca las imágenes que quieras usar para tu video dentro de la carpeta `assets/images/` (formatos `.jpg`, `.png`, `.webp`). Si la dejas vacía, el script creará 3 imágenes de prueba automáticamente para que puedas probar todo el flujo.

---

## 3. Cómo Depurar Cada Módulo por Separado

Tal como se diseñó en tu arquitectura, puedes probar cada etapa individualmente antes de ejecutar el flujo completo:

### Paso 1: Generar guion, voz y video base
```powershell
python generator.py --topic "3 misterios sin resolver de la historia"
```
Generará `output/guion.txt`, `output/narration.mp3` y `output/video_base.mp4`.

### Paso 2: Transcribir con Whisper y quemar subtítulos con FFmpeg
```powershell
python subtitles.py --video output/video_base.mp4
```
Generará `output/subtitles.srt` y `output/video_final.mp4`.

### Paso 3: Subir el MP4 final a Facebook
```powershell
python uploader.py --video output/video_final.mp4 --caption "¡Increíble dato! Síguenos en ERPA VARDE #reels #curiosidades"
```
La primera vez que se abra Chrome, iniciará sesión y guardará las cookies en `browser_profile/` para no pedirte confirmación en futuras subidas.

---

## 4. Ejecutar Todo el Flujo Automatizado

Para generar, subtitular y publicar en un solo comando:

```powershell
python main.py --topic "5 datos curiosos del cerebro humano" --caption "¿Ya los conocías? #reels #viral"
```

Si quieres generar el video completo con subtítulos pero **revisarlo antes de subirlo a Facebook**, agrega `--skip-upload`:

```powershell
python main.py --topic "5 datos curiosos del cerebro humano" --skip-upload
```
