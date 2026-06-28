from dataclasses import dataclass
from typing import Literal, cast
import chevron
import lxml.html
import json
import prairielearn as pl  # type: ignore
from circuit import parse_circuit, render_circuit, AnalogCircuit
from circuit.formats import from_circuitikz


ANALOG_CIRCUIT_TEMPLATE_NAME = "pl-analog-circuit.mustache"


@dataclass
class defaults:
    debug = False
    width = 600
    height = 400
    format: Literal["json", "circuitikz"] = "json"
    scale = 1.0


def _get_name(element: lxml.html.HtmlElement) -> str:
    answers_name = pl.get_string_attrib(element, "answers-name", None)
    if answers_name is None:
        raise ValueError("pl-analog-circuit requires 'answers-name'")
    return answers_name


def prepare(element_html: str, data: pl.QuestionData) -> None:
    element: lxml.html.HtmlElement = lxml.html.fragment_fromstring(element_html)
    required_attribs = ["answers-name"]
    optional_attribs = [
        "debug",
        "width",
        "height",
        "format",
        "scale",
    ]

    pl.check_attribs(element, required_attribs, optional_attribs)

    name = _get_name(element)

    debug = pl.get_boolean_attrib(element, "debug", defaults.debug)
    width = pl.get_integer_attrib(element, "width", defaults.width)
    height = pl.get_integer_attrib(element, "height", defaults.height)
    format = pl.get_string_attrib(element, "format", defaults.format)
    scale = pl.get_float_attrib(element, "scale", defaults.scale)

    params = data["params"].setdefault(name, {})

    params["debug"] = debug
    params["width"] = width
    params["height"] = height
    params["scale"] = scale

    match format:
        case "json":
            raw_circuit = params.get("circuit")
            if raw_circuit is None:
                inline_json = element.text_content().strip()
                if not inline_json:
                    raise ValueError(
                        f"missing 'circuit' in params for answer name '{name}'"
                    )
                raw_circuit = json.loads(inline_json)
            params["circuit_parsed"] = parse_circuit(raw_circuit)
        case "circuitikz":
            raw_circuit = element.text_content()
            params["circuit_parsed"] = from_circuitikz(raw_circuit)
        case _:
            raise ValueError(f"unknown format '{format}' for pl-analog-circuit")


def render(element_html: str, data: pl.QuestionData) -> str:
    element = lxml.html.fragment_fromstring(element_html)
    name = _get_name(element)
    if data["panel"] != "question":
        return ""

    with open(ANALOG_CIRCUIT_TEMPLATE_NAME, "r", encoding="utf-8") as f:
        template = f.read()

    params = data["params"][name]

    debug = params.get("debug", defaults.debug)
    width = params.get("width", defaults.width)
    height = params.get("height", defaults.height)
    scale = params.get("scale", defaults.scale)

    circuit = params.get("circuit_parsed")
    if circuit is None:
        raise ValueError("unable to find parsed circuit in params")
    circuit = cast(AnalogCircuit, circuit)

    rendered_circuit_url = render_circuit(circuit, scale=scale, debug=debug)

    if data["panel"] == "question":
        html_params = {
            "question": True,
            "debug": debug,
            "width": width,
            "height": height,
            "data": json.dumps(circuit, indent=2),
            "img": rendered_circuit_url,
        }
        return chevron.render(template, html_params)


def grade(element_html: str, data: pl.QuestionData) -> None:
    return None
