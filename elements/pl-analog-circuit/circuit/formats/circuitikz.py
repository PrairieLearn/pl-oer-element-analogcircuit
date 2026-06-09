import re
from dataclasses import dataclass
from typing import Literal

from ..circuit_types import AnalogCircuit, Component2TermTypes, ComponentTypes, Node, Label, LabelUnion
from ..helpers import int_or_float, parse_circuit

header_pattern = re.compile(r"\\begin\{(?P<env>circuitikz|tikzpicture)\}(?:\[(?P<options>[^\]]*)\])?")
end_pattern = re.compile(r"\\end\{(?P<env>circuitikz|tikzpicture)\}")
draw_pattern = re.compile(r"\\draw(?:\[[^\]]*\])?\s*(?P<body>[^;]*);", re.DOTALL)


Coordinate = tuple[float | int, float | int]
LabelList = list[str | Label]
DotValue = Literal['open', 'filled']


@dataclass(frozen=True)
class TwoTermAlias:
    iec: Component2TermTypes
    ieee: Component2TermTypes | None = None

    def resolve(self, *, american: bool) -> Component2TermTypes:
        if american and self.ieee:
            return self.ieee
        return self.iec


@dataclass(frozen=True)
class SinglePoleAlias:
    iec: ComponentTypes
    ieee: ComponentTypes | None = None

    def resolve(self, *, american: bool) -> ComponentTypes:
        if american and self.ieee:
            return self.ieee
        return self.iec


two_term_aliases: dict[str, TwoTermAlias] = {
    "r": TwoTermAlias("ResistorIEC", "ResistorIEEE"),
    "res": TwoTermAlias("ResistorIEC", "ResistorIEEE"),
    "resistor": TwoTermAlias("ResistorIEC", "ResistorIEEE"),
    "rv": TwoTermAlias("ResistorVarIEC", "ResistorVarIEEE"),
    "rvar": TwoTermAlias("ResistorVarIEC", "ResistorVarIEEE"),
    "resistorv": TwoTermAlias("ResistorVarIEC", "ResistorVarIEEE"),
    "resistorvar": TwoTermAlias("ResistorVarIEC", "ResistorVarIEEE"),
    "c": TwoTermAlias("Capacitor"),
    "cap": TwoTermAlias("Capacitor"),
    "capacitor": TwoTermAlias("Capacitor"),
    "l": TwoTermAlias("Inductor"),
    "ind": TwoTermAlias("Inductor"),
    "inductor": TwoTermAlias("Inductor"),
    "sv": TwoTermAlias("SourceV"),
    "vs": TwoTermAlias("SourceV"),
    "vsource": TwoTermAlias("SourceV"),
    "voltage source": TwoTermAlias("SourceV"),
    "voltage": TwoTermAlias("SourceV"),
    "battery": TwoTermAlias("Battery"),
    "si": TwoTermAlias("SourceI"),
    "is": TwoTermAlias("SourceI"),
    "current source": TwoTermAlias("SourceI"),
    "current": TwoTermAlias("SourceI"),
    "diode": TwoTermAlias("Diode"),
    "short": TwoTermAlias("Line"),
    "wire": TwoTermAlias("Line"),
    "line": TwoTermAlias("Line"),
}


single_pole_aliases: dict[str, SinglePoleAlias] = {
    "ground": SinglePoleAlias("Ground"),
    "gnd": SinglePoleAlias("Ground"),
    "earth": SinglePoleAlias("Ground"),
    "vss": SinglePoleAlias("Vss"),
    "vdd": SinglePoleAlias("Vdd"),
}

label_keys = {"l", "label", "a"}


def determine_label_loc(kind: str, modifiers: set[str]) -> str | None:
    if "^" in modifiers:
        return "top"
    if "_" in modifiers:
        return "bottom"
    if kind == "l":
        return "top"
    if kind == "a":
        return "bottom"
    return None


def make_label_entry(kind: str, value: str, modifiers: set[str]) -> Label | str:
    loc = determine_label_loc(kind, modifiers)
    if loc:
        return {"label": value, "loc": loc}
    return value


@dataclass
class SegmentStyle:
    type: Component2TermTypes = "Line"
    label: LabelList | None = None
    start_dot: DotValue | None = None
    end_dot: DotValue | None = None


