# Instrucciones de uso — the-hub-aniv v03 (capas + banco B)

Máquina de función: **MacBook Pro, Max 9.2+**. El patch sigue siendo compatible con Max 8
(la Mac mini queda como respaldo).

**Qué es:** un primer ejercicio, a propósito austero: las 3 obras del diseñador (2 capas cada
una) se componen con su transparencia original y se animan con movimientos lentos
(respiración, deriva, giro) y fundidos entre escenas. Sin efectos de imagen todavía: sirve
para probar proyección, encuadre, legibilidad y cómo se complementan las capas.

## 1. Requisitos

- Max 8 (probado como objetivo: solo objetos de Max 8) o Max 9. No necesita paquetes.
- La carpeta `show/` completa: patch + `hub_anim.js` + 6 PNG, **juntos en la misma carpeta**.
- Akai LPD8 Wireless conectado por USB (recomendado en función) o Bluetooth.
- Proyector como segunda pantalla (extendida, no espejo).

## 2. Abrir

1. Doble clic en `show/the-hub-aniv_v03.maxpat`. Abre en **presentación**.
   Para ver el cableado: Cmd+Alt+E sale del modo presentación y Cmd+E desbloquea (edición).
2. Se abre la ventana **hub** (960×540). En ~1 s aparecen las imágenes (Escena 1).
3. Arrastra la ventana **hub** al proyector y, con ella al frente, pulsa **esc** (o el
   interruptor "Pantalla completa"). esc otra vez para salir.
4. Abre la consola de Max (⌘M / menú Window → Max Console): no debe haber
   errores rojos. Si los hay, cópialos a Claude Code.

## 3. Conectar el LPD8 Wireless

- **USB:** se reconoce solo.
- **Bluetooth (Mac):** Audio MIDI Setup → Ventana → Mostrar estudio MIDI → icono Bluetooth
  → *Connect* junto al LPD8. Luego en Max: Options → MIDI Setup y verifica que aparezca.
- Elige el LPD8 en el menú **"Puerto MIDI del LPD8"**. Ese menú fija el puerto del monitor
  **y de los pads**: así otro equipo conectado (p. ej. el Launchpad) no dispara escenas.
  El menú no recuerda la elección al reabrir el patch: elígelo cada vez (sin elegir, escucha
  todos los puertos).
- Toca pads/perillas: el monitor MIDI muestra CC (valor · número · canal) y nota
  (tono · velocidad · canal).

## 4. Pads y perillas: cómo entran (cambio de la v02)

**Perillas K1–K8 → Assign MIDI Map.** Ya vienen mapeadas en el patch con lo que grabaste en
el ensayo (CC 1–8). Si cambias de programa en el LPD8, re-mapea con el botón **MIDI**
(*Assign MIDI Map*) de la barra inferior y guarda.

**Pads 1–8 → ruta MIDI directa (no los mapees).** Un `notein` recibe las notas del LPD8,
deja pasar solo el **golpe** (note-on, velocidad > 0) y "presiona" el mismo botón que
presiona la tecla 1–8. Por eso pad y tecla ahora se comportan igual.

- Ajustes en el panel del monitor: **nota A1** (36: pads A = 36–43), **nota B1** (ver §4b) y el
  interruptor **LPD8 en modo TOGGLE**.
- Recomendado: en el editor del LPD8 Wireless pon los pads en **MOMENTARY** (momentáneo).
  Si no puedes cambiarlo, enciende **LPD8 en modo TOGGLE** y cada golpe contará igual.
- Si alguna vez mapeas un pad con Assign MIDI Map además de la ruta directa, ese pad
  disparará dos veces: deja los pads sin mapear.

### Por qué el LPD8 "se comía" golpes y el teclado no (ensayo 2026-11-15)

| | Teclado (1–8) | LPD8 con Assign MIDI Map (v01) |
|---|---|---|
| Qué llega al botón | un `bang` por tecla | un **valor** del parámetro (1 al golpear, 0 después) |
| Qué hace `live.button` | dispara siempre | dispara solo cuando el valor pasa a 1 |
| Resultado | 1 tecla = 1 disparo | el mapeo de nota alternó 1 / 0 en golpes sucesivos (o el pad estaba en TOGGLE): **1 de cada 2 golpes no hacía nada** |
| Pad 8 (negro) | 2 teclas = encender + apagar | 4 golpes = encender + apagar |

En el archivo del ensayo, los pads quedaron mapeados como notas 36–43 en canal 10 con un
modo distinto al de las perillas (`flags 3` contra `flags 2`); las perillas, que mandan
valores continuos, funcionaron bien. Con la ruta directa ya no importa cómo Max interprete
la nota: cada golpe es un `bang`, igual que una tecla.

**Cómo comprobar el modo del pad:** en el monitor MIDI golpea un pad varias veces y mira la
velocidad. MOMENTARY: golpe = número > 0 y al soltar 0. TOGGLE: un golpe da > 0 y el
siguiente da 0.

## 4b. Bancos A y B del LPD8 (v03)

El botón **BANK A/B** del LPD8 cambia lo que mandan los 8 pads: **luz verde = banco A**,
**luz roja = banco B**. Las perillas no cambian con el banco.

