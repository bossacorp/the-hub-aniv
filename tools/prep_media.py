#!/usr/bin/env python3
"""
prep_media.py — prepara las capas del diseñador para el patch de Max.

Lee los PNG originales (con alfa) desde media_src/ y escribe versiones
optimizadas en show/ (misma carpeta que el patch, así Max las encuentra
sin configurar rutas). Conserva la transparencia y la proporción.

Uso:
    python3 tools/prep_media.py              # lado mayor = 1600 px (default)
    python3 tools/prep_media.py --max 2048   # más resolución (MacBook Pro)

Para agregar una obra nueva: copia sus capas a media_src/ y agrega una
línea a CAPAS con  (archivo_original, nombre_en_show).
"""
import argparse
import os
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (original en media_src/, nombre final en show/)
CAPAS = [
    # Par 1 — "Mano y flor" (2953 x 2953)
    ("Ilustracion_sin_titulo-03.png", "e1_mano_tinta.png"),     # dibujo azul, opaco (fondo)
    ("Ilustracion_sin_titulo-04.png", "e1_mano_boceto.png"),    # boceto claro, con alfa
    # Par 2 — "Luna" (3543 x 3543)
    ("Ilustracion_sin_titulo-02.png", "e2_luna_paisaje.png"),   # anillo de paisaje, con alfa
    ("Ilustracion_sin_titulo_01.png", "e2_luna_luna.png"),      # luna con rostro, con alfa
    # Par 3 — "Bosque" (3024 x 4032, vertical)
    ("IMG_2990-01.png", "e3_bosque_foto.png"),                  # fotografía, opaca (fondo)
    ("IMG_2990-02.png", "e3_bosque_figuras.png"),               # figuras etéreas, con alfa
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=1600, help="lado mayor en px")
    args = ap.parse_args()
    src_dir = os.path.join(RAIZ, "media_src")
    dst_dir = os.path.join(RAIZ, "show")
    os.makedirs(dst_dir, exist_ok=True)
    for src, dst in CAPAS:
        im = Image.open(os.path.join(src_dir, src)).convert("RGBA")
        w, h = im.size
        k = args.max / max(w, h)
        if k < 1:
            im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        out = os.path.join(dst_dir, dst)
        im.save(out, optimize=True)
        print(f"{src:34s} {w}x{h} -> {dst} {im.size[0]}x{im.size[1]} "
              f"({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main()
