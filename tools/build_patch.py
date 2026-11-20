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

v02 (ensayo 2026-11-15): pads por ruta MIDI directa (no Assign MIDI Map),
  mapeo de perillas del ensayo conservado, fpsgui al outlet 1 de jit.world.
v03: banco B del LPD8 (16 pads). Cada banco tiene su rango de notas, su panel y
  sus teclas; los pads 6–7–8 hacen lo mismo en ambos bancos (pulso, segura,
  negro) para que equivocarse de banco nunca sea grave. Aviso si los rangos
  de notas de A y B se empalman. Obra 4 "Sombrero" en B1.

Agregar una obra: capas en CAPAS (aquí), en prep_media.py y en hub_anim.js
(CAPAS, NOMBRES, ESCENAS); su pad en PADS. preview.py lo toma solo.
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

VERSION = "v03"
NOMBRE = f"the-hub-aniv_{VERSION}"

# capa → (archivo en show/, @layer = orden de dibujo). Mismo orden que NOMBRES en
# hub_anim.js. Las dimensiones de cada jit.matrix se leen del PNG.
CAPAS = [
    ("foto",     "e3_bosque_foto.png",     1),
    ("tinta",    "e1_mano_tinta.png",      2),
    ("luna",     "e2_luna_luna.png",       3),
    ("paisaje",  "e2_luna_paisaje.png",    4),
    ("figuras",  "e3_bosque_figuras.png",  5),
    ("boceto",   "e1_mano_boceto.png",     6),
    ("sombrero", "e4_sombrero_foto.png",   7),
    ("noche",    "e4_sombrero_noche.png",  8),
    ("hongo",    "e5_hongo_foto.png",      9),
    ("criatura", "e5_hongo_criatura.png", 10),
    ("ficus",    "e6_nahual_foto.png",     11),
    ("nahual",   "e6_nahual_animales.png", 12),
]

# Pads: (banco, número, etiqueta, mensaje al motor JS). Escena = número de pad:
# banco A → escenas 1–5; banco B → escenas 11–15. Pads 6/7/8 iguales en A y B.
PADS = [
    ("A", 1, "A1 · Mano y flor", "scene 1"),
    ("A", 2, "A2 · Luna", "scene 2"),
    ("A", 3, "A3 · Bosque", "scene 3"),
    ("A", 4, "A4 · Luna en bosque", "scene 4"),
    ("A", 5, "A5 · Boceto paisaje", "scene 5"),
    ("A", 6, "A6 · Pulso", "pulse"),
    ("A", 7, "A7 · SEGURA", "scene 6"),
    ("A", 8, "A8 · NEGRO", None),          # va al toggle de negro (cada golpe alterna)
    ("B", 1, "B1 · Sombrero", "scene 11"),
    ("B", 2, "B2 · Hongo criatura", "scene 12"),
    ("B", 3, "B3 · Nahual", "scene 13"),
    ("B", 4, "B4 · (próx. par)", "scene 14"),
    ("B", 5, "B5 · (próx. par)", "scene 15"),
    ("B", 6, "B6 · Pulso", "pulse"),
    ("B", 7, "B7 · SEGURA", "scene 6"),
    ("B", 8, "B8 · NEGRO", None),
]
# Notas del LPD8 Wireless. A: medido en el ensayo 2026-11-15 (36–43, canal 10).
# B: 2026-11-19 el usuario verificó en el LPD8 que A y B no se empalman (aviso "sin
# empalme"). Si en pantalla se ajustó "nota B1", poner aquí ese valor. El aviso de
# empalme se enciende si los rangos chocan.
NOTA_A1 = 36
NOTA_B1 = 44
# Teclas: fila de números = banco A; fila q-w-e-r-t-y-u-i = banco B.
TECLAS = {"A": [ord(c) for c in "12345678"], "B": [ord(c) for c in "qwertyui"]}

# Perillas del LPD8 (número, longname, etiqueta corta, mensaje, valor inicial).
# Las perillas no cambian con el banco A/B del LPD8 (el banco solo afecta los pads).
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
VERDE = [0.45, 0.85, 0.5, 1.0]
ROJO = [0.95, 0.45, 0.4, 1.0]


