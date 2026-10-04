"""Wizard tests for matched-role cards, location and the combined download.

The engine is patched; these check rendering and state, not model quality.
"""

from unittest.mock import patch

import pytest
import streamlit as st

from test_app_state import run_app, fill_minimum, press_analyse, FAKE_RESULT
from i18n import STRINGS

EN = STRINGS["English"]


@pytest.fixture(autouse=True)
def fresh_job_cache():
    """open_jobs() is cached per process; each test must load its own list."""
    st.cache_resource.clear()
    yield
    st.cache_resource.clear()

MATCH = {
    "job_id": "DEMO-014", "reason": "Trained 40 jawans; road safety briefings.",
    "matched_skills": ["driver training"], "gaps": ["Civilian licence class not stated"],
    "source_ids": [1], "title": "Driving Instructor (Light and Heavy Vehicles)",
    "employer": "Sarathi Motor Training School (fictional)", "location": "Pune, Maharashtra",
    "qualification_requirements": ["Valid civilian driving licence"],
    "application_url": "https://sarathi-motor.example.invalid/careers/driving-instructor",
    "source_url": "https://sarathi-motor.example.invalid/careers",
    "contact": "hr@sarathi-motor.example.invalid (fictional)",
    "last_checked": "2026-10-03", "is_demo": True,
}


def analysed(result):
    at = fill_minimum(run_app())
    with patch("career_engine.generate", return_value=result) as generate, patch(
        "career_engine.profile_markdown", return_value="# Draft profile"
    ):
        press_analyse(at)
    assert not at.exception, at.exception
    return at, generate


def test_open_jobs_are_passed_to_the_engine():
    _, generate = analysed(dict(FAKE_RESULT, _matches=[]))
    offered = generate.call_args.kwargs["jobs"]
    ids = {job.job_id for job in offered}
    assert "DEMO-014" in ids and "DEMO-013" not in ids


def test_matches_render_with_demo_label_and_contact_without_apply_button():
    at, _ = analysed(dict(FAKE_RESULT, _matches=[MATCH]))
    assert at.session_state.step == 2
    text = " ".join(str(el.value) for el in [*at.markdown, *at.caption])
    assert MATCH["title"] in text and MATCH["employer"] in text
    assert EN["demo_badge"] in text
    assert MATCH["contact"] in text
    assert not at.get("link_button")


def test_no_matches_shows_honest_message():
    at, _ = analysed(dict(FAKE_RESULT, _matches=[]))
    assert any(EN["no_matches"] in i.value for i in at.info)


def test_old_results_without_matches_still_render():
    at, _ = analysed(FAKE_RESULT)
    assert any(EN["no_matches"] in i.value for i in at.info)


def test_location_survives_navigation_and_keeps_transcript_approval():
    at = run_app()
    at.text_input(key="w_location").set_value("Pune").run()
    at.session_state.voice_source = True
    at.session_state.transcript_approved = True
    at.run()
    at.text_input(key="w_location").set_value("Pune, Maharashtra").run()
    assert at.session_state.transcript_approved is True
    assert at.session_state.location == "Pune, Maharashtra"


def test_step_three_offers_combined_pack_download():
    at, _ = analysed(dict(FAKE_RESULT, _matches=[MATCH]))
    at.button(key="btn_next").click().run()
    assert not at.exception, at.exception
    labels = [str(el.proto.label) for el in at.get("download_button")]
    assert EN["dl_pack"] in labels



def test_backup_model_use_is_stated_on_step_two():
    at, _ = analysed(dict(FAKE_RESULT, _matches=[], _model="gemini-3.5-flash", _backup_used=True))
    assert any(EN["backup_used"] in i.value and "gemini-3.5-flash" in i.value for i in at.info)


def test_no_backup_notice_normally():
    at, _ = analysed(dict(FAKE_RESULT, _matches=[]))
    assert not any(EN["backup_used"] in i.value for i in at.info)


def test_discarded_matches_warning_shows_beside_cards():
    at, _ = analysed(dict(FAKE_RESULT, _matches=[MATCH], _discarded_matches=1))
    assert any("1 suggested match(es) were removed" in w.value for w in at.warning)


def test_role_families_are_collapsed_into_one_section():
    at, _ = analysed(dict(FAKE_RESULT, _matches=[MATCH]))
    labels = [e.label for e in at.expander]
    assert EN["role_families"] in labels
    assert "Warehouse Supervisor" not in labels


def test_sheet_failure_falls_back_to_demo_list_and_says_so(monkeypatch):
    import jobs as job_data
    monkeypatch.setenv("JOBS_SHEET_CSV_URL", "https://docs.google.com/x.csv")

    def broken(url):
        raise job_data.JobDataError("offline")

    with patch("jobs.fetch_jobs_csv", broken):
        at, generate = analysed(dict(FAKE_RESULT, _matches=[MATCH]))
    offered = generate.call_args.kwargs["jobs"]
    assert "DEMO-014" in {j.job_id for j in offered}
    assert any(EN["jobs_source_demo_fallback"] in c.value for c in at.caption)


def test_live_sheet_jobs_are_offered_when_configured(monkeypatch):
    import jobs as job_data
    monkeypatch.setenv("JOBS_SHEET_CSV_URL", "https://docs.google.com/x.csv")
    sheet = job_data.parse_jobs_csv(
        "job_id,title,employer,required_skills,city_or_district,application_url,last_checked,status\n"
        'S-9,Stores Lead,Acme (fictional),stock audit,Pune,https://e.invalid/a,2026-10-03,open\n')
    with patch("jobs.fetch_jobs_csv", return_value=sheet):
        at, generate = analysed(dict(FAKE_RESULT, _matches=[MATCH]))
    assert [j.job_id for j in generate.call_args.kwargs["jobs"]] == ["S-9"]
    assert any(EN["jobs_source_sheet"] in c.value for c in at.caption)
