# VetAlign-AI | India-Focused Hackathon Blueprint & Delivery Plan

**Working identity:** VetAlign-AI — सैन्य अनुभव से नागरिक करियर तक  
**Competition:** Be10X Build for Good · Solo · One project, one track  
**Selected track:** **Track 3 — Product Build**, confirmed by the participant on 27 September 2026. Deliver a publicly accessible, voice-first Streamlit web product; do not switch to the AI Agent track or rebuild around the template's illustrative tools.  
**Approved idea:** #09 — Ex-servicemen skill matcher  
**Deadline:** **4 October 2026**, confirmed by the organisers through the participant. The handbook's main timeline states 11:59 PM; confirm the time zone separately. Its older September FAQ dates do not govern this plan.  
**Working budget:** 2–3 hours daily, 27 September–4 October: approximately 16–24 hours.  
**Revision:** 27 September 2026 — reconciled against the complete project-template screenshots supplied by the participant.  
**Baseline:** `checkpoints/checkpoint-1/` preserves the approved bilingual three-step design. Do not edit this snapshot. No Checkpoint 2 is created by this planning revision.  
**Scope:** Voice-first input → reviewed civilian profile → matching against specific job records → usable output. Video planning is included now that the participant has supplied the full submission guidance; recording remains pending.

## Source Decisions and Unresolved Rule Conflicts

The complete template is stronger evidence of the intended **functional outcome** than the earlier short idea description. It explicitly says “Voice first”, matching against a list of open roles, and testing Hindi or Marathi voice input. Our previous text-first scope was therefore incomplete.

| Topic | Sources supplied | Planning decision |
| :--- | :--- | :--- |
| Deadline | Participant confirms organisers said 4 October 2026; older FAQ contains September dates. | Use **4 October 2026**. Confirm time zone for the handbook's 11:59 PM cutoff. |
| Judging | Handbook/earlier screenshot: 25/30/20/15/10. Complete template: 40/25/20/15. | Track the newer template weights provisionally; ask which rubric governs the final submission. Do not merge them into a fictitious combined score. |
| Video | Complete template: **3 minutes**. Handbook: both 3–5 and 5–10 minutes. | Prepare a three-minute master following the supplied template. Confirm final duration before recording/submitting; do not assume the conflict is resolved. |
| Written submission | Template: one page. Handbook: 1–3 pages. | Prepare a **one-page** explainer, which fits both ranges, plus private supporting test notes. |
| Submission mechanism | Template lists working link/video/one page; handbook specifies Drive and Google Form. | Retain Drive sharing and Form submission unless organisers replace that mechanism. |
| Track and tools | Idea #09 is labelled AI Agent in the template; participant has selected Track 3 and confirms tools are unrestricted. | **Track 3 — Product Build** is the project decision. Keep Streamlit and reproduce the voice-to-profile/job-matching outcome; Telegram/n8n/Docs/Sheets are not mandatory. |

**Immediate organiser questions:** Which judging weights apply? Is the recording exactly three minutes or another range? What is the deadline time zone? These questions need not block implementation. The participant's track choice is settled: **Track 3 — Product Build**.

---

## 1. Re-evaluation: Keep the Lean Stack, Change the Priorities

The Streamlit + Gemini direction and Checkpoint 1 design remain suitable for a solo hackathon. Stop additional cosmetic redesign. The current implementation has Indian examples and bilingual screens, but it is **text-first and suggests generic role families**, rather than accepting a voice note and matching specific job listings. Live end-to-end behaviour has not yet been verified.

The revised priority is:

> Help a retiring or retired Indian service member describe non-sensitive experience by voice in Hindi or Marathi, review the transcript, and receive a civilian application profile plus up to three relevant jobs from a maintained list, with evidence-based reasons and source-provided application routes.

### Competition alignment

| Criterion | Weight | What this project must demonstrate |
| :--- | :--- | :--- |
| Real-world usefulness | 40 | A specific beneficiary, actual feedback where available, and a usable voice-to-profile/job-shortlist outcome. |
| Working demo | 25 | Live input through transcription, reviewed profile, sourced matches and download; not screenshots or cached output disguised as live generation. |
| Three-minute pitch | 20 | Problem, beneficiary, live workflow, limitations and next step, in that order. Duration provisional pending clarification. |
| Sustainability next month | 15 | Free-first operation, maintainable job list, documented limits, and a simple handover a non-technical helper can follow. |
| Real-user bonus | Up to +5 | Actual testing with an affected person or relevant NGO, with consent and honest reporting. Do not claim testing before it occurs. |

Fancy UI, complex architecture and tool choice receive no direct marks. Use modest branding; spend the saved time on correctness, deployment and user feedback. No score or prize is guaranteed.

The older rubric still rewards the same useful work: document the specific problem, why semantic interpretation needs AI, measured benefit, end-to-end execution and clear explanation. Both sources include privacy/human-approval penalties. The optional brand video is deferred until every core requirement is met; bonus wording differs between sources.

---

## 2. Indian Beneficiary and Problem Definition

### Initial beneficiary

An Indian ex-serviceman preparing an early civilian job application, starting with **Army logistics, stores, transport or maintenance experience**. The broader interface can include Indian Army, Indian Navy and Indian Air Force, but the first validation should stay narrow.

Seek feedback from one willing ex-serviceman, a veteran-support volunteer, or a resettlement counsellor. A Zila Sainik Welfare Office or ex-servicemen association is a possible outreach route, **not an assumed partner or endorsement**.

### Pain to validate, not assume

- Service duties are expressed in terminology civilian recruiters may not understand.
- Applicants may struggle to identify suitable roles and describe transferable skills.
- Generic AI writing may inflate seniority, invent achievements or overlook qualification gaps.
- Paid assistance or repeated manual rewriting may be burdensome; establish actual time/cost with a tester rather than inventing statistics.

### Product positioning

**An application-preparation assistant, not a recruitment authority.** It suggests roles and drafts materials. It does not certify equivalence, guarantee employment, make hiring decisions, determine pension eligibility, or provide legal/financial advice.

### Localisation rules

