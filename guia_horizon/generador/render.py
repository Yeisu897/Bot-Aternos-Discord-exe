import sys, os, math, hashlib, subprocess, re, random
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = "/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad"
sys.path.insert(0, S + "/work")
from episodios import EPISODIOS
from tts import tts_text

W, H, FPS, SR = 1920, 1080, 25, 24000
TX = S + "/addon/Horizonbeta_RP/textures/"
FD = S + "/fonts/"
def font(name, w, size):
    return ImageFont.truetype(f"{FD}fontsource-{name}-5.0.0/package/files/{name}-latin-{w}-normal.woff2", size)
F_TITLE = font("fredoka", 600, 62)
F_BIG = font("fredoka", 700, 110)
F_MED = font("fredoka", 600, 54)
F_TAG = font("fredoka", 600, 30)
F_BUL = font("nunito", 700, 46)
F_SUB = font("nunito", 700, 38)

PINK = (255, 139, 224); GOLD = (255, 205, 90); WHITE = (255, 255, 255)
PX, PY, PW, PH = 590, 40, 1290, 790          # pizarra
SXY = (590, 852, 1290, 200)                   # subtítulos

# ───────────── utilidades ─────────────
def icon(name, size):
    im = Image.open(TX + "items/" + name + ".png").convert("RGBA")
    return im.resize((size, size), Image.NEAREST)

def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

def text_shadow(d, xy, txt, f, fill, sh=(20, 5, 40), off=3):
    d.text((xy[0] + off, xy[1] + off), txt, font=f, fill=sh)
    d.text(xy, txt, font=f, fill=fill)

def diamond(d, cx, cy, r, fill):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)

def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

# ───────────── fondos ─────────────
def make_bg(kind):
    if kind == "eclipse":
        base = cover(Image.open(TX + "ui/hm_pausa_fondo.png").convert("RGB"), W, H)
        tint = (90, 10, 20)
    elif kind == "espacio":
        base = cover(Image.open(TX + "ui/panorama_0.png").convert("RGB"), W, H)
        tint = (10, 10, 40)
    else:
        base = cover(Image.open(TX + "ui/hm_pausa_fondo.png").convert("RGB"), W, H)
        tint = (40, 15, 80)
    base = base.filter(ImageFilter.GaussianBlur(3))
    base = Image.blend(base, Image.new("RGB", (W, H), tint), 0.45).convert("RGBA")
    # viñeta
    vg = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(vg)
    for i in range(40):
        dv.rectangle((i * 6, i * 4, W - i * 6, H - i * 4), outline=int(150 * (1 - i / 40)), width=6)
    base.alpha_composite(Image.new("RGBA", (W, H), (5, 0, 15, 255)), (0, 0)) if False else None
    dark = Image.new("RGBA", (W, H), (5, 0, 15, 0)); dark.putalpha(vg.filter(ImageFilter.GaussianBlur(30)))
    base.alpha_composite(dark)
    return base

BGS = {}
def bg(kind):
    if kind not in BGS: BGS[kind] = make_bg(kind)
    return BGS[kind]

rng = random.Random(7)
STARS = [(rng.randrange(W), rng.randrange(H), rng.random() * 6.28, rng.uniform(1.5, 4), rng.uniform(0.6, 1.6)) for _ in range(70)]
def draw_stars(img, t):
    d = ImageDraw.Draw(img)
    for x, y, ph, r, sp in STARS:
        a = 0.5 + 0.5 * math.sin(t * sp * 2 + ph)
        if a < 0.35: continue
        rr = r * a
        c = (255, 230, 255, int(220 * a))
        d.line((x - rr * 2.2, y, x + rr * 2.2, y), fill=c, width=2)
        d.line((x, y - rr * 2.2, x, y + rr * 2.2), fill=c, width=2)

# ───────────── avatar ─────────────
AV_H = 1000
AV = []
for k in range(3):
    a = Image.open(f"{S}/assets/avatar_m{k}.png")
    s = AV_H / a.height
    AV.append(a.resize((int(a.width * s), AV_H), Image.LANCZOS))
AV_W = AV[0].width
GLOW = Image.new("RGBA", (500, 120), (0, 0, 0, 0))
ImageDraw.Draw(GLOW).ellipse((40, 30, 460, 100), fill=(255, 120, 230, 120))
GLOW = GLOW.filter(ImageFilter.GaussianBlur(18))

