#!/bin/zsh
# T3 gamma-stratified horizon -- full pipeline. Thread-pinned, single process.
set -e
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
       VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
D="/private/tmp/claude-501/-Users-resorb-Documents-Claude-Sessions-Transaction-Calculus/cef41221-e44d-4bc0-91a6-ef7af3cbe582/scratchpad/t3_brody_gamma"
F="$D/brody_poisson_clicks_trials.parquet"
EXPECT="86b51a3e5747fd44ce2e02fd4178faf2acea4e393a9b50b1d3ec7b9c9520bd99"
T0=$(date -u +%s)

echo "== assembling parts =="
for i in 0 1 2 3 4 5 6 7; do cat "$D/parts/p$i" >> "$F"; done
rm -rf "$D/parts"
SZ=$(stat -f%z "$F"); echo "size=$SZ (expect 2131341109)"
[ "$SZ" -eq 2131341109 ] || { echo "SIZE MISMATCH"; exit 1; }

echo "== sha256 =="
GOT=$(shasum -a 256 "$F" | awk '{print $1}')
echo "got    $GOT"
echo "expect $EXPECT"
[ "$GOT" = "$EXPECT" ] || { echo "SHA MISMATCH"; exit 1; }
python3 - "$F" "$GOT" "$SZ" <<'PY'
import sys, json, os
json.dump({"sha256": sys.argv[2], "bytes": int(sys.argv[3]),
           "matches_release_manifest": True},
          open(os.path.join(os.path.dirname(sys.argv[1]), "input_sha256.json"), "w"), indent=1)
PY

echo "== pass1 =="
python3 "$D/pass1_extract.py" "$F" "$D/chunks" 400000
echo "== pass2 =="
python3 "$D/pass2_horizons.py" "$D"
T1=$(date -u +%s)
PEAK=$(awk '{gsub(/[{}]/,""); if ($2+0 > m) m=$2+0} END {print m}' "$D/loadlog.txt")
echo "== pass3 == peak load $PEAK, wall $((T1-T0))s"
python3 "$D/pass3_finalize.py" "$D" "$PEAK" "$((T1-T0))s"
echo "PIPELINE DONE in $(( $(date -u +%s) - T0 ))s"
