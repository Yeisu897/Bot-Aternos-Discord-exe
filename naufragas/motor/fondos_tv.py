"""Fondos de estudio de televisión hortera para comerciales e infomerciales."""
import math
import random

from PIL import ImageDraw

import fondos as F
from fondos import W, H, grad, glow


def _piso(d, y0, c1, c2):
    for i, y in enumerate(range(y0, H, 40)):
        for j, x in enumerate(range(0, W, 80)):
            d.rectangle((x, y, x + 80, y + 40), fill=c1 if (i + j) % 2 else c2)


def estudio():
    img = grad((120, 20, 140), (255, 120, 60), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 260
    for i in range(24):
        a = i * math.pi / 12
        d.polygon([(cx, cy), (cx + math.cos(a) * 1400, cy + math.sin(a) * 1400),
                   (cx + math.cos(a + 0.13) * 1400, cy + math.sin(a + 0.13) * 1400)], fill=(255, 200, 60, 70))
    img = img.convert("RGB").convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in (140, 1140):
        glow(img, x, 90, 140, (255, 255, 220), 150)
        d.polygon([(x - 40, 20), (x + 40, 20), (x + 25, 70), (x - 25, 70)], fill=(40, 40, 50))
    d = ImageDraw.Draw(img)
    _piso(d, 560, (250, 220, 60), (220, 40, 120))
    rnd = random.Random(3)
    for _ in range(40):
        x, y = rnd.randrange(W), rnd.randrange(30, 520)
        d.line([(x - 8, y), (x + 8, y)], fill=(255, 255, 255), width=3)
        d.line([(x, y - 8), (x, y + 8)], fill=(255, 255, 255), width=3)
    return img, dict(tinte=(1, 1, 1))


def estudio_retro():
    img = grad((10, 10, 40), (60, 10, 90), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.ellipse((440, 80, 840, 480), fill=(255, 120, 60))
    for k, y in enumerate(range(300, 480, 22)):
        d.rectangle((440, y, 840, y + 6 + k), fill=(60, 10, 90))
    for x in range(-W, 2 * W, 90):
        d.line([(W / 2, 460), (x, H)], fill=(255, 0, 200), width=3)
    for i in range(12):
        y = 460 + (i ** 1.7) * 4
        d.line([(0, y), (W, y)], fill=(0, 255, 255), width=2)
    d.rectangle((0, 455, W, 462), fill=(255, 0, 200))
    return img, dict(tinte=(0.95, 0.85, 1.0))


def estudio_dorado():
    img = grad((40, 20, 10), (120, 70, 20), W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(0, W, 90):
        d.rectangle((x, 0, x + 60, 540), fill=(170, 30, 40))
        d.line([(x + 30, 0), (x + 30, 540)], fill=(120, 20, 30), width=6)
    d.rectangle((0, 0, W, 50), fill=(220, 180, 60))
    for x in range(20, W, 60):
        d.ellipse((x, 15, x + 20, 35), fill=(255, 240, 150))
    glow(img, 640, 300, 280, (255, 220, 140), 120)
    d = ImageDraw.Draw(img)
    _piso(d, 540, (60, 40, 30), (30, 20, 15))
    return img, dict(tinte=(1.0, 0.95, 0.85))


F.FONDOS.update({"estudio": estudio, "estudio_retro": estudio_retro, "estudio_dorado": estudio_dorado})
