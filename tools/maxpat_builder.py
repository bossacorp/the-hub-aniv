#!/usr/bin/env python3
"""
maxpat_builder.py — genera patches de Max (.maxpat) que abren en modo presentación,
con cables conectados y comentados por detrás, controles con Parameter Mode (mapeables
con "Assign MIDI Map") y un mapa de cables en Markdown para las instrucciones de uso.

USO COMO BIBLIOTECA (lo normal):

    import sys; sys.path.insert(0, "<carpeta-donde-guardaste-este-archivo>")
    from maxpat_builder import Patch

    p = Patch("Feedback de cámara", target=8, size=(900, 560))   # target=8 → Max 8 compatible
    p.section("ENTRADA: cámara USB", x=30, y=30)                   # comentario de bloque (vista edición)
    cam  = p.obj("jit.grab @output_texture 1", 30, 60)
    world = p.obj("jit.world feedback @enable 1 @fsmenubar 0", 30, 300)
    dial = p.dial("fb_cantidad", "Feedback", x=300, y=60, pres=(40, 120, 60, 80),
                  lo=0.0, hi=0.98, init=0.6)
    p.connect(cam, 0, world, 0)                                     # (origen, outlet, destino, inlet)
    p.title_block(pres_xy=(20, 10), subtitle="Mueve el fader 1 del MIDI Mix")
    p.midi_monitor(x=600, y=60, pres=(620, 400))
    p.usage_notes(["1. Enciende la cámara...", "2. ..."], pres=(20, 440, 560, 100))
    warnings = p.validate()            # revisa IDs, índices de outlets/inlets, objetos de Max 9
    p.save("feedback_camara.maxpat")
    p.save_wiring_md("feedback_camara_cables.md")

Notas:
- Max recalcula inlets/outlets reales al abrir el patch; la tabla IO de abajo solo sirve para
  validar que no conectes a un outlet que no existe. Objeto desconocido → aviso, no error.
- No fabrica módulos Vizzie (sus nombres internos no están verificados). Para Vizzie usa
  p.send_out("nombre", fuente) y en la guía indica qué módulo arrastrar y qué `receive` conectar.
- Paneles se dibujan detrás (se agregan con background=1).
- Para `js`/`v8` con varios outlets, pasa io=(inlets, outlets) a p.obj(...).

CLI:
    python maxpat_builder.py --demo salida.maxpat     # patch de ejemplo
    python maxpat_builder.py --validate archivo.maxpat [--target 8]
"""

import json
import re
import sys

MAX9_ONLY_PREFIXES = ("v8", "v8ui", "v8.codebox", "jit.fx.", "jit.geom.", "abl.", "jit.ui",
                      "node.codebox", "dict.codebox", "coll.codebox", "gen.codebox",
                      "jit.gen.codebox", "jit.pix.codebox", "jit.gl.pix.codebox", "osc.codebox",
                      "text.codebox", "messageview", "listbox", "textbox")

# (inlets, outlets) aproximados de objetos comunes. None = depende de argumentos (ver _io()).
IO = {
    "jit.world": (1, 3), "jit.grab": (1, 2), "jit.movie": (1, 2), "jit.playlist": (1, 3),
    "jit.gl.texture": (1, 2), "jit.gl.slab": (2, 2), "jit.gl.pix": (2, 2),
    "jit.gl.videoplane": (1, 2), "jit.gl.syphonserver": (1, 1), "jit.gl.syphonclient": (1, 2),
    "jit.gl.layer": (1, 2), "jit.gl.mesh": (9, 2), "jit.slide": (1, 2), "jit.rgb2luma": (1, 2), "v8": (1, 1), "jit.gl.gridshape": (1, 2),
    "jit.matrix": (1, 2), "jit.op": (2, 2), "jit.bfg": (1, 2), "jit.gl.bfg": (1, 2),
    "send": (1, 0), "s": (1, 0), "receive": (1, 1), "r": (1, 1),
    "loadbang": (1, 1), "loadmess": (1, 1), "metro": (2, 1), "qmetro": (2, 1), "print": (1, 0),
    "scale": (6, 1), "slide": (3, 1), "prepend": (1, 1), "append": (1, 1),
    "*": (2, 1), "/": (2, 1), "%": (2, 1), "+": (2, 1), "-": (2, 1), "!-": (2, 1), "clip": (3, 1),
    "noteout": (3, 0), "ctlout": (3, 0), "change": (1, 3), "speedlim": (2, 1),
    "peakamp~": (2, 1), "line": (3, 2), "random": (2, 1), "average~": (2, 1), "toggle": (1, 1), "button": (1, 1),
    "js": (1, 1), "pak": None, "node.script": (1, 2), "udpreceive": (1, 1), "udpsend": (1, 0),
    "pattrstorage": (1, 3), "autopattr": (1, 4), "mappings": (1, 1),
    "midiinfo": (2, 1), "stripnote": (2, 2), "split": (3, 2), "int": (2, 1), "i": (2, 1),
    "float": (2, 1), "f": (2, 1), "deferlow": (1, 1), "jit.fpsgui": (1, 1),
}
UI_IO = {
    "live.dial": (1, 2), "live.slider": (1, 2), "live.toggle": (1, 1), "live.button": (1, 1),
    "comment": (1, 0), "message": (2, 1), "panel": (1, 0), "number": (1, 2), "flonum": (1, 2),
    "toggle": (1, 1), "button": (1, 1), "jit.pwindow": (1, 2), "jit.fpsgui": (1, 1),
    "umenu": (1, 3),
}


