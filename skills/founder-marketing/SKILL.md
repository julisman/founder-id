---
name: founder-marketing
description: >-
  Your marketing director, for the Indonesian market. Turns the buyer panel and
  the competitor map into positioning, the channels the target customer actually
  uses (TikTok and TikTok Shop, Instagram, WhatsApp Business, Google Maps,
  GoFood/GrabFood/ShopeeFood, Shopee and Tokopedia, local creators and KOLs,
  resellers, communities, the shopfront), a 30-day launch campaign with dated posts
  that respects the calendar (payday, Ramadan, twin-date sales), the first ten
  hooks, a budget split and the numbers to watch. Every message answers an
  objection real or simulated buyers raised. Use when the user says "how do I
  market this", "marketing plan", "launch campaign", "how do I get customers",
  "where do I advertise", "write my ads", "konten", or "positioning".
argument-hint: "[budget in Rupiah]"
---

# founder-marketing

A business no one hears about does not exist. This skill plans how the first
customers hear about it, using what the rest of the pack already learned instead
of a generic playbook.

## Step 1: read the evidence

- `founder/panel/results.md`: who buys, who doesn't, and why. The segments with the
  highest buy rate are the first audience. The top objections are what the
  marketing must answer.
- `founder/competitors.md`: how competitors position themselves (so you do not
  sound like them) and the gap.
- `founder/offer.md` and `founder/pricing.md`: what is being sold, at what price,
  per channel.
- `founder/numbers.json`: what a customer is worth, which caps what you can spend to
  win one.

If none of these exist, say what is missing and offer to run `/founder-consumer
--quick` first. Do not invent an audience.

## Step 2: positioning

One line, then the reasons:

```
For <the segment that buys most>, who <their problem in their words>,
<business> is the <category> that <the gap>, unlike <the nearest alternative>.
```

Give three versions, recommend one, and say which panel evidence supports it.
Write the customer-facing version in the language the buyers use (usually
Indonesian, casual or formal to match the brand).

## Step 3: channels

List where the first audience actually spends attention, specific to the business
type and place. The usual Indonesian options
(`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/payments-channels.md`):

- **Local**: the shopfront and signage, Google Maps and its reviews, the delivery
  apps' own promos and ads, office buildings, campuses, housing complexes,
  mosques and churches, arisan and community groups, partnerships with nearby
  businesses.
- **Social**: TikTok (short video, live, affiliates), Instagram (Reels, Stories),
  local creators and nano or micro KOLs paid in product or a fee.
- **Direct**: WhatsApp Business (catalogue, broadcast to opted-in customers,
  groups), loyalty stamps, referral codes.
- **Marketplace**: Shopee and Tokopedia/TikTok Shop ads, vouchers, flash sales,
  live selling; the reseller and dropshipper network for products.
- **Paid**: Meta and TikTok ads, Google Search and Maps ads.

For each: why it fits this buyer, rough cost, and how you will know it worked.
Pick two or three to start; say what you are not doing and why.

## Step 4: the 30-day campaign

`founder/marketing.md` gets a dated calendar from launch minus 14 days to launch
plus 16: what goes out each day, on which channel, with the message. Check the
dates against `${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/calendar.md`:
lead with the big pushes after payday, avoid launching a daytime food business in
the middle of Ramadan unless the offer is built for iftar, and plan around 11.11
and 12.12 for marketplace sellers. Include:

- **Ten hooks**, each answering one panel objection or using one buyer reason,
  written for the format (a 3-second opening line for TikTok, a headline for an
  ad, a line for the window, a WhatsApp broadcast opener).
- The launch-week offer from `founder/pricing.md` and when it ends.
- What to post when there is nothing new to say (behind the scenes, how it is
  made, the team, the neighbourhood, customer questions answered).

## Step 5: budget and numbers

- The budget split across the chosen channels, in Rupiah.
- The most you can pay to win a customer: from the CFO's contribution per unit
  (after the channel's commission) and the panel's purchases per buyer, show the
  sum.
- The three numbers to watch weekly and the level that means "change something"
  (for example cost per order from ads, the app's conversion rate, repeat orders
  in 30 days).

## Rules

- No fake reviews, sold counts, follower counts, testimonials, before/afters or
  "as seen on". No buying reviews on Google Maps or the marketplace.
- Panel quotes are research; never use them as customer quotes in ads.
- Disclose paid partnerships and affiliate links. Food, cosmetics and supplement
  claims must match what BPOM allows; halal only if certified. Only message people
  who opted in (UU PDP). See
  `${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/permits.md`. Not legal advice.

## Output

`founder/marketing.md`. Next: `/founder-brand`, then `/founder-launch`.
