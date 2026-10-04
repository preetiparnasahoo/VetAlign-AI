"""VetAlign-AI — Indian ex-servicemen skill matcher (Be10X Build for Good).

A three-step assistant: Input & Consent -> Skills & Role Fit -> Application Draft.
It drafts and suggests; the veteran reviews, edits and decides. It does not
certify qualification equivalence, decide eligibility or guarantee employment.
"""

from __future__ import annotations

import os
import json
import time
from html import escape

import altair as alt
import pandas as pd
import streamlit as st

import career_engine as engine
import audio_service as audio
import jobs as job_data
import theme
from i18n import tr
from profiles import DEMO_PROFILES, SERVICES


def stored_api_key() -> str:
    """The app-owned Gemini key from secrets.toml or GEMINI_API_KEY, else ""."""
    return config_value("GEMINI_API_KEY")


st.set_page_config(
    page_title="VetAlign-AI | Veteran Experience Translator",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(theme.CSS, unsafe_allow_html=True)

FIELDS = {
    "service": SERVICES[0],
    "rank": "",
    "trade": "",
    "years": 0,
    "education": "",
    "certifications": "",
    "duties": "",
    "location": "",
    "job_description": "",
}
DEFAULTS = dict(
    FIELDS, step=1, ui_lang="English", result=None, result_key=None,
    edited_profile="", error="", consent=False,
    audio_consent=False, audio_language=audio.LANGUAGES[0],
    audio_source="record", audio_pending=False, audio_error="",
    voice_source=False, transcript_approved=False, transcription_elapsed=None,
    transcription_backup=None,
    extracted_background=None, selected_job=None,
)

# Credentials live outside DEFAULTS so that "Clear" and "Start over" wipe the
# veteran's data without also discarding the operator's API key.
st.session_state.setdefault("api_key", "")

# Model selection is split in two: a dropdown choice plus a free-text box used
# only when "Other" is picked. Keeping them separate means switching away from
# a typed name and back does not lose what was typed.
MODEL_OPTIONS = [value for value, _ in engine.MODEL_CHOICES] + [engine.CUSTOM_MODEL_OPTION]
MODEL_LABELS = dict(engine.MODEL_CHOICES)
st.session_state.setdefault("model_choice", engine.DEFAULT_MODEL)
st.session_state.setdefault("custom_model", "")

for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)
st.session_state.setdefault("audio_epoch", 0)
st.session_state.setdefault("last_transcription_attempt", 0.0)


AUDIO_LANGUAGE_LABELS = dict(zip(audio.LANGUAGES, ("audio_hindi", "audio_english")))


def config_value(name: str) -> str:
    """A server-side setting from secrets.toml or the environment, else ""."""
    try:
        value = st.secrets.get(name, "")
    except Exception:  # no secrets.toml present
        value = ""
    return str(value or os.environ.get(name, "")).strip()


# Refreshed every 5 minutes, so a volunteer's sheet edit appears without a
# redeploy. The list is app-owned and identical for every user, so caching is safe.
@st.cache_resource(ttl=300)
def open_jobs() -> tuple[list, str, str]:
    """``(jobs, error, source)``: open current jobs, why none, and where from.

    A configured Google Sheet is preferred. If it cannot be read or has no open
    rows, the built-in demo list is used and ``source`` says so, so a live demo
    never silently loses its job list.
    """
    sheet_url = config_value("JOBS_SHEET_CSV_URL")
    if sheet_url:
        try:
            sheet = job_data.fetch_jobs_csv(sheet_url).open_jobs()
            if sheet:
                return sheet, "", "sheet"
        except job_data.JobDataError:
            pass
    try:
        return job_data.load_jobs().open_jobs(), "", "demo_fallback" if sheet_url else "demo"
    except job_data.JobDataError as exc:
        return [], str(exc), "none"


def active_model() -> str:
    """The model name to send, resolving the 'Other' case."""
    choice = st.session_state.model_choice
    if choice == engine.CUSTOM_MODEL_OPTION:
        return st.session_state.custom_model.strip()
    return choice


