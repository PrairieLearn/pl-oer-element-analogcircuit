# PrairieLearn OER Element: Analog Circuit

This element was developed as a PrairieLearn OER element. Please carefully test
the element and understand its features and limitations before deploying it in a
course. It is provided as-is and not officially maintained by PrairieLearn, so
we can only provide limited support for any issues you encounter!

If you like this element, you can use it in your own PrairieLearn course by
copying the contents of the `elements` folder into your own course repository.
After syncing, the element can be used as illustrated by the example questions
that are also contained in this repository.


## `pl-analog-circuit` element

This element renders analog circuit schematics in PrairieLearn questions. It can
render circuits from JSON circuit dictionaries or from CircuitikZ/TikZ inputs.
The element itself only displays the circuit. Other elements need to be used to
collect student answers for grading.

### Example

```html
<pl-question-panel>
  <p>Use the circuit below to answer the following question.</p>
</pl-question-panel>

<pl-analog-circuit answers-name="circuit"></pl-analog-circuit>
<pl-number-input answers-name="voltage" label="$V_R =$" suffix="$V$"></pl-number-input>
```

```python
def generate(data):
    data["correct_answers"]["voltage"] = 2.7
    data["params"]["circuit"] = {
        "circuit": {
            "components": [
                {"from": "0,0", "to": "0,4", "type": "SourceV", "label": "$V_S$"},
                {"from": "0,4", "to": "3,4", "type": "Resistor", "label": "$R_1$"},
                {"from": "3,4", "to": "3,0", "type": "Resistor", "label": "$R_2$"},
                {"from": "3,0", "to": "0,0"},
                {"pos": "0,0", "type": "Ground"},
            ],
            "nodes": [
                {"pos": "0,4", "dot": "filled", "label": "a"},
            ],
            "annotations": [
                {"type": "LoopCurrent", "bounds": ("0,0", "3,4"), "label": "$I$"},
            ],
        }
    }
```

### Element Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `answers-name` | string (required) | Key in `data["params"]` containing the circuit data. |
| `format` | string (default: `"json"`) | Circuit input format: `"json"` or `"circuitikz"`. |
| `width` | integer (default: `600`) | Rendered image width attribute. |
| `height` | integer (default: `400`) | Rendered image height attribute. |
| `scale` | float (default: `1.0`) | Coordinate scale applied while rendering. |
| `debug` | boolean (default: `false`) | If `true`, shows the parsed circuit data below the rendered image. |

### JSON Circuit Data

For JSON circuits, set `data["params"][answers_name]["circuit"]` in
`server.py`, or place the JSON directly inside the `<pl-analog-circuit>` tag.
The value should be a dictionary with this structure:

| Key | Type | Description |
|-----|------|-------------|
| `components` | list (required) | Wires and circuit elements to draw. |
| `nodes` | list (optional) | Named or labeled points in the circuit. |
| `annotations` | list (optional) | Top-level annotations (e.g., loop current arrows). |


#### Circuit Components

Two-terminal components use `to` plus optional `from`, `type`, `label`, and
`annotations` keys. If `from` is omitted, it defaults to `(0, 0)` for the first
component or the previous component's `to` position afterward. If `type` is
omitted, the component is drawn as a `Line`. One-position components, such as
grounds, use `pos` and `type`.

Component `type` values are forwarded to
[`schemdraw.elements`](https://schemdraw.readthedocs.io/en/latest/elements/electrical.html),
such as `Resistor`, `Capacitor`, `SourceV`, `SourceI`, `Line`, and `Ground`.

Component positions can be tuples, `"x,y"` strings, or node names (see below).

Component labels can be strings, Schemdraw label dictionaries, or lists of
either form:

```python
{"label": "$R_1$"}
{"label": {"label": "$R_1$", "loc": "bottom"}}
{"label": [{"label": "$I$", "loc": "top"}, {"label": "$+$", "loc": "left"}]}
```

The only currently supported component annotation is `CurrentLabel`, with optional
`label`, `top`, `ofst`, and `reverse` keys.

#### Circuit Nodes

Nodes require `pos` and can include `label`, `name`, and `dot`. Node labels are
always plain strings. Set `dot` to `"filled"` or `"open"` to draw a node marker. 
A node `name` is not rendered, but can be used as a position alias in component
endpoints or annotation bounds.

#### Circuit Annotations

The only currently supported top-level annotation is `LoopCurrent`, with `bounds`, 
optional `pad`, and optional `label`. Bounds is a tuple or list of the top left and 
bottom right bounds of the annotation, which can take the same format as component 
endpoints.


### CircuitikZ Usage

Set `format="circuitikz"` to render a CircuitikZ/TikZ source.
This feature is rather limited and experimental. Using JSON is highly recommended!

The element accepts either a `circuitikz` or `tikzpicture` environment:

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

The parser currently reads `\draw` paths made of coordinates connected by
`--`, `-`, or `to[...]`. Coordinates can be absolute, such as `(2,0)`, or
relative with `++`, such as `++(2,0)`. Comments beginning with `%` are ignored.

Supported component aliases include resistors (`R`, `resistor`), variable
resistors (`rv`, `resistorvar`), capacitors (`C`), inductors (`L`), voltage
sources (`sV`, `vs`, `voltage source`), current sources (`si`, `is`, `current
source`), batteries, diodes, and shorts/wires/lines. `american` in the
environment options or component token selects IEEE-style resistors where
available.

Labels can be supplied with `l=...`, `label=...`, `a=...`, or common component
label forms such as `R={4k}` and `v^>={12V}`. Dot markers in path options, such
as `-*`, `o-*`, and `*-*`, create open or filled circuit nodes. Single-position
node elements are limited to `node[ground]`, `node[gnd]`, `node[earth]`,
`node[vss]`, and `node[vdd]`.
