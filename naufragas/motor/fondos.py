"""Fondos 2D dibujados por código + capas animadas (olas, nubes, estrellas, fuego, lluvia...)."""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1280, 720
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache", "fondos")
os.makedirs(CACHE, exist_ok=True)

PAL = {
    "dia": dict(cielo=((80, 160, 235), (200, 235, 252)), mar=((60, 185, 215), (25, 120, 180)),
                arena=((245, 225, 175), (225, 195, 140)), astro="sol", tinte=(1, 1, 1)),
    "atardecer": dict(cielo=((80, 60, 135), (255, 160, 95)), mar=((235, 140, 110), (80, 70, 120)),
                      arena=((225, 170, 130), (170, 115, 100)), astro="sol_bajo", tinte=(1.0, 0.86, 0.78)),
    "amanecer": dict(cielo=((110, 140, 210), (255, 200, 150)), mar=((230, 170, 150), (70, 110, 160)),
                     arena=((235, 200, 160), (190, 150, 125)), astro="sol_bajo", tinte=(1.0, 0.92, 0.85)),
    "noche": dict(cielo=((8, 12, 35), (40, 52, 95)), mar=((35, 55, 95), (12, 22, 50)),
                  arena=((85, 85, 110), (55, 55, 80)), astro="luna", tinte=(0.55, 0.6, 0.85)),
    "tormenta": dict(cielo=((40, 44, 55), (95, 100, 112)), mar=((70, 88, 95), (30, 45, 55)),
                     arena=((140, 130, 112), (100, 95, 85)), astro=None, tinte=(0.68, 0.7, 0.78)),
}


_sky = [None]


def sky_snapshot(img):
    _sky[0] = img.copy()


def grad(c1, c2, w, h):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(c1, float)[None, None, :]
    b = np.array(c2, float)[None, None, :]
    g = a * (1 - t) + b * t
    return Image.fromarray(np.repeat(g, w, axis=1).astype(np.uint8))


def ridge(x0, x1, base, amp, seed, step=8):
    rnd = random.Random(seed)
    ph = [rnd.random() * 6.28 for _ in range(4)]
    pts = []
    for x in range(x0, x1 + step, step):
        y = base - amp * (0.5 * math.sin(x / 140 + ph[0]) + 0.3 * math.sin(x / 61 + ph[1])
                          + 0.15 * math.sin(x / 23 + ph[2]) + 0.05 * math.sin(x / 9 + ph[3]))
        pts.append((x, y))
    return pts


def glow(img, x, y, r, color, alpha=160):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(10, 0, -1):
        rr = r * k / 10
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color + (int(alpha * (1 - k / 11) ** 2),))
    lay = lay.filter(ImageFilter.GaussianBlur(r / 6))
    img.alpha_composite(lay)


def palm(img, bx, by, h, lean, s=1.0, trunk=(120, 85, 55), leaf=(40, 130, 60), seed=0):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((bx + lean * t * t, by - h * t))
    for i in range(20):
        w = (22 - 10 * i / 20) * s
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        d.line([(x0, y0), (x1, y1)], fill=trunk, width=int(w))
        if i % 2 == 0:
            d.line([(x0 - w / 2, y0), (x0 + w / 2, y0 - 3)], fill=tuple(max(0, c - 35) for c in trunk), width=2)
    tx, ty = pts[-1]
    dark = tuple(max(0, c - 30) for c in leaf)
    for k in range(8):
        ang = -math.pi / 2 + (k - 3.5) * 0.48 + rnd.uniform(-0.12, 0.12)
        length = h * rnd.uniform(0.42, 0.55)
        droop = rnd.uniform(0.6, 1.1)
        spine = []
        for j in range(16):
            t = j / 15
            x = tx + math.cos(ang) * length * t
            y = ty + math.sin(ang) * length * t + droop * (length * t) ** 2 / (length * 0.9)
            spine.append((x, y))
        left, right = [], []
        for j, (x, y) in enumerate(spine):
            wdt = 18 * s * math.sin(math.pi * min(1, j / 15 + 0.05))
            if j < 15:
                nx, ny = spine[j + 1]
            else:
                nx, ny = x + (x - spine[j - 1][0]), y + (y - spine[j - 1][1])
            dx, dy = nx - x, ny - y
            ln = math.hypot(dx, dy) + 1e-6
            px, py = -dy / ln, dx / ln
            left.append((x + px * wdt, y + py * wdt))
            right.append((x - px * wdt * 0.6, y - py * wdt * 0.6))
        d.polygon(left + right[::-1], fill=leaf if k % 2 else dark)
        d.line(spine, fill=dark, width=max(1, int(3 * s)))
    for k in range(3):
        d.ellipse((tx - 12 + k * 9, ty + 2, tx + k * 9, ty + 14), fill=(90, 65, 35))


