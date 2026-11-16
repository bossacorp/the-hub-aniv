# CLAUDE.md — reglas del repo the-hub-aniv

Proyección interactiva en Max (Jitter + js clásico) para el aniversario de una casa de
producción. Responde en español.

## Reglas

- **Compatibilidad Max 8**: solo objetos de Max 8 (nada de `v8`, `jit.fx.*`, `jit.geom.*`,
  `*.codebox`, `abl.*`). El JS es ES5 para el objeto `js`.
- **El `.maxpat` se genera**: edita `tools/build_patch.py` y corre `python3 tools/build_patch.py`.
  No edites `show/*.maxpat` a mano salvo emergencia; si alguien lo cambió en Max, pasa el cambio
  al script y anótalo en `docs/bitacora.md`.
- **Todo lo que Max necesita vive en `show/`** (patch, js, png) para que cargue sin rutas.
  Nombres de archivo sin espacios ni acentos.
- **Escenas y movimiento** en `show/hub_anim.js` → tabla `ESCENAS` (a0/a1, s, x, y, resp,
  deriva, giro). Coordenadas: alto de ventana −1..1, ancho ±aspecto (`@transform_reset 1`).
- Antes de commit: `bash tools/check.sh` (node --check, regenerar y validar patch, previews).
  Mira `previews/escenas_mix.jpg` después de tocar una escena.
- Originales en alta van en `media_src/` (ignorado por git). Para agregar una obra: copiar
  capas a `media_src/`, agregarlas en `tools/prep_media.py`, `CAPAS` de `hub_anim.js`,
  `CAPAS` de `build_patch.py` y `tools/preview.py`.
- Máquina de función: MacBook Pro con Max 9.2+ (la Mac mini con Max 8 es respaldo; por eso
  se mantiene la compatibilidad con Max 8).
- Controlador: Akai LPD8 Wireless (8 pads, 8 perillas).
  - **Perillas** → Parameter Mode + Assign MIDI Map. El mapeo del ensayo (CC 1–8) se inyecta
    desde `MIDI_MAP_PERILLAS` en `build_patch.py`.
  - **Pads** → ruta MIDI directa (`notein` → `stripnote` → `sel` → mismos botones que el
    teclado). NUNCA mapear pads con Assign MIDI Map: una nota mapeada a `live.button` dispara
    uno de cada dos golpes (ver `docs/instrucciones.md` §4). Nota base configurable (36).
  - No asumir números de CC/nota nuevos sin verlos en el monitor MIDI.
- Versionar con etiquetas por ensayo: `git tag ensayo-AAAA-MM-DD` y una línea en `docs/bitacora.md`.
- Commits pequeños y descriptivos en español.
