"""Motor de la serie "Náufragas": guion (.txt) -> video MP4 2D con voces, música y animación.

Uso:
    python motor/engine.py episodios/ep01.txt [salida.mp4] [--preview]
"""
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio  # noqa: E402
import fondos  # noqa: E402
import tts  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1280, 720, 24
SR = audio.SR
SERIE = "NÁUFRAGAS"
SUBTITULO = "Tres en la isla"
INTRO, OUTRO = 7.0, 6.0

FONT = lambda f, s: ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", f), s)  # noqa: E731
F_TEXT = FONT("NotoSans-Regular.ttf", 30)
F_ITAL = FONT("NotoSans-Italic.ttf", 30)
F_NAME = FONT("ComicNeue-Bold.otf", 34)
F_TITLE = FONT("NotoSerif-BoldItalic.ttf", 108)
F_SUB = FONT("NotoSerif-BoldItalic.ttf", 44)
F_CARD = FONT("NotoSerif-BoldItalic.ttf", 54)
F_SMALL = FONT("NotoSans-Regular.ttf", 22)

CHARS = {
    "yei": dict(nombre="Yei", color=(110, 215, 255), acento=(150, 100, 255), defecto="feliz",
                poses=dict(base=610, cadera=600, estirando=600, frente=600, sentada=420)),
    "kitzuki": dict(nombre="Kitzuki", color=(220, 220, 232), acento=(60, 60, 70), defecto="normal",
                    poses=dict(base=650, cadera=600, frente=625, sentada=400, acostada=250)),
    "kirane": dict(nombre="Kirane", color=(60, 205, 180), acento=(40, 150, 70), defecto="normal",
                   poses=dict(base=655, nuca=640, brazos=640, frente=640, sentada=430, acostada=270)),
}
LIFT = {"acostada": 190, "sentada": 70}
ALIAS = {
    "yei": {"seria": "timida", "preocupada": "nerviosa", "pensativa": "timida", "picara": "feliz", "sonrojada": "timida"},
    "kitzuki": {"triste": "avergonzada", "preocupada": "nerviosa", "miedo": "sorpresa", "feliz": "normal", "molesta": "enojada"},
    "kirane": {"seria": "normal", "miedo": "sorpresa", "pensativa": "triste", "picara": "feliz", "cansada": "preocupada",
               "nerviosa": "preocupada", "avergonzada": "timida", "sonrojada": "timida"},
}
EXTRAS = {"abuela": dict(nombre="Abuela Marina", color=(240, 170, 190), acento=(120, 60, 80)),
          "marinero": dict(nombre="Marinero", color=(150, 180, 220), acento=(40, 60, 90))}
POS = {"izq": 250, "izq2": 430, "centro": 640, "der2": 850, "der": 1030, "fuera_izq": -320, "fuera_der": 1600}
COMANDOS = {"titulo", "fondo", "musica", "ambiente", "efecto", "entra", "sale", "mueve", "pose", "voltea",
            "zoom", "sfx", "pausa", "tarjeta", "temblor", "relampago", "destello", "fundido"}


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ recursos
_sprites = {}


def sprite(who, pose, tinte, dim=False, flip=False):
    key = (who, pose, tinte, dim, flip)
    if key in _sprites:
        return _sprites[key]
    path = os.path.join(ROOT, "assets", "chars", who, pose + ".png")
    im = Image.open(path).convert("RGBA")
    h = CHARS[who]["poses"].get(pose, 600)
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    if tinte != (1, 1, 1) or dim:
        k = [c * (0.78 if dim else 1.0) for c in tinte]
        r, g, b, a = im.split()
        r = r.point(lambda v, m=k[0]: min(255, int(v * m)))
        g = g.point(lambda v, m=k[1]: min(255, int(v * m)))
        b = b.point(lambda v, m=k[2]: min(255, int(v * m)))
        im = Image.merge("RGBA", (r, g, b, a))
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    _sprites[key] = im
    return im


_portraits = {}