- Retain the Indian service context already introduced; do not reintroduce US pay grades or evaluation terminology.
- Use service/trade, rank, years served, duties, responsibilities, education and user-declared certifications. Optional fields must not block a useful first draft.
- Use Indian English, ₹ and Indian number formatting where relevant. Preserve supplied amounts; never fabricate salary or asset values.
- Keep the existing English/हिन्दी UI toggle and show one interface language at a time. Preserve the English tagline **“From service experience to a civilian career”** and its Hindi counterpart only when Hindi is selected.
- Voice-input language is independent of interface language. Prioritise Hindi and mixed Hindi/English; test Marathi voice as the next language before claiming support. The template explicitly asks for a Hindi **or** Marathi voice test. Do not delay the core Hindi journey for an unvalidated Marathi UI.
- Keep the application draft in professional English, with selected-language explanations and an editable transcript. Never infer language support merely from a model's advertised capabilities.
- Treat rank and trade as context, not an automatic corporate designation. A Havildar is not automatically a manager; a senior service rank is not proof of director-level civilian suitability.
- Do not infer caste, religion, disability, age, medical fitness or security clearance from rank, name or branch.

---

## 3. MVP: One Reliable End-to-End Journey

Preserve the approved three-step wizard and hero panel. Add capability within those steps, not another dashboard redesign.

### Step 1 — Speak, review and consent

- Make **Record your experience** the primary input using Streamlit's native audio input if supported by the tested version; allow an audio-file upload and typed text as fallbacks.
- Start with a 30–90-second recording in Hindi or mixed Hindi/English. Initial limits: two minutes and 10 MB, enforced server-side; verify compatible MIME types with the selected SDK/model. Support browser-recorded WAV first; Telegram-specific OGA support is unnecessary for the web MVP.
- Obtain consent **before any audio is uploaded to Gemini**, not after transcription. Explain cloud processing, warn against identifiers/restricted information, and avoid claims of local-only or guaranteed confidential processing.
- Show the transcript for correction. Ask the user to approve it before profile generation. Silence, noise or unclear content must prompt re-recording, not invented service details.
- Extract service, rank, years and duties into editable fields. Keep optional education/certifications; ask only for missing useful information rather than requiring the veteran to retype the recording.
- Add optional **preferred work city/district** and relocation preference, not home address or military posting. Keep target role separate from a pasted job description.
- Keep the four fictional profiles and add fictional voice samples recorded with permission. Never request discharge papers, Aadhaar/PAN, service numbers, medical records or operational documents.

### Step 2 — Skills and specific job matches

- Show source duty → transferable skill → civilian wording with source references.
- Build a structured, reviewable profile: years, rank, preferred work location, civilian skills, short civilian headline and three-sentence summary. Unknown facts stay unknown; keep the actual service rank in experience history.
- Compare skills and preferences against a **small maintained set of specific job records**, not merely six broad role-family descriptions.
- Return **up to three** relevant records with title, employer, location, supported requirements, clarification gaps, one concise matching reason, and a source-provided application URL or public business contact.
- Copy employer/location/contact/link fields from records in code; never ask the model to invent them. If only one or two plausible matches exist, show that number and explain. Zero matches is a valid result.
- Label sample vacancies explicitly as fictional. For real listings show source and last-checked date; never claim a stale or unverified listing is currently open.
- Preserve useful charts, but label them counts of extracted evidence rather than confidence, employability or match percentages. Additional charts are not a priority.

### Step 3 — Review, download and act

- Present a concise, one-page-style civilian profile plus the job shortlist with reasons and application routes. User edits and reviews before use; the app does not send applications or contact employers.
- Retain TXT/Markdown downloads and add the shortlist to the downloadable pack. The template explicitly allows sending text; PDF is a usability enhancement after the required flow works, not a blocker. Use a tested font/renderer if PDF is added.
- Keep existing interview preparation as secondary functionality; defer expanding it if it threatens voice/matching/testing delivery.
- Preserve inputs, consent, transcripts, matches and edited drafts across wizard navigation and language switches. Changed source data must invalidate downstream output/review state.
- Clear audio references after transcription when no longer needed; never intentionally retain recordings or transcripts in logs. Session clearing cannot delete provider-retained copies or downloaded files.

### In scope versus deferred

**Core:** Hindi voice input, transcription review, text fallback, structured profile, grounded job matching, usable text output, human control, a hosted working app and tested error handling.

**Next if time permits:** verified Marathi voice support, PDF export, Google Sheets as a maintainable job source, more languages and broader job coverage.

**Deferred:** Telegram delivery, n8n, Google Docs automation, employer submission forms, weekly digests, accounts, job-board scraping, vector databases, auto-applications, pensions and unrelated document OCR. The supplied Telegram/n8n recipe is an implementation option; recreating it alongside the working browser app would double integration risk without improving the core outcome.

---

## 4. Respectful Indian Visual Identity

Use national identity to orient the user, not to imply government ownership.

| Placement | Planned treatment |
| :--- | :--- |
| App header | Preserve the approved gradient hero, Indian flag and tagline. Show English or Hindi text according to the selected UI language, not both simultaneously. Keep the full flag uncropped and unobscured. |
| Theme | Restrained saffron and green accents on an off-white background, with navy text and accessible contrast. Never use colour alone to communicate status. |
| Branch selector | Text labels and neutral, original icons for land, maritime and aviation experience. These are navigation symbols, not official service badges. |
| Product mark | An original skills-to-career symbol that is distinct from official military and government insignia. |
| Footer | “Independent career-support prototype. Not affiliated with or endorsed by the Government of India or the Indian Armed Forces.” |
| Application exports | Plain professional text. Omit flags, national emblems and decorative service imagery from the applicant's draft. |

### Flag and emblem safeguards

- Before publishing a flag asset, verify its provenance, usage permissions and current official guidance under the Flag Code of India and applicable laws. Prefer an accurate static asset over a distorted or recoloured rendering.
- Preserve the flag's 3:2 proportions, saffron/white/green order and centred navy-blue 24-spoke Ashoka Chakra. Do not animate, overlay text on, or use the flag as a button, progress bar or full-page decoration.
- **Do not include the State Emblem of India/Lion Capital, government seals, official service crests or rank insignia in the MVP without verified permission and applicable usage compliance.** Availability online is not permission to reuse.
- A disclaimer does not substitute for permission. Default to the flag, subject to verified guidance, and original non-official icons; omit any asset whose permitted use is unclear.
- Cap initial branding work at approximately 30–45 minutes. Accessibility and usability take precedence over decoration.

---

## 5. Lean Architecture

Streamlit provides the browser UI and server-side Python logic in one deployment. The Gemini model remains an **external service**; a virtual environment is dependency isolation, not a container or privacy boundary.

