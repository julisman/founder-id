---
name: founder-product-mix
description: >-
  Maps every product, menu item or service into four quadrants by margin per unit
  (after the channel's commission) and volume sold: Stars (keep), Plowhorses
  (raise the price or cut the cost), Puzzles (promote), Dogs (drop or redo). Gives
  an action per quadrant and new prices rounded the way Indonesian buyers read
  them, capped at 10% per round. Menu engineering for F&B, product-mix analysis
  for retail and online sellers, service-mix for service businesses. Use when the
  owner wants to know which items really make money, wants to raise prices, wants
  to trim the menu or the catalogue, or after purchase prices rose. Phrases: "which
  menu makes the most", "what should I drop", "which prices should go up".
argument-hint: "[period]"
---

# founder-product-mix

## When to use

- The owner asks "which items make the most money", "which should I drop", or
  "which prices should go up".
- After purchase prices rose and the owner wants to know whose margins shrank.
- Every 3 months, or when designing a new menu, catalogue or price list.

## The data

| source | required columns | notes |
| --- | --- | --- |
| Item sales | item name, category, selling price, quantity sold, total sales, channel | at least 1 month, 3 is better; from the POS, delivery apps and marketplaces |
| Cost per unit | item name, direct cost per unit (Rp) | F&B: from recipe x ingredient prices. Retail: the landed purchase cost. Services: materials + direct labour time x hourly cost |
| Channel fees | commission and fees per channel | from the P&L or `founder/numbers.json`, so an item sold mostly on an app is judged after the app's cut |

If unit costs are missing, help the owner calculate them for the **20 best
sellers** first. Items outside those 20 go in with the label **(cost estimated from
the category average)**.

Keep categories that are not comparable apart: food, drinks and snacks; or for a
shop, the product categories with different margins (accessories vs the main
product). Drinks and accessories almost always carry high margins, so they are
analysed in their own group, otherwise everything else looks bad.

## Steps

Per category:

1. **Margin per unit** = average actual selling price - cost per unit - channel
   fees per unit. (Average actual selling price = total sales / quantity, so
   discounts and promo prices count.)
2. **Margin %** = margin per unit / average selling price.
3. **Total margin** = margin per unit x quantity sold.
4. **Volume line** = average quantity sold per item in the category x 0.7 (0.7
   because sales are almost always skewed to a few best sellers; the owner can
   change it).
5. **Margin line** = the weighted average margin per unit in the category (total
   margin / total quantity).
6. Place each item:

| quadrant | volume | margin | name | default action |
| --- | --- | --- | --- | --- |
| A | at or above the line | at or above the line | **Star** | keep; do not touch the recipe or spec; show it most prominently |
| B | at or above the line | below the line | **Plowhorse** | raise the price gradually or cut the cost (portion of sides, packaging, a cheaper supplier) |
| C | below the line | at or above the line | **Puzzle** | promote it, move it up the menu or the store page, bundle it with a Star |
| D | below the line | below the line | **Dog** | drop it, or redo it completely; do not promote it |

7. **New prices** for quadrant B: the price that brings the margin % to the
   category's margin line, rounded the way buyers read prices (Rp500 steps under
   Rp20.000, Rp1.000 above; for retail and online, endings like Rp49.900 or
   Rp99.000 if the store already uses them), capped at a 10% rise per round. Show
   the Rupiah rise per unit and the effect per month = rise x quantity sold x 0.9
   (assuming 10% fewer buyers; the owner can change it). If an item is sold on a
   delivery app or marketplace, check the platform's rules on price differences.
8. **Effect of dropping quadrant D**: the total margin lost per month (usually
   small) against the materials or stock that no longer need to be held (name
   items used only by D products).

## Verification rules (required)

- The total sales in your table must equal the export's total. If not, state the
  difference and likely causes (items with no category, voids, modifiers or
  add-ons, bundles).
- Show the volume and margin lines used per category with their formulas, so the
  owner can move them.
- Mark items with estimated costs in the table. Do not recommend dropping an item
  whose cost is estimated; recommend calculating its cost first.
- New items (selling for less than 4 weeks) do not go into quadrant D. Label them
  (new, wait for data).
- Do not recommend raising any price more than 10% at once unless the owner asks.

## Output format (fixed)

```
PRODUCT MIX: [Business], [period]
Category: [Food] | Volume line xx units/month | Margin line Rp xx.xxx/unit

QUADRANT MAP
Stars (keep):              [item, item, item]
Plowhorses (raise price):  [item, item]
Puzzles (promote):         [item, item]
Dogs (drop or redo):       [item]

FULL TABLE
| Item | Qty | Avg price | Unit cost | Channel fee | Margin/unit | Margin % | Total margin | Quadrant | Note |

NEW PRICES (quadrant B)
| Item | Price now | Proposed | Rise | New margin % | Effect/month |

EFFECT OF DROPPING QUADRANT D
Margin lost Rp xxx.xxx/month | Stock no longer needed: [...]

[repeat for each category]

3 FINDINGS
1. ...
2. ...
3. ...

1 ACTION THIS WEEK
[usually: raise the price of 1 to 3 quadrant B items, or move 1 Puzzle to the top of the menu or store page]

1 NUMBER TO DOUBLE-CHECK
[the unit cost of the item with the largest total margin, because an error there moves everything]

Source: [export file, rows, period]
```

## Save the report

After showing the report, save it so next time (and the founder-id dashboard) can
use it. Two files in `founder/reports/product-mix/`, named by the month or period:

- `2027-01.md`: the report exactly as shown above.
- `2027-01.json`: its key numbers, in this shape (money in full Rupiah as plain
  numbers, percentages as fractions: 0.45 means 45%):

```json
{
  "period": "2027-01",
  "items": [
    {"item": "Es kopi susu gula aren", "category": "drinks", "qty": 3100, "avg_price": 22000,
     "unit_cost": 9700, "channel_fee": 1760, "margin_unit": 10540, "total_margin": 32674000,
     "quadrant": "star", "new_price": null},
    "... every item analysed"
  ]
}
```

Get the paths with `python3 "${CLAUDE_SKILL_DIR}/../founder-weekly-report/reports.py"` `path product-mix 2027-01`, write both files, then run
`python3 "${CLAUDE_SKILL_DIR}/../founder-weekly-report/reports.py"` `check founder/reports/product-mix/2027-01.json`. It checks that total_margin = qty x margin_unit, quadrant is star, plowhorse, puzzle, dog or new.
If it reports a problem, fix the numbers (never the check) and say what changed.
Copy numbers from the report; do not compute new ones for the JSON.

## Thresholds the owner can change (in founder/profile.md)

- Volume line multiplier (default 0.7)
- Largest price rise per round (default 10%)
- Buyers lost after a price rise (default 10%)
- Price rounding (default Rp500 under Rp20.000, Rp1.000 above)
- Age of new items excluded from quadrant D (default 4 weeks)
