# PIR — Project Initiation Request

A single-page browser tool (`pir.html`) to plan project resource allocation and
submit a **Project Initiation Request** to the Jira Service Desk. You define the
project, the total hours per role, and the people with their weekly allocation;
the tool computes every derived value, generates the CSV attachment, a shareable
link, and can submit directly to Jira.

## Files

- **`pir.html`** — the tool. Open it in a browser (locally or served).
- **`submit-pir.js`** — the submit widget used by `pir.html`.
- **`server/server.py`** — local backend for the Jira submission (OAuth + the
  `/api/submit` endpoint). See `server/README.md`.
- **`ALLOCATION-RULES.md`** / **`ALLOCATION-RULES-PT.md`** — the allocation rules
  the Suggest feature applies (English / Portuguese).
- Favicons + `site.webmanifest` — icons.

## How it works

1. **Project** — name, start date, duration (weeks). The end date is derived.
2. **Breakdown per role (hours)** — enter the hours per role (10 roles visible,
   5 more behind a toggle).
3. **✨ Suggest allocation** — spreads the breakdown hours across the weeks into
   person-lines, following the rules in `ALLOCATION-RULES.md` (per-role people
   caps, weekly caps, Business Analyst front-loading, manager top-ups, etc.).
   You can also add/edit people manually.
4. **People grid** — per person: Role, Allocation Type, Suggested Resource,
   Staffing Validation Status, Preferred Area (mandatory), Preferred Seniority,
   and the weekly hours. Add/remove weeks and people inline.
5. **Download CSV** — exports the "Request" layout (dates in ISO `yyyy-mm-dd`).
6. **Share** — encodes the whole plan in a URL (`#id=...&d=...`) that re-opens
   the exact plan with no server.
7. **Submit PIR** — posts to the Jira Service Desk via the local backend; when
   opened from `file://` it falls back to opening the Jira portal and
   downloading the CSV.

## Running locally

Open `pir.html` directly in a browser for planning and CSV/export. For the
**Submit PIR** flow (Jira), run the local backend and open the served page:

```bash
cd server
python3 server.py            # serves http://localhost:8723/pir.html
```

Configuration (service desk / request type IDs, field IDs, OAuth) lives in the
backend; see `server/README.md`. No third-party Python dependencies beyond the
standard library (the backend uses `certifi` for TLS).

## Notes

- The CSV is already fully computed — if the portal needs `.xlsx`, open it in
  Excel or Google Sheets and save as `.xlsx`.
- Allocation rules are documented (and kept in sync with the code) in
  `ALLOCATION-RULES.md` and `ALLOCATION-RULES-PT.md`.
