"""Personajes caricaturescos dibujados 100% por código (para comerciales e infomerciales).

Cada personaje tiene 3 poses (base, brazos, senala) x 5 expresiones (normal, feliz, sorpresa,
triste, enojada) x boca cerrada/abierta (para animar el habla). Se generan en cache/personajes.
"""
import math
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache", "personajes")
CW, CH = 1000, 1400          # lienzo a 2x
CX = CW // 2
HY = 330                    # centro de la cabeza
INK = (40, 30, 40)
POSES = ("base", "brazos", "senala")
EXPRS = ("normal", "feliz", "sorpresa", "triste", "enojada")

PERSONAJES = {
    "chucho": dict(nombre="Don Chucho Ofertas", color=(190, 120, 255), piel=(240, 195, 160), pelo=(30, 25, 30),
                   estilo="engominado", ropa="traje", c1=(140, 60, 200), c2=(255, 255, 255), c3=(230, 40, 60),
                   pantalon=(110, 45, 160), extras=["bigote", "lunar"], ancho=1.05, altura=1.0),
    "lupita": dict(nombre="Lupita Wow", color=(255, 120, 190), piel=(250, 210, 185), pelo=(250, 215, 90),
                   estilo="copete80", ropa="vestido", c1=(255, 80, 170), c2=(255, 230, 120), c3=(255, 255, 255),
                   pantalon=(250, 210, 185), extras=["aretes", "chapitas", "pestanas"], ancho=0.9, altura=0.97),
    "patino": dict(nombre="Dr. Patiño", color=(140, 220, 255), piel=(235, 200, 170), pelo=(200, 200, 205),
                   estilo="calvo_lados", ropa="bata", c1=(250, 250, 250), c2=(150, 200, 160), c3=(60, 90, 200),
                   pantalon=(80, 80, 95), extras=["lentes_gruesos"], ancho=0.95, altura=0.96),
    "rigoberto": dict(nombre="Rigoberto", color=(200, 200, 150), piel=(225, 180, 140), pelo=(90, 65, 40),
                      estilo="despeinado", ropa="camiseta", c1=(235, 235, 225), c2=(200, 180, 120), c3=(90, 70, 50),
                      pantalon=(70, 90, 140), extras=["barba", "mancha"], ancho=1.12, altura=0.98),
    "cleta": dict(nombre="Doña Cleta", color=(255, 190, 140), piel=(240, 205, 180), pelo=(215, 215, 220),
                  estilo="chongo", ropa="chal", c1=(150, 60, 90), c2=(240, 160, 60), c3=(120, 40, 70),
                  pantalon=(120, 40, 70), extras=["lentes_chicos", "collar"], ancho=0.95, altura=0.88),
    "brayan": dict(nombre="Brayan Fitness", color=(120, 255, 120), piel=(215, 160, 120), pelo=(240, 180, 40),
                   estilo="corto", ropa="deportivo", c1=(120, 255, 60), c2=(255, 60, 200), c3=(40, 40, 40),
                   pantalon=(40, 40, 60), extras=["banda", "munequeras"], ancho=1.3, altura=1.04),
}


def dark(c, k=0.7):
    return tuple(int(v * k) for v in c)


def limb(d, pts, w, col):
    d.line(pts, fill=INK, width=w + 12, joint="curve")
    for p in (pts[0], pts[-1]):
        d.ellipse((p[0] - (w + 12) / 2, p[1] - (w + 12) / 2, p[0] + (w + 12) / 2, p[1] + (w + 12) / 2), fill=INK)
    d.line(pts, fill=col, width=w, joint="curve")
    for p in (pts[0], pts[-1]):
        d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=col)


def blob(d, box, col, w=6):
    d.ellipse(box, fill=col, outline=INK, width=w)


def poly(d, pts, col, w=6):
    d.polygon(pts, fill=col, outline=INK, width=w)


def brazos_pos(pose, a):
    sh = 150 * a
    if pose == "base":
        return [((CX - sh, 560), (CX - sh - 30, 760), (CX - sh - 20, 930)),
                ((CX + sh, 560), (CX + sh + 30, 760), (CX + sh + 20, 930))]
    if pose == "brazos":
        return [((CX - sh, 560), (CX - sh - 110, 400), (CX - sh - 150, 210)),
                ((CX + sh, 560), (CX + sh + 110, 400), (CX + sh + 150, 210))]
    return [((CX - sh, 560), (CX - sh - 30, 760), (CX - sh - 20, 930)),
            ((CX + sh, 560), (CX + sh + 160, 560), (CX + sh + 330, 540))]


