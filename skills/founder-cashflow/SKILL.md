---
name: founder-cashflow
description: >-
  Projects the cash balance week by week for the next 4 weeks (up to 8) from the
  daily sales pattern per channel, the payout delay of each channel (cash and QRIS
  next day, delivery apps a few days, marketplaces after the order completes),
  supplier due dates, payroll, THR, BPJS, PPh Final and fixed costs, then flags the
  weeks at risk of going negative and gives two ways to handle each. Cash, not
  profit. Works for any business. Use when the owner asks "will the money last
  until payday", "cukup tidak uangnya", before a big purchase, before Lebaran
  (THR), or at the start of every month.
argument-hint: "[weeks, default 4]"
---

# founder-cashflow

## When to use

- The owner asks whether cash will cover wages, rent, THR or suppliers.
- Before a big spending decision (equipment, renovation, a big stock order, a
  marketplace campaign).
- At the start of each month, before Lebaran, or when `/founder-weekly-report`
  flags cash falling two weeks running.

This skill is about **cash**, not profit. A business that is profitable on its
P&L can run out of cash because bills fall due in the same week, marketplace
money is held, or THR lands. Say so if the owner mixes them up.

## The data

| source | required columns | notes |
| --- | --- | --- |
| Daily sales | date, net sales, channel | at least the last 8 weeks; channel matters because payouts arrive at different times |
| Cash today | one number: cash in the drawer + the operating account (+ balances waiting in platform wallets, listed separately) | with the date |
| Supplier due dates | supplier, amount, due date | from the purchases tab, or typed by the owner |
| Payroll | total wages, pay date | include overtime, and THR if it falls in the period |
| Fixed costs and statutory payments | item, amount, date | rent, utilities, internet, loan instalments, subscriptions; BPJS by the 10th; PPh Final by the 15th; PBJT per the region |
| Business profile | `founder/profile.md`: payout delay per channel, planned big purchases | default delays: cash/QRIS 1 day; delivery apps 3 to 7 days; marketplaces 3 to 14 days after the order completes; B2B invoices per their terms |

If supplier due dates are not recorded, ask the owner for **the 3 biggest
suppliers and how they are paid** (cash, 7, 14, 30 days, consignment). Do not
assume everything is cash.

## Steps

1. **Sales pattern**: the average net sales per weekday (Monday to Sunday) over
   the last 8 weeks, per channel. Use the median instead if there were big event
   days. Adjust for the calendar ahead
   (`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/calendar.md`): payday
   weeks, Ramadan, Lebaran and mudik, 11.11 and 12.12, and say what you assumed.
2. **Trend**: compare the last 4 weeks with the 4 before. If up or down by more
   than 10%, use the last 4 weeks and state the trend.
3. **Cash in per week** for weeks 1 to 4 = sum of (sales per day per channel,
   shifted by that channel's payout delay). A Friday GoFood sale lands next week,
   not this week.
4. **Cash out per week** = supplier due dates + payroll + THR + fixed costs +
   BPJS + taxes + routine purchases (estimate: direct cost % x that week's sales,
   for suppliers paid in cash) + planned big purchases.
5. **End-of-week balance** = opening balance + cash in - cash out. Week 1 opens
   with today's balance.
6. **Lowest balance inside the week**: if a big bill falls early in the week before
   sales come in, compute the balance on that day. A week can end positive and be
   negative on Tuesday.
7. **Pessimistic case**: repeat steps 3 to 6 with sales 15% lower (adjustable).
   Weeks negative only in the pessimistic case are "watch"; weeks negative in the
   normal case are "at risk".
8. **Two options** for each week at risk, from: move a supplier due date (name the
   supplier and amount), delay a big purchase, withdraw platform balances early,
   collect receivables, a promotion the week before to pull cash in, split THR
   payment within the legal window, or as a last resort an owner top-up for an
   exact amount.

## Verification rules (required)

- Show the cash-in and cash-out table per week with its detail, not only the end
  balance.
- State the date of the opening balance and its source. A balance typed from
  memory is labelled (from memory).
- The 8-week sales total you use must equal the data's total. Exclude incomplete
  weeks (fewer than 6 trading days) and say so.
- Do not include income that is not certain (an order with no deposit, a loan
  not yet disbursed). If the owner insists, put it on its own line labelled (not
  certain) and show the balance with and without it.
- If the owner gives no supplier due dates, write in the title **(no supplier
  schedule: the balance may be lower than this)**.

## Output format (fixed)

```
4-WEEK CASH FORECAST: [Business], from [date]
Cash today Rp xxx.xxx.xxx ([source]) | Pattern from 8 weeks, trend xx% | Payouts: cash 1 day, GoFood 5 days, Shopee 7 days

| Week | Cash in | Suppliers | Payroll/THR | Fixed + BPJS + tax | Routine buying | Big purchases | End balance | Lowest (day) | Status |
| 1 (dd-dd) | ... | ... | ... | ... | ... | ... | ... | ... | safe/watch/at risk |
| 2 | |
| 3 | |
| 4 | |

Pessimistic case (sales -15%): week 4 end balance Rp xxx.xxx.xxx, negative weeks: [..]

WEEKS AT RISK
Week x (dd-dd): negative Rp xxx.xxx on [day] because [which payment].
  Option A: [action, amount, who to contact, when]
  Option B: [action, amount]

3 FINDINGS
1. ...
2. ...
3. ...

1 ACTION THIS WEEK
[usually: call one supplier to move a due date, or delay one purchase]

1 NUMBER TO DOUBLE-CHECK
[the opening balance, or the biggest supplier due date]

Source: [tabs, rows, balance date]
```

## Thresholds the owner can change (in founder/profile.md)

- Payout delay per channel
- Pessimistic sales drop (default 15%)
- Minimum safe balance (default: one week of operating costs)
- Number of weeks (default 4, at most 8)
