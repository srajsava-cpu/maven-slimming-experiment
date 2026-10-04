# maven-slimming-experiment

This is a measured experiment in **Maven dependency slimming**. It asks how much an executable Spring Boot JAR can be shrunk by removing or excluding dependencies, how good the two common analyzers are at finding what to remove, and how often a passing test suite hides a removal that breaks behaviour.

**Scope.** One project was run: **Spring PetClinic** at commit `500158f7` (Spring Boot 4.1.0, JDK 17), in a GitHub Codespace (4 vCPU, 16 GB, x86_64), on 2026-10-03/04. The JHipster sample app and Dependency-Track were planned but **not run**, so there is no cross-project summary.

## Method, in one paragraph

* **Baseline.** Build exactly as the project documents (`./mvnw verify`, with the MySQL and Postgres container tests really running). Measure the artifact, libraries, dependencies, tests, startup, build time, Trivy vulnerabilities and the container image. Write a 58-item HTTP behaviour checklist and run it against H2, MySQL and Postgres.
* **Analysis.** Run `dependency:analyze` and DepClean.
* **Slimming.** Try every flagged dependency, plus reductions found by reading the tree, one commit at a time. Each commit gets a full clean `verify` and the full checklist on all three databases. A change is kept only if the same tests pass and every checklist item is identical.
* **After and verification.** Re-measure everything. Have a separate agent that had not seen any numbers rebuild baseline and slimmed versions from a fresh clone.

## Headline numbers (PetClinic, all measured)

Kept changes are split into three classes and never added together without the split:

| class | meaning | library bytes removed | % of the 65,831,325-byte JAR |
|---|---|---|---|
| free | no capability lost for any app | 20,255 | 0.03 % |
| conditional | unused by PetClinic, but removes a capability another app may rely on (YAML config, AspectJ, WebSocket, Log4j-API bridge, percentiles, JMS/Mail metrics, JSR-330) | 3,485,347 | 5.29 % |
| feature-removing | removes a supported feature (MySQL and Postgres support, jarmode tools, devtools) | 3,803,880 | 5.78 % |

* **Measured artifact change:** −3,513,027 B (−5.34 %) for free + conditional; −7,326,516 B (−11.13 %) with feature removal too.
* **Startup and clean-build time:** no measurable change.
* **Known vulnerabilities (Trivy):** 14 → 13 → 12.
* **Analyzers:** `dependency:analyze` flagged 23 of 28 declared dependencies. 17 were false positives, and the 6 removable ones save 0 runtime bytes. DepClean flagged 55. 84 % of the runtime bytes removed came from changes **neither tool suggested**.
* **The test suite missed 12 of 45 breaking removals.** 11 were caught only by the behaviour checklist; examples include an XML endpoint returning 500, a silently swapped cache provider, missing static assets and missing actuator endpoints. 1 (log routing) was caught by neither and found by reading logs.
* **Independent verification:** reproduced every count exactly. Artifact sizes matched to within 31–56 bytes, all in `git.properties` build metadata.

The full write-up, including scope and limits, is in **[results/petclinic/REPORT.md](results/petclinic/REPORT.md)**.

## Where things are

| path | contents |
|---|---|
| `results/petclinic/REPORT.md` | the report: environment, before/after table, every change, analyzer verdicts, what broke and how it was found, verification, reproduction commands, scope and limits |
| `results/petclinic/metrics.json` | all raw numbers, including the classification, subtotals and candidate counts |
| `results/petclinic/PROGRESS.md` | one line per candidate evaluation (80) with its result |
| `results/petclinic/INCIDENTS.md` | everything that went wrong with the experiment harness and how it was handled, plus corrections made after review |
| `results/petclinic/CHECKLIST.md` | the behaviour checklist with baseline results for H2, MySQL and Postgres |
| `results/petclinic/kept-changes-*.diff`, `rejected/` | the kept changes as patches against the pinned commit, and every rejected change |
| `results/petclinic/baseline/`, `after/`, `analysis/`, `changes/<id>/`, `verification/` | raw evidence: dependency trees, test results, checklist outputs, app and build logs (large logs gzipped) |
| `results/scripts/` | the measurement and evaluation scripts. `env.sh` puts caches on `/tmp`; `run_candidate.sh` / `evaluate_candidate.sh` drive one candidate; `measure.py` does the counting |
| `work/` | local clones of the projects. Git-ignored, never committed |