def mano(d, p, piel, senala=False):
    x, y = p
    d.ellipse((x - 40, y - 40, x + 40, y + 40), fill=piel, outline=INK, width=6)
    if senala:
        d.rounded_rectangle((x + 20, y - 16, x + 95, y + 12), 12, fill=piel, outline=INK, width=6)
    else:
        d.line([(x - 15, y + 10), (x - 15, y + 30)], fill=INK, width=4)
        d.line([(x + 5, y + 12), (x + 5, y + 34)], fill=INK, width=4)


def cuerpo(d, s, pose):
    a = s["ancho"]
    piel, c1, c2, c3 = s["piel"], s["c1"], s["c2"], s["c3"]
    ropa = s["ropa"]
    # piernas y zapatos
    if ropa in ("vestido", "chal"):
        legcol = piel if ropa == "vestido" else s["pantalon"]
    else:
        legcol = s["pantalon"]
    for dx in (-65, 65):
        limb(d, [(CX + dx * a, 980), (CX + dx * a, 1300)], int(95 * min(a, 1.15)), legcol)
        shoe = (240, 60, 120) if ropa == "vestido" else (255, 255, 255) if ropa == "deportivo" else (30, 25, 30)
        blob(d, (CX + dx * a - 70 + (20 if dx > 0 else -20), 1290, CX + dx * a + 70 + (20 if dx > 0 else -20), 1365), shoe)
    if ropa == "deportivo":
        poly(d, [(CX - 140 * a, 930), (CX + 140 * a, 930), (CX + 150 * a, 1080), (CX - 150 * a, 1080)], c3)
    # brazos (detrás del torso cuando están abajo)
    manga = {"traje": c1, "bata": c1, "chal": c1, "vestido": piel, "camiseta": piel, "deportivo": piel}[ropa]
    arms = brazos_pos(pose, a)
    bw = int(80 * a) if ropa == "deportivo" else 72
    for i, arm in enumerate(arms):
        limb(d, list(arm), bw, manga)
        if ropa in ("vestido", "camiseta", "deportivo"):
            pass
        elif ropa == "traje":
            d.ellipse((arm[-1][0] - 44, arm[-1][1] - 44, arm[-1][0] + 44, arm[-1][1] + 44), fill=c2, outline=INK, width=6)
        if ropa == "deportivo" and "munequeras" in s["extras"]:
            x, y = arm[-1]
            ex, ey = arm[1]
            mx, my = x + (ex - x) * 0.25, y + (ey - y) * 0.25
            d.ellipse((mx - 45, my - 30, mx + 45, my + 30), fill=c2, outline=INK, width=6)
        mano(d, arm[-1], piel, senala=(pose == "senala" and i == 1))
    # torso
    top, bot = 160 * a, 130 * a
    if ropa == "vestido":
        poly(d, [(CX - 120 * a, 520), (CX + 120 * a, 520), (CX + 110 * a, 760), (CX - 110 * a, 760)], c1)
        poly(d, [(CX - 110 * a, 750), (CX + 110 * a, 750), (CX + 260, 1060), (CX - 260, 1060)], c1)
        for i in range(40):
            x = CX - 230 + (i * 53) % 460
            y = 560 + (i * 97) % 480
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=c2)
        d.line([(CX - 120 * a, 520), (CX - 90, 470)], fill=c1, width=22)
        d.line([(CX + 120 * a, 520), (CX + 90, 470)], fill=c1, width=22)
        return
    if ropa == "chal":
        poly(d, [(CX - top, 520), (CX + top, 520), (CX + bot + 30, 1000), (CX - bot - 30, 1000)], c1)
        poly(d, [(CX - top - 20, 520), (CX + top + 20, 520), (CX, 820)], c2)
        for i in range(12):
            x = CX - 140 + (i * 47) % 280
            y = 540 + (i * 61) % 200
            if abs(x - CX) < (820 - y) * 0.55:
                d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=c3)
        return
    if ropa == "bata":
        poly(d, [(CX - top, 520), (CX + top, 520), (CX + bot + 50, 1110), (CX - bot - 50, 1110)], c1)
        poly(d, [(CX - 70, 520), (CX + 70, 520), (CX, 660)], c2)
        d.line([(CX, 660), (CX, 1110)], fill=INK, width=5)
        d.rectangle((CX + 50, 720, CX + 130, 800), outline=INK, width=5)
        d.line([(CX + 70, 700), (CX + 70, 760)], fill=c3, width=10)
        d.line([(CX + 100, 700), (CX + 100, 760)], fill=(220, 40, 40), width=10)
        return
    torso = [(CX - top, 520), (CX + top, 520), (CX + bot, 980), (CX - bot, 980)]
    if ropa == "traje":
        poly(d, torso, c1)
        poly(d, [(CX - 70, 520), (CX + 70, 520), (CX, 760)], c2)
        poly(d, [(CX - 18, 540), (CX + 18, 540), (CX + 26, 760), (CX, 800), (CX - 26, 760)], c3, 4)
        d.line([(CX - 70, 520), (CX - 20, 780)], fill=INK, width=6)
        d.line([(CX + 70, 520), (CX + 20, 780)], fill=INK, width=6)
        for y in (830, 900):
            d.ellipse((CX - 12, y - 12, CX + 12, y + 12), fill=(250, 210, 60), outline=INK, width=3)
    elif ropa == "camiseta":
        poly(d, torso, c1)
        d.arc((CX - 80, 450, CX + 80, 590), 20, 160, fill=INK, width=6)
        d.ellipse((CX + 20, 760, CX + 90, 810), fill=c2)
        d.ellipse((CX - 80, 690, CX - 40, 715), fill=c2)
    elif ropa == "deportivo":
        poly(d, torso, c1)
        d.line([(CX - 60, 600), (CX - 60, 700)], fill=dark(c1), width=5)
        d.line([(CX + 60, 600), (CX + 60, 700)], fill=dark(c1), width=5)
        d.line([(CX - 80, 760), (CX + 80, 760)], fill=dark(c1), width=5)
        d.text((CX - 40, 800), "GYM", fill=INK)