def cloud_sprite(seed, w=260, h=110, color=(255, 255, 255), alpha=220):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(9):
        cx = rnd.uniform(w * 0.2, w * 0.8)
        cy = rnd.uniform(h * 0.42, h * 0.55)
        r = rnd.uniform(h * 0.2, h * 0.34)
        d.ellipse((cx - r * 1.3, cy - r, cx + r * 1.3, cy + r), fill=color + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(5))


def rocks(d, items, col):
    for (x, y, r) in items:
        d.ellipse((x - r * 1.4, y - r, x + r * 1.4, y + r * 0.6), fill=col)
        d.ellipse((x - r * 0.9, y - r * 0.9, x + r * 0.3, y - r * 0.2), fill=tuple(min(255, c + 25) for c in col))


def tint(col, k):
    return tuple(int(c * k[i % 3]) for i, c in enumerate(col))


# ---------------------------------------------------------------- escenas
def playa(p, extra=None):
    P = PAL[p]
    img = grad(*P["cielo"], W, 330).convert("RGBA")
    full = Image.new("RGBA", (W, H))
    full.paste(img, (0, 0))
    img = full
    d = ImageDraw.Draw(img)
    if P["astro"] == "sol":
        glow(img, 980, 110, 160, (255, 250, 210), 200)
        d.ellipse((945, 75, 1015, 145), fill=(255, 252, 225))
    elif P["astro"] == "sol_bajo":
        glow(img, 640, 330, 260, (255, 190, 120), 230)
        d.ellipse((590, 280, 690, 380), fill=(255, 220, 150))
    elif P["astro"] == "luna":
        glow(img, 960, 120, 120, (200, 210, 255), 150)
        d.ellipse((925, 85, 995, 155), fill=(235, 238, 255))
        d.ellipse((945, 100, 960, 115), fill=(210, 214, 235))
        d.ellipse((965, 125, 985, 140), fill=(215, 218, 238))
        rnd = random.Random(3)
        for _ in range(160):
            x, y = rnd.randrange(W), rnd.randrange(300)
            b = rnd.randint(120, 255)
            d.point((x, y), fill=(b, b, b))
    sky_snapshot(img)
    # isla lejana
    isl = [(x, min(330, y)) for x, y in ridge(40, 560, 318, 22, 7)]
    d.polygon([(40, 330)] + isl + [(560, 330)], fill=tint((60, 110, 120), P["tinte"]))
    # mar
    sea = grad(*P["mar"], W, 150).convert("RGBA")
    img.alpha_composite(sea, (0, 330))
    rnd = random.Random(5)
    for _ in range(70):
        x, y = rnd.randrange(W), rnd.randrange(335, 470)
        ln = rnd.randint(10, 50)
        c = tuple(min(255, v + 50) for v in P["mar"][0])
        d.line([(x, y), (x + ln, y)], fill=c + (150,), width=2)
    if P["astro"] == "sol_bajo":
        for k in range(14):
            y = 335 + k * 9
            w = 90 - k * 3 + rnd.randint(-10, 10)
            d.line([(640 - w, y), (640 + w, y)], fill=(255, 210, 150, 170), width=3)
    # arena
    sand = grad(*P["arena"], W, H - 455).convert("RGBA")
    img.alpha_composite(sand, (0, 455))
    shore = ridge(0, W, 462, 10, 11)
    d.polygon(shore + [(W, 480), (0, 480)], fill=tint((205, 185, 140), P["tinte"]) + (255,))
    rnd = random.Random(9)
    for _ in range(900):
        x, y = rnd.randrange(W), rnd.randrange(480, H)
        c = tint((200, 175, 130), P["tinte"])
        d.point((x, y), fill=c)
    rocks(d, [(140, 560, 30), (1150, 600, 40), (1210, 585, 22)], tint((120, 110, 100), P["tinte"]))
    leaf = tint((40, 130, 60), P["tinte"])
    trunk = tint((125, 88, 58), P["tinte"])
    palm(img, 90, 640, 470, 120, 1.2, trunk, leaf, 1)
    palm(img, 1200, 660, 420, -110, 1.1, trunk, leaf, 2)
    palm(img, 1100, 560, 260, -50, 0.7, trunk, tint((50, 140, 70), P["tinte"]), 3)
    meta = dict(tinte=P["tinte"], olas=465, nubes=(P["astro"] != "luna"), estrellas=(P["astro"] == "luna"),
                nube_color=(70, 75, 85) if p == "tormenta" else (255, 230, 220) if p in ("atardecer", "amanecer") else (255, 255, 255))
    if extra == "campamento":
        campamento(img, P)
        meta["fuego"] = (430, 590, 1.0)
    return img, meta


