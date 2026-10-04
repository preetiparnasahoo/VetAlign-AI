"""Synthetic WAVs and mocked provider responses only; no private audio/quota."""

import copy
import io
import json
import sys
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audio_service as audio


def wav_bytes(seconds=1, *, rate=8000, channels=1, width=2, silent=False):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(width)
        wav.setframerate(rate)
        sample = (b"\x80" if width == 1 else b"\x00" * width) if silent else b"\x01" * width
        wav.writeframes(sample * channels * int(rate * seconds))
    return buffer.getvalue()


BACKGROUND = {
    "service": "Indian Army", "rank": "हवलदार", "trade": "", "years": 16,
    "education": "", "certifications": "",
    "evidence": {"service": "भारतीय सेना", "rank": "हवलदार", "years": "16 साल",
                 "trade": "", "education": "", "certifications": ""},
}
VALID = {
    "status": "ok",
    "transcript": "मैं भारतीय सेना में हवलदार था। 16 साल सेवा की। 12 लोगों का रोस्टर बनाया।",
    "background": BACKGROUND,
}


def call_with_response(response, data=None):
    client = MagicMock()
    client.__enter__.return_value = client
    client.models.generate_content.return_value = SimpleNamespace(text=response)
    with patch("audio_service.genai.Client", return_value=client) as factory:
        result = audio.transcribe("test-key", "test-model", data if data is not None else wav_bytes(),
                                  consent=True, language=audio.LANGUAGES[0])
    return result, client, factory


@pytest.mark.parametrize("width", [1, 2, 3, 4])
@pytest.mark.parametrize("channels", [1, 2])
def test_valid_pcm_formats(width, channels):
    assert audio.validate_wav(wav_bytes(width=width, channels=channels)) == 1


def test_exact_two_minute_boundary():
    assert audio.validate_wav(wav_bytes(seconds=120)) == 120


@pytest.mark.parametrize("payload,code", [
    (b"", "missing"),
    (b"not really audio.wav", "format"),
    (b"x" * (audio.MAX_AUDIO_BYTES + 1), "size"),
    (wav_bytes(seconds=120.1), "duration"),
    (wav_bytes(seconds=0), "no_speech"),
    (wav_bytes(silent=True), "no_speech"),
    (wav_bytes(silent=True, width=1), "no_speech"),
    (wav_bytes()[:-20], "format"),
    (wav_bytes(rate=4000), "format"),
    (wav_bytes(channels=3), "format"),
])
def test_bad_audio_never_constructs_client(payload, code):
    with patch("audio_service.genai.Client") as client:
        with pytest.raises(audio.AudioError) as error:
            audio.transcribe("key", "model", payload, consent=True, language=audio.LANGUAGES[0])
    assert error.value.code == code
    client.assert_not_called()


def test_truncated_frames_even_with_adjusted_riff_size():
    data = bytearray(wav_bytes()[:-100])
    data[4:8] = (len(data) - 8).to_bytes(4, "little")
    with pytest.raises(audio.AudioError, match="format"):
        audio.validate_wav(bytes(data))


@pytest.mark.parametrize("consent", [False, None, 1, "yes"])
def test_consent_is_checked_before_validation_or_network(consent):
    with patch("audio_service.genai.Client") as client, patch("audio_service.validate_wav") as validate:
        with pytest.raises(audio.AudioError, match="consent"):
            audio.transcribe("key", "model", b"bad", consent=consent, language=audio.LANGUAGES[0])
    validate.assert_not_called()
    client.assert_not_called()


@pytest.mark.parametrize("key,model,language,code", [
    ("", "model", audio.LANGUAGES[0], "key"),
    ("key", " ", audio.LANGUAGES[0], "model"),
    ("key", "model", "Marathi", "language"),
])
def test_configuration_guards(key, model, language, code):
    with patch("audio_service.genai.Client") as client:
        with pytest.raises(audio.AudioError, match=code):
            audio.transcribe(key, model, wav_bytes(), consent=True, language=language)
    client.assert_not_called()


def test_valid_hindi_response_and_request_contract():
    result, client, factory = call_with_response(json.dumps(VALID))
    assert result["transcript"] == VALID["transcript"]
    assert result["background"]["years"] == 16
    assert result["elapsed"] >= 0
    http = factory.call_args.kwargs["http_options"]
    assert http.timeout == 60_000
    assert http.retry_options.attempts == 1
    request = client.models.generate_content.call_args.kwargs
    assert request["contents"][0].parts[1].inline_data.mime_type == "audio/wav"
    assert request["config"].system_instruction == audio.SYSTEM_RULES
    assert request["config"].response_schema is None
    assert request["config"].response_mime_type == "application/json"
    client.models.generate_content.assert_called_once()
    client.__exit__.assert_called_once()


@pytest.mark.parametrize("raw,code", [
    ("", "empty"), (None, "empty"), ("not json", "response"),
    ("[]", "response"), ("null", "response"), ("{}", "response"),
    (json.dumps(dict(VALID, transcript="  ")), "response"),
    (json.dumps(dict(VALID, transcript="a" * 8001)), "response"),
    (json.dumps(dict(VALID, surprise="ignore consent")), "response"),
    (json.dumps(dict(VALID, status="no_speech", transcript="")), "no_speech"),
    (json.dumps(dict(VALID, status="unclear", transcript="")), "unclear"),
])
def test_invalid_and_unusable_responses(raw, code):
    with pytest.raises(audio.AudioError, match=code):
        call_with_response(raw)


