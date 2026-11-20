---
name: founder-launch
description: >-
  Your launch lead, for Indonesia. Builds a dated, step-by-step launch plan: a
  cheap real-world test first (a WhatsApp pre-order with a bank transfer, a stall
  at a weekend market or car-free day, a test listing on Shopee or TikTok Shop, a
  pop-up in an office lobby, three paid pilot clients), so real buyers confirm what
  the simulated panel said; then the countdown to opening day with owners and
  deadlines, built around permit lead times, the payday cycle and Ramadan; the
  launch-day run sheet; and the first 30 days of what to measure and what to
  change. Use when the user says "how do I launch", "launch plan", "when can I
  open", "launch checklist", "go live", "grand opening", or "soft open".
argument-hint: "[target launch date]"
---

# founder-launch

Launching is a project with a date. This skill turns everything else in the pack
into a dated plan, and starts with the cheapest way to find out if real people
will pay before the big money goes out.

## Step 1: test before you spend

Pick the cheapest real test that fits the business, and run it before signing the
big costs in `founder/numbers.json` (the kiosk rent paid a year up front, the
machine, the first big stock order):

| business | the test |
| --- | --- |
| food and drink | a stall at a weekend market, car-free day or office bazaar; a pre-order list on WhatsApp with a price, a pick-up date and payment by transfer or QRIS |
| physical product | a small batch on Shopee or TikTok Shop, or a pre-order through WhatsApp and Instagram with payment up front |
| cosmetics or packaged food | the above, only once the required PIRT, BPOM notification or halal step is done (`/founder-indonesia`) |
| service or agency | three paid pilot clients at the planned price |
| subscription or class | a founding-member batch, paid up front |

Write the success line before running it (for example: 80 pre-orders paid in two
weeks at Rp22.000), and compare the result with the panel's buy rate. If real
buyers fall well short of the panel, trust the real buyers and go back to
`/founder-offer` or `/founder-pricing`.

## Step 2: the countdown

From today to launch day, with real dates (ask for the target date; default to the
earliest realistic one given the permit and supplier lead times in
`founder/ops.md`). Check the date against
`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/calendar.md`: a launch just
after payday beats one in the lean days before it; avoid the mudik weeks; a
daytime food launch in the middle of Ramadan needs an iftar plan. Weekly blocks,
each task with an owner and a deadline:

- Legal and money: NIB on OSS, tax, a business bank account, QRIS, the permits and
  certificates from `founder/ops.md`, the trademark filing.
- Build: renovation or website, marketplace and delivery-app store set-up and
  approval (allow time for the platforms' review), suppliers ordered by their lead
  times.
- Brand: sign, packaging, profiles and store pages from `founder/brand.md`.
- Marketing: the calendar in `founder/marketing.md` from launch minus 14 days.
- Team: hiring, BPJS registration and training on the SOPs.
- A soft open or friends-and-family day before the public launch.

Mark the critical path: the tasks that move the launch date if they slip
(permits, platform approval and equipment delivery are the usual ones).

## Step 3: launch day

An hour-by-hour run sheet: who is where, what goes out on which channel, the
opening offer, how app and marketplace orders are handled next to walk-ins, and
what to do if something breaks (from the risk register: the QRIS is down, the app
order queue overflows, stock runs out by noon).

## Step 4: the first 30 days

The weekly numbers to track (from the CFO: units a day against break-even; from
marketing: the channel numbers; from the platforms: rating and cancellation rate),
the level that triggers a change, and a review on days 7, 14 and 30 with the
questions to answer. From week 1, run `/founder-weekly-report` every Monday.

## Output

`founder/launch.md` with the test, the countdown, the run sheet and the 30-day
review. Next: `/founder-plan` compiles everything into the business plan.
