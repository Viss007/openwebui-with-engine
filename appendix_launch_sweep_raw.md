# Appendix — Launch Sweep (2025‑09‑06)

**Guardrail:** Agent mode **OFF** by default. Run only when explicitly invoked.

**Note on currency:** All non‑EUR prices converted to EUR using pinned FX (rounded 2 decimals): **USD→EUR 0.92** (so **\$1 ≈ €0.92**), **GBP→EUR 1.15** (so **£1 ≈ €1.15**), **EUR→GBP 0.8678** (so **£1 ≈ €1.153**). Rounded to **2 decimals**.

---

## A) Competitor snapshot — **agencies** (Notion automation/ops)

| Agency                           | Offer tag                                         | Entry price (EUR) | Format        | 2 differentiators                                                                            |
| -------------------------------- | ------------------------------------------------- | ----------------- | ------------- | -------------------------------------------------------------------------------------------- |
| **Anna Builds — Notion Ops Kit** | Productized ops kit for leads→clients             | €1,200            | Fixed package | 2–3 systems bundled; 2 weeks of support + async Q&A                                          |
| **Taina & Co. (Notion Partner)** | Workspace migration/implementation                | €2,500–€6,000     | Project       | Notion Partner badge; documented budget bands on directory; broad services incl. automations |
| **CJ Wray (Consultant)**         | Hourly Notion consulting (setup, DB, automations) | €120–€160         | Hourly        | Public hourly anchor; scope expands to full builds                                           |

**Takeaway:** Agencies skew project/productized; clear scope + visible pricing wins trust.

---

## A2) Competitor snapshot — **platforms** (context)

| Platform         | Tagline                | Free plan       | Entry pricing (EUR) | Note                                       |
| ---------------- | ---------------------- | --------------- | ------------------- | ------------------------------------------ |
| **Make**         | Visual automations     | Yes             | \~€9/mo             | Popular with Notion users; scenario limits |
| **Zapier**       | No‑code automation     | Yes             | \~€20/mo            | Broad app coverage; task pricing           |
| **n8n**          | Open‑source workflows  | Yes (self‑host) | \~€20/mo Cloud      | Dev‑friendly; fair‑code license            |
| **FlowHunt**     | AI agents & flows      | Trial           | \~€20–€50/mo        | AI‑native, agent primitives                |
| **Activepieces** | Open‑source Zapier alt | Yes             | \~€15/mo Cloud      | Simple, open source                        |

**Takeaway:** Platforms are low‑entry, but KPI‑tied outcomes are not guaranteed.

---

## B) Launch assets (Notion page contents)

- 🚀 **Hero:** “Cut Support **FRT −30%** in 14 days.”
- 📈 **Proof:** mini case; KPI chart image.
- 🎯 **Offer:** pilot (€1,500) → credited if KPI met.
- 🧩 **Scope:** data connectors (Notion, Zendesk/Intercom, Slack), evaluators, dashboards.
- 🛡️ **SLA & Risk reversal:** “KPI or it’s free.”
- ❓ **FAQ:** data security, support, limits.
- 📅 **CTA:** “Book discovery (30m)” + calendar link.

---

## C) Outreach & DM scripts (EU)

**First DM (LinkedIn/Email)**

> Hey {{first}}, noticed your team handles a high ticket volume. We run a 14‑day pilot that cuts **First Response Time \~30%** using an AI support autopilot (Notion + Zendesk/Intercom). If we don’t hit the KPI, the pilot’s free. Worth a 20‑min call?

**Follow‑up (2–3 days)**

> Quick nudge, {{first}} — happy to share a 1‑pager and a before/after KPI chart. If not you, who’s best to speak with on support ops?

---

**Email variant (metric‑led)**

> Subject: Cut FRT \~30% in 14 days (quick idea)
>
> Hi {{first}} — we recently helped a support team cut **First Response Time by 37%** in two weeks using an AI autopilot for Intercom/Zendesk. If we don’t hit an agreed KPI in 14 days, it’s free. Interested in a 20‑min walkthrough?

---

## D) Sprint board (W1–W4)

- 🗓️ **W1 — Offer & Targeting**: finalize outcome+SLA offer; shortlist 20 design partners; prep ROI calc; polish Notion kit; line up reference metrics.
- 🛠️ **W2 — Deploy**: install **Intercom (Unlisted)**; set up **Zendesk Preview**; baseline KPIs; enable 2–3 flows (assist mode); turn on evaluators (LangSmith/TruLens/Evals).
- 📏 **W3 — Measure**: mid‑pilot KPI check; if ≥20% lift, enable limited auto‑resolutions; fix low‑groundedness cases; expand FAQ/KB.
- 📣 **W4 — Proof & Listings**: publish mini‑case + teardown; prep **Intercom listing** (copy, 2–5 images ≥1600×1000 (8:5), PNG, <21 MB, Start Guide); build **Zendesk ZIP** (manifest, OAuth, headers) with pricing/trial; outreach 15–20 lookalikes.

### Submission mini‑checklists (snapshots)