def active_api_key() -> str:
    """Never seed a browser widget with an app-owned secret."""
    return st.session_state.api_key.strip() or stored_api_key()


# ------------------------------------------------------------ state plumbing
# Streamlit discards the state of widgets that a rerun does not render. Because
# steps 2 and 3 do not draw the step-1 inputs, keying those widgets directly on
# the data keys silently destroyed the veteran's answers on navigation.
#
# So the durable answer lives under its own key (e.g. "duties") and the widget
# is keyed separately ("w_duties"). Before each widget renders we copy durable
# -> widget; when the user edits, on_change copies widget -> durable. The
# durable store is therefore the single source of truth, and it survives every
# step change. It also lets callbacks such as load_sample() rewrite answers
# without touching an already-instantiated widget, which Streamlit forbids.

def wkey(name: str) -> str:
    return f"w_{name}"


def _sync(name: str) -> None:
    """Widget -> durable store. Runs as an on_change callback."""
    st.session_state[name] = st.session_state[wkey(name)]
    if name == "job_description":
        st.session_state.selected_job = None  # typed over: no longer the listed job
    if name in FIELDS or name in ("api_key", "model_choice", "custom_model", "consent",
                                  "transcript_approved"):
        st.session_state.error = ""
    # A work-location preference is not part of the transcript, so editing it
    # must not revoke the veteran's transcript approval.
    if name in FIELDS and name != "location" and st.session_state.voice_source:
        st.session_state.transcript_approved = False
        if name == "duties":
            # Do not keep an extracted fact whose supporting words were removed.
            background = st.session_state.extracted_background or {}
            for field, quote in background.get("evidence", {}).items():
                if (quote not in st.session_state.duties
                        and st.session_state[field] == background.get(field)):
                    st.session_state[field] = 0 if field == "years" else ""
    if name in ("audio_source", "audio_language") or (
        name == "audio_consent" and not st.session_state.audio_consent
    ):
        clear_audio_capture()


def bind(name: str) -> dict:
    """Seed the widget from durable state and return its kwargs."""
    st.session_state[wkey(name)] = st.session_state[name]
    return {"key": wkey(name), "on_change": _sync, "args": (name,)}


def form_values() -> dict:
    return {k: st.session_state[k] for k in FIELDS}


def signature() -> str:
    return json.dumps(dict(form_values(), language=st.session_state.ui_lang,
                           voice_source=st.session_state.voice_source,
                           approved=st.session_state.transcript_approved),
                      sort_keys=True, ensure_ascii=False)


def clear_audio_capture() -> None:
    """Release widget-held audio; never copy recordings into durable state."""
    for key in list(st.session_state):
        if key.startswith(("audio_record_", "audio_upload_")):
            del st.session_state[key]
    st.session_state.audio_epoch += 1
    st.session_state.audio_pending = False


def capture_changed(key: str) -> None:
    st.session_state.audio_pending = st.session_state.get(key) is not None
    st.session_state.transcript_approved = False
    st.session_state.result_key = None
    st.session_state.audio_error = ""


def use_typed_input() -> None:
    """Explicitly leave the voice review flow; preserve user-editable text."""
    clear_audio_capture()
    st.session_state.update(voice_source=False, transcript_approved=False,
                            audio_error="", extracted_background=None,
                            transcription_elapsed=None, transcription_backup=None,
                            result_key=None)


