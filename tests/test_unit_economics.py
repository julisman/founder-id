import json
import math
import unittest

from _load import load, example

ue = load("founder-cfo", "unit_economics")


def spec():
    with open(example("founder-cfo", "example.json"), encoding="utf-8") as fh:
        return json.load(fh)


class UnitEconomics(unittest.TestCase):
    def test_example_reproduces_the_plan(self):
        a = ue.analyse(spec())
        self.assertAlmostEqual(a["contribution"], 10430, places=2)
        self.assertEqual(round(a["margin_at_plan"] * 100), 23)
        self.assertEqual(math.ceil(a["breakeven_per_day"]), 95)
        self.assertEqual(round(a["year1_profit"]), 146332535)
        self.assertEqual(a["startup"], 196000000)
        self.assertEqual(a["payback_month"], 11)
        self.assertEqual(round(a["cash_needed"]), 196000000)
        self.assertEqual(round(a["year1_after_startup"]), 46332535)
        self.assertEqual(len(a["flags"]), 1)
        self.assertIn("3 month(s) lose money", a["flags"][0])

    def test_percentage_costs_and_shares(self):
        s = {"price": 10000, "variable": [{"cost": 2000}, {"cost": 1000, "share": 0.5}],
             "variable_pct": [{"pct": 0.2, "share": 0.5}, {"pct": 0.005}],
             "fixed_monthly": [], "plan_per_day": 10}
        a = ue.analyse(s)
        # 2000 + 500 + 10000*0.2*0.5 + 10000*0.005
        self.assertAlmostEqual(a["variable_per_unit"], 3550)
        s["variable_pct"][0]["pct"] = 20
        with self.assertRaises(ue.NumbersError):
            ue.analyse(s)

    def test_prepaid_rent_counts_in_profit_not_twice_in_cash(self):
        base = {"price": 1000, "variable": [], "plan_per_day": 10, "days_per_month": 30,
                "fixed_monthly": [{"cost": 6000, "prepaid_months": 12}], "startup": [{"cost": 72000}]}
        a = ue.analyse(base)
        self.assertEqual(a["months"][0]["profit"], 300000 - 6000)
        self.assertEqual(a["months"][0]["cash"], 300000)
        self.assertEqual(a["year1_after_startup"], 12 * 300000 - 72000)
        self.assertEqual(a["year1_profit"], 12 * (300000 - 6000))

    def test_one_off_and_season_land_in_their_month(self):
        s = spec()
        a = ue.analyse(s)
        feb = a["months"][1]
        self.assertAlmostEqual(feb["per_day"], 90 * 0.85)
        self.assertEqual(feb["one_off"], 2864938)
        self.assertEqual(a["months"][0]["one_off"], 0)
        self.assertEqual(feb["label"], "Feb 2027")
        s["one_off"][0]["month"] = 13
        with self.assertRaises(ue.NumbersError):
            ue.analyse(s)
        s = spec()
        s["season"] = [1.0] * 11
        with self.assertRaises(ue.NumbersError):
            ue.analyse(s)

    def test_price_below_variable_cost_is_flagged(self):
        s = spec()
        s["price"] = 9000
        a = ue.analyse(s)
        self.assertTrue(math.isinf(a["breakeven_per_day"]))
        self.assertTrue(any("loses money" in f for f in a["flags"]))

    def test_breakeven_above_capacity_is_flagged(self):
        s = spec()
        s["capacity_per_day"] = 80
        a = ue.analyse(s)
        self.assertTrue(any("capacity is 80" in f for f in a["flags"]))

    def test_what_ifs_move_the_right_way(self):
        base = ue.analyse(spec())
        cheaper = ue.analyse(spec(), price=base["price"] * 0.9)
        fewer = ue.analyse(spec(), volume=0.8)
        self.assertLess(cheaper["year1_profit"], base["year1_profit"])
        self.assertGreater(cheaper["breakeven_per_day"], base["breakeven_per_day"])
        self.assertLess(fewer["year1_profit"], base["year1_profit"])
        self.assertEqual(len(ue.sensitivity(spec())), 4)

    def test_bad_input_is_refused_not_guessed(self):
        s = spec()
        s["ramp_per_day"] = [100] * 11
        with self.assertRaises(ue.NumbersError):
            ue.analyse(s)
        s = spec()
        del s["price"]
        with self.assertRaises(ue.NumbersError):
            ue.analyse(s)
        s = spec()
        s["variable"][0]["cost"] = "lots"
        with self.assertRaises(ue.NumbersError):
            ue.analyse(s)
        s = spec()
        s["start"] = "January"
        with self.assertRaises(ue.NumbersError):
            ue.analyse(s)

    def test_money_formats(self):
        self.assertEqual(ue.money(1250000), "Rp1.250.000")
        self.assertEqual(ue.money(-7546846.4), "-Rp7.546.846")
        self.assertEqual(ue.money(6.5, "USD", cents=True), "$6.50")

    def test_report_mentions_the_key_numbers(self):
        s = spec()
        text = ue.report(s, ue.analyse(s))
        for needle in ("Rp10.430", "95 cups a day", "**23%**", "Rp146.332.535", "month 11", "Feb 2027", "THR"):
            self.assertIn(needle, text)
        self.assertNotIn("$", text)


if __name__ == "__main__":
    unittest.main()
