#!/usr/bin/env python3
# =============================================================
# pto_from_ics.py
# Extracts a person's PTO ("Out of Office") ranges from an
# iCalendar (.ics) feed and prints them in the format the
# allocation planner expects:  dd/mm/yyyy-dd/mm/yyyy, ...
#
# Rules:
#   - Only whole-day "Out of Office" events count. Events tagged
#     "- Afternoon" (half days) are ignored (treated as working).
#   - iCalendar DTEND is exclusive for all-day events, so the last
#     day off is DTEND - 1 day. This is corrected automatically.
#   - Name matching is "contains all words": every word you pass
#     must appear (case-insensitive) in the calendar person's name.
#     e.g. "Clara Pereira" matches "Clara Gomes Ramos Pereira".
#
# Usage:
#   # from a URL:
#   python3 pto_from_ics.py --url "https://.../cal.ics" "Miguel Pereira"
#   # from a local file (download it first with curl):
#   python3 pto_from_ics.py --file cal.ics "Miguel Pereira" "Clara Pereira"
#   # list everyone in the feed:
#   python3 pto_from_ics.py --file cal.ics --list
#
# No third-party dependencies. Fetch uses urllib (stdlib), which
# ignores the server's content-type (the HiBob feed mislabels the
# .ics as application/octet-stream).
# =============================================================

import sys
import re
import argparse
from datetime import datetime, timedelta
from urllib.request import urlopen, Request

OOO_SUFFIX = "- Out of Office"
HALF_DAY_MARKERS = ("- Afternoon", "- Morning")


def load_ics(url=None, path=None):
    if url:
        req = Request(url, headers={"User-Agent": "pto-from-ics/1.0"})
        with urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", errors="replace")
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def parse_events(raw):
    # Unfold folded lines (continuation lines start with space/tab).
    raw = re.sub(r"\r?\n[ \t]", "", raw)
    events, cur = [], None
    for ln in raw.split("\n"):
        if ln.startswith("BEGIN:VEVENT"):
            cur = {}
        elif ln.startswith("END:VEVENT"):
            if cur is not None:
                events.append(cur)
            cur = None
        elif cur is not None and ":" in ln:
            key, val = ln.split(":", 1)
            cur[key.split(";")[0]] = val.strip()
    return events


def parse_dt(v):
    v = (v or "").strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%dT%H%M%S", "%Y%m%d"):
        try:
            return datetime.strptime(v, fmt)
        except ValueError:
            continue
    return None


def person_name(summary):
    """'Miguel Pereira - Out of Office' -> 'Miguel Pereira'."""
    s = summary
    if OOO_SUFFIX in s:
        s = s.split(OOO_SUFFIX)[0]
    return s.strip(" -")


def is_half_day(summary):
    return any(m in summary for m in HALF_DAY_MARKERS)


def matches(query, cal_name):
    """contains-all-words, case-insensitive."""
    qwords = [w for w in re.split(r"\s+", query.lower().strip()) if w]
    target = cal_name.lower()
    return all(w in target for w in qwords)


def list_people(events):
    from collections import Counter
    c = Counter()
    for e in events:
        su = e.get("SUMMARY", "")
        if OOO_SUFFIX in su and not is_half_day(su):
            c[person_name(su)] += 1
    return c


def ranges_for(events, query):
    out = []
    for e in events:
        su = e.get("SUMMARY", "")
        if OOO_SUFFIX not in su or is_half_day(su):
            continue
        if not matches(query, person_name(su)):
            continue
        ds = parse_dt(e.get("DTSTART", ""))
        de = parse_dt(e.get("DTEND", ""))
        if not ds:
            continue
        # iCal DTEND is exclusive for all-day events -> last day = DTEND - 1
        last = (de - timedelta(days=1)) if de else ds
        if last < ds:
            last = ds
        out.append((ds.date(), last.date()))
    # merge/sort
    out.sort()
    return out


def fmt_range(s, e):
    f = lambda d: d.strftime("%d/%m/%Y")
    return f"{f(s)}-{f(e)}"


def main():
    ap = argparse.ArgumentParser(description="Extract PTO ranges from an ICS feed.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="ICS feed URL")
    src.add_argument("--file", help="local .ics file")
    ap.add_argument("--list", action="store_true", help="list all people in the feed")
    ap.add_argument("names", nargs="*", help="one or more names to extract")
    args = ap.parse_args()

    raw = load_ics(url=args.url, path=args.file)
    events = parse_events(raw)

    if args.list:
        people = list_people(events)
        print(f"{len(people)} people with whole-day OOO events:\n")
        for name, n in sorted(people.items()):
            print(f"  {n:3}  {name}")
        return

    if not args.names:
        ap.error("provide at least one name, or use --list")

    for q in args.names:
        rngs = ranges_for(events, q)
        # figure out who matched, for a friendly header
        matched = sorted({person_name(e.get("SUMMARY", ""))
                          for e in events
                          if OOO_SUFFIX in e.get("SUMMARY", "")
                          and not is_half_day(e.get("SUMMARY", ""))
                          and matches(q, person_name(e.get("SUMMARY", "")))})
        print(f"\n# {q}")
        if not matched:
            print("  (no match found)")
            continue
        if len(matched) > 1:
            print(f"  ⚠ matched {len(matched)} people: {', '.join(matched)}")
        else:
            print(f"  matched: {matched[0]}")
        if not rngs:
            print("  (no PTO)")
        else:
            print("  " + ", ".join(fmt_range(s, e) for s, e in rngs))


if __name__ == "__main__":
    main()
