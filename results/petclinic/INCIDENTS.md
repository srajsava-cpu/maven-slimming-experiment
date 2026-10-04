# PetClinic — what went wrong during the experiment

These are problems with the experiment harness, not with PetClinic itself. Each entry says how it was found, what it affected, and what was done.

## 1. Docker volume leak filled /workspaces (2026-10-04, found ~01:22 UTC)

- **Cause.** `petclinic_run_checklist.sh` removed its MySQL/Postgres containers with `docker rm -f` without `-v`, so every checklist run left the containers' anonymous data volumes behind. Postgres tests run through Docker Compose (`docker compose stop`) also leave stopped containers and volumes. By the time the user's low-disk warning arrived, Docker held **130 orphaned volumes = 13.05 GB** plus 3.78 GB of images. The project files themselves were 65 MB.
- **Free space on /workspaces (measured):** 16.19 GB before the baseline image build (~22:55 UTC), 1.68 GB at ~01:22 UTC during candidate C13, **18.75 GB after cleanup**. /tmp stayed above 100 GB throughout.
- **Cleanup:** `docker container prune`, `docker volume prune -a`, `docker image prune -a`, `docker builder prune -a`. Reclaimed 13.05 GB of volumes and 3.78 GB of images. Per-candidate JAR copies on /tmp were deleted after checking that each candidate's `artifact.json` (size + library list) and `artifact.sha256` were recorded and the checksum matched (2.2 GB → 63 MB; the baseline JAR is kept for the after-measurements). No build output was being saved under results/ or elsewhere on /workspaces; the clone's `target/` was 18 MB.
- **Fix:** the runner now uses `docker rm -f -v`. `evaluate_candidate.sh` prunes stopped containers and unused volumes after every candidate, deletes that candidate's JAR copy once recorded, writes `disk-free-before.txt` / `disk-free-after.txt` per candidate, and refuses to start a candidate if /workspaces has under 5 GB free.
- **Which candidates ran with little disk.** Free space was not sampled per candidate before the fix, so this is an **estimate**, not a measurement: assuming the leak grew roughly linearly between the two measured points, free space fell below ~3 GB around 01:03 UTC. That covers candidates **C05–C13**. Rejected candidates in that window: C05, C06 (compile errors, which disk space cannot cause), C07, C08, C12, C13.
- **Log search across every candidate** for `No space left`, `ENOSPC`, write errors, failed image pulls/extractions and container start/initialisation failures found one hit, in A10. There `ContainerLaunchException` was caused by `NoDriverFoundException: Could not get Driver`: Testcontainers needs the MySQL JDBC driver that A10 had just removed. So it was not disk-related. No checklist run had a startup failure. Every checklist-caught rejection shows the **same number of differences on all three profiles, including in-memory H2**, which rules out a database-container cause.
- **Re-runs (conservative):** C07, C08, C12, C13 (rejected inside the low-disk window, failure involves runtime behaviour) and A22 (failure symptom was a database connection error, even though the log shows Compose was never started because the module was removed). Results: see section 6 below and PROGRESS.md.

## 2. Wrong process killed during a status check (2026-10-04 ~01:15 UTC)

While answering a status check I killed what I believed was a stuck "wait for group A" shell. It was actually the parent shell of the running group B→C batch. The batch script (`candidates-C.sh`) survived, re-parented to init, and kept writing to its log. Only the automatic completion notification was lost; a replacement watcher was started on its PID. No candidate results were affected (verified: one commit and one `changes/<id>/` directory per candidate).

## 3. Wait loops that matched themselves

Two of my wait loops used `pgrep -f '<pattern>'`. The loop's own command line contains the pattern, so the loop never ended. Both were found and killed; neither affected any measurement. Later waits use the batch PID (`kill -0 <pid>`) instead.

## 4. Script edited while a running instance was executing it (2026-10-03 ~23:05 UTC)

I edited `run_candidate.sh` (to add the HOLD option) while group A was running it. Bash reads scripts incrementally, so a shifted byte offset could have made the running instance re-execute lines. The original bytes were restored within seconds, while the in-flight candidate (A02) was inside its Maven build. The edit was re-applied after the batch finished. Checked afterwards: exactly one commit and one result directory per candidate.

## 5. Checklist readiness probe depended on actuator

The checklist runner first waited for `/actuator/health` before running the checklist. For A02 (actuator starter removed) the app was therefore reported as "never started" and every item as "missing". The probe was changed to `GET /` and A02's checklist was re-run on its saved JAR: 41 differences per profile, all actuator endpoints returning 404. A02 was rejected either way. All later candidates used the `/` probe.

## 6. Re-run outcomes

Re-run 2026-10-04 with 16–18 GB free on /workspaces. They were applied on top of the branch as it stood then, which also contained the changes kept between the original run and the re-run. **No verdict changed, and the error counts were identical:**

