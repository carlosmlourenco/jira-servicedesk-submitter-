#!/usr/bin/env python3
# =============================================================
# plan_from_calendar.py
# End-to-end allocation planner:
#   1. reads a JSON plan config (project + resources + ICS source)
#   2. fetches the calendar and auto-fills each resource's PTO by name
#   3. spreads the total-hours budget across the timeline, respecting
#      Portugal holidays (national + Lisbon/Porto/Coimbra municipal),
#      PTO, PM-as-secondary, auto-created backups, filling to the cap
#   4. writes the plan CSV in the CR template format
#
# This mirrors planner.html exactly, with PTO sourced from the calendar.
#
# Usage:
#   python3 plan_from_calendar.py plan-config.json -o plan.csv
#   python3 plan_from_calendar.py plan-config.json --file cal.ics -o plan.csv
#
# Config keys (see plan-config.example.json):
#   project_name, start_date (dd/mm/yyyy), end_date, cost_tracker_id,
#   total_hours, ics_url (optional if --file given),
#   resources: [{name, role, capacity, city, backup?, pto?}]
# PTO is normally pulled from the calendar; an explicit "pto" list on a
# resource (["dd/mm/yyyy-dd/mm/yyyy", ...]) is merged in as well.
#
# No third-party dependencies (stdlib only).
# =============================================================

import sys, os, re, json, csv, argparse
from datetime import datetime, timedelta, date
from urllib.request import urlopen, Request

HOURS_PER_DAY=8; FULL_WEEK=5; MIN=0.25; MAXLINE=4; PM_RATE=0.25
PIR_ORDER=["DM","PM","DS","RiskC","BA","ENG (TS)"]
ROLE_TO_PIR={"project manager":"PM","delivery manager":"DM","data scientist":"DS",
 "data analyst":"DS","risk consultant":"RiskC","risk&ai manager":"RiskC","risk & ai manager":"RiskC",
 "business analyst":"BA","software engineer":"ENG (TS)","technical lead":"ENG (TS)",
 "solution architect":"ENG (TS)","engineering manager":"ENG (TS)"}
MUNICIPAL={"Lisbon":(6,13),"Porto":(6,24),"Coimbra":(7,4)}
OOO_SUFFIX="- Out of Office"; HALF_DAY=("- Afternoon","- Morning")

# ---------------- .env ----------------
def load_env_value(key):
    """Read a single KEY from the project .env (one dir up), if present.
    Minimal parser: KEY=value or KEY="value"; ignores comments/blank lines."""
    env_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    env_path=os.path.normpath(env_path)
    if not os.path.isfile(env_path):
        return None
    try:
        for line in open(env_path, encoding="utf-8"):
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k,v=line.split("=",1)
            if k.strip()==key:
                v=v.strip().strip('"').strip("'")
                return v or None
    except OSError:
        return None
    return None

# ---------------- ICS ----------------
def load_ics(url=None, path=None):
    if path: return open(path, encoding="utf-8", errors="replace").read()
    req=Request(url, headers={"User-Agent":"plan-from-calendar/1.0"})
    with urlopen(req, timeout=30) as r: return r.read().decode("utf-8","replace")

def parse_events(raw):
    raw=re.sub(r"\r?\n[ \t]","",raw); events=[]; cur=None
    for ln in raw.split("\n"):
        if ln.startswith("BEGIN:VEVENT"): cur={}
        elif ln.startswith("END:VEVENT"):
            if cur is not None: events.append(cur)
            cur=None
        elif cur is not None and ":" in ln:
            k,v=ln.split(":",1); cur[k.split(";")[0]]=v.strip()
    return events

def _dt(v):
    v=(v or "").strip()
    for f in ("%Y%m%dT%H%M%SZ","%Y%m%dT%H%M%S","%Y%m%d"):
        try: return datetime.strptime(v,f)
        except ValueError: pass
    return None

def person_name(su):
    return su.split(OOO_SUFFIX)[0].strip(" -") if OOO_SUFFIX in su else su.strip(" -")

def is_half(su): return any(m in su for m in HALF_DAY)