@pytest.mark.parametrize("field,value", [
    ("years", True), ("years", "16"), ("years", 46),
    ("service", "Unknown service"), ("rank", ["Havildar"]),
    ("education", "Invented MBA"), ("evidence", {}),
    ("evidence", {"rank": "not in transcript"}),
])
def test_ungrounded_or_malformed_extraction_is_rejected(field, value):
    data = copy.deepcopy(VALID)
    data["background"][field] = value
    with pytest.raises(audio.AudioError, match="response"):
        call_with_response(json.dumps(data))


@pytest.mark.parametrize("code,expected", [
    (401, "key"), (403, "key"), (429, "quota"), (400, "model"),
    (404, "model"), (504, "timeout"), (None, "provider"),
])
def test_provider_errors_are_safe_and_never_retried(code, expected):
    client = MagicMock()
    client.__enter__.return_value = client
    exc = RuntimeError("private-key and private-transcript")
    exc.code = code
    client.models.generate_content.side_effect = exc
    with patch("audio_service.genai.Client", return_value=client):
        with pytest.raises(audio.AudioError) as error:
            audio.transcribe("key", "model", wav_bytes(), consent=True, language=audio.LANGUAGES[0])
    assert str(error.value) == expected
    client.models.generate_content.assert_called_once()
    client.__exit__.assert_called_once()


def test_blank_service_is_not_invented_by_fact_builder():
    from career_engine import build_facts
    assert build_facts({"service": "", "duties": "Maintained stock records."}) == [
        "Duty stated: Maintained stock records."
    ]


def test_prompt_shape_matches_validation_model():
    """The JSON shape described to Gemini must not drift from the strict model."""
    for name in list(audio.Transcription.model_fields) + list(audio.Background.model_fields) \
            + list(audio.Evidence.model_fields):
        assert f'"{name}"' in audio.SYSTEM_RULES, name

def test_out_of_bounds_wav_chunk_is_safe():
    chunk = b"JUNK" + (2**31).to_bytes(4, "little")
    data = b"RIFF" + (len(chunk) + 4).to_bytes(4, "little") + b"WAVE" + chunk
    with pytest.raises(audio.AudioError, match="format"):
        audio.validate_wav(data)


def test_metadata_is_not_sent_to_provider():
    original = wav_bytes()
    metadata = b"private-name-private-address"
    chunk = b"LIST" + len(metadata).to_bytes(4, "little") + metadata
    if len(metadata) % 2:
        chunk += b"\x00"
    data = bytearray(original[:12] + chunk + original[12:])
    data[4:8] = (len(data) - 8).to_bytes(4, "little")
    _, client, _ = call_with_response(json.dumps(VALID), bytes(data))
    sent = client.models.generate_content.call_args.kwargs["contents"][0].parts[1].inline_data.data
    assert metadata not in sent
    assert sent == original

@pytest.mark.parametrize("code", [500, 502, 503])
def test_busy_errors_get_one_retry_and_one_backup_try_then_fail_safely(code):
    client = MagicMock()
    client.__enter__.return_value = client
    exc = RuntimeError("private-key and private-transcript")
    exc.code = code
    client.models.generate_content.side_effect = [exc, exc, exc]
    with patch("audio_service.genai.Client", return_value=client), \
            patch("audio_service.time.sleep") as sleep:
        with pytest.raises(audio.AudioError) as error:
            audio.transcribe("key", "gemini-3.8-flash", wav_bytes(), consent=True,
                             language=audio.LANGUAGES[0])
    assert str(error.value) == "busy"
    models = [c.kwargs["model"] for c in client.models.generate_content.call_args_list]
    assert models == ["gemini-3.8-flash", "gemini-3.8-flash", "gemini-3.5-flash"]
    sleep.assert_called_once_with(audio.BUSY_RETRY_DELAY_S)


def test_busy_then_success_returns_transcript():
    client = MagicMock()
    client.__enter__.return_value = client
    exc = RuntimeError("busy")
    exc.code = 503
    client.models.generate_content.side_effect = [exc, MagicMock(text=json.dumps(VALID))]
    with patch("audio_service.genai.Client", return_value=client), \
            patch("audio_service.time.sleep"):
        result = audio.transcribe("key", "model", wav_bytes(), consent=True,
                                  language=audio.LANGUAGES[0])
    assert result["transcript"] == VALID["transcript"]


def test_backup_model_rescues_busy_transcription_and_is_reported():
    client = MagicMock()
    client.__enter__.return_value = client
    exc = RuntimeError("busy")
    exc.code = 503
    client.models.generate_content.side_effect = [exc, exc, MagicMock(text=json.dumps(VALID))]
    with patch("audio_service.genai.Client", return_value=client), \
            patch("audio_service.time.sleep"):
        result = audio.transcribe("key", "gemini-3.8-flash", wav_bytes(), consent=True,
                                  language=audio.LANGUAGES[0])
    assert result["model"] == "gemini-3.5-flash" and result["backup_used"] is True


def test_spoken_work_location_is_extracted_when_quoted():
    data = copy.deepcopy(VALID)
    data["transcript"] += " मैं पुणे में काम करना चाहता हूँ।"
    data["background"]["location"] = "पुणे"
    data["background"]["evidence"]["location"] = "पुणे में काम करना चाहता हूँ"
    result, _, _ = call_with_response(json.dumps(data))
    assert result["background"]["location"] == "पुणे"


def test_ungrounded_location_is_dropped_without_losing_the_transcript():
    data = copy.deepcopy(VALID)
    data["background"]["location"] = "Mumbai"
    data["background"]["evidence"]["location"] = "not in transcript"
    result, _, _ = call_with_response(json.dumps(data))
    assert result["background"]["location"] == ""
    assert result["transcript"] == VALID["transcript"]


def test_prompt_forbids_posting_locations():
    assert "never a posting, unit, base or deployment location" in audio.SYSTEM_RULES