| candidate | original | re-run |
|---|---|---|
| A22 remove spring-boot-docker-compose (test) | REJECT: 81 run, 2 errors (PostgresIntegrationTests) | REJECT: 81 run, 2 errors |
| C07 exclude jaxb-runtime | REJECT: tests pass, checklist: `GET /vets` as XML → 500 on all 3 profiles | REJECT: identical |
| C08 exclude byte-buddy | REJECT: 81 run, 70 errors | REJECT: 81 run, 70 errors |
| C12 exclude jspecify | REJECT: 81 run, 63 errors | REJECT: 81 run, 63 errors |
| C13 exclude antlr4-runtime | REJECT: 81 run, 20 errors | REJECT: 81 run, 20 errors |

Conclusion: the low-disk period did not change any PetClinic result.

## 7. Four candidates were no-ops but logged as "KEPT"

B23 (micrometer-observation-test), B25 (spring-boot-micrometer-metrics-test), B26 (spring-boot-cache-test) and C10 (log4j-api) were already absent from the resolved graph when their turn came. Their parent had been removed by an earlier kept change (A21, A21, A23, C09 respectively). So the exclusion helper made no edit, `git commit` had nothing to commit, and the evaluation re-measured the previous commit and logged "KEPT". These four results contribute **0 bytes** and are now marked NO-OP in PROGRESS.md (`changes/<id>/NOOP.txt`). Found by checking each result's recorded commit against its candidate id. **No harm was done:** none of the no-ops was followed by a REJECT, which would have reset away the previous real commit. `run_candidate.sh` now stops and records a NO-OP when an edit changes nothing.

## 8. A kept change (B03, jul-to-slf4j) changed logging; the checklist did not cover logs

Found by inspecting app logs before classifying the kept changes. Without `jul-to-slf4j`, everything that logs through `java.util.logging` (Tomcat/Catalina/Coyote) bypasses Logback. It prints in the JDK's two-line SimpleFormatter format and no longer follows `logging.level.*` or any Logback appender. The 81 tests and the 57-item HTTP checklist were all unchanged, so B03 had been kept.

Action: the checklist gained a **log-routing** item (count of JUL SimpleFormatter lines in the app log; baseline 0). The baseline checklist was re-run with it: the 57 original items were unchanged, and log-routing = 0 on all profiles. The previous version is kept as `baseline/checklist-v1/`. Applied retroactively to the saved app logs of every candidate: 0 before B03; 7 from B03 onwards, inherited by every later cumulative state, and in no candidate before B03. B03 was reverted on the branch by commit R01. After R01 the H2 checklist (58 items) matches baseline exactly, and log-routing is 0 on all profiles. **B03 is counted as rejected, caught by neither the tests nor the original checklist.**

## 9. MySQL readiness race made C18 fail on one profile

C18 (exclude jakarta.inject-api) passed all tests and matched the checklist on H2 and Postgres. But the app failed to start on the `mysql` profile: `CommunicationsException: Communications link failure` while running the init script. Cause: the runner considered MySQL ready once `docker exec ... mysql -e 'select 1'` succeeded. The `mysql:9.7` image first runs a temporary, socket-only server to initialise the database, so that check can pass before the real TCP server is up. C18 was the first MySQL start after the disk cleanup had pruned the image (cold pull + first init). Fix: readiness now uses `mysqladmin ping -h 127.0.0.1 --protocol=tcp`, which only the real server answers. Search of every candidate's checklist logs: the only other "APP FAILED TO START" was A02, whose cause was the actuator probe (incident 5). The race can only produce false rejections, never false passes. C18 was re-run on the free-only branch (the full branch no longer supports MySQL): **verdict changed from REJECT to KEEP** (81 tests, 58×3 checklist items identical, −11,384 B). It was then applied to the full branch as `C18-jakarta-inject-api-on-full` and evaluated there (77 tests, checklist identical to the pre-C18 full state). All after-measurements and the independent verification were redone with C18 included; the earlier ones are kept in `after-superseded-pre-C18/` and `verification-superseded-pre-C18/`.

## 10. Report errors corrected after review (2026-10-04)

Found in review of REPORT.md, corrected in text only (no re-runs):
- **Group-C total.** The tool-unsuggested total was given as 2,950,725 B, but its six listed items (artifact deltas) sum to 2,938,717 B: an arithmetic error. All subtotals now use exact library bytes (group C 2,933,561 B = 83.68 %; DepClean 572,041 B = 16.32 %). These reconcile exactly with the measured library-byte change.
- **Exclusion count.** "8 exclusions of runtime libraries" named 9. The free + conditional state has 9 runtime-library changes, removing 10 JARs.
- **Candidate counts.** The relation between candidate counts was unexplained. A table now reconciles 70 unique candidates, 80 evaluations, 22 kept, 4 no-ops, 44 rejected, 45 breaking removals and 51 rejected diffs. The "82" in a chat message was a miscount (80).
- **Classification.** "Free" was too generous. A **conditional** class was added (safe for this app as exercised, removes a capability another app may use). log4j-to-slf4j was reclassified from free to conditional (same failure family as jul-to-slf4j, B03). Free is now 20,255 B; conditional 3,485,347 B; feature-removing 3,803,880 B.
