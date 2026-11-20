#!/usr/bin/env python3
"""Compiles the business plan for founder-plan. Standard library only, no network.

Reads everything the build skills wrote into founder/ and assembles one
document, founder/business-plan.md, with a verdict at the top. It also writes
founder/profile.md, the business profile the run skills (weekly report, P&L,
cash flow, cost leak, product mix, staffing) read their targets from. The verdict is
computed from the numbers, never written by hand:

    Profitable   every check that has data passes
    Not yet      at least one check fails (each failure is listed with its number)
    Incomplete   there are no numbers yet (run founder-cfo first)

The checks:
    1. each unit earns money before fixed costs        (founder/numbers.json)
    2. year 1 makes an operating profit                 (founder/numbers.json)
    3. break-even fits inside capacity, if capacity is given
    4. enough of the buyer panel buys                   (founder/panel/results.json, --min-buy-rate, default 25%)

    python3 compile.py                      # reads ./founder, writes ./founder/business-plan.md
    python3 compile.py --dir path/to/founder --min-buy-rate 0.3
    python3 compile.py --check              # print the verdict and exit 0 (Profitable) or 1
    python3 compile.py --profile-only       # refresh founder/profile.md only
"""

import argparse
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = [  # (file in founder/, heading, which skill writes it)
    ("summary.md", "Summary", "founder-plan"),
    ("board.md", "What the board said", "founder-board"),
    ("competitors.md", "The competition", "founder-competitors"),
    ("panel/results.md", "The buyer panel", "founder-consumer"),
    ("pricing.md", "Pricing", "founder-pricing"),
    ("offer.md", "The offer", "founder-offer"),
    ("cfo.md", "The numbers", "founder-cfo"),
    ("marketing.md", "Marketing", "founder-marketing"),
    ("brand.md", "Brand", "founder-brand"),
    ("ops.md", "Operations", "founder-ops"),
    ("launch.md", "Launch plan", "founder-launch"),
]


def _load_unit_economics():
    path = os.path.join(HERE, "..", "founder-cfo", "unit_economics.py")
    spec = importlib.util.spec_from_file_location("founder_unit_economics", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()
    except FileNotFoundError:
        return None


def _strip_h1(text):
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    # demote headings one level so they nest under the section heading
    return "\n".join(("#" + l) if l.startswith("#") else l for l in lines).strip()


def _money(v, currency="IDR"):
    return _load_unit_economics().money(v, currency)


def profile_md(numbers, name):
    """The business profile the run skills read. Every number is from numbers.json."""
    M = lambda v: _money(v, numbers["currency"])
    u, p = numbers["unit"], numbers["price"]
    be = numbers["breakeven_per_day"]
    goods_pct = sum(c for _, c, k in numbers["variable_lines"] if k == "goods") / p
    fee_pct = sum(c for _, c, k in numbers["variable_lines"] if k == "fee") / p
    L = ["# Business profile: %s" % name, "",
         "Written by founder-plan from founder/numbers.json. The run skills (founder-weekly-report, founder-pnl,"
         " founder-cashflow, founder-cost-leak, founder-product-mix, founder-staffing) read their targets here."
         " Edit a threshold by hand when real numbers replace the plan; keep the line format.", "",
         "## From the plan", "",
         "- Unit: %s, price %s (before PB1/PBJT or PPN collected on top)" % (u, M(p)),
         "- Selling days per month: %s" % "{:g}".format(numbers["days_per_month"]),
         "- Break-even per day: %s %ss, %s of sales" % ("never" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)).replace(",", "."), u,
                                                       "n/a" if math.isinf(be) else M(numbers["breakeven_revenue_per_day"])),
         "- Weekly sales target at plan: %s (%s %ss a day)" % (M(numbers["plan_per_day"] * 7 * p), "{:,.0f}".format(numbers["plan_per_day"]).replace(",", "."), u),
         "- Fixed costs per month: %s" % M(numbers["fixed_monthly"]),
         "- Planned direct goods cost (COGS / food cost): %.1f%% of price" % (goods_pct * 100),
         "- Planned platform fees, payment fees and turnover tax: %.1f%% of price" % (fee_pct * 100),
         "", "## Thresholds the run skills use (defaults, change them here)", "",
         "- Direct cost (COGS / food cost) alert: %.0f%% of net sales (plan + 5 points)" % (goods_pct * 100 + 5),
         "- Labour alert: 25% of net sales",
         "- Healthy net margin: at least 10%",
         "- Sales drop alert: 10% week on week",
         "- Average ticket drop alert: 5%",
         "- Days below break-even that trigger an alert: 3 a week",
         "- Minimum safe cash: 1 week of operating costs",
         "", "## Fill in when known", "",
         "- Channels and settlement days: cash/QRIS 1 day; delivery apps ? days; marketplace ? days after the order completes",
         "- Biggest suppliers and payment terms: ?",
         "- Payday and THR month: ?",
         "- Opening hours and service standard (e.g. 1 cashier per 15 transactions an hour): ?"]
    return "\n".join(L) + "\n"


