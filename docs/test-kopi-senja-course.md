# Run-skill test: Kopi Senja course data

Date: 2026-11-20. Model: Claude Opus 5.5, in the session that wrote the skills (a
fresh session would be a stronger test). Data: the AGJ course's fictional Kopi
Senja Demo (`demo/kopi-senja/`, CSVs and `profil-outlet.md`), periods as in the
course README. Each skill's `SKILL.md` was followed without reading the answer key;
the reports were saved to `founder/reports/` and checked with `reports.py`, then
compared with `expected-results.json` and `jawaban-pengajar.md`.

| skill | result against the key |
| --- | --- |
| founder-pnl (Oct) | pass: net sales Rp35.114.400, food cost 47,0462%, labour 28,4783%, profit Rp4.594.400, BEP Rp852.843,66/day |
| founder-weekly-report (26 Oct-1 Nov) | pass: -Rp1.999.200 (-24,04%), 252 transactions, ticket +1,28%, food cost 46,54% and 47,14%; exactly the 3 expected alerts, none extra; team version without profit, wages, cash or supplier names. Minor: the source line omitted the 28 purchase rows |
| founder-cost-leak (Oct) | pass: Ayam 23,6 kg / Rp944.000, waste 5,9 kg, unexplained 17,7 kg / Rp708.000 (75% of the gap), other items 0 |
| founder-staffing (5 Oct-1 Nov) | pass: 1,875 and 9,375 per staff, 10-12 overstaffed, 28 h/week, Rp2.424.800 labelled a simulation |
| founder-cashflow (2-29 Nov) | pass on every number, normal and pessimistic; weeks 1, 2, 4 at risk. Missed: weeks under the Rp4.000.000 safe minimum. Fixed in the skill |
| founder-product-mix (Oct) | same quadrants (A/B/C/D). Margins differ by design: founder-id deducts the GoFood commission (line Rp13.798), the key does not (Rp16.500). Two real faults, fixed in the skill: the new-price target mixed % with a Rupiah line, and "rise x qty x 0,9" overstated the gain (Rp1.062.000; correct about Rp507.040/month for Ayam Crispy at Rp26.000) |

All six saved JSON reports passed `reports.py check` and load in the dashboard.

Not tested yet: the course's problem cases (`kasus-bermasalah/`: three missing
sales days, a missing recipe), and a fresh session following the skills cold.
