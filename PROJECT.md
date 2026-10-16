# PROJECT — "Security LeetCode": Quantified Hands-On Security Skill Profiles

> Skeleton v1.0 · 2026-10-15 · thesis revised (reaffirmed by founder, evening of 2026-10-15)
> Thesis: **certs ≠ real ability** — even an OSCP can't be mapped to real job
> performance for a beginner; "years of experience" is an equally unquantifiable
> black box. This product lets genuinely skilled security people **skip the
> "work timeline"**: verifiable hands-on measurement replaces lazy "X years"
> screening, and **auto-generates resume content** — one click produces
> HR-readable skill evidence for job applications.
> Mechanism: **NICE framework skill points × hands-on challenges × AI grading
> × resume auto-generation**.

## 1. Vision

- **Problem**: broken on both ends — career changers with zero experience can't
  get interviews (nowhere to prove themselves); certified people (even OSCP)
  can't map certs to real ability; "3 years SOC experience" says nothing about
  what someone can actually do. Employers fall back on lazy years-based
  screening, and genuinely skilled people get stuck behind the timeline.
- **Solution**: standardized hands-on challenges → NICE skill-point scoring →
  level profile (L1/L2/L3) → mapping to cert domains and job JDs →
  **one-click resume skill blocks** (bullet points / one-page profile / LinkedIn
  version). Goal: let employers replace "years required" with "profile level"
  in initial screening.
- **North star**: an HR person looks at the profile and knows "what this person
  can do, where the evidence is, what it maps to"; the candidate clicks once and
  the resume gains an evidence-backed skill statement.
- **Trust mechanism (the precondition for "skipping the timeline")**: levels
  must be credible or employers won't buy in. Path: public rubric (v1) →
  behavioral process scoring + anti-cheat (v2) → hiring-manager endorsement /
  pilot partnerships (v3). Before v3, never claim "equals X years of experience"
  externally — only state evidence and levels.

## 1.5 Two-sided model (added by founder, evening of 2026-10-15)

The product has two faces: one acquires users, one makes money.

- **Candidate side (acquisition)**: free. Practice skills → earn profile →
  one-click resume generation. Solves "skilled but stuck behind the timeline".
- **Employer side (monetization)**: HR receives a resume claiming "5 years SOC
  experience" with no way to verify — send a test link, the candidate completes
  a leveled assessment, the platform outputs a **standardized skill verification
  report** (NICE mapping + level + evidence summary + anti-cheat statement),
  and HR screens on the report. This is HackerRank/Codility for security, but
  organized by the NICE framework and designed for security roles.

Flywheel: employers screen with reports → candidates must build profiles →
more profile data → more employer trust → more employers. This **solves HR
cold-start in reverse**: instead of waiting for HR to recognize profiles, sell
employers the verification tool and let the market pull candidates in.

Honest notes:
- The employer side is high-stakes; anti-cheat/proctoring must come first (a
  v2 precondition), or reports are worthless.
- Verifying "3/5/10 years" needs senior-differentiating challenges: architecture
  reviews, incident command, detection engineering at scale — an order of
  magnitude harder than junior CTF-style questions. That's the content moat.
- US employment testing has EEOC compliance requirements (tests must be
  job-related, avoid disparate impact) — flagged as legal risk, not solved in v1.

## 2. Competitive analysis (market research, 2026-10-15)

### Open source: largely empty
- The two closest never took off:
  - `csimpson4/chris-ai` — LLM maps job descriptions to NICE; PhD thesis
    project, never productized;
  - `v-k-tsalikidis/Cyber-Posting-Ledger` (★2) — tiny.
- **Conclusion**: no open-source project does "skill quantification + HR
  readability". The niche is empty.

### Commercial: concept validated, but not on the candidate side
- **Cloud Range** — NIST success story
  (https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-resources/success-12):
  maps labs and assessments to NICE KSAs, tracks team capability by work role.
  But it's **B2B**: sold to enterprises for team readiness, not for candidates.
- **HireVue**-style vendors: federal hiring assessments, enterprise/HR
  procurement route.
- **Conclusion**: the NICE-mapping road **has paying customers** (validated on
  the enterprise side) — the concept works.

### HTB Academy deep dive (point-by-point, 2026-10-16)
- **Scale**: 25+ learning paths (job-role paths + skill paths), 355+ modules,
  1770+ hands-on labs — "path packaging" is a validated format.
- **NICE mapping**: modules mapped to NICE Tasks/Knowledge/Skills, with
  in-platform Skill Progress Mapping. **Corrects the 10-15 assessment**: NICE
  mapping is not a blank space — HTB does it. Differentiation is in the four
  points below, not in "having NICE".
- **Zero-friction hands-on**: in-browser VM (Pwnbox), "no infrastructure or
  tool requirements" — zero-setup practice is the industry standard.
- **Report as gate**: certifications require a commercial-grade report to pass —
  this validates the weight of D3/incident-report writing in the profile; report
  quality is the watershed.
