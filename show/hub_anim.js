/*
  hub_anim.js — motor de escenas y animación suave para "The Hub · Aniversario"
  ---------------------------------------------------------------------------
  Objeto en Max:  [js hub_anim.js]   (Max 8 y Max 9; ES5, sin v8)

  Qué hace
    - Recibe un "bang" por cuadro (qmetro 16 en el patch).
    - Calcula para cada capa (un jit.gl.videoplane por imagen) su opacidad,
      escala, posición y rotación, y lo manda por el outlet 0 como
          <capa> color r g b a
          <capa> scale sx sy 1
          <capa> position x y 0
          <capa> rotatexyz 0 0 grados
          <capa> enable 0|1
      En el patch, [route foto tinta luna ...] reparte cada mensaje a su
      videoplane (un nombre por capa, mismo orden que NOMBRES).
    - Outlet 1: estado para la interfaz ("escena 2 Luna").

  Mensajes que entiende (inlet 0), todos los valores de perilla son 0–1
    bang            avanza un cuadro
    scene n         cambia a la escena n con fundido. Numeración = pad del LPD8:
                      banco A: 1–5 escenas, 6 segura (pad 7)
                      banco B: 11–15 escenas (pads B1–B5)
    snap            salta a la escena actual sin fundido (al abrir el patch)
    mix f           K1  mezcla entre las capas de la escena (A ↔ B)
    speed f         K2  velocidad del movimiento (0 = congelado)
    amp f           K3  amplitud del movimiento (respiración, deriva, giro)
    zoom f          K4  encuadre global (0.5 = tamaño natural)
    fade f          K5  tiempo de transición entre escenas (0.2 s – 20 s)
    tone f          K6  tono de color: 0 frío · 0.5 neutro · 1 cálido
    master f        K8  brillo / fundido general
    pulse [v]       acento: empuja la mezcla hacia B y da un "latido" de escala
    black 0|1       fundido a negro (pad 8)

  Coordenadas: los videoplanes usan @transform_reset 1, así que el alto de la
  ventana va de -1 a 1 y el ancho de -aspecto a +aspecto (16:9 → ±1.78).
  Una capa con escala 1 ocupa todo el alto de la pantalla.

  Para afinar una escena: edita ESCENAS más abajo y guarda. Con autowatch = 1
  Max recarga el archivo solo (la escena actual se conserva al recargar).
*/

autowatch = 1;
inlets = 1;
outlets = 2;
setinletassist(0, "bang por cuadro / mensajes de control");
setoutletassist(0, "a [route] de capas → jit.gl.videoplane");
setoutletassist(1, "estado para la interfaz");

