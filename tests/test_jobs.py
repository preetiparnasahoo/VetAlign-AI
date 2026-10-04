"""Tests for the job dataset loader.

Run from the project root:  python -m pytest -q
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import jobs as jobs_module
from jobs import JobDataError, load_jobs


def write(tmp_path: Path, payload: dict) -> Path:
    target = tmp_path / "jobs.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def record(**overrides) -> dict:
    base = {
        "job_id": "T-001",
        "title": "Stores Supervisor",
        "employer": "Fictional Co",
        "required_skills": ["inventory management"],
        "preferred_skills": [],
        "qualification_requirements": [],
        "city_or_district": "Pune, Maharashtra",
        "application_url": "https://example.invalid/apply",
        "source_url": "https://example.invalid",
        "last_checked": "2026-09-28",
        "status": "open",
        "is_demo": True,
    }
    base.update(overrides)
    return base


# ----------------------------------------------------------- shipped dataset


def test_demo_dataset_loads():
    data = load_jobs()
    assert 10 <= len(data) <= 15, "plan calls for 10-15 curated records"
    assert data.warnings == [], f"shipped demo data should be clean: {data.warnings}"


def test_demo_dataset_is_entirely_fictional():
    """Guards against a real employer's link leaking into public demo data."""
    for job in load_jobs().jobs:
        assert job.is_demo is True, f"{job.job_id} is not flagged as demo"
        # Dummy contacts are allowed so the demo shows a route, but only on the
        # reserved domain: a real recruiter's details must never ship here.
        assert job.contact is None or ".example.invalid" in job.contact, (
            f"{job.job_id} carries a non-fictional contact detail"
        )
        for url in (job.application_url, job.source_url):
            assert ".example.invalid" in url, f"{job.job_id} points outside the reserved domain: {url}"


def test_demo_dataset_covers_the_three_template_scenarios():
    """Each required test scenario must have candidate records to match against."""
    skills = [" ".join(j.required_skills + [j.title]).lower() for j in load_jobs().open_jobs()]

    def count(*terms: str) -> int:
        return sum(1 for text in skills if any(t in text for t in terms))

    assert count("stock", "inventory", "stores", "warehouse") >= 3, "scenario 1: stores"
    assert count("transport", "fleet", "dispatch", "convoy", "route") >= 3, "scenario 1: transport"
    assert count("telecom", "communication", "troubleshoot", "radio", "helpdesk") >= 3, "scenario 2: signals"


def test_closed_jobs_are_excluded_from_shortlisting():
    data = load_jobs()
    closed = [j for j in data.jobs if not j.is_open]
    assert closed, "keep at least one closed record so status handling is exercised"
    open_ids = {j.job_id for j in data.open_jobs()}
    assert not open_ids & {j.job_id for j in closed}


def test_prompt_dict_withholds_links_and_contacts():
    """The model must not be able to echo a mangled or fabricated URL."""
    sent = load_jobs().jobs[0].prompt_dict()
    for leaked in ("application_url", "source_url", "contact", "employer", "is_demo"):
        assert leaked not in sent


# ------------------------------------------------------------- id resolution


def test_resolve_rejects_unknown_and_duplicate_ids():
    data = load_jobs()
    good = data.jobs[0].job_id
    resolved, rejected = data.resolve([good, "DEMO-999", good, ""])
    assert [j.job_id for j in resolved] == [good]
    assert rejected == ["DEMO-999", good, ""]


def test_resolve_handles_none_and_empty():
    data = load_jobs()
    assert data.resolve(None) == ([], [])
    assert data.resolve([]) == ([], [])


# --------------------------------------------------------------- bad input


def test_missing_file_raises():
    with pytest.raises(JobDataError, match="not found"):
        load_jobs("/no/such/file.json")


def test_invalid_json_raises(tmp_path):
    target = tmp_path / "jobs.json"
    target.write_text("{ not json", encoding="utf-8")
    with pytest.raises(JobDataError, match="not valid JSON"):
        load_jobs(target)


def test_wrong_shape_raises(tmp_path):
    with pytest.raises(JobDataError, match="'jobs' list"):
        load_jobs(write(tmp_path, {"jobs": "oops"}))


def test_duplicate_job_id_raises(tmp_path):
    path = write(tmp_path, {"jobs": [record(), record()]})
    with pytest.raises(JobDataError, match="Duplicate job_id"):
        load_jobs(path)


def test_missing_required_field_raises(tmp_path):
    bad = record()
    del bad["employer"]
    with pytest.raises(JobDataError, match="employer"):
        load_jobs(write(tmp_path, {"jobs": [bad]}))


def test_empty_required_skills_raises(tmp_path):
    path = write(tmp_path, {"jobs": [record(required_skills=[])]})
    with pytest.raises(JobDataError, match="required_skills"):
        load_jobs(path)


def test_empty_dataset_is_allowed_for_no_match_path(tmp_path):
    data = load_jobs(write(tmp_path, {"jobs": []}))
    assert data.is_empty and len(data) == 0


# --------------------------------------------------- non-fatal data problems


@pytest.mark.parametrize("hostile", ["javascript:alert(1)", "data:text/html,<script>", "ftp://x.invalid"])
def test_unsafe_url_scheme_is_stripped_not_rendered(tmp_path, hostile):
    data = load_jobs(write(tmp_path, {"jobs": [record(application_url=hostile)]}))
    assert data.jobs[0].application_url == ""
    assert any("application_url" in w for w in data.warnings)


def test_unknown_status_degrades_to_unknown(tmp_path):
    data = load_jobs(write(tmp_path, {"jobs": [record(status="maybe")]}))
    assert data.jobs[0].status == "unknown"
    assert not data.jobs[0].is_open


def test_unparseable_date_is_treated_as_stale(tmp_path):
    data = load_jobs(write(tmp_path, {"jobs": [record(last_checked="soon")]}))
    assert data.jobs[0].last_checked is None
    assert data.jobs[0].is_stale()


def test_old_job_is_stale_and_not_shortlisted(tmp_path):
    data = load_jobs(write(tmp_path, {"jobs": [record(last_checked="2026-01-01")]}))
    today = date(2026, 9, 28)
    assert data.jobs[0].is_stale(today)
    assert data.open_jobs(today) == []


def test_fresh_job_is_not_stale(tmp_path):
    data = load_jobs(write(tmp_path, {"jobs": [record(last_checked="2026-09-20")]}))
    today = date(2026, 9, 28)
    assert not data.jobs[0].is_stale(today)
    assert len(data.open_jobs(today)) == 1


def test_record_inherits_dataset_demo_flag(tmp_path):
    raw = record()
    del raw["is_demo"]
    data = load_jobs(write(tmp_path, {"is_demo": False, "jobs": [raw]}))
    assert data.jobs[0].is_demo is False


def test_maintainer_report_counts_and_flags_stale(tmp_path):
    from jobs import report
    code, text = report(today=date(2026, 10, 4))
    assert code == 0
    assert "shown to veterans now : 13" in text
    code, text = report(today=date(2026, 12, 31))
    assert "STALE" in text


def test_maintainer_report_rejects_broken_file(tmp_path):
    from jobs import report
    bad = tmp_path / "jobs.json"
    bad.write_text("{not json", encoding="utf-8")
    code, text = report(bad)
    assert code == 1 and text.startswith("NOT USABLE")