def cabeza(d, s, expr, habla):
    piel, pelo, est = s["piel"], s["pelo"], s["estilo"]
    rx, ry = 125, 145
    # pelo trasero
    if est == "copete80":
        for (dx, dy, r) in ((-150, -40, 120), (150, -40, 120), (-110, -150, 130), (110, -150, 130), (0, -200, 140),
                            (-170, 90, 100), (170, 90, 100)):
            blob(d, (CX + dx - r, HY + dy - r, CX + dx + r, HY + dy + r), pelo)
    if est == "chongo":
        blob(d, (CX - 80, HY - 280, CX + 80, HY - 130), pelo)
    # cuello y orejas
    d.rectangle((CX - 45, HY + 110, CX + 45, HY + 200), fill=piel, outline=INK, width=6)
    for sx in (-1, 1):
        blob(d, (CX + sx * rx - 30, HY - 10, CX + sx * rx + 30, HY + 60), piel)
        if "aretes" in s["extras"]:
            d.ellipse((CX + sx * rx - 22, HY + 55, CX + sx * rx + 22, HY + 105), outline=(240, 200, 40), width=10)
    blob(d, (CX - rx, HY - ry, CX + rx, HY + ry), piel)
    if "barba" in s["extras"]:
        d.chord((CX - rx + 8, HY - 20, CX + rx - 8, HY + ry - 6), 10, 170, fill=dark(piel, 0.82))
    # pelo frontal
    if est == "engominado":
        d.chord((CX - rx - 6, HY - ry - 20, CX + rx + 6, HY + 40), 180, 360, fill=pelo, outline=INK, width=6)
        d.arc((CX - 70, HY - ry, CX + 40, HY - 40), 200, 300, fill=(200, 200, 230), width=8)
        d.line([(CX - 40, HY - ry + 5), (CX - 50, HY - 60)], fill=(90, 90, 110), width=5)
    elif est == "copete80":
        for (dx, r) in ((-70, 80), (0, 90), (70, 80)):
            blob(d, (CX + dx - r, HY - ry - 50, CX + dx + r, HY - ry + 90), pelo)
    elif est == "calvo_lados":
        d.arc((CX - 60, HY - ry + 15, CX + 10, HY - ry + 70), 190, 300, fill=(255, 255, 255), width=8)
        for sx in (-1, 1):
            for k in range(3):
                blob(d, (CX + sx * (rx + 5) - 45, HY - 70 + k * 30, CX + sx * (rx + 5) + 45, HY - 10 + k * 30), pelo, 4)
    elif est == "despeinado":
        pts = []
        for k in range(13):
            ang = math.pi + k * math.pi / 12
            r = (rx + 40) if k % 2 else rx - 10
            pts.append((CX + math.cos(ang) * r, HY - 30 + math.sin(ang) * (ry + (35 if k % 2 else -5))))
        poly(d, pts + [(CX + rx, HY - 10), (CX - rx, HY - 10)], pelo)
    elif est == "chongo":
        d.chord((CX - rx - 4, HY - ry - 10, CX + rx + 4, HY + 20), 180, 360, fill=pelo, outline=INK, width=6)
    elif est == "corto":
        d.chord((CX - rx - 4, HY - ry - 25, CX + rx + 4, HY + 10), 180, 360, fill=pelo, outline=INK, width=6)
    if "banda" in s["extras"]:
        d.rectangle((CX - rx - 4, HY - 95, CX + rx + 4, HY - 55), fill=s["c2"], outline=INK, width=5)
    # cejas y ojos
    ey = HY - 5
    for sx in (-1, 1):
        ex = CX + sx * 52
        if expr == "feliz":
            d.arc((ex - 30, ey - 20, ex + 30, ey + 30), 200, 340, fill=INK, width=9)
        else:
            big = expr == "sorpresa"
            w, h = (38, 48) if big else (32, 38)
            d.ellipse((ex - w, ey - h, ex + w, ey + h), fill=(255, 255, 255), outline=INK, width=5)
            py = ey + (12 if expr == "triste" else 4)
            pr = 11 if big else 15
            d.ellipse((ex - pr, py - pr, ex + pr, py + pr), fill=INK)
            d.ellipse((ex - pr + 6, py - pr + 4, ex - pr + 12, py - pr + 10), fill=(255, 255, 255))
            if expr == "enojada":
                d.polygon([(ex - 40, ey - 45), (ex + 40, ey - 45), (ex - sx * 40, ey - 5) if True else None,
                           (ex + sx * 40, ey - 18)], fill=piel)
            if expr == "triste":
                d.chord((ex - w - 2, ey - h - 2, ex + w + 2, ey + 6), 180, 360, fill=piel)
                d.line([(ex - w, ey - 4), (ex + w, ey - 4)], fill=INK, width=5)
        # cejas
        by = ey - 62
        if expr == "enojada":
            d.line([(ex - sx * 38, by + 2), (ex + sx * 38, by + 28)], fill=INK, width=12)
        elif expr == "triste":
            d.line([(ex - sx * 38, by + 26), (ex + sx * 38, by + 4)], fill=INK, width=10)
        elif expr == "sorpresa":
            d.arc((ex - 40, by - 30, ex + 40, by + 20), 200, 340, fill=INK, width=10)
        else:
            d.line([(ex - 36, by + 12), (ex + 36, by + 8)], fill=INK, width=10)
        if "pestanas" in s["extras"] and expr != "feliz":
            for k in range(3):
                d.line([(ex + sx * (10 + k * 12), ey - 38), (ex + sx * (18 + k * 16), ey - 58)], fill=INK, width=5)
    if "lentes_gruesos" in s["extras"]:
        for sx in (-1, 1):
            ex = CX + sx * 52
            d.ellipse((ex - 50, ey - 50, ex + 50, ey + 50), outline=INK, width=12)
        d.line([(CX - 4, ey), (CX + 4, ey)], fill=INK, width=10)
    if "lentes_chicos" in s["extras"]:
        for sx in (-1, 1):
            ex = CX + sx * 52
            d.rectangle((ex - 40, ey + 2, ex + 40, ey + 40), outline=(180, 140, 40), width=6)
        d.line([(CX - 12, ey + 15), (CX + 12, ey + 15)], fill=(180, 140, 40), width=6)
    if "chapitas" in s["extras"]:
        for sx in (-1, 1):
            d.ellipse((CX + sx * 78 - 26, HY + 40, CX + sx * 78 + 26, HY + 72), fill=(255, 140, 160))
    if "lunar" in s["extras"]:
        d.ellipse((CX + 70, HY + 60, CX + 84, HY + 74), fill=INK)
    # nariz
    d.arc((CX - 22, HY + 10, CX + 22, HY + 60), 300, 240, fill=dark(piel, 0.6), width=6)
    # boca
    my = HY + 95
    if "bigote" in s["extras"]:
        d.polygon([(CX - 80, my - 15), (CX, my - 38), (CX + 80, my - 15), (CX + 60, my - 5), (CX, my - 20),
                   (CX - 60, my - 5)], fill=s["pelo"], outline=INK)
    red, tongue = (150, 30, 40), (240, 110, 120)
    if habla:
        if expr == "triste":
            d.ellipse((CX - 26, my - 6, CX + 26, my + 30), fill=red, outline=INK, width=5)
        elif expr == "sorpresa":
            d.ellipse((CX - 32, my - 20, CX + 32, my + 48), fill=red, outline=INK, width=5)
        else:
            w = 62 if expr in ("feliz", "enojada") else 48
            d.chord((CX - w, my - 30, CX + w, my + 50), 0, 180, fill=red, outline=INK, width=5)
            d.ellipse((CX - 26, my + 12, CX + 26, my + 44), fill=tongue)
            if expr == "enojada":
                d.rectangle((CX - w + 12, my + 8, CX + w - 12, my + 20), fill=(255, 255, 255))
    else:
        if expr == "feliz":
            d.chord((CX - 60, my - 35, CX + 60, my + 40), 0, 180, fill=red, outline=INK, width=5)
            d.rectangle((CX - 46, my + 2, CX + 46, my + 14), fill=(255, 255, 255))
        elif expr == "sorpresa":
            d.ellipse((CX - 20, my - 10, CX + 20, my + 30), fill=red, outline=INK, width=5)
        elif expr == "triste":
            d.arc((CX - 40, my + 4, CX + 40, my + 50), 200, 340, fill=INK, width=7)
        elif expr == "enojada":
            d.rounded_rectangle((CX - 46, my, CX + 46, my + 28), 8, fill=(255, 255, 255), outline=INK, width=5)
            d.line([(CX - 46, my + 14), (CX + 46, my + 14)], fill=INK, width=3)
        else:
            d.arc((CX - 44, my - 20, CX + 44, my + 26), 20, 160, fill=INK, width=7)
    if "collar" in s["extras"]:
        for k in range(9):
            a = math.pi * (0.15 + 0.7 * k / 8)
            d.ellipse((CX + math.cos(a) * 90 - 11, HY + 170 + math.sin(a) * 50 - 11,
                       CX + math.cos(a) * 90 + 11, HY + 170 + math.sin(a) * 50 + 11), fill=(250, 250, 240), outline=INK, width=2)