```text
Browser: consent -> voice recording/upload OR typed fallback
    |
    v
Server: audio size/type/duration checks -> Gemini transcription
    |
    v
User reviews transcript -> approves numbered source facts
    |
    v
Gemini: structured civilian profile -> schema/evidence validation
    |
    v
Local matcher: load jobs -> normalise skills -> shortlist candidates
    |
    v
Gemini: semantic comparison of supplied candidate job IDs only
    |
    v
Server: validate IDs -> attach original job details/links -> up to 3 matches
    |
    v
User review -> editable profile + shortlist -> TXT/Markdown export
```

### Model calls and latency budget

Use separate stages for transcription, profile extraction and grounded matching. A normal voice journey initially requires up to **three** model requests; typed input skips transcription. This is justified by the template's audio-to-structure-to-match workflow and the transcript review boundary.

Keep the approved transcript/profile as the source of truth; do not feed an embellished résumé back as unverified evidence. A strict job-ID contract keeps the model from manufacturing vacancies. Consider combining profile generation and matching only after correctness and latency testing demonstrate that it helps. Never cache private content across users.

### Structured output contract

Use a validated schema containing:

- `skills`: civilian skill, source fact IDs and explanation.
- `matches`: supplied `job_id`, supported skill/source references, gaps and a concise reason; employer, location, contact and links are attached from the job source, not generated.
- `job_requirement_checks`: optional requirement-to-evidence comparisons.
- `profile`: summary, competencies and experience bullets with evidence references.
- `interview`: questions and answer outlines grounded in source facts.
- `warnings`: ambiguity, unsupported requests and information needing review.

Render structured data into Markdown in application code. Source IDs and number checks help detect errors but **do not prove semantic correctness**; retain human review.

### Apply the template's five prompting rules

1. **Role:** an Indian ex-servicemen career assistant, not a hiring or qualification authority.
2. **Exact output:** typed JSON with defined fields/enums; validate nested structures in code rather than relying on “JSON only”.
3. **One example:** include a small fictional input/output pair showing stores duties → inventory skills and source references, without adding credentials or performance figures.
4. **Prohibitions:** never invent facts, vacancies, contacts or licences; uncertain transcription requires clarification. Do not force six skills or three matches from inadequate evidence.
5. **Named language:** explicitly request Hindi or Marathi where applicable; keep the reviewed application profile in English unless the user explicitly chooses otherwise.

Separate system instructions from transcript/job-description data. Treat retrieved job text as untrusted input too. A prompt is a safeguard, not a substitute for ID validation, safe rendering and human review.

### Job data and matching strategy

Start with **10–15 curated records** across stores/warehouse, transport/fleet, maintenance, security operations and IT/telecom support, covering the three template test cases. Keep role-family descriptions only as explanatory reference.

Record schema: `job_id`, `title`, `employer`, `required_skills`, `preferred_skills`, `qualification_requirements`, `city_or_district`, `application_url`, optional public business `contact`, `source_url`, `last_checked`, `status`, and `is_demo`.

- Use fictional records during development/public demos. A separately labelled real-listing dataset should contain only records from permitted public sources or consenting partner employers; verify before claiming any vacancy is open. Record acquisition is a real delivery dependency, not an assumed integration.
- Never mix fictional jobs with real jobs without visible labels. Public demo contacts must be dummy; real-user mode can link to an employer's official application page without exposing a personal recruiter's phone number.
- Start with local JSON/CSV. Allow a non-technical helper to maintain a spreadsheet and export CSV; direct Google Sheets integration is optional. No paid jobs API or scraping is required.
- Normalize common equivalents, e.g. stores → inventory management, convoy coordination → fleet logistics, training jawans → team training, signals → telecom support. These are contextual candidates, not proof of every associated qualification.
- Use skill overlap and stated location preferences to shortlist; apply semantic comparison to supplied records. Unstated location/qualification is a clarification need, not grounds for inventing eligibility or silently excluding the person.
- Reject unknown/duplicate job IDs; retain original links and contacts. Validate external URL schemes and render safe links. Handle a missing/empty/stale dataset without making up replacements.
- For sustainability, document who would update the list, a proposed weekly review, how records expire and how to disable obsolete entries. Name a real maintainer only once someone has agreed.

### Minimal operational logging

The template appends a Google Sheet row; its purpose is operational traceability, not compulsory storage of veteran narratives. For the web MVP, record only an event ID, time, stage, outcome, duration and aggregate match count where needed. Do not log raw audio, transcripts, names, contacts or detailed profiles. An optional restricted sheet can hold the same non-identifying events; never share it publicly. Hosting/provider retention remains a separate disclosure.

---

## 6. Technical Corrections and Reliability

### Current implementation audit — static inspection, not live validation

**Already present:** supported `google.genai` import, configurable model (default `gemini-2.5-flash`), bilingual three-step UI, fictional Indian profiles, session-held results, draft downloads, charts, basic JSON/reference checks, `requirements.txt`, ignore rules and light-theme config. Model availability and live generation are still unverified. Do not reopen these as entirely unimplemented tasks.

**Fix before adding more UI:**

1. Separate durable application data from widget keys. Widgets disappear between wizard steps; Streamlit cleanup can erase input or edited-draft state. Test forward/back and language changes.
2. Move sample loading/reset into callbacks that run before widget creation. Current quick-profile buttons mutate already-rendered widget keys; inline Start over can do the same for the draft.
3. Give API/model fields stable keys across translated labels. Include language, source inputs and job-data version in output invalidation. Do not expose the app's server key in the UI.
4. Resolve hidden `target_role` versus visible `job_description` values: sample selection must not leave a conflicting hidden target.
5. Replace partial dictionary checks with typed nested schema validation. Invalid types, missing properties, booleans used as source IDs and unknown job IDs must fail safely before rendering.
6. Escape generated text in HTML cards, or render it with safe native widgets. Do not interpolate untrusted output into raw HTML.
7. Replace “nothing has been invented” with a review reminder. Source references support checking but do not certify truthfulness. Remove error guidance referring to Sample mode until an actual labelled offline-output mode exists.

These are code-review findings to reproduce and test, not claims of observed failures in a browser. HTTP 200 only confirms the server responds; it does **not** prove Streamlit widget execution or live Gemini output succeeds.

### Stack and configuration

