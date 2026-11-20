---
name: founder-ops
description: >-
  Your operations manager, for Indonesia. Works out how the business actually
  runs on day one: suppliers (pasar induk, distributors, makloon and OEM makers,
  importers) and what they cost, who works when at the local UMK with BPJS and
  THR, the step-by-step routines for opening, serving or packing and shipping, and
  closing, the tools to run it (POS with QRIS, marketplace and delivery-app
  dashboards, bookkeeping), the permits to get through OSS (NIB, KBLI, PIRT, BPOM,
  halal, SLHS, signage), and a risk register (floods, mudik, platform fee changes,
  a bad review). Feeds real costs back to the CFO. Use when the user says "how do I
  run this", "operations", "suppliers", "staffing", "SOP", "what do I need to
  open", "perizinan", "permits", or "day one".
argument-hint: "[city or region]"
---

# founder-ops

A plan that works on paper fails at 6am on a Monday. This skill makes sure the
first day, week and month can actually be run, and that the CFO's numbers include
what running it really costs.

## Step 1: what the business has to do every day

From `founder/idea.md`, `founder/offer.md` and `founder/numbers.json`, write the
daily cycle as a list of steps from first thing to last (for a café: deliveries,
prep, open, serve counter and app orders, clean, cash up and reconcile QRIS and
app payouts, order; for an online store: orders in from each marketplace and
WhatsApp, pick, pack, hand to the courier, returns and complaints, restock; for a
service: bookings, the job, invoice, follow-up). Mark which steps a customer sees.

## Step 2: suppliers

For every input in the CFO's variable costs and every piece of equipment: two or
three real suppliers the user can contact (local distributors, the pasar induk,
makloon or OEM producers for private-label products, wholesale on the
marketplaces, importers), their public prices or how to get a quote, minimum
orders, lead times, payment terms (cash, tempo 7/14/30 days, consignment) and
whether they issue invoices the accountant can use. Link the sources. Where only a
quote will tell, say so and add it to the open questions. If a real price differs
from `founder/numbers.json`, update it and say the CFO should re-run.

## Step 3: people

Who does what, when: a weekly rota for the planned volume and for the slow first
month, and the weeks around Lebaran when staff go home. The roles, the hours (40
a week, 6 x 7 or 5 x 8), and the wage assumption: the UMK for the city from the
governor's or regent's decree (linked), or the agreed wage for a micro business,
plus employer BPJS, THR and overtime rules from
`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/payroll.md`. Contract type
(PKWT, PKWTT, daily) and what each costs at the end. Flag the details for the
accountant.

## Step 4: routines (SOPs)

Short, numbered routines for the moments that make or break the business: opening,
the core service or fulfilment, handling a complaint (including a public review on
Google Maps or the marketplace), closing and cashing up, and a weekly reorder.
Each fits on one page someone could follow on their first day. Write them in
Indonesian if the team reads Indonesian; keep the English summary in `ops.md`.

## Step 5: tools

The smallest stack that runs it: payments (QRIS, the EDC if needed), point of
sale (with the delivery apps connected if possible), the marketplace seller
centres, scheduling, bookkeeping, inventory, WhatsApp Business. Real products with
their published prices, and why each.

## Step 6: licences, permits and insurance

A checklist of what this business needs, from
`${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/permits.md`: the legal form,
the NIB and the right KBLI on OSS, tax registration, PIRT or BPOM, halal (and the
deadline that applies), SLHS, signage, the building's own rules, BPJS
registration, trademark filing. For each: where to apply (the official page),
the cost, the lead time and what must be ready first. Put the lead times into the
launch countdown. Say plainly that rules differ by region and change, and the user
must confirm each with the office or a professional. Not legal advice.

## Step 7: risk register

The ten things most likely to go wrong (a supplier runs out or raises prices, a
key person does not come back after mudik, the QRIS or POS goes down, the
delivery app or marketplace changes its fees or ranking, a flood, a bad review
goes viral, a slow Ramadan, a power cut), each with how likely, how bad, and the
plan.

## Output

`founder/ops.md`, plus updated `founder/numbers.json` if real costs changed. Next:
`/founder-launch`.
