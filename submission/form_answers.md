# Google Form answers (paste-ready, each under 100 words)

**Project title:** VetAlign-AI
**Track:** Product
**Live app:** https://vetalign-ai-preetiparnasahoo.streamlit.app/
**Code:** https://github.com/preetiparnasahoo/VetAlign-AI

---

**Q1. What real problem are you solving?**

A Havildar retiring after 15 years has run a battalion's stores and transport and trained 40
jawans, but on a civilian job portal that reads as nothing because the words don't match.
Recruiters search for "inventory management" and "fleet coordination", not "stores" and "convoy".
Writing a civilian CV means typing in English, and generic AI writers invent titles and certificates.
VetAlign-AI turns a short Hindi voice note into a reviewed civilian profile and up to three matching
open roles, each with a reason, gaps to check and the employer's contact.

*(90 words)*

**Q2. Who is the problem for?**

Retiring and retired Indian Army, Navy and Air Force personnel, especially those more comfortable
speaking Hindi than typing English, who are looking for civilian work in logistics, transport,
maintenance, security and telecom. Secondary users are resettlement counsellors and ex-servicemen
association volunteers who help them prepare applications. [FILL if tested: "Tested with … (with
consent)".]

*(55 words)*

**Q3. How does your solution use AI?**

Gemini does three jobs a form cannot. It transcribes code-switched Hindi speech and extracts rank,
years and trade, telling "15 साल" (service) from "40 जवान" (team size). It translates military duties
into specific civilian skills using a mapping (stores → inventory, signals → telecom/IT), each skill
cited to the veteran's own words. It ranks open roles by skills, not titles, and explains fit and gaps.
Code then rejects invented or closed jobs and copies employer details from the list, so nothing is
made up.

*(87 words)*

**Q4. What AI tools/platforms have been used?**

AI in the product: Google Gemini (3.8 Flash, with 3.5 Flash as an automatic backup) through the
official google-genai SDK and a Google AI Studio key. It transcribes Hindi/English speech, extracts
service details, translates duties into civilian skills, ranks open jobs and drafts the profile.
Built with: Claude Code (Anthropic) as a coding assistant. Platforms: Streamlit, Streamlit
Community Cloud (hosting), GitHub, Google Sheets and Forms (volunteer-maintained job list).

*(68 words)*

**Q5. How does your solution help the user?**

Effort: the veteran speaks for 30–90 seconds in Hindi instead of typing a CV in English; the app
fills in the form and they only check it. Time: in testing, the AI turned a typed service history
into civilian skills, a draft profile and three matched roles in 23.5 seconds [FILL: measured
end-to-end time, including review]. Cost: free for the veteran, with no sign-up, API key or paid CV
writer. Quality: skills use the words recruiters search for ("inventory management", not
"stores"), and every claim traces back to what the veteran said.

*(92 words)*

**Q6. Explain your solution in detail.**

A bilingual (Hindi/English) web app in three steps. 1) The veteran records or types their
service; Gemini transcribes it and fills the form, and the veteran corrects and approves it.
2) Gemini translates duties into civilian skills, each cited to the veteran's own words, and picks
the top three roles from a volunteer-run Google Sheet, with reasons and gaps. 3) An editable
profile, interview questions and an action plan to download. A second tab lists every open job.
Useful because military experience becomes searchable, without English typing or invented claims.

*(90 words)*

**Q7. What was the biggest challenge you faced during this hackathon?**

Making the AI trustworthy for people applying for real jobs. Generic AI writers inflate ranks into
titles never held and invent certificates or vacancies. A prompt alone could not stop that, so the
checks moved into code: every skill must cite a numbered fact from the veteran's words, the AI sees
only job IDs and skills, and employer details are copied from the job list. Anything unsupported is
discarded and the screen says so. A second challenge: Google's free tier often returned "busy", so
we added retries and a backup model.

*(91 words)*

---

Before submitting: replace every [FILL], take a screenshot of "Your response has been recorded"
(there is no confirmation email).