- **Second B2B leg**: companies like NVISO use Academy to onboard new hires
  (fill knowledge gaps by track). Enterprises buy not just hiring filters but
  **post-hire capability baselines**.
- **Threat-informed**: training methodology is threat-intel driven — isomorphic
  with Phase 3's CVE-driven lab cards.

**Design inputs adopted from HTB Academy (on the roadmap)**:
1. **Role-path packaging** (Phase 2.5): bundle challenges into job tracks like
   "SOC Analyst Tier 1 ready" — HTB proves candidates pay for "job readiness",
   not "skill points".
2. **B2B onboarding leg** (Phase 4 extension): second use of the profile —
   employers scan new hires for capability baselines and auto-generate training
   plans from gaps. The NVISO model, candidate-side version.
3. **Zero-setup iron rule** (all phases): every challenge must run with one
   command (or one browser open); the pytest setup already meets this — write
   it into lab-card acceptance criteria.
4. **Report quality gate** (Phase 3): advanced lab cards require "report quality
   fit for client delivery" — directly benchmarked against HTB's
   commercial-grade report bar.

**Honest differentiation (corrected)**: HTB is platform-locked (profiles can't
leave HTB), assessments are flag/exercise-based (no open-ended AI grading),
profiles are hacker-facing (HR can't parse them in 30 seconds), closed source.
**soc-skills' niche**: candidate-owned portable skill passport + open-ended AI
grading + HR-readable + open source. NICE mapping is table stakes, not a moat.

### TryHackMe deep dive (point-by-point, 2026-10-16)
- **Positioning**: "Go from wherever you are to the role you want" — role-led,
  beginner-friendly; 1000+ labs, 8M+ users. Paths include Cyber Security 101,
  Pre Security (pure-beginner entry), SOC Level 1, Jr Pentester, AI Security
  (new 2026), CompTIA Pentest+ (cert-alignment track).
- **Methodology**: learn by doing + guided learning (fading scaffolding) +
  gamified labs (streak/point retention).
- **Third B2B leg**: teaching dashboard — instructors assign labs, monitor
  student progress; customers include Google, KPMG, Accenture. The third thing
  enterprises buy: **teaching delivery**.

**Design inputs adopted from TryHackMe (on the roadmap)**:
1. **Diagnostic entry** (Phase 2.5): "from where you are to the role you want" —
   new users take a diagnostic challenge set, auto-routed to a starting track.
   Both an acquisition hook and the profile's first data point.
2. **Pre-Security-style L0 entry track** (Phase 3): a pure-beginner / career-
   changer track (the founder herself is the MRO-to-cyber sample) — lowers the
   top-of-funnel barrier; L0 grants "completion" only, no levels, to avoid
   grade inflation.
3. **Education delivery leg** (Phase 4 extension): the same challenge engine's
   third buyer — bootcamps/universities use challenges + AI grading as homework
   infra. All three B2B legs: hiring filter (hire) → onboarding baseline
   (onboard, HTB model) → teaching delivery (teach, THM model).

**THM's gaps (same niche)**: platform-locked, no portable passport, no
open-ended AI grading, hacker-facing UI. Same conclusion as HTB.

### SkillCertPro (CEH practice-test vendor) deep dive (2026-10-16)
- **How it sells**: 1250 questions / 30 sets / $19.99, "100% Pass Guaranteed",
  online mock exams, lifetime access, Master Cheat Sheet (cram 2–3 days before
  the exam).
- **Teachable mechanisms (legitimate)**:
  1. **Readiness gate**: score 85%+ on mocks before sitting the real exam — a
     quantified "ready to book" bar.
  2. **Review wrong AND right**: review explanations for correct answers too —
     catches lucky guesses.
  3. **Living question bank**: weekly updates from student feedback on what
     appeared on the real exam — the bank is alive, not static.
- **Red line (never touch)**: "real exam questions" / "appeared on the real
  exam" is braindump gray area and violates EC-Council NDAs. Our stance:
  **never touch real exam content** — a trust asset, and the fundamental
  difference from these vendors: they sell "passing", we sell "being able".

**Mechanisms adopted from SkillCertPro (on the roadmap)**:
1. **85% readiness gate** (Phase 2.5): a "book-the-exam bar" per domain —
   recommend booking only after two consecutive mocks ≥85%. Doubles as the
   founder's own GSEC prep yardstick.
2. **Guess detection** (Phase 2): AI grading judges more than right/wrong —
   flags "correct answer, weak reasoning / missing process" for mandatory
   review — the "review right answers" counterpart.
3. **Pre-exam cram sheet** (Phase 4): auto-generate a one-page cheat sheet from
   personal weak domains 3 days before the exam — SkillCertPro's generic cheat
   sheet, personalized.

**Positioning in one line**: SkillCertPro proves "cert anxiety" is the
highest willingness-to-pay scenario; we don't compete for the "cram to pass"
business — we own "actually skilled after passing". The former is the traffic
entry; the latter is retention.

### Positioning: the broken middle
```
HTB / TryHackMe (gamified, HR can't read it)
        ↕ gap
Cloud Range / HireVue (enterprise B2B, out of candidates' reach)
```
**Entry point**: candidate-side, open source, HR-readable — no one occupies
all three today. Strategy: enter with free open-source candidate tooling,
accumulate profile data via community content (CVE-driven lab cards, AI
grader); the NICE language enterprises already know needs no market education.

### Risk honesty notes
1. **Grading authority**: who decides "this challenge = 2 years experience"?
   Public rubric + community early; hiring-manager endorsement long-term.
2. **Anti-cheat**: writeup sharing, flag sharing. Mitigation: dynamic
   questions, behavioral process scoring (not just flags).
3. **HR cold start**: profiles need HR recognition to have value. Mitigation:
   serve candidates first (resume links), spread via "someone got interviews".

### Hiring-manager field feedback (2026-10-16, Reddit, Top 1% commenter, 10 years of data)
One data point — "10 years of portfolio links on my resume, 1 recruiter ever
clicked" — changed four product assumptions:

1. **Distribution assumption corrected**: link-on-resume is the failure mode,
   not the design. The 30-second summary must be readable **without clicking**
   (resume-embedded text, ATS-parseable); the link is only the audit trail.
   Primary channel is employer-initiated (employer sends the challenge), not
   candidate-posted links.
2. **New profile view: multi-hat readiness**: HMs hire "1 person to do 3–4
   jobs"; pedigree can't show the 4th hat. The profile adds a **breadth
   coverage view** (7 domains × level matrix) answering "how many hats can
   they wear" at a glance. Core component of the Phase 4 profile page.
3. **Honest positioning**: the product doesn't create demand (junior-market
   tightening is macro fact) — it only lowers the cost of finding signal; and
   profiles serve **seniors too** — multi-hat verification for experienced
   hires is equally a need.