def name_matches(query, cal_name):
    qs=[w for w in re.split(r"\s+", query.lower().strip()) if w]
    return all(w in cal_name.lower() for w in qs)

def pto_ranges_for(events, query):
    out=[]
    for e in events:
        su=e.get("SUMMARY","")
        if OOO_SUFFIX not in su or is_half(su): continue
        if not name_matches(query, person_name(su)): continue
        ds=_dt(e.get("DTSTART","")); de=_dt(e.get("DTEND",""))
        if not ds: continue
        last=(de-timedelta(days=1)) if de else ds
        if last<ds: last=ds
        out.append((ds.date(), last.date()))
    out.sort(); return out

# ---------------- dates / holidays ----------------
def parse_dmy(s):
    p=s.strip().split("/"); 
    if len(p)!=3: return None
    d,m,y=map(int,p); y=y+2000 if y<100 else y
    return date(y,m,d)

def easter(y):
    a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3
    h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7;m=(a+11*h+22*l)//451
    mon=(h+l-7*m+114)//31;day=((h+l-7*m+114)%31)+1
    return date(y,mon,day)

def national(y):
    out=[date(y,m,d) for m,d in [(1,1),(4,25),(5,1),(6,10),(8,15),(10,5),(11,1),(12,1),(12,8),(12,25)]]
    eas=easter(y); out+= [eas-timedelta(days=2), eas, eas+timedelta(days=60)]
    return out

def city_holidays(city, years):
    out=[]
    for y in years:
        out+=national(y)
        if city in MUNICIPAL:
            m,d=MUNICIPAL[city]; out.append(date(y,m,d))
    return set(out)

def monday_of(d): return d - timedelta(days=d.weekday())

def build_weeks(s,e):
    out=[]; cur=monday_of(s); em=monday_of(e)
    while cur<=em: out.append(cur); cur+=timedelta(days=7)
    return out

def weekday_count_in_week(mon, dateset_or_ranges, is_ranges=False):
    c=0
    for i in range(5):
        day=mon+timedelta(days=i)
        if is_ranges:
            if any(r[0]<=day<=r[1] for r in dateset_or_ranges): c+=1
        else:
            if day in dateset_or_ranges: c+=1
    return c

# ---------------- spread ----------------
def weekly_capacity(res, weeks, holset):
    caps=[]
    for w in weeks:
        hol=weekday_count_in_week(w, holset)
        pto=weekday_count_in_week(w, res["pto"], is_ranges=True)
        if pto>=5: caps.append((0.0,hol,pto)); continue
        capd=res["capacity"]-hol-pto
        if capd<=0: caps.append((0.0,hol,pto)); continue
        if capd<MIN: capd=MIN
        capd=round(capd/MIN)*MIN
        caps.append((capd,hol,pto))
    return caps

def r025(x):
    x=round(x/MIN)*MIN
    return x

