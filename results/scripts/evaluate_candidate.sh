#!/usr/bin/env bash
# Evaluate the current (committed) state of a project clone against the project baseline.
# usage: evaluate_candidate.sh <project> <candidate-id> <reference-dir>
#   <project>        petclinic | jhipster | dtrack   (selects build command, jar and checklist runner)
#   <reference-dir>  directory holding baseline tests.json, artifact.json and checklist/ (normally results/<project>/baseline)
# Writes results/<project>/changes/<candidate-id>/ : verify.log, tests.json, artifact.json, dependency-tree.txt,
# resolved.json, checklist/, checklist-compare.txt, summary.json
set -u
P=$1; ID=$2; REF=$(realpath "$3")
TOP=/workspaces/maven-slimming-experiment
S=$TOP/results/scripts
OUT=$TOP/results/$P/changes/$ID; rm -rf "$OUT"; mkdir -p "$OUT"
source "$S/project_config.sh" "$P"     # sets CLONE, VERIFY_CMD, ARTIFACT_GLOB, CHECKLIST_RUNNER, CHECKLIST_PROFILES, REPORT_DIRS
cd "$CLONE" || exit 2
git log -1 --format='%H %s' > "$OUT/commit.txt"
git diff "$BASE_REF" HEAD > "$OUT/cumulative.diff"
git show HEAD --format= > "$OUT/change.diff"
df -B1 --output=target,avail /workspaces /tmp > "$OUT/disk-free-before.txt"
avail=$(df -B1 --output=avail /workspaces | tail -1)
if [ "$avail" -lt 5000000000 ]; then echo "ABORT: /workspaces has only $avail bytes free" | tee "$OUT/ABORTED-low-disk"; exit 9; fi

eval "$VERIFY_CMD" > "$OUT/verify.log" 2>&1; rc=$?
echo "$rc" > "$OUT/verify.exit"
python3 "$S/measure.py" tests $REPORT_DIRS > "$OUT/tests.json"
JAR=$(ls $ARTIFACT_GLOB 2>/dev/null | head -1)
if [ "$rc" = 0 ] && [ -n "$JAR" ]; then
  python3 "$S/measure.py" artifact "$JAR" > "$OUT/artifact.json"
  sha256sum "$JAR" > "$OUT/artifact.sha256"
  mkdir -p "$CACHE_ROOT/artifacts"; cp "$JAR" "$CACHE_ROOT/artifacts/$P-$ID.${JAR##*.}"
fi
./mvnw -B -q $TREE_ARGS dependency:tree -DoutputFile="$OUT/dependency-tree.txt" > "$OUT/tree.log" 2>&1
python3 "$S/measure.py" tree "$OUT/dependency-tree.txt" > "$OUT/resolved.json" 2>/dev/null

CL=skipped
if [ "$rc" = 0 ] && [ -n "$JAR" ]; then
  "$CHECKLIST_RUNNER" "$CACHE_ROOT/artifacts/$P-$ID.${JAR##*.}" "$OUT/checklist" > "$OUT/checklist-run.log" 2>&1
  CL=pass
  : > "$OUT/checklist-compare.txt"
  for prof in $CHECKLIST_PROFILES; do
    echo "== $prof" >> "$OUT/checklist-compare.txt"
    python3 "$S/checklist_compare.py" "$REF/checklist/checklist-$prof.json" "$OUT/checklist/checklist-$prof.json" >> "$OUT/checklist-compare.txt" || CL=FAIL
  done
fi

# Housekeeping (added after the 2026-10-04 disk incident): the size, library list and sha256 of the
# candidate artifact are recorded above, so the copy is discarded; stopped containers and their
# anonymous volumes are pruned; free space on both disks is recorded per candidate.
rm -f "$CACHE_ROOT/artifacts/$P-$ID".*
docker container prune -f >/dev/null 2>&1; docker volume prune -af >/dev/null 2>&1
df -B1 --output=target,avail /workspaces /tmp > "$OUT/disk-free-after.txt"

python3 - "$REF" "$OUT" "$rc" "$CL" <<'EOF' | tee "$OUT/summary.json"
import json, os, sys
ref, out, rc, cl = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
bt, ct = json.load(open(f"{ref}/tests.json")), json.load(open(f"{out}/tests.json"))
s = {"verify_exit": rc, "tests_run": ct["run"], "failures": ct["failures"], "errors": ct["errors"], "skipped": ct["skipped"],
     "baseline_tests_run": bt["run"], "baseline_skipped": bt["skipped"]}
s["test_classes_missing_or_changed"] = {k: [bt["per_class"].get(k), ct["per_class"].get(k)]
                                        for k in set(bt["per_class"]) | set(ct["per_class"])
                                        if bt["per_class"].get(k) != ct["per_class"].get(k)}
s["same_tests_as_baseline"] = (not s["test_classes_missing_or_changed"]) and ct["skipped"] == bt["skipped"]
if os.path.exists(f"{out}/artifact.json"):
    a, b = json.load(open(f"{ref}/artifact.json")), json.load(open(f"{out}/artifact.json"))
    s.update({"artifact_bytes": b["artifact_bytes"], "lib_count": b["lib_count"],
              "artifact_delta_vs_baseline": b["artifact_bytes"] - a["artifact_bytes"],
              "libs_removed_vs_baseline": sorted(set(a["libs"]) - set(b["libs"])),
              "libs_added_vs_baseline": sorted(set(b["libs"]) - set(a["libs"]))})
try:
    s["resolved_total"] = json.load(open(f"{out}/resolved.json"))["total"]
except Exception:
    s["resolved_total"] = None
s["checklist"] = cl
s["tests_pass"] = rc == 0 and ct["failures"] == 0 and ct["errors"] == 0
s["verdict"] = "KEEP-ELIGIBLE" if (s["tests_pass"] and s["same_tests_as_baseline"] and cl == "pass") else "REJECT"
print(json.dumps(s, indent=1))
EOF