| Component | Decision |
| :--- | :--- |
| Runtime | Prefer a tested Python 3.11 or 3.12 environment supported by the chosen dependencies and host. The existing Python 3.9 environment is not the deployment baseline. |
| UI/server | Streamlit; no separate API server needed. |
| AI SDK | `google-genai`, with a verified configurable model identifier. |
| Validation | Pydantic for typed response validation; declare it explicitly if imported directly. |
| Testing | Standard-library unit tests for pure logic plus Streamlit AppTest where practical and manual cloud checks. |
| Hosting | Streamlit Community Cloud, subject to current availability and limits. |
| Dependencies | Pin versions actually tested together in `requirements.txt`; match local and cloud Python versions. |

### Free-first tool choices

| Need | First choice | Cost/operational guardrail |
| :--- | :--- | :--- |
| Browser app and recording | Existing Streamlit app and native audio component | Validate installed-version/browser support; HTTPS required for hosted microphone use. |
| Transcription and semantic work | Google Gen AI SDK with a tested audio-capable model | Confirm free-tier eligibility, model availability, quotas and provider data terms. No paid upgrade without explicit approval. |
| Job source | Local CSV/JSON; optional Google Sheet | No paid job feed; human source/freshness verification remains necessary. |
| Export | Existing TXT/Markdown; optional local PDF library | No paid document-conversion API. |
| Hosting | Streamlit Community Cloud if suitable | Verify current limits and supported repository access. A public app is required; public source code is not established as a competition requirement. |
| Screen recording | macOS recorder or OBS | Free; no paid brand-video work until core acceptance tests pass. |
| Optional messaging | Telegram/n8n only if a validated user need requires it | Trials expire; do not add a second delivery channel during the core build. |

Use app-owner secrets so a veteran does not need an AI Studio account. Keep developer key entry under optional settings during local work. Provider/project quota controls and input/output limits must be in place before public access; session cooldown alone is insufficient abuse protection.

### Key handling and public access

- Configure the app-owned API key through deployment secrets or server environment variables. Ordinary beneficiaries should not need to obtain a developer key.
- Never put keys in source, browser content, downloads, screenshots or logs. Ignore `.streamlit/secrets.toml`, `.env`, virtual environments and local caches.
- Apply input/output limits, a session cooldown and provider/project quota controls where available. A session cooldown alone is **not** robust public abuse protection.
- Check provider data-use/retention terms before inviting real inputs. Do not promise confidential processing or zero retention without verification.
- If safe public live access cannot be supported within quota, expose a clearly labelled sample experience and disclose the live-access limitation rather than claiming unrestricted availability.

### Failure handling

- Reject whitespace-only required input and cap narrative/job-description size; initial combined limit: 8,000 characters, adjustable after testing.
- Treat user narratives and job descriptions as data, not instructions; keep behavioural rules in the system instruction.
- Handle missing key, invalid key, unavailable model, quota exhaustion, network timeout, empty/blocked response and invalid schema separately with safe messages.
- Use a bounded request timeout, initially around 60 seconds, and at most one bounded retry for eligible transient failures. Honour provider retry guidance; do not retry invalid keys or exhausted daily quota automatically.
- Keep valid previous output on failure, labelled with its input/version. Never present incomplete or invalid output as success.
- Provide pre-generated, fictional sample outputs for outage demonstrations, labelled **“Sample output — not generated live.”** Never silently switch from live generation to a canned result.
- Do not cache API clients containing user-specific credentials or private results globally. Make no claim of persistence across browser closure, server restart or session expiry.

### Honest cost and performance targets

Aim to remain within free-tier allowances; **₹0 cost is an operating target, not a guarantee**. Verify quotas and avoid enabling paid usage unintentionally. There is no guaranteed two-minute deployment or sub-three-second generation.

Initial target: most tested individual model requests complete within 30 seconds. Track transcription, extraction and matching separately; initial total automated-processing budget is 90 seconds, excluding recording and human review. These are targets, not achieved measurements. Bound each call and the complete workflow, show stage progress, and provide actionable timeout handling.

---

## 7. Truthfulness, Privacy and Human Control

1. **Evidence first:** Every achievement must come from the supplied narrative. Never add degrees, certifications, civilian employers, salary history, metrics or proficiency claims.
2. **No false equivalence:** Military maintenance experience does not automatically confer a civilian aviation licence; service leadership does not automatically satisfy corporate management requirements.
3. **Separate unknown from absent:** “Not evidenced in the provided information” is different from “the applicant does not have this skill.” Ask for clarification.
4. **Sensitive-input prevention:** Display a warning not to paste personal identifiers, unit locations, equipment readiness, classified material or other restricted operational details. Any identifier detection is best-effort, not a guarantee of sanitisation.
5. **No raw-content logging:** Avoid storing prompts and generated profiles in application logs or a database. Log only minimal operational metadata where necessary.
6. **Human review:** Users edit and approve their own draft. Role recommendations are advisory, not a decision on employability or rights.
7. **Demo safety:** Use fictional people and generic duties throughout public examples and submission materials. Do not expose beneficiary identities when reporting feedback.
8. **Honest validation:** With consent, describe a real tester's role or organisation only as permitted by competition privacy rules. Seek organiser clarification if bonus attribution conflicts with the dummy-data requirement.

---

## 8. Fictional Indian Demo Scenarios

All sample quantities below are invented solely for testing, not real service records. Use no named units, bases, platforms or identifying details. Have a knowledgeable reviewer check terminology if available.

| Sample | Non-sensitive illustrative experience | Civilian direction | Check |
| :--- | :--- | :--- | :--- |
| Indian Army — Havildar, stores/logistics duties | Supervised 12 personnel, maintained stock records and coordinated dispatches; no civilian software certification supplied. | Warehouse/stores supervisor or logistics coordinator | Preserve team size; do not invent SAP experience or a business degree. |
| Indian Navy — Petty Officer, technical maintenance duties | Planned routine equipment checks, maintained fault logs and coordinated a six-person maintenance team. | Maintenance coordinator or technical support supervisor | Do not invent civilian licences, networking certifications or equipment uptime. |
| Indian Air Force — Sergeant, maintenance-support duties | Coordinated shift handovers, tools and maintenance documentation for eight technicians. | Maintenance planning assistant or operations coordinator | Do not claim DGCA licensing or automatic engineer/manager equivalence. |

Reuse the existing Hindi/mixed-language Army sample and add a corresponding fictional voice fixture. Test an ambiguous abbreviation that the model should ask about instead of confidently expanding.

### Template's three required scenarios

