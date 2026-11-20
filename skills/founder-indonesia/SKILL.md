---
name: founder-indonesia
description: >-
  The Indonesia desk for the founder-id pack. Answers what a business in
  Indonesia must register, pay, collect and plan for: OSS-RBA and the NIB, KBLI
  codes, PIRT, BPOM, halal certification, PPh Final UMKM 0.5%, PPN and the PKP
  threshold, PBJT (ex-PB1) restaurant tax, UMP/UMK wages, BPJS, THR, QRIS and
  e-wallet fees, delivery-app and marketplace commissions, and the calendar that
  moves sales (Ramadan, Lebaran, mudik, payday, 11.11 and 12.12). Every other
  founder skill reads its reference files. Use when the user asks "what permits do
  I need", "what tax do I pay", "do I need halal", "how much is BPJS", "when is
  THR due", "what does GoFood take", or "is this legal to sell in Indonesia".
argument-hint: "[topic: tax | permits | payroll | payments | calendar | sources]"
---

# founder-indonesia

The country layer of the pack. The method in the other skills (board, panel, CFO,
plan) works anywhere; this skill holds what is specific to Indonesia so the
others do not guess it.

What the user typed after `/founder-indonesia`: `$ARGUMENTS`.

## The reference files

All in `${CLAUDE_SKILL_DIR}/reference/` (if that path is not expanded, use the
base directory Claude Code printed for this skill):

| file | what is in it |
| --- | --- |
| `reference/tax.md` | PPh Final UMKM, PPN and PKP, PBJT/PB1, PPh 21, deadlines, what is revenue and what is a pass-through |
| `reference/permits.md` | business forms, OSS-RBA and NIB, KBLI, PIRT, BPOM, halal, SLHS, trademarks, domains, e-commerce and advertising rules |
| `reference/payroll.md` | UMP/UMK, the micro and small business wage rule, BPJS rates, THR, overtime, contracts |
| `reference/payments-channels.md` | QRIS fees, e-wallets, COD, paylater, delivery apps, marketplaces, logistics, government procurement |
| `reference/calendar.md` | Ramadan and Lebaran dates, mudik, payday cycle, shopping festivals, school year, rainy season |
| `reference/sources.md` | the official sites to confirm each item, and where to find market data |

Read only the file the question needs.

## How to answer

1. **Find the business type first**: what it sells (food and drink, physical
   goods, cosmetics, services, digital), where (one city, online nationwide), the
   legal form (individual, PT Perorangan, CV, PT) and the expected yearly turnover.
   Most rules turn on these four facts. Ask for any that are missing (at most three
   questions).
2. **Answer from the reference file**, then **confirm the numbers that change**
   (rates, thresholds, deadlines, platform fees) on the official source in
   `reference/sources.md`, with the link and the date you checked. The reference
   files are dated; anything marked *check* changes often.
3. **Say what applies and what does not**, as a checklist with the official page
   for each item.
4. If the founder pack is running, write the result where the other skills read
   it: costs go into `founder/numbers.json` (via `/founder-cfo`), permits and
   lead times into `founder/ops.md` (via `/founder-ops`).

## Rules

- Regional rules differ. PBJT rates and thresholds, UMK, signage permits and
  zoning are set by each province, regency or city. Name the region and check its
  own regulation (Perda, Pergub, Perbup/Perwal).
- Never present a remembered rate as current. If the official page cannot be
  reached, say so, give the dated figure from the reference file, and mark it
  *to confirm*.
- Not legal or tax advice. Say once that a tax consultant (konsultan pajak), a
  notary or the relevant office (KPP, DPMPTSP, Disnaker, BPJPH) confirms it.

## Output

An answer in the conversation, with links. When run inside the pack, the updates
to `founder/numbers.json` and `founder/ops.md` named above.
