#!/usr/bin/env bash
# Run the PetClinic behaviour checklist against a built jar for every supported database profile.
# usage: petclinic_run_checklist.sh <jar> <out-dir>
# Writes <out-dir>/checklist-{h2,mysql,postgres}.json and app logs.
set -u
JAR=$(realpath "$1"); OUT=$(realpath -m "$2"); mkdir -p "$OUT"
HERE=$(dirname "$(realpath "$0")")
PORT=18080

wait_up() {
  for i in $(seq 1 180); do
    curl -sf "http://localhost:$PORT/" >/dev/null && return 0
    kill -0 "$APP" 2>/dev/null || return 1
    sleep 1
  done
  return 1
}

for profile in h2 mysql postgres; do
  docker rm -f -v pc-mysql pc-postgres >/dev/null 2>&1
  case $profile in
    mysql)
      docker run -d --name pc-mysql -e MYSQL_USER=petclinic -e MYSQL_PASSWORD=petclinic -e MYSQL_ROOT_PASSWORD=root \
        -e MYSQL_DATABASE=petclinic -p 3306:3306 mysql:9.7 >/dev/null
      # TCP ping: the image's temporary init server is socket-only, so only the real server answers over TCP
      until docker exec pc-mysql mysqladmin ping -h 127.0.0.1 --protocol=tcp -upetclinic -ppetclinic >/dev/null 2>&1; do sleep 2; done
      PROFILE_ARG=--spring.profiles.active=mysql ;;
    postgres)
      docker run -d --name pc-postgres -e POSTGRES_USER=petclinic -e POSTGRES_PASSWORD=petclinic -e POSTGRES_DB=petclinic \
        -p 5432:5432 postgres:18.4 >/dev/null
      until docker exec pc-postgres pg_isready -U petclinic -h localhost >/dev/null 2>&1; do sleep 2; done
      sleep 2
      PROFILE_ARG=--spring.profiles.active=postgres ;;
    *) PROFILE_ARG= ;;
  esac
  java -jar "$JAR" --server.port=$PORT --logging.level.org.springframework.cache=trace $PROFILE_ARG > "$OUT/app-$profile.log" 2>&1 &
  APP=$!
  if wait_up; then
    python3 "$HERE/petclinic_checklist.py" "http://localhost:$PORT" "$OUT/checklist-$profile.json" "$OUT/app-$profile.log"
    # confirm the write really reached the external database
    case $profile in
      mysql) n=$(docker exec pc-mysql mysql -N -upetclinic -ppetclinic -e "select count(*) from owners where last_name='Lovelace'" petclinic 2>/dev/null) ;;
      postgres) n=$(docker exec pc-postgres psql -tA -U petclinic -c "select count(*) from owners where last_name='Lovelace'" petclinic) ;;
      *) n="n/a (in-memory)" ;;
    esac
    python3 - "$OUT/checklist-$profile.json" "$n" <<'EOF'
import json,sys
p,n=sys.argv[1],sys.argv[2]
d=json.load(open(p)); d.append({"id":"db-row","description":"Created owner row present in the external database","request":"SQL count","status":None,"content_type":None,"signature":f"rows={n.strip()}"})
json.dump(d,open(p,"w"),indent=1)
EOF
  else
    echo "APP FAILED TO START for profile $profile" | tee "$OUT/checklist-$profile.json.failed"
    echo '[{"id":"startup","status":"FAILED","content_type":null,"signature":"app did not start","description":"startup","request":""}]' > "$OUT/checklist-$profile.json"
  fi
  kill "$APP" 2>/dev/null; wait "$APP" 2>/dev/null
done
docker rm -f -v pc-mysql pc-postgres >/dev/null 2>&1
echo done
