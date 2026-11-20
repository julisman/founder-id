---
name: founder-offer
description: >-
  Builds an offer too good to refuse, for Indonesian buyers. Lists every problem
  the buyer hits on the way to the result they want, turns each into a solution,
  trims to what is cheap to deliver and valuable to the buyer, and stacks it with
  honest bonuses, a guarantee the CFO can afford, real urgency and a clear name.
  Uses the trust tools that matter locally (halal and BPOM status, COD, a real
  address, a WhatsApp number that answers, easy returns) and avoids training
  buyers to wait for promos. Scores it on the value equation and re-tests it on a
  quick buyer panel. Use when the user says "make my offer better", "why won't
  people buy", "what should I include", "guarantee", "bonus", "paket", "grand slam
  offer", or after the panel shows people passing.
argument-hint: "[what you sell]"
---

# founder-offer

Most businesses sell a product. Good ones sell an offer: the product plus
everything that makes buying it an easy yes. This skill builds that, using the
Offers lens in `${CLAUDE_SKILL_DIR}/../founder-board/lenses.md` as the method (a
summary of the framework in Alex Hormozi's *$100M Offers*; never present it as
his words), with the Local market lens in the same file as the check.

## Step 1: read what is already known

- `founder/idea.md` and `founder/pitch.md`: what is sold today.
- `founder/panel/results.md`: why buyers pass, in their words. This is the raw
  material: every top objection should be answered by something in the offer.
- `founder/competitors.md`: what competitors' customers complain about.
- `founder/numbers.json`: what each extra costs, so the stack stays profitable.
- `founder/board.md`: the board's conditions.

## Step 2: the problem list

Write every obstacle between the buyer and the result they want, in the buyer's
words: before buying (doubt, price against the promo they already have, "is it
halal / is it original / is it safe", effort to switch, how to pay), during
(waiting, delivery time, learning), after (does it last, what if it is wrong or
broken, can I return it). Aim for 15 to 30. Pull from the panel objections and
the competitor complaints first.

## Step 3: solutions, trimmed and stacked

Turn each problem into a solution (a feature, a service, a guarantee, a format, a
payment option). Score each on value to the buyer (1 to 5) and cost to deliver
(1 to 5, from the CFO's numbers). Keep high value, low cost. Stack what is left
into:

- **The core**: the thing itself, described by the outcome, not the ingredients.
- **Bonuses**: two or three, each killing one specific objection.
- **Trust**: the proof that answers "can I trust a new seller": certificates the
  business really holds, a real address and Google Maps pin, COD or a marketplace's
  buyer protection for first orders, a WhatsApp number that answers.
- **The guarantee**: what happens if it does not deliver (replace, refund, redo).
  Model what it costs at a realistic claim rate with the CFO's tool before
  promising it.
- **Urgency and scarcity**: only if they are true (a launch week, a limited first
  batch, a pre-order window). Never fake a countdown or "sisa 3".
- **The name**: a clear, specific name for the offer, not the company.

Prefer bundles, bonuses and loyalty (stamp cards, member prices, reseller
tiers) to price cuts: they lift the value without teaching buyers the real price
is the promo price.

## Step 4: score it

On the value equation, before and after, 1 to 10 each: dream outcome, perceived
likelihood of getting it, time to the result, effort and sacrifice. Say which
element of the stack moves which score.

## Step 5: re-test it

Write the new offer into `founder/pitch.md` (keep the old one as
`founder/pitch-v1.md`) and run `/founder-consumer --quick` with the same seed.
Report the buy rate before and after and which objections dropped. If nothing
moved, say so: the problem may be the market or the price, not the offer.

## Rules

- Every promise must be deliverable and affordable; check costs with the CFO.
- No fake reviews, testimonials, sold counts, scarcity, discounts or "as seen on".
- Claim only the certificates the business holds (halal, BPOM, PIRT, SNI). Follow
  the consumer-protection and advertising rules in
  `${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/permits.md`. Not legal advice.

## Output

`founder/offer.md` (problem list, the stack, costs, the value-equation scores, the
re-test result) and the updated `founder/pitch.md`. Next: `/founder-cfo` to re-run
the numbers with the stack, then `/founder-marketing`.
