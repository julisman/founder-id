---
name: founder-competitors
description: >-
  Maps every competitor and the gap they leave, for a business in Indonesia.
  Finds the direct competitors, the indirect ones and the substitutes a buyer
  would use instead (including the informal ones: the warung, the kaki lima, the
  home seller on WhatsApp, the reseller on Shopee), from public sources only:
  Google Maps, GoFood/GrabFood/ShopeeFood menus, Shopee and Tokopedia/TikTok Shop
  listings, Instagram, TikTok, review sites and news. Records what each sells, at
  what price, how they position themselves and what their customers complain
  about, every fact with a link. Ends with a positioning map and the gap the new
  business can own. Use when the user says "who are my competitors", "is this
  market crowded", "competitor analysis", "kompetitor", "find the gap", or "who am
  I up against".
argument-hint: "[city, area or channel]"
---

# founder-competitors

Every buyer already solves this problem somehow. This skill finds out how, what
they pay, and what they hate about it, so the new business starts with a gap
instead of a guess.

## The rules

- **Public sources only, every fact linked.** Websites, menus and price lists,
  Google Maps listings, delivery-app menus, marketplace listings and ratings,
  Instagram and TikTok profiles, app store pages, news. If a source cannot be
  reached, say so. Never invent a competitor, a price, a rating or a review.
- **Read, do not scrape.** Read pages as a person would. Respect each site's terms.
- **Quotes are verbatim** (in Indonesian if that is how they were written, with a
  short English gloss), with the link. They are research, never testimonials.
- **Record the price and the channel together.** A drink on GoFood often costs more
  than at the counter; a marketplace price may include a voucher. Say which.

## Step 1: who is there

From `founder/idea.md` (write it first if missing; see `/founder-board` step 0):

| type | what it means | example for a kopi susu kiosk |
| --- | --- | --- |
| Direct | sells the same thing to the same buyer | other kopi susu counters and chains within walking distance and on the apps |
| Indirect | a different product for the same job | the minimarket's ready-to-drink coffee, tea chains, the office pantry |
| Informal | small, unregistered or home-based sellers | the kopi keliling bicycle, the warung's sachet coffee |
| Substitute | how buyers solve it without a business | sachet coffee at home, bottled coffee bought in bulk |

Aim for 5 to 10 direct and indirect, the informal ones a buyer actually uses, and
the main substitutes. For a local business, search the map and the delivery apps
for the exact area; for online, search the marketplaces and TikTok the way a
buyer would ("<thing> murah", "<thing> terbaik", "<thing> untuk <who>").

## Step 2: the facts

One row per competitor in `founder/competitors.csv`:

`name,type,url,location_or_channel,price_of_comparable_item,price_channel,what_it_sells,positioning_line,rating,review_count,trust_signals,source_date`

- `positioning_line` is their own headline, tagline or bio, copied.
- `price_of_comparable_item` is in Rupiah for the item closest to what the new
  business sells, with what it includes; `price_channel` says where that price
  was seen (counter, GoFood, Shopee with voucher...).
- `trust_signals`: halal logo, BPOM/PIRT number, official store badge, number of
  outlets, years open.

## Step 3: what their customers say

For the top 3 to 5, read their reviews on Google Maps and the marketplace or
app (1 to 3 stars first, then the "enak, tapi..." 4 stars) and the comments under
their TikTok and Instagram posts. Note recurring complaints as themes with counts
and one or two linked quotes each. Mark a theme thin if it has under three
reviews.

## Step 4: the map and the gap

Write `founder/competitors.md`:

1. The table (from the CSV), sorted by how directly each competes.
2. Price range: lowest, median, highest for the comparable item, by channel.
3. A positioning map in text: two axes that matter to this buyer (price and
   convenience, quality and speed, trust and price...), where each competitor sits.
4. The complaints, ranked, with links.
5. **The gap**: what nobody does well that this business could, tied to the
   evidence. If there is no gap, say so plainly; that is the most useful result
   this skill can give.
6. The threat: who could copy the new business fastest (a chain adding the item,
   a reseller cloning it on Shopee within weeks), and how.

## Output

`founder/competitors.csv`, `founder/competitors.md`. Next: `/founder-consumer`
uses the complaints to write real objections; `/founder-pricing` uses the price
range.
