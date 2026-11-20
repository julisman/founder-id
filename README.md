# founder-id

Eighteen Claude skills that test a business in Indonesia before you launch it,
then help you run it once it is open. Free, MIT, no signup, no API key, nothing
to connect. Numbers in Rupiah, rules from Indonesia, any kind of business: food
and drink, retail, online sellers, cosmetics, services, digital.

It joins two packs:

- **Build** (before opening): a fork of Jake Schincariol's
  [founder-skill](https://github.com/Jakeschincariol/founder-skill), rewritten for
  Indonesia. A board of directors, a competitor scout, a consumer panel of 100
  simulated Indonesian buyers, pricing, the offer, a CFO, marketing, brand,
  operations, a launch plan and the business plan.
- **Run** (after opening): the AGJ finance skills. A Monday report, a P&L in plain words,
  a 4-week cash forecast, a cost-leak check, product-mix analysis and staffing
  against busy hours.

The Indonesia desk links them: tax (PPh Final UMKM, PPN, PBJT), permits (OSS and
the NIB, KBLI, PIRT, BPOM, halal), payroll (UMK, BPJS, THR), payments and channels
(QRIS, e-wallets, COD, delivery apps, marketplaces) and the calendar (Ramadan,
Lebaran, mudik, payday, 11.11 and 12.12).

## Install

As a plugin, in Claude Code:

```
/plugin marketplace add julisman/founder-id
/plugin install founder-id@founder-id
```

Installed as a plugin the skills show up as `/founder-id:founder-board` and so on.
Copy the folders instead if you want plain `/founder-board`:

```bash
git clone https://github.com/julisman/founder-id.git
cp -r founder-id/skills/founder-* ~/.claude/skills/
```

Copy all the folders: several skills read files from `founder-indonesia`,
`founder-board` and `founder-cfo`. Project-local instead of global: copy them into
your repo's `.claude/skills/`. No Claude Code at all? Paste any single `SKILL.md`
at the top of a chat and it runs as a mode. You lose the sub-agents and the Python
tools, but the method works.

The tools need Python 3.8 or newer. Nothing to pip install.

## The eighteen

**Build: before you open**

| command | job | what it does |
| --- | --- | --- |
| `/founder-board` | Board of Directors | Four sub-agents, each applying one lens (Offers, from *$100M Offers*; Monopoly, from *Zero to One*; Product, from Isaacson's *Steve Jobs*; and the Local market lens for Indonesia), score the idea, name what would kill it and vote. |
| `/founder-competitors` | Competitor Scout | Direct, indirect, informal (warung, kaki lima, home sellers, resellers) and substitutes, from Google Maps, delivery apps, marketplaces, TikTok and Instagram, with prices per channel and what their customers complain about, every fact linked. |
| `/founder-consumer` | Consumer Panel | 100 simulated Indonesian buyers (monthly income in Rupiah, region, habits like promo hunting or ordering on the app), built to resist the polite yes. Who buys, who doesn't, and why. |
| `/founder-pricing` | Pricing Strategist | A Van Westendorp range in Rupiah from the panel, set against competitors per channel, the platform's cut and the margin. |
| `/founder-offer` | Offer Architect | The offer stack (bonuses, trust signals, guarantee, real urgency, a name) that answers the panel's objections, re-tested on the panel. |
| `/founder-cfo` | CFO | Unit economics in Rupiah: contribution after commissions and PPh Final, the real margin, break-even per day, year 1 month by month with Ramadan, THR and rent paid up front, cash needed, payback, what-ifs. |
| `/founder-marketing` | Marketing Director | Positioning, the channels Indonesian buyers use, a dated 30-day campaign around payday and the calendar, ten hooks, the most you can pay for a customer. |
| `/founder-brand` | Brand Designer | Names with the PDKI trademark, .id domain and handle checks, a voice, a promise and a brief for the look. |
| `/founder-ops` | Operations Manager | Suppliers, a rota at the UMK with BPJS and THR, SOPs, tools, the OSS permits and certificates, a risk register. |
| `/founder-launch` | Launch Lead | A cheap real test first (WhatsApp pre-order, bazaar stall, test listing), then a dated countdown around permit lead times, the launch-day run sheet and the first 30 days. |
| `/founder-plan` | Business Planner | One business plan with a computed verdict: Profitable, Not yet or Incomplete. Also writes `founder/profile.md` for the run skills. |

**Run: after you open**

| command | was | what it does |
| --- | --- | --- |
| `/founder-weekly-report` | `agj-laporan-senin` | The Monday report: last week against the week before, alerts only when a threshold is crossed, one action, a team version. |
| `/founder-pnl` | `agj-pnl-bahasa-owner` | The month's P&L in the owner's words, commissions and tax on their own lines, prive taken out. |
| `/founder-cashflow` | `agj-cashflow-4-minggu` | Cash week by week for 4 weeks with each channel's payout delay, supplier terms, payroll, THR, BPJS and tax; flags the weeks at risk. |
| `/founder-cost-leak` | `agj-deteksi-bocor-food-cost` | What was bought against what sales explain (recipes, bills of materials, or unit stock): the five biggest gaps in Rupiah and how to check them. |
| `/founder-product-mix` | `agj-menu-engineering` | Stars, Plowhorses, Puzzles, Dogs by margin after channel fees and volume; new prices capped at 10% a round. |
| `/founder-staffing` | `agj-jadwal-vs-jam-ramai` | Workload per hour against the roster: overstaffed and understaffed slots, a new roster within the working-time rules, the saving. |

**Always**

| command | job |
| --- | --- |
| `/founder-indonesia` | The Indonesia desk: tax, permits, payroll, payments and channels, calendar, and the official sources to confirm each. |

## How to use it

Run the build skills in this order. Each one reads what the others wrote, in a
`founder/` folder in your project.

```
build:  board -> competitors -> consumer -> pricing -> offer -> cfo -> marketing -> brand -> ops -> launch -> plan
run:    weekly-report every Monday; pnl and cashflow every month; cost-leak, product-mix, staffing when an alert says so
always: indonesia
```

An example: Kopi Senja, a grab-and-go kopi susu kiosk by the Blok M MRT in South
Jakarta, es kopi susu gula aren at Rp22.000 a cup, 40% of cups sold on the
delivery apps. (Every input is in the example files in this repo, so you can run
the tools on it.)

1. **`/founder-board`** writes `founder/idea.md` and puts it in front of four
   board members. The Local market member asks why a buyer would leave the big
   chain with its app vouchers, and what the apps' cut leaves.
2. **`/founder-competitors`** maps the chains, the independent counters and the
   kopi keliling within walking distance and on GoFood, with prices per channel.
3. **`/founder-consumer`** deals 100 buyers across students, office staff and
   managers, from promo hunters to app-only orderers, and tallies who buys.
4. **`/founder-pricing`** and **`/founder-offer`** set the counter and app prices
   and build the opening offer.
5. **`/founder-cfo`** runs the numbers. With the example: each cup leaves Rp10.430
   after ingredients, packaging, the app commission and PPh Final; break-even is 95
   cups a day; the margin at the planned 180 cups a day is 23%; year 1 makes
   Rp146.332.535 on operations after a slow ramp, a Ramadan dip and pro-rata THR;
   the Rp196.000.000 startup spend (including a year of rent paid up front) is
   earned back in month 11; January to March lose money and the tool flags them.
6. **`/founder-marketing`**, **`/founder-brand`**, **`/founder-ops`** and
   **`/founder-launch`** turn it into a campaign timed to payday, a name with its
   PDKI checks, the NIB and halal self-declare steps, a rota at the Jakarta UMP and
   a launch that starts with a weekend bazaar stall.
7. **`/founder-plan`** compiles `founder/business-plan.md` with a computed verdict,
   and `founder/profile.md` with the break-even per day and alert thresholds.
8. After opening, **`/founder-weekly-report`** every Monday reads that profile and
   says when to run the cost-leak, product-mix, cash-flow or staffing skill.

## The tools

Four of them, all standard-library Python. None touch the network.

```bash
python3 skills/founder-cfo/unit_economics.py founder/numbers.json --out founder/cfo.md   # margins, break-even, year 1
python3 skills/founder-consumer/panel.py init --customer founder/customer.json --pitch founder/pitch.md
python3 skills/founder-pricing/van_westendorp.py founder/panel/answers --price 22000     # the acceptable price range
python3 skills/founder-plan/compile.py --dir founder                                     # the plan, its verdict, the profile
```

**`unit_economics.py`** reads one JSON (example: `skills/founder-cfo/example.json`).
On top of the original it handles Rupiah, costs as a share of price (commissions,
payment fees, PPh Final) with a channel `share`, seasonal multipliers, one-off
months (THR), and rent prepaid for the year, keeping profit and cash apart. Every
number traces to an input; a missing field is an error, never a guess.

**`panel.py`** deals persona cards from your target customer (same seed, same
cards), with monthly incomes in Rupiah, Indonesian names and optional regions,
writes one brief per buyer, checks the answers and tallies them. It never answers
for a buyer.

**`van_westendorp.py`** reads four price answers per buyer (from the panel, or a
CSV from a real survey; `22000`, `Rp22.000` and `22.000` all read as twenty-two
thousand) and finds the acceptable range.

**`compile.py`** assembles the plan, computes the verdict and writes the profile.

```bash
python3 -m unittest discover -s tests -v
```

## Fine print

**The board applies published frameworks. It is not those people.** Three lenses
are short summaries, in our words, of ideas from *$100M Offers* by Alex Hormozi,
*Zero to One* by Peter Thiel with Blake Masters, and Walter Isaacson's biography of
Steve Jobs. The fourth is this pack's own checklist. The board never speaks as
anyone, quotes them or claims they endorse anything. This project is not
affiliated with any of them.

**The consumer panel is simulated buyers, not customers.** It is a fast, cheap way
to find objections, segments and wording before you spend. It is not a forecast:
language models lean agreeable, and so do polite real buyers, so read the buy rate
as an upper bound and confirm the big calls with real people. `/founder-launch`
starts with exactly that test. Panel answers are research; never use them as
testimonials.

**Indonesian rules change.** Tax rates, the halal deadlines, QRIS fees, platform
commissions and minimum wages all changed in 2025 and 2026. The reference files in
`skills/founder-indonesia/reference/` are dated, and the skills confirm current
figures on the official sources before using them.

**The numbers are only as good as the inputs.** The CFO marks every estimate as an
estimate and asks for real quotes. Check costs with suppliers and the structure,
payroll and tax with an accountant or konsultan pajak.

**Research uses public sources, with links.** No invented competitors, prices,
reviews or quotes. No scraping against a site's terms.

**Not financial, legal or tax advice.** The skills tell you what to check and
where; a professional confirms it.

## Files

```
skills/founder-indonesia/    SKILL.md, reference/ (tax, permits, payroll, payments-channels, calendar, sources)
skills/founder-board/        SKILL.md, lenses.md
skills/founder-competitors/  SKILL.md
skills/founder-consumer/     SKILL.md, panel.py, customer.example.json, pitch.example.md
skills/founder-pricing/      SKILL.md, van_westendorp.py
skills/founder-offer/        SKILL.md
skills/founder-cfo/          SKILL.md, unit_economics.py, example.json
skills/founder-marketing/    SKILL.md
skills/founder-brand/        SKILL.md
skills/founder-ops/          SKILL.md
skills/founder-launch/       SKILL.md
skills/founder-plan/         SKILL.md, compile.py
skills/founder-weekly-report/ skills/founder-pnl/ skills/founder-cashflow/
skills/founder-cost-leak/    skills/founder-product-mix/ skills/founder-staffing/
tests/                       the tests for every tool and the repo
```

Your own files live in `founder/` in your project. The skills read each other's.

## Credit

The build skills are a fork of [founder-skill](https://github.com/Jakeschincariol/founder-skill)
by Jake Schincariol ([opusjake.ai](https://opusjake.ai)), MIT. The run skills come
from the AGJ finance skills for F&B owners. Both under the MIT licence in
`LICENSE`.

## License

MIT. Take it, change it, ship it.
