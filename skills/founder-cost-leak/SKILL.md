---
name: founder-cost-leak
description: >-
  Finds the materials or stock used up faster than sales explain, by comparing
  what was bought (and the stock count) with what should have been used for what
  was sold: recipes for F&B, a bill of materials for products made in-house, one
  unit per unit for retail and online sellers. Ranks the five biggest gaps in
  Rupiah, separates price rises from waste and shrinkage, and gives a field check
  for each, without accusing anyone. Use when direct cost (food cost, COGS) is
  above the threshold, when the owner suspects non-standard portions, waste,
  missing stock or theft, or when purchase prices rose and the owner does not know
  which items are hit. Phrases: "which material is wasted", "bocor", "stock is
  missing", "why is buying up when sales are flat".
argument-hint: "[month]"
---

# founder-cost-leak

## When to use

- Last month's direct cost % is above the threshold in `founder/profile.md`
  (default 35% for F&B; ask for other businesses).
- The owner asks "what are we wasting", "why is buying up when sales are the
  same", "is stock going missing".
- After `/founder-pnl` finds a high direct cost.

This skill **does not accuse people**. The result is a list of items with the
biggest gaps and likely causes that can be checked. Who is responsible is for the
owner to decide after checking on the ground.

## The data

| source | required columns | notes |
| --- | --- | --- |
| Purchases | date, item, quantity, unit, total Rp | one full month, one outlet or warehouse |
| Sales per item | product or menu item, quantity sold | from the POS, the delivery apps and the marketplaces, same period |
| Usage per unit sold | product, the main materials, quantity per unit, unit | **F&B**: a rough recipe, 2 to 3 main ingredients per menu item is enough. **Made in-house**: the bill of materials. **Retail / online**: 1 unit of stock per unit sold (plus packaging per order if it matters) |
| Stock (optional) | item, opening stock, closing stock, unit | with it, actual usage is far more accurate |
| Waste and returns (optional) | date, item, quantity, value, reason | from a daily waste form, the returns log or the marketplace returns; explains part of the gap |

If there is no recipe or bill of materials at all, ask the owner to fill a rough
table for the **10 best sellers only**. Do not continue with made-up quantities. If
the owner insists, use common quantities and label every affected number
**(assumed quantity)**.

Units must match. If purchases are in kg and recipes in grams, convert first and
write the conversion.

## Steps

For each item in the usage table:

1. **Expected usage** = sum of (quantity sold x quantity per unit) across every
   product that uses it.
2. **Actual usage** = opening stock + purchases - closing stock. Without stock:
   actual usage = purchases, labelled (no stock count).
3. **Gap (quantity)** = actual usage - expected usage.
4. **Gap %** = gap / expected usage.
5. **Gap (Rp)** = gap x the month's average purchase price (total Rp bought /
   total quantity bought).
6. Sort by **gap in Rupiah**, biggest first. Take the top 5.
7. For each of the top 5, check the **purchase price**: the average in the first
   week against the last week. A rise above 10% is reported separately as "price
   rise", not "waste".
8. If waste and returns data exist: subtract the recorded waste for each item. The
   rest is the **unexplained gap**, and that is what gets reported as worth
   checking. Recorded waste has its own column.

A normal gap for fresh ingredients is 5 to 10% (trimming, shrinkage, tasting); for
packaged retail stock, close to 0 to 2%. Above 15% for fresh, or above 3% for
packaged, is worth checking. A large negative gap (actual far below expected) is
also a finding: the recipe is wrong, portions were cut, or sales are missing from
the POS.

## Likely causes (pick the best fit, more than one is fine)

| pattern in the data | likely cause | how to check on the ground |
| --- | --- | --- |
| The gap is spread across all protein or main materials | non-standard portions or usage | weigh 5 random portions or builds against the recipe |
| A big gap in 1 or 2 expensive items only | unrecorded waste, or used for something else | check 7 days of the waste form, staff meals, samples and giveaways |
| Packaged stock missing, sales flat | shrinkage, theft, or orders sent but not recorded | count stock today; match marketplace orders against shipments and returns |
| Purchases up, sales flat, no closing stock | stock piling up or expiring | count physical stock today, check expiry dates |
| Average purchase price up more than 10% | the supplier raised prices, selling prices have not followed | compare 2 suppliers, review prices with `/founder-product-mix` |
| A large negative gap | the recipe or BOM does not match practice, or sales did not go through the POS | ask the head cook or the packer, check manual transactions |
| The gap appears only on certain dates | a specific event (a bazaar, a shift, a flash sale) | match against the roster and the order log for those dates |

## Verification rules (required)

- Show the calculation table for the top 5 items with every column: expected,
  actual, gap quantity, gap %, gap Rp, source rows.
- Compare the top 5's total gap in Rupiah with the total direct-cost gap (actual
  direct cost - direct cost if everything matched the recipe or BOM). If the top 5
  explain less than 50% of the total gap, say so and name where the rest is.
- Never name employees or shifts, never allege theft. Write "worth checking" and
  how to check.
- If some products sold have no recipe or BOM, give their count and their share of
  sales. If more than 20% of sales have none, label the title **(low recipe
  coverage)**.

## Output format (fixed)

```
COST LEAK CHECK: [Business], [Month Year]
Recipe/BOM coverage: xx% of sales | Direct cost this month xx.x% (benchmark xx-xx%)

TOP 5 ITEMS BY GAP
| Item | Expected | Actual | Gap | Gap % | Gap Rp | Likely cause |
| ... |
Top 5 total gap: Rp xxx.xxx (xx% of the total direct-cost gap of Rp xxx.xxx)

PURCHASE PRICES THAT ROSE
[item, price at the start -> end of the month, % rise, products affected] or "No rise above 10%"

3 FINDINGS
1. ...
2. ...
3. ...

1 ACTION THIS WEEK
[one concrete field check: which item, who checks, when, where the result is recorded]

1 NUMBER TO DOUBLE-CHECK
[usually: the recipe quantity of the item with the biggest gap, or the closing stock]

Source: [tabs and rows]
```

## Thresholds the owner can change (in founder/profile.md)

- Normal gap % (default 10% fresh, 2% packaged)
- Gap % worth checking (default 15% fresh, 3% packaged)
- Purchase price rise to report (default 10%)
- Number of items shown (default 5)
