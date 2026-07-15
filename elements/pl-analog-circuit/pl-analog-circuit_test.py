import importlib
import json
import os
import sys
import types
from pathlib import Path

import pytest

ELEMENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ELEMENT_DIR))

sys.modules["chevron"] = types.SimpleNamespace(
    render=lambda _template, params: json.dumps(params)
)

pl_stub = types.SimpleNamespace(
    QuestionData=dict,
    get_string_attrib=lambda element, name, default=None: element.get(name, default),
    get_boolean_attrib=lambda element, name, default=None: (
        element.get(name, str(default)).lower() in {"true", "1", "yes"}
        if element.get(name) is not None
        else default
    ),
    get_integer_attrib=lambda element, name, default=None: (
        int(element.get(name)) if element.get(name) is not None else default
    ),
    get_float_attrib=lambda element, name, default=None: (
        float(element.get(name)) if element.get(name) is not None else default
    ),
    check_attribs=lambda _element, _required, _optional: None,
)
sys.modules["prairielearn"] = pl_stub

pl_analog = importlib.import_module("pl-analog-circuit")


def _render(element_html: str, data: dict) -> dict | str:
    old_cwd = os.getcwd()
    try:
        os.chdir(ELEMENT_DIR)
        rendered = pl_analog.render(element_html, data)
        return json.loads(rendered) if rendered else ""
    finally:
        os.chdir(old_cwd)


def test_prepare_requires_answers_name() -> None:
    with pytest.raises(ValueError, match="answers-name"):
        pl_analog.prepare("<pl-analog-circuit></pl-analog-circuit>", {"params": {}})


def test_prepare_parses_json_circuit_from_params_and_preserves_render_options() -> None:
    data = {
        "params": {
            "circuit": {
                "circuit": {
                    "components": [
                        {"from": "0,0", "to": "0,1", "type": "SourceV"},
                        {"from": "0,1", "to": "1,1", "type": "Resistor"},
                    ]
                }
            }
        }
    }

    pl_analog.prepare(
        '<pl-analog-circuit answers-name="circuit" width="320" height="200" '
        'scale="0.5" debug="true"></pl-analog-circuit>',
        data,
    )

    params = data["params"]["circuit"]
    assert params["width"] == 320
    assert params["height"] == 200
    assert params["scale"] == 0.5
    assert params["debug"] is True
    assert len(params["circuit_parsed"]["components"]) == 2


def test_prepare_parses_inline_json_when_params_are_absent() -> None:
    data = {"params": {}}

    pl_analog.prepare(
        '<pl-analog-circuit answers-name="inline">'
        '{"components": [{"from": "0,0", "to": "1,0"}]}'
        "</pl-analog-circuit>",
        data,
    )

    assert len(data["params"]["inline"]["circuit_parsed"]["components"]) == 1


def test_render_returns_empty_string_outside_question_panel() -> None:
    assert (
        pl_analog.render(
            '<pl-analog-circuit answers-name="circuit"></pl-analog-circuit>',
            {"panel": "submission", "params": {"circuit": {}}},
        )
        == ""
    )


def test_prepare_rejects_missing_json_circuit() -> None:
    with pytest.raises(ValueError, match="missing 'circuit'"):
        pl_analog.prepare(
            '<pl-analog-circuit answers-name="missing"></pl-analog-circuit>',
            {"params": {}},
        )


def test_prepare_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="unknown format"):
        pl_analog.prepare(
            '<pl-analog-circuit answers-name="circuit" format="spice"></pl-analog-circuit>',
            {"params": {"circuit": {"circuit": {"components": []}}}},
        )


def test_prepare_parses_circuitikz_inline_source() -> None:
    data = {"params": {}}

    pl_analog.prepare(
        r'<pl-analog-circuit answers-name="tikz" format="circuitikz">'
        r"\begin{circuitikz}"
        r"\draw (0,0) to[R] (1,0);"
        r"\end{circuitikz}"
        r"</pl-analog-circuit>",
        data,
    )

    assert "circuit_parsed" in data["params"]["tikz"]


def test_render_question_panel_includes_svg_url_and_dimensions() -> None:
    data = {"panel": "question", "params": {"circuit": {}}}
    pl_analog.prepare(
        '<pl-analog-circuit answers-name="circuit" width="320" height="200">'
        '{"components": [{"from": "0,0", "to": "1,0"}]}'
        "</pl-analog-circuit>",
        data,
    )
    old_render_circuit = pl_analog.render_circuit
    try:
        pl_analog.render_circuit = lambda circuit, scale, debug: (
            "data:image/svg+xml,test"
        )
        rendered = _render(
            '<pl-analog-circuit answers-name="circuit"></pl-analog-circuit>',
            data,
        )
    finally:
        pl_analog.render_circuit = old_render_circuit

    assert rendered["question"] is True
    assert rendered["width"] == 320
    assert rendered["height"] == 200
    assert rendered["img"] == "data:image/svg+xml,test"
    assert json.loads(rendered["data"])["components"]


def test_render_requires_prepared_circuit() -> None:
    with pytest.raises(ValueError, match="parsed circuit"):
        _render(
            '<pl-analog-circuit answers-name="circuit"></pl-analog-circuit>',
            {"panel": "question", "params": {"circuit": {}}},
        )


def test_grade_is_noop() -> None:
    data = {"partial_scores": {}}

    assert pl_analog.grade("<pl-analog-circuit></pl-analog-circuit>", data) is None
    assert data == {"partial_scores": {}}
