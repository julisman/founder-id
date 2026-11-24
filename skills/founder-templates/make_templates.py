#!/usr/bin/env python3
"""A daily sales and purchases logbook for a business with no POS yet.
Standard library only, no network.

Writes, into <dir>/templates/:

    catatan-harian.xlsx      the logbook (Excel, Google Sheets, WPS), in Indonesian:
                             Petunjuk, Penjualan, Pembelian, Ringkasan Minggu, Daftar
    sales-template.csv       the same sales columns, English headers
    purchases-template.csv   the same purchase columns, English headers

The columns are the ones /founder-weekly-report reads: date, channel, gross sales,
discounts, platform commission and fees, net sales, transactions; and for purchases
date, item, total. Net sales, totals, the day name and the weekly summary are
formulas, so the sheet recalculates as the team types. Nothing is computed here.

    python3 make_templates.py --dir founder --type fnb
    python3 make_templates.py --dir founder --channels "Walk-in (tunai)=0;GoFood=0.2" \\
        --categories "Bahan baku;Kemasan;Gas LPG" --example-date 2027-01-25

It reads founder/profile.md (break-even per day, the direct-cost alert, the weekly
target) and the business name from founder/numbers.json when they exist. A value
it cannot find stays 0 for the owner to fill in: it never invents a break-even.
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

PRESETS = {
    "fnb": {
        "channels": [("Walk-in (tunai)", 0.0), ("Walk-in (QRIS)", 0.0), ("WhatsApp pre-order", 0.0),
                     ("GoFood", 0.20), ("GrabFood", 0.20), ("ShopeeFood", 0.20)],
        "categories": ["Bahan baku", "Minuman / kopi", "Kemasan", "Gas & energi", "Kebersihan",
                       "Peralatan kecil", "Lain-lain"],
        "direct_cost_alert": 0.35,
    },
    "retail": {
        "channels": [("Toko (tunai)", 0.0), ("Toko (QRIS)", 0.0), ("WhatsApp / Instagram", 0.0),
                     ("Shopee", 0.10), ("Tokopedia / TikTok Shop", 0.10)],
        "categories": ["Stok barang", "Kemasan", "Ongkos kirim", "Lain-lain"],
        "direct_cost_alert": 0.60,
    },
    "service": {
        "channels": [("Langsung (tunai/QRIS)", 0.0), ("Transfer / invoice", 0.0), ("Marketplace / platform", 0.15)],
        "categories": ["Bahan", "Subkontraktor", "Transport", "Lain-lain"],
        "direct_cost_alert": 0.40,
    },
}
PAYMENT = ["Tunai", "QRIS", "Transfer", "Tempo (bayar nanti)"]
HALAL = ["Ya, ada sertifikat", "Tidak ada", "Tidak perlu"]
ROWS = 1000          # log rows prepared with formulas (rows 2 to ROWS + 1)
LIST_ROWS = 12       # room in each Daftar list

SALES_HEAD = ["Tanggal", "Hari", "Kanal", "Penjualan kotor (Rp)", "Diskon (Rp)",
              "Komisi & biaya platform (Rp)", "Perkiraan komisi (otomatis)", "Penjualan bersih (Rp)",
              "Jumlah transaksi", "Diisi oleh", "Catatan"]
PURCHASE_HEAD = ["Tanggal", "Pemasok", "Barang", "Kategori", "Jumlah", "Satuan", "Harga satuan (Rp)",
                 "Total (Rp)", "Cara bayar", "Jatuh tempo", "No. nota", "Sertifikat halal pemasok", "Catatan"]
SALES_CSV = ["date", "channel", "gross_sales", "discounts", "platform_fees", "net_sales", "transactions",
             "entered_by", "note"]
PURCHASES_CSV = ["date", "supplier", "item", "category", "qty", "unit", "unit_price", "total", "payment",
                 "due_date", "invoice_no", "supplier_halal_cert", "note"]


# ── a small xlsx writer ──────────────────────────────────────────────────────

class Styles:
    """Collects the fonts, fills and number formats the sheets ask for."""

    FONTS = {  # key: (bold, italic, size, colour)
        "base": (False, False, 10, "FF000000"), "bold": (True, False, 10, "FF000000"),
        "title": (True, False, 14, "FF000000"), "head": (True, False, 10, "FFFFFFFF"),
        "input": (False, False, 10, "FF0000FF"), "link": (False, False, 10, "FF008000"),
        "note": (False, True, 9, "FF666666"),
    }
    FILLS = {"none": None, "head": "FF1B2440", "input": "FFFFF2CC", "auto": "FFEDEDED", "example": "FFE2EFDA"}
    NUMFMTS = {"general": 0, "rp": 164, "pct": 165, "date": 166, "int": 167, "qty": 168}
    NUMFMT_CODES = {164: '#,##0;-#,##0;"-"', 165: '0.0%;-0.0%;"-"', 166: "dd/mm/yyyy", 167: "#,##0",
                    168: "#,##0.##"}

    def __init__(self):
        self.fonts = list(self.FONTS)
        self.fills = list(self.FILLS)
        self.xfs = [("base", "none", False, "general", False)]

    def get(self, font="base", fill="none", border=False, numfmt="general", wrap=False):
        key = (font, fill, border, numfmt, wrap)
        if key not in self.xfs:
            self.xfs.append(key)
        return self.xfs.index(key)

    def xml(self):
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
               '<numFmts count="%d">' % len(self.NUMFMT_CODES)]
        for i, code in self.NUMFMT_CODES.items():
            out.append('<numFmt numFmtId="%d" formatCode="%s"/>' % (i, escape(code, {'"': "&quot;"})))
        out.append("</numFmts>")
        out.append('<fonts count="%d">' % len(self.fonts))
        for k in self.fonts:
            bold, italic, size, colour = self.FONTS[k]
            out.append("<font>%s%s<sz val=\"%d\"/><color rgb=\"%s\"/><name val=\"Arial\"/><family val=\"2\"/></font>"
                       % ("<b/>" if bold else "", "<i/>" if italic else "", size, colour))
        out.append("</fonts>")
        out.append('<fills count="%d"><fill><patternFill patternType="none"/></fill>'
                   '<fill><patternFill patternType="gray125"/></fill>' % (len(self.fills) + 1))
        for k in self.fills[1:]:
            out.append('<fill><patternFill patternType="solid"><fgColor rgb="%s"/><bgColor indexed="64"/>'
                       "</patternFill></fill>" % self.FILLS[k])
        out.append("</fills>")
        out.append('<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>'
                   '<border><left style="thin"><color rgb="FFBFBFBF"/></left><right style="thin"><color rgb="FFBFBFBF"/></right>'
                   '<top style="thin"><color rgb="FFBFBFBF"/></top><bottom style="thin"><color rgb="FFBFBFBF"/></bottom>'
                   "<diagonal/></border></borders>")
        out.append('<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>')
        out.append('<cellXfs count="%d">' % len(self.xfs))
        for font, fill, border, numfmt, wrap in self.xfs:
            fill_id = 0 if fill == "none" else self.fills.index(fill) + 1
            out.append('<xf numFmtId="%d" fontId="%d" fillId="%d" borderId="%d" xfId="0" applyNumberFormat="1" '
                       'applyFont="1" applyFill="1" applyBorder="1"%s>%s</xf>'
                       % (self.NUMFMTS[numfmt], self.fonts.index(font), fill_id, 1 if border else 0,
                          ' applyAlignment="1"' if wrap else "",
                          '<alignment wrapText="1" vertical="center"/>' if wrap else ""))
        out.append("</cellXfs>")
        out.append('<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>')
        out.append("</styleSheet>")
        return "".join(out)


def col_letter(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def excel_date(d):
    return (d - dt.date(1899, 12, 30)).days


class Sheet:
    def __init__(self, name, styles):
        self.name, self.st = name, styles
        self.cells = {}          # (row, col) -> (kind, value, style)
        self.widths = {}
        self.heights = {}
        self.freeze = None       # row number that stays on top, e.g. 1
        self.validations = []    # (sqref, formula)

    def set(self, ref, value, **style):
        m = re.match(r"([A-Z]+)(\d+)$", ref)
        col = 0
        for ch in m.group(1):
            col = col * 26 + ord(ch) - 64
        row = int(m.group(2))
        sid = self.st.get(**style)
        if value is None:
            kind = "blank"
        elif isinstance(value, str) and value.startswith("="):
            kind = "f"
        elif isinstance(value, str):
            kind = "s"
        elif isinstance(value, dt.date):
            kind, value = "n", excel_date(value)
        else:
            kind = "n"
        self.cells[(row, col)] = (kind, value, sid)

    def xml(self):
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
               '<sheetViews><sheetView workbookViewId="0">']
        if self.freeze:
            out.append('<pane ySplit="%d" topLeftCell="A%d" activePane="bottomLeft" state="frozen"/>'
                       % (self.freeze, self.freeze + 1))
        out.append("</sheetView></sheetViews>")
        out.append('<sheetFormatPr defaultRowHeight="15"/>')
        if self.widths:
            out.append("<cols>")
            for c in sorted(self.widths):
                out.append('<col min="%d" max="%d" width="%s" customWidth="1"/>' % (c, c, self.widths[c]))
            out.append("</cols>")
        out.append("<sheetData>")
        rows = sorted({r for r, _ in self.cells})
        for r in rows:
            ht = ' ht="%s" customHeight="1"' % self.heights[r] if r in self.heights else ""
            out.append('<row r="%d"%s>' % (r, ht))
            for c in sorted(c for rr, c in self.cells if rr == r):
                kind, value, sid = self.cells[(r, c)]
                ref = "%s%d" % (col_letter(c), r)
                if kind == "blank":
                    out.append('<c r="%s" s="%d"/>' % (ref, sid))
                elif kind == "f":
                    out.append('<c r="%s" s="%d"><f>%s</f></c>' % (ref, sid, escape(value[1:])))
                elif kind == "s":
                    out.append('<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                               % (ref, sid, escape(value)))
                else:
                    out.append('<c r="%s" s="%d"><v>%s</v></c>' % (ref, sid, repr(value) if isinstance(value, float) else value))
            out.append("</row>")
        out.append("</sheetData>")
        if self.validations:
            out.append('<dataValidations count="%d">' % len(self.validations))
            for sqref, kind, formula, message in self.validations:
                if kind == "list":
                    out.append('<dataValidation type="list" allowBlank="1" showInputMessage="1" showErrorMessage="1" '
                               'errorTitle="Pilih dari daftar" error="%s" sqref="%s"><formula1>%s</formula1></dataValidation>'
                               % (escape(message, {'"': "&quot;"}), sqref, escape(formula)))
                else:
                    out.append('<dataValidation type="date" operator="greaterThan" allowBlank="1" showErrorMessage="1" '
                               'errorTitle="Tanggal" error="%s" sqref="%s"><formula1>%s</formula1></dataValidation>'
                               % (escape(message, {'"': "&quot;"}), sqref, escape(formula)))
            out.append("</dataValidations>")
        out.append('<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>')
        out.append("</worksheet>")
        return "".join(out)


def save_xlsx(path, sheets, styles):
    names = [s.name for s in sheets]
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>',
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
          '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
    for i in range(len(sheets)):
        ct.append('<Override PartName="/xl/worksheets/sheet%d.xml" '
                  'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1))
    ct.append("</Types>")
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/></Relationships>')
    wb = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>']
    for i, n in enumerate(names):
        wb.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (escape(n), i + 1, i + 1))
    wb.append('</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
    wbrels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
              '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i in range(len(sheets)):
        wbrels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                      'Target="worksheets/sheet%d.xml"/>' % (i + 1, i + 1))
    wbrels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
                  'Target="styles.xml"/></Relationships>' % (len(sheets) + 1))
    sheet_xml = [s.xml() for s in sheets]  # build first so every style is registered
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", "".join(wb))
        z.writestr("xl/_rels/workbook.xml.rels", "".join(wbrels))
        z.writestr("xl/styles.xml", styles.xml())
        for i, x in enumerate(sheet_xml):
            z.writestr("xl/worksheets/sheet%d.xml" % (i + 1), x)


# ── what goes in the logbook ─────────────────────────────────────────────────

def read_pack(fdir):
    """Settings the pack already knows: from profile.md (founder-plan) and numbers.json (founder-cfo)."""
    out = {}
    p = os.path.join(fdir, "profile.md")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            t = fh.read()
        m = re.search(r"Break-even per day:.*?Rp([\d.]+)", t)
        if m:
            out["breakeven"] = int(m.group(1).replace(".", ""))
        m = re.search(r"Direct cost.*?alert:\s*([\d.]+)%", t)
        if m:
            out["direct_cost_alert"] = float(m.group(1)) / 100
        m = re.search(r"Weekly sales target.*?Rp([\d.]+)", t)
        if m:
            out["weekly_target"] = int(m.group(1).replace(".", ""))
    n = os.path.join(fdir, "numbers.json")
    if os.path.exists(n):
        try:
            with open(n, encoding="utf-8") as fh:
                name = json.load(fh).get("business", "")
            out["business"] = re.split(r"[:(]", name)[0].strip() or None
        except (ValueError, OSError):
            pass
    return out


def parse_channels(text):
    out = []
    for part in text.split(";"):
        if part.strip():
            name, _, rate = part.partition("=")
            out.append((name.strip(), float(rate) if rate.strip() else 0.0))
    return out


def settings(args):
    pack = read_pack(args.dir)
    preset = PRESETS[args.type]
    return {
        "business": args.business or pack.get("business") or "Usaha saya",
        "channels": parse_channels(args.channels) if args.channels else preset["channels"],
        "categories": [c.strip() for c in args.categories.split(";") if c.strip()] if args.categories else preset["categories"],
        "breakeven": args.breakeven if args.breakeven is not None else pack.get("breakeven", 0),
        "direct_cost_alert": args.direct_cost_alert if args.direct_cost_alert is not None
        else pack.get("direct_cost_alert", preset["direct_cost_alert"]),
        "weekly_target": args.weekly_target if args.weekly_target is not None else pack.get("weekly_target", 0),
        "source": "founder/profile.md" if "breakeven" in pack else "diisi sendiri (belum ada founder/profile.md)",
        "example_date": dt.date.fromisoformat(args.example_date),
    }


def head(sheet, row, labels, widths):
    for i, (lab, w) in enumerate(zip(labels, widths), start=1):
        sheet.set("%s%d" % (col_letter(i), row), lab, font="head", fill="head", border=True, wrap=True)
        sheet.widths[i] = w
    sheet.heights[row] = 32


def build(cfg):
    st = Styles()
    last = ROWS + 1
    ex_date = cfg["example_date"]

    # Petunjuk
    pt = Sheet("Petunjuk", st)
    pt.widths = {1: 3, 2: 110}
    lines = [
        ("title", "Catatan Harian: Penjualan & Pembelian, " + cfg["business"]),
        ("base", "Untuk usaha yang belum punya POS atau aplikasi pembukuan. Isi setiap hari, kira-kira 5 menit setelah tutup."),
        (None, ""),
        ("bold", "Cara pakai"),
        ("base", "1. Sheet 'Penjualan': satu baris per hari per kanal (mis. 'Walk-in (tunai)', 'GoFood'). Isi sel kuning saja."),
        ("base", "2. Sheet 'Pembelian': satu baris per barang di nota. Simpan notanya dan tulis nomornya."),
        ("base", "3. Sheet 'Ringkasan Minggu': ketik tanggal hari Senin di sel kuning B3, angka minggu itu muncul sendiri."),
        ("base", "4. Sheet 'Daftar': kanal, tarif komisi, kategori, break-even dan ambang biaya. Ubah kalau berubah."),
        ("base", "5. Setiap Senin: kirim file ini (atau export CSV) ke owner, atau jalankan /founder-weekly-report."),
        (None, ""),
        ("bold", "Arti warna"),
        ("base", "Kuning, angka biru = diisi manual. Abu-abu = otomatis, jangan diketik. Hijau = baris CONTOH, hapus setelah dibaca."),
        (None, ""),
        ("bold", "Aturan isi"),
        ("base", "- Penjualan kotor = total harga sebelum diskon dan komisi. Diskon = potongan yang ditanggung usaha, bukan voucher yang dibayar aplikasi."),
        ("base", "- Komisi & biaya platform: dari laporan GoBiz, GrabMerchant atau seller centre. Kalau belum ada, kosongkan: kolom 'Perkiraan komisi' dipakai sementara."),
        ("base", "- Pajak restoran (PBJT/PB1) atau PPN yang ditagih ke pembeli BUKAN penjualan. Catat penjualan tanpa pajak itu."),
        ("base", "- Uang pribadi owner (prive) jangan dicatat sebagai pembelian usaha."),
        ("base", "- Hari tutup: tulis satu baris dengan penjualan 0 dan Catatan 'tutup', supaya tidak dianggap lupa diisi."),
        ("base", "- Lupa mencatat? Kosongkan dan beri tahu owner. Jangan isi angka kira-kira."),
        (None, ""),
        ("bold", "Nama kolom untuk /founder-weekly-report"),
        ("base", "Tanggal = date, Kanal = channel, Penjualan kotor = gross sales, Diskon = discounts, Komisi & biaya = platform commission and fees,"),
        ("base", "Penjualan bersih = net sales, Jumlah transaksi = transactions. Pembelian: Tanggal = date, Barang = item, Total = total."),
        (None, ""),
        ("note", "Break-even dan ambang biaya langsung di sheet 'Daftar' berasal dari " + cfg["source"] + ". Ganti setelah ada angka nyata."),
        ("note", "Tarif komisi aplikasi di 'Daftar' adalah perkiraan sampai kontrak merchant ada."),
        ("note", "Nomor WA atau nama pelanggan jangan dicatat di file ini (UU PDP 27/2022)."),
    ]
    for i, (font, text) in enumerate(lines, start=1):
        if font:
            pt.set("B%d" % i, text, font=font, wrap=True)

    # Daftar
    dl = Sheet("Daftar", st)
    dl.widths = {1: 30, 2: 14, 3: 3, 4: 24, 5: 3, 6: 22, 7: 3, 8: 26}
    dl.set("A1", "Daftar & pengaturan", font="title")
    dl.set("A2", "Sel kuning boleh diubah. Daftar ini dipakai untuk pilihan (dropdown) di sheet lain.", font="note")
    for ref, lab in (("A4", "Kanal penjualan"), ("B4", "Tarif komisi"), ("D4", "Kategori pembelian"),
                     ("F4", "Cara bayar"), ("H4", "Sertifikat halal pemasok")):
        dl.set(ref, lab, font="head", fill="head", border=True)
    for i in range(LIST_ROWS):
        r = 5 + i
        name, rate = cfg["channels"][i] if i < len(cfg["channels"]) else (None, None)
        dl.set("A%d" % r, name, font="input", fill="input", border=True)
        dl.set("B%d" % r, rate, font="input", fill="input", border=True, numfmt="pct")
        for col, vals in (("D", cfg["categories"]), ("F", PAYMENT), ("H", HALAL)):
            dl.set("%s%d" % (col, r), vals[i] if i < len(vals) else None, font="input", fill="input", border=True)
    dl.set("A18", "Tarif komisi aplikasi: perkiraan. Ganti dengan tarif di kontrak merchant.", font="note")
    dl.set("A19", "Pengaturan", font="bold")
    for r, lab, val, fmt in ((20, "Break-even per hari (Rp penjualan bersih)", cfg["breakeven"], "rp"),
                             (21, "Ambang biaya langsung (% penjualan bersih)", cfg["direct_cost_alert"], "pct"),
                             (22, "Target penjualan mingguan (Rp)", cfg["weekly_target"], "rp")):
        dl.set("A%d" % r, lab)
        dl.set("B%d" % r, val, font="input", fill="input", border=True, numfmt=fmt)
    dl.set("D20", "Sumber: " + cfg["source"] + ". Ganti setelah ada angka nyata.", font="note")
    ch_list, rate_list = "Daftar!$A$5:$A$%d" % (4 + LIST_ROWS), "Daftar!$B$5:$B$%d" % (4 + LIST_ROWS)

    # Penjualan
    sp = Sheet("Penjualan", st)
    sp.freeze = 1
    head(sp, 1, SALES_HEAD, [12, 6, 22, 16, 12, 18, 16, 18, 12, 12, 34])
    for r in range(2, last + 1):
        for col in "ACDEFIJK":
            fmt = {"A": "date", "D": "rp", "E": "rp", "F": "rp", "I": "int"}.get(col, "general")
            sp.set("%s%d" % (col, r), None, font="input", fill="input", border=True, numfmt=fmt)
        sp.set("B%d" % r, '=IF(A{r}="","",CHOOSE(WEEKDAY(A{r},2),"Sen","Sel","Rab","Kam","Jum","Sab","Min"))'.format(r=r),
               fill="auto", border=True)
        sp.set("G%d" % r, '=IF(OR(A{r}="",C{r}=""),"",ROUND(D{r}*IFERROR(INDEX({rate},MATCH(C{r},{ch},0)),0),0))'
               .format(r=r, rate=rate_list, ch=ch_list), fill="auto", border=True, numfmt="rp")
        sp.set("H%d" % r, '=IF(A{r}="","",D{r}-E{r}-IF(F{r}="",G{r},F{r}))'.format(r=r),
               fill="auto", border=True, numfmt="rp")
    example = {"A": (ex_date, "date"), "C": (cfg["channels"][0][0], "general"), "D": (1250000, "rp"), "E": (0, "rp"),
               "I": (48, "int"), "J": ("Contoh", "general"), "K": ("CONTOH: hapus baris ini", "general")}
    for col in "ACDEFIJK":
        val, fmt = example.get(col, (None, {"F": "rp"}.get(col, "general")))
        sp.set("%s2" % col, val, font="input", fill="example", border=True, numfmt=fmt)
    for col, f in (("B", sp.cells[(2, 2)][1]), ("G", sp.cells[(2, 7)][1]), ("H", sp.cells[(2, 8)][1])):
        sp.set("%s2" % col, f, fill="example", border=True, numfmt="general" if col == "B" else "rp")
    sp.validations.append(("C2:C%d" % last, "list", ch_list, "Pilih kanal dari sheet Daftar."))
    sp.validations.append(("A2:A%d" % last, "date", "DATE(2020,1,1)", "Isi tanggal, mis. 25/01/2027"))

    # Pembelian
    pb = Sheet("Pembelian", st)
    pb.freeze = 1
    head(pb, 1, PURCHASE_HEAD, [12, 20, 24, 18, 9, 9, 15, 15, 16, 12, 12, 22, 30])
    for r in range(2, last + 1):
        for col in "ABCDEFGIJKLM":
            fmt = {"A": "date", "J": "date", "E": "qty", "G": "rp"}.get(col, "general")
            pb.set("%s%d" % (col, r), None, font="input", fill="input", border=True, numfmt=fmt)
        pb.set("H%d" % r, '=IF(OR(E{r}="",G{r}=""),"",ROUND(E{r}*G{r},0))'.format(r=r),
               fill="auto", border=True, numfmt="rp")
    example = {"A": (ex_date, "date"), "B": ("Contoh: toko bahan", "general"), "C": ("Tepung terigu 25 kg", "general"),
               "D": (cfg["categories"][0], "general"), "E": (1, "qty"), "F": ("sak", "general"), "G": (260000, "rp"),
               "I": (PAYMENT[0], "general"), "K": ("001", "general"), "L": (HALAL[0], "general"),
               "M": ("CONTOH: hapus baris ini", "general")}
    for col in "ABCDEFGIJKLM":
        val, fmt = example.get(col, (None, {"J": "date"}.get(col, "general")))
        pb.set("%s2" % col, val, font="input", fill="example", border=True, numfmt=fmt)
    pb.set("H2", pb.cells[(2, 8)][1], fill="example", border=True, numfmt="rp")
    for sqref, src, msg in (("D2:D%d" % last, "Daftar!$D$5:$D$%d" % (4 + LIST_ROWS), "Pilih kategori dari sheet Daftar."),
                            ("I2:I%d" % last, "Daftar!$F$5:$F$%d" % (4 + LIST_ROWS), "Pilih cara bayar dari sheet Daftar."),
                            ("L2:L%d" % last, "Daftar!$H$5:$H$%d" % (4 + LIST_ROWS), "Pilih dari sheet Daftar.")):
        pb.validations.append((sqref, "list", src, msg))
    pb.validations.append(("A2:A%d" % last, "date", "DATE(2020,1,1)", "Isi tanggal, mis. 25/01/2027"))

    # Ringkasan Minggu
    rs = Sheet("Ringkasan Minggu", st)
    rs.freeze = 5
    rs.set("A1", "Ringkasan minggu: " + cfg["business"], font="title")
    rs.set("A3", "Senin minggu ini (isi):", font="bold")
    rs.set("B3", ex_date - dt.timedelta(days=ex_date.weekday()), font="input", fill="input", border=True, numfmt="date")
    rs.set("C3", '=IF(B3="","",IF(WEEKDAY(B3,2)<>1,"Bukan hari Senin, cek tanggalnya","s/d (Minggu)"))', font="note")
    rs.set("D3", '=IF(B3="","",B3+6)', numfmt="date")
    sA, sC, sH, sI = ("Penjualan!$%s$2:$%s$%d" % (c, c, last) for c in "ACHI")
    pA, pH = ("Pembelian!$%s$2:$%s$%d" % (c, c, last) for c in "AH")
    head(rs, 5, ["Tanggal", "Hari", "Penjualan bersih (Rp)", "Transaksi", "Rata-rata (Rp)", "vs break-even",
                 "Baris tercatat"], [26, 16, 20, 12, 16, 16, 16])
    for i in range(7):
        r = 6 + i
        rs.set("A%d" % r, "=$B$3+%d" % i, border=True, numfmt="date")
        rs.set("B%d" % r, '=CHOOSE(WEEKDAY(A%d,2),"Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu")' % r, border=True)
        rs.set("C%d" % r, "=SUMIFS(%s,%s,A%d)" % (sH, sA, r), border=True, numfmt="rp")
        rs.set("D%d" % r, "=SUMIFS(%s,%s,A%d)" % (sI, sA, r), border=True, numfmt="int")
        rs.set("E%d" % r, '=IF(D{r}=0,"-",ROUND(C{r}/D{r},0))'.format(r=r), border=True, numfmt="rp")
        rs.set("F%d" % r, '=IF(G{r}=0,"Belum diisi",IF(C{r}<Daftar!$B$20,"Di bawah","OK"))'.format(r=r), border=True)
        rs.set("G%d" % r, "=COUNTIFS(%s,A%d)" % (sA, r), border=True, numfmt="int")
    rs.set("A13", "Total minggu", font="bold", border=True)
    rs.set("B13", None, border=True)
    rs.set("C13", "=SUM(C6:C12)", font="bold", border=True, numfmt="rp")
    rs.set("D13", "=SUM(D6:D12)", font="bold", border=True, numfmt="int")
    rs.set("E13", '=IF(D13=0,"-",ROUND(C13/D13,0))', font="bold", border=True, numfmt="rp")
    rs.set("F13", '=COUNTIF(F6:F12,"Di bawah")&" hari di bawah"', font="bold", border=True)
    rs.set("G13", '=COUNTIF(G6:G12,0)&" hari kosong"', font="bold", border=True)

    rs.set("A15", "Dibanding minggu lalu", font="bold")
    for r, lab, formula, fmt, font in (
            (16, "Penjualan bersih minggu lalu", '=SUMIFS(%s,%s,">="&($B$3-7),%s,"<="&($B$3-1))' % (sH, sA, sA), "rp", "base"),
            (17, "Selisih (Rp)", "=C13-C16", "rp", "base"),
            (18, "Selisih (%)", '=IF(C16=0,"-",C17/C16)', "pct", "base"),
            (19, "Target mingguan", "=Daftar!$B$22", "rp", "link"),
            (20, "Capaian target", '=IF(C19=0,"-",C13/C19)', "pct", "base")):
        rs.set("A%d" % r, lab)
        rs.set("C%d" % r, formula, font=font, numfmt=fmt)

    rs.set("A22", "Per kanal", font="bold")
    head(rs, 23, ["Kanal", "Penjualan bersih (Rp)", "Porsi"], [26, 16, 20])
    for i in range(LIST_ROWS):
        r, d = 24 + i, 5 + i
        rs.set("A%d" % r, '=IF(Daftar!$A${d}="","",Daftar!$A${d})'.format(d=d), font="link")
        rs.set("B%d" % r, '=IF(A{r}="","",SUMIFS({h},{c},A{r},{a},">="&$B$3,{a},"<="&($B$3+6)))'
               .format(r=r, h=sH, c=sC, a=sA), numfmt="rp")
        rs.set("C%d" % r, '=IF(OR(A{r}="",$C$13=0),"",B{r}/$C$13)'.format(r=r), numfmt="pct")

    rs.set("A37", "Biaya langsung (perkiraan)", font="bold")
    for r, lab, formula, fmt, font in (
            (38, "Pembelian minggu ini (Rp)", '=SUMIFS(%s,%s,">="&$B$3,%s,"<="&($B$3+6))' % (pH, pA, pA), "rp", "base"),
            (39, "Biaya langsung % (perkiraan, tanpa stok opname)", '=IF(C13=0,"-",C38/C13)', "pct", "base"),
            (40, "Ambang", "=Daftar!$B$21", "pct", "link"),
            (41, "Status", '=IF(C13=0,"-",IF(C39>C40,"Di atas ambang","OK"))', "general", "base")):
        rs.set("A%d" % r, lab)
        rs.set("C%d" % r, formula, font=font, numfmt=fmt)
    rs.set("A43", "Perkiraan: pembelian minggu ini dibagi penjualan bersih, tanpa stok opname. Belanja besar "
                  "sekali seminggu membuat angka naik-turun; lihat trennya, bukan satu minggu.", font="note")

    return [pt, sp, pb, rs, dl], st


def write(args):
    cfg = settings(args)
    outdir = os.path.join(args.dir, "templates")
    os.makedirs(outdir, exist_ok=True)
    sheets, st = build(cfg)
    xlsx = os.path.join(outdir, args.filename)
    save_xlsx(xlsx, sheets, st)
    ex = cfg["example_date"].isoformat()
    with open(os.path.join(outdir, "sales-template.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SALES_CSV)
        w.writerow([ex, cfg["channels"][0][0], 1250000, 0, 0, 1250000, 48, "example", "EXAMPLE: delete this row"])
    with open(os.path.join(outdir, "purchases-template.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(PURCHASES_CSV)
        w.writerow([ex, "example supplier", "Tepung terigu 25 kg", cfg["categories"][0], 1, "sak", 260000, 260000,
                    PAYMENT[0], "", "001", "yes", "EXAMPLE: delete this row"])
    used = {k: v for k, v in cfg.items() if k != "example_date"}
    used["example_date"] = ex
    return {"xlsx": xlsx, "sales_csv": os.path.join(outdir, "sales-template.csv"),
            "purchases_csv": os.path.join(outdir, "purchases-template.csv"), "used": used}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default="founder", help="the founder/ folder; files go in <dir>/templates/")
    ap.add_argument("--type", choices=sorted(PRESETS), default="fnb", help="business type preset")
    ap.add_argument("--channels", help='"Walk-in (tunai)=0;GoFood=0.2" (rate as a fraction)')
    ap.add_argument("--categories", help='"Bahan baku;Kemasan;Gas LPG"')
    ap.add_argument("--business", help="business name for the titles")
    ap.add_argument("--breakeven", type=int, help="break-even net sales per day, Rupiah")
    ap.add_argument("--direct-cost-alert", type=float, help="direct-cost alert as a fraction, e.g. 0.35")
    ap.add_argument("--weekly-target", type=int, help="weekly net sales target, Rupiah")
    ap.add_argument("--example-date", default=dt.date.today().isoformat(), help="date in the example rows, YYYY-MM-DD")
    ap.add_argument("--filename", default="catatan-harian.xlsx")
    args = ap.parse_args(argv)
    try:
        dt.date.fromisoformat(args.example_date)
    except ValueError:
        ap.error("--example-date must be YYYY-MM-DD")
    print(json.dumps(write(args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
