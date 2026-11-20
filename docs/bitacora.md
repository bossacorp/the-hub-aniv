# Bitácora

Una entrada por ensayo o cambio importante. Si se ajustó algo a mano en Max, anotarlo aquí
para pasarlo a `tools/build_patch.py`.

## 2026-11-15 — v01: prueba de capas

- Primer patch generado: 3 obras × 2 capas, 6 escenas (3 por obra + 2 cruces + segura),
  negro, pulso; LPD8 por Assign MIDI Map; teclas 1–8 de respaldo.
- Imágenes optimizadas a 1600 px (lado mayor) con alfa; originales fuera de git.
- Pendiente probar en Max: carga de alfa con `importmovie`, fps en Mac mini, encuadres en proyector.
- Ideas para v02: textura de salida → Vizzie (K7), luz/halo de la luna, grano fino,
  respiración con el audio del músico (envolvente de la mezcladora).

### Notas del ensayo 2026-11-15 (v01, etiqueta `ensayo-2026-11-15`)
- Máquina / versión de Max: MacBook Pro, Max 9.2 → será la máquina de la función.
- LPD8 Wireless: pads = notas 36–43 (canal 10); perillas = CC 1–8.
  Archivo con el mapeo: `docs/ensayos/2026-11-15_the-hub-aniv_v01_mapeo-lpd8.maxpat`.
- Hallazgo: las teclas 1–8 funcionan siempre; con el LPD8 mapeado por Assign MIDI Map cada
  golpe no completaba el efecto (pad 8: 4 golpes para negro on/off en vez de 2).
  Causa: nota mapeada a `live.button` = valor 1/0 que alterna, no un disparo por golpe
  (o pad en modo TOGGLE en el LPD8). Las perillas (CC continuo) sí funcionaron bien.

## 2026-11-15 — v02: pads por MIDI directo

- Pads: `notein` → `stripnote` (solo golpes) → `- nota pad 1` → `sel 0..7` → mismos botones
  que el teclado. Interruptor "LPD8 en modo TOGGLE" para pads en toggle. Pads sin mapear.
- Perillas: se conserva el mapeo del ensayo (CC 1–8) dentro del patch generado.
- El menú de puerto ahora fija monitor **y** pads (evita disparos del Launchpad).
- `jit.fpsgui` conectado al outlet 1 (bang por cuadro) de `jit.world`.
- El estado de escena ya no sale entre comillas.
- Dimensiones de las matrices se leen de los PNG (permite regenerar a 2048 px).
- Por probar: 8 golpes del pad 8 = 4 ciclos de negro; fps en pantalla completa en la MacBook Pro.

## 2026-11-19 — v03: banco B del LPD8 + obra 4 "Sombrero" (par 1 de 5 nuevos)

- Archivos del diseñador: `par05-01.jpeg` (foto de día) y `par05-02.jpeg` (pintura nocturna
  sobre negro), 721×1280 (9:16). JPEG sin transparencia → la pintura se convierte con modo
  `luma` (el negro se vuelve transparente; sobre negro se ve igual al original).
- Escena 11 "Sombrero: día y noche" en B1. La pintura es el mismo encuadre que la foto:
  se mueve pegada a ella (`sigue`) para que nunca se desalineen.
- Banco B: 16 pads en pantalla (paneles verde/rojo como las luces del LPD8), notas por
  rango (A1 = 36 medido, B1 = 44 por medir), aviso de empalme, "Último pad", teclas q–i.
  Pads 6/7/8 iguales en ambos bancos. B2–B5 reservados para los próximos 4 pares.
- Por probar: nota real de B1 en el LPD8 Wireless; que el aviso diga "sin empalme".

- 2026-11-19: verificado en el LPD8 — bancos A y B sin empalme, ambos funcionan.

## 2026-11-19 — obra 5 "Hongo y criatura" (par 2 de 5) en B2

- Archivos: `par06-02.jpeg` (foto de hongos cola de pavo, opaca) y `par06-01.jpeg`
  (criatura pintada sobre negro → modo `luma`), 900×1600 (9:16).
- Escena 12: K1 de los hongos a la criatura; capas independientes (encuadres distintos),
  la criatura flota y gira suave sobre su torso. El cuello de la criatura repite los
  anillos naranja/verde del hongo.

## 2026-11-19 — obra 6 "Nahual" (par 3 de 5) en B3

- Archivos: `par07-01.jpeg` (ficus con silla roja y papel picado, opaca) y `par07-02.jpeg`
  (jaguar nahual en la silla, jaguares y loros en las ramas, sobre negro → `luma`), 960×1280 (3:4).
- La pintura está calcada sobre la foto → capa `nahual` con `sigue: "ficus"`.
- Escena 13: K1 de la silla vacía a los animales habitando el árbol; la foto baja a 30 %,
  no a negro, para que el lugar siga presente.

## 2026-11-19 — obra 7 "Acuarela y noche" (par 4 de 5) en B4

- Archivos: `par04-01.jpeg` (paisaje reflejado en acuarela sobre BLANCO) y `par04-02.jpeg`
  (escena nocturna: sol con rostro, madre e hijo con luna, estrellas), 1280×468 (2.74:1).
- Primera capa pintada sobre blanco del set. El modo `papel` (blanco → transparente exacto)
  dejaba los pastel oscuros y turbios sobre negro; nuevo modo `pastel` conserva el color
  original y usa la pintura reforzada (×2.5) como alfa: la acuarela queda luminosa.
  Si el diseñador prefiere ver el papel blanco, cambiar el modo a `opaca` (proyecta mucha luz).
- Escena 14: s = 0.65 para que la panorámica llene el ancho 16:9. K1 de la acuarela sola
  a la noche; en 0.5 la acuarela es una bruma sobre la noche.

### Notas del próximo ensayo (llenar)
- Nota que manda B1 (luz roja), si no es 44:
- fps escena 4 en pantalla completa:
- Escenas que funcionaron / que no:
