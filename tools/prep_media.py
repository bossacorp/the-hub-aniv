#!/usr/bin/env python3
"""
prep_media.py — prepara las capas del diseñador para el patch de Max.

Lee los originales desde media_src/ y escribe PNG optimizados en show/
(misma carpeta que el patch, así Max los encuentra sin configurar rutas).
Conserva la transparencia y la proporción; nunca agranda.

Modos por capa:
  "alfa"  — la imagen ya trae transparencia (PNG del diseñador). Se respeta tal cual.
  "opaca" — fotografía o fondo sin transparencia (JPEG). Se guarda opaca.
  "luma"  — capa pintada sobre NEGRO sin transparencia (JPEG). El brillo se vuelve
            alfa: el negro desaparece y lo luminoso queda (como un modo "pantalla").
            Sobre fondo negro se ve idéntica al original.

Uso:
    python3 tools/prep_media.py              # lado mayor = 1600 px (default)
    python3 tools/prep_media.py --max 2048   # más resolución

Para agregar una obra nueva: copia sus capas a media_src/ y agrega una línea
a CAPAS con (archivo_original, nombre_en_show, modo).
"""
import argparse
import os

import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (original en media_src/, nombre final en show/, modo)
CAPAS = [
    # Obra 1 — "Mano y flor" (2953 x 2953)
    ("Ilustracion_sin_titulo-03.png", "e1_mano_tinta.png", "alfa"),     # dibujo azul, opaco
    ("Ilustracion_sin_titulo-04.png", "e1_mano_boceto.png", "alfa"),    # boceto claro
    # Obra 2 — "Luna" (3543 x 3543)
    ("Ilustracion_sin_titulo-02.png", "e2_luna_paisaje.png", "alfa"),   # anillo de paisaje
    ("Ilustracion_sin_titulo_01.png", "e2_luna_luna.png", "alfa"),      # luna con rostro
    # Obra 3 — "Bosque" (3024 x 4032, vertical)
    ("IMG_2990-01.png", "e3_bosque_foto.png", "alfa"),                  # fotografía, opaca
    ("IMG_2990-02.png", "e3_bosque_figuras.png", "alfa"),               # figuras etéreas
    # Obra 4 — "Sombrero" (721 x 1280, vertical 9:16; archivos del diseñador par05-*)
    ("par05-01.jpeg", "e4_sombrero_foto.png", "opaca"),                 # fotografía de día
    ("par05-02.jpeg", "e4_sombrero_noche.png", "luma"),                 # pintura nocturna sobre negro
    # Obra 5 — "Hongo y criatura" (900 x 1600, vertical 9:16; archivos par06-*)
    ("par06-02.jpeg", "e5_hongo_foto.png", "opaca"),                    # fotografía de hongos (cola de pavo)
    ("par06-01.jpeg", "e5_hongo_criatura.png", "luma"),                 # criatura pintada sobre negro
    # Obra 6 — "Nahual" (960 x 1280, vertical 3:4; archivos par07-*)
    ("par07-01.jpeg", "e6_nahual_foto.png", "opaca"),                   # ficus con silla roja y papel picado
    ("par07-02.jpeg", "e6_nahual_animales.png", "luma"),                # jaguar nahual, jaguares y loros sobre negro
]

UMBRAL_LUMA = 6   # 0–255: el ruido de compresión JPEG por debajo de esto se vuelve transparente


def a_luma(im):
    """Negro → transparente. alfa = canal más brillante; color = color / alfa (sin premultiplicar),
    así alfa*color reproduce el original exacto sobre negro."""
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    m = rgb.max(axis=2)
    a = np.clip((m - UMBRAL_LUMA) / (255.0 - UMBRAL_LUMA), 0, 1)
    seguro = np.maximum(a, 1e-6)[..., None]
    col = np.clip(rgb / 255.0 / seguro, 0, 1)
    col[a == 0] = 0
    out = np.dstack([col * 255, a * 255]).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=1600, help="lado mayor en px")
    args = ap.parse_args()
    src_dir = os.path.join(RAIZ, "media_src")
    dst_dir = os.path.join(RAIZ, "show")
    os.makedirs(dst_dir, exist_ok=True)
    for src, dst, modo in CAPAS:
        ruta = os.path.join(src_dir, src)
        if not os.path.exists(ruta):
            print(f"FALTA {src} (se conserva show/{dst} si existe)")
            continue
        im = Image.open(ruta)
        w, h = im.size
        k = args.max / max(w, h)
        im = im.convert("RGB" if modo != "alfa" else "RGBA")
        if k < 1:
            im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        if modo == "luma":
            im = a_luma(im)
        elif modo == "opaca":
            im = im.convert("RGBA")   # alfa 255: mismo formato ARGB que las demás en Jitter
        out = os.path.join(dst_dir, dst)
        im.save(out, optimize=True)
        print(f"{src:34s} {w}x{h} -> {dst} {im.size[0]}x{im.size[1]} [{modo}] "
              f"({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main()
