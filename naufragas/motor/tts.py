"""Voces gratuitas y offline: espeak-ng + MBROLA (es3, voz femenina española).

Cada personaje tiene su propio tono, velocidad y timbre (desplazamiento de tono por remuestreo).
Las emociones modifican tono y velocidad.
"""
import hashlib
import os
import re
import subprocess
import tempfile

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache", "voces")
os.makedirs(CACHE, exist_ok=True)

# voz espeak, velocidad (ppm), tono (0-99), factor de timbre, volumen
VOCES = {
    "yei": dict(voz="mb-es3", vel=165, tono=60, f0=265, rango=1.35, timbre=1.06, vol=1.0),
    "kitzuki": dict(voz="mb-es3", vel=148, tono=50, f0=200, rango=0.9, timbre=1.0, vol=1.0),
    "kirane": dict(voz="mb-es3", vel=172, tono=50, f0=225, rango=1.15, timbre=0.97, vol=1.0),
    "abuela": dict(voz="mb-es3", vel=128, tono=45, f0=175, rango=0.8, timbre=0.96, vol=1.0),
    "marinero": dict(voz="mb-es1", vel=160, tono=40, timbre=1.0, vol=1.0),
    "teo": dict(voz="mb-es3", vel=178, tono=60, f0=300, rango=1.4, timbre=1.12, vol=1.0),
    "jefa": dict(voz="mb-es3", vel=160, tono=50, f0=185, rango=1.0, timbre=0.95, vol=1.0),
    "periodista": dict(voz="mb-es3", vel=170, tono=50, f0=210, rango=1.2, timbre=1.0, vol=1.0),
    "profesor": dict(voz="mb-es2", vel=140, tono=35, timbre=1.0, vol=1.0),
    "vecino": dict(voz="mb-es1", vel=150, tono=45, timbre=1.0, vol=1.0),
    "cliente": dict(voz="mb-es1", vel=165, tono=50, timbre=1.03, vol=1.0),
    "instructor": dict(voz="mb-es2", vel=165, tono=45, timbre=1.0, vol=1.0),
    "chucho": dict(voz="mb-es1", vel=190, tono=62, timbre=1.07, vol=1.0),
    "lupita": dict(voz="mb-es3", vel=185, tono=60, f0=250, rango=1.7, timbre=1.04, vol=1.0),
    "patino": dict(voz="mb-es2", vel=135, tono=30, timbre=1.0, vol=1.0),
    "rigoberto": dict(voz="mb-mx1", vel=150, tono=40, timbre=1.0, vol=1.0),
    "cleta": dict(voz="mb-es3", vel=125, tono=45, f0=165, rango=0.9, timbre=0.94, vol=1.0),
    "brayan": dict(voz="mb-mx2", vel=195, tono=65, timbre=1.0, vol=1.0),
    "locutor": dict(voz="mb-es1", vel=150, tono=25, timbre=0.95, vol=1.0),
    "narrador": dict(voz="mb-es2", vel=140, tono=38, timbre=1.0, vol=0.95),
    "otro": dict(voz="mb-es1", vel=155, tono=45, timbre=1.0, vol=1.0),
}

EMOCION = {
    "feliz": (6, 6), "risa": (10, 10), "picara": (4, 0), "sorpresa": (16, 10), "miedo": (14, 16),
    "enojada": (6, 22), "molesta": (0, 10), "triste": (-12, -22), "cansada": (-10, -28),
    "timida": (-2, -14), "avergonzada": (0, -10), "nerviosa": (8, 18), "preocupada": (-4, -8),
    "seria": (-6, -6), "pensativa": (-4, -16), "sonrojada": (4, -6), "lentes": (-4, -4),
}


