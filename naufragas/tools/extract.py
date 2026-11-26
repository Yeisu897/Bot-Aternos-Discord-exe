"""Recorta sprites y retratos de las hojas de personaje (fondo blanco -> transparente).

Uso: python tools/extract.py   (desde la carpeta naufragas/)
"""
import os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS = os.path.join(ROOT, "assets", "sheets")
OUT = os.path.join(ROOT, "assets", "chars")

# (hoja, caja x0,y0,x1,y1)
SPRITES = {
    # cuerpo entero principal
    "yei/base": ("yei_partes.png", (0, 0, 343, 1118), [(298, 655, 343, 1118)]),
    "kitzuki/base": ("kitzuki_partes.png", (0, 0, 352, 1172)),
    "kirane/base": ("kirane_partes.png", (0, 0, 300, 1199)),
    # poses extra
    "yei/cadera": ("yei_hoja.png", (0, 478, 200, 850), [(186, 600, 200, 850)]),
    "yei/sentada": ("yei_hoja.png", (325, 535, 525, 852)),
    "yei/estirando": ("yei_hoja.png", (688, 476, 835, 852)),
    "yei/frente": ("yei_hoja.png", (330, 35, 470, 425)),
    "kitzuki/cadera": ("kitzuki_hoja.png", (0, 858, 165, 1199)),
    "kitzuki/sentada": ("kitzuki_hoja.png", (395, 862, 595, 1199)),
    "kitzuki/acostada": ("kitzuki_hoja.png", (565, 895, 850, 1150)),
    "kitzuki/frente": ("kitzuki_hoja.png", (0, 0, 205, 505)),
    "kirane/nuca": ("kirane_hoja.png", (0, 618, 200, 1220)),
    "kirane/brazos": ("kirane_hoja.png", (505, 618, 665, 1222)),
    "kirane/sentada": ("kirane_hoja.png", (610, 795, 965, 1225), [(800, 795, 965, 925), (893, 900, 965, 1132)]),
    "kirane/acostada": ("kirane_hoja.png", (790, 640, 1112, 912)),
    "kirane/frente": ("kirane_hoja.png", (90, 0, 275, 622)),
    # efectos
    "fx/amuleto": ("yei_partes.png", (995, 893, 1175, 1060)),
}

# retratos (se usan con marco, no necesitan transparencia)
def grid(sheet, xs, ys, names):
    out = {}
    k = 0
    for r in range(len(ys) - 1):
        for c in range(len(xs) - 1):
            out[names[k]] = (sheet, (xs[c], ys[r], xs[c + 1], ys[r + 1]))
            k += 1
    return out

PORTRAITS = {}
PORTRAITS.update({"yei/" + k: v for k, v in grid(
    "yei_hoja.png", [872, 1018, 1166, 1312], [32, 165, 300, 452],
    ["feliz", "risa", "sorpresa", "enojada", "timida", "triste", "nerviosa", "miedo", "cansada"]).items()})
PORTRAITS.update({"kitzuki/" + k: v for k, v in grid(
    "kitzuki_hoja.png", [2, 198, 396, 592, 792, 992, 1196], [508, 690, 856],
    ["normal", "picara", "risa", "enojada", "avergonzada", "nerviosa",
     "timida", "seria", "pensativa", "cansada", "sonrojada", "sorpresa"]).items()})
PORTRAITS["kitzuki/lentes"] = ("kitzuki_hoja.png", (760, 20, 1160, 420))
PORTRAITS.update({"kirane/" + k: v for k, v in grid(
    "kirane_hoja.png", [787, 967, 1112, 1254], [2, 230, 438, 628],
    ["feliz", "risa", "normal", "molesta", "triste", "sorpresa", "timida", "preocupada", "enojada"]).items()})


def cutout(im, extra=False):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    mn = a.min(axis=2)
    mx = a.max(axis=2)
    near_white = (mn > 236) & ((mx - mn) < 22)
    lab, n = ndimage.label(near_white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    border.discard(0)
    bg = np.isin(lab, list(border))
    fg = ~bg
    fg = ndimage.binary_opening(fg, iterations=1)
    lab2, n2 = ndimage.label(fg)
    if n2 > 1:
        sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
        big = int(np.argmax(sizes)) + 1
        keep = lab2 == big
        # conservar mechones sueltos grandes cercanos
        for i, s in enumerate(sizes, start=1):
            if extra and i != big and s > sizes.max() * 0.02:
                keep |= lab2 == i
        fg = keep
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    bb = alpha.point(lambda v: 255 if v > 20 else 0).getbbox()
    return out.crop(bb) if bb else out


def main():
    cache = {}
    def sheet(name):
        if name not in cache:
            cache[name] = Image.open(os.path.join(SHEETS, name)).convert("RGB")
        return cache[name]

    for key, spec in SPRITES.items():
        sh, box = spec[0], spec[1]
        src = sheet(sh).copy()
        if len(spec) > 2:
            from PIL import ImageDraw
            d = ImageDraw.Draw(src)
            for r in spec[2]:
                d.rectangle(r, fill=(255, 255, 255))
        path = os.path.join(OUT, key + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cutout(src.crop(box), extra=key.endswith('/base')).save(path)
        print("sprite", key)
    for key, (sh, box) in PORTRAITS.items():
        c, k = key.split("/")
        path = os.path.join(OUT, c, "retrato", k + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        sheet(sh).crop(box).save(path)
    print("retratos", len(PORTRAITS))


if __name__ == "__main__":
    main()
