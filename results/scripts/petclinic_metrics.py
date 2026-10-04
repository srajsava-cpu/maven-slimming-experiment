#!/usr/bin/env python3
"""Assemble results/petclinic/metrics.json and print Markdown tables for the report from the raw files."""
import csv, glob, json, os, re, statistics as st, subprocess

R = "/workspaces/maven-slimming-experiment/results/petclinic"
J = lambda p: json.load(open(os.path.join(R, p)))


def tsv(p, col, filt=None):
    rows = csv.DictReader(open(os.path.join(R, p)), delimiter="\t")
    return [float(r[col]) for r in rows if (filt is None or filt(r)) and r[col] not in ("", "FAILED")]


def rng(v):
    return {"n": len(v), "median": round(st.median(v), 3), "min": min(v), "max": max(v), "values": v}


def state(d, tests_dir):
    a = J(f"{d}/artifact.json")
    t = J(f"{tests_dir}/tests.json")
    return {
        "artifact_bytes": a["artifact_bytes"], "lib_count": a["lib_count"], "lib_bytes": a["lib_bytes_uncompressed"],
        "top15": a["top15"], "declared_by_scope": J(f"{d}/declared.json")["by_scope_count"],
        "declared_total": J(f"{d}/declared.json")["total"], "resolved": J(f"{d}/resolved.json"),
        "tests": {k: t[k] for k in ("run", "failures", "errors", "skipped")}, "skipped_list": t["skipped_list"],
        "startup_wall_s": rng(tsv(f"{d}/startup.tsv", "wall_seconds")),
        "startup_self_reported_s": rng(tsv(f"{d}/startup.tsv", "self_reported")),
        "clean_build_s": rng(tsv(f"{d}/build-time.tsv", "wall_seconds")),
        "trivy": J(f"{d}/trivy-summary.json") if os.path.exists(f"{R}/{d}/trivy-summary.json") else None,
    }


m = {"project": "spring-petclinic", "commit": "500158f732419217507c7656904b8e6aa1bcc0d6", "states": {}}
# session 1 baseline (2026-10-03 22:40-22:56 UTC)
b = state("baseline", "baseline")
b["trivy"] = json.loads(subprocess.check_output(
    ["python3", "/workspaces/maven-slimming-experiment/results/scripts/measure.py", "trivy", f"{R}/baseline/trivy.json"]))
b["image"] = J("baseline/image.json")
m["states"]["baseline_session1"] = b
for name, tdir in [("baseline-rerun", "baseline"), ("free-only", "changes/C18-jakarta-inject-api-rerun"), ("full", "changes/C18-jakarta-inject-api-on-full")]:
    m["states"][name] = state(f"after/{name}", tdir)
il = "after/build-time-interleaved.tsv"
m["clean_build_interleaved_s"] = {s: rng(tsv(il, "wall_seconds", lambda r, s=s: r["state"] == s)) for s in ("baseline", "free-only", "full")}
m["images"] = J("after/images.json")
m["trivy_db"] = J("baseline/trivy-db.json")

# per-candidate records
cands = {}
for d in sorted(glob.glob(f"{R}/changes/*/")):
    cid = os.path.basename(d.rstrip("/"))
    if os.path.exists(d + "NOOP.txt"):
        cands[cid] = {"noop": open(d + "NOOP.txt").read().strip()}
    elif os.path.exists(d + "summary.json"):
        cands[cid] = json.load(open(d + "summary.json"))
m["candidates"] = cands
json.dump(m, open(f"{R}/metrics.json", "w"), indent=1)

# kept-change table: delta vs previous kept state on the `slim` branch, in branch order
order = ["A01-devtools", "A16-starter-restclient", "A18-starter-thymeleaf-test", "A19-starter-validation-test",
         "A21-starter-actuator-test", "A23-starter-cache-test", "B01-snakeyaml", "B02-HdrHistogram", "B03-jul-to-slf4j",
         "B04-micrometer-jakarta9", "B21-commons-codec-test", "B22-awaitility-test", "B24-boot-restclient-test",
         "C01-aspectjweaver", "C02-spring-aspects", "C03-tomcat-embed-websocket", "C04-no-jarmode-tools",
         "C09-log4j-to-slf4j", "C11-error-prone-annotations", "F01-drop-mysql", "F02-drop-postgres",
         "F03-drop-testcontainers", "R01-revert-B03-jul-to-slf4j", "C18-jakarta-inject-api-on-full"]
prev = m["states"]["baseline_session1"]["artifact_bytes"]
print("| change | artifact bytes after | Δ vs previous kept state | libs removed (vs previous) |")
prev_libs = set(J("baseline/artifact.json")["libs"])
for c in order:
    s = cands[c]
    libs = set(J(f"changes/{c}/artifact.json")["libs"])
    print(f"| {c} | {s['artifact_bytes']:,} | {s['artifact_bytes'] - prev:+,} | {', '.join(sorted(prev_libs - libs)) or '—'}"
          + (f" (+{', '.join(sorted(libs - prev_libs))})" if libs - prev_libs else "") + " |")
    prev, prev_libs = s["artifact_bytes"], libs