def dibujar(pid, pose, expr, habla=False):
    s = PERSONAJES[pid]
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cuerpo(d, s, pose)
    cabeza(d, s, expr, habla)
    if pose == "brazos":  # manos por delante del pelo
        for arm in brazos_pos(pose, s["ancho"]):
            mano(d, arm[-1], s["piel"])
    return im.resize((CW // 2, CH // 2), Image.LANCZOS)


def generar(pid):
    base = os.path.join(CACHE, pid)
    marca = os.path.join(base, ".ok")
    if os.path.exists(marca):
        return base
    os.makedirs(os.path.join(base, "retrato"), exist_ok=True)
    for pose in POSES:
        for expr in EXPRS:
            for habla in (False, True):
                im = dibujar(pid, pose, expr, habla)
                im.save(os.path.join(base, f"{pose}__{expr}{'_habla' if habla else ''}.png"))
                if pose == "base" and not habla:
                    top = 40
                    head = im.crop((CX // 2 - 150, top, CX // 2 + 150, top + 300))
                    bg = Image.new("RGBA", head.size, PERSONAJES[pid]["color"] + (255,))
                    bg.alpha_composite(head)
                    bg.convert("RGB").save(os.path.join(base, "retrato", f"{expr}.png"))
    open(marca, "w").write("ok")
    return base


if __name__ == "__main__":
    for p in PERSONAJES:
        generar(p)
        print("ok", p)
