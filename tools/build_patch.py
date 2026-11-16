#!/usr/bin/env python3
"""
build_patch.py — genera show/the-hub-aniv_<VERSION>.maxpat (y su mapa de cables).

El patch se GENERA desde este script para que los cambios queden legibles en
git (un diff de Python se entiende; un diff de .maxpat casi no).
Flujo recomendado:
    1. Cambia este script (o pídeselo a Claude Code).
    2. python3 tools/build_patch.py      → regenera el patch y valida
    3. Abre el patch en Max y prueba.  Si ajustas algo a mano en Max,
       anótalo en docs/bitacora.md para pasarlo al script.

Compatibilidad: Max 8 y Max 9 (solo objetos de Max 8; JS clásico `js`).
Máquina de función: MacBook Pro con Max 9.2+.

v02 (ensayo 2026-11-15):
  - Pads del LPD8 por ruta MIDI DIRECTA (notein → solo golpes → mismos botones
    que el teclado). Ya no se mapean con Assign MIDI Map: ese mapeo de nota a
    live.button alternaba 1/0 en cada golpe y "se comía" uno de cada dos.
  - Conserva el mapeo de perillas hecho en el ensayo (CC 1–8) en el patch.
  - jit.fpsgui conectado al outlet de bang por cuadro de jit.world (outlet 1).
"""
import json
import os
import sys

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import maxpat_builder  # noqa: E402
from maxpat_builder import Patch, validate_file  # noqa: E402

maxpat_builder.UI_IO.setdefault("live.numbox", (1, 2))
maxpat_builder.IO.setdefault("switch", (3, 1))

VERSION = "v02"
NOMBRE = f"the-hub-aniv_{VERSION}"

# capa → (archivo en show/, @layer = orden de dibujo). Las dimensiones de cada
# jit.matrix se leen del PNG, así se puede regenerar a otra resolución.
CAPAS = [
    ("foto",    "e3_bosque_foto.png",    1),
    ("tinta",   "e1_mano_tinta.png",     2),
    ("luna",    "e2_luna_luna.png",      3),
    ("paisaje", "e2_luna_paisaje.png",   4),
    ("figuras", "e3_bosque_figuras.png", 5),
    ("boceto",  "e1_mano_boceto.png",    6),
]

# Pads del LPD8 (número de pad, etiqueta, mensaje al motor JS)
PADS = [
    (1, "1 · Mano y flor", "scene 1"),
    (2, "2 · Luna", "scene 2"),
    (3, "3 · Bosque", "scene 3"),
    (4, "4 · Luna en bosque", "scene 4"),
    (5, "5 · Boceto paisaje", "scene 5"),
    (6, "6 · Pulso", "pulse"),
    (7, "7 · SEGURA", "scene 6"),
    (8, "8 · NEGRO", None),          # va a un toggle (cada golpe alterna)
]
NOTA_PAD1 = 36   # LPD8 Wireless, programa del ensayo: pads = notas 36–43 (canal 10)

# Perillas del LPD8 (número, longname, etiqueta corta, mensaje, valor inicial)
KNOBS = [
    (1, "k1_mezcla", "K1 Mezcla", "mix", 0.5),
    (2, "k2_velocidad", "K2 Velocid", "speed", 0.35),
    (3, "k3_amplitud", "K3 Amplitud", "amp", 0.5),
    (4, "k4_zoom", "K4 Zoom", "zoom", 0.5),
    (5, "k5_transicion", "K5 Transic", "fade", 0.6),
    (6, "k6_tono", "K6 Tono", "tone", 0.5),
    (7, "k7_vizzie", "K7 Vizzie", None, 0.0),   # reserva → [s vz_k7]
    (8, "k8_master", "K8 Master", "master", 1.0),
]
KNOB_DESC = {1: "capa A ↔ B", 2: "0 = congelado", 3: "respiración/deriva", 4: "encuadre",
             5: "0.2 s … 20 s", 6: "frío ↔ cálido", 7: "reserva (s vz_k7)", 8: "brillo / fundido"}

# Mapeo de perillas tal como lo guardó Max en el ensayo del 2026-11-15
# (docs/ensayos/2026-11-15_the-hub-aniv_v01_mapeo-lpd8.maxpat). Los pads NO se
# mapean: van por la ruta MIDI directa.
MIDI_MAP_PERILLAS = {f"k{i}_{n}": f"{i}.ctrl.0.chan.midi" for i, n in
                     [(1, "mezcla"), (2, "velocidad"), (3, "amplitud"), (4, "zoom"),
                      (5, "transicion"), (6, "tono"), (7, "vizzie"), (8, "master")]}

GRIS = [0.72, 0.72, 0.74, 1.0]


