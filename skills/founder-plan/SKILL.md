---
name: founder-plan
description: >-
  Your business planner. Compiles everything the other founder skills wrote (the
  board's verdict, the competitors, the buyer panel, pricing, the offer, the CFO's
  Rupiah numbers, marketing, brand, operations and the launch plan) into one
  business plan with a verdict at the top that is computed from the numbers, never
  written by hand: Profitable, Not yet (with the failing numbers) or Incomplete.
  Adds an executive summary, a one-page version for a partner, a bank (for a KUR
  loan, for example) or an investor, and the business profile the run skills use
  after opening. Use when the user says "write my business plan", "rencana bisnis",
  "put it all together", "is it profitable", "give me the plan", or at the end of
  the founder pack.
argument-hint: "[--min-buy-rate 0.25]"
---

# founder-plan

The last step before opening. One document a founder can act on, or hand to a
partner, a bank or an investor, built only from what the pack found.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir founder
```

## Step 1: see what is there

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir founder --check
```

prints the verdict and each check. The checks, all computed:

1. Each unit earns money before fixed costs, after the platform's cut and PPh
   Final (`founder/numbers.json`).
2. Year 1 makes an operating profit.
3. The break-even fits inside capacity, if a capacity was given.
4. Enough simulated buyers buy (`founder/panel/results.json`; default bar 25%,
   change it with `--min-buy-rate` and say why).

If there are no numbers, the verdict is Incomplete: offer to run `/founder-cfo`.
List the other missing sections with the skill that fills each. Do not fill a
missing section yourself from guesses.

## Step 2: the summary

Write `founder/summary.md`, half a page, plain words:

- What the business is and who it is for, in two sentences.
- The verdict and the three numbers behind it (margin, break-even, year 1).
- What the buyer panel and the board agreed on, and where they disagreed.
- The biggest risk and what will be done about it.
- What the founder needs to start (cash from the CFO, the permits from ops, the
  first test from launch).
- The one thing to do this week.

If the verdict is Not yet, the summary leads with what has to change and which skill
changes it. Never soften a failing check.

## Step 3: compile

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir founder
```

writes `founder/business-plan.md`: title, the verdict and its checks, the key numbers
table, the idea, then every section the pack produced (summary, board, competition,
panel, pricing, offer, numbers, marketing, brand, operations, launch), and what is
not done yet.

It also writes **`founder/profile.md`**, the business profile the run skills read
after opening: break-even per day in units and Rupiah, the weekly sales target,
fixed costs, the planned direct-cost percentage and the alert thresholds. Tell the
user to fill in the "Fill in when known" lines (settlement days per channel,
supplier terms, payday, service standard) and to update thresholds once real
numbers replace the plan. Refresh it alone with `--profile-only`.

## Step 4: the one-pager

Write `founder/one-pager.md` for someone deciding in two minutes: the problem, the
customer, the offer and price, the numbers table, the evidence (panel result,
competitor gap, any real test), what the money is for, and the ask. Same numbers as
the plan, word for word. If the reader is a bank, add the legal form, the NIB and
the collateral or guarantee available; do not promise a loan programme's terms
without linking them.

## Rules

- The verdict comes from `compile.py`. Never write Profitable by hand, and never
  round a failing number into a passing one.
- Say once, clearly: the panel is simulated buyers and the numbers are projections;
  real customers and real quotes confirm them. Not financial, legal or tax advice.
- If the user wants a PDF, a Word file or a deck, offer to export the plan, but keep
  the markdown as the source of truth.

## Output

`founder/summary.md`, `founder/business-plan.md`, `founder/one-pager.md`,
`founder/profile.md`. Then give the user the verdict in one line and the one thing
to do this week. After opening, the run skills take over: `/founder-weekly-report`
every Monday, `/founder-pnl` and `/founder-cashflow` each month.
