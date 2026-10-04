#!/usr/bin/env python3
"""PetClinic behaviour checklist. Usage: petclinic_checklist.py <base-url> <out.json>

Each item records HTTP status, content type and a short deterministic signature of the
response body, so that runs before and after a change can be compared with
checklist_compare.py. No redirects are followed (Location is recorded instead).
"""
import json, re, sys, urllib.request, urllib.parse, urllib.error

BASE = sys.argv[1].rstrip("/")
OUT = sys.argv[2]
APP_LOG = sys.argv[3] if len(sys.argv) > 3 else None  # app started with logging.level.org.springframework.cache=trace
BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


opener = urllib.request.build_opener(NoRedirect)


def req(method, path, accept=None, form=None):
    data = urllib.parse.urlencode(form).encode() if form is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method)
    if accept:
        r.add_header("Accept", accept)
    if form is not None:
        r.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        resp = opener.open(r, timeout=30)
        status, headers, body = resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as e:
        status, headers, body = e.code, e.headers, e.read()
    ctype = (headers.get("Content-Type") or "").split(";")[0].strip()
    return status, ctype, headers, body


def title(b):
    m = re.search(rb"<title>(.*?)</title>", b, re.S)
    return m.group(1).decode().strip() if m else None


def h2(b):
    m = re.search(rb"<h2[^>]*>(.*?)</h2>", b, re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1).decode())).strip() if m else None


def rows(b):
    m = re.search(rb"<tbody>(.*?)</tbody>", b, re.S)
    return len(re.findall(rb"<tr", m.group(1))) if m else 0


def has(b, *words):
    return ",".join(f"{w}={'y' if w.encode() in b else 'n'}" for w in words)


results = []


def check(cid, desc, method, path, sig, accept=BROWSER, form=None):
    status, ctype, headers, body = req(method, path, accept, form)
    try:
        s = sig(status, headers, body)
    except Exception as e:  # signature extraction must never abort the run
        s = f"SIGERR {type(e).__name__}: {e}"
    results.append({"id": cid, "description": desc, "request": f"{method} {path}" + (f" Accept: {accept}" if accept else ""),
                    "status": status, "content_type": ctype, "signature": s})
    return status, headers, body


html = lambda s, h, b: f"title={title(b)}; h2={h2(b)}; rows={rows(b)}"
size = lambda s, h, b: f"bytes={len(b)}"
loc = lambda s, h, b: f"location={re.sub(r';jsessionid=[0-9A-F]+', '', re.sub(r'^https?://[^/]+', '', h.get('Location') or ''))}"


def vets_json(s, h, b):
    d = json.loads(b)
    vl = d["vetList"]
    return f"keys={sorted(d)}; vets={len(vl)}; vet0keys={sorted(vl[0])}; specialties={sum(len(v['specialties']) for v in vl)}"


def vets_xml(s, h, b):
    t = b.decode(errors="replace")
    root = re.search(r"<(\w+)[ >]", t.split("?>")[-1])
    return f"root={root.group(1) if root else None}; vetList={t.count('<vetList>')}; firstName={t.count('<firstName>')}"


def jkeys(path):
    def f(s, h, b):
        d = json.loads(b)
        for p in path:
            d = d[p]
        return f"{'.'.join(path) or 'root'}={sorted(d) if isinstance(d, dict) else d}"
    return f


def health(s, h, b):
    d = json.loads(b)
    return f"status={d.get('status')}; components={sorted(d.get('components', {}))}"


def caches(s, h, b):
    d = json.loads(b)
    return "; ".join(f"{m}:{n}->{c['target']}" for m, v in sorted(d["cacheManagers"].items())
                     for n, c in sorted(v["caches"].items()))


def metric_names(s, h, b):
    names = json.loads(b)["names"]
    return f"count={len(names)}; cache.*={sorted(n for n in names if n.startswith('cache'))}"


def sbom(s, h, b):
    return f"ids={json.loads(b)['ids']}"


def info(s, h, b):
    d = json.loads(b)
    return f"keys={sorted(d)}; build.keys={sorted(d.get('build', {}))}"


