"""
Generador de Efectos de Sonido (SFX) Cinéticos y Procedurales de Alta Calidad:
  - whoosh: Transición de cámara / zoom punch (frecuencia modulada de 80Hz a 450Hz).
  - pop: Impacto de subtítulo cinético (burst percusivo de 950Hz amortiguado en 35ms).
  - ding: Campanilla cristalina de revelación o punchline (armónicos 2200Hz y 4400Hz).
"""

import math
import wave
from pathlib import Path
import numpy as np

from config import BASE_DIR

SFX_DIR = BASE_DIR / "assets" / "sfx"
SFX_DIR.mkdir(parents=True, exist_ok=True)


def generate_sfx_library() -> None:
    sr = 44100

    # 1. POP SFX (para entrada de palabras clave)
    dur_pop = 0.045
    t_pop = np.linspace(0, dur_pop, int(sr * dur_pop), endpoint=False)
    # Burst percusivo con caída exponencial rápida
    pop_wave = np.sin(2 * np.pi * 920.0 * t_pop) * np.exp(-120.0 * t_pop)
    pop_wave = (pop_wave * 0.45 * 32767).astype(np.int16)
    with wave.open(str(SFX_DIR / "pop.wav"), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pop_wave.tobytes())

    # 2. WHOOSH SFX (para transiciones de escena)
    dur_whoosh = 0.35
    t_whoosh = np.linspace(0, dur_whoosh, int(sr * dur_whoosh), endpoint=False)
    # Ruido modulado con envolvente Gaussiana
    noise = np.random.normal(0, 0.4, len(t_whoosh))
    env = np.exp(-((t_whoosh - dur_whoosh / 2) ** 2) / (2 * (0.07 ** 2)))
    # Barrido de frecuencia de aire
    sweep = np.sin(2 * np.pi * (100.0 + 350.0 * (t_whoosh / dur_whoosh)) * t_whoosh)
    whoosh_wave = (noise * 0.6 + sweep * 0.4) * env
    whoosh_wave = np.clip(whoosh_wave, -0.9, 0.9)
    whoosh_wave = (whoosh_wave * 0.35 * 32767).astype(np.int16)
    with wave.open(str(SFX_DIR / "whoosh.wav"), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(whoosh_wave.tobytes())

    # 3. DING / CHIME SFX (para momentos de dinero, éxito o remate)
    dur_ding = 0.65
    t_ding = np.linspace(0, dur_ding, int(sr * dur_ding), endpoint=False)
    chime = (
        0.55 * np.sin(2 * np.pi * 2150.0 * t_ding) * np.exp(-8.0 * t_ding)
        + 0.30 * np.sin(2 * np.pi * 4300.0 * t_ding) * np.exp(-12.0 * t_ding)
        + 0.15 * np.sin(2 * np.pi * 6450.0 * t_ding) * np.exp(-18.0 * t_ding)
    )
    chime = np.clip(chime, -0.9, 0.9)
    chime = (chime * 0.40 * 32767).astype(np.int16)
    with wave.open(str(SFX_DIR / "ding.wav"), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(chime.tobytes())

    print(f"[SFX] Librería procedural de efectos creada en {SFX_DIR}: pop.wav, whoosh.wav, ding.wav")


if __name__ == "__main__":
    generate_sfx_library()
