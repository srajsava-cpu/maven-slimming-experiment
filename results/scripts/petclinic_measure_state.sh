#!/usr/bin/env bash
# Step 1/4 measurements for one PetClinic state (a git ref of the clone).
# usage: petclinic_measure_state.sh <state-name> <git-ref>
# Writes results/petclinic/after/<state-name>/: build-time.tsv (5x clean package -DskipTests, warm cache),
# artifact.json, artifact.sha256, effective-pom.xml, declared.json, dependency-tree.txt, resolved.json,
# startup.tsv (10 runs), trivy.json + trivy-summary.json (DB updates disabled: same DB as the baseline scan).
set -u
NAME=$1; REF=$2
TOP=/workspaces/maven-slimming-experiment; S=$TOP/results/scripts
source "$S/project_config.sh" petclinic
OUT=$TOP/results/petclinic/after/$NAME; mkdir -p "$OUT/logs"
cd "$CLONE" && git checkout -q "$REF" && git rev-parse HEAD > "$OUT/commit.txt"
./mvnw -B -q help:effective-pom -Doutput="$OUT/effective-pom.xml" > /dev/null 2>&1
python3 "$S/measure.py" declared "$OUT/effective-pom.xml" > "$OUT/declared.json"
./mvnw -B -q dependency:tree -DoutputFile="$OUT/dependency-tree.txt" > /dev/null 2>&1
python3 "$S/measure.py" tree "$OUT/dependency-tree.txt" > "$OUT/resolved.json"
"$S/build_time.sh" 5 "$OUT/build-time.tsv" "$OUT/logs/build" -- ./mvnw -B clean package -DskipTests > /dev/null
JAR=$(ls $ARTIFACT_GLOB | head -1)
python3 "$S/measure.py" artifact "$JAR" > "$OUT/artifact.json"; sha256sum "$JAR" > "$OUT/artifact.sha256"
mkdir -p "$CACHE_ROOT/artifacts/state-$NAME"; cp "$JAR" "$CACHE_ROOT/artifacts/state-$NAME/app.jar"
"$S/startup_time.sh" 10 "$OUT/startup.tsv" http://localhost:18080/actuator/health -- java -jar "$CACHE_ROOT/artifacts/state-$NAME/app.jar" --server.port=18080 > /dev/null
trivy rootfs --skip-db-update --skip-java-db-update --scanners vuln --format json -o "$OUT/trivy.json" "$CACHE_ROOT/artifacts/state-$NAME" > "$OUT/logs/trivy.log" 2>&1
python3 "$S/measure.py" trivy "$OUT/trivy.json" > "$OUT/trivy-summary.json"
trivy version --format json > "$OUT/trivy-db.json"
echo "$NAME done: $(python3 -c "import json;a=json.load(open('$OUT/artifact.json'));print(a['artifact_bytes'],a['lib_count'])")"
