#!/usr/bin/env bash
# Apply one candidate reduction as one commit on the `slim` branch, evaluate it, and revert it if rejected.
# usage: run_candidate.sh <project> <id> "<commit message>" "<edit command 1>" ["<edit command 2>" ...]
#   Each edit command is run with bash inside the clone; $PE expands to "python3 .../pomedit.py".
# Decision rule (mechanical): keep only if verify passes, the same tests ran (none newly skipped) and every
# checklist item on every profile matches baseline. Otherwise the commit is dropped and its diff saved to
# results/<project>/rejected/<id>.diff. With HOLD=1 a failing commit is left in place for a manual decision
# (used only for feature-removing candidates, whose removed feature is expected to differ).
set -u
P=$1; ID=$2; MSG=$3; shift 3
TOP=/workspaces/maven-slimming-experiment
source "$TOP/results/scripts/project_config.sh" "$P"
export PE="python3 $TOP/results/scripts/pomedit.py"
cd "$CLONE"
git diff --quiet || { echo "clone not clean"; exit 2; }
for cmd in "$@"; do bash -c "$cmd" || { echo "edit failed: $cmd"; git checkout -q .; exit 3; }; done
if git diff --quiet; then
  # the edit changed nothing (artifact already absent): record a no-op instead of re-measuring the previous commit
  mkdir -p "$TOP/results/$P/changes/$ID"; echo "NO-OP: edit produced no change (already absent)" > "$TOP/results/$P/changes/$ID/NOOP.txt"
  echo "$ID NO-OP"; exit 0
fi
git commit -qam "$ID: $MSG"
"$TOP/results/scripts/evaluate_candidate.sh" "$P" "$ID" "$TOP/results/$P/baseline" > /dev/null
OUT=$TOP/results/$P/changes/$ID
V=$(python3 -c "import json;print(json.load(open('$OUT/summary.json'))['verdict'])")
if [ "$V" = REJECT ] && [ "${HOLD:-0}" = 1 ]; then
  echo "$ID HELD for manual decision (verdict by the strict rule: REJECT)"
elif [ "$V" = REJECT ]; then
  mkdir -p "$TOP/results/$P/rejected"; cp "$OUT/change.diff" "$TOP/results/$P/rejected/$ID.diff"
  git reset -q --hard HEAD~1
  echo "$ID REJECTED (reverted)"
else
  echo "$ID KEPT"
fi
python3 - "$OUT" <<'EOF'
import json,sys
s=json.load(open(sys.argv[1]+"/summary.json"))
print({k:s.get(k) for k in ["verify_exit","tests_run","failures","errors","skipped","same_tests_as_baseline","artifact_bytes","artifact_delta_vs_baseline","lib_count","resolved_total","checklist","libs_removed_vs_baseline"]})
EOF
grep -h DIFF "$OUT/checklist-compare.txt" 2>/dev/null | head -12
grep -E "COMPILATION ERROR|ERROR\] .*\.java|Tests run:.*(Fail|Err)[a-z]*: [1-9]|\[ERROR\] (Failures|Errors|  )" "$OUT/verify.log" | head -8
