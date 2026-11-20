import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

plan = load("founder-plan", "compile")


class Compile(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "idea.md"), "w") as fh:
            fh.write("# Kopi Senja\n\nA kopi susu kiosk by the Blok M MRT.\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def numbers(self, **change):
        with open(example("founder-cfo", "example.json")) as fh:
            s = json.load(fh)
        s.update(change)
        with open(os.path.join(self.d, "numbers.json"), "w") as fh:
            json.dump(s, fh)

    def panel(self, buys, n=100):
        os.makedirs(os.path.join(self.d, "panel"), exist_ok=True)
        with open(os.path.join(self.d, "panel", "results.json"), "w") as fh:
            json.dump({"buys": buys, "passes": n - buys, "answered": n, "buy_rate": buys / float(n)}, fh)

    def test_no_numbers_is_incomplete(self):
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Incomplete")
        self.assertIn("run /founder-cfo", text)

    def test_good_numbers_and_panel_is_profitable(self):
        self.numbers()
        self.panel(40)
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Profitable")
        self.assertTrue(text.startswith("# Kopi Senja · Business plan"))
        self.assertIn("| Profit margin at plan | 23% per cup |", text)
        self.assertIn("| Price | Rp22.000 a cup |", text)
        self.assertIn("Each cup earns Rp10.430", text)
        self.assertNotIn("$", text)
        self.assertIn("40 buy · 60 pass", text)
        self.assertIn("- The buyer panel: run /founder-consumer", text.replace("## Not done yet", ""))

    def test_a_weak_panel_means_not_yet(self):
        self.numbers()
        self.panel(12)
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Not yet")
        self.assertIn("✗ 12 of 100 simulated buyers buy", text)

    def test_losing_money_means_not_yet(self):
        self.numbers(price=9000)
        v, _ = plan.compile_plan(self.d)
        self.assertEqual(v, "Not yet")


class Profile(unittest.TestCase):
    def test_main_writes_the_profile_for_the_run_skills(self):
        d = tempfile.mkdtemp()
        try:
            with open(example("founder-cfo", "example.json")) as fh, open(os.path.join(d, "numbers.json"), "w") as out:
                out.write(fh.read())
            self.assertEqual(plan.main(["--dir", d, "--profile-only"]), 0)
            with open(os.path.join(d, "profile.md"), encoding="utf-8") as fh:
                prof = fh.read()
            self.assertIn("Break-even per day: 95 cups, Rp2.070.619 of sales", prof)
            self.assertIn("Weekly sales target at plan: Rp27.720.000", prof)
            self.assertIn("direct goods cost (COGS / food cost): 44.1% of price", prof)
            self.assertIn("alert: 49% of net sales", prof)
            self.assertFalse(os.path.exists(os.path.join(d, "business-plan.md")))
            self.assertEqual(plan.main(["--dir", d]), 0)
            self.assertTrue(os.path.exists(os.path.join(d, "business-plan.md")))
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