// ------------------------------------------------------------------
// CAPAS: nombre → proporción ancho/alto de la imagen y pivote de giro
// (pivote en coordenadas locales del plano, -1..1; la luna gira sobre
//  su propio centro, que está un poco arriba del centro del lienzo).
// El orden de dibujo NO se define aquí: es el @layer de cada videoplane.
// ------------------------------------------------------------------
var CAPAS = {
    foto:    { asp: 0.75, piv: [0, 0] },     // e3_bosque_foto.png      (fondo opaco)
    tinta:   { asp: 1.0,  piv: [0, 0] },     // e1_mano_tinta.png       (fondo opaco)
    luna:    { asp: 1.0,  piv: [0, 0.14] },  // e2_luna_luna.png        (alfa)
    paisaje: { asp: 1.0,  piv: [0, 0] },     // e2_luna_paisaje.png     (alfa)
    figuras: { asp: 0.75, piv: [0, 0] },     // e3_bosque_figuras.png   (alfa)
    boceto:  { asp: 1.0,  piv: [0, 0] },     // e1_mano_boceto.png      (alfa)
    // Obra 4 — "Sombrero" (9:16). La pintura nocturna es el MISMO encuadre que la
    // foto: "sigue" la obliga a moverse idéntica a la foto (misma fase y geometría)
    // para que nunca se desalineen.
    sombrero: { asp: 721 / 1280, piv: [0, 0] },                    // e4_sombrero_foto.png  (opaca)
    noche:    { asp: 721 / 1280, piv: [0, 0], sigue: "sombrero" }, // e4_sombrero_noche.png (alfa por brillo)
    // Obra 5 — "Hongo y criatura" (9:16). Encuadres distintos: cada capa se mueve
    // por su lado (la criatura flota sobre la foto). La criatura gira sobre su torso.
    hongo:    { asp: 900 / 1600, piv: [0, 0] },                    // e5_hongo_foto.png     (opaca)
    criatura: { asp: 900 / 1600, piv: [0, 0.2] },                  // e5_hongo_criatura.png (alfa por brillo)
    // Obra 6 — "Nahual" (3:4). La pintura está calcada sobre la foto (el jaguar se
    // sienta en la silla, los animales en las ramas): va pegada a la foto.
    ficus:    { asp: 960 / 1280, piv: [0, 0] },                    // e6_nahual_foto.png     (opaca)
    nahual:   { asp: 960 / 1280, piv: [0, 0], sigue: "ficus" },    // e6_nahual_animales.png (alfa por brillo)
    // Obra 7 — "Acuarela y noche" (panorámica 2.74:1). Encuadres distintos.
    // Con s = 0.65 el ancho llena una pantalla 16:9 (franjas negras arriba y abajo).
    noche7:   { asp: 1280 / 468, piv: [0, 0] },                    // e7_acuarela_noche.png   (opaca)
    reflejo:  { asp: 1280 / 468, piv: [0, 0] }                     // e7_acuarela_reflejo.png (alfa: papel fuera, color pastel)
};
// Orden de proceso. Una capa que "sigue" a otra va DESPUÉS de su guía.
var NOMBRES = ["foto", "tinta", "luna", "paisaje", "figuras", "boceto", "sombrero", "noche",
               "hongo", "criatura", "ficus", "nahual", "noche7", "reflejo"];

