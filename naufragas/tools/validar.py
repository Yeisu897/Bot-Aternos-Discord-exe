"""Revisa los guiones: comandos, fondos, poses, expresiones, música, ambientes y efectos."""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "motor"))
import audio  # noqa: E402
import engine  # noqa: E402
import fondos  # noqa: E402

SFX = {"trueno", "golpe", "chapuzon", "brillo", "sting", "revelacion", "bocina", "latido", "pasos", "rama",
       "fuego_on", "comico", "alegria", "caida", "timbre", "ladrido", "explosion", "aplausos",
       "telefono", "bocinazo", "pop"}
AMB = {"olas", "lluvia", "viento", "selva", "noche", "fuego", "cueva", "barco", "nada"}
FX = {"lluvia", "niebla", "brillo", "barco", "fuego", "apagado", "noche", "nada", "vhs", "byn"}

problemas = 0
carpetas = sys.argv[1:] or [os.path.join(ROOT, "episodios")]
for path in sorted(p for c in carpetas for p in glob.glob(os.path.join(c, "ep*.txt"))):
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        s = line.strip()
        if not s or s.startswith("//"):
            continue
        m = re.match(r"^([a-záéíóúñ_0-9]+)(?:\[([a-záéíóúñ_]+)\])?\s*:\s*(.*)$", s, re.I)
        cmd = (m.group(1) if m else s.split()[0]).lower()
        arg = (m.group(3) if m else " ".join(s.split()[1:])).split()
        err = None
        if m and cmd not in engine.COMANDOS:
            expr = m.group(2)
            if cmd in engine.CHARS and engine.CHARS[cmd].get("dibujado"):
                pass
            elif cmd in engine.CHARS and expr:
                expr = engine.ALIAS.get(cmd, {}).get(expr, expr)
                if not os.path.exists(os.path.join(ROOT, "assets", "chars", cmd, "retrato", expr + ".png")):
                    err = f"expresión sin retrato: {cmd}[{expr}]"
            elif cmd not in engine.CHARS and cmd not in engine.EXTRAS and cmd != "narrador":
                err = f"hablante desconocido: {cmd}"
        elif cmd not in engine.COMANDOS:
            err = f"comando desconocido: {cmd}"
        elif cmd == "fondo" and arg[0] not in fondos.FONDOS:
            err = f"fondo desconocido: {arg[0]}"
        elif cmd in ("entra", "pose"):
            who = arg[0]
            pose = (arg[2] if len(arg) > 2 else "base") if cmd == "entra" else arg[1]
            if who not in engine.CHARS or pose not in engine.CHARS[who]["poses"]:
                err = f"pose desconocida: {who} {pose}"
            if cmd == "entra" and len(arg) > 1 and arg[1] not in engine.POS:
                err = f"posición desconocida: {arg[1]}"
        elif cmd == "musica" and arg[0] not in audio.MOODS and arg[0] != "nada":
            err = f"música desconocida: {arg[0]}"
        elif cmd == "ambiente" and any(a not in AMB for a in " ".join(arg).replace(",", " ").split()):
            err = f"ambiente desconocido: {arg}"
        elif cmd == "efecto" and any(a not in FX for a in " ".join(arg).replace(",", " ").split()):
            err = f"efecto desconocido: {arg}"
        elif cmd == "sfx" and arg[0] not in SFX:
            err = f"sfx desconocido: {arg[0]}"
        if err:
            problemas += 1
            print(f"{os.path.basename(path)}:{n}: {err}")
print("problemas:", problemas)
