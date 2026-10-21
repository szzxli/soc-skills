# soc-skills — Quantified Cybersecurity Skill Profiles

> **Free, open-source SOC analyst skill assessment.** Grade your real hands-on work against a public, NIST NICE-mapped rubric and get an evidence-backed skill profile you can put on a resume.
>
> **▶ Live demo:** https://szzxli.github.io/soc-skills/web/ — runs in your browser, no sign-up, no install.

**Quick start**

1. Open the [live site](https://szzxli.github.io/soc-skills/web/) and take the self-assessment.
2. Build evidence with the CISA KEV-driven lab cards in [`labs/`](labs/).
3. Paste your project evidence into **Grade**, bring your own API key (it stays in your browser), and get a per-domain gap analysis.
4. Copy the one-line summary to the top of your resume.

**"Years of experience" is unquantifiable. Certifications don't map to real ability. This project fixes that.**

`soc-skills` is an open framework for turning hands-on security work into **HR-readable, evidence-backed skill profiles** — mapped to the [NIST NICE Cybersecurity Workforce Framework](https://niccs.cisa.gov/workforce-development/nice-framework), graded against public rubrics, and honest about scope. Think *LeetCode for cybersecurity hiring*.

## The problem

- A career-changer with zero experience can't get interviews — nothing on the resume is verifiable.
- A cert-holder (even OSCP) can't map the cert to real-world ability.
- "3 years of SOC experience" tells a hiring manager nothing about what you can actually do.

Result: employers fall back on lazy year-count filters, and skilled people get stuck behind the timeline.

## What this repo contains

| File | What it is |
|---|---|
| [TAXONOMY.md](TAXONOMY.md) | 7 skill domains × 3 levels (L1 guided / L2 independent hands-on / L3 production), anchored to NICE work roles Cyber Defense Analyst (PR-CDA-001) and Incident Responder (PR-CIR-001), each level with observable evidence criteria |
| [MAPPING.md](MAPPING.md) | 5 real home-lab projects graded against the taxonomy, with cert alignment (GSEC / Security+ / OSCP — honest version) and an anti-inflation checklist |
| [PROFILE.md](PROFILE.md) | The author's first one-page, HR-readable skill profile — linkable from a resume |
| [PROJECT.md](PROJECT.md) | The product thesis: two-sided model (free candidate profiles → paid employer verification reports), competitive landscape, phased roadmap |
| [grader/](grader/) | AI grader v1: executable rubric prompt + evidence-bundle harness + validation report (14/15 exact match vs human grades; the 1 miss made the AI *stricter*) |
| [intel/](intel/) | Weekly threat-intel pipeline (CISA KEV + NVD) feeding future lab cards |

Companion repo with the actual labs: [szzxli/soc-home-lab](https://github.com/szzxli/soc-home-lab)

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
- **Phase 4** — Public profile pages: one-click resume/LinkedIn export
- **Future** — Employer-side verification reports ("you claim 5 years — take the test")

## Contributing

This is early. The most useful contributions right now:
- Stress-test the rubric against your own projects — where is it vague?
- Suggest lab cards from recent CVEs (see `intel/`)
- If you hire SOC analysts: what would make you trust a skill profile?

## License

MIT — take it, adapt it, make it yours.
