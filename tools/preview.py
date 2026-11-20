#!/usr/bin/env python3
"""
preview.py — vista previa de las escenas SIN abrir Max.

Corre show/hub_anim.js con Node (tools/sim_anim.js) y compone las capas de
show/*.png igual que los jit.gl.videoplane del patch (@transform_reset 1,
mezcla alfa, fondo negro), para revisar encuadres y fundidos desde Claude Code
o en cualquier computadora.

    python3 tools/preview.py stills            # previews/escenas_mix.jpg (cada escena con K1 en 0, 0.5, 1)
    python3 tools/preview.py video [--fps 24]  # previews/recorrido.mp4 (las 6 escenas con fundidos)

Es una aproximación: no simula el filtrado de textura de la GPU ni el gamma
del proyector. La verdad final es la proyección en sitio.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW = os.path.join(RAIZ, "show")
OUT = os.path.join(RAIZ, "previews")

# Capas (archivo, @layer) desde build_patch.py y escenas desde hub_anim.js:
# al agregar una obra no hay que tocar este archivo.
sys.path.insert(0, os.path.join(RAIZ, "tools"))
from build_patch import CAPAS as _CAPAS, PADS  # noqa: E402

CAPAS = {c[0]: (c[1], c[2]) for c in _CAPAS}


def escenas():
    r = subprocess.run(["node", os.path.join(RAIZ, "tools", "sim_anim.js"), "--escenas"],
                       capture_output=True, text=True, check=True)
    return {int(k): v for k, v in json.loads(r.stdout).items()}


def etiqueta_pad(n):
    """Qué pad dispara la escena n (p. ej. 'A2', 'B1')."""
    for banco, num, _, msg in PADS:
        if msg == f"scene {n}":
            return f"{banco}{num}"
    return "?"


def cargar(alto):
    imgs = {}
    for capa, (archivo, _) in CAPAS.items():
        im = Image.open(os.path.join(SHOW, archivo)).convert("RGBA")
        k = alto / im.size[1]
        imgs[capa] = im.resize((round(im.size[0] * k), alto), Image.LANCZOS)
    return imgs


def simular(guion):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(guion, f)
        ruta = f.name
    r = subprocess.run(["node", os.path.join(RAIZ, "tools", "sim_anim.js"), ruta],
                       capture_output=True, text=True, check=True)
    if r.stderr:
        sys.stderr.write(r.stderr)
    return json.loads(r.stdout)


def componer(estado, imgs, W, H):
    lienzo = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    for capa in sorted(CAPAS, key=lambda c: CAPAS[c][1]):
        e = estado.get(capa)
        if not e or e.get("enable", [1])[0] == 0 or "color" not in e:
            continue
        r, g, b, a = e["color"]
        sx, sy, _ = e["scale"]
        x, y, _ = e["position"]
        rot = e["rotatexyz"][2]
        w, h = max(1, round(sx * H)), max(1, round(sy * H))
        im = imgs[capa].resize((w, h), Image.BILINEAR)
        if (r, g, b) != (1, 1, 1):
            canales = im.split()
            canales = [c.point(lambda v, k=k: v * k) for c, k in zip(canales[:3], (r, g, b))] + [canales[3]]
            im = Image.merge("RGBA", canales)
        im.putalpha(im.getchannel("A").point(lambda v: v * a))
        if abs(rot) > 0.01:
            im = im.rotate(rot, resample=Image.BILINEAR, expand=True)
        cx, cy = W / 2 + x * H / 2, H / 2 - y * H / 2
        capa_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        capa_img.paste(im, (round(cx - im.size[0] / 2), round(cy - im.size[1] / 2)))
        lienzo = Image.alpha_composite(lienzo, capa_img)
    return lienzo.convert("RGB")


def stills(W=960, H=540):
    imgs = cargar(H * 2)
    mixes = [0.0, 0.5, 1.0]
    nombres = escenas()
    ids = sorted(nombres)
    filas = []
    for n in ids:
        fila = []
        for m in mixes:
            cu = simular([["scene", n], ["mix", m], ["snap"], ["frames", 1, 30]])
            fila.append(componer(cu[-1], imgs, W, H))
        filas.append(fila)
    pad, rot = 8, 26
    hoja = Image.new("RGB", (len(mixes) * (W + pad) + pad, len(ids) * (H + pad + rot) + pad),
                     (24, 24, 26))
    d = ImageDraw.Draw(hoja)
    for i, fila in enumerate(filas):
        for j, im in enumerate(fila):
            ox, oy = pad + j * (W + pad), pad + i * (H + pad + rot)
            n = ids[i]
            d.text((ox, oy + 4), f"Pad {etiqueta_pad(n)} · escena {n} · {nombres[n]} · K1 mezcla = {mixes[j]}",
                   fill=(220, 220, 220))
            hoja.paste(im, (ox, oy + rot))
    os.makedirs(OUT, exist_ok=True)
    ruta = os.path.join(OUT, "escenas_mix.jpg")
    hoja.save(ruta, quality=88)
    print(ruta)


def video(fps=24, W=960, H=540):
    imgs = cargar(H * 2)
    # recorrido: cada escena ~7 s, fundido de ~3 s, velocidad alta para ver el movimiento
    g = [["speed", 0.6], ["amp", 0.6], ["fade", 0.6], ["mix", 0.5], ["scene", 1], ["snap"]]
    ids = sorted(escenas())
    for n in ids:
        if n != ids[0]:
            g.append(["scene", n])
        g += [["mix", 0.2], ["frames", fps * 3, fps], ["mix", 0.9], ["frames", fps * 3, fps],
              ["pulse"], ["frames", fps * 1, fps]]
    g += [["black", 1], ["frames", fps * 2, fps]]
    cuadros = simular(g)
    os.makedirs(OUT, exist_ok=True)
    ruta = os.path.join(OUT, "recorrido.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264",
                           "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", ruta],
                          stdin=subprocess.PIPE)
    for c in cuadros:
        ff.stdin.write(componer(c, imgs, W, H).tobytes())
    ff.stdin.close()
    ff.wait()
    print(ruta, len(cuadros), "cuadros")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["stills", "video"])
    ap.add_argument("--fps", type=int, default=24)
    a = ap.parse_args()
    stills() if a.modo == "stills" else video(a.fps)
