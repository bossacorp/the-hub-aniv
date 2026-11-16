# Mapa de cables — The Hub · Aniversario — Proyección v01 (capas del diseñador)

| # | Desde (outlet) | Hacia (inlet) |
|---|---|---|
| 1 | `js hub_anim.js` (0) | `route foto tinta luna paisaje figuras boceto` (0) |
| 2 | `[live.button] pad1` (0) | `[msg] scene 1` (0) |
| 3 | `[msg] scene 1` (0) | `js hub_anim.js` (0) |
| 4 | `[live.button] pad2` (0) | `[msg] scene 2` (0) |
| 5 | `[msg] scene 2` (0) | `js hub_anim.js` (0) |
| 6 | `[live.button] pad3` (0) | `[msg] scene 3` (0) |
| 7 | `[msg] scene 3` (0) | `js hub_anim.js` (0) |
| 8 | `[live.button] pad4` (0) | `[msg] scene 4` (0) |
| 9 | `[msg] scene 4` (0) | `js hub_anim.js` (0) |
| 10 | `[live.button] pad5` (0) | `[msg] scene 5` (0) |
| 11 | `[msg] scene 5` (0) | `js hub_anim.js` (0) |
| 12 | `[live.button] pad6` (0) | `[msg] pulse` (0) |
| 13 | `[msg] pulse` (0) | `js hub_anim.js` (0) |
| 14 | `[live.button] pad7` (0) | `[msg] scene 6` (0) |
| 15 | `[msg] scene 6` (0) | `js hub_anim.js` (0) |
| 16 | `[live.button] pad8` (0) | `[toggle]` (0) |
| 17 | `[toggle]` (0) | `prepend black` (0) |
| 18 | `prepend black` (0) | `js hub_anim.js` (0) |
| 19 | `key` (0) | `sel 49 50 51 52 53 54 55 56` (0) |
| 20 | `sel 49 50 51 52 53 54 55 56` (0) | `[live.button] pad1` (0) |
| 21 | `sel 49 50 51 52 53 54 55 56` (1) | `[live.button] pad2` (0) |
| 22 | `sel 49 50 51 52 53 54 55 56` (2) | `[live.button] pad3` (0) |
| 23 | `sel 49 50 51 52 53 54 55 56` (3) | `[live.button] pad4` (0) |
| 24 | `sel 49 50 51 52 53 54 55 56` (4) | `[live.button] pad5` (0) |
| 25 | `sel 49 50 51 52 53 54 55 56` (5) | `[live.button] pad6` (0) |
| 26 | `sel 49 50 51 52 53 54 55 56` (6) | `[live.button] pad7` (0) |
| 27 | `sel 49 50 51 52 53 54 55 56` (7) | `[live.button] pad8` (0) |
| 28 | `[live.dial] k1_mezcla` (0) | `prepend mix` (0) |
| 29 | `prepend mix` (0) | `js hub_anim.js` (0) |
| 30 | `[live.dial] k2_velocidad` (0) | `prepend speed` (0) |
| 31 | `prepend speed` (0) | `js hub_anim.js` (0) |
| 32 | `[live.dial] k3_amplitud` (0) | `prepend amp` (0) |
| 33 | `prepend amp` (0) | `js hub_anim.js` (0) |
| 34 | `[live.dial] k4_zoom` (0) | `prepend zoom` (0) |
| 35 | `prepend zoom` (0) | `js hub_anim.js` (0) |
| 36 | `[live.dial] k5_transicion` (0) | `prepend fade` (0) |
| 37 | `prepend fade` (0) | `js hub_anim.js` (0) |
| 38 | `[live.dial] k6_tono` (0) | `prepend tone` (0) |
| 39 | `prepend tone` (0) | `js hub_anim.js` (0) |
| 40 | `[live.dial] k7_vizzie` (0) | `s vz_k7` (0) |
| 41 | `[live.dial] k8_master` (0) | `prepend master` (0) |
| 42 | `prepend master` (0) | `js hub_anim.js` (0) |
| 43 | `js hub_anim.js` (1) | `route escena fade negro` (0) |
| 44 | `route escena fade negro` (0) | `prepend set Escena` (0) |
| 45 | `prepend set Escena` (0) | `[msg] Escena —` (0) |
| 46 | `route escena fade negro` (1) | `[flonum]` (0) |
| 47 | `loadbang` (0) | `delay 600` (0) |
| 48 | `[live.button] recargar` (0) | `delay 600` (0) |
| 49 | `delay 600` (0) | `t b b b b b b` (0) |
| 50 | `t b b b b b b` (5) | `[msg] importmovie e3_bosque_foto.png, bang` (0) |
| 51 | `[msg] importmovie e3_bosque_foto.png, bang` (0) | `jit.matrix 4 char 1200 1600` (0) |
| 52 | `jit.matrix 4 char 1200 1600` (0) | `jit.gl.videoplane hub @layer 1 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 53 | `route foto tinta luna paisaje figuras boceto` (0) | `jit.gl.videoplane hub @layer 1 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 54 | `t b b b b b b` (4) | `[msg] importmovie e1_mano_tinta.png, bang` (0) |
| 55 | `[msg] importmovie e1_mano_tinta.png, bang` (0) | `jit.matrix 4 char 1600 1600` (0) |
| 56 | `jit.matrix 4 char 1600 1600` (0) | `jit.gl.videoplane hub @layer 2 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 57 | `route foto tinta luna paisaje figuras boceto` (1) | `jit.gl.videoplane hub @layer 2 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 58 | `t b b b b b b` (3) | `[msg] importmovie e2_luna_luna.png, bang` (0) |
| 59 | `[msg] importmovie e2_luna_luna.png, bang` (0) | `jit.matrix 4 char 1600 1600` (0) |
| 60 | `jit.matrix 4 char 1600 1600` (0) | `jit.gl.videoplane hub @layer 3 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 61 | `route foto tinta luna paisaje figuras boceto` (2) | `jit.gl.videoplane hub @layer 3 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 62 | `t b b b b b b` (2) | `[msg] importmovie e2_luna_paisaje.png, bang` (0) |
| 63 | `[msg] importmovie e2_luna_paisaje.png, bang` (0) | `jit.matrix 4 char 1600 1600` (0) |
| 64 | `jit.matrix 4 char 1600 1600` (0) | `jit.gl.videoplane hub @layer 4 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 65 | `route foto tinta luna paisaje figuras boceto` (3) | `jit.gl.videoplane hub @layer 4 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 66 | `t b b b b b b` (1) | `[msg] importmovie e3_bosque_figuras.png, bang` (0) |
| 67 | `[msg] importmovie e3_bosque_figuras.png, bang` (0) | `jit.matrix 4 char 1200 1600` (0) |
| 68 | `jit.matrix 4 char 1200 1600` (0) | `jit.gl.videoplane hub @layer 5 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 69 | `route foto tinta luna paisaje figuras boceto` (4) | `jit.gl.videoplane hub @layer 5 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 70 | `t b b b b b b` (0) | `[msg] importmovie e1_mano_boceto.png, bang` (0) |
| 71 | `[msg] importmovie e1_mano_boceto.png, bang` (0) | `jit.matrix 4 char 1600 1600` (0) |
| 72 | `jit.matrix 4 char 1600 1600` (0) | `jit.gl.videoplane hub @layer 6 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 73 | `route foto tinta luna paisaje figuras boceto` (5) | `jit.gl.videoplane hub @layer 6 @blend_enable 1 @depth_enable 0 @transform_reset 1 @color 1 1 1 0 @enable 0` (0) |
| 74 | `[live.toggle] animar` (0) | `qmetro 16` (0) |
| 75 | `qmetro 16` (0) | `js hub_anim.js` (0) |
| 76 | `loadbang` (0) | `delay 100` (0) |
| 77 | `delay 100` (0) | `[msg] scene 1, snap` (0) |
| 78 | `[msg] scene 1, snap` (0) | `js hub_anim.js` (0) |
| 79 | `[live.toggle] pantalla_completa` (0) | `prepend fullscreen` (0) |
| 80 | `prepend fullscreen` (0) | `jit.world hub @enable 1 @erase_color 0 0 0 1 @size 960 540 @fsmenubar 0 @fsaa 1` (0) |
| 81 | `jit.world hub @enable 1 @erase_color 0 0 0 1 @size 960 540 @fsmenubar 0 @fsaa 1` (0) | `[jit.fpsgui]` (0) |
| 82 | `ctlin` (0) | `[number]` (0) |
| 83 | `ctlin` (1) | `[number]` (0) |
| 84 | `ctlin` (2) | `[number]` (0) |
| 85 | `notein` (0) | `[number]` (0) |
| 86 | `notein` (1) | `[number]` (0) |
| 87 | `notein` (2) | `[number]` (0) |
| 88 | `loadbang` (0) | `[msg] -1` (0) |
| 89 | `[msg] -1` (0) | `midiinfo` (1) |
| 90 | `midiinfo` (0) | `[umenu]` (0) |
| 91 | `[umenu]` (1) | `ctlin` (0) |
| 92 | `[umenu]` (1) | `notein` (0) |
