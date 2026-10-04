# Product Requirement Document (PRD)
## Project VetAlign-AI — सैन्य अनुभव से नागरिक करियर तक

| Attribute | Details |
| :--- | :--- |
| **Product Name** | VetAlign-AI |
| **Track & Track ID** | Product Build Track (Solo) — Approved Idea #09: Ex-servicemen skill matcher |
| **Target Launch Date** | **04 October 2026** (11:59 PM) |
| **Document Status** | Approved / Baseline MVP |

---

## 1. Executive Summary & Problem Framing
### 1.1 Objective
**VetAlign-AI** is a lightweight, high-reliability application assistant built to help **Indian ex-servicemen** translate their non-sensitive military duties into civilian transferable skills, recommended career paths, and tailored application profiles. 

The primary metric of success is **measured time saved** for the veteran during application drafting, including human-in-the-loop review and correction time.

### 1.2 Target Beneficiary
Indian Armed Forces veterans (starting with an MVP focus on **Army logistics, stores, transport, or maintenance experience**) transitioning into early civilian employment.

### 1.3 The Core Problems Addressed
1. **Terminology Barrier:** Civilian recruiters do not understand military jargon, ranks, or operational duties (e.g., *Havildar, Petty Officer, Sergeant*).
2. **AI Embellishment / Fabrication:** Generic AI engines often hallucinate certifications, inflate organizational seniority, or fabricate metrics not present in a veteran's actual background.
3. **Application Friction:** Rewriting tailored applications manually for various local roles is costly and highly time-consuming.

### 1.4 Product Positioning
* **What it is:** A local application-preparation assistant and advisory career companion.
* **What it is NOT:** A recruitment authority, live job board, official equivalence certifier, or provider of legal/pension/financial advice.

---

## 2. User Journey & Core Functional Requirements

The MVP restricts the user experience to **one reliable, end-to-end user journey** separated across three distinct wizard phases within a single page layout.

```
[Step 1: Input & Safe Consent] 
       │
       ▼
[Step 2: Single-Call Pipeline Model Processing] 
       │
       ├─► Tab 1: Skills & Role Fit
       ├─► Tab 2: Application Draft
       └─► Tab 3: Interview Prep
       │
       ▼
[Step 3: Human Review, Edit, & Text Export]
```

### 2.1 Step 1: Input & Safety Control
The interface enforces a clean configuration form capturing contextual markers without requesting personally identifiable information (PII).

* **Service Branch Selection:** Dropdown menu: `Indian Army`, `Indian Navy`, or `Indian Air Force`.
* **Context Fields (Optional):** Rank, Trade, Years Served, Education, and Certifications.
* **Service Narrative (Required):** Free text input for service experiences/duties.
* **Target Context (Optional):** Preferred civilian role or pasted job description text.
* **Localization Language Toggles:** Choose output explanation delivery in either `English` or `Hindi`.
* **Privacy & Consent Box (Required Checklist):** A mandatory checkbox stating that submitted content contains no restricted operational data, no personal identifiers, and will be evaluated via external AI providers.
* **Fictional Profiles Loader:** A functional module providing three one-click fictional Indian sample profiles (Army, Navy, Air Force) to let judges and users test the application safely without entering live data.

### 2.2 Step 2: Core Processing & UI Output Tabs
A single backend pipeline processes inputs to prevent multi-call latency. It renders three data evaluation tabs:

#### Tab 1: Skills & Role Fit
* Maps specific source duties directly to civilian transferable skill summaries.
* Recommends up to three local civilian target role families utilizing an internal illustrative catalog (e.g., *Warehouse Supervisor, Logistics Coordinator*).
* Matches candidate data against requirements when a target job description is pasted—explicitly labeling components as *Supported*, *Needs Clarification*, or *Not Evidenced*.
* **Constraint:** Zero percentage-based fit scores, salary projections, or employment guarantees are allowed.

#### Tab 2: Application Draft
* Outputs an ATS-friendly, clean professional summary and structured experience bullets.
* **Constraint:** Retains true military titles alongside civilian descriptions rather than replacing them with artificial corporate job designations.

#### Tab 3: Interview Preparation
* Generates two situational/behavioral questions and two functional questions anchored solely on the input data.
* Outlines answering structures using the STAR approach (Situation, Task, Action, Result), mapping clear placeholders if key metrics are missing from the profile input.

