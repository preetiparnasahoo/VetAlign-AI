"""Voice wizard state tests; capture widgets mocked where AppTest lacks upload.

These do not establish microphone/browser support or real speech accuracy.
"""

import io
from unittest.mock import patch

import pytest

from test_app_state import run_app, fill_minimum, analyse_ok, press_analyse
from test_audio_service import VALID
from i18n import STRINGS
import audio_service as audio


def captured_app():
    at = run_app()
    with patch("streamlit.audio_input", return_value=None):
        at.checkbox(key="w_audio_consent").set_value(True).run()
        key = f"audio_record_{at.session_state.audio_epoch}"
        # Mock before registration: AppTest otherwise serializes the actual
        # (empty) binary widget and overwrites this injected capture on rerun.
        at.session_state[key] = io.BytesIO(b"fake WAV handled by mocked service")
        at.session_state.audio_pending = True
        at.run()
    return at, key


def transcribed_app():
    at, key = captured_app()
    with patch("streamlit.audio_input", return_value=None), patch(
        "audio_service.transcribe", return_value=dict(VALID, elapsed=1.5)
    ) as transcribe:
        at.button(key="btn_transcribe").click().run()
    assert not at.exception, at.exception
    assert transcribe.call_args.kwargs["consent"] is True
    assert key not in at.session_state
    return at


def test_capture_widgets_absent_before_consent():
    at = run_app()
    assert not at.get("audio_input")
    assert not at.get("file_uploader")
    assert not [b for b in at.button if b.key == "btn_transcribe"]
    assert at.text_area(key="w_duties") is not None


def test_capture_and_upload_available_only_after_consent():
    at = run_app()
    at.checkbox(key="w_audio_consent").set_value(True).run()
    assert not at.exception
    assert len(at.get("audio_input")) == 1
    assert at.button(key="btn_transcribe").disabled
    at.radio(key="w_audio_source").set_value("upload").run()
    assert len(at.get("file_uploader")) == 1
    assert not at.get("audio_input")
    at.checkbox(key="w_audio_consent").set_value(False).run()
    assert not at.get("file_uploader")


def test_transcription_fills_review_fields_not_profile():
    at = transcribed_app()
    assert at.session_state.step == 1
    assert at.session_state.result is None
    assert at.session_state.duties == VALID["transcript"]
    assert at.text_input(key="w_rank").value == "हवलदार"
    assert at.session_state.years == 16
    assert at.session_state.transcript_approved is False
    assert at.session_state.audio_pending is False


def test_profile_requires_transcript_approval_even_with_text_consent():
    at = transcribed_app()
    at.checkbox(key="w_consent").set_value(True).run()
    with patch("career_engine.generate") as generate:
        press_analyse(at)
    generate.assert_not_called()
    assert at.session_state.step == 1
    assert at.session_state.error == STRINGS["English"]["audio_err_review"]


def test_corrected_transcript_is_used_and_approval_survives_navigation():
    at = transcribed_app()
    corrected = VALID["transcript"] + " Maintained stock records."
    at.text_area(key="w_duties").set_value(corrected).run()
    at.checkbox(key="w_transcript_approved").set_value(True).run()
    at.checkbox(key="w_consent").set_value(True).run()
    from test_app_state import FAKE_RESULT
    with patch("career_engine.generate", return_value=FAKE_RESULT) as generate, patch(
        "career_engine.profile_markdown", return_value="# Draft"
    ):
        press_analyse(at)
    assert generate.call_args.args[2]["duties"] == corrected
    assert at.session_state.step == 2
    at.button(key="btn_next").click().run()
    at.text_area(key="w_edited_profile").set_value("My reviewed draft").run()
    at.button(key="lang_हिन्दी").click().run()
    at.button(key="btn_back").click().run()
    at.button(key="btn_back").click().run()
    assert not at.exception
    assert at.session_state.duties == corrected
    assert at.session_state.transcript_approved is True
    assert at.session_state.edited_profile == "My reviewed draft"
    assert at.session_state.audio_consent is True
    assert at.session_state.audio_language == audio.LANGUAGES[0]
    at.text_area(key="w_duties").set_value("Corrected duties only.").run()
    assert at.session_state.transcript_approved is False
    assert at.session_state.rank == ""
    assert at.session_state.years == 0


def test_background_edits_and_branch_selection_revoke_approval():
    at = transcribed_app()
    at.checkbox(key="w_transcript_approved").set_value(True).run()
    at.text_input(key="w_trade").set_value("Stores").run()
    assert at.session_state.transcript_approved is False
    at.checkbox(key="w_transcript_approved").set_value(True).run()
    at.button(key="br_Indian Navy").click().run()
    assert at.session_state.transcript_approved is False


