#!/usr/bin/env python3
"""Measurement helpers shared by all projects. Every sub-command prints JSON.

  measure.py artifact <file.jar|file.war>      size + bundled library JARs
  measure.py declared <effective-pom.xml>      declared dependencies by scope
  measure.py tree <tree.txt>                   resolved deps (direct/transitive) by scope
  measure.py tests <dir> [<dir> ...]           surefire/failsafe XML report totals + skipped list
  measure.py trivy <trivy.json>                vulnerability counts by severity
  measure.py stats <n1> <n2> ...               median/min/max
"""
import json, os, re, statistics, sys, zipfile, glob
import xml.etree.ElementTree as ET


def artifact(path):
    z = zipfile.ZipFile(path)
    libs = [i for i in z.infolist()
            if re.match(r'^(BOOT-INF|WEB-INF)/lib/[^/]+\.jar$', i.filename)]
    libs.sort(key=lambda i: -i.file_size)
    return {
        "artifact": os.path.basename(path),
        "artifact_bytes": os.path.getsize(path),
        "lib_count": len(libs),
        "lib_bytes_uncompressed": sum(i.file_size for i in libs),
        "lib_bytes_in_archive": sum(i.compress_size for i in libs),
        "top15": [{"name": i.filename.split('/')[-1], "bytes": i.file_size} for i in libs[:15]],
        "libs": sorted(i.filename.split('/')[-1] for i in libs),
    }


def declared(effective_pom):
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    root = ET.parse(effective_pom).getroot()
    # effective-pom output may wrap several projects; take the first <project>
    proj = root if root.tag.endswith("project") else root.find("m:project", ns)
    deps = proj.find("m:dependencies", ns)
    out = {}
    for d in (deps if deps is not None else []):
        g = d.findtext("m:groupId", namespaces=ns)
        a = d.findtext("m:artifactId", namespaces=ns)
        s = d.findtext("m:scope", default="compile", namespaces=ns)
        opt = d.findtext("m:optional", default="false", namespaces=ns) == "true"
        out.setdefault(s, []).append(f"{g}:{a}" + (" (optional)" if opt else ""))
    return {"by_scope_count": {k: len(v) for k, v in out.items()},
            "total": sum(len(v) for v in out.values()), "by_scope": out}


TREE_LINE = re.compile(r'^(?P<prefix>[| +\\-]*)(?P<coord>[^\s:]+:[^\s:]+:[^\s]+)')


def tree(path):
    """Parse `dependency:tree` text output (one or more modules). Root lines have no prefix."""
    direct, trans = {}, {}
    seen = set()
    for line in open(path):
        line = line.rstrip("\n")
        line = re.sub(r'^\[INFO\] ', '', line)
        m = TREE_LINE.match(line)
        if not m:
            continue
        prefix, coord = m.group("prefix"), m.group("coord")
        parts = coord.split(":")
        if not prefix:          # module root
            continue
        if len(parts) < 5:
            continue
        scope = parts[-1].split()[0]
        ga = parts[0] + ":" + parts[1] + (":" + parts[3] if len(parts) == 6 else "")
        depth = len(prefix) // 3
        key = (ga, scope)
        if key in seen:
            continue
        seen.add(key)
        (direct if depth == 1 else trans).setdefault(scope, []).append(coord)
    scopes = sorted(set(direct) | set(trans))
    return {
        "by_scope": {s: {"direct": len(direct.get(s, [])), "transitive": len(trans.get(s, [])),
                         "total": len(direct.get(s, [])) + len(trans.get(s, []))} for s in scopes},
        "direct_total": sum(map(len, direct.values())),
        "transitive_total": sum(map(len, trans.values())),
        "total": sum(map(len, direct.values())) + sum(map(len, trans.values())),
    }


def tests(*dirs):
    tot = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    skipped, per_class = [], {}
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "TEST-*.xml"))):
            r = ET.parse(f).getroot()
            for k in tot:
                tot[k] += int(r.get(k, 0))
            per_class[r.get("name")] = int(r.get("tests", 0))
            for tc in r.iter("testcase"):
                s = tc.find("skipped")
                if s is not None:
                    skipped.append({"test": f'{tc.get("classname")}#{tc.get("name")}',
                                    "reason": s.get("message") or (s.text or "").strip()[:300]})
    tot["run"] = tot["tests"]
    tot["skipped_list"] = skipped
    tot["per_class"] = per_class
    return tot


def trivy(path):
    data = json.load(open(path))
    counts, ids = {}, set()
    for res in data.get("Results", []) or []:
        for v in res.get("Vulnerabilities", []) or []:
            key = (v["VulnerabilityID"], v["PkgName"], v.get("InstalledVersion"))
            if key in ids:
                continue
            ids.add(key)
            counts[v["Severity"]] = counts.get(v["Severity"], 0) + 1
    return {"by_severity": counts, "total": sum(counts.values()),
            "findings": sorted(f"{a} {b}@{c}" for a, b, c in ids)}


def stats(*nums):
    xs = [float(x) for x in nums]
    return {"n": len(xs), "median": statistics.median(xs), "min": min(xs), "max": max(xs), "values": xs}


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    print(json.dumps(globals()[cmd](*args), indent=2))
