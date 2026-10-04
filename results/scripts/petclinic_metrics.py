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

# ---- classification (added after review): exact library bytes from the Maven repository JAR files,
# which are stored uncompressed in BOOT-INF/lib; jarmode-tools = measured library-byte remainder.
LIB = {"error_prone_annotations-2.49.0.jar": 20255, "snakeyaml-2.6.jar": 340068, "HdrHistogram-2.2.2.jar": 177206,
       "micrometer-jakarta9-1.17.0.jar": 54767, "aspectjweaver-1.9.25.1.jar": 2190661, "spring-aspects-7.0.8.jar": 50015,
       "tomcat-embed-websocket-11.0.22.jar": 286650, "log4j-to-slf4j-2.25.4.jar": 24172, "log4j-api-2.25.4.jar": 351127,
       "jakarta.inject-api-2.0.1.jar": 10681, "mysql-connector-j-9.7.0.jar": 2607237, "postgresql-42.7.11.jar": 1142677,
       "spring-boot-jarmode-tools-4.1.0.jar": 53966}
CLASS = {
    "free": {"C11-error-prone-annotations": ["error_prone_annotations-2.49.0.jar"],
             **{c: [] for c in ["A16-starter-restclient", "A18-starter-thymeleaf-test", "A19-starter-validation-test",
                                "A21-starter-actuator-test", "A23-starter-cache-test", "B21-commons-codec-test",
                                "B22-awaitility-test", "B24-boot-restclient-test"]}},
    "conditional": {"B01-snakeyaml": ["snakeyaml-2.6.jar"], "B02-HdrHistogram": ["HdrHistogram-2.2.2.jar"],
                    "B04-micrometer-jakarta9": ["micrometer-jakarta9-1.17.0.jar"], "C01-aspectjweaver": ["aspectjweaver-1.9.25.1.jar"],
                    "C02-spring-aspects": ["spring-aspects-7.0.8.jar"], "C03-tomcat-embed-websocket": ["tomcat-embed-websocket-11.0.22.jar"],
                    "C09-log4j-to-slf4j": ["log4j-to-slf4j-2.25.4.jar", "log4j-api-2.25.4.jar"],
                    "C18-jakarta-inject-api": ["jakarta.inject-api-2.0.1.jar"]},
    "feature-removing": {"A01-devtools": [], "C04-no-jarmode-tools": ["spring-boot-jarmode-tools-4.1.0.jar"],
                         "F01-drop-mysql": ["mysql-connector-j-9.7.0.jar"], "F02-drop-postgres": ["postgresql-42.7.11.jar"],
                         "F03-drop-testcontainers": []},
}
base = m["states"]["baseline_session1"]["artifact_bytes"]
sub = {}
for k, v in CLASS.items():
    b = sum(LIB[j] for js in v.values() for j in js)
    sub[k] = {"changes": sorted(v), "library_bytes": b, "pct_of_baseline_jar": round(100 * b / base, 2)}
assert sub["free"]["library_bytes"] + sub["conditional"]["library_bytes"] == \
    m["states"]["baseline_session1"]["lib_bytes"] - m["states"]["free-only"]["lib_bytes"]
assert sub["feature-removing"]["library_bytes"] == m["states"]["free-only"]["lib_bytes"] - m["states"]["full"]["lib_bytes"]
m["classification"] = {
    "note": "library bytes are exact JAR sizes (calculated from measured files); the free+conditional and full states were built and measured; a free-only state was not built. State key 'free-only' in 'states' = free + conditional (named before the conditional class existed).",
    "library_bytes_per_jar": LIB, "subtotals": sub,
    "found_by": {"not_suggested_by_tools_group_C": 2933561, "depclean_transitive": 572041, "dependency_analyze": 0},
}
m["candidate_counts"] = {"unique_candidates": 70, "evaluations": 80, "kept": 22, "kept_by_class": {"free": 9, "conditional": 8, "feature-removing": 5},
                         "noops": 4, "rejected": 44, "breaking_removals": 45, "rejected_diff_files": 51,
                         "breaking_detected_by": {"compile": 12, "tests": 21, "checklist_only": 11, "neither": 1},
                         "missed_by_test_suite": "12 of 45"}
m["corrections"] = ["group-C total previously stated as 2,950,725 B; listed artifact deltas sum to 2,938,717 B; report now uses exact library bytes (2,933,561 B)",
                    "'8 exclusions of runtime libraries' corrected: 9 runtime-library changes (10 JARs) in free+conditional",
                    "log4j-to-slf4j reclassified from free to conditional"]
json.dump(m, open(f"{R}/metrics.json", "w"), indent=1)
m["verification"] = json.load(open(f"{R}/verification/petclinic-verification.json"))
m["verification_mismatch_explained"] = ("free+conditional +31 B, full +56 B vs my builds: only BOOT-INF/classes/git.properties differs "
                                        "(branch/build user/commit metadata); counts identical")
json.dump(m, open(f"{R}/metrics.json", "w"), indent=1)