def campamento(img, P):
    d = ImageDraw.Draw(img)
    k = P["tinte"]
    # refugio de palos y hojas
    wood = tint((110, 78, 50), k)
    d.line([(800, 600), (900, 420)], fill=wood, width=12)
    d.line([(1040, 600), (920, 420)], fill=wood, width=12)
    d.line([(880, 425), (1110, 470)], fill=wood, width=10)
    d.polygon([(900, 420), (1110, 468), (1150, 610), (800, 610)], fill=tint((60, 120, 55), k))
    for i in range(10):
        x = 820 + i * 33
        d.polygon([(x, 610), (x + 30, 610), (x + 50 - i * 2, 460 + i * 4)], fill=tint((45, 105 + i * 4, 50), k))
    d.polygon([(900, 470), (1000, 470), (1030, 610), (870, 610)], fill=tint((30, 40, 30), k))
    # hoguera: piedras y troncos
    rocks(d, [(370 + i * 30, 615 + (i % 2) * 4, 13) for i in range(5)], tint((120, 115, 110), k))
    d.line([(380, 605), (480, 585)], fill=tint((90, 60, 40), k), width=12)
    d.line([(380, 585), (480, 605)], fill=tint((100, 66, 44), k), width=12)


def selva(p="dia", claro=False):
    k = {"dia": (0.95, 1.0, 0.95), "noche": (0.45, 0.5, 0.7), "atardecer": (1.0, 0.85, 0.75)}.get(p, (1, 1, 1))
    img = grad(tint((150, 205, 160), k), tint((60, 120, 70), k), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    rnd = random.Random(21)
    for layer, (col, n, r) in enumerate([((70, 130, 80), 18, 120), ((45, 105, 60), 14, 100), ((30, 80, 45), 10, 90)]):
        for _ in range(n):
            x = rnd.randrange(-50, W + 50)
            y = rnd.randrange(50, 380) + layer * 40
            d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=tint(col, k))
        for _ in range(5 + layer * 2):
            x = rnd.randrange(0, W)
            w = 12 + layer * 10
            d.rectangle((x, 100 + layer * 60, x + w, H), fill=tint((70 - layer * 10, 50, 35), k))
    # rayos de luz
    if p == "dia":
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for x in (300, 560, 820):
            ld.polygon([(x, 0), (x + 70, 0), (x + 260, H), (x + 120, H)], fill=(255, 255, 200, 40))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
    # suelo y camino
    d.polygon(ridge(0, W, 560, 15, 4) + [(W, H), (0, H)], fill=tint((75, 95, 50), k))
    d.polygon([(560, 560), (720, 560), (900, H), (380, H)], fill=tint((140, 115, 80), k))
    if claro:
        d.polygon(ridge(0, W, 545, 10, 8) + [(W, H), (0, H)], fill=tint((110, 120, 70), k))
    # hojas grandes en primer plano
    for (x, y, a, s) in [(40, 680, -0.6, 1.6), (130, 720, -0.2, 1.3), (1230, 690, 3.6, 1.5), (1150, 730, 3.3, 1.2), (-20, 300, 0.2, 1.2), (1300, 260, 3.0, 1.2)]:
        L = 220 * s
        pts = []
        for j in range(20):
            t = j / 19
            pts.append((x + math.cos(a) * L * t, y + math.sin(a) * L * t - 40 * s * math.sin(math.pi * t)))
        top = [(px, py - 40 * s * math.sin(math.pi * j / 19)) for j, (px, py) in enumerate(pts)]
        bot = [(px, py + 40 * s * math.sin(math.pi * j / 19)) for j, (px, py) in enumerate(pts)]
        d.polygon(top + bot[::-1], fill=tint((35, 115, 50), k))
        d.line(pts, fill=tint((25, 80, 35), k), width=4)
    # lianas
    for x in (220, 470, 1010):
        d.line([(x + 10 * math.sin(y / 40), y) for y in range(0, 330, 10)], fill=tint((50, 90, 40), k), width=5)
    tinte = {"dia": (0.92, 1.0, 0.92), "noche": (0.5, 0.55, 0.8), "atardecer": (1.0, 0.85, 0.78)}[p]
    return img, dict(tinte=tinte, luciernagas=(p == "noche"))


