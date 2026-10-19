#!/usr/bin/env python3
# =============================================================
# server.py — local backend for submitting the PIR to Jira
# Service Management (Option B: OAuth + attachment upload).
#
# Python standard library only (plus certifi if available, for TLS
# on macOS python.org installs). No framework, no pip install needed.
#
# What it does:
#   - serves the allocation-plan/ HTML tools over http://localhost
#     (so the browser can call /api/* without CORS / file:// issues)
#   - OAuth 3LO with Atlassian:  /auth/login -> consent -> /auth/callback
#   - /api/me       : who am I (401 if not authenticated)
#   - /api/fields   : request-type fields (for reference)
#   - /api/submit   : attachTemporaryFile + create the Service Desk request
#
# IMPORTANT — this is built to run, but real submission needs:
#   - an Atlassian OAuth app (client id/secret) with a registered
#     redirect URI that matches REDIRECT_URI below
#   - the app granted the Service Desk scopes
#   - it hosted somewhere HTTPS for production (localhost is fine to dev)
# Until those exist, /auth/login will fail at Atlassian's side — expected.
#
# Config: reads ../.env (same file as the rest of the project).
# =============================================================

import os, re, json, ssl, base64, secrets, mimetypes, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# ---------- paths ----------
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR    = os.path.normpath(os.path.join(SERVER_DIR, ".."))   # allocation-plan/
ENV_PATH   = os.path.normpath(os.path.join(SERVER_DIR, "..", "..", ".env"))

# ---------- tiny .env loader ----------
def load_env():
    cfg = {}
    if os.path.isfile(ENV_PATH):
        for line in open(ENV_PATH, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    # environment overrides .env
    for k in list(cfg) + ["ATLASSIAN_CLIENT_ID","ATLASSIAN_CLIENT_SECRET","REDIRECT_URI",
                            "JIRA_CLOUD_ID","JIRA_BASE_URL","JIRA_EMAIL","JIRA_API_TOKEN",
                            "SERVICE_DESK_ID_PIR","REQUEST_TYPE_ID_PIR","FORECAST_FIELD_ID","PORT"]:
        if os.environ.get(k):
            cfg[k] = os.environ[k]
    return cfg

CFG = load_env()
PORT = int(CFG.get("PORT", "8723"))

# Discovered values (defaults; override in .env if the portal changes).
# Uses *_PIR keys so it doesn't clash with the other tool's SERVICE_DESK_ID.
SERVICE_DESK_ID  = CFG.get("SERVICE_DESK_ID_PIR", "2067")   # API id (portal 2065)
REQUEST_TYPE_ID  = CFG.get("REQUEST_TYPE_ID_PIR", "2866")
FORECAST_FIELD   = CFG.get("FORECAST_FIELD_ID", "customfield_19943")
JIRA_BASE_URL    = CFG.get("JIRA_BASE_URL", "https://fdz.atlassian.net").rstrip("/")

# OAuth config (fill in .env to enable the OAuth flow)
CLIENT_ID     = CFG.get("ATLASSIAN_CLIENT_ID", "")
CLIENT_SECRET = CFG.get("ATLASSIAN_CLIENT_SECRET", "")
REDIRECT_URI  = CFG.get("REDIRECT_URI", f"http://localhost:{PORT}/auth/callback")
CLOUD_ID      = CFG.get("JIRA_CLOUD_ID", "")   # resolved from token if blank
SCOPES        = "read:servicedesk-request write:servicedesk-request read:jira-user offline_access"

# Basic-auth fallback (API token) — handy for local dev / discovery while the
# OAuth app isn't registered yet. Never use in production.
EMAIL = CFG.get("JIRA_EMAIL", "")
TOKEN = CFG.get("JIRA_API_TOKEN", "")

def ssl_ctx():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()

CTX = ssl_ctx()

# ---------- in-memory session (single-user local dev) ----------
SESSION = {"access_token": None, "cloud_id": CLOUD_ID or None, "oauth_state": None}

def auth_mode():
    """Prefer OAuth if we have a token; else basic-auth token if present."""
    if SESSION["access_token"]:
        return "oauth"
    if EMAIL and TOKEN and "paste" not in TOKEN:
        return "basic"
    return None

def api_base():
    """Return (base_url, headers) for a Jira REST call in the active auth mode."""
    mode = auth_mode()
    if mode == "oauth":
        cid = SESSION["cloud_id"]
        return (f"https://api.atlassian.com/ex/jira/{cid}",
                {"Authorization": f"Bearer {SESSION['access_token']}"})
    if mode == "basic":
        a = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
        return (JIRA_BASE_URL, {"Authorization": f"Basic {a}"})
    return (None, None)

# ---------- HTTP helpers ----------
def http_json(method, url, headers=None, body=None):
    h = {"Accept": "application/json", "User-Agent": "pir-server/1.0"}
    if headers: h.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8"); h["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=h, method=method)
    with urlopen(req, timeout=60, context=CTX) as r:
        raw = r.read().decode("utf-8")
        return r.status, (json.loads(raw) if raw.strip() else {})

