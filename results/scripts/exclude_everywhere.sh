#!/usr/bin/env bash
# Exclude a transitive artifact from every declared dependency that brings it in (run inside a clone).
# Loops: find the declared dependency on the path shown by dependency:tree, add an <exclusion>, repeat
# until the artifact no longer resolves. usage: exclude_everywhere.sh <groupId> <artifactId>
set -u
G=$1; A=$2
PE="python3 /workspaces/maven-slimming-experiment/results/scripts/pomedit.py"
T=$(mktemp)
for i in $(seq 1 20); do
  ./mvnw -B -q dependency:tree -Dincludes="$G:$A" -DoutputFile="$T" >/dev/null 2>&1 || { echo "tree failed"; exit 1; }
  # line 2 of the filtered tree is the declared (depth-1) dependency on the path
  decl=$(sed -n 2p "$T" | sed -E 's/^[+\\| -]*//' | cut -d: -f1,2)
  [ -z "$decl" ] && { echo "excluded $G:$A after $((i-1)) exclusion(s)"; rm -f "$T"; exit 0; }
  if [ "$decl" = "$G:$A" ]; then echo "$G:$A is declared directly; use remove"; exit 1; fi
  $PE exclude pom.xml "${decl%%:*}" "${decl##*:}" "$G" "$A" || exit 1
done
echo "gave up"; exit 1