def cabana(p="dia"):
    img, meta = selva(p, claro=True)
    d = ImageDraw.Draw(img)
    k = {"dia": (1, 1, 1), "noche": (0.5, 0.55, 0.75), "atardecer": (1, 0.85, 0.75)}[p]
    wood = tint((125, 90, 60), k)
    for i in range(9):
        x = 700 + i * 46
        d.rectangle((x, 330, x + 42, 560), fill=tint((115 + (i % 3) * 10, 82, 55), k), outline=tint((70, 50, 30), k), width=2)
    d.polygon([(660, 340), (930, 190), (1160, 340)], fill=tint((150, 130, 70), k))
    for i in range(14):
        d.line([(680 + i * 34, 335), (930, 195)], fill=tint((120, 100, 55), k), width=2)
    d.rectangle((880, 400, 960, 560), fill=tint((40, 30, 25), k))
    d.rectangle((760, 380, 830, 440), fill=tint((50, 45, 40), k), outline=wood, width=4)
    d.line([(1080, 560), (1120, 470)], fill=wood, width=6)
    meta["tinte"] = {"dia": (0.95, 1, 0.95), "noche": (0.5, 0.55, 0.8), "atardecer": (1, 0.86, 0.78)}[p]
    return img, meta


def cascada():
    img, meta = selva("dia")
    d = ImageDraw.Draw(img)
    d.polygon([(380, 0), (560, 0), (560, 470), (330, 520)], fill=(95, 100, 95))
    d.polygon([(720, 0), (900, 0), (950, 520), (720, 470)], fill=(90, 95, 92))
    for i in range(30):
        x = random.Random(i).randrange(330, 950)
        y = random.Random(i + 99).randrange(0, 480)
        if 560 < x < 720:
            continue
        d.line([(x, y), (x + 20, y + 30)], fill=(75, 80, 75), width=3)
    d.rectangle((560, 0, 720, 480), fill=(185, 225, 240))
    d.ellipse((300, 450, 980, 610), fill=(70, 160, 190))
    d.ellipse((360, 470, 920, 590), fill=(95, 185, 210))
    glow(img, 640, 480, 160, (255, 255, 255), 120)
    meta.update(cascada=(560, 720, 0, 480))
    return img, meta


