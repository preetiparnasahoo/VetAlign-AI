"""Tests for transient-failure handling in the Gemini call.

The free tier returns HTTP 503 "high demand" intermittently; this was observed
during live testing on 28 September 2026. These tests pin the retry behaviour
and the wording of user-facing errors. No network calls are made.

Run from the project root:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import career_engine as engine
from career_engine import EngineError

FORM = {
    "service": "Indian Army",
    "rank": "Havildar",
    "trade": "Stores",
    "years": 16,
    "education": "Class 12",
    "certifications": "",
    "duties": "I supervised a team of 12 personnel. I maintained stock registers.",
    "job_description": "",
    "language": "English",
}

VALID_JSON = """{
  "skills": [{"skill": "inventory management", "category": "Logistics & Inventory",
              "civilian_wording": "Inventory management", "source_ids": [2],
              "explanation": "Maintained stock registers."}],
  "role_suggestions": [{"role": "Warehouse Supervisor", "why": "Stock and team experience.",
                        "supported_by": ["Maintained stock registers."], "gaps": [],
                        "questions_to_confirm": []}],
  "profile": {"summary": "Stores supervisor.",
              "experience_bullets": [{"text": "Supervised 12 personnel.", "source_ids": [1]}]},
  "interview": {"behavioural": [], "functional": [], "action_plan": []}
}"""


class FakeServerError(Exception):
    """Stands in for google.genai ServerError, which carries a numeric code."""

    def __init__(self, message: str, code: int = 503):
        super().__init__(message)
        self.code = code


def ok_response():
    response = MagicMock()
    response.text = VALID_JSON
    return response


def client_returning(*side_effects):
    """Build a patched genai.Client whose generate_content follows side_effects."""
    client = MagicMock()
    client.models.generate_content.side_effect = list(side_effects)
    return client


# --------------------------------------------------------- transient detection


@pytest.mark.parametrize(
    "message",
    [
        "503 UNAVAILABLE. This model is currently experiencing high demand.",
        "500 INTERNAL. Internal error encountered.",
        "The model is overloaded. Please try again later.",
    ],
)
def test_overload_errors_are_classified_transient(message):
    assert engine._is_transient(Exception(message))


def test_numeric_code_alone_is_enough():
    assert engine._is_transient(FakeServerError("something opaque", code=503))


@pytest.mark.parametrize(
    "message",
    [
        "401 UNAUTHENTICATED. API key not valid.",
        "404 NOT_FOUND. This model is no longer available to new users.",
        "429 RESOURCE_EXHAUSTED. Quota exceeded.",
    ],
)
def test_permanent_errors_are_not_retried(message):
    assert not engine._is_transient(Exception(message))


# ------------------------------------------------------------------- retrying


def test_transient_failure_is_retried_and_can_succeed():
    """A 503 followed by success must produce a result, not an error."""
    fake = client_returning(FakeServerError("503 high demand"), ok_response())
    with patch("career_engine.genai.Client", return_value=fake), patch(
        "career_engine.time.sleep"
    ) as slept:
        result = engine.generate("key", "gemini-3.8-flash", FORM)
    assert result["skills"], "should return the successful second attempt"
    assert fake.models.generate_content.call_count == 2
    assert slept.called, "must back off before retrying"


def test_retries_stop_at_the_configured_limit_plus_one_backup_try():
    fake = client_returning(*[FakeServerError("503 high demand")] * (engine.MAX_ATTEMPTS + 1))
    with patch("career_engine.genai.Client", return_value=fake), patch("career_engine.time.sleep"):
        with pytest.raises(EngineError, match="backup model was busy too"):
            engine.generate("key", "gemini-3.8-flash", FORM)
    calls = fake.models.generate_content.call_args_list
    assert len(calls) == engine.MAX_ATTEMPTS + 1
    assert [c.kwargs["model"] for c in calls] == ["gemini-3.8-flash"] * engine.MAX_ATTEMPTS + [
        engine.BACKUP_MODEL
    ]


def test_backup_model_rescues_a_busy_primary_and_is_reported():
    fake = client_returning(*[FakeServerError("503 high demand")] * engine.MAX_ATTEMPTS,
                            ok_response())
    with patch("career_engine.genai.Client", return_value=fake), patch("career_engine.time.sleep"):
        result = engine.generate("key", "gemini-3.8-flash", FORM)
    assert result["_model"] == engine.BACKUP_MODEL
    assert result["_backup_used"] is True


def test_no_backup_switch_for_permanent_errors():
    fake = client_returning(Exception("429 RESOURCE_EXHAUSTED quota"))
    with patch("career_engine.genai.Client", return_value=fake), patch("career_engine.time.sleep"):
        with pytest.raises(EngineError, match="quota"):
            engine.generate("key", "gemini-3.8-flash", FORM)
    assert fake.models.generate_content.call_count == 1


def test_backup_is_never_the_same_model():
    assert engine.backup_model("gemini-3.8-flash") == engine.BACKUP_MODEL
    assert engine.backup_model(engine.BACKUP_MODEL) != engine.BACKUP_MODEL


def test_normal_result_reports_primary_model():
    fake = client_returning(ok_response())
    with patch("career_engine.genai.Client", return_value=fake):
        result = engine.generate("key", "gemini-3.8-flash", FORM)
    assert result["_model"] == "gemini-3.8-flash" and result["_backup_used"] is False


def test_permanent_failure_is_not_retried():
    """Retrying a rejected key wastes the user's time and the quota."""
    fake = client_returning(Exception("401 UNAUTHENTICATED. API key not valid."))
    with patch("career_engine.genai.Client", return_value=fake), patch("career_engine.time.sleep"):
        with pytest.raises(EngineError, match="key was rejected"):
            engine.generate("key", "gemini-3.8-flash", FORM)
    assert fake.models.generate_content.call_count == 1


