#!/usr/bin/env bash
# Clean build time with a warm dependency cache. Runs the command N times, records wall seconds and exit code.
# usage: build_time.sh <runs> <out.tsv> <log-prefix> -- <build command...>
set -u
N=$1; OUT=$2; LOGP=$3; shift 4
echo -e "run\twall_seconds\texit" > "$OUT"
for i in $(seq 1 "$N"); do
  t0=$(date +%s.%N); "$@" > "$LOGP-$i.log" 2>&1; rc=$?; t1=$(date +%s.%N)
  echo -e "$i\t$(python3 -c "print(round($t1 - $t0, 3))")\t$rc" >> "$OUT"
done
cat "$OUT"