def draw_avatar(img, t, level, x0=60, y0=70, alpha=1.0):
    bob = math.sin(t * 2.0) * 7
    sway = math.sin(t * 1.3) * 4
    av = AV[level]
    img.alpha_composite(GLOW, (int(x0 + AV_W / 2 - 250 + sway), int(y0 + AV_H - 75)))
    if alpha < 1:
        av = av.copy(); av.putalpha(av.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(av, (int(x0 + sway), int(y0 + bob)))

# ───────────── Yei: poses y expresiones ─────────────
YD = S + "/yei/"
POSE_CFG = {  # nombre: (alto en pantalla, borde inferior, voltear)
    "explica": (880, H + 30, False), "aww": (980, H + 40, False), "si": (980, H + 40, False),
    "hmm": (980, H + 40, False), "mira": (980, H + 40, True), "sentada": (760, 1060, False), "chibi": (700, 1050, False)}
POSES = {}
for k, (h, bot, fl) in POSE_CFG.items():
    im = Image.open(YD + k + ".png").convert("RGBA")
    if fl: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2)); rgb.putalpha(im.getchannel("A"))
    POSES[k] = (rgb, bot)
AV_CX = 60 + AV_W // 2

EXPRS = {}
def badge(nm):
    if nm in EXPRS: return EXPRS[nm]
    f = Image.open(YD + "e_" + nm + ".png").convert("RGBA")
    bw = 200; f = f.resize((bw, int(bw * f.height / f.width)), Image.LANCZOS)
    bh = min(f.height, 230)
    im = Image.new("RGBA", (bw + 30, bh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    m = Image.new("L", (bw, bh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, bw - 1, bh - 1), 28, fill=255)
    im.paste(f.crop((0, 0, bw, bh)), (15, 10), m)
    d.rounded_rectangle((13, 8, bw + 16, bh + 11), 30, outline=PINK, width=5)
    d.polygon([(30, bh + 8), (14, bh + 36), (62, bh + 8)], fill=PINK)   # colita hacia Yei
    EXPRS[nm] = im
    return im

def pick(say, si, li, nlines, first_ep, last_ep, k):
    s = say.lower()
    has = lambda *w: any(x in s for x in w)
    pose = "base"
    if first_ep and li == 0: pose = "si"
    elif last_ep: pose = "aww"
    elif has("¡ojo", "cuidado", "importante", "recuerda", "un consejo", "pero cuidado"): pose = "mira"
    elif has("popo", "romántico", "no sirve para nada", "tung tung", "¡qué aventura"): pose = "chibi"
    elif has("receta", "se hace con", "se fabrica", "fabrica un", "se hacen con") : pose = "explica"
    elif "?" in s: pose = "hmm"
    elif li == 0 and si > 0: pose = "explica"
    elif k % 7 == 3: pose = "sentada"
    if has("¡hola", "¡nos vemos", "¡chao", "adiós", "preciosa", "divertid", "¡y hasta", "¡qué", "¡hasta"): ex = "feliz"
    elif has("mata", "mueres", "muere", "morir", "zombi", "peligro", "aplasta", "radiactiv", "explota", "te quema", "congelas"): ex = "asustada" if k % 2 else "miedosa"
    elif has("x5", "cinco veces", "enfurecen", "roban", "no puedes", "no se puede", "no existe", "te desordenan"): ex = "enojada"
    elif has("pierdes un", "pierdes 1", "se pudren", "podrid", "duele", "miedo"): ex = "triste"
    elif has("amor", "beso", "casar", "boda", "pareja", "corazones sobre", "love"): ex = "sonrojada" if k % 2 else "coqueta"
    elif has("¡hola", "¡nos vemos", "¡chao", "adiós", "preciosa", "divertid", "¡y hasta", "ricos", "¡qué"): ex = "feliz"
    elif has("infinito", "250 bloques", "1000", "espacio", "hasta 50", "lonsdale"): ex = "sorprendida"
    elif has("cansad", "sin dormir"): ex = "cansada"
    elif re.search(r"\d", s): ex = ["pensativa", "seria", "curiosa"][k % 3]
    else: ex = ["feliz", "curiosa", "burlona", "seria"][k % 4]
    return pose, ex

def ease_back(k):
    c = 1.7; k = k - 1
    return 1 + (c + 1) * k ** 3 + c * k ** 2

def draw_pose(img, t, name, level, alpha=1.0, dy=0):
    pim, bot = POSES[name]
    bob = math.sin(t * 2.0) * 6 - level * 3
    x = AV_CX - pim.width // 2 + int(math.sin(t * 1.3) * 4)
    if alpha < 1:
        pim = pim.copy(); pim.putalpha(pim.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(GLOW, (AV_CX - 250, 1005))
    img.alpha_composite(pim, (x, int(bot - pim.height + bob + dy)))

def draw_yei(img, t, level, lines_all):
    cur = None; prev = None
    for ln in lines_all:
        if ln["start"] <= t: prev, cur = cur, ln
    if cur is None:
        draw_avatar(img, t, level); return
    pose = cur["pose"]; pp = prev["pose"] if prev else "base"
    dt = t - cur["start"]
    def one(p, alpha, dy):
        if p == "base": draw_avatar(img, t, level, y0=70 + dy, alpha=alpha)
        else: draw_pose(img, t, p, level, alpha, dy)
    if pose != pp and dt < 0.35:
        k = dt / 0.35
        one(pp, 1 - k, 0); one(pose, k, int(30 * (1 - k)))
    else:
        one(pose, 1.0, 0)
    if pose == "base":
        same = prev is not None and prev["pose"] == "base" and prev["ex"] == cur["ex"]
        b = badge(cur["ex"])
        k = 1.0 if same else min(1, dt / 0.35)
        sc = max(0.05, ease_back(k)) if k < 1 else 1.0
        bb = b if sc == 1.0 else b.resize((max(1, int(b.width * sc)), max(1, int(b.height * sc))), Image.LANCZOS)
        bx, by = 352, 30 + int(math.sin(t * 2.4) * 4)
        img.alpha_composite(bb, (bx + (b.width - bb.width) // 2, by + (b.height - bb.height)))

NAMEPLATE = Image.new("RGBA", (230, 64), (0, 0, 0, 0))
_d = ImageDraw.Draw(NAMEPLATE)
_d.rounded_rectangle((0, 0, 229, 63), 32, fill=(30, 12, 60, 230), outline=PINK, width=4)
diamond(_d, 38, 32, 9, GOLD); diamond(_d, 192, 32, 9, GOLD)
_d.text((115 - F_MED.getlength("Yei") / 2, 0), "Yei", font=F_MED, fill=PINK)

# ───────────── pizarra ─────────────
def panel_base(scene, ep):
    p = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    d.rounded_rectangle((0, 0, PW - 1, PH - 1), 38, fill=(22, 10, 48, 215), outline=PINK, width=5)
    d.rounded_rectangle((10, 10, PW - 11, PH - 11), 30, outline=(255, 205, 90, 120), width=2)
    ic = icon(scene["icon"], 96)
    p.alpha_composite(ic, (40, 30))
    text_shadow(d, (160, 40), scene["t"], F_TITLE, PINK)
    tag = f"EPISODIO {ep['n']}"
    tw = F_TAG.getlength(tag)
    d.rounded_rectangle((PW - tw - 80, 44, PW - 40, 92), 24, fill=(255, 139, 224, 60), outline=PINK, width=2)
    d.text((PW - tw - 60, 50), tag, font=F_TAG, fill=WHITE)
    # separador ▬▬◆▬▬
    y = 150
    d.line((40, y, PW / 2 - 24, y), fill=(160, 80, 200), width=4)
    d.line((PW / 2 + 24, y, PW - 40, y), fill=(160, 80, 200), width=4)
    diamond(d, PW // 2, y, 12, WHITE)
    return p

BUL_X, BUL_W, BUL_Y0, BUL_YMAX = 60, PW - 130, 180, PH - 30
def bullet_img(text, icons):
    lines = wrap(text, F_BUL, BUL_W)
    ih = 72 if icons else 0
    h = len(lines) * 58 + (ih + 8 if icons else 0) + 22
    im = Image.new("RGBA", (PW - 80, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    diamond(d, 16, 31, 12, PINK)
    for i, ln in enumerate(lines):
        text_shadow(d, (44, i * 58 + 2), ln, F_BUL, WHITE, off=2)
    if icons:
        x, y = 44, len(lines) * 58 + 8
        for nm in icons[:8]:
            d.rounded_rectangle((x - 4, y - 4, x + 68, y + 68), 12, fill=(255, 255, 255, 30), outline=(255, 205, 90, 160), width=2)
            im.alpha_composite(icon(nm, 64), (x, y)); x += 86
    return im

# ───────────── subtítulos ─────────────
def sub_chunks(text):
    parts = re.split(r"(?<=[\.\!\?\:;])\s+", text)
    out = []
    for p in parts:
        if F_SUB.getlength(p) > 1180 * 2:
            sub = re.split(r"(?<=,)\s+", p); cur = ""
            for s_ in sub:
                if cur and F_SUB.getlength(cur + " " + s_) > 1180 * 2: out.append(cur); cur = s_
                else: cur = (cur + " " + s_).strip()
            if cur: out.append(cur)
        else: out.append(p)
    return [o for o in out if o.strip()]

SUBC = {}
def sub_img(text):
    if text in SUBC: return SUBC[text]
    lines = wrap(text, F_SUB, 1200)
    h = len(lines) * 48 + 30
    im = Image.new("RGBA", (SXY[2], h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, SXY[2] - 1, h - 1), 26, fill=(10, 4, 25, 190), outline=(255, 139, 224, 140), width=2)
    for i, ln in enumerate(lines):
        x = (SXY[2] - F_SUB.getlength(ln)) / 2
        d.text((x + 2, 14 + i * 48 + 2), ln, font=F_SUB, fill=(0, 0, 0))
        d.text((x, 14 + i * 48), ln, font=F_SUB, fill=(255, 245, 200) if i % 2 == 0 and False else WHITE)
    SUBC[text] = im
    return im

# ───────────── música de fondo ─────────────
def music(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    prog = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
    bar = 3.2
    for i in range(int(dur / bar) + 1):
        ch = prog[i % 4]; s0 = int(i * bar * SR); s1 = min(n, int((i + 1) * bar * SR + SR * 0.8))
        if s0 >= n: break
        tt = np.arange(s1 - s0) / SR
        env = np.minimum(1, tt / 0.6) * np.exp(-tt / 3.5)
        for f in ch:
            out[s0:s1] += 0.05 * env * (np.sin(2 * np.pi * f / 2 * tt) + 0.3 * np.sin(2 * np.pi * f * tt))
        # arpegio suave (campanitas)
        for j, f in enumerate(ch + [ch[0] * 2]):
            a0 = s0 + int(j * bar / 4 * SR); a1 = min(n, a0 + int(1.2 * SR))
            if a0 >= n: break
            ta = np.arange(a1 - a0) / SR
            out[a0:a1] += 0.022 * np.exp(-ta * 4) * np.sin(2 * np.pi * f * 2 * ta)
    fade = np.minimum(1, np.minimum(t / 1.5, (dur - t) / 2.0))
    return out * np.clip(fade, 0, 1)

def chime(n_s=1.2, f=(880, 1320, 1760)):
    t = np.arange(int(n_s * SR)) / SR
    return sum(0.12 * np.exp(-t * 3) * np.sin(2 * np.pi * x * t) for x in f)

# ───────────── línea de tiempo ─────────────
INTRO, SCENE_IN, GAP, OUTRO = 4.5, 1.3, 0.45, 4.0

def build(ep):
    tl, t = [], INTRO
    voice_parts = []
    for si, sc in enumerate(ep["escenas"]):
        t += SCENE_IN if si else 0.6
        scene = dict(sc=sc, start=t - (SCENE_IN if si else 0.6), lines=[])
        for (say, bul, ics) in sc["lineas"]:
            el = f"{S}/el/ep{ep['n']}_{len(voice_parts):02d}.wav"
            if os.environ.get("VOZ") == "el" and os.path.exists(el):
                a, sr = sf.read(el)
            else:
                h = hashlib.md5(tts_text(say).encode()).hexdigest()[:12]
                a, sr = sf.read(f"{S}/voz/{h}.wav")
            assert sr == SR
            a = a.astype(np.float64)
            dur = len(a) / SR
            scene["lines"].append(dict(say=say, bul=bul, ics=ics, start=t, dur=dur))
            voice_parts.append((t, a))
            t += dur + GAP
        scene["end"] = t
        tl.append(scene)
    allines = [ln for sc in tl for ln in sc["lines"]]
    k = 0
    for si, sc in enumerate(tl):
        for li, ln in enumerate(sc["lines"]):
            ln["pose"], ln["ex"] = pick(ln["say"], si, li, len(sc["lines"]), si == 0 and li == 0 and ep["n"] >= 1,
                                        ln is allines[-1], k)
            k += 1
    total = t + OUTRO
    return tl, total, voice_parts

def paginate(scene):
    """asigna cada viñeta a una página según el alto"""
    y, page = BUL_Y0, 0
    for ln in scene["lines"]:
        if not ln["bul"]: ln["page"] = page; ln["img"] = None; continue
        im = bullet_img(ln["bul"], ln["ics"])
        if y + im.height > BUL_YMAX: page += 1; y = BUL_Y0
        ln["page"], ln["img"], ln["y"] = page, im, y
        y += im.height + 6

def render(n, outdir, preview=None):
    ep = [e for e in EPISODIOS if e["n"] == n][0]
    tl, total, voice_parts = build(ep)
    # audio
    N = int(total * SR) + SR
    voice = np.zeros(N)
    for t0, a in voice_parts:
        s0 = int(t0 * SR); voice[s0:s0 + len(a)] += a
    mus = music(N / SR)
    mix = voice * 0.95 + mus
    for sc in tl[1:]:
        s0 = int(sc["start"] * SR); c = chime(); mix[s0:s0 + len(c)] += c * 0.6
    c = chime(2.0, (523, 659, 784, 1047)); mix[int(0.3 * SR):int(0.3 * SR) + len(c)] += c
    mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.95), -1, 1)
    wav = f"{outdir}/ep{n:02d}.wav"; sf.write(wav, mix, SR)
    # boca: RMS por frame
    nf = int(total * FPS)
    hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2)) for i in range(nf)])
    ref = np.percentile(rms[rms > 1e-4], 90) if (rms > 1e-4).any() else 1
    lv = np.where(rms / ref > 0.45, 2, np.where(rms / ref > 0.12, 1, 0))
    for i in range(1, nf - 1):   # suavizado: evita parpadeo de 1 frame
        if lv[i] != lv[i - 1] and lv[i] != lv[i + 1]: lv[i] = lv[i - 1]

    for sc in tl:
        paginate(sc)
        sc["base"] = panel_base(sc["sc"], ep)
        sc["fondo"] = sc["sc"].get("fondo", "normal")
        # subtítulos por línea (proporcionales a caracteres)
        for ln in sc["lines"]:
            ch = sub_chunks(ln["say"]); L = sum(len(c) for c in ch); acc = 0; ln["subs"] = []
            for c in ch:
                ln["subs"].append((ln["start"] + ln["dur"] * acc / L, c)); acc += len(c)

    allines = [ln for sc in tl for ln in sc["lines"]]
    logo = Image.open(TX + "ui/hm_logo.png").convert("RGBA")
    logo = logo.resize((1100, int(1100 * logo.height / logo.width)), Image.LANCZOS)

    frames = range(nf) if preview is None else preview
    if preview is None:
        out = f"{outdir}/Horizon_Guia_Ep{n:02d}.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    cache = {}
    for fi in frames:
        t = fi / FPS
        # escena actual
        cur = tl[0]
        for sc in tl:
            if t >= sc["start"]: cur = sc
        fondo = cur["fondo"] if t >= INTRO else "normal"
        img = bg(fondo).copy()
        draw_stars(img, t)
        if t < INTRO:   # ─── portada
            k = min(1, t / 0.8)
            e = 1 - (1 - k) ** 3
            lx = (W - logo.width) // 2 + 180
            img.alpha_composite(logo, (lx, int(60 - 200 * (1 - e))))
            d = ImageDraw.Draw(img)
            if t > 0.6:
                a = min(1, (t - 0.6) / 0.6)
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
                s1 = f"Episodio {n}"; s2 = ep["titulo"]; s3 = ep["sub"]
                cx = W // 2 + 180
                text_shadow(dl, (cx - F_MED.getlength(s1) / 2, 470), s1, F_MED, GOLD)
                tl2 = wrap(s2, F_BIG, 1250)
                for i, l2 in enumerate(tl2):
                    text_shadow(dl, (cx - F_BIG.getlength(l2) / 2, 545 + i * 120), l2, F_BIG, PINK, off=5)
                yy = 560 + len(tl2) * 120
                text_shadow(dl, (cx - F_BUL.getlength(s3) / 2, yy), s3, F_BUL, WHITE)
                s4 = "con Yei"
                text_shadow(dl, (cx - F_TAG.getlength(s4) / 2, yy + 70), s4, F_TAG, GOLD)
                lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
                img.alpha_composite(lay)
            ax = int(-500 + 560 * (1 - (1 - min(1, t / 1.0)) ** 3))
            draw_avatar(img, t, 0, x0=ax)
        else:
            # pizarra
            tin = t - cur["start"]
            vis = [ln for ln in cur["lines"] if ln["img"] is not None and t >= ln["start"]]
            page = vis[-1]["page"] if vis else 0
            vis = [ln for ln in vis if ln["page"] == page]
            key = (id(cur), page, len(vis))
            settled = [ln for ln in vis if t - ln["start"] > 0.5]
            pk = (id(cur), page, len(settled))
            if pk not in cache:
                cache.clear()
                p = cur["base"].copy()
                for ln in settled: p.alpha_composite(ln["img"], (BUL_X - 30, ln["y"]))
                cache[pk] = p
            p = cache[pk]
            anim = [ln for ln in vis if t - ln["start"] <= 0.5]
            if anim:
                p = p.copy()
                for ln in anim:
                    k = (t - ln["start"]) / 0.5; e = 1 - (1 - k) ** 3
                    im = ln["img"].copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * e)))
                    p.alpha_composite(im, (int(BUL_X - 30 + 60 * (1 - e)), ln["y"]))
            if tin < 0.5:   # entrada de escena
                k = tin / 0.5; e = 1 - (1 - k) ** 3
                p = p.copy(); p.putalpha(p.getchannel("A").point(lambda v: int(v * e)))
                img.alpha_composite(p, (PX, int(PY + 40 * (1 - e))))
            else:
                img.alpha_composite(p, (PX, PY))
            # subtítulo
            for ln in cur["lines"]:
                if ln["start"] <= t < ln["start"] + ln["dur"] + 0.25:
                    txt = [c for (st, c) in ln["subs"] if st <= t][-1]
                    si = sub_img(txt)
                    img.alpha_composite(si, (SXY[0], SXY[1] + (SXY[3] - si.height) // 2))
            lvl = int(lv[fi]) if fi < len(lv) else 0
            draw_yei(img, t, lvl, allines)
            img.alpha_composite(NAMEPLATE, (AV_CX - 115, 1000))
            # outro
            end = tl[-1]["end"]
            if t > end:
                a = min(1, (t - end) / 1.0)
                lay = Image.new("RGBA", (W, H), (12, 4, 30, int(235 * a)))
                img.alpha_composite(lay)
                lg = logo.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
                img.alpha_composite(lg, ((W - logo.width) // 2, 220))
                d = ImageDraw.Draw(img)
                msg = "¡Gracias por ver!" if n == len(EPISODIOS) else f"Próximo: Episodio {n + 1} · " + [e for e in EPISODIOS if e["n"] == n + 1][0]["titulo"]
                col = tuple(int(c * a) for c in PINK)
                d.text(((W - F_MED.getlength(msg)) / 2, 700), msg, font=F_MED, fill=col)
        if preview is None:
            ff.stdin.write(img.convert("RGB").tobytes())
        else:
            img.convert("RGB").save(f"{outdir}/prev_{n}_{fi}.png")
    if preview is None:
        ff.stdin.close(); ff.wait(); os.remove(wav)
        print("listo", out, round(total, 1), "s", flush=True)

if __name__ == "__main__":
    n = int(sys.argv[1]); outdir = sys.argv[2]
    prev = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    os.makedirs(outdir, exist_ok=True)
    render(n, outdir, prev)
