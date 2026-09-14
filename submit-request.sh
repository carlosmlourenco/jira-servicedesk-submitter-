#!/usr/bin/env bash
# =============================================================
# submit-request.sh
# Submits a request to the Jira Service Desk portal on your behalf.
#
# It reads the field values from a JSON file (default:
# request-fields.json) whose keys are Jira field IDs, e.g.:
#
#   {
#     "summary": "Laptop won't boot",
#     "description": "Since this morning it shows a black screen."
#   }
#
# Run ./discover-fields.sh first to learn the exact field IDs and
# which ones are required for this request type.
#
# Usage:
#   ./submit-request.sh                     # uses request-fields.json
#   ./submit-request.sh my-fields.json      # custom file
#   ./submit-request.sh --dry-run           # build & show payload, don't send
# =============================================================

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
load_env

DRY_RUN="false"
FIELDS_FILE="${SCRIPT_DIR}/request-fields.json"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN="true" ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) FIELDS_FILE="$arg" ;;
  esac
done

if [[ ! -f "$FIELDS_FILE" ]]; then
  echo "❌ Fields file not found: ${FIELDS_FILE}" >&2
  echo "   Create it (see request-fields.example.json) or pass a path." >&2
  exit 1
fi

echo "🚀 Jira Service Desk — Submit Request"
echo "   As user     : ${JIRA_EMAIL}"
echo "   Service Desk : ${SERVICE_DESK_ID}   Request Type: ${REQUEST_TYPE_ID}"
echo "   Fields file  : ${FIELDS_FILE}"
echo "──────────────────────────────────────────────"

# Build the request payload:
#   { serviceDeskId, requestTypeId, requestFieldValues: {…your fields…} }
PAYLOAD_FILE="$(mktemp)"
trap 'rm -f "$PAYLOAD_FILE"' EXIT

python3 - "$FIELDS_FILE" "$SERVICE_DESK_ID" "$REQUEST_TYPE_ID" > "$PAYLOAD_FILE" <<'PY'
import sys, json
fields_file, sd_id, rt_id = sys.argv[1], sys.argv[2], sys.argv[3]
with open(fields_file) as fh:
    field_values = json.load(fh)
if not isinstance(field_values, dict):
    sys.stderr.write("Fields file must be a JSON object of fieldId -> value.\n")
    sys.exit(1)
payload = {
    "serviceDeskId": sd_id,
    "requestTypeId": rt_id,
    "requestFieldValues": field_values,
}
print(json.dumps(payload, indent=2))
PY

echo "→ Payload to be sent:"
cat "$PAYLOAD_FILE"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
  echo "🧪 Dry run — nothing was submitted."
  exit 0
fi

read -r -p "Submit this request now? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Cancelled. Nothing submitted."
  exit 0
fi

echo "→ Submitting..."
api_post_json "${JIRA_BASE_URL}/rest/servicedeskapi/request" "$PAYLOAD_FILE"

if [[ "$HTTP_CODE" == "201" || "$HTTP_CODE" == "200" ]]; then
  ISSUE_KEY="$(echo "$BODY" | json_get "['issueKey']")"
  LINK="$(echo "$BODY" | json_get "['_links']['web']")"
  echo "✅ Request created: ${ISSUE_KEY}"
  [[ -n "$LINK" ]] && echo "   View it: ${LINK}"
else
  echo "❌ Submission failed (HTTP ${HTTP_CODE}): $(explain_http "$HTTP_CODE")" >&2
  echo "$BODY" | json_pretty >&2 || echo "$BODY" >&2
  exit 1
fi