def limpiar(texto, voz):
    t = texto.replace("…", ",").replace("...", ",").replace("—", ",").replace("–", ",")
    t = re.sub(r"[*_\"“”«»()]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


# ---------------------------------------------------------------- MBROLA es3 directo
ES3 = "/usr/share/mbrola/es3/es3"
INV = set("_ a e i o u j p b t d k g f s z m n l r R".split())
MAPA = {"B": "b", "D": "d", "G": "g", "T": "s", "x": "k", "X": "k", "h": "k", "H": "k", "L": "j",
        "J": "n j", "J^": "n j", "N": "n", "tS": "t s", "R2": "R", "rr": "R", "T": "R", "w": "u", "aI": "a i",
        "eI": "e i", "oI": "o i", "aU": "a u", "eU": "e u", "I": "i", "U": "u", ";": "j", "Z": "j",
        "jj": "j", "y": "j", "S": "s", "j\\": "j", "r2": "R", "ts": "t s"}
_faltan = None


def faltantes():
    global _faltan
    if _faltan is not None:
        return _faltan
    import json
    import itertools
    path = os.path.join(CACHE, "es3_faltantes.json")
    if os.path.exists(path):
        _faltan = set(json.load(open(path)))
        return _faltan
    miss = []
    inv = sorted(INV)
    with tempfile.TemporaryDirectory() as td:
        pho, wav = os.path.join(td, "p.pho"), os.path.join(td, "p.wav")
        for a, b in itertools.product(inv, inv):
            if a == b == "_":
                continue
            body = f"{a} 80\n{b} 80\n" if "_" in (a, b) else f"_ 50\n{a} 80\n{b} 80\n_ 50\n"
            open(pho, "w").write(body)
            r = subprocess.run(["mbrola", ES3, pho, wav], capture_output=True, text=True)
            if r.returncode != 0 and f"{a}-{b}" in (r.stderr + r.stdout):
                miss.append(f"{a}-{b}")
    json.dump(miss, open(path, "w"))
    _faltan = set(miss)
    return _faltan


def a_fonemas(texto):
    """Texto -> fonemas de espeak (es-419) con la rr marcada como T, conservando la puntuación."""
    texto = texto.replace("¿", " ").replace("¡", " ")
    trozos = re.findall(r"([^,.;:!?]+)([,.;:!?]*)", texto)
    out = []
    for frase, punt in trozos:
        if not re.search(r"\w", frase):
            out.append(punt)
            continue
        r = subprocess.run(["espeak-ng", "-v", "es-419", "-q", "-x", frase], capture_output=True, text=True)
        ph = " ".join(r.stdout.split()).replace("R2", "T").replace("dZ", "J^")
        out.append(f"[[{ph}]]{punt} ")
    return "".join(out)


def pho_es3(pho_txt, f0=220, rango=1.0):
    seq = []
    vals = []
    for line in pho_txt.splitlines():
        parts = line.split()
        vals += [float(v) for v in parts[3::2]]
    med = float(np.median(vals)) if vals else 100.0
    for line in pho_txt.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        ph, dur, pts = parts[0].replace("/", ""), int(parts[1]), parts[2:]
        pts = [pts[i] if i % 2 == 0 else str(int(f0 * (float(pts[i]) / med) ** rango)) for i in range(len(pts))]
        rep = MAPA.get(ph, ph).split()
        rep = [r for r in rep if r in INV]
        if not rep:
            continue
        if len(rep) == 1:
            seq.append([rep[0], dur, pts])
        else:
            d1 = int(dur * 0.6)
            seq.append([rep[0], d1, pts])
            last = pts[-2:] if len(pts) >= 2 else []
            seq.append([rep[1], max(20, dur - d1), (["50"] + last[1:]) if last else []])
    falt = faltantes()
    out = []
    for item in seq:
        if out:
            prev = out[-1]
            if prev[0] == item[0]:
                prev[1] += item[1]
                continue
            pair = f"{prev[0]}-{item[0]}"
            if pair in falt:
                if item[0] == "j" and f"{prev[0]}-i" not in falt:
                    item[0] = "i"
                elif prev[0] == "j" and f"i-{item[0]}" not in falt:
                    prev[0] = "i"
                elif item[0] == "r" and f"{prev[0]}-R" not in falt:
                    item[0] = "R"
                elif f"{prev[0]}-_" not in falt and f"_-{item[0]}" not in falt:
                    out.append(["_", 12, []])
        out.append(item)
    if out and out[0][0] == "r":
        out[0][0] = "R"
    return "\n".join(f"{p} {d} {' '.join(pts)}".strip() for p, d, pts in out) + "\n"


def sintetizar(quien, texto, emocion=None):
    cfg = VOCES.get(quien, VOCES["otro"])
    dt, dv = EMOCION.get(emocion or "", (0, 0))
    tono = int(np.clip(cfg["tono"] + dt, 0, 99))
    vel = int(cfg["vel"] + dv)
    timbre = cfg["timbre"]
    limpio = limpiar(texto, cfg["voz"])
    if not re.search(r"\w", limpio):
        return np.zeros(int(SR * 1.0), dtype=np.float32)
    key = hashlib.md5(f"v3|{quien}|{emocion}|{limpio}|{tono}|{vel}|{timbre}|{cfg}".encode()).hexdigest()
    path = os.path.join(CACHE, key + ".npy")
    if os.path.exists(path):
        return np.load(path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    # se sintetiza más lento y luego se acelera por remuestreo => sube el timbre sin alargar
    if cfg["voz"] == "mb-es3":
        r = subprocess.run(["espeak-ng", "-v", "mb-es2", "-q", "--pho", "-s", str(int(vel / timbre)), "-p", str(tono),
                            a_fonemas(limpio)], check=True, capture_output=True, text=True)
        f0 = cfg["f0"] * (1 + dt / 100.0)
        with tempfile.NamedTemporaryFile("w", suffix=".pho", delete=False) as f:
            f.write(pho_es3(r.stdout, f0, cfg["rango"]))
            pho = f.name
        subprocess.run(["mbrola", "-e", ES3, pho, tmp], check=True, capture_output=True)
        os.unlink(pho)
    else:
        entrada = a_fonemas(limpio).replace("T", "r") if cfg["voz"].startswith("mb-") else limpio
        subprocess.run(["espeak-ng", "-v", cfg["voz"], "-s", str(int(vel / timbre)), "-p", str(tono),
                        "-w", tmp, entrada], check=True, capture_output=True)
    sr, x = wavfile.read(tmp)
    os.unlink(tmp)
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x /= (np.abs(x).max() + 1e-9)
    n_out = int(len(x) * SR / sr / timbre)
    y = signal.resample(x, n_out)
    # suavizar agudos metálicos y dar cuerpo
    y = signal.lfilter(*signal.butter(2, 7000 / (SR / 2)), y)
    y = signal.lfilter(*signal.butter(1, 90 / (SR / 2), "high"), y)
    # recorte de silencios
    thr = 0.02
    idx = np.where(np.abs(y) > thr)[0]
    if len(idx):
        y = y[max(0, idx[0] - 400): idx[-1] + 2000]
    y = y / (np.abs(y).max() + 1e-9) * 0.9 * cfg["vol"]
    np.save(path, y.astype(np.float32))
    return y
