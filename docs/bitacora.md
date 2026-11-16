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

### Notas del próximo ensayo (llenar)
- fps escena 4 en pantalla completa:
- Escenas que funcionaron / que no:
