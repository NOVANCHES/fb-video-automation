#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# INSTALADOR AUTOMÁTICO PARA XIAOMI REDMI NOTE 10S (TERMUX ANDROID)
# Ejecuta la generación diaria de videos animados sin necesitar la computadora
# =============================================================================

set -e

echo "============================================================"
echo " Configurando Automatización de Videos en Xiaomi Redmi Note 10S"
echo "============================================================"

pkg update -y && pkg upgrade -y
pkg install -y python ffmpeg cronie termux-services git libjpeg-turbo zlib freetype

# Evitar que MIUI / HyperOS del Xiaomi duerma el proceso en segundo plano
termux-wake-lock

pip install --upgrade pip
pip install google-genai edge-tts moviepy Pillow python-dotenv requests g4f

# Programar ejecución diaria a las 7:00 PM (19:00 hrs) en el cron del teléfono
CRON_JOB="0 19 * * * cd \$HOME/fb-video-automation && python main.py --topic auto --format auto >> \$HOME/fb-video-automation/cron.log 2>&1"
(crontab -l 2>/dev/null | grep -v "fb-video-automation"; echo "$CRON_JOB") | crontab -

sv-enable crond
crond

echo "============================================================"
echo " ¡LISTO! Tu Xiaomi Redmi Note 10S ya tiene el cron activo"
echo " para generar y publicar contenido todos los días a las 7 PM."
echo "============================================================"
