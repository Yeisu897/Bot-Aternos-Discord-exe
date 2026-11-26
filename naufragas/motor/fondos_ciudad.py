"""Fondos de ciudad para "Las 3 Chifladas": departamento, cocina, cuarto, calle, parque, café, súper, aula, piscina, feria."""
import math
import random

import os

from PIL import Image, ImageDraw, ImageFont

import fondos as F
from fondos import W, H, grad, glow, ridge, tint, sky_snapshot

NOCHE = (0.62, 0.62, 0.82)
_FT = lambda n: ImageFont.truetype(os.path.join(F.ROOT, "assets", "fonts", "ComicNeue-Bold.otf"), n)  # noqa: E731


def _ventana(img, box, noche=False):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    sky = grad((20, 25, 60), (60, 60, 110), x1 - x0, y1 - y0) if noche else grad((110, 180, 240), (200, 230, 250), x1 - x0, y1 - y0)
    img.paste(sky, (x0, y0))
    rnd = random.Random(x0)
    for i in range(6):
        bx = x0 + i * (x1 - x0) // 6
        bh = rnd.randint(40, (y1 - y0) - 20)
        col = (30, 30, 50) if noche else (140, 160, 190)
        d.rectangle((bx, y1 - bh, bx + (x1 - x0) // 6 - 4, y1), fill=col)
        for wy in range(y1 - bh + 8, y1 - 6, 14):
            for wx in range(bx + 5, bx + (x1 - x0) // 6 - 8, 12):
                if rnd.random() < (0.5 if noche else 0.25):
                    d.rectangle((wx, wy, wx + 5, wy + 6), fill=(255, 220, 120) if noche else (210, 230, 250))
    if noche:
        d.ellipse((x1 - 70, y0 + 20, x1 - 35, y0 + 55), fill=(240, 240, 255))
    d.rectangle(box, outline=(250, 250, 250), width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=(250, 250, 250), width=8)


def sala(noche=False):
    k = NOCHE if noche else (1, 1, 1)
    img = grad(tint((250, 228, 200), k), tint((235, 205, 175), k), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    _ventana(img, (760, 90, 1160, 360), noche)
    d.rectangle((0, 520, W, H), fill=tint((170, 120, 80), k))
    for y in range(530, H, 28):
        d.line([(0, y), (W, y)], fill=tint((150, 104, 68), k), width=2)
    d.ellipse((260, 590, 1020, 700), fill=tint((200, 90, 100), k))
    # sofá
    d.rounded_rectangle((140, 390, 640, 560), 30, fill=tint((90, 120, 170), k))
    d.rounded_rectangle((120, 440, 200, 570), 20, fill=tint((75, 100, 150), k))
    d.rounded_rectangle((580, 440, 660, 570), 20, fill=tint((75, 100, 150), k))
    for x in (230, 380):
        d.rounded_rectangle((x, 410, x + 130, 470), 20, fill=tint((240, 200, 90), k) if x == 230 else tint((230, 120, 160), k))
    # cuadro de la isla
    d.rectangle((300, 140, 500, 280), fill=(255, 255, 255), outline=tint((120, 80, 50), k), width=8)
    d.rectangle((312, 152, 488, 268), fill=tint((110, 190, 230), k))
    d.polygon([(330, 268), (400, 200), (470, 268)], fill=tint((60, 150, 80), k))
    d.ellipse((440, 165, 470, 195), fill=tint((255, 230, 120), k))
    # tele y planta
    d.rectangle((900, 440, 1180, 540), fill=tint((110, 80, 55), k))
    d.rectangle((930, 370, 1150, 445), fill=(25, 25, 35))
    d.rectangle((40, 470, 100, 560), fill=tint((200, 110, 70), k))
    for i in range(7):
        a = -math.pi / 2 + (i - 3) * 0.35
        d.line([(70, 470), (70 + math.cos(a) * 90, 470 + math.sin(a) * 110)], fill=tint((50, 140, 70), k), width=12)
    if noche:
        glow(img, 690, 330, 160, (255, 210, 140), 160)
        d.line([(690, 330), (690, 560)], fill=(60, 60, 60), width=6)
        d.polygon([(650, 300), (730, 300), (710, 340), (670, 340)], fill=(255, 225, 160))
    return img, dict(tinte=(0.85, 0.78, 0.8) if noche else (1, 1, 1))


def cocina():
    img = grad((235, 245, 240), (215, 230, 225), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):
        for y in range(250, 420, 40):
            d.rectangle((x + 1, y + 1, x + 39, y + 39), outline=(200, 215, 210), width=2)
    _ventana(img, (480, 80, 800, 260))
    d.rectangle((0, 420, W, 560), fill=(240, 240, 235))
    d.rectangle((0, 410, W, 430), fill=(180, 160, 140))
    for x in range(20, W, 210):
        d.rectangle((x, 440, x + 190, 550), outline=(200, 200, 195), width=4)
        d.ellipse((x + 85, 485, x + 105, 505), fill=(170, 170, 170))
    for x in range(20, 460, 150):
        d.rectangle((x, 60, x + 130, 200), fill=(250, 250, 245), outline=(200, 200, 195), width=4)
    d.rectangle((900, 300, 1060, 420), fill=(60, 60, 65))
    for cx in (940, 1020):
        d.ellipse((cx - 25, 330, cx + 25, 360), outline=(150, 150, 150), width=5)
    d.ellipse((925, 290, 985, 330), fill=(200, 60, 50))
    d.rectangle((1110, 120, 1260, 560), fill=(245, 245, 250), outline=(190, 190, 200), width=4)
    d.line([(1110, 300), (1260, 300)], fill=(190, 190, 200), width=4)
    d.rectangle((0, 560, W, H), fill=(200, 190, 170))
    return img, dict(tinte=(1, 1, 1))


def cuarto_noche():
    k = NOCHE
    img = grad(tint((200, 190, 240), k), tint((170, 160, 210), k), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    _ventana(img, (520, 80, 760, 300), True)
    d.rectangle((0, 540, W, H), fill=tint((140, 110, 90), k))
    for x0, col in ((40, (230, 120, 150)), (930, (110, 200, 170))):
        d.rectangle((x0, 430, x0 + 310, 560), fill=tint((140, 100, 70), k))
        d.rounded_rectangle((x0 + 10, 400, x0 + 300, 470), 20, fill=tint(col, k))
        d.rounded_rectangle((x0 + 20, 380, x0 + 110, 420), 15, fill=tint((250, 250, 250), k))
    d.rectangle((380, 150, 480, 280), fill=tint((120, 200, 255), k))
    d.rectangle((820, 140, 900, 250), fill=tint((240, 200, 90), k))
    rnd = random.Random(2)
    for _ in range(20):
        x, y = rnd.randrange(W), rnd.randrange(20, 360)
        d.text((x, y), "*", fill=(255, 250, 200))
    glow(img, 640, 520, 90, (255, 200, 120), 120)
    return img, dict(tinte=(0.7, 0.68, 0.88))


def calle():
    img = grad((100, 170, 235), (200, 230, 250), W, H).convert("RGBA")
    sky_snapshot(img)
    d = ImageDraw.Draw(img)
    rnd = random.Random(12)
    x = -20
    while x < W:
        w = rnd.randint(140, 220)
        h = rnd.randint(200, 380)
        col = rnd.choice([(230, 180, 150), (200, 200, 220), (240, 220, 170), (180, 210, 200), (220, 160, 170)])
        d.rectangle((x, 520 - h, x + w, 520), fill=col)
        for wy in range(520 - h + 20, 500, 50):
            for wx in range(x + 18, x + w - 30, 45):
                d.rectangle((wx, wy, wx + 24, wy + 30), fill=(170, 210, 240), outline=(255, 255, 255), width=2)
        x += w + 6
    d.rectangle((0, 520, W, 590), fill=(200, 200, 200))
    d.rectangle((0, 590, W, H), fill=(80, 80, 90))
    for x in range(0, W, 120):
        d.rectangle((x, 650, x + 60, 660), fill=(240, 240, 240))
    for x in (180, 640, 1100):
        d.line([(x, 590), (x, 380)], fill=(60, 60, 70), width=8)
        d.ellipse((x - 20, 365, x + 20, 395), fill=(255, 240, 180))
        d.ellipse((x + 90, 420, x + 200, 530), fill=(70, 150, 80))
        d.line([(x + 145, 530), (x + 145, 590)], fill=(110, 80, 50), width=10)
    return img, dict(tinte=(1, 1, 1), nubes=True, nube_color=(255, 255, 255))


def parque():
    img = grad((110, 180, 240), (210, 235, 250), W, H).convert("RGBA")
    glow(img, 1050, 110, 130, (255, 250, 210), 200)
    sky_snapshot(img)
    d = ImageDraw.Draw(img)
    d.polygon(ridge(0, W, 420, 25, 5) + [(W, H), (0, H)], fill=(110, 180, 90))
    d.polygon([(560, 420), (720, 420), (980, H), (300, H)], fill=(220, 200, 160))
    rnd = random.Random(3)
    for x, s in ((90, 1.3), (330, 0.9), (1000, 1.1), (1200, 1.4), (820, 0.7)):
        d.line([(x, 470), (x, 470 - 140 * s)], fill=(110, 80, 50), width=int(22 * s))
        for _ in range(6):
            cx = x + rnd.randint(-70, 70) * s
            cy = 470 - 200 * s + rnd.randint(-50, 40) * s
            r = rnd.randint(55, 85) * s
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rnd.choice([(60, 140, 70), (75, 160, 80), (50, 125, 60)]))
    d.rectangle((150, 520, 420, 540), fill=(150, 100, 60))
    d.rectangle((150, 480, 420, 500), fill=(150, 100, 60))
    for x in (170, 400):
        d.line([(x, 540), (x, 580)], fill=(60, 60, 60), width=8)
    for _ in range(70):
        x, y = rnd.randrange(W), rnd.randrange(450, H)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=rnd.choice([(255, 255, 255), (255, 220, 80), (240, 120, 160)]))
    return img, dict(tinte=(1, 1, 1), nubes=True, nube_color=(255, 255, 255), petalos=False)


def cafe():
    img = grad((120, 80, 60), (160, 110, 80), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle((60, 70, 480, 300), fill=(35, 40, 35), outline=(150, 110, 70), width=10)
    for i, txt in enumerate(["CAFÉ ... 2", "TÉ ...... 2", "PASTEL .. 3", "MANGO! .. 4"]):
        d.text((90, 90 + i * 50), txt, font=_FT(36), fill=(240, 240, 230))
    for x in (600, 850, 1100):
        d.line([(x, 0), (x, 120)], fill=(40, 30, 25), width=4)
        d.polygon([(x - 50, 160), (x + 50, 160), (x + 25, 120), (x - 25, 120)], fill=(240, 170, 60))
        glow(img, x, 180, 90, (255, 210, 130), 130)
    d.rectangle((0, 400, W, 560), fill=(200, 150, 100))
    d.rectangle((0, 390, W, 410), fill=(90, 60, 40))
    d.rectangle((820, 300, 960, 395), fill=(180, 180, 190))
    d.rectangle((845, 330, 935, 390), fill=(60, 60, 70))
    for x in (600, 680):
        d.rectangle((x, 350, x + 50, 395), fill=(250, 250, 250))
    d.rectangle((0, 560, W, H), fill=(110, 75, 55))
    return img, dict(tinte=(1.0, 0.93, 0.86))


def super_():
    img = grad((245, 245, 250), (225, 228, 235), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(100, W, 360):
        d.rectangle((x, 40, x + 200, 55), fill=(255, 255, 240))
    rnd = random.Random(9)
    for sx in (0, 680):
        d.rectangle((sx, 150, sx + 600, 540), fill=(200, 205, 215))
        for sy in range(170, 540, 90):
            d.rectangle((sx, sy + 70, sx + 600, sy + 80), fill=(150, 155, 170))
            x = sx + 10
            while x < sx + 580:
                w = rnd.randint(25, 50)
                h = rnd.randint(35, 65)
                d.rectangle((x, sy + 70 - h, x + w, sy + 70), fill=rnd.choice(
                    [(230, 80, 70), (250, 200, 60), (80, 160, 220), (90, 190, 110), (240, 140, 50), (200, 100, 200)]))
                x += w + 4
    d.rectangle((0, 540, W, H), fill=(220, 220, 225))
    for x in range(0, W, 80):
        d.line([(x, 540), (x - 60, H)], fill=(200, 200, 205), width=2)
    return img, dict(tinte=(1, 1, 1))


def aula():
    img = grad((240, 235, 215), (225, 215, 195), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle((200, 80, 1080, 360), fill=(40, 80, 60), outline=(150, 110, 70), width=14)
    d.text((250, 110), "Ecosistemas insulares - Tema 1", font=_FT(44), fill=(240, 240, 230))
    d.line([(260, 170), (700, 170)], fill=(240, 240, 230), width=2)
    d.ellipse((780, 170, 980, 300), outline=(240, 240, 230), width=3)
    d.rectangle((0, 470, W, H), fill=(180, 140, 100))
    for x in range(40, W, 300):
        d.rectangle((x, 520, x + 220, 545), fill=(150, 110, 70))
        d.line([(x + 20, 545), (x + 20, 640)], fill=(80, 80, 80), width=6)
        d.line([(x + 200, 545), (x + 200, 640)], fill=(80, 80, 80), width=6)
    return img, dict(tinte=(1, 1, 1))


def piscina():
    img = grad((235, 245, 250), (210, 230, 240), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(0, W, 160):
        d.rectangle((x, 0, x + 150, 60), fill=(200, 230, 250))
    d.rectangle((0, 330, W, 560), fill=(60, 170, 220))
    for y in (380, 440, 500):
        for x in range(0, W, 30):
            d.ellipse((x, y - 5, x + 12, y + 5), fill=(250, 80, 80) if (x // 30) % 2 else (250, 250, 250))
    rnd = random.Random(4)
    for _ in range(80):
        x, y = rnd.randrange(W), rnd.randrange(340, 550)
        d.line([(x, y), (x + rnd.randint(10, 40), y)], fill=(150, 220, 250), width=2)
    d.rectangle((0, 560, W, H), fill=(230, 230, 225))
    d.rectangle((1100, 200, 1140, 560), fill=(240, 240, 240))
    d.rectangle((1060, 200, 1180, 230), fill=(250, 250, 250))
    for x in (60, 120):
        d.line([(x, 330), (x, 250)], fill=(200, 200, 210), width=6)
    return img, dict(tinte=(1, 1, 1))


def feria():
    img = grad((15, 15, 45), (70, 40, 90), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    rnd = random.Random(6)
    for _ in range(120):
        d.point((rnd.randrange(W), rnd.randrange(300)), fill=(255, 255, 255))
    cx, cy, r = 880, 270, 210
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(220, 220, 240), width=6)
    for i in range(12):
        a = i * math.pi / 6
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.line([(cx, cy), (x, y)], fill=(200, 200, 220), width=3)
        d.rounded_rectangle((x - 18, y, x + 18, y + 26), 6, fill=rnd.choice([(240, 90, 90), (90, 200, 240), (250, 210, 70)]))
    d.line([(cx, cy), (cx - 120, 560)], fill=(200, 200, 220), width=8)
    d.line([(cx, cy), (cx + 120, 560)], fill=(200, 200, 220), width=8)
    for k in range(3):
        y0 = 80 + k * 50
        pts = [(x, y0 + 30 * math.sin(x / 200 + k)) for x in range(0, W, 40)]
        d.line(pts, fill=(60, 50, 60), width=2)
        for i, (x, y) in enumerate(pts):
            c = [(255, 220, 100), (255, 120, 160), (120, 220, 255)][(i + k) % 3]
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=c)
    for x in (40, 330):
        d.rectangle((x, 380, x + 250, 560), fill=(200, 60, 70))
        for i in range(6):
            d.polygon([(x + i * 42, 380), (x + i * 42 + 42, 380), (x + i * 42 + 21, 340)], fill=(250, 250, 250) if i % 2 else (230, 80, 90))
    glow(img, 640, 600, 300, (255, 180, 120), 90)
    d.rectangle((0, 560, W, H), fill=(60, 50, 60))
    return img, dict(tinte=(0.85, 0.75, 0.9))


F.FONDOS.update({
    "sala": lambda: sala(False),
    "sala_noche": lambda: sala(True),
    "cocina": cocina,
    "cuarto_noche": cuarto_noche,
    "calle": calle,
    "parque": parque,
    "cafe": cafe,
    "super": super_,
    "aula": aula,
    "piscina": piscina,
    "feria": feria,
})