def build_plan(cfg, events):
    start=parse_dmy(cfg["start_date"]); end=parse_dmy(cfg["end_date"])
    weeks=build_weeks(start,end)
    years={w.year for w in weeks} | {end.year}
    cap=float(cfg["total_hours"])
    notes=[]

    # resolve resources; pull PTO from calendar by name (+ merge explicit pto)
    resources=[]
    for r in cfg["resources"]:
        pto=[]
        if events is not None:
            pto=pto_ranges_for(events, r["name"])
        for rng in r.get("pto",[]) or []:
            a,b=(rng.split("-")+[None])[:2]
            s=parse_dmy(a); e2=parse_dmy(b or a)
            if s and e2: pto.append((s,e2))
        pto=sorted(set(pto))
        resources.append({"name":r["name"],"role":r["role"],"capacity":float(r["capacity"]),
                          "city":r.get("city","Lisbon"),"backup":r.get("backup","") or "",
                          "pto":pto,"coverFor":None})

    hands=[r for r in resources if ROLE_TO_PIR.get(r["role"].lower())!="PM" and r["capacity"]>0]
    pms=[r for r in resources if ROLE_TO_PIR.get(r["role"].lower())=="PM"]

    # auto-spawn backups
    for prim in [h for h in list(hands) if h["backup"]]:
        bname=prim["backup"]
        if any(x["name"].lower()==bname.lower() for x in hands):
            notes.append(f'Backup "{bname}" already a resource — using existing row.'); continue
        bpto=pto_ranges_for(events, bname) if events is not None else []
        hands.append({"name":bname,"role":prim["role"],"capacity":prim["capacity"],
                      "city":prim["city"],"backup":"","pto":sorted(set(bpto)),"coverFor":prim["name"]})
        notes.append(f'Auto-created backup "{bname}" ({prim["role"]}, {prim["city"]}) covering {prim["name"]} PTO.')

    holcache={}
    def hols(city):
        if city not in holcache: holcache[city]=city_holidays(city, years)
        return holcache[city]

    capByName={h["name"]:weekly_capacity(h, weeks, hols(h["city"])) for h in hands}

    remaining=cap
    alloc={h["name"]:[0.0]*len(weeks) for h in hands}
    pmAlloc={p["name"]:[0.0]*len(weeks) for p in pms}

    for wi in range(len(weeks)):
        if remaining<=1e-9: break
        work=[]
        for h in hands:
            if h["coverFor"]:
                t=next((x for x in hands if x["name"].lower()==h["coverFor"].lower()),None)
                if not t: continue
                primPto=capByName[t["name"]][wi][2]
                if primPto<=0: continue
                dcap=min(primPto, h["capacity"]); dcap=r025(dcap)
                if dcap<MIN: dcap=MIN
            else:
                dcap=capByName[h["name"]][wi][0]
            if dcap>0: work.append((h,dcap))
        if not work: continue

        handH=sum(d*HOURS_PER_DAY for _,d in work)
        pmH=len(pms)*PM_RATE*HOURS_PER_DAY
        weekH=handH+pmH
        if weekH<=remaining+1e-9:
            for h,d in work: alloc[h["name"]][wi]=d
            for p in pms: pmAlloc[p["name"]][wi]=PM_RATE
            remaining-=weekH
        else:
            budget=remaining; pmCost=len(pms)*PM_RATE*HOURS_PER_DAY
            if pmCost<=budget:
                for p in pms: pmAlloc[p["name"]][wi]=PM_RATE
                budget-=pmCost
            totalCap=sum(d for _,d in work)
            for h,d in work:
                share=budget*(d/totalCap)
                alloc[h["name"]][wi]=round(share/HOURS_PER_DAY,4)
            remaining=0

    # assemble rows for CSV (hands then pms)
    rows=[]
    for h in hands:
        rows.append({"name":h["name"],"role":h["role"],"city":h["city"],"weekly":alloc[h["name"]]})
    for p in pms:
        rows.append({"name":p["name"],"role":p["role"],"city":p["city"],"weekly":pmAlloc[p["name"]]})

    return {"start":start,"end":end,"weeks":weeks,"rows":rows,"cap":cap,
            "allocated":cap-remaining,"notes":notes}

# ---------------- CSV ----------------
def fnum(n):
    if n is None: return ""
    r=round(n*100)/100
    return str(int(r)) if r==int(r) else str(r)

