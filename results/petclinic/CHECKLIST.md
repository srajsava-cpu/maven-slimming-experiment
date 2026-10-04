# PetClinic behaviour checklist: baseline (commit 500158f), 58 items

Each item is run against every profile listed. Status, content type and signature must match baseline.

| # | id | what | request | h2 status | mysql status | postgres status | content type | baseline signature (h2) |
|---|---|---|---|---|---|---|---|---|
| 1 | home | Welcome page | `GET / Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Welcome; rows=0; Welcome=y,pets.png=y |
| 2 | home-de | i18n: German welcome | `GET /?lang=de Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | Willkommen=y |
| 3 | home-es | i18n: Spanish welcome | `GET /?lang=es Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | Bienvenido=y |
| 4 | find | Find owners form | `GET /owners/find Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Find Owners; rows=0 |
| 5 | list-all | Owner list page 1 (all owners) | `GET /owners?lastName= Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Owners; rows=5 |
| 6 | list-p2 | Owner list page 2 | `GET /owners?lastName=&page=2 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Owners; rows=5 |
| 7 | list-davis | Owner search with 2 matches | `GET /owners?lastName=Davis Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Owners; rows=2 |
| 8 | search-one | Owner search with 1 match redirects | `GET /owners?lastName=Franklin Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 302 | 302 | 302 |  | location=/owners/1 |
| 9 | search-none | Owner search with no match | `GET /owners?lastName=Nobody Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Find Owners; rows=0; has not been found=y |
| 10 | owner1 | Owner details | `GET /owners/1 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Owner Information; rows=0; George=y,Franklin=y,Leo=y |
| 11 | owner-missing | Unknown owner id | `GET /owners/9999 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 500 | 500 | 500 | text/html | title=PetClinic :: a Spring Framework demonstration |
| 12 | owner-edit-form | Edit owner form | `GET /owners/1/edit Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | George=y,Update Owner=y |
| 13 | pet-new-form | New pet form (pet types from DB) | `GET /owners/1/pets/new Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | hamster=y,lizard=y,snake=y |
| 14 | pet-edit-form | Edit pet form | `GET /owners/1/pets/1/edit Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | Leo=y,Update Pet=y |
| 15 | visit-form | New visit form | `GET /owners/1/pets/1/visits/new Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | Leo=y,Add Visit=y |
| 16 | vets-html | Vet list HTML page 1 | `GET /vets.html Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Veterinarians; rows=5 |
| 17 | vets-html-p2 | Vet list HTML page 2 | `GET /vets.html?page=2 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | title=PetClinic :: a Spring Framework demonstration; h2=Veterinarians; rows=1 |
| 18 | vets-json | Vets resource as JSON | `GET /vets Accept: application/json` | 200 | 200 | 200 | application/json | keys=['vetList']; vets=6; vet0keys=['firstName', 'id', 'lastName', 'new', 'nrOfSpecialties', 'specialties']; specialties=5 |
| 19 | vets-xml | Vets resource as XML | `GET /vets Accept: application/xml` | 200 | 200 | 200 | application/xml | root=vets; vetList=6; firstName=6 |
| 20 | vets-default | Vets resource, no Accept header preference | `GET /vets Accept: */*` | 200 | 200 | 200 | application/json | bytes=797 |
| 21 | oups | Deliberate exception page | `GET /oups Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 500 | 500 | 500 | text/html | Something happened=y |
| 22 | notfound | Unknown URL | `GET /does-not-exist Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 404 | 404 | 404 | text/html |  |
| 23 | css | Compiled stylesheet | `GET /resources/css/petclinic.css Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/css | bytes=278931 |
| 24 | img | Image | `GET /resources/images/pets.png Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | image/png | bytes=67721 |
| 25 | font | Web font | `GET /resources/fonts/montserrat-webfont.woff Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | font/woff | bytes=24240 |
| 26 | favicon | Favicon | `GET /resources/images/favicon.png Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | image/png | bytes=528 |
| 27 | webjar-bs | Bootstrap JS via webjars locator (versionless URL) | `GET /webjars/bootstrap/dist/js/bootstrap.bundle.min.js Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/javascript | bytes=80496 |
| 28 | webjar-fa | Font Awesome CSS via webjars locator | `GET /webjars/font-awesome/css/font-awesome.min.css Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/css | bytes=31000 |
| 29 | webjar-fa-font | Font Awesome font via webjars locator | `GET /webjars/font-awesome/fonts/fontawesome-webfont.woff2 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | font/woff2 | bytes=77160 |
| 30 | owner-create | Create owner (write) | `POST /owners/new Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 302 | 302 | 302 |  | location=/owners/11 |
| 31 | owner-created | Read back created owner | `GET /owners?lastName=Lovelace Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 302 | 302 | 302 |  | location=/owners/11 |
| 32 | owner-create-invalid | Create owner with validation errors | `POST /owners/new Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | must not be blank=y,Telephone must be a 10-digit number=y |
| 33 | owner-update | Update owner (write) | `POST /owners/1/edit Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 302 | 302 | 302 |  | location=/owners/1 |
| 34 | pet-create | Add pet (write) | `POST /owners/1/pets/new Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 302 | 302 | 302 |  | location=/owners/1 |
| 35 | visit-create | Add visit (write) | `POST /owners/1/pets/1/visits/new Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 302 | 302 | 302 |  | location=/owners/1 |
| 36 | owner1-after | Owner details after writes | `GET /owners/1 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | text/html | Rex=y,checkup=y |
| 37 | act-root | Actuator discovery | `GET /actuator Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json | _links=['beans', 'caches', 'caches-cache', 'conditions', 'configprops', 'configprops-prefix', 'env', 'env-toMatch', 'health', 'health-path', 'info', 'loggers', 'loggers-name', 'mappings', 'metrics', 'metrics-requiredMetricName', 'sbom', 'sbom-id', 'scheduledtasks', 'self', 'threaddump'] |
| 38 | health | Health | `GET /actuator/health Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json | status=UP; components=[] |
| 39 | health-db | Health: db component (404 = components not exposed) | `GET /actuator/health/db Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 404 | 404 | 404 |  |  |
| 40 | info | Info (build + git) | `GET /actuator/info Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json | keys=['build', 'git']; build.keys=['artifact', 'encoding', 'group', 'java', 'name', 'time', 'version'] |
| 41 | metrics | Metrics names | `GET /actuator/metrics Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json | count=67; cache.*=[] |
| 42 | metric-jvm | Metric jvm.memory.used | `GET /actuator/metrics/jvm.memory.used Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json | name=jvm.memory.used |
| 43 | caches | Cache managers and cache provider class | `GET /actuator/caches Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json | cacheManager:vets->com.github.benmanes.caffeine.cache.UnboundedLocalCache$UnboundedLocalManualCache |
| 44 | sbom | SBOM ids | `GET /actuator/sbom Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json | ids=['application'] |
| 45 | sbom-app | Application SBOM | `GET /actuator/sbom/application Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.cyclonedx+json | bomFormat=CycloneDX |
| 46 | prometheus | Prometheus scrape endpoint | `GET /actuator/prometheus Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 404 | 404 | 404 | text/html |  |
| 47 | act-beans | Actuator beans | `GET /actuator/beans Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json |  |
| 48 | act-conditions | Actuator conditions | `GET /actuator/conditions Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json |  |
| 49 | act-configprops | Actuator configprops | `GET /actuator/configprops Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json |  |
| 50 | act-env | Actuator env | `GET /actuator/env Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json |  |
| 51 | act-loggers | Actuator loggers | `GET /actuator/loggers Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json |  |
| 52 | act-mappings | Actuator mappings | `GET /actuator/mappings Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json |  |
| 53 | act-scheduledtasks | Actuator scheduledtasks | `GET /actuator/scheduledtasks Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json |  |
| 54 | act-threaddump | Actuator threaddump | `GET /actuator/threaddump Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 200 | 200 | 200 | application/vnd.spring-boot.actuator.v3+json |  |
| 55 | act-heapdump | Actuator heapdump | `GET /actuator/heapdump Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | 404 | 404 | 404 | text/html |  |
| 56 | cache-hit | Repeated GET /vets served from the 'vets' cache (cache interceptor trace log) | `GET /vets (json) repeated` | None | None | None |  | findAll() cache entries created=1; findAll() served from cache=yes |
| 57 | log-routing | All log output routed through Logback (no raw java.util.logging lines) | `app log` | None | None | None |  | jul_simpleformatter_lines=0 |
| 58 | db-row | Created owner row present in the external database | `SQL count` | None | None | None |  | rows=n/a (in-memory) — differs on mysql: `rows=1`, postgres: `rows=1` |

Notes:
- **How it runs.** Runner: `results/scripts/petclinic_run_checklist.sh <jar> <out>`. For each profile it starts fresh `mysql:9.7` / `postgres:18.4` containers, then starts the app with `--logging.level.org.springframework.cache=trace` (a runtime option; no project file is changed) so cache hits can be observed.
- **Item 58, log-routing,** was added during Step 3 after B03 (see INCIDENTS.md #8). The first 57-item baseline is kept in `baseline/checklist-v1/`. The 57 shared items were identical when the baseline was re-run.
- **db-row** checks that the write reached the external database, so it is "n/a" for in-memory H2.