def cueva(simbolos=False):
    img = Image.new("RGBA", (W, H), (25, 24, 30, 255))
    d = ImageDraw.Draw(img)
    # boca de luz al fondo
    glow(img, 640, 300, 240, (150, 190, 230), 170)
    d.polygon([(520, 420), (560, 230), (640, 190), (730, 240), (770, 420)], fill=(150, 185, 215))
    # paredes
    rnd = random.Random(31)
    for layer, col in enumerate([(60, 58, 70), (45, 43, 52), (32, 30, 38)]):
        left = [(0, 0)] + [(380 - layer * 90 + rnd.randint(-40, 40), y) for y in range(0, H + 60, 60)] + [(0, H)]
        right = [(W, 0)] + [(900 + layer * 90 + rnd.randint(-40, 40), y) for y in range(0, H + 60, 60)] + [(W, H)]
        d.polygon(left, fill=col)
        d.polygon(right, fill=col)
        top = [(0, 0)] + [(x, 120 - layer * 30 + rnd.randint(-30, 30)) for x in range(0, W + 80, 80)] + [(W, 0)]
        d.polygon(top, fill=col)
    for x in range(420, 880, 55):
        ln = rnd.randint(30, 90)
        d.polygon([(x, 80), (x + 18, 80), (x + 9, 80 + ln)], fill=(55, 52, 62))
    d.polygon(ridge(0, W, 520, 12, 3) + [(W, H), (0, H)], fill=(50, 47, 55))
    d.ellipse((500, 560, 820, 620), fill=(40, 60, 80))
    if simbolos:
        for (cx, cy, r) in [(190, 300, 55), (1090, 280, 60), (250, 470, 35)]:
            rosa(img, cx, cy, r)
    return img, dict(tinte=(0.62, 0.62, 0.75), gotas=True, simbolos=simbolos)


def rosa(img, cx, cy, r, col=(170, 120, 255)):
    glow(img, cx, cy, r * 1.8, col, 120)
    d = ImageDraw.Draw(img)
    for k in range(6):
        a = k * math.pi / 3
        x, y = cx + math.cos(a) * r * 0.5, cy + math.sin(a) * r * 0.5
        d.ellipse((x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45), outline=col + (255,), width=3)
    d.ellipse((cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3), outline=(230, 210, 255, 255), width=3)