def test_success_on_first_attempt_does_not_sleep():
    fake = client_returning(ok_response())
    with patch("career_engine.genai.Client", return_value=fake), patch(
        "career_engine.time.sleep"
    ) as slept:
        engine.generate("key", "gemini-3.8-flash", FORM)
    assert not slept.called


# ------------------------------------------------------------ message honesty


def test_overload_is_not_described_as_a_connection_problem():
    """The original bug: a provider 503 was reported as the user's connection."""
    message = engine._friendly_error(FakeServerError("503 UNAVAILABLE. high demand"))
    lowered = message.lower()
    assert "busy" in lowered
    assert "temporary" in lowered
    # Must not send the user off to debug their own network.
    assert "check your internet" not in lowered
    assert "check your connection" not in lowered


def test_overload_message_says_answers_are_kept():
    message = engine._friendly_error(FakeServerError("503 high demand"))
    assert "answers are kept" in message.lower()


def test_model_unavailable_message_does_not_blame_the_key():
    message = engine._friendly_error(Exception("404 NOT_FOUND. no longer available to new users"))
    assert "not necessarily mean the key is invalid" in message


def test_genuine_connection_failure_still_mentions_the_connection():
    message = engine._friendly_error(Exception("Failed to establish a new connection"))
    assert "internet connection" in message.lower()


def test_no_error_message_leaks_the_api_key():
    secret = "AQ.SuperSecretValue123"
    for exc in (
        Exception(f"401 UNAUTHENTICATED key={secret}"),
        FakeServerError(f"503 high demand key={secret}"),
        Exception(f"unmapped failure key={secret}"),
    ):
        assert secret not in engine._friendly_error(exc)


# --------------------------------------------------------------- guard rails


def test_missing_api_key_fails_before_any_network_call():
    with patch("career_engine.genai.Client") as client:
        with pytest.raises(EngineError, match="No API key"):
            engine.generate("", "gemini-3.8-flash", FORM)
    assert not client.called


def test_empty_narrative_fails_before_any_network_call():
    with patch("career_engine.genai.Client") as client:
        with pytest.raises(EngineError, match="describe your service duties"):
            engine.generate("key", "gemini-3.8-flash", dict(FORM, duties="   "))
    assert not client.called


def test_empty_model_response_is_reported_clearly():
    blank = MagicMock()
    blank.text = ""
    with patch("career_engine.genai.Client", return_value=client_returning(blank)):
        with pytest.raises(EngineError, match="empty response"):
            engine.generate("key", "gemini-3.8-flash", FORM)
