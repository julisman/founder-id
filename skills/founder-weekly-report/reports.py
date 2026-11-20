#!/usr/bin/env python3
"""Saved reports for the run skills. Standard library only, no network.

The run skills (weekly report, P&L, cash flow, cost leak, product mix, staffing)
answer in the chat AND save each report in founder/reports/, as two files:

    founder/reports/<kind>/<key>.md     the report exactly as shown to the owner
    founder/reports/<kind>/<key>.json   its key numbers, for the dashboard and next time

This tool knows where each kind goes, what its JSON must hold, and checks the
arithmetic the skills' verification rules ask for (totals that must add up,
balances that must chain). It never writes a number itself.

    python3 reports.py path weekly 2027-W05 [--dir founder]   # where to save it
    python3 reports.py check founder/reports/weekly/2027-W05.json
    python3 reports.py list [--dir founder]                  # what is saved, newest first

The kinds and their key:

    weekly        week      2027-W05      (ISO week)
    pnl           month     2027-01       (add "outlet" for one file per outlet)
    cashflow      from      2027-02-03    (the date of the opening balance)
    cost-leak     month     2027-01
    product-mix   period    2027-01 or 2027-Q1
    staffing      period    2027-01 or 2027-W05

Money is in full Rupiah (plain numbers, no dots). Percentages are fractions:
0.32 means 32%.
"""

import argparse
import glob
import json
import os
import re
import sys

KINDS = {
    "weekly": {"key": "week", "pattern": r"^\d{4}-W\d{2}$", "skill": "founder-weekly-report",
               "numbers": ["net_sales", "transactions"]},
    "pnl": {"key": "month", "pattern": r"^\d{4}-\d{2}$", "skill": "founder-pnl",
            "numbers": ["net_sales", "direct_cost", "labour", "fixed_costs", "net_profit"]},
    "cashflow": {"key": "from", "pattern": r"^\d{4}-\d{2}-\d{2}$", "skill": "founder-cashflow",
                 "numbers": ["opening_balance"]},
    "cost-leak": {"key": "month", "pattern": r"^\d{4}-\d{2}$", "skill": "founder-cost-leak", "numbers": []},
    "product-mix": {"key": "period", "pattern": r"^\d{4}-(\d{2}|Q[1-4]|W\d{2})$", "skill": "founder-product-mix",
                    "numbers": []},
    "staffing": {"key": "period", "pattern": r"^\d{4}-(\d{2}|Q[1-4]|W\d{2})$", "skill": "founder-staffing",
                 "numbers": ["labour_pct"]},
}
STATUSES = ("safe", "watch", "at risk")
QUADRANTS = ("star", "plowhorse", "puzzle", "dog", "new")


class ReportError(Exception):
    pass


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _close(a, b, total=None):
    """Equal within Rp1 per line and 0.1% of the total: rounding, not a missing row."""
    tol = max(2.0, 0.001 * abs(total if total is not None else b))
    return abs(a - b) <= tol


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def filename(kind, doc):
    spec = KINDS[kind]
    key = str(doc.get(spec["key"], ""))
    if kind == "pnl" and doc.get("outlet"):
        key += "-" + _slug(doc["outlet"])
    return key


def path(fdir, kind, key):
    if kind not in KINDS:
        raise ReportError("unknown kind %r: one of %s" % (kind, ", ".join(KINDS)))
    return os.path.join(fdir, "reports", kind, key + ".json")


def kind_of(file_path):
    parent = os.path.basename(os.path.dirname(os.path.abspath(file_path)))
    if parent not in KINDS:
        raise ReportError("%s is not under founder/reports/<kind>/" % file_path)
    return parent


