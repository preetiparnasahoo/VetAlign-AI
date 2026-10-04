"""State-handling tests for the three-step wizard.

These use Streamlit's AppTest harness, which runs app.py in-process the same way
the browser does, so navigation and widget behaviour are genuinely exercised.
The Gemini call is patched out: no API key, no network, no quota consumed.

Run from the project root:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
APP = str(ROOT / "app.py")

FAKE_RESULT = {
    "_facts": ["Supervised 12 personnel.", "Maintained stock records."],
    "_elapsed": 1.2,
    "skills": [
        {"skill": "inventory management", "category": "Logistics", "source_ids": [2]},
        {"skill": "team supervision", "category": "People", "source_ids": [1]},
    ],
    "role_suggestions": [
        {
            "role": "Warehouse Supervisor",
            "why": "Stock and team experience.",
            "supported_by": ["Maintained stock records."],
            "gaps": ["No stated warehouse-software experience."],
            "questions_to_confirm": ["Which software is used?"],
        }
    ],
    "job_requirement_checks": [],
    "profile": {"summary": "Stores supervisor.", "bullets": ["Supervised 12 personnel."]},
    "interview": {"behavioural": [], "functional": [], "action_plan": ["Prepare examples."]},
    "warnings": [],
}


def run_app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    return at


def fill_minimum(at: AppTest, duties: str = "Supervised 12 personnel in stores.") -> AppTest:
    at.text_area(key="w_duties").set_value(duties).run()
    at.checkbox(key="w_consent").set_value(True).run()
    return at


def press_analyse(at: AppTest) -> AppTest:
    at.button(key="btn_analyse").click().run()
    return at


def analyse_ok(at: AppTest) -> AppTest:
    with patch("career_engine.generate", return_value=FAKE_RESULT), patch(
        "career_engine.profile_markdown", return_value="# Draft profile"
    ):
        press_analyse(at)
    return at


# ------------------------------------------------------------------- smoke


def test_app_starts_without_exception():
    at = run_app()
    assert not at.exception, at.exception


def test_starts_on_step_one():
    assert run_app().session_state.step == 1


def test_default_model_is_the_live_verified_replacement():
    import career_engine

    at = run_app()
    assert at.selectbox(key="w_model_choice").value == "gemini-3.8-flash"
    assert career_engine.DEFAULT_MODEL == "gemini-3.8-flash"


def test_model_dropdown_offers_only_text_generation_models():
    """Image, audio and TTS models cannot serve this JSON workload."""
    options = at_options(run_app())
    assert options, "expected model choices"
    for name in options:
        assert not any(
            bad in name for bad in ("image", "tts", "transcribe", "lyria", "robotics", "banana")
        ), f"{name} cannot produce the JSON profile"


def at_options(at):
    import career_engine

    return [o for o in at.selectbox(key="w_model_choice").options
            if o != career_engine.CUSTOM_MODEL_OPTION]


def test_choosing_another_model_preserves_answers_and_clears_error():
    at = fill_minimum(run_app(), "Stores and dispatch duties.")
    at.session_state.error = "Model unavailable"
    at.selectbox(key="w_model_choice").set_value("gemini-3.5-flash").run()
    assert not at.exception
    assert at.session_state.error == ""
    assert at.session_state.model_choice == "gemini-3.5-flash"
    assert at.session_state.duties == "Stores and dispatch duties."
    assert at.session_state.consent is True


def test_model_choice_survives_language_switch():
    at = run_app()
    at.selectbox(key="w_model_choice").set_value("gemini-3.5-flash").run()
    at.button(key="lang_हिन्दी").click().run()
    assert at.selectbox(key="w_model_choice").value == "gemini-3.5-flash"


def test_custom_model_box_appears_only_when_other_is_selected():
    import career_engine

    at = run_app()
    assert not [t for t in at.text_input if t.key == "w_custom_model"]
    at.selectbox(key="w_model_choice").set_value(career_engine.CUSTOM_MODEL_OPTION).run()
    assert [t for t in at.text_input if t.key == "w_custom_model"], "expected a name box"


def test_typed_model_name_is_used():
    import career_engine

    at = fill_minimum(run_app())
    at.selectbox(key="w_model_choice").set_value(career_engine.CUSTOM_MODEL_OPTION).run()
    at.text_input(key="w_custom_model").set_value("gemini-flash-latest").run()
    with patch("career_engine.generate", return_value=FAKE_RESULT) as gen, patch(
        "career_engine.profile_markdown", return_value="# Draft"
    ):
        press_analyse(at)
    assert gen.call_args.args[1] == "gemini-flash-latest"


def test_empty_custom_model_is_refused_before_any_api_call():
    import career_engine

    at = fill_minimum(run_app())
    at.selectbox(key="w_model_choice").set_value(career_engine.CUSTOM_MODEL_OPTION).run()
    with patch("career_engine.generate") as gen:
        press_analyse(at)
    assert not gen.called, "must not call the API without a model name"
    assert at.session_state.step == 1
    assert at.session_state.error


# --------------------------------------------- the defect this change fixes


def test_answers_survive_navigation_through_all_steps_and_back():
    """Step-1 inputs must not be discarded when their widgets stop rendering."""
    at = run_app()
    fill_minimum(at, "Maintained stock records for eight years.")
    at.text_input(key="w_rank").set_value("Havildar").run()
    analyse_ok(at)
    assert at.session_state.step == 2

    for step in (3, 2, 1):
        at.session_state.step = step
        at.run()
        assert not at.exception, f"exception on step {step}: {at.exception}"
        assert at.session_state.duties == "Maintained stock records for eight years."
        assert at.session_state.rank == "Havildar"


def test_widget_shows_durable_value_after_returning_to_step_one():
    at = run_app()
    at.text_input(key="w_trade").set_value("Logistics").run()
    analyse_ok(fill_minimum(at))

    at.button(key="btn_back").click().run()
    assert at.session_state.step == 1
    assert at.text_input(key="w_trade").value == "Logistics"


def test_next_and_back_move_between_steps():
    at = analyse_ok(fill_minimum(run_app()))
    at.button(key="btn_next").click().run()
    assert at.session_state.step == 3
    at.button(key="btn_back").click().run()
    assert at.session_state.step == 2


def test_result_is_not_marked_stale_merely_by_navigating():
    """The 'inputs changed' banner must not fire when nothing was edited."""
    at = analyse_ok(fill_minimum(run_app()))
    key_after_analysis = at.session_state.result_key
    at.button(key="btn_next").click().run()
    at.button(key="btn_back").click().run()
    assert at.session_state.result_key == key_after_analysis


def test_editing_an_answer_marks_the_result_stale():
    at = analyse_ok(fill_minimum(run_app()))
    at.session_state.step = 1
    at.run()
    previous_key = at.session_state.result_key
    at.text_input(key="w_rank").set_value("Naik").run()
    assert at.session_state.result_key == previous_key
    assert any("Your inputs changed" in item.value for item in at.markdown)


# ------------------------------------------------------------ sample data


def test_sample_button_populates_fields_without_error():
    """Previously this mutated an already-rendered widget and raised."""
    at = run_app()
    samples = [b for b in at.button if b.key and b.key.startswith("q_")]
    assert samples, "expected quick-profile buttons on step 1"
    samples[0].click().run()
    assert not at.exception, at.exception
    assert at.session_state.duties.strip(), "sample should fill the narrative"
    assert at.text_area(key="w_duties").value == at.session_state.duties


def test_sample_button_clears_a_previous_result():
    at = analyse_ok(fill_minimum(run_app()))
    at.session_state.step = 1
    at.run()
    [b for b in at.button if b.key and b.key.startswith("q_")][0].click().run()
    assert at.session_state.result is None
    assert at.session_state.edited_profile == ""


def test_branch_button_selects_service_without_clearing_other_answers():
    at = run_app()
    fill_minimum(at, "Signals and equipment duties.")
    at.button(key="br_Indian Navy").click().run()
    assert not at.exception, at.exception
    assert at.session_state.service == "Indian Navy"
    assert at.session_state.duties == "Signals and equipment duties."


# -------------------------------------------------------------- language


def test_language_switch_preserves_answers():
    at = run_app()
    fill_minimum(at, "Coordinated convoy movements.")
    at.button(key="lang_हिन्दी").click().run()
    assert not at.exception, at.exception
    assert at.session_state.ui_lang == "हिन्दी"
    assert at.session_state.duties == "Coordinated convoy movements."
    assert at.session_state.consent is True


def test_language_switch_keeps_server_key_out_of_widgets():
    at = run_app()
    at.secrets["GEMINI_API_KEY"] = "test-key-123"
    at.button(key="lang_हिन्दी").click().run()
    assert not at.exception, at.exception
    assert at.secrets["GEMINI_API_KEY"] == "test-key-123"
    assert not any(w.key == "w_api_key" for w in at.text_input)
    assert "test-key-123" not in str(at)


def test_language_switch_on_a_later_step_does_not_lose_results():
    at = analyse_ok(fill_minimum(run_app()))
    at.button(key="lang_हिन्दी").click().run()
    assert not at.exception, at.exception
    assert at.session_state.step == 2
    assert at.session_state.result is not None


# ----------------------------------------------------------------- reset


def test_clear_wipes_answers_but_keeps_credentials():
    at = run_app()
    at.secrets["GEMINI_API_KEY"] = "test-key-123"
    fill_minimum(at, "Stores duties.")
    at.button(key="btn_clear").click().run()
    assert not at.exception, at.exception
    assert at.session_state.duties == ""
    assert at.session_state.consent is False
    assert at.secrets["GEMINI_API_KEY"] == "test-key-123"
    assert not any(w.key == "w_api_key" for w in at.text_input)


def test_clear_also_empties_the_rendered_widget():
    at = run_app()
    fill_minimum(at, "Stores duties.")
    at.button(key="btn_clear").click().run()
    assert at.text_area(key="w_duties").value == ""


def test_restart_returns_to_step_one_and_empties_fields():
    at = analyse_ok(fill_minimum(run_app(), "Stores duties."))
    at.button(key="btn_next").click().run()
    at.button(key="btn_restart").click().run()
    assert not at.exception, at.exception
    assert at.session_state.step == 1
    assert at.session_state.duties == ""
    assert at.session_state.result is None


# ------------------------------------------------------------ validation


def test_analyse_requires_consent():
    at = run_app()
    at.text_area(key="w_duties").set_value("Stores duties.").run()
    press_analyse(at)
    assert at.session_state.step == 1
    assert at.session_state.error, "expected a consent error"


def test_analyse_requires_a_narrative():
    at = run_app()
    at.checkbox(key="w_consent").set_value(True).run()
    press_analyse(at)
    assert at.session_state.step == 1
    assert at.session_state.error, "expected a missing-narrative error"


def test_whitespace_only_narrative_is_rejected():
    at = run_app()
    at.text_area(key="w_duties").set_value("   \n  ").run()
    at.checkbox(key="w_consent").set_value(True).run()
    press_analyse(at)
    assert at.session_state.step == 1
    assert at.session_state.error


def test_successful_analysis_advances_to_step_two():
    at = analyse_ok(fill_minimum(run_app()))
    assert not at.exception, at.exception
    assert at.session_state.step == 2
    assert at.session_state.result is not None
    assert at.session_state.error == ""


def test_engine_failure_keeps_the_user_on_step_one_with_answers_intact():
    import career_engine

    at = run_app()
    fill_minimum(at, "Stores and dispatch duties.")
    with patch("career_engine.generate", side_effect=career_engine.EngineError("quota exhausted")):
        press_analyse(at)
    assert not at.exception, at.exception
    assert at.session_state.step == 1
    assert "quota" in at.session_state.error
    assert at.session_state.duties == "Stores and dispatch duties.", "answers must survive a failure"


def test_fixing_an_answer_clears_the_previous_error():
    at = run_app()
    press_analyse(at)
    assert at.session_state.error
    at.text_area(key="w_duties").set_value("Stores duties.").run()
    assert at.session_state.error == ""


# ----------------------------------------------------- later-step guards


def test_steps_two_and_three_are_safe_without_a_result():
    for step in (2, 3):
        at = run_app()
        at.session_state.step = step
        at.run()
        assert not at.exception, f"step {step} raised without a result: {at.exception}"


def test_ticking_consent_clears_the_consent_error():
    at = run_app()
    at.text_area(key="w_duties").set_value("Supervised 12 personnel in stores.").run()
    press_analyse(at)
    assert at.session_state.error
    at.checkbox(key="w_consent").set_value(True).run()
    assert at.session_state.error == ""