def _io(text):
    """Devuelve (inlets, outlets) para un objeto por su texto, o None si es desconocido."""
    toks = text.split()
    name = toks[0]
    args = [t for t in toks[1:] if not t.startswith("@")]
    # cortar argumentos en el primer atributo
    if any(t.startswith("@") for t in toks[1:]):
        args = []
        for t in toks[1:]:
            if t.startswith("@"):
                break
            args.append(t)
    n = len(args)
    if name == "ctlin":
        return (1, 3 - min(n, 2))
    if name == "notein":
        return (1, 3 if n == 0 else 2)
    if name in ("route", "routepass", "select", "sel"):
        return (2 if n == 1 else 1, n + 1)
    if name in ("trigger", "t"):
        return (1, max(n, 1))
    if name == "pack" or name == "pak":
        return (max(n, 2), 1)
    if name == "unpack":
        return (1, max(n, 2))
    if name == "gate":
        return (2, int(args[0]) if args and args[0].isdigit() else 1)
    if name == "expr":
        nums = [int(m) for m in re.findall(r"\$[fis](\d+)", text)]
        return (max(nums) if nums else 1, 1)
    if name == "adc~":
        return (1, max(n, 2))
    return IO.get(name)


class Patch:
    def __init__(self, title, target=8, size=(1000, 650)):
        self.title = title
        self.target = target
        self.size = size
        self.boxes = []
        self.lines = []
        self.meta = {}  # id -> dict(text, kind, io)
        self._n = 0
        self.params = {}

    # ---------- primitivas ----------
    def _id(self):
        self._n += 1
        return f"obj-{self._n}"

    def _add(self, box, text, io, pres=None, background=False):
        bid = self._id()
        box["id"] = bid
        box["numinlets"], box["numoutlets"] = io if io else (1, 1)
        box.setdefault("outlettype", [""] * box["numoutlets"])
        if pres:
            box["presentation"] = 1
            box["presentation_rect"] = list(map(float, pres))
        if background:
            box["background"] = 1
        self.boxes.append({"box": box})
        self.meta[bid] = {"text": text, "io": io}
        return bid

    def obj(self, text, x, y, w=None, h=22, pres=None, io=None):
        """Objeto normal (newobj): p.obj('jit.grab @output_texture 1', x, y).
        io=(inlets, outlets) para fijar a mano los de objetos como `js`/`v8` con varios outlets."""
        w = w or max(60, 7 * len(text) + 16)
        io = io or _io(text)
        return self._add({"maxclass": "newobj", "text": text,
                          "patching_rect": [x, y, w, h]}, text, io, pres)

    def msg(self, text, x, y, w=None, pres=None):
        w = w or max(40, 7 * len(text) + 14)
        return self._add({"maxclass": "message", "text": text,
                          "patching_rect": [x, y, w, 22]}, f"[msg] {text}", UI_IO["message"], pres)

    def comment(self, text, x, y, w=260, h=None, pres=None, size=12.0, bold=False, color=None):
        h = h or 20 * (1 + text.count("\n"))
        box = {"maxclass": "comment", "text": text, "patching_rect": [x, y, w, h],
               "fontsize": size, "linecount": 1 + text.count("\n")}
        if bold:
            box["fontface"] = 1
        if color:
            box["textcolor"] = color
        return self._add(box, f"[comentario] {text[:40]}", UI_IO["comment"], pres)

    def section(self, text, x, y, w=300):
        """Comentario de bloque en la vista de edición (no en presentación)."""
        return self.comment(f"▼ {text}", x, y, w=w, bold=True, color=[0.9, 0.55, 0.1, 1.0])

    def panel(self, pres, color=(0.13, 0.13, 0.15, 1.0), x=None, y=None):
        """Panel de fondo para agrupar controles en presentación."""
        px, py, pw, ph = pres
        return self._add({"maxclass": "panel", "patching_rect": [x if x is not None else self.size[0] + 40,
                          y if y is not None else py, pw, ph],
                          "bgcolor": list(color), "rounded": 8, "mode": 0},
                         "[panel]", UI_IO["panel"], pres, background=True)

    def _param_ui(self, maxclass, longname, shortname, x, y, w, h, pres, lo, hi, init, ptype,
                  enum=None):
        if longname in self.params:
            raise ValueError(f"parameter_longname repetido: {longname}")
        valueof = {"parameter_longname": longname, "parameter_shortname": shortname,
                   "parameter_type": ptype, "parameter_mmin": float(lo),
                   "parameter_mmax": float(hi), "parameter_initial_enable": 1,
                   "parameter_initial": [init]}
        if enum:
            valueof["parameter_enum"] = enum
        if ptype == 0:
            valueof["parameter_unitstyle"] = 1
        box = {"maxclass": maxclass, "parameter_enable": 1, "varname": longname,
               "patching_rect": [x, y, w, h],
               "saved_attribute_attributes": {"valueof": valueof}}
        bid = self._add(box, f"[{maxclass}] {longname}", UI_IO[maxclass], pres)
        self.params[longname] = bid
        return bid

    def dial(self, longname, label, x, y, pres=None, lo=0.0, hi=1.0, init=0.0):
        """Perilla mapeable (live.dial). Sale float entre lo y hi por el outlet 0."""
        return self._param_ui("live.dial", longname, label, x, y, 44, 48, pres, lo, hi, init, 0)

    def slider(self, longname, label, x, y, pres=None, lo=0.0, hi=1.0, init=0.0):
        """Fader mapeable (live.slider). Sale float por el outlet 0."""
        return self._param_ui("live.slider", longname, label, x, y, 39, 106, pres, lo, hi, init, 0)

    def toggle(self, longname, label, x, y, pres=None, init=0):
        """Interruptor mapeable (live.toggle): 0/1."""
        return self._param_ui("live.toggle", longname, label, x, y, 24, 24, pres, 0, 1, init, 2,
                              enum=["off", "on"])

    def button(self, longname, label, x, y, pres=None):
        """Botón de disparo mapeable (live.button): bang/1."""
        return self._param_ui("live.button", longname, label, x, y, 24, 24, pres, 0, 1, 0, 2,
                              enum=["off", "on"])

    def ui(self, maxclass, x, y, w, h, pres=None, **attrs):
        """Otro UI (jit.pwindow, jit.fpsgui, number, flonum, toggle, button...)."""
        box = {"maxclass": maxclass, "patching_rect": [x, y, w, h]}
        box.update(attrs)
        return self._add(box, f"[{maxclass}]", UI_IO.get(maxclass), pres)

    def connect(self, src, outlet, dst, inlet):
        self.lines.append({"patchline": {"source": [src, outlet], "destination": [dst, inlet]}})

    # ---------- bloques de alto nivel ----------
    def title_block(self, pres_xy=(20, 10), subtitle=""):
        x, y = pres_xy
        self.comment(self.title, 30, 4, w=500, pres=(x, y, 600, 30), size=20.0, bold=True)
        if subtitle:
            self.comment(subtitle, 30, 28, w=500, pres=(x, y + 30, 600, 20), size=12.0,
                         color=[0.7, 0.7, 0.7, 1.0])

    def send_out(self, name, src, outlet=0, x=None, y=None):
        """Publica un valor con [s name] (p. ej. para conectarlo a una entrada de Vizzie con [r name])."""
        sx = x if x is not None else 0
        sy = y if y is not None else 0
        s = self.obj(f"s {name}", sx, sy)
        self.connect(src, outlet, s, 0)
        return s

    def midi_monitor(self, x, y, pres=None):
        """Muestra último CC (valor, número, canal) y última nota (pitch, velocidad, canal)."""
        self.section("MONITOR MIDI: verifica qué manda cada control", x, y - 24, w=340)
        ctl = self.obj("ctlin", x, y)
        nin = self.obj("notein", x + 170, y)
        boxes = []
        for i in range(3):
            nb = self.ui("number", x + i * 50, y + 40, 46, 22,
                         pres=(pres[0] + i * 52, pres[1] + 20, 48, 22) if pres else None)
            self.connect(ctl, i, nb, 0)
            boxes.append(nb)
        for i in range(3):
            nb = self.ui("number", x + 170 + i * 50, y + 40, 46, 22,
                         pres=(pres[0] + 170 + i * 52, pres[1] + 20, 48, 22) if pres else None)
            self.connect(nin, i, nb, 0)
            boxes.append(nb)
        if pres:
            self.comment("Monitor MIDI  —  CC: valor · número · canal      Nota: tono · velocidad · canal",
                         x, y + 70, w=340, pres=(pres[0], pres[1], 360, 18), size=10.0,
                         color=[0.7, 0.7, 0.7, 1.0])
        return ctl, nin

    def port_menu(self, label, targets, x, y, pres=None, direction="in"):
        """Menú de puerto MIDI (midiinfo → umenu) que fija el puerto de los objetos `targets`
        (notein/ctlin si direction='in'; noteout/ctlout si 'out'). Evita que dos controladores
        con las mismas notas/CC se mezclen. Se llena al abrir el patch (loadbang)."""
        lb = self.obj("loadbang", x, y)
        mi = self.obj("midiinfo", x, y + 30)
        # entradas: número en inlet derecho (-1 = no cambiar selección); salidas: bang en el izquierdo
        if direction == "in":
            m1 = self.msg("-1", x + 70, y)
            self.connect(lb, 0, m1, 0)
            self.connect(m1, 0, mi, 1)
        else:
            self.connect(lb, 0, mi, 0)
        um = self.ui("umenu", x, y + 60, 180, 22, pres=pres)
        self.connect(mi, 0, um, 0)
        for t in targets:
            self.connect(um, 1, t, 0)   # outlet 1 de umenu = nombre del puerto
        if pres:
            self.comment(label, x + 190, y + 60, w=200,
                         pres=(pres[0], pres[1] - 18, 200, 18), size=10.0,
                         color=[0.7, 0.7, 0.7, 1.0])
        return um

    def usage_notes(self, lines, pres, x=30, y=None):
        text = "CÓMO USAR\n" + "\n".join(lines)
        yy = y if y is not None else self.size[1] + 40
        return self.comment(text, x, yy, w=pres[2], h=pres[3], pres=pres, size=11.0)

    # ---------- validación y salida ----------
    def validate(self):
        warns = []
        ids = set(self.meta)
        for ln in self.lines:
            (s, so), (d, di) = ln["patchline"]["source"], ln["patchline"]["destination"]
            for bid in (s, d):
                if bid not in ids:
                    warns.append(f"ERROR conexión con id inexistente: {bid}")
            if s in ids and self.meta[s]["io"]:
                if so >= self.meta[s]["io"][1]:
                    warns.append(f"outlet {so} fuera de rango en '{self.meta[s]['text']}'")
            if d in ids and self.meta[d]["io"]:
                if di >= self.meta[d]["io"][0]:
                    warns.append(f"inlet {di} fuera de rango en '{self.meta[d]['text']}'")
        for bid, m in self.meta.items():
            name = m["text"].split()[0]
            if m["io"] is None:
                warns.append(f"aviso: '{m['text']}' no está en la tabla IO (verifícalo al abrir)")
            if self.target < 9 and name.startswith(MAX9_ONLY_PREFIXES):
                warns.append(f"INCOMPATIBLE con Max 8: '{m['text']}'")
        return warns

    def to_dict(self):
        major, minor = (8, 5) if self.target < 9 else (9, 0)
        parameters = {bid: [ln, ln, 0] for ln, bid in self.params.items()}
        parameters["inherited_shortname"] = 1
        # paneles primero para que queden detrás
        boxes = sorted(self.boxes, key=lambda b: 0 if b["box"].get("background") else 1)
        return {"patcher": {
            "fileversion": 1,
            "appversion": {"major": major, "minor": minor, "revision": 0,
                           "architecture": "x64", "modernui": 1},
            "classnamespace": "box",
            "rect": [80.0, 80.0, float(self.size[0]), float(self.size[1])],
            "openinpresentation": 1,
            "default_fontsize": 12.0, "default_fontface": 0, "default_fontname": "Arial",
            "gridonopen": 1, "gridsize": [15.0, 15.0], "gridsnaponopen": 1,
            "toolbarvisible": 1, "boxanimatetime": 200,
            "description": self.title, "digest": "", "tags": "", "style": "",
            "boxes": boxes, "lines": self.lines,
            "parameters": parameters,
            "dependency_cache": [], "autosave": 0,
        }}

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=1, ensure_ascii=False)
        return path

    def wiring_md(self):
        out = [f"# Mapa de cables — {self.title}", "",
               "| # | Desde (outlet) | Hacia (inlet) |", "|---|---|---|"]
        for i, ln in enumerate(self.lines, 1):
            (s, so), (d, di) = ln["patchline"]["source"], ln["patchline"]["destination"]
            out.append(f"| {i} | `{self.meta[s]['text']}` ({so}) | `{self.meta[d]['text']}` ({di}) |")
        return "\n".join(out) + "\n"

    def save_wiring_md(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.wiring_md())
        return path