def check(kind, doc):
    """Problems with a report's JSON, as a list of strings. Empty means it is fine."""
    spec = KINDS[kind]
    P = []
    if not isinstance(doc, dict):
        return ["the JSON must be an object"]
    key = doc.get(spec["key"])
    if not isinstance(key, str) or not re.match(spec["pattern"], key):
        P.append("'%s' must look like %s" % (spec["key"], {"weekly": "2027-W05", "pnl": "2027-01", "cashflow": "2027-02-03",
                                                            "cost-leak": "2027-01"}.get(kind, "2027-01")))
    for f in spec["numbers"]:
        if not _num(doc.get(f)):
            P.append("'%s' is missing or not a plain number" % f)
    for f, v in doc.items():
        if f.endswith("_pct") and _num(v) and not -1 <= v <= 2:
            P.append("'%s' is a fraction (0.32 means 32%%), got %s" % (f, v))
    if P:
        return P
    CHECKS[kind](doc, P)
    return P


def _check_weekly(d, P):
    total = d["net_sales"]
    daily = d.get("daily") or []
    if daily:
        s = sum(x.get("net_sales", 0) for x in daily)
        if not _close(s, total):
            P.append("the daily net sales add up to %s, not net_sales %s" % (round(s), round(total)))
        if len(daily) > 7:
            P.append("a week has at most 7 days (got %d)" % len(daily))
    ch = d.get("channels") or {}
    if ch:
        s = sum(v for v in ch.values() if _num(v))
        if not _close(s, total):
            P.append("the channels add up to %s, not net_sales %s" % (round(s), round(total)))
    if _num(d.get("avg_ticket")) and d["transactions"]:
        if not _close(d["avg_ticket"], total / d["transactions"], total / d["transactions"] * 10):
            P.append("avg_ticket should be net_sales / transactions = %s" % round(total / d["transactions"]))
    for a in d.get("alerts") or []:
        if not isinstance(a, dict) or not a.get("text"):
            P.append("every alert is {\"text\": ..., \"skill\": ...}")
            break


def _check_pnl(d, P):
    expected = d["net_sales"] - d["direct_cost"] - d["labour"] - d["fixed_costs"] - d.get("pph_final", 0) - d.get("other_costs", 0)
    if not _close(d["net_profit"], expected, d["net_sales"]):
        P.append("net_profit should be net_sales - direct_cost - labour - fixed_costs - pph_final - other_costs = %s"
                 " (platform commission is already out of net_sales)" % round(expected))
    ch = d.get("channels") or {}
    if ch and not _close(sum(v for v in ch.values() if _num(v)), d["net_sales"]):
        P.append("the channels add up to %s, not net_sales" % round(sum(ch.values())))


def _check_cashflow(d, P):
    weeks = d.get("weeks") or []
    if not weeks:
        P.append("'weeks' needs at least one week")
        return
    bal = d["opening_balance"]
    for i, w in enumerate(weeks, 1):
        for f in ("cash_in", "cash_out", "end_balance"):
            if not _num(w.get(f)):
                P.append("week %d: '%s' is missing or not a number" % (i, f))
                return
        parts = [w[f] for f in ("suppliers", "payroll", "fixed", "routine", "big") if _num(w.get(f))]
        if parts and not _close(sum(parts), w["cash_out"]):
            P.append("week %d: suppliers + payroll + fixed + routine + big = %s, not cash_out %s" % (i, round(sum(parts)), round(w["cash_out"])))
        if not _close(bal + w["cash_in"] - w["cash_out"], w["end_balance"], max(abs(bal), w["cash_in"])):
            P.append("week %d: opening %s + in %s - out %s should end at %s, not %s" % (
                i, round(bal), round(w["cash_in"]), round(w["cash_out"]), round(bal + w["cash_in"] - w["cash_out"]), round(w["end_balance"])))
        if w.get("status") not in STATUSES:
            P.append("week %d: status is one of %s" % (i, ", ".join(STATUSES)))
        if w["end_balance"] < 0 and w.get("status") == "safe":
            P.append("week %d ends negative but is marked safe" % i)
        bal = w["end_balance"]


