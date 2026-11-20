/* English is the key; another language would map the English text to its own.
   Dotted keys (step.board, status.done, ...) have English entries too. */
(function () {
  "use strict";
  const STEPS = {
    board: ["Board", "Four lenses, including the Local market lens, score the idea and vote."],
    competitors: ["Competitors", "Who is already there, at what price, and the gap they leave."],
    consumer: ["Consumer panel", "100 simulated Indonesian buyers see the pitch: who buys, who passes, why."],
    pricing: ["Pricing", "The price range buyers accept, against competitors and margin."],
    offer: ["Offer", "Bonuses, guarantee and urgency that answer the objections."],
    cfo: ["CFO", "Unit economics in Rupiah: margin, break-even, year 1, cash needed."],
    marketing: ["Marketing", "Positioning, channels, a 30-day campaign and hooks."],
    brand: ["Brand", "Names, voice, promise and a brief for the look."],
    ops: ["Operations", "Suppliers, staffing at the UMK, routines, OSS permits and risks."],
    launch: ["Launch", "A cheap real test first, then a dated countdown."],
    plan: ["Business plan", "Everything in one plan, a computed verdict, and the profile for the run skills."],
  };
  const en = {
    "add": "Add",
    "lens.title": "{l} lens",
    "tab.pipeline": "Pipeline", "tab.board": "Board", "tab.competitors": "Competitors", "tab.panel": "Panel", "tab.pricing": "Pricing",
    "tab.offer": "Offer", "tab.cfo": "CFO", "tab.docs": "Docs", "tab.rounds": "Rounds",
    "status.empty": "not started", "status.partial": "partial", "status.done": "done", "status.stale": "re-run", "status.running": "running",
  };
  for (const [k, v] of Object.entries(STEPS)) { en["step." + k] = v[0]; en["role." + k] = v[1]; }
  // English only for now. To add a language (Bahasa Indonesia, say), map the English text to it
  // in a second dictionary and add it here: const DICT = { en, id };
  const DICT = { en };
  const I18N = {
    lang: "en",
    set(l) { this.lang = DICT[l] ? l : "en"; },
    t(key, vars) {
      let s = (DICT[I18N.lang] && DICT[I18N.lang][key]) || en[key] || key;
      if (vars) s = s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m));
      return s;
    },
  };
  window.I18N = I18N;
})();