1. **Hindi voice: stores and transport.** A fictional speaker describes years served, stock duties, transport coordination and training a stated number of personnel. Expect a logistics-focused civilian profile and three relevant jobs **when the test dataset contains three suitable records**; preserve every quantity.
2. **Voice: signals experience.** Describe equipment troubleshooting, communications support and maintenance records. Expect plausible IT/telecom skill mapping, not invented network certifications or claims of software expertise. Add this fixture; the existing maintenance profiles do not fully cover it.
3. **Empty/unclear audio.** Silence, corrupted upload or unintelligible speech must trigger a helpful request to record again or type instead. Do not generate a fictitious profile or match jobs from noise.

Use at least one Hindi voice test; add Marathi voice verification if time permits. Record audio-consent, transcript corrections and grounded output checks for each test, without publishing the speaker's identity.

---

## 9. Delivery Schedule: 27 September–4 October 2026

The 16–24-hour calendar budget includes work already spent on Checkpoint 1; it is **not all remaining time**. Treat the dates below as target windows and revise against actual time logged. Freeze the visual design and reuse current code. The participant is the solo implementer; organiser clarification, willing testers and job sources are external dependencies.

| Phase / target | Time box | Work package | Exit gate and evidence | Initial status |
| :--- | :--- | :--- | :--- | :--- |
| P0 · 27 Sep | Remaining time today | Reconcile template, preserve Checkpoint 1, ask rule questions, seek one tester and a job source. | Revised scope agreed; unresolved questions recorded; no unverified user/partner claims. | Plan updated; outreach/confirmation pending. |
| P1 · 28 Sep | 2–3 h | Fix sample/reset/navigation state; strict response validation and safe rendering; test an actual Gemini request. | AppTest/mock checks pass for forward/back/language/reset; one reviewed live text output. | **Done (state + live call).** Safe rendering and nested validation still outstanding. |
| P2 · 29 Sep | 2–3 h | Add consent-before-upload recording, transcription, transcript review and text fallback; deploy an early slice. | Hindi voice survives the full input/review flow on local and hosted browser; silence handled safely. | **Implemented / live acceptance pending (1 Oct).** WAV capture/upload, consent, reviewed transcription and text fallback tested offline; actual Hindi speech/browser/hosting checks pending. |
| P3 · 30 Sep | 2–3 h | Define job-record schema, curate 10–15 fictional/source-backed records and implement grounded shortlist/ranking. | Top three from supplied IDs where appropriate; no-match path works; links/contacts copied exactly. | **Data layer done** (13 records, `jobs.py`, 22 tests). Matching not yet wired to the UI. |
| P4 · 1 Oct | 2–3 h | Connect voice → profile → jobs → downloadable pack; secure hosted key handling; verify public access. | One complete live journey on another device/network; edited draft survives navigation/download. | Not started. |
| P5 · 2 Oct | 2–3 h | Run the three template tests; quota/failure/privacy checks; seek real-user feedback; measure review-inclusive completion time. | Test results and limitations recorded; major defects fixed; feedback honestly attributed. | Not started. |
| P6 · 3 Oct | 2–3 h | Freeze features; write one-page explainer and operator instructions; rehearse and record the provisional three-minute video. | Working app link, clear recording, Drive files and drafted form answers; duration confirmed or conflict escalated. | Not started. |
| P7 · 4 Oct | 2–3 h buffer | Retest links, dataset freshness, quotas and permissions; submit and retain confirmation. | Full official checklist reconciled; form confirmation captured before cutoff. | Not started. |

If a phase overruns, reduce optional functionality rather than silently claim completion. If strict three-minute live timing is impractical, measure the bottleneck and shorten inputs/output scope; do not fake processing or hide edited-out waiting as a one-take demonstration.

### Scope-cut order if behind

1. Defer extra graphics, additional charts, brand video, voice playback and expanded interview coaching.
2. Defer Telegram/n8n/Docs integration, automated Sheets sync, PDF/DOCX and Marathi UI. Use text output and CSV-based job maintenance.
3. Narrow job coverage and focus on validated Hindi audio, while clearly disclosing language/geographic limits.
4. **Do not cut:** voice-first Hindi acceptance, transcript review, specific sourced/demo-labelled job matching, truthful outputs, public live operation, human control or mandatory submission materials.

### Progress register — update after every implementation session

Status meanings: **Implemented / unverified** = present in source, not accepted; **Verified** = acceptance evidence recorded; **Not started** = no implementation; **Needs fix** = static audit finding awaiting reproduction/fix. Record date, test method, result and remaining limitation before changing a row to Verified.

| ID | Deliverable | Current status | Evidence / next action |
| :--- | :--- | :--- | :--- |
| D01 | Approved light wizard, hero and English/हिन्दी selection | **Verified** | 28 Sep: 25 AppTest cases cover navigation, language switch, reset. Checkpoint 2. |
| D02 | Gemini text generation, draft export, basic charts | **Verified** | 28 Sep: live call, 28.8 s, 12 facts → 7 skills / 3 roles; quantities preserved, SAP/WMS held as a gap. |
| D03 | Safe wizard persistence, quick samples, reset and target handling | **Verified** | 28 Sep: durable/widget state split; loss-on-navigation reproduced then fixed; `target_role` removed. |
| D04 | Typed validation, escaped output and honest safety copy | Partially implemented | 1 Oct: generated HTML card values escaped; absolute truthfulness copy replaced with review reminders; transcription schema strictly validated. Existing career-generation nested schema validation remains outstanding. |
| D05 | Consent-first audio and reviewed transcription | **Implemented / live acceptance pending** | 1 Oct: `audio_service.py`; bilingual consent-before-capture, WAV recording/upload, explicit single bounded transcription request, transcript/background approval and typed fallback. Synthetic WAV + mocked AppTest checks pass; no real Hindi recording, live audio API request or microphone-denial/mobile test performed. |
| D06 | Job dataset, provenance, freshness and maintenance route | **Implemented / verified by tests** | 28 Sep: `data/jobs_demo.json`, 13 fictional records on `.invalid` domain; `jobs.py` validates schema, URL schemes, staleness, duplicate IDs; 22 tests. |
| D07 | Skill-based matching of supplied job IDs with reasons | **Implemented / live acceptance pending** | 3 Oct: matching folded into the single generation request (no third call). Prompt carries the template's mapping table and a match-by-skills rule; only open, current job IDs are offered, without employer/links. `_resolve_matches` drops unknown/closed/duplicate IDs and matches lacking a valid source fact, caps at 3, copies employer/location/link/contact from the record. Step 2 shows match cards with demo label; zero matches shown honestly. 21 new tests. No live model output reviewed yet (sandbox blocks API). |
| D08 | Combined profile + job shortlist text export | **Implemented / unverified live** | 3 Oct: Step 3 primary download = edited profile + `shortlist_markdown` (reason, gaps, employer requirements, apply link, contact, last-checked, FICTIONAL label). |
| D09 | Public hosting, secrets and bounded usage | Partially implemented / hosting unverified | 1 Oct: server key no longer seeds browser password widget; transcription has 60-second request timeout, SDK retries disabled and a 10-second session cooldown. Provider quotas/terms, total workflow bounds, hosted HTTPS microphone and public/external-device tests remain pending. Session cooldown is not robust abuse protection. |
| D10 | Template tests and actual beneficiary feedback | Not started | No real-user testing or measured impact recorded. |
| D11 | Video, one-page explainer, handover and submission | Not started | Track 3 selected; confirm duration/rubric and prepare by 3 October. |

