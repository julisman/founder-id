---
name: founder-weekly-report
description: >-
  The Monday report. Builds a fixed-format weekly finance summary from last
  week's sales export (POS, delivery apps, marketplaces, WhatsApp orders,
  invoices) and purchases, compares it with the week before, raises an alert only
  when a threshold in founder/profile.md is crossed (direct cost, sales drop,
  average ticket, days below break-even, cash against bills due), suggests which
  run skill to use next, and prepares a short version for the team. Works for any
  business: F&B, retail, online sellers, services. Use every Monday morning as a
  routine, or when the owner says "last week's report", "laporan minggu lalu", "how
  was last week", or pastes a week of sales.
argument-hint: "[path to last week's sales export]"
---

# founder-weekly-report

A routine, not a deep analysis. The goal: the owner reads it in three minutes,
decides one action, done. When something is off, this skill **suggests** another
skill; it does not run a long analysis itself.

## When to use

- Every Monday morning, for the Monday to Sunday just finished.
- When the owner says "last week's report", "how was last week", or pastes a
  week of sales.

## The data

| source | required columns | notes |
| --- | --- | --- |
| Last week's sales | date, channel, gross sales, discounts, platform commission and fees, net sales, transactions (orders) | 7 days; one export per channel is fine (POS, GoFood/GrabFood/ShopeeFood, Shopee, Tokopedia/TikTok Shop, WhatsApp/transfer, invoices) |
| The week before | the same | for the comparison: use `founder/reports/weekly/<last week>.json` if it was saved, otherwise the export, or what is already in this conversation |
| Last week's purchases | date, item, total | for the weekly direct-cost estimate (no stock count, so an estimate) |
| Cash on Monday morning | one number | optional, for the cash alert |
| Business profile | `founder/profile.md`: direct-cost alert, weekly target, break-even per day, nearest supplier and payroll dates | written by `/founder-plan`; if missing, ask for the three thresholds or use the defaults below |

"Direct cost" means what the business buys to make or deliver what it sells:
food cost for F&B, cost of goods for retail and online sellers, materials and
subcontractors for services. Use the business's own word in the report.

If last week's purchases are missing, write the report without the direct-cost
line and say so under "Not recorded".

No POS and no exports at all? Suggest `/founder-templates`. It writes
`founder/templates/catatan-harian.xlsx`, a daily logbook in exactly these columns.
When the data comes from that logbook:

- **Net sales:** use the **Penjualan bersih** column.
- **The example row:** skip any row whose Catatan starts with "CONTOH".
- **Estimated fees:** an app-channel row with **Komisi & biaya platform** blank used the rate estimate. List those dates under "Not recorded" as "platform fee estimated".

`founder/profile.md` is written by `/founder-plan`. A business that skipped the
build stage often has its own outlet profile instead (an owner's notes, a course
`profil-outlet.md`): use it the same way, and say which file the thresholds came
from. Where both exist and disagree, the owner's own file wins.

## Steps

1. **Net sales last week**, per day and in total, per channel. Net sales = gross
   minus discounts minus platform commission and fees.
2. **Comparison** with the week before: the difference in Rupiah and %. If four
   weeks of data are in the conversation, add the four-week average.
3. **Transactions** and **average ticket** (net sales / transactions), against the
   week before.
4. **Best and worst day** last week, against the break-even per day from the
   profile. Count the days below break-even.
5. **Weekly direct cost (estimate)** = last week's purchases / last week's net
   sales. Label it an estimate because there is no stock count. Compare with the
   threshold.
6. **Alerts** (show only the ones triggered):
   - Direct cost estimate above the threshold two weeks running: suggest
     `/founder-cost-leak`.
   - Sales down more than 10% on the week before with no holiday to explain it:
     say which channel fell and suggest checking it.
   - More than 2 days below break-even: name the days.
   - Supplier bills, payroll, THR, BPJS or tax due in the next 7 days larger than
     the cash on hand: suggest `/founder-cashflow`.
   - Average ticket down more than 5%: likely too many discounts or cheap items
     dominating; suggest `/founder-product-mix` this month.
7. **One action**: pick one, the one with the biggest effect on profit that can
   start today. Not three.
8. **Team version**: five lines without profit, wages or cash. Only sales,
   transactions, the best day, direct cost (if any) and one focus for the week.

