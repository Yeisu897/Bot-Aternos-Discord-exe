# Motor v2: Yei explica Horizon con HUD animado, tarjetas, efectos, transiciones y subtítulos karaoke.
import sys, os, math, hashlib, subprocess, re, random
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

S = "/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad"
sys.path.insert(0, S + "/work")
import render as R                      # reutiliza fondos, avatar, poses, música...
from episodios2 import EPISODIOS
from tts import tts_text

W, H, FPS, SR = R.W, R.H, R.FPS, R.SR
TX, UI = R.TX, R.TX + "ui/"
PINK, GOLD, WHITE = R.PINK, R.GOLD, R.WHITE
CYAN = (120, 230, 255)
font = R.font
F_TITLE = font("fredoka", 600, 60)
F_HUGE = font("fredoka", 700, 170)
F_BIG = font("fredoka", 700, 110)
F_MED = font("fredoka", 600, 54)
F_CAP = font("fredoka", 600, 44)
F_TAG = font("fredoka", 600, 30)
F_SUB = font("nunito", 700, 40)
F_SLOT = font("nunito", 700, 19)
F_HUD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
F_HUDS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
F_CMD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 40)
F_SYM = {}
def fsym(size):
    if size not in F_SYM: F_SYM[size] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    return F_SYM[size]
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)

PX, PY, PW, PH = 590, 40, 1290, 790
VX, VY, VW, VH = 30, 160, 1230, 600            # área visual dentro de la pizarra
SXY = (590, 858, 1290, 196)

def ease(k): k = max(0, min(1, k)); return 1 - (1 - k) ** 3
def ease_back(k):
    k = max(0, min(1, k)); c = 1.7; k -= 1
    return 1 + (c + 1) * k ** 3 + c * k ** 2
def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im
def scaled(im, s):
    if abs(s - 1) < 0.01: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
