"""Música, ambientes y efectos generados con numpy (100% originales, sin licencias)."""
import os
import zlib
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "audio")
os.makedirs(CACHE, exist_ok=True)

NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def hz(name, octave):
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


CHORDS = {
    "C": ["C", "E", "G"], "G": ["G", "B", "D"], "Am": ["A", "C", "E"], "F": ["F", "A", "C"],
    "D": ["D", "F#", "A"], "Em": ["E", "G", "B"], "Dm": ["D", "F", "A"], "Bb": ["A#", "D", "F"],
    "B": ["B", "D#", "F#"], "Cmaj7": ["C", "E", "G", "B"], "B7": ["B", "D#", "A"], "E": ["E", "G#", "B"],
    "A": ["A", "C#", "E"], "Gm": ["G", "A#", "D"], "Fmaj7": ["F", "A", "C", "E"], "Am7": ["A", "C", "E", "G"],
}


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    na, nr = min(na, n // 2), min(nr, n // 2)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def pad(freqs, dur, vol=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.6, 0.6):
            ph = np.random.rand() * 6.28
            out += np.sin(2 * np.pi * (f + det) * t + ph) + 0.3 * np.sin(4 * np.pi * (f + det) * t + ph)
    out *= env(n, dur * 0.35, dur * 0.35) * vol / len(freqs)
    return out


def pluck(f, dur, vol=0.3, bright=0.5):
    n = int(dur * SR)
    p = max(2, int(SR / f))
    buf = (np.random.rand(p) * 2 - 1)
    out = np.zeros(n)
    decay = 0.996 - (1 - bright) * 0.006
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * vol


def pluck_fast(f, dur, vol=0.3, bright=0.5):
    # aproximación vectorizada (seno amortiguado con armónicos) — mucho más rápida
    n = int(dur * SR)
    t = np.arange(n) / SR
    d = 3.0 + (1 - bright) * 4
    s = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.5 * bright + 0.2), (3, 0.25 * bright), (4, 0.12 * bright)):
        s += a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * d * k * 0.8)
    s *= env(n, 0.004, 0.05)
    return s * vol


def bell(f, dur, vol=0.18):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)
         + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6))
    return s * np.exp(-t * 1.6) * vol * env(n, 0.003, 0.1)


def bass(f, dur, vol=0.22):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return s * vol * env(n, 0.02, min(0.3, dur * 0.4))


def kick(vol=0.5):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    f = 110 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * vol


def shaker(vol=0.08):
    n = int(0.08 * SR)
    s = np.random.randn(n)
    s = signal.lfilter(*signal.butter(2, 6000 / (SR / 2), "high"), s)
    return s * np.exp(-np.arange(n) / SR * 50) * vol


def place(buf, clip, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i]


MOODS = {
    # nombre: (progresión, tempo, octava arpegio, estilo)
    "tema": (["F", "C", "Dm", "Bb"], 104, 4, "alegre"),
    "calma": (["C", "G", "Am", "F"], 84, 4, "suave"),
    "alegre": (["G", "D", "Em", "C"], 112, 4, "alegre"),
    "triste": (["Am", "F", "C", "G"], 64, 4, "triste"),
    "tension": (["Dm", "Dm", "Bb", "A"], 96, 3, "tension"),
    "misterio": (["Em", "Cmaj7", "Am7", "B7"], 72, 5, "misterio"),
    "esperanza": (["F", "C", "Dm", "Bb"], 78, 4, "suave"),
    "accion": (["Em", "C", "D", "B"], 138, 3, "accion"),
    "romance": (["Fmaj7", "Em", "Dm", "C"], 70, 4, "suave"),
}


