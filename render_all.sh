#!/usr/bin/env bash
# Render every clip into clips/ and stitch them, in talk order, into investing_early.mp4.
#
#   ./render_all.sh              # 1080p30 (default)
#   ./render_all.sh -qh          # 1080p60
#   ./render_all.sh -ql          # fast 480p preview
#   JOBS=4 ./render_all.sh       # render 4 clips at a time
set -euo pipefail
cd "$(dirname "$0")"

MANIM=${MANIM:-manim}
JOBS=${JOBS:-1}
FLAGS=("$@")
if [ ${#FLAGS[@]} -eq 0 ]; then
  FLAGS=(--resolution 1920,1080 --frame_rate 30)
fi

SCENES=(
  Ownership CashVsInflation
  StockPicking ActiveFunds IndexFund Fees
  Compounding StartEarly
  TimeHorizon Crashes BeatTheCouch TimingRules BestDays
  DollarCostAveraging LumpSum
  Taxes Priorities
)

[ -f data/derived.json ] || python data/prepare.py

for scene in "${SCENES[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
  "$MANIM" "${FLAGS[@]}" --disable_caching investing.py "$scene" &
done
wait

rm -rf clips && mkdir clips
list=$(mktemp)
trap 'rm -f "$list"' EXIT
i=0
for scene in "${SCENES[@]}"; do
  i=$((i + 1))
  # newest render of this scene, whatever quality folder it landed in
  file=$(find media/videos/investing -name "$scene.mp4" -not -path "*partial*" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
  out=$(printf "clips/%02d_%s.mp4" "$i" "$scene")
  cp "$file" "$out"
  echo "file '$PWD/$out'" >> "$list"
done

ffmpeg -v error -y -f concat -safe 0 -i "$list" -c copy investing_early.mp4
echo "Wrote clips/ and $(pwd)/investing_early.mp4"
