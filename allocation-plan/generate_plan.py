#!/usr/bin/env python3
# =============================================================
# generate_plan.py
# Builds a Project Plan / Allocation Plan CSV for the Jira CR,
# computing every derived value so it matches the official
# spreadsheet template.
#
# Input : a simple CSV (see input.example.csv) describing the
#         project header, one row per resource with weekly
#         allocation values, and optional BPE hours per PIR code.
# Output: the full plan CSV with all calculations filled in.
#
# Usage:
#   python3 generate_plan.py input.csv > plan.csv
#   python3 generate_plan.py input.csv -o plan.csv
#
# No third-party dependencies — standard library only.
# =============================================================

import sys
import csv
import argparse
from datetime import datetime, timedelta

HOURS_PER_DAY = 8
FULL_WEEK_DAYS = 5            # FTE basis: AVERAGE(active weeks) / 5
MIN_ALLOC = 0.25
MAX_ALLOC_PER_LINE = 4.0

# ROLE (as typed in the grid)  ->  PIR code
ROLE_TO_PIR = {
    "project manager":    "PM",
    "delivery manager":   "DM",
    "data scientist":     "DS",
    "data analyst":       "DS",
    "risk consultant":    "RiskC",
    "risk&ai manager":    "RiskC",
    "risk & ai manager":  "RiskC",
    "business analyst":   "BA",
    "software engineer":  "ENG (TS)",
    "technical lead":     "ENG (TS)",
    "solution architect": "ENG (TS)",
    "engineering manager":"ENG (TS)",
}

# Order the PIR rows are displayed in
PIR_ORDER = ["DM", "PM", "DS", "RiskC", "BA", "ENG (TS)"]


def pir_code_for_role(role):
    return ROLE_TO_PIR.get(role.strip().lower())


def parse_date(s):
    s = s.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date: {s!r} (use dd/mm/yyyy)")


def week_headers(start, end):
    """Weekly column labels (dd/mm) from start to end, stepping 7 days."""
    labels, cur = [], start
    while cur <= end:
        labels.append(cur.strftime("%d/%m"))
        cur += timedelta(days=7)
    return labels


def num(x):
    """Parse a numeric cell; blank/empty -> None (blank, not zero)."""
    if x is None:
        return None
    s = str(x).strip()
    if s == "":
        return None
    return float(s)


def fmt(n):
    """Trim trailing .0 for whole numbers, keep up to 2 decimals otherwise."""
    if n == int(n):
        return str(int(n))
    return f"{n:.2f}".rstrip("0").rstrip(".")


def read_input(path):
    """
    Input CSV structure (see input.example.csv):
      Section [HEADER]:  key,value pairs (project_name, start_date, end_date, cost_tracker_id)
      Section [RESOURCES]: header row then resource rows
      Section [BPE]:  pir_code,hours pairs (optional)
    """
    header, resources, bpe = {}, [], {}
    section = None
    res_cols = None

    with open(path, newline="", encoding="utf-8-sig") as fh:
        for raw in csv.reader(fh):
            if not raw or all(c.strip() == "" for c in raw):
                continue
            tag = raw[0].strip().upper()
            if tag in ("[HEADER]", "[RESOURCES]", "[BPE]"):
                section = tag
                res_cols = None
                continue
            if section == "[HEADER]":
                header[raw[0].strip().lower()] = raw[1].strip() if len(raw) > 1 else ""
            elif section == "[RESOURCES]":
                if res_cols is None:
                    res_cols = [c.strip() for c in raw]
                else:
                    row = {res_cols[i]: (raw[i] if i < len(raw) else "")
                           for i in range(len(res_cols))}
                    resources.append(row)
            elif section == "[BPE]":
                bpe[raw[0].strip()] = num(raw[1]) if len(raw) > 1 else None
    return header, resources, bpe


