#!/usr/bin/env bash
# Group C: reductions the analyzers did not suggest, found by reading the dependency tree and jar contents.
R=/workspaces/maven-slimming-experiment/results/scripts/run_candidate.sh
X=/workspaces/maven-slimming-experiment/results/scripts/exclude_everywhere.sh
ex() { $R petclinic "$1" "exclude $2:$3 everywhere" "$X $2 $3"; }
ex C01-aspectjweaver org.aspectj aspectjweaver
ex C02-spring-aspects org.springframework spring-aspects
ex C03-tomcat-embed-websocket org.apache.tomcat.embed tomcat-embed-websocket
$R petclinic C04-no-jarmode-tools "spring-boot-maven-plugin: includeTools=false (drop spring-boot-jarmode-tools)" \
  "python3 -c \"import re;p='pom.xml';s=open(p).read();i=s.index('<artifactId>spring-boot-maven-plugin</artifactId>');s=s[:i]+s[i:].replace('<executions>','<configuration>\n          <includeTools>false</includeTools>\n        </configuration>\n        <executions>',1);open(p,'w').write(s)\""
$R petclinic C05-cache-api "remove javax.cache:cache-api" "\$PE remove pom.xml javax.cache cache-api"
$R petclinic C06-jakarta-xml-bind-api "remove jakarta.xml.bind:jakarta.xml.bind-api" "\$PE remove pom.xml jakarta.xml.bind jakarta.xml.bind-api"
ex C07-jaxb-runtime org.glassfish.jaxb jaxb-runtime
ex C08-byte-buddy net.bytebuddy byte-buddy
ex C09-log4j-to-slf4j org.apache.logging.log4j log4j-to-slf4j
ex C10-log4j-api org.apache.logging.log4j log4j-api
ex C11-error-prone-annotations com.google.errorprone error_prone_annotations
ex C12-jspecify org.jspecify jspecify
ex C13-antlr4-runtime org.antlr antlr4-runtime
ex C14-HikariCP com.zaxxer HikariCP
ex C15-tomcat-embed-el org.apache.tomcat.embed tomcat-embed-el
ex C16-jboss-logging org.jboss.logging jboss-logging
ex C17-hibernate-models org.hibernate.models hibernate-models
ex C18-jakarta-inject-api jakarta.inject jakarta.inject-api
