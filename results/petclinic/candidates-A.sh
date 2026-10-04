#!/usr/bin/env bash
# Group A: every direct dependency flagged by dependency:analyze and/or DepClean, removed one at a time.
R=/workspaces/maven-slimming-experiment/results/scripts/run_candidate.sh
B=org.springframework.boot
rm1() { $R petclinic "$1" "remove $2:$3" "\$PE remove pom.xml $2 $3"; }
rm1 A02-starter-actuator $B spring-boot-starter-actuator
rm1 A03-starter-cache $B spring-boot-starter-cache
rm1 A04-starter-data-jpa $B spring-boot-starter-data-jpa
rm1 A05-starter-thymeleaf $B spring-boot-starter-thymeleaf
rm1 A06-starter-validation $B spring-boot-starter-validation
rm1 A07-starter-webmvc $B spring-boot-starter-webmvc
rm1 A08-h2 com.h2database h2
rm1 A09-caffeine com.github.ben-manes.caffeine caffeine
rm1 A10-mysql-connector-j com.mysql mysql-connector-j
rm1 A11-postgresql org.postgresql postgresql
rm1 A12-webjars-locator-lite org.webjars webjars-locator-lite
rm1 A13-webjar-bootstrap org.webjars.npm bootstrap
rm1 A14-webjar-font-awesome org.webjars.npm font-awesome
rm1 A15-starter-data-jpa-test $B spring-boot-starter-data-jpa-test
rm1 A16-starter-restclient $B spring-boot-starter-restclient
rm1 A17-starter-restclient-test $B spring-boot-starter-restclient-test
rm1 A18-starter-thymeleaf-test $B spring-boot-starter-thymeleaf-test
rm1 A19-starter-validation-test $B spring-boot-starter-validation-test
rm1 A20-starter-webmvc-test $B spring-boot-starter-webmvc-test
rm1 A21-starter-actuator-test $B spring-boot-starter-actuator-test
rm1 A22-docker-compose $B spring-boot-docker-compose
rm1 A23-starter-cache-test $B spring-boot-starter-cache-test