### 2.3 Step 3: Review and Data Export
* **Inline Modifications:** The generated application draft must be completely editable by the user inside a text area widget before exporting.
* **Export Action:** Single-click downloading of the customized text as `.txt` or `.md` files.
* **Session Safeguards:** The data must survive active browser window reruns or export triggers. If inputs change, the current output must instantly flag itself as *stale* and prompt for regeneration.
* **Clear Session Action:** A manual button to flush memory variables instantly.

---

## 3. Boundary Conditions & Non-Functional Requirements

### 3.1 Strict System Guardrails (Anti-Fabrication & Anti-Hallucination)
1. **Evidence Binding:** Every bullet point, skill assertion, or interview recommendation must tie directly back to an explicit input fact from the user's input.
2. **No Extrapolation:** The platform must never inject external business degrees, modern software capabilities (e.g., SAP, Salesforce), or arbitrary percentage metrics if not stated by the user.
3. **The "Not Evidenced" Principle:** If critical target qualifications are missing, the system must declare them "not evidenced in provided information" rather than assuming the applicant does not possess the capacity.

### 3.2 Technical Scope Reductions (Explicitly Out of Scope)
To preserve execution quality for a single developer track, the following features are completely out of scope:
* Database layers, user authentication systems, or persistent storage.
* Live external job boards, scraping pipelines, or automated application sending.
* Automated document parsing, OCR integrations, or PDF profile attachments.
* Voice dictation engines or multi-agent orchestration backends.

---

## 4. Technical Architecture & Stack Specifications

```
                       ┌─────────────────────────┐
                       │  Streamlit Frontend UI  │
                       └────────────┬────────────┘
                                    │ (Input Context & Form Validation)
                                    ▼
                       ┌─────────────────────────┐
                       │   Prompt Engine Core    │
                       │ (Structured Schema Laws)│
                       └────────────┬────────────┘
                                    │ (Single API Call Request)
                                    ▼
                   ┌─────────────────────────────────┐
                   │ Gemini Pro API (google-genai)   │
                   └────────────────┬────────────────┘
                                    │ (Pydantic Validated JSON)
                                    ▼
                       ┌─────────────────────────┐
                       │ Streamlit Session State │
                       │    (Edits & Exports)    │
                       └─────────────────────────┘
```

### 4.1 System Stack Components
* **Runtime Environment:** Python 3.11 or Python 3.12.
* **Interface & Processing Engine:** Streamlit Framework (handles both browser layer and server-side workflow routing simultaneously).
* **AI Core Integration Layer:** Google GenAI SDK (`google-genai`) calling active production models.
* **Structure Constraints & Validations:** Pydantic models enforcing structured data schemas.
* **Cloud Hosting Pipeline:** Streamlit Community Cloud tied to the project repository.

### 4.2 Code Integration Fixes & Compliance Laws
* **Import Architecture:** Do not use `from google_genai import client`. Implement the officially maintained structural syntax:
  ```python
  from google import genai
  client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
  ```
  *(Ensure `gemini-1.5-flash` legacy configurations are updated to active verified model identifiers during deployment.)*
* **Input Limits & Sanitation:** Hard cap form entry blocks at a combined size of 8,000 characters. Intercept whitespace-only inputs before triggering network infrastructure.
* **Error Handling Protocols:** Gracefully catch API key issues, quota exhaustions, and timeout limits (bounded at 60 seconds). If the server crashes, present pre-rendered fallback mock templates explicitly labeled: *"Sample output — not generated live."*

---

## 5. Visual Theme & Indian Identity Guidelines

Visual components are styled to create an authentic local orientation without misleading users into assuming official government authorization.

| Interface Element | Design Rule & Constraint |
| :--- | :--- |
| **National Flag Accent** | Small, uncropped 3:2 proportion official flag next to the main title. Never layer text over it, animate it, or modify its colors. |
| **Color Scheme Palette** | Soft off-white base layer, navy text typography, with restrained saffron and green component micro-accents. Contrast must support high accessibility. |
| **Service Branch Selection** | Plain text choices accompanied by simple, customized original vector shapes. Do not use official military crests. |
| **Regulatory Footer Notice** | Mandatory Text: *"Independent career-support prototype. Not affiliated with or endorsed by the Government of India or the Indian Armed Forces."* |
| **Export Profile Assets** | Clean, minimalist, and standard text output layout. Remove flags, country symbols, or decoration markers from the final document content. |