For each session, append a short entry here: `Date | Phase/IDs | Work completed | Evidence | Time spent | Blockers | Next action`. Do not create a new documentation file for every change.

- **27 Sep 2026 | P0 | Reconciled full template and audited current source | Screenshots + static source review; no live tests in this revision | Time not measured | Rule conflicts, job source and tester pending | P1 reliability fixes.**
- **28 Sep 2026 | P1 + P3 (data) | Rewrote wizard state (durable store vs widget keys); moved all buttons to `on_click`; removed dead `target_role`; added 503 retry with honest error copy; built `data/jobs_demo.json` (13 records) and `jobs.py`; added model dropdown | 71 tests pass; state loss reproduced before fix (`'...'` → `''`); one live Gemini generation reviewed for grounding; Checkpoint 2 saved and re-run from its own folder | Time not measured | Voice input not begun; key pasted in chat still needs rotation | P2: consent-first voice capture and reviewed transcription.**
- **1 Oct 2026 | P2 / D04–D05 / D09 (partial) | Added in-memory PCM WAV validation (10 MB / 120 seconds), malformed/truncated chunk checks, metadata stripping and digital-silence rejection; one explicit consent-gated Gemini transcription request with typed evidence-linked background extraction; bilingual transcript/background review and approval, persistence, invalidation, audio-widget reference release and text fallback. Escaped generated card text, removed absolute truthfulness copy and kept the server key out of browser widgets | 147 pytest tests pass (7.91 s), including offline real-SDK schema conversion; no editor diagnostics; `pip check` passes. Python 3.13.13, Streamlit 1.64.0, google-genai 2.25.0, Pydantic 2.13.5. The latter three direct dependencies are pinned; pandas/Altair retain existing version ranges. No live API calls or recorded personal data used | Time not measured | Real Hindi speech, browser permissions, selected-model audio capability, provider terms/quotas, key rotation and authorised deployment remain unverified; career-generation nested schema validation still outstanding | Perform the P2 manual acceptance below, then connect specific job matching in P3/P4. No checkpoint, Git operation or public upload performed.**