def cumbre(p="dia"):
    P = PAL["amanecer" if p == "amanecer" else p]
    img = grad(*P["cielo"], W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    if p == "amanecer":
        glow(img, 980, 420, 260, (255, 200, 130), 230)
        d.ellipse((930, 370, 1030, 470), fill=(255, 225, 160))
    elif p == "noche":
        rnd = random.Random(4)
        for _ in range(220):
            b = rnd.randint(120, 255)
            d.point((rnd.randrange(W), rnd.randrange(420)), fill=(b, b, b))
        d.ellipse((200, 90, 260, 150), fill=(235, 238, 255))
    else:
        glow(img, 200, 120, 140, (255, 250, 210), 200)
    sky_snapshot(img)
    sea = grad(*P["mar"], W, 120).convert("RGBA")
    img.alpha_composite(sea, (0, 430))
    d.polygon(ridge(0, W, 470, 30, 41) + [(W, H), (0, H)], fill=tint((60, 110, 70), P["tinte"]))
    d.polygon(ridge(0, W, 560, 25, 42) + [(W, H), (0, H)], fill=tint((110, 100, 90), P["tinte"]))
    rocks(d, [(150, 650, 50), (1130, 640, 60), (1000, 690, 30)], tint((90, 85, 80), P["tinte"]))
    # pila de leña para la señal
    for i in range(6):
        d.line([(900 + i * 14, 600), (960, 520)], fill=tint((110, 80, 50), P["tinte"]), width=8)
        d.line([(1020 - i * 14, 600), (960, 520)], fill=tint((100, 72, 46), P["tinte"]), width=8)
    meta = dict(tinte=P["tinte"], nubes=(p != "noche"), estrellas=(p == "noche"),
                nube_color=(255, 225, 210) if p == "amanecer" else (255, 255, 255))
    return img, meta


def cubierta():
    P = PAL["dia"]
    img = grad(*P["cielo"], W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    glow(img, 1050, 100, 140, (255, 250, 210), 200)
    sky_snapshot(img)
    img.alpha_composite(grad(*P["mar"], W, 200).convert("RGBA"), (0, 360))
    d.polygon(ridge(60, 300, 362, 25, 5) + [(300, 362), (60, 362)], fill=(70, 130, 110))
    d.rectangle((0, 540, W, H), fill=(175, 130, 90))
    for y in range(550, H, 26):
        d.line([(0, y), (W, y)], fill=(150, 108, 72), width=2)
    for x in range(0, W, 120):
        d.line([(x, 540), (x, 420)], fill=(245, 245, 245), width=7)
    for y in (420, 470, 520):
        d.line([(0, y), (W, y)], fill=(250, 250, 250), width=6)
    d.ellipse((1080, 430, 1180, 530), outline=(235, 70, 60), width=16)
    d.rectangle((0, 0, 70, 540), fill=(240, 240, 245))
    return img, dict(tinte=(1, 1, 1), nubes=True, nube_color=(255, 255, 255), olas_barco=True)


def jardin():
    P = PAL["atardecer"]
    img = grad(*P["cielo"], W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    glow(img, 1000, 300, 220, (255, 190, 120), 220)
    sky_snapshot(img)
    d.polygon(ridge(0, W, 430, 30, 77) + [(W, H), (0, H)], fill=(110, 140, 80))
    # casa
    d.rectangle((760, 240, 1180, 470), fill=(235, 215, 190))
    d.polygon([(730, 250), (970, 120), (1210, 250)], fill=(170, 80, 70))
    d.rectangle((930, 350, 1010, 470), fill=(120, 80, 60))
    for x in (800, 1060):
        d.rectangle((x, 300, x + 80, 370), fill=(255, 220, 150), outline=(255, 255, 255), width=5)
    d.rectangle((0, 500, W, H), fill=(95, 135, 70))
    for x in range(0, W, 40):
        d.rectangle((x, 470, x + 14, 560), fill=(245, 240, 230))
    d.line([(0, 490), (W, 490)], fill=(245, 240, 230), width=8)
    d.line([(0, 540), (W, 540)], fill=(245, 240, 230), width=8)
    rnd = random.Random(8)
    for _ in range(140):
        x, y = rnd.randrange(W), rnd.randrange(570, H)
        c = rnd.choice([(240, 90, 120), (255, 210, 80), (200, 120, 255), (255, 255, 255)])
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=c)
    palm(img, 120, 600, 400, 60, 1.0, (120, 90, 60), (60, 130, 60), 9)
    return img, dict(tinte=(1, 0.88, 0.8), nubes=True, nube_color=(255, 220, 210), petalos=True)


def negro():
    return Image.new("RGBA", (W, H), (8, 8, 14, 255)), dict(tinte=(0.4, 0.4, 0.5))


FONDOS = {
    "playa_dia": lambda: playa("dia"),
    "playa_atardecer": lambda: playa("atardecer"),
    "playa_noche": lambda: playa("noche"),
    "playa_tormenta": lambda: playa("tormenta"),
    "playa_amanecer": lambda: playa("amanecer"),
    "campamento_dia": lambda: playa("dia", "campamento"),
    "campamento_atardecer": lambda: playa("atardecer", "campamento"),
    "campamento_noche": lambda: playa("noche", "campamento"),
    "campamento_tormenta": lambda: playa("tormenta", "campamento"),
    "selva": lambda: selva("dia"),
    "selva_atardecer": lambda: selva("atardecer"),
    "selva_noche": lambda: selva("noche"),
    "cascada": cascada,
    "cueva": lambda: cueva(False),
    "cueva_simbolos": lambda: cueva(True),
    "cabana": lambda: cabana("dia"),
    "cabana_noche": lambda: cabana("noche"),
    "cumbre": lambda: cumbre("dia"),
    "cumbre_noche": lambda: cumbre("noche"),
    "cumbre_amanecer": lambda: cumbre("amanecer"),
    "cubierta": cubierta,
    "jardin": jardin,
    "negro": negro,
}

_mem = {}


def fondo(nombre):
    if nombre in _mem:
        return _mem[nombre]
    path = os.path.join(CACHE, nombre + ".png")
    _sky[0] = None
    img, meta = FONDOS[nombre]()
    if _sky[0] is not None:
        a = np.asarray(img.convert("RGB")).astype(int)
        b = np.asarray(_sky[0].convert("RGB")).astype(int)
        m = (np.abs(a - b).sum(axis=2) < 8).astype(np.uint8) * 255
        meta["cielo"] = Image.fromarray(m).filter(ImageFilter.GaussianBlur(1))
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
    else:
        img.save(path)
    img = img.convert("RGB")
    _mem[nombre] = (img, meta)
    return img, meta


# ---------------------------------------------------------------- capas animadas
_clouds = None


def nubes(img, t, color, mask=None):
    if mask is not None:
        lay = img.copy()
        nubes(lay, t, color)
        img.paste(lay, (0, 0), mask)
        return
    global _clouds
    if _clouds is None:
        _clouds = [cloud_sprite(i) for i in range(4)]
    key = ("nubes", color)
    if key not in _mem:
        sprites = []
        for c in _clouds:
            r, g, b, a = c.split()
            col = Image.new("RGBA", c.size, color + (0,))
            col.putalpha(a)
            sprites.append(col)
        _mem[key] = sprites
    for i, c in enumerate(_mem[key]):
        x = int((i * 380 + t * (8 + i * 3)) % (W + 300)) - 280
        y = 30 + (i * 53) % 150
        img.paste(c, (x, y), c)


def olas(img, t, y0, tinte):
    d = ImageDraw.Draw(img, "RGBA")
    adv = 10 * math.sin(t * 0.8)
    col = tuple(int(255 * k) for k in tinte)
    pts = [(x, y0 + adv + 6 * math.sin(x / 50 + t * 1.6)) for x in range(0, W + 20, 20)]
    d.polygon(pts + [(W, y0 - 25), (0, y0 - 25)], fill=col + (30,))
    d.line(pts, fill=col + (170,), width=3)
    pts2 = [(x, y0 - 22 + 4 * math.sin(x / 35 - t * 2.1)) for x in range(0, W + 20, 20)]
    d.line(pts2, fill=col + (110,), width=2)


_stars = [(random.Random(i).randrange(W), random.Random(i * 7).randrange(320), random.Random(i * 3).random() * 6) for i in range(70)]


def estrellas(img, t):
    d = ImageDraw.Draw(img)
    for x, y, ph in _stars:
        b = int(150 + 105 * (0.5 + 0.5 * math.sin(t * 2.3 + ph)))
        d.point((x, y), fill=(b, b, b))
        if b > 240:
            d.point([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)], fill=(b - 60,) * 3)


_glow_cache = {}


def _glow_sprite(r, color):
    key = (r, color)
    if key not in _glow_cache:
        g = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
        glow(g, r, r, r, color, 200)
        _glow_cache[key] = g
    return _glow_cache[key]


def fuego(img, t, x, y, s=1.0):
    g = _glow_sprite(int(170 * s), (255, 150, 60))
    k = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    a = g.split()[3].point(lambda v: int(v * k))
    img.paste(g, (int(x - g.width / 2), int(y - g.height / 2) - 20), a)
    d = ImageDraw.Draw(img)
    for layer, (col, hh, ww) in enumerate([((255, 120, 30), 95, 42), ((255, 190, 60), 65, 28), ((255, 245, 190), 35, 14)]):
        pts = []
        n = 9
        for i in range(n + 1):
            u = i / n
            ang = math.pi * u
            rr = ww * s * (0.8 + 0.2 * math.sin(t * 17 + i * 1.7 + layer))
            hx = x + math.cos(ang) * rr
            hy = y - math.sin(ang) * rr * 0.4
            pts.append((hx, hy))
        tip = (x + 8 * math.sin(t * 9 + layer), y - hh * s * (0.85 + 0.2 * math.sin(t * 11 + layer * 2)))
        d.polygon([pts[0], (x + ww * s * 0.6, y - hh * s * 0.45), tip, (x - ww * s * 0.6, y - hh * s * 0.5), pts[-1]] + pts[::-1], fill=col)
    for i in range(4):
        ph = (t * 1.3 + i * 0.27) % 1
        sx = x + 25 * math.sin(i * 2.1 + t * 3) * s
        sy = y - 60 * s - ph * 140 * s
        d.ellipse((sx - 2, sy - 2, sx + 2, sy + 2), fill=(255, 200, 90))


def lluvia(img, t, fuerte=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(int(t * 24))
    for _ in range(int(220 * fuerte)):
        x, y = rnd.randrange(-100, W), rnd.randrange(-40, H)
        d.line([(x, y), (x + 12, y + 34)], fill=(210, 220, 240, 120), width=2)


def cascada_anim(img, t, box):
    x0, x1, y0, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(14):
        x = x0 + 8 + i * (x1 - x0 - 16) / 13
        off = (t * 260 + i * 53) % 120
        for y in range(int(y0 - 120 + off), y1, 120):
            d.line([(x, y), (x, y + 60)], fill=(255, 255, 255, 140), width=4)
    for i in range(10):
        ph = (t * 0.7 + i * 0.1) % 1
        r = 20 + ph * 70
        cx = x0 + (x1 - x0) / 2 + (i - 5) * 18
        d.ellipse((cx - r, y1 - r * 0.3, cx + r, y1 + r * 0.3), outline=(255, 255, 255, int(150 * (1 - ph))), width=3)


def luciernagas(img, t):
    d = ImageDraw.Draw(img)
    for i in range(18):
        x = (i * 173 + 40 * math.sin(t * 0.6 + i)) % W
        y = 250 + (i * 97) % 350 + 25 * math.sin(t * 0.9 + i * 2)
        b = 0.5 + 0.5 * math.sin(t * 3 + i)
        if b > 0.3:
            r = 2 + 2 * b
            d.ellipse((x - r, y - r, x + r, y + r), fill=(int(200 + 55 * b), 255, int(120 * b)))


def gotas(img, t):
    d = ImageDraw.Draw(img)
    for i in range(5):
        ph = (t * 0.5 + i * 0.37) % 1
        x = 430 + i * 95
        y = 110 + ph * 450
        d.ellipse((x - 2, y - 4, x + 2, y + 4), fill=(170, 200, 230))


def petalos(img, t):
    d = ImageDraw.Draw(img)
    for i in range(16):
        x = (i * 97 + t * 40 + 30 * math.sin(t + i)) % W
        y = (i * 61 + t * 55) % H
        d.ellipse((x - 4, y - 2, x + 4, y + 2), fill=(255, 190, 210))


def barco_lejano(img, t, t0, tinte):
    x = 300 + (t - t0) * 9
    y = 322
    col = tuple(int(c * k) for c, k in zip((60, 60, 70), tinte))
    d = ImageDraw.Draw(img)
    d.polygon([(x, y), (x + 70, y), (x + 60, y + 9), (x + 8, y + 9)], fill=col)
    d.rectangle((x + 20, y - 12, x + 48, y), fill=col)
    d.rectangle((x + 30, y - 22, x + 36, y - 12), fill=col)