def verdict(d, min_buy_rate=0.25):
    """Return (verdict, checks, numbers, panel). checks = [(ok, text)]."""
    checks = []
    numbers = panel = None
    raw = _read(os.path.join(d, "numbers.json"))
    if raw:
        ue = _load_unit_economics()
        numbers = ue.analyse(json.loads(raw))
        u = numbers["unit"]
        M = lambda v: ue.money(v, numbers["currency"])
        c = numbers["contribution"]
        checks.append((c > 0, "Each %s earns %s before fixed costs (%.0f%% contribution)." % (u, M(c), numbers["contribution_pct"] * 100)
                       if c > 0 else "Each %s LOSES %s before fixed costs." % (u, M(-c))))
        y = numbers["year1_profit"]
        checks.append((y > 0, "Year 1 operating profit: %s." % M(y) if y > 0
                       else "Year 1 operating LOSS: %s." % M(-y)))
        be, cap = numbers["breakeven_per_day"], numbers["capacity_per_day"]
        if cap is not None:
            fits = not math.isinf(be) and be <= float(cap)
            checks.append((fits, "Break-even is %s %ss a day against a capacity of %s." % (
                "never reached" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)), u, cap)))
    raw = _read(os.path.join(d, "panel", "results.json"))
    if raw:
        panel = json.loads(raw)
        r = panel["buy_rate"]
        checks.append((r >= min_buy_rate, "%d of %d simulated buyers buy (%.0f%%, the bar is %.0f%%)." % (
            panel["buys"], panel["answered"], r * 100, min_buy_rate * 100)))
    if numbers is None:
        v = "Incomplete"
    elif all(ok for ok, _ in checks):
        v = "Profitable"
    else:
        v = "Not yet"
    return v, checks, numbers, panel


def compile_plan(d, min_buy_rate=0.25):
    idea = _read(os.path.join(d, "idea.md"))
    name = None
    if idea:
        first = idea.splitlines()[0]
        name = first[2:].strip() if first.startswith("# ") else None
    v, checks, numbers, panel = verdict(d, min_buy_rate)
    title = name or (numbers["business"] if numbers and numbers.get("business") else "Your business")
    L = ["# %s · Business plan" % title, ""]
    L.append("**Verdict: %s**" % v)
    L.append("")
    for ok, text in checks:
        L.append("- %s %s" % ("✓" if ok else "✗", text))
    if v == "Incomplete":
        L.append("- No numbers yet. Run /founder-cfo, then compile again.")
    L.append("")
    if numbers:
        be = numbers["breakeven_per_day"]
        M = lambda v: _money(v, numbers["currency"])
        L += ["| key number | |", "| --- | ---: |",
              "| Price | %s a %s |" % (M(numbers["price"]), numbers["unit"]),
              "| Profit margin at plan | %.0f%% per %s |" % (numbers["margin_at_plan"] * 100, numbers["unit"]),
              "| Break-even | %s %ss a day |" % ("never" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)), numbers["unit"]),
              "| Year 1 operating profit | %s |" % M(numbers["year1_profit"]),
              "| Startup spend | %s |" % M(numbers["startup"]),
              "| Cash needed before it pays for itself | %s |" % M(numbers["cash_needed"]),
              "| Startup money earned back | %s |" % ("month %d" % numbers["payback_month"] if numbers["payback_month"] else "not in year 1")]
        if panel:
            L.append("| Buyer panel | %d buy · %d pass |" % (panel["buys"], panel["passes"]))
        L.append("")
    if idea:
        L += ["## The idea", "", _strip_h1(idea), ""]
    missing = []
    for fname, heading, skill in SECTIONS:
        text = _read(os.path.join(d, fname))
        if text:
            L += ["## %s" % heading, "", _strip_h1(text), ""]
        else:
            missing.append((heading, skill))
    if missing:
        L += ["## Not done yet", ""]
        for heading, skill in missing:
            L.append("- %s: run /%s" % (heading, skill))
        L.append("")
    L.append("_The panel is simulated buyers and the numbers are projections from your inputs. Confirm demand with real"
             " customers and costs with real quotes before you spend. Not financial, legal or tax advice._")
    return v, "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default="founder")
    ap.add_argument("--min-buy-rate", type=float, default=0.25)
    ap.add_argument("--check", action="store_true", help="print the verdict only; exit 0 if Profitable")
    ap.add_argument("--out", help="default: <dir>/business-plan.md")
    ap.add_argument("--profile-only", action="store_true", help="write <dir>/profile.md only")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.dir):
        print("error: no %s/ folder here. Run the other founder skills first." % a.dir, file=sys.stderr)
        return 2
    v, text = compile_plan(a.dir, a.min_buy_rate)
    if a.check:
        _, checks, _, _ = verdict(a.dir, a.min_buy_rate)
        print("Verdict: %s" % v)
        for ok, t in checks:
            print("  %s %s" % ("✓" if ok else "✗", t))
        return 0 if v == "Profitable" else 1
    _, _, numbers, _ = verdict(a.dir, a.min_buy_rate)
    if numbers:
        name = text.splitlines()[0][2:].split(" · ")[0]
        with open(os.path.join(a.dir, "profile.md"), "w", encoding="utf-8") as fh:
            fh.write(profile_md(numbers, name))
    if a.profile_only:
        print("Wrote %s" % os.path.join(a.dir, "profile.md") if numbers else "error: no numbers.json, run /founder-cfo first")
        return 0 if numbers else 2
    out = a.out or os.path.join(a.dir, "business-plan.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("Verdict: %s. Wrote %s%s" % (v, out, " and profile.md" if numbers else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
