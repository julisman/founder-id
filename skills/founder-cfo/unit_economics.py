#!/usr/bin/env python3
"""Unit economics for founder-cfo. Standard library only, no network.

Takes one JSON file describing the business and prints the numbers a CFO would
check before a single rupiah is spent: what one unit earns, the real margin at
the volume you plan, how many units a day you need to break even, what year 1
looks like month by month, and how long it takes to earn the startup money back.

    python3 unit_economics.py founder/numbers.json
    python3 unit_economics.py founder/numbers.json --out founder/cfo.md
    python3 unit_economics.py founder/numbers.json --json
    python3 unit_economics.py founder/numbers.json --price 25000 --volume 0.8

The input (see example.json in this folder):

    business          name, for the report
    currency          "IDR" (default, shown as Rp25.000) or "USD"
    unit              what you sell one of: "cup", "order", "client-month"
    price             what you keep per unit, before PB1/PBJT or PPN collected on top
    variable          [{label, cost, share?}]  cost of ONE unit in money: ingredients,
                      packaging, shipping. share (0 to 1) = the part of units it
                      applies to (delivery packaging on 40% of orders: share 0.4)
    variable_pct      [{label, pct, share?}]  cost as a fraction of price: delivery-app
                      or marketplace commission (0.20), payment fee, PPh Final (0.005)
    fixed_monthly     [{label, cost, prepaid_months?}]  every month whatever you sell:
                      rent, salaries, BPJS, software. prepaid_months = months of
                      this line already paid inside startup (yearly rent paid up
                      front: 12), so year-1 cash does not count it twice
    one_off           [{label, month, cost}]  a cost that lands in one month of year 1:
                      THR before Lebaran, a yearly licence, a festival stall
    startup           [{label, cost}]  one-off spend before you open
    days_per_month    selling days in a month (default 30; 26 if closed one day a week)
    capacity_per_day  the most units a day you can physically sell (optional)
    plan_per_day      the volume you plan for once you are up and running
    ramp_per_day      12 numbers: units a day in each month of year 1
    season            12 multipliers on the ramp (Ramadan, Lebaran, rainy season;
                      default 1.0 every month)
    start             first month of year 1 as "YYYY-MM" (optional, for the labels)

Every number in the report comes from that file. Nothing is looked up or
guessed. If a field is missing the tool says so instead of filling it in.

Two results are kept apart on purpose: profit (what the business earns, with
rent counted every month) and cash (when the money actually leaves). Payback
and cash needed use cash; year-1 profit and the margin use profit.
"""

import argparse
import json
import math
import sys

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class NumbersError(Exception):
    pass


def money(v, currency="IDR", cents=False):
    """Rp1.250.000 for IDR (no decimals, dot thousands); $1,250.00 for USD."""
    sign = "-" if v < 0 else ""
    if currency == "IDR":
        return "%sRp%s" % (sign, "{:,.0f}".format(abs(round(v))).replace(",", "."))
    if cents:
        return "%s$%s" % (sign, "{:,.2f}".format(abs(v)))
    return "%s$%s" % (sign, "{:,.0f}".format(abs(round(v))))


def _num(x, where):
    try:
        return float(x)
    except (TypeError, ValueError):
        raise NumbersError("%s is not a number: %r" % (where, x))


def _share(it, field, i):
    s = _num(it.get("share", 1), "%s[%d].share" % (field, i))
    if not 0 <= s <= 1:
        raise NumbersError("%s[%d].share must be between 0 and 1" % (field, i))
    return s


def _items(items, field, key="cost"):
    out = []
    for i, it in enumerate(items or []):
        if not isinstance(it, dict) or key not in it:
            raise NumbersError("%s[%d] needs a '%s'" % (field, i, key))
        out.append((it, _num(it[key], "%s[%d].%s" % (field, i, key))))
    return out


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise NumbersError("no such file: %s" % path)
    except json.JSONDecodeError as e:
        raise NumbersError("%s is not valid JSON: %s" % (path, e))


