#!/usr/bin/env bash
# Сборка: studio.glb (из Blender) → сжатие meshopt → встраивание в index.html
set -e
cd "$(dirname "$0")"
SRC=${1:-models/studio.glb}
npx --yes @gltf-transform/cli@4 weld "$SRC" /tmp/_w.glb >/dev/null
npx --yes @gltf-transform/cli@4 meshopt /tmp/_w.glb models/studio.min.glb --level medium >/dev/null
python3 - <<'PY'
import base64
s=open('src/viewer.html').read()
g=base64.b64encode(open('models/studio.min.glb','rb').read()).decode()
open('index.html','w').write(s.replace('__GLB__',g))
print('index.html', len(s)+len(g), 'bytes')
PY
