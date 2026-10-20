# PIR Submission Server

A small local backend (Python standard library only) that lets the web tools
submit a **Project Initiation Request** to the Jira Service Desk, including the
generated CSV as an attachment.

It exists because a browser **cannot** call the Jira API directly from a
`file://` page or another origin (CORS), and cannot safely hold OAuth secrets.
The server serves the HTML tools over `http://localhost` and does the
authenticated API calls on their behalf.

## What it provides

- Serves `allocation-plan/` at `http://localhost:8723` (so `/api/*` works).
- `GET /auth/login` → Atlassian OAuth consent → `GET /auth/callback`.
- `GET /api/me` → who is signed in (401 if not).
- `GET /api/fields` → the request type's fields (handy for debugging).
- `POST /api/submit` → uploads the CSV (`attachTemporaryFile`) then creates the
  request (`POST /rest/servicedeskapi/request`).

## Run it

```bash
cd allocation-plan/server
python3 server.py
# then open http://localhost:8723/ (index.html)
```

(`certifi` is used if present, for TLS on macOS python.org Python. The project
already installs it for the calendar feature.)

## Config (../../.env)

Reads the project `.env`. Relevant keys (see `.env.example`):

| Key | Purpose |
| --- | --- |
| `PORT` | server port (default 8723) |
| `SERVICE_DESK_ID_PIR` | API service desk id — **2067** (portal shows 2065) |
| `REQUEST_TYPE_ID_PIR` | request type — **2866** (Project Initiation Request) |
| `FORECAST_FIELD_ID` | `customfield_19943` (Project Forecast Page) |
| `ATLASSIAN_CLIENT_ID` / `ATLASSIAN_CLIENT_SECRET` | OAuth app credentials |
| `REDIRECT_URI` | must match the app's registered callback |
| `JIRA_EMAIL` / `JIRA_API_TOKEN` | dev-only Basic-auth fallback |

## Field mapping (discovered from the live request type)

| Portal label | API field | Required |
| --- | --- | --- |
| Summary | `summary` | yes |
| Request Justification | `description` | yes |
| Project Forecast Page | `customfield_19943` | yes (we send `#`) |
| Allocation plan | `attachment` | yes (the CSV) |
| Certinia Project ID | `customfield_19679` | no (ignored) |

## OAuth setup (for real, SSO-based submission)

1. Create an app at <https://developer.atlassian.com/console/myapps/>.
2. Add the **Jira Service Management** API.
3. Add scopes: `read:servicedesk-request`, `write:servicedesk-request`,
   `read:jira-user`, `offline_access`.
4. Set the callback URL to your `REDIRECT_URI`
   (e.g. `http://localhost:8723/auth/callback` for local dev, or your HTTPS
   server URL in production).
5. Put the client id/secret in `.env`.

On the first submit, the user is redirected to the company Atlassian login;
after consent they return to the app and the request is submitted.

## Status / limitations (honest notes)

- **Not yet runnable end-to-end** until an OAuth app is registered (needs an
  Atlassian admin) and, for sharing with others, the server is hosted on HTTPS.
- A **Basic-auth fallback** (your `.env` API token) is included so you can test
  the submit flow locally today, without OAuth. It acts as *you* — local use only.
- The session is in-memory and single-user — fine for local/dev, not for a
  shared deployment. A real deployment needs per-user sessions and token refresh.
- `.env` (with secrets) is git-ignored; only `.env.example` is committed.
