# Per-project settings, sourced by evaluate_candidate.sh. usage: source project_config.sh <project>
TOP=/workspaces/maven-slimming-experiment
source "$TOP/results/scripts/env.sh" >/dev/null
case $1 in
  petclinic)
    use_jdk 17 >/dev/null
    CLONE=$TOP/work/petclinic
    BASE_REF=500158f732419217507c7656904b8e6aa1bcc0d6
    VERIFY_CMD="./mvnw -B clean verify"
    ARTIFACT_GLOB="target/spring-petclinic-*.jar"
    REPORT_DIRS="target/surefire-reports target/failsafe-reports"
    TREE_ARGS=""
    CHECKLIST_RUNNER=$TOP/results/scripts/petclinic_run_checklist.sh
    CHECKLIST_PROFILES="h2 mysql postgres"
    ;;
  *) echo "unknown project $1" >&2; return 1 ;;
esac
