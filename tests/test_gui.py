import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request

from _load import ROOT

sys.path.insert(0, os.path.join(ROOT, "gui"))

import demo  # noqa: E402
from founder_gui import registry, rounds, server, steps  # noqa: E402
from founder_gui.project import NotFound, Project  # noqa: E402

def slurp(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def build_demo(upto="plan"):
    d = tempfile.mkdtemp(prefix="fgui-")
    with open(os.devnull, "w") as null:
        old, sys.stdout = sys.stdout, null
        try:
            demo.main([d, "--upto", upto])
        finally:
            sys.stdout = old
    return d


class Steps(unittest.TestCase):
    def test_status_from_files(self):
        now = 1000.0
        files = {"idea.md": 100, "board.md": 101, "board/offers.md": 100, "competitors.csv": 102}
        st = {s["key"]: s for s in steps.status(files, now=now)}
        self.assertEqual(st["board"]["status"], "done")
        self.assertEqual(st["competitors"]["status"], "partial")
        self.assertEqual(st["consumer"]["status"], "empty")
        self.assertEqual(steps.next_step(list(st.values())), "competitors")

    def test_stale_when_a_dependency_is_newer(self):
        files = {"pitch.md": 500, "panel/results.md": 100, "customer.json": 90}
        st = {s["key"]: s for s in steps.status(files, now=10000)}
        self.assertEqual(st["consumer"]["status"], "stale")
        self.assertEqual(st["consumer"]["stale_by"], ["pitch.md"])

    def test_running_when_just_written_or_gui_run(self):
        st = {s["key"]: s for s in steps.status({"board.md": 995}, now=1000)}
        self.assertEqual(st["board"]["status"], "running")
        st = {s["key"]: s for s in steps.status({}, active_runs={"cfo"}, now=1000)}
        self.assertEqual(st["cfo"]["status"], "running")

    def test_owner(self):
        self.assertEqual(steps.owner("panel/answers/P001.json"), "consumer")
        self.assertEqual(steps.owner("cfo.md"), "cfo")
        self.assertIsNone(steps.owner("feedback/cfo.md"))


class ProjectReads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = build_demo()
        cls.p = Project(cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_resolve_accepts_root_or_founder(self):
        self.assertEqual(Project(self.dir).fdir, Project(os.path.join(self.dir, "founder")).fdir)

    def test_numbers_match_the_example(self):
        a = self.p.cfo()["analysis"]
        self.assertAlmostEqual(a["contribution"], 10430, places=2)
        self.assertEqual(round(a["year1_profit"]), 146332535)
        self.assertEqual(len(a["variable_items"]), 7)
        self.assertEqual(len(a["startup_items"]), 8)
        self.assertEqual(self.p.verdict()["verdict"], "Profitable")

    def test_state_is_json_safe(self):
        st = self.p.state()
        json.dumps(st, allow_nan=False)
        self.assertEqual(len(st["steps"]), 11)
        self.assertEqual(st["name"], "Kopi Senja")
        self.assertEqual(st["currency"], "IDR")
        self.assertEqual(len(st["checklist"]), 6)
        self.assertIn("profile.md", [d["path"] for d in st["docs"]])

    def test_panel_and_pricing(self):
        pn = self.p.panel()
        self.assertEqual((pn["n"], pn["answered"]), (100, 100))
        self.assertIsNotNone(pn["live"]["buy_rate"])
        pr = self.p.pricing()
        self.assertEqual(len(pr["curves"]["grid"]), 121)
        self.assertEqual(len(pr["competitors"]), 6)
        self.assertEqual(pr["competitors"][0]["price"], 24000)  # "Rp24.000" read as Rupiah, not 24

    def test_whatif_never_touches_numbers_json(self):
        path = os.path.join(self.p.fdir, "numbers.json")
        before = slurp(path)
        a = self.p.whatif({"price": 24000, "volume": 0.8, "fixed_scale": 1.1})
        self.assertEqual(a["price"], 24000)
        self.assertEqual(slurp(path), before)
        base = self.p.cfo()["analysis"]
        no_fees = self.p.whatif({"pct_scale": 0})
        self.assertAlmostEqual(no_fees["contribution"] - base["contribution"], 1760 + 110)
        self.assertEqual(slurp(path), before)

    def test_paths_cannot_escape_founder(self):
        with self.assertRaises(NotFound):
            self.p.read("../../etc/passwd")
        with self.assertRaises(NotFound):
            self.p.brief("../x")

    def test_profile_card_and_competitor_columns(self):
        st = self.p.state()
        sections = [x["section"] for x in st["profile"]]
        self.assertIn("From the plan", sections)
        rows = dict(st["profile"][0]["rows"])
        self.assertIn("95 cups", rows["Break-even per day"])
        comp = self.p.competitors()["rows"]
        self.assertEqual(comp[0]["price_channel"], "counter")
        self.assertIn("informal", {r["type"] for r in comp})

    def test_cfo_months_carry_cash_and_one_offs(self):
        a = self.p.cfo()["analysis"]
        feb = a["months"][1]
        self.assertEqual(feb["label"], "Feb 2027")
        self.assertEqual(feb["one_off"], 2864938)
        self.assertEqual(feb["cash"] - feb["profit"], 8000000)  # rent prepaid: profit counts it, cash does not
        self.assertEqual(a["one_off"][0][0], 2)

    def test_run_stage_reports(self):
        r = self.p.run()
        self.assertTrue(r["any"])
        counts = {k["kind"]: k["count"] for k in r["kinds"]}
        self.assertEqual(counts, {"weekly": 6, "pnl": 4, "cashflow": 1, "cost-leak": 1, "product-mix": 1, "staffing": 1})
        self.assertEqual(r["targets"]["healthy_margin"], 0.10)  # read from profile.md
        apr = r["reports"]["pnl"][0]
        base = apr["net_sales"] + apr["platform_commission"]
        parts = apr["direct_cost"] + apr["labour"] + apr["fixed_costs"] + apr["pph_final"] + apr["platform_commission"] + apr["net_profit"]
        self.assertAlmostEqual(parts, base)  # the Rp100.000 split adds up to what came in
        self.assertEqual(sum(k["problems"] for k in r["kinds"]), 0)  # the demo passes its own checks
        self.assertEqual(r["reports"]["weekly"][0]["week"], "2027-W19")  # newest first
        self.assertEqual(round(r["targets"]["breakeven_week"]), 14494331)
        self.assertEqual([w["status"] for w in r["reports"]["cashflow"][0]["weeks"]], ["safe", "safe", "watch", "at risk"])
        st = self.p.state()
        self.assertIn("1 week(s) at risk", st["run_summary"])
        self.assertIn("reports", {d["step"] for d in st["docs"]})
        json.dumps(r, allow_nan=False)

    def test_healthy_margin_follows_profile(self):
        path = os.path.join(self.p.fdir, "profile.md")
        before = slurp(path)
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(before.replace("Healthy net margin: at least 10%", "Healthy net margin: at least 12,5%"))
            self.assertEqual(self.p.run()["targets"]["healthy_margin"], 0.125)
        finally:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(before)

    def test_build_only_demo_has_no_run_stage(self):
        d = tempfile.mkdtemp(prefix="fgui-")
        try:
            with open(os.devnull, "w") as null:
                old, sys.stdout = sys.stdout, null
                try:
                    demo.main([d, "--no-run"])
                finally:
                    sys.stdout = old
            p = Project(d)
            self.assertFalse(p.run()["any"])
            self.assertIsNone(p.state()["run_summary"])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_board_memos(self):
        b = self.p.board()
        self.assertEqual(sorted(m["lens"] for m in b["memos"]), ["local-market", "monopoly", "offers", "product"])
        self.assertEqual({m["vote"] for m in b["memos"]}, {"FUND", "FUND IF", "PASS"})

    def test_checklist_tick(self):
        cid = self.p.checklist()[0]["id"]
        self.p.tick(cid, True, "panel says 31%")
        self.assertTrue(self.p.checklist()[0]["done"])


class Rounds(unittest.TestCase):
    def test_snapshot_and_compare(self):
        d = build_demo()
        try:
            p = Project(d)
            r1 = rounds.snapshot(p, "Pitch v1")
            self.assertTrue(r1["id"].endswith("pitch-v1"))
            with open(os.path.join(p.fdir, "offer.md"), "a") as fh:
                fh.write("\nA new bonus.\n")
            c = rounds.compare(p, r1["id"], "current")
            self.assertIn("offer.md", c["changed"])
            self.assertEqual(c["a"]["metrics"]["verdict"], "Profitable")
            self.assertEqual(rounds.as_project(p, r1["id"]).name(), "Kopi Senja")
            self.assertEqual(len(rounds.listing(p)), 1)
            with self.assertRaises(ValueError):
                rounds.as_project(p, "../../x")
        finally:
            shutil.rmtree(d, ignore_errors=True)


class Stop(unittest.TestCase):
    def test_shutdown_needs_the_header_then_stops_the_hub(self):
        home = tempfile.mkdtemp(prefix="fgui-home-")
        os.environ["FOUNDER_GUI_HOME"] = home
        try:
            app, httpd = server.serve(0)
            port = httpd.server_address[1]
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()

            def post(headers):
                req = urllib.request.Request("http://127.0.0.1:%d/api/shutdown" % port, method="POST", data=b"{}",
                                             headers=dict({"Content-Type": "application/json"}, **headers))
                try:
                    with urllib.request.urlopen(req, timeout=5) as r:
                        return r.status
                except urllib.error.HTTPError as e:
                    with e:
                        return e.code
            self.assertEqual(post({}), 403)  # a page on another site cannot stop it
            self.assertTrue(t.is_alive())
            self.assertEqual(post({server.HEADER: "1"}), 200)
            t.join(5)
            self.assertFalse(t.is_alive())
            httpd.server_close()
        finally:
            os.environ.pop("FOUNDER_GUI_HOME", None)
            shutil.rmtree(home, ignore_errors=True)


class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = tempfile.mkdtemp(prefix="fgui-home-")
        os.environ["FOUNDER_GUI_HOME"] = cls.home
        cls.dir = build_demo()
        cls.pid = registry.add(cls.dir).id
        cls.app, cls.httpd = server.serve(0)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.app.watcher.stop()
        os.environ.pop("FOUNDER_GUI_HOME", None)
        shutil.rmtree(cls.home, ignore_errors=True)
        shutil.rmtree(cls.dir, ignore_errors=True)

    def call(self, path, method="GET", body=None, headers=None):
        h = {"Content-Type": "application/json"}
        h.update(headers or {})
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path), method=method, headers=h,
                                     data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            with e:
                return e.code, e.read()

    def test_ping_and_views(self):
        code, body = self.call("/api/ping")
        self.assertEqual((code, json.loads(body)["app"]), (200, "founder-id-gui"))
        for view in ("state", "board", "competitors", "panel", "pricing", "cfo", "offer", "run", "rounds"):
            code, body = self.call("/api/p/%s/%s" % (self.pid, view))
            self.assertEqual(code, 200, view)
        code, body = self.call("/")
        self.assertIn(b"founder-id", body)

    def test_read_only_dashboard_has_no_runs_or_feedback(self):
        for path, method in (("/api/p/%s/runs" % self.pid, "GET"), ("/api/p/%s/runs" % self.pid, "POST"),
                             ("/api/p/%s/feedback" % self.pid, "GET"), ("/api/p/%s/feedback/board" % self.pid, "POST")):
            code, _ = self.call(path, method, {} if method == "POST" else None, {server.HEADER: "1"})
            self.assertEqual(code, 404, path)
        for mod in ("runs", "sessions", "feedback"):
            self.assertFalse(os.path.exists(os.path.join(ROOT, "gui", "founder_gui", mod + ".py")), mod)

    def test_writes_need_the_header(self):
        code, _ = self.call("/api/p/%s/rounds" % self.pid, "POST", {"label": "x"})
        self.assertEqual(code, 403)
        code, _ = self.call("/api/p/%s/rounds" % self.pid, "POST", {"label": "x"}, {server.HEADER: "1"})
        self.assertEqual(code, 200)

    def test_foreign_host_is_refused(self):
        code, _ = self.call("/api/ping", headers={"Host": "evil.example:80"})
        self.assertEqual(code, 403)

    def test_static_cannot_escape(self):
        code, _ = self.call("/static/../founder_gui/server.py")
        self.assertEqual(code, 404)

    def test_export_is_self_contained(self):
        code, body = self.call("/api/p/%s/export" % self.pid)
        html = body.decode()
        self.assertEqual(code, 200)
        self.assertIn("window.__FOUNDER_SNAPSHOT__", html)
        self.assertNotIn('src="/static/', html)
        self.assertNotIn('href="/static/', html)
        self.assertIn("Rp10.430", html)  # the CFO report travels inside the snapshot
        self.assertIn("2027-W19", html)  # and the run-stage reports


if __name__ == "__main__":
    unittest.main()