def music_loop(mood):
    path = os.path.join(CACHE, f"music_{mood}.npy")
    if os.path.exists(path):
        return np.load(path)
    rng_state = np.random.get_state()
    np.random.seed(zlib.crc32(mood.encode()))
    prog, tempo, oc, style = MOODS[mood]
    beat = 60 / tempo
    bar = beat * 4
    total = bar * len(prog) * 2
    buf = np.zeros(int(total * SR) + SR)
    for rep in range(2):
        for ci, ch in enumerate(prog):
            t0 = (rep * len(prog) + ci) * bar
            notes = CHORDS[ch]
            freqs = [hz(n, oc) for n in notes]
            place(buf, pad([f / 2 for f in freqs], bar * 1.15, 0.10 if style != "tension" else 0.13), t0)
            root = hz(notes[0], 2)
            if style in ("alegre", "suave", "triste", "romance"):
                pattern = [0, 1, 2, 1, 0, 2, 1, 2] if style != "triste" else [0, 2, 1, 2]
                step = bar / len(pattern)
                for k, idx in enumerate(pattern):
                    f = freqs[idx % len(freqs)] * (2 if (k == 4 and style == "alegre") else 1)
                    place(buf, pluck_fast(f, step * 2.5, 0.16 if style != "triste" else 0.2,
                                          0.7 if style == "alegre" else 0.4), t0 + k * step)
                place(buf, bass(root, bar * 0.9, 0.18), t0)
                if style == "alegre":
                    for b in range(8):
                        place(buf, shaker(0.05), t0 + b * beat / 2)
                    place(buf, kick(0.25), t0)
                    place(buf, kick(0.2), t0 + 2 * beat)
            elif style == "tension":
                for b in range(8):
                    place(buf, bass(root, beat * 0.45, 0.22), t0 + b * beat / 2)
                place(buf, bell(hz("A#", 5), bar, 0.05), t0)
                place(buf, bell(hz("A", 5), bar, 0.05), t0 + beat * 2)
                place(buf, kick(0.3), t0)
                place(buf, kick(0.25), t0 + beat * 2.5)
            elif style == "misterio":
                for k in range(3):
                    f = freqs[np.random.randint(len(freqs))] * (2 if np.random.rand() < 0.4 else 1)
                    place(buf, bell(f, bar, 0.12), t0 + k * bar / 3 + np.random.rand() * 0.2)
                place(buf, bass(root, bar, 0.12), t0)
            elif style == "accion":
                for b in range(8):
                    place(buf, bass(root, beat * 0.4, 0.24), t0 + b * beat / 2)
                    place(buf, shaker(0.07), t0 + b * beat / 2 + beat / 4)
                for b in range(4):
                    place(buf, kick(0.45), t0 + b * beat)
                for k, idx in enumerate([0, 1, 2, 1]):
                    place(buf, pluck_fast(freqs[idx] * 2, beat, 0.12, 0.8), t0 + k * beat)
    buf = buf[: int(total * SR)]
    # reverb sencilla (eco múltiple)
    rev = buf.copy()
    for d, g in ((0.031, 0.35), (0.047, 0.3), (0.089, 0.22), (0.137, 0.16), (0.21, 0.1)):
        k = int(d * SR)
        rev[k:] += buf[:-k] * g
    rev /= max(1e-6, np.abs(rev).max())
    np.random.set_state(rng_state)
    np.save(path, rev.astype(np.float32))
    return rev


def noise(n, color="white"):
    w = np.random.randn(n)
    if color == "brown":
        b = np.cumsum(w)
        b = signal.lfilter([1, -1], [1, -0.995], b)
        return b / (np.abs(b).max() + 1e-9)
    if color == "pink":
        b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
        p = signal.lfilter(b, a, w)
        return p / (np.abs(p).max() + 1e-9)
    return w / np.abs(w).max()


def lowpass(x, f):
    return signal.lfilter(*signal.butter(2, f / (SR / 2)), x)