def transcribe_capture(key: str) -> None:
    """Only an explicit button press can send audio to the provider."""
    st.session_state.audio_error = ""
    try:
        if not st.session_state.audio_consent:
            raise audio.AudioError("consent")
        recording = st.session_state.get(key)
        if recording is None:
            raise audio.AudioError("missing")
        if time.monotonic() - st.session_state.last_transcription_attempt < audio.COOLDOWN_SECONDS:
            raise audio.AudioError("cooldown")
        st.session_state.last_transcription_attempt = time.monotonic()
        with st.spinner(tr(st.session_state.ui_lang)["audio_processing"]):
            output = audio.transcribe(
                active_api_key(), active_model(), recording.getvalue(),
                consent=st.session_state.audio_consent,
                language=st.session_state.audio_language,
            )
        background = output["background"]
        for field in ("service", "rank", "trade", "years", "education", "certifications",
                      "location"):
            if field == "location" and not background.get("location"):
                continue  # not spoken: keep any typed preference
            st.session_state[field] = background.get(field) or (0 if field == "years" else "")
        st.session_state.update(
            duties=output["transcript"], voice_source=True, transcript_approved=False,
            extracted_background=background, transcription_elapsed=output["elapsed"],
            transcription_backup=output.get("model") if output.get("backup_used") else None,
            result_key=None, error="",
        )
    except audio.AudioError as exc:
        st.session_state.audio_error = exc.code
    finally:
        clear_audio_capture()


def load_sample(name: str) -> None:
    use_typed_input()
    sample = DEMO_PROFILES[name]
    for key in FIELDS:
        # A job picked in the jobs tab describes the target, not the veteran.
        if key == "job_description" and st.session_state.selected_job:
            continue
        st.session_state[key] = sample.get(key, FIELDS[key])
    st.session_state.update(result=None, result_key=None, edited_profile="", error="")


def reset_all() -> None:
    clear_audio_capture()
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


def set_service(service: str) -> None:
    st.session_state.service = service
    st.session_state.transcript_approved = False


def go_to(step: int) -> None:
    st.session_state.step = step


def use_job(job_id: str) -> None:
    """Copy a listed job into the target-role field and return to step 1."""
    job = next((j for j in open_jobs()[0] if j.job_id == job_id), None)
    if job is None:
        return
    st.session_state.job_description = job.target_text()
    st.session_state.update(selected_job=job_id, step=1, error="")


def set_lang(lang: str) -> None:
    st.session_state.ui_lang = lang


T = tr(st.session_state.ui_lang)

