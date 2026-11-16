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
- Controlador: Akai LPD8 Wireless (8 pads, 8 perillas). Los controles de la interfaz usan
  Parameter Mode → se mapean con Assign MIDI Map; no asumir números de CC/nota.
- Versionar con etiquetas por ensayo: `git tag ensayo-AAAA-MM-DD` y una línea en `docs/bitacora.md`.
- Commits pequeños y descriptivos en español.
