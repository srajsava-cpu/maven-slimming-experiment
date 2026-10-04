# Spring PetClinic: dependency slimming report

**Verdict.** The kept changes fall into three classes. They are reported separately here and should not be added into one headline without the split. Sizes are exact library bytes removed from the executable JAR; the baseline JAR is 65,831,325 bytes.

| class | meaning | library bytes removed | % of baseline JAR |
|---|---|---|---|
| **free** | no capability lost for any app | **20,255** (error_prone_annotations) | **0.03 %** |
| **conditional** | safe for this app as exercised, but removes a capability another app could rely on | **3,485,347** (9 JARs) | **5.29 %** |
| **feature-removing** | removes a capability this project supports | **3,803,880** (MySQL and Postgres drivers, jarmode tools) | **5.78 %** |

**Measured artifact totals** for the two states that were built and verified:
* **free + conditional:** −3,513,027 B (−5.34 %).
* **all kept changes:** −7,326,516 B (−11.13 %).
* These include a few KB of zip and metadata overhead on top of the library bytes.

**What did not change.** Startup time and clean build time showed **no measurable change**. Known vulnerabilities fell from 14 to 13 (free + conditional) or 12 (all kept).

**Honest reading.** Almost nothing here is a no-strings saving. The 5.3 % comes from removing optional capabilities PetClinic does not use: YAML config, AspectJ, WebSocket, percentile histograms, the Log4j-API bridge, JMS/Mail metrics, JSR-330. Each is fine for this app and a trap for one that uses them. Most of the rest is dropping two supported databases.

**The analyzers were a poor guide.**
* `dependency:analyze` flagged 23 of 28 declared dependencies. 17 were false positives; the 6 removable ones are test-scope or devtools and save 0 runtime bytes.
* DepClean flagged 55. Acting on its list saves 572,041 B, all of it in the conditional class.
* 84 % of the runtime library bytes removed came from changes neither tool suggested (aspectjweaver alone is 2.19 MB).

**The test suite missed 12 of 45 breaking removals.** 11 were caught only by the behaviour checklist; 1 (log routing) was caught by neither and found by reading logs.

**All numbers below were measured in this run** unless marked *calculated* or *static*. Nothing is carried over from the earlier Mac run. One project, one Spring Boot version, one machine: see section 9, Scope and limits.

---

## 1. Environment

