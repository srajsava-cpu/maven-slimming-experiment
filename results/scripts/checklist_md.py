#!/usr/bin/env python3
"""Render checklist JSON files (one per profile) to a Markdown table.
usage: checklist_md.py <title> <profile>=<file.json> ..."""
import json, sys
title, pairs = sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]]
data = {p: {c["id"]: c for c in json.load(open(f))} for p, f in pairs}
first = data[pairs[0][0]]
print(f"# {title}\n")
print("Each item is run against every profile listed. Status, content type and signature must match baseline.\n")
print("| # | id | what | request | " + " | ".join(f"{p} status" for p, _ in pairs) + " | content type | baseline signature (" + pairs[0][0] + ") |")
print("|---|---|---|---|" + "---|" * len(pairs) + "---|---|")
for i, (k, c) in enumerate(first.items(), 1):
    sig = str(c["signature"]).replace("|", "\\|")
    others = [p for p, _ in pairs[1:] if data[p].get(k, {}).get("signature") != c["signature"]]
    if others:
        sig += " — differs on " + ", ".join(f"{p}: `{data[p].get(k, {}).get('signature')}`" for p in others)
    print(f"| {i} | {k} | {c['description']} | `{c['request']}` | " + " | ".join(str(data[p].get(k, {}).get("status")) for p, _ in pairs)
          + f" | {c['content_type'] or ''} | {sig} |")
