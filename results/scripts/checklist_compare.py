#!/usr/bin/env python3
"""Compare two checklist JSON files (baseline vs candidate). Exit 1 on any difference.
usage: checklist_compare.py <baseline.json> <candidate.json>"""
import json, sys

a = {c["id"]: c for c in json.load(open(sys.argv[1]))}
b = {c["id"]: c for c in json.load(open(sys.argv[2]))}
diffs = []
for k in list(a) + [k for k in b if k not in a]:
    x, y = a.get(k), b.get(k)
    if x is None or y is None:
        diffs.append(f"{k}: missing in {'baseline' if x is None else 'candidate'}")
        continue
    for f in ("status", "content_type", "signature"):
        if x[f] != y[f]:
            diffs.append(f"{k} [{f}]: baseline={x[f]!r} candidate={y[f]!r}")
print(f"{len(a)} baseline items, {len(b)} candidate items, {len(diffs)} differences")
for d in diffs:
    print("  DIFF", d)
sys.exit(1 if diffs else 0)
