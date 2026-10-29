# soc-skills — SOC Skill Gap Analysis from Your Own Evidence

> **Free, open-source gap analysis for SOC job seekers.** Grade your real hands-on work against a public, NIST NICE-mapped rubric, see what you're still missing for a SOC analyst role, and where to learn it. It **complements** certs and platforms like Security+/CySA+, BTL1 and TryHackMe/Hack The Box — it doesn't replace them.
>
> **▶ Live demo:** https://szzxli.github.io/soc-skills/web/?ref=gh-socskills — runs in your browser, no sign-up, no install.

**Quick start**

1. Open the [live site](https://szzxli.github.io/soc-skills/web/?ref=gh-socskills) and take the self-assessment.
2. Build evidence with the CISA KEV-driven lab cards in [`labs/`](labs/).
3. Paste your project evidence into **Grade**, bring your own API key (it stays in your browser), and get a per-domain gap analysis with "where to learn this" links (TryHackMe, LetsDefend, CyberDefenders, BTL1, CompTIA objectives, MITRE ATT&CK).
4. Copy the one-line summary to the top of your resume, or print the one-page summary (Résumé/LinkedIn one-pager).

**Rubric version:** v1.3 (2026-10-20). Changelog in [grader/README.md](grader/README.md#versions). The stored example and sample profile were graded with v1.1; D1–D7 criteria are unchanged since then.

**"Years of experience" says little about what you can do, and a cert tests knowledge, not the work you've shown. This project adds the missing piece: an evidence-based gap list.**

`soc-skills` is an open framework for turning hands-on security work into **HR-readable, evidence-backed skill profiles** — mapped to the [NIST NICE Cybersecurity Workforce Framework](https://niccs.cisa.gov/workforce-development/nice-framework), graded against public rubrics, and honest about scope. Think *LeetCode for cybersecurity hiring*.

## The problem

- A career-changer with zero experience can't get interviews — nothing on the resume is verifiable.
- A cert-holder (even OSCP) can't map the cert to real-world ability.
- "3 years of SOC experience" tells a hiring manager nothing about what you can actually do.

Result: employers fall back on lazy year-count filters, and skilled people get stuck behind the timeline.

## What this repo contains

| File | What it is |
|---|---|
| [TAXONOMY.md](TAXONOMY.md) | 8 skill domains × 3 levels (L1 guided / L2 independent hands-on / L3 production), D1–D6 anchored to NICE work roles Cyber Defense Analyst (PR-CDA-001) and Incident Responder (PR-CIR-001) (D7 cross-role, D8 AI agent security has no NICE mapping yet), each level with observable evidence criteria |
| [MAPPING.md](MAPPING.md) | 5 real home-lab projects graded against the taxonomy, with cert alignment (GSEC / Security+ / OSCP — honest version) and an anti-inflation checklist |
| [PROFILE.md](PROFILE.md) | The author's first one-page, HR-readable skill profile — linkable from a resume |
| [PROJECT.md](PROJECT.md) | The product thesis: two-sided model (free candidate profiles → paid employer verification reports), competitive landscape, phased roadmap |
| [grader/](grader/) | AI grader (rubric v1.3): executable rubric prompt + evidence-bundle harness + validation report (14/15 domains matched the **author's own** ratings of the author's own 5 projects — not independent raters; see Limitations) |
| [intel/](intel/) | Weekly threat-intel pipeline (CISA KEV + NVD) feeding future lab cards |
| [labs/](labs/) | CVE / KEV-driven lab cards, each with a `*-detect.py` detector (synthetic sample logs live in the companion repo, `soc-home-lab/07-kev-hunting/samples/`) |
| [web/](web/) | The static site: self-assessment, AI grading (BYOK), gap analysis with learning links, progress history with JSON export/import, résumé one-pager, verification packages — live at https://szzxli.github.io/soc-skills/web/?ref=gh-socskills |

Companion repo with the actual labs: [szzxli/soc-home-lab](https://github.com/szzxli/soc-home-lab)

## Verification packages: what they prove

A verification package is the profile JSON plus a SHA-256 hash of it. A matching hash on the [Verify page](https://szzxli.github.io/soc-skills/web/verify.html?ref=gh-socskills) proves **the file is unchanged since the hash was made** — nothing more. It is not a digital signature: it does not prove the content is truthful, who made it, or when (the "issued" time is self-asserted), and anyone who edits a package can recompute its hash.

**Optional free public timestamp:** post the package hash in a **public GitHub gist** (the Verify page has a "Copy gist text" button). GitHub records when the gist was created and last edited, so the Verify page can show the hash was public *no later than* that date. No server, no paid service. Commit dates can be backdated by the committer, so only gists are checked; [OpenTimestamps](https://opentimestamps.org/) is an alternative for advanced users (not checked by the site).

## Limitations

- **Small, self-made validation set:** the rubric was checked on the author's own 5 home-lab projects, against the author's own ratings, with the author's own rubric.
- **No human-rater comparison yet** and no inter-rater reliability data.
- **AI grades vary between runs**, especially with free/small models; run-to-run variance has not been measured (the evaluator-independence results in `grader/` are illustrative, not measured).
- **Evidence is taken at face value**: the grader reads what you paste; it does not run your code.
- **Not a certification.** Advisory gap analysis only.

## Help validate

If you work in a SOC or hire for one: blind-rate a public sample evidence bundle with the rubric before looking at the AI grade, and submit your levels with the [blind rating issue form](https://github.com/szzxli/soc-skills/issues/new?template=blind-rating.yml). Protocol: [grader/HUMAN-RATING.md](grader/HUMAN-RATING.md). Ratings are public and will be published as inter-rater data.

## Grading philosophy

1. **Evidence first** — every level needs observable proof. No evidence, no points.
2. **Scope suffixes** — L2 is always labeled `(lab)` / `(synthetic)` / `(reconstructed)`. Never oversell.
3. **L3 stays empty** — no self-assessed production experience, period.
4. **Downgrade on doubt** — ambiguous evidence grades low, not high.
5. **Honest cert mapping** — "aligned with GSEC domains" ≠ "at GSEC level". OSCP is not claimed on a defensive track.

## Roadmap

- **Phase 1** ✅ — Taxonomy + first profile (this repo's core)
- **Phase 2** ✅ — AI grader with validation
- **Phase 3** — Weekly CVE-driven lab cards (threat intel → reproducible scenarios → NICE-mapped)
- **Phase 4** — Public profile pages (a printable résumé/LinkedIn one-pager ships today)
- **Validation** — collect blind human ratings; publish inter-rater agreement
- **Future** — Employer-side verification reports ("you claim 5 years — take the test")

## Contributing

This is early. The most useful contributions right now:
- Stress-test the rubric against your own projects — where is it vague?
- Suggest lab cards from recent CVEs (see `intel/`)
- If you hire SOC analysts: what would make you trust a skill profile?

## License

MIT — take it, adapt it, make it yours.

## Privacy

Privacy: we count anonymous page views with [GoatCounter](https://www.goatcounter.com) — no cookies, no personal data, no consent banner needed. Your content never goes to the counter: anything you type, paste or upload stays in your browser (except requests you start yourself, such as an AI-grading or lookup call to a provider you choose). Exactly what is sent is documented at the top of the site's `analytics.js`.