# --- pages ---------------------------------------------------------------
check("home", "Welcome page", "GET", "/", lambda s, h, b: html(s, h, b) + "; " + has(b, "Welcome", "pets.png"))
check("home-de", "i18n: German welcome", "GET", "/?lang=de", lambda s, h, b: has(b, "Willkommen"))
check("home-es", "i18n: Spanish welcome", "GET", "/?lang=es", lambda s, h, b: has(b, "Bienvenido"))
check("find", "Find owners form", "GET", "/owners/find", html)
check("list-all", "Owner list page 1 (all owners)", "GET", "/owners?lastName=", html)
check("list-p2", "Owner list page 2", "GET", "/owners?lastName=&page=2", html)
check("list-davis", "Owner search with 2 matches", "GET", "/owners?lastName=Davis", html)
check("search-one", "Owner search with 1 match redirects", "GET", "/owners?lastName=Franklin", loc)
check("search-none", "Owner search with no match", "GET", "/owners?lastName=Nobody", lambda s, h, b: html(s, h, b) + "; " + has(b, "has not been found"))
check("owner1", "Owner details", "GET", "/owners/1", lambda s, h, b: html(s, h, b) + "; " + has(b, "George", "Franklin", "Leo"))
check("owner-missing", "Unknown owner id", "GET", "/owners/9999", lambda s, h, b: f"title={title(b)}")
check("owner-edit-form", "Edit owner form", "GET", "/owners/1/edit", lambda s, h, b: has(b, "George", "Update Owner"))
check("pet-new-form", "New pet form (pet types from DB)", "GET", "/owners/1/pets/new", lambda s, h, b: has(b, "hamster", "lizard", "snake"))
check("pet-edit-form", "Edit pet form", "GET", "/owners/1/pets/1/edit", lambda s, h, b: has(b, "Leo", "Update Pet"))
check("visit-form", "New visit form", "GET", "/owners/1/pets/1/visits/new", lambda s, h, b: has(b, "Leo", "Add Visit"))
check("vets-html", "Vet list HTML page 1", "GET", "/vets.html", html)
check("vets-html-p2", "Vet list HTML page 2", "GET", "/vets.html?page=2", html)
check("vets-json", "Vets resource as JSON", "GET", "/vets", vets_json, accept="application/json")
check("vets-xml", "Vets resource as XML", "GET", "/vets", vets_xml, accept="application/xml")
check("vets-default", "Vets resource, no Accept header preference", "GET", "/vets", lambda s, h, b: f"bytes={len(b)}", accept="*/*")
check("oups", "Deliberate exception page", "GET", "/oups", lambda s, h, b: has(b, "Something happened"))
check("notfound", "Unknown URL", "GET", "/does-not-exist", lambda s, h, b: "")
# --- static assets -------------------------------------------------------
check("css", "Compiled stylesheet", "GET", "/resources/css/petclinic.css", size)
check("img", "Image", "GET", "/resources/images/pets.png", size)
check("font", "Web font", "GET", "/resources/fonts/montserrat-webfont.woff", size)
check("favicon", "Favicon", "GET", "/resources/images/favicon.png", size)
check("webjar-bs", "Bootstrap JS via webjars locator (versionless URL)", "GET", "/webjars/bootstrap/dist/js/bootstrap.bundle.min.js", size)
check("webjar-fa", "Font Awesome CSS via webjars locator", "GET", "/webjars/font-awesome/css/font-awesome.min.css", size)
check("webjar-fa-font", "Font Awesome font via webjars locator", "GET", "/webjars/font-awesome/fonts/fontawesome-webfont.woff2", size)
# --- writes --------------------------------------------------------------
check("owner-create", "Create owner (write)", "POST", "/owners/new", loc,
      form={"firstName": "Ada", "lastName": "Lovelace", "address": "1 Analytical St", "city": "London", "telephone": "0123456789"})
