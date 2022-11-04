#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(wslpath -w "$PWD")
LAYOUT_PY="create_ortho_prints.py"
OUTPUTS_DIR="$SCRIPT_DIR\outputs"
QGZ_FILE="$1"
SNAPSHOT_TARGET="${OUTPUTS_DIR}\\${QGZ_FILE}.png"
DEFAULT_EXTENT="89749,6681742,127170,6721089"
EXTENT="${2:-$DEFAULT_EXTENT}"

[[ "$DEFAULT_EXTENT" = "$EXTENT" ]] && echo "Using default extent."

echo "Creating snapshot of ${QGZ_FILE}."

[[ -a "$QGZ_FILE" ]] || (echo "Input file does not exist." && exit 1)

pushd /mnt/c/Program\ Files/QGIS\ 3.18/bin

QGZ_FILE_PATH="$SCRIPT_DIR\\$QGZ_FILE"
LAYOUT_PY_PATH="$SCRIPT_DIR\\$LAYOUT_PY"
QGIS_BIN=./qgis-bin.exe

[[ -a "$QGIS_BIN" ]] || (echo "${QGIS_BIN} does not exist at destination." && exit 1)

./qgis-bin.exe \
          --noplugins \
          --noversioncheck \
          --nologo \
          --nocustomization \
          --code $LAYOUT_PY_PATH \
          -- "$QGZ_FILE_PATH"

popd
