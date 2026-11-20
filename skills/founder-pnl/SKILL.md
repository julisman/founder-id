---
name: founder-pnl
description: >-
  Reads a month's profit and loss (from a P&L sheet, or from raw sales,
  purchases, stock, payroll and fixed-cost tabs) and explains it in the owner's
  language, not the accountant's. Shows platform commissions and fees as their own
  line, keeps PBJT/PPN collected and the owner's personal drawings (prive) out of
  the business's numbers, and compares the ratios with the business profile. Works
  for F&B, retail, online sellers and services, one outlet or several. Use when
  the owner asks "did we make money last month", "untung atau tidak", "why are
  sales up but there's no money", or wants a P&L summary per outlet or channel.
argument-hint: "[path to the P&L or the raw tabs]"
---

# founder-pnl

## When to use

- The owner uploads or pastes a **P&L** (or the raw tabs: sales, purchases,
  payroll, fixed costs, stock) for a month.
- The owner asks whether the business made money, how much, or where the money
  went.
- At the start of the month, to close the month before.

Not for per-item analysis (use `/founder-product-mix`) or finding where materials
leak (use `/founder-cost-leak`). If the owner asks that, finish the P&L first,
then suggest the right skill.

## The data

At least one outlet or store, one full month:

| source | required columns |
| --- | --- |
| Sales | date, outlet or store, channel, gross sales, discounts, platform commission and fees, net sales |
| Purchases | date, outlet, item, total |
| Stock | item, opening stock (Rp), closing stock (Rp) |
| Payroll | outlet, total wages (base + overtime + meals + employer BPJS), THR if paid this month |
| Fixed costs | outlet, item, amount per month |
| Taxes | PPh Final paid on the month's turnover; PBJT/PPN collected (to keep out of sales) |

If a P&L tab is already filled in, use its numbers. If only raw tabs exist,
calculate with the formulas below and say you calculated from raw data.

If a column is missing, **ask first**, do not invent. If the owner does not have
it (for example closing stock), go ahead with an estimate and label every number
it touches **(estimate)**.

## Steps

All in full Rupiah, no rounding until the last step.

1. **Net sales** = gross sales minus discounts minus platform commission and fees.
   Platform commission (GoFood, GrabFood, ShopeeFood, Shopee, Tokopedia/TikTok
   Shop, payment fees) is a cost: show it on its own line, never hide it in sales.
   PBJT or PPN collected from customers is **not** sales: take it out if the export
   includes it.
2. **Direct cost** (food cost / COGS / materials) = opening stock + purchases -
   closing stock. Without stock: direct cost = purchases, labelled (estimate).
3. **Direct cost %** = direct cost / net sales.
4. **Gross profit** = net sales - direct cost.
5. **Labour** = wages + overtime + staff meals + employer BPJS (+ THR in the month
   it is paid; say so, because it makes that month look worse). **Labour %** =
   labour / net sales.
6. **Fixed costs** = rent (a yearly rent counts as rent/12 each month) +
   electricity + water + internet + apps + accountant + other fixed items.
7. **PPh Final** (0.5% of gross turnover, if the business uses it) on its own line.
8. **Net profit** = gross profit - labour - fixed costs - PPh Final - platform
   commission (if not already taken off in step 1; never twice).
9. **Net margin %** = net profit / net sales.
10. **Owner's drawings (prive) are not a business cost.** If you find them in
    purchases or costs, take them out and state the amount.

Compare with the benchmarks in `founder/profile.md`, and with last month if
`founder/reports/pnl/` holds its saved report. If there is none, use
defaults for the business type and say which: F&B direct cost 28 to 35% and
labour 18 to 25%; for retail and online sellers ask for the target gross margin
(it varies by category); a healthy net margin is above 10% for most small
businesses.

## Verification rules (required)

- Every number must be traceable: say which tab and how many rows were summed,
  for example "Net sales Rp84.250.000 (Sales tab, 31 rows, Kemang outlet)".
