# Agent Tool-Execution Endpoints Without Authentication — One Pattern, Five CVEs

**Status: DETECTOR VALIDATED on synthetic log (TP=1 FP=0, 2026-10-20) · no live-instance lab — detection runs on enriched HTTP access / proxy logs only**
**Severity:** Critical · **CVSS v3.1:** 9.8 (all five) · **CWE-306** (Missing Authentication for Critical Function) / **CWE-1188** (Insecure Default Initialization) · **NOT in CISA KEV** (as of 2026-10-20)
(Five AI agent frameworks published the same morning, 2026-10-20 — same flaw shape, five codebases)

> Anti-inflation: reading this card = L1 at most. Running the detection
> validation = evidence toward L2. Standing up one of the vulnerable
> frameworks to "try the request" is exploit work, not SOC work — it is
> deliberately out of scope here.

## Verified facts (checked against NVD, 2026-10-20)

All five entries were published to NVD on 2026-10-20 (Cognition's on
2026-10-19). Scores below are the CNA base scores carried by NVD.

| CVE | Product / affected | Endpoint(s) | Mechanism |
|---|---|---|---|
| CVE-2026-77936 | Letta, through 0.16.8 | `POST /v1/tools/run`, `/v1/admin/*` | Shipped `compose.yaml` never enables `LETTA_SERVER_SECURE`, so the password middleware is never added and **all API routes are unauthenticated**; the same compose file exposes a superuser PostgreSQL port with default credentials. Attackers execute arbitrary Python via the tools endpoint, or OS commands via PostgreSQL `COPY … PROGRAM`. |
| CVE-2026-75128 | Langchain-Chatchat, through 0.3.1.3 | `POST /tools/call` | The endpoint invokes any registered tool by name **without authentication**, and a shell tool is always registered. One request naming it executes arbitrary OS commands as the server user — root in the shipped Docker image. |
| CVE-2026-77932 | DB-GPT, through 0.8.2 | `POST /api/v1/chat/react-agent` | The endpoint's `get_user_from_headers` is a mock that **grants every caller the admin role**. Prompts drive the ReAct agent's unsandboxed `code_interpreter` and `shell_interpreter` tools to run arbitrary Python/bash as root in the webserver container. (Adjacent: CVE-2026-77933 — hardcoded MySQL root password in the same product's default compose file.) |
| CVE-2026-109442 | piflow 2.0.0 – 2.0.1 | `POST /chat`, `POST /chat/stream` | The DeepAgents chat endpoints **lack authentication**. Attackers instruct the agent to call the `exec_shell` tool, which runs commands via `subprocess.run` with no human approval and no allow-list — exposing environment secrets (LLM API keys, database credentials). |
| CVE-2026-109437 | Cognition, before 0.13.0 | `POST /sessions`, `POST /sessions/{id}/messages` | The agent sandbox backend **defaults to local execution** and the REST/SSE API ships **no authentication**. Creating a session and posting a message runs attacker-directed shell commands through the local shell backend as the server process. **Fixed in 0.13.0.** |

- **The shared pattern:** the feature that makes an agent useful — a
  tool that runs shell commands or code — is exposed on an HTTP
  endpoint with no authentication in front of it. The "exploit" is one
  ordinary API request; there is no malformed input to signature.
- **Why this keeps happening:** these frameworks are built demo-first.
  Auth is a deployment option (an env flag in Letta's case) rather
  than a default, the sandbox is a config value rather than an
  enforced boundary, and the shipped Docker/compose files optimize
  for "runs on first try" — as root.
- **Blast radius is the host, not the app:** code executes as the
  server user, and agent processes typically hold the keys to
  everything else — LLM API keys, database credentials, mounted
  cloud metadata. Treat a hit as host compromise until cleared.
- **Fixes / mitigations:** upgrade where a fixed release exists
  (Cognition ≥ 0.13.0). Everywhere else the durable fix is
  architectural: put authentication in front of the agent API (the
  framework's own mechanism, e.g. enabling `LETTA_SERVER_SECURE`, or
  an authenticated reverse proxy), never expose agent ports directly,
  run the agent process unprivileged, and sandbox the shell/code
  tools or remove them from the tool registry.

## 1. Mechanics

There is no memory corruption and no input-validation failure to
study — the vulnerability is an **absent control**. The request that
exploits Letta's tools endpoint is byte-for-byte the request the
product's own client sends; it simply arrives without credentials,
from anywhere on the network, because the server never asks for any.

That shapes the whole detection problem:

- Payload inspection still earns its keep — attackers ask the tool
  to do attacker things (`os.system`, `curl … | sh`, `cat
  /etc/passwd`, `printenv`) — but a patient attacker can phrase
  commands the payload markers won't catch.
- The invariant signal is the **combination**: a tool-execution
  endpoint + no credentials presented + (payload markers or a
  successful, repeated session flow). Any one leg alone is weak
  evidence; the three together are the CVE firing.
- Stock access logs cannot see the middle leg. You need a proxy/WAF
  log that records whether any credential was presented
  (`Authorization`/cookie presence) and a body excerpt — the same
  header-enrichment lesson as the Ivanti lab.

## 2. Hunt markers (use these, in order)

1. **POST to a known agent tool-execution endpoint** — `/v1/tools/run`
   (Letta), `/tools/call` (Langchain-Chatchat),
   `/api/v1/chat/react-agent` (DB-GPT), `/chat` + `/chat/stream`
   (piflow), `/sessions` + `/sessions/{id}/messages` (Cognition).
   Enumerate the equivalent routes for whatever agent framework you
   actually run; the class matters more than this list.
2. **No credential presented** (`auth=none` in the enriched log) on
   any request from marker 1. On a correctly deployed instance this
   combination should not exist at all.
3. **Shell/code payload markers in the body** — shell/code-interpreter
   tool names (`shell`, `exec_shell`, `code_interpreter`,
   `shell_interpreter`) or OS-command plumbing (`os.system`,
   `subprocess`, `$(…)`, `curl … | sh`, `cat /etc/passwd`,
   `printenv`, `/dev/tcp/`).
4. **2xx responses to marker-1 requests** — the call was accepted.
   Combined with 2+3 it separates exploitation from probing.
5. **Bursts** — ≥3 endpoint hits from one source inside 10 minutes:
   scanners working through a framework fingerprint set, or the
   session-create → message flow that drives session-based agents.

## 3. Triage decision tree

- Markers (1)+(2)+(3) from one source → incident: the CVE pattern,
  weaponized. Isolate the host, preserve process/memory state before
  restart, and rotate **everything the agent process could read** —
  LLM API keys, database credentials, cloud tokens in its
  environment. Review the agent's own tool-call history for what
  else it was asked to do.
- Markers (1)+(2)+(4)+(5) without (3) → incident: an unauthenticated
  session flow ran repeatedly; assume commands ran even if your
  payload markers didn't fire (attackers phrase around wordlists).
- Marker (1)+(2) alone → suspicious: probing or a mis-deployed
  internal client. Identify the source; if it isn't yours, the
  instance is internet-visible and unauthenticated — that is the
  finding, fix the exposure first.
- Marker (1)+(3) **with** credentials → suspicious, different shape:
  an authenticated caller driving the shell tool from an unusual
  source — stolen token, insider, or a compromised upstream app.
  Pull that identity's full tool-call history.
- Endpoint hits from your allowlisted application server, with
  credentials → expected. That traffic *is* the product; your
  detection budget belongs on everything else.

## 4. Lab exercises (do them yourself)

1. Run `agent-tool-unauth-rce-detect.py` against
   `samples/agent-tool-unauth-rce-access.log`; confirm it flags the
   five-request attack source (INCIDENT, all five markers), both
   partial sources (SUSPICIOUS — one unauthenticated with no payload
   evidence, one authenticated shell-tool call), and none of the
   benign traffic including the allowlisted app server's own tool
   calls (FP=0).
2. The detector's endpoint list covers five frameworks. Pick any
   other agent framework, find its tool-execution or chat routes from
   its public docs/source, and add the patterns. Write down what you
   used as evidence for each route — guessing URLs is how detection
   rules rot.
3. Write the incident report for the INCIDENT source: timeline
   across all five endpoint hits, why the blast radius is "the host
   and every secret the agent process holds" rather than "the app",
   and the exposure fix you would verify (auth in front of the API,
   agent ports not publicly bound) before closing.

## Honest limitations

- **Enrichment is a prerequisite, not a nicety.** A plain access log
  shows endpoint + status only: markers 1, 4, 5 survive, the decisive
  marker 2 (no credential presented) does not. The detector scores
  what the log gives it and the card's verdicts assume the enriched
  format documented at the top of the script.
- **Endpoint lists age fast.** These are the routes named in the
  2026-10-20 NVD entries. Frameworks rename routes between minor
  versions, and `/chat`-style paths collide with unrelated products
  — run this detector against logs of hosts that actually run agent
  frameworks, not the whole estate.
- **Payload markers are a wordlist.** They catch the noisy,
  script-driven exploitation these CVEs invite on day one. A
  targeted attacker who phrases commands innocuously still trips
  markers 1+2+4 — which is why the no-auth leg, not the wordlist,
  carries the verdict.
- No live vulnerable instance in this lab — detection runs on the
  synthetic enriched log only.
