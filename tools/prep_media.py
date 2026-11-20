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
  "luma_fuerte" — como "luma" pero los oscuros quedan más opacos (alfa reforzado ×3):
            para ilustraciones con fondo negro y figuras con zonas oscuras (trajes, sombras)
            que no deben volverse transparentes sobre otra capa. Sobre negro, idéntica.
  "papel" — capa pintada sobre BLANCO sin transparencia (acuarela). Lo inverso de "luma":
            el blanco del papel se vuelve transparente y queda la pintura (como un modo
            "multiplicar"). Sobre fondo blanco se ve idéntica al original; sobre negro, los
            pigmentos quedan flotando y el papel desaparece. OJO: sobre negro los colores
            pastel se vuelven oscuros y turbios.
  "pastel" — capa pintada sobre BLANCO que va a verse sobre NEGRO: conserva el color
            original (pastel) y usa la cantidad de pintura, reforzada, como alfa. El
            papel desaparece y la acuarela queda luminosa; el blanco tenue queda como bruma.

Uso:
    python3 tools/prep_media.py              # lado mayor = 1600 px (default)
    python3 tools/prep_media.py --max 2048   # más resolución

Para agregar una obra nueva: copia sus capas a media_src/ y agrega una línea
a CAPAS con (archivo_original, nombre_en_show, modo[, opciones]).
Opciones (dict, opcional):
  difumina: 0–0.5  fracción del lado que se desvanece en las orillas (quita bordes
                   rectos de una ilustración que flota sobre otra capa).
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
    # Obra 7 — "Acuarela y noche" (1280 x 468, panorámica 2.74:1; archivos par04-*)
    ("par04-01.jpeg", "e7_acuarela_reflejo.png", "pastel"),             # paisaje reflejado en acuarela sobre blanco
    ("par04-02.jpeg", "e7_acuarela_noche.png", "opaca"),                # escena nocturna: sol, madre e hijo, estrellas
    # Obra 8 — "Calaveras en la luna" (1280 x 1280, cuadrada; archivos par08-*)
    ("par08-01.jpeg", "e8_luna_textura.png", "opaca"),                  # textura de aerosol verde/violeta (fondo)
    ("par08-02.jpeg", "e8_luna_calaveras.png", "luma_fuerte",           # pareja de calaveras en la luna creciente
     {"difumina": 0.14}),                                               # orillas suaves sobre la textura
]

UMBRAL_LUMA = 6   # 0–255: el ruido de compresión JPEG por debajo de esto se vuelve transparente
REFUERZO_PASTEL = 2.5   # modo "pastel": cuánto se refuerza la pintura (más = más opaca)


def a_luma(im, refuerzo=1.0):
    """Negro → transparente. alfa = canal más brillante (× refuerzo); color = color / alfa (sin
    premultiplicar), así alfa*color reproduce el original exacto sobre negro."""
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    m = rgb.max(axis=2)
    a = np.clip((m - UMBRAL_LUMA) / (255.0 - UMBRAL_LUMA) * refuerzo, 0, 1)
    seguro = np.maximum(a, 1e-6)[..., None]
    col = np.clip(rgb / 255.0 / seguro, 0, 1)
    col[a == 0] = 0
    out = np.dstack([col * 255, a * 255]).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def a_papel(im):
    """Blanco → transparente. tinta = 255 − color; alfa = canal con más tinta; color = el
    pigmento puro que, sobre blanco con ese alfa, reproduce el original exacto."""
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    tinta = 255.0 - rgb
    m = tinta.max(axis=2)
    a = np.clip((m - UMBRAL_LUMA) / (255.0 - UMBRAL_LUMA), 0, 1)
    seguro = np.maximum(a, 1e-6)[..., None]
    col = np.clip(1.0 - tinta / 255.0 / seguro, 0, 1)
    col[a == 0] = 1
    out = np.dstack([col * 255, a * 255]).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def a_pastel(im):
    """Blanco → transparente conservando el color original: alfa = tinta reforzada."""
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    tinta = (255.0 - rgb).max(axis=2)
    a = np.clip((tinta - UMBRAL_LUMA) / (255.0 - UMBRAL_LUMA) * REFUERZO_PASTEL, 0, 1) ** 0.8
    out = np.dstack([rgb, a * 255]).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def difuminar(im, frac):
    """Desvanece el alfa hacia las orillas (rampa suave en una franja de `frac` del lado)."""
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    def rampa(n):
        t = np.minimum(np.arange(n), np.arange(n)[::-1]) / max(1.0, frac * n)
        t = np.clip(t, 0, 1)
        return t * t * (3 - 2 * t)          # suavizado (smoothstep)
    mascara = rampa(h)[:, None] * rampa(w)[None, :]
    a[..., 3] *= mascara
    return Image.fromarray(a.round().astype(np.uint8), "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=1600, help="lado mayor en px")
    args = ap.parse_args()
    src_dir = os.path.join(RAIZ, "media_src")
    dst_dir = os.path.join(RAIZ, "show")
    os.makedirs(dst_dir, exist_ok=True)
    for src, dst, modo, *extra in CAPAS:
        opciones = extra[0] if extra else {}
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
        elif modo == "luma_fuerte":
            im = a_luma(im, refuerzo=3.0)
        elif modo == "papel":
            im = a_papel(im)
        elif modo == "pastel":
            im = a_pastel(im)
        elif modo == "opaca":
            im = im.convert("RGBA")   # alfa 255: mismo formato ARGB que las demás en Jitter
        if opciones.get("difumina"):
            im = difuminar(im.convert("RGBA"), opciones["difumina"])
        out = os.path.join(dst_dir, dst)
        im.save(out, optimize=True)
        print(f"{src:34s} {w}x{h} -> {dst} {im.size[0]}x{im.size[1]} [{modo}{' ' + str(opciones) if opciones else ''}] "
              f"({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main()
