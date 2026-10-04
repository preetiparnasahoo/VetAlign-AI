"""Tests for the "Browse open jobs" tab: listing, filtering and picking a job.

The sheet download is patched to fail so every test uses the built-in demo list.
"""

from unittest.mock import patch

import pytest
import streamlit as st

import jobs as job_data
from test_app_state import run_app
from i18n import STRINGS

EN = STRINGS["English"]


@pytest.fixture(autouse=True)
def demo_jobs_only():
    st.cache_resource.clear()
    with patch("jobs.fetch_jobs_csv", side_effect=job_data.JobDataError("offline")):
        yield
    st.cache_resource.clear()


def demo_open_jobs():
    return job_data.load_jobs().open_jobs()


def use_buttons(at):
    return [b for b in at.button if str(b.key).startswith("use_")]


def test_tab_lists_every_open_job_without_analysis():
    at = run_app()
    assert not at.exception, at.exception
    assert [t.label for t in at.tabs] == [EN["tab_assistant"], EN["tab_jobs"]]
    expected = demo_open_jobs()
    assert {b.key for b in use_buttons(at)} == {f"use_{j.job_id}" for j in expected}
    assert "use_DEMO-013" not in {b.key for b in use_buttons(at)}  # closed listing
    assert at.session_state.result is None


def test_job_cards_keep_contact_without_apply_buttons():
    at = run_app()
    assert not at.exception, at.exception
    assert any(job.application_url for job in demo_open_jobs())
    assert not at.get("link_button")
    text = " ".join(c.value for c in at.caption)
    for job in demo_open_jobs():
        if job.contact:
            assert job.contact in text
    assert use_buttons(at)


def test_search_filters_by_skill_or_title():
    at = run_app()
    at.text_input(key="jobs_query").set_value("driving").run()
    assert [b.key for b in use_buttons(at)] == ["use_DEMO-014"]
    at.text_input(key="jobs_query").set_value("no such job xyz").run()
    assert not use_buttons(at)
    assert any(EN["jobs_no_filter_match"] in i.value for i in at.info)


def test_city_filter():
    at = run_app()
    city = demo_open_jobs()[0].city_or_district
    at.selectbox(key="jobs_city").set_value(city).run()
    wanted = {f"use_{j.job_id}" for j in demo_open_jobs() if j.city_or_district == city}
    assert {b.key for b in use_buttons(at)} == wanted


def test_use_job_fills_target_role_and_returns_to_step_one():
    at = run_app()
    at.session_state.step = 2
    at.button(key="use_DEMO-014").click().run()
    assert not at.exception, at.exception
    job = next(j for j in demo_open_jobs() if j.job_id == "DEMO-014")
    assert at.session_state.step == 1
    assert at.session_state.job_description == job.target_text()
    assert at.text_area(key="w_job_description").value == job.target_text()
    assert at.button(key="use_DEMO-014").disabled
    assert any(EN["jobs_used_note"] in s.value for s in at.success)


def test_editing_target_role_clears_selection():
    at = run_app()
    at.button(key="use_DEMO-014").click().run()
    at.text_area(key="w_job_description").set_value("Something else").run()
    assert at.session_state.selected_job is None
    assert not at.button(key="use_DEMO-014").disabled


def test_loading_a_sample_profile_keeps_the_selected_job():
    at = run_app()
    at.button(key="use_DEMO-014").click().run()
    sample = next(b.key for b in at.button if str(b.key).startswith("q_"))
    at.button(key=sample).click().run()
    job = next(j for j in demo_open_jobs() if j.job_id == "DEMO-014")
    assert at.session_state.job_description == job.target_text()
    assert at.session_state.selected_job == "DEMO-014"
    assert at.session_state.duties  # the sample itself was loaded


def test_target_text_contains_listing_details():
    job = next(j for j in demo_open_jobs() if j.job_id == "DEMO-014")
    text = job.target_text()
    assert job.title in text and job.employer in text
    assert all(skill in text for skill in job.required_skills)