def month_labels(spec):
    start = spec.get("start")
    if not start:
        return ["%d" % m for m in range(1, 13)]
    try:
        y, mo = [int(x) for x in str(start).split("-")[:2]]
        assert 1 <= mo <= 12
    except (ValueError, AssertionError):
        raise NumbersError("'start' must look like 2027-01")
    out = []
    for k in range(12):
        m = (mo - 1 + k) % 12
        out.append("%s %d" % (MONTHS[m], y + (mo - 1 + k) // 12))
    return out


def analyse(spec, price=None, volume=1.0):
    """Return a dict of every number in the report. Pure function, easy to test."""
    if "price" not in spec and price is None:
        raise NumbersError("'price' is missing")
    p = _num(price if price is not None else spec["price"], "price")
    if p <= 0:
        raise NumbersError("price must be above zero")
    cur = spec.get("currency", "IDR")
    days = _num(spec.get("days_per_month", 30), "days_per_month")

    var_lines = []
    for i, (it, c) in enumerate(_items(spec.get("variable"), "variable")):
        var_lines.append((it.get("label", "cost"), c * _share(it, "variable", i), "goods"))
    for i, (it, pct) in enumerate(_items(spec.get("variable_pct"), "variable_pct", "pct")):
        if not 0 <= pct < 1:
            raise NumbersError("variable_pct[%d].pct is a fraction: 0.20 means 20%%" % i)
        var_lines.append((it.get("label", "fee"), p * pct * _share(it, "variable_pct", i), "fee"))
    var = sum(c for _, c, _ in var_lines)

    fixed_items = _items(spec.get("fixed_monthly"), "fixed_monthly")
    fixed = sum(c for _, c in fixed_items)
    prepaid = []  # (monthly cost, months already paid)
    for i, (it, c) in enumerate(fixed_items):
        k = int(_num(it.get("prepaid_months", 0), "fixed_monthly[%d].prepaid_months" % i))
        if k:
            prepaid.append((c, k))
    one_off = []
    for i, (it, c) in enumerate(_items(spec.get("one_off"), "one_off")):
        m = int(_num(it.get("month"), "one_off[%d].month" % i))
        if not 1 <= m <= 12:
            raise NumbersError("one_off[%d].month is the month of year 1, 1 to 12" % i)
        one_off.append((m, it.get("label", "one-off"), c))
    startup = sum(c for _, c in _items(spec.get("startup"), "startup"))

    if "plan_per_day" not in spec and "ramp_per_day" not in spec:
        raise NumbersError("give 'plan_per_day' or 'ramp_per_day' (12 numbers)")
    plan = _num(spec.get("plan_per_day", 0), "plan_per_day") * volume
    ramp = spec.get("ramp_per_day")
    if ramp is None:
        ramp = [plan] * 12
    else:
        if len(ramp) != 12:
            raise NumbersError("'ramp_per_day' needs 12 numbers, one per month (got %d)" % len(ramp))
        ramp = [_num(v, "ramp_per_day") * volume for v in ramp]
    season = spec.get("season") or [1.0] * 12
    if len(season) != 12:
        raise NumbersError("'season' needs 12 multipliers, one per month (got %d)" % len(season))
    season = [_num(v, "season") for v in season]
    if not plan:
        plan = ramp[-1]

    contribution = p - var
    contribution_pct = contribution / p
    breakeven_day = math.inf if contribution <= 0 else fixed / (contribution * days)
    plan_units_month = plan * days
    margin_at_plan = (contribution - (fixed / plan_units_month if plan_units_month else math.inf)) / p

    labels = month_labels(spec)
    months = []
    cumulative = -startup
    payback_month = None
    for m, (per_day, mult) in enumerate(zip(ramp, season), start=1):
        per_day = per_day * mult
        units = per_day * days
        revenue = units * p
        variable_cost = units * var
        extra = sum(c for mm, _, c in one_off if mm == m)
        profit = revenue - variable_cost - fixed - extra
        cash = profit + sum(c for c, k in prepaid if m <= k)
        cumulative += cash
        if payback_month is None and cumulative >= 0:
            payback_month = m
        months.append({"month": m, "label": labels[m - 1], "per_day": per_day, "units": units,
                       "revenue": revenue, "variable": variable_cost, "fixed": fixed, "one_off": extra,
                       "profit": profit, "cash": cash, "cumulative": cumulative})
    year_profit = sum(m["profit"] for m in months)
    year_revenue = sum(m["revenue"] for m in months)
    lowest = min([-startup] + [m["cumulative"] for m in months])
    cash_needed = -lowest

    capacity = spec.get("capacity_per_day")
    flags = []
    if contribution <= 0:
        flags.append("Each unit loses money before rent and salaries: the price is below the variable cost.")
    if capacity is not None and breakeven_day > float(capacity):
        flags.append("Break-even needs %.0f %ss a day but capacity is %s." % (breakeven_day, spec.get("unit", "unit"), capacity))
    if capacity is not None and plan > float(capacity):
        flags.append("The plan (%.0f a day) is above capacity (%s)." % (plan, capacity))
    if year_profit < 0:
        flags.append("Year 1 loses money on operations (%s)." % money(year_profit, cur))
    if payback_month is None:
        flags.append("The startup spend is not earned back within year 1.")
    losing = [r for r in months if r["profit"] < 0]
    if losing and year_profit > 0:
        worst = min(losing, key=lambda r: r["profit"])
        flags.append("%d month(s) lose money even though the year is profitable (%s); the worst is %s at %s. Plan the cash for them." % (
            len(losing), ", ".join(r["label"] for r in losing), worst["label"], money(worst["profit"], cur)))

    return {
        "business": spec.get("business", ""), "unit": spec.get("unit", "unit"), "currency": cur,
        "price": p, "variable_per_unit": var, "variable_lines": var_lines, "contribution": contribution,
        "contribution_pct": contribution_pct, "fixed_monthly": fixed, "startup": startup,
        "one_off": one_off, "plan_per_day": plan, "margin_at_plan": margin_at_plan,
        "breakeven_per_day": breakeven_day, "breakeven_revenue_per_day": (
            math.inf if math.isinf(breakeven_day) else breakeven_day * p),
        "days_per_month": days, "capacity_per_day": capacity, "year1_revenue": year_revenue,
        "year1_profit": year_profit, "year1_after_startup": cumulative,
        "payback_month": payback_month, "cash_needed": cash_needed, "months": months, "flags": flags,
        "fixed_items": spec.get("fixed_monthly", []), "startup_items": spec.get("startup", []),
        "variable_items": [{"label": l, "cost": c, "kind": k} for l, c, k in var_lines],
    }


def sensitivity(spec):
    """The three what-ifs every plan should survive."""
    base = analyse(spec)
    rows = [("Base plan", base)]
    rows.append(("Price -10%", analyse(spec, price=base["price"] * 0.9)))
    rows.append(("Volume -20%", analyse(spec, volume=0.8)))
    worse = json.loads(json.dumps(spec))
    for it in worse.get("variable", []):
        it["cost"] = float(it["cost"]) * 1.15
    rows.append(("Unit costs +15%", analyse(worse)))
    return rows


def _units(v):
    return "never" if math.isinf(v) else "{:,.0f}".format(math.ceil(v)).replace(",", ".")


def report(spec, a):
    u, cur = a["unit"], a["currency"]
    M = lambda v: money(v, cur, cents=True)
    W = lambda v: money(v, cur)
    L = ["# Unit economics: %s" % (a["business"] or "your business"), "",
         "Every number below comes from the input file. Nothing is looked up or guessed.", "",
         "## One %s" % u, "", "| line | per %s |" % u, "| --- | ---: |", "| Price | %s |" % M(a["price"])]
    for label, c, _ in a["variable_lines"]:
        L.append("| %s | -%s |" % (label, M(c)))
    L.append("| **Contribution** (what each %s leaves to pay the fixed costs) | **%s** (%.0f%%) |"
             % (u, M(a["contribution"]), a["contribution_pct"] * 100))
    L += ["", "## The margin that matters", ""]
    L.append("Fixed costs: %s a month (%s)." % (W(a["fixed_monthly"]), ", ".join(
        "%s %s" % (it.get("label", "cost"), W(float(it["cost"]))) for it in a["fixed_items"]) or "none given"))
    L.append("")
    be = a["breakeven_per_day"]
    L.append("- **Break-even: %s %ss a day** (%s of sales a day over %s selling days a month). Below that you lose money every month." % (
        _units(be), u, "n/a" if math.isinf(be) else W(a["breakeven_revenue_per_day"]), "{:g}".format(a["days_per_month"])))
    L.append("- **Profit margin at your plan** (%s a day): **%.0f%%** of every sale, after every cost." % (
        _units(a["plan_per_day"]), a["margin_at_plan"] * 100))
    if a["capacity_per_day"] is not None:
        L.append("- Capacity: %s a day." % a["capacity_per_day"])
    if a["one_off"]:
        L.append("- One-off costs in year 1: %s." % ", ".join("%s %s in month %d" % (lbl, W(c), m) for m, lbl, c in a["one_off"]))
    L += ["", "## Year 1, month by month", "",
          "| month | %ss a day | revenue | profit | cash | cumulative cash (after %s startup) |" % (u, W(a["startup"])),
          "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for m in a["months"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (m["label"], _units(m["per_day"]), W(m["revenue"]),
                                                    W(m["profit"]), W(m["cash"]), W(m["cumulative"])))
    L += ["",
          "- **Year 1 operating profit: %s** on %s of revenue." % (W(a["year1_profit"]), W(a["year1_revenue"])),
          "- Cash position at the end of year 1, after the %s startup spend: %s." % (W(a["startup"]), W(a["year1_after_startup"])),
          "- Startup money earned back: %s." % ("month %d" % a["payback_month"] if a["payback_month"] else "not within year 1"),
          "- Cash you need before it pays for itself: **%s**." % W(a["cash_needed"]),
          "", "## What if", "", "| scenario | margin at plan | break-even a day | year 1 profit |",
          "| --- | ---: | ---: | ---: |"]
    for name, s in sensitivity(spec):
        L.append("| %s | %.0f%% | %s | %s |" % (name, s["margin_at_plan"] * 100, _units(s["breakeven_per_day"]), W(s["year1_profit"])))
    L.append("")
    if a["flags"]:
        L += ["## Red flags", ""] + ["- %s" % f for f in a["flags"]]
    else:
        L.append("No red flags in these numbers. They are only as good as the inputs: check every cost against a real quote.")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("numbers", help="the business's numbers.json")
    ap.add_argument("--out", help="write the report here (markdown)")
    ap.add_argument("--json", action="store_true", help="print the numbers as JSON")
    ap.add_argument("--price", type=float, help="what-if price")
    ap.add_argument("--volume", type=float, default=1.0, help="what-if volume multiplier")
    args = ap.parse_args(argv)
    try:
        spec = load(args.numbers)
        if args.price is not None:
            spec = dict(spec, price=args.price)
        if args.volume != 1.0:
            spec = dict(spec)
            if "plan_per_day" in spec:
                spec["plan_per_day"] = float(spec["plan_per_day"]) * args.volume
            if "ramp_per_day" in spec:
                spec["ramp_per_day"] = [float(v) * args.volume for v in spec["ramp_per_day"]]
        a = analyse(spec)
    except NumbersError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if args.json:
        out = {k: v for k, v in a.items() if not k.endswith("_items")}
        for k in ("breakeven_per_day", "breakeven_revenue_per_day"):
            out[k] = None if math.isinf(out[k]) else out[k]
        print(json.dumps(out, indent=1))
        return 0
    text = report(spec, a)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