- **3 Oct 2026 | P4 / D07–D08 (+ location, data) | Rebuilt test env (`.venv312`, Python 3.12.11; the AirDropped venvs lacked pydantic_core's compiled binary). Single-call profile + grounded top-3 matching, mapping table, 8-word headline / 3-sentence summary contract, optional preferred work location (does not revoke transcript approval), DEMO-014 fictional driving school (template demo trio: warehouse/security/driving), dummy `.example.invalid` contacts on 3 records, combined download | 173 pytest tests pass (17 s); live Gemini call blocked by local network sandbox, so match quality is unreviewed | Time not measured | Live run must be done outside the sandbox | Live Havildar sample + Hindi voice run; then P5 template tests and P6 submission.**

- **3 Oct 2026 | P5 (started) / D05 | Live tests on localhost. Test A (typed Havildar sample): live, 5.2 s on Flash Lite, 2 grounded matches, demo labels and copied contacts correct; only 4 skills, and the Fleet reason implied a civilian licence from a defence licence. First live transcription failed with the generic "model" error on both Flash Lite and 3.8 Flash; fixed by removing `response_schema` (strict schema with additionalProperties=false) and describing the JSON shape in the prompt, with unchanged strict local validation. Transcription now works on gemini-3.8-flash with synthetic Hindi WAV (macOS Lekha voice). Added metadata-only failure logging (class/code/status/model) | 172 tests pass | Time not measured | Real-microphone Hindi recording still pending | Finish template tests 1–3, re-run Test A on 3.8 Flash.**

- **3 Oct 2026 | P5 / Test B (template test 1) | Synthetic Hindi WAV → transcript in Devanagari: Army, हवलदार, trade verbatim, years 15 with "40 जवान" kept out of years, education/certs blank. Analyse: 3.8 Flash busy, backup gemini-3.5-flash produced the result and was labelled; Warehouse Supervisor (Pune) + Logistics Coordinator (location gap stated); 6 skills; 58.6 s (over target). Fixes after the run: primary attempts 3→2 before backup, 3 matches requested whenever 3 jobs share an evidenced skill, job-match source_ids clarified, defence-issued licence wording, discarded-match count shown beside cards, role families collapsed, spoken preferred work location extracted (never postings; ungrounded location dropped, not fatal) | 190 tests pass | Time not measured | Busy 3.8 Flash capacity | Re-run Test B, then C (signals) and D (silence).**

- **4 Oct 2026 | P6 / D09 prep, D11 | Handbook re-read: public hosting is mandatory ("localhost doesn't count"); video 3–5 vs 5–10 min conflict → script targets ~5:00; rubric 25/30/20/15/10. Added `README.md` (run, deploy, operator handover), `python jobs.py` maintainer health check (+2 tests), `submission/` (explainer .html/.docx ~2 pages, form answers <100 words each, 5-minute video script), `.gitignore` for checkpoints/drafts/editor files; repo dry-run shows no secrets or local paths | 192 tests pass | Time not measured | Deployment (GitHub + Streamlit Cloud) needs participant; Test B rerun, C, D results still to fill [FILL] markers; key rotation | Deploy, verify public URL, record video, submit before 11:59 PM.**

- **4 Oct 2026 | D06 sustainability | Re-read template rules: no n8n/Telegram needed for Track 3 (tools not judged); "15% · survive next month: a non-technical person can run it" exposed JSON-only job maintenance. Added Google Sheet job source (`JOBS_SHEET_CSV_URL`, published CSV, https only, 1 MB cap, 8 s timeout, 5-minute cache), Google-Form-style headers, bad rows skipped with reasons, Form rows hidden until a volunteer sets status/last_checked, rows fictional unless `is_demo`=no, fallback to the demo list stated on screen; `data/jobs_sheet_template.csv` (round-trips identically to the JSON); README handover for Sheet + employer Form; corrected two overstated test claims in README/explainer | 207 tests pass; live Sheet fetch untested (sandbox) | Time not measured | Participant to create/publish Sheet | Deploy, then test with the Sheet secret set.**

### P2 manual acceptance still required

1. Before real inputs, rotate the previously exposed key and review the provider's current processing/retention terms and project quota limits. Do not enable paid usage without explicit approval. The selected text model has **not** been validated for audio by this implementation session.
2. In a local browser, confirm no microphone/upload widget appears before audio consent. After consent, record a **fictional** 30–90-second Hindi/mixed-language stores or transport narrative. Include service, rank, years and a small team quantity that must not be confused with years. Obtain permission for anyone else's recording; do not commit personal audio. The 120-second limit is checked on the server after capture, not a browser recording auto-stop.
3. Press **Transcribe and fill review fields**. Confirm original-language transcript, quantities and verbatim background wording. Unknown facts must remain blank; service is not inferred from rank. A successful transcription replaces previous background/narrative values; failure preserves previous text/results. Source-quote validation is not proof of semantic accuracy, particularly normalised service/years.
4. Correct the Service Narrative and suggested background, approve both, grant the separate text-processing consent, then analyse. Verify the corrected text reaches source facts. Editing source fields must revoke transcript approval; back/next and interface-language switches must preserve it when the source is unchanged. A language switch marks old generated output stale without discarding it.
5. Test microphone permission denial with WAV upload and typed fallback; test a silent clip, unclear/noisy speech, a corrupted WAV, a file over 10 MB and audio over two minutes. Exact digital silence is rejected locally; noise/near-silence depends on provider interpretation and human review. No automatic transcription retries; a failed attempt requires recapture/upload or typed fallback. No silent canned response fallback.
6. Verify Clear/Start over, source-mode changes and post-transcription cleanup discard audio-widget references. This does not promise deletion of browser/provider copies or downloaded files. Test transcript/edited-draft navigation and downloads without another transcription request.
7. After explicit deployment authorisation, test the same flow over HTTPS on a second device/network, including microphone denial and cold start. Record model, timings and reviewed outcomes here before marking P2 Verified. AppTest simulates binary capture for callbacks; it does not validate actual microphone recording/upload transport. Marathi remains unoffered/unverified.

### Checkpoint policy

Keep `checkpoints/checkpoint-1/` unchanged. Only when the participant explicitly approves a design/implementation and requests a checkpoint, inspect existing checkpoint numbers and save the next number (currently **4**; Checkpoint 3 saved 3 Oct 2026) locally. Include actual tested status and known limitations; exclude environments, logs, credentials and personal audio/data. A local snapshot is not an off-device backup. This revised plan does not authorise an automatic new checkpoint, Git operation or public upload.

---

## 10. Acceptance and Testing Matrix

Automate pure validation/rendering checks with mocked model responses. Use a small number of deliberate live tests; do not consume quota in loops.

| ID | Scenario | Expected result |
| :--- | :--- | :--- |
| TC-001 | Missing/invalid API configuration | Clear safe error, no key exposure and no retry loop. |
| TC-002 | Empty/whitespace-only narrative | Rejected before any API call; target role remains optional. |
| TC-003 | Load each Indian sample | Correct keyed fields update; unrelated reruns preserve user edits. |
| TC-004 | Normal live generation | All required sections validate; elapsed time recorded; no unsupported facts in reviewed output. |
| TC-005 | Downloads and widget reruns | TXT/Markdown contain the reviewed text; outputs do not disappear or trigger new generation. |
| TC-006 | Change input after generation | Existing result marked stale; new generation resets review state. |
| TC-007 | Quota, timeout or unavailable model | Actionable message; no unbounded retries; sample mode clearly distinguished. |
| TC-008 | Empty/blocked/invalid structured response | No success message or broken export; offer safe retry or labelled sample. |
| TC-009 | Fabrication trap | Request to invent an MBA, SAP certification or improvement percentage is not fulfilled as fact. |
| TC-010 | Evidence and rank mapping | Skill references point to real input facts; rank is not rewritten as an unsupported corporate job title. |
| TC-011 | Prompt injection in narrative/job description | Embedded instructions do not override career-assistant rules or trigger credential disclosure. |
| TC-012 | Hindi, mixed language and ambiguity | Quantities retain meaning; unclear terms produce clarification rather than invented expansions. |
| TC-013 | Privacy acknowledgement and input limits | Missing acknowledgement or oversized input blocked; sensitive-input warning visible. |
| TC-014 | Session isolation and reset | Two sessions do not share profiles or edits; reset clears this session's inputs/results. |
| TC-015 | Public/mobile access | Live URL works from another network; readable layout, adequate contrast and keyboard-accessible controls. |
| TC-016 | Job-description comparison | Missing requirements labelled not evidenced; no invented eligibility or match score. |
| TC-017 | Hindi stores/transport voice | Reviewed transcript preserves quantities; profile maps logistics duties; returns three suitable supplied jobs when available. |
| TC-018 | Signals voice narrative | Maps evidenced telecom/IT-support skills without invented licences/certifications. |
| TC-019 | Empty, noisy, corrupted or oversized audio | Reject or request re-recording; no fabricated transcript/profile/matches and no unintended billable loop. |
| TC-020 | Consent timing and microphone denial | No provider call before consent; microphone denial offers upload/text fallback. |
| TC-021 | Transcript edit/approval | Corrected text, not the old transcript, becomes the source of facts; downstream results invalidated on edits. |
| TC-022 | Supplied job IDs and source fields | Unknown/duplicate IDs rejected; employer, contact, location and links copied from source records. |
| TC-023 | Fewer than three/zero matches | Honest shortlist size or no-match explanation; never fill with invented jobs. |
| TC-024 | Stale/missing dataset or fictional records | Clear unavailable/stale/demo label; fictional listings never presented as live vacancies. |
| TC-025 | Forward/back, language switch and reset | Durable inputs, approved transcript and edited draft survive navigation; reset works without state-mutation exceptions. |
| TC-026 | Mocked malformed nested JSON and HTML payload | Typed validation catches bad shapes; generated markup renders as safe text rather than injected HTML. |
| TC-027 | Noisy spelling and title-only matching traps | Matching uses supporting duties/skills; titles alone do not determine a recommendation. |
| TC-028 | Marathi support claim, if enabled | Test actual Marathi recordings with a fluent reviewer; otherwise label support unverified and do not advertise it. |
| TC-029 | Operational logging | Logs contain no keys, raw recordings, transcripts or personal profiles; confirm app and deployment settings. |

Passing these tests supports an execution claim; it does not guarantee a perfect rubric score or comprehensive security.

### Impact evidence to collect

- Time to prepare a comparable draft manually versus with the app, **including user review and correction**.
- Number of unsupported claims found and corrected; target zero in final reviewed sample outputs.
- Whether the tester understands the suggested roles and can use the exported draft.
- Test count, dates, input type and observed generation times. For a small sample, report individual values/range rather than implying statistically reliable performance.
- Distinguish measured results from targets. Do not claim “four hours to three minutes,” cost savings or improved hiring outcomes unless supported by evidence.

---

## 11. Planned Repository and Deployment

Keep modules small and testable without building a framework. Preserve current module names; do not migrate data merely to make the tree look cleaner. Items marked planned below are not yet implemented.

```text
app.py                       # Streamlit UI, session state and review flow
career_engine.py             # Model call, prompt construction and validation
theme.py                     # Existing approved visual identity
i18n.py                      # Existing bilingual copy; completeness needs testing
profiles.py                  # Existing fictional profiles and role-family reference
audio_service.py             # Implemented: consent-gated WAV validation/transcription
job_matcher.py               # Planned: candidate selection, job-ID validation
schemas.py                   # Planned: structured response models
data/
    jobs_demo.json           # Planned: explicitly fictional job records
    jobs.csv                 # Planned: permitted, checked real records; separate from demo
tests/
    test_career_engine.py    # Planned: mocked validation and failure paths
    test_job_matcher.py      # Planned: grounding, no-match and source fidelity
    test_app.py              # Planned: Streamlit AppTest wizard/state regression
requirements.txt             # Exists; pin only after compatibility testing
.gitignore                   # Secrets, environments and local artefacts excluded
.streamlit/
    config.toml              # Existing non-secret theme settings
README.md                    # Planned: setup, limits and operator handover
development_plan.md          # This plan
checkpoints/checkpoint-1/     # Existing immutable local snapshot
submission/
    problem_solution.md      # Planned source for one-page explainer
    form_answers.md          # Planned concise submission answers
```

### Deployment checklist

1. Verify the selected Python version, SDK import and actual model availability locally.
2. Pin tested dependencies and exclude all secrets, local environments and private test records from Git.
3. When repository/deployment setup is authorised, review intended source files and choose private/public access according to the host's current requirements. The competition requires a public working app, not necessarily a public code repository. Do not publish checkpoints, local handbook/screenshots or private records accidentally.
4. Configure Streamlit Community Cloud with the correct repository, branch, `app.py`, Python version and server-side secrets.
5. Verify the public URL in incognito and on another network, including cold-start behaviour and a real generation request.
6. Check download behaviour, safe failure messages, quota limits and session isolation on the hosted app.
7. Record the deployed model/configuration and known limitations in `README.md`. Free-tier availability and deployment time remain external dependencies.

---

## 12. Submission, Three-Minute Video and Handover

Use the local participant handbook and screenshot rubric as the competition reference, with **4 October 2026 overriding the stale FAQ date as confirmed by the organisers**.

- Submit under **Track 3 — Product Build**, aligned with idea #09. Present the hosted browser product and its voice-to-profile/job-matching journey, not an AI Agent-track submission.
- Prepare a **one-page** PDF/Word explainer: problem, who was consulted, solution, three test results, known failures and next step. Include measured results only when recorded.
- Prepare concise answers to the form's three questions: problem, beneficiary and why AI is necessary. Separate observed impact from intended impact.
- Include the hosted app link, optional project files and fictional screenshots as appropriate.
- Create the submission Drive folder, set **Anyone with the link → Viewer**, and test access from an incognito window.
- Submit through the organiser's form and retain the confirmation screen. Do not reproduce participant contact details in public product demos.
- Include the working public URL, a provisional **three-minute** live-workflow recording and the one-page explainer. Confirm the conflicting duration instructions before final recording/submission.

### Video storyboard from the supplied template

| Time | Content | Evidence to show |
| :--- | :--- | :--- |
| 0:00–0:20 | Problem | One specific retiring/retired Indian service member's task; use fictional details on screen. |
| 0:20–0:40 | Who it helps | Describe an actual consultation only if it happened; disclose absence of user testing otherwise. Obtain permission for organisation attribution and avoid exposing personal identity. |
| 0:40–2:20 | Live workflow | Record a short Hindi voice note, show transcription/review, civilian profile and up to three matches with reasons/application routes. Label demo jobs. Do not pretend prerecorded output was generated live. |
| 2:20–2:45 | What breaks | Small job list, availability/freshness limits, unclear audio, quota or language limitations actually observed. |
| 2:45–3:00 | Next step and owner | Who would maintain the job list, how it can be updated and the next validated improvement. Do not invent an NGO partnership. |

Use macOS screen recording or OBS. Rehearse on the actual model/quota and network early; keep a truthful backup recording but retain a functioning live app. If a call takes longer than expected, show the real delay or re-record honestly; do not label edited waiting time as a live one-take run.

### Sustainability / operator handover

Document in the final README: startup/deployment, secret configuration without revealing keys, how to add/expire a job CSV row, weekly freshness checks, quota/model failure handling, privacy limitations and the three acceptance tests. Test whether a non-technical helper can maintain the job list without editing Python. No agreed operator currently exists; finding one is an outreach task, not a completed benefit.

### Definition of ready

The product is ready when a user can open the hosted app, record a non-sensitive Hindi service narrative, correct and approve the transcript, receive an evidence-linked civilian profile and up to three matches from the supplied job dataset, review the application pack and download it. The three template tests must pass, failure states must be clear, and demo/real jobs must be unambiguous.

The submission is ready only when the full mandatory checklist is satisfied, the applicable rubric/duration conflicts have been resolved or explicitly escalated, **Track 3 — Product Build** is selected in the submission, and the working link, recording, one-page explainer and Form/Drive access have been checked. A revised plan or successful server startup alone is not completion evidence.