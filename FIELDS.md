# Change Request (CR) — Portal Field Reference

These are the fields shown on the portal request type
(`portal/2065 … create/2932`). The portal shows **labels**; the REST API needs
the internal **field IDs** and, for dropdowns, the **option IDs**.

> Run `./discover-fields.sh` to get the real `fieldId` for each label below and
> the valid option IDs for the Yes/No and dropdown fields, then fill those into
> `request-fields.json`. Until then, the IDs here are placeholders.

## Required fields (marked * on the portal)

| Label | Type | Notes |
| --- | --- | --- |
| Summary * | text | One-line title |
| Will this CR fix the problem? * | select | Yes / No |
| Is this an avoidable Concession? * | select | Yes / No |
| Certinia Project URL * | text/url | |
| Certinia Project Name * | text | |
| Region (Project) * | select | |
| Project Forecast Page * | text/url | |
| Current Project Due Date * | date | format e.g. 14/Sep/26 |
| New Estimated Due Date * | date | format e.g. 14/Sep/26 |
| Budget Exhaustion Date * | date | when current budget is exhausted |
| Project Manager * | user | name or email |
| Engineering Manager * | user | name or email |
| Risk & AI Manager * | user | name or email |
| Allocation plan * | attachment | **see limitation below** |

## Optional fields

| Label | Type | Notes |
| --- | --- | --- |
| CR Justification or Reason | textarea | Root Cause / why needed / implication of not doing / lesson learned |
| Additional Scope? | text/select | |
| Salesforce Opportunity ID | text | mandatory for WAR |
| Total Remaining Hours | number | |
| Total Number of additional hours required | number | |
| Total Number of additional hours being requested | number | |
| Leakage Hours - Client-induced Loss or Delay | number | |
| Leakage Hours - Executive Commitment | number | |
| Leakage Hours - Force Majeure | number | |
| Leakage Hours - Poor Deal Construction | number | |
| Leakage Hours - Quality or Availability of Personnel | number | |
| Leakage Hours - Variances to Team Estimates | number | |
| Leakage Hours - Variances to Contract | number | |
| Leakage Hours - Product Quality Index (PQI) | number | |

## Known limitations

- **Attachment (Allocation plan):** the create-request call cannot include a
  file directly. The Service Desk API requires a two-step flow — upload with
  `POST /rest/servicedeskapi/servicedesk/{id}/attachTemporaryFile`, then attach
  the returned temp id. If the field is mandatory, the request may be rejected
  when submitted purely via API without it. Confirm the behaviour with a
  `--dry-run` and a real test.
- **User fields** (Project/Engineering/Risk & AI Manager) usually need the
  user's Atlassian **accountId**, not a display name. `discover-fields.sh` will
  show the expected format.
- **Select fields** (Yes/No, Region) need the **option id**, not the label.

Allocation plan template (for reference):
<https://docs.google.com/spreadsheets/d/1OmeNqtrbbc2cE83Vvp5Yl-qilbuYiW28_EMX3QeeloQ/edit?gid=0#gid=0>