def dims_png(archivo):
    with Image.open(os.path.join(RAIZ, "show", archivo)) as im:
        return im.size


def build():
    p = Patch(f"The Hub · Aniversario — Proyección {VERSION} (capas del diseñador)",
              target=8, size=(1000, 820))

    # ---------------- PRESENTACIÓN: paneles ----------------
    p.panel((20, 70, 470, 235), x=1700, y=20, color=(0.11, 0.16, 0.12, 1.0))    # banco A (verde)
    p.panel((510, 70, 470, 235), x=1700, y=60, color=(0.18, 0.11, 0.11, 1.0))   # banco B (rojo)
    p.panel((20, 318, 470, 235), x=1700, y=100)                                 # perillas
    p.panel((510, 318, 470, 115), x=1700, y=140)                                # estado
    p.panel((510, 443, 470, 110), x=1700, y=180)                                # salida
    p.panel((20, 566, 470, 240), x=1700, y=220, color=(0.10, 0.10, 0.12, 1.0))  # monitor
    p.panel((510, 566, 470, 240), x=1700, y=260, color=(0.10, 0.10, 0.12, 1.0)) # cómo usar
    p.title_block(pres_xy=(20, 12), subtitle="LPD8 Wireless · BANCO A (luz verde) obras 1–3 · "
                  "BANCO B (luz roja) obras nuevas · pads 6-7-8 iguales en ambos bancos")
    p.comment("BANCO A — luz verde · teclas 1–8", 30, 60, w=260, pres=(32, 76, 300, 20),
              bold=True, color=VERDE)
    p.comment("BANCO B — luz roja · teclas Q W E R T Y U I", 560, 60, w=300, pres=(522, 76, 340, 20),
              bold=True, color=ROJO)
    p.comment("PERILLAS — iguales en ambos bancos", 30, 300, w=260, pres=(32, 324, 300, 20),
              bold=True)

    # ---------------- JS: motor de escenas ----------------
    p.section("MOTOR: escenas, mezcla y animación suave (show/hub_anim.js)", 520, 420, w=420)
    js = p.obj("js hub_anim.js", 520, 450, w=160, io=(1, 2))
    rte = p.obj("route " + " ".join(c[0] for c in CAPAS), 520, 490, w=420)
    p.connect(js, 0, rte, 0)

    # ---------------- PADS (botones en pantalla) ----------------
    p.section("CONTROL: pads A y B (clic, teclado o LPD8 por MIDI directo; NO usar Assign MIDI Map)",
              30, 20, w=560)
    # Último pad disparado (para saber en qué banco está el LPD8)
    ultimo = p.msg("Último pad: —", 900, 330, w=150, pres=(760, 384, 200, 24))
    p.comment("Así sabes en qué banco está el LPD8:", 900, 300, w=220,
              pres=(760, 364, 210, 18), size=10.0, color=GRIS)
    pad_ids = {}
    neg = p.ui("toggle", 440, 300, 24, 24, pres=(600, 384, 24, 24))
    p.comment("NEGRO", 470, 300, w=60, pres=(628, 388, 60, 18), size=10.0, color=GRIS)
    for banco, num, etiqueta, mensaje in PADS:
        col = (num - 1) % 4
        fila_arriba = num >= 5                    # LPD8: arriba 5–8, abajo 1–4
        off = 0 if banco == "A" else 490
        px = 45 + col * 112 + off
        py = 104 if fila_arriba else 200
        ex = 30 + (num - 1) * 50
        ey = 90 if banco == "A" else 300
        b = p.button(f"pad{banco}{num}", f"Pad {banco}{num}", ex, ey, pres=(px, py, 54, 54))
        pad_ids[(banco, num)] = b
        p.comment(etiqueta, ex, ey + 30, w=48, pres=(px - 12, py + 58, 104, 18), size=10.0,
                  color=GRIS)
        m_ult = p.msg(f"set Último pad: {banco}{num}", ex, ey + 60, w=46)
        p.connect(b, 0, m_ult, 0)
        p.connect(m_ult, 0, ultimo, 0)
        if mensaje:
            m = p.msg(mensaje, ex, ey + 90)
            p.connect(b, 0, m, 0)
            p.connect(m, 0, js, 0)
        else:
            p.connect(b, 0, neg, 0)              # pad 8 de A o de B: alterna negro
    pblack = p.obj("prepend black", 440, 340)
    p.connect(neg, 0, pblack, 0)
    p.connect(pblack, 0, js, 0)

    # Teclado: 1–8 = banco A, q w e r t y u i = banco B
    p.section("TECLADO: 1–8 = banco A · q w e r t y u i = banco B", 450, 150, w=360)
    key = p.obj("key", 450, 175, io=(0, 4))
    for i, banco in enumerate(("A", "B")):
        sel = p.obj("sel " + " ".join(map(str, TECLAS[banco])), 500 + i * 180, 175, w=170)
        p.connect(key, 0, sel, 0)
        for j in range(8):
            p.connect(sel, j, pad_ids[(banco, j + 1)], 0)

    # ---------------- PADS LPD8: ruta MIDI directa (A y B) ----------------
    # notein → stripnote (solo golpes) → [switch] modo toggle → t i i →
    #   (− nota A1 → sel 0..7 → pads A)   y   (− nota B1 → sel 0..7 → pads B)
    # Una nota solo cae en un banco si los rangos no se empalman (aviso abajo).
    p.section("PADS LPD8 DIRECTO: notein → solo golpes → rango de notas A o B → botones", 30, 960, w=560)
    nin_pads = p.obj("notein", 30, 990)
    strip = p.obj("stripnote", 30, 1030, io=(2, 2))
    p.connect(nin_pads, 1, strip, 1)    # velocidad (llega primero: notein sale de der. a izq.)
    p.connect(nin_pads, 0, strip, 0)    # tono
    modo = p.toggle("lpd8_modo_toggle", "LPD8 toggle", 200, 990, pres=(320, 712, 24, 24), init=0)
    p.comment("LPD8 en modo TOGGLE", 230, 990, w=150, pres=(348, 715, 140, 18), size=10.0,
              color=GRIS)
    mas1 = p.obj("+ 1", 200, 1030)
    p.connect(modo, 0, mas1, 0)
    sw = p.obj("switch 2", 30, 1070, io=(3, 1))
    p.connect(mas1, 0, sw, 0)
    p.connect(strip, 0, sw, 1)          # 1 = solo note-on (pads momentáneos, recomendado)
    p.connect(nin_pads, 0, sw, 2)       # 2 = cualquier evento de nota (pads en toggle)
    tii = p.obj("t i i", 30, 1110)
    p.connect(sw, 0, tii, 0)
    bases = {}
    for i, (banco, nota, xpres) in enumerate((("A", NOTA_A1, 96), ("B", NOTA_B1, 236))):
        x = 30 + i * 220
        base = p._param_ui("live.numbox", f"nota_{banco.lower()}1", f"Nota {banco}1", x + 120, 1150,
                           44, 15, (xpres, 714, 44, 18), 0, 127, nota, 1)
        p.comment(f"nota {banco}1", x + 170, 1150, w=60, pres=(xpres - 64, 715, 62, 18), size=10.0,
                  color=VERDE if banco == "A" else ROJO)
        bases[banco] = base
        resta = p.obj(f"- {nota}", x, 1150)
        p.connect(base, 0, resta, 1)
        p.connect(tii, 1 - i, resta, 0)
        selp = p.obj("sel 0 1 2 3 4 5 6 7", x, 1190, w=160)
        p.connect(resta, 0, selp, 0)
        for j in range(8):
            p.connect(selp, j, pad_ids[(banco, j + 1)], 0)

    # Aviso: ¿los rangos de notas de A y B se empalman?
    pk = p.obj("pak 36 44", 480, 1150)
    p.connect(bases["A"], 0, pk, 0)
    p.connect(bases["B"], 0, pk, 1)
    ex_ = p.obj("expr abs($i1 - $i2) < 8", 480, 1190, w=170)
    p.connect(pk, 0, ex_, 0)
    chg = p.obj("change", 480, 1230)
    p.connect(ex_, 0, chg, 0)
    sel_ok = p.obj("sel 0 1", 480, 1270)
    p.connect(chg, 0, sel_ok, 0)
    m_ok = p.msg("set Bancos A y B sin empalme: cada pad dispara una sola cosa.", 480, 1310, w=300)
    m_mal = p.msg("set ¡AVISO! A y B comparten notas: corrige 'nota B1' con el monitor.", 480, 1340,
                  w=300)
    p.connect(sel_ok, 0, m_ok, 0)
    p.connect(sel_ok, 1, m_mal, 0)
    aviso = p.msg("Bancos: —", 480, 1380, w=320, pres=(32, 744, 450, 22))
    p.connect(m_ok, 0, aviso, 0)
    p.connect(m_mal, 0, aviso, 0)

    # ---------------- PERILLAS ----------------
    p.section("CONTROL: perillas LPD8 (mapeadas con Assign MIDI Map: CC 1–8)", 560, 20, w=400)
    for num, longname, etiqueta, mensaje, init in KNOBS:
        col = (num - 1) % 4
        fila_arriba = num <= 4
        px = 50 + col * 112
        py = 350 if fila_arriba else 446
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
    p.section("ESTADO: lo que reporta el motor", 720, 420, w=260)
    rst = p.obj("route escena fade negro", 720, 530, w=170)
    p.connect(js, 1, rst, 0)
    pset = p.obj("prepend set Escena", 720, 560)
    p.connect(rst, 0, pset, 0)
    est = p.msg("Escena —", 720, 590, w=240, pres=(586, 328, 384, 24))
    p.connect(pset, 0, est, 0)
    p.comment("Activa:", 700, 590, w=60, pres=(522, 330, 62, 20), bold=True)
    fl = p.ui("flonum", 900, 590, 60, 22, pres=(522, 384, 50, 22))
    p.connect(rst, 1, fl, 0)
    p.comment("s transición", 960, 590, w=90, pres=(522, 364, 80, 18), size=10.0, color=GRIS)
    p.comment("A1–A5 obras 1–3 y cruces · B1–B5 obras nuevas · 6 pulso · 7 segura · 8 negro "
              "(en ambos bancos)", 720, 620, w=360, pres=(522, 412, 450, 18), size=9.5, color=GRIS)

    # ---------------- CARGA DE IMÁGENES + VIDEOPLANES ----------------
    p.section("IMÁGENES → TEXTURAS: cada PNG (con alfa) a un videoplane. "
              "Archivos en la MISMA carpeta que el patch.", 30, 640, w=700)
    lb = p.obj("loadbang", 30, 670)
    dl = p.obj("delay 600", 100, 670, io=(2, 1))
    p.connect(lb, 0, dl, 0)
    recargar = p.button("recargar", "Recargar", 200, 670, pres=(700, 460, 30, 30))
    p.comment("Recargar imágenes", 230, 670, w=120, pres=(734, 466, 120, 20), size=10.0)
    p.connect(recargar, 0, dl, 0)
    n = len(CAPAS)
    tr = p.obj("t " + " ".join(["b"] * n), 30, 700, w=30 * n)
    p.connect(dl, 0, tr, 0)
    for i, (capa, archivo, layer) in enumerate(CAPAS):
        w, h = dims_png(archivo)
        x = 30 + i * 200
        m = p.msg(f"importmovie {archivo}, bang", x, 740, w=190)
        p.connect(tr, n - 1 - i, m, 0)
        mx = p.obj(f"jit.matrix 4 char {w} {h}", x, 770)
        p.connect(m, 0, mx, 0)
        vp = p.obj(f"jit.gl.videoplane hub @layer {layer} @blend_enable 1 @depth_enable 0 "
                   f"@transform_reset 1 @color 1 1 1 0 @enable 0", x, 850, w=190, h=50)
        p.connect(mx, 0, vp, 0)
        p.connect(rte, i, vp, 0)
        p.comment(f"capa {layer}: {capa}", x, 820, w=180, size=10.0, color=GRIS)

    # ---------------- RELOJ + MUNDO ----------------
    p.section("SALIDA: ventana de proyección (esc = pantalla completa)", 1100, 20, w=420)
    anim = p.toggle("animar", "Animación", 1100, 50, pres=(530, 460, 30, 30), init=1)
    p.comment("Animación", 1130, 50, w=80, pres=(564, 466, 80, 20), size=10.0)
    qm = p.obj("qmetro 16", 1100, 80)
    p.connect(anim, 0, qm, 0)
    p.connect(qm, 0, js, 0)
    init = p.obj("loadbang", 1210, 50)
    dl2 = p.obj("delay 100", 1210, 80, io=(2, 1))
    p.connect(init, 0, dl2, 0)
    m_init = p.msg("scene 1, snap", 1210, 110)
    p.connect(dl2, 0, m_init, 0)
    p.connect(m_init, 0, js, 0)

    fs = p.toggle("pantalla_completa", "Pantalla", 1100, 150, pres=(530, 505, 30, 30), init=0)
    p.comment("Pantalla completa (o tecla esc en la ventana)", 1130, 150, w=200,
              pres=(564, 511, 260, 20), size=10.0)
    pfs = p.obj("prepend fullscreen", 1100, 180)
    p.connect(fs, 0, pfs, 0)
    world = p.obj("jit.world hub @enable 1 @erase_color 0 0 0 1 @size 960 540 "
                  "@fsmenubar 0 @fsaa 1", 1100, 240, w=420)
    p.connect(pfs, 0, world, 0)
    fps = p.ui("jit.fpsgui", 1100, 280, 80, 35, pres=(880, 460, 80, 35))
    p.comment("fps", 1190, 280, w=40, pres=(850, 468, 30, 20), size=10.0)
    p.connect(world, 1, fps, 0)   # outlet 1 = bang por cuadro dibujado

    # ---------------- MONITOR MIDI + PUERTO ----------------
    ctl, nin = p.midi_monitor(x=1100, y=400, pres=(32, 576))
    p.port_menu("Puerto MIDI del LPD8 (monitor y pads)", [ctl, nin, nin_pads], 1100, 500,
                pres=(32, 644, 200, 22))
    p.comment("Golpea un pad y mira el TONO: así sabes la nota de cada banco. Velocidad > 0 al "
              "golpear y 0 al soltar = MOMENTARY; golpes alternos en 0 = TOGGLE.",
              1100, 580, w=330, pres=(32, 672, 450, 34), size=10.0, color=GRIS)
    p.comment("Vizzie: K7 ya publica [s vz_k7] 0–1.", 1100, 620, w=330,
              pres=(32, 776, 450, 18), size=10.0, color=GRIS)

    # ---------------- CÓMO USAR ----------------
    p.usage_notes([
        "1. Deja los PNG y hub_anim.js en la MISMA carpeta que este patch.",
        "2. Arrastra la ventana 'hub' al proyector → esc (pantalla completa).",
        "3. Elige el LPD8 en 'Puerto MIDI'. Perillas: ya mapeadas (CC 1–8).",
        "4. Pads: NO los mapees; entran por MIDI directo.",
        "   Botón BANK del LPD8: verde = A (obras 1–3), rojo = B (nuevas).",
        "   Revisa 'nota A1' y 'nota B1' con el monitor (golpea A1 y B1).",
        "   El aviso 'Bancos' debe decir 'sin empalme'.",
        "5. Pads 6 · 7 · 8 hacen lo mismo en ambos bancos:",
        "   pulso · escena segura · negro on/off.",
        "6. 'Último pad' muestra en qué banco estás.",
        "7. Teclado: 1–8 = banco A · q w e r t y u i = banco B.",
    ], pres=(522, 576, 450, 222), x=1100, y=700)

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
