/* =============================================================
 * submit-pir.js — shared PIR submission modal (Option B frontend)
 *
 * Reusable across the HTML tools. A page calls:
 *
 *   PirSubmit.open({
 *     summary:       "PIR: Project — 400h",
 *     justification: "https://.../#id=...",   // the unique shareable URL
 *     forecast:      "#",                       // placeholder for now
 *     csv:           "<the generated CSV text>",
 *     filename:      "project-pir.csv"
 *   });
 *
 * It opens a modal with those fields PRE-FILLED (editable), checks auth via
 * the backend (/api/me); if not signed in it sends the user to /auth/login
 * (company Jira SSO). On submit it POSTs to /api/submit which uploads the CSV
 * as an attachment and creates the Service Desk request.
 *
 * Requires the local backend (server/server.py). When opened from file://
 * there is no backend, so it shows a clear message instead of failing badly.
 * ============================================================= */
(function () {
  const API = {
    me: "/api/me",
    submit: "/api/submit",
    login: "/auth/login",
  };

  // running without the backend? (file:// or no server)
  const hasBackend = location.protocol === "http:" || location.protocol === "https:";

  function el(tag, attrs, children) {
    const n = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      if (k === "style") n.style.cssText = attrs[k];
      else if (k.startsWith("aria") || k === "role" || k === "for" || k === "type")
        n.setAttribute(k, attrs[k]);
      else n[k] = attrs[k];
    }
    (children || []).forEach(c => n.appendChild(typeof c === "string" ? document.createTextNode(c) : c));
    return n;
  }

  function ensureStyles() {
    if (document.getElementById("pir-modal-style")) return;
    const css = `
    .pir-ovl{position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;
      align-items:flex-start;justify-content:center;z-index:1000;padding:40px 16px;overflow:auto}
    .pir-modal{background:#fff;color:#232F0F;width:100%;max-width:640px;border-radius:12px;
      box-shadow:0 12px 40px rgba(0,0,0,.3);font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
    .pir-hd{background:#232F0F;color:#fff;padding:14px 18px;border-radius:12px 12px 0 0;
      display:flex;align-items:center;justify-content:space-between}
    .pir-hd h2{font-size:16px;margin:0}
    .pir-x{background:transparent;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1}
    .pir-bd{padding:16px 18px}
    .pir-bd label{display:block;font-size:12px;color:#6b7261;margin:10px 0 3px;font-weight:600}
    .pir-bd input,.pir-bd textarea{width:100%;font:inherit;padding:8px;border:1px solid #e0e2d8;
      border-radius:6px;color:#232F0F;box-sizing:border-box}
    .pir-bd textarea{min-height:70px;resize:vertical}
    .pir-ft{padding:12px 18px 18px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
    .pir-btn{font:inherit;font-weight:700;padding:9px 16px;border:none;border-radius:6px;cursor:pointer}
    .pir-primary{background:#B9FF8D;color:#232F0F}
    .pir-ghost{background:#fff;border:1px solid #232F0F;color:#232F0F}
    .pir-status{font-size:13px;margin-left:auto}
    .pir-ok{color:#2f7d32}.pir-bad{color:#b3261e}
    .pir-note{font-size:12px;color:#6b7261;margin-top:6px}
    .pir-btn:focus-visible,.pir-x:focus-visible,.pir-bd input:focus-visible,.pir-bd textarea:focus-visible{
      outline:3px solid #232F0F;outline-offset:2px}
    `;
    const s = el("style", { id: "pir-modal-style" }); s.textContent = css;
    document.head.appendChild(s);
  }

  let lastFocus = null;

  function close(ovl) {
    ovl.remove();
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    document.removeEventListener("keydown", escClose);
  }
  let currentOvl = null;
  function escClose(e) { if (e.key === "Escape" && currentOvl) close(currentOvl); }

  async function getJSON(url, opts) {
    const r = await fetch(url, Object.assign({ headers: { "Accept": "application/json" } }, opts || {}));
    let body = null;
    try { body = await r.json(); } catch (e) {}
    return { status: r.status, body };
  }

  async function open(data) {
    ensureStyles();
    lastFocus = document.activeElement;
    data = data || {};

    const fSummary = el("input", { type: "text", value: data.summary || "", "aria-label": "Summary" });
    const fJust = el("textarea", { "aria-label": "Request Justification" }); fJust.value = data.justification || "";
    const fForecast = el("input", { type: "text", value: data.forecast || "#", "aria-label": "Project Forecast Page" });
    const fFile = el("input", { type: "text", value: data.filename || "allocation-plan.csv", "aria-label": "Attachment file name" });

    const status = el("span", { className: "pir-status" });
    const submitBtn = el("button", { className: "pir-btn pir-primary", type: "button" }, ["Submit PIR"]);
    const cancelBtn = el("button", { className: "pir-btn pir-ghost", type: "button" }, ["Cancel"]);
    const xBtn = el("button", { className: "pir-x", type: "button", "aria-label": "Close" }, ["×"]);

    const body = el("div", { className: "pir-bd" }, [
      el("label", {}, ["Summary"]), fSummary,
      el("label", {}, ["Request Justification"]), fJust,
      el("label", {}, ["Project Forecast Page"]), fForecast,
      el("label", {}, ["Allocation plan (attached CSV file name)"]), fFile,
      el("div", { className: "pir-note" }, ["The generated CSV is attached automatically. Fields are pre-filled — edit if needed."]),
    ]);
    const header = el("div", { className: "pir-hd" }, [el("h2", {}, ["Submit Project Initiation Request"]), xBtn]);
    const footer = el("div", { className: "pir-ft" }, [submitBtn, cancelBtn, status]);
    const modal = el("div", { className: "pir-modal", role: "dialog", "aria-label": "Submit PIR" }, [header, body, footer]);
    const ovl = el("div", { className: "pir-ovl" }, [modal]);
    document.body.appendChild(ovl);
    currentOvl = ovl;
    document.addEventListener("keydown", escClose);
    ovl.addEventListener("mousedown", e => { if (e.target === ovl) close(ovl); });
    xBtn.onclick = () => close(ovl);
    cancelBtn.onclick = () => close(ovl);
    fSummary.focus();

    if (!hasBackend) {
      status.className = "pir-status pir-bad";
      status.textContent = "Open via the local server (server/server.py) to submit.";
      submitBtn.disabled = true;
      return;
    }

    // check auth up front (non-blocking)
    getJSON(API.me).then(res => {
      if (res.status === 200 && res.body && res.body.authenticated) {
        status.className = "pir-status pir-ok";
        status.textContent = "Signed in as " + (res.body.displayName || res.body.email || "you");
      } else {
        status.className = "pir-status";
        status.textContent = "Not signed in — you'll be asked to log in on submit.";
      }
    }).catch(() => {});

    submitBtn.onclick = async () => {
      submitBtn.disabled = true;
      status.className = "pir-status";
      status.textContent = "Checking sign-in…";
      // 1) ensure authenticated
      const me = await getJSON(API.me).catch(() => ({ status: 0 }));
      if (!(me.status === 200 && me.body && me.body.authenticated)) {
        status.textContent = "Redirecting to company login…";
        window.location.href = API.login;   // SSO; returns to the app after consent
        return;
      }
      // 2) submit
      status.textContent = "Submitting…";
      const res = await getJSON(API.submit, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({
          summary: fSummary.value, justification: fJust.value,
          forecast: fForecast.value || "#", csv: data.csv || "", filename: fFile.value,
        }),
      }).catch(e => ({ status: 0, body: { error: String(e) } }));

      if (res.status === 200 && res.body && res.body.ok) {
        status.className = "pir-status pir-ok";
        const key = res.body.issueKey || "created";
        status.textContent = "✓ Submitted: " + key;
        if (res.body.web) {
          const a = el("a", { href: res.body.web, target: "_blank", style: "margin-left:8px;color:#2f7d32;font-weight:700" }, ["View"]);
          footer.appendChild(a);
        }
      } else if (res.status === 401) {
        status.textContent = "Session expired — redirecting to login…";
        window.location.href = API.login;
      } else {
        status.className = "pir-status pir-bad";
        const err = (res.body && (res.body.error || JSON.stringify(res.body))) || ("HTTP " + res.status);
        status.textContent = "Failed: " + String(err).slice(0, 240);
        submitBtn.disabled = false;
      }
    };
  }

  window.PirSubmit = { open };
})();