def paste_c(dst, im, cx, cy):
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ───────────── texto con símbolos y emojis ─────────────
def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or ch in "✨⚡☀✔"
def rich(text, f, fill, size, shadow=True, stroke=0):
    """Dibuja texto mezclando Fredoka/Nunito, símbolos (DejaVu) y emojis (Noto). Devuelve RGBA."""
    parts, cur, kind = [], "", None
    for ch in text:
        k = "e" if is_emoji(ch) else ("s" if ord(ch) > 0x24F and ch not in "¡¿" else "t")
        if k != kind and cur: parts.append((kind, cur)); cur = ""
        kind = k; cur += ch
    if cur: parts.append((kind, cur))
    pieces = []
    for k, s in parts:
        if k == "e":
            for ch in s:
                e = Image.new("RGBA", (140, 130), (0, 0, 0, 0)); ImageDraw.Draw(e).text((0, 0), ch, font=EMO, embedded_color=True)
                e = e.crop(e.getbbox() or (0, 0, 1, 1)); e = e.resize((int(size * 1.05 * e.width / max(1, e.height)), int(size * 1.05)), Image.LANCZOS)
                pieces.append(("img", e))
        else:
            ff = f if k == "t" else fsym(int(size * 0.92))
            pieces.append(("txt", (s, ff)))
    total = 0; hmax = int(size * 1.35)
    for k, p in pieces: total += p.width if k == "img" else int(p[1].getlength(p[0]))
    im = Image.new("RGBA", (total + 12 + stroke * 2, hmax + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 4 + stroke
    for k, p in pieces:
        if k == "img":
            im.alpha_composite(p, (x, int((hmax - p.height) / 2) + 2)); x += p.width
        else:
            s, ff = p
            yo = int(size * 0.08) if ff is not f else 0
            if shadow: d.text((x + 4, 4 + yo + 4), s, font=ff, fill=(25, 5, 45), stroke_width=stroke, stroke_fill=(25, 5, 45))
            d.text((x, 4 + yo), s, font=ff, fill=fill, stroke_width=stroke, stroke_fill=(60, 10, 90))
            x += int(ff.getlength(s))
    return im

# ───────────── íconos: pack + Minecraft ─────────────
MC = S + "/mc/tex/"
VAN = {"Manzana dorada": "mc:apple_golden", "Manzana encantada": "mc:apple_golden*", "Cristal": "mc:glass", "Hilo": "mc:string", "Cuero": "mc:leather",
       "Botella": "mc:potion_bottle_empty", "Tablones": "mc:planks_oak", "Antorcha": "mc:torch_on", "Farol": "mc:lantern", "Espada netherita": "mc:netherite_sword",
       "Vara de blaze": "mc:blaze_rod", "Cubeta de lava": "mc:bucket_lava", "Maza": "mc:mace", "Netherita": "mc:netherite_ingot", "Bloque de oro": "mc:gold_block",
       "Oro": "mc:gold_ingot", "Amatista": "mc:amethyst_shard", "Cuarzo": "mc:quartz_block_side", "Cobre": "mc:copper_ingot", "Hierro": "mc:iron_ingot",
       "~Faro": "blk:hm_faro_lado", "~Altar": "mc:quartz_block_side"}
ICC = {}
def ic(name, size):
    """Ícono por nombre: ítem del pack, 'blk:' bloque del pack, 'mc:' textura de Minecraft ('*' = brillo de encantamiento)."""
    name = VAN.get(name, name)
    key = (name, size)
    if key in ICC: return ICC[key]
    glint = name.endswith("*"); nm = name.rstrip("*")
    if nm.startswith("mc:"): im = Image.open(MC + nm[3:] + ".png").convert("RGBA")
    elif nm.startswith("blk:"): im = Image.open(TX + "blocks/" + nm[4:] + ".png").convert("RGBA")
    else: im = Image.open(TX + "items/" + nm + ".png").convert("RGBA")
    if nm == "mc:lantern": im = im.crop((0, 0, 6, 15))
    if im.height > im.width * 1.5 and nm != "mc:lantern": im = im.crop((0, 0, im.width, im.width))
    if im.width != im.height:
        q = max(im.size); sq = Image.new("RGBA", (q, q), (0, 0, 0, 0)); sq.paste(im, ((q - im.width) // 2, (q - im.height) // 2)); im = sq
    if glint:
        g = Image.new("RGBA", im.size, (190, 90, 255, 0)); a = im.getchannel("A").point(lambda v: int(v * 0.28)); g.putalpha(a); im.alpha_composite(g)
    im = im.resize((size, size), Image.NEAREST)
    ICC[key] = im
    return im
def has_ic(name):
    name = VAN.get(name, name).rstrip("*")
    if name.startswith("mc:"): return os.path.exists(MC + name[3:] + ".png")
    if name.startswith("blk:"): return os.path.exists(TX + "blocks/" + name[4:] + ".png")
    return os.path.exists(TX + "items/" + name + ".png")

# ───────────── Yei ─────────────
YD = S + "/yei/"
EXP_OK = ["feliz", "seria", "enojada", "triste", "sorprendida", "sonrojada"]   # solo la hoja 1
EXP_MAP = {"asustada": "sorprendida", "miedosa": "sorprendida", "confundida": "seria", "pensativa": "seria", "curiosa": "feliz",
           "burlona": "feliz", "coqueta": "sonrojada", "cansada": "triste"}
def turn_img(name, h=1000):
    im = Image.open(YD + f"t_{name}.png").convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
TURN = {"espalda": turn_img("espalda", R.AV_H)}

def pick(say, si, li, first, last, k, vis):
    pose, ex = R.pick(say, si, li, 0, first, last, k)
    ex = EXP_MAP.get(ex, ex)
    if vis and vis[0] == "hud" and pose == "base" and k % 2 == 0: pose = "mira"
    if vis and vis[0] == "receta" and pose == "base": pose = "explica"
    return pose, ex

def draw_yei(img, t, level, lines_all, scene_starts):
    # giro al cambiar de escena: frente → lado → espalda → lado → frente
    for st in scene_starts:
        if 0 <= t - st < 0.7:
            k = (t - st) / 0.7
            fr = R.AV[0] if (k < 0.25 or k >= 0.75) else TURN["espalda"]   # frente → espalda → frente (sin vista de perfil)
            sx = max(0.08, abs(math.cos(k * 2 * math.pi)))
            fr = fr.resize((max(1, int(fr.width * sx)), fr.height), Image.BILINEAR)
            hop = -math.sin(k * math.pi) * 40
            img.alpha_composite(R.GLOW, (R.AV_CX - 250, 1005))
            img.alpha_composite(fr, (int(R.AV_CX - fr.width / 2), int(70 + hop)))
            return "giro"
    cur = prev = None
    for ln in lines_all:
        if ln["start"] <= t: prev, cur = cur, ln
    if cur is None:
        R.draw_avatar(img, t, level); return "base"
    pose, pp = cur["pose"], (prev["pose"] if prev else "base")
    dt = t - cur["start"]
    hop = 0
    if cur.get("hop") and dt < 0.5: hop = -int(math.sin(dt / 0.5 * math.pi) * 45)
    def one(p, a, dy):
        if p == "base": R.draw_avatar(img, t, level, y0=70 + dy, alpha=a)
        else: R.draw_pose(img, t, p, level, a, dy)
    if pose != pp and dt < 0.3:
        k = dt / 0.3; one(pp, 1 - k, 0); one(pose, k, int(30 * (1 - k)) + hop)
    else: one(pose, 1.0, hop)
    if pose == "base":
        same = prev is not None and prev["pose"] == "base" and prev["ex"] == cur["ex"]
        b = R.badge(cur["ex"])
        k = 1.0 if same else min(1, dt / 0.35)
        sc = max(0.05, ease_back(k)) if k < 1 else 1.0
        bb = scaled(b, sc)
        bx, by = 352, 30 + int(math.sin(t * 2.4) * 4)
        img.alpha_composite(bb, (bx + (b.width - bb.width) // 2, by + (b.height - bb.height)))
    return pose

# ───────────── HUD de Minecraft (maqueta animada) ─────────────
OW, OH = 1066, 600                      # tamaño final de la maqueta
SSF = 2                                 # se dibuja al doble y se reduce (texto nítido con zoom)
GW, GH = OW * SSF, OH * SSF
G = GW / 640                            # pantalla de 640 px de GUI
def gi(v): return int(round(v * G))
def ui(name): return Image.open(UI + name + ".png").convert("RGBA")
def up(im, s=None):
    s = s or G
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.NEAREST)
def nine(name, w, h, b=5, s=None):
    s = s or G
    src = ui(name); sw, sh = src.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); bb = max(1, round(b * s))
    def part(box, size): return src.crop(box).resize((max(1, size[0]), max(1, size[1])), Image.NEAREST)
    out.paste(part((0, 0, b, b), (bb, bb)), (0, 0)); out.paste(part((sw - b, 0, sw, b), (bb, bb)), (w - bb, 0))
    out.paste(part((0, sh - b, b, sh), (bb, bb)), (0, h - bb)); out.paste(part((sw - b, sh - b, sw, sh), (bb, bb)), (w - bb, h - bb))
    out.paste(part((b, 0, sw - b, b), (w - 2 * bb, bb)), (bb, 0)); out.paste(part((b, sh - b, sw - b, sh), (w - 2 * bb, bb)), (bb, h - bb))
    out.paste(part((0, b, b, sh - b), (bb, h - 2 * bb)), (0, bb)); out.paste(part((sw - b, b, sw, sh - b), (bb, h - 2 * bb)), (w - bb, bb))
    out.paste(part((b, b, sw - b, sh - b), (w - 2 * bb, h - 2 * bb)), (bb, bb))
    return out
F_HUD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
F_HUDS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
LH = 32

def world_bg():
    rng = random.Random(3)
    im = Image.new("RGBA", (GW, GH)); d = ImageDraw.Draw(im)
    for y in range(GH):
        k = y / GH; d.line((0, y, GW, y), fill=(int(110 + 60 * k), int(170 + 40 * k), 255))
    B = 60; cols = GW // B + 1; hts = []; h = 12
    for i in range(cols):
        h += rng.choice([-1, 0, 0, 0, 1]); h = max(9, min(15, h)); hts.append(h)
    for i, hh in enumerate(hts):
        top = GH - hh * B + 480
        for j in range(0, 40):
            y = top + j * B
            if y > GH: break
            c = (95, 160, 60) if j == 0 else (130, 90, 55) if j < 3 else (120, 120, 125)
            jit = rng.randint(-8, 8)
            d.rectangle((i * B, y, i * B + B - 1, y + B - 1), fill=tuple(max(0, min(255, v + jit)) for v in c))
            d.rectangle((i * B, y, i * B + B - 1, y + B - 1), outline=tuple(max(0, v - 25) for v in c))
        if rng.random() < 0.18:
            tx = i * B; ty = top - 4 * B
            for q in range(4): d.rectangle((tx, ty + q * B, tx + B - 1, ty + q * B + B - 1), fill=(110, 80, 45))
            for a in range(-2, 3):
                for b2 in range(-2, 1):
                    if abs(a) + abs(b2) < 4:
                        d.rectangle((tx + a * B, ty + b2 * B - B, tx + a * B + B - 1, ty + b2 * B - 1), fill=(60 + rng.randint(0, 25), 130 + rng.randint(0, 25), 50))
    d.rectangle((1380, 300, 1520, 440), fill=(255, 240, 170))
    return im.filter(ImageFilter.GaussianBlur(2.0))

HUDC = {}
def hud_static():
    if "s" in HUDC: return HUDC["s"]
    im = world_bg(); cx = GW // 2
    hb = Image.new("RGBA", (182, 22), (0, 0, 0, 0))
    hb.paste(ui("hotbar_start_cap"), (0, 0))
    for i in range(9): hb.paste(ui(f"hotbar_{i}"), (1 + i * 20, 0))
    hb.paste(ui("hotbar_end_cap"), (181, 0))
    hb = up(hb); hbx, hby = cx - hb.width // 2, GH - hb.height
    im.alpha_composite(hb, (hbx, hby))
    im.alpha_composite(up(ui("selected_hotbar_slot")), (hbx - gi(1), hby - gi(1)))
    for k, nm in enumerate(["pastilla", "bloqueador", "hm_cantimplora", "gancho", "libro"]):
        im.alpha_composite(R.icon(nm, gi(16)), (hbx + gi(3 + 20 * k), hby + gi(3)))
    im.alpha_composite(up(ui("experience_bar_empty")), (hbx, hby - gi(6)))
    im.alpha_composite(up(ui("experience_bar_full").crop((0, 0, 70, 5))), (hbx, hby - gi(6)))
    base_y = GH; left = cx - gi(91)
    for i in range(10):
        im.alpha_composite(up(ui("heart_background")), (left + gi(i * 8), base_y - gi(39)))
        im.alpha_composite(up(ui("heart")), (left + gi(i * 8), base_y - gi(39)))
        im.alpha_composite(up(ui("food_full")), (left + gi(172 - i * 8), base_y - gi(39)))
    HUDC["s"] = (im, left, base_y)
    return HUDC["s"]

def frame_strip(name, i, fw, fh):
    key = (name, i % (ui(name).width // fw))
    if key not in HUDC:
        src = ui(name); n = src.width // fw; j = i % n
        HUDC[key] = up(src.crop((j * fw, 0, j * fw + fw, fh)))
    return HUDC[key]

CARD = {0: "S", 45: "SO", 90: "O", 135: "NO", 180: "N", 225: "NE", 270: "E", 315: "SE"}
def compass_text(h, casa=None):
    h = int(round(h / 5) * 5); out = ""; i = 0
    while i < 37:
        a = (h + (i - 18) * 5) % 360
        c = CARD.get(a)
        if casa is not None and abs(((a - casa + 180) % 360) - 180) < 3: out += "#"
        elif c: out += c; i += len(c) - 1
        else: out += "." if a % 15 == 0 else " "
        i += 1
    return out

COLS = {"{p}": PINK, "{w}": WHITE, "{g}": (175, 175, 175), "{y}": (255, 230, 90), "{a}": (120, 230, 120), "{b}": CYAN, "{r}": (255, 90, 90), "{o}": (255, 170, 60)}
def text_panel(lines, pad=None):
    padx, pady = gi(6), gi(4)
    ws = [F_HUD.getlength(re.sub(r"\{[^}]*\}", "", l)) for l in lines]
    w = int(max(ws) + padx * 2); h = len(lines) * LH + pady * 2
    p = nine("hm_info_panel", w, h, 5); d = ImageDraw.Draw(p)
    for i, l in enumerate(lines):
        x = padx; col = WHITE
        for seg in re.split(r"(\{[^}]*\})", l):
            if not seg: continue
            if seg.startswith("{"): col = COLS[seg]; continue
            d.text((x, pady + i * LH), seg, font=F_HUD, fill=col); x += F_HUD.getlength(seg)
    return p

def hud_frame(foco, t, dt):
    base, left, base_y = hud_static()
    im = base.copy(); d = ImageDraw.Draw(im); cx = GW // 2
    temp = "c"
    if foco == "temp_ciclo": temp = "abcde"[int(dt / 0.95) % 5]
    elif foco == "borde_calor": temp = "e"
    elif foco == "borde_frio": temp = "a"
    orb = frame_strip(f"hm_temp_{temp}", int(t * 6), 16, 16)
    ox, oy = cx - gi(8), base_y - gi(59)
    im.alpha_composite(orb, (ox, oy))
    n = 16
    if foco == "sed": n = max(4, 20 - int(dt * 3))
    elif foco == "sed_urge": n = 5
    elif foco == "sed_llenar": n = min(20, 4 + int(dt * 4))
    urge = n <= 6
    for i in range(10):
        e = "F" if n >= (i + 1) * 2 else ("H" if n == i * 2 + 1 else "E")
        if urge and e in "FH": e = "U" if e == "F" else "V"
        im.alpha_composite(frame_strip(f"hm_sed/g{i}_{e}", int(t * 8), 9, 10), (left + gi(171 - 8 * i), base_y - gi(52)))
    # brújula (arriba al centro, y=34) + dinero debajo (y=54)
    head = (t * 18) % 360 if foco in ("brujula", "brujula_casa") else 180
    casa = (head + 25) % 360 if foco == "brujula_casa" else None
    ct = compass_text(head, casa)
    cw = int(F_HUD.getlength(ct)) + gi(10); ch = LH + gi(4)
    cp = nine("hm_info_panel", cw, ch, 5); dc = ImageDraw.Draw(cp)
    x = gi(5)
    for c in ct:
        dc.text((x, gi(2)), c, font=F_HUD, fill=(255, 215, 70) if c == "#" else WHITE); x += F_HUD.getlength(c)
    im.alpha_composite(cp, (cx - cw // 2, gi(34)))
    d.text((cx - 10, gi(34) + ch - 4), "▼", font=F_HUDS, fill=PINK)
    tot = 12 + (int(dt * 9) % 50 if foco == "dinero" else 0)
    segs = [("♥ ", None), (str(tot), "ficha"), (" 3", "ficha_verde"), (" 1", "ficha_azul")]
    wtot = sum(F_HUD.getlength(s) + (gi(9) if ic else 0) for s, ic in segs)
    xx = cx - wtot / 2; yy = gi(54)
    for s, ic in segs:
        d.text((xx, yy), s, font=F_HUD, fill=PINK if ic is None else WHITE); xx += F_HUD.getlength(s)
        if ic: im.alpha_composite(R.icon(ic, gi(8)), (int(xx), yy + 1)); xx += gi(9)
    d.text((cx - 36, yy + LH), "45", font=F_HUD, fill=(255, 190, 60)); im.alpha_composite(R.icon("ticket", gi(8)), (cx + 4, yy + LH + 2))
    # panel izquierdo (4, 30)
    mis = min(24, int(dt * 4)) if foco == "izq" else 12
    izq = ["{p}✦ {g}X {w}128 {g}Y {w}71 {g}Z {w}-340  {b}➤ N 180°", "{a}♣ {w}Llanuras", "{y}⌂ {w}Casa {g}85 m",
           "{w}Tala troncos {y}%d{g}/24" % mis, "{a}✓ Pica piedra {g}(64)", "{w}Pesca peces {y}2{g}/5"]
    if foco == "debug":
        izq = ["{w}Horizonbeta · Debug", "{g}FPS 60 · TPS 20.0", "{w}XYZ 128.4 / 71.0 / -340.2", "{w}Bioma: plains", "{w}Calor 54 · Sed 81", "{w}Entidades: 23"]
    lp = text_panel(izq); im.alpha_composite(lp, (gi(10), gi(30)))
    # radar (arriba a la derecha: -4, 46, 56×56)
    rw = gi(56); rx, ry = GW - gi(10) - rw, gi(46)
    im.alpha_composite(ui("hm_radar").resize((rw, rw), Image.NEAREST), (rx, ry))
    sweep = ui("hm_radar_barrido"); fi = int(t * 8) % 8
    im.alpha_composite(sweep.crop((fi * 56, 0, fi * 56 + 56, 56)).resize((rw, rw), Image.NEAREST), (rx, ry))
    dots = [("m", 0, -8), ("m", 11, 11), ("a", -16, 0), ("a", 6, 6), ("j", -11, -11), ("m", 0, 16)]
    for k, (ty, dx, dy) in enumerate(dots):
        if foco == "radar" and (t * 3 + k) % 3 < 0.6: continue
        dot = up(ui(f"hm_radar_{ty}"))
        im.alpha_composite(dot, (rx + rw // 2 + gi(dx) - dot.width // 2, ry + rw // 2 + gi(dy) - dot.height // 2))
    # panel derecho (actionbar: -66, 34 desde arriba a la derecha)
    der = ["{o}☀ {w}Día {y}37{g}/1000 · {w}14:20", "{g}Velocidad I 1:20", "{r}☠ Zombi 4:12 {p}· {a}☀ Protegido 8:41", "{o}☄ Meteoritos {w}2:35"]
    rp = text_panel(der); rpx = GW - gi(72) - rp.width
    im.alpha_composite(rp, (rpx, gi(34)))
    if foco == "borde_calor":
        a = 0.6 + 0.4 * math.sin(t * 6)
        im.alpha_composite(with_alpha(ui("hm_borde_q").resize((GW, GH), Image.NEAREST), a))
    if foco == "borde_frio":
        im.alpha_composite(with_alpha(ui("hm_frost").resize((GW, GH), Image.BILINEAR), min(1, dt / 1.2)))
        im.alpha_composite(ui("hm_borde_r").resize((GW, GH), Image.NEAREST))
    sed_c = (left + gi(135), base_y - gi(47))
    FOCO = {"todo": (GW / 2, GH / 2, 1.0), "brujula": (cx, gi(42), 3.0), "brujula_casa": (cx, gi(42), 3.0), "dinero": (cx, gi(62), 3.4),
            "izq": (lp.width / 2 + gi(10), gi(30) + lp.height / 2, 2.6), "debug": (lp.width / 2 + gi(10), gi(30) + lp.height / 2, 2.6),
            "radar": (rx + rw / 2, ry + rw / 2, 3.2), "der": (rpx + rp.width / 2, gi(34) + rp.height / 2, 2.4),
            "temp": (cx, oy + gi(8), 3.6), "temp_ciclo": (cx, oy + gi(8), 4.2), "sed": (*sed_c, 3.2), "sed_urge": (*sed_c, 3.2), "sed_llenar": (*sed_c, 3.2),
            "borde_calor": (GW / 2, GH / 2, 1.0), "borde_frio": (GW / 2, GH / 2, 1.0)}
    fx_, fy_, z = FOCO.get(foco, (GW / 2, GH / 2, 1.0))
    k = ease(dt / 0.9)
    z = 1 + (z - 1) * k
    if foco == "todo": z = 1 + 0.04 * math.sin(t)
    cxz = GW / 2 + (fx_ - GW / 2) * k; cyz = GH / 2 + (fy_ - GH / 2) * k
    ww, hh = GW / z, GH / z
    x0 = min(max(0, cxz - ww / 2), GW - ww); y0 = min(max(0, cyz - hh / 2), GH - hh)
    im = im.crop((int(x0), int(y0), int(x0 + ww), int(y0 + hh))).resize((OW, OH), Image.BILINEAR if z > 1.6 else Image.LANCZOS)
    m = Image.new("L", (OW, OH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, OW - 1, OH - 1), 22, fill=255)
    out = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); out.paste(im, (0, 0), m)
    ImageDraw.Draw(out).rounded_rectangle((0, 0, OW - 1, OH - 1), 22, outline=PINK, width=5)
    return out

# ───────────── tarjetas visuales ─────────────
CUAD = {}
def cuadro(n, size=470):
    if n not in CUAD:
        im = Image.open(TX + f"entity/cuadros/cuadro_{n}.png").convert("RGBA").crop((0, 0, 34, 34))
        CUAD[n] = im.resize((size, size), Image.NEAREST)
    return CUAD[n]

GLOWC = Image.new("RGBA", (420, 420), (0, 0, 0, 0)); ImageDraw.Draw(GLOWC).ellipse((60, 60, 360, 360), fill=(255, 140, 230, 150))
GLOWC = GLOWC.filter(ImageFilter.GaussianBlur(40))

def sparkle(d, x, y, r, a=255, col=(255, 240, 255)):
    c = col + (a,)
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22), (x, y + r), (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=c)

def card_cuadro(n, t, dt):
    out = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    k = ease_back(dt / 0.6)
    z = (0.2 + 0.8 * k) * (1 + 0.05 * min(1, dt / 6))
    im = scaled(cuadro(n), z)
    rot = (1 - ease(dt / 0.6)) * -20 + math.sin(t * 1.4) * 2
    im = im.rotate(rot, Image.BICUBIC, expand=True)
    paste_c(out, GLOWC, VW / 2, VH / 2)
    paste_c(out, im, VW / 2, VH / 2 + math.sin(t * 2) * 6)
    d = ImageDraw.Draw(out)
    for i in range(6):
        ang = t * 0.8 + i * 1.047; rr = 300 + 20 * math.sin(t * 2 + i)
        a = int(200 * (0.5 + 0.5 * math.sin(t * 3 + i)))
        sparkle(d, VW / 2 + math.cos(ang) * rr, VH / 2 + math.sin(ang) * rr * 0.75, 14, a)
    return out

def card_items(ics, t, dt):
    out = Image.new("RGBA", (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    n = len(ics); sz = 220 if n <= 2 else 170 if n <= 4 else 140 if n <= 6 else 120
    gap = sz + 40
    rows = [ics] if n <= 5 else [ics[:(n + 1) // 2], ics[(n + 1) // 2:]]
    j = 0
    for r, row in enumerate(rows):
        y = VH / 2 + (r - (len(rows) - 1) / 2) * (sz + 60)
        for i, nm in enumerate(row):
            x = VW / 2 + (i - (len(row) - 1) / 2) * gap
            k = (dt - j * 0.14) / 0.45
            if k > 0:
                s = ease_back(k)
                fl = math.sin(t * 2.5 + j) * 8
                paste_c(out, scaled(GLOWC, sz / 300 * max(0.01, s)), x, y + fl)
                d.ellipse((x - sz * 0.62, y - sz * 0.62 + fl, x + sz * 0.62, y + sz * 0.62 + fl), outline=(255, 205, 90, int(160 * min(1, k))), width=4)
                icm = ic(nm, sz)
                icm = scaled(icm, max(0.05, s)).rotate(math.sin(t * 2 + j) * 6, Image.NEAREST, expand=True)
                paste_c(out, icm, x, y + fl)
            j += 1
    return out

SLOT = 128
def slot_tile(tok):
    key = ("slot", tok)
    if key in HUDC: return HUDC[key]
    im = Image.new("RGBA", (SLOT, SLOT), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, SLOT - 1, SLOT - 1), fill=(139, 139, 139, 255))
    d.line((0, 0, SLOT - 1, 0), fill=(55, 55, 55), width=6); d.line((0, 0, 0, SLOT - 1), fill=(55, 55, 55), width=6)
    d.line((0, SLOT - 3, SLOT - 1, SLOT - 3), fill=(255, 255, 255), width=6); d.line((SLOT - 3, 0, SLOT - 3, SLOT - 1), fill=(255, 255, 255), width=6)
    HUDC[key] = im
    return im
def item_tile(tok, size=104):
    key = ("item", tok, size)
    if key in HUDC: return HUDC[key]
    if has_ic(tok):
        im = ic(tok, size)
    else:
        name = tok.lstrip("~")
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((2, 2, size - 3, size - 3), 18, fill=(60, 30, 100, 235), outline=PINK, width=3)
        lines = R.wrap(name, F_SLOT, size - 12)[:4]
        for i, l in enumerate(lines):
            d.text(((size - F_SLOT.getlength(l)) / 2, size / 2 - len(lines) * 12 + i * 24), l, font=F_SLOT, fill=WHITE)
    HUDC[key] = im
    return im

def card_receta(grid, res, t, dt):
    out = Image.new("RGBA", (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    gx, gy = 250, (VH - 3 * SLOT - 16) / 2
    d.rounded_rectangle((gx - 30, gy - 30, gx + 3 * SLOT + 46, gy + 3 * SLOT + 46), 20, fill=(198, 198, 198, 245), outline=(40, 40, 40), width=4)
    for i in range(9):
        x = gx + (i % 3) * (SLOT + 8); y = gy + (i // 3) * (SLOT + 8)
        out.alpha_composite(slot_tile("s"), (int(x), int(y)))
    order = [i for i in range(9) if grid[i]]
    for j, i in enumerate(order):
        k = (dt - 0.15 - j * 0.12) / 0.35
        if k <= 0: continue
        x = gx + (i % 3) * (SLOT + 8) + SLOT / 2; y = gy + (i // 3) * (SLOT + 8) + SLOT / 2
        s = ease_back(k); tile = scaled(item_tile(grid[i]), max(0.05, s))
        paste_c(out, tile, x, y - (1 - ease(k)) * 60)
    tdone = 0.15 + len(order) * 0.12 + 0.35
    ax = gx + 3 * SLOT + 90
    ka = ease((dt - tdone) / 0.3)
    if ka > 0:
        pts = [(ax, VH / 2 - 30), (ax + 110 * ka, VH / 2 - 30), (ax + 110 * ka, VH / 2 - 60), (ax + 110 * ka + 60, VH / 2), (ax + 110 * ka, VH / 2 + 60), (ax + 110 * ka, VH / 2 + 30), (ax, VH / 2 + 30)]
        d.polygon(pts, fill=(255, 255, 255, 230), outline=PINK)
    kr = (dt - tdone - 0.25) / 0.45
    if kr > 0:
        rx = ax + 330; ry = VH / 2
        paste_c(out, scaled(GLOWC, 0.9 + 0.1 * math.sin(t * 4)), rx, ry)
        big = scaled(slot_tile("s"), 1.5); paste_c(out, big, rx, ry)
        paste_c(out, scaled(item_tile(res, 160), max(0.05, ease_back(kr))), rx, ry)
        for i in range(5):
            ang = t * 1.5 + i * 1.25; sparkle(d, rx + math.cos(ang) * 150, ry + math.sin(ang) * 150, 16, int(255 * min(1, kr)))
    return out

def card_big(txt, sub, t, dt, icons=None):
    out = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    key = ("big", txt)
    if key not in HUDC:
        f = F_HUGE if len(txt) <= 7 else F_BIG
        size = 170 if f is F_HUGE else 110
        HUDC[key] = rich(txt, f, PINK, size, stroke=6)
    im = HUDC[key]
    if im.width > VW - 40: im = scaled(im, (VW - 40) / im.width)
    s = ease_back(dt / 0.5) * (1 + 0.03 * math.sin(t * 5))
    rot = math.sin(t * 3) * 2.5
    ty = VH / 2 - 60
    if icons:                                   # fila de texturas (pack / Minecraft) encima del texto
        ty = VH / 2 + 10
        if im.height > 170: im = scaled(im, 170 / im.height)
        n = len(icons); sz = 150 if n <= 3 else 120; gap = sz + 40
        for j, nm in enumerate(icons):
            k = (dt - j * 0.12) / 0.4
            if k <= 0: continue
            x = VW / 2 + (j - (n - 1) / 2) * gap; y = 130 + math.sin(t * 3 + j) * 8
            paste_c(out, scaled(GLOWC, sz / 300), x, y)
            paste_c(out, scaled(ic(nm, sz), max(0.05, ease_back(k))).rotate(math.sin(t * 2.2 + j) * 7, Image.NEAREST, expand=True), x, y)
    paste_c(out, GLOWC.resize((900, 420)), VW / 2, ty + 20)
    paste_c(out, scaled(im, max(0.05, s)).rotate(rot, Image.BICUBIC, expand=True), VW / 2, ty)
    if sub:
        k2 = ease((dt - 0.35) / 0.4)
        if k2 > 0:
            key2 = ("sub", sub)
            if key2 not in HUDC: HUDC[key2] = rich(sub, F_MED, WHITE, 54)
            si = HUDC[key2]
            if si.width > VW - 40: si = scaled(si, (VW - 40) / si.width)
            paste_c(out, with_alpha(si, k2), VW / 2, ty + (125 if icons else 190) + 30 * (1 - k2))
    return out

def card_cmd(cmd, t, dt):
    out = Image.new("RGBA", (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    # tecla T + caja de chat
    bw, bh = 1000, 110; bx, by = (VW - bw) / 2, VH / 2 - 20
    d.rounded_rectangle((bx, by, bx + bw, by + bh), 14, fill=(0, 0, 0, 170), outline=(255, 255, 255, 120), width=3)
    n = int(max(0, dt - 0.3) / 0.07)
    shown = cmd[:n]
    d.text((bx + 30, by + 30), shown, font=F_CMD, fill=WHITE)
    if int(t * 2.5) % 2 == 0 or n < len(cmd):
        cx = bx + 30 + F_CMD.getlength(shown) + 4; d.rectangle((cx, by + 30, cx + 20, by + 78), fill=(255, 255, 255, 220))
    d.text((bx, by - 70), "Chat", font=F_CAP, fill=PINK)
    if n >= len(cmd) + 4:
        k = ease((dt - 0.3 - (len(cmd) + 4) * 0.07) / 0.3)
        lab = rich("↵ Enter", F_CAP, GOLD, 44)
        paste_c(out, with_alpha(lab, k), VW / 2, by + bh + 80)
    return out

def card_board(lines_vis):
    return None

def render_vis(v, t, dt):
    if v is None: return None
    kind = v[0]
    if kind == "hud":
        im = hud_frame(v[1], t, dt)
        k = ease(dt / 0.4)
        out = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        out.alpha_composite(with_alpha(im, k), ((VW - OW) // 2, 0))
        return out
    if kind == "cuadro": return card_cuadro(v[1], t, dt)
    if kind == "items": return card_items(v[1], t, dt)
    if kind == "receta": return card_receta(v[1], v[2], t, dt)
    if kind == "big": return card_big(v[1], v[2] if len(v) > 2 else "", t, dt, v[3] if len(v) > 3 else None)
    if kind == "cmd": return card_cmd(v[1], t, dt)

# ───────────── efectos (partículas) ─────────────
PR = random.Random(11)
PARTS = [(PR.random(), PR.random(), PR.random(), PR.random()) for _ in range(90)]
def draw_fx(img, fx, t, dt):
    if not fx: return
    d = ImageDraw.Draw(img)
    a_in = min(1, dt / 0.4)
    if fx == "nieve":
        for (a, b, c, e) in PARTS:
            x = (a * W + math.sin(t * 1.5 + c * 6) * 30) % W; y = (b * H + t * (80 + 90 * c)) % H; r = 3 + 5 * e
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(220 * a_in)))
    elif fx == "brasas":
        for (a, b, c, e) in PARTS[:60]:
            x = (a * W + math.sin(t * 2 + c * 6) * 25) % W; y = H - (b * H + t * (60 + 120 * c)) % H; r = 2 + 4 * e
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, int(120 + 100 * e), 40, int(230 * a_in)))
    elif fx == "corazones":
        for (a, b, c, e) in PARTS[:28]:
            x = (a * W); y = H - (b * H + t * (70 + 80 * c)) % H; s = 16 + 18 * e
            d.text((x, y), "♥", font=fsym(int(s * 2)), fill=(255, 110 + int(80 * c), 190, int(220 * a_in)))
    elif fx == "sangre":
        img.alpha_composite(Image.new("RGBA", (W, H), (150, 0, 20, int(60 * a_in))))
        for (a, b, c, e) in PARTS:
            x = a * W; y = (b * H + t * (500 + 300 * c)) % H
            d.line((x, y, x - 3, y + 22), fill=(190, 10, 30, int(230 * a_in)), width=3)
    elif fx == "confeti":
        cols = [(255, 120, 200), (255, 220, 80), (120, 220, 255), (150, 255, 150), (200, 140, 255)]
        for i, (a, b, c, e) in enumerate(PARTS[:70]):
            x = (a * W + math.sin(t * 2 + c * 6) * 40) % W; y = (b * H + t * (160 + 120 * c)) % H
            ang = t * 4 + c * 6; dx, dy = math.cos(ang) * 10, math.sin(ang) * 5
            d.polygon([(x - dx, y - dy), (x + dy, y - dx), (x + dx, y + dy), (x - dy, y + dx)], fill=cols[i % 5] + (int(240 * a_in),))
    elif fx == "burbujas":
        for (a, b, c, e) in PARTS[:45]:
            x = (a * W + math.sin(t * 2 + c * 6) * 20) % W; y = H - (b * H + t * (90 + 100 * c)) % H; r = 5 + 12 * e
            d.ellipse((x - r, y - r, x + r, y + r), outline=(190, 240, 255, int(200 * a_in)), width=3)
    elif fx == "estrellas":
        for i, (a, b, c, e) in enumerate(PARTS[:40]):
            al = 0.5 + 0.5 * math.sin(t * (2 + 3 * c) + i)
            sparkle(d, a * W, b * H, 8 + 14 * e * al, int(230 * al * a_in), (255, 235, 140) if i % 3 == 0 else (255, 220, 255))
    elif fx == "rayos" and dt < 0.5:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(160 * (1 - dt / 0.5)))))
        x = 1300; pts = [(x, 0)]
        rr = random.Random(int(t)); y = 0
        while y < H: y += 90; x += rr.randint(-70, 70); pts.append((x, y))
        d.line(pts, fill=(255, 255, 200, int(255 * (1 - dt / 0.5))), width=8)

# ───────────── subtítulos karaoke ─────────────
def sub_karaoke(text, prog):
    lines = R.wrap(text, F_SUB, 1210)
    h = len(lines) * 50 + 28
    im = Image.new("RGBA", (SXY[2], h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, SXY[2] - 1, h - 1), 26, fill=(10, 4, 25, 200), outline=(255, 139, 224, 150), width=2)
    total = sum(len(l) for l in lines); upto = prog * total; acc = 0
    for i, ln in enumerate(lines):
        x = (SXY[2] - F_SUB.getlength(ln)) / 2; y = 13 + i * 50
        for w_ in re.split(r"(\s+)", ln):
            if not w_: continue
            col = (255, 160, 230) if acc + len(w_) / 2 <= upto else WHITE
            d.text((x + 2, y + 2), w_, font=F_SUB, fill=(0, 0, 0)); d.text((x, y), w_, font=F_SUB, fill=col)
            x += F_SUB.getlength(w_); acc += len(w_)
    return im

# ───────────── línea de tiempo ─────────────
INTRO, SCENE_IN, GAP, OUTRO = 4.5, 1.5, 0.35, 4.0
def build(ep):
    tl, t, voice_parts = [], INTRO, []
    for si, sc in enumerate(ep["escenas"]):
        st = t; t += SCENE_IN if si else 0.8
        scene = dict(sc=sc, start=st, lines=[])
        for (say, bul, ics, vis, fx) in sc["lineas"]:
            elp = f"{S}/el2/l{ep['n']}_{si}_{len(scene['lines']):02d}.wav"
            if os.environ.get("VOZ") == "el" and os.path.exists(elp):
                a, sr = sf.read(elp)
            else:
                h = hashlib.md5(tts_text(say).encode()).hexdigest()[:12]
                a, sr = sf.read(f"{S}/voz2/{h}.wav")
            assert sr == SR
            a = a.astype(np.float64); dur = len(a) / SR
            scene["lines"].append(dict(say=say, bul=bul, ics=ics, vis=vis, fx=fx, start=t, dur=dur))
            voice_parts.append((t, a)); t += dur + GAP
        scene["end"] = t; tl.append(scene)
    allines = [ln for sc in tl for ln in sc["lines"]]
    k = 0
    for si, sc in enumerate(tl):
        for li, ln in enumerate(sc["lines"]):
            ln["pose"], ln["ex"] = pick(ln["say"], si, li, si == 0 and li == 0, ln is allines[-1], k, ln["vis"])
            ln["hop"] = (ln["vis"] and ln["vis"][0] == "big") or ln["fx"] in ("temblor", "confeti")
            k += 1
    return tl, t + OUTRO, voice_parts

def caption(text):
    key = ("cap", text)
    if key in HUDC: return HUDC[key]
    lab = rich(text, F_CAP, WHITE, 44, shadow=False)
    if lab.width > VW - 80: lab = scaled(lab, (VW - 80) / lab.width)
    im = Image.new("RGBA", (lab.width + 60, lab.height + 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 30, fill=(200, 60, 160, 235), outline=GOLD, width=3)
    im.alpha_composite(lab, (30, 7))
    HUDC[key] = im
    return im

def panel_base(scene, ep):
    p = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(p)
    d.rounded_rectangle((0, 0, PW - 1, PH - 1), 38, fill=(22, 10, 48, 200), outline=PINK, width=5)
    d.rounded_rectangle((10, 10, PW - 11, PH - 11), 30, outline=(255, 205, 90, 110), width=2)
    p.alpha_composite(ic(scene["icon"], 88), (40, 30))
    R.text_shadow(d, (150, 38), scene["t"], F_TITLE, PINK)
    tag = f"EPISODIO {ep['n']}"; tw = F_TAG.getlength(tag)
    d.rounded_rectangle((PW - tw - 80, 44, PW - 40, 92), 24, fill=(255, 139, 224, 60), outline=PINK, width=2)
    d.text((PW - tw - 60, 50), tag, font=F_TAG, fill=WHITE)
    y = 140
    d.line((40, y, PW / 2 - 24, y), fill=(160, 80, 200), width=4); d.line((PW / 2 + 24, y, PW - 40, y), fill=(160, 80, 200), width=4)
    R.diamond(d, PW // 2, y, 12, WHITE)
    return p

def title_card(scene, t, dt):
    """tarjeta de título al empezar cada escena"""
    out = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    k = ease_back(dt / 0.5)
    ic_ = ic(scene["sc"]["icon"], 220).rotate((1 - ease(dt / 0.6)) * 360, Image.NEAREST, expand=True)
    paste_c(out, GLOWC, PW / 2, PH / 2 - 90)
    paste_c(out, scaled(ic_, max(0.05, k)), PW / 2, PH / 2 - 90)
    lab = rich(scene["sc"]["t"], F_BIG, PINK, 110, stroke=4)
    if lab.width > PW - 60: lab = scaled(lab, (PW - 60) / lab.width)
    k2 = ease((dt - 0.2) / 0.5)
    paste_c(out, with_alpha(lab, k2), PW / 2 + (1 - k2) * 200, PH / 2 + 110)
    return out

def render(n, outdir, preview=None):
    ep = [e for e in EPISODIOS if e["n"] == n][0]
    tl, total, voice_parts = build(ep)
    N = int(total * SR) + SR
    voice = np.zeros(N)
    for t0, a in voice_parts:
        s0 = int(t0 * SR); voice[s0:s0 + len(a)] += a
    mix = voice * 0.95 + R.music(N / SR)
    for sc in tl[1:]:
        s0 = int(sc["start"] * SR); c = R.chime(); mix[s0:s0 + len(c)] += c * 0.6
    for sc in tl:                                           # "pop" suave al aparecer cada tarjeta
        for ln in sc["lines"]:
            s0 = int(ln["start"] * SR); c = R.chime(0.25, (1320, 1760)); mix[s0:s0 + len(c)] += c * 0.25
    c = R.chime(2.0, (523, 659, 784, 1047)); mix[int(0.3 * SR):int(0.3 * SR) + len(c)] += c
    mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.95), -1, 1)
    wav = f"{outdir}/ep{n:02d}_v2.wav"; sf.write(wav, mix, SR)
    nf = int(total * FPS); hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2)) for i in range(nf)])
    ref = np.percentile(rms[rms > 1e-4], 90)
    lv = np.where(rms / ref > 0.45, 2, np.where(rms / ref > 0.12, 1, 0))
    for i in range(1, nf - 1):
        if lv[i] != lv[i - 1] and lv[i] != lv[i + 1]: lv[i] = lv[i - 1]
    for sc in tl:
        sc["base"] = panel_base(sc["sc"], ep); sc["fondo"] = sc["sc"].get("fondo", "normal")
        for ln in sc["lines"]:
            ch = R.sub_chunks(ln["say"]); L = sum(len(c) for c in ch); acc = 0; ln["subs"] = []
            for c in ch:
                ln["subs"].append((ln["start"] + ln["dur"] * acc / L, ln["dur"] * len(c) / L, c)); acc += len(c)
    allines = [ln for sc in tl for ln in sc["lines"]]
    starts = [sc["start"] for sc in tl[1:]]
    logo = Image.open(TX + "ui/hm_logo.png").convert("RGBA"); logo = logo.resize((1100, int(1100 * logo.height / logo.width)), Image.LANCZOS)
    frames = range(nf) if preview is None else preview
    if preview is None:
        out = f"{outdir}/Horizon_Guia_Ep{n:02d}.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fi in frames:
        t = fi / FPS
        cur = tl[0]
        for sc in tl:
            if t >= sc["start"]: cur = sc
        fondo = cur["fondo"] if t >= INTRO else "normal"
        img = R.bg(fondo).copy()
        R.draw_stars(img, t)
        if t < INTRO:
            k = ease(t / 0.8)
            img.alpha_composite(logo, ((W - logo.width) // 2 + 180, int(60 - 200 * (1 - k))))
            if t > 0.6:
                a = min(1, (t - 0.6) / 0.6)
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
                cx = W // 2 + 180
                R.text_shadow(dl, (cx - F_MED.getlength(f"Episodio {n}") / 2, 470), f"Episodio {n}", F_MED, GOLD)
                tl2 = R.wrap(ep["titulo"], F_BIG, 1250)
                for i, l2 in enumerate(tl2): R.text_shadow(dl, (cx - F_BIG.getlength(l2) / 2, 545 + i * 120), l2, F_BIG, PINK, off=5)
                yy = 560 + len(tl2) * 120
                R.text_shadow(dl, (cx - R.F_BUL.getlength(ep["sub"]) / 2, yy), ep["sub"], R.F_BUL, WHITE)
                R.text_shadow(dl, (cx - F_TAG.getlength("con Yei") / 2, yy + 70), "con Yei", F_TAG, GOLD)
                img.alpha_composite(with_alpha(lay, a))
            # Yei entra caminando de lado y se voltea al frente
            if t < 1.2:
                k = ease_back(t / 1.2); x0 = int(-450 + 510 * k); hop = -abs(math.sin(t * 7.5)) * 40 * (1 - t / 1.2)
                R.draw_avatar(img, t, 0, x0=x0, y0=int(70 + hop))
            else:
                R.draw_avatar(img, t, 0)
            draw_fx(img, "estrellas", t, t)
        else:
            tin = t - cur["start"]
            curl = None
            for ln in cur["lines"]:
                if ln["start"] <= t: curl = ln
            p = cur["base"].copy()
            first = cur["lines"][0]["start"]
            if t < first:                                   # tarjeta de título de la escena
                p.alpha_composite(title_card(cur, t, tin))
            elif curl is not None:
                dt = t - curl["start"]
                vis = render_vis(curl["vis"], t, dt)
                if vis is not None: p.alpha_composite(vis, (VX, VY - 10))
                if curl["bul"]:
                    cap = caption(curl["bul"]); k = ease_back((dt - 0.2) / 0.45)
                    if k > 0: paste_c(p, scaled(cap, max(0.05, k)), PW / 2, PH - 48)
            # entrada de la pizarra en cada escena: barrido
            if tin < 0.45:
                k = ease(tin / 0.45)
                p = with_alpha(p, k)
                img.alpha_composite(p, (int(PX + 120 * (1 - k)), PY))
            else:
                img.alpha_composite(p, (PX, PY))
            # subtítulo karaoke
            for ln in cur["lines"]:
                if ln["start"] <= t < ln["start"] + ln["dur"] + 0.25:
                    st, du, txt = [s for s in ln["subs"] if s[0] <= t][-1]
                    si = sub_karaoke(txt, min(1, (t - st) / max(0.1, du)))
                    img.alpha_composite(si, (SXY[0], SXY[1] + (SXY[3] - si.height) // 2))
            lvl = int(lv[fi]) if fi < len(lv) else 0
            draw_yei(img, t, lvl, allines, starts)
            img.alpha_composite(R.NAMEPLATE, (R.AV_CX - 115, 1000))
            if curl is not None: draw_fx(img, curl["fx"], t, t - curl["start"])
            # temblor de cámara
            if curl is not None and curl["fx"] == "temblor" and t - curl["start"] < 0.7:
                a = (1 - (t - curl["start"]) / 0.7) * 14
                img = ImageChops.offset(img, int(math.sin(t * 90) * a), int(math.cos(t * 77) * a))
            # barrido rosa entre escenas
            for st in starts:
                dd = t - st
                if -0.35 < dd < 0.35:
                    k = (dd + 0.35) / 0.7
                    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
                    xx = -900 + k * (W + 1800)
                    dl.polygon([(xx - 500, 0), (xx + 300, 0), (xx + 500, H), (xx - 300, H)], fill=(255, 140, 225, 235))
                    dl.polygon([(xx - 620, 0), (xx - 520, 0), (xx - 320, H), (xx - 420, H)], fill=(255, 210, 90, 235))
                    img.alpha_composite(lay)
            end = tl[-1]["end"]
            if t > end:
                a = min(1, (t - end) / 1.0)
                img.alpha_composite(Image.new("RGBA", (W, H), (12, 4, 30, int(235 * a))))
                img.alpha_composite(with_alpha(logo, a), ((W - logo.width) // 2, 200))
                d = ImageDraw.Draw(img)
                msg = "¡Gracias por ver!" if n == len(EPISODIOS) else f"Próximo: Episodio {n + 1} · " + [e for e in EPISODIOS if e["n"] == n + 1][0]["titulo"]
                d.text(((W - F_MED.getlength(msg)) / 2, 680), msg, font=F_MED, fill=tuple(int(c * a) for c in PINK))
                draw_fx(img, "estrellas", t, t - end)
        if preview is None: ff.stdin.write(img.convert("RGB").tobytes())
        else: img.convert("RGB").save(f"{outdir}/v2_{n}_{fi}.png")
    if preview is None:
        ff.stdin.close(); ff.wait(); os.remove(wav)
        print("listo", out, round(total, 1), "s", flush=True)

if __name__ == "__main__":
    n = int(sys.argv[1]); outdir = sys.argv[2]
    prev = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    os.makedirs(outdir, exist_ok=True)
    render(n, outdir, prev)
