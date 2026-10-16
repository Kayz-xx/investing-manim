#!/usr/bin/env bash
# Render every scene into planar/clips/ and stitch them, in order, into planar/planar_graphs.mp4.
#
#   ./planar/render.sh              # 1080p30 (default)
#   ./planar/render.sh -ql          # fast 480p preview
#   JOBS=5 ./planar/render.sh       # render 5 scenes at a time
set -euo pipefail
cd "$(dirname "$0")"

MANIM=${MANIM:-manim}
JOBS=${JOBS:-1}
FLAGS=("$@")
if [ ${#FLAGS[@]} -eq 0 ]; then
  FLAGS=(--resolution 1920,1080 --frame_rate 30)
fi

SCENES=(Puzzle Euler Faces Contradiction Torus)

# Each scene gets its own media folder so parallel renders don't race on the LaTeX cache.
for scene in "${SCENES[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
  "$MANIM" "${FLAGS[@]}" --disable_caching --media_dir "../media/planar/$scene" planar.py "$scene" &
done
wait

rm -rf clips && mkdir clips
list=$(mktemp)
trap 'rm -f "$list"' EXIT
i=0
for scene in "${SCENES[@]}"; do
  i=$((i + 1))
  file=$(find "../media/planar/$scene/videos" -name "$scene.mp4" -not -path "*partial*" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
  out=$(printf "clips/%d_%s.mp4" "$i" "$scene")
  cp "$file" "$out"
  echo "file '$PWD/$out'" >> "$list"
done

ffmpeg -v error -y -f concat -safe 0 -i "$list" -c copy planar_graphs.mp4
echo "Wrote planar/clips/ and $(pwd)/planar_graphs.mp4"
