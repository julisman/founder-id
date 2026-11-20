import json
import os
import shutil
import tempfile
import unittest

from _load import load

rp = load("founder-weekly-report", "reports")


def weekly(**change):
    d = {"week": "2027-W05", "start": "2027-02-01", "end": "2027-02-07", "net_sales": 300000, "transactions": 12,
         "avg_ticket": 25000, "daily": [{"date": "2027-02-0%d" % (i + 1), "net_sales": 100000} for i in range(3)],
         "channels": {"walk-in": 180000, "GoFood": 120000}, "direct_cost_pct": 0.45,
         "alerts": [{"text": "x", "skill": "founder-cost-leak"}]}
    d.update(change)
    return d


def cash(**change):
    d = {"from": "2027-02-03", "opening_balance": 1000000, "weeks": [
        {"label": "1", "cash_in": 500000, "suppliers": 300000, "payroll": 0, "cash_out": 300000, "end_balance": 1200000, "status": "safe"},
        {"label": "2", "cash_in": 100000, "suppliers": 1400000, "cash_out": 1400000, "end_balance": -100000, "status": "at risk"}]}
    d.update(change)
    return d


class Checks(unittest.TestCase):
    def test_a_good_weekly_report_passes(self):
        self.assertEqual(rp.check("weekly", weekly()), [])

    def test_weekly_totals_must_add_up(self):
        probs = rp.check("weekly", weekly(net_sales=350000, avg_ticket=29167))
        self.assertTrue(any("daily net sales add up to 300000" in p for p in probs), probs)
        self.assertTrue(any("channels add up" in p for p in probs), probs)
        self.assertTrue(rp.check("weekly", weekly(avg_ticket=40000)))
        self.assertTrue(rp.check("weekly", weekly(week="2027-5")))
        self.assertTrue(rp.check("weekly", weekly(direct_cost_pct=45)))  # 45 is not a fraction

    def test_pnl_net_profit_must_follow_from_the_lines(self):
        d = {"month": "2027-01", "net_sales": 1000, "direct_cost": 400, "labour": 200, "fixed_costs": 100, "pph_final": 5,
             "net_profit": 295}
        self.assertEqual(rp.check("pnl", d), [])
        d["net_profit"] = 300000
        self.assertTrue(any("net_profit should be" in p for p in rp.check("pnl", d)))
        self.assertEqual(rp.filename("pnl", dict(d, outlet="Blok M")), "2027-01-blok-m")

    def test_cash_balances_must_chain(self):
        self.assertEqual(rp.check("cashflow", cash()), [])
        bad = cash()
        bad["weeks"][1]["end_balance"] = 50000
        self.assertTrue(any("week 2" in p for p in rp.check("cashflow", bad)))
        bad = cash()
        bad["weeks"][1]["status"] = "safe"
        self.assertTrue(any("negative but is marked safe" in p for p in rp.check("cashflow", bad)))
        bad = cash()
        bad["weeks"][0]["cash_out"] = 250000
        self.assertTrue(any("not cash_out" in p for p in rp.check("cashflow", bad)))

    def test_cost_leak_product_mix_staffing(self):
        cl = {"month": "2027-01", "items": [{"item": "milk", "expected": 10, "actual": 12, "gap_qty": 2, "gap_rp": 30000},
                                            {"item": "beans", "expected": 5, "actual": 5.2, "gap_rp": 40000}]}
        self.assertTrue(any("sorted" in p for p in rp.check("cost-leak", cl)))
        pm = {"period": "2027-01", "items": [{"item": "a", "qty": 10, "margin_unit": 1000, "total_margin": 10000, "quadrant": "star"}]}
        self.assertEqual(rp.check("product-mix", pm), [])
        pm["items"][0]["quadrant"] = "cow"
        self.assertTrue(rp.check("product-mix", pm))
        sf = {"period": "2027-01", "labour_pct": 0.24, "heatmap": {"days": ["Mon", "Tue"], "hours": [7], "values": [[1, 2, 3]]}}
        self.assertTrue(rp.check("staffing", sf))

    def test_cli_paths_check_and_list(self):
        d = tempfile.mkdtemp()
        try:
            f = rp.path(d, "weekly", "2027-W05")
            self.assertTrue(f.endswith(os.path.join("reports", "weekly", "2027-W05.json")))
            os.makedirs(os.path.dirname(f))
            with open(f, "w") as fh:
                json.dump(weekly(), fh)
            self.assertEqual(rp.main(["check", f]), 0)
            wrong = os.path.join(os.path.dirname(f), "last-week.json")
            shutil.copy(f, wrong)
            self.assertEqual(rp.main(["check", wrong]), 1)  # named so the reports sort by date
            allr = rp.load_all(d)
            self.assertEqual([x["_key"] for x in allr["weekly"]], ["last-week", "2027-W05"])
            with self.assertRaises(rp.ReportError):
                rp.path(d, "monthly", "x")
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