def bandpass(x, lo, hi):
    return signal.lfilter(*signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"), x)


def ambience(name, dur=30.0):
    path = os.path.join(CACHE, f"amb_{name}.npy")
    if os.path.exists(path):
        return np.load(path)
    np.random.seed(zlib.crc32(name.encode()))
    n = int(dur * SR)
    t = np.arange(n) / SR
    if name == "olas":
        base = lowpass(noise(n, "pink"), 900)
        swell = (0.55 + 0.45 * np.sin(2 * np.pi * t / 7.5) ** 2) * (0.7 + 0.3 * np.sin(2 * np.pi * t / 3.1))
        hiss = bandpass(noise(n), 2000, 7000) * np.clip(np.sin(2 * np.pi * t / 7.5 - 0.6), 0, 1) ** 3 * 0.5
        s = base * swell + hiss
    elif name == "lluvia":
        s = bandpass(noise(n), 400, 9000) * 0.6 + lowpass(noise(n, "brown"), 300) * 0.6
        for _ in range(int(dur * 25)):
            place(s, bell(3000 + np.random.rand() * 3000, 0.03, 0.15), np.random.rand() * dur)
    elif name == "viento":
        s = bandpass(noise(n), 200, 1200) * (0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 5.3)) ** 2)
    elif name == "selva":
        s = lowpass(noise(n, "pink"), 600) * 0.25
        for _ in range(int(dur * 1.5)):
            st = np.random.rand() * dur
            f0 = 2200 + np.random.rand() * 2500
            ln = 0.06 + np.random.rand() * 0.1
            m = int(ln * SR)
            tt = np.arange(m) / SR
            ch = np.sin(2 * np.pi * np.cumsum(f0 + 1500 * np.sin(tt * 40)) / SR) * env(m, 0.01, 0.03) * 0.25
            for r in range(np.random.randint(1, 4)):
                place(s, ch, st + r * (ln + 0.04))
        ins = np.sin(2 * np.pi * 5200 * t) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * t))) * 0.03
        s = s + ins * (0.5 + 0.5 * np.sin(2 * np.pi * t / 9))
    elif name == "noche":
        s = lowpass(noise(n, "pink"), 500) * 0.2
        chirp = np.sin(2 * np.pi * 4400 * t) * (np.sin(2 * np.pi * 30 * t) > 0.3)
        gate = (np.sin(2 * np.pi * 1.1 * t) > 0.2).astype(float)
        s = s + chirp * gate * 0.06
    elif name == "fuego":
        s = lowpass(noise(n, "brown"), 250) * 0.5
        for _ in range(int(dur * 18)):
            m = int(0.004 * SR)
            c = np.random.randn(m) * np.exp(-np.arange(m) / m * 5) * (0.3 + np.random.rand() * 0.7)
            place(s, bandpass(np.pad(c, (0, 200)), 1500, 8000), np.random.rand() * dur)
    elif name == "cueva":
        s = lowpass(noise(n, "brown"), 150) * 0.5
        for _ in range(int(dur * 0.8)):
            st = np.random.rand() * dur
            m = int(0.25 * SR)
            tt = np.arange(m) / SR
            d = np.sin(2 * np.pi * np.cumsum(1400 - 600 * tt * 4) / SR) * np.exp(-tt * 20) * 0.3
            place(s, d, st)
            place(s, d * 0.3, st + 0.18)
    elif name == "barco":
        s = lowpass(noise(n, "pink"), 700) * 0.6 + np.sin(2 * np.pi * 52 * t) * 0.08
    else:
        s = np.zeros(n)
    # fundido para bucle sin cortes
    f = int(0.5 * SR)
    s[:f] = s[:f] * np.linspace(0, 1, f) + s[-f:] * np.linspace(1, 0, f)
    s = s[: n - f]
    s = s / (np.abs(s).max() + 1e-9)
    np.save(path, s.astype(np.float32))
    return s


