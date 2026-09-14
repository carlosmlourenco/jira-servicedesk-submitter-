# Jira Service Desk Submitter

Submit requests to a Jira Service Management customer portal from the command
line, using nothing but `bash`, `curl`, and `python3` (all built in on macOS).

It targets a specific portal request type — for example the one behind:

```
https://fdz.atlassian.net/servicedesk/customer/portal/2065/group/2232/create/2932
```

where `2065` is the service desk (portal) ID and `2932` is the request type ID.

## Why the REST API instead of the web form

The customer portal is behind an authenticated login, so it can't be driven by
a simple script. Jira Service Management exposes a REST API for exactly this —
`POST /rest/servicedeskapi/request` — which creates a request as *you*, using
your own API token. That's what this project uses.

## Requirements

- macOS (or Linux) with `bash`, `curl`, and `python3` — all standard on macOS.
- A Jira account with access to the portal.
- A Jira API token: <https://id.atlassian.com/manage-profile/security/api-tokens>

No `node`, `npm`, or `jq` required. If `jq` happens to be installed, it's used
for nicer JSON output, but it's optional.

## Setup

1. Copy the example config and fill in your details:

   ```bash
   cp .env.example .env
   # then edit .env
   ```

   Fill in `JIRA_EMAIL`, `JIRA_API_TOKEN`, and confirm `SERVICE_DESK_ID` /
   `REQUEST_TYPE_ID`. The `.env` file is git-ignored and never committed.

2. Confirm your credentials and discover the fields this request type expects:

   ```bash
   ./discover-fields.sh
   ```

   This authenticates you, verifies the IDs, and prints every field with its
   ID, whether it's required, its type, and allowed values for dropdowns.
   The raw schema is also saved to `last-fields.json`.

## Submitting a request

1. Create your field values file from the example:

   ```bash
   cp request-fields.example.json request-fields.json
   # edit request-fields.json — keys are the field IDs from discover-fields.sh
   ```

   Example:

   ```json
   {
     "summary": "Laptop won't boot",
     "description": "Since this morning it shows a black screen on startup."
   }
   ```

2. Preview the exact payload without sending (recommended first):

   ```bash
   ./submit-request.sh --dry-run
   ```

3. Submit for real (asks for confirmation before sending):

   ```bash
   ./submit-request.sh
   ```

   On success it prints the created issue key and a link to view it.

   You can also point at a custom file:

   ```bash
   ./submit-request.sh path/to/other-fields.json
   ```

## Project layout

```
jira-servicedesk-submitter/
├── .env.example                  # config template (copy to .env)
├── .gitignore                    # keeps .env and secrets out of git
├── discover-fields.sh            # lists required/optional fields
├── submit-request.sh             # builds payload + submits the request
├── request-fields.example.json   # sample field values (copy to request-fields.json)
├── lib/
│   └── common.sh                 # shared helpers (auth, HTTP, JSON)
└── README.md
```

## How it works

- `lib/common.sh` loads `.env`, then makes authenticated `curl` calls using
  HTTP basic auth (`email:api_token`), which is the supported scheme for
  Atlassian Cloud REST APIs.
- `discover-fields.sh` calls
  `GET /rest/servicedeskapi/servicedesk/{id}/requesttype/{id}/field`.
- `submit-request.sh` wraps your field values into the request body
  (`serviceDeskId`, `requestTypeId`, `requestFieldValues`) and calls
  `POST /rest/servicedeskapi/request`.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `401 Unauthorized` | Wrong email or token | Recheck `.env`; regenerate the API token |
| `403 Forbidden` | No access to that portal | Ask for portal access; confirm you can open it in a browser |
| `404 Not Found` on fields | Portal ID ≠ API service desk ID | List desks: `curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" "$JIRA_BASE_URL/rest/servicedeskapi/servicedesk" \| python3 -m json.tool` |
| `400 Bad Request` on submit | A field value was rejected | Re-run `discover-fields.sh`; match required fields and allowed values |

## Security notes

- Your API token lives only in `.env`, which is git-ignored. Never commit it.
- Treat the token like a password. Revoke it any time from your Atlassian
  account security page.
- The scripts send data only to your configured `JIRA_BASE_URL`.
