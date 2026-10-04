#!/usr/bin/env python3
"""Regenerate results/<project>/PROGRESS.md from changes/*/summary.json and the candidate batch logs.
usage: progress_md.py <project>"""
import glob, json, os, re, sys, datetime
P = sys.argv[1]
R = f"/workspaces/maven-slimming-experiment/results/{P}"
verdicts = {}
for log in sorted(glob.glob(f"{R}/logs/candidates-*.log")) + [f"{R}/logs/manual-candidates.log"]:
    if os.path.exists(log):
        for m in re.finditer(r"^(\S+) (KEPT|REJECTED|HELD)", open(log).read(), re.M):
            verdicts[m.group(1)] = m.group(2)
rows = []
for d in sorted(glob.glob(f"{R}/changes/*/")):
    cid = os.path.basename(d.rstrip("/"))
    s = json.load(open(d + "summary.json")) if os.path.exists(d + "summary.json") else None
    msg = open(d + "commit.txt").read().split(" ", 1)[1].strip() if os.path.exists(d + "commit.txt") else ""
    if os.path.exists(d + "NOOP.txt"):
        msg = ""
    v = verdicts.get(cid, "IN PROGRESS" if s is None else "?")
    if os.path.exists(d + "NOOP.txt"):
        rows.append(f"| {cid} | {msg} | NO-OP | | | | | {open(d + 'NOOP.txt').read().strip()} |"); continue
    if s is None:
        rows.append(f"| {cid} | {msg} | IN PROGRESS | | | | | |"); continue
    tests = f"{s['tests_run']} run / {s['failures']}F {s['errors']}E {s['skipped']}S" + ("" if s["verify_exit"] == 0 else " (build failed)")
    delta = "" if s.get("artifact_delta_vs_baseline") is None else f"{s['artifact_delta_vs_baseline']:+,}"
    caught_by = ""
    if v == "REJECTED":
        caught_by = "tests/build" if not s["tests_pass"] or not s["same_tests_as_baseline"] else "checklist only"
    rows.append(f"| {cid} | {msg} | {v} | {tests} | {s['checklist']} | {delta} | {s.get('lib_count') or ''} | {caught_by} |")
out = [f"# {P} — progress", "", f"Regenerated {datetime.datetime.now(datetime.UTC):%Y-%m-%d %H:%M} UTC from `changes/*/summary.json` "
       "(script: `results/scripts/progress_md.py`). Artifact delta is against the unmodified baseline JAR and is cumulative "
       "over the changes kept before it. 'checklist only' = full test suite passed, the behaviour checklist caught the break.", "",
       "| candidate | change | result | tests (full verify) | checklist | artifact Δ bytes vs baseline | libs | caught by |",
       "|---|---|---|---|---|---|---|---|"] + rows
open(f"{R}/PROGRESS.md", "w").write("\n".join(out) + "\n")
print(f"{len(rows)} candidates written")
