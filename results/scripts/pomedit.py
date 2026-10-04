#!/usr/bin/env python3
"""Minimal, formatting-preserving pom.xml edits used for slimming candidates.

  pomedit.py remove  <pom> <groupId> <artifactId>
  pomedit.py exclude <pom> <declaredGroupId> <declaredArtifactId> <exclGroupId> <exclArtifactId>
  pomedit.py add     <pom> <groupId> <artifactId> [scope]   (version managed by parent/BOM)

Edits only the project's top-level <dependencies> section (never dependencyManagement or plugins).
"""
import re, sys


def deps_span(s):
    # top-level <dependencies> = the first one not inside <dependencyManagement> or <plugin>
    for m in re.finditer(r"<dependencies>", s):
        before = s[:m.start()]
        if before.count("<dependencyManagement>") > before.count("</dependencyManagement>"):
            continue
        if before.count("<plugin>") > before.count("</plugin>"):
            continue
        if before.count("<profile>") > before.count("</profile>"):
            continue
        end = s.index("</dependencies>", m.end())
        return m.end(), end
    raise SystemExit("no top-level <dependencies>")


def find_dep(s, g, a):
    start, end = deps_span(s)
    for m in re.finditer(r"([ \t]*)<dependency>(.*?)</dependency>[ \t]*\n?", s[start:end], re.S):
        body = m.group(2)
        if re.search(rf"<groupId>\s*{re.escape(g)}\s*</groupId>", body) and \
           re.search(rf"<artifactId>\s*{re.escape(a)}\s*</artifactId>", body):
            return start + m.start(), start + m.end(), m.group(1), body
    raise SystemExit(f"dependency {g}:{a} not declared")


def remove(pom, g, a):
    s = open(pom).read()
    i, j, _, _ = find_dep(s, g, a)
    open(pom, "w").write(s[:i] + s[j:])


def exclude(pom, g, a, eg, ea):
    s = open(pom).read()
    i, j, ind, body = find_dep(s, g, a)
    excl = f"{ind}    <exclusion>\n{ind}      <groupId>{eg}</groupId>\n{ind}      <artifactId>{ea}</artifactId>\n{ind}    </exclusion>\n"
    if "<exclusions>" in body:
        new = s[i:j].replace(f"{ind}  </exclusions>", excl + f"{ind}  </exclusions>", 1)
    else:
        new = s[i:j].replace(f"{ind}</dependency>", f"{ind}  <exclusions>\n{excl}{ind}  </exclusions>\n{ind}</dependency>", 1)
    open(pom, "w").write(s[:i] + new + s[j:])


def add(pom, g, a, scope=None):
    s = open(pom).read()
    start, end = deps_span(s)
    sc = f"\n      <scope>{scope}</scope>" if scope else ""
    block = f"    <dependency>\n      <groupId>{g}</groupId>\n      <artifactId>{a}</artifactId>{sc}\n    </dependency>\n  "
    open(pom, "w").write(s[:end].rstrip() + "\n" + block + s[end:])


if __name__ == "__main__":
    {"remove": remove, "exclude": exclude, "add": add}[sys.argv[1]](*sys.argv[2:])