def resolve_cloud_id():
    """For OAuth: map the token to the site's cloudId."""
    if SESSION["cloud_id"]:
        return SESSION["cloud_id"]
    s, data = http_json("GET", "https://api.atlassian.com/oauth/token/accessible-resources",
                         headers={"Authorization": f"Bearer {SESSION['access_token']}"})
    if isinstance(data, list) and data:
        SESSION["cloud_id"] = data[0]["id"]
    return SESSION["cloud_id"]

# ---------- Service Desk operations ----------
def sd_attach_temp_file(filename, content_bytes):
    """Upload a temporary file; returns its temporaryAttachmentId."""
    base, headers = api_base()
    url = f"{base}/rest/servicedeskapi/servicedesk/{SERVICE_DESK_ID}/attachTemporaryFile"
    boundary = "----pirboundary" + secrets.token_hex(8)
    body = bytearray()
    body += f"--{boundary}\r\n".encode()
    body += (f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n').encode()
    body += b"Content-Type: text/csv\r\n\r\n"
    body += content_bytes + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    h = dict(headers)
    h["X-Atlassian-Token"] = "no-check"
    h["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    h["Accept"] = "application/json"
    h["User-Agent"] = "pir-server/1.0"
    req = Request(url, data=bytes(body), headers=h, method="POST")
    with urlopen(req, timeout=60, context=CTX) as r:
        doc = json.loads(r.read().decode("utf-8"))
    return doc["temporaryAttachments"][0]["temporaryAttachmentId"]

def sd_create_request(summary, justification, forecast, temp_attachment_id):
    base, headers = api_base()
    url = f"{base}/rest/servicedeskapi/request"
    payload = {
        "serviceDeskId": SERVICE_DESK_ID,
        "requestTypeId": REQUEST_TYPE_ID,
        "requestFieldValues": {
            "summary": summary,
            "description": justification,
            FORECAST_FIELD: forecast,
        },
    }
    if temp_attachment_id:
        payload["requestFieldValues"]["attachment"] = {
            "temporaryAttachmentIds": [temp_attachment_id],
            "public": True,
        }
    h = dict(headers); h["Content-Type"] = "application/json"; h["Accept"] = "application/json"
    return http_json("POST", url, headers=h, body=payload)

# ---------- request handler ----------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass   # quiet

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---- GET: static files + auth + small APIs ----
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        route = p.path

        if route == "/auth/login":
            return self.handle_login()
        if route == "/auth/callback":
            return self.handle_callback(urllib.parse.parse_qs(p.query))
        if route == "/api/me":
            return self.handle_me()
        if route == "/api/fields":
            return self.handle_fields()
        # static
        return self.serve_static(route)

    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/api/submit":
            return self.handle_submit()
        self._send(404, {"error": "not found"})

    # ---- static file serving (the HTML tools) ----
    def serve_static(self, route):
        if route == "/" or route == "":
            route = "/pir.html"
        rel = route.lstrip("/")
        full = os.path.normpath(os.path.join(WEB_DIR, rel))
        if not full.startswith(WEB_DIR) or not os.path.isfile(full):
            return self._send(404, "Not found", "text/plain")
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ---- OAuth ----
    def handle_login(self):
        if not CLIENT_ID:
            return self._send(500, "OAuth not configured. Set ATLASSIAN_CLIENT_ID / "
                              "ATLASSIAN_CLIENT_SECRET / REDIRECT_URI in .env.", "text/plain")
        state = secrets.token_urlsafe(16)
        SESSION["oauth_state"] = state
        params = {
            "audience": "api.atlassian.com", "client_id": CLIENT_ID,
            "scope": SCOPES, "redirect_uri": REDIRECT_URI,
            "state": state, "response_type": "code", "prompt": "consent",
        }
        url = "https://auth.atlassian.com/authorize?" + urllib.parse.urlencode(params)
        self.send_response(302); self.send_header("Location", url); self.end_headers()

    def handle_callback(self, q):
        code = (q.get("code") or [None])[0]
        state = (q.get("state") or [None])[0]
        if not code or state != SESSION.get("oauth_state"):
            return self._send(400, "Invalid OAuth state/code.", "text/plain")
        try:
            s, tok = http_json("POST", "https://auth.atlassian.com/oauth/token", body={
                "grant_type": "authorization_code", "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET, "code": code, "redirect_uri": REDIRECT_URI,
            })
            SESSION["access_token"] = tok.get("access_token")
            resolve_cloud_id()
        except HTTPError as e:
            return self._send(502, f"Token exchange failed: {e.read().decode('utf-8','replace')}", "text/plain")
        # back to the app
        self.send_response(302); self.send_header("Location", "/pir.html?auth=ok"); self.end_headers()

    # ---- small APIs ----
    def handle_me(self):
        if not auth_mode():
            return self._send(401, {"authenticated": False, "login": "/auth/login"})
        try:
            base, headers = api_base()
            s, me = http_json("GET", f"{base}/rest/api/3/myself", headers=headers)
            return self._send(200, {"authenticated": True, "mode": auth_mode(),
                                    "displayName": me.get("displayName"), "email": me.get("emailAddress")})
        except HTTPError as e:
            return self._send(e.code, {"authenticated": False, "error": e.read().decode("utf-8","replace")})

    def handle_fields(self):
        if not auth_mode():
            return self._send(401, {"error": "not authenticated", "login": "/auth/login"})
        base, headers = api_base()
        url = f"{base}/rest/servicedeskapi/servicedesk/{SERVICE_DESK_ID}/requesttype/{REQUEST_TYPE_ID}/field"
        try:
            s, doc = http_json("GET", url, headers=headers)
            return self._send(200, doc)
        except HTTPError as e:
            return self._send(e.code, {"error": e.read().decode("utf-8","replace")})

    def handle_submit(self):
        if not auth_mode():
            return self._send(401, {"error": "not authenticated", "login": "/auth/login"})
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            return self._send(400, {"error": "invalid JSON body"})

        summary = (data.get("summary") or "").strip()
        justification = (data.get("justification") or "").strip()
        forecast = (data.get("forecast") or "#").strip() or "#"
        csv_text = data.get("csv") or ""
        csv_name = data.get("filename") or "allocation-plan.csv"

        if not summary or not justification:
            return self._send(400, {"error": "summary and justification are required"})

        try:
            temp_id = None
            if csv_text:
                temp_id = sd_attach_temp_file(csv_name, csv_text.encode("utf-8"))
            status, resp = sd_create_request(summary, justification, forecast, temp_id)
            key = resp.get("issueKey")
            link = ((resp.get("_links") or {}).get("web")) or ""
            return self._send(200, {"ok": True, "issueKey": key, "web": link})
        except HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            return self._send(e.code, {"ok": False, "error": detail})
        except URLError as e:
            return self._send(502, {"ok": False, "error": str(e)})

def main():
    print(f"PIR server on http://localhost:{PORT}  (serving {WEB_DIR})")
    print(f"  auth mode available: {auth_mode() or 'none — configure OAuth or API token in .env'}")
    print(f"  service desk {SERVICE_DESK_ID}, request type {REQUEST_TYPE_ID}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

if __name__ == "__main__":
    main()
