import csv
import os
import tempfile
import unittest

from _load import load

vw = load("founder-pricing", "van_westendorp")


def rows(n=40):
    out = []
    for i in range(n):
        k = i / float(n - 1)
        out.append((2.5 + k, 4.0 + k, 6.0 + 1.5 * k, 7.5 + 2 * k))
    return out


class Pricing(unittest.TestCase):
    def test_points_are_ordered_and_inside_the_answers(self):
        res = vw.analyse(rows())
        p = res["points"]
        for k in ("PMC", "PME", "OPP", "IPP"):
            self.assertIsNotNone(p[k], k)
            self.assertTrue(2.5 <= p[k] <= 9.5, (k, p[k]))
        self.assertLess(p["PMC"], p["PME"])
        self.assertLessEqual(p["PMC"], p["OPP"])
        self.assertLessEqual(p["OPP"], p["PME"])

    def test_out_of_order_and_incomplete_rows_are_dropped(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "p.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(vw.KEYS)
            for r in rows(10):
                w.writerow(r)
            w.writerow((9, 4, 6, 8))       # too cheap above a bargain: out of order
            w.writerow((3, "", 6, 8))      # incomplete
        got, dropped = vw.read(path)
        self.assertEqual((len(got), dropped), (10, 2))

    def test_too_few_answers_is_refused(self):
        with self.assertRaises(vw.PricingError):
            vw.analyse(rows(4))

    def test_rupiah_text_is_read_right(self):
        for raw, want in (("Rp22.000", 22000), ("22.000", 22000), ("Rp 22.500,50", 22500.5), (22000, 22000),
                          ("$6.50", 6.5), ("1,250", 1250), ("", None), ("murah", None)):
            self.assertEqual(vw._f(raw), want, raw)
        rows_idr = [(12000 + i * 100, 16000 + i * 100, 24000 + i * 200, 30000 + i * 300) for i in range(30)]
        text = vw.report(vw.analyse(rows_idr), 0, price=22000)
        self.assertIn("Rp22.000", text)
        self.assertIn("**inside** the acceptable range", text)

    def test_report_places_the_price(self):
        res = vw.analyse(rows())
        self.assertIn("**inside** the acceptable range", vw.report(res, 0, price=6.5, currency="USD"))
        self.assertIn("**above** the acceptable range", vw.report(res, 0, price=40))


if __name__ == "__main__":
    unittest.main()
