# The Hub · Aniversario — proyección interactiva

Visuales en vivo para el cierre del taller de paisaje sonoro (20–30 min, improvisación
planeada). Se proyectan obras de un diseñador regional, separadas en capas, que se
mezclan y animan en Max con un **Akai LPD8 Wireless**.

## Para la función (lo único que hay que saber)

1. Abre **`show/the-hub-aniv_v01.maxpat`** en Max 8 o Max 9 (abre en modo presentación).
2. Arrastra la ventana **hub** al proyector → tecla **esc** = pantalla completa.
3. LPD8: **pads 1–5** escenas · **6** pulso · **7** escena segura · **8** negro (on/off).
   Perillas: K1 mezcla · K2 velocidad · K3 amplitud · K4 zoom · K5 transición · K6 tono · K7 reserva Vizzie · K8 master.
4. Sin controlador: teclas **1–8** con Max al frente.

Instrucciones completas, mapeo MIDI, problemas comunes y checklist de ensayo:
**[`docs/instrucciones_v01.md`](docs/instrucciones_v01.md)**.

## Estructura

```
show/        ← TODO lo que necesita Max, en una sola carpeta (copiar esta carpeta basta)
  the-hub-aniv_v01.maxpat   patch (generado por tools/build_patch.py)
  hub_anim.js               motor de escenas y animación (js clásico, Max 8/9)
  e1_* e2_* e3_*.png        capas del diseñador optimizadas (1600 px, con alfa)
tools/
  build_patch.py            genera el .maxpat (editar aquí, no a mano)
  maxpat_builder.py         biblioteca de generación de patches
  prep_media.py             originales (media_src/) → show/*.png
  sim_anim.js, preview.py   simulan hub_anim.js y renderizan vistas previas sin Max
  check.sh                  verifica todo antes de un commit
docs/        instrucciones, mapa de cables, bitácora de ensayos
previews/    hojas de contacto de las escenas (el .mp4 se genera, no se versiona)
media_src/   originales en alta (NO se suben a git; ver .gitignore)
```

## Flujo de trabajo con Claude Code

```bash
bash tools/check.sh          # JS válido + patch regenerado y validado + previews
git add -A && git commit -m "v01: ajusta encuadre luna en escena 4"
```

Cambios de escenas (opacidades, encuadres, movimiento) → `show/hub_anim.js`, tabla `ESCENAS`.
Cambios de interfaz/cableado → `tools/build_patch.py`. Ver `CLAUDE.md`.

## Créditos

Obra gráfica: diseñador invitado (derechos reservados; uso exclusivo para este evento).