- 🛠️ **Intercom (Appendix I):** Start Guide bullets • 2–5 images **≥1600×1000 (8:5)**, PNG, <21 MB • listing copy • direct install URL.
- 🧰 **Zendesk (Appendix J):** ZAT scaffold + `manifest.json` • global OAuth client (mandatory; no API tokens/basic auth) • required request headers • preview link.
- 📦 **Notion (Appendix K):** enable **Duplicate** • 2–3 screenshots • submission form text.
- 🔗 **Drive assets folder (Intercom & Zendesk):** [https://drive.google.com/drive/folders/1RvewW11H0yDmtHrqgLIb3Q8SIyg-oe3E?usp=drive\_link](https://drive.google.com/drive/folders/1RvewW11H0yDmtHrqgLIb3Q8SIyg-oe3E?usp=drive_link)

## Copy‑paste prompts (internal)

**Agencies only (recommended)**

> Agent: Launch Sweep v2 — scope: EU agencies offering Notion automations/ops; collect 3–5 with entry pricing in EUR; note 2 differentiators each; save to `/mnt/data/research/vissai/agencies_YYYY‑MM‑DD.md`. Stop when saved.

**Platforms only (context)**

> Agent: Platform Scan — scope: Make, Zapier, n8n, FlowHunt, Activepieces; capture free plan and entry pricing; save to `/mnt/data/research/vissai/platforms_YYYY‑MM‑DD.md`. Stop when saved.

---

## Checklists

- ⏱️ **Pre‑run (30s):** scope picked • deliverable picked • EUR pinned • destination chosen.

- 🔄 **During:** switch source once if blocked → else mark unknown • keep cells short • collect ≤5 sources.

- ✅ **After:** artifact opens • sources resolve • pointer added (if needed).

---

## E) Website — SEO/JSON‑LD & Publishing

**Meta & OG**

- 🏷️ Set **Title** (≤60) & **Description** (≤160) for **every page**.
- 🖼️ **Default OG image** = `og-image.png`; page‑level OG for **Pricing** = `og-image-pricing.png`, **Results** = `og-image-results.png`.
- 🔗 Ensure **canonical URLs**, **sitemap.xml** and **robots.txt** are present.

**JSON‑LD (paste into Page Settings → Head)**

- 🏠 **Home**: Organization JSON‑LD.
- 🧾 **Pricing**: FAQ + Product JSON‑LD (reflect outcome pricing).
- ✅ Validate **Home** and **Pricing** in Google Rich Results (pass required).

**Snippets**

- 📅 **Calendly** on `/book‑a‑demo` (or `/book‑demo`) via Embed (CSS + JS + container div; fixed height).
- 💬 **Intercom**: project \*\*Before \*\*; **Plausible**: project **Head**.
- 🧠 Remember: scripts **render only on published site** (Designer/Editor show a warning).

---

## F) Accessibility & Performance

**Accessibility (WCAG 2.2 AA)**

- 🔎 Ensure **Focus not obscured** on active elements (2.4.11)
- 🎯 **Target Size (Minimum)** for interactive elements (2.5.8)
- 🔐 **Accessible Authentication (Minimum)** (3.3.8)
- 🧲 **Dragging Movements** alternatives available (2.5.7)
- ⏭️ Add **Skip to content** link; ensure **visible focus** on links/buttons.
- 🏷️ Alt text on images; one **H1** per page; semantic headings.

**Performance**

- ⚡ Target **INP ≤200 ms @ p75**
- 🖼️ Convert hero/section images to **WebP**; enable asset compression.
- 💤 **Lazy‑load** non‑hero media; 🔤 **preload** primary font; avoid layout shifts.
- 📱 Target **Lighthouse (mobile) ≥90** on **Home** and **Pricing** (Performance/SEO/Best Practices/Accessibility).

---

## G) Legal & AI Transparency (website copy hooks)

- 🔗 Footer link: **“How we use AI”** — disclose assistant labeling, output marking, and logging for quality.
- 🔒 **Privacy**: note evaluator logging (accuracy/safety), data minimization/redaction, retention windows.
- 📄 **Terms**: define **“AI resolution”** as the billing unit; credit/rollback policy reference.
- 🗨️ UI text: show **“You’re interacting with an AI assistant.”** in chat and mark AI‑generated emails.

---

## H) Staging vs Production

- 📊 **Plausible** counts only on **vissai.com**; expect **no analytics** on `*.webflow.io` staging.
- 🧩 Browser blockers can hide Calendly/Intercom; test with blockers off.
- 🚦 Keep production snippets gated behind “approval to publish” in runbooks.

---

## I) Publish & Domain Mapping

1. 🚀 **Publish to staging** (`*.webflow.io`) → verify: Calendly on Book a demo, Intercom bubble, JSON‑LD valid, OG cards render.
2. 🌐 **Map domain**: add `vissai.com` + `www.vissai.com` in Hosting; create DNS **A** and **CNAME** records; set default host; publish and confirm **HTTPS + canonical redirects**.
3. 📊 Re‑run Lighthouse (mobile) and Rich Results after go‑live; confirm Plausible events on **vissai.com**.

---

## Upgrade Policy — command protocol

Use one‑line commands to request changes. I’ll return patches and, if needed, a full updated file and a revert block.

```
UPGRADE REQUEST
 doc: Launch Sweep
 scope: <section|full>
 confirm: yes
```

**Rules**

- ➕ Additive first; micro‑fixes auto‑apply; risky writes (Project Settings, DNS, publish) require approval.
- 🗂️ Keep this appendix website‑focused; deeper specs live in **Ops Library — Appendices**.

---

*Source: /mnt/data/launch\_sweep.md · last updated 2025‑09‑07.*



Source: Launch Sweep — Appendix · canvas