def write_csv(cfg, plan, out):
    w=csv.writer(out); weeks=[f"{d.day:02d}/{d.month:02d}" for d in plan["weeks"]]
    d2=lambda d: d.strftime("%d/%m/%Y")
    w.writerow([cfg.get("project_name",""),"","","(Mandatory fields)","Project Start date",d2(plan["start"])])
    w.writerow(["","","","","Project End date",d2(plan["end"])])
    w.writerow(["Cost Tracker ID",cfg.get("cost_tracker_id",""),"","","Hours per day",HOURS_PER_DAY])
    w.writerow([]); w.writerow(["","","","","","","","Weekly Resourcing Need"])
    w.writerow(["","","","(Mandatory fields)","","","",plan["start"].year])
    w.writerow(["Name Suggestion","Days per role","Hours per role","FTE Average","ROLE",
                "PREFERRED ALLOCATION AREA","PREFERRED SENIORITY"]+weeks)
    gd=gh=0.0; pir={c:0.0 for c in PIR_ORDER}
    for r in plan["rows"]:
        active=[v for v in r["weekly"] if v>0]
        days=sum(r["weekly"]); hours=days*HOURS_PER_DAY
        fte=(days/len(active)/FULL_WEEK) if active else None
        gd+=days; gh+=hours
        code=ROLE_TO_PIR.get(r["role"].lower())
        if code: pir[code]+=days
        w.writerow([r["name"],fnum(days),f"{hours:.2f}","#DIV/0!" if fte is None else f"{fte:.2f}",
                    r["role"],r["city"],""]+[fnum(v) if v>0 else "" for v in r["weekly"]])
    w.writerow(["TOTAL",fnum(gd),fnum(gh)]); w.writerow([]); w.writerow([])
    w.writerow(["","","(Use below values in the PIR)","(Mandatory field)"])
    w.writerow(["Time Loging","Days","Hours","BPE Hours per role","AI Comment"])
    pd=ph=0.0
    for code in PIR_ORDER:
        d=pir[code]; h=d*HOURS_PER_DAY; pd+=d; ph+=h
        w.writerow([code,fnum(d),fnum(h),"",""])
    w.writerow(["Total",fnum(pd),fnum(ph)])
    w.writerow(["Total Values Match?", "TRUE" if round(gh*1e6)==round(ph*1e6) else "FALSE"])
    return gh, ph

def main():
    ap=argparse.ArgumentParser(description="Build allocation plan CSV from a config + calendar.")
    ap.add_argument("config", help="plan config JSON")
    ap.add_argument("--file", help="local .ics file (highest priority calendar source)")
    ap.add_argument("--url", help="ICS URL (overrides config ics_url and .env HIBOB_ICS_URL)")
    ap.add_argument("-o","--output", help="output CSV path (default stdout)")
    ap.add_argument("--no-calendar", action="store_true", help="ignore calendar; use only explicit pto in config")
    args=ap.parse_args()

    cfg=json.load(open(args.config, encoding="utf-8"))
    events=None
    if not args.no_calendar:
        # calendar source precedence:
        #   --file  >  --url  >  config ics_url  >  .env HIBOB_ICS_URL
        src_file=args.file
        src_url=(args.url or cfg.get("ics_url") or load_env_value("HIBOB_ICS_URL"))
        # treat the example placeholder as "not set"
        if src_url and "REPLACE" in src_url:
            src_url=None
        if src_file:
            events=parse_events(load_ics(path=src_file))
            sys.stderr.write(f"Calendar: local file {src_file}\n")
        elif src_url:
            events=parse_events(load_ics(url=src_url))
            where = "--url" if args.url else ("config" if cfg.get("ics_url") and "REPLACE" not in (cfg.get("ics_url") or "") else ".env HIBOB_ICS_URL")
            sys.stderr.write(f"Calendar: fetched from {where}\n")
        else:
            sys.stderr.write(
                "No calendar source found. PTO will use only explicit 'pto' in the config.\n"
                "  → First-run tip: copy .env.example to .env and set HIBOB_ICS_URL to your\n"
                "    personal calendar feed, then it's picked up automatically every run.\n"
                "    (Or pass --url / --file, or add ics_url to the config.)\n")

    plan=build_plan(cfg, events)

    if args.output:
        with open(args.output,"w",newline="",encoding="utf-8") as fh:
            gh,ph=write_csv(cfg, plan, fh)
        dest=args.output
    else:
        gh,ph=write_csv(cfg, plan, sys.stdout); dest="stdout"

    for n in plan["notes"]: sys.stderr.write(f"• {n}\n")
    sys.stderr.write(f"✓ Plan -> {dest} | allocated {fnum(round(plan['allocated'],2))}h of "
                     f"{fnum(plan['cap'])}h cap | grid {fnum(gh)}h vs PIR {fnum(ph)}h "
                     f"-> Match? {'TRUE' if round(gh*1e6)==round(ph*1e6) else 'FALSE'}\n")

if __name__=="__main__":
    main()