def test_pending_audio_cannot_be_bypassed_by_analyse():
    at, _ = captured_app()
    with patch("streamlit.audio_input", return_value=None):
        fill_minimum(at)
        with patch("career_engine.generate") as generate:
            press_analyse(at)
    generate.assert_not_called()
    assert at.session_state.error == STRINGS["English"]["audio_err_review"]


def test_failure_preserves_previous_draft_and_releases_audio():
    at, key = captured_app()
    at.session_state.duties = "Previous reviewed text."
    at.session_state.edited_profile = "Previous draft"
    with patch("streamlit.audio_input", return_value=None), patch(
        "audio_service.transcribe", side_effect=audio.AudioError("quota")
    ):
        at.button(key="btn_transcribe").click().run()
    assert not at.exception
    assert at.session_state.audio_error == "quota"
    assert at.session_state.duties == "Previous reviewed text."
    assert at.session_state.edited_profile == "Previous draft"
    assert key not in at.session_state
    assert at.session_state.audio_pending is False


def test_reruns_and_language_changes_do_not_retranscribe():
    at = transcribed_app()
    with patch("audio_service.transcribe") as transcribe:
        at.run()
        at.button(key="lang_हिन्दी").click().run()
        at.selectbox(key="w_audio_language").set_value(audio.LANGUAGES[1]).run()
    transcribe.assert_not_called()
    assert at.session_state.duties == VALID["transcript"]


@pytest.mark.parametrize("action", ["clear", "sample", "text"])
def test_reset_sample_and_explicit_text_exit_voice_mode(action):
    at = transcribed_app()
    if action == "sample":
        [b for b in at.button if b.key and b.key.startswith("q_")][0].click().run()
    else:
        at.button(key="btn_clear" if action == "clear" else "btn_use_text").click().run()
    assert not at.exception
    assert at.session_state.voice_source is False
    assert at.session_state.transcript_approved is False
    assert at.session_state.audio_pending is False
    assert at.session_state.extracted_background is None
    if action == "clear":
        assert at.session_state.duties == ""
        assert at.session_state.audio_consent is False
    else:
        analyse_ok(fill_minimum(at))
        assert at.session_state.step == 2


def test_cooldown_is_not_reset_by_clear():
    at = transcribed_app()
    timestamp = at.session_state.last_transcription_attempt
    assert timestamp > 0
    at.button(key="btn_clear").click().run()
    assert at.session_state.last_transcription_attempt == timestamp


def test_input_size_guard_prevents_profile_call():
    at = fill_minimum(run_app(), "x" * 8001)
    with patch("career_engine.generate") as generate:
        press_analyse(at)
    generate.assert_not_called()
    assert at.session_state.error == STRINGS["English"]["err_input_length"]


def test_translations_have_matching_keys():
    assert set(STRINGS["English"]) == set(STRINGS["हिन्दी"])


def test_server_key_is_used_but_never_seeded_into_browser_widget():
    import streamlit
    from test_app_state import FAKE_RESULT
    server_key = "fake-server-secret-for-test"
    with patch.object(type(streamlit.secrets), "get", return_value=server_key):
        at = fill_minimum(run_app())
        assert at.text_input(key="w_api_key").value == ""
        assert at.session_state.api_key == ""
        with patch("career_engine.generate", return_value=FAKE_RESULT) as generate, patch(
            "career_engine.profile_markdown", return_value="# Draft"
        ):
            press_analyse(at)
    assert not at.exception
    assert generate.call_args.args[0] == server_key
    assert server_key not in str(at)

def test_spoken_location_fills_field_and_unspoken_keeps_typed_value():
    import copy
    at, key = captured_app()
    at.session_state.location = "Typed city"
    output = copy.deepcopy(dict(VALID, elapsed=1.0))
    with patch("streamlit.audio_input", return_value=None), patch(
        "audio_service.transcribe", return_value=output
    ):
        at.button(key="btn_transcribe").click().run()
    assert at.session_state.location == "Typed city"

    at, key = captured_app()
    output = copy.deepcopy(dict(VALID, elapsed=1.0))
    output["background"]["location"] = "पुणे"
    with patch("streamlit.audio_input", return_value=None), patch(
        "audio_service.transcribe", return_value=output
    ):
        at.button(key="btn_transcribe").click().run()
    assert at.session_state.location == "पुणे"