// ------------------------------------------------------------------
// ESCENAS
//   a0 / a1 : opacidad con la perilla de mezcla (K1) en 0 y en 1
//   s       : escala (1 = alto de pantalla)       x, y : posición
//   resp    : respiración (escala, ±fracción)      deriva : desplazamiento lento
//   giro    : rotación lenta (± grados)
// Las capas que no aparecen en una escena se apagan.
// ------------------------------------------------------------------
var ESCENAS = {
    1: { nombre: "Mano y flor", capas: {
        tinta:  { a0: 0.0, a1: 1.0,  s: 1.0,  x: 0, y: 0, resp: 0.015, deriva: 0.012, giro: 0 },
        boceto: { a0: 1.0, a1: 0.35, s: 1.0,  x: 0, y: 0, resp: 0.025, deriva: 0.035, giro: 0.6 }
    }},
    2: { nombre: "Luna", capas: {
        luna:    { a0: 0.45, a1: 1.0, s: 1.0, x: 0, y: 0, resp: 0.035, deriva: 0.008, giro: 3.0 },
        paisaje: { a0: 1.0,  a1: 1.0, s: 1.0, x: 0, y: 0, resp: 0.008, deriva: 0.010, giro: 0 }
    }},
    3: { nombre: "Bosque", capas: {
        foto:    { a0: 1.0,  a1: 1.0, s: 1.0, x: 0, y: 0, resp: 0.020, deriva: 0.015, giro: 0 },
        figuras: { a0: 0.15, a1: 1.0, s: 1.0, x: 0, y: 0, resp: 0.030, deriva: 0.045, giro: 0.8 }
    }},
    4: { nombre: "Luna en el bosque", capas: {
        foto:    { a0: 1.0, a1: 1.0, s: 1.0,  x: 0,    y: 0,    resp: 0.020, deriva: 0.015, giro: 0 },
        luna:    { a0: 0.9, a1: 0.5, s: 0.42, x: 0.02, y: 0.38, resp: 0.040, deriva: 0.010, giro: 4.0 },
        figuras: { a0: 0.0, a1: 0.9, s: 1.0,  x: 0,    y: 0,    resp: 0.030, deriva: 0.045, giro: 0.8 }
    }},
    5: { nombre: "Boceto en el paisaje", capas: {
        luna:    { a0: 0.9,  a1: 0.35, s: 1.0, x: 0, y: 0, resp: 0.030, deriva: 0.008, giro: 2.0 },
        paisaje: { a0: 1.0,  a1: 1.0,  s: 1.0, x: 0, y: 0, resp: 0.008, deriva: 0.010, giro: 0 },
        boceto:  { a0: 0.25, a1: 0.9,  s: 1.0, x: 0, y: 0, resp: 0.025, deriva: 0.035, giro: 0.6 }
    }},
    6: { nombre: "Segura (luna sola)", capas: {
        luna:    { a0: 1.0, a1: 1.0, s: 0.85, x: 0, y: -0.05, resp: 0.020, deriva: 0.004, giro: 1.5 }
    }},

    // ---------------- BANCO B (pads B1–B5 = escenas 11–15) ----------------
    11: { nombre: "Sombrero: día y noche", capas: {
        // K1 en 0: foto de día · 0.5: la noche se enciende sobre la foto · 1: solo la noche
        sombrero: { a0: 1.0, a1: 0.0, s: 1.0, x: 0, y: 0, resp: 0.012, deriva: 0.008, giro: 0.4 },
        noche:    { a0: 0.0, a1: 1.0 }   // geometría y movimiento: los de "sombrero"
    }},
    12: { nombre: "Hongo y criatura", capas: {
        // K1 en 0: los hongos, con la criatura apenas insinuada · 1: la criatura sobre negro,
        // los hongos como un eco tenue. El cuello de la criatura repite los anillos del hongo.
        hongo:    { a0: 1.0,  a1: 0.2, s: 1.0, x: 0, y: 0, resp: 0.015, deriva: 0.012, giro: 0 },
        criatura: { a0: 0.15, a1: 1.0, s: 1.0, x: 0, y: 0, resp: 0.030, deriva: 0.020, giro: 1.2 }
    }},
    13: { nombre: "Nahual", capas: {
        // K1 en 0: el ficus con la silla vacía · 0.5: aparecen los animales · 1: los animales
        // habitan el árbol, la foto queda en penumbra (no se apaga: el lugar sigue ahí).
        ficus:  { a0: 1.0, a1: 0.3, s: 1.0, x: 0, y: 0, resp: 0.012, deriva: 0.008, giro: 0.3 },
        nahual: { a0: 0.0, a1: 1.0 }     // geometría y movimiento: los de "ficus"
    }},
    14: { nombre: "Acuarela y noche", capas: {
        // K1 en 0: la acuarela sola, luminosa sobre negro (sin el papel) · 0.5: la noche
        // aparece debajo y la acuarela queda como un velo · 1: la noche completa.
        noche7:  { a0: 0.0, a1: 1.0,  s: 0.65, x: 0, y: 0, resp: 0.010, deriva: 0.010, giro: 0 },
        reflejo: { a0: 1.0, a1: 0.15, s: 0.65, x: 0, y: 0, resp: 0.020, deriva: 0.025, giro: 0 }
    }}
    // 15: último par del diseñador
};

// Frecuencias base (Hz) de los osciladores, a velocidad 1.
var F_RESP = 1 / 16, F_DERIVA_1 = 1 / 23, F_DERIVA_2 = 1 / 37, F_GIRO = 1 / 29;

// ------------------------------------------------------------------
// Estado
// ------------------------------------------------------------------
var P = { mix: 0.5, speed: 0.35, amp: 0.5, zoom: 0.5, fade: 0.6, tone: 0.5, master: 1.0 };
var escena = 1;
var negro = 0;
var tAnim = 0;          // tiempo de animación (avanza según la velocidad)
var ultimo = 0;         // reloj real del último cuadro (ms)
var pulso = 0;          // envolvente del acento (decae sola)
var nivelNegro = 1;     // 1 = visible, 0 = negro
var masterCur = 1;
var cur = {};           // estado actual por capa
var fase = {};          // fases distintas por capa para que no se muevan igual

(function init() {
    for (var i = 0; i < NOMBRES.length; i++) {
        var n = NOMBRES[i];
        cur[n] = { a: 0, s: 1, x: 0, y: 0, resp: 0, deriva: 0, giro: 0, on: -1 };
        fase[n] = (i * 2.399) % (2 * Math.PI);   // ángulo áureo
    }
    for (var j = 0; j < NOMBRES.length; j++) {     // capas que siguen a otra: misma fase
        var g = CAPAS[NOMBRES[j]].sigue;
        if (g) fase[NOMBRES[j]] = fase[g];
    }
})();

