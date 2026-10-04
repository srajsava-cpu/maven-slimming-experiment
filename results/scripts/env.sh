# Source this at the start of every shell session: `source results/scripts/env.sh`
# All re-downloadable caches live on /tmp (separate disk, erased on Codespace stop).
export CACHE_ROOT=/tmp/mse-cache
mkdir -p "$CACHE_ROOT"/{m2/repository,npm,trivy,verify}
# Maven wrapper distributions -> $MAVEN_USER_HOME/wrapper
export MAVEN_USER_HOME="$CACHE_ROOT/m2"
# Maven local repository (system property, works on every Maven version)
export MAVEN_OPTS="-Dmaven.repo.local=$CACHE_ROOT/m2/repository ${MAVEN_OPTS_EXTRA:-}"
export npm_config_cache="$CACHE_ROOT/npm"
export TRIVY_CACHE_DIR="$CACHE_ROOT/trivy"
export SDKMAN_DIR=/usr/local/sdkman
_u=$-; set +u; source "$SDKMAN_DIR/bin/sdkman-init.sh"; [[ $_u == *u* ]] && set -u
# usage: use_jdk 17|21
use_jdk() {
  local v; v=$(ls "$SDKMAN_DIR/candidates/java" | grep -E "^$1\." | sort -V | tail -1)
  export JAVA_HOME="$SDKMAN_DIR/candidates/java/$v"; export PATH="$JAVA_HOME/bin:$PATH"
  echo "JAVA_HOME=$JAVA_HOME"
}
