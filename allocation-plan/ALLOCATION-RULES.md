# Role Allocation Rules — PIR

> This file documents **all allocation rules** that `pir.html` applies in the
> **✨ Suggest allocation** feature and when filling the people grid. It is the
> human-readable source of truth, kept in sync with `allocation-plan/pir.html`.
>
> Portuguese version: [`ALLOCATION-RULES-PT.md`](ALLOCATION-RULES-PT.md)
>
> Last updated: 2026-09-14 (per-role rules; 13 roles; unallocated-hours warning; Preferred Area/Seniority dropdowns; region-gated holiday-reduced weeks + area auto-fill)

---

## Global rules (apply to every role)

| Rule | Value | Notes |
|------|-------|-------|
| Weekly allocation unit | **hours/week** | The grid is filled in hours per week. |
| Minimum per person/week | **2 h** | An allocated person never goes below 2 h in a week they work. |
| Maximum per person/week | **32 h** | Global cap (= 4 days). Some roles have a lower cap (see per role). |
| Increment (step) | **2 h** | Values go up/down in 2-hour steps. |
| Hours per day | **8 h** | Converts hours ⇄ days (Total Days = Total Hours ÷ 8). |
| Full week | **5 days (40 h)** | Basis for the FTE calculation. |
| Duration | **N weeks** (*Duration* field) | Allocation is spread **flat** across the N weeks, starting at the *Start date*. The *End date* is derived. |
| Never exceeds the breakdown | ✔️ | The suggestion never allocates **more** hours than the role's breakdown. |
| Hours that do not fit | **not allocated + warning** | Surplus hours are **left unassigned** and a **warning** is shown in the *People* section naming the role and the hours left over. |
| Holiday-reduced week | **cap × 80% (EMEA/GDC/Partner only)** | A week containing a Portugal public holiday loses one of five working days, so **every role's weekly cap is reduced to 80%** that week (floored to the 2h step): e.g. 32 h → 24 h, 16 h → 12 h, 8 h → 6 h. These weeks are lightly highlighted (amber) in the grid. Uses PT national holidays (fixed dates + Good Friday, Easter, Corpus Christi). **Applies only when the project Region is EMEA, GDC or Partner** (PT-staffed). APAC/LATAM/NAMER: no reduction, no highlight. |
| Project Region | top of the form | A **Region** dropdown (same options as Preferred Area) sits next to Project name. It drives the holiday rule above and pre-fills each suggested row's Preferred Area (editable afterwards). |

### Internal spread (how the suggestion distributes per person)

- The internal spread works in **hours** on a 2-hour grid (`MIN_H = 2`, `STEP_H = 2`).
- People per role = `ceil( role_hours / (weekly_cap × N) )`, limited by the role's
  **maximum number of people**.
- The distribution is **flat** across the N weeks (extra 2 h units are placed one
  per week from the start), respecting the role's weekly cap.

### Staffing Validation Status (cross-cutting rule)

- Options: `Pre-Approved by GDC Mgmt (Ready to Book)` · `PM Preference (Pending GDC Approval)` · `Open Demand (WFM to Source)`
- **If *Suggested Resource (Optional)* is empty → the status is forced to
  `Open Demand (WFM to Source)`** (the select is disabled while in automatic mode).
- Every auto-suggested line comes **without a resource** → they enter as **Open Demand**.

### Allocation Type (cross-cutting rule)

- Options: `add` · `remove` · `split` · `swap` — one per line, **default `add`**.

### Preferred Area / Preferred Seniority (cross-cutting rule)

- **Preferred Area** (dropdown, **mandatory before Submit**): `APAC` · `EMEA` · `LATAM` · `NAMER` · `GDC` · `Partner`.
  Submit is blocked with a warning if any allocated row (one with weekly hours) has no area.
  Suggest pre-fills it from the project **Region**; it stays editable per row.
- **Preferred Seniority** (dropdown, **optional**): `Associate` · `Professional` · `Senior Professional` · `Advanced` · `Expert` · `Principal` · `Senior Principal` · `Manager` · `Senior Manager` · `Director` · `Senior Director`.

---

## Maximum people per role

| Role | Max people |
|------|:----------:|
| Data Scientist | **up to 3** |
| Software Engineer | **up to 3** |
| All other roles | **1** |

---

