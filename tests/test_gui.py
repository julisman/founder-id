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
        for view in ("state", "board", "competitors", "panel", "pricing", "cfo", "offer", "rounds"):
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


if __name__ == "__main__":
    unittest.main()