def dims_png(archivo):
    with Image.open(os.path.join(RAIZ, "show", archivo)) as im:
        return im.size


def build():
    p = Patch(f"The Hub · Aniversario — Proyección {VERSION} (capas del diseñador)",
              target=8, size=(1000, 690))

    # ---------------- PRESENTACIÓN: paneles ----------------
    p.panel((20, 70, 470, 235), x=1300, y=20)
    p.panel((510, 70, 470, 235), x=1300, y=60)
    p.panel((20, 318, 470, 120), x=1300, y=100)
    p.panel((510, 318, 470, 120), x=1300, y=140)
    p.panel((20, 452, 470, 225), x=1300, y=180, color=(0.10, 0.10, 0.12, 1.0))
    p.panel((510, 452, 470, 225), x=1300, y=220, color=(0.10, 0.10, 0.12, 1.0))
    p.title_block(pres_xy=(20, 12), subtitle="LPD8 Wireless · pads = escenas y disparos (MIDI directo) · "
                  "perillas = mezcla y movimiento · teclas 1–8 = pads")
    p.comment("PADS — ESCENAS", 30, 60, w=200, pres=(32, 76, 200, 20), bold=True)
    p.comment("PERILLAS — MEZCLA Y MOVIMIENTO", 560, 60, w=260, pres=(522, 76, 300, 20), bold=True)

    # ---------------- JS: motor de escenas ----------------
    p.section("MOTOR: escenas, mezcla y animación suave (show/hub_anim.js)", 430, 300, w=420)
    js = p.obj("js hub_anim.js", 430, 330, w=160, io=(1, 2))
    rte = p.obj("route " + " ".join(c[0] for c in CAPAS), 430, 380, w=330)
    p.connect(js, 0, rte, 0)

    # ---------------- PADS (botones en pantalla) ----------------
    p.section("CONTROL: pads (clic, teclas 1–8 o LPD8 por MIDI directo; NO usar Assign MIDI Map)",
              30, 20, w=520)
    pad_ids = {}
    # Disposición física LPD8: fila de arriba pads 5–8, fila de abajo pads 1–4
    for num, etiqueta, mensaje in PADS:
        col = (num - 1) % 4
        fila_arriba = num >= 5
        px = 45 + col * 112
        py = 104 if fila_arriba else 200
        ex = 30 + (num - 1) * 50
        b = p.button(f"pad{num}", f"Pad {num}", ex, 90, pres=(px, py, 54, 54))
        pad_ids[num] = b
        p.comment(etiqueta, ex, 120, w=48, pres=(px - 12, py + 58, 104, 18), size=10.0,
                  color=GRIS)
        if mensaje:
            m = p.msg(mensaje, ex, 230)
            p.connect(b, 0, m, 0)
            p.connect(m, 0, js, 0)

    # Pad 8 → toggle (negro) → js
    neg = p.ui("toggle", 380, 230, 24, 24, pres=(400, 360, 30, 30))
    p.comment("NEGRO activo", 410, 230, w=90, pres=(436, 366, 50, 34), size=10.0, color=GRIS)
    p.connect(pad_ids[8], 0, neg, 0)
    pblack = p.obj("prepend black", 380, 270)
    p.connect(neg, 0, pblack, 0)
    p.connect(pblack, 0, js, 0)

    # Teclado: teclas 1–8 disparan los pads
    p.section("TECLADO: 1–8 = pads", 30, 150, w=300)
    key = p.obj("key", 30, 175, io=(0, 4))
    sel = p.obj("sel 49 50 51 52 53 54 55 56", 80, 175, w=200)
    p.connect(key, 0, sel, 0)
    for i in range(8):
        p.connect(sel, i, pad_ids[i + 1], 0)

    # ---------------- PADS LPD8: ruta MIDI directa ----------------
    # notein → stripnote (solo note-on = un golpe) → − nota del pad 1 → sel 0..7 → botón.
    # Si el LPD8 está en modo TOGGLE (un golpe manda note-on, el siguiente note-off),
    # el interruptor "LPD8 en modo toggle" deja pasar también los note-off.
    p.section("PADS LPD8 DIRECTO: notein → solo golpes → mismos botones que el teclado", 30, 960, w=520)
    nin_pads = p.obj("notein", 30, 990)
    strip = p.obj("stripnote", 30, 1030, io=(2, 2))
    p.connect(nin_pads, 1, strip, 1)    # velocidad (llega primero: notein sale de der. a izq.)
    p.connect(nin_pads, 0, strip, 0)    # tono
    modo = p.toggle("lpd8_modo_toggle", "LPD8 toggle", 200, 990, pres=(170, 640, 24, 24), init=0)
    p.comment("LPD8 en modo TOGGLE (cada golpe cuenta)", 230, 990, w=200,
              pres=(198, 643, 280, 18), size=10.0, color=GRIS)
    mas1 = p.obj("+ 1", 200, 1030)
    p.connect(modo, 0, mas1, 0)
    sw = p.obj("switch 2", 30, 1070, io=(3, 1))
    p.connect(mas1, 0, sw, 0)
    p.connect(strip, 0, sw, 1)          # 1 = solo note-on (pads momentáneos, recomendado)
    p.connect(nin_pads, 0, sw, 2)       # 2 = cualquier evento de nota (pads en toggle)
    base = p._param_ui("live.numbox", "nota_pad1", "Nota pad 1", 330, 990, 44, 15,
                       (96, 642, 44, 18), 0, 127, NOTA_PAD1, 1)
    p.comment("nota pad 1", 380, 990, w=80, pres=(32, 643, 62, 18), size=10.0, color=GRIS)
    resta = p.obj("- 36", 30, 1110)
    p.connect(base, 0, resta, 1)
    p.connect(sw, 0, resta, 0)
    selp = p.obj("sel 0 1 2 3 4 5 6 7", 30, 1150, w=160)
    p.connect(resta, 0, selp, 0)
    for i in range(8):
        p.connect(selp, i, pad_ids[i + 1], 0)

    # ---------------- PERILLAS ----------------
    p.section("CONTROL: perillas LPD8 (mapeadas con Assign MIDI Map: CC 1–8)", 560, 20, w=400)
    for num, longname, etiqueta, mensaje, init in KNOBS:
        col = (num - 1) % 4
        fila_arriba = num <= 4
        px = 540 + col * 112
        py = 100 if fila_arriba else 196
        ex = 560 + (num - 1) * 60
        d = p.dial(longname, etiqueta, ex, 90, pres=(px, py, 50, 56), init=init)
        p.comment(KNOB_DESC[num], ex, 145, w=56, pres=(px - 22, py + 58, 100, 18), size=10.0,
                  color=GRIS)
        if mensaje:
            pr = p.obj(f"prepend {mensaje}", ex, 230)
            p.connect(d, 0, pr, 0)
            p.connect(pr, 0, js, 0)
        else:
            p.send_out("vz_k7", d, x=ex, y=230)   # puente a Vizzie: [r vz_k7] en el módulo que elijas

    # ---------------- ESTADO ----------------
    p.section("ESTADO: lo que reporta el motor", 620, 300, w=260)
    rst = p.obj("route escena fade negro", 620, 330, w=170)
    p.connect(js, 1, rst, 0)
    pset = p.obj("prepend set Escena", 620, 360)
    p.connect(rst, 0, pset, 0)
    est = p.msg("Escena —", 620, 390, w=240, pres=(110, 330, 360, 24))
    p.connect(pset, 0, est, 0)
    p.comment("Activa:", 600, 390, w=60, pres=(32, 332, 70, 20), bold=True)
    fl = p.ui("flonum", 800, 390, 60, 22, pres=(110, 362, 60, 22))
    p.connect(rst, 1, fl, 0)
    p.comment("seg. de transición (K5)", 860, 390, w=150, pres=(174, 364, 160, 20), size=10.0,
              color=GRIS)
    p.comment("Escenas 1–3 = cada obra con sus 2 capas. 4–5 = cruces entre obras. 7 = segura.",
              620, 420, w=360, pres=(32, 406, 450, 20), size=10.0, color=GRIS)

    # ---------------- CARGA DE IMÁGENES + VIDEOPLANES ----------------
    p.section("IMÁGENES → TEXTURAS: cada PNG (con alfa) a un videoplane. "
              "Archivos en la MISMA carpeta que el patch.", 30, 430, w=700)
    lb = p.obj("loadbang", 30, 460)
    dl = p.obj("delay 600", 100, 460, io=(2, 1))
    p.connect(lb, 0, dl, 0)
    recargar = p.button("recargar", "Recargar", 200, 460, pres=(690, 345, 30, 30))
    p.comment("Recargar imágenes", 230, 460, w=120, pres=(724, 350, 120, 20), size=10.0)
    p.connect(recargar, 0, dl, 0)
    tr = p.obj("t b b b b b b", 30, 490, w=200)
    p.connect(dl, 0, tr, 0)
    for i, (capa, archivo, layer) in enumerate(CAPAS):
        w, h = dims_png(archivo)
        x = 30 + i * 200
        m = p.msg(f"importmovie {archivo}, bang", x, 530, w=190)
        p.connect(tr, 5 - i, m, 0)
        mx = p.obj(f"jit.matrix 4 char {w} {h}", x, 560)
        p.connect(m, 0, mx, 0)
        vp = p.obj(f"jit.gl.videoplane hub @layer {layer} @blend_enable 1 @depth_enable 0 "
                   f"@transform_reset 1 @color 1 1 1 0 @enable 0", x, 640, w=190, h=50)
        p.connect(mx, 0, vp, 0)
        p.connect(rte, i, vp, 0)
        p.comment(f"capa {layer}: {capa}", x, 610, w=180, size=10.0, color=GRIS)

    # ---------------- RELOJ + MUNDO ----------------
    p.section("SALIDA: ventana de proyección (esc = pantalla completa)", 30, 720, w=420)
    anim = p.toggle("animar", "Animación", 30, 750, pres=(530, 345, 30, 30), init=1)
    p.comment("Animación", 60, 750, w=80, pres=(564, 350, 80, 20), size=10.0)
    qm = p.obj("qmetro 16", 30, 780)
    p.connect(anim, 0, qm, 0)
    p.connect(qm, 0, js, 0)
    init = p.obj("loadbang", 140, 750)
    dl2 = p.obj("delay 100", 140, 780, io=(2, 1))
    p.connect(init, 0, dl2, 0)
    m_init = p.msg("scene 1, snap", 140, 810)
    p.connect(dl2, 0, m_init, 0)
    p.connect(m_init, 0, js, 0)

    fs = p.toggle("pantalla_completa", "Pantalla", 300, 750, pres=(530, 395, 30, 30), init=0)
    p.comment("Pantalla completa (o tecla esc en la ventana)", 330, 750, w=200,
              pres=(564, 400, 220, 20), size=10.0)
    pfs = p.obj("prepend fullscreen", 300, 780)
    p.connect(fs, 0, pfs, 0)
    world = p.obj("jit.world hub @enable 1 @erase_color 0 0 0 1 @size 960 540 "
                  "@fsmenubar 0 @fsaa 1", 300, 840, w=420)
    p.connect(pfs, 0, world, 0)
    fps = p.ui("jit.fpsgui", 300, 880, 80, 35, pres=(880, 340, 80, 35))
    p.comment("fps", 390, 880, w=40, pres=(850, 348, 30, 20), size=10.0)
    p.connect(world, 1, fps, 0)   # outlet 1 = bang por cuadro dibujado

    # ---------------- MONITOR MIDI + PUERTO ----------------
    ctl, nin = p.midi_monitor(x=1100, y=460, pres=(32, 462))
    p.port_menu("Puerto MIDI del LPD8 (monitor y pads)", [ctl, nin, nin_pads], 1100, 560,
                pres=(32, 530, 200, 22))

    # ---------------- CÓMO USAR ----------------
    p.usage_notes([
        "1. Deja los 6 PNG y hub_anim.js en la MISMA carpeta que este patch.",
        "2. Abre el patch: la ventana 'hub' carga las imágenes en ~1 s.",
        "3. Arrastra la ventana al proyector y pulsa esc (pantalla completa).",
        "4. Perillas K1–K8: ya vienen mapeadas a CC 1–8 (Assign MIDI Map).",
        "5. Pads: NO los mapees. Entran por MIDI directo (notas 36–43).",
        "   Elige el LPD8 en 'Puerto MIDI'. Si un golpe sí y otro no:",
        "   el LPD8 está en TOGGLE → ponlo en MOMENTARY o activa el",
        "   interruptor 'LPD8 en modo TOGGLE'.",
        "6. Pads 1–5 escenas · 6 pulso · 7 segura · 8 negro on/off.",
        "7. Teclas 1–8 hacen lo mismo que los pads (respaldo).",
    ], pres=(522, 460, 450, 210), x=1100, y=700)
    p.comment("Monitor MIDI: golpea un pad y mira la velocidad. Golpe = valor > 0, "
              "soltar = 0 (MOMENTARY). Si golpes alternos dan 0 → el pad está en TOGGLE.",
              1100, 640, w=330, pres=(32, 560, 450, 34), size=10.0, color=GRIS)
    p.comment("Vizzie: K7 ya publica [s vz_k7] 0–1.", 1100, 670, w=330,
              pres=(32, 600, 450, 18), size=10.0, color=GRIS)

    avisos = p.validate()
    d = p.to_dict()
    pmap = {}
    for longname, src in MIDI_MAP_PERILLAS.items():
        pmap[longname] = {"srcname": src, "min": 0.0, "max": 1.0, "flags": 2}
    d["patcher"]["parameter_map"] = {"midi": pmap}
    out = os.path.join(RAIZ, "show", f"{NOMBRE}.maxpat")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    p.save_wiring_md(os.path.join(RAIZ, "docs", f"cables_{VERSION}.md"))
    avisos += validate_file(out, target=8)
    return out, avisos


if __name__ == "__main__":
    ruta, avisos = build()
    print("patch:", ruta)
    print("\n".join(avisos) if avisos else "validación: sin avisos")
