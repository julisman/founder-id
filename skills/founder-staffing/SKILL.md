---
name: founder-staffing
description: >-
  Compares workload per hour (transactions from the POS, app orders, marketplace
  orders to pack, bookings) with the shift roster to find the hours with too many
  and too few staff, then proposes a new roster and estimates the saving in
  Rupiah and in labour %, within Indonesian working-time and overtime rules. Works
  for F&B, shops, warehouses and online sellers' packing, salons, clinics and
  other service businesses. Use when labour % is above the threshold, when the
  owner feels staff are often idle or overwhelmed, before the Ramadan or Lebaran
  roster, or when planning next month's schedule. Phrases: "what are the busiest
  hours", "do I need more people", "can we save on wages", "jadwal shift".
argument-hint: "[weeks of data, default 4]"
---

# founder-staffing

## When to use

- Labour % is above the threshold in `founder/profile.md` (default 25%).
- The owner asks "what are the busiest hours", "do I need another person", or "can
  we save on wages".
- Before building next month's roster, and before Ramadan (shifted peak hours)
  and Lebaran (mudik leave).

## The data

| source | required columns | notes |
| --- | --- | --- |
| Workload per hour | date, hour, number of transactions (or orders, or bookings), sales | POS export per hour or per transaction (grouped per hour), app and marketplace orders, booking system; at least 4 weeks |
| Shift roster | day, start, end, staff per role (cashier, kitchen, bar, floor, packer, stylist...) | the roster actually worked, not the ideal one |
| Pay (optional) | role, hourly pay, or monthly pay + hours per month | to calculate the Rupiah saving; hourly = monthly / 173 if only monthly pay is known |
| Business profile | opening hours, days closed, service standard (for example 1 cashier per 15 transactions an hour) | `founder/profile.md` |

If the roster is not written down, ask the owner to type last week's roster from
memory and label it **(roster from memory)**.


`founder/profile.md` is written by `/founder-plan`. A business that skipped the
build stage often has its own outlet profile instead (an owner's notes, a course
`profil-outlet.md`): use it the same way, and say which file the thresholds came
from. Where both exist and disagree, the owner's own file wins.

## Steps

1. Group the workload by **weekday x hour** (Monday 10.00, Monday 11.00, and so
   on). Use a 4-week average, not one week, so a rainy day or payday does not
   mislead.
2. Compute **transactions per hour** and **sales per hour** for each slot.
3. From the roster, compute **staff present per slot** per role.
4. **Transactions per staff per hour** = transactions in the slot / staff present.
   This is the main number.
5. Set the **standard** per role from the profile. If there is none, use these
   defaults and write them down: cashier 12 to 20 transactions an hour, kitchen 8
   to 15 orders an hour per person, floor 4 to 6 active tables, packer 15 to 30
   parcels an hour, service roles by booking length.
6. Mark each slot:
   - **Overstaffed**: transactions per staff below 50% of the standard for 2 or more
     hours in a row.
   - **Understaffed**: transactions per staff above 120% of the standard.
   - **Right**: the rest.
7. **Proposed roster**: shift or cut hours in overstaffed slots, add in
   understaffed ones. Shift first (no extra people), then cut hours. Keep within 40
   hours a week (6 x 7 or 5 x 8) and the overtime limits (at most 4 hours a day and
   18 a week, paid 1.5x the first hour and 2x after, see
   `${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/payroll.md`). Never cut a
   worker below the contracted hours if the owner mentions them.
8. **Saving** = hours cut per week x hourly pay x 4.33. Show it in Rupiah per month
   and as the drop in labour % (saving / monthly net sales).
9. Also estimate **sales likely lost** in understaffed slots: when queues are long,
   assume 5% of transactions walk away or app orders are cancelled (adjustable). If
   adding a person to that slot saves more than it costs, propose adding.

## Verification rules (required)

- Show the heat map (weekday x hour) of transactions per staff, not only the
  conclusion. The owner must be able to see the pattern.
- The total transactions in your table must equal the export's total for the
  period.
- Name slots with fewer than 3 weeks of data (closed days, holidays) and leave them
  out of the recommendations.
- Never recommend firing anyone. Recommendations are about hours and slots only. If
  total hours fall sharply, say "the owner needs to discuss this with the team", not
  "cut one person". Contract and severance rules apply to any change in a
  permanent worker's terms.
- The standard per staff is an assumption. Label it (assumed) and ask the owner to
  confirm it by watching 2 busy hours.

## Output format (fixed)

```
STAFFING VS BUSY HOURS: [Business], [4]-week average to [date]
Labour last month xx.x% (benchmark xx-xx%) | Standards used: cashier xx trx/hour, kitchen xx orders/hour (assumed)

TRANSACTIONS PER STAFF (weekday x hour)
| Hour | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
| 10 | 3.1 | ... |
(number = transactions per staff per hour; ▼ overstaffed, ▲ understaffed)

OVERSTAFFED SLOTS
| Day | Hour | Staff | Transactions/hour | Per staff | Suggestion |

UNDERSTAFFED SLOTS
| Day | Hour | Staff | Transactions/hour | Per staff | Suggestion |

PROPOSED ROSTER
| Day | Hours | Cashier | Kitchen | Floor | Change from now |

EFFECT
Hours cut: xx/week -> saving Rp xxx.xxx/month -> labour from xx.x% to xx.x%
Hours added: xx/week -> cost Rp xxx.xxx/month -> sales saved about Rp xxx.xxx/month (assumed)

3 FINDINGS
1. ...
2. ...
3. ...

1 ACTION THIS WEEK
[usually: change the roster on one day as a trial, watch 2 busy hours to confirm the standard]

1 NUMBER TO DOUBLE-CHECK
[the standard per staff, or a roster that came from memory]

Source: [export file, period, rows; roster from ...]
```

## Save the report

After showing the report, save it so next time (and the founder-id dashboard) can
use it. Two files in `founder/reports/staffing/`, named by the month or period:

- `2027-01.md`: the report exactly as shown above.
- `2027-01.json`: its key numbers, in this shape (money in full Rupiah as plain
  numbers, percentages as fractions: 0.45 means 45%):

```json
{
  "period": "2027-01", "labour_pct": 0.247, "labour_pct_after": 0.221,
  "hours_cut": 14, "hours_added": 6, "saving_month": 1990000,
  "standard": "cashier 15 transactions/hour (assumed)",
  "heatmap": {"days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "hours": [6, 7, 8],
              "values": [[3.1, 2.8, 3.0, 2.9, 3.3, 1.2, 0.9], ["... one row per hour"]]}
}
```

Get the paths with `python3 "${CLAUDE_SKILL_DIR}/../founder-weekly-report/reports.py"` `path staffing 2027-01`, write both files, then run
`python3 "${CLAUDE_SKILL_DIR}/../founder-weekly-report/reports.py"` `check founder/reports/staffing/2027-01.json`. It checks that one heatmap row per hour, one value per day.
If it reports a problem, fix the numbers (never the check) and say what changed.
Copy numbers from the report; do not compute new ones for the JSON.

## Thresholds the owner can change (in founder/profile.md)

- Standard per staff per role
- Overstaffed threshold (default 50% of standard, 2 hours in a row)
- Understaffed threshold (default 120% of standard)
- Walk-away assumption when queues form (default 5%)
- Minimum hours per worker per week