# ================================================================= sidebar
with st.sidebar:
    st.markdown(
        f'<div class="va-brand">{theme.flag_svg(34)}'
        f'<span class="va-brand-name">VetAlign-AI</span></div>'
        f'<p class="va-brand-tag">{T["step1"]} · {T["step2"]} · {T["step3"]}</p>',
        unsafe_allow_html=True,
    )

    st.markdown(f'<p class="va-eyebrow">{T["sys_lang"]}</p>', unsafe_allow_html=True)
    lang_cols = st.columns(2)
    for col, lang in zip(lang_cols, ["English", "हिन्दी"]):
        col.button(
            lang,
            key=f"lang_{lang}",
            use_container_width=True,
            type="primary" if st.session_state.ui_lang == lang else "secondary",
            on_click=set_lang,
            args=(lang,),
        )

    st.markdown(f'<p class="va-eyebrow">{T["steps"]}</p>', unsafe_allow_html=True)
    for num, label in enumerate([T["step1"], T["step2"], T["step3"]], start=1):
        state = "on" if st.session_state.step == num else ("done" if num < st.session_state.step else "")
        st.markdown(
            f'<div class="va-rail {state}"><span class="va-num">{num}</span>{label}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f'<p class="va-eyebrow">{T["api_key"].upper()}</p>', unsafe_allow_html=True)
    st.text_input(
        T["api_key"],
        type="password",
        label_visibility="collapsed",
        **bind("api_key"),
    )

    # Model is a dropdown of names the API listed for this key, with a typed
    # fallback. Availability is per-key and changes, so the list is a
    # convenience, not a guarantee; an unavailable name returns a clear 404.
    st.selectbox(
        T["model"],
        options=MODEL_OPTIONS,
        format_func=lambda value: (
            T["model_other"] if value == engine.CUSTOM_MODEL_OPTION
            else MODEL_LABELS.get(value, value)
        ),
        **bind("model_choice"),
    )
    if st.session_state.model_choice == engine.CUSTOM_MODEL_OPTION:
        st.text_input(
            T["model_custom"],
            placeholder="gemini-3.8-flash",
            **bind("custom_model"),
        )

    api_key = active_api_key()
    model = active_model()
    if not model:
        st.caption(T["model_needed"])
    elif st.session_state.model_choice == engine.CUSTOM_MODEL_OPTION:
        st.caption(T["model_custom_note"])

    if not st.session_state.api_key and api_key:
        st.caption(T["server_key_configured"])
    else:
        st.caption("[Google AI Studio →](https://aistudio.google.com/apikey)")

    st.button(T["clear"], key="btn_clear", use_container_width=True, on_click=reset_all)
    st.markdown(
        f'<div class="va-sb-foot">{T["clear_note"]}<br><br>{T["disclaimer"]}</div>',
        unsafe_allow_html=True,
    )

# ================================================================= header
st.markdown(
    f"""<div class="va-hero">{theme.hero_backdrop()}
  <div class="va-hero-inner">{theme.flag_svg(52)}
    <div>
      <p class="va-h1">VetAlign-AI — {T["app_title"]}</p>
      <p class="va-h1-sub"><span class="va-hero-tag">{T["tagline"]}</span>
         &nbsp;·&nbsp; {T["app_sub"]}</p>
    </div>
  </div>
  <div class="va-chips">
    <span class="va-chip s">{T["chip1"]}</span>
    <span class="va-chip g">{T["chip2"]}</span>
    <span class="va-chip">{T["chip3"]}</span>
    <span class="va-chip">{T["chip4"]}</span>
  </div>
</div>""",
    unsafe_allow_html=True,
)

result = st.session_state.result
if st.session_state.error:
    st.error(st.session_state.error)
if result and st.session_state.result_key != signature():
    st.markdown(f'<div class="va-stale">{T["stale"]}</div>', unsafe_allow_html=True)


# ============================================================ step 1: input
def render_voice_input() -> None:
    with st.container(border=True):
        st.subheader(T["audio_title"])
        st.caption(T["audio_help"])
        st.warning(T["audio_privacy"])
        st.checkbox(T["audio_consent"], **bind("audio_consent"))
        st.selectbox(
            T["audio_language"], audio.LANGUAGES,
            format_func=lambda value: T[AUDIO_LANGUAGE_LABELS[value]],
            **bind("audio_language"),
        )
        st.radio(
            T["audio_source"], ("record", "upload"), horizontal=True,
            format_func=lambda value: T[f"audio_{value}"], **bind("audio_source"),
        )
        # Do not instantiate capture/upload widgets before explicit consent.
        if st.session_state.audio_consent:
            source = st.session_state.audio_source
            key = f"audio_{source}_{st.session_state.audio_epoch}"
            if source == "record":
                st.audio_input(T["audio_record"], sample_rate=16000, key=key,
                               on_change=capture_changed, args=(key,))
            else:
                st.file_uploader(T["audio_upload"], type=["wav"], max_upload_size=10,
                                 key=key, on_change=capture_changed, args=(key,))
            st.caption(T["audio_replace_note"])
            st.button(T["audio_transcribe"], key="btn_transcribe", type="primary",
                      disabled=not st.session_state.audio_pending,
                      on_click=transcribe_capture, args=(key,))
        if st.session_state.audio_error:
            st.error(T[f"audio_err_{st.session_state.audio_error}"])
            st.caption(T["audio_released"])
        if st.session_state.voice_source:
            st.info(T["audio_review"])
            st.caption(f'{T["audio_time"]}: {st.session_state.transcription_elapsed}s')
            if st.session_state.transcription_backup:
                st.caption(f'{T["backup_used"]}: {st.session_state.transcription_backup}')
        if st.session_state.audio_pending or st.session_state.voice_source:
            st.button(T["audio_use_text"], key="btn_use_text", on_click=use_typed_input)


def render_step1() -> None:
    render_voice_input()
    with st.container(border=True):
        st.markdown(
            f'<p class="va-card-title">{T["bg_title"]}</p>'
            f'<p class="va-card-note">{T["privacy_note"]}</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'**{T["branch"]}** <span class="va-req">*</span>', unsafe_allow_html=True
        )
        st.markdown('<div class="va-branch">', unsafe_allow_html=True)
        branch_cols = st.columns(3)
        labels = {
            "Indian Army": T["army"],
            "Indian Navy": T["navy"],
            "Indian Air Force": T["airforce"],
        }
        for col, service in zip(branch_cols, SERVICES):
            col.button(
                labels[service],
                key=f"br_{service}",
                use_container_width=True,
                type="primary" if st.session_state.service == service else "secondary",
                on_click=set_service,
                args=(service,),
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        c1, c2, c3 = st.columns([4, 4, 2])
        c1.text_input(T["rank"], placeholder="Havildar", **bind("rank"))
        c2.text_input(T["trade"], placeholder="Logistics / Stores", **bind("trade"))
        c3.number_input(T["years"], min_value=0, max_value=45, step=1, **bind("years"))

        c4, c5 = st.columns(2)
        c4.text_input(T["education"], **bind("education"))
        c5.text_input(T["certs"], **bind("certifications"))
        st.text_input(T["location"], placeholder=T["location_ph"], **bind("location"))

        st.markdown(
            f'**{T["narrative"]}** <span class="va-req">*</span>', unsafe_allow_html=True
        )
        st.text_area(
            T["narrative"],
            height=150,
            placeholder=T["narrative_ph"],
            label_visibility="collapsed",
            **bind("duties"),
        )

        st.text_area(
            T["target"], height=90, placeholder=T["target_ph"], **bind("job_description")
        )
        if st.session_state.selected_job:
            st.caption(T["jobs_selected"])

        if st.session_state.voice_source:
            st.checkbox(T["audio_approve"], **bind("transcript_approved"))
        st.checkbox(T["consent"], **bind("consent"))

    st.write("")
    left, right = st.columns([6, 4])
    with left:
        st.caption(T["quick"])
        quick_cols = st.columns(len(DEMO_PROFILES))
        for col, name in zip(quick_cols, DEMO_PROFILES):
            short = name.split(" · ")[0] + " · " + name.split("(")[-1].rstrip(")")
            col.button(
                short,
                key=f"q_{name}",
                use_container_width=True,
                on_click=load_sample,
                args=(name,),
            )
    with right:
        if st.button(T["analyse"], key="btn_analyse", type="primary", use_container_width=True):
            st.session_state.error = ""
            if not st.session_state.consent:
                st.session_state.error = T["err_consent"]
            elif st.session_state.audio_pending or (
                st.session_state.voice_source and not st.session_state.transcript_approved
            ):
                st.session_state.error = T["audio_err_review"]
            elif not st.session_state.duties.strip():
                st.session_state.error = T["err_duties"]
            elif sum(len(str(value)) for value in form_values().values()) > engine.MAX_INPUT_CHARS:
                st.session_state.error = T["err_input_length"]
            elif not model:
                st.session_state.error = T["err_model"]
            else:
                payload = dict(form_values(), language=st.session_state.ui_lang)
                try:
                    with st.spinner("…"):
                        st.session_state.result = engine.generate(
                            api_key, model, payload, jobs=open_jobs()[0]
                        )
                    st.session_state.result_key = signature()
                    st.session_state.edited_profile = engine.profile_markdown(
                        st.session_state.result, payload
                    )
                    st.session_state.step = 2
                except engine.EngineError as exc:
                    st.session_state.error = str(exc)
            st.rerun()


# ======================================================= step 2: skills/fit
def render_matches(matches: list[dict]) -> None:
    """Job cards. Every employer/location/link value is copied from the dataset."""
    with st.container(border=True):
        st.markdown(
            f'<p class="va-card-title">{T["matches_title"]}</p>'
            f'<p class="va-card-note">{T["matches_sub"]}</p>',
            unsafe_allow_html=True,
        )
        source_note = T.get(f"jobs_source_{open_jobs()[2]}")
        if source_note:
            st.caption(source_note)
        if result.get("_discarded_matches"):
            st.warning(T["matches_discarded"].format(n=result["_discarded_matches"]))
        if not matches:
            st.info(T["no_jobs_data"] if open_jobs()[1] else T["no_matches"])
            return
        for col, match in zip(st.columns(len(matches)), matches):
            with col.container(border=True):
                st.markdown(f"**{match['title']}**")
                st.caption(f"{match['employer']} · {match['location']}")
                if match.get("is_demo"):
                    st.caption(f":orange[{T['demo_badge']}]")
                st.write(f"{T['why_fit']}: {match['reason']}")
                for skill in match.get("matched_skills", []):
                    st.markdown(
                        f'<div class="va-evidence">{escape(skill)}</div>', unsafe_allow_html=True
                    )
                for gap in match.get("gaps", []):
                    st.markdown(
                        f'<div class="va-gap">{T["to_check"]}: {escape(gap)}</div>',
                        unsafe_allow_html=True,
                    )
                for req in match.get("qualification_requirements", []):
                    st.caption(f'{T["employer_requires"]}: {req}')
                if match.get("contact"):
                    st.caption(f'{T["contact"]}: {match["contact"]}')
                if match.get("last_checked"):
                    st.caption(f'{T["last_checked"]}: {match["last_checked"]}')


def render_step2() -> None:
    if not result:
        st.info(T["no_result"])
        return

    matches = result.get("_matches") or []
    m = st.columns(5)
    m[0].metric(T["m_years"], st.session_state.years or "—")
    m[1].metric(T["m_facts"], len(result["_facts"]))
    m[2].metric(T["m_skills"], len(result["skills"]))
    m[3].metric(T["m_matches"], len(matches))
    m[4].metric(T["m_time"], f"{result['_elapsed']}s")
    st.write("")

    if result.get("_backup_used"):
        st.info(f'{T["backup_used"]}: {result["_model"]}')
    render_matches(matches)

    with st.container(border=True):
        st.markdown(
            f'<p class="va-card-title">{T["s2_title"]}</p>'
            f'<p class="va-card-note">{T["s2_sub"]}</p>',
            unsafe_allow_html=True,
        )

        left, right = st.columns(2, gap="large")
        with left:
            counts = (
                pd.DataFrame(result["skills"])["category"]
                .value_counts().rename_axis("Category").reset_index(name="Skills")
            )
            st.markdown(f"**{T['chart_skills']}**")
            st.altair_chart(
                alt.Chart(counts)
                .mark_bar(cornerRadiusEnd=4, color=theme.NAVY)
                .encode(
                    x=alt.X("Skills:Q", axis=alt.Axis(tickMinStep=1, title=None)),
                    y=alt.Y("Category:N", sort="-x", title=None),
                    tooltip=["Category", "Skills"],
                )
                .properties(height=max(160, 34 * len(counts))),
                use_container_width=True,
            )

        roles = result["role_suggestions"]
        with right:
            if roles:
                ev = pd.DataFrame(
                    {
                        "Role": [r["role"] for r in roles],
                        "Evidenced": [len(r.get("supported_by") or []) for r in roles],
                        "Gaps": [len(r.get("gaps") or []) for r in roles],
                    }
                ).melt("Role", var_name="Type", value_name="Count")
                st.markdown(f"**{T['chart_roles']}**")
                st.altair_chart(
                    alt.Chart(ev)
                    .mark_bar(cornerRadiusEnd=3)
                    .encode(
                        x=alt.X("Count:Q", axis=alt.Axis(tickMinStep=1, title=None)),
                        y=alt.Y("Role:N", title=None),
                        color=alt.Color(
                            "Type:N",
                            scale=alt.Scale(
                                domain=["Evidenced", "Gaps"],
                                range=[theme.INDIA_GREEN, theme.SAFFRON],
                            ),
                            legend=alt.Legend(orient="bottom", title=None),
                        ),
                        tooltip=["Role", "Type", "Count"],
                    )
                    .properties(height=max(160, 52 * len(roles))),
                    use_container_width=True,
                )
        st.caption(T["chart_note"])

        if roles:
            # Secondary to the job cards above, so collapsed by default.
            # Streamlit forbids nested expanders, hence headings per role.
            with st.expander(T["role_families"]):
                for r in roles:
                    st.markdown(f"**{r['role']}**")
                    st.write(r.get("why", ""))
                    for s in r.get("supported_by") or []:
                        st.markdown(
                            f'<div class="va-evidence">{T["evidenced"]}: {escape(s)}</div>',
                            unsafe_allow_html=True,
                        )
                    for g in r.get("gaps") or []:
                        st.markdown(
                            f'<div class="va-gap">{T["gap"]}: {escape(g)}</div>',
                            unsafe_allow_html=True,
                        )
                    for q in r.get("questions_to_confirm") or []:
                        st.caption(f'{T["confirm_emp"]}: {q}')

        checks = result.get("job_requirement_checks") or []
        if checks:
            st.markdown(f"**{T['jd_check']}**")
            st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)

    with st.expander(T["facts_title"]):
        st.dataframe(
            pd.DataFrame({"#": range(1, len(result["_facts"]) + 1), "Fact": result["_facts"]}),
            use_container_width=True, hide_index=True,
        )
        st.markdown(f"**{T['trace_title']}**")
        st.dataframe(
            pd.DataFrame(
                {
                    "Skill": [s["skill"] for s in result["skills"]],
                    "Category": [s["category"] for s in result["skills"]],
                    "From fact #": [
                        ", ".join(map(str, s["source_ids"])) or "unverified"
                        for s in result["skills"]
                    ],
                }
            ),
            use_container_width=True, hide_index=True,
        )
        for w in result.get("warnings", []):
            st.warning(w)


# ==================================================== step 3: application
def render_step3() -> None:
    if not result:
        st.info(T["no_result"])
        return

    with st.container(border=True):
        st.markdown(
            f'<p class="va-card-title">{T["s3_title"]}</p>'
            f'<p class="va-card-note">{T["s3_sub"]}</p>',
            unsafe_allow_html=True,
        )
        tab_profile, tab_interview = st.tabs([T["tab_profile"], T["tab_interview"]])

        with tab_profile:
            st.text_area(
                T["tab_profile"], height=420,
                label_visibility="collapsed",
                **bind("edited_profile"),
            )
            st.download_button(
                T["dl_pack"],
                st.session_state.edited_profile + "\n\n" + engine.shortlist_markdown(result),
                "vetalign_profile_and_matches.txt", "text/plain",
                type="primary", use_container_width=True,
            )
            d1, d2 = st.columns(2)
            d1.download_button(
                T["dl_txt"], st.session_state.edited_profile,
                "vetalign_application_profile.txt", "text/plain",
                use_container_width=True,
            )
            d2.download_button(
                T["dl_md"], st.session_state.edited_profile,
                "vetalign_application_profile.md", "text/markdown",
                use_container_width=True,
            )

        with tab_interview:
            iv = result["interview"]
            for label, items in (
                (T["behavioural"], iv.get("behavioural", [])),
                (T["functional"], iv.get("functional", [])),
            ):
                st.markdown(f"**{label}**")
                for i, q in enumerate(items, 1):
                    with st.expander(f"{i}. {q['question']}"):
                        st.write(q.get("answer_outline", ""))
                        for ph in q.get("placeholders", []):
                            st.markdown(
                                f'<div class="va-gap">{T["fill_in"]}: {escape(ph)}</div>',
                                unsafe_allow_html=True,
                            )
            st.markdown(f"**{T['action_plan']}**")
            for a in iv.get("action_plan", []):
                st.markdown(f"- {a}")
            st.download_button(
                T["dl_interview"], engine.interview_markdown(result),
                "vetalign_interview_guide.md", "text/markdown",
            )


# ================================================== browse all open jobs
def render_jobs_tab() -> None:
    """Every open job, browsable before (or without) analysing a profile."""
    jobs, error, source = open_jobs()
    with st.container(border=True):
        st.markdown(
            f'<p class="va-card-title">{T["jobs_title"]}</p>'
            f'<p class="va-card-note">{T["jobs_sub"]}</p>',
            unsafe_allow_html=True,
        )
        source_note = T.get(f"jobs_source_{source}")
        if source_note:
            st.caption(source_note)
        if not jobs:
            st.info(T["jobs_none"] if not error else T["no_jobs_data"])
            return

        c1, c2 = st.columns([3, 2])
        query = c1.text_input(T["jobs_search"], placeholder=T["jobs_search_ph"], key="jobs_query")
        cities = sorted({j.city_or_district for j in jobs})
        city = c2.selectbox(
            T["jobs_city"], [""] + cities, key="jobs_city",
            format_func=lambda value: value or T["jobs_city_all"],
        )

        needle = query.strip().lower()
        shown = [
            j for j in jobs
            if (not city or j.city_or_district == city)
            and (not needle or needle in " ".join(
                [j.title, j.employer, *j.required_skills, *j.preferred_skills]
            ).lower())
        ]
        if st.session_state.selected_job:
            st.success(T["jobs_used_note"])
        st.caption(T["jobs_count"].format(n=len(shown), total=len(jobs)))
        if not shown:
            st.info(T["jobs_no_filter_match"])
            return

    for job in shown:
        with st.container(border=True):
            head, action = st.columns([7, 3])
            with head:
                st.markdown(f"**{job.title}**")
                st.caption(f"{job.employer} · {job.city_or_district}")
                if job.is_demo:
                    st.caption(f":orange[{T['demo_badge']}]")
            with action:
                selected = st.session_state.selected_job == job.job_id
                st.button(
                    T["jobs_selected_btn"] if selected else T["jobs_use"],
                    key=f"use_{job.job_id}",
                    type="secondary" if selected else "primary",
                    use_container_width=True,
                    disabled=selected,
                    on_click=use_job,
                    args=(job.job_id,),
                )
            if job.required_skills:
                st.markdown(
                    f'**{T["jobs_required"]}:** ' + ", ".join(job.required_skills)
                )
            if job.preferred_skills:
                st.markdown(
                    f'**{T["jobs_preferred"]}:** ' + ", ".join(job.preferred_skills)
                )
            for req in job.qualification_requirements:
                st.caption(f'{T["employer_requires"]}: {req}')
            if job.contact:
                st.caption(f'{T["contact"]}: {job.contact}')
            if job.last_checked:
                st.caption(f'{T["last_checked"]}: {job.last_checked}')


tab_assist, tab_jobs = st.tabs([T["tab_assistant"], T["tab_jobs"]])
with tab_jobs:
    render_jobs_tab()

with tab_assist:
    {1: render_step1, 2: render_step2, 3: render_step3}[st.session_state.step]()

    # ============================================================ nav bar
    st.write("")
    nav_back, _, nav_next = st.columns([2, 6, 2])
    if st.session_state.step > 1:
        nav_back.button(
            T["back"], key="btn_back", use_container_width=True, on_click=go_to,
            args=(st.session_state.step - 1,),
        )
    if st.session_state.step == 2:
        nav_next.button(
            T["next"], key="btn_next", type="primary", use_container_width=True,
            on_click=go_to, args=(3,),
        )
    if st.session_state.step == 3:
        nav_next.button(T["restart"], key="btn_restart", use_container_width=True, on_click=reset_all)

st.markdown(
    f'<div class="va-foot">{T["disclaimer"]} VetAlign-AI drafts and suggests only — '
    "it does not certify qualification equivalence, decide eligibility or guarantee "
    "employment. Review every line before use. Sample profiles are fictional.</div>",
    unsafe_allow_html=True,
)