## Per-role rules

Legend: **Visible** = shown in the breakdown by default · **Expand** = behind the "+ More roles" toggle.
**IC** = Individual Contributor · **Manager** = Manager group (informational; the cap is per role).

### Delivery Manager
- Group: **Individual Contributor**
- Visibility: **Visible**
- Max people: **1**
- Shape: **flat** allocation across the whole project.
- Time: **default 2 h/week**. If the role has spare hours it may grow up to **8 h/week**; any remainder beyond that is **not allocated**.

### Project Manager
- Group: **Individual Contributor**
- Visibility: **Visible**
- Max people: **1**
- Shape: **flat** allocation across the whole project.
- Cap: at most **50% of the time = 16 h/week**.

### Compliance Manager
- Group: **Individual Contributor**
- Visibility: **Visible**
- Max people: **1**

### Engineering Manager
- Group: **Manager**
- Visibility: **Visible**
- Max people: **1**
- Time: **default 2 h/week** (may grow up to 8 h/week; remainder not allocated).
- **Conditional:** if there are hours on **Software Engineer** and **none** on Engineering Manager →
  assign **2 h/week** to Engineering Manager, **taken from** Software Engineer.
  Otherwise, use the time defined for the role.

### Solution Architect
- Group: **Individual Contributor**
- Visibility: **Visible**
- Max people: **1**

### Software Engineer
- Group: **Individual Contributor**
- Visibility: **Visible**
- Max people: **up to 3** (typical team is 1).

### Risk & AI Manager
- Group: **Manager**
- Visibility: **Visible**
- Max people: **1**
- **Conditional:** if there are hours on **Data Scientist / Risk Consultant / Business Analyst**
  and **none** on Risk & AI Manager →
  assign **2 h/week** to Risk & AI Manager, **taken proportionally** from those roles.
  Otherwise, use the time defined for the role.

### Data Scientist
- Group: **Individual Contributor**
- Visibility: **Visible**
- Max people: **up to 3** (typical team is 1).

### Business Analyst
- Group: **Individual Contributor**
- Visibility: **Visible**
- Max people: **1**
- Shape: the work is concentrated in the **first 30% of the project weeks**
  (e.g. a 9-week project → work done in 3 weeks).

### Risk Consultant
- Group: **Individual Contributor**
- Visibility: **Visible**
- Max people: **1**

### Project Director
- Group: **Manager**
- Visibility: **Expand** (hidden by default)
- Max people: **1**

### Quality Assurance Engineer
- Group: **Individual Contributor**
- Visibility: **Expand** (hidden by default)
- Max people: **1**

### Delivery Consultant
- Group: **Individual Contributor**
- Visibility: **Expand** (hidden by default)
- Max people: **1**

---

## Quick summary (table)

| Role | Group | Visibility | Max people | Weekly cap | Special shape |
|------|-------|------------|:----------:|------------|---------------|
| Delivery Manager | IC | Visible | 1 | 2→8 h | flat; default 2 h |
| Project Manager | IC | Visible | 1 | 16 h | flat |
| Compliance Manager | IC | Visible | 1 | 32 h | — |
| Engineering Manager | Manager | Visible | 1 | 2→8 h | default 2 h; conditional vs Software Engineer |
| Solution Architect | IC | Visible | 1 | 32 h | — |
| Software Engineer | IC | Visible | up to 3 | 32 h | — |
| Risk & AI Manager | Manager | Visible | 1 | 32 h | conditional vs DS/Risk Consultant/BA |
| Data Scientist | IC | Visible | up to 3 | 32 h | — |
| Business Analyst | IC | Visible | 1 | 32 h | first 30% of the weeks |
| Risk Consultant | IC | Visible | 1 | 32 h | — |
| Project Director | Manager | Expand | 1 | 32 h | — |
| Quality Assurance Engineer | IC | Expand | 1 | 32 h | — |
| Delivery Consultant | IC | Expand | 1 | 32 h | — |

---

## Implementation notes / to validate

- The conditional rules (Risk & AI Manager and Engineering Manager receiving
  2 h/week taken from other roles) are **under test** — to be tuned based on
  real-world results.
- "Taken proportionally" (Risk & AI Manager): the 2 h/week × N weeks are
  subtracted from the total of the dependent roles, split by each one's weight.
