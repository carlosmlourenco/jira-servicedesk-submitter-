#!/usr/bin/env bash
# =============================================================
# discover-fields.sh
# Lists the fields (required + optional) that this Service Desk
# request type expects, so you know exactly what to submit.
#
# Also verifies your credentials and that the SERVICE_DESK_ID /
# REQUEST_TYPE_ID in .env are valid.
#
# Usage:  ./discover-fields.sh
# =============================================================

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
load_env

echo "🔎 Jira Service Desk — Field Discovery"
echo "   Base URL   : ${JIRA_BASE_URL}"
echo "   As user    : ${JIRA_EMAIL}"
echo "   Service Desk: ${SERVICE_DESK_ID}   Request Type: ${REQUEST_TYPE_ID}"
echo "──────────────────────────────────────────────"

# 1) sanity check: who am I?
echo "→ Verifying credentials..."
api_get "${JIRA_BASE_URL}/rest/api/3/myself"
if [[ "$HTTP_CODE" != "200" ]]; then
  echo "❌ Credential check failed (HTTP ${HTTP_CODE}): $(explain_http "$HTTP_CODE")" >&2
  echo "$BODY" | json_pretty >&2 || true
  exit 1
fi
DISPLAY_NAME="$(echo "$BODY" | json_get "['displayName']")"
echo "✅ Authenticated as: ${DISPLAY_NAME}"
echo ""

# 2) fetch the fields for this request type
echo "→ Fetching fields for request type ${REQUEST_TYPE_ID}..."
FIELDS_URL="${JIRA_BASE_URL}/rest/servicedeskapi/servicedesk/${SERVICE_DESK_ID}/requesttype/${REQUEST_TYPE_ID}/field"
api_get "$FIELDS_URL"

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "❌ Could not fetch fields (HTTP ${HTTP_CODE}): $(explain_http "$HTTP_CODE")" >&2
  echo "$BODY" | json_pretty >&2 || true
  echo "" >&2
  echo "   Tip: portal IDs in the URL can differ from the API's serviceDeskId." >&2
  echo "   List your service desks with:" >&2
  echo "     curl -s -u \"\$JIRA_EMAIL:\$JIRA_API_TOKEN\" \\" >&2
  echo "       \"${JIRA_BASE_URL}/rest/servicedeskapi/servicedesk\" | python3 -m json.tool" >&2
  exit 1
fi

# 3) pretty-print the field list in a readable table
echo "✅ Fields for this request type:"
echo ""
echo "$BODY" | python3 - "$@" <<'PY'
import sys, json
doc = json.load(sys.stdin)
fields = doc.get("requestTypeFields", [])
if not fields:
    print("  (no fields returned)")
    sys.exit(0)

print(f"  {'FIELD ID':<24} {'REQ':<4} {'TYPE':<12} NAME")
print("  " + "-" * 70)
for f in fields:
    fid   = f.get("fieldId", "")
    req   = "yes" if f.get("required") else "no"
    name  = f.get("name", "")
    jira  = f.get("jiraSchema", {}) or {}
    ftype = jira.get("type", "")
    print(f"  {fid:<24} {req:<4} {ftype:<12} {name}")

    # show allowed values for select-style fields, if any
    vals = f.get("validValues", []) or []
    if vals:
        shown = ", ".join(v.get("label", v.get("value","")) for v in vals[:8])
        more  = "" if len(vals) <= 8 else f" …(+{len(vals)-8} more)"
        print(f"      allowed: {shown}{more}")

print("")
print("  Legend: REQ=yes means the field is mandatory when submitting.")
print("  Put required fields into request-fields.json before running submit-request.sh")
PY

# 4) save the raw response for reference / debugging
OUT="${SCRIPT_DIR}/last-fields.json"
echo "$BODY" | json_pretty > "$OUT" 2>/dev/null || echo "$BODY" > "$OUT"
echo ""
echo "📄 Raw field schema saved to: ${OUT}"
