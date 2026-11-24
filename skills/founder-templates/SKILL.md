---
name: founder-templates
description: Makes a ready-to-fill daily sales and purchases logbook (one Excel file that opens in Google Sheets and WPS, in Indonesian) plus matching CSV templates, for a small Indonesian business that has no POS or bookkeeping app yet, so /founder-weekly-report, /founder-pnl and /founder-cost-leak get clean data from day one. Pre-fills the channels, the platform commission rates, the purchase categories, the break-even per day and the direct-cost alert from founder/profile.md and founder/numbers.json when they exist. Use when the owner says "make a sales template", "purchase template", "template penjualan", "template pembelian", "catatan harian", "buku kas", "we don't have a POS yet", "how should the staff record sales", or before a test weekend, a soft open or the first weekly report.
---

# founder-templates

Many small businesses open with a notebook and a calculator. This skill gives them a logbook that already speaks the language of the run skills, so the Monday report takes three minutes instead of an evening of retyping receipts.

Tool in this folder (standard library only, nothing to install):

```bash
python3 "${CLAUDE_SKILL_DIR}/make_templates.py" --dir founder --type fnb
```

## What it makes

In `founder/templates/`:

| file | what it is |
| --- | --- |
| `catatan-harian.xlsx` | The logbook. Opens in Excel, Google Sheets (File, Import) or WPS. Five sheets, below. |
| `sales-template.csv` | The sales columns with English headers, for a tool that imports CSV |
| `purchases-template.csv` | The purchase columns with English headers |

The five sheets of the logbook:

| sheet | what the team does there |
| --- | --- |
| **Petunjuk** | Reads it once: how to fill it in, the colour legend, the rules (tax is not sales, the owner's drawings are not purchases, a missed day stays blank) |
| **Penjualan** | One row per day per channel. Types the date, picks the channel, then enters gross sales, discounts, the platform's fee and the number of transactions. The day name and net sales are formulas. An app fee left blank uses an estimate from the channel's rate. |
| **Pembelian** | One row per line on a supplier's invoice. Enters the supplier, item, category, quantity, unit and unit price, the payment (cash, QRIS, transfer or tempo), the due date, the invoice number and whether the supplier holds a halal certificate. The total is a formula. |
| **Ringkasan Minggu** | Types a Monday's date and reads the week. It shows each day against break-even, which days are blank, last week and the change, each channel's share, and purchases with direct cost % (labelled an estimate, no stock count). |
| **Daftar** | The dropdown lists and the settings: break-even per day, the direct-cost alert, the weekly target. All of them can be edited. |

Yellow cells with blue text are typed in. Grey cells are formulas. One green example row in each log shows the format, and the team deletes it.

## Step 1: read what the pack knows

Look for these files in `founder/`:
- `profile.md` (from `/founder-plan`)
- `numbers.json` (from `/founder-cfo`)
- `ops.md` and `pricing.md`

From them, take:

- the business name
- the channels actually used: walk-in cash, walk-in QRIS, WhatsApp pre-order, each delivery app or marketplace
- each platform's commission rate, from `numbers.json` `variable_pct` or the merchant contract
- purchase categories that match the CFO's variable costs and the ops supplier list
- the break-even per day, the direct-cost alert and the weekly target. The tool reads these from `profile.md` itself.

If there is no pack, ask for the business type and the channels, and leave the settings at 0 for the owner to fill in. **Never invent a break-even.**

## Step 2: build it

```bash
python3 "${CLAUDE_SKILL_DIR}/make_templates.py" --dir founder --type fnb \
  --business "Nama Usaha" \
  --channels "Walk-in (tunai)=0;Walk-in (QRIS)=0;WhatsApp pre-order=0;GoFood=0.2;GrabFood=0.2" \
  --categories "Bahan baku;Kemasan;Gas LPG;Kebersihan;Lain-lain" \
  --example-date 2027-01-25
```

- **`--type`**: `fnb`, `retail` or `service`. It sets default channels, categories and a direct-cost alert. Use it when there is no `--channels`, `--categories` or `profile.md` value.
- **`--breakeven`, `--direct-cost-alert` (a fraction) and `--weekly-target`** override `profile.md`.
- **`--example-date`** sets the date in the example rows and the week the summary opens on. Use the first real trading day, or the first test weekend.

The tool prints the files it wrote and the settings it used, with where each came from. Commission rates stay estimates until the merchant contract is in.

## Step 3: tell the owner

- where the files are, and that the xlsx opens in Google Sheets
- which settings came from which file
- what the team fills in daily: about 5 minutes after closing, one row per channel, one row per invoice line
- to delete the green example rows
- to replace the commission estimates with the contract rates in **Daftar**
- on Monday, to send the file to `/founder-weekly-report`. Monthly, `/founder-pnl` and `/founder-cost-leak` read the same sheets.

Suggest starting on the first real-money day. That is usually the test weekend from `/founder-launch`: those rows are the first real sales and the first real cost per unit.

## How the run skills read it

| the run skill needs | logbook column |
| --- | --- |
| date, channel, gross sales, discounts, platform commission and fees, net sales, transactions | Penjualan: Tanggal, Kanal, Penjualan kotor, Diskon, Komisi & biaya platform, Penjualan bersih, Jumlah transaksi |
| purchases: date, item, total | Pembelian: Tanggal, Barang, Total |

When a run skill reads the logbook:

- **Net sales:** use **Penjualan bersih** (column H).
- **Estimated fees:** an app-channel row with **Komisi & biaya platform** (column F) blank used the estimate in column G. List those dates under "Not recorded" as "platform fee estimated".
- **The example row:** skip any row whose Catatan starts with "CONTOH".

## Rules

- The logbook records the business's money only. The owner's personal spending (prive) and tax collected from buyers (PBJT/PB1, PPN) are neither sales nor purchases. The Petunjuk sheet says so.
- No customer phone numbers or names in the logbook (UU PDP 27/2022). Customer lists live in WhatsApp Business, with consent.
- Blank stays blank: a missed day is reported as missing, never filled with an average.
- The tool computes nothing about the business. It writes formulas, and the numbers come from what the team types.
- Not accounting or tax advice. An accountant can map these sheets to proper books later.

## Output

`founder/templates/catatan-harian.xlsx`, `founder/templates/sales-template.csv` and `founder/templates/purchases-template.csv`.

Next: `/founder-weekly-report` every Monday, reading the logbook.