4. **Employer-side cost iron rule**: under budget pressure, any design that
   adds HM work is dead on arrival. The employer side must be near-zero cost:
   one glance, standardized signal, no new tabs.

## 3. MVP roadmap

### Phase 1 · Skeleton (✅ done, 2026-10-15)
- **Input**: 5 home-lab projects + public NICE framework materials.
- **Output**: 4 files in this directory —
  `TAXONOMY.md` (7 skill domains × L1/L2/L3 rubric),
  `MAPPING.md` (5 projects tagged + cert mapping),
  `PROFILE.md` (first HR-readable profile),
  `PROJECT.md` (this file).
- **Acceptance**: profile is resume-ready; every L2 has an evidence chain; L3
  stays empty; anti-inflation checklist passes.

### Phase 2 · AI grader (next)
- **Input**: TAXONOMY rubric + user-submitted training reports/code.
- **Output**: `grader/` — prompts/scripts scoring against the rubric item by
  item; output: per-item scores + evidence references + upgrade guidance
  ("what's missing for L2").
- **Acceptance**: grades the founder's own 5 projects within ±1 band of the
  MAPPING.md human ratings; scoring rationale explainable and reproducible.
- **Dogfood**: the first graded subject is the founder herself.

### Phase 3 · CVE-driven lab cards
- **Input**: weekly public CVEs (CISA KEV first).
- **Output**: standardized lab cards — vuln mechanics → repro steps → detection
  rules → remediation → mapped NICE skill points and levels; all in isolated lab.
- **Acceptance**: 1 card/week; each card has a "solvability check" (founder
  walks it through by hand); each card carries NICE mapping.
- **Design input (2026-10-16, from community feedback)**: lab cards must answer
  the "line cook test" — real work isn't finishing one dish, it's sustaining
  output under a boss-set cadence, shifting priorities, and surprise events.
  Advanced lab cards add **mid-task injects** (mid-task priority changes, new
  alerts cutting the queue, tools suddenly unavailable) to test triage
  discipline and output stability under disruption. Positioning: the profile is
  a **trial shift, not a resume** — cooks get hired via staging; security
  analysts deserve the same gate.

### Phase 4 · Public profile page
- **Input**: Phase 2 grader + user-authorized public training records.
- **Output**: static profile page template (skill snapshot table + evidence
  chain links + cert mapping), one-click generated, resume/LinkedIn-ready.
- **Core components (added from 2026-10-16 HM feedback)**:
  - **30-second summary**: plain text, resume-embeddable, ATS-parseable — no
    link-click required;
  - **multi-hat readiness matrix**: 7 domains × levels, breadth at a glance
    ("how many hats");
  - evidence chain: folded under the summary, for whoever wants to audit.
- **Acceptance**: founder's profile page live; 3 external users trial it and
  give feedback; viewed by at least 1 real interviewer (counted during the
  founder's job search).

## 4. Not-doing list (v1)
- No online judge system (no resources; human + AI grading first).
- Never touch official cert question banks verbatim (copyright risk; only
  original labs and public-material mappings).
- No "guaranteed interviews" / "equals X years experience" marketing — the
  profile states evidence and levels only; "skipping the timeline" is earned
  through employer trust mechanisms (§1), not a slogan.
