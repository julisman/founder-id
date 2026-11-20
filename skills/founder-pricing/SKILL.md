---
name: founder-pricing
description: >-
  Finds the price Indonesian buyers will actually pay. Reads the consumer
  panel's four price answers per buyer into a Van Westendorp price-sensitivity
  range in Rupiah (too cheap, a bargain, getting expensive, too expensive), sets
  it against what competitors really charge on each channel (counter, GoFood,
  Shopee with voucher), against the platform's commission and against the CFO's
  margin, and recommends a price per channel, a price ladder and an opening offer
  that does not train buyers to wait for promos. Use when the user says "how much
  should I charge", "price this", "harga jual", "is Rp X too expensive", "pricing
  strategy", or after the consumer panel.
argument-hint: "[current price]"
---

# founder-pricing

Price is the fastest lever on the margin and the one founders guess most. This
skill sets it from four things you can check: what buyers said, what competitors
charge, what each channel takes, and what the business needs to earn.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/van_westendorp.py" founder/panel/answers --price 22000 --out founder/pricing-curve.md
```

It reads prices written as `22000`, `Rp22.000` or `22.000` (Indonesian thousands
dots) and reports in Rupiah (`--currency USD` for dollars).

## Step 1: what buyers said

If `/founder-consumer` ran, every buyer answered four price questions. Run the
tool on `founder/panel/answers` (or a CSV with the columns `too_cheap, cheap,
expensive, too_expensive` from a real survey, for example a Google Form sent to a
WhatsApp group, which beats simulated answers every time). It reports:

| point | meaning |
| --- | --- |
| PMC | below this, too many think it is too cheap to be good |
| OPP | the price with the least resistance either way |
| IPP | where as many call it a bargain as call it expensive |
| PME | above this, too many will not buy at all |

PMC to PME is the acceptable range. If the panel has not run, say so and offer to
run `/founder-consumer --quick` first. Do not invent a range.

## Step 2: what competitors charge

From `founder/competitors.md` (or look them up now, with links): the price of the
nearest substitutes for the same job, **per channel**. Compare like with like: the
counter price with counter prices, the app price with app prices, and the
marketplace price after the vouchers the buyer would actually get.

## Step 3: what each channel takes, and what the business needs

From `founder/numbers.json`: the variable cost per unit and the break-even. Add
each channel's cut (delivery-app commission, marketplace fees, payment fees; see
`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/payments-channels.md`, and
use the seller centre's real rate). Many businesses price higher on the apps to
cover the commission; check the platform allows it and say so.

Run the CFO's tool at two or three candidate prices to see the margin and
break-even at each:

```bash
python3 "${CLAUDE_SKILL_DIR}/../founder-cfo/unit_economics.py" founder/numbers.json --price 24000
```

## Step 4: decide

Write `founder/pricing.md`:

1. **The price**, per channel, and why: where it sits in the acceptable range,
   against the competitors, and the margin it gives (from the tool, not a guess).
   Round to prices people read easily (Rp22.000, Rp24.500, Rp49.900).
2. **The ladder**, if the business can have one: a good / better / best (size,
   bundle, paket hemat, subscription, reseller tiers) with a reason to step up each
   rung.
3. **The opening offer**: an intro price, a bundle or a bonus for launch with an
   end date. Prefer a bonus or a bundle to a deep discount: buyers who learn the
   price is always on promo wait for the promo.
4. **What to test with real buyers**: two prices inside the range and how to test
   them (two WhatsApp pre-order prices, two marketplace listings, the counter board
   on different weeks).
5. The panel's verbatim price objections (top three), so marketing can answer them.
6. Taxes on top: say whether PBJT or PPN will be added to the shown price, so the
   price the buyer sees is right
   (`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/tax.md`).

## Rules

- Price answers from simulated buyers pick what to test. They are not proof.
- Never price below variable cost (after the platform's cut) to "buy" customers
  without saying so, and how long the CFO says the business can afford it.
- No fake anchors: no "was Rp X" price that was never charged (UU 8/1999).

## Output

`founder/pricing-curve.md`, `founder/pricing.md`. If the price changed, update
`founder/numbers.json` and re-run `/founder-cfo`. Next: `/founder-offer`.