def retrato(who, expr, size=190):
    key = (who, expr, size)
    if key in _portraits:
        return _portraits[key]
    base = os.path.join(ROOT, "assets", "chars", who, "retrato")
    expr = ALIAS.get(who, {}).get(expr, expr)
    path = os.path.join(base, f"{expr}.png")
    if not os.path.exists(path):
        path = os.path.join(base, CHARS[who]["defecto"] + ".png")
    im = Image.open(path).convert("RGB")
    s = min(im.size)
    im = im.crop(((im.width - s) // 2, 0, (im.width - s) // 2 + s, s)).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), 22, fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    _portraits[key] = out
    return out


def wrap(text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.getlength(test) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ guion -> línea de tiempo
class Episodio:
    def __init__(self, path):
        self.path = path
        m = re.search(r"(\d+)", os.path.basename(path))
        self.num = int(m.group(1)) if m else 0
        self.titulo = ""
        self.bg, self.fx, self.cams, self.shakes, self.flashes = [], [], [], [], []
        self.chars = {}
        self.lines, self.cards = [], []
        self.voices, self.sfx, self.music, self.amb, self.fades = [], [], [], [], []
        self.barco_t0 = None
        self._build()

    def ev(self, who, t, act, *args):
        self.chars.setdefault(who, []).append((t, act, args))

    def _build(self):
        t = INTRO
        self.music.append((0.0, "tema"))
        self.sfx.append((2.6, "brillo"))
        cur_fx = set()
        on_stage = {}
        with open(self.path, encoding="utf-8") as f:
            raw = [l.rstrip("\n") for l in f]
        for line in raw:
            s = line.strip()
            if not s or s.startswith("//"):
                continue
            m = re.match(r"^([a-záéíóúñ_0-9]+)(?:\[([a-záéíóúñ_]+)\])?\s*:\s*(.*)$", s, re.I)
            cmd = s.split()[0].lower() if not m else m.group(1).lower()
            if m and cmd not in COMANDOS:
                who, expr, text = cmd, (m.group(2) or "").lower() or None, m.group(3).strip()
                if who in CHARS and not expr:
                    expr = CHARS[who]["defecto"]
                clip = tts.sintetizar(who, text, expr)
                dur = len(clip) / SR
                total = max(1.8, dur + 0.55)
                self.lines.append(dict(t0=t, t1=t + total, who=who, expr=expr, text=text, dur=dur))
                self.voices.append((t + 0.15, clip))
                t += total
                continue
            arg = m.group(3).strip() if m else " ".join(s.split()[1:])
            a = arg.split()
            if cmd == "titulo":
                self.titulo = arg
            elif cmd == "fondo":
                self.bg.append((t, a[0]))
                if self.barco_t0 is not None and "barco" not in cur_fx:
                    self.barco_t0 = None
                t += 0.4
            elif cmd == "musica":
                self.music.append((t, a[0]))
            elif cmd == "ambiente":
                self.amb.append((t, [x.strip() for x in arg.replace(",", " ").split()]))
            elif cmd == "efecto":
                cur_fx = set(x for x in arg.replace(",", " ").split() if x != "nada")
                self.fx.append((t, frozenset(cur_fx)))
                if "barco" in cur_fx:
                    self.barco_t0 = t
            elif cmd == "entra":
                who, pos = a[0], a[1] if len(a) > 1 else "centro"
                pose = a[2] if len(a) > 2 else "base"
                self.ev(who, t, "entra", POS.get(pos, 640), pose)
                on_stage[who] = True
                t += 0.3
            elif cmd == "sale":
                self.ev(a[0], t, "sale")
                on_stage.pop(a[0], None)
                t += 0.3
            elif cmd == "mueve":
                self.ev(a[0], t, "mueve", POS.get(a[1], 640))
                t += 0.2
            elif cmd == "pose":
                self.ev(a[0], t, "pose", a[1])
            elif cmd == "voltea":
                self.ev(a[0], t, "voltea")
            elif cmd == "zoom":
                z = float(a[0])
                fx = POS.get(a[1], 640) if len(a) > 1 else 640
                self.cams.append((t, z, fx))
            elif cmd == "sfx":
                self.sfx.append((t, a[0]))
            elif cmd == "pausa":
                t += float(a[0]) if a else 1.0
            elif cmd == "tarjeta":
                self.cards.append((t, t + 3.0, arg))
                t += 3.0
            elif cmd == "temblor":
                self.shakes.append(t)
            elif cmd == "relampago":
                self.flashes.append(t)
                self.sfx.append((t + 0.1, "trueno"))
            elif cmd == "destello":
                self.flashes.append(t)
            elif cmd == "fundido":
                self.fades.append(t)
                t += 1.2
        t += 1.0
        self.body_end = t
        self.total = t + OUTRO
        self.music.append((self.body_end, "tema"))
        self.amb.append((self.body_end, []))

    # -------------------------------------------------------------- consulta de estado
    def bg_at(self, t):
        cur, prev, tc = self.bg[0][1] if self.bg else "negro", None, -10
        for tt, name in self.bg:
            if tt <= t:
                prev, cur, tc = cur, name, tt
        return cur, prev, tc

    def fx_at(self, t):
        cur = frozenset()
        for tt, s in self.fx:
            if tt <= t:
                cur = s
        return cur

    def cam_at(self, t):
        z0, x0, z1, x1, tc = 1.0, 640, 1.0, 640, -10
        for tt, z, fx in self.cams:
            if tt <= t:
                u = ease((tt - tc) / 0.9) if tc > -10 else 1
                z0, x0 = z0 + (z1 - z0) * u, x0 + (x1 - x0) * u
                z1, x1, tc = z, fx, tt
        u = ease((t - tc) / 0.9)
        return z0 + (z1 - z0) * u, x0 + (x1 - x0) * u

    def char_state(self, who, t):
        st = dict(on=False, x0=640, x1=640, ts=-10, dur=0.5, a0=0, a1=0, pose="base", flip=False, tp=-10)
        for tt, act, args in self.chars.get(who, []):
            if tt > t:
                break
            if act == "entra":
                x = args[0]
                side = -360 if x < 640 else 1640
                if not st["on"] and st["a1"] == 0:
                    st.update(x0=side if x != 640 else x, x1=x, ts=tt, a0=0, a1=1, on=True, pose=args[1], dur=0.6)
                else:
                    st.update(x0=st["x1"], x1=x, ts=tt, a0=st["a1"], a1=1, on=True, pose=args[1], dur=0.6)
            elif act == "sale":
                side = -360 if st["x1"] < 640 else 1640
                st.update(x0=st["x1"], x1=side if st["x1"] != 640 else st["x1"], ts=tt, a0=1, a1=0, on=False, dur=0.6)
            elif act == "mueve":
                st.update(x0=st["x1"], x1=args[0], ts=tt, a0=st["a1"], a1=st["a1"], dur=0.7)
            elif act == "pose":
                st.update(pose=args[0], tp=tt)
            elif act == "voltea":
                st["flip"] = not st["flip"]
        u = ease((t - st["ts"]) / st["dur"])
        st["x"] = st["x0"] + (st["x1"] - st["x0"]) * u
        st["alpha"] = st["a0"] + (st["a1"] - st["a0"]) * u
        return st

    def line_at(self, t):
        for i, ln in enumerate(self.lines):
            if ln["t0"] <= t < ln["t1"]:
                return i, ln
        return None, None


# ------------------------------------------------------------------ dibujo
class Render:
    def __init__(self, ep):
        self.ep = ep
        self._box = {}
        self.next_title = self._next_title()

    def _next_title(self):
        d = os.path.dirname(self.ep.path)
        p = os.path.join(d, f"ep{self.ep.num + 1:02d}.txt")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                for l in f:
                    if l.lower().startswith("titulo:"):
                        return l.split(":", 1)[1].strip()
        return None

    def scene(self, t, show_chars=True):
        ep = self.ep
        cur, prev, tc = ep.bg_at(t)
        img = self.bg_layer(cur, t)
        if prev and t - tc < 0.8:
            img = Image.blend(self.bg_layer(prev, t), img, ease((t - tc) / 0.8))
        meta = fondos.fondo(cur)[1]
        fx = ep.fx_at(t)
        tinte = meta.get("tinte", (1, 1, 1))
        if "noche" in fx:
            tinte = (0.55, 0.6, 0.85)
        if meta.get("fuego") and "noche" in cur and "apagado" not in fx:
            tinte = (0.85, 0.68, 0.62)
        tinte = tuple(round(c, 2) for c in tinte)
        if show_chars:
            idx, ln = ep.line_at(t)
            speaker = ln["who"] if ln else None
            order = sorted(CHARS, key=lambda w: (w == speaker))
            for who in order:
                st = ep.char_state(who, t)
                if st["alpha"] <= 0.01:
                    continue
                dim = speaker is not None and speaker in CHARS and speaker != who
                sp = sprite(who, st["pose"], tinte, dim, st["flip"])
                bob = 2.5 * math.sin(t * 2.1 + hash(who) % 7)
                if ln and speaker == who and t - ln["t0"] < 0.35:
                    bob -= 10 * math.sin(math.pi * (t - ln["t0"]) / 0.35)
                if t - st["tp"] < 0.3:
                    bob -= 8 * math.sin(math.pi * (t - st["tp"]) / 0.3)
                x = int(st["x"] - sp.width / 2)
                y = int(H + 12 - sp.height + bob - LIFT.get(st["pose"], 0))
                if st["alpha"] < 0.99:
                    a = sp.split()[3].point(lambda v, k=st["alpha"]: int(v * k))
                    img.paste(sp, (x, y), a)
                else:
                    img.paste(sp, (x, y), sp)
                if who == "yei" and "brillo" in fx:
                    self.amuleto(img, st["x"], y + 140, t)
        # efectos globales
        if "lluvia" in fx:
            fondos.lluvia(img, t, 1.0)
        if "niebla" in fx:
            img = Image.blend(img, Image.new("RGB", img.size, (200, 205, 215)), 0.25)
        return img

    def bg_layer(self, name, t):
        base, meta = fondos.fondo(name)
        img = base.copy()
        if meta.get("nubes"):
            fondos.nubes(img, t, meta.get("nube_color", (255, 255, 255)), meta.get("cielo"))
        if meta.get("estrellas"):
            fondos.estrellas(img, t)
        if self.ep.barco_t0 is not None and "barco" in self.ep.fx_at(t) and meta.get("olas"):
            fondos.barco_lejano(img, t, self.ep.barco_t0, meta["tinte"])
        if meta.get("olas"):
            fondos.olas(img, t, meta["olas"], meta["tinte"])
        if meta.get("fuego") and ("noche" in name or "fuego" in self.ep.fx_at(t)):
            if "apagado" not in self.ep.fx_at(t):
                fondos.fuego(img, t, *meta["fuego"])
        if meta.get("cascada"):
            fondos.cascada_anim(img, t, meta["cascada"])
        if meta.get("luciernagas"):
            fondos.luciernagas(img, t)
        if meta.get("gotas"):
            fondos.gotas(img, t)
        if meta.get("petalos"):
            fondos.petalos(img, t)
        return img

    def amuleto(self, img, x, y, t):
        g = fondos._glow_sprite(150, (170, 110, 255))
        k = 0.6 + 0.4 * math.sin(t * 3)
        a = g.split()[3].point(lambda v: int(v * k))
        img.paste(g, (int(x - 150), int(y - 150)), a)
        am = _amuleto_sprite()
        img.paste(am, (int(x - am.width / 2), int(y - am.height / 2 + 6 * math.sin(t * 2))), am)
        d = ImageDraw.Draw(img)
        for i in range(8):
            ang = t * 1.5 + i * math.pi / 4
            r = 90 + 15 * math.sin(t * 2 + i)
            sx, sy = x + math.cos(ang) * r, y + math.sin(ang) * r * 0.6
            d.line([(sx - 6, sy), (sx + 6, sy)], fill=(230, 210, 255), width=2)
            d.line([(sx, sy - 6), (sx, sy + 6)], fill=(230, 210, 255), width=2)

    def camera(self, img, t):
        z, fx = self.ep.cam_at(t)
        sx = sy = 0
        for ts in self.ep.shakes:
            if 0 <= t - ts < 0.6:
                k = 1 - (t - ts) / 0.6
                sx += int(14 * k * math.sin(t * 90))
                sy += int(10 * k * math.cos(t * 77))
        if abs(z - 1) < 0.005 and sx == 0 and sy == 0:
            return img
        if sx or sy:
            z = max(z, 1.05)
        cw, ch = W / z, H / z
        cx = min(max(fx, cw / 2), W - cw / 2)
        cy = min(max(H * 0.42, ch / 2), H - ch / 2) if z > 1.005 else H / 2
        bx = min(max(cx - cw / 2 - sx, 0), W - cw)
        by = min(max(cy - ch / 2 - sy, 0), H - ch)
        box = (bx, by, bx + cw, by + ch)
        return img.resize((W, H), Image.BILINEAR, box=box)

    def dialog(self, img, t):
        idx, ln = self.ep.line_at(t)
        if ln is None:
            return img
        if idx not in self._box:
            self._box[idx] = self.make_box(ln)
        box, lines, font, x0, y0, col = self._box[idx]
        fade = min(1.0, (t - ln["t0"]) / 0.15, (ln["t1"] - t) / 0.15)
        out = img.convert("RGBA")
        if fade < 1:
            a = box.split()[3].point(lambda v: int(v * fade))
            out.paste(box, (0, 0), a)
        else:
            out.alpha_composite(box)
        total = sum(len(l) for l in lines)
        n = int(total * min(1.0, (t - ln["t0"] - 0.1) / max(0.4, ln["dur"] * 0.9)))
        d = ImageDraw.Draw(out)
        y = y0
        for l in lines:
            if n <= 0:
                break
            s = l[:n]
            d.text((x0 + 2, y + 2), s, font=font, fill=(0, 0, 0))
            d.text((x0, y), s, font=font, fill=col)
            n -= len(l)
            y += 40
        return out.convert("RGB")

    def make_box(self, ln):
        who = ln["who"]
        box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        if who == "narrador":
            d.rounded_rectangle((90, 548, W - 90, 700), 20, fill=(10, 10, 20, 200), outline=(230, 200, 120, 255), width=3)
            lines = wrap(ln["text"], F_ITAL, W - 260)
            return box, lines, F_ITAL, 130, 572 if len(lines) > 1 else 600, (250, 235, 200)
        info = CHARS.get(who) or EXTRAS.get(who) or dict(nombre=who.capitalize(), color=(200, 200, 200), acento=(80, 80, 80))
        col = info["color"]
        d.rounded_rectangle((40, 530, W - 40, 706), 22, fill=(16, 18, 34, 215), outline=col + (255,), width=4)
        tx = 70
        if who in CHARS:
            p = retrato(who, ln["expr"])
            d.rounded_rectangle((44, 466, 44 + 200, 466 + 200), 26, fill=col + (255,))
            box.alpha_composite(p, (49, 471))
            tx = 270
        name = info["nombre"]
        nw = int(F_NAME.getlength(name)) + 40
        d.rounded_rectangle((tx - 8, 502, tx - 8 + nw, 548), 18, fill=col + (255,), outline=(255, 255, 255, 255), width=2)
        d.text((tx + 12, 506), name, font=F_NAME, fill=(20, 20, 30))
        lines = wrap(ln["text"], F_TEXT, W - 70 - tx - 20)
        return box, lines, F_TEXT, tx + 4, 562 if len(lines) <= 3 else 556, (255, 255, 255)

    def card(self, img, t):
        for t0, t1, text in self.ep.cards:
            if t0 <= t < t1:
                k = min(1.0, (t - t0) / 0.5, (t1 - t) / 0.5)
                over = Image.new("RGB", (W, H), (6, 6, 12))
                d = ImageDraw.Draw(over)
                lines = wrap(text, F_CARD, W - 200)
                y = H / 2 - len(lines) * 35
                for l in lines:
                    d.text(((W - F_CARD.getlength(l)) / 2, y), l, font=F_CARD, fill=(240, 225, 190))
                    y += 70
                return Image.blend(img, over, k)
        for tf in self.ep.fades:
            if tf <= t < tf + 1.2:
                k = 1 - abs((t - tf) - 0.6) / 0.6
                return Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), max(0, k))
        return img

    def flash(self, img, t):
        for tf in self.ep.flashes:
            if 0 <= t - tf < 0.5:
                k = (1 - (t - tf) / 0.5) * (0.9 if (t - tf) < 0.08 or 0.16 < (t - tf) < 0.22 else 0.4)
                img = Image.blend(img, Image.new("RGB", (W, H), (240, 245, 255)), k)
        return img

    # ---------------------------------------------------------- intro / outro
    def intro(self, t):
        img = self.bg_layer("playa_atardecer", t + 20)
        for i, (who, x) in enumerate((("kitzuki", 300), ("yei", 640), ("kirane", 980))):
            t0 = 0.3 + i * 0.45
            u = ease((t - t0) / 0.7)
            if u <= 0:
                continue
            sp = sprite(who, "base", (1.0, 0.86, 0.78))
            y = int(H + 12 - sp.height + (1 - u) * 400)
            img.paste(sp, (int(x - sp.width / 2), y), sp)
            if t > t0 + 0.5 and t < 2.6:
                d = ImageDraw.Draw(img)
                nm = CHARS[who]["nombre"]
                w = F_NAME.getlength(nm)
                d.rounded_rectangle((x - w / 2 - 20, 600, x + w / 2 + 20, 648), 18, fill=CHARS[who]["color"])
                d.text((x - w / 2, 604), nm, font=F_NAME, fill=(20, 20, 30))
        if t > 2.5:
            k = ease((t - 2.5) / 0.6)
            dark = Image.new("RGB", (W, H), (20, 10, 40))
            img = Image.blend(img, dark, 0.45 * k)
            d = ImageDraw.Draw(img)
            tw = F_TITLE.getlength(SERIE)
            y = 150 - (1 - k) * 60
            for dx, dy in ((4, 4), (0, 0)):
                d.text(((W - tw) / 2 + dx, y + dy), SERIE, font=F_TITLE,
                       fill=(40, 20, 60) if dx else (int(255 * k), int(235 * k), int(170 * k)))
            sw = F_SUB.getlength(SUBTITULO)
            d.text(((W - sw) / 2, y + 135), SUBTITULO, font=F_SUB, fill=(int(170 * k + 30), int(230 * k), int(255 * k)))
        if t > 4.4:
            k = ease((t - 4.4) / 0.5)
            d = ImageDraw.Draw(img)
            s1 = f"Episodio {self.ep.num}"
            s2 = self.ep.titulo
            d.rounded_rectangle((W / 2 - 420, 430, W / 2 + 420, 560), 24, fill=(int(20 * k), int(15 * k), int(40 * k)),
                                outline=(int(230 * k), int(200 * k), int(120 * k)), width=3)
            d.text(((W - F_SUB.getlength(s1)) / 2, 440), s1, font=F_SUB, fill=(int(255 * k), int(230 * k), int(170 * k)))
            d.text(((W - F_SUB.getlength(s2)) / 2, 495), s2, font=F_SUB, fill=(int(255 * k),) * 3)
        if t > INTRO - 0.6:
            img = Image.blend(img, Image.new("RGB", (W, H)), ease((t - (INTRO - 0.6)) / 0.6))
        return img

    def outro(self, t):
        u = t - self.ep.body_end
        img = Image.new("RGB", (W, H), (10, 8, 22))
        d = ImageDraw.Draw(img)
        k = ease(u / 0.8)
        final = self.next_title is None
        s = "FIN" if final else "Continuará..."
        d.text(((W - F_TITLE.getlength(s)) / 2, 180), s, font=F_TITLE, fill=(int(240 * k), int(220 * k), int(160 * k)))
        if u > 1.0:
            k2 = ease((u - 1.0) / 0.6)
            s2 = "Gracias por acompañar a Yei, Kitzuki y Kirane" if final else f"Próximo episodio: {self.next_title}"
            d.text(((W - F_SUB.getlength(s2)) / 2, 360), s2, font=F_SUB, fill=(int(200 * k2), int(230 * k2), int(255 * k2)))
        cred = "Náufragas · Voces: espeak-ng + MBROLA · Música y fondos generados por código"
        d.text(((W - F_SMALL.getlength(cred)) / 2, 650), cred, font=F_SMALL, fill=(120, 120, 150))
        x = 0
        for i, who in enumerate(("kitzuki", "yei", "kirane")):
            p = retrato(who, {"kitzuki": "picara", "yei": "risa", "kirane": "feliz"}[who], 120)
            img.paste(p, (W // 2 - 200 + i * 140, 470), p)
        if u > OUTRO - 0.7:
            img = Image.blend(img, Image.new("RGB", (W, H)), ease((u - (OUTRO - 0.7)) / 0.7))
        return img

    def frame(self, t):
        ep = self.ep
        if t < INTRO:
            return self.intro(t)
        if t >= ep.body_end:
            return self.outro(t)
        img = self.scene(t)
        img = self.camera(img, t)
        img = self.flash(img, t)
        img = self.dialog(img, t)
        img = self.card(img, t)
        if t - INTRO < 0.8:
            img = Image.blend(Image.new("RGB", (W, H)), img, ease((t - INTRO) / 0.8))
        if ep.body_end - t < 0.8:
            img = Image.blend(Image.new("RGB", (W, H)), img, ease((ep.body_end - t) / 0.8))
        return img


# ------------------------------------------------------------------ audio
def mezcla(ep):
    n = int(ep.total * SR) + SR
    voz = np.zeros(n)
    for t, clip in ep.voices:
        audio.place(voz, clip, t)
    efx = np.zeros(n)
    for t, name in ep.sfx:
        audio.place(efx, audio.sfx(name) * 0.55, t)
    mus = np.zeros(n)
    seq = sorted(ep.music)
    for i, (t, mood) in enumerate(seq):
        t_end = seq[i + 1][0] if i + 1 < len(seq) else ep.total
        if mood == "nada" or mood not in audio.MOODS:
            continue
        loop = audio.music_loop(mood)
        a, b = int(t * SR), int(t_end * SR) + int(1.5 * SR)
        b = min(b, n)
        seg = np.resize(loop, b - a)
        e = np.ones(b - a)
        fi = min(int(1.2 * SR), len(e) // 2)
        e[:fi] = np.linspace(0, 1, fi)
        e[-fi:] *= np.linspace(1, 0, fi)
        mus[a:b] += seg * e
    amb = np.zeros(n)
    seq = sorted(ep.amb, key=lambda x: x[0])
    for i, (t, names) in enumerate(seq):
        t_end = seq[i + 1][0] if i + 1 < len(seq) else ep.total
        a, b = int(t * SR), min(n, int(t_end * SR) + SR)
        e = np.ones(b - a)
        fi = min(int(1.0 * SR), len(e) // 2)
        if fi > 0:
            e[:fi] = np.linspace(0, 1, fi)
            e[-fi:] *= np.linspace(1, 0, fi)
        for nm in names:
            if nm == "nada":
                continue
            amb[a:b] += np.resize(audio.ambience(nm), b - a) * e * 0.5
    # ducking de la música bajo las voces
    envv = np.abs(voz)
    k = int(0.3 * SR)
    envv = np.convolve(envv[::100], np.ones(k // 100) / (k // 100), mode="same")
    envv = np.repeat(envv, 100)[:n]
    duck = 1 - 0.55 * np.clip(envv * 6, 0, 1)
    mix = voz * 0.95 + mus * 0.22 * duck + amb * 0.16 * (1 - 0.3 * np.clip(envv * 6, 0, 1)) + efx
    return mix[: int(ep.total * SR)]


def render(path, out, preview=False):
    ep = Episodio(path)
    r = Render(ep)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    wav = out + ".wav"
    audio.save_wav(wav, mezcla(ep))
    fps = 12 if preview else FPS
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast" if not preview else "ultrafast",
           "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(ep.total * fps)
    for i in range(nframes):
        img = r.frame(i / fps)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    os.unlink(wav)
    print(f"{out}: {ep.total:.1f}s, {len(ep.lines)} líneas")
    return ep


_am = None


def _amuleto_sprite():
    global _am
    if _am is None:
        im = Image.open(os.path.join(ROOT, "assets", "chars", "fx", "amuleto.png")).convert("RGBA")
        _am = im.resize((72, int(72 * im.height / im.width)), Image.LANCZOS)
    return _am


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = args[0]
    out = args[1] if len(args) > 1 else os.path.join(ROOT, "videos", os.path.basename(src).replace(".txt", ".mp4"))
    render(src, out, preview="--preview" in sys.argv)