def _check_cost_leak(d, P):
    items = d.get("items") or []
    if not items:
        P.append("'items' needs the items with the biggest gaps")
    for it in items:
        if not it.get("item") or not all(_num(it.get(f)) for f in ("expected", "actual", "gap_rp")):
            P.append("every item needs item, expected, actual and gap_rp")
            return
        if _num(it.get("gap_qty")) and not _close(it["gap_qty"], it["actual"] - it["expected"], max(abs(it["actual"]), 1)):
            P.append("%s: gap_qty should be actual - expected" % it["item"])
    gaps = [it["gap_rp"] for it in items]
    if gaps != sorted(gaps, reverse=True):
        P.append("items are sorted by gap_rp, biggest first")


def _check_product_mix(d, P):
    items = d.get("items") or []
    if not items:
        P.append("'items' needs every item analysed")
    for it in items:
        if not it.get("item") or not _num(it.get("qty")) or not _num(it.get("margin_unit")):
            P.append("every item needs item, qty and margin_unit")
            return
        if it.get("quadrant") not in QUADRANTS:
            P.append("%s: quadrant is one of %s" % (it["item"], ", ".join(QUADRANTS)))
        if _num(it.get("total_margin")) and not _close(it["total_margin"], it["qty"] * it["margin_unit"], it["total_margin"]):
            P.append("%s: total_margin should be qty x margin_unit" % it["item"])


def _check_staffing(d, P):
    hm = d.get("heatmap")
    if hm:
        days, hours, vals = hm.get("days") or [], hm.get("hours") or [], hm.get("values") or []
        if len(vals) != len(hours) or any(len(r) != len(days) for r in vals):
            P.append("heatmap.values needs one row per hour, one value per day")


CHECKS = {"weekly": _check_weekly, "pnl": _check_pnl, "cashflow": _check_cashflow, "cost-leak": _check_cost_leak,
          "product-mix": _check_product_mix, "staffing": _check_staffing}


def load(file_path):
    try:
        with open(file_path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise ReportError("no such file: %s" % file_path)
    except json.JSONDecodeError as e:
        raise ReportError("%s is not valid JSON: %s" % (file_path, e))


def load_all(fdir):
    """{kind: [doc, ...]} newest first; each doc gets _file, _md (if saved) and _problems."""
    out = {}
    for kind in KINDS:
        docs = []
        for fp in glob.glob(os.path.join(fdir, "reports", kind, "*.json")):
            rel = os.path.relpath(fp, fdir).replace(os.sep, "/")
            try:
                doc = load(fp)
            except ReportError as e:
                docs.append({"_file": rel, "_problems": [str(e)], "_key": os.path.basename(fp)[:-5]})
                continue
            if not isinstance(doc, dict):
                doc = {}
            doc["_file"] = rel
            doc["_key"] = os.path.basename(fp)[:-5]
            md = fp[:-5] + ".md"
            doc["_md"] = rel[:-5] + ".md" if os.path.exists(md) else None
            doc["_problems"] = check(kind, doc)
            docs.append(doc)
        docs.sort(key=lambda x: x["_key"], reverse=True)
        out[kind] = docs
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default="founder")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("path")
    p.add_argument("kind")
    p.add_argument("key")
    c = sub.add_parser("check")
    c.add_argument("files", nargs="+")
    sub.add_parser("list")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "path":
            j = path(a.dir, a.kind, a.key)
            print(j)
            print(j[:-5] + ".md")
            return 0
        if a.cmd == "check":
            bad = 0
            for f in a.files:
                kind = kind_of(f)
                doc = load(f)
                probs = check(kind, doc)
                want = filename(kind, doc) + ".json"
                if not probs and os.path.basename(f) != want:
                    probs.append("save it as %s so the reports sort by date" % want)
                if probs:
                    bad += 1
                    print("%s:" % f)
                    for pr in probs:
                        print("  - %s" % pr)
                else:
                    print("%s: ok" % f)
            return 1 if bad else 0
        if a.cmd == "list":
            allr = load_all(a.dir)
            for kind, docs in allr.items():
                if docs:
                    print("%-12s %d saved, latest %s%s" % (kind, len(docs), docs[0]["_key"],
                                                         "" if not docs[0]["_problems"] else " (has problems: run check)"))
            if not any(allr.values()):
                print("no reports saved in %s/reports yet" % a.dir)
            return 0
    except ReportError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
