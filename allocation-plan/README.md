# Allocation Plan Generator

Generates the Project Plan / Allocation Plan CSV required as the mandatory
attachment on the Change Request (CR) portal. You provide a small input CSV
with the project header and each resource's weekly allocation; the generator
computes every derived value so the output matches the official spreadsheet.

## Three ways to build a plan

1. **`generate_plan.py`** — CLI, takes an input CSV, writes the plan CSV.
2. **`index.html`** — browser form for manual weekly entry; live totals; CSV
   download. Open the file directly, no server needed.
3. **`planner.html`** — browser **auto-planner**: declare total hours, roles,
   capacity, city and PTO; it spreads the allocation across the timeline until
   the hours run out, reducing weeks for Portugal holidays (national + Lisbon /
   Porto / Coimbra municipal) and PTO, auto-covering PTO with a same-role
   teammate, and filling the final week to hit the cap exactly.

## Run (CLI)

```bash
python3 generate_plan.py input.csv -o plan.csv
# or print to screen:
python3 generate_plan.py input.csv
```

No dependencies — Python 3 standard library only.

## Input format

The input CSV has three tagged sections (see `input.example.csv`):

```
[HEADER]
project_name,Paysafe | RMA - Billable
start_date,05/01/2026        # dd/mm/yyyy
end_date,31/08/2026
cost_tracker_id,a6eW50000000QlhIAE

[RESOURCES]
Name Suggestion,ROLE,PREFERRED ALLOCATION AREA,PREFERRED SENIORITY,05/01,12/01,...
,Project Manager,EMEA,Senior Professional,2,2,...

[BPE]
PM,512      # optional: BPE hours per PIR code, from team estimation
DS,440
```

- **Weekly columns**: the header row of `[RESOURCES]` uses `dd/mm` week labels.
  Only the weeks you fill are counted; blank = not allocated (not zero).
- **BPE** values are the hours you (as PM) received from the team estimation.
  They are inputs, not calculated.

## Calculations

| Output | Rule |
| --- | --- |
| Days per role | sum of the row's weekly values |
| Hours per role | Days × 8 (hours/day) |
| FTE Average | `AVERAGE(active weeks) / 5` — blanks excluded (matches `=AVERAGE(...)/5`) |
| TOTAL row | column sums of Days and Hours |
| PIR Days/Hours | grid rows grouped by role into PIR codes (see mapping) |
| AI Comment | planned Hours `<` BPE → "hours missing"; `>` BPE → "exceed"; equal → blank |
| Total Values Match? | grid TOTAL hours `==` PIR total hours → TRUE / FALSE |

### Role → PIR mapping

| PIR code | Grid roles |
| --- | --- |
| PM | Project Manager |
| DM | Delivery Manager |
| DS | Data Scientist, Data Analyst |
| RiskC | Risk Consultant, Risk&AI Manager |
| BA | Business Analyst |
| ENG (TS) | Software Engineer, Technical Lead, Solution Architect, Engineering Manager |

## Validation warnings

Printed to stderr (they don't stop generation):

- weekly value above 4 days/line (split across resources instead)
- weekly value not a multiple of 0.25

## Notes

- The output is CSV. If the portal needs `.xlsx`, open the CSV in Excel or
  Google Sheets and save as `.xlsx` — the values are already computed, so no
  formulas are required.
- Verified to reproduce the official example's numbers exactly.
