#!/usr/bin/env bash
# Startup time: wall clock from `java -jar` launch until the health URL first returns HTTP 200,
# polled every 50 ms; also records the framework's own "Started ... in X seconds" line if present.
# usage: startup_time.sh <runs> <out.tsv> <health-url> -- <command to start the app...>
set -u
N=$1; OUT=$2; URL=$3; shift 4
echo -e "run\twall_seconds\tself_reported" > "$OUT"
for i in $(seq 1 "$N"); do
  LOG=$(mktemp)
  t0=$(date +%s.%N)
  "$@" > "$LOG" 2>&1 &
  APP=$!
  ok=0
  for j in $(seq 1 6000); do
    if [ "$(curl -s -o /dev/null -w '%{http_code}' "$URL")" = 200 ]; then ok=1; break; fi
    kill -0 $APP 2>/dev/null || break
    sleep 0.05
  done
  t1=$(date +%s.%N)
  self=$(grep -oE 'Started [A-Za-z]+ in [0-9.]+ seconds' "$LOG" | grep -oE '[0-9.]+' | head -1)
  kill $APP 2>/dev/null; wait $APP 2>/dev/null
  if [ $ok = 1 ]; then echo -e "$i\t$(python3 -c "print(round($t1 - $t0, 3))")\t${self:-}" >> "$OUT"; else echo -e "$i\tFAILED\t" >> "$OUT"; cp "$LOG" "$OUT.failed-run-$i.log"; fi
  rm -f "$LOG"
  sleep 2
done
cat "$OUT"
