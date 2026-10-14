#!/usr/bin/env bash
# Render every scene and stitch them into investing_early.mp4.
#
#   ./render_all.sh              # 1080p30 (default)
#   ./render_all.sh -qh          # 1080p60
#   ./render_all.sh -ql          # fast 480p preview
#   JOBS=4 ./render_all.sh       # render 4 scenes at a time
set -euo pipefail
cd "$(dirname "$0")"

MANIM=${MANIM:-manim}
JOBS=${JOBS:-1}
FLAGS=("$@")
if [ ${#FLAGS[@]} -eq 0 ]; then
  FLAGS=(--resolution 1920,1080 --frame_rate 30)
fi

SCENES=(Intro WhatIsInvesting IndexFunds Compounding StartEarly RecurringInvesting TaxesLongTerm MakingDecisions Recap)

for scene in "${SCENES[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
  "$MANIM" "${FLAGS[@]}" --disable_caching investing_early.py "$scene" &
done
wait

list=$(mktemp)
trap 'rm -f "$list"' EXIT
for scene in "${SCENES[@]}"; do
  # newest render of this scene, whatever quality folder it landed in
  file=$(find media/videos/investing_early -name "$scene.mp4" -not -path "*partial*" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
  echo "file '$PWD/$file'" >> "$list"
done

ffmpeg -v error -y -f concat -safe 0 -i "$list" -c copy investing_early.mp4
echo "Wrote $(pwd)/investing_early.mp4"