// ------------------------------------------------------------------
// Utilidades
// ------------------------------------------------------------------
function clamp(v, lo, hi) { return v < lo ? lo : (v > hi ? hi : v); }
function lerp(a, b, k) { return a + (b - a) * k; }
function suaviza(actual, meta, dt, tau) {
    if (tau <= 0.0001) return meta;
    return actual + (meta - actual) * (1 - Math.exp(-dt / tau));
}
function factorVelocidad() { return P.speed * 2; }                 // 0 … 2
function factorAmp() { return P.amp * 2; }                         // 0 … 2
function factorZoom() { return Math.pow(2, (P.zoom - 0.5) * 1.6); } // 0.57 … 1.74
function segundosFade() { return 0.2 * Math.pow(100, P.fade); }    // 0.2 … 20 s
function colorTono() {
    var frio = [0.82, 0.92, 1.0], neutro = [1, 1, 1], calido = [1.0, 0.9, 0.74];
    if (P.tone < 0.5) {
        var k = P.tone / 0.5;
        return [lerp(frio[0], 1, k), lerp(frio[1], 1, k), lerp(frio[2], 1, k)];
    }
    var k2 = (P.tone - 0.5) / 0.5;
    return [lerp(1, calido[0], k2), lerp(1, calido[1], k2), lerp(1, calido[2], k2)];
}

// Meta de una capa en la escena actual (opacidad ya mezclada con K1 + pulso)
function meta(n) {
    var def = ESCENAS[escena] ? ESCENAS[escena].capas[n] : null;
    if (!def) return null;
    var m = clamp(P.mix + pulso * 0.6, 0, 1);
    var geo = def;
    var guia = CAPAS[n].sigue;                 // capa que copia la geometría de su guía
    if (guia && ESCENAS[escena].capas[guia]) geo = ESCENAS[escena].capas[guia];
    return { a: lerp(def.a0, def.a1, m), s: geo.s, x: geo.x, y: geo.y,
             resp: geo.resp, deriva: geo.deriva, giro: geo.giro };
}

// ------------------------------------------------------------------
// Cuadro
// ------------------------------------------------------------------
function bang() {
    var ahora = new Date().getTime();
    var dt = ultimo ? clamp((ahora - ultimo) / 1000, 0, 0.1) : 1 / 60;
    ultimo = ahora;
    paso(dt);
}

