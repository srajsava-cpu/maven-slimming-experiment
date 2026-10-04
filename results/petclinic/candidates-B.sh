#!/usr/bin/env bash
# Group B: transitive dependencies flagged by DepClean that contain classes, each excluded from every path.
# (POM-only starter JARs flagged by DepClean are not tried: they contain no classes and are already
#  left out of the Boot fat jar; excluding one would only drop its own transitive dependencies.)
R=/workspaces/maven-slimming-experiment/results/scripts/run_candidate.sh
X=/workspaces/maven-slimming-experiment/results/scripts/exclude_everywhere.sh
B=org.springframework.boot
ex() { $R petclinic "$1" "exclude $2:$3 everywhere" "$X $2 $3"; }
ex B01-snakeyaml org.yaml snakeyaml
ex B02-HdrHistogram org.hdrhistogram HdrHistogram
ex B03-jul-to-slf4j org.slf4j jul-to-slf4j
ex B04-micrometer-jakarta9 io.micrometer micrometer-jakarta9
ex B05-boot-actuator $B spring-boot-actuator
ex B06-boot-actuator-autoconfigure $B spring-boot-actuator-autoconfigure
ex B07-boot-micrometer-metrics $B spring-boot-micrometer-metrics
ex B08-boot-micrometer-observation $B spring-boot-micrometer-observation
ex B09-boot-health $B spring-boot-health
ex B10-boot-web-server $B spring-boot-web-server
ex B11-boot-tomcat $B spring-boot-tomcat
ex B12-boot-http-converter $B spring-boot-http-converter
ex B13-boot-servlet $B spring-boot-servlet
ex B14-boot-thymeleaf $B spring-boot-thymeleaf
ex B15-thymeleaf-spring6 org.thymeleaf thymeleaf-spring6
ex B16-attoparser org.attoparser attoparser
ex B17-unbescape org.unbescape unbescape
ex B18-boot-data-commons $B spring-boot-data-commons
ex B19-boot-validation $B spring-boot-validation
ex B20-boot-data-jpa $B spring-boot-data-jpa
ex B21-commons-codec-test commons-codec commons-codec
ex B22-awaitility-test org.awaitility awaitility
ex B23-micrometer-observation-test io.micrometer micrometer-observation-test
ex B24-boot-restclient-test $B spring-boot-restclient-test
ex B25-boot-micrometer-metrics-test $B spring-boot-micrometer-metrics-test
ex B26-boot-cache-test $B spring-boot-cache-test
