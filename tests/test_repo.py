import json
import os
import re
import unittest

from _load import ROOT, SKILLS_DIR

BUILD = ["founder-board", "founder-competitors", "founder-consumer", "founder-pricing", "founder-offer", "founder-cfo",
         "founder-marketing", "founder-brand", "founder-ops", "founder-launch", "founder-plan"]
RUN = ["founder-weekly-report", "founder-pnl", "founder-cashflow", "founder-cost-leak", "founder-product-mix",
       "founder-staffing"]
SKILLS = BUILD + RUN + ["founder-indonesia"]
REFERENCE = ["tax.md", "permits.md", "payroll.md", "payments-channels.md", "calendar.md", "sources.md"]


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


EM = chr(0x2014)  # built in code so this file does not trip its own check


def text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".py", ".json", ".txt")) or f in ("LICENSE", ".gitignore"):
                yield os.path.join(base, f)


class Repo(unittest.TestCase):
    def test_eighteen_skill_folders(self):
        found = sorted(d for d in os.listdir(SKILLS_DIR) if os.path.isfile(os.path.join(SKILLS_DIR, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertRegex(fm, r"description: ", s)
            self.assertGreater(len(fm), 300, "%s description is too thin" % s)
            self.assertGreater(len(text.splitlines()), 60, s)

    def test_tools_named_in_skills_exist(self):
        for s in SKILLS:
            _, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            for tool in re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([\w.\-/]+\.(?:py|md))", text):
                self.assertTrue(os.path.exists(os.path.normpath(os.path.join(SKILLS_DIR, s, tool))), "%s: %s" % (s, tool))
            for other in re.findall(r"`/(founder-[\w-]+)", text):
                self.assertIn(other, SKILLS, "%s mentions /%s, which does not exist" % (s, other))

    def test_indonesia_reference_files(self):
        for f in REFERENCE:
            path = os.path.join(SKILLS_DIR, "founder-indonesia", "reference", f)
            self.assertTrue(os.path.isfile(path), f)
            self.assertIn("reference/%s" % f, frontmatter(os.path.join(SKILLS_DIR, "founder-indonesia", "SKILL.md"))[1])

    def test_no_dollars_in_the_indonesian_examples(self):
        for rel in ("founder-cfo/example.json", "founder-consumer/customer.example.json",
                    "founder-consumer/pitch.example.md"):
            with open(os.path.join(SKILLS_DIR, rel), encoding="utf-8") as fh:
                self.assertNotIn("$", fh.read(), rel)

    def test_run_skills_read_the_profile_and_keep_verification_rules(self):
        for s in RUN:
            _, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            self.assertIn("founder/profile.md", text, s)
            self.assertIn("## Verification rules (required)", text, s)
            self.assertIn("## Output format (fixed)", text, s)
            self.assertIn("## Save the report", text, s)
            self.assertIn("founder/reports/", text, s)
            self.assertIn("reports.py", text, s)

    def test_plugin_manifests(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "founder-id")
        self.assertIn("Indonesia", plugin["description"])
        self.assertEqual(plugin["license"], "MIT")
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["name"], "founder-id")
        self.assertEqual(market["plugins"][0]["name"], "founder-id")
        self.assertEqual(market["plugins"][0]["source"], "./")

    def test_readme_lists_every_skill_and_credits_the_fork(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = " ".join(fh.read().split())
        self.assertTrue(readme.startswith("# founder-id"))
        for line in ("https://github.com/Jakeschincariol/founder-skill", "## Fine print", "## Credit",
                     "/plugin install founder-id@founder-id"):
            self.assertIn(line, readme)
        for s in SKILLS:
            self.assertIn("/%s`" % s, readme)
        with open(os.path.join(ROOT, "LICENSE"), encoding="utf-8") as fh:
            self.assertIn("Jake Schincariol", fh.read())

    def test_examples_parse(self):
        for rel in ("founder-cfo/example.json", "founder-consumer/customer.example.json"):
            with open(os.path.join(SKILLS_DIR, rel), encoding="utf-8") as fh:
                json.load(fh)

    def test_no_em_dashes(self):
        for path in text_files():
            with open(path, encoding="utf-8") as fh:
                self.assertNotIn(EM, fh.read(), os.path.relpath(path, ROOT))


if __name__ == "__main__":
    unittest.main()