check("owner-created", "Read back created owner", "GET", "/owners?lastName=Lovelace", loc)
check("owner-create-invalid", "Create owner with validation errors", "POST", "/owners/new",
      lambda s, h, b: has(b, "must not be blank", "Telephone must be a 10-digit number"),
      form={"firstName": "", "lastName": "", "address": "", "city": "", "telephone": "12"})
check("owner-update", "Update owner (write)", "POST", "/owners/1/edit", loc,
      form={"id": "1", "firstName": "George", "lastName": "Franklin", "address": "110 W. Liberty St.", "city": "Madison", "telephone": "6085551023"})
check("pet-create", "Add pet (write)", "POST", "/owners/1/pets/new", loc, form={"name": "Rex", "birthDate": "2020-01-01", "type": "dog"})
check("visit-create", "Add visit (write)", "POST", "/owners/1/pets/1/visits/new", loc, form={"date": "2099-01-01", "description": "checkup"})
check("owner1-after", "Owner details after writes", "GET", "/owners/1", lambda s, h, b: has(b, "Rex", "checkup"))
# --- actuator ------------------------------------------------------------
check("act-root", "Actuator discovery", "GET", "/actuator", jkeys(["_links"]))
check("health", "Health", "GET", "/actuator/health", health)
check("health-db", "Health: db component (404 = components not exposed)", "GET", "/actuator/health/db", lambda s, h, b: "")
check("info", "Info (build + git)", "GET", "/actuator/info", info)
check("metrics", "Metrics names", "GET", "/actuator/metrics", metric_names)
check("metric-jvm", "Metric jvm.memory.used", "GET", "/actuator/metrics/jvm.memory.used", jkeys(["name"]))
check("caches", "Cache managers and cache provider class", "GET", "/actuator/caches", caches)
check("sbom", "SBOM ids", "GET", "/actuator/sbom", sbom)
check("sbom-app", "Application SBOM", "GET", "/actuator/sbom/application", lambda s, h, b: f"bomFormat={json.loads(b).get('bomFormat')}")
check("prometheus", "Prometheus scrape endpoint", "GET", "/actuator/prometheus", lambda s, h, b: "")
for ep in ["beans", "conditions", "configprops", "env", "loggers", "mappings", "scheduledtasks", "threaddump", "heapdump"]:
    check(f"act-{ep}", f"Actuator {ep}", "GET", f"/actuator/{ep}", lambda s, h, b: "")


# --- caching behaviour: repeated /vets lookups must be served from the 'vets' cache --
req("GET", "/vets", accept="application/json")
req("GET", "/vets", accept="application/json")
if APP_LOG:
    import time; time.sleep(1)
    log = open(APP_LOG, errors="replace").read()
    created = log.count("Creating cache entry for key 'SimpleKey []' in cache(s) [vets]")
    found = log.count("Cache entry for key 'SimpleKey []' found in cache(s) [vets]")
    sig = f"findAll() cache entries created={created}; findAll() served from cache={'yes' if found > 0 else 'no'}"
else:
    sig = "not measured (no app log)"
results.append({"id": "cache-hit", "description": "Repeated GET /vets served from the 'vets' cache (cache interceptor trace log)",
                "request": "GET /vets (json) repeated", "status": None, "content_type": None, "signature": sig})

# --- log routing: every log line must go through Logback (Spring Boot format). Lines in the JDK's
# java.util.logging SimpleFormatter format ("Oct 03, 2026 11:57:14 PM <logger> <method>" / "INFO: ...")
# mean JUL output is no longer bridged to SLF4J (added after B03 showed this is invisible over HTTP).
if APP_LOG:
    log = open(APP_LOG, errors="replace").read()
    jul = len(re.findall(r"^[A-Z][a-z]{2} \d{2}, \d{4} \d{1,2}:\d{2}:\d{2} [AP]M ", log, re.M))
    sig = f"jul_simpleformatter_lines={jul}"
else:
    sig = "not measured (no app log)"
results.append({"id": "log-routing", "description": "All log output routed through Logback (no raw java.util.logging lines)",
                "request": "app log", "status": None, "content_type": None, "signature": sig})

json.dump(results, open(OUT, "w"), indent=1)
print(f"{len(results)} checks written to {OUT}")