class PathParser:
    """Very small path parser for circuitikz draw commands."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def skip_ws(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def at_end(self) -> bool:
        self.skip_ws()
        return self.pos >= len(self.text)

    def startswith(self, token: str) -> bool:
        return self.text.startswith(token, self.pos)

    def consume(self, token: str) -> bool:
        if self.startswith(token):
            self.pos += len(token)
            return True
        return False

    def read_enclosed(self, opener: str, closer: str) -> str:
        if not self.consume(opener):
            raise ValueError(f"expected '{opener}' in path segment")
        depth = 1
        start = self.pos
        while self.pos < len(self.text) and depth > 0:
            ch = self.text[self.pos]
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
            self.pos += 1
        if depth != 0:
            raise ValueError(f"unbalanced '{opener}{closer}' in path segment")
        return self.text[start : self.pos - 1]

    def read_brackets(self) -> str:
        return self.read_enclosed("[", "]")

    def read_braces(self) -> str:
        return self.read_enclosed("{", "}")

    def parse_coordinate(self, last_point: Coordinate | None) -> Coordinate:
        self.skip_ws()
        relative = 0
        while self.pos < len(self.text) and self.text[self.pos] == "+":
            relative += 1
            self.pos += 1
        if self.pos >= len(self.text) or self.text[self.pos] != "(":
            raise ValueError("expected coordinate")
        coord_contents = self.read_enclosed("(", ")")
        parts = coord_contents.split(",")
        if len(parts) != 2:
            raise ValueError("invalid coordinate")
        x = int_or_float(parts[0].strip())
        y = int_or_float(parts[1].strip())
        if relative:
            if last_point is None:
                raise ValueError("relative coordinate without reference point")
            return (last_point[0] + x, last_point[1] + y)
        return (x, y)


def strip_comments(raw: str) -> str:
    cleaned: list[str] = []
    for line in raw.splitlines():
        idx = line.find("%")
        if idx != -1:
            line = line[:idx]
        cleaned.append(line)
    return "\n".join(cleaned)


def split_options(options: str | None) -> list[str]:
    if not options:
        return []
    tokens: list[str] = []
    current: list[str] = []
    stack: list[str] = []
    matching = {"[": "]", "(": ")", "{": "}"}
    for ch in options:
        if ch in matching:
            stack.append(matching[ch])
        elif stack and ch == stack[-1]:
            stack.pop()
        if ch == "," and not stack:
            token = "".join(current).strip()
            if token:
                tokens.append(token)
            current = []
            continue
        current.append(ch)
    token = "".join(current).strip()
    if token:
        tokens.append(token)
    return tokens


def clean_value(value: str) -> str:
    value = value.strip()
    if value.startswith("{") and value.endswith("}"):
        value = value[1:-1].strip()
    return value


def key_metadata(key: str) -> tuple[str, set[str], bool]:
    raw = key.strip()
    modifiers: list[str] = []
    while raw and raw[-1] in "^_<>+-":
        modifiers.append(raw[-1])
        raw = raw[:-1]
    american_override = False
    lowered = " ".join(raw.split()).lower()
    if lowered.startswith("american "):
        american_override = True
        lowered = lowered[len("american "):].strip()
    elif lowered.endswith(" american"):
        american_override = True
        lowered = lowered[: -len(" american")].strip()
    lowered = " ".join(lowered.split())
    return lowered, set(modifiers), american_override


def normalize_key(key: str) -> str:
    norm_key, _, _ = key_metadata(key)
    return norm_key


def normalize_alias_key(key: str) -> tuple[str, bool]:
    norm_key, _, american_override = key_metadata(key)
    return norm_key, american_override


def resolve_two_term_alias(key: str, american_style: bool) -> Component2TermTypes | None:
    if not key:
        return None
    alias = two_term_aliases.get(key)
    if alias is None:
        return None
    return alias.resolve(american=american_style)


def resolve_two_term_alias_token(token: str, american_style: bool) -> Component2TermTypes | None:
    key, _, american_override = key_metadata(token)
    return resolve_two_term_alias(key, american_style or american_override)


def parse_dot_token(token: str) -> tuple[DotValue | None, DotValue | None]:
    token = token.strip()
    if not token:
        return (None, None)
    dot_map: dict[str, DotValue] = {"*": "filled", "o": "open"}
    start = dot_map.get(token[0]) if token[0] in dot_map else None
    end = dot_map.get(token[-1]) if token[-1] in dot_map else None
    return (start, end)


def parse_segment_options(options: str | None, *, american_style: bool) -> SegmentStyle:
    tokens = split_options(options)
    component_type: Component2TermTypes = "Line"
    labels: LabelList = []
    start_dot: DotValue | None = None
    end_dot: DotValue | None = None

    for token in tokens:
        if not token:
            continue
        if "=" in token:
            key, value = token.split("=", 1)
            key_base, modifiers, american_override = key_metadata(key)
            value_clean = clean_value(value)
            if not value_clean:
                continue
            if key_base in label_keys:
                labels.append(make_label_entry(key_base, value_clean, modifiers))
                continue
            resolved_alias = resolve_two_term_alias(key_base, american_style or american_override)
            if resolved_alias and component_type == "Line":
                component_type = resolved_alias
            if key_base.startswith("v"):
                labels.append(value_clean)
            elif resolved_alias:
                labels.append(value_clean)
            elif key_base == "name":
                continue
            elif key_base == "i":
                continue
            else:
                labels.append(value_clean)
        else:
            component_override = resolve_two_term_alias_token(token, american_style)
            if component_override and component_type == "Line":
                component_type = component_override
                continue
            start, end = parse_dot_token(token)
            start_dot = start_dot or start
            end_dot = end_dot or end

    return SegmentStyle(
        type=component_type,
        label=labels or None,
        start_dot=start_dot,
        end_dot=end_dot,
    )


def label_union_from(labels: LabelList | None) -> LabelUnion | None:
    if not labels:
        return None
    if len(labels) == 1:
        return labels[0]
    return labels


def register_dot(nodes: dict[Coordinate, Node], pos: Coordinate, dot_type: DotValue | None) -> None:
    if not dot_type:
        return
    node = nodes.setdefault(pos, {"pos": pos})
    if dot_type == "filled" or node.get("dot") != "filled":
        node["dot"] = dot_type


def resolve_single_component(options: str | None, american_style: bool) -> ComponentTypes | None:
    if not options:
        return None
    tokens = split_options(options)
    for token in tokens:
        if not token:
            continue
        key = token.split("=", 1)[0]
        alias_key, _, alias_override = key_metadata(key)
        alias = single_pole_aliases.get(alias_key)
        if alias:
            return alias.resolve(american=american_style or alias_override)
    return None


def parse_node_tokens(
    parser: PathParser,
    pos: Coordinate,
    components: list[dict],
    *,
    american_style: bool,
) -> None:
    while True:
        parser.skip_ws()
        if not parser.startswith("node"):
            break
        parser.consume("node")
        parser.skip_ws()
        options = parser.read_brackets() if parser.startswith("[") else None
        parser.skip_ws()
        node_pos: Coordinate | None = None
        if parser.pos < len(parser.text) and parser.text[parser.pos] in "+(":
            node_pos = parser.parse_coordinate(pos)
            parser.skip_ws()
        if parser.startswith("{"):
            parser.read_braces()
        component_type = resolve_single_component(options, american_style)
        if component_type:
            components.append({
                "pos": node_pos or pos,
                "type": component_type,
            })


def parse_draw_command(
    body: str,
    components: list[dict],
    nodes: dict[Coordinate, Node],
    *,
    american_style: bool,
) -> None:
    parser = PathParser(body)
    try:
        current = parser.parse_coordinate(None)
    except ValueError:
        return
    parse_node_tokens(parser, current, components, american_style=american_style)
    while not parser.at_end():
        style: SegmentStyle | None = None
        if parser.consume("--") or parser.consume("-"):
            style = SegmentStyle()
        elif parser.consume("to"):
            parser.skip_ws()
            options = parser.read_brackets() if parser.startswith("[") else None
            style = parse_segment_options(options, american_style=american_style)
        else:
            break
        parser.skip_ws()
        try:
            target = parser.parse_coordinate(current)
        except ValueError:
            break
        component = {
            "from": current,
            "to": target,
            "type": style.type,
        }
        label_union = label_union_from(style.label)
        if label_union is not None:
            component["label"] = label_union
        components.append(component)
        register_dot(nodes, current, style.start_dot)
        register_dot(nodes, target, style.end_dot)
        current = target
    parse_node_tokens(parser, current, components, american_style=american_style)


def strip_body(raw_circuitikz: str) -> tuple[str, bool]:
    cleaned = strip_comments(raw_circuitikz.strip())
    header_match = header_pattern.match(cleaned)
    if not header_match:
        raise ValueError("Invalid circuitikz format: missing header")
    env = header_match.group("env")
    options = header_match.group("options") or ""
    american = "american" in options.lower()
    end_match = end_pattern.search(cleaned, header_match.end())
    while end_match and end_match.group("env") != env:
        end_match = end_pattern.search(cleaned, end_match.end())
    if not end_match:
        raise ValueError("Invalid circuitikz format: missing end tag")
    body = cleaned[header_match.end() : end_match.start()]
    return body, american


def parse_circuit_body(body: str, american: bool) -> AnalogCircuit:
    components: list[dict] = []
    nodes: dict[Coordinate, Node] = {}
    for match in draw_pattern.finditer(body):
        command_body = match.group("body").strip()
        if not command_body:
            continue
        parse_draw_command(command_body, components, nodes, american_style=american)
    circuit: dict = {"components": components}
    if nodes:
        circuit["nodes"] = list(nodes.values())
    return parse_circuit(circuit)


def from_circuitikz(raw_circuitikz: str) -> AnalogCircuit:
    body, american = strip_body(raw_circuitikz)
    circuit = parse_circuit_body(body, american)
    return circuit
