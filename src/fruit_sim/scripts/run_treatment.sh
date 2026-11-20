#!/usr/bin/env bash
# Open one treatment section of the Roza row in Isaac Sim.
# Usage: src/fruit_sim/scripts/run_treatment.sh <pruned_thinned|pruned|control> [lod]
#   lod: 0 (full detail, default) .. 5 (coarsest, fastest)
# Set CUTS="0.33 0.67" to move the section boundaries (fractions of row length).
# Cropped/converted files are cached in data/gaussian_splats/roza_split_by_treatment/treatments/.
set -e

TREATMENT="$1"
LOD="${2:-0}"
case "$TREATMENT" in
    pruned_thinned|pruned|control) ;;
    *) echo "Usage: $0 <pruned_thinned|pruned|control> [lod 0-5]" >&2; exit 1 ;;
esac

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
GSPLAT_BIN="${GSPLAT_BIN:-$HOME/gsplat-env/bin}"
DATA="$REPO/data/gaussian_splats/roza_split_by_treatment"
SRC="$DATA/roza_cosmic_split_by_management/roza_cosmic_split_by_management_$LOD.ply"
CUTS="${CUTS:-0.3333 0.6667}"
OUT="$DATA/treatments"
TAG="${TREATMENT}_lod${LOD}_cuts${CUTS// /_}"

[ -f "$SRC" ] || { echo "Missing $SRC" >&2; exit 1; }
mkdir -p "$OUT"

if [ ! -f "$OUT/$TAG.usdc" ]; then
    "$GSPLAT_BIN/python" "$REPO/src/fruit_sim/fruit_sim/split_treatment.py" \
        "$SRC" "$OUT/$TAG.ply" "$TREATMENT" --cuts $CUTS
    "$GSPLAT_BIN/omni_gsplat_convert" -i "$OUT/$TAG.ply" -o "$OUT/$TAG.usdc" --up-axis Z -n splat
    rm "$OUT/$TAG.ply"
fi

exec "$REPO/src/fruit_sim/scripts/run_splat.sh" "$OUT/$TAG.usdc"
