"""Google Sheet job source: a non-technical volunteer maintains the list.

No network: urlopen is patched. Run from the project root:  python -m pytest -q
"""

from __future__ import annotations

import sys
from datetime import date
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import jobs
from jobs import JobDataError, fetch_jobs_csv, parse_jobs_csv

TODAY = date(2026, 10, 4)
HEADER = ("job_id,title,employer,required_skills,city_or_district,application_url,"
          "contact,last_checked,status,is_demo\n")


def row(job_id="S-1", title="Stores Lead", skills="stock audit; issue and receipt records",
        url="https://example.invalid/apply", status="open", checked="2026-10-03", demo=""):
    return f'{job_id},{title},Acme (fictional),{skills},"Pune, Maharashtra",{url},,{checked},{status},{demo}\n'


def test_template_csv_matches_the_json_demo_list():
    sheet = parse_jobs_csv((ROOT / "data" / "jobs_sheet_template.csv").read_text(encoding="utf-8"))
    assert [j.job_id for j in sheet.jobs] == [j.job_id for j in jobs.load_jobs().jobs]
    assert sheet.warnings == []


def test_semicolon_skills_become_a_list_and_rows_default_to_demo():
    job = parse_jobs_csv(HEADER + row()).jobs[0]
    assert job.required_skills == ["stock audit", "issue and receipt records"]
    assert job.is_demo is True
    assert job.source_url == job.application_url  # defaulted for Form rows


def test_real_listing_must_be_marked_explicitly():
    assert parse_jobs_csv(HEADER + row(demo="no")).jobs[0].is_demo is False


def test_bad_rows_are_skipped_with_a_reason_not_fatal():
    text = HEADER + row("S-1") + row("S-2", skills="") + row("S-3", status="") + row("S-1")
    data = parse_jobs_csv(text)
    assert [j.job_id for j in data.jobs] == ["S-1"]
    assert any("Row 3 skipped" in w for w in data.warnings)
    assert any("Row 4 skipped" in w for w in data.warnings)
    assert any("duplicate" in w for w in data.warnings)


def test_unsafe_link_is_hidden():
    job = parse_jobs_csv(HEADER + row(url="javascript:alert(1)")).jobs[0]
    assert job.application_url == ""


def test_unchecked_or_unapproved_form_rows_are_not_shown():
    # A Form submission has no last_checked/status until a volunteer reviews it.
    data = parse_jobs_csv(HEADER + row(checked="", status="unknown"))
    assert data.open_jobs(TODAY) == []


def test_google_form_style_headers_are_understood():
    text = ("Timestamp,Job title,Company,Skills required,City,Application link,Last checked,Status\n"
            '10/4/2026 9:00,Driver Trainer,Acme (fictional),driver training; road safety,Pune,'
            "https://example.invalid/a,2026-10-04,open\n")
    job = parse_jobs_csv(text).jobs[0]
    assert (job.title, job.employer, job.city_or_district) == ("Driver Trainer", "Acme (fictional)", "Pune")
    assert job.job_id == "SHEET-002"


def test_empty_sheet_is_an_error():
    with pytest.raises(JobDataError):
        parse_jobs_csv("")


def fake_urlopen(body: bytes):
    class Response(BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    return lambda request, timeout: Response(body)


def test_fetch_requires_https():
    with pytest.raises(JobDataError, match="https"):
        fetch_jobs_csv("http://docs.google.com/x.csv")


def test_fetch_parses_published_sheet():
    with patch("urllib.request.urlopen", fake_urlopen((HEADER + row()).encode())):
        assert len(fetch_jobs_csv("https://docs.google.com/x/pub?output=csv")) == 1


def test_fetch_network_failure_is_a_job_data_error():
    from urllib.error import URLError

    def boom(request, timeout):
        raise URLError("offline")

    with patch("urllib.request.urlopen", boom):
        with pytest.raises(JobDataError, match="Could not download"):
            fetch_jobs_csv("https://docs.google.com/x.csv")


def test_fetch_rejects_oversized_sheet():
    with patch("urllib.request.urlopen", fake_urlopen(b"x" * (jobs.MAX_SHEET_BYTES + 5))):
        with pytest.raises(JobDataError, match="1 MB"):
            fetch_jobs_csv("https://docs.google.com/x.csv")


def test_maintainer_report_reads_a_csv_file(tmp_path):
    path = tmp_path / "jobs.csv"
    path.write_text(HEADER + row() + row("S-2", skills=""), encoding="utf-8")
    code, text = jobs.report(path, today=TODAY)
    assert code == 0
    assert "shown to veterans now : 1" in text and "Row 3 skipped" in text