Default thresholds if the profile has none: direct cost 35% for F&B (ask for
other businesses), sales drop 10%, average ticket drop 5%, 3 days below
break-even.

## Verification rules (required)

- Total net sales must equal the export's total. Write how many rows were used.
- If a day has no data, list the date under "Not recorded". Never fill it with an
  average.
- Every % comes with the Rupiah. "Down 12%" without Rupiah is not allowed.
- The weekly direct cost is always labelled (estimate). Never write it as a
  precise figure.
- Alerts only when the threshold is really crossed. Do not add alerts to make
  the report look complete.
- Do not repeat last week's findings if nothing changed. If last week's action is
  recorded (in the conversation, or as `action` in last week's saved JSON), start
  with its result.

## Output format (fixed)

```
WEEKLY REPORT: [Business] - week [dd-dd month]

Net sales          Rp xx.xxx.xxx   (▲/▼ Rp x.xxx.xxx, xx% vs last week)
Transactions       xxx             (▲/▼ xx)   average ticket Rp xx.xxx (▲/▼ x%)
Best day           [day dd] Rp x.xxx.xxx   |   Worst day [day dd] Rp x.xxx.xxx
Below break-even   x of 7 days   (break-even Rp x.xxx.xxx a day)
Direct cost        xx% (estimate, from purchases of Rp x.xxx.xxx)   threshold xx%
Channels           walk-in xx% | GoFood xx% | Shopee xx% | WhatsApp xx% | other xx%

Last week's action: [what was decided] -> [the result, if visible in the numbers]

ALERTS
[only the triggered ones, one line each, with the number and the suggested skill]
or: No alerts this week.

1 ACTION THIS WEEK
[one action, who, when, measured by what next week]

NOT RECORDED
[missing dates, purchases not in, cash not given] or: Complete.

---- TEAM VERSION (can go straight to the group) ----
Week [dd-dd]: sales Rp xx.xxx.xxx (▲/▼ xx%), xxx transactions.
Best day [day], worst [day].
Direct cost about xx%, target under xx%.
Focus this week: [one sentence, the team's version of the action above].
Thanks, keep it up.

Source: sales export [file name], xx rows, [dd-dd]; purchases [file name], xx rows.
```

Write the team version in the language the team uses (usually Indonesian).

## Save the report

After showing the report, save it so next time (and the founder-id dashboard) can
use it. Two files in `founder/reports/weekly/`, named by the ISO week:

- `2027-W05.md`: the report exactly as shown above.
- `2027-W05.json`: its key numbers, in this shape (money in full Rupiah as plain
  numbers, percentages as fractions: 0.45 means 45%):

```json
{
  "week": "2027-W05", "start": "2027-02-01", "end": "2027-02-07",
  "net_sales": 18450000, "prev_net_sales": 17200000, "transactions": 760, "avg_ticket": 24276,
  "breakeven_per_day": 2070619, "days_below_breakeven": 2,
  "purchases": 8300000, "direct_cost_pct": 0.45, "direct_cost_threshold": 0.49,
  "channels": {"walk-in": 11070000, "GoFood/GrabFood": 7380000},
  "daily": [{"date": "2027-02-01", "day": "Mon", "net_sales": 2900000}, "... one per day"],
  "alerts": [{"text": "Direct cost 52% (estimate), above 49% two weeks running", "skill": "founder-cost-leak"}],
  "last_action": "what was decided last week", "action": "the one action this week",
  "not_recorded": ["2027-02-04: no POS export"]
}
```

Get the paths with `python3 "${CLAUDE_SKILL_DIR}/reports.py"` `path weekly 2027-W05`, write both files, then run
`python3 "${CLAUDE_SKILL_DIR}/reports.py"` `check founder/reports/weekly/2027-W05.json`. It checks that the daily rows and the channels add up to net_sales; avg_ticket = net_sales / transactions.
If it reports a problem, fix the numbers (never the check) and say what changed.
Copy numbers from the report; do not compute new ones for the JSON.

## Thresholds the owner can change (in founder/profile.md)

- Weekly direct-cost threshold
- Sales drop that triggers an alert (default 10%)
- Average ticket drop that triggers an alert (default 5%)
- Days below break-even that trigger an alert (default 3)
- What may go in the team version
