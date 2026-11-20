---
name: founder-cfo
description: >-
  Your CFO, in Rupiah. Builds the unit economics of an Indonesian business before
  money is spent: what one unit earns after its direct costs, delivery-app or
  marketplace commission, payment fees and PPh Final UMKM; the real profit margin
  at the planned volume; the break-even in units and Rupiah a day; year 1 month by
  month with Ramadan, Lebaran and other seasons, THR and yearly rent paid up front;
  the cash needed before it pays for itself; how long the startup spend takes to
  earn back; and what happens if the price drops, sales come in low or costs rise.
  Every number traces to an input the user can check. Use when the user says
  "find the profit margins", "do the numbers", "hitung modal", "is this
  profitable", "break-even", "BEP", "unit economics", "how much do I need to
  start", or "run the CFO".
argument-hint: "[path to numbers.json]"
---

# founder-cfo

The person who asks "and what does that cost?" Margins decide whether a good idea
is a business. This skill finds them, with every number traceable to an input.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/unit_economics.py" founder/numbers.json --out founder/cfo.md
```

## Step 1: gather the inputs

Write `founder/numbers.json` (shape: `example.json` in this folder, a kopi susu
kiosk in South Jakarta). It needs:

| field | what goes in it |
| --- | --- |
| `currency` | `IDR` |
| `unit` | what one sale is: a cup, an order, a pack, a client-month, a seat |
| `price` | what the business keeps per unit, **before** PBJT/PB1 or PPN collected on top |
| `variable` | the cost of ONE unit in Rupiah: ingredients, materials, packaging, shipping you pay. Add `share` when it applies to only part of the units |
| `variable_pct` | costs that are a fraction of the price: delivery-app or marketplace commission (with `share` = that channel's part of sales), payment fees above the free QRIS band, reseller margin, **PPh Final UMKM `0.005`** |
| `fixed_monthly` | what you pay every month regardless: wages, employer BPJS, rent, utilities, internet, apps, accountant. Rent paid a year up front: keep it here as rent/12 with `prepaid_months: 12`, and put the year's payment in `startup` |
| `one_off` | costs that land in one month of year 1: **THR** (month before Lebaran, pro rata in year 1), a yearly licence, a bazaar stall, festival stock |
| `startup` | one-off spend before opening: rent paid up front and deposits, renovation, equipment, first stock, permits and certification, launch promo |
| `start` | first month of year 1, `YYYY-MM`, so the months carry real names |
| `days_per_month` | selling days: 30 for every day, 26 for six days a week, about 22 for office days only |
| `plan_per_day` | the volume once it is up and running |
| `ramp_per_day` | 12 numbers: realistic volume in each month of year 1 |
| `season` | 12 multipliers for the calendar: Ramadan, Lebaran and mudik, payday-heavy months, 11.11 and 12.12, the rainy season |
| `capacity_per_day` | the most you can physically sell or make in a day, if there is a limit |

For the Indonesian items (BPJS rates, THR rules, PPh Final, QRIS fees, platform
commissions, the Ramadan dates), read the files in
`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/` and confirm current
figures on the official sources it lists.

Where the numbers come from, in this order:

1. The user's own quotes, invoices, leases, supplier price lists, merchant
   contracts.
2. Public prices the user can check (a supplier's price list, a kiosk listing on
   a property site, a platform's seller-centre fee page, the governor's UMP
   decree). Write the source next to the number in `founder/cfo-sources.md`.
3. Your estimate, clearly marked as an estimate in its `label`, with the
   reasoning. Never present an estimate as a fact.

Ask the user for anything only they know (the rent quoted, wages they will pay,
the channel mix they expect). Use the price from `founder/pricing.md` or
`founder/pitch.md` if those exist.

**The ramp is where plans lie.** Month 1 is almost never the plan volume. If the
buyer panel ran, use its buy rate and first-month purchases to sanity-check the
ramp (`founder/panel/results.md`), and say how you did it. Put seasons in
`season`, not in the ramp, so each can be argued separately.

## Step 2: run it

```bash
python3 "${CLAUDE_SKILL_DIR}/unit_economics.py" founder/numbers.json --out founder/cfo.md
```

It writes: the per-unit table and the contribution (what each sale leaves after
its own costs and fees), fixed costs, the break-even in units and Rupiah a day,
the profit margin at the plan volume, year 1 month by month (profit and cash kept
apart, so rent paid up front and THR show in the right month), the year 1
operating profit, the cash position at the end of year 1, the cash needed before
it pays for itself, the month the startup money is earned back, and a what-if
table (price -10%, volume -20%, unit costs +15%). It flags a price below variable
cost, a break-even above capacity, a losing year 1, a payback beyond 12 months and
losing months inside a profitable year.

What-ifs without editing the file:

```bash
python3 "${CLAUDE_SKILL_DIR}/unit_economics.py" founder/numbers.json --price 24000
python3 "${CLAUDE_SKILL_DIR}/unit_economics.py" founder/numbers.json --volume 0.8
```

For a channel what-if (more sales on the apps, a higher commission), copy the
file, change the `share` or `pct`, and run both.

## Step 3: the CFO's note

Add a short section at the top of `founder/cfo.md`, in plain words:

- **The margin**: the profit margin at plan, and the contribution per unit.
- **The line to watch**: the one cost or assumption that moves the result most
  (usually the ramp, rent, the channel mix or the price), with the what-if that
  proves it.
- **Cash**: how much money the founder needs before it pays for itself, and the
  hard months (Ramadan, THR, the rent renewal).
- **Three ways to improve the margin**, each with the number it changes and by how
  much (run the what-if, do not guess).
- Taxes: that the price excludes PBJT/PPN collected on top, that PPh Final is in
  the costs, and when the business would cross the Rp4,8 miliar PKP threshold.
- Whether the board's conditions about money (`founder/board.md`) are met.

## Rules

- Every number in your note comes from the tool's output or an input you can name.
- Not financial, tax or legal advice. Say once that an accountant or konsultan
  pajak should check the structure, payroll costs and tax before money moves.

## Output

`founder/numbers.json`, `founder/cfo.md`, `founder/cfo-sources.md`. Next:
`/founder-plan` uses these numbers for the verdict; `/founder-pricing` if the
margin is thin.