def validate_file(path, target=8):
    """Valida un .maxpat existente: JSON, IDs de conexiones y objetos de Max 9."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    pt = d["patcher"]
    ids, warns = {}, []
    for b in pt.get("boxes", []):
        bx = b["box"]
        ids[bx["id"]] = bx
        txt = bx.get("text", "")
        if target < 9 and bx.get("maxclass") == "newobj" and txt.split()[:1] and \
                txt.split()[0].startswith(MAX9_ONLY_PREFIXES):
            warns.append(f"INCOMPATIBLE con Max 8: '{txt}'")
    for ln in pt.get("lines", []):
        (s, so), (d2, di) = ln["patchline"]["source"], ln["patchline"]["destination"]
        for bid, idx, kind in ((s, so, "numoutlets"), (d2, di, "numinlets")):
            if bid not in ids:
                warns.append(f"ERROR conexión a id inexistente {bid}")
            elif idx >= ids[bid].get(kind, 99):
                warns.append(f"índice {idx} fuera de rango ({kind}) en {ids[bid].get('text', ids[bid]['maxclass'])}")
    if not pt.get("openinpresentation"):
        warns.append("aviso: no abre en modo presentación")
    return warns


def _demo(path):
    p = Patch("Demo — cámara con feedback y fader", target=8, size=(980, 620))
    p.panel((10, 90, 300, 260))
    p.title_block(subtitle="Fader 1 = cantidad de feedback · Pad = negro")
    p.section("ENTRADA: cámara USB a textura", 30, 60)
    on = p.toggle("camara_on", "Cámara", 30, 90, pres=(30, 110, 24, 24), init=1)
    cam = p.obj("jit.grab @output_texture 1", 30, 140)
    op = p.msg("open", 150, 115, pres=(30, 150, 50, 22))
    p.connect(op, 0, cam, 0)
    metro = p.obj("qmetro 33", 30, 115)
    p.connect(on, 0, metro, 0)
    p.connect(metro, 0, cam, 0)
    p.section("CONTROL: fader de feedback (mapéalo con Assign MIDI Map)", 300, 60)
    fb = p.slider("feedback", "Feedback", 300, 90, pres=(90, 110, 39, 106), lo=0.0, hi=0.98, init=0.5)
    p.send_out("fb_amount", fb, x=300, y=210)
    p.section("SALIDA", 30, 260)
    world = p.obj("jit.world demo @enable 1", 30, 290)
    p.connect(cam, 0, world, 0)
    p.ui("jit.fpsgui", 30, 330, 80, 35, pres=(160, 110, 80, 35))
    p.midi_monitor(x=560, y=90, pres=(20, 380))
    p.usage_notes(["1. No necesitas instalar nada: solo Max 8+.", "2. Activa 'Cámara'.",
                   "3. Clic derecho en el fader → Assign MIDI Map → mueve el fader 1 del MIDI Mix."],
                  pres=(20, 440, 560, 90))
    for w in p.validate():
        print(w)
    p.save(path)
    p.save_wiring_md(re.sub(r"\.maxpat$", "", path) + "_cables.md")
    print("ok:", path)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--demo":
        _demo(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "--validate":
        tgt = int(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else 8
        ws = validate_file(sys.argv[2], tgt)
        print("\n".join(ws) if ws else "sin avisos")
    else:
        print(__doc__)
