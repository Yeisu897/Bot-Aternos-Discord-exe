# Náufragas: Tres en la isla

Serie animada 2D de 20 episodios: tres chicas (Yei, Kitzuki y Kirane) naufragan
en una isla desierta y tienen que sobrevivir juntas.

Todo se genera con herramientas gratuitas y offline:

| Parte | Herramienta |
|---|---|
| Voces | espeak-ng + MBROLA (voz femenina `es3`, inyección de fonemas para corregir rr/ñ/ll/ch) |
| Música | Generada por código con numpy (originales, sin derechos) |
| Ambientes y efectos | Generados por código (olas, lluvia, selva, fuego, trueno, bocina...) |
| Fondos | Dibujados por código con Pillow (playa, selva, cascada, cueva, cabaña, cumbre, barco, jardín) |
| Personajes | Recortados automáticamente de las hojas de personaje (`assets/sheets`) |
| Video | ffmpeg (H.264 + AAC, 1280x720, 24 fps) |

## Personajes

- **Yei** (pelo celeste): dulce y optimista. Lleva el amuleto de la rosa de su abuela Marina.
- **Kitzuki** (pelo blanco y negro, lentes): estudiante de biología, lista y sarcástica.
- **Kirane** (pelo verde): ex salvavidas, impulsiva, fuerte y de buen corazón.

## Episodios

| # | Título | # | Título |
|---|---|---|---|
| 1 | El naufragio | 11 | Mensaje en una botella |
| 2 | Agua | 12 | El barco |
| 3 | Fuego | 13 | Lo que no decimos |
| 4 | Refugio | 14 | Huellas |
| 5 | La tormenta | 15 | La cabaña |
| 6 | Grietas | 16 | La verdad del amuleto |
| 7 | Sola | 17 | La gran tormenta |
| 8 | La cueva de los símbolos | 18 | Sacrificio |
| 9 | El secreto de Yei | 19 | La señal |
| 10 | Fiebre | 20 | Hogar |

## Cómo generar los videos

Requisitos (Ubuntu/Debian):

```bash
sudo apt install ffmpeg espeak-ng mbrola mbrola-es1 mbrola-es2 mbrola-es3
pip install numpy scipy pillow
```

```bash
cd naufragas
python3 tools/extract.py          # recorta sprites y retratos de las hojas
python3 tools/validar.py          # revisa los guiones
python3 motor/engine.py episodios/ep01.txt videos/ep01.mp4
# todos en paralelo:
ls episodios/ep*.txt | xargs -P 4 -I{} python3 motor/engine.py {}
```

## Escribir o editar un episodio

Los guiones están en `episodios/epNN.txt`. Cada línea es un diálogo o un comando:

```
titulo: El naufragio
fondo: playa_dia              # playa_*, campamento_*, selva*, cascada, cueva*, cabana*, cumbre*, cubierta, jardin
musica: calma                 # tema, calma, alegre, triste, tension, misterio, esperanza, accion, romance, nada
ambiente: olas viento         # olas, lluvia, viento, selva, noche, fuego, cueva, barco, nada
efecto: lluvia brillo         # lluvia, niebla, brillo (amuleto), barco, fuego, apagado, nada
entra: yei centro [pose]      # izq, izq2, centro, der2, der
sale: kirane
mueve: kitzuki der
pose: kirane sentada          # base, sentada, acostada, cadera, brazos, nuca, estirando, frente
zoom: 1.2 centro
sfx: trueno                   # trueno, golpe, chapuzon, brillo, sting, revelacion, bocina, latido, pasos...
temblor / relampago / destello / fundido
pausa: 1.5
tarjeta: Tres semanas después
narrador: Texto del narrador.
yei[feliz]: Diálogo con emoción.
```

Emociones con retrato: Yei (feliz, risa, sorpresa, enojada, timida, triste, nerviosa, miedo, cansada),
Kitzuki (normal, picara, risa, enojada, avergonzada, nerviosa, timida, seria, pensativa, cansada,
sonrojada, sorpresa, lentes), Kirane (feliz, risa, normal, molesta, triste, sorpresa, timida,
preocupada, enojada). Otras emociones se asignan al retrato más parecido.

Las voces se ajustan en `motor/tts.py` (`VOCES`: tono base `f0`, rango, velocidad, timbre).
