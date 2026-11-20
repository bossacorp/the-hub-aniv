#!/usr/bin/env bash
# check.sh — verificación antes de commit/ensayo. Uso: bash tools/check.sh [--video]
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== JS =="
node --check show/hub_anim.js && echo "hub_anim.js OK"
echo "== Patch =="
python3 tools/build_patch.py
for f in show/*.maxpat; do echo "$f"; python3 tools/maxpat_builder.py --validate "$f" --target 8; done
echo "== Archivos que Max necesita en show/ =="
for f in hub_anim.js $(python3 -c "import sys; sys.path.insert(0,'tools'); from build_patch import CAPAS; print(' '.join(c[1] for c in CAPAS))"); do
  [ -f "show/$f" ] && echo "  ok  $f" || { echo "  FALTA $f"; exit 1; }
done
echo "== Previews =="
python3 tools/preview.py stills
if [ "${1:-}" = "--video" ]; then python3 tools/preview.py video; fi