function paso(dt) {
    tAnim += dt * factorVelocidad();
    pulso = pulso * Math.exp(-dt / 0.35);
    nivelNegro = suaviza(nivelNegro, negro ? 0 : 1, dt, 0.5);
    masterCur = suaviza(masterCur, P.master, dt, 0.08);

    var tau = segundosFade() / 3;   // ~95 % del fundido en el tiempo elegido
    var z = factorZoom();
    var A = factorAmp();
    var tono = colorTono();
    var global = nivelNegro * masterCur;

    for (var i = 0; i < NOMBRES.length; i++) {
        var n = NOMBRES[i], c = cur[n], m = meta(n), f = fase[n];
        var aMeta = m ? m.a : 0;
        if (m) {
            if (c.a < 0.003) {      // estaba invisible: toma la geometría nueva sin deslizarse
                c.s = m.s; c.x = m.x; c.y = m.y; c.resp = m.resp; c.deriva = m.deriva; c.giro = m.giro;
            } else {
                c.s = suaviza(c.s, m.s, dt, tau);
                c.x = suaviza(c.x, m.x, dt, tau);
                c.y = suaviza(c.y, m.y, dt, tau);
                c.resp = suaviza(c.resp, m.resp, dt, tau);
                c.deriva = suaviza(c.deriva, m.deriva, dt, tau);
                c.giro = suaviza(c.giro, m.giro, dt, tau);
            }
        }
        var guia = CAPAS[n].sigue;
        if (m && guia && ESCENAS[escena].capas[guia]) {   // pegada a su guía: misma geometría exacta
            var cg = cur[guia];
            c.s = cg.s; c.x = cg.x; c.y = cg.y; c.resp = cg.resp; c.deriva = cg.deriva; c.giro = cg.giro;
        }
        c.a = suaviza(c.a, aMeta, dt, tau);
        if (c.a < 0.003 && aMeta === 0) c.a = 0;

        var aSalida = c.a * global;
        if (aSalida < 0.002) {
            if (c.on !== 0) { outlet(0, n, "enable", 0); c.on = 0; }
            continue;
        }
        if (c.on !== 1) { outlet(0, n, "enable", 1); c.on = 1; }

        // movimiento: respiración (escala), deriva (dos senos = casi ruido), giro
        var w = 2 * Math.PI;
        var resp = 1 + c.resp * A * Math.sin(w * F_RESP * tAnim + f) + pulso * 0.02;
        var dx = c.deriva * A * (Math.sin(w * F_DERIVA_1 * tAnim + f) + 0.5 * Math.sin(w * F_DERIVA_2 * tAnim + 2 * f));
        var dy = c.deriva * A * (Math.cos(w * F_DERIVA_2 * tAnim + f) + 0.5 * Math.cos(w * F_DERIVA_1 * tAnim + 3 * f));
        var giro = c.giro * A * Math.sin(w * F_GIRO * tAnim + f);

        var sy = c.s * resp * z;
        var sx = sy * CAPAS[n].asp;
        // girar alrededor del pivote de la capa (no del centro del lienzo)
        var pv = CAPAS[n].piv, ox = pv[0] * sx, oy = pv[1] * sy;
        var r = giro * Math.PI / 180, cs = Math.cos(r), sn = Math.sin(r);
        var px = (c.x + dx) * z + ox - (ox * cs - oy * sn);
        var py = (c.y + dy) * z + oy - (ox * sn + oy * cs);

        outlet(0, n, "color", tono[0], tono[1], tono[2], aSalida);
        outlet(0, n, "scale", sx, sy, 1);
        outlet(0, n, "position", px, py, 0);
        outlet(0, n, "rotatexyz", 0, 0, giro);
    }
}

// ------------------------------------------------------------------
// Mensajes
// ------------------------------------------------------------------
function scene(n) {
    n = Math.round(n);
    if (!ESCENAS[n]) {   // pad de banco B aún sin obra: no cambia nada, solo avisa
        post("hub_anim: la escena " + n + " todavía no existe\n");
        outlet(1, ["escena", n, "vacía", "·", "sigue"].concat(ESCENAS[escena].nombre.split(" ")));
        return;
    }
    escena = n;
    // nombre en palabras sueltas: así el message box no lo muestra entre comillas
    outlet(1, ["escena", n].concat(ESCENAS[n].nombre.split(" ")));
}
function snap() {   // sin fundido: usar al abrir el patch
    for (var i = 0; i < NOMBRES.length; i++) {
        var n = NOMBRES[i], m = meta(n), c = cur[n];
        if (m) { c.a = m.a; c.s = m.s; c.x = m.x; c.y = m.y; c.resp = m.resp; c.deriva = m.deriva; c.giro = m.giro; }
        else c.a = 0;
    }
}
function mix(v)    { P.mix = clamp(v, 0, 1); }
function speed(v)  { P.speed = clamp(v, 0, 1); }
function amp(v)    { P.amp = clamp(v, 0, 1); }
function zoom(v)   { P.zoom = clamp(v, 0, 1); }
function fade(v)   { P.fade = clamp(v, 0, 1); outlet(1, "fade", Math.round(segundosFade() * 10) / 10); }
function tone(v)   { P.tone = clamp(v, 0, 1); }
function master(v) { P.master = clamp(v, 0, 1); }
function pulse(v)  { pulso = (arguments.length && v > 0) ? clamp(v, 0, 1) : 1; }
function black(v)  { negro = v ? 1 : 0; outlet(1, "negro", negro); }
function anything() { post("hub_anim: mensaje desconocido '" + messagename + "'\n"); }

// Para el simulador de Node (tools/sim_anim.js); en Max no existe "module".
if (typeof module !== "undefined") {
    module.exports = { paso: paso, scene: scene, snap: snap, mix: mix, speed: speed, amp: amp,
        zoom: zoom, fade: fade, tone: tone, master: master, pulse: pulse, black: black,
        ESCENAS: ESCENAS, CAPAS: CAPAS };
}