- Match total net sales against the POS or platform total if the owner gives it.
  A difference above 1% is a finding, not something to adjust quietly.
- If dates are missing mid-month, list them. Do not fill them with an average.
- If total costs exceed sales and the owner says the business is profitable, do not
  go along. Show the numbers and ask what may not be recorded.
- Never create a number that is not in the data. If you must estimate, write
  **(estimate)** and explain the basis in one sentence.

## Output format (fixed)

```
PROFIT AND LOSS: [Business / outlet], [Month Year]

Net sales             Rp xxx.xxx.xxx   (walk-in xx%, GoFood xx%, Shopee xx%, ...)
Direct cost           Rp xxx.xxx.xxx   xx.x%   [benchmark xx-xx%]
Labour                Rp xxx.xxx.xxx   xx.x%   [benchmark xx-xx%]
Fixed costs           Rp xxx.xxx.xxx   xx.x%
Platform commission   Rp xxx.xxx.xxx   xx.x%
PPh Final             Rp xxx.xxx.xxx   xx.x%
------------------------------------------------
NET PROFIT            Rp xxx.xxx.xxx   xx.x%

In plain words:
Of every Rp100.000 that comes in, Rp xx.xxx goes on [materials/stock], Rp xx.xxx on wages,
Rp xx.xxx on rent and bills, Rp x.xxx on the apps' commission, Rp xxx on tax.
What is left for the owner: Rp xx.xxx.

3 FINDINGS
1. [the finding with the biggest effect on profit, with the number and the source rows]
2. [the second]
3. [the third]

1 ACTION THIS WEEK
[one concrete action that can start tomorrow, who does it, measured by which number]

1 NUMBER TO DOUBLE-CHECK
[the most doubtful or estimated number, and how to check it]

Source: [the tabs and rows used]
```

With more than one outlet, store or channel: one block each, then one comparison
line: which has the highest and lowest net margin, with the gap in Rupiah.

## Save the report

After showing the report, save it so next time (and the founder-id dashboard) can
use it. Two files in `founder/reports/pnl/`, named by the month (and outlet):

- `2027-01.md`: the report exactly as shown above.
- `2027-01.json`: its key numbers, in this shape (money in full Rupiah as plain
  numbers, percentages as fractions: 0.45 means 45%):

```json
{
  "month": "2027-01", "outlet": "Blok M",
  "gross_sales": 84000000, "discounts": 1200000, "platform_commission": 6900000,
  "net_sales": 75900000, "direct_cost": 33500000, "labour": 18950000, "fixed_costs": 10500000,
  "pph_final": 420000, "other_costs": 0, "net_profit": 12530000,
  "channels": {"walk-in": 45500000, "GoFood/GrabFood": 30400000},
  "estimates": ["direct cost from purchases, no closing stock"]
}
```

Get the paths with `python3 "${CLAUDE_SKILL_DIR}/../founder-weekly-report/reports.py"` `path pnl 2027-01`, write both files, then run
`python3 "${CLAUDE_SKILL_DIR}/../founder-weekly-report/reports.py"` `check founder/reports/pnl/2027-01.json`. It checks that net_profit = net_sales - direct_cost - labour - fixed_costs - pph_final - other_costs (net_sales is already after the platform commission); one file per outlet, the outlet's name added to the file name.
If it reports a problem, fix the numbers (never the check) and say what changed.
Copy numbers from the report; do not compute new ones for the JSON.

## Thresholds the owner can change (in founder/profile.md)

- Direct cost % benchmark
- Labour % benchmark
- Minimum healthy net margin (default 10%)
- Report language (default plain English; Indonesian on request, casual or formal)

## Style

Write as if explaining to a friend who runs a warung, not to an auditor. Avoid
"accrual", "COGS" without explaining it once, "EBITDA". Short sentences. Rupiah
always in full with dots for thousands.
