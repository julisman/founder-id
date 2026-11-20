# founder-id dashboard

A local, read-only web page for reading what the build skills wrote: every step,
every result, live while the skills run. It reads the same `founder/` folder the
skills write, and every number comes from the skills' own Python tools
(`unit_economics.py`, `panel.py`, `van_westendorp.py`, `compile.py`), so the page
and the terminal never disagree. Money is shown in Rupiah.

Standard library only, like the rest of the pack. Python 3.8 or newer, nothing
to install, no network: the server listens on 127.0.0.1.

```bash
python3 gui/serve.py --dir path/to/project            # opens the browser
python3 gui/demo.py /tmp/kopi-senja-demo              # a demo project from the Kopi Senja example
python3 gui/serve.py --dir /tmp/kopi-senja-demo
```

From Claude Code, with the plugin installed: `/founder-id:founder-gui` to start
it, `/founder-id:founder-gui-stop` to stop it. Or press **■ stop** at the bottom of
the sidebar (twice, so it is not hit by accident), or from a terminal:

```bash
python3 gui/serve.py --status    # is it running, and where
python3 gui/serve.py --stop      # stop it; your founder/ files and the project list stay
```

## What it shows

| view | what is on it |
| --- | --- |
| Pipeline | the eleven build steps with their status (not started, partial, done, re-run, running), the computed verdict and its checks, the board's conditions as a checklist, the business profile from `profile.md`, a one-line summary of what was saved after opening, the next step and its command |
| Board | the four memos side by side (Offers, Monopoly, Product, Local market): score, vote, risks, conditions |
| Competitors | the table from `competitors.csv` (with the channel each price was seen on and the trust signals) and price against rating |
| Panel | the buyers as tiles that fill in as answers arrive; filter by segment, behaviour, answer; open a buyer for the persona, the answer and the brief it got; buy rate by segment, behaviour, income and region; why they pass, why they buy, what would flip a no |
| Pricing | the Van Westendorp curves in Rupiah with the acceptable range, your price, competitor prices and the unit cost |
| Offer | the pitch before and after, word by word |
| CFO | the key numbers, year 1 month by month (profit and cash side by side, the season multiplier, THR and other one-off costs), the three what-ifs, and a what-if simulator (price, volume, unit costs, commissions and fees, fixed and startup costs) that runs `unit_economics.py` on a copy |
| After opening | the run skills' saved reports as trends: net sales by week against break-even, direct cost by week against its alert, last week day by day, channels, every alert and action, the 4-week cash forecast with the weeks at risk, the P&L month by month (in plain words, where every Rp100.000 goes as stacked bars, and net margin against the healthy margin in `profile.md`), the latest cost leak, product mix and staffing heatmap |
| Docs | every file in `founder/`, rendered, including `profile.md` and the saved reports |
| Rounds | dated copies of `founder/`, compared side by side |

## How it works

- **Live.** The hub polls `founder/` once a second and pushes changes to the page
  (server-sent events). A step counts as running while its files keep changing,
  and as "re-run" when a file it depends on changed after it ran (for example
  `pitch.md` rewritten by the offer after the panel saw it).
- **Analysis.** The what-if simulator never edits `numbers.json`. Rounds are dated
  copies of `founder/` you can compare: save one, change the price or the pitch,
  re-run the skill, compare.
- **Export HTML.** One self-contained file, the same page with the data frozen
  inside, that opens anywhere, offline, read-only. Good for sending to a partner
  or a bank.
- **One hub for every project.** The first `/founder-id:founder-gui` starts the hub
  (`~/.founder-id-gui/hub.json` says where it is); later ones, from other folders,
  only add their folder to it. The sidebar lists them all.

It never starts a Claude session and never changes the skills' files.

## After opening

The run skills answer in the chat and also save each report in
`founder/reports/<kind>/` as a `.md` (the report as shown) and a `.json` (its key
numbers). `skills/founder-weekly-report/reports.py` says where each one goes and
checks its arithmetic (daily sales add up to the week, cash balances chain week to
week, net profit follows from the lines). A report that does not add up shows with
a warning instead of being drawn as if it were right.

## Files

The dashboard only writes in `founder/.gui/`: its own state (rounds, checklist
ticks).

## Security

It binds to 127.0.0.1, refuses any Host header other than localhost (DNS
rebinding), and every write needs an `X-Founder-GUI` header that a page on
another site cannot send without a CORS preflight, which the hub never answers.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

`tests/test_gui.py` builds the demo project (build stage plus six weeks of
reports after opening), checks every view against the example numbers (Rp10.430 a cup, break-even 95 a day, Rp146.332.535 in year 1),
checks the what-if leaves `numbers.json` alone, compares rounds, checks the
security guards and the export, and checks that no run or feedback endpoint
exists.

## Credit

Ported from Luis Siqueira's Founder GUI
([pull request #5](https://github.com/Jakeschincariol/founder-skill/pull/5) on
founder-skill, MIT): the viewer and analysis parts, adapted for founder-id and
Rupiah. The feedback and browser-run parts were left out.
