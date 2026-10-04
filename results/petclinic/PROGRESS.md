# petclinic — progress

Regenerated 2026-10-04 03:15 UTC from `changes/*/summary.json` (script: `results/scripts/progress_md.py`). Artifact delta is against the unmodified baseline JAR and is cumulative over the changes kept before it. 'checklist only' = full test suite passed, the behaviour checklist caught the break.

| candidate | change | result | tests (full verify) | checklist | artifact Δ bytes vs baseline | libs | caught by |
|---|---|---|---|---|---|---|---|
| A01-devtools | A01-devtools: remove spring-boot-devtools | ? | 81 run / 0F 0E 0S | pass | -672 | 93 |  |
| A02-starter-actuator | A02-starter-actuator: remove org.springframework.boot:spring-boot-starter-actuator | REJECTED | 81 run / 0F 0E 0S | FAIL | -2,085,034 | 85 | checklist only |
| A03-starter-cache | A03-starter-cache: remove org.springframework.boot:spring-boot-starter-cache | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| A04-starter-data-jpa | A04-starter-data-jpa: remove org.springframework.boot:spring-boot-starter-data-jpa | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| A05-starter-thymeleaf | A05-starter-thymeleaf: remove org.springframework.boot:spring-boot-starter-thymeleaf | REJECTED | 81 run / 0F 0E 0S | FAIL | -1,596,107 | 88 | checklist only |
| A06-starter-validation | A06-starter-validation: remove org.springframework.boot:spring-boot-starter-validation | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| A07-starter-webmvc | A07-starter-webmvc: remove org.springframework.boot:spring-boot-starter-webmvc | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| A08-h2 | A08-h2: remove com.h2database:h2 | REJECTED | 81 run / 0F 16E 0S (build failed) | skipped |  |  | tests/build |
| A09-caffeine | A09-caffeine: remove com.github.ben-manes.caffeine:caffeine | REJECTED | 81 run / 0F 0E 0S | FAIL | -1,051,583 | 91 | checklist only |
| A10-mysql-connector-j | A10-mysql-connector-j: remove com.mysql:mysql-connector-j | REJECTED | 80 run / 0F 1E 0S (build failed) | skipped |  |  | tests/build |
| A11-postgresql | A11-postgresql: remove org.postgresql:postgresql | REJECTED | 81 run / 0F 2E 0S (build failed) | skipped |  |  | tests/build |
| A12-webjars-locator-lite | A12-webjars-locator-lite: remove org.webjars:webjars-locator-lite | REJECTED | 81 run / 0F 0E 0S | FAIL | -10,062 | 92 | checklist only |
| A13-webjar-bootstrap | A13-webjar-bootstrap: remove org.webjars.npm:bootstrap | REJECTED | 81 run / 0F 0E 0S | FAIL | -1,842,583 | 92 | checklist only |
| A14-webjar-font-awesome | A14-webjar-font-awesome: remove org.webjars.npm:font-awesome | REJECTED | 81 run / 0F 0E 0S | FAIL | -682,724 | 92 | checklist only |
| A15-starter-data-jpa-test | A15-starter-data-jpa-test: remove org.springframework.boot:spring-boot-starter-data-jpa-test | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| A16-starter-restclient | A16-starter-restclient: remove org.springframework.boot:spring-boot-starter-restclient | KEPT | 81 run / 0F 0E 0S | pass | -652 | 93 |  |
| A17-starter-restclient-test | A17-starter-restclient-test: remove org.springframework.boot:spring-boot-starter-restclient-test | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| A18-starter-thymeleaf-test | A18-starter-thymeleaf-test: remove org.springframework.boot:spring-boot-starter-thymeleaf-test | KEPT | 81 run / 0F 0E 0S | pass | -656 | 93 |  |
| A19-starter-validation-test | A19-starter-validation-test: remove org.springframework.boot:spring-boot-starter-validation-test | KEPT | 81 run / 0F 0E 0S | pass | -662 | 93 |  |
| A20-starter-webmvc-test | A20-starter-webmvc-test: remove org.springframework.boot:spring-boot-starter-webmvc-test | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| A21-starter-actuator-test | A21-starter-actuator-test: remove org.springframework.boot:spring-boot-starter-actuator-test | KEPT | 81 run / 0F 0E 0S | pass | -669 | 93 |  |
| A22-docker-compose-rerun | A22-docker-compose-rerun: re-run after disk incident: remove spring-boot-docker-compose | REJECTED | 81 run / 0F 2E 0S (build failed) | skipped |  |  | tests/build |
| A22-docker-compose | A22-docker-compose: remove org.springframework.boot:spring-boot-docker-compose | REJECTED | 81 run / 0F 2E 0S (build failed) | skipped |  |  | tests/build |
| A23-starter-cache-test | A23-starter-cache-test: remove org.springframework.boot:spring-boot-starter-cache-test | KEPT | 81 run / 0F 0E 0S | pass | -676 | 93 |  |
| B01-snakeyaml | B01-snakeyaml: exclude org.yaml:snakeyaml everywhere | KEPT | 81 run / 0F 0E 0S | pass | -341,446 | 92 |  |
| B02-HdrHistogram | B02-HdrHistogram: exclude org.hdrhistogram:HdrHistogram everywhere | KEPT | 81 run / 0F 0E 0S | pass | -519,594 | 91 |  |
| B03-jul-to-slf4j | B03-jul-to-slf4j: exclude org.slf4j:jul-to-slf4j everywhere | REJECTED | 81 run / 0F 0E 0S | pass | -526,635 | 90 | checklist only |
| B04-micrometer-jakarta9 | B04-micrometer-jakarta9: exclude io.micrometer:micrometer-jakarta9 everywhere | KEPT | 81 run / 0F 0E 0S | pass | -582,012 | 89 |  |
| B05-boot-actuator | B05-boot-actuator: exclude org.springframework.boot:spring-boot-actuator everywhere | REJECTED | 81 run / 0F 10E 0S (build failed) | skipped |  |  | tests/build |
| B06-boot-actuator-autoconfigure | B06-boot-actuator-autoconfigure: exclude org.springframework.boot:spring-boot-actuator-autoconfigure everywhere | REJECTED | 81 run / 0F 0E 0S | FAIL | -1,081,572 | 87 | checklist only |
| B07-boot-micrometer-metrics | B07-boot-micrometer-metrics: exclude org.springframework.boot:spring-boot-micrometer-metrics everywhere | REJECTED | 81 run / 0F 0E 0S | FAIL | -1,776,300 | 86 | checklist only |
| B08-boot-micrometer-observation | B08-boot-micrometer-observation: exclude org.springframework.boot:spring-boot-micrometer-observation everywhere | REJECTED | 81 run / 0F 10E 0S (build failed) | skipped |  |  | tests/build |
| B09-boot-health | B09-boot-health: exclude org.springframework.boot:spring-boot-health everywhere | REJECTED | 81 run / 0F 0E 0S | FAIL | -737,884 | 88 | checklist only |
| B10-boot-web-server | B10-boot-web-server: exclude org.springframework.boot:spring-boot-web-server everywhere | REJECTED | 81 run / 0F 10E 0S (build failed) | skipped |  |  | tests/build |
| B11-boot-tomcat | B11-boot-tomcat: exclude org.springframework.boot:spring-boot-tomcat everywhere | REJECTED | 81 run / 0F 10E 0S (build failed) | skipped |  |  | tests/build |
| B12-boot-http-converter | B12-boot-http-converter: exclude org.springframework.boot:spring-boot-http-converter everywhere | REJECTED | 81 run / 0F 51E 0S (build failed) | skipped |  |  | tests/build |
| B13-boot-servlet | B13-boot-servlet: exclude org.springframework.boot:spring-boot-servlet everywhere | REJECTED | 81 run / 0F 51E 0S (build failed) | skipped |  |  | tests/build |
| B14-boot-thymeleaf | B14-boot-thymeleaf: exclude org.springframework.boot:spring-boot-thymeleaf everywhere | REJECTED | 81 run / 2F 4E 0S (build failed) | skipped |  |  | tests/build |
| B15-thymeleaf-spring6 | B15-thymeleaf-spring6: exclude org.thymeleaf:thymeleaf-spring6 everywhere | REJECTED | 81 run / 2F 4E 0S (build failed) | skipped |  |  | tests/build |
| B16-attoparser | B16-attoparser: exclude org.attoparser:attoparser everywhere | REJECTED | 81 run / 2F 32E 0S (build failed) | skipped |  |  | tests/build |
| B17-unbescape | B17-unbescape: exclude org.unbescape:unbescape everywhere | REJECTED | 81 run / 2F 32E 0S (build failed) | skipped |  |  | tests/build |
| B18-boot-data-commons | B18-boot-data-commons: exclude org.springframework.boot:spring-boot-data-commons everywhere | REJECTED | 81 run / 0F 0E 0S | FAIL | -612,951 | 88 | checklist only |
| B19-boot-validation | B19-boot-validation: exclude org.springframework.boot:spring-boot-validation everywhere | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| B20-boot-data-jpa | B20-boot-data-jpa: exclude org.springframework.boot:spring-boot-data-jpa everywhere | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| B21-commons-codec-test | B21-commons-codec-test: exclude commons-codec:commons-codec everywhere | KEPT | 81 run / 0F 0E 0S | pass | -582,000 | 89 |  |
| B22-awaitility-test | B22-awaitility-test: exclude org.awaitility:awaitility everywhere | KEPT | 81 run / 0F 0E 0S | pass | -581,984 | 89 |  |
| B23-micrometer-observation-test |  | NO-OP | | | | | NO-OP: already absent from the resolved graph; removed together with its parent spring-boot-starter-actuator-test by A21 |
| B24-boot-restclient-test | B24-boot-restclient-test: exclude org.springframework.boot:spring-boot-restclient-test everywhere | KEPT | 81 run / 0F 0E 0S | pass | -581,958 | 89 |  |
| B25-boot-micrometer-metrics-test |  | NO-OP | | | | | NO-OP: already absent; removed with its parent spring-boot-starter-actuator-test by A21 |
| B26-boot-cache-test |  | NO-OP | | | | | NO-OP: already absent; removed with its parent spring-boot-starter-cache-test by A23 |
| C01-aspectjweaver | C01-aspectjweaver: exclude org.aspectj:aspectjweaver everywhere | KEPT | 81 run / 0F 0E 0S | pass | -2,773,410 | 88 |  |
| C02-spring-aspects | C02-spring-aspects: exclude org.springframework:spring-aspects everywhere | KEPT | 81 run / 0F 0E 0S | pass | -2,824,032 | 87 |  |
| C03-tomcat-embed-websocket | C03-tomcat-embed-websocket: exclude org.apache.tomcat.embed:tomcat-embed-websocket everywhere | KEPT | 81 run / 0F 0E 0S | pass | -3,111,325 | 86 |  |
| C04-no-jarmode-tools | C04-no-jarmode-tools: spring-boot-maven-plugin: includeTools=false (drop spring-boot-jarmode-tools) | KEPT | 81 run / 0F 0E 0S | pass | -3,165,456 | 85 |  |
| C05-cache-api | C05-cache-api: remove javax.cache:cache-api | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| C06-jakarta-xml-bind-api | C06-jakarta-xml-bind-api: remove jakarta.xml.bind:jakarta.xml.bind-api | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| C07-jaxb-runtime-rerun | C07-jaxb-runtime-rerun: re-run after disk incident: exclude jaxb-runtime | REJECTED | 81 run / 0F 0E 0S | FAIL | -4,754,657 | 77 | checklist only |
| C07-jaxb-runtime | C07-jaxb-runtime: exclude org.glassfish.jaxb:jaxb-runtime everywhere | REJECTED | 81 run / 0F 0E 0S | FAIL | -4,356,703 | 80 | checklist only |
| C08-byte-buddy-rerun | C08-byte-buddy-rerun: re-run after disk incident: exclude byte-buddy | REJECTED | 81 run / 0F 70E 0S (build failed) | skipped |  |  | tests/build |
| C08-byte-buddy | C08-byte-buddy: exclude net.bytebuddy:byte-buddy everywhere | REJECTED | 81 run / 0F 70E 0S (build failed) | skipped |  |  | tests/build |
| C09-log4j-to-slf4j | C09-log4j-to-slf4j: exclude org.apache.logging.log4j:log4j-to-slf4j everywhere | KEPT | 81 run / 0F 0E 0S | pass | -3,542,410 | 83 |  |
| C10-log4j-api |  | NO-OP | | | | | NO-OP: already absent; log4j-api was only a dependency of log4j-to-slf4j, excluded by C09 |
| C11-error-prone-annotations | C11-error-prone-annotations: exclude com.google.errorprone:error_prone_annotations everywhere | KEPT | 81 run / 0F 0E 0S | pass | -3,563,422 | 82 |  |
| C12-jspecify-rerun | C12-jspecify-rerun: re-run after disk incident: exclude jspecify | REJECTED | 81 run / 0F 63E 0S (build failed) | skipped |  |  | tests/build |
| C12-jspecify | C12-jspecify: exclude org.jspecify:jspecify everywhere | REJECTED | 81 run / 0F 63E 0S (build failed) | skipped |  |  | tests/build |
| C13-antlr4-runtime-rerun | C13-antlr4-runtime-rerun: re-run after disk incident: exclude antlr4-runtime | REJECTED | 81 run / 0F 20E 0S (build failed) | skipped |  |  | tests/build |
| C13-antlr4-runtime | C13-antlr4-runtime: exclude org.antlr:antlr4-runtime everywhere | REJECTED | 81 run / 0F 20E 0S (build failed) | skipped |  |  | tests/build |
| C14-HikariCP | C14-HikariCP: exclude com.zaxxer:HikariCP everywhere | REJECTED | 81 run / 0F 4E 0S (build failed) | skipped |  |  | tests/build |
| C15-tomcat-embed-el | C15-tomcat-embed-el: exclude org.apache.tomcat.embed:tomcat-embed-el everywhere | REJECTED | 81 run / 0F 22E 0S (build failed) | skipped |  |  | tests/build |
| C16-jboss-logging | C16-jboss-logging: exclude org.jboss.logging:jboss-logging everywhere | REJECTED | 81 run / 0F 65E 0S (build failed) | skipped |  |  | tests/build |
| C17-hibernate-models | C17-hibernate-models: exclude org.hibernate.models:hibernate-models everywhere | REJECTED | 81 run / 0F 20E 0S (build failed) | skipped |  |  | tests/build |
| C18-jakarta-inject-api-on-full | C18-jakarta-inject-api-on-full: apply C18 (exclude jakarta.inject-api) to the full branch | KEPT | 77 run / 0F 0E 0S | FAIL | -7,326,516 | 80 |  |
| C18-jakarta-inject-api-rerun | C18-jakarta-inject-api-rerun: re-run after MySQL readiness fix, on free-only branch: exclude jakarta.inject-api | KEPT | 81 run / 0F 0E 0S | pass | -3,513,027 | 83 |  |
| C18-jakarta-inject-api | C18-jakarta-inject-api: exclude jakarta.inject:jakarta.inject-api everywhere | REJECTED | 81 run / 0F 0E 0S | FAIL | -3,574,792 | 81 | checklist only |
| F01-drop-mysql | F01-drop-mysql: feature-removing: drop MySQL support (driver, Testcontainers MySQL module + MySQL test classes, mysql profile + SQL) | KEPT | 79 run / 0F 0E 0S | FAIL | -6,175,229 | 81 |  |
| F01a-drop-mysql-too-broad | F01-drop-mysql: feature-removing: drop MySQL support (driver, Testcontainers MySQL tests, mysql profile + SQL) | REJECTED | 0 run / 0F 0E 0S (build failed) | skipped |  |  | tests/build |
| F02-drop-postgres | F02-drop-postgres: feature-removing: drop PostgreSQL support (driver, Postgres tests + Docker Compose test support, postgres profile + SQL) | KEPT | 77 run / 0F 0E 0S | FAIL | -7,322,118 | 80 |  |
| F03-drop-testcontainers | F03-drop-testcontainers: consequence of F01+F02: remove now-unused Testcontainers test dependencies | KEPT | 77 run / 0F 0E 0S | FAIL | -7,322,192 | 80 |  |
| R01-revert-B03-jul-to-slf4j | R01-revert-B03-jul-to-slf4j: revert B03: jul-to-slf4j exclusion changed log routing (found after the fact; checklist extended with log-routing item) | KEPT | 77 run / 0F 0E 0S | FAIL | -7,315,105 | 81 |  |
| S-free-only | FREE-ONLY state: the 16 kept 'free' changes (A16 A18 A19 A21 A23 B01 B02 B04 B21 B22 B24 C01 C02 C03 C09 C11) applied to 500158f | ? | 81 run / 0F 0E 0S | pass | -3,501,643 | 84 |  |
