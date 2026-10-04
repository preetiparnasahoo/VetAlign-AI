# VetAlign-AI — सैन्य अनुभव से नागरिक करियर तक

**From service experience to a civilian career.** A voice-first web app for retiring
and retired Indian service personnel: describe your service by voice in Hindi (or
type it), and get a civilian application profile plus up to three matching open
roles, each with a reason, gaps to check and the employer's application route.

Build for Good (Be10X) · Track 3 — Product Build · Idea #09 Ex-servicemen skill matcher.

> Independent career-support prototype. Not affiliated with or endorsed by the
> Government of India or the Indian Armed Forces. It drafts and suggests only; it
> does not certify qualification equivalence, decide eligibility or guarantee
> employment. **All job listings in this demo are fictional.**

## How it works

```text
Voice note (Hindi / mixed / English) ──► Gemini: transcript + background, each field quoted
        or typed text                        │
                                             ▼
                              Veteran reviews, corrects, approves
                                             │
                                             ▼
        Gemini: civilian skills (cited to numbered facts) + profile + top-3 job IDs
                                             │
                                             ▼
        App: drops unknown/closed/uncited job IDs; copies employer, link, contact
             from the job list (never from the AI)
                                             │
                                             ▼
        Step 2: matched roles with reasons and gaps  ·  Step 3: editable profile + download
```

Two Gemini calls per voice journey (one for typed input). If the chosen model is
busy, the app retries once and then tries a backup model once, and says so on screen.

## Run locally

Requires Python 3.12.

```bash
python3.12 -m venv .venv312
.venv312/bin/pip install -r requirements.txt
mkdir -p .streamlit && echo 'GEMINI_API_KEY = "your-key"' > .streamlit/secrets.toml
.venv312/bin/streamlit run app.py          # http://localhost:8501
.venv312/bin/python -m pytest -q           # offline tests, no API calls
```

`.streamlit/secrets.toml` is git-ignored. Never commit a key.

## Deploy (Streamlit Community Cloud, free)

1. Push this folder to a GitHub repository. `.gitignore` already excludes secrets,
   virtual environments, checkpoints, logs and competition material. Check
   `git status` before the first push.
2. On share.streamlit.io choose **Create app** → the repository → branch → `app.py`.
   Under **Advanced settings** pick **Python 3.12** and paste the secrets:
   `GEMINI_API_KEY = "your-key"` and, if a job Sheet is published,
   `JOBS_SHEET_CSV_URL = "the published CSV link"`.
3. Open the public URL in an incognito window and on a phone (mobile data), and
   run the Havildar sample end to end. The microphone works there because the
   app is served over HTTPS.

## Maintaining the job list (operator handover)

A volunteer keeps the jobs in a **Google Sheet**; no code or redeploy is needed.
Employers can offer roles through a **Google Form**. Without a Sheet configured,
the app uses the built-in fictional list in `data/jobs_demo.json`.

**Who:** a volunteer at an ex-servicemen association, a resettlement counsellor or
a Zila Sainik Welfare Office helper. *This is a proposed role: no one has agreed to it yet.*

### One-time setup (about 15 minutes)

1. **Create the Sheet.** In Google Sheets choose File → Import → Upload
   `data/jobs_sheet_template.csv` → *Replace spreadsheet*. Rename the tab `jobs`.
   One row = one role. Put several skills in one cell, separated by `;`.
2. **Publish it.** File → Share → **Publish to web** → choose the `jobs` tab and
   **Comma-separated values (.csv)** → Publish → copy the link.
3. **Connect the app.** In Streamlit Cloud → app → Settings → Secrets, add
   `JOBS_SHEET_CSV_URL = "the link"`. The app reads the Sheet every 5 minutes.
   Step 2 of the app says "live Google Sheet" when it is working.
4. **Employer Form (optional).** Create a Google Form with the questions *Job title,
   Company, Skills required, City, Application link, Contact*. In the Form's
   Responses tab choose **Link to Sheets** → the same spreadsheet, so answers land in
   a separate tab. Share the Form link with employers.

### Weekly routine (about 15 minutes)

- **Review new Form answers.** Check that the employer and link are genuine, then copy
  the row into the `jobs` tab and fill in `last_checked` (YYYY-MM-DD), `status` = `open`
  and `is_demo` = `no`. Nothing appears to veterans until you do this.
- **Close filled roles:** set `status` to `closed`.
- **Re-check open roles** and update `last_checked`. A role not checked for 45 days is
  hidden automatically.
- **Check the Sheet:** `python jobs.py "<published CSV link>"` lists how many roles
  veterans will see, which are stale, and any row it skipped and why. A bad row is
  skipped; it never breaks the whole list.

### Rules for real listings

Use only roles from consenting employers or permitted public sources, with an
official application link. Never add a recruiter's personal phone number. Rows are
treated as fictional unless `is_demo` is set to `no`. If the Sheet cannot be read,
the app falls back to the fictional demo list and says so on screen.

## Privacy and safety

- Consent before any audio leaves the browser; a second consent before profile generation.
- No database. Audio and transcripts are not logged. Failure logs record only the
  error class, HTTP code and model name.
- Warnings against recording names, service numbers, Aadhaar/PAN, unit locations or
  restricted information. Spoken work location is taken only as a preference, never
  a posting.
- Every skill must cite a numbered fact from the veteran's own words; the veteran
  reviews and edits everything before use.

## Known limits

- The demo job list is small (13 open fictional roles). The Sheet and Form make it
  maintainable by a non-technical volunteer, but no one has agreed to maintain it yet.
- Tested with synthetic Hindi speech only; a real-microphone test on the hosted app is
  still pending. Marathi is not offered yet.
- Free-tier Gemini is sometimes busy: the retry and backup model reduce failures but
  cannot remove them.
- Provider data retention is governed by Google's terms. The app cannot delete
  copies held by the provider.

## Project layout

| File | Purpose |
| :--- | :--- |
| `app.py` | Streamlit UI, three-step wizard, session state |
| `audio_service.py` | WAV validation and consent-gated transcription |
| `career_engine.py` | Prompt, Gemini call, validation, grounded job matching |
| `jobs.py` | Job list loading and validation (JSON or Google Sheet CSV); `python jobs.py` health check |
| `i18n.py` | English and Hindi interface text |
| `profiles.py`, `data/jobs_demo.json` | Fictional sample profiles and jobs |
| `data/jobs_sheet_template.csv` | The same demo jobs, ready to import into Google Sheets |
| `tests/` | 200+ offline tests (no network, no quota) |