| Regla | Para qué |
|---|---|
| Cada banco manda un **rango de notas distinto** (A: 36–43 medido en ensayo; B: por medir, 44–51 por defecto) | una nota solo puede caer en un banco |
| El patch revisa los dos rangos y muestra **"Bancos: … sin empalme"** o **¡AVISO!** | si se empalman lo ves antes de la función |
| **Pads 6 · 7 · 8 hacen lo mismo en A y en B** (pulso · segura · negro) | si te equivocas de banco, los pads de emergencia siguen en el mismo lugar |
| Escena = pad: **A1–A5 → escenas 1–5**, **B1–B5 → escenas 11–15** | nunca hay dos pads que llamen a la misma escena |
| **"Último pad: B1"** en pantalla y paneles verde/rojo como las luces del LPD8 | sabes en qué banco está el LPD8 con un vistazo |
| Pads de B sin obra todavía (B5) **no hacen nada** (la escena actual sigue) | un golpe a un pad libre nunca deja la pantalla en negro |

**Antes del ensayo (2 min):** elige el LPD8 en "Puerto MIDI", pon el LPD8 en banco A y golpea
el pad 1: el monitor debe mostrar tono 36 (= "nota A1"). Cambia a banco B (luz roja) y golpea el
pad 1: escribe ese tono en **"nota B1"**. El aviso debe decir **sin empalme**. Si el LPD8 manda
las mismas notas en A y en B, cambia las notas del banco B en el editor del LPD8 (por ejemplo
44–51) y guarda el programa.

## 5. Mapa de ejecución

Disposición igual a la física del LPD8 (fila de arriba pads 5–8, abajo 1–4).

| Control | Parámetro | Rango | Comportamiento |
|---|---|---|---|
| A1 · tecla 1 | Escena **Mano y flor** (boceto ↔ tinta azul) | — | disparo, fundido con K5 |
| A2 · tecla 2 | Escena **Luna** (luna dentro del anillo de paisaje) | — | disparo |
| A3 · tecla 3 | Escena **Bosque** (foto + figuras etéreas) | — | disparo |
| A4 · tecla 4 | Cruce **Luna en el bosque** | — | disparo |
| A5 · tecla 5 | Cruce **Boceto en el paisaje** | — | disparo |
| B1 · tecla q | Escena 11 **Sombrero: día y noche** (foto ↔ pintura nocturna) | — | disparo |
| B2 · tecla w | Escena 12 **Hongo y criatura** (foto de hongos ↔ criatura pintada) | — | disparo |
| B3 · tecla e | Escena 13 **Nahual** (ficus con silla ↔ jaguar nahual y animales) | — | disparo |
| B4 · tecla r | Escena 14 **Acuarela y noche** (reflejo en acuarela ↔ escena nocturna) | — | disparo |
| B5 · tecla t | escena 15, para el último par | — | sin efecto hasta agregarlo |
| A6 / B6 · teclas 6 / y | **Pulso**: acento que empuja la mezcla y da un latido de escala | — | momentáneo, decae en ~0.4 s |
| A7 / B7 · teclas 7 / u | **Escena segura** (luna sola, estable) | — | disparo |
| A8 / B8 · teclas 8 / i | **Negro** | on/off | alterna; fundido de ~1.5 s |
| K1 | Mezcla capa A ↔ B dentro de la escena | 0–1 | continuo |
| K2 | Velocidad del movimiento | 0 (congelado) – 2× | continuo, sin saltos |
| K3 | Amplitud del movimiento | 0 – 2× | continuo |
| K4 | Zoom / encuadre global | 0.57× – 1.74× (centro = 1×) | continuo |
| K5 | Tiempo de transición entre escenas | 0.2 s – 20 s (exponencial) | se lee en "seg. de transición" |
| K6 | Tono | frío ↔ neutro ↔ cálido | continuo |
| K7 | Reserva para Vizzie (`[s vz_k7]`, 0–1) | 0–1 | sin efecto en v01 |
| K8 | Master / brillo general | 0–1 | continuo (a 0 = negro) |
| Teclado | 1–8 = banco A · q w e r t y u i = banco B | — | respaldo, con Max al frente |

**Qué hace K1 en cada escena**

| Escena | K1 en 0 | K1 en 1 |
|---|---|---|
| 1 Mano y flor | solo el boceto/luz sobre negro | dibujo azul completo, boceto tenue encima |
| 2 Luna | luna atenuada, el paisaje manda | luna plena |
| 3 Bosque | foto con figuras apenas visibles | figuras plenas sobre la foto |
| 4 Luna en el bosque | luna sobre la foto, sin figuras | figuras plenas, luna tenue |
| 5 Boceto en el paisaje | paisaje + luna | la luz del boceto entra en el anillo, luna tenue |
| 7 Segura | luna sola (K1 no cambia nada) | |
| B1 Sombrero (11) | foto de día | solo la pintura nocturna sobre negro (en 0.5: la noche se enciende sobre la foto) |
| B2 Hongo y criatura (12) | hongos, criatura apenas insinuada | criatura plena, hongos como eco tenue |
| B3 Nahual (13) | el ficus con la silla vacía | los animales habitan el árbol, foto en penumbra |
| B4 Acuarela y noche (14) | la acuarela luminosa sobre negro (sin papel blanco) | la noche completa; en 0.5 la acuarela es una bruma sobre la noche |

