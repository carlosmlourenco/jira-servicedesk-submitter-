#!/usr/bin/env bash
# =============================================================
# lib/common.sh — shared helpers for the Service Desk scripts
# Sourced by discover-fields.sh and submit-request.sh
# Zero external dependencies: uses curl (built in) and python3
# (built in on macOS) for JSON. Auto-uses jq if it is installed.
# =============================================================

set -euo pipefail

# ---- locate project root regardless of where we're called from ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---- load .env -------------------------------------------------
load_env() {
  local env_file="${SCRIPT_DIR}/.env"
  if [[ ! -f "$env_file" ]]; then
    echo "❌ No .env file found at ${env_file}" >&2
    echo "   Copy .env.example to .env and fill in your details." >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  set -a; source "$env_file"; set +a

  : "${JIRA_BASE_URL:?JIRA_BASE_URL is not set in .env}"
  : "${JIRA_EMAIL:?JIRA_EMAIL is not set in .env}"
  : "${JIRA_API_TOKEN:?JIRA_API_TOKEN is not set in .env}"
  : "${SERVICE_DESK_ID:?SERVICE_DESK_ID is not set in .env}"
  : "${REQUEST_TYPE_ID:?REQUEST_TYPE_ID is not set in .env}"

  # strip any accidental trailing slash on the base URL
  JIRA_BASE_URL="${JIRA_BASE_URL%/}"
}

# ---- JSON pretty-print (jq if present, else python3) -----------
json_pretty() {
  if command -v jq >/dev/null 2>&1; then
    jq .
  else
    python3 -m json.tool
  fi
}

# ---- extract a value from JSON on stdin ------------------------
# usage: echo "$json" | json_get '["issueKey"]'
# The argument is a python indexing expression applied to the parsed doc.
json_get() {
  local expr="$1"
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d${expr})" 2>/dev/null || true
}

# ---- authenticated GET ; prints body, sets HTTP_CODE ----------
api_get() {
  local url="$1"
  local resp
  resp="$(curl -sS -w $'\n%{http_code}' \
    -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
    -H "Accept: application/json" \
    "$url")"
  HTTP_CODE="${resp##*$'\n'}"
  BODY="${resp%$'\n'*}"
}

# ---- authenticated POST of a JSON body ; prints body, sets HTTP_CODE ----
api_post_json() {
  local url="$1"
  local data_file="$2"
  local resp
  resp="$(curl -sS -w $'\n%{http_code}' \
    -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -X POST \
    --data @"${data_file}" \
    "$url")"
  HTTP_CODE="${resp##*$'\n'}"
  BODY="${resp%$'\n'*}"
}

# ---- friendly explanation for common HTTP codes ----------------
explain_http() {
  case "$1" in
    200|201) echo "OK" ;;
    204)     echo "OK (no content)" ;;
    400)     echo "Bad request — a field value was rejected. Check the field mapping." ;;
    401)     echo "Unauthorized — check JIRA_EMAIL and JIRA_API_TOKEN in .env." ;;
    403)     echo "Forbidden — your account lacks permission on this portal." ;;
    404)     echo "Not found — check SERVICE_DESK_ID / REQUEST_TYPE_ID (portal vs API id mismatch?)." ;;
    *)       echo "Unexpected HTTP $1." ;;
  esac
}
