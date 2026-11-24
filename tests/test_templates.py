import csv
import html
import io
import json
import os
import re
import shutil
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout

from _load import load

tpl = load("founder-templates", "make_templates")

PROFILE = """# Business profile: Kopi Senja

## From the plan

- Break-even per day: 98 cups, Rp2.070.619 of sales
- Weekly sales target at plan: Rp27.720.000 (180 cups a day)
- Fixed costs per month: Rp29.449.846

## Thresholds the run skills use (defaults, change them here)

- Direct cost (COGS / food cost) alert: 49% of net sales (plan + 5 points)
"""


class Templates(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.fdir = os.path.join(self.dir, "founder")
        os.makedirs(self.fdir)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_tool(self, *extra):
        out = io.StringIO()
        with redirect_stdout(out):
            tpl.main(["--dir", self.fdir, "--example-date", "2027-01-25"] + list(extra))
        return json.loads(out.getvalue())

    def sheets(self, path):
        """Sheet names and each sheet's XML text. Plain regex, no XML parser: some Python builds lack expat."""
        with zipfile.ZipFile(path) as z:
            wb = z.read("xl/workbook.xml").decode("utf-8")
            self.assertIn('fullCalcOnLoad="1"', wb)
            names = [html.unescape(n) for n in re.findall(r'<sheet name="([^"]+)"', wb)]
            parts = {n: z.read("xl/worksheets/sheet%d.xml" % (i + 1)).decode("utf-8") for i, n in enumerate(names)}
            for part in ["xl/styles.xml", "[Content_Types].xml"] + ["xl/worksheets/sheet%d.xml" % (i + 1) for i in range(len(names))]:
                text = z.read(part).decode("utf-8")
                self.assertTrue(text.startswith("<?xml") and text.count("<") == text.count(">"), part)
        return names, parts

    @staticmethod
    def cell(sheet, ref):
        m = re.search(r'<c r="%s"[^>]*?(?:/>|>(.*?)</c>)' % ref, sheet)
        if not m or m.group(1) is None:
            return None
        body = m.group(1)
        for pat, prefix in ((r"<f>(.*?)</f>", "="), (r"<t[^>]*>(.*?)</t>", ""), (r"<v>(.*?)</v>", "")):
            g = re.search(pat, body)
            if g:
                return prefix + html.unescape(g.group(1))
        return None

    def test_writes_the_three_files_and_five_sheets(self):
        res = self.run_tool()
        for k in ("xlsx", "sales_csv", "purchases_csv"):
            self.assertTrue(os.path.isfile(res[k]), k)
        names, _ = self.sheets(res["xlsx"])
        self.assertEqual(names, ["Petunjuk", "Penjualan", "Pembelian", "Ringkasan Minggu", "Daftar"])

    def test_columns_match_what_the_weekly_report_reads(self):
        res = self.run_tool()
        with open(res["sales_csv"], encoding="utf-8") as fh:
            head = next(csv.reader(fh))
        for col in ("date", "channel", "gross_sales", "discounts", "platform_fees", "net_sales", "transactions"):
            self.assertIn(col, head)
        with open(res["purchases_csv"], encoding="utf-8") as fh:
            head = next(csv.reader(fh))
        for col in ("date", "item", "total"):
            self.assertIn(col, head)
        _, parts = self.sheets(res["xlsx"])
        heads = [self.cell(parts["Penjualan"], "%s1" % c) for c in "ACDEFHI"]
        self.assertEqual(heads, ["Tanggal", "Kanal", "Penjualan kotor (Rp)", "Diskon (Rp)",
                                 "Komisi & biaya platform (Rp)", "Penjualan bersih (Rp)", "Jumlah transaksi"])

    def test_net_sales_and_totals_are_formulas_not_numbers(self):
        _, parts = self.sheets(self.run_tool()["xlsx"])
        sp, pb, rs = parts["Penjualan"], parts["Pembelian"], parts["Ringkasan Minggu"]
        last = tpl.ROWS + 1
        self.assertEqual(self.cell(sp, "H2"), '=IF(A2="","",D2-E2-IF(F2="",G2,F2))')
        self.assertEqual(self.cell(sp, "H%d" % last), '=IF(A{0}="","",D{0}-E{0}-IF(F{0}="",G{0},F{0}))'.format(last))
        self.assertIn("INDEX(Daftar!$B$5:$B$16,MATCH(C2,Daftar!$A$5:$A$16,0))", self.cell(sp, "G2"))
        self.assertEqual(self.cell(pb, "H2"), '=IF(OR(E2="",G2=""),"",ROUND(E2*G2,0))')
        self.assertEqual(self.cell(rs, "C6"), "=SUMIFS(Penjualan!$H$2:$H$%d,Penjualan!$A$2:$A$%d,A6)" % (last, last))
        self.assertIn("Daftar!$B$20", self.cell(rs, "F6"))
        self.assertEqual(self.cell(rs, "C39"), '=IF(C13=0,"-",C38/C13)')
        self.assertEqual(self.cell(rs, "C40"), "=Daftar!$B$21")

    def test_reads_the_profile_and_never_invents_a_breakeven(self):
        with open(os.path.join(self.fdir, "profile.md"), "w", encoding="utf-8") as fh:
            fh.write(PROFILE)
        used = self.run_tool()["used"]
        self.assertEqual(used["breakeven"], 2070619)
        self.assertAlmostEqual(used["direct_cost_alert"], 0.49)
        self.assertEqual(used["weekly_target"], 27720000)
        self.assertEqual(used["source"], "founder/profile.md")
        os.remove(os.path.join(self.fdir, "profile.md"))
        used = self.run_tool()["used"]
        self.assertEqual(used["breakeven"], 0)
        self.assertEqual(used["weekly_target"], 0)

    def test_channels_and_rates_land_in_the_lists(self):
        res = self.run_tool("--channels", "Walk-in (tunai)=0;GoFood=0.2", "--categories", "Bahan baku;Kemasan")
        _, parts = self.sheets(res["xlsx"])
        dl = parts["Daftar"]
        self.assertEqual(self.cell(dl, "A5"), "Walk-in (tunai)")
        self.assertEqual(self.cell(dl, "A6"), "GoFood")
        self.assertEqual(float(self.cell(dl, "B6")), 0.2)
        self.assertEqual(self.cell(dl, "D6"), "Kemasan")
        sp = parts["Penjualan"]
        dvs = re.findall(r'<dataValidation [^>]*sqref="([^"]+)"', sp)
        self.assertIn("C2:C%d" % (tpl.ROWS + 1), dvs)

    def test_example_rows_are_marked_and_the_week_starts_on_monday(self):
        res = self.run_tool()
        _, parts = self.sheets(res["xlsx"])
        self.assertTrue(self.cell(parts["Penjualan"], "K2").startswith("CONTOH"))
        self.assertTrue(self.cell(parts["Pembelian"], "M2").startswith("CONTOH"))
        monday = int(self.cell(parts["Ringkasan Minggu"], "B3"))
        self.assertEqual(monday, (tpl.dt.date(2027, 1, 25) - tpl.dt.date(1899, 12, 30)).days)

    def test_presets(self):
        for kind in tpl.PRESETS:
            res = self.run_tool("--type", kind)
            self.assertEqual(res["used"]["channels"][0][0], tpl.PRESETS[kind]["channels"][0][0])

    def test_no_locale_dependent_text_formats(self):
        _, parts = self.sheets(self.run_tool()["xlsx"])
        for name, sheet in parts.items():
            for f in re.findall(r"<f>(.*?)</f>", sheet):
                self.assertNotRegex(html.unescape(f), r"\bTEXT\(", name)


if __name__ == "__main__":
    unittest.main()
