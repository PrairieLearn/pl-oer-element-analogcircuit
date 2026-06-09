# `pl-analog-circuit` element

`pl-analog-circuit` renders analog circuit schematics in PrairieLearn questions.
It currently renders a circuit image in the question panel; grading is a no-op
unless the question uses other input elements.

The element supports two input formats:

- JSON circuit dictionaries from `data["params"]` or inline element text.
- A limited CircuitikZ/TikZ parser via `format="circuitikz"`.

Runtime dependency: this element uses the Python `schemdraw` package, which is
included in current PrairieLearn runtimes.

## Element Attributes

| Attribute | Description | Optional | Default Value |
| --------- | ----------- | -------- | ------------- |
| `answers-name` | Key in `data["params"]` containing the circuit data. Use this for new questions. | Yes, if `circuit-name` is set | |
| `circuit-name` | Backward-compatible alias for `answers-name`. | Yes, if `answers-name` is set | |
| `debug` | Shows the parsed circuit data below the rendered image. | Yes | `false` |
| `width` | Rendered image width attribute. | Yes | `600` |
| `height` | Rendered image height attribute. | Yes | `400` |
| `format` | Circuit input format: `json` or `circuitikz`. | Yes | `json` |
| `scale` | Coordinate scale applied while rendering. | Yes | `1.0` |

If both `answers-name` and `circuit-name` are provided, they must match.

## JSON Circuit Data

In `server.py`, set `data["params"][answers_name]["circuit"]` to a dictionary
with a required `components` list and optional `nodes` and `annotations` lists.

Two-terminal components use `from`, `to`, `type`, and optional labels. If
`from` is omitted, it defaults to `(0, 0)` for the first component or the
previous component's `to` position afterward.

One-position components use `pos` and `type`.

Positions can be tuples, lists, `"x,y"` strings, or two-digit strings such as
`"01"`.

Labels can be strings, Schemdraw label dictionaries such as
`{"label": "$R_1$", "loc": "bottom"}`, or lists of those values.

Supported annotations:

- Component-level `CurrentLabel`, with optional `label`, `top`, `ofst`, and
  `reverse` keys.
- Top-level `LoopCurrent`, with `bounds`, optional `pad`, and optional `label`.

The renderer places components directly by endpoint coordinates, so components
do not need to be connected to `(0, 0)` and diagonal components are supported.
Component `type` values are forwarded to `schemdraw.elements`.

## Example Usage

```html
<pl-question-panel>
  <p>Use the circuit below to answer the following question.</p>
  <pl-analog-circuit answers-name="circuit"></pl-analog-circuit>
  <pl-number-input answers-name="volt" label="$V_R =$" suffix="$V$"></pl-number-input>
</pl-question-panel>
```

```python
from circuit import AnalogCircuit


def generate(data):
    data["correct_answers"]["volt"] = 2.7
    schematic: AnalogCircuit = {
        "components": [
            {"to": (1, 0)},
            {"to": (2, 0)},
            {"to": (2, 1), "type": "SourceV", "label": {"label": "1 V", "loc": "bottom"}},
            {"to": (1, 1), "type": "Resistor", "label": r"10 $\Omega$"},
            {"to": (0, 1), "type": "Resistor", "label": r"5 $\Omega$"},
            {"from": (0, 0), "to": (0, 1), "type": "SourceV", "label": "$V_S$"},
            {
                "from": (1, 0),
                "to": (1, 1),
                "type": "Resistor",
                "label": [
                    {"label": r"30 $\Omega$"},
                    {"label": ["-", "$V_R$", "+"], "loc": "bottom"},
                ],
            },
        ]
    }
    data["params"]["circuit"] = {"circuit": schematic}
```

## CircuitikZ Usage

```html
<pl-analog-circuit answers-name="circuit" format="circuitikz" scale="0.5">
  \begin{tikzpicture}
    \draw (5, 3) to[american voltage source, l={$5V$}] (5, 6);
    \draw (5, 6) to[american resistor, l={$10\Omega$}] (8, 6);
    \draw (8, 6) to[american resistor, l={$20\Omega$}] (8, 3);
    \draw (8, 3) -- (5, 3);
  \end{tikzpicture}
</pl-analog-circuit>
```

The CircuitikZ parser is intentionally limited and should be treated as a
preview feature. Prefer JSON for generated questions.

## Current Limitations

- The element renders only in the question panel.
- The element itself does not collect or grade student input.
- Student-fillable circuit placeholders are not implemented.
- The JSON schema is still experimental and should be treated as preview API.

## Implementation Note

This branch includes the direct coordinate renderer and annotation support from
closed PrairieLearn/pl-uiuc-csed-dev PR #208.