def build(header, resources, bpe):
    start = parse_date(header["start_date"])
    end = parse_date(header["end_date"])
    weeks = week_headers(start, end)

    warnings = []
    rows = []          # each: dict with computed fields + weekly list
    for idx, r in enumerate(resources, start=1):
        weekly = []
        for w in weeks:
            weekly.append(num(r.get(w)))
        active = [v for v in weekly if v is not None]

        # validation
        for v in active:
            if v > MAX_ALLOC_PER_LINE:
                warnings.append(f"Row {idx} ({r.get('ROLE','?')}): weekly {fmt(v)} exceeds max {MAX_ALLOC_PER_LINE}/line.")
            if v != 0 and (round(v / MIN_ALLOC) != v / MIN_ALLOC):
                warnings.append(f"Row {idx} ({r.get('ROLE','?')}): weekly {fmt(v)} is not a multiple of {MIN_ALLOC}.")

        days = sum(active)
        hours = days * HOURS_PER_DAY
        fte = (sum(active) / len(active) / FULL_WEEK_DAYS) if active else None
        rows.append({
            "name": r.get("Name Suggestion", ""),
            "days": days,
            "hours": hours,
            "fte": fte,
            "role": r.get("ROLE", ""),
            "area": r.get("PREFERRED ALLOCATION AREA", ""),
            "seniority": r.get("PREFERRED SENIORITY", ""),
            "weekly": weekly,
        })

    total_days = sum(x["days"] for x in rows)
    total_hours = sum(x["hours"] for x in rows)

    # PIR aggregation
    pir_days = {code: 0.0 for code in PIR_ORDER}
    for x in rows:
        code = pir_code_for_role(x["role"])
        if code:
            pir_days[code] += x["days"]
        elif x["role"].strip():
            warnings.append(f"Role {x['role']!r} has no PIR mapping — excluded from PIR totals.")

    pir_rows = []
    pir_total_days = 0.0
    pir_total_hours = 0.0
    for code in PIR_ORDER:
        d = pir_days[code]
        h = d * HOURS_PER_DAY
        pir_total_days += d
        pir_total_hours += h
        b = bpe.get(code)
        comment = ""
        if b is not None:
            if h < b:
                comment = "hours missing"
            elif h > b:
                comment = "exceed"
        pir_rows.append({"code": code, "days": d, "hours": h,
                         "bpe": b, "comment": comment})

    match = "TRUE" if round(total_hours, 6) == round(pir_total_hours, 6) else "FALSE"

    return {
        "start": start, "end": end, "weeks": weeks,
        "rows": rows, "total_days": total_days, "total_hours": total_hours,
        "pir_rows": pir_rows, "pir_total_days": pir_total_days,
        "pir_total_hours": pir_total_hours, "match": match,
        "warnings": warnings,
    }


def write_csv(header, plan, out):
    w = csv.writer(out)
    weeks = plan["weeks"]
    blanks = lambda n: [""] * n

    # ---- header block ----
    w.writerow([header.get("project_name", ""), "", "", "(Mandatory fields)",
                "Project Start date", plan["start"].strftime("%d/%m/%Y")])
    w.writerow(["", "", "", "", "Project End date", plan["end"].strftime("%d/%m/%Y")])
    w.writerow(["Cost Tracker ID", header.get("cost_tracker_id", ""), "", "",
                "Hours per day", HOURS_PER_DAY])
    w.writerow([])
    w.writerow(["", "", "", "", "", "", "", "Weekly Resourcing Need"])
    w.writerow(["", "", "", "(Mandatory fields)", "", "", "", plan["start"].year])

    # ---- grid header ----
    w.writerow(["Name Suggestion", "Days per role", "Hours per role", "FTE Average",
                "ROLE", "PREFERRED ALLOCATION AREA", "PREFERRED SENIORITY"] + weeks)

    # ---- resource rows ----
    for x in plan["rows"]:
        fte = "#DIV/0!" if x["fte"] is None else f"{x['fte']:.2f}"
        weekly = ["" if v is None else fmt(v) for v in x["weekly"]]
        w.writerow([x["name"], fmt(x["days"]), f"{x['hours']:.2f}", fte,
                    x["role"], x["area"], x["seniority"]] + weekly)

    # ---- TOTAL row ----
    w.writerow(["TOTAL", fmt(plan["total_days"]), fmt(plan["total_hours"])])
    w.writerow([])
    w.writerow([])

    # ---- PIR section ----
    w.writerow(["", "", "(Use below values in the PIR)", "(Mandatory field)"])
    w.writerow(["Time Loging", "Days", "Hours", "BPE Hours per role", "AI Comment"])
    for p in plan["pir_rows"]:
        bpe = "" if p["bpe"] is None else fmt(p["bpe"])
        w.writerow([p["code"], fmt(p["days"]), fmt(p["hours"]), bpe, p["comment"]])
    w.writerow(["Total", fmt(plan["pir_total_days"]), fmt(plan["pir_total_hours"])])
    w.writerow(["Total Values Match?", plan["match"]])


def main():
    ap = argparse.ArgumentParser(description="Generate a CR allocation-plan CSV.")
    ap.add_argument("input", help="input CSV describing header + resources + BPE")
    ap.add_argument("-o", "--output", help="output CSV path (default: stdout)")
    args = ap.parse_args()

    header, resources, bpe = read_input(args.input)
    plan = build(header, resources, bpe)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            write_csv(header, plan, fh)
        dest = args.output
    else:
        write_csv(header, plan, sys.stdout)
        dest = "stdout"

    for wmsg in plan["warnings"]:
        sys.stderr.write(f"⚠️  {wmsg}\n")
    sys.stderr.write(
        f"✓ Plan written to {dest} — grid {fmt(plan['total_hours'])}h vs "
        f"PIR {fmt(plan['pir_total_hours'])}h → Match? {plan['match']}\n")


if __name__ == "__main__":
    main()
