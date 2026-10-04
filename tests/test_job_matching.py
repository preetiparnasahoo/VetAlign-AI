"""Grounded job matching: the model may only pick job IDs it was offered.

Employer names, locations, links and contacts must be copied from the dataset,
never taken from model output. The Gemini client is patched: no network.

Run from the project root:  python -m pytest -q
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import career_engine as engine
import jobs

FORM = {
    "service": "Indian Army",
    "rank": "Havildar",
    "trade": "Stores",
    "years": 15,
    "education": "",
    "certifications": "",
    "duties": "Handled stores for a battalion. Coordinated transport. Trained 40 jawans.",
    "location": "Pune, Maharashtra",
    "job_description": "",
    "language": "English",
}
TODAY = date(2026, 10, 3)


@pytest.fixture(scope="module")
def offered():
    return jobs.load_jobs().open_jobs(TODAY)


def payload(matches):
    return {
        "skills": [{"skill": "inventory management", "category": "Logistics & Inventory",
                    "civilian_wording": "Inventory management", "source_ids": [4],
                    "explanation": "Handled stores."}],
        "role_suggestions": [{"role": "Warehouse Supervisor", "why": "Stores.",
                              "supported_by": [], "gaps": [], "questions_to_confirm": []}],
        "job_matches": matches,
        "profile": {"headline": "Logistics & inventory supervisor", "summary": "Stores lead.",
                    "experience_bullets": [{"text": "Handled stores.", "source_ids": [4]}]},
        "interview": {"behavioural": [], "functional": [], "action_plan": []},
    }


def match(job_id, **extra):
    return dict({"job_id": job_id, "reason": "Stores and team skills.",
                 "matched_skills": ["inventory management"], "gaps": [],
                 "source_ids": [4]}, **extra)


def run(matches, offered_jobs):
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(text=json.dumps(payload(matches)))
    with patch("career_engine.genai.Client", return_value=client):
        result = engine.generate("key", "model", FORM, jobs=offered_jobs)
    return result, client.models.generate_content.call_args.kwargs["contents"]


def test_dataset_covers_the_template_demo_trio(offered):
    titles = " ".join(j.title.lower() for j in offered)
    for kind in ("warehouse", "security", "driving"):
        assert kind in titles


def test_closed_job_is_never_offered(offered):
    assert "DEMO-013" not in {j.job_id for j in offered}


def test_prompt_lists_offered_ids_and_mapping_but_not_links(offered):
    _, prompt = run([], offered)
    for job in offered:
        assert job.job_id in prompt
        assert job.application_url not in prompt
        assert job.employer not in prompt
    assert "signals / radio / line" in prompt and "telecom / IT support" in prompt
    assert "SKILLS, not by title" in prompt
    assert "Pune, Maharashtra" in prompt


def test_valid_matches_get_details_copied_from_dataset(offered):
    result, _ = run([match("DEMO-001", employer="Fake Corp", application_url="javascript:x"),
                     match("DEMO-011"), match("DEMO-014")], offered)
    ids = [m["job_id"] for m in result["_matches"]]
    assert ids == ["DEMO-001", "DEMO-011", "DEMO-014"]
    first = result["_matches"][0]
    record = jobs.load_jobs().by_id("DEMO-001")
    assert first["employer"] == record.employer
    assert first["application_url"] == record.application_url
    assert first["contact"] == record.contact
    assert first["is_demo"] is True
    assert result["_jobs_offered"] == len(offered)


@pytest.mark.parametrize("bad", [
    match("DEMO-999"),                      # invented
    match("DEMO-013"),                      # closed, not offered
    match("DEMO-001", source_ids=[]),       # no evidence
    match("DEMO-001", source_ids=[99]),     # out-of-range evidence
    match("DEMO-001", source_ids=[True]),   # bool is not a fact id
    match("DEMO-001", reason="  "),         # no reason
    "DEMO-001",                             # not an object
])
def test_unsupported_matches_are_dropped_with_a_warning(offered, bad):
    result, _ = run([bad], offered)
    assert result["_matches"] == []
    assert any("discarded" in w for w in result["warnings"])


def test_duplicates_are_dropped_and_list_is_capped_at_three(offered):
    ids = ["DEMO-001", "DEMO-001", "DEMO-002", "DEMO-003", "DEMO-004"]
    result, _ = run([match(i) for i in ids], offered)
    assert [m["job_id"] for m in result["_matches"]] == ["DEMO-001", "DEMO-002", "DEMO-003"]


def test_zero_matches_is_valid_and_has_no_warning(offered):
    result, _ = run([], offered)
    assert result["_matches"] == []
    assert not any("discarded" in w for w in result["warnings"])


def test_missing_job_matches_key_is_tolerated(offered):
    data = payload([])
    del data["job_matches"]
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(text=json.dumps(data))
    with patch("career_engine.genai.Client", return_value=client):
        result = engine.generate("key", "model", FORM, jobs=offered)
    assert result["_matches"] == []


def test_without_jobs_the_prompt_asks_for_no_matches():
    result, prompt = run([match("DEMO-001")], [])
    assert "none supplied" in prompt
    assert result["_matches"] == []


def test_job_list_does_not_count_against_the_input_limit(offered):
    # ~11k-char prompt alone: under the 16k applicant limit, over it with jobs added.
    form = dict(FORM, duties=("Maintained stock ledgers. " * 300)[:4000])
    assert len(engine._build_prompt(form, engine.build_facts(form))) < engine.MAX_INPUT_CHARS * 2
    assert len(engine._build_prompt(form, engine.build_facts(form), offered)) > engine.MAX_INPUT_CHARS * 2
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(text=json.dumps(payload([])))
    with patch("career_engine.genai.Client", return_value=client):
        engine.generate("key", "model", form, jobs=offered)


def test_shortlist_export_labels_demo_and_includes_routes(offered):
    result, _ = run([match("DEMO-014", gaps=["Civilian licence class not stated"])], offered)
    text = engine.shortlist_markdown(result)
    record = jobs.load_jobs().by_id("DEMO-014")
    assert record.title in text and record.employer in text
    assert "FICTIONAL DEMO LISTING" in text
    assert record.application_url in text and record.contact in text
    assert "Civilian licence class not stated" in text
    assert "Valid civilian driving licence" in text


def test_shortlist_export_handles_no_matches():
    assert "No listed job matched" in engine.shortlist_markdown({"_matches": []})


def test_profile_shows_preferred_location():
    data = payload([])
    text = engine.profile_markdown(data, FORM)
    assert "Preferred work location: Pune, Maharashtra" in text


def test_prompt_asks_for_three_matches_when_supported_and_defence_licence_wording(offered):
    _, prompt = run([], offered)
    assert "Return 3 job_matches whenever 3 listed jobs" in prompt
    assert "source_ids are APPLICANT FACTS numbers" in prompt
    assert '"defence-issued"' in prompt


def test_discarded_match_count_is_exposed_for_the_ui(offered):
    result, _ = run([match("DEMO-999"), match("DEMO-001")], offered)
    assert result["_discarded_matches"] == 1
    assert [m["job_id"] for m in result["_matches"]] == ["DEMO-001"]