| item | value |
|---|---|
| Project / commit | spring-projects/spring-petclinic `500158f732419217507c7656904b8e6aa1bcc0d6` (2026-09-29), Spring Boot 4.1.0 |
| Where | GitHub Codespace (4-core machine type), session 2026-10-03 22:36 – 2026-10-04 ~03:30 UTC |
| CPU / cores | AMD EPYC 7763, 4 vCPUs, x86_64 |
| RAM | 16,770,494,464 bytes (15.6 GiB), no swap |
| OS | Ubuntu 24.04.5 LTS, kernel 6.8.0-1064-azure |
| JDK | Microsoft Build of OpenJDK 17.0.20.1 (SDKMAN `17.0.20+1-ms`), selected per project via `JAVA_HOME` |
| Maven | 3.9.16 via the project's wrapper (wrapper 3.3.4) |
| Docker | 29.8.0-1 (client and server), Docker-in-Docker, containerd image store |
| Docker storage disk | `/var/lib/docker` and `/var/lib/containerd` on `/dev/loop6`, **the same disk as /workspaces** (not moved: see "What went wrong" #1) |
| Caches | **On /tmp** (`/dev/sda1`, separate disk): Maven local repository, Maven wrapper distributions, npm cache, Trivy DB cache, verification clones. Set per session via `results/scripts/env.sh` (`MAVEN_OPTS=-Dmaven.repo.local=…`, `MAVEN_USER_HOME`, `npm_config_cache`, `TRIVY_CACHE_DIR`). No project file was edited for this. |
| Trivy | 0.75.0; vulnerability DB updated 2026-10-03T19:02:38Z, Java DB updated 2026-10-03T01:07:11Z. All after-scans used `--skip-db-update --skip-java-db-update`, so before and after were scanned against the same DB |
| Analyzers | maven-dependency-plugin 3.10.0 (`dependency:analyze`), DepClean `se.kth.castor:depclean-maven-plugin:2.2.0` |

Build as documented by the project (README and CI workflow): `./mvnw -B verify` with JDK 17. The container image uses `./mvnw spring-boot:build-image`; the project has no Dockerfile.

---

## 2. Before/after

Three states were built and measured:
* **baseline** = the pinned commit.
* **free + conditional** = all kept changes except the feature-removing ones: branch `slim-free`, diff `kept-changes-free-only.diff`.
  * The branch and file names predate the conditional class. This state contains the 1 free runtime change, the 8 conditional changes and the 8 test-scope changes.
* **full** = everything kept: branch `slim`, diff `kept-changes-full.diff`.

A "free only" state (just error_prone_annotations plus the test-scope changes) was **not built**. Its library saving of 20,255 B is calculated from the exact JAR size. Percentages are relative to baseline. The last column is the extra effect of the feature-removing changes (full minus free + conditional).

| metric | baseline | free + conditional | Δ | full | Δ full (vs baseline) | of which feature-removing |
|---|---|---|---|---|---|---|
| Executable JAR (bytes) | 65,831,325 | 62,318,298 | −3,513,027 (−5.34 %) | 58,504,809 | −7,326,516 (−11.13 %) | −3,813,489 |
| Bundled library JARs (count) | 93 | 83 | −10 (−10.8 %) | 80 | −13 (−14.0 %) | −3 |
| Bundled library JARs (bytes) | 65,137,021 | 61,631,419 | −3,505,602 (−5.38 %) | 57,827,539 | −7,309,482 (−11.22 %) | −3,803,880 |
| Declared deps (compile / runtime / test) | 9 / 7 / 12 = 28 | 9 / 7 / 7 = 23 | −5 | 8 / 5 / 3 = 16 | −12 | −7 |
| Resolved deps, total (`dependency:tree`) | 171 | 150 | −21 (−12.3 %) | 131 | −40 (−23.4 %) | −19 |
| — compile (direct + transitive) | 89 | 82 | −7 | 81 | −8 | −1 |
| — runtime | 17 | 14 | −3 | 12 | −5 | −2 |
| — test | 65 | 54 | −11 | 38 | −27 | −16 |
| Tests run / failed / skipped | 81 / 0 / 0 | 81 / 0 / 0 | same tests | 77 / 0 / 0 | −4 (MySQL + Postgres integration tests deleted with the feature) | −4 |
| Startup, wall to first HTTP 200 on `/actuator/health`, 10 runs: median [min–max] s | 9.312 [9.040–10.059] | 9.261 [8.938–10.372] | no measurable change | 9.133 [8.767–9.539] | no measurable change | — |
| Startup, Spring's "Started … in" (same runs) s | 8.296 [8.020–9.042] | 8.253 [7.947–9.127] | no measurable change | 8.149 [7.725–8.591] | no measurable change | — |
| Clean build, warm cache (`clean package -DskipTests`), 5 runs interleaved: median [min–max] s | 15.880 [15.453–17.891] | 15.438 [14.799–16.613] | no measurable change | 14.520 [13.507–16.219] | no measurable change | — |
| Trivy vulnerabilities in the JAR (C / H / M / L) | 3 / 6 / 5 / 0 = 14 | 3 / 6 / 4 / 0 = 13 | −1 M (CVE-2026-49844, log4j-api: a conditional change) | 3 / 5 / 4 / 0 = 12 | −2 | −1 H (CVE-2026-54291, postgresql) |
| Container image, `docker save` archive (compressed layers) bytes | 276,368,384 | 272,721,408 | −3,646,976 (−1.32 %) | 268,836,864 | −7,531,520 (−2.73 %) | −3,884,544 |
| Container image, `docker image inspect` Size bytes¹ | 570,913,253 | 563,608,549 | −7,304,704 (−1.28 %) | 555,832,804 | −15,080,449 (−2.64 %) | −7,775,745 |

¹ With the containerd image store, `Size` counts compressed blobs *plus* the unpacked snapshot, so a change shows up roughly twice. This was checked by exporting the image filesystems (on the pre-C18 build of the same state). The free + conditional image held 3,494,921 fewer bytes of `BOOT-INF/lib` and ~100 KB less SBOM, and nothing else differed. Quote the `docker save` row. The image content is otherwise dominated by the JRE layer (184.7 MB uncompressed), which slimming does not touch.

**Timing notes.**
* Timings were measured three times in one session: the original baseline (22:52 UTC: startup 9.698–10.091 s, build 15.168–15.685 s); a pre-C18 after-session (02:05–02:24); and the final after-session above (02:37–02:50). The baseline was re-measured in each after-session so before and after share a session.
* In the pre-C18 session the full state's build range (13.697–14.581 s, interleaved) did not overlap the baseline (14.995–15.518 s). In the final session it does overlap.
* Because a separation that appears in one session and not the next is not robust on this shared machine, the report says **no measurable change** for build time. All startup comparisons overlap in every session.
* The baseline's own build median moved from 15.4 s (22:53) to 14.3 s (02:05) to 15.9 s (02:50). That gives a sense of the noise.

**Top 15 bundled JARs**
* Baseline, bytes: hibernate-core 15,258,514; byte-buddy 4,655,898; tomcat-embed-core 3,599,448; h2 2,685,418; mysql-connector-j 2,607,237; spring-web 2,218,865; aspectjweaver 2,190,661; spring-data-jpa 2,178,660; spring-core 2,035,553; jackson-databind 1,940,679; bootstrap (webjar) 1,841,258; spring-data-commons 1,773,391; hibernate-validator 1,404,084; spring-context 1,398,484; spring-boot 1,391,652.
* Free + conditional: aspectjweaver leaves the list.
* Full: aspectjweaver and mysql-connector-j leave the list.
* Full lists for every state are in `metrics.json` (`states.*.top15`) and `after/*/artifact.json`.

**Skipped tests:** none in any state. Database and container tests really ran in the baseline:
* `MySqlIntegrationTests` (2 tests) started `mysql:9.7` through Testcontainers.
* `PostgresIntegrationTests` (2 tests) started `postgres:18.4` through Spring Boot's Docker Compose support.

---

## 3. Changes

Every candidate was applied as one commit on the local branch `slim` and evaluated the same way:
1. `./mvnw -B clean verify`: all 81 tests, including the MySQL/Postgres containers.
2. Artifact, library and `dependency:tree` measurement.
3. The full behaviour checklist on all three database profiles (H2, MySQL, Postgres).

**Keep rule.** A candidate was kept only if:
* verify passed;
* the same tests ran (per-class counts identical, none newly skipped); and
* every checklist item matched baseline on every profile.

Otherwise it was reverted. Feature-removing candidates (F01–F03) used a declared, narrower rule, decided by hand: the removed database's own tests and checklist profile were expected to go, and everything else had to be identical.

### 3.0 Candidate counts

| | count | how it is made up |
|---|---|---|
| **Unique candidate reductions** | **70** | group A 23 (direct deps flagged by the tools), B 26 (transitive deps flagged by DepClean), C 18 (not suggested by the tools), F 3 (feature removals) |
| **Evaluations run** (`changes/` directories) | **80** | 70 first runs + 5 re-runs after the disk incident (A22, C07, C08, C12, C13) + 1 C18 re-run after the MySQL-readiness fix + 1 C18 applied to the full branch + 1 superseded variant F01a + 1 revert evaluation R01 + 1 evaluation of the assembled free + conditional state. (An earlier chat message said "82"; that was a miscount.) |
| **Kept** | **22** | free 9 (1 runtime + 8 test-scope) · conditional 8 · feature-removing 5. See 3.1 |
| **No-ops** | **4** | B23, B25, B26, C10: already gone with their parent; 0 bytes |
| **Rejected** | **44** | 70 − 22 − 4. Includes B03 (kept first, rejected later) |
| **Breaking removals** | **45** | the 44 rejected + F01a (a first, too broad version of F01 that broke test compilation). All broke something: 12 at compile, 21 in the test suite, **11 only in the checklist, 1 in neither** |
| Files in `rejected/` | 51 | the 45 breaking changes + 5 re-run diffs + the first C18 run (a harness failure, superseded by its re-run) |

### 3.1 Kept changes

* **Library bytes** = the exact size of the JAR(s) the change removes from `BOOT-INF/lib`, from the Maven repository files. They are stored uncompressed in the fat JAR. These are the numbers used for every subtotal.
* **Artifact Δ** = measured change of the whole executable JAR versus the previous kept state on the `slim` branch. It includes zip-entry overhead and build metadata (`git.properties`, embedded POM, SBOM), so changes with 0 library bytes still move by a few bytes.

| change | what | library bytes | artifact Δ | class | tests | checklist |
|---|---|---|---|---|---|---|
| A16 | remove `spring-boot-starter-restclient` (test scope) | 0 | +20 | free (test scope) | 81 pass | identical |
| A18 | remove `spring-boot-starter-thymeleaf-test` | 0 | −4 | free (test scope) | 81 pass | identical |
| A19 | remove `spring-boot-starter-validation-test` | 0 | −6 | free (test scope) | 81 pass | identical |
| A21 | remove `spring-boot-starter-actuator-test` | 0 | −7 | free (test scope) | 81 pass | identical |
| A23 | remove `spring-boot-starter-cache-test` | 0 | −7 | free (test scope) | 81 pass | identical |
| B21 | exclude `commons-codec` (test) | 0 | +12 | free (test scope) | 81 pass | identical |
| B22 | exclude `awaitility` (test) | 0 | +16 | free (test scope) | 81 pass | identical |
| B24 | exclude `spring-boot-restclient-test` (test) | 0 | +26 | free (test scope) | 81 pass | identical |
| C11 | exclude `error_prone_annotations` | 20,255 | −21,012 | **free** | 81 pass | identical |
| B01 | exclude `snakeyaml` | 340,068 | −340,770 | **conditional** | 81 pass | identical |
| B02 | exclude `HdrHistogram` | 177,206 | −178,148 | **conditional** | 81 pass | identical |
| B04 | exclude `micrometer-jakarta9` | 54,767 | −55,377 | **conditional** | 81 pass | identical |
| C01 | exclude `aspectjweaver` | 2,190,661 | −2,191,452 | **conditional** | 81 pass | identical |
| C02 | exclude `spring-aspects` | 50,015 | −50,622 | **conditional** | 81 pass | identical |
| C03 | exclude `tomcat-embed-websocket` | 286,650 | −287,293 | **conditional** | 81 pass | identical |
| C09 | exclude `log4j-to-slf4j` (drops `log4j-api` with it) | 375,299 (24,172 + 351,127) | −376,954 | **conditional** (reclassified, see 3.2) | 81 pass | identical |
| C18 | exclude `jakarta.inject-api` (re-run; see What went wrong #9) | 10,681 | −11,384 (free branch) / −11,411 (full branch) | **conditional** | 81 pass | identical |
| A01 | remove `spring-boot-devtools` (optional) | 0 (never packaged) | −672 | **feature-removing**: development-time restart/live-reload | 81 pass | identical |
| C04 | `spring-boot-maven-plugin` `includeTools=false` (drops `spring-boot-jarmode-tools`) | 53,966 | −54,131 | **feature-removing**: `java -Djarmode=tools -jar … extract / list-layers` (layered extraction, CDS training) no longer available. The buildpack image still builds | 81 pass | identical |
| F01 | drop MySQL: driver, `testcontainers-mysql`, MySQL test classes, `application-mysql.properties`, `db/mysql/` | 2,607,237 | −2,611,807 | **feature-removing** | 79 pass (−2 MySQL tests) | H2 + Postgres identical; `mysql` profile now **silently runs on in-memory H2** (only the external-DB row check differs) |
| F02 | drop Postgres: driver, `spring-boot-docker-compose`, Postgres test, `application-postgres.properties`, `db/postgres/` | 1,142,677 | −1,146,889 | **feature-removing** | 77 pass (−2 Postgres tests) | H2 identical; `postgres` profile also silently falls back to H2 |
| F03 | remove now-unused `testcontainers-junit-jupiter`, `spring-boot-testcontainers` (test) | 0 | −74 | feature-removing (consequence of F01/F02) | 77 pass | as F02 |
| *(R01)* | *revert of B03, see 3.3* | *(+7,041 restored)* | +7,087 | — | 77 pass | H2 identical incl. log routing |

**Subtotals (library bytes, exact):**

| class | changes | library bytes | % of baseline JAR | where it shows up measured |
|---|---|---|---|---|
| free | C11 (runtime) + 8 test-scope changes | 20,255 | 0.03 % | not built on its own (*calculated*) |
| conditional | B01 B02 B04 C01 C02 C03 C09 C18 | 3,485,347 | 5.29 % | free + conditional state: −3,505,602 library bytes, −3,513,027 artifact bytes (measured) |
| feature-removing | A01 C04 F01 F02 F03 | 3,803,880 | 5.78 % | full state minus free + conditional: −3,803,880 library bytes, −3,813,489 artifact bytes (measured) |
| **all kept** | 22 | 7,309,482 | 11.10 % | full state: −7,326,516 artifact bytes (−11.13 %, measured) |

The test-scope changes shrink the test classpath (resolved test dependencies 65 → 54) and save 0 runtime bytes.

### 3.2 The conditional class: what each kept runtime exclusion gives up

PetClinic does not use any of these capabilities, and that is why the tests and the 58-item checklist stayed identical. Another app could rely on them.
* **Static evidence:** a scan of the class files of the 83 remaining libraries for references to the removed packages. It shows which libraries would use the removed JAR if the feature were switched on.
* **Not measured:** the effect in another app. That is reasoning, not a test.

| exclusion | capability lost | apps affected | static evidence |
|---|---|---|---|
| **snakeyaml** | YAML configuration: `application.yml`, `application-<profile>.yml`, YAML via `spring.config.import` | any app configured in YAML (very common), or one that adds a YAML file later | Spring Boot's YAML property-source loader and Spring's `YamlProcessor` reference snakeyaml (spring-boot, spring-beans) |
| **HdrHistogram** | Micrometer client-side percentiles and percentile histograms (`management.metrics.distribution.percentiles*`, SLO buckets) | apps that publish latency percentiles | micrometer-core references `org.HdrHistogram` |
| **micrometer-jakarta9** | Micrometer instrumentation of Jakarta JMS and Jakarta Mail (observations/metrics) | apps using JMS or mail with observability | no remaining library references it, because PetClinic has no JMS or mail |
| **aspectjweaver** | AspectJ annotation-style AOP: `@Aspect` beans, AspectJ pointcut expressions, and Micrometer's `@Timed`, `@Counted` and `@Observed` aspects | apps with their own aspects or annotation-driven metrics/tracing. Boot's auto-configuration for those aspects is conditional on AspectJ being present, so the annotation-driven metrics could **silently stop being recorded** rather than fail | spring-aop (33 classes), micrometer-core/observation/commons, spring-boot-autoconfigure, spring-boot-micrometer-metrics/observation reference `org.aspectj` |
| **spring-aspects** | AspectJ-mode `@Transactional`, `@Cacheable`, `@Async` (`mode = ASPECTJ`), `@Configurable` injection into non-Spring objects | apps using AspectJ weaving | spring-data-jpa references Spring's AspectJ support |
| **tomcat-embed-websocket** | WebSocket server support in embedded Tomcat (Jakarta WebSocket endpoints; the base for Spring WebSocket/STOMP) | any app that adds WebSocket endpoints | no remaining library references `jakarta.websocket`, because PetClinic has no WebSocket code |
| **log4j-to-slf4j (+ log4j-api)** | routing of Log4j 2 API log calls into SLF4J/Logback | apps containing any library that logs through the Log4j 2 API. **The same failure family as jul-to-slf4j (B03), which was rejected for breaking log routing.** | spring-boot (22 classes), commons-logging 1.3.6, micrometer-core, jboss-logging and spring-boot-micrometer-metrics contain code referencing the Log4j API |
| **jakarta.inject-api** | JSR-330 support: `@Inject`, `@Named`, `Provider<T>` on Spring beans | apps or libraries that use JSR-330 annotations instead of `@Autowired` | spring-beans, spring-data-commons and hibernate-core reference `jakarta.inject` |

**Why log4j-to-slf4j moved from "free" to "conditional".**
* It does for the Log4j 2 API what jul-to-slf4j does for `java.util.logging`.
* The two differ here only because PetClinic happens to have no library that logs through the Log4j API, while Tomcat does log through JUL. B03's break was visible and C09's is not.
* Evidence that C09 is safe for *this* app is weaker than it looks: the log-routing checklist item counts only JUL-format lines; it does not look for Log4j-routed output. The safety rests on all 81 tests and every checklist item being identical, and on no `NoClassDefFoundError` appearing.
* Commons-logging 1.3.6, which Spring 7 logs through, contains code referencing the Log4j API. Reading its discovery logic (static, not tested), it prefers the Log4j API when present. So in an app where some other library brings `log4j-api` back without this bridge, Spring's own log output could bypass Logback.
* Treat it as conditional, like jul-to-slf4j, not as free.

**Why error_prone_annotations stays "free".** It contains only annotations, referenced by caffeine (19 classes). The JVM ignores annotations whose classes are missing, and nothing in the application reads them reflectively. No app capability depends on it at runtime.

### 3.3 Rejected changes

The 44 rejected candidates plus F01a = 45 breaking removals (see 3.0). Every candidate ran the **full test suite**, so for checklist-caught breaks the suite really did run, and passed.

**Removals that only the behaviour checklist caught (full test suite passed, 81/81):**

| change | what broke (checklist, all 3 profiles) |
|---|---|
| A02 remove `spring-boot-starter-actuator` | all 19 actuator endpoints → 404 (41 item differences per profile) |
| A05 remove `spring-boot-starter-thymeleaf` | every HTML page → 404/400 (36 differences). The tests could not see it because `spring-boot-starter-thymeleaf-test` puts Thymeleaf on the *test* classpath |
| A09 remove `caffeine` | cache provider silently changed from Caffeine to `ConcurrentHashMap` (`/actuator/caches`). Caching itself still worked. Rejected by the rule; the practical difference is small because the Caffeine cache was itself unbounded here |
| A12 remove `webjars-locator-lite` | versionless webjar URLs (Bootstrap JS, Font Awesome CSS and font) → 404 |
| A13 remove Bootstrap webjar | `bootstrap.bundle.min.js` → 404 |
| A14 remove Font Awesome webjar | Font Awesome CSS and font → 404 |
| B06 exclude `spring-boot-actuator-autoconfigure` | all actuator endpoints → 404 |
| B07 exclude `spring-boot-micrometer-metrics` | `/actuator/metrics*` → 404 |
| B09 exclude `spring-boot-health` | `/actuator/health` → 404 |
| B18 exclude `spring-boot-data-commons` | one metric fewer in `/actuator/metrics` (67 → 66) |
| C07 exclude `jaxb-runtime` | **`GET /vets` with `Accept: application/xml` → HTTP 500**; JSON and HTML unaffected. The same failure mode as the XML break in the earlier run. Re-run with plenty of disk: identical |

**Caught by neither tests nor the original checklist:**
* B03 exclude `jul-to-slf4j` (−7,041 B). Tomcat/Catalina logs bypass Logback: they print in the JDK's two-line format and ignore `logging.level.*`.
* It was found by reading app logs while classifying the kept changes. The checklist then got a **log-routing** item (58 items).
* B03 was reverted by R01 and is counted as rejected.

**Caught by the build or the test suite:**

| change | detection |
|---|---|
| A03 starter-cache, A04 starter-data-jpa, A06 starter-validation, A07 starter-webmvc | main compile error |
| A15 starter-data-jpa-test, A17 starter-restclient-test, A20 starter-webmvc-test | test compile error |
| A08 h2 | 16 test errors (no default DataSource) |
| A10 mysql-connector-j | `MySqlIntegrationTests` error (Testcontainers needs the driver: `NoDriverFoundException`) |
| A11 postgresql | `PostgresIntegrationTests`, 2 errors |
| A22 spring-boot-docker-compose (test) | `PostgresIntegrationTests`, 2 errors (no database started). Re-run: identical |
| B05 spring-boot-actuator | 10 errors (`AuditEventsEndpoint` class missing) |
| B08 spring-boot-micrometer-observation | 10 errors |
| B10 spring-boot-web-server, B11 spring-boot-tomcat | 10 errors each (no embedded server) |
| B12 spring-boot-http-converter, B13 spring-boot-servlet | 51 errors each |
| B14 spring-boot-thymeleaf, B15 thymeleaf-spring6 | 4 errors + 2 failures (views unresolved) |
| B16 attoparser, B17 unbescape | 32 errors + 2 failures (`NoClassDefFoundError`) |
| B19 spring-boot-validation, B20 spring-boot-data-jpa | main compile error (exclusion removes Hibernate Validator / Hibernate subtree) |
| C05 cache-api, C06 jakarta.xml.bind-api | main compile error |
| C08 byte-buddy | 70 errors (Mockito and Hibernate proxies) |
| C12 jspecify | 63 errors (`NoClassDefFoundError` at runtime) |
| C13 antlr4-runtime | 20 errors (Hibernate HQL parser) |
| C14 HikariCP | 4 errors |
| C15 tomcat-embed-el | 22 errors (Bean Validation message interpolation) |
| C16 jboss-logging | 65 errors |
| C17 hibernate-models | 20 errors |
| F01a first "drop MySQL" attempt | test compile error: it also removed `testcontainers-junit-jupiter`, which `PostgresIntegrationTests` uses. Redone as F01 |

**Re-runs:** A22, C07, C08, C12 and C13 were re-run after the disk incident: identical verdicts and error counts. C18 was re-run after the MySQL readiness fix: the verdict **changed** from reject to keep. See What went wrong #1 and #9.

---

## 4. What the analyzers flagged

### 4.1 `dependency:analyze`: 23 of 28 declared dependencies "unused declared"

Measured = removed and observed. Static = verdict from reading code or config.

| dependency (scope) | verdict | why the tool could not see the usage | evidence |
|---|---|---|---|
| spring-boot-starter-actuator | false positive | POM-only starter; endpoints come from auto-configuration | measured A02 (checklist only) |
| spring-boot-starter-cache | false positive | POM-only starter; code uses classes it brings transitively (`JCacheManagerCustomizer` in spring-boot-cache) | measured A03 (compile) |
| spring-boot-starter-data-jpa | false positive | POM-only starter (JPA API, Hibernate, Spring Data via transitive deps) | measured A04 (compile) |
| spring-boot-starter-thymeleaf | false positive | POM-only starter; templates resolved through auto-configuration | measured A05 (checklist only) |
| spring-boot-starter-validation | false positive | POM-only starter | measured A06 (compile) |
| spring-boot-starter-webmvc | false positive | POM-only starter | measured A07 (compile) |
| h2 (runtime) | false positive | runtime-only JDBC driver, chosen by auto-configuration | measured A08 (tests) |
| caffeine (runtime) | false positive | auto-configuration picks the cache provider by classpath presence | measured A09 (checklist only) |
| mysql-connector-j (runtime) | false positive (removable only as a feature removal, F01) | runtime-only driver, config-driven (`mysql` profile) | measured A10 (tests), F01 |
| postgresql (runtime) | false positive (feature removal F02) | runtime-only driver, config-driven | measured A11 (tests), F02 |
| webjars-locator-lite (runtime) | false positive | resolves versionless webjar URLs; auto-configured | measured A12 (checklist only) |
| bootstrap webjar (runtime) | false positive | static web assets | measured A13 (checklist only) |
| font-awesome webjar (runtime) | false positive | static web assets | measured A14 (checklist only) |
| spring-boot-devtools (optional) | truly unused at runtime; dev-time tool, not packaged | n/a | measured A01 (kept, feature-removing, 0 runtime bytes) |
| spring-boot-starter-data-jpa-test (test) | false positive | POM-only test starter; tests use `@DataJpaTest` from its transitive module | measured A15 (test compile) |
| spring-boot-starter-restclient (test) | **truly unused** | — | measured A16 (kept) |
| spring-boot-starter-restclient-test (test) | false positive | POM-only; tests use `RestTemplateBuilder`/`TestRestTemplate` from its transitive modules | measured A17 (test compile) |
| spring-boot-starter-thymeleaf-test (test) | **truly unused** | — | measured A18 (kept) |
| spring-boot-starter-validation-test (test) | **truly unused** | — | measured A19 (kept) |
| spring-boot-starter-webmvc-test (test) | false positive | POM-only; tests use `@WebMvcTest` | measured A20 (test compile) |
| spring-boot-starter-actuator-test (test) | **truly unused** | — | measured A21 (kept) |
| spring-boot-docker-compose (test) | false positive | config-driven (`spring.docker.compose.*` in the Postgres test); no code reference | measured A22 (tests) |
| spring-boot-starter-cache-test (test) | **truly unused** | — | measured A23 (kept) |

**Result: 23 flagged → 17 false positives, 6 removable (truly unused, 0 runtime bytes): 5 test-scope starters classed *free* and devtools classed *feature-removing* (development-time restart/live-reload; see 3.1).**
* The 6 removable ones are 5 test-scope starters and the optional devtools. **None of the 6 is in the JAR**, so removing them saves 0 runtime bytes.
* All 23 verdicts are measured.
* This differs from the earlier Mac run, where all 23 were judged false positives. Here the 6 removals were measured, then re-measured as part of the free + conditional and full states, and independently reproduced by the verification subagent (both variants 81/81 or 77/77 tests).
* The earlier run's verdict method is not known to this run, so the two cannot be reconciled further.

The 5 declared dependencies **not** flagged (cache-api, jakarta.xml.bind-api and the 3 Testcontainers/test-support deps) are all used. `cache-api` and `jakarta.xml.bind-api` removal was measured as compile errors (C05, C06).

### 4.2 DepClean 2.2.0: 18 direct + 37 transitive "potentially unused"

It ran without failing, but with a partial-analysis error: `[ERROR] ZIP bomb detected: too many entries in archive (10000)` / `Problem decompressing jar file: …/testcontainers-2.0.5.jar`. That JAR was not fully analysed. Output: `analysis/depclean.log`, `analysis/depclean-results.json.gz`.

**Direct (18).** All 18 are also in `dependency:analyze`'s list, with the verdicts from 4.1: **6 removable** (devtools + the 5 test starters), **12 false positives**. Unlike `dependency:analyze`, DepClean counted h2, mysql, postgresql, caffeine and webjars-locator-lite as used. It got those right.

**Transitive (37):**

| group | members | verdict | evidence |
|---|---|---|---|
| POM-only starters (11) | spring-boot-starter, -starter-jdbc, -starter-tomcat, -starter-tomcat-runtime, -starter-logging, -starter-jackson, -starter-micrometer-metrics; test: -starter-test, -starter-jdbc-test, -starter-micrometer-metrics-test, -starter-jackson-test | **not actionable**: each JAR holds only MANIFEST/LICENSE/NOTICE, and Spring Boot 4.1's repackager already leaves starter JARs out of the fat JAR (13 starter JARs resolved, 0 packaged). Excluding one would only drop its transitive deps | static (JAR listing in the Maven repo; fat-JAR listing), same mechanism as the measured direct starters A02–A07 |
| Spring Boot auto-configuration modules (13) | spring-boot-actuator, -actuator-autoconfigure, -micrometer-metrics, -micrometer-observation, -health, -web-server, -tomcat, -http-converter, -servlet, -thymeleaf, -data-commons, -validation, -data-jpa | **false positive**: loaded via `META-INF/spring/…AutoConfiguration.imports` or `spring.factories` | all measured B05–B20: 4 checklist only (B06, B07, B09, B18), 9 tests/compile |
| Thymeleaf engine (3) | thymeleaf-spring6, attoparser, unbescape | false positive: used by the template engine via reflection/auto-config | measured B15–B17 (tests) |
| logging bridge (1) | jul-to-slf4j | **false positive**: installed reflectively by Boot's logging system | measured B03 (caught by neither tests nor original checklist; reverted) |
| unused by this app (3 runtime) | snakeyaml, HdrHistogram, micrometer-jakarta9 | **conditional**: unused by PetClinic, but each removes an optional capability (YAML config, percentiles, JMS/Mail metrics; see 3.2) | measured B01, B02, B04 (kept; 572,041 library bytes) |
| truly unused (test) (6) | commons-codec, awaitility, spring-boot-restclient-test; micrometer-observation-test, spring-boot-micrometer-metrics-test, spring-boot-cache-test | truly unused | measured B21, B22, B24 (kept); the last three were removed together with their parent starter (A21/A23) and their own runs were no-ops |

11 + 13 + 3 + 1 + 3 + 6 = 37.

**DepClean totals.**
* 55 flagged: 12 truly unused (6 direct, 6 transitive), of which 11 are test scope and classed *free* and 1 is devtools, classed *feature-removing*; 3 conditional (transitive runtime); 29 false positives (12 direct, 17 transitive); 11 not actionable (POM-only).
* Runtime library bytes saved by acting on DepClean's list: **572,041 B**, all conditional. That is 16.32 % of the free + conditional library saving. **0 B** of it is free.

### 4.3 Savings the tools did not suggest (group C, from reading the tree and the JAR)

* **Kept:** 2,933,561 library bytes in total.
  * Conditional: aspectjweaver 2,190,661; log4j-to-slf4j + log4j-api 375,299; tomcat-embed-websocket 286,650; spring-aspects 50,015; jakarta.inject-api 10,681.
  * Free: error_prone_annotations 20,255.
* **Kept, feature-removing:** jarmode tools, 53,966.
* **Rejected:** cache-api, jakarta.xml.bind-api, jaxb-runtime, byte-buddy, jspecify, antlr4-runtime, HikariCP, tomcat-embed-el, jboss-logging, hibernate-models (see 3.3).

**Who found the free + conditional library bytes (3,505,602 B):**

| found by | library bytes | share |
|---|---|---|
| not suggested by either tool (group C) | 2,933,561 | 83.68 % |
| DepClean's transitive list (snakeyaml, HdrHistogram, micrometer-jakarta9) | 572,041 | 16.32 % |
| `dependency:analyze` | 0 | 0 % |

*Correction note.* An earlier version of this section gave the group-C total as 2,950,725 B. The six items it listed, taken as artifact deltas, sum to 2,938,717 B, so 2,950,725 was an arithmetic error. Artifact deltas also carry tens to hundreds of bytes of metadata noise, so the totals and the 83.68 % / 16.32 % split now use exact library bytes. They add up to the measured library-byte change of the free + conditional state (3,505,602 B).

**Observation (static, not changed).**
* `CacheConfiguration` registers a `JCacheManagerCustomizer`. But no JCache provider is on the classpath: only Caffeine core, not `caffeine-jcache`. So Spring Boot uses its native Caffeine cache manager.
* The JCache customizer and the `cache-api` dependency therefore do nothing at runtime. JCache statistics are never enabled and no `cache.*` metrics exist (checklist: `metrics` shows `cache.*=[]`).
* Removing `cache-api` needs a code change, so it was not pursued.

---

## 5. Everything that broke and how it was detected

45 breaking removals (the 44 rejected candidates + F01a; see 3.0):

| detected by | count | candidates |
|---|---|---|
| main or test compile | 12 | A03 A04 A06 A07 A15 A17 A20 B19 B20 C05 C06 F01a |
| test suite (runtime) | 21 | A08 A10 A11 A22 B05 B08 B10 B11 B12 B13 B14 B15 B16 B17 C08 C12 C13 C14 C15 C16 C17 |
| **behaviour checklist only (tests passed)** | **11** | A02 A05 A09 A12 A13 A14 B06 B07 B09 B18 C07 |
| **neither (found by log inspection)** | **1** | B03 |

Not counted: the first C18 run, whose failure came from the harness, not the change (What went wrong #9).

**The test suite missed 12 of 45 breaking removals (27 %).**
* They include both failure modes from the earlier run: an XML endpoint broken (C07, jaxb-runtime) and a silent caching change (A09, Caffeine → ConcurrentHashMap).
* The suite *did* run in full on each of them: the pipeline always runs `clean verify` before the checklist.
* If you look only at removals that got past compilation (33), the suite missed 12 of 33.

**One more hazard, inside a kept feature-removing change.**
* After F01/F02, starting the app with `spring.profiles.active=mysql` (or `postgres`) does not fail. The profile's properties file is gone, so the app silently runs on an in-memory H2 database.
* Every page, write and actuator endpoint looks normal. Only the checklist's external-database row check showed it.
* Anyone dropping a database this way should also make the old profile fail loudly.

---

## 6. Independent verification (Step 5)

A separate subagent was given only the pinned commit, the two kept-changes diffs and the measurement commands. It was not shown any numbers and was told not to read `results/` or `work/`. It ran after my own builds had finished. It cloned fresh from GitHub into `/tmp/mse-cache/verify/`, applied each diff with `git apply`, and ran `./mvnw -B clean verify` for baseline, free + conditional and full, one at a time. Output: `verification/`.

| | my measurement | verifier | match |
|---|---|---|---|
| baseline artifact bytes | 65,831,325 | 65,831,325 | exact, same SHA-256 `c06eabde…` |
| free + conditional artifact bytes | 62,318,298 | 62,318,329 | +31 B: `git.properties` only |
| full artifact bytes | 58,504,809 | 58,504,865 | +56 B: `git.properties` only |
| library count (baseline / free+cond / full) | 93 / 83 / 80 | 93 / 83 / 80 | exact |
| resolved deps (baseline / free+cond / full) | 171 / 150 / 131 | 171 / 150 / 131 | exact |
| tests run / failed / errors / skipped | 81/0/0/0 · 81/0/0/0 · 77/0/0/0 | 81/0/0/0 · 81/0/0/0 · 77/0/0/0 | exact; per-class counts identical |

**The size mismatch was investigated.** Both JARs of each variant were unpacked and compared file by file. The **only** differing file is `BOOT-INF/classes/git.properties`: branch name (`slim`/`slim-free` vs the detached commit), build user, commit message and id. Every class, library and resource is identical. The verifier also found Docker had 6 `pack-cache-*` buildpack volumes from my image builds and pruned them (1.1 GB), as instructed. That does not affect any number.

**An earlier verification, before C18 was added, also matched exactly** (baseline identical SHA; free 62,329,681 vs 62,329,682; full 58,516,229 vs 58,516,220; counts identical). It is kept in `verification-superseded-pre-C18/`.

---

## 7. What went wrong during the run

Full details in `INCIDENTS.md`. In short:
1. **Docker volume leak filled /workspaces** (free space fell to 1.68 GB). The checklist runner removed DB containers without `-v`; 130 orphaned volumes (13.05 GB). Cleaned up and the runner fixed; a ≥ 5 GB free-space guard was added. The candidates that ran with < 3 GB free (estimated C05–C13; free space was not logged per candidate before the fix) were checked: no disk-related errors in any log. The 5 rejected candidates whose failure could conceivably be environmental (A22, C07, C08, C12, C13) were re-run: no verdict changed.
2. I killed the wrong process during a status check (the batch's parent shell). The batch survived; no results were affected.
3. Two wait loops matched their own command line and never ended. They were killed; no effect on measurements.
4. A running script was edited mid-batch; the bytes were restored within seconds. Verified: one commit and one result per candidate.
5. The checklist's readiness probe depended on actuator, so A02's first checklist reported "never started". It was re-run with a `/` probe (41 real differences per profile). Verdict unchanged.
6. Re-runs after the disk incident: all identical.
7. Four candidates were no-ops logged as "kept" (B23, B25, B26, C10). They are marked NO-OP, contribute 0 bytes, and the script now detects no-ops.
8. **B03 (jul-to-slf4j) was wrongly kept.** The checklist did not look at logs. The checklist was extended with a log-routing item and B03 reverted (R01).
9. **MySQL readiness race** made C18 fail on the `mysql` profile only. The readiness check was fixed to use TCP. The C18 re-run passed and was kept. The after-measurements and verification were redone with C18 included; superseded copies are in `after-superseded-pre-C18/` and `verification-superseded-pre-C18/`.

---

## 8. Reproduce

```bash
source results/scripts/env.sh          # caches on /tmp, SDKMAN; then:
use_jdk 17
git clone https://github.com/spring-projects/spring-petclinic.git work/petclinic
cd work/petclinic && git checkout 500158f732419217507c7656904b8e6aa1bcc0d6
./mvnw -version                                       # Maven 3.9.16, Java 17.0.20.1

# Step 1 baseline
./mvnw -B clean verify                                # tests: target/surefire-reports
python3 ../../results/scripts/measure.py tests target/surefire-reports target/failsafe-reports
python3 ../../results/scripts/measure.py artifact target/spring-petclinic-4.0.0-SNAPSHOT.jar
./mvnw -B -q dependency:tree -DoutputFile=tree.txt && python3 ../../results/scripts/measure.py tree tree.txt
./mvnw -B -q help:effective-pom -Doutput=effective-pom.xml && python3 ../../results/scripts/measure.py declared effective-pom.xml
../../results/scripts/startup_time.sh 10 startup.tsv http://localhost:18080/actuator/health -- java -jar target/spring-petclinic-4.0.0-SNAPSHOT.jar --server.port=18080
../../results/scripts/build_time.sh 5 build.tsv buildlog -- ./mvnw -B clean package -DskipTests
mkdir /tmp/scan && cp target/*.jar /tmp/scan && trivy rootfs --scanners vuln --format json -o trivy.json /tmp/scan
./mvnw -B spring-boot:build-image -DskipTests -Dspring-boot.build-image.builder=paketobuildpacks/builder-noble-java-tiny@sha256:b95da27fce97b58037f0c11ae934760c50730da4c9a24976205b53638592eba9
../../results/scripts/petclinic_run_checklist.sh target/spring-petclinic-4.0.0-SNAPSHOT.jar checklist/   # H2, MySQL, Postgres

# Step 2
./mvnw -B dependency:analyze
./mvnw -B se.kth.castor:depclean-maven-plugin:2.2.0:depclean -DcreateResultJson=true

# Step 3: one candidate (example), evaluated against the baseline
../../results/scripts/run_candidate.sh petclinic B01-snakeyaml "exclude snakeyaml" "../../results/scripts/exclude_everywhere.sh org.yaml snakeyaml"

# Step 4: apply a kept-changes diff to a clean checkout and repeat Step 1, or:
git apply ../../results/petclinic/kept-changes-free-only.diff   # or kept-changes-full.diff
../../results/scripts/petclinic_measure_state.sh <name> <git-ref>
```

Batch scripts used: `candidates-A.sh`, `candidates-B.sh`, `candidates-C.sh`. Per-candidate evidence is in `changes/<id>/`: verify log, tests.json, artifact.json, tree, checklist JSON + app logs, summary.json.

## 9. Scope and limits

**What this is.**
* One project: Spring PetClinic at one commit.
* On one Spring Boot version (4.1.0, Spring Framework 7.0.8), one JDK (17.0.20, Microsoft build), one Maven version (3.9.16).
* On one machine: a 4-vCPU, 16 GB GitHub Codespace, shared cloud hardware.
* With one set of analyzer versions: maven-dependency-plugin 3.10.0, DepClean 2.2.0.
* The planned comparison projects (JHipster sample app, Dependency-Track) were **not run**. Nothing here says whether the patterns hold outside this app, outside Spring Boot, or for WAR packaging.

**What the results show.**
* For this app, at this commit, the exact bytes each kept change removes and whether it changed the 81 tests or the 58-item behaviour checklist on H2, MySQL and Postgres. All of it was measured and independently reproduced: sizes to within `git.properties` metadata, counts exactly.
* How the two analyzers' flags turned out when acted on, one dependency at a time, with the reason each was wrong where it was.
* That this test suite let 12 of 45 breaking removals through, and which kinds: actuator endpoints, templates, static assets, content negotiation, cache provider, logging.
* That startup and clean-build time differences were within the noise of this machine. The baseline's own build median moved by 1.6 s across the session.

**What the results do not show.**
* **The conditional changes are not proven safe in general.** "Conditional" means safe for PetClinic as exercised. Section 3.2's "apps affected" column is reasoning backed by a static scan, not a test.
* **The checklist is not exhaustive.** It found one gap during the run (log routing; B03 got through it) and may have others: Log4j-routed output, JMX, non-HTTP behaviour, every page × locale, load and concurrency. A "pass" means identical on 58 items × 3 profiles, nothing more.
* **Ordering effects.** Candidates were applied cumulatively, and exclusion placement depends on declaration order (Maven resolves `spring-boot-starter` once via its first path). A different order could need different exclusions; the final states were checked as a whole.
* **No timing claim at finer resolution.** Changes in startup or build time below roughly 1 s would not be detectable here.
* **Vulnerability counts** are for one Trivy DB snapshot (2026-10-03) and only for what Trivy can identify inside the JAR. Removing a vulnerable JAR is not the same as fixing the vulnerability for apps that need that library.
* **The earlier Mac run's figures** (9.5 % reduction; "23 of 28 flagged, all false positives") were not re-run here with that run's method. This run found 6 of the 23 removable (all test-scope or devtools, 0 runtime bytes). The two runs cannot be reconciled further without knowing how the earlier verdicts were made.

---

## 10. Files

* **Numbers:** `metrics.json` holds all raw numbers, including the three-way classification, the subtotals and the candidate counts.
* **Records:**
  * `PROGRESS.md`: every candidate evaluation.
  * `INCIDENTS.md`: harness problems and how each was handled.
  * `CHECKLIST.md` + `baseline/checklist/`: the 58-item behaviour checklist on 3 profiles.
* **Diffs:**
  * `kept-changes-free-only.diff`: the free + conditional state; named before the conditional class existed.
  * `kept-changes-full.diff`.
  * `rejected/*.diff`.
  * `kept-changes-table.md`: per-commit artifact deltas.
* **Measurements:**
  * `baseline/` and `after/` (`after/free-only/` = free + conditional).
  * `after-superseded-pre-C18/`.
  * `analysis/`: `dependency:analyze` and DepClean output.
* **Per-candidate evidence:** `changes/<id>/`: verify log, tests.json, artifact.json, tree, checklist JSON + app logs, summary.json.
* **Verification:** `verification/` and `verification-superseded-pre-C18/`.
* **Other:**
  * `logs/` and the batch scripts `candidates-{A,B,C}.sh`.
  * Large logs are gzipped (`*.log.gz`). DepClean's 20 MB result JSON is `analysis/depclean-results.json.gz`.
  * Measurement scripts are in `../scripts/`.
