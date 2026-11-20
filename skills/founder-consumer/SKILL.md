---
name: founder-consumer
description: >-
  The consumer panel, for Indonesian buyers. Spins up a swarm of buyer sub-agents
  (default 100, --quick for 20) drawn from the user's target customer, each with a
  monthly income in Rupiah, an age, a region, a buying habit (promo hunter, orders
  on the app, loyal to a chain, payday treat...) and an objection, shows every one
  the same pitch, and tallies who buys, who doesn't, and why. Built to resist the
  polite yes ("boleh juga", "nanti deh") that makes simulated and real Indonesian
  buyers look keener than they are. Returns buy rates by segment, behaviour,
  income and region, the reasons people pass in their own words, what would flip a
  no, and price answers for founder-pricing. Use when the user says "would people
  buy this", "test it on customers", "run the consumer panel", "simulate buyers",
  "who is my customer", "validasi pasar", or "validate demand".
argument-hint: "[--n 100 | --quick] [--seed S]"
---

# founder-consumer

Instead of guessing whether people will buy, you ask a hundred of them, each one
a sub-agent playing a specific buyer drawn from your target customer. You are the
moderator. You never answer for a buyer.

What the user typed after `/founder-consumer`: `$ARGUMENTS`

## The tool

All bookkeeping goes through `panel.py` in this skill's folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/panel.py" <command>
```

Below, `PANEL` means exactly that. If the path is not expanded, use the base
directory Claude Code printed for this skill. State lives in `founder/panel/`.

## Step 1: the target customer

Write `founder/customer.json` (shape: `customer.example.json` in this folder):

- `business`, and `target`: who the customer is, in one specific line.
- `currency`: `IDR`. `income_period`: `month` (Indonesians think in monthly pay).
- `segments`: 2 to 4 groups with a `share` and a monthly `income` range
  [low, high] in Rupiah. Anchor the ranges on something real: the local UMK
  (`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/payroll.md`), BPS data for
  the region, or what the user knows about their buyers.
- `behaviours`: 4 to 8 buying behaviours with a `share` and a `how` line. Common
  Indonesian ones: promo hunter (e-wallet cashback, vouchers, flash sales), orders
  on the app, checks TikTok or Instagram first, loyal to a big chain or a regular
  warung, payday treat, COD only, buys through a reseller, checks halal or BPOM
  first, buys in bulk for the family.
- `objections`: the 4 to 8 doubts this kind of buyer really has.
- `regions` (optional): for a business selling across regions, a list of
  `{name, share}` (for example Jabodetabek 0.4, other Java 0.35, outside Java
  0.25). Leave it out for a single-location business; `where` is used instead.
- `habits` (optional): everyday context lines that make a buyer concrete.

Ground it in something real. Use what the user knows about their customers, and
if `/founder-competitors` ran, the complaints in `founder/competitors.md`. If the
user has real customer data (interviews, reviews, survey answers, WhatsApp
chats), prefer it to your guesses and say which parts are guesses. Show the user
the profile in a few lines and let them correct it before you deal: a wrong
customer makes the whole panel wrong.

## Step 2: the pitch

Write `founder/pitch.md`: what a buyer would actually see. The product, the price
in Rupiah, where and how to get it (the counter, which apps, which marketplace,
WhatsApp), how to pay, any opening offer. Three to six plain lines, no
superlatives, nothing the business cannot deliver. Every buyer sees exactly this.

## Step 3: deal and run

```bash
PANEL init --customer founder/customer.json --pitch founder/pitch.md --n 100
PANEL prompts
```

`init` deals the persona cards (same seed, same cards; the seed is recorded).
`prompts` writes one brief per buyer and lists them in waves of 10. For each wave,
send ONE message with one Agent tool call per buyer in that wave:

- `subagent_type`: `general-purpose`
- `description`: `panel <id>`
- `prompt`: `Read <brief path> and follow it exactly. It is your whole brief.`

Wait for the whole wave before the next one. After the last wave:

```bash
PANEL check      # lists missing or broken answers
PANEL prompts    # rewrites briefs for those only; run them once more
PANEL tally
```

If a buyer printed its JSON in its reply instead of writing the file, file its
own reply with `PANEL save <id>` and the reply on stdin; `save` refuses anything
that is not a valid answer. A buyer that fails twice is left out and counted in
the results. Never write an answer for a buyer yourself.

Before a 100-buyer run, tell the user it is 100 sub-agent calls and suggest
`--quick` (20 buyers) for a first look. Sub-agents write one file each into
`founder/panel/answers/`; in the default permission mode that is one approval per
file, so suggest accept-edits mode (Shift+Tab) for the run.

## Step 4: read it to the user

`PANEL tally` writes `founder/panel/results.md` and `results.json`. Give the user:

1. The headline: "40 buy · 60 pass" and the buy rate.
2. Who buys and who doesn't: the segment, behaviour, income and region rows that
   differ most.
3. Why they pass: the top three reasons with one quote each, as written.
4. What would flip a no: the most repeated answers.
5. One sentence on what to change before spending money, and which skill does it
   (pricing, offer, marketing).

## Honest limits, say them once

These are simulated buyers. They are good at surfacing objections, segments and
wording you had not thought of, and bad at predicting real conversion: language
models lean agreeable, and Indonesian politeness pushes real answers the same way,
so treat the buy rate as an upper bound. Confirm the big calls with real people
(a pre-order through WhatsApp with a transfer, a stall at a weekend market, a
small test listing on Shopee) before signing anything. Do not present panel quotes
as customer testimonials.

## The brief every buyer gets

`panel.py` fills the card into a fixed template (see `BRIEF` in the script): who
the buyer is (name, age, segment, monthly income in Rupiah, region, buying
behaviour, a habit, the doubt that comes to mind), the pitch word for word, an
instruction that a polite maybe is a no and not to invent facts, a nudge to think
about payday and the promos they already know, and the exact JSON to write: buys,
purchases in the first month, a reason code, the reason in their own voice, their
main objection, what would change their mind, and four price answers in Rupiah
(too cheap, a bargain, getting expensive, too expensive). Never edit a brief for
one buyer.

## Output

`founder/customer.json`, `founder/pitch.md`, `founder/panel/` (cards, briefs,
answers, results). Next: `/founder-pricing` reads the price answers,
`/founder-offer` and `/founder-marketing` read the objections.