Vista de todas: `previews/escenas_mix.jpg`.

> Obra 7 es panorámica (2.74:1): llena el ancho con franjas negras arriba y abajo.
> Obras 4–6 son verticales (9:16 y 3:4): en pantalla 16:9 queda una columna con negro a los lados.
> K4 la agranda (recorta arriba/abajo). La foto y la pintura se mueven pegadas: nunca se desalinean.

## 6. Cómo se usa durante el set (improvisación planeada)

- Arranca con K8 abajo o con Pad 8 (negro). Sube cuando el músico empieza.
- **K2 + K3 son "la respiración"**: con texturas largas, K2 bajo y K3 medio; cuando la
  pieza se agita, sube K2. Congelar (K2 en 0) en silencios funciona muy bien.
- **K5 decide el carácter de los cortes**: largo (8–15 s) para disolver entre paisajes;
  corto (<1 s) para cortes ante un golpe del músico.
- **K1 es el gesto principal**: "revelar" la obra (boceto → tinta, aparecen figuras).
- Pad 6 (pulso) para acompañar acentos; úsalo poco.
- Recorrido sugerido de 25 min: 1 → 5 → 2 → 4 → 3 → 2 → negro (ver `docs/bitacora.md`).

## 7. Verificación rápida (5 min)

1. A1–A5, B1 y 7 cambian de escena; 8 funde a negro y regresa, en ambos bancos.
   "Bancos" dice *sin empalme*; "Último pad" muestra A o B según la luz del LPD8.
2. Cada perilla hace algo visible (K7 no, es reserva).
3. `fps` ≥ 30 en la máquina de función, con la ventana en pantalla completa.
4. Escenas 3 y 4 (verticales) muestran barras negras laterales: es intencional.
   K4 hacia arriba llena la pantalla recortando arriba/abajo.

## 8. Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Ventana negra, sin imágenes | PNG no encontrados (no están junto al patch) | Pon los 6 PNG en la carpeta del patch y pulsa *Recargar imágenes* |
| Las imágenes salen con fondo blanco/negro opaco en vez de transparente | el importador no trajo el alfa | Avísale a Claude Code: se cambia la carga a `jit.movie @output_texture 1` |
| La imagen aparece estirada | aspecto de ventana raro | revisa que la ventana sea 16:9; los videoplanes usan `@transform_reset 1` |
| Nada se mueve | interruptor *Animación* apagado o K2 en 0 | enciéndelo / sube K2 |
| `js: can't find file hub_anim.js` | falta el JS junto al patch | copia `hub_anim.js` a `show/` |
| Un golpe del pad sí y otro no | pad en TOGGLE en el LPD8, o el pad quedó mapeado con Assign MIDI Map | pon los pads en MOMENTARY (o enciende "LPD8 en modo TOGGLE"); borra mapeos de pads |
| Los pads disparan escenas equivocadas | otro programa del LPD8 (otras notas) | ajusta **nota A1** / **nota B1** al tono que muestra el monitor al golpear el pad 1 de cada banco |
| Un pad dispara en A y en B a la vez / aviso de empalme | los dos bancos mandan notas que se cruzan | cambia las notas del banco B en el editor del LPD8 y corrige **nota B1** |
| En banco B no pasa nada | **nota B1** no coincide con lo que manda el LPD8 | golpea B1, lee el tono en el monitor y escríbelo en **nota B1** |
| Los pads no responden, las perillas sí | puerto equivocado en el menú | elige el LPD8 en "Puerto MIDI del LPD8" |
| El LPD8 no responde | Bluetooth caído | monitor MIDI; usa USB; teclas 1–8 de respaldo |
| fps bajos en la Mac mini | GPU modesta | `python3 tools/prep_media.py --max 1280`, cerrar otras apps, `@fsaa 0` |
| `fps` muestra 0 aunque se vea bien | el contador no recibe el bang por cuadro | v02 lo conecta al outlet 1 de `jit.world`; si sigue en 0, avisa |

## 9. Checklist de ensayo

1. Monitor MIDI: todos los pads y perillas llegan; 8 golpes seguidos del pad 8 = 4 veces negro on/off.
2. fps con escena 4 o 5 (las de 3 capas) en pantalla completa, en la máquina de función.
3. Proyector: resolución nativa, sin keystone digital extremo, aspecto correcto.
4. Recorrido completo con el músico (o con un audio parecido) usando solo el LPD8.
5. Fallo: apagar el LPD8 a la mitad → seguir con teclado (1–8 / q–i) o mouse; reconectar.
6. Luz de sala: el negro del proyector se ve gris; probar K8 y escenas con fondo negro.
7. Mac en función: sin notificaciones, sin protector de pantalla, sin actualizaciones.
8. Abrir el patch 30 min antes y dejarlo corriendo.