def sfx(name):
    path = os.path.join(CACHE, f"sfx_{name}.npy")
    if os.path.exists(path):
        return np.load(path)
    np.random.seed(zlib.crc32(name.encode()))
    if name == "trueno":
        n = int(3.5 * SR)
        t = np.arange(n) / SR
        s = lowpass(noise(n, "brown"), 400) * np.exp(-t * 1.1) * (1 + 2 * np.exp(-t * 12))
        s += bandpass(noise(n), 300, 3000) * np.exp(-t * 9) * 0.6
    elif name == "golpe":
        s = kick(1.0)
        s[: 2000] += np.random.randn(2000) * np.exp(-np.arange(2000) / 300) * 0.5
    elif name == "chapuzon":
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        s = bandpass(noise(n), 300, 5000) * np.exp(-t * 4) * (1 - np.exp(-t * 60))
    elif name == "brillo":
        s = np.zeros(int(2.2 * SR))
        for k, f in enumerate([hz("E", 6), hz("G#", 6), hz("B", 6), hz("E", 7), hz("D#", 7)]):
            place(s, bell(f, 1.6, 0.3), k * 0.09)
    elif name == "sting":
        s = np.zeros(int(3.0 * SR))
        for f in (hz("D", 3), hz("F", 3), hz("G#", 3), hz("D", 4)):
            place(s, pad([f], 3.0, 0.5) * np.exp(-np.arange(int(3.0 * SR)) / SR * 0.8), 0)
        place(s, kick(0.8), 0)
    elif name == "revelacion":
        s = np.zeros(int(3.0 * SR))
        for k, f in enumerate([hz("A", 4), hz("C", 5), hz("E", 5), hz("A", 5)]):
            place(s, bell(f, 2.5, 0.25), k * 0.12)
        place(s, pad([hz("A", 3), hz("E", 4)], 3.0, 0.4), 0)
    elif name == "bocina":
        n = int(2.8 * SR)
        t = np.arange(n) / SR
        s = signal.sawtooth(2 * np.pi * 98 * t) * 0.5 + signal.sawtooth(2 * np.pi * 123.5 * t) * 0.4
        s = lowpass(s, 900) * env(n, 0.15, 0.6)
    elif name == "latido":
        s = np.zeros(int(1.0 * SR))
        place(s, kick(0.9), 0)
        place(s, kick(0.6), 0.22)
    elif name == "pasos":
        s = np.zeros(int(1.6 * SR))
        for k in range(4):
            c = lowpass(noise(int(0.08 * SR)), 1200) * np.exp(-np.arange(int(0.08 * SR)) / SR * 40)
            place(s, c * 0.8, k * 0.38)
    elif name == "rama":
        n = int(0.4 * SR)
        s = bandpass(noise(n), 800, 6000) * np.exp(-np.arange(n) / SR * 18)
    elif name == "fuego_on":
        n = int(2.0 * SR)
        t = np.arange(n) / SR
        s = lowpass(noise(n, "pink"), 1500) * (1 - np.exp(-t * 3)) * np.exp(-t * 0.8)
    elif name == "comico":
        s = np.zeros(int(0.8 * SR))
        for k, f in enumerate([hz("C", 5), hz("G", 4), hz("C", 4)]):
            place(s, pluck_fast(f, 0.4, 0.4, 0.8), k * 0.15)
    elif name == "alegria":
        s = np.zeros(int(1.8 * SR))
        for k, f in enumerate([hz("C", 5), hz("E", 5), hz("G", 5), hz("C", 6)]):
            place(s, pluck_fast(f, 1.0, 0.35, 0.9), k * 0.1)
    elif name == "caida":
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t * 2.5) + 80) / SR) * 0.4 * env(n, 0.01, 0.2)
        place(s, kick(0.9), 0.95)
    else:
        s = np.zeros(SR // 4)
    s = s / (np.abs(s).max() + 1e-9)
    np.save(path, s.astype(np.float32))
    return s


def save_wav(path, x):
    x = np.tanh(x * 1.1) * 0.95
    wavfile.write(path, SR, (x * 32767).astype(np.int16))
