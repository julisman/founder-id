/* Founder GUI: the page. Plain JS, no build step.
   Reads the hub's JSON API, re-renders the open view when files change (SSE),
   and in an exported file reads the frozen snapshot instead. */
(function () {
  "use strict";
  const SNAP = window.__FOUNDER_SNAPSHOT__ || null;
  const esc = MD.esc, t = I18N.t;
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));

  const STEP_TAB = { board: "board", competitors: "competitors", consumer: "panel", pricing: "pricing", offer: "offer", cfo: "cfo" };
  const TABS = ["pipeline", "board", "competitors", "panel", "pricing", "offer", "cfo", "run", "docs", "rounds"];
  const TAB_STEPS = { board: ["board"], competitors: ["competitors"], panel: ["consumer"], pricing: ["pricing", "consumer"], offer: ["offer", "consumer"], cfo: ["cfo"] };
  const S = { projects: [], pid: null, tab: "pipeline", sub: null, query: {}, st: null, ui: {} };

  // ── helpers ──────────────────────────────────────────────────────────────────
  async function api(url, opts) {
    opts = opts || {};
    if (SNAP) {
      if (opts.method && opts.method !== "GET") throw new Error(t("Read-only export"));
      const key = decodeURIComponent(url.replace(/[?&]round=[^&]*/, ""));
      if (key in SNAP.data) return JSON.parse(JSON.stringify(SNAP.data[key]));
      throw new Error(t("Not included in this export"));
    }
    const r = await fetch(url, { method: opts.method || "GET", headers: { "Content-Type": "application/json", "X-Founder-GUI": "1" },
      body: opts.body ? JSON.stringify(opts.body) : undefined });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { const e = new Error(j.error || r.statusText); e.status = r.status; e.data = j; throw e; }
    return j;
  }
  const P = (view, extra) => {
    const q = new URLSearchParams(extra || {});
    if (S.query.round) q.set("round", S.query.round);
    const s = q.toString();
    return "/api/p/" + S.pid + "/" + view + (s ? "?" + s : "");
  };
  const fileUrl = path => P("file", { path });
  const LOC = () => "en-US";  // dates and plain counts
  const CUR = () => (S.st && S.st.currency) || "IDR";
  // Rupiah the way the CFO tool writes it: Rp1.250.000, no decimals. Dollars keep cents when asked.
  const money = (v, d) => {
    if (v == null || !isFinite(v)) return "n/a";
    const sign = v < 0 ? "-" : "";
    if (CUR() === "IDR") return sign + "Rp" + Math.round(Math.abs(v)).toLocaleString("id-ID");
    return sign + "$" + Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d == null ? 0 : d, maximumFractionDigits: d == null ? 0 : d });
  };
  const money2 = v => money(v, 2);
  const pct = (v, d) => v == null ? "n/a" : (v * 100).toFixed(d || 0) + "%";
  const intf = v => v == null ? "n/a" : (isFinite(v) ? Math.ceil(v).toLocaleString(LOC()) : "never");
  function ago(ts) {
    if (!ts) return "";
    const s = Date.now() / 1000 - ts;
    if (s < 60) return t("just now");
    if (s < 3600) return t("{n} min ago", { n: Math.floor(s / 60) });
    if (s < 86400) return t("{n} h ago", { n: Math.floor(s / 3600) });
    return new Date(ts * 1000).toLocaleDateString(LOC());
  }
  function toast(msg) {
    const el = $("#toast"); el.textContent = msg; el.hidden = false;
    clearTimeout(toast._t); toast._t = setTimeout(() => { el.hidden = true; }, 3200);
  }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  const chip = (cls, text) => '<span class="chip ' + esc(cls) + '">' + esc(text) + "</span>";
  const stepName = k => t("step." + k);
  const empty = msg => '<div class="empty">' + msg + "</div>";
  const cmd = k => "/founder-id:founder-" + k;

  // ── routing ──────────────────────────────────────────────────────────────────
  function parseHash() {
    const h = location.hash.replace(/^#\/?/, "");
    const [path, qs] = h.split("?");
    const parts = path.split("/").filter(Boolean);
    S.query = Object.fromEntries(new URLSearchParams(qs || ""));
    if (parts[0] === "p" && parts[1]) {
      S.pid = parts[1]; S.tab = TABS.includes(parts[2]) ? parts[2] : "pipeline"; S.sub = parts.slice(3).join("/") || null;
    } else if (SNAP) {
      S.pid = SNAP.project; S.tab = "pipeline"; S.sub = null;
    } else { S.pid = null; }
  }
  function go(tab, sub, query) {
    const q = new URLSearchParams(query || (S.query.round ? { round: S.query.round } : {})).toString();
    location.hash = "#/p/" + S.pid + "/" + tab + (sub ? "/" + sub : "") + (q ? "?" + q : "");
  }

  // ── sidebar ──────────────────────────────────────────────────────────────────
  async function loadProjects() {
    try { S.projects = await api("/api/projects"); } catch (e) { S.projects = []; }
    renderProjects();
  }
  function renderProjects() {
    $("#projects").innerHTML = S.projects.map(p => {
      return '<a class="proj' + (p.id === S.pid ? " on" : "") + '" href="#/p/' + p.id + '/pipeline" title="' + esc(p.root) + '">' +
        '<div class="t"><span>' + esc(p.name) + "</span>" + (p.running.length ? chip("running", t("live")) : "") + "</div>" +
        '<div class="meta" style="margin-top:2px"><span class="num" style="font-size:11px">' + esc(p.root.split("/").pop()) + "/</span></div>" +
        '<div class="meta"><span class="verdict ' + esc(p.verdict.replace(" ", "-")) + '" style="padding:0 6px;font-size:10.5px">' + esc(t(p.verdict)) + "</span>" +
        "<span>" + p.done + "/" + p.total + "</span>" +
        "<span>" + esc(ago(p.updated)) + "</span></div></a>";
    }).join("") || '<div class="muted" style="padding:6px">' + esc(t("No projects yet")) + "</div>";
    $("#hub-note").textContent = SNAP ? t("Exported report") : t("{n} projects", { n: S.projects.length });
  }

  // ── main frame ───────────────────────────────────────────────────────────────
  async function render() {
    parseHash();
    renderProjects();
    const main = $("#main");
    if (!S.pid) { main.innerHTML = welcome(); return; }
    try {
      S.st = await api(P("state"));
    } catch (e) {
      main.innerHTML = '<div class="empty-state"><h1>' + esc(t("Project not found")) + "</h1><p>" + esc(e.message) + "</p></div>";
      return;
    }
    main.innerHTML = '<div id="hdr">' + header() + '</div><div id="view"></div>';
    bindHeader();
    await renderView();
  }

  function welcome() {
    return '<div class="empty-state"><h1>Founder GUI</h1><p>' + esc(t("Follow the founder skills in the browser: every step, suggestion and result, live while Claude works.")) +
      "</p><p>" + esc(t("Open a project from Claude Code:")) + "</p><pre>/founder-id:founder-gui</pre><p>" + esc(t("or from a terminal:")) +
      "</p><pre>python3 gui/serve.py --dir path/to/project\npython3 gui/demo.py /tmp/kopi-senja-demo   # " + esc(t("a demo project")) + "</pre></div>";
  }

  function header() {
    const st = S.st, v = st.verdict.verdict;
    const running = st.steps.filter(s => s.status === "running").map(s => s.key);
    let h = '<div class="head"><div><h1>' + esc(st.name) + '</h1><div class="path">' + esc(st.root) + "</div></div>" +
      '<div class="actions"><span class="verdict ' + esc(v.replace(" ", "-")) + '">' + esc(t(v)) + "</span>";
    if (SNAP) h += '<span class="snapshot-note">' + esc(t("Exported {d}, read-only", { d: new Date(SNAP.exported * 1000).toLocaleString(LOC()) })) + "</span>";
    else h += '<a class="btn" href="/api/p/' + S.pid + '/export">⤓ ' + esc(t("Export HTML")) + "</a>" +
      '<button class="btn" id="snap-btn">◷ ' + esc(t("Save round")) + "</button>" +
      '<button class="btn danger sm" id="forget">' + esc(t("Forget")) + "</button>";
    h += "</div></div>";
    if (S.query.round) h += '<div class="banner info" style="margin-top:14px"><span>' + esc(t("Viewing round {r} (read-only copy).", { r: S.query.round })) +
      '</span><a class="btn sm" href="#/p/' + S.pid + "/" + S.tab + '">' + esc(t("Back to current")) + "</a></div>";
    const tabStep = tab => (TAB_STEPS[tab] || []).some(k => running.includes(k));
    h += '<nav class="tabs">' + TABS.filter(x => !(SNAP && x === "rounds")).map(x =>
      '<a href="#/p/' + S.pid + "/" + x + (S.query.round ? "?round=" + encodeURIComponent(S.query.round) : "") + '" class="' + (x === S.tab ? "on" : "") + '">' + esc(t("tab." + x)) +
      (tabStep(x) ? '<span class="dot"></span>' : "") + "</a>").join("") + "</nav>";
    return h;
  }

  function bindHeader() {
    const sb = $("#snap-btn");
    if (sb) sb.onclick = async () => {
      const label = (S.ui.roundLabel || "").trim() || t("Round") + " " + new Date().toLocaleString(LOC());
      try { await api("/api/p/" + S.pid + "/rounds", { method: "POST", body: { label } }); toast(t("Round saved")); if (S.tab === "rounds") renderView(); }
      catch (e) { toast(e.message); }
    };
    const fg = $("#forget");
    if (fg) fg.onclick = async () => {
      if (!fg.dataset.armed) { fg.dataset.armed = "1"; fg.textContent = t("Click again to forget (files stay)"); return; }
      await api("/api/projects/" + S.pid, { method: "DELETE" });
      location.hash = "#/"; loadProjects();
    };
  }

  async function renderView() {
    const el = $("#view");
    if (!el) return;
    try { await (VIEWS[S.tab] || VIEWS.pipeline)(el); }
    catch (e) { el.innerHTML = empty(esc(e.message)); console.error(e); }
  }

  // ── pipeline ─────────────────────────────────────────────────────────────────
  const VIEWS = {};
  VIEWS.pipeline = async el => {
    const st = S.st;
    const checks = st.verdict.checks.map(c => '<li><span class="ic ' + (c.ok ? "ok" : "ko") + '">' + (c.ok ? "✓" : "✗") + "</span><span>" + esc(c.text) + "</span></li>").join("");
    const next = st.next;
    let h = '<div class="grid g-side">';
    h += '<div class="card"><div class="card-head"><h2>' + esc(t("Verdict")) + '</h2><span class="verdict ' + esc(st.verdict.verdict.replace(" ", "-")) + '">' + esc(t(st.verdict.verdict)) + "</span></div>" +
      (checks ? '<ul class="checks">' + checks + "</ul>" : '<p class="muted">' + esc(t("No numbers yet. The verdict is computed once the CFO has run.")) + "</p>") +
      (next ? '<div class="banner info" style="margin:14px 0 0"><span>' + esc(t("Next step:")) + " <b>" + esc(stepName(next)) + "</b> <code class=\"copy\" data-copy=\"" + esc(cmd(next)) + '">' + esc(cmd(next)) + "</code></span></div>" : "") + "</div>";
    h += '<div class="card"><h2>' + esc(t("Board conditions")) + "</h2>" + checklist(st.checklist) + "</div></div>";
    if (st.profile) h += '<div class="card" style="margin-top:14px"><div class="card-head"><h2>' + esc(t("Business profile")) + '</h2><a class="btn sm" href="#/p/' + S.pid + '/docs/profile.md">profile.md</a></div>' +
      '<p class="muted" style="font-size:12px;margin-top:-4px">' + esc(t("Written by founder-plan from the numbers. The run skills read their targets and alert thresholds here.")) + '</p><div class="grid g3">' +
      st.profile.map(sec => '<div><h3>' + esc(sec.section) + '</h3><table class="t">' + sec.rows.map(([k, v]) => "<tr><td>" + esc(k) + '</td><td class="r' + (v.trim() === "?" || /\?/.test(v) ? " muted" : "") + '">' +
        esc(v) + "</td></tr>").join("") + "</table></div>").join("") + "</div></div>";
    if (st.run_summary) h += '<div class="banner info" style="margin-top:14px"><span>' + esc(t("After opening: {s}", { s: st.run_summary })) +
      '</span><a class="btn sm" href="#/p/' + S.pid + '/run">' + esc(t("Open")) + "</a></div>";
    h += '<h2 style="margin:22px 0 10px">' + esc(t("The eleven steps")) + '</h2><div class="pipe">';
    for (const s of st.steps) {
      const open = STEP_TAB[s.key] ? "#/p/" + S.pid + "/" + STEP_TAB[s.key] : "#/p/" + S.pid + "/docs/" + encodeURIComponent(s.primary);
      h += '<div class="step ' + s.status + (s.key === next ? " next" : "") + '"><h3>' + esc(stepName(s.key)) + '</h3><div class="role">' + esc(t("role." + s.key)) + "</div>" +
        '<div class="row">' + chip(s.status, t("status." + s.status)) + (s.updated ? "<small>" + esc(ago(s.updated)) + "</small>" : "") +
        "</div>" +
        (s.stale_by.length ? '<div class="row"><small>' + esc(t("changed since: {f}", { f: s.stale_by.join(", ") })) + "</small></div>" : "") +
        '<div class="acts">' + (s.files.length ? '<a class="btn sm" href="' + open + '">' + esc(t("Open")) + "</a>" : "") +
        '<button class="btn sm copy" data-copy="' + esc(cmd(s.key)) + '" title="' + esc(t("Copy the command")) + '">⧉</button></div></div>';
    }
    h += "</div>";
    el.innerHTML = h;
    bindChecklist(el);
  };

  function checklist(items) {
    if (!items || !items.length) return '<p class="muted">' + esc(t("The board's conditions show up here once board.md has a checklist.")) + "</p>";
    const done = items.filter(i => i.done).length;
    return '<div class="progress" style="margin-bottom:10px"><i style="width:' + (100 * done / items.length) + '%;background:var(--accent)"></i></div><div class="checklist">' +
      items.map(i => '<label><input type="checkbox" data-tick="' + i.id + '"' + (i.done ? " checked" : "") + (SNAP || S.query.round ? " disabled" : "") + '><span class="' + (i.done ? "done" : "") + '">' + MD.inline(i.text) + "</span></label>").join("") + "</div>";
  }
  function bindChecklist(el) {
    $$("[data-tick]", el).forEach(cb => cb.onchange = async () => {
      try { S.st.checklist = await api("/api/p/" + S.pid + "/checklist", { method: "POST", body: { id: cb.dataset.tick, done: cb.checked } }); renderView(); }
      catch (e) { toast(e.message); }
    });
  }

  // ── markdown ─────────────────────────────────────────────────────────────────
  function doc(text) {
    if (!text) return "";
    return '<div class="md">' + MD.render(text, { commentable: false }) + "</div>";
  }
  document.addEventListener("click", async ev => {
    const cp = ev.target.closest("[data-copy]");
    if (!cp) return;
    try { await navigator.clipboard.writeText(cp.dataset.copy); toast(t("Copied: {c}", { c: cp.dataset.copy })); } catch (e) { toast(cp.dataset.copy); }
  });

  // ── board ────────────────────────────────────────────────────────────────────
  VIEWS.board = async el => {
    const b = await api(P("board"));
    if (!b.memos.length && !b.summary && !b.idea) { el.innerHTML = empty(esc(t("No board yet. Run {c}.", { c: cmd("board") }))); return; }
    const scores = b.memos.map(m => m.score).filter(x => x != null);
    const avg = scores.length ? (scores.reduce((a, x) => a + x, 0) / scores.length).toFixed(1) : "n/a";
    let h = '<div class="grid g4" style="margin-bottom:14px">' +
      kpi(avg, t("average score")) + b.memos.map(m => kpi(m.vote || "?", t("lens.title", { l: m.lens.replace(/[-_]/g, " ") }))).join("") + "</div>";
    h += '<div class="grid ' + (b.memos.length === 4 ? "g2" : "g3") + '">' + b.memos.map(m => {
      const secs = Object.entries(m.sections).map(([k, v]) => '<div class="sec"><h4>' + esc(k) + "</h4>" + doc(v, m.file, "board") + "</div>").join("");
      return '<div class="card memo"><div class="top"><div><h2>' + esc(t("lens.title", { l: m.lens.replace(/[-_]/g, " ") })) + "</h2>" + (m.vote ? chip(m.vote.replace(" ", "-"), m.vote) : "") + "</div>" +
        (m.score != null ? '<div class="score" style="--s:' + m.score + '"><span>' + m.score + "</span></div>" : "") + "</div>" + secs + "</div>";
    }).join("") + "</div>";
    h += '<div class="grid g-side" style="margin-top:14px"><div class="card"><h2>' + esc(t("The chair's summary")) + "</h2>" + (doc(b.summary, "board.md", "board") || '<p class="muted">board.md</p>') + "</div>" +
      '<div class="card"><h2>' + esc(t("Board conditions")) + "</h2>" + checklist(b.checklist) + "<h2 style=\"margin-top:18px\">" + esc(t("The idea")) + "</h2>" + doc(b.idea, "idea.md", "board") + "</div></div>";
    el.innerHTML = h;
    bindChecklist(el);
  };
  const kpi = (v, l, d) => '<div class="card kpi"><div class="v">' + esc(v) + '</div><div class="l">' + esc(l) + "</div>" + (d ? '<div class="d">' + d + "</div>" : "") + "</div>";

  // ── competitors ──────────────────────────────────────────────────────────────
  VIEWS.competitors = async el => {
    const c = await api(P("competitors"));
    let ours = null;
    try { ours = (await api(P("cfo"))).spec; } catch (e) { /* no numbers yet */ }
    if (!c.rows.length && !c.report) { el.innerHTML = empty(esc(t("No competitor map yet. Run {c}.", { c: cmd("competitors") }))); return; }
    const types = {};
    c.rows.forEach(r => { types[r.type] = (types[r.type] || 0) + 1; });
    let h = '<div class="grid g4" style="margin-bottom:14px">' + kpi(c.rows.length, t("competitors")) +
      Object.entries(types).slice(0, 3).map(([k, n]) => kpi(n, k)).join("") + "</div>";
    h += '<div class="grid g-side"><div class="card"><h2>' + esc(t("Price vs rating")) + '</h2><div id="sc"></div></div><div class="card"><h2>' + esc(t("The gap")) + "</h2>" + doc(c.report, "competitors.md", "competitors") + "</div></div>";
    h += '<div class="card" style="margin-top:14px"><h2>' + esc(t("Every competitor")) + '</h2><div class="table-wrap"><table class="t"><thead><tr><th>' +
      [t("name"), t("type"), t("where"), t("price"), t("price seen on"), t("rating"), t("reviews"), t("trust signals"), t("positioning")].map(esc).join("</th><th>") + "</th></tr></thead><tbody>" +
      c.rows.map(r => "<tr><td>" + (r.url ? '<a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(r.name) + "</a>" : esc(r.name)) + "</td><td>" + chip("", r.type || "") + "</td><td>" + esc(r.location_or_channel || "") +
        '</td><td class="r">' + esc(r.price_of_comparable_item || "") + "</td><td>" + esc(r.price_channel || "") + '</td><td class="r">' + esc(r.rating || "") + '</td><td class="r">' + esc(r.review_count || "") +
        "</td><td>" + esc(r.trust_signals || "") + "</td><td>" + esc(r.positioning_line || "") + "</td></tr>").join("") +
      "</tbody></table></div></div>";
    el.innerHTML = h;
    Charts.scatter($("#sc"), { points: c.rows.map((r, i) => ({ x: r.price, y: r.rating_num, label: r.name, cls: { direct: "f3", indirect: "f2", substitute: "f4", informal: "f5" }[r.type] || "f" + ((i % 5) + 1) })),
      xfmt: money2, yfmt: v => (+v).toFixed(1), xlabel: t("price of the comparable item"), ylabel: t("rating"),
      vline: ours && ours.price ? { x: ours.price, label: t("you {p}", { p: money2(ours.price) }) } : null });
  };

  // ── consumer panel ───────────────────────────────────────────────────────────
  VIEWS.panel = async el => {
    const p = await api(P("panel"));
    if (!p.exists) { el.innerHTML = empty(esc(t("No panel yet. Run {c}.", { c: cmd("consumer") }))); return; }
    const ui = S.ui.panel = S.ui.panel || { seg: "", beh: "", buy: "" };
    const seen = S.ui.panelSeen || {};
    const res = p.live || p.results;
    const buyers = p.buyers;
    const segs = [...new Set(buyers.map(b => b.segment))], behs = [...new Set(buyers.map(b => b.behaviour))];
    const match = b => (!ui.seg || b.segment === ui.seg) && (!ui.beh || b.behaviour === ui.beh) &&
      (!ui.buy || (ui.buy === "yes" ? b.answer && b.answer.buys : ui.buy === "no" ? b.answer && !b.answer.buys : !b.answer));
    const live = p.answered < p.n;
    let h = '<div class="grid g4" style="margin-bottom:14px">' +
      kpi(res ? pct(res.buy_rate) : "n/a", t("would buy")) + kpi(res ? res.buys + " · " + res.passes : "n/a", t("buy · pass")) +
      kpi(p.answered + "/" + p.n, t("answered"), live ? '<div class="progress" style="margin-top:6px"><i style="width:' + (100 * p.answered / p.n) + '%"></i></div>' : "") +
      kpi(res && res.purchases_first_month_per_buyer != null ? res.purchases_first_month_per_buyer.toFixed(1) : "n/a", t("purchases in month 1, per buyer")) + "</div>";
    h += '<div class="grid g-side"><div class="card"><div class="card-head"><h2>' + esc(t("The buyers")) + "</h2>" + (live ? chip("running", t("answers arriving")) : "") + "</div>" +
      '<div class="filters">' + sel("seg", t("every segment"), segs, ui.seg) + sel("beh", t("every behaviour"), behs, ui.beh) +
      sel("buy", t("everyone"), [["yes", t("buys")], ["no", t("passes")], ["wait", t("no answer yet")]], ui.buy) +
      '<span class="legend"><span><i style="background:var(--good)"></i>' + esc(t("buys")) + '</span><span><i style="background:color-mix(in srgb,var(--bad) 60%,var(--panel))"></i>' + esc(t("passes")) +
      '</span><span><i style="background:var(--muted-soft)"></i>' + esc(t("waiting")) + "</span></span></div>" +
      '<div class="tiles">' + buyers.map(b => {
        const cls = b.answer ? (b.answer.buys ? "yes" : "no") : "";
        const fresh = b.answer && seen[b.id] === false ? " fresh" : "";
        return '<button class="tile ' + cls + (match(b) ? "" : " dim") + fresh + '" data-buyer="' + b.id + '" title="' + esc(b.name + ", " + b.age + " · " + b.segment + " · " + b.behaviour) + '">' + b.id.slice(1) + "</button>";
      }).join("") + "</div></div>";
    h += '<div class="card"><h2>' + esc(t("The pitch they saw")) + '</h2><div class="md"><p>' + MD.inline(p.pitch || "").replace(/\n/g, "<br>") + "</p></div>" +
      (p.pitch_now && p.pitch && p.pitch_now.trim() !== p.pitch.trim() ? '<div class="banner warn">' + esc(t("pitch.md changed after this panel was dealt. Re-run the panel to test the new pitch.")) + "</div>" : "") +
      '<p class="muted" style="font-size:12px">' + esc(t("Seed {s}: the same cards can be dealt again.", { s: p.seed })) + "</p></div></div>";
    if (res) {
      const barsFor = (rows) => '<div class="bars">' + rows.map(([k, n, r]) => '<div class="bar"><span class="lbl" title="' + esc(k) + '">' + esc(k) + ' <small>(' + n + ')</small></span><span class="track"><i style="width:' + (r * 100) + '%"></i></span><span class="n">' + pct(r) + "</span></div>").join("") + "</div>";
      const region = res.by_region && res.by_region.length > 1;
      h += '<div class="grid ' + (region ? "g4" : "g3") + '" style="margin-top:14px"><div class="card"><h3>' + esc(t("By segment")) + "</h3>" + barsFor(res.by_segment) + '</div><div class="card"><h3>' + esc(t("By behaviour")) + "</h3>" + barsFor(res.by_behaviour) +
        '</div><div class="card"><h3>' + esc(t("By income")) + "</h3>" + barsFor(res.by_income) + "</div>" +
        (region ? '<div class="card"><h3>' + esc(t("By region")) + "</h3>" + barsFor(res.by_region) + "</div>" : "") + "</div>";
      const reasons = (rows, total) => '<div class="reasons">' + rows.map(([code, n, quotes]) => '<div class="reason"><div class="bar"><span class="lbl"><b>' + esc(code) + '</b></span><span class="track"><i style="width:' + (100 * n / Math.max(1, total)) + '%;background:var(--c3)"></i></span><span class="n">' + n + "</span></div>" +
        quotes.map(q => '<div class="q">"' + esc(q) + '"</div>').join("") + "</div>").join("") + "</div>";
      const flips = {};
      (res.flip || []).forEach(f => { const k = f.trim().replace(/\.$/, ""); flips[k] = (flips[k] || 0) + 1; });
      h += '<div class="grid g3" style="margin-top:14px"><div class="card"><h3>' + esc(t("Why they pass")) + "</h3>" + reasons(res.why_not, res.passes) + '</div><div class="card"><h3>' + esc(t("Why they buy")) + "</h3>" + reasons(res.why_yes, res.buys) +
        '</div><div class="card"><h3>' + esc(t("What would flip a no")) + '</h3><div class="bars">' + Object.entries(flips).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([k, n]) =>
          '<div class="bar"><span class="lbl" title="' + esc(k) + '">' + esc(k) + '</span><span class="track"><i style="width:' + (100 * n / Math.max(1, res.passes)) + '%;background:var(--c2)"></i></span><span class="n">' + n + "</span></div>").join("") + "</div>" +
"</div></div>";
    }
    if (p.report) h += '<details class="card" style="margin-top:14px"><summary class="link" style="font-size:14px">panel/results.md</summary>' + doc(p.report, "panel/results.md", "consumer") + "</details>";
    el.innerHTML = h;
    S.ui.panelSeen = Object.fromEntries(buyers.map(b => [b.id, !!b.answer]));
    $$("select[data-f]", el).forEach(s => s.onchange = () => { ui[s.dataset.f] = s.value; VIEWS.panel(el); });
    $$("[data-buyer]", el).forEach(b => b.onclick = () => buyer(buyers.find(x => x.id === b.dataset.buyer)));
  };
  function sel(key, all, opts, cur) {
    return '<select data-f="' + key + '"><option value="">' + esc(all) + "</option>" + opts.map(o => {
      const [v, l] = Array.isArray(o) ? o : [o, o];
      return '<option value="' + esc(v) + '"' + (v === cur ? " selected" : "") + ">" + esc(l) + "</option>";
    }).join("") + "</select>";
  }
  async function buyer(b) {
    const a = b.answer;
    let h = '<div class="card-head"><h2>' + esc(b.name) + ", " + b.age + ' <small class="num">' + b.id + '</small></h2><button class="btn sm" data-close>✕</button></div><div class="persona"><dl>' +
      [["segment", b.segment], ["income", money(b.income)], ["behaviour", b.behaviour + (b.behaviour_how ? ": " + b.behaviour_how : "")], ["habit", b.habit], ["first objection", b.objection]]
        .filter(x => x[1]).map(([k, v]) => "<dt>" + esc(t(k)) + "</dt><dd>" + esc(v) + "</dd>").join("") + "</dl></div>";
    if (a) {
      h += '<div class="card" style="margin-top:14px"><div class="card-head"><h3>' + esc(t("The answer")) + "</h3>" + chip(a.buys ? "good" : "bad", a.buys ? t("buys") : t("passes")) + "</div>" +
        '<p style="font-size:15px;font-family:var(--serif)">"' + esc(a.reason) + '"</p><div class="persona"><dl>' +
        [["reason", a.reason_code], ["objection", a.objection], ["would change my mind", a.would_change_my_mind], ["purchases in month 1", a.purchases_first_month]]
          .filter(x => x[1] !== "" && x[1] != null).map(([k, v]) => "<dt>" + esc(t(k)) + "</dt><dd>" + esc(v) + "</dd>").join("") + "</dl></div>" +
        '<h3 style="margin-top:14px">' + esc(t("Price answers")) + '</h3><table class="t"><tr><th>' + esc(t("too cheap")) + '</th><th>' + esc(t("a bargain")) + "</th><th>" + esc(t("getting expensive")) + "</th><th>" + esc(t("too expensive")) + '</th></tr><tr><td class="r">' +
        [a.price_too_cheap, a.price_cheap, a.price_expensive, a.price_too_expensive].map(money2).join('</td><td class="r">') + "</td></tr></table></div>";
    } else h += '<div class="empty" style="margin-top:14px">' + esc(t("No answer yet.")) + "</div>";
    h += '<details style="margin-top:14px"><summary class="link">' + esc(t("The brief this buyer agent received")) + '</summary><pre id="brief" class="md" style="white-space:pre-wrap;font-size:12px">…</pre></details>';
    openDrawer(h);
    try { $("#brief").textContent = (await api(P("panel/brief/" + b.id))).text; } catch (e) { $("#brief").textContent = t("Not available"); }
  }
  function openDrawer(html) {
    const d = $("#drawer");
    $(".drawer-body", d).innerHTML = html; d.hidden = false;
    d.onclick = e => { if (e.target === d || e.target.closest("[data-close]")) d.hidden = true; };
  }
  document.addEventListener("keydown", e => { if (e.key === "Escape") $("#drawer").hidden = true; });

  // ── pricing ──────────────────────────────────────────────────────────────────
  VIEWS.pricing = async el => {
    const p = await api(P("pricing"));
    if (!p.analysis && !p.report) { el.innerHTML = empty(esc(t("No price answers yet: the consumer panel collects them. Then run {c}.", { c: cmd("pricing") }))); return; }
    let h = "";
    if (p.analysis) {
      const pts = p.analysis.points;
      h += '<div class="grid g4" style="margin-bottom:14px">' + kpi(t("{a} to {b}", { a: money2(pts.PMC), b: money2(pts.PME) }), t("acceptable range")) + kpi(money2(pts.OPP), t("optimal price (OPP)")) +
        kpi(money2(pts.IPP), t("indifference price (IPP)")) + kpi(p.price != null ? money2(p.price) : "n/a", t("your price now"),
          p.price != null && pts.PMC != null ? (p.price >= pts.PMC && p.price <= pts.PME ? '<span class="up">' + esc(t("inside the range")) + "</span>" : '<span class="down">' + esc(t("outside the range")) + "</span>") : "") + "</div>";
      h += '<div class="card"><div class="card-head"><h2>' + esc(t("Price sensitivity (Van Westendorp)")) + '</h2><small>' + esc(t("{n} complete answers, {d} dropped", { n: p.n, d: p.dropped })) + '</small></div><div id="vw"></div>' +
        '<p class="muted" style="font-size:12px">' + esc(t("Shaded: the acceptable range. Dots: competitor prices. Simulated buyers: use the range to pick what to test.")) + "</p></div>";
    }
    h += '<div class="grid g2" style="margin-top:14px"><div class="card"><h2>pricing.md</h2>' + (doc(p.report, "pricing.md", "pricing") || '<p class="muted">' + esc(t("Not written yet.")) + "</p>") + '</div><div class="card"><h2>pricing-curve.md</h2>' + (doc(p.curve_report, "pricing-curve.md", "pricing") || "") + "</div></div>";
    el.innerHTML = h;
    if (p.analysis) {
      const c = p.curves, pts = p.analysis.points;
      const markers = [{ x: pts.PMC, label: "PMC" }, { x: pts.OPP, label: "OPP" }, { x: pts.IPP, label: "IPP" }, { x: pts.PME, label: "PME" }];
      if (p.price != null) markers.push({ x: p.price, label: t("you"), cls: "price" });
      if (p.variable_per_unit != null) markers.push({ x: p.variable_per_unit, label: t("unit cost") });
      Charts.line($("#vw"), { x: c.grid, label: "Van Westendorp", height: 320, band: p.analysis.range, markers, ymin: 0, ymax: 1,
        dots: p.competitors.map(x => ({ x: x.price, label: x.name + " " + money2(x.price) })),
        series: [{ name: t("too cheap"), values: c.too_cheap }, { name: t("a bargain"), values: c.cheap }, { name: t("too expensive"), values: c.too_expensive }, { name: t("getting expensive"), values: c.expensive }],
        xfmt: money2, yfmt: v => pct(v) });
    }
  };

  // ── offer ────────────────────────────────────────────────────────────────────
  VIEWS.offer = async el => {
    const o = await api(P("offer"));
    let panel = null;
    try { panel = await api(P("panel")); } catch (e) { /* none */ }
    if (!o.report && !o.pitch_v1) { el.innerHTML = empty(esc(t("No offer yet. Run {c} after the panel.", { c: cmd("offer") }))); return; }
    let h = "";
    if (o.pitch_v1 || o.pitch_now) {
      h += '<div class="card"><div class="card-head"><h2>' + esc(t("The pitch, before and after")) + "</h2>" +
        (panel && (panel.live || panel.results) ? chip("", t("panel now: {r} buy", { r: pct((panel.live || panel.results).buy_rate) })) : "") + "</div>" +
        '<div class="side-by-side"><div><h3>pitch-v1.md</h3><pre>' + wordDiff(o.pitch_v1 || "", o.pitch_now || "", "del") + "</pre></div><div><h3>pitch.md</h3><pre>" + wordDiff(o.pitch_v1 || "", o.pitch_now || "", "ins") + "</pre></div></div>" +
        '<p class="muted" style="font-size:12px">' + esc(t("To compare buy rates before and after, save a round before the offer re-test, then compare rounds.")) + "</p></div>";
    }
    h += '<div class="card" style="margin-top:14px"><h2>offer.md</h2>' + doc(o.report, "offer.md", "offer") + "</div>";
    el.innerHTML = h;
  };
  function wordDiff(a, b, side) {
    const A = a.split(/(\s+)/), B = b.split(/(\s+)/);
    const n = A.length, m = B.length;
    if (n * m > 4e6) return esc(side === "del" ? a : b);
    const L = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1));
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) L[i][j] = A[i] === B[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
    let i = 0, j = 0, out = "";
    while (i < n || j < m) {
      if (i < n && j < m && A[i] === B[j]) { out += esc(A[i]); i++; j++; }
      else if (j < m && (i >= n || L[i][j + 1] >= L[i + 1][j])) { if (side === "ins") out += /^\s+$/.test(B[j]) ? esc(B[j]) : '<mark class="ins">' + esc(B[j]) + "</mark>"; j++; }
      else { if (side === "del") out += /^\s+$/.test(A[i]) ? esc(A[i]) : '<mark class="del">' + esc(A[i]) + "</mark>"; i++; }
    }
    return out;
  }

  // ── cfo ──────────────────────────────────────────────────────────────────────
  VIEWS.cfo = async el => {
    const c = await api(P("cfo"));
    if (!c.spec) { el.innerHTML = empty(esc(t("No numbers yet. Run {c}.", { c: cmd("cfo") }))); return; }
    if (c.error) { el.innerHTML = '<div class="banner warn">' + esc(t("numbers.json has a problem: {e}", { e: c.error })) + "</div>"; return; }
    const a = c.analysis, u = a.unit;
    const ui = S.ui.cfo = S.ui.cfo || { price: a.price, volume: 100, variable: 100, fees: 100, fixed: 100, startup: 100 };
    const idr = CUR() === "IDR", pstep = idr ? 500 : 0.05;
    const pround = v => idr ? Math.round(v / 500) * 500 : +v.toFixed(2);
    let h = '<div class="grid g4" style="margin-bottom:14px">' +
      kpi(money2(a.contribution), t("each {u} earns, before fixed costs", { u }), pct(a.contribution_pct) + " " + esc(t("contribution"))) +
      kpi(intf(a.breakeven_per_day), t("{u}s a day to break even", { u }), a.capacity_per_day ? esc(t("capacity {c}", { c: a.capacity_per_day })) : "") +
      kpi(pct(a.margin_at_plan), t("profit margin at plan ({n}/day)", { n: a.plan_per_day })) +
      kpi(money(a.year1_profit), t("year 1 operating profit"), esc(t("after startup: {v}", { v: money(a.year1_after_startup) }))) + "</div>";
    h += '<div class="grid g4" style="margin-bottom:14px">' + kpi(money(a.startup), t("startup spend")) + kpi(money(a.cash_needed), t("cash needed before it pays for itself")) +
      kpi(a.payback_month ? t("month {m}", { m: a.payback_month }) : t("not in year 1"), t("startup money earned back")) + kpi(money(a.fixed_monthly), t("fixed costs a month")) + "</div>";
    h += '<div class="grid g-side"><div class="card"><div class="card-head"><h2>' + esc(t("Year 1, month by month")) + '</h2><small id="wi-note"></small></div><div id="y1"></div></div>';
    h += '<div class="card"><div class="card-head"><h2>' + esc(t("What if")) + "</h2>" + (SNAP ? "" : '<button class="btn sm" id="wi-reset">' + esc(t("Reset")) + "</button>") + "</div>" +
      (SNAP ? '<p class="muted">' + esc(t("The what-if needs the live GUI.")) + "</p>" : '<div class="sliders">' +
        slider("price", t("price per {u}", { u }), pround(a.price * 0.5), pround(a.price * 1.6), pstep, ui.price, money2) +
        slider("volume", t("sales volume"), 40, 160, 5, ui.volume, v => v + "%") +
        slider("variable", t("unit costs"), 50, 200, 5, ui.variable, v => v + "%") +
        slider("fees", t("commissions, fees and turnover tax"), 0, 200, 5, ui.fees, v => v + "%") +
        slider("fixed", t("fixed costs"), 50, 200, 5, ui.fixed, v => v + "%") +
        slider("startup", t("startup spend"), 50, 200, 5, ui.startup, v => v + "%") + '</div><div id="wi-out" style="margin-top:14px"></div>') +
      '<p class="muted" style="font-size:12px">' + esc(t("Runs the CFO's own unit_economics.py on a copy. numbers.json is never changed.")) + "</p></div></div>";
    h += '<div class="card" style="margin-top:14px"><h2>' + esc(t("The three what-ifs every plan should survive")) + '</h2><div class="table-wrap"><table class="t"><thead><tr><th></th><th class="r">' +
      [t("price"), t("contribution"), t("margin at plan"), t("break-even/day"), t("year 1 profit"), t("cash needed"), t("payback")].map(esc).join('</th><th class="r">') + "</th></tr></thead><tbody>" +
      c.sensitivity.map(s => { const r = s.result; return "<tr><td>" + esc(s.label) + '</td><td class="r">' + [money2(r.price), money2(r.contribution), pct(r.margin_at_plan), intf(r.breakeven_per_day),
        '<span class="' + (r.year1_profit >= 0 ? "up" : "down") + '">' + money(r.year1_profit) + "</span>", money(r.cash_needed), r.payback_month ? t("month {m}", { m: r.payback_month }) : "n/a"].join('</td><td class="r">') + "</td></tr>"; }).join("") +
      "</tbody></table></div></div>";
    const season = (c.spec.season || []);
    h += '<div class="card" style="margin-top:14px"><h2>' + esc(t("Year 1, month by month")) + '</h2><p class="muted" style="font-size:12px;margin-top:-4px">' +
      esc(t("Profit counts every cost in its month (rent every month); cash is when money actually leaves (rent paid up front is in the startup spend).")) + '</p><div class="table-wrap"><table class="t"><thead><tr><th>' +
      [t("month"), t("{u}s a day", { u }), t("season"), t("revenue"), t("one-off"), t("profit"), t("cash"), t("cumulative cash")].map(esc).join('</th><th class="r">') + "</th></tr></thead><tbody>" +
      a.months.map((m, i) => "<tr><td>" + esc(m.label || String(m.month)) + '</td><td class="r">' + intf(m.per_day) + '</td><td class="r">' + (season[i] != null && season[i] !== 1 ? "×" + season[i] : "") +
        '</td><td class="r">' + money(m.revenue) + '</td><td class="r">' + (m.one_off ? money(m.one_off) : "") + '</td><td class="r"><span class="' + (m.profit >= 0 ? "up" : "down") + '">' + money(m.profit) +
        '</span></td><td class="r">' + money(m.cash) + '</td><td class="r"><span class="' + (m.cumulative >= 0 ? "up" : "down") + '">' + money(m.cumulative) + "</span></td></tr>").join("") +
      "</tbody></table></div></div>";
    const oneOff = (a.one_off || []).map(o => ({ label: o[1] + " (" + t("month {m}", { m: o[0] }) + ")", cost: o[2] }));
    h += '<div class="grid g2" style="margin-top:14px">' + items(t("Cost of one {u}", { u }), a.variable_items) + items(t("Fixed, every month"), a.fixed_items) +
      items(t("Startup, once"), a.startup_items) + (oneOff.length ? items(t("One-off, in year 1"), oneOff) : "") + "</div>";
    h += '<div class="card" style="margin-top:14px"><h2>cfo.md</h2>' + doc(c.report, "cfo.md", "cfo") + '</div><div class="card" style="margin-top:14px"><h2>cfo-sources.md</h2>' + (doc(c.sources, "cfo-sources.md", "cfo") || '<p class="muted">' + esc(t("Not written yet.")) + "</p>") + "</div>";
    el.innerHTML = h;
    const drawYear = (b, w) => Charts.bars($("#y1"), { labels: b.months.map(m => m.label && isNaN(+m.label) ? m.label.slice(0, 3) : "M" + m.month), values: (w || b).months.map(m => m.profit), name: w ? t("profit (what-if)") : t("profit"),
      line: { name: t("cumulative, after startup"), values: (w || b).months.map(m => m.cumulative) }, ghost: w ? b.months.map(m => m.profit) : null, ghostName: t("profit (plan)"), yfmt: money, height: 280 });
    drawYear(a);
    if (SNAP) return;
    let timer;
    const recalc = async () => {
      const body = { price: ui.price, volume: ui.volume / 100, variable_scale: ui.variable / 100, pct_scale: ui.fees / 100, fixed_scale: ui.fixed / 100, startup_scale: ui.startup / 100 };
      const same = Math.abs(ui.price - a.price) < 1e-9 && ui.volume === 100 && ui.variable === 100 && ui.fees === 100 && ui.fixed === 100 && ui.startup === 100;
      if (same) { drawYear(a); $("#wi-out").innerHTML = ""; $("#wi-note").textContent = ""; return; }
      try {
        const w = await api("/api/p/" + S.pid + "/cfo/whatif", { method: "POST", body });
        drawYear(a, w);
        $("#wi-note").textContent = t("showing the what-if; grey bars are the plan");
        const d = (x, y, f, good) => { const diff = x - y; return f(x) + ' <small class="' + ((good ? diff >= 0 : diff <= 0) ? "up" : "down") + '">' + (diff >= 0 ? "+" : "") + f(diff) + "</small>"; };
        $("#wi-out").innerHTML = '<table class="t"><tr><td>' + esc(t("contribution")) + '</td><td class="r">' + d(w.contribution, a.contribution, money2, true) + "</td></tr><tr><td>" + esc(t("break-even/day")) + '</td><td class="r">' +
          (w.breakeven_per_day == null ? t("never") : d(Math.ceil(w.breakeven_per_day), Math.ceil(a.breakeven_per_day), v => Math.round(v).toLocaleString(LOC()), false)) + "</td></tr><tr><td>" + esc(t("year 1 profit")) + '</td><td class="r">' + d(w.year1_profit, a.year1_profit, money, true) +
          "</td></tr><tr><td>" + esc(t("cash needed")) + '</td><td class="r">' + d(w.cash_needed, a.cash_needed, money, false) + "</td></tr><tr><td>" + esc(t("payback")) + '</td><td class="r">' + (w.payback_month ? t("month {m}", { m: w.payback_month }) : t("not in year 1")) + "</td></tr></table>";
      } catch (e) { $("#wi-out").innerHTML = '<div class="banner warn">' + esc(e.message) + "</div>"; }
    };
    $$("input[data-s]", el).forEach(inp => inp.oninput = () => {
      ui[inp.dataset.s] = +inp.value;
      inp.closest(".slider").querySelector("b").textContent = inp.dataset.s === "price" ? money2(+inp.value) : inp.value + "%";
      clearTimeout(timer); timer = setTimeout(recalc, 120);
    });
    $("#wi-reset").onclick = () => { S.ui.cfo = null; VIEWS.cfo(el); };
    recalc();
  };
  function slider(key, label, min, max, step, val, f) {
    return '<div class="slider"><label><span>' + esc(label) + "</span><b class=\"num\">" + esc(f(val)) + '</b></label><input type="range" data-s="' + key + '" min="' + min + '" max="' + max + '" step="' + step + '" value="' + val + '"></div>';
  }
  function items(title, list) {
    const total = (list || []).reduce((s, x) => s + (+x.cost || 0), 0);
    return '<div class="card"><h3>' + esc(title) + '</h3><table class="t">' + (list || []).map(x => "<tr><td>" + esc(x.label) + '</td><td class="r">' + money(+x.cost, total < 100 ? 2 : 0) + (x.prepaid_months ? ' <small class="muted">' + esc(t("prepaid {m} months", { m: x.prepaid_months })) + "</small>" : "") + "</td></tr>").join("") +
      '<tr><td><b>' + esc(t("total")) + '</b></td><td class="r"><b>' + money(total, total < 100 ? 2 : 0) + "</b></td></tr></table></div>";
  }

  // ── after opening: the run skills' saved reports ───────────────────────────
  const RUN_KINDS = { weekly: "Weekly report", pnl: "Profit and loss", cashflow: "Cash forecast", "cost-leak": "Cost leak",
    "product-mix": "Product mix", staffing: "Staffing" };
  const RUN_CMD = { weekly: "founder-weekly-report", pnl: "founder-pnl", cashflow: "founder-cashflow", "cost-leak": "founder-cost-leak",
    "product-mix": "founder-product-mix", staffing: "founder-staffing" };
  const runCmd = k => "/founder-id:" + RUN_CMD[k];
  const docLink = r => r && r._md ? '<a class="btn sm" href="#/p/' + S.pid + "/docs/" + encodeURIComponent(r._md) + '">' + esc(t("full report")) + "</a>" : "";
  const probs = r => r && r._problems && r._problems.length ? '<div class="banner warn"><span>' + esc(t("{f} does not add up:", { f: r._file })) + " " +
    r._problems.map(esc).join("; ") + "</span></div>" : "";
  const STATUS_CHIP = { safe: "good", watch: "warn", "at risk": "bad" };
  const QUAD = { star: ["Stars", "keep"], plowhorse: ["Plowhorses", "raise the price or cut the cost"], puzzle: ["Puzzles", "promote"],
    dog: ["Dogs", "drop or redo"], new: ["New", "wait for data"] };

  VIEWS.run = async el => {
    const r = await api(P("run"));
    const R = r.reports, T = r.targets;
    if (!r.any) {
      el.innerHTML = '<div class="empty-state" style="text-align:left;max-width:720px"><h1>' + esc(t("After opening")) + "</h1><p>" +
        esc(t("Once the business is open, the run skills save every report in founder/reports/ and this page turns them into trends: weekly sales against break-even, direct cost, the cash forecast, the P&L month by month.")) +
        "</p><pre>" + Object.keys(RUN_CMD).map(k => runCmd(k)).join("\n") + "</pre></div>";
      return;
    }
    let h = '<div class="grid g3" style="margin-bottom:14px">' + r.kinds.map(k => '<div class="card"><div class="card-head"><h3>' + esc(t(RUN_KINDS[k.kind])) + "</h3>" +
      (k.problems ? chip("bad", t("{n} with problems", { n: k.problems })) : k.latest ? chip("done", k.latest) : chip("", t("none yet"))) + '</div><div class="meta" style="display:flex;gap:8px;align-items:center">' +
      "<small>" + esc(t("{n} saved", { n: k.count })) + '</small><code class="copy" data-copy="' + esc(runCmd(k.kind)) + '">' + esc(runCmd(k.kind)) + "</code></div></div>").join("") + "</div>";

    // weekly
    const weeks = (R.weekly || []).filter(w => !w._problems || !w._problems.length || w.net_sales != null).slice().reverse();
    if (weeks.length) {
      const w = weeks[weeks.length - 1], prev = weeks.length > 1 ? weeks[weeks.length - 2] : null;
      const prevNet = w.prev_net_sales != null ? w.prev_net_sales : prev && prev.net_sales;
      const diff = prevNet ? '<span class="' + (w.net_sales >= prevNet ? "up" : "down") + '">' + (w.net_sales >= prevNet ? "▲ " : "▼ ") + money(Math.abs(w.net_sales - prevNet)) + ", " + pct(Math.abs(w.net_sales / prevNet - 1)) + "</span>" : "";
      const thr = w.direct_cost_threshold != null ? w.direct_cost_threshold : T.direct_cost_alert;
      h += '<h2 style="margin:8px 0 10px">' + esc(t("Week {w}", { w: w.week })) + " <small class=\"muted\">" + esc((w.start || "") + " – " + (w.end || "")) + "</small></h2>";
      h += probs(w) + '<div class="grid g4" style="margin-bottom:14px">' + kpi(money(w.net_sales), t("net sales"), diff) +
        kpi(w.transactions != null ? w.transactions.toLocaleString("id-ID") : "n/a", t("transactions"), w.avg_ticket != null ? esc(t("average ticket {v}", { v: money(w.avg_ticket) })) : "") +
        kpi(w.days_below_breakeven != null ? w.days_below_breakeven + "/7" : "n/a", t("days below break-even"), T.breakeven_day ? esc(t("break-even {v} a day", { v: money(T.breakeven_day) })) : "") +
        kpi(w.direct_cost_pct != null ? pct(w.direct_cost_pct) : "n/a", t("direct cost (estimate)"), thr != null ? '<span class="' + (w.direct_cost_pct > thr ? "down" : "up") + '">' + esc(t("alert at {p}", { p: pct(thr) })) + "</span>" : "") + "</div>";
      h += '<div class="grid g2"><div class="card"><div class="card-head"><h2>' + esc(t("Net sales by week")) + "</h2>" + docLink(w) + '</div><div id="run-weeks"></div></div>' +
        '<div class="card"><h2>' + esc(t("Direct cost by week (estimate)")) + '</h2><div id="run-cost"></div></div></div>';
      h += '<div class="grid g-side" style="margin-top:14px"><div class="card"><h2>' + esc(t("Last week, day by day")) + '</h2><div id="run-days"></div></div>' +
        '<div class="card"><h2>' + esc(t("Channels")) + "</h2><div class=\"bars\">" + Object.entries(w.channels || {}).map(([k, v]) => '<div class="bar"><span class="lbl">' + esc(k) +
          '</span><span class="track"><i style="width:' + (100 * v / Math.max(1, w.net_sales)) + '%"></i></span><span class="n">' + pct(v / Math.max(1, w.net_sales)) + "</span></div>").join("") + "</div></div></div>";
      h += '<div class="card" style="margin-top:14px"><h2>' + esc(t("Alerts and actions")) + '</h2><div class="table-wrap"><table class="t"><thead><tr><th>' +
        [t("week"), t("net sales"), t("alerts"), t("the one action"), t("last week's action")].map(esc).join("</th><th>") + "</th></tr></thead><tbody>" +
        weeks.slice().reverse().map(x => "<tr><td>" + esc(x.week) + '</td><td class="r">' + money(x.net_sales) + "</td><td>" + ((x.alerts || []).map(a => chip("warn", a.text) +
          (a.skill ? ' <code class="copy" data-copy="/founder-id:' + esc(a.skill) + '">/' + esc(a.skill) + "</code>" : "")).join("<br>") || '<span class="muted">' + esc(t("none")) + "</span>") +
          "</td><td>" + esc(x.action || "") + '</td><td class="muted">' + esc(x.last_action || "") + "</td></tr>").join("") + "</tbody></table></div></div>";
    }

    // cash
    const cf = (R.cashflow || [])[0];
    if (cf && cf.weeks) {
      h += '<h2 style="margin:22px 0 10px">' + esc(t("Cash forecast from {d}", { d: cf.from })) + "</h2>" + probs(cf);
      h += '<div class="grid g-side"><div class="card"><div class="card-head"><h2>' + esc(t("End-of-week balance")) + "</h2>" + docLink(cf) + '</div><div id="run-cash"></div></div><div class="card"><h2>' +
        esc(t("Weeks")) + '</h2><table class="t">' + cf.weeks.map(x => "<tr><td>" + esc(t("Week {w}", { w: x.label })) + "<br><small class=\"muted\">" + esc((x.start || "") + " – " + (x.end || "")) + '</small></td><td class="r">' +
          '<span class="' + (x.end_balance >= 0 ? "up" : "down") + '">' + money(x.end_balance) + "</span></td><td>" + chip(STATUS_CHIP[x.status] || "", t(x.status)) + "</td></tr>").join("") + "</table>" +
        ((cf.options || []).length ? "<h3 style=\"margin-top:12px\">" + esc(t("Options")) + "</h3><ul>" + cf.options.map(o => "<li>" + esc(o) + "</li>").join("") + "</ul>" : "") + "</div></div>";
    }

    // P&L
    const pnl = (R.pnl || []).filter(m => m.net_sales != null).slice().reverse();
    if (pnl.length) {
      // one point per month: several outlets are added together for the charts, kept apart in the table
      const months = [], byMonth = {};
      pnl.forEach(m => {
        const k = m.month;
        if (!byMonth[k]) { byMonth[k] = { month: k, outlets: 0, net_sales: 0, platform_commission: 0, direct_cost: 0, labour: 0, fixed_costs: 0, pph_final: 0, other_costs: 0, net_profit: 0 }; months.push(byMonth[k]); }
        const a = byMonth[k]; a.outlets += 1;
        ["net_sales", "platform_commission", "direct_cost", "labour", "fixed_costs", "pph_final", "other_costs", "net_profit"].forEach(f => { a[f] += +m[f] || 0; });
      });
      months.sort((a, b) => a.month < b.month ? -1 : 1);
      const multi = months.some(m => m.outlets > 1);
      // "what comes in" is net sales before the apps take their cut, as in the owner's P&L
      const per100k = m => {
        const base = m.net_sales + m.platform_commission, k = base ? 100000 / base : 0;
        return { base, stock: m.direct_cost * k, wages: m.labour * k, rent: m.fixed_costs * k, apps: m.platform_commission * k,
          tax: (m.pph_final + m.other_costs) * k, owner: m.net_profit * k };
      };
      const last = months[months.length - 1], lp = per100k(last), hm = T.healthy_margin;
      const lastMargin = last.net_sales ? last.net_profit / last.net_sales : null;
      const rp = v => money(Math.round(v / 100) * 100);
      h += '<h2 style="margin:22px 0 10px">' + esc(t("Profit and loss by month")) + (multi ? ' <small class="muted">' + esc(t("charts add the outlets together")) + "</small>" : "") + "</h2>";
      h += '<div class="card" style="margin-bottom:14px"><h3>' + esc(t("In plain words, {m}", { m: last.month })) + '</h3><p style="font-size:15px;line-height:1.6">' +
        esc(t("Of every Rp100.000 that comes in, {a} goes on stock and materials, {b} on wages, {c} on rent and bills, {d} on the apps' commission and {e} on tax.", {
          a: rp(lp.stock), b: rp(lp.wages), c: rp(lp.rent), d: rp(lp.apps), e: rp(lp.tax) })) + " <b>" +
        esc(lp.owner >= 0 ? t("What is left for the owner: {v}.", { v: rp(lp.owner) }) : t("Nothing is left for the owner: the business lost {v}.", { v: rp(-lp.owner) })) + "</b></p></div>";
      h += '<div class="grid g2"><div class="card"><h2>' + esc(t("Where every Rp100.000 goes")) + '</h2><div id="run-pnl-split"></div></div>' +
        '<div class="card"><div class="card-head"><h2>' + esc(t("Net margin by month")) + "</h2>" +
        (lastMargin != null && hm != null ? chip(lastMargin >= hm ? "good" : "bad", t("{m}: {p}", { m: last.month, p: pct(lastMargin, 1) })) : "") + '</div><div id="run-pnl-margin"></div>' +
        (hm != null ? '<p class="muted" style="font-size:12px">' + esc(t("Healthy is at least {p} (from profile.md).", { p: pct(hm) })) + "</p>" : "") + "</div></div>";
      h += '<div class="card" style="margin-top:14px"><div class="table-wrap"><table class="t"><thead><tr><th>' +
        [t("month"), t("net sales"), t("direct cost"), t("labour"), t("fixed"), t("commission"), t("net profit"), t("net margin"), ""].map(esc).join('</th><th class="r">') + "</th></tr></thead><tbody>" +
        pnl.map(m => "<tr><td>" + esc(m.month + (m.outlet ? " · " + m.outlet : "")) + (m._problems && m._problems.length ? " " + chip("bad", t("does not add up")) : "") + '</td><td class="r">' + money(m.net_sales) +
          '</td><td class="r">' + money(m.direct_cost) + " <small>" + pct(m.direct_cost / m.net_sales) + '</small></td><td class="r">' + money(m.labour) + " <small>" + pct(m.labour / m.net_sales) +
          '</small></td><td class="r">' + money(m.fixed_costs) + '</td><td class="r">' + (m.platform_commission != null ? money(m.platform_commission) : "") + '</td><td class="r"><span class="' +
          (m.net_profit >= 0 ? "up" : "down") + '">' + money(m.net_profit) + '</span></td><td class="r">' + pct(m.net_profit / m.net_sales, 1) + '</td><td class="r">' + docLink(m) + "</td></tr>").join("") +
        "</tbody></table></div></div>";
      S.ui.pnlCharts = { months, per100k, hm };
    } else S.ui.pnlCharts = null;

    // cost leak, product mix, staffing
    const cl = (R["cost-leak"] || [])[0], pm = (R["product-mix"] || [])[0], sf = (R.staffing || [])[0];
    if (cl || pm) h += '<div class="grid g2" style="margin-top:22px">';
    if (cl) h += '<div class="card"><div class="card-head"><h2>' + esc(t("Cost leak, {m}", { m: cl.month })) + "</h2>" + docLink(cl) + "</div>" + probs(cl) + '<table class="t">' +
      (cl.items || []).map(x => "<tr><td>" + esc(x.item) + (x.cause ? '<br><small class="muted">' + esc(x.cause) + "</small>" : "") + '</td><td class="r">' + (x.gap_pct != null ? pct(x.gap_pct) : "") +
        '</td><td class="r"><span class="down">' + money(x.gap_rp) + "</span></td></tr>").join("") + "</table>" +
      ((cl.price_rises || []).length ? '<p class="muted" style="font-size:12px">' + esc(t("Price rises: {l}", { l: cl.price_rises.map(x => x.item + " " + money(x.from) + " → " + money(x.to)).join(", ") })) + "</p>" : "") + "</div>";
    if (pm) {
      const byQ = {}, cats = new Set((pm.items || []).map(x => x.category));
      (pm.items || []).forEach(x => (byQ[x.quadrant] = byQ[x.quadrant] || []).push(x));
      h += '<div class="card"><div class="card-head"><h2>' + esc(t("Product mix, {p}", { p: pm.period })) + "</h2>" + docLink(pm) + "</div>" + probs(pm) +
        Object.keys(QUAD).filter(q => byQ[q]).map(q => "<h3>" + esc(t(QUAD[q][0])) + ' <small class="muted">' + esc(t(QUAD[q][1])) + '</small></h3><table class="t">' +
          byQ[q].map(x => "<tr><td>" + esc(x.item) + (cats.size > 1 && x.category ? ' <small class="muted">' + esc(x.category) + "</small>" : "") + '</td><td class="r">' + x.qty.toLocaleString("id-ID") + '</td><td class="r">' + money(x.margin_unit) + "</td></tr>").join("") + "</table>").join("") + "</div>";
    }
    if (cl || pm) h += "</div>";
    if (sf) {
      const hm = sf.heatmap, mx = hm ? Math.max(...hm.values.flat()) : 1;
      h += '<div class="card" style="margin-top:14px"><div class="card-head"><h2>' + esc(t("Staffing, {p}", { p: sf.period })) + "</h2>" + docLink(sf) + "</div>" + probs(sf) +
        '<p>' + esc(t("Labour {a} → {b} of net sales", { a: pct(sf.labour_pct, 1), b: sf.labour_pct_after != null ? pct(sf.labour_pct_after, 1) : "n/a" })) +
        (sf.saving_month != null ? "<br>" + esc(t("saving {v} a month", { v: money(sf.saving_month) })) : "") + "</p>" +
        (hm ? '<div class="table-wrap"><table class="t heat"><thead><tr><th></th><th>' + hm.days.map(esc).join("</th><th>") + "</th></tr></thead><tbody>" +
          hm.hours.map((hr, i) => "<tr><td>" + esc(String(hr)) + "</td>" + hm.values[i].map(v => '<td class="r" style="background:color-mix(in srgb,var(--accent) ' + Math.round(70 * v / mx) + '%,transparent)">' +
            v + "</td>").join("") + "</tr>").join("") + "</tbody></table></div>" : "") + "</div>";
    }
    el.innerHTML = h;

    if (weeks.length) {
      const w = weeks[weeks.length - 1], thr = w.direct_cost_threshold != null ? w.direct_cost_threshold : T.direct_cost_alert;
      const be = weeks.map(x => x.breakeven_per_day ? x.breakeven_per_day * 7 : T.breakeven_week);
      Charts.bars($("#run-weeks"), { labels: weeks.map(x => x.week.slice(5)), values: weeks.map(x => x.net_sales), name: t("net sales"),
        line: be.every(v => v != null) ? { name: t("break-even for the week"), values: be } : null, yfmt: money, height: 240 });
      Charts.bars($("#run-cost"), { labels: weeks.map(x => x.week.slice(5)), values: weeks.map(x => x.direct_cost_pct), name: t("direct cost (estimate)"),
        line: thr != null ? { name: t("alert threshold"), values: weeks.map(() => thr) } : null, yfmt: v => pct(v), height: 240 });
      const dbe = w.breakeven_per_day || T.breakeven_day;
      Charts.bars($("#run-days"), { labels: (w.daily || []).map(x => x.day || x.date.slice(5)), values: (w.daily || []).map(x => x.net_sales), name: t("net sales"),
        line: dbe ? { name: t("break-even a day"), values: (w.daily || []).map(() => dbe) } : null, yfmt: money, height: 220 });
    }
    const pc = S.ui.pnlCharts;
    if (pc) {
      const parts = pc.months.map(pc.per100k);
      Charts.stacked($("#run-pnl-split"), { labels: pc.months.map(m => m.month), yfmt: money, height: 260, series: [
        { name: t("stock and materials"), color: "var(--c1)", values: parts.map(p => p.stock) },
        { name: t("wages"), color: "var(--c5)", values: parts.map(p => p.wages) },
        { name: t("rent and bills"), color: "var(--c4)", values: parts.map(p => p.rent) },
        { name: t("apps' commission"), color: "var(--c2)", values: parts.map(p => p.apps) },
        { name: t("tax"), color: "var(--ink-3)", values: parts.map(p => p.tax) },
        { name: t("left for the owner"), color: "var(--good)", values: parts.map(p => Math.max(0, p.owner)) },
        { name: t("loss"), color: "var(--bad)", values: parts.map(p => Math.min(0, p.owner)) }] });
      Charts.bars($("#run-pnl-margin"), { labels: pc.months.map(m => m.month), values: pc.months.map(m => m.net_sales ? m.net_profit / m.net_sales : 0), name: t("net margin"),
        line: pc.hm != null ? { name: t("healthy margin"), values: pc.months.map(() => pc.hm) } : null, yfmt: v => pct(v, 1), height: 260 });
    }
    if (cf && cf.weeks) Charts.bars($("#run-cash"), { labels: cf.weeks.map(x => "W" + x.label), values: cf.weeks.map(x => x.end_balance), name: t("end-of-week balance"),
      line: { name: t("cash in"), values: cf.weeks.map(x => x.cash_in) }, yfmt: money, height: 240 });
  };

  // ── docs ─────────────────────────────────────────────────────────────────────
  VIEWS.docs = async el => {
    const docs = S.st.docs;
    if (!docs.length) { el.innerHTML = empty(esc(t("Nothing written yet."))); return; }
    const cur = S.sub ? decodeURIComponent(S.sub) : (docs.find(d => d.path === "business-plan.md") || docs.find(d => d.path.endsWith(".md")) || docs[0]).path;
    const groups = {};
    docs.forEach(d => { const g = d.step || "other"; (groups[g] = groups[g] || []).push(d); });
    const order = ["board", "competitors", "consumer", "pricing", "offer", "cfo", "marketing", "brand", "ops", "launch", "plan", "reports", "other"];
    let list = order.filter(g => groups[g]).map(g => '<div class="grp">' + esc(g === "other" ? t(g) : g === "reports" ? t("Reports, after opening") : stepName(g)) + "</div>" + groups[g].map(d =>
      '<a href="#/p/' + S.pid + "/docs/" + encodeURIComponent(d.path) + (S.query.round ? "?round=" + encodeURIComponent(S.query.round) : "") + '" class="' + (d.path === cur ? "on" : "") + '"><span>' + esc(d.path) + "</span><small>" + esc(ago(d.mtime)) + "</small></a>").join("")).join("");
    el.innerHTML = '<div class="docs"><nav class="doclist">' + list + '</nav><div class="card" id="docview">…</div></div>';
    const meta = docs.find(d => d.path === cur) || {};
    try {
      const f = await api(fileUrl(cur));
      let body;
      if (cur.endsWith(".csv")) {
        const rows = MD.csvTable(f.text);
        body = '<div class="table-wrap"><table class="t"><thead><tr><th>' + (rows[0] || []).map(esc).join("</th><th>") + "</th></tr></thead><tbody>" + rows.slice(1).map(r => "<tr><td>" + r.map(esc).join("</td><td>") + "</td></tr>").join("") + "</tbody></table></div>";
      } else if (cur.endsWith(".json")) {
        let pretty = f.text; try { pretty = JSON.stringify(JSON.parse(f.text), null, 2); } catch (e) { /* show as is */ }
        body = '<div class="md"><pre><code>' + esc(pretty) + "</code></pre></div>";
      } else body = doc(f.text, cur, meta.step);
      $("#docview").innerHTML = '<div class="card-head"><h2 class="num" style="font-family:var(--mono);font-size:14px">' + esc(cur) + "</h2><small>" + (meta.step ? esc(stepName(meta.step)) + " · " : "") + esc(ago(f.mtime)) + "</small></div>" + body;
    } catch (e) { $("#docview").innerHTML = empty(esc(e.message)); }
  };

  // ── rounds (phase 2) ─────────────────────────────────────────────────────────
  VIEWS.rounds = async el => {
    const list = await api("/api/p/" + S.pid + "/rounds");
    const ui = S.ui.rounds = S.ui.rounds || { a: list[0] ? list[0].id : "current", b: "current" };
    const rows = [["verdict", m => t(m.verdict || "n/a")], ["buy rate", m => pct(m.buy_rate)], ["price", m => money2(m.price)], ["contribution", m => money2(m.contribution)],
      ["margin at plan", m => pct(m.margin_at_plan)], ["break-even/day", m => intf(m.breakeven_per_day)], ["year 1 profit", m => money(m.year1_profit)], ["cash needed", m => money(m.cash_needed)],
      ["payback", m => m.payback_month ? t("month {m}", { m: m.payback_month }) : "n/a"], ["acceptable price", m => m.price_range && m.price_range[0] != null ? t("{a} to {b}", { a: money2(m.price_range[0]), b: money2(m.price_range[1]) }) : "n/a"],
      ["board score", m => m.board_score != null ? m.board_score.toFixed(1) : "n/a"]];
    let h = '<form class="card" id="round-add" style="margin-bottom:14px;display:flex;gap:10px;align-items:end;flex-wrap:wrap"><label class="field" style="flex:1;min-width:220px"><span>' + esc(t("Save the current state as a round")) +
      '</span><input type="text" name="label" placeholder="' + esc(t("e.g. Pitch v1, before the offer")) + '"></label><button class="btn primary">◷ ' + esc(t("Save round")) + "</button></form>";
    h += '<div class="banner info">' + esc(t("A round is a dated copy of founder/. To test two versions (two pitches, two prices), run one, save a round, change it, run again. Do not run two sessions in the same folder.")) + "</div>";
    if (!list.length) h += empty(esc(t("No rounds yet.")));
    else {
      h += '<div class="card table-wrap"><table class="t"><thead><tr><th>' + esc(t("round")) + "</th>" + rows.map(r => '<th class="r">' + esc(t(r[0])) + "</th>").join("") + "<th></th></tr></thead><tbody>" +
        list.map(r => "<tr><td><b>" + esc(r.label) + "</b><br><small>" + esc(new Date(r.created * 1000).toLocaleString(LOC())) + "</small></td>" + rows.map(x => '<td class="r">' + esc(x[1](r.metrics)) + "</td>").join("") +
          '<td><a class="btn sm" href="#/p/' + S.pid + "/pipeline?round=" + encodeURIComponent(r.id) + '">' + esc(t("View")) + "</a></td></tr>").join("") + "</tbody></table></div>";
      const opts = cur => ['<option value="current"' + (cur === "current" ? " selected" : "") + ">" + esc(t("current")) + "</option>"].concat(list.map(r => '<option value="' + esc(r.id) + '"' + (r.id === cur ? " selected" : "") + ">" + esc(r.label) + "</option>")).join("");
      h += '<div class="card" style="margin-top:14px"><div class="card-head"><h2>' + esc(t("Compare")) + '</h2><div style="display:flex;gap:8px;align-items:center"><select id="ra" style="width:auto">' + opts(ui.a) + '</select>→<select id="rb" style="width:auto">' + opts(ui.b) + '</select></div></div><div id="cmp">…</div></div>';
    }
    el.innerHTML = h;
    $("#round-add").onsubmit = async e => {
      e.preventDefault();
      try { const r = await api("/api/p/" + S.pid + "/rounds", { method: "POST", body: { label: e.target.label.value } }); ui.a = r.id; toast(t("Round saved")); VIEWS.rounds(el); } catch (err) { toast(err.message); }
    };
    if (!list.length) return;
    const cmp = async () => {
      const c = await api("/api/p/" + S.pid + "/rounds/compare?a=" + encodeURIComponent(ui.a) + "&b=" + encodeURIComponent(ui.b));
      const delta = (k, a, b) => {
        if (a == null || b == null || typeof a !== "number" || typeof b !== "number" || a === b) return "";
        const bad = ["breakeven_per_day", "cash_needed", "payback_month"].includes(k);
        return ' <small class="' + ((b > a) !== bad ? "up" : "down") + '">' + (b > a ? "▲" : "▼") + "</small>";
      };
      const keys = { "verdict": "verdict", "buy rate": "buy_rate", "price": "price", "contribution": "contribution", "margin at plan": "margin_at_plan", "break-even/day": "breakeven_per_day", "year 1 profit": "year1_profit",
        "cash needed": "cash_needed", "payback": "payback_month", "acceptable price": "price_range", "board score": "board_score" };
      let x = '<table class="t"><thead><tr><th></th><th class="r">' + esc(c.a.id === "current" ? t("current") : c.a.label) + '</th><th class="r">' + esc(c.b.id === "current" ? t("current") : c.b.label) + "</th></tr></thead><tbody>" +
        rows.map(r => "<tr><td>" + esc(t(r[0])) + '</td><td class="r">' + esc(r[1](c.a.metrics)) + '</td><td class="r">' + esc(r[1](c.b.metrics)) + delta(keys[r[0]], c.a.metrics[keys[r[0]]], c.b.metrics[keys[r[0]]]) + "</td></tr>").join("") + "</tbody></table>";
      const ch = Object.entries(c.changed);
      x += '<h3 style="margin:16px 0 8px">' + esc(t("{n} documents changed", { n: ch.length })) + "</h3>" + ch.map(([f, d]) => '<details style="margin-bottom:6px"><summary><code>' + esc(f) + "</code> " + (d.added ? chip("good", t("new")) : d.removed ? chip("bad", t("removed")) : "") + '</summary><div class="diff">' +
        d.diff.map(l => '<div class="' + (l[0] === "+" ? "add" : l[0] === "-" ? "del" : l[0] === "@" ? "hunk" : "") + '">' + esc(l) + "</div>").join("") + "</div></details>").join("");
      $("#cmp").innerHTML = x;
    };
    $("#ra").onchange = e => { ui.a = e.target.value; cmp(); };
    $("#rb").onchange = e => { ui.b = e.target.value; cmp(); };
    cmp().catch(e => { $("#cmp").innerHTML = empty(esc(e.message)); });
  };

  // ── live updates ─────────────────────────────────────────────────────────────
  let refreshTimer = null, lastTouched = [];
  function typing() {
    const a = document.activeElement;
    return a && $("#main").contains(a) && (a.tagName === "TEXTAREA" || (a.tagName === "INPUT" && a.type === "text") || a.tagName === "SELECT");
  }
  async function refreshState() {
    try { S.st = await api(P("state")); } catch (e) { return; }
    const hdr = $("#hdr");
    if (!hdr) return;
    hdr.innerHTML = header();
    bindHeader();
  }
  // throttled, not debounced: while a skill writes, events arrive every second and a debounce would never fire
  function scheduleRefresh(touched) {
    lastTouched = lastTouched.concat(touched || []);
    if (refreshTimer) return;
    refreshTimer = setTimeout(async () => {
      refreshTimer = null;
      if (typing() || !$("#drawer").hidden) { scheduleRefresh(); return; }
      const t2 = lastTouched; lastTouched = [];
      await refreshState();
      const rel = TAB_STEPS[S.tab];
      if (["pipeline", "docs"].includes(S.tab) || !rel || rel.some(k => t2.includes(k)) || !t2.length) renderView();
    }, 500);
  }
  function connect() {
    if (SNAP || !window.EventSource) return;
    const es = new EventSource("/api/events");
    let opened = false;
    es.onopen = () => { if (opened) { loadProjects(); if (S.pid) scheduleRefresh(); } opened = true; };  // resync after the hub restarts
    es.onmessage = m => {
      let msg; try { msg = JSON.parse(m.data); } catch (e) { return; }
      const d = msg.data;
      if (msg.kind === "files") {
        if (!connect._p) connect._p = setTimeout(() => { connect._p = null; loadProjects(); }, 1500);
        if (d.project === S.pid && !S.query.round) scheduleRefresh(d.steps);
      }
    };
  }

  // ── chrome ───────────────────────────────────────────────────────────────────
  function applyTheme() {
    const th = store("fg-theme") || "auto";
    if (th === "auto") document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", th);
    $("#theme").textContent = { auto: "◐ auto", light: "☀ light", dark: "☾ dark" }[th];
  }
  $("#theme").onclick = () => { const order = ["auto", "light", "dark"]; store("fg-theme", order[(order.indexOf(store("fg-theme") || "auto") + 1) % 3]); applyTheme(); };
  function applyLang() {
    document.documentElement.lang = "en";
    $$("[data-i18n]").forEach(n => { n.textContent = t(n.dataset.i18n); });
  }
  $("#add-project").onsubmit = async e => {
    e.preventDefault();
    const path = e.target.path.value.trim();
    if (!path) return;
    try { const p = await api("/api/projects", { method: "POST", body: { path } }); e.target.path.value = ""; await loadProjects(); location.hash = "#/p/" + p.id + "/pipeline"; }
    catch (err) { toast(err.message); }
  };
  if (SNAP) $("#add-project").hidden = true;

  I18N.set("en");
  applyLang(); applyTheme();
  window.addEventListener("hashchange", () => { render(); });
  loadProjects().then(() => {
    if (!location.hash && S.projects.length === 1) location.hash = "#/p/" + S.projects[0].id + "/pipeline";
    else render();
  });
  connect();
})();